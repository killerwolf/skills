---
name: devto-post
description: End-to-end publishing pipeline for a developer's technical writing — turns a raw idea into a finished dev.to article in the author's voice, with a cover built from real technology logos and the right tags, waits while the author publishes it by hand, then drafts the matching LinkedIn promo and schedules it once the author approves. Use this whenever the user wants to write up something technical, publish a dev.to article, blog about a project they built or updated, turn a finding or a debugging session into a post, or promote an article on LinkedIn — including loose openers like "I want to write about X", "let's make a post out of this", or "can you write this up?". Also use it when the user asks to update or re-publish an existing article.
---

# dev.to + LinkedIn publishing pipeline

## Before you start: load the author profile

The author's details live outside this skill, so plugin updates never overwrite them:

- `~/.config/devto-post/profile.md` — name, dev.to username, timezone, posting slots,
  publishing language, tag vocabulary, what the articles are for, and an optional reference
  article. Everything below that says "the profile" means this file.
- `~/.config/devto-post/voice.md` — optional: the author's own style guide. Without it, use
  `references/voice.md`.

Read them with `cat` — a read-only shell command, so it works from any project without a
permission prompt.

**No profile yet? Run first-time setup before anything else:**

1. Ask the author for their dev.to username, their timezone (an IANA name such as
   `Europe/Berlin`), their publishing language, 5-10 tags they write under and, optionally,
   what their articles are for. Posting slots default to 12:00 and 18:00; ask whether those
   suit their readers.
2. Check the username: `https://dev.to/api/users/by_username?url=<username>` returns the
   account (take the display name from its `name` field) or a 404 if there is no such user.
3. Write `~/.config/devto-post/profile.md` from `references/profile.template.md`, then show
   the author what you wrote and where it lives.
4. If they have published articles (`https://dev.to/api/articles?username=<username>`), offer
   to draft `~/.config/devto-post/voice.md` from their two or three best ones, following the
   sections of `references/voice.md`, and to record the best one as the reference article.

Throughout, `${CLAUDE_SKILL_DIR}` is this skill's directory; the reference files write it as
`<skill-dir>`. (If that path shows up as a literal variable instead of a real path, use the
directory this SKILL.md was loaded from.)

## The shape of a run

Three acts, and the ordering is not negotiable:

1. **You prepare the article** — research, draft, cover image, tags. No scheduling on dev.to.
2. **The author publishes it themselves, immediately.** You wait, without burning turns.
3. **You write the LinkedIn promo** and, once the author approves it, schedule it for the next
   good slot.

Only the LinkedIn post gets scheduled. The article goes out by hand, live, as soon as the
author has read it.

The waiting in act 2 isn't just politeness — it's structural. dev.to rewrites the article's URL
when it publishes: a draft sits at `.../my-title-364j-temp-slug-1499615` and becomes
`.../my-title-1efl`, with an unpredictable suffix. A LinkedIn post written before publication
would carry a dead link. So the promo can only be written once the article is actually live.

---

## Act 1 — the article

### Sharpen the idea into an angle

An idea is "Node 26 SEA stuff". An angle is "the build went from 5 manual steps to 1, and the
flag isn't on LTS yet". Before writing anything, work out:

- What's the single interesting claim? If you can't name it, the post isn't ready — ask the
  author what surprised them about the thing, or go research until something surprises you.
- What does the reader do differently after reading it?
- Is there a before/after? The strongest posts almost always have one, because it makes the
  value legible in five seconds.

Ask the author only if the idea is genuinely ambiguous. A draft they can redirect beats three
clarifying questions.

### Research and verify — do not skip this

What makes these posts land is **first-hand verification**: a finding nobody else has written
down, backed by evidence. One post worked because it showed that a flag everyone was blogging
about wasn't on the current Node.js LTS yet — proved by installing that version and pasting the
real error. A post that only restates documentation isn't worth the author's name on it.

Your training data has a cutoff and the topic is probably newer than it. Assume you are out
of date.

