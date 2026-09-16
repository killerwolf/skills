---
name: repo-glowup
description: >
  Audit and upgrade a project's discoverability and credibility — README, badges,
  package/extension metadata, social preview card, CI, CHANGELOG/CONTRIBUTING, and the
  GitHub listing (description, homepage, topics). Adapts to whatever the project turns
  out to be: npm library, browser extension, CLI tool, Python/Rust/Go package, or a
  plain repo. Use this whenever the user wants to polish or launch a project, make a
  repo "look pro" or "more discoverable", rewrite a README, prep an npm or Chrome Web
  Store listing, add badges or an OG/social-preview image, or asks to apply to one repo
  what was done to another. Reach for it even when the ask sounds narrow ("add some
  badges", "write me a better README") — the audit is one command and it surfaces the
  rest of what's missing.
---

# Repo glow-up

## Why this exists

A project gets judged in about thirty seconds. Someone lands on the GitHub page, the
npm page or the store listing and decides whether this is a serious, maintained thing
they can depend on — before reading a line of source. That judgement runs almost
entirely on surface signals: does the first sentence say what this actually does, do
the badges prove it builds and ships, does the link render a preview when pasted into
Slack, is there a licence, is there any sign that releases happen on purpose.

None of that is about the code being good. It's about the code being *legible to a
stranger who owes you no patience*. This skill walks that surface, reports what's
missing, and fixes the mechanical parts — while leaving the judgement calls (the
tagline, the keywords, what the project promises) to the human, because those need
taste and honesty rather than automation.

Throughout, `${CLAUDE_SKILL_DIR}` is this skill's directory; the reference files write it
as `<skill-dir>`. (If that path shows up as a literal variable instead of a real path, use
the directory this SKILL.md was loaded from.)

## Workflow

Four phases — **audit → agree the scope → apply → report**. Run the audit even when
the request sounds narrow, because it identifies the project type, and the project
type changes nearly everything downstream.

### Phase 1 — Audit

From inside the repo being polished:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/audit.py" --markdown
```

It detects the project type, lists what's present and what's missing, flags empty
metadata fields, and suggests a badge row built from the real package name, repo slug
and workflow filenames. Add `--json` if you want to read it programmatically.

The script is deliberately dumb about *quality* — it can see that a README exists and
that it has 400 words, not whether those words are any good. So after running it, read
the README yourself, and skim enough source to be able to describe what the project
does in one honest sentence. You cannot write a value proposition from a file listing.

### Phase 2 — Agree the scope

Show the user the gap list grouped by effort, and say which project type you detected
and what that implies. Then ask what's in scope. Some of these are opinionated changes
to *their* project's voice, and doing all of it uninvited is how a "glow-up" turns into
a revert.

A few things worth raising explicitly at this point, because they are the ones people
most often don't realise are missing or don't think to ask for:

- **The social preview image.** Every GitHub link they paste anywhere currently renders
  as grey text. See Phase 3.
- **The repo description and topics.** GitHub's own search runs on these. An empty
  description means the repo is close to unfindable.
- **A landing page**, if the audit shows none and the project type is visual — an
  extension, a desktop or web app, anything whose pitch lands better seen than read.
  Not every project wants one; it's a real scope addition (a new page, a CI workflow,
  a one-time Settings change), so ask rather than build it by default. See
  `references/landing-page.md`.

Default to working on a branch (`chore/discoverability` or similar) and grouping the
work into a few coherent commits — metadata, README, assets, CI — rather than one
sprawling commit. It reviews better and it lets the user drop one piece without losing
the rest.

### Phase 3 — Apply

Work through the core checklist below, then the type-specific reference file. Read the
reference for the detected type before writing anything type-specific:

| Detected type | Read this |
| --- | --- |
| `npm-library` | `references/npm-library.md` |
| `browser-extension` | `references/browser-extension.md` |
| `cli-tool` | `references/cli-tool.md` |
| `desktop-app`, `web-app`, `app` | `references/apps.md` |
| `python`, `rust`, `go`, `generic` | `references/other-ecosystems.md` |
| Any type, when touching the README | `references/readme-anatomy.md` |
| Any type, when a landing page is in scope | `references/landing-page.md` |

The audit prints its evidence for the type it picked. When that evidence reads as
hedged — "could be a library that never had its packaging finished" — resolve it by
looking at the repo rather than accepting the guess, because the two branches lead to
completely different work.

#### Core checklist (every project type)

**LICENCE.** No licence means "legally do not touch this" to any company. If it's
missing, ask which one rather than picking for them; MIT is the common default for
small tools but that's their call. Make sure the year and name are real.

**README.** The single highest-leverage artefact. `references/readme-anatomy.md` has
the structure that works and the writing rules that matter (numbers over adjectives,
absolute image URLs, naming the tool you are *not*).

**Badges.** The audit script suggests a row. Badges earn their place by answering a
question a stranger has — is it published, is it small, is it typed, does it build, can
I legally use it. A row of eight decorative badges reads as noise; four or five that
each answer something reads as competence.

**CONTRIBUTING.md and CHANGELOG.md.** Templates in `assets/`. The CHANGELOG matters
more than people expect: it's the fastest proof that a project is alive. Follow Keep a
Changelog, and write entries that say what changed *for the user*, not which files
moved.

**CI.** If there's no workflow at all, add one (`assets/workflows/`) — a green check on
every commit is a credibility signal, and the badge that comes with it is one of the
few that a reader actually trusts. If CI exists, check the badge in the README points
at the right workflow file.

**Landing page.** Optional — only when it was agreed in scope during Phase 2. The
audit's "Landing page (GitHub Pages)" row says whether one already exists (a workflow
that deploys Pages, a recognised source folder, or Pages already enabled on the repo
per the API). When adding one: `assets/landing-page.html` for the page,
`assets/workflows/gh-pages.yml` for the deploy, `references/landing-page.md` for the
full playbook including the one manual Settings step. Skip this for a plain npm
library or small CLI by default — see the reference for when it earns its place.

**GitHub listing — description, homepage, topics.** This is API-automatable, so do it:

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/repo_meta.sh" --description "..." --homepage "..." --topics "topic-a,topic-b"
```

The script shows the current values first, normalises topics to GitHub's rules
(lowercase, hyphens, ≤50 chars, ≤20 of them) and asks before writing. Topics are how
GitHub's own search and "explore" surfaces find a repo, so treat them as keywords with
intent — mix the obvious ones with the ones a person would actually type.

**Social preview image.** Generate a 1280×640 card:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/make_card.py" \
  --title "Project Name" \
  --tagline "One honest sentence about what it does." \
  --icon path/to/icon.png \
  --fact "zero dependencies" --fact "3.6 kB gzipped" --fact "MIT" \
  --out .github/assets/social-preview.png
```

It fills an HTML template and shoots it with headless Chrome. Pass `--template` with an
edited copy of `assets/social-card.html` when the project deserves something more
bespoke than the default layout — a screenshot of the tool in use next to the icon
beats an icon alone every time.

Uploading it is the one step that genuinely cannot be automated: GitHub only accepts a
social preview through the web UI. Hand the user the direct link
(`https://github.com/<owner>/<repo>/settings` → Social preview → Edit → Upload) and
say so plainly rather than pretending it's done.

If the project also has a docs, demo, or landing site, that site needs its own Open
Graph and Twitter card metadata pointing at an absolute image URL — a relative
`og:image` path silently fails everywhere it matters. `references/readme-anatomy.md`
has the meta block; `references/landing-page.md` covers building and deploying the
landing-page case specifically.

#### Rules that keep this honest

Do not invent facts to fill a template. No bundle size you haven't measured, no user
count, no "blazing fast", no feature that isn't implemented, no benchmark. Measure the
size (`npx bundlephobia` or the build output), read the source for the feature list. An
inflated README is worse than a thin one, because the first thing it teaches a reader
is that the project's claims can't be trusted.

Equally: don't delete the user's voice. If their README has a joke in it or an unusual
structure that works, keep it. The goal is a project that reads as *theirs, taken
seriously* — not one that reads as generated.

### Phase 4 — Report

Close with a short markdown report under three headings, and nothing else:

```markdown
## Changed
- ...

## Skipped (already in good shape)
- ...

## Left for you
- ...
```

"Left for you" is the important one. It's where the social preview upload goes, along
with anything needing credentials the user holds (npm trusted-publisher configuration,
store listing edits), and any judgement call you deliberately didn't make on their
behalf. Be specific — link the exact settings page, name the exact field.

## Applying this to several repos

If the user wants this across a batch of projects, do the audit for each one first and
present the combined gap list before touching anything. Repos vary more than people
remember, and the audit is cheap. Don't run the apply phase unattended across
repositories — the value-prop sentence is different every time, and that sentence is
most of the value.
