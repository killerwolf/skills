# skills

Claude Code skills I use day to day, packaged as a plugin marketplace so each one can be
installed on its own.

## Skills

| Skill | What it does | Requirements |
| --- | --- | --- |
| [`repo-glowup`](skills/repo-glowup) | Audits and upgrades a repo's discoverability: README, badges, package metadata, social preview card, CI, CHANGELOG/CONTRIBUTING, GitHub description and topics, and an optional landing page. | python3 ≥ 3.8 and git. Optional: an authenticated `gh`, for reading and setting the GitHub description and topics. Chrome or Chromium for social cards (macOS app paths, or `google-chrome`/`chromium` on `PATH`). |
| [`devto-post`](skills/devto-post) | Researches, drafts and loads a dev.to article in your voice, waits for you to publish it by hand, then drafts the matching LinkedIn promo and schedules it once you approve. | Claude in Chrome, logged in to dev.to and LinkedIn; python3; `rsvg-convert` (librsvg); curl. |

Notes on `devto-post`:

- On first use it asks for your dev.to username, timezone, publishing language and tags, and
  saves them to `~/.config/devto-post/profile.md` — outside the plugin, so updates never
  overwrite them.
- It writes in a bundled default voice unless you add your own style guide at
  `~/.config/devto-post/voice.md`; first-time setup offers to draft one from your published
  articles.
- What it never does: click Publish on dev.to, or post to LinkedIn on its own. The article
  always goes out by hand, and the LinkedIn post is scheduled at least an hour ahead, only
  after you approve its text and time.

## Install

### Option 1: plugin marketplace

```bash
claude plugin marketplace add killerwolf/skills
claude plugin install repo-glowup@killerwolf
claude plugin install devto-post@killerwolf
```

Install either plugin on its own, or both. Inside a Claude Code session, the equivalent slash
commands do the same thing:

```
/plugin marketplace add killerwolf/skills
/plugin install repo-glowup@killerwolf
/plugin install devto-post@killerwolf
```

Plugin skills are namespaced by plugin name, e.g. `/repo-glowup:repo-glowup`.

### Option 2: personal skill

Clone the repo, then symlink or copy the skill you want into `~/.claude/skills/`:

```bash
git clone https://github.com/killerwolf/skills.git
ln -s "$(pwd)/skills/skills/repo-glowup" ~/.claude/skills/repo-glowup
ln -s "$(pwd)/skills/skills/devto-post" ~/.claude/skills/devto-post
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
│   ├── devto-post/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   │   ├── browser-playbook.md
│   │   │   ├── cover-image.md
│   │   │   ├── profile.template.md
│   │   │   ├── voice.md
│   │   │   └── waiting.md
│   │   └── scripts/
│   │       ├── make-cover.py
│   │       └── wait-for-publish.sh
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
