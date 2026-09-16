# Browser mechanics for dev.to and LinkedIn

Everything here was learned by doing it. The gotchas are marked — they cost real time to
discover and will silently waste yours if you skip them.

Last checked against dev.to and LinkedIn in September 2026. If a label or step below doesn't
match the page, trust the page and tell the author what changed.

## Before anything: reach the browser tools, then pick the right Chrome

`mcp__claude-in-chrome__*` drives the author's real Chrome, where they're already logged into
both sites. In some environments these tools are **deferred** — listed by name only, and
calling one directly fails until its schema is loaded. Load everything you need in **one**
`ToolSearch` call; one call per tool wastes a round trip each time:

```
ToolSearch(query: "select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__read_page,mcp__claude-in-chrome__form_input,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__browser_batch,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__tabs_close_mcp,mcp__claude-in-chrome__list_connected_browsers,mcp__claude-in-chrome__select_browser,mcp__claude-in-chrome__find,mcp__claude-in-chrome__file_upload,mcp__claude-in-chrome__javascript_tool")
```

The last three — `find`, `file_upload`, and `javascript_tool` — aren't in the base set but are
needed later: the cover-upload flow needs `find` and `file_upload`, and the LinkedIn
`Confirm`-button check (GOTCHA #7) needs `javascript_tool`.

If more than one Chrome is connected, the tools refuse to act until one is selected — list
them, ask the author which, then `select_browser` with that deviceId. If **no** browser is
connected, stop and tell the author rather than retrying — there is nothing to select from.

Then `tabs_context_mcp` (with `createIfEmpty: true`) before any other browser call, and
`tabs_create_mcp` for a fresh tab rather than hijacking one the author is using. Close tabs
you opened when you're done.

Batch sequences with `browser_batch` — a click, a type, and a screenshot in one round trip is
much faster than three calls.

---

## GOTCHA #1: never fill dev.to fields by clicking coordinates

The dev.to editor reports an internal viewport (~2326x1644) that doesn't match screenshot
coordinates (~1319x932). Coordinate clicks therefore land in empty space: the typing goes
nowhere, **no error is raised**, and the screenshot afterwards looks like nothing happened.

Do this instead:

```
read_page(filter: "interactive")   → gives refs like ref_73 "Post Title"
form_input(ref: <that ref>, value: "…")
```

Match elements by their accessible name, not by remembered ref numbers — refs are regenerated
on every `read_page` call and are not stable across page loads.

Names you'll want in the dev.to editor:

| Accessible name | What it is |
|---|---|
| `Post Title` | title textbox |
| `Add up to 4 tags...` | tags textbox |
| `Post Content` | markdown body textarea |
| `Upload Cover Image` / `Change` | cover file input — the default path |
| `🍌 Generate Image` | AI cover image — **not used**, see cover-image.md |
| `Advanced Post options` | opens the modal with scheduling |
| `Save` / `Save Draft` | saves without publishing |
| `Publish` | publishes, or schedules if a date is set |
| `Preview` / `Edit` | toggles rendered preview |

## Body content: no frontmatter

The default rich editor has **separate fields** for title and tags, so the body must not start
with a `---` frontmatter block — it would render as literal text. (Frontmatter only applies in
"basic markdown" mode, which the author isn't using.)

Markdown inside the body works normally: `##` headings, fenced code blocks, tables, links.

## Tags

Click the tags field, then type them comma-separated in one go, **with a trailing comma**:
`node, javascript, typescript, opensource, ` — each comma converts the preceding word into a
chip. Verify by zooming: chips render as `# node ×`. Four is the hard maximum; the UI shows
"Only 4 selections allowed" when you hit it.

## Cover image: upload the composed file (the default)

Covers are built from real technology logos with `scripts/make-cover.py`, not generated. See
`references/cover-image.md` for the why and the layouts. The upload mechanics:

```
find(query: "cover image file input")   → ref for the <input type="file">
file_upload(ref: <that ref>, paths: ["/abs/path/cover.png"])
```

**Never click the file input or the `Upload Cover Image` / `Change` label** — that opens a
native file picker that you cannot see or dismiss, and the editor is then stuck behind it.
`file_upload` writes straight to the input and the thumbnail updates within a few seconds.

To change the cover on an **already-published** article: go to `<article-url>/edit`, upload the
same way, then click `Save changes`. That button keeps the post published — it is not a
re-publish, and the URL does not change. Worth doing when the cover needs to carry real logos
into a LinkedIn preview card, which reads whatever the article's cover currently is.

## Cover image via "Generate Image" — do not use

Documented so nobody rediscovers the button and assumes it is the intended path. Every cover is
composed with `scripts/make-cover.py`; there is a `text` layout for posts with no logo, so this
button has no remaining use.

1. Click `🍌 Generate Image` → a modal opens with an "Image Description" textarea.
2. Click the textarea, type the prompt, click the modal's `Generate Image` submit button.
3. It takes roughly 30-60 seconds. A toast reads "AI image generated successfully!" and the
   thumbnail replaces the button row.

### GOTCHA #2: image models garble small text

A prompt asking for a Node.js logo produced a hexagon reading **"noje"**. Big headline text
renders fine; small lettering inside icons does not.

So write prompts that ask for **large text only** and explicitly exclude small lettering:

> Bold, high-contrast YouTube-thumbnail-style tech graphic, dark navy background. Large chunky
> bold white sans-serif text at the top reading "NODE.JS SEA" and smaller green text below it
> reading "--build-sea". **No logos, no brand marks, no small icons with text on them.** On the
> right, a glowing green cube-shaped package with a bold white arrow pointing into it from a
> scattered cluster of gray gears, laptops, and puzzle pieces. Vibrant green (#339933) and white
> accents, dramatic lighting, punchy flat vector illustration style, clean and legible.

That prompt shape — big title text, a simple before→after visual metaphor, a named accent
color, "no logos" — produced the image the author kept.

### GOTCHA #3: always zoom in to check the image

```
computer(action: "zoom", region: [<the thumbnail's box>])
```

Glitched lettering is invisible at thumbnail size and obvious once it's on the author's feed. If
the text is wrong, regenerate — mention what to avoid explicitly in the new prompt. Regenerating
replaces the current image, so there's no cleanup to do.

Composed covers need checking too, for different failure modes: a Simple Icons slug can resolve
to the wrong company's mark, and a long `--subtitle` can run past the canvas edge. `Read` the
PNG file directly before uploading — that catches both, and it is cheaper than a zoom.

## Advanced Options — not used in this workflow

`Advanced Options` (bottom bar) opens a modal with **Canonical URL**, **Schedule Publication**
(Date + Time), and **Series**.

Leave it alone. Articles go out by hand, immediately — only the LinkedIn post gets scheduled.
It's documented here just so nobody rediscovers it and assumes it should be used.

Worth knowing if it ever *is* needed: a date set here does nothing until the **Publish** button
is clicked (Save Draft won't arm it), and dev.to's date input follows the browser locale —
`jj/mm/aaaa` on a French-locale browser, the opposite convention from LinkedIn's scheduler
below.

## Saving a draft

`Save Draft` redirects to a preview URL carrying an "Unpublished Post" banner and a long
`?preview=…` token. That page is the read-back view; `Edit` in its banner returns to the editor.

### GOTCHA #4: the draft URL is not the published URL

Draft: `…/nodejs-sea-just-got-way-simpler-…-364j-temp-slug-1499615`
Published: `…/nodejs-sea-just-got-way-simpler-…-1efl`

The suffix changes on publish and isn't predictable, so any link written while drafting will be
dead.

Get the live URL from the **public JSON API** rather than scraping the profile page:

```
https://dev.to/api/articles?username=<username>&per_page=1
```

with `<username>` from the author profile. It returns only *published* articles, each with a
canonical `url`, `title`, `id`, and `published_at`. No auth needed. `<skill-dir>/scripts/wait-for-publish.sh`
and `references/waiting.md` are both built on this endpoint.

### GOTCHA #5: the sandbox shell may not reach dev.to

In a sandboxed environment (such as Cowork), the session's shell may run in a cloud container
behind an egress allowlist, and `curl https://dev.to/...` fails with `CONNECT tunnel failed,
response 403`. Use `WebFetch` for the API instead — it goes through a different path and works.
The browser tools are also unaffected, since they run in the author's Chrome, not in the
container. See `references/waiting.md` for how this affects act 2.

---

## LinkedIn composer

1. Go to `https://www.linkedin.com/feed/`.
2. Click **Start a post**. The first click sometimes only focuses the feed — if the modal
   doesn't appear, click again.
3. Click inside the "What do you want to talk about?" area, then type. Plain `computer` typing
   works fine here; unlike dev.to, coordinates are reliable in this modal.
4. Paste/type the article URL on its own line — LinkedIn fetches a preview card automatically
   after a moment, pulling the dev.to title and cover image. Confirm the card appears: it's
   most of the post's visual footprint in the feed.
5. Hashtags go at the end, space-separated, 5-6 of them.

To replace text you already typed: click into the box, `cmd+a`, `Delete`, then type the
replacement. `cmd+a` inside the composer selects only the composer's content.

## LinkedIn scheduling

The **clock icon** sits immediately left of the `Post` button and opens a "Schedule post" modal:

- A line confirming the interpreted slot: *"Fri, Aug 21, 11:30 AM Central European Summer Time,
  based on your location"* — read it back, it's the ground truth for what LinkedIn understood.
- **Date** field
- **Time** field
- `Back` / `Next` buttons, plus a **"View all scheduled posts →"** link for managing what's queued.

### GOTCHA #6: LinkedIn and dev.to use opposite date formats

LinkedIn's date field has shown **US format `M/D/YYYY`** (`8/21/2026`) and its time field
**12-hour with AM/PM** (`11:30 AM`) — in the same browser where dev.to's date input, which
follows the browser locale, showed French `jj/mm/aaaa`. Don't carry a format assumption from
one to the other — type the value, then read the confirmation line above the fields to check
it landed as intended.

`Next` advances to confirmation; the `Post` button then becomes the schedule action. A scheduled
post remains editable and cancellable from "View all scheduled posts" until it fires — which is
what makes scheduling with an hour or more of lead time safe in a way that posting immediately
is not.

### GOTCHA #7: the time field strips the space, and then refuses to validate

Typing `6:00 PM` into the Time field lands as `6:00PM` — the component eats the space. The
confirmation line above still reads "Posting at Fri, Sep 11, 6:00 PM", so it *looks* accepted,
but **`Confirm` silently greys out** and clicking it does nothing. `input.validity.valid` is
`true` the whole time, so HTML validation tells you nothing either.

Two ways through, in order of preference:

1. **Focus the field and pick from its dropdown.** Focusing (not clicking the clock icon, which
   is decorative) opens a list of 15-minute slots with the current value check-marked. Clicking
   the entry commits it through the component's own handler and enables `Confirm`.
2. **Set the value through React's native setter** when the dropdown doesn't cooperate:

   ```js
   const setter = Object.getOwnPropertyDescriptor(
     window.HTMLInputElement.prototype, 'value').set;
   setter.call(timeInput, '6:00 PM');
   timeInput.dispatchEvent(new Event('input', { bubbles: true }));
   ```

   Assigning `.value` directly does *not* work — React overrides the property, so its onChange
   never fires and its internal state stays stale.

Either way, check `Confirm`'s real state rather than trusting the screenshot: a disabled button
and an enabled one differ only in shade.

```js
[...document.querySelectorAll('button')].find(b => b.innerText.trim() === 'Confirm').disabled
```

**Never click plain `Post`**, and don't open the scheduler before the author has approved the
text and the slot.
