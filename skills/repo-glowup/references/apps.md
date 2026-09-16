# Apps — desktop, web, and everything else that isn't a package

An app has no registry listing to lean on. There is no npm page doing half the
explaining, no `npm install` line that proves the thing is real. The repo *is* the
product page, which raises the stakes on the README, the screenshot and the release.

## Desktop apps (Electron, Tauri)

**The release is the product.** If a stranger cannot get a running app in two clicks,
nothing else on the page matters.

- Link the latest release prominently, near the top: a "Download for macOS / Windows /
  Linux" row beats a paragraph explaining how to clone and build.
- Badges: latest release version and total download count
  (`img.shields.io/github/v/release/<slug>` and `github/downloads/<slug>/total`).
  Downloads are the credibility number for an app the way npm downloads are for a CLI.
- The release workflow should build and attach the actual installers (`.dmg`, `.exe`,
  `.AppImage`). A release with only source zips reads as unfinished.
- **Say what happens on first launch if the app isn't signed.** An unsigned macOS build
  shows "damaged and can't be opened", which most people read as malware rather than as
  an unpaid $99 developer account. One sentence and a right-click-Open instruction saves
  every one of those users. The same applies to the SmartScreen warning on Windows.
- Screenshots do the entire selling job here. Show the app doing its actual work, in a
  real window, with real content — not an empty state.

## Web apps and sites

**The deployed URL is the product.** The link at the top of the README, and in the
repo's homepage field, is the highest-value thing on the page.

- Deploy it somewhere, even if it's a toy. A live link converts an order of magnitude
  better than a repo someone has to run locally. GitHub Pages is a free option for a
  static build with no server component — see `references/landing-page.md` for the
  workflow.
- The site needs its own head metadata — title, description, canonical, OG and Twitter
  cards with an absolute `og:image`. See `readme-anatomy.md`. Without it, every share of
  the URL renders as bare grey text.
- A full favicon set (`favicon.ico`, a 192px PNG, an apple-touch-icon) and a
  `theme-color`. Cheap, and their absence is conspicuous.
- Screenshot or GIF in the README anyway — people evaluate from GitHub before they
  click through.
- If it's self-hostable, a one-click deploy button and a documented `.env` example.

## Personal projects, experiments, scripts

Not everything needs the full treatment, and pretending otherwise produces a README
that oversells a weekend experiment. But two things are worth doing on *any* repo that
is public, because they cost minutes and compound:

1. **A first sentence that says what it is and whether it works.** "An experiment in X.
   Works, but rough" is a perfectly good README opener and far better than an empty
   page. Say the status honestly — abandoned, experimental, maintained.
2. **The GitHub description and topics.** Without them the repo is unfindable, including
   by the author in two years.

If the project name is still the scaffolding default (`my-app`, `wxt-react-starter`,
`hello-world`), fix that before anything else. It's the loudest possible signal that
nobody has looked at this since `create-whatever` ran, and it silently discounts
everything else on the page.
