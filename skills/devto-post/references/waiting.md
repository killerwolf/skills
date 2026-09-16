# Act 2 — waiting for publication

The goal of this act is narrow: get the **real published URL** of the new article, without
blocking the session and without pestering the author. Everything here exists because the
draft URL is not the published URL (see GOTCHA #4 in `browser-playbook.md`).

## Step 0 — capture the baseline, before handing the draft over

Do this *before* you tell the author the draft is ready. You need to know what the newest
published article was, so a new one is unmistakable.

Use `WebFetch` — it works in every environment, including sandboxes whose shell has no
route to dev.to:

```
WebFetch(
  url: "https://dev.to/api/articles?username=<username>&per_page=1&_=<epoch-seconds>",
  prompt: "Return the id, title, url and published_at of the single article in this JSON array."
)
```

**The `&_=<epoch-seconds>` cache-buster is mandatory.** `WebFetch` caches responses per URL
for 15 minutes, so without a changing parameter every poll returns the same stale answer and
the watch never fires. Get the value with `date +%s`.

Write the baseline to a state file so a compacted context can recover it:

```bash
echo '{"baseline_id": <id>, "username": "<username>", "attempt": 0}' > /tmp/devto-watch-state.json
```

## Step 1 — pick the mechanism

Check, in this order. Don't assume — probe.

**Path A — background watcher (any environment whose Bash tool backgrounds, and whose shell
reaches dev.to).** Both conditions must hold:

1. Your `Bash` tool accepts a `run_in_background` parameter. Look at its actual schema —
   not every environment has one.
2. The shell can reach dev.to:
   ```bash
   curl -s --max-time 10 -o /dev/null -w "%{http_code}" \
     "https://dev.to/api/articles?username=<username>&per_page=1"
   ```
   `200` means yes. `000` with a `CONNECT tunnel failed` error means a sandbox's egress
   allowlist blocks it — that is the normal result in a sandboxed environment such as Cowork.

If both hold, use it. Go to **Path A** below.

**Path B — scheduled self check-ins.** For when the Bash tool has no background option, or
the shell can't reach dev.to. Requires a tool that delivers a delayed follow-up message back
into this same session. Go to **Path B** below.

**Path C — manual check-in.** Neither of the above is available. Go to **Path C** below.

---

## Path A — background watcher

```
Bash(command: "bash '<skill-dir>/scripts/wait-for-publish.sh' <username>", run_in_background: true)
```

`<username>` is the dev.to username from the author profile.

The script captures its own baseline, polls every 30s, and exits the moment a new
*published* article appears — printing `PUBLISHED_URL=…` and `PUBLISHED_TITLE=…`. Because it
exits on the event, you get exactly one completion notification and act 3 resumes on its own.

Use background `Bash` for this rather than `Monitor`: you want a single notification when a
condition becomes true, which is precisely what a backgrounded `until`-style script is for.
`Monitor` is for repeated events.

The script gives up after two hours (`exit 2`).

---

## Path B — scheduled self check-ins

The loop is: schedule a wake-up → on waking, poll once → new article? act 3 : schedule the
next wake-up.

**Schedule the first check-in in the same turn as the handover.** The mechanism is whatever
this environment offers for delivering a delayed follow-up message into this same session —
don't assume any particular one always exists. The example available in Cowork is
`mcp__claude-code-remote__send_later` (load it with `ToolSearch` first if it's deferred:
`select:mcp__claude-code-remote__send_later`):

```
mcp__claude-code-remote__send_later(
  delay_minutes: 10,
  initiation: "own_followup",
  name: "dev.to publish check",
  message: "dev.to publish check 1/12. Baseline article id <id> for <username>.
            Re-read /tmp/devto-watch-state.json, poll the dev.to API with a fresh
            cache-buster, and either continue to act 3 with the new URL or schedule
            check 2."
)
```

**On each wake-up:**

1. Read `/tmp/devto-watch-state.json` for the baseline id and attempt count. Trust the file
   over your recollection.
2. Poll once, with a fresh cache-buster:
   ```
   WebFetch(url: "https://dev.to/api/articles?username=<username>&per_page=1&_=<new-epoch>", …)
   ```
3. If the returned id differs from the baseline id, that is the new article. Take its `url`
   as `PUBLISHED_URL`, delete the state file, and go straight into act 3 — no need to ask
   the author anything first.
4. If it's unchanged, increment `attempt` in the state file and schedule the next check-in
   with `delay_minutes: 10`.
5. If a poll fails or returns something that isn't the expected JSON, treat it as unchanged
   and keep going. Never let a transient network blip look like a new article — that would
   fire act 3 with no URL.
6. At attempt 12 (two hours), stop scheduling. Ask the author whether they still want the
   LinkedIn post, and delete the state file.

Ten minutes is the right interval: `WebFetch`'s cache is 15 minutes but the cache-buster
sidesteps it, and shorter intervals just spend turns to save a few minutes on a step gated by
how fast the author reads.

**Keep each check-in cheap.** A wake-up where nothing changed should be one `WebFetch`, one
state-file write, one scheduled follow-up, and no message to the author. They do not need
twelve notifications telling them the article still isn't published.

---

## Path C — manual check-in

Tell the author plainly, in the handover message: *"Tell me once it's live and I'll write
the LinkedIn post."* Then stop.

When the author says it's published, poll the API once (with a cache-buster) to get the
canonical URL, and run act 3. Do not ask the author to paste the URL — the API has it, and a
hand-copied URL is a chance to get the suffix wrong.
