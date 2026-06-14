#!/usr/bin/env bash
# ============================================================================
# progress.sh — peek at how far each AI student has gotten, mid-run.
#
#   bash .claude/harness/progress.sh             # one-shot snapshot, all personas
#   bash .claude/harness/progress.sh sofia       # just one
#   bash .claude/harness/progress.sh --watch     # self-refresh every 30s
#   bash .claude/harness/progress.sh --watch 10  # self-refresh every 10s
#   bash .claude/harness/progress.sh --watch sofia priya   # watch a subset
#
# Reads what the running subagents have already written to runs/<id>/ — chiefly
# journal.md, which the brief requires them to append to after EVERY item, so it
# grows in real time even while a persona is still working. Nothing here talks to
# the agents; it just reads files on disk, so it's safe to run anytime.
#
# THE SUBAGENT CAVEAT / HOW TO GET LIVE VISIBILITY
#   While a subagent runs, the parent session is blocked and can't surface its
#   internal progress. The fix is to run the cohort UNATTENDED IN THE BACKGROUND
#   (bash .claude/harness/run-students.sh keeps moving through all personas on its
#   own), which leaves you free to run this script — or `--watch` it — for live
#   progress. No per-week prompting required.
# ============================================================================
set -uo pipefail

RUNS_DIR="${RUNS_DIR:-runs}"
ALL=(priya marcus sofia kenji aisha david)

# ---- args: optional --watch [interval], optional persona list ---------------
WATCH=0; INTERVAL=30
if [ "${1:-}" = "--watch" ] || [ "${1:-}" = "-w" ]; then
  WATCH=1; shift
  if [[ "${1:-}" =~ ^[0-9]+$ ]]; then INTERVAL="$1"; shift; fi
fi
if [ "$#" -gt 0 ]; then IDS=("$@"); else IDS=("${ALL[@]}"); fi

render() {
  if [ ! -d "$RUNS_DIR" ]; then echo "No '$RUNS_DIR/' yet — nothing has started."; return; fi
  local now; now=$(date +%s)
  printf '%-8s %-6s %-22s %-9s %-7s %s\n' "STUDENT" "ITEMS" "LAST ENTRY" "REPORTS" "FRESH" "STATUS"
  printf '%-8s %-6s %-22s %-9s %-7s %s\n' "-------" "-----" "----------" "-------" "-----" "------"

  for id in "${IDS[@]}"; do
    local dir="$RUNS_DIR/$id"
    if [ ! -d "$dir" ]; then
      printf '%-8s %-6s %-22s %-9s %-7s %s\n' "$id" "-" "-" "0/3" "-" "not started"; continue
    fi

    local journal="$dir/journal.md" items=0 last="(no journal yet)" fresh="-"
    if [ -f "$journal" ]; then
      items=$(grep -cE '^\[Week' "$journal" 2>/dev/null || echo 0)
      last=$(grep -E '^\[Week' "$journal" 2>/dev/null | tail -1 | sed 's/^\[//; s/\]$//' | cut -c1-22)
      [ -z "$last" ] && last="(writing…)"
      local mt; mt=$(stat -c %Y "$journal" 2>/dev/null || stat -f %m "$journal" 2>/dev/null || echo "$now")
      fresh="$(( (now - mt) / 60 ))m"
    fi

    local reports=0 short=0 r w
    if compgen -G "$dir/project/report_week*.md" >/dev/null 2>&1; then
      for r in "$dir"/project/report_week*.md; do
        reports=$((reports + 1)); w=$(wc -w < "$r" 2>/dev/null || echo 0)
        [ "$w" -lt 1800 ] && short=$((short + 1))
      done
    fi
    local rep="${reports}/3"; [ "$short" -gt 0 ] && rep="${rep}!"

    local status="in progress"
    if [ -f "$dir/report.md" ] && [ "$reports" -ge 3 ] && [ "$short" -eq 0 ]; then
      status="DONE ✓"
    elif [ -f "$dir/report.md" ] && { [ "$reports" -lt 3 ] || [ "$short" -gt 0 ]; }; then
      status="⚠ report.md but project under-spec"
    elif [ "$fresh" != "-" ] && [ "${fresh%m}" -gt 15 ]; then
      status="⚠ idle ${fresh} — maybe stalled"
    fi

    printf '%-8s %-6s %-22s %-9s %-7s %s\n' "$id" "$items" "$last" "$rep" "$fresh" "$status"
  done

  echo
  echo "ITEMS = journal entries logged | REPORTS n/3 (! = one under ~1,800 words)"
  echo "FRESH = minutes since journal last changed (rising = working; flat = idle)"
}

if [ "$WATCH" -eq 1 ]; then
  while true; do
    clear 2>/dev/null || printf '\033[2J\033[H'
    echo "=== AI-student progress  $(date '+%H:%M:%S')  (refresh ${INTERVAL}s, Ctrl-C to stop) ==="
    render
    sleep "$INTERVAL"
  done
else
  render
fi
