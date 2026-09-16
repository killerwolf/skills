# Contributing

<!--
Fill the placeholders from the real repo — read package.json / pyproject.toml for the
actual script names rather than assuming. Delete sections that don't apply; a short
accurate guide beats a long aspirational one.

This doubles as the maintainer's own notes. The release section in particular is the
thing that gets forgotten between releases, so write it as steps that can be followed
tired.
-->

## Development environment

### Requirements

- <RUNTIME AND VERSION RANGE, e.g. Node.js >=18 — match `engines`>
- <PACKAGE MANAGER>

### Setup

```bash
git clone https://github.com/<OWNER>/<REPO>.git
cd <REPO>
<INSTALL COMMAND>
```

## Project structure

```
<REPO>/
├── .github/workflows/   # CI and release automation
├── src/                 # Source
├── ...
└── README.md
```

## Scripts

| Script | Purpose |
| --- | --- |
| `<build>` | Produce the distributable output |
| `<test>` | Run the test suite once |
| `<lint>` | Check linting and formatting |

## Making a change

1. Branch from `main`.
2. Make the change, with a test where the behaviour is testable.
3. Run the checks above locally — CI runs the same ones.
4. Add a `CHANGELOG.md` entry under `## [Unreleased]` if the change is user-visible.
5. Open a pull request describing what changed and why.

## Releasing

<!-- Be specific and literal. Future-you follows this at 11pm. -->

1. Move the `## [Unreleased]` entries into a new version section with today's date.
2. Bump the version in `<VERSION FILE>`.
3. Commit, merge to `main`.
4. Tag and push: `git tag <VERSION> && git push origin <VERSION>`.
5. The release workflow publishes and creates the GitHub Release.

## Code of conduct

Be decent to people. Report problems to <CONTACT>.
