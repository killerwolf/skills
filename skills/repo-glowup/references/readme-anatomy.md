# README anatomy

The README is the product page. Someone arrives from a search result or a link with a
specific question — *can this do the thing I need, and how much will it cost me to find
out* — and leaves within a minute either way. Structure the page so the answer arrives
before their patience runs out.

## The order that works

1. **Title with the icon inline.** A small logo beside the H1 costs nothing and reads
   as a project someone cares about.
2. **One sentence of what it does.** Directly under the title, no heading. This exact
   sentence gets reused as the npm description, the GitHub description, the og:description
   and the search snippet, so it has to survive alone with no context. Say what the thing
   *is* and what you *get back* from it.
3. **Badge row**, centred. Four or five, each answering a real question.
4. **A picture of it working** — GIF for anything interactive, screenshot otherwise,
   terminal recording for a CLI. This is the highest-value element on the page and the
   one most often missing. It converts "I think I understand" into "I understand".
5. **Links row**: live demo · playground (JSFiddle/StackBlitz/CodeSandbox) · docs.
6. **Features**, as bullets with numbers in them.
7. **"Is this the right tool?"** — see below.
8. **Install**, including a no-install path if one exists (CDN, `npx`, store link).
9. **Quick start** — the shortest complete runnable example. Not a tour, the one
   snippet someone can paste.
10. **API / options reference.**
11. **Contributing, licence, links.**

## The section that earns the most trust

A "Is this the right tool?" section, placed early, with an explicit **Yes, if…** and
**No, if…**:

```markdown
**Yes, if** you need <the precise job> and want <the precise output>.

**No, if** you need <the adjacent job this does not do>. <Named alternative> is
built for that.
```

Naming the tool you are *not* is counter-intuitive and it works. It disqualifies the
wrong reader in ten seconds instead of after an hour of their frustration turning into
an issue on your tracker, and it signals to the right reader that the claims elsewhere
on the page have been thought about. Where the project produces structured output, a
small table mapping *what you get* → *where it tends to go* does the same job.

## Writing rules

**Numbers, not adjectives.** "3.6 kB gzipped" instead of "lightweight". "Zero
dependencies" instead of "minimal". "Works in every browser released since 2020"
instead of "modern". Adjectives are free, so readers correctly discount them; numbers
are checkable, so they carry weight. Never write a number you have not measured.

**Absolute image URLs.** Relative paths break the moment the README is rendered
anywhere except GitHub — npm, package aggregators, social previews. Use
`https://raw.githubusercontent.com/<owner>/<repo>/main/<path>` for every image.

**Show the failure mode.** If there's a gotcha every user hits — a UMD global that
nests differently from the ESM export, a permission that must be granted first — put it
in the quick start, not in an issue thread six months later.

**Keep their voice.** If the existing README has a joke or an unusual framing that
works, keep it. The target is *their project, taken seriously*, not a page that reads
as generated.

## Metadata for a docs, demo, or landing site

If the project has a site — docs, demo, or a dedicated landing page, see
`references/landing-page.md` — it needs its own head metadata; the README does not
cover it. `og:image` must be an absolute URL or the preview silently fails everywhere:

```html
<title>Project Name — what it does in a few words</title>
<meta name="description" content="One sentence. Same one as the README opener." />
<link rel="canonical" href="https://example.com/project/" />

<meta property="og:type" content="website" />
<meta property="og:site_name" content="Project Name" />
<meta property="og:title" content="Project Name — what it does" />
<meta property="og:description" content="One sentence." />
<meta property="og:url" content="https://example.com/project/" />
<meta property="og:image" content="https://example.com/project/social-preview.jpg" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:image:alt" content="Describe the image for a screen reader." />

<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Project Name — what it does" />
<meta name="twitter:description" content="One sentence." />
<meta name="twitter:image" content="https://example.com/project/social-preview.jpg" />
```

Two different images are in play and they are easy to confuse: the **site** OG image
(1200×630, lives with the site, referenced by absolute URL) and the **GitHub repo**
social preview (1280×640, uploaded through repo Settings, cannot be set by API).
