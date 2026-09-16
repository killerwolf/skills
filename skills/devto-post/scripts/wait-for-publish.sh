#!/usr/bin/env bash
# Block until a NEW article appears on a dev.to profile, then print its URL.
#
# Run this with Bash(run_in_background: true) right after handing the draft over for
# publication. It captures a baseline at startup, polls the public dev.to API, and exits as
# soon as a new published article shows up — which produces exactly one completion
# notification. The API only lists *published* articles, so a saved draft won't trip it.
#
# Usage: wait-for-publish.sh <username> [poll_seconds] [timeout_minutes]
#
# Output on success (stdout, last lines):
#   PUBLISHED_URL=https://dev.to/<username>/…
#   PUBLISHED_TITLE=…
#
# Exit codes: 0 published, 1 API unreachable at startup, 2 timed out, 64 usage.

if [ -z "${1:-}" ]; then
  echo "Usage: wait-for-publish.sh <username> [poll_seconds] [timeout_minutes]" >&2
  exit 64
fi

USERNAME="$1"
INTERVAL="${2:-30}"
TIMEOUT_MIN="${3:-120}"

API="https://dev.to/api/articles?username=${USERNAME}&per_page=1"

# Prints the newest published article as "id<TAB>url<TAB>title", or ERR on any failure.
# Never let a transient network blip look like a new article — that would fire the
# notification early and send the LinkedIn step off with no URL.
latest() {
  curl -s --max-time 20 "$API" 2>/dev/null | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    if not d:
        print('EMPTY')
    else:
        a = d[0]
        print('%s\t%s\t%s' % (a['id'], a['url'], a['title']))
except Exception:
    print('ERR')
" 2>/dev/null || echo ERR
}

baseline="$(latest)"
if [ "$baseline" = "ERR" ]; then
  echo "Could not reach the dev.to API to establish a baseline; aborting." >&2
  echo "If this is a sandboxed environment, its egress allowlist probably blocks dev.to." >&2
  echo "See references/waiting.md for a fallback that doesn't need shell access to dev.to." >&2
  exit 1
fi
baseline_id="$(printf '%s' "$baseline" | cut -f1)"
echo "Watching dev.to/${USERNAME} for a new published article (baseline id: ${baseline_id})."

deadline=$(( $(date +%s) + TIMEOUT_MIN * 60 ))

while :; do
  sleep "$INTERVAL"

  if [ "$(date +%s)" -ge "$deadline" ]; then
    echo "Timed out after ${TIMEOUT_MIN} minutes with no new article." >&2
    exit 2
  fi

  current="$(latest)"
  # Skip transient failures rather than treating them as a change.
  case "$current" in
    ERR|EMPTY) continue ;;
  esac

  current_id="$(printf '%s' "$current" | cut -f1)"
  [ "$current_id" = "$baseline_id" ] && continue

  url="$(printf '%s' "$current" | cut -f2)"
  title="$(printf '%s' "$current" | cut -f3)"
  echo "PUBLISHED_URL=${url}"
  echo "PUBLISHED_TITLE=${title}"
  exit 0
done
