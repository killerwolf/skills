#!/usr/bin/env bash
# Set a GitHub repo's description, homepage and topics — the fields GitHub's own
# search runs on, and the ones most often left empty.
#
# Shows the current values first and asks before writing, because these are public
# and overwriting a considered description with a generated one is a real cost.
#
# Usage:
#   repo_meta.sh --description "..." [--homepage "..."] [--topics "a,b,c"] [--yes]
#
# Topics are normalised to GitHub's rules: lowercase, alphanumeric plus hyphens,
# max 50 chars each, max 20 total. Invalid characters become hyphens rather than
# being silently dropped, so you can see what happened and fix it.

set -euo pipefail

DESCRIPTION="" HOMEPAGE="" TOPICS="" ASSUME_YES=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --description) DESCRIPTION="$2"; shift 2 ;;
    --homepage)    HOMEPAGE="$2";    shift 2 ;;
    --topics)      TOPICS="$2";      shift 2 ;;
    --yes|-y)      ASSUME_YES=1;     shift ;;
    -h|--help)     awk 'NR>1 && /^#/ {sub(/^# ?/,""); print; next} NR>1 {exit}' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

command -v gh >/dev/null 2>&1 || { echo "gh CLI not installed — see https://cli.github.com" >&2; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "gh is not authenticated. Run: gh auth login" >&2; exit 1; }

echo "Current listing:"
gh repo view --json nameWithOwner,description,homepageUrl,repositoryTopics \
  --template '  repo:        {{.nameWithOwner}}
  description: {{if .description}}{{.description}}{{else}}(empty){{end}}
  homepage:    {{if .homepageUrl}}{{.homepageUrl}}{{else}}(empty){{end}}
  topics:      {{if .repositoryTopics}}{{range .repositoryTopics}}{{.name}} {{end}}{{else}}(none){{end}}
'

ARGS=()
[[ -n "$DESCRIPTION" ]] && ARGS+=(--description "$DESCRIPTION")
[[ -n "$HOMEPAGE" ]] && ARGS+=(--homepage "$HOMEPAGE")

NORMALISED=()
if [[ -n "$TOPICS" ]]; then
  IFS=',' read -ra RAW <<< "$TOPICS"
  for t in "${RAW[@]}"; do
    clean=$(echo "$t" \
      | tr '[:upper:]' '[:lower:]' \
      | tr -c 'a-z0-9-' '-' \
      | sed -E 's/-+/-/g; s/^-//; s/-$//' \
      | cut -c1-50)
    [[ -n "$clean" ]] && NORMALISED+=("$clean")
  done
  if [[ ${#NORMALISED[@]} -gt 20 ]]; then
    echo "note: GitHub allows 20 topics; keeping the first 20." >&2
    NORMALISED=("${NORMALISED[@]:0:20}")
  fi
  if [[ ${#NORMALISED[@]} -gt 0 ]]; then
    for t in "${NORMALISED[@]}"; do ARGS+=(--add-topic "$t"); done
  fi
fi

if [[ ${#ARGS[@]} -eq 0 ]]; then
  echo "Nothing to change. Pass --description, --homepage or --topics."
  exit 0
fi

echo
echo "About to set:"
[[ -n "$DESCRIPTION" ]] && echo "  description: $DESCRIPTION"
[[ -n "$HOMEPAGE" ]] && echo "  homepage:    $HOMEPAGE"
[[ ${#NORMALISED[@]} -gt 0 ]] && echo "  add topics:  ${NORMALISED[*]}"

if [[ $ASSUME_YES -eq 0 ]]; then
  echo
  read -r -p "Apply to the repo above? [y/N] " reply
  [[ "$reply" =~ ^[Yy]$ ]] || { echo "Aborted."; exit 0; }
fi

gh repo edit "${ARGS[@]}"
echo "Done. Topics only ever get added here — remove any stale ones with:"
echo "  gh repo edit --remove-topic <topic>"