- **Web search first**, for anything version-, release-, or date-sensitive. Then read the
  primary source (official docs, release notes, the maintainer's own blog post) rather than
  aggregator articles, which are frequently wrong about exactly the details worth writing about.
- **Run the thing.** If the post claims a command behaves a certain way, execute it and paste
  the real output. If it claims a feature is missing somewhere, install that version and show
  the actual error. This is where the article's credibility comes from, and it is also how
  you catch your own wrong assumptions before the author publishes them under their name.
- **Note the contradictions.** When blog posts say X and the primary source says Y, that gap
  *is* the article. Say so explicitly and show your evidence.
- Anything you couldn't verify: either cut it, or mark it clearly as unverified in the draft
  and flag it to the author. Never let an unchecked claim slide into a published post.

### Write it in the author's voice

Follow the voice file you loaded — the author's own, or `references/voice.md` — for tone,
structure, title patterns, and length targets. If the profile names a reference article, read
it: it's the author's own model of what "right" looks like.

Write in the profile's publishing language — always, regardless of what language the author
uses with you.

### Load it into dev.to

Read `references/browser-playbook.md` for the exact mechanics. The single most important
point, which will silently waste your time if you ignore it: **fill the fields with
`form_input` and element refs from `read_page`, never with coordinate clicks.** The dev.to
editor's internal viewport doesn't match screenshot coordinates, so coordinate clicks land in
empty space and type nothing, with no error.

### Cover image

**Build it from the real technology logos. Do not reach for dev.to's AI "Generate Image"
button.** This is the default for every post that names a technology — which is nearly all of
them.

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/make-cover.py" compare \
    --left si:electron --left-label ELECTRON --left-value "289 MB" \
    --right si:tauri   --right-label TAURI   --right-value "15 MB" \
    --middle "18.9x SMALLER" --subtitle "…" --out cover.png
```

`si:<slug>` pulls the official mark from Simple Icons (3000+ brands, brand-coloured, vector).
Layouts: `compare` for before/after, `single` for one technology, `text` for posts with no logo.
Read `references/cover-image.md` before your first cover — it has the layouts, the logo-source
fallbacks, and the upload mechanics.

Put the article's best measured number on the cover. "289 MB → 15 MB" is what stops the scroll.

Then **read the PNG back** to confirm every logo resolved and no text overran, and upload it
through the `Upload Cover Image` file input — never by clicking the file input itself.

There is a `text` layout for posts with no technology to show, so this holds for **every**
post. Never use dev.to's `🍌 Generate Image` button.

### Tags

Four maximum, from the profile's tag vocabulary. Prefer one or two big-reach tags plus one or
two specific ones: the broad tag gets impressions, the narrow tag gets the readers who care.

### Save the draft and hand it over

Save the draft — **don't touch Advanced Options or set any publish date.** Scheduling on dev.to
would defeat the point: the author wants the article live as soon as they're happy with it.

Saving redirects to a preview URL that starts with `https://dev.to/<username>/`. If that
username isn't the one in the profile, stop here: Chrome is logged in to a different dev.to
account, or the profile is wrong. Ask the author which is right and fix it before going on —
otherwise act 2 would watch the wrong account.

Then tell the author it's ready to publish, and say plainly what's set: title, tags, and
anything you couldn't verify. Then start waiting, in the same turn.

---

## Act 2 — wait for the author to publish

If the Bash tool accepts `run_in_background` and the shell can reach dev.to, start the bundled
watcher in the background:

```
Bash(command: "bash '${CLAUDE_SKILL_DIR}/scripts/wait-for-publish.sh' <username>", run_in_background: true)
```

with `<username>` the dev.to username from the profile. It captures a baseline from the public
dev.to API, polls every 30s, and exits the moment a new *published* article appears — printing
`PUBLISHED_URL=…` and `PUBLISHED_TITLE=…`. Because it exits on the event, you get exactly one
completion notification and act 3 resumes on its own. Saved drafts don't appear in that API,
so a draft can't trigger it by accident.

If the Bash tool has no `run_in_background` option, or the shell can't reach dev.to (sandboxed
environments), follow `references/waiting.md` instead — it covers that case and a manual
fallback.

Use the background Bash tool for this rather than `Monitor` — you want a single notification
when a condition becomes true, which is precisely what a backgrounded `until`-style script is
for. Never poll with foreground `sleep`; it blocks the session for no reason.

While it runs, stay available. The author may want to keep working on something else, and the
notification will find you regardless of what you're doing. If they go quiet, don't nag.

The watcher gives up after two hours. If it times out, just ask whether the author still wants
the LinkedIn post — don't silently drop the thread.

---

## Act 3 — the LinkedIn promo, approved then scheduled

The URL comes from the watcher's `PUBLISHED_URL` output. Don't reconstruct a slug by hand and
never reuse a draft URL.

### Write it

In the profile's publishing language. Concise — three short paragraphs, roughly 100 words,
then the link, then hashtags. It's a trailer, not the article.

1. What the author built or updated, in one sentence a non-specialist can follow.
2. The interesting finding — the part that shows the author investigated rather than
   summarized. This is the paragraph doing the personal-branding work, so give it the
   specifics.
3. One line pointing to the full write-up, then the URL on its own line.

Then 5-6 hashtags mixing reach and specificity: `#NodeJS #JavaScript #TypeScript #OpenSource
#WebDevelopment #SoftwareEngineering` is a good shape — adapt to the topic.

**Don't add a job-hunting ask to the post** — no "open to work", no "hire me", nothing
recruiting-flavored. Demonstrated competence recruits better than a request does, and the ask
would undercut the technical credibility the article just built; the work speaks for itself.
If the author explicitly asks for a call-to-action, add it — but don't volunteer one.

### Pick the slot

Target the next posting slot from the profile (12:00 or 18:00 unless it says otherwise) in the
author's timezone — lunch and commute peaks for readers in that timezone.

Require **at least an hour of lead time**. If the next slot is closer than that, take the one
after it. The lead time is what makes this safe: a scheduled LinkedIn post stays editable and
cancellable until it fires, so that gap is the author's second review window. Scheduling
something 10 minutes out removes that and is effectively posting.

### Get a yes, then schedule it

Paste the full post text and the exact slot into the chat, and ask the author to approve both.
Don't open LinkedIn's composer until they say yes; if they edit the text or pick another slot,
use theirs.

Then type the post, set the schedule and commit it (`references/browser-playbook.md` has the
modal's mechanics and its date-format trap). Confirm the date and time LinkedIn shows, and
remind the author they can edit or cancel the post from LinkedIn's "View all scheduled posts".

---

## Guardrails

- **Never click Publish on dev.to.** The author publishes their own articles. It's their
  byline, and the handoff is the last chance to catch a wrong claim.
- **Nothing goes to LinkedIn without the author's yes** on the exact text and slot, and never
  click plain "Post" — scheduling with real lead time keeps their chance to intervene.
- **Never publish a technical claim you didn't verify.** If it's unverified, say so out loud in
  the handoff.
- Articles and LinkedIn posts go out in the profile's publishing language, regardless of the
  language the author is using with you.
- If the author asks to *update* an existing published article, edit that article rather than
  creating a new one — a new post at a new URL splits the audience and loses the existing
  engagement.
