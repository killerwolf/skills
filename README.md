# skills

Claude Code skills I use day to day, packaged as a plugin marketplace so each one can be
installed on its own.

<p align="center">
  <a href="https://github.com/killerwolf/skills/actions/workflows/validate.yml"><img alt="validate" src="https://github.com/killerwolf/skills/actions/workflows/validate.yml/badge.svg"></a>
  <a href="https://github.com/killerwolf/skills/blob/main/LICENSE"><img alt="licence" src="https://img.shields.io/github/license/killerwolf/skills"></a>
</p>

## Skills

| Skill | What it does | Requirements |
| --- | --- | --- |
| **Dev** | | |
| [`repo-glowup`](skills/repo-glowup) | Audits and upgrades a repo's discoverability: README, badges, package metadata, social preview card, CI, CHANGELOG/CONTRIBUTING, GitHub description and topics, and an optional landing page. | python3 ≥ 3.8 and git. Optional: an authenticated `gh`, for reading and setting the GitHub description and topics. Chrome or Chromium for social cards (macOS app paths, or `google-chrome`/`chromium` on `PATH`). |
| **Writing** | | |
| [`devto-post`](skills/devto-post) | Researches, drafts and loads a dev.to article in your voice, waits for you to publish it by hand, then drafts the matching LinkedIn promo and schedules it once you approve. | Claude in Chrome, logged in to dev.to and LinkedIn; python3; `rsvg-convert` (librsvg); curl. |
| **Video** | | |
| [`gemini-voices`](skills/gemini-voices) | Generates video voices with Gemini (narration, characters, two-voice dialogue) and splits a dialogue into one file per line. Written in French. | `uv` (or python3 with `google-genai` and `numpy`), `ffmpeg`, and a `GEMINI_API_KEY`. |
| [`sound-design`](skills/sound-design) | Adds sound design to short videos: CC0 whooshes, pops, impacts, typing and dings timed to on-screen text and transitions, mixed under the voice. Ships 12 CC0 sounds and can add more from Freesound. Written in French. | python3 ≥ 3.8 and `ffmpeg`. Optional: a `FREESOUND_API_KEY` to add sounds from Freesound. |

The two video skills pair well with [StudioVisualIdentity](https://github.com/killerwolf/StudioVisualIdentity),
a catalogue of 14 visual styles for vertical shorts plus the tooling to produce episodes.

### Try it

Once a skill is installed, just ask in plain words; the skill triggers on its own.

| Skill | Say something like |
| --- | --- |
| `repo-glowup` | "Glow up this repo's README and GitHub metadata." |
| `devto-post` | "Write a dev.to post about how we cut our CI time in half." |
| `gemini-voices` | « Génère la narration de cet épisode avec Gemini, voix Charon, ton documentaire. » |
| `sound-design` | « Ajoute du sound design à cette vidéo » · « plus punchy » · « remplace le son de frappe ». |

### Notes on `devto-post`

- On first use it asks for your dev.to username, timezone, publishing language and tags, and
  saves them to `~/.config/devto-post/profile.md` — outside the plugin, so updates never
  overwrite them.
- It writes in a bundled default voice unless you add your own style guide at
  `~/.config/devto-post/voice.md`; first-time setup offers to draft one from your published
  articles.
- What it never does: click Publish on dev.to, or post to LinkedIn on its own. The article
  always goes out by hand, and the LinkedIn post is scheduled at least an hour ahead, only
  after you approve its text and time.

### Notes on `gemini-voices`

- One generation is one API call: it announces the number of calls first, never retries on
  its own, and never overwrites an existing file.
- The key is read from `GEMINI_API_KEY` or a `.env` in the project; it is never printed or
  asked for in the chat.

### Notes on `sound-design`

- Each video gets a small `sfx_events.json` (time, sound role, gain): the "sound score" you can
  read, version and tweak, then `sound_design.py poser` builds the effects track and `mixer`
  lays it under the existing audio (optionally ducking under a voice track).
- It can't listen: it measures levels (peak ≤ −1 dBFS, no slice suddenly louder) and always asks
  you to listen before publishing.
- Only CC0 or license-checked sounds, each credited in `credits.json`. To add sounds from
  Freesound, get a free key at <https://freesound.org/apiv2/apply> and set `FREESOUND_API_KEY`;
  in a cloud environment, `freesound.org` must be allowed by the network settings.
- Work on a per-project copy of the library (`--biblio DIR` or `SOUND_DESIGN_LIB`) so updates to
  the plugin never overwrite your sounds.

## Install

### Option 1: plugin marketplace

```bash
claude plugin marketplace add killerwolf/skills
claude plugin install repo-glowup@killerwolf
claude plugin install devto-post@killerwolf
claude plugin install gemini-voices@killerwolf
claude plugin install sound-design@killerwolf
```

Install any plugin on its own, or several. Inside a Claude Code session, the equivalent slash
commands do the same thing:

```
/plugin marketplace add killerwolf/skills
/plugin install repo-glowup@killerwolf
/plugin install devto-post@killerwolf
/plugin install gemini-voices@killerwolf
/plugin install sound-design@killerwolf
```

Plugin skills are namespaced by plugin name, e.g. `/repo-glowup:repo-glowup`.

### Option 2: personal skill

Clone the repo, then symlink or copy the skill you want into `~/.claude/skills/`:

```bash
git clone https://github.com/killerwolf/skills.git
ln -s "$(pwd)/skills/skills/repo-glowup" ~/.claude/skills/repo-glowup
ln -s "$(pwd)/skills/skills/devto-post" ~/.claude/skills/devto-post
ln -s "$(pwd)/skills/skills/gemini-voices" ~/.claude/skills/gemini-voices
ln -s "$(pwd)/skills/skills/sound-design" ~/.claude/skills/sound-design
```

(or `cp -R` instead of `ln -s` if you'd rather have an independent copy).

## Compatibility

Built and tested with Claude Code. The skill folders follow the standard `SKILL.md` layout,
so they may work with other agents that support the same convention, but that hasn't been
tested here.

## Repo layout

```
skills/
├── .claude-plugin/marketplace.json   # one plugin per skill (bump its version on every change)
├── skills/
│   └── <skill>/
│       ├── SKILL.md                  # what the agent reads
│       ├── references/               # longer docs loaded on demand
│       ├── scripts/                  # helpers the skill runs
│       └── assets/                   # templates, sounds, images
├── .github/workflows/validate.yml    # claude plugin validate --strict
├── CHANGELOG.md
├── CONTRIBUTING.md
└── README.md
```

Current skills: `devto-post`, `gemini-voices`, `repo-glowup`, `sound-design`.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for adding or changing a skill, and
[CHANGELOG.md](CHANGELOG.md) for what's shipped.

## Maintaining

- When a skill changes, bump that plugin's `version` in `.claude-plugin/marketplace.json` —
  installed copies only update when the version is bumped.
- Run `claude plugin validate --strict .` before pushing — CI runs the same check.

## License

MIT — see [LICENSE](LICENSE).
