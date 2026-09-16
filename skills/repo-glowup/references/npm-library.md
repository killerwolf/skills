# npm library

## package.json metadata

`npm pkg fix` cleans up trivial problems first. Then fill these by hand, because they
are the fields npm's search and every aggregator index on:

| Field | Why it matters |
| --- | --- |
| `description` | The one line under the name on npm and in search results. Same sentence as the README opener. |
| `keywords` | npm search runs on these. Aim for 8–15: the obvious terms, the synonyms someone would actually type, and the problem words (`focal-point`, `crop-tool`, `zero-dependency`). |
| `repository` / `bugs` / `homepage` | Turns into the sidebar links on npm. A missing `repository` also costs you the provenance link. |
| `license` | An SPDX string, matching the LICENSE file. |
| `engines` | Set the range you actually test. Too narrow blocks installs, too wide is a lie. |
| `files` | Ship `dist` and whatever source the sourcemaps and types point at, nothing else. Check with `npm pack --dry-run`. |
| `exports` | Modern resolution. Get this wrong and both TypeScript and bundlers quietly fall back or fail. |
| `publishConfig.access` | Scoped packages default to restricted; public ones need `"access": "public"`. |

## Types

Shipping declarations moves a package from "usable" to "pleasant", and the npm types
badge shows it on the listing. The declarations need to be reachable through *both*
resolution modes:

```json
{
  "types": "./src/index.d.ts",
  "exports": {
    ".": {
      "types": "./src/index.d.ts",
      "import": "./dist/lib.esm.js",
      "require": "./dist/lib.cjs",
      "default": "./dist/lib.esm.js"
    }
  }
}
```

`types` must come first inside each condition block — resolution takes the first match,
so a `types` entry after `import` is dead. Verify the whole picture rather than assuming:

```bash
npx publint                      # packaging mistakes
npx @arethetypeswrong/cli --pack # types resolution under every mode
```

Hand-written `.d.ts` files drift from the implementation silently. A compile-time test
file that exercises the public surface, checked by `tsc --noEmit` in CI, is what stops
that.

## Release workflow with provenance

Publishing from CI with OIDC trusted publishing means no long-lived npm token exists to
leak, and npm shows a verified provenance badge on the listing. Set the trusted
publisher up on npmjs.com first (package → Settings → Trusted publisher → GitHub
Actions, naming the repo and the workflow filename), then use
`assets/workflows/npm-publish-oidc.yml`.

Three failure modes worth knowing before they cost an afternoon:

- **Do not set `registry-url` on `actions/setup-node`.** It writes an `_authToken` line
  into `.npmrc`; npm then treats auth as already configured, skips the OIDC exchange
  entirely and fails with a confusing `E404`. Put the registry in a checked-in `.npmrc`
  instead.
- **npm must be ≥ 11.5.1.** Node 22 bundles npm 10.x, so the workflow needs an explicit
  `npm install -g npm@latest` step.
- **A tag push bypasses your PR checks.** If CI only runs on pushes to `main` and PRs,
  nothing gates the tag — run the test suite inside the publish workflow too, or a red
  commit ships.

Cut the release by pushing a tag, and let the workflow create the GitHub Release with
`--generate-notes` after the publish succeeds, so a failed publish doesn't leave an
orphan release behind.

## Badges that earn their place

npm version, gzipped size (bundlephobia), types, CI status, licence. Size is the one
readers care about most for a browser library and the one they can't easily check
themselves.

## Install section

Give the no-install path as well as the npm one — a CDN `<script>` tag or an
`import` from esm.sh, plus a JSFiddle or StackBlitz link. Being able to try the library
without touching a terminal is the difference between an evaluation and a bookmark.
Pin an exact version in any example that a reader might copy into production.
