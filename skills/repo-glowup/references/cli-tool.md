# CLI tool

A CLI is evaluated by running it, so the job of the README is to get someone from
reading to running in one paste. Everything below serves that.

## Lead with the no-install run

`npx your-tool` (or `uvx`, `pipx run`, `go run`) as the *first* thing in the install
section, before the global install. Trying a CLI without committing to a global install
removes the main reason people bounce.

```markdown
## Install

Run it without installing:

    npx your-tool ./some-file

Or install it globally:

    npm install -g your-tool
```

## package.json specifics

```json
{
  "bin": { "your-tool": "./bin/cli.js" },
  "files": ["bin", "dist"],
  "engines": { "node": ">=18" }
}
```

The entry file needs `#!/usr/bin/env node` on line one and the executable bit set in
git — npm sets the mode on install, but a missing bit breaks every contributor running
it locally:

```bash
git update-index --chmod=+x bin/cli.js
```

## Put `--help` in the README

A fenced block containing the real `--help` output is the fastest way for a reader to
tell whether the tool does what they need. The risk is drift, so generate it rather than
pasting once — a small script that runs the CLI and rewrites the block between two
marker comments, run in CI with a "docs are stale" check, keeps it honest.

Make sure the tool actually behaves like a CLI while you're there:

- `--version` and `--help` both work and exit `0`
- non-zero exit codes on failure, with the error on stderr
- a `--json` output mode if the output is structured, so people can pipe it
- honours `NO_COLOR`, and detects a non-TTY before emitting colour or spinners
- reads stdin when piped, where that makes sense

## A terminal recording beats a screenshot

For a CLI, the demo asset is a recording. [vhs](https://github.com/charmbracelet/vhs)
is the one to reach for: the recording is defined by a `.tape` script you commit, so it
can be regenerated when the output changes rather than becoming a stale artefact.

```
# demo.tape
Output demo.gif
Set FontSize 18
Set Width 1000
Type "npx your-tool ./example"
Enter
Sleep 4s
```

`vhs demo.tape` produces the GIF. Commit both the tape and the GIF, reference the GIF
by absolute raw URL. asciinema works too but embeds as a link rather than an inline
image on GitHub.

## Badges

npm version, monthly downloads, CI, licence. Downloads matter more for a CLI than for a
library — it's the closest thing to a review count that a terminal tool has.
