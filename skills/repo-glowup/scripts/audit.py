#!/usr/bin/env python3
"""Audit a repository's discoverability surface.

Detects the project type, reports which credibility signals are present or missing,
and suggests a badge row built from the project's real identifiers.

Usage:
    python3 audit.py [--markdown | --json] [path]
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# A manifest in a source directory is the file to edit. One in a build directory is
# generated (WXT, Plasmo, a bundler) — it still proves this is an extension, but
# editing it is pointless because the next build overwrites it.
MANIFEST_SOURCE_DIRS = [".", "src", "public", "extension", "app", "static"]
MANIFEST_BUILD_DIRS = [
    ".output/chrome-mv3",
    ".output",
    "dist/chrome-mv3",
    "dist",
    "build",
    "out",
]

# Names that mean the project was scaffolded and never renamed. Worth flagging: it is
# the single loudest "unfinished" signal a stranger can see, and it is invisible to
# whoever has been staring at the repo for months.
STARTER_NAME_PATTERNS = [
    "starter",
    "boilerplate",
    "template",
    "hello-world",
    "helloworld",
    "my-app",
    "my-project",
    "example-app",
    "untitled",
    "vite-project",
    "react-app",
]

EXTENSION_DEPS = {"wxt", "plasmo", "webextension-polyfill", "@types/chrome", "crxjs",
                  "@crxjs/vite-plugin", "@plasmohq/storage", "webext-bridge"}
DESKTOP_DEPS = {"electron", "electron-builder", "electron-updater", "@electron/remote",
                "@tauri-apps/api", "@tauri-apps/cli", "nw"}
WEBAPP_DEPS = {"react", "react-dom", "vue", "svelte", "next", "nuxt", "@angular/core",
               "astro", "solid-js", "vite", "express", "fastify", "koa", "@nestjs/core"}

# Where a static landing page (as opposed to markdown docs) tends to live.
LANDING_PAGE_CANDIDATES = [
    "docs/index.html",
    "site/index.html",
    "www/index.html",
    "landing/index.html",
    "landing-page/index.html",
]


def run(cmd, cwd=None, timeout=10):
    try:
        out = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout
        )
        return out.stdout.strip() if out.returncode == 0 else None
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


def repo_root(start):
    top = run(["git", "rev-parse", "--show-toplevel"], cwd=start)
    return Path(top) if top else Path(start).resolve()


def load_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def find_file(root, names):
    """Return the first existing path matching any of `names` (case-insensitive)."""
    lowered = {n.lower() for n in names}
    try:
        for entry in os.listdir(root):
            if entry.lower() in lowered:
                return root / entry
    except OSError:
        pass
    return None


# GitHub recognises these "community health" files in the repo root, .github/, or
# docs/ — a project that keeps CONTRIBUTING.md in docs/ isn't missing one.
COMMUNITY_FILE_DIRS = [".", ".github", "docs"]


def find_community_file(root, names):
    for d in COMMUNITY_FILE_DIRS:
        found = find_file(root / d, names)
        if found:
            return found
    return None


def find_manifest(root):
    """Return (path, data, is_generated). Source manifests win over built ones."""
    for dirs, generated in ((MANIFEST_SOURCE_DIRS, False), (MANIFEST_BUILD_DIRS, True)):
        for d in dirs:
            candidate = root / d / "manifest.json"
            if candidate.is_file():
                data = load_json(candidate)
                if data and "manifest_version" in data:
                    return candidate, data, generated
    return None, None, False


def all_deps(pkg):
    if not pkg:
        return set()
    names = set()
    for field in ("dependencies", "devDependencies", "peerDependencies"):
        names |= set((pkg.get(field) or {}).keys())
    return names


def looks_like_starter(name):
    if not name:
        return False
    lowered = name.lower()
    return any(p in lowered for p in STARTER_NAME_PATTERNS)


def git_remote_slug(root):
    url = run(["git", "remote", "get-url", "origin"], cwd=root)
    if not url:
        return None
    m = re.search(r"github\.com[:/]+([^/]+)/(.+?)(?:\.git)?$", url)
    return f"{m.group(1)}/{m.group(2)}" if m else None


def gh_repo_info(root):
    """Current GitHub listing metadata. Returns None if gh is missing or unauthed."""
    out = run(
        ["gh", "repo", "view", "--json", "description,homepageUrl,repositoryTopics"],
        cwd=root,
        timeout=15,
    )
    if not out:
        return None
    data = load_json_string(out)
    if not data:
        return None
    topics = [
        t.get("name")
        for t in (data.get("repositoryTopics") or [])
        if isinstance(t, dict)
    ]
    return {
        "description": data.get("description") or "",
        "homepage": data.get("homepageUrl") or "",
        "topics": topics,
    }


def load_json_string(text):
    try:
        return json.loads(text)
    except ValueError:
        return None


def find_pages_workflow(workflow_dir):
    """A workflow that deploys to GitHub Pages, detected by the actions it calls
    rather than its filename — people name these things differently."""
    if not workflow_dir.is_dir():
        return None
    for p in sorted(workflow_dir.glob("*.y*ml")):
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if re.search(r"actions/deploy-pages|actions/configure-pages", text):
            return p.name
    return None


def has_gh_pages_branch(root):
    return bool(run(["git", "branch", "-r", "--list", "*/gh-pages"], cwd=root))


def gh_pages_status(root, slug):
    """Whether GitHub Pages is switched on for this repo, per the API. None when
    `gh` is missing/unauthenticated as well as when Pages is off — same ambiguity
    `gh_repo_info` already has, and the markdown report hedges accordingly."""
    if not slug:
        return None
    out = run(["gh", "api", f"repos/{slug}/pages"], cwd=root, timeout=15)
    if not out:
        return None
    data = load_json_string(out)
    if not data:
        return None
    return {
        "url": data.get("html_url"),
        "build_type": data.get("build_type"),  # "workflow" (Actions) or "legacy" (branch)
    }


def find_landing_page(root, slug):
    workflow_dir = root / ".github" / "workflows"
    return {
        "workflow": find_pages_workflow(workflow_dir),
        "source_candidates": [
            c for c in LANDING_PAGE_CANDIDATES if (root / c).is_file()
        ],
        "gh_pages_branch": has_gh_pages_branch(root),
        "pages_configured": gh_pages_status(root, slug),
    }


def detect_type(root, pkg, manifest, manifest_generated):
    """Return (primary_type, notes).

    Ordered by how decisive each signal is. `main` on its own is a famously weak
    signal — Electron apps, scripts and half the repos on GitHub have one — so a
    library verdict needs a publishing signal too, not just an entry point.
    """
    notes = []
    deps = all_deps(pkg)

    if manifest is not None:
        where = "a build directory" if manifest_generated else "the source tree"
        notes.append(f"manifest.json with manifest_version found in {where}")
        if manifest_generated:
            notes.append(
                "that manifest is generated — edit the framework config or source "
                "manifest instead"
            )
        return "browser-extension", notes

    ext_deps = deps & EXTENSION_DEPS
    if ext_deps:
        notes.append(f"extension tooling in dependencies: {', '.join(sorted(ext_deps))}")
        if (root / "entrypoints").is_dir():
            notes.append("`entrypoints/` directory (WXT layout)")
        return "browser-extension", notes

    if pkg is not None:
        desktop = deps & DESKTOP_DEPS
        if desktop or (root / "src-tauri").is_dir():
            notes.append(
                "desktop app shell detected: "
                + (", ".join(sorted(desktop)) if desktop else "src-tauri/")
            )
            return "desktop-app", notes

        if pkg.get("bin"):
            notes.append("package.json has a `bin` field")
            return "cli-tool", notes

        publishing_signals = [
            f
            for f in ("exports", "files", "module", "types", "typings", "publishConfig")
            if pkg.get(f)
        ]
        if not pkg.get("private") and publishing_signals:
            notes.append(
                f"package.json is publishable and declares {', '.join(publishing_signals)}"
            )
            return "npm-library", notes

        webapp = deps & WEBAPP_DEPS
        if webapp:
            notes.append(
                f"application framework in dependencies: {', '.join(sorted(webapp)[:4])}"
            )
            return "web-app", notes

        if pkg.get("main") and not pkg.get("private"):
            notes.append(
                "package.json has `main` but no exports/files/types — could be a "
                "library that never had its packaging finished, or just a script; "
                "check before treating it as publishable"
            )
            return "npm-library", notes

        notes.append("package.json with no entry points, bin or framework deps")
        return "app", notes
    for filename, kind in (
        ("pyproject.toml", "python"),
        ("setup.py", "python"),
        ("Cargo.toml", "rust"),
        ("go.mod", "go"),
        ("composer.json", "php"),
        ("Gemfile", "ruby"),
    ):
        if (root / filename).is_file():
            notes.append(f"{filename} found")
            return kind, notes
    notes.append("no recognised package manifest")
    return "generic", notes


def analyse_readme(path):
    if path is None:
        return {"present": False}
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {"present": False}
    raw_headings = re.findall(r"^#{1,3} +(.+)$", text, re.MULTILINE)
    headings = []
    for h in raw_headings:
        # Headings often carry an inline <img> logo; keep the words, drop the markup.
        clean = re.sub(r"<[^>]+>", "", h)
        clean = re.sub(r"[*`_]", "", clean).strip()
        if clean:
            headings.append(clean[:60])
    lowered = text.lower()
    return {
        "present": True,
        "path": path.name,
        "words": len(text.split()),
        "headings": headings[:20],
        "has_badges": "img.shields.io" in lowered or "badge.svg" in lowered,
        "has_images": bool(re.search(r"!\[|<img", text)),
        "has_install": any(
            re.search(rf"^#{{1,3}} *.*{kw}", text, re.MULTILINE | re.IGNORECASE)
            for kw in ("install", "getting started", "quick ?start", "setup")
        ),
        "has_relative_images": bool(
            re.search(r"!\[[^\]]*\]\((?!https?://|data:)", text)
        ),
    }


def empty_fields(obj, fields):
    missing = []
    for f in fields:
        value = obj.get(f)
        if value in (None, "", [], {}):
            missing.append(f)
    return missing


def suggest_badges(ctx):
    """Build a badge row from real identifiers. Returns a list of markdown lines."""
    badges = []
    slug = ctx.get("repo_slug")
    pkg = ctx.get("package_json") or {}
    name = pkg.get("name")
    workflows = ctx.get("workflows") or []
    ptype = ctx["project_type"]

    if ptype in ("npm-library", "cli-tool") and name and not pkg.get("private"):
        enc = name.replace("/", "%2F")
        badges.append(
            f'<a href="https://www.npmjs.com/package/{name}">'
            f'<img alt="npm version" src="https://img.shields.io/npm/v/{enc}?color=cb3837&logo=npm"></a>'
        )
        if ptype == "cli-tool":
            badges.append(
                f'<a href="https://www.npmjs.com/package/{name}">'
                f'<img alt="downloads" src="https://img.shields.io/npm/dm/{enc}"></a>'
            )
        else:
            badges.append(
                f'<a href="https://bundlephobia.com/package/{name}">'
                f'<img alt="gzipped size" src="https://img.shields.io/bundlephobia/minzip/{enc}?label=gzipped"></a>'
            )
            badges.append(
                f'<a href="https://www.npmjs.com/package/{name}">'
                f'<img alt="types included" src="https://img.shields.io/npm/types/{enc}"></a>'
            )
    if ptype == "browser-extension":
        badges.append(
            '<a href="https://chromewebstore.google.com/detail/EXTENSION_ID">'
            '<img alt="Chrome Web Store version" src="https://img.shields.io/chrome-web-store/v/EXTENSION_ID"></a>'
        )
        badges.append(
            '<a href="https://chromewebstore.google.com/detail/EXTENSION_ID">'
            '<img alt="users" src="https://img.shields.io/chrome-web-store/users/EXTENSION_ID"></a>'
        )
    if ptype == "python":
        badges.append(
            '<a href="https://pypi.org/project/PACKAGE/">'
            '<img alt="PyPI" src="https://img.shields.io/pypi/v/PACKAGE"></a>'
        )
    if ptype == "rust":
        badges.append(
            '<a href="https://crates.io/crates/CRATE">'
            '<img alt="crates.io" src="https://img.shields.io/crates/v/CRATE"></a>'
        )
    if ptype == "desktop-app" and slug:
        # For an app nobody installs from a registry, the release is the product.
        badges.append(
            f'<a href="https://github.com/{slug}/releases/latest">'
            f'<img alt="latest release" src="https://img.shields.io/github/v/release/{slug}"></a>'
        )
        badges.append(
            f'<a href="https://github.com/{slug}/releases">'
            f'<img alt="downloads" src="https://img.shields.io/github/downloads/{slug}/total"></a>'
        )
    if ptype == "go" and slug:
        badges.append(
            f'<a href="https://pkg.go.dev/github.com/{slug}">'
            f'<img alt="Go reference" src="https://pkg.go.dev/badge/github.com/{slug}.svg"></a>'
        )
    if slug and workflows:
        wf = next(
            (w for w in workflows if re.search(r"ci|quality|test|build", w, re.I)),
            workflows[0],
        )
        badges.append(
            f'<a href="https://github.com/{slug}/actions/workflows/{wf}">'
            f'<img alt="CI status" src="https://github.com/{slug}/actions/workflows/{wf}/badge.svg"></a>'
        )
    if slug:
        badges.append(
            f'<a href="https://github.com/{slug}/blob/main/LICENSE">'
            f'<img alt="licence" src="https://img.shields.io/github/license/{slug}"></a>'
        )
    return badges


def audit(path):
    root = repo_root(path)
    pkg_path = root / "package.json"
    pkg = load_json(pkg_path) if pkg_path.is_file() else None
    manifest_path, manifest, manifest_generated = find_manifest(root)

    project_type, type_notes = detect_type(root, pkg, manifest, manifest_generated)

    readme_path = find_file(root, ["README.md", "README.rst", "README.txt", "README"])
    license_path = find_community_file(root, ["LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"])
    contributing = find_community_file(root, ["CONTRIBUTING.md", "CONTRIBUTING"])
    changelog = find_community_file(root, ["CHANGELOG.md", "CHANGELOG", "HISTORY.md"])
    coc = find_community_file(root, ["CODE_OF_CONDUCT.md"])

    workflow_dir = root / ".github" / "workflows"
    workflows = (
        sorted(p.name for p in workflow_dir.glob("*.y*ml")) if workflow_dir.is_dir() else []
    )

    social_candidates = []
    for pattern in ("social*", "og-image*", "*preview*", "banner*"):
        for base in (root / ".github" / "assets", root / "assets", root / "docs", root):
            if base.is_dir():
                social_candidates += [
                    str(p.relative_to(root))
                    for p in base.glob(pattern)
                    if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")
                ]

    ctx = {
        "root": str(root),
        "project_type": project_type,
        "type_evidence": type_notes,
        "repo_slug": git_remote_slug(root),
        "package_json": pkg,
        "workflows": workflows,
    }

    result = {
        "root": str(root),
        "project_type": project_type,
        "type_evidence": type_notes,
        "repo_slug": ctx["repo_slug"],
        "readme": analyse_readme(readme_path),
        "files": {
            "LICENSE": bool(license_path),
            "CONTRIBUTING": bool(contributing),
            "CHANGELOG": bool(changelog),
            "CODE_OF_CONDUCT": bool(coc),
            ".gitignore": (root / ".gitignore").is_file(),
        },
        "ci_workflows": workflows,
        "social_image_candidates": sorted(set(social_candidates)),
        "github_listing": gh_repo_info(root),
        "landing_page": find_landing_page(root, ctx["repo_slug"]),
        "metadata_gaps": {},
        "warnings": [],
        "suggested_badges": suggest_badges(ctx),
    }

    project_name = (pkg or {}).get("name") or (manifest or {}).get("name")
    if looks_like_starter(project_name):
        result["warnings"].append(
            f"the project is still called `{project_name}` — a scaffolding name that "
            "was never changed. Rename it before anything else; it undoes every other "
            "signal on the page."
        )
    if manifest_generated:
        result["warnings"].append(
            f"`{manifest_path.relative_to(root)}` is a build artifact. Extension "
            "metadata must be edited at its source (wxt.config.ts, a source "
            "manifest.json, or the bundler's extension plugin config)."
        )

    if pkg is not None:
        core = [
            "name",
            "version",
            "description",
            "keywords",
            "license",
            "author",
            "repository",
            "bugs",
            "homepage",
            "engines",
            "files",
        ]
        gaps = empty_fields(pkg, core)
        if project_type == "npm-library":
            if not pkg.get("exports"):
                gaps.append("exports")
            if not pkg.get("types") and not pkg.get("typings"):
                gaps.append("types")
        kw = pkg.get("keywords") or []
        result["metadata_gaps"]["package.json"] = {
            "empty_fields": gaps,
            "keyword_count": len(kw),
            "keywords_thin": len(kw) < 5,
            "description_length": len(pkg.get("description") or ""),
            "private": bool(pkg.get("private")),
        }

    if manifest is not None:
        gaps = empty_fields(
            manifest, ["name", "description", "version", "icons", "homepage_url"]
        )
        icons = manifest.get("icons") or {}
        desc = manifest.get("description") or ""
        result["metadata_gaps"]["manifest.json"] = {
            "path": str(manifest_path.relative_to(root)),
            "generated": manifest_generated,
            "empty_fields": gaps,
            "missing_icon_sizes": [s for s in ("16", "48", "128") if s not in icons],
            "description_length": len(desc),
            "description_too_long_for_store": len(desc) > 132,
            "permissions": manifest.get("permissions") or [],
            "host_permissions": manifest.get("host_permissions") or [],
            "manifest_version": manifest.get("manifest_version"),
        }

    return result


def to_markdown(r):
    L = []
    tick = lambda b: "yes" if b else "**MISSING**"  # noqa: E731
    L.append(f"# Discoverability audit — `{Path(r['root']).name}`")
    L.append("")
    L.append(f"**Detected type:** `{r['project_type']}`  ")
    L.append(f"**Evidence:** {'; '.join(r['type_evidence'])}  ")
    L.append(f"**Repo:** {r['repo_slug'] or '_no github remote_'}")
    L.append("")

    if r.get("warnings"):
        L.append("## Fix these first")
        L.append("")
        for w in r["warnings"]:
            L.append(f"- {w}")
        L.append("")

    L.append("## Files")
    L.append("")
    L.append("| Signal | Present |")
    L.append("| --- | --- |")
    for k, v in r["files"].items():
        L.append(f"| {k} | {tick(v)} |")
    rd = r["readme"]
    L.append(f"| README | {tick(rd.get('present'))} |")
    L.append(
        f"| CI workflow | {tick(bool(r['ci_workflows']))}"
        + (f" ({', '.join(r['ci_workflows'])})" if r["ci_workflows"] else "")
        + " |"
    )
    L.append(
        f"| Social preview image | {tick(bool(r['social_image_candidates']))}"
        + (
            f" ({', '.join(r['social_image_candidates'][:3])})"
            if r["social_image_candidates"]
            else ""
        )
        + " |"
    )
    lp = r["landing_page"]
    lp_local = bool(lp["workflow"] or lp["source_candidates"] or lp["gh_pages_branch"])
    L.append(
        f"| Landing page (GitHub Pages) | {tick(lp_local or bool(lp['pages_configured']))}"
        + (f" ({lp['workflow']})" if lp["workflow"] else "")
        + " |"
    )
    L.append("")

    if lp["pages_configured"] and not lp_local:
        # The API says Pages is on but nothing in the tree explains what it serves —
        # possibly a docs folder outside our candidate list, worth a manual look.
        L.append(
            "_GitHub Pages is enabled on this repo per the API, but no local workflow "
            "or recognised source folder explains what it serves — check Settings > Pages._"
        )
        L.append("")

    if rd.get("present"):
        L.append("## README")
        L.append("")
        L.append(f"- {rd['words']} words, {len(rd['headings'])} headings")
        L.append(f"- badges: {tick(rd['has_badges'])}")
        L.append(f"- images/screenshots: {tick(rd['has_images'])}")
        L.append(f"- install or quick-start section: {tick(rd['has_install'])}")
        if rd.get("has_relative_images"):
            L.append(
                "- **relative image paths found** — these break on npm and in social "
                "previews; use absolute raw.githubusercontent.com URLs"
            )
        if rd["headings"]:
            L.append(f"- headings: {', '.join(rd['headings'][:12])}")
        L.append("")

    gh = r["github_listing"]
    L.append("## GitHub listing")
    L.append("")
    if gh is None:
        L.append("_`gh` unavailable or not authenticated — check manually._")
    else:
        L.append(f"- description: {gh['description'] or '**EMPTY**'}")
        L.append(f"- homepage: {gh['homepage'] or '**EMPTY**'}")
        L.append(
            f"- topics ({len(gh['topics'])}): "
            + (", ".join(gh["topics"]) if gh["topics"] else "**NONE**")
        )
    L.append("")

    for source, gaps in r["metadata_gaps"].items():
        L.append(f"## Metadata — `{gaps.get('path', source)}`")
        L.append("")
        if gaps.get("empty_fields"):
            L.append(f"- empty or missing: `{'`, `'.join(gaps['empty_fields'])}`")
        else:
            L.append("- all core fields populated")
        if "keyword_count" in gaps:
            L.append(
                f"- keywords: {gaps['keyword_count']}"
                + (" — **thin, aim for 8-15**" if gaps["keywords_thin"] else "")
            )
            L.append(f"- description length: {gaps['description_length']} chars")
        if "missing_icon_sizes" in gaps:
            if gaps["missing_icon_sizes"]:
                L.append(f"- missing icon sizes: {', '.join(gaps['missing_icon_sizes'])}")
            L.append(
                f"- description length: {gaps['description_length']} chars"
                + (
                    " — **over the 132-char Web Store limit**"
                    if gaps["description_too_long_for_store"]
                    else ""
                )
            )
            perms = gaps["permissions"] + gaps["host_permissions"]
            if perms:
                L.append(
                    f"- permissions to justify in the README: `{'`, `'.join(perms)}`"
                )
        L.append("")

    if r["suggested_badges"]:
        L.append("## Suggested badge row")
        L.append("")
        L.append("```html")
        L.append('<p align="center">')
        for b in r["suggested_badges"]:
            L.append(f"  {b}")
        L.append("</p>")
        L.append("```")
        L.append("")
        L.append(
            "_Placeholders in caps (EXTENSION_ID, PACKAGE, CRATE) need the real "
            "identifier before use. Drop any badge that doesn't answer a real question._"
        )
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path", nargs="?", default=".")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--markdown", action="store_true", help="human-readable report")
    args = ap.parse_args()

    result = audit(args.path)
    if args.json or not args.markdown:
        print(json.dumps(result, indent=2))
    else:
        print(to_markdown(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
