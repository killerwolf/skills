# Browser / Chrome extension

An extension has two audiences that a library doesn't: the store's reviewers, who can
reject it, and non-technical users, who read the listing and the permission prompt and
decide whether this thing is trustworthy. Both are addressed with words rather than
code, which is why the README and the listing carry so much weight here.

## manifest.json — mind the source vs. the build output

Frameworks like WXT and Plasmo don't ship a hand-written `manifest.json` — they
generate one at build time from the framework config, into a build directory
(`.output/chrome-mv3/manifest.json` for WXT, `build/chrome-mv3-prod/manifest.json`
for Plasmo). `scripts/audit.py` tells the two apart automatically and says so in its
output; if it reports the manifest as "generated", every field below is edited at its
actual source instead of the file the audit found:

- **WXT**: the `manifest` object in `wxt.config.ts` (`defineConfig({ manifest: {...} })`).
- **Plasmo**: the relevant `package.json` fields, or `manifest.json` at the project
  root if the project uses one as an override — Plasmo merges it in rather than
  replacing it.
- **A plain unbundled extension**: `manifest.json` itself, wherever it sits in the
  source tree — this is the only case where editing the found file is correct.

Never hand-edit a manifest inside a build/output directory — the next build silently
overwrites it, and whatever was fixed there quietly reverts.

| Field | Constraint worth knowing |
| --- | --- |
| `name` | Max 75 chars. This is the store title. |
| `short_name` | ~12 chars; used where space is tight, e.g. under the icon. |
| `description` | **Max 132 characters.** Hard limit — a longer one fails validation at upload. It's also the line under your name in store search results, so make it a sentence about what the user gets, not a feature list. |
| `version` | 1–4 dot-separated integers, each 0–65535, no leading zeros. `1.0.0-beta` is rejected. |
| `icons` | 16, 32, 48 and 128. The 128 is required for the store and is what people see everywhere. |
| `homepage_url` | Point it at the repo or the project page. |
| `manifest_version` | Must be 3. MV2 can no longer be published. |
| `permissions` / `host_permissions` | Request the minimum. Every extra one widens the install-time warning and slows review. |

## The README needs two sections a library doesn't

**Permissions, justified.** A table of every permission and one plain sentence on why
it's needed. Users read the scary install prompt and go looking for an explanation; if
they don't find one, they don't install. Reviewers ask the same question.

```markdown
| Permission | Why |
| --- | --- |
| `activeTab` | Reads the current page only when you click the toolbar icon. |
| `storage` | Saves your settings locally. Nothing is sent anywhere. |
```

**Privacy.** Say plainly what data is collected and what leaves the machine — even if
the answer is "nothing ever leaves your browser", *especially* then, since that's a
selling point. If the extension handles any user data, the store requires a privacy
policy URL in the dashboard, so the page has to exist anyway.

## Store listing assets

These live in the developer dashboard, not the repo — but generate them into
`store-assets/` so they're versioned and reproducible, and list them in the final report
as an upload step:

- **Screenshots**: 1280×800 or 640×400, 24-bit PNG (no alpha) or JPEG. At least one,
  up to five. These do more selling than any other asset. Show the extension mid-task,
  not an empty popup.
- **Small promo tile**: 440×280. Required for the listing.
- **Marquee promo tile**: 1400×560. Only needed if you want to be eligible for
  featuring. (The old 920×680 large tile is retired.)
- **Store icon**: 128×128.

`scripts/make_card.py` can produce the promo tiles — but the store requires *exact*
pixel dimensions, and the script renders at 2× by default, so pass `--scale 1`:

```bash
python3 <skill-dir>/scripts/make_card.py --title "Name" --tagline "..." \
  --width 440 --height 280 --scale 1 --out store-assets/promo-small.png
```

It cannot produce the screenshots; those need the real UI.

## CI

Even without publishing automation, a workflow that zips the extension on every tag and
attaches it to the GitHub Release is worth having: it gives people a way to install the
exact reviewed build, and it proves the tree actually packages. See
`assets/workflows/extension-package.yml`.

`npx web-ext lint` catches manifest problems early. It's Mozilla's tool, so a few of its
warnings are Firefox-specific, but the manifest validation applies to both stores.

## Badges

Once published, the store badges are the credibility signal — version, user count and
rating, all of which come straight from the listing:

```html
<img src="https://img.shields.io/chrome-web-store/v/EXTENSION_ID">
<img src="https://img.shields.io/chrome-web-store/users/EXTENSION_ID">
<img src="https://img.shields.io/chrome-web-store/stars/EXTENSION_ID">
```

The ID is the long string in the listing URL. For a Firefox add-on the equivalents are
`amo/v`, `amo/users` and `amo/stars` with the add-on slug. If the extension isn't
published yet, skip these rather than committing dead badges — an unpublished extension
should lead with a screenshot and "load unpacked" install instructions instead.

## Landing page

Worth raising explicitly for an extension: the store listing is thin real estate for
a pitch — a title, 132 characters, a few screenshots — and it's Google's or Mozilla's
page, not yours, so it can't carry a badge row, a GIF-sized demo, or a link back to
the repo above the fold. A simple hosted site fixes that and gives the project a
memorable URL to put in the store listing's homepage field. Ask for the hosting choice
instead of assuming GitHub Pages. See `references/landing-page.md`; use
`assets/workflows/gh-pages.yml` only when GitHub Pages is selected.

## Unpublished extensions

Plenty of extensions never go to the store. They still deserve the rest of the
playbook, plus a clear "Install from source" section: download or clone,
`chrome://extensions`, enable Developer mode, Load unpacked, select the folder. Say
which folder — the repo root and the build output are frequently not the same, and
that's the single most common reason someone gives up.
