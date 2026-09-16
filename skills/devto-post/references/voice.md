# Default writing voice

Use this when the author has no `~/.config/devto-post/voice.md`. It was distilled from the
skill author's published dev.to articles, and the quoted lines and titles below come from
them — treat those as models of the style, never as facts about the person you're writing for.

## Register

Pragmatic practitioner writing to another practitioner. The author is showing what they found
and what it cost them, not lecturing from authority. Think experienced colleague explaining
something at a desk — direct, specific, a little wry, zero LinkedIn-influencer energy.

- **First person, past tense, real experience.** "I hadn't touched it in a while, so I went
  back to check if it still held up." Not "Developers often find that…".
- **Lead with the point.** No throat-clearing preamble about how important the topic is.
- **Say the annoying part out loud.** "That `postject` step was the annoying one — an external
  WASM-based tool you had to `npx` in, with a sentinel fuse string you copy-pasted from the
  docs and just trusted." Naming the friction is what makes readers trust the rest.
- **Admit what surprised you.** "Here's the part that surprised me. I assumed X had landed by
  now… and the flag simply isn't there." Being wrong in public, then showing the evidence, reads
  as credible rather than weak.
- **No hype, no emoji in article bodies, no exclamation marks.** The interesting thing is
  interesting on its own.

## Sentence-level texture

- Em-dashes for asides — use them freely; they suit the voice.
- Parentheticals for the caveat that would otherwise interrupt (like this).
- Occasional deliberate fragment for emphasis. "That's it."
- Backticks around every command, flag, filename, and package name.
- Contractions throughout: "isn't", "doesn't", "you're". Formal contraction-free prose reads
  stiff.

## Structure

Target **3-6 minute read** (roughly 700-1200 words). Long enough to be worth the click, short
enough to finish.

A shape that works well for a "thing changed / I investigated" post:

1. **Hook** — what the author built or looked at, and why they came back to it. 2-3 sentences.
2. **Quick recap** — what the technology actually is, for readers who don't know. Short; don't
   let this eat the post.
3. **The old way** — with real code, showing the friction.
4. **What changed** — the new approach, with real code, ideally much shorter than the old.
5. **Before/after table** — it makes the delta legible instantly.
6. **The catch** — caveats, what isn't true yet, what the other blog posts get wrong. This
   section is the credibility payload. Never skip it if there's a real caveat.
7. **Wrapping up** — what the author did to the repo, plus the link to it.
8. **References** — 2-4 links to primary sources.

Adapt freely — a cheatsheet-style post is organized by task instead, with a quick-reference
table at the end. Match the shape to the content, not to this list.

## Titles

The pattern is `[Specific thing]: [what you get]` or `[Thing] Just [changed]: [context]`.
Descriptive over clever, concrete nouns, often a colon or em-dash.

Examples from the articles this guide was distilled from:
- "The Production-Ready Miniconda Cheatsheet: From Homebrew to JupyterLab"
- "Chrome Extension Network Interception: The Modern Way to Scrape Instagram (and Beyond)"
- "Understanding Composer Version Constraints: A Comprehensive Guide"
- "Node.js SEA Just Got Way Simpler — Updating My node-sea Boilerplate for Node 26"

Avoid: clickbait ("You won't believe…"), listicle counts, and vague abstractions
("Thoughts on modern tooling").

## Code blocks

- Always language-tagged (```js, ```bash, ```json).
- Real code from the actual project, not invented illustrative snippets.
- Terminal output pasted verbatim when it proves a claim — including the error text. The
  `node: bad option: --build-sea` line did more work than a paragraph of explanation would have.
- Comment the steps inside longer blocks (`// 1. Generate the blob`).

## Things to avoid

- "In today's fast-paced world of software development…" and every cousin of it.
- Padding the word count with generic advice the reader already knows.
- Claiming something is "the best practice" without saying who says so.
- Restating docs. If the post could have been written without touching a terminal, rethink it.
- Presenting an unverified claim as fact — flag it or cut it.
