# Contributing

## Requirements

- [Claude Code](https://claude.com/claude-code) (for `claude plugin validate`)
- git

## Adding or changing a skill

```bash
git clone https://github.com/killerwolf/skills.git
cd skills
```

1. Put the skill under `skills/<name>/`, following the standard `SKILL.md` layout.
2. Register it as a plugin in `.claude-plugin/marketplace.json` (or, for an existing
   skill, bump that plugin's `version` — installed copies only update when the
   version changes).
3. Add or update its row in the README's skill table.
4. Add a `CHANGELOG.md` entry under `## [Unreleased]`.
5. Run `claude plugin validate --strict .` locally — CI runs the same check.
6. Open a pull request describing what changed and why.

## Releasing

1. Move the `## [Unreleased]` entries in `CHANGELOG.md` into a new dated section.
2. Merge to `main`. There's no separate publish step — the marketplace is read
   directly from this repo, so a merged version bump is live immediately for anyone
   who runs `claude plugin update`.

## Code of conduct

Be decent to people. Report problems by opening an issue.
