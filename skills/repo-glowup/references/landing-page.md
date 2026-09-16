# Landing page (GitHub Pages)

A landing page is optional and type-dependent — raise it in Phase 2 rather than
building it unasked. It earns its place when the project's pitch is visual and the
existing product page undersells it:

- **Skip it** for a typical npm library or a small CLI. The README already *is* the
  landing page, and a second page just splits the one audience that matters.
- **Worth it** for a browser extension, a desktop or web app, or any tool whose value
  is obvious once someone sees it working but not from a wall of markdown — a store
  listing has little room for a pitch, and a bare repo has none. Also worth it as a
  redirect target: `https://yourtool.dev` reads as more finished than a GitHub URL,
  even when it's the same GitHub Pages content behind it.

If there's nothing real to demo yet — no working screenshot, no GIF — that's a sign
the page is premature, not a reason to fake one. A thin landing page with a mockup
undermines trust the same way an inflated README does; better to ship it once there's
something true to show.

## What goes on it

One page is enough. In order:

1. **One clear promise**, as the H1 — the same sentence that opens the README, reused
   rather than reinvented so the two pages agree with each other.
2. **A primary call to action** — the store link, the install command, the download
   button. Whatever the single next action is, it should be the only button that
   stands out; a row of six equal-weight buttons asks the reader to make a decision
   they came here to avoid.
3. **A real screenshot or GIF**, full width, the thing actually running. This is the
   whole reason the page exists instead of just linking the README.
4. **Three or four features**, one line each. Not the full feature list — that's what
   the README is for.
5. **Footer**: GitHub link, licence, nothing else. No fake testimonials, no "as seen
   in" logos that aren't real, no invented user counts — see the honesty rules in
   `SKILL.md`; they apply here at least as much as in the README, because a page with
   its own domain reads as more authoritative and so is trusted more by default.

`assets/landing-page.html` is a working starting point with these sections already
built — a dark/light-aware single file, no build step, no JS. Copy it into the site
source directory (`docs/` by convention, see below) and fill in the `{{PLACEHOLDER}}`
tokens by hand: title, tagline, icon, CTA link and label, screenshot path, three
features, footer text, licence link. Delete the screenshot block entirely rather than
leave a placeholder image if there's nothing to show yet.

## Head metadata

The page needs its own OG/Twitter block — the README's metadata doesn't cover it, and
a missing or relative `og:image` means every share of the link renders as bare grey
text. The template already has the tags wired to `{{OG_IMAGE}}` and friends; see
`readme-anatomy.md`'s "Metadata for a docs, demo, or landing site" section for the full
block and the two-images-not-one gotcha (site `og:image` vs. the separate GitHub repo
social preview).

Generate the OG image with the same tool used for the repo social preview —
`scripts/make_card.py` already produces the right size for either:

```bash
python3 <skill-dir>/scripts/make_card.py \
  --title "Project Name" --tagline "One honest sentence." \
  --icon path/to/icon.png --fact "MIT" --fact "zero dependencies" \
  --width 1200 --height 630 --out docs/og-image.png
```

## Wiring it to GitHub Pages

`assets/workflows/gh-pages.yml` deploys via the modern Actions-based method (build →
`upload-pages-artifact` → `deploy-pages`) rather than pushing to a `gh-pages` branch —
no bot commits, no branch to keep in sync with main.

1. Copy the workflow to `.github/workflows/gh-pages.yml`.
2. Put the filled-in `landing-page.html` at `docs/index.html` (rename it), plus any
   image assets it references, all under `docs/`. That's the workflow's default
   `SOURCE_DIR` and also GitHub's own default Pages folder, so the two conventions
   line up without extra config.
3. **The one step that can't be automated**: in the repo's Settings → Pages →
   "Build and deployment" → Source, switch it to **GitHub Actions**. The workflow
   will run either way, but the deploy step fails until this is set once by hand.
   Put this in the final report's "Left for you" section with the direct
   `https://github.com/<owner>/<repo>/settings/pages` link.
4. Push to `main`. The workflow runs, and the deployment URL — normally
   `https://<owner>.github.io/<repo>/`, or the custom domain below — shows up in the
   Actions run summary and in Settings → Pages.

**If `docs/` is already the markdown documentation folder**, don't collide with it —
use `landing/` or `site/` instead, and change `SOURCE_DIR` in the workflow to match
(the audit script checks a few common folder names, including these, so it'll still
get picked up next time).

**Custom domain**: if the project has one, a `CNAME` file containing just the domain
goes inside the source folder (`docs/CNAME`, committed) — it's plain content as far
as the Actions deploy is concerned, so it survives every redeploy the same as any
other file. The domain's DNS still needs an `A`/`ALIAS`/`CNAME` record pointing at
GitHub Pages, which is on the user, not something this workflow can do.

**If the site needs a real build step** (a static-site generator, a bundler) rather
than being plain HTML, add a build job before the upload step and point
`SOURCE_DIR`/the upload path at the build output directory instead of the source —
the deploy half of the workflow doesn't change.

## Badges

Once the page is live, a "site" badge next to the others is a fair signal it's not a
dead link:

```html
<a href="https://<owner>.github.io/<repo>/">
  <img alt="site" src="https://img.shields.io/website?url=https%3A%2F%2F<owner>.github.io%2F<repo>%2F">
</a>
```
