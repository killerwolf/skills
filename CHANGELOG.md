# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and each skill's plugin version follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed

- **Breaking:** the five one-skill plugins are replaced by two plugins, `studio` (v1.0.0:
  `gemini-voices`, `sound-design`, `studio-mate`) and `toolbox` (v1.0.0: `devto-post`,
  `repo-glowup`). Uninstall the old plugins and install the new ones; skills are now
  namespaced by the new plugin, e.g. `/studio:gemini-voices`.

### Fixed

- `studio-mate` (v1.0.1): no angle brackets in the skill description, which claude.ai rejects.

### Added

- `studio-mate` plugin (v1.0.0) — pilots video studios from Notion without code or GitHub:
  what is waiting across all studios, ideas, review feedback, unblocking, dates.
- CI workflow validating the plugin marketplace on every push and PR.
- CONTRIBUTING.md and this changelog.
- Repo social preview card.
- `gemini-voices` plugin (v1.0.0) — generates video voices with Gemini and splits a
  dialogue into one file per line.
- `sound-design` plugin (v1.0.0) — adds sound design to short videos: CC0 sound effects
  timed to on-screen text and transitions, mixed under the voice, with a bundled,
  extendable sound library (OpenGameArt, Freesound).

## [2026-09-16]

### Added

- `repo-glowup` plugin (v1.0.0) — audits and upgrades a repo's discoverability.
- `devto-post` plugin (v1.0.0) — researches, drafts and loads a dev.to article in your
  voice, waits for you to publish it by hand, then drafts the matching LinkedIn promo
  and schedules it once you approve.
