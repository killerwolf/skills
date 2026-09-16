#!/usr/bin/env python3
"""Render a social preview / OG card to PNG using headless Chrome.

Fills an HTML template with the project's name, tagline, icon and a few facts, then
screenshots it. Chrome is used because it is the one HTML renderer already installed
on nearly every machine — no image library needs to exist in the target repo.

Usage:
    python3 make_card.py --title "Visual Image Tool" \\
        --tagline "Pick focal points and crop zones on images." \\
        --icon demo/android-chrome-192x192.png \\
        --fact "zero dependencies" --fact "3.6 kB gzipped" --fact "MIT" \\
        --out .github/assets/social-preview.png

Sizes: 1280x640 suits the GitHub repo social preview, 1200x630 suits og:image.
"""

import argparse
import base64
import html
import mimetypes
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CHROME_PATHS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "google-chrome",
    "chromium",
    "chromium-browser",
]

DEFAULT_TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "social-card.html"


def find_chrome():
    for candidate in CHROME_PATHS:
        if "/" in candidate:
            if Path(candidate).exists():
                return candidate
        else:
            found = shutil.which(candidate)
            if found:
                return found
    return None


def data_uri(path):
    """Inline the icon so the render never races a file:// image load."""
    p = Path(path)
    if not p.is_file():
        raise SystemExit(f"icon not found: {path}")
    mime = mimetypes.guess_type(str(p))[0] or "image/png"
    return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"


def build_html(template, args):
    facts = "".join(
        f"<span class='fact'>{html.escape(f)}</span>" for f in (args.fact or [])
    )
    icon_block = ""
    if args.icon:
        icon_block = f"<img class='icon' src='{data_uri(args.icon)}' alt=''>"
    shot_block = ""
    if args.screenshot:
        shot_block = f"<img class='shot' src='{data_uri(args.screenshot)}' alt=''>"

    return (
        template.replace("{{TITLE}}", html.escape(args.title))
        .replace("{{TAGLINE}}", html.escape(args.tagline or ""))
        .replace("{{ICON}}", icon_block)
        .replace("{{SCREENSHOT}}", shot_block)
        .replace("{{FACTS}}", facts)
        .replace("{{ACCENT}}", html.escape(args.accent))
        .replace("{{BACKGROUND}}", html.escape(args.background))
        .replace("{{FOREGROUND}}", html.escape(args.foreground))
        .replace("{{FOOTER}}", html.escape(args.footer or ""))
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--title", required=True)
    ap.add_argument("--tagline", default="")
    ap.add_argument("--icon", help="path to a square icon/logo")
    ap.add_argument("--screenshot", help="optional product screenshot, shown alongside")
    ap.add_argument("--fact", action="append", help="short pill, repeatable")
    ap.add_argument("--footer", default="", help="e.g. github.com/owner/repo")
    ap.add_argument("--accent", default="#e5484d")
    ap.add_argument("--background", default="#101113")
    ap.add_argument("--foreground", default="#f5f6f7")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=640)
    ap.add_argument("--scale", type=float, default=2.0)
    ap.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--keep-html", action="store_true", help="keep the filled template")
    args = ap.parse_args()

    chrome = find_chrome()
    if not chrome:
        raise SystemExit(
            "No Chrome/Chromium found. Install one, or open the generated HTML in a "
            "browser and export it by hand (rerun with --keep-html to keep the file)."
        )
    if not args.template.is_file():
        raise SystemExit(f"template not found: {args.template}")

    filled = build_html(args.template.read_text(encoding="utf-8"), args)

    tmp = Path(tempfile.mkdtemp(prefix="social-card-"))
    html_path = tmp / "card.html"
    html_path.write_text(filled, encoding="utf-8")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    out = args.out.resolve()

    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--default-background-color=00000000",
        f"--force-device-scale-factor={args.scale}",
        f"--window-size={args.width},{args.height}",
        f"--screenshot={out}",
        # Let webfonts and layout settle before the shot is taken.
        "--virtual-time-budget=3000",
        html_path.as_uri(),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    if not out.is_file():
        sys.stderr.write(proc.stderr[-2000:] + "\n")
        raise SystemExit("Chrome did not produce a screenshot.")

    size_kb = out.stat().st_size / 1024
    print(f"wrote {out} ({size_kb:.0f} kB, {int(args.width * args.scale)}x{int(args.height * args.scale)})")
    if args.keep_html:
        print(f"template: {html_path}")
    if size_kb > 1024:
        print(
            "WARNING: over GitHub's 1 MB social-preview limit. Re-run with --scale 1, "
            "or convert to JPEG:  sips -s format jpeg -s formatOptions 80 "
            f"{out} --out {out.with_suffix('.jpg')}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
