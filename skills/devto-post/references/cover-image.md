# Cover images

## The rule

**Every cover is composed. Never use dev.to's AI image generator — not as a fallback, not
for "just this one".**

The rule comes from the skill author's own feedback, after a Tauri migration post whose first
cover was a generic AI illustration of a crate and a cube: *"try leveraging existing
technology icon/logo for next skill calls, do not generate a generic ai image, try harder
next time."*

The reasoning holds up on its own:

- **Recognition.** A reader scrolling a feed identifies the Electron atom and the Tauri mark
  instantly. They cannot identify a generic glowing cube as anything.
- **Legibility.** Vector text rendered by `rsvg-convert` is exact at any size. Image models
  garble lettering — a requested Node.js hexagon once came out reading **"noje"**.
- **Reproducibility.** The same command regenerates or tweaks the cover. An AI generation is a
  dice roll you cannot re-roll identically.
- **Honesty.** The article is about two specific technologies. The cover should show them.

## The tool

`python3 "<skill-dir>/scripts/make-cover.py"` builds a 1000x420 cover. Three layouts, which
between them cover every post — that is what makes "always composed" a rule you can actually
keep:

```bash
# Two technologies — before/after, migration, comparison
python3 "<skill-dir>/scripts/make-cover.py" compare \
    --left si:electron --left-label ELECTRON --left-value "289 MB" \
    --right si:tauri   --right-label TAURI   --right-value "15 MB" \
    --middle "18.9x SMALLER" \
    --subtitle "Migrating a macOS menu-bar app from Electron to Tauri 2" \
    --out cover.png

# One technology — a feature, a release, a how-to
python3 "<skill-dir>/scripts/make-cover.py" single \
    --logo si:nodedotjs \
    --headline "NODE.JS SEA" --kicker "--build-sea" \
    --subtitle "One flag instead of five manual steps" \
    --out cover.png

# No technology to show — career pieces, opinion, retrospectives
python3 "<skill-dir>/scripts/make-cover.py" text \
    --kicker "Field notes" \
    --headline "Two years of shipping | a side project alone" \
    --subtitle "What I would tell myself at commit one" \
    --out cover.png
```

`--accent` sets the highlight colour (default `#FFC131`); use the subject technology's brand
colour. `--no-disc` turns off the circular clip. In the `text` layout, `|` splits the headline
across two lines (two maximum — it errors on three).

Pick the layout by what the post is about, not by how much effort each takes:

| Post | Layout |
|---|---|
| Migration, comparison, before/after | `compare` |
| One technology — a feature, release, how-to | `single` |
| No technology — career, opinion, retrospective | `text` |

The numbers in `--left-value` / `--right-value` are the hook. Put the article's single best
measured figure there — it is what makes someone stop scrolling.

## Where logos come from

**Simple Icons is the default, and it covers nearly everything.** Over 3000 official brand
marks, single-path SVGs, served in the brand's own colour:

```
si:tauri              → https://cdn.simpleicons.org/tauri
si:electron:FFFFFF    → forced white
```

Verified working slugs include `tauri`, `electron`, `rust`, `nodedotjs`, `python`, `php`,
`react`, `docker`, `typescript`. Slugs are lowercase, punctuation stripped, and dots spelled
out — Node.js is `nodedotjs`, not `node.js`. Check <https://simpleicons.org> when unsure.

Fallbacks, in order:

1. `gh:<org>` — the GitHub org avatar (`gh:tauri-apps`). Good for projects Simple Icons lacks.
   Note these are raster and usually have a solid background, so keep `--disc` on.
2. The project's own site — `https://www.electronjs.org/assets/img/logo.svg` works, for example.
3. A local file path.

Guessed asset paths inside a project's repo are a waste of time — `tauri-apps/tauri/dev/app-icon.png`
and several similar guesses all 404'd. Go to Simple Icons first.

## Always look at the result

Read the PNG back before uploading. The script cannot tell you that a slug resolved to the
wrong company's logo, or that a long `--subtitle` ran past the edge. One `Read` of the file
costs nothing and catches both.

## Uploading it to dev.to

Do **not** use the `🍌 Generate Image` button. Use the file input behind `Upload Cover Image`
(or `Change`, when a cover is already set):

```
find(query: "cover image file input")      → a ref for the <input type="file">
file_upload(ref: <that ref>, paths: ["/abs/path/cover.png"])
```

Do not *click* the file input — that opens a native picker you cannot interact with.

Changing the cover on an already-published article is fine and takes effect immediately: open
`<article-url>/edit`, upload, then `Save changes` (which keeps it published — it is not a
re-publish). This is also how you get real logos into a LinkedIn link-preview card, since
LinkedIn reads the article's cover.

## The AI generator

Don't. There is a layout for every case, including posts with no logo at all.

It is documented in the browser playbook only so that nobody rediscovers the `🍌 Generate Image`
button and assumes it is the intended path. The one thing worth remembering about it is why the
rule exists: asked for a Node.js logo, it produced a hexagon reading **"noje"**, and that was
invisible until the post was already live.
