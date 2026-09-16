# skills

Claude Code skills I use day to day, packaged as a plugin marketplace so each one can be
installed on its own.

## Skills

| Skill | What it does | Requirements |
| --- | --- | --- |
| [`repo-glowup`](skills/repo-glowup) | Audits and upgrades a repo's discoverability: README, badges, package metadata, social preview card, CI, CHANGELOG/CONTRIBUTING, GitHub description and topics, and an optional landing page. | python3 ≥ 3.8 and git. Optional: an authenticated `gh`, for reading and setting the GitHub description and topics. Chrome or Chromium for social cards (macOS app paths, or `google-chrome`/`chromium` on `PATH`). |

## Install

### Option 1: plugin marketplace

```bash
claude plugin marketplace add killerwolf/skills
claude plugin install repo-glowup@killerwolf
```

Inside a Claude Code session, the equivalent slash commands do the same thing:

```
/plugin marketplace add killerwolf/skills
/plugin install repo-glowup@killerwolf
```

Plugin skills are namespaced by plugin name, e.g. `/repo-glowup:repo-glowup`.

### Option 2: personal skill

Clone the repo, then symlink or copy the skill into `~/.claude/skills/`:

```bash
git clone https://github.com/killerwolf/skills.git
ln -s "$(pwd)/skills/skills/repo-glowup" ~/.claude/skills/repo-glowup
```

(or `cp -R` instead of `ln -s` if you'd rather have an independent copy).

## Compatibility

Built and tested with Claude Code. The skill folders follow the standard `SKILL.md` layout,
so they may work with other agents that support the same convention, but that hasn't been
tested here.

## Repo layout

```
skills/
├── .claude-plugin/
│   └── marketplace.json
├── skills/
│   └── repo-glowup/
│       ├── SKILL.md
│       ├── assets/
│       │   ├── CHANGELOG.template.md
│       │   ├── CONTRIBUTING.template.md
│       │   ├── landing-page.html
│       │   ├── social-card.html
│       │   └── workflows/
│       │       ├── extension-package.yml
│       │       ├── gh-pages.yml
│       │       ├── node-quality.yml
│       │       └── npm-publish-oidc.yml
│       ├── references/
│       │   ├── apps.md
│       │   ├── browser-extension.md
│       │   ├── cli-tool.md
│       │   ├── landing-page.md
│       │   ├── npm-library.md
│       │   ├── other-ecosystems.md
│       │   └── readme-anatomy.md
│       └── scripts/
│           ├── audit.py
│           ├── make_card.py
│           └── repo_meta.sh
├── .gitignore
├── LICENSE
└── README.md
```

## Maintaining

- When a skill changes, bump that plugin's `version` in `.claude-plugin/marketplace.json` —
  installed copies only update when the version is bumped.
- Run `claude plugin validate --strict .` before pushing.

## License

MIT — see [LICENSE](LICENSE).
