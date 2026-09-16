# Other ecosystems

The core checklist in SKILL.md applies unchanged. What differs is where the metadata
lives and which badges exist.

## Python

Metadata goes in `pyproject.toml` under `[project]`:

```toml
[project]
name = "your-package"
description = "One sentence. The same one as the README opener."
readme = "README.md"
requires-python = ">=3.9"
license = { text = "MIT" }
keywords = ["these", "feed", "pypi", "search"]
classifiers = [
  "Development Status :: 4 - Beta",
  "Intended Audience :: Developers",
  "Programming Language :: Python :: 3",
]

[project.urls]
Homepage = "https://github.com/owner/repo"
Documentation = "https://..."
Issues = "https://github.com/owner/repo/issues"
Changelog = "https://github.com/owner/repo/blob/main/CHANGELOG.md"
```

`[project.urls]` becomes the sidebar links on PyPI and is usually the biggest missing
piece. `classifiers` drive PyPI's filtered browsing. Check the rendered result before
publishing with `python -m build && twine check dist/*` — a README that fails to render
on PyPI is a common and invisible failure.

PyPI also supports trusted publishing from GitHub Actions (OIDC, no token stored),
configured under the project's Publishing settings.

Badges: `pypi/v`, `pypi/pyversions`, `pypi/dm`, CI, licence — all via
`https://img.shields.io/pypi/v/PACKAGE`.

## Rust

`Cargo.toml` under `[package]`: `description`, `repository`, `homepage`,
`documentation`, `license`, `readme`, `keywords` (**max 5**, each ≤20 chars) and
`categories` (from crates.io's fixed slug list — invalid ones fail the publish).

`cargo publish --dry-run` catches metadata problems and packaging mistakes before they
become a permanent version on crates.io, which cannot be unpublished.

Badges: `crates/v`, `crates/d`, and docs.rs — `https://docs.rs/CRATE/badge.svg`. docs.rs
builds automatically from the published crate, so the doc comments *are* the
documentation site; a crate-level `//!` comment at the top of `lib.rs` is what a reader
lands on.

## Go

The module path in `go.mod` is the import path, and pkg.go.dev is the docs site whether
you like it or not. Which means:

- The package comment (`// Package foo …` above the `package` clause, conventionally in
  `doc.go`) is the landing paragraph on pkg.go.dev. Write it as prose for a stranger.
- Runnable `Example` functions in `_test.go` files render on pkg.go.dev as executable
  examples. They're the highest-leverage docs a Go package can have.
- Tags need the `v` prefix (`v1.2.0`) and semver, or the module proxy won't serve them.

Badge: `https://pkg.go.dev/badge/github.com/owner/repo.svg`, plus CI and licence, plus
`goreportcard.com/badge/github.com/owner/repo` if it scores well.

## Anything else, or nothing at all

Plenty of repos are just a repo — a script collection, a config, a small app. The core
checklist still applies and is worth doing: LICENCE, a README that opens with one clear
sentence, a picture if there's anything visual, the GitHub description, homepage and
topics, and a social preview image. Those five cover almost all of the discoverability
gap for a project with no registry listing to lean on.

Where there's no package registry, GitHub topics are doing all the discovery work, so
spend the extra minute on them.
