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
# marker written by prepare-env.sh when the heavy one-time setup is complete; lets us
# tell "stuck in env setup" apart from "actually doing coursework".
MARKER="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." 2>/dev/null && pwd)/.harness-env-ready"

# ---- args: optional --watch [interval], optional persona list ---------------
WATCH=0; INTERVAL=30
if [ "${1:-}" = "--watch" ] || [ "${1:-}" = "-w" ]; then
  WATCH=1; shift
  if [[ "${1:-}" =~ ^[0-9]+$ ]]; then INTERVAL="$1"; shift; fi
fi
if [ "$#" -gt 0 ]; then IDS=("$@"); else IDS=("${ALL[@]}"); fi

# is this persona's headless session actually running right now? Matches the
# "student-<id> subagent" text the harness puts in the `claude -p` prompt, so a
# crashed/absent session is distinguishable from one that merely just started.
is_alive() {
  ps -eo args 2>/dev/null | grep -F "student-${1} subagent" | grep -vq "grep"
}

render() {
  if [ ! -d "$RUNS_DIR" ]; then echo "No '$RUNS_DIR/' yet — nothing has started."; return; fi
  local now; now=$(date +%s)
  local fmt='%-8s %-6s %-20s %-9s %-5s %-6s %s\n'
  # shellcheck disable=SC2059
  printf "$fmt" "STUDENT" "ITEMS" "LAST ENTRY" "REPORTS" "LIVE" "FRESH" "STATUS"
  printf "$fmt" "-------" "-----" "----------" "-------" "----" "-----" "------"

  for id in "${IDS[@]}"; do
    local dir="$RUNS_DIR/$id" alive="no"
    is_alive "$id" && alive="yes"

    if [ ! -d "$dir" ]; then
      if [ "$alive" = "yes" ]; then
        local s0="starting…"; [ -f "$MARKER" ] || s0="⏳ env preparing (shared setup)"
        printf "$fmt" "$id" "0" "-" "0/3" "yes" "-" "$s0"
      else
        printf "$fmt" "$id" "-" "-" "0/3" "-" "-" "not started"
      fi
      continue
    fi

    local journal="$dir/journal.md" items=0 last="(no journal yet)" fresh="-"
    if [ -f "$journal" ]; then
      items=$(grep -cE '^\[Week' "$journal" 2>/dev/null || echo 0)
      last=$(grep -E '^\[Week' "$journal" 2>/dev/null | tail -1 | sed 's/^\[//; s/\]$//' | cut -c1-20)
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

    # status: done > under-spec > crashed/absent > exited-early > stalled > working
    local status="in progress"
    if [ -f "$dir/report.md" ] && [ "$reports" -ge 3 ] && [ "$short" -eq 0 ]; then
      status="DONE ✓"
    elif [ -f "$dir/report.md" ]; then
      status="⚠ report.md but project under-spec"
    elif [ "$items" -eq 0 ] && [ "$alive" = "no" ]; then
      status="✗ not running, no progress — likely failed at launch (check log)"
    elif [ "$items" -eq 0 ] && [ "$alive" = "yes" ]; then
      if [ -f "$MARKER" ]; then status="starting…"; else status="⏳ env preparing (shared setup)"; fi
    elif [ "$alive" = "no" ]; then
      status="✗ exited early — no report (check log)"
    elif [ "$fresh" != "-" ] && [ "${fresh%m}" -gt 15 ]; then
      status="⚠ idle ${fresh} — maybe stalled"
    fi

    printf "$fmt" "$id" "$items" "$last" "$rep" "$alive" "$fresh" "$status"
  done

  echo
  echo "ITEMS = journal entries logged | REPORTS n/3 (! = one under ~1,800 words)"
  echo "LIVE  = a 'claude -p ... student-<id>' process is running right now"
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
