#!/usr/bin/env bash
# ============================================================================
# progress.sh — peek at how far each AI student has gotten, mid-run.
#
#   bash .claude/harness/progress.sh            # snapshot of every persona
#   bash .claude/harness/progress.sh sofia      # just one
#   watch -n 30 bash .claude/harness/progress.sh # refresh every 30s (CLI only)
#
# Reads what the running subagents have already written to runs/<id>/ — chiefly
# journal.md, which the brief requires them to append to after EVERY item, so it
# grows in real time even while a persona is still working. Nothing here talks to
# the agents; it just reads files on disk, so it's safe to run anytime.
#
# WHY THIS EXISTS / THE SUBAGENT CAVEAT
#   While a subagent runs, the parent session is blocked and can't surface its
#   internal progress. But file writes land immediately, so this script (run from
#   another shell, or by the orchestrator session between dispatches) is how you
#   see live progress. In a single web session, prefer per-week dispatch (see
#   .claude/students/orchestrate-students.md) so control returns between weeks.
# ============================================================================
set -uo pipefail

RUNS_DIR="${RUNS_DIR:-runs}"
ALL=(priya marcus sofia kenji aisha david)
if [ "$#" -gt 0 ]; then IDS=("$@"); else IDS=("${ALL[@]}"); fi

[ -d "$RUNS_DIR" ] || { echo "No '$RUNS_DIR/' yet — nothing has started."; exit 0; }

now=$(date +%s)
printf '%-8s %-6s %-22s %-9s %-7s %s\n' "STUDENT" "ITEMS" "LAST ENTRY" "REPORTS" "FRESH" "STATUS"
printf '%-8s %-6s %-22s %-9s %-7s %s\n' "-------" "-----" "----------" "-------" "-----" "------"

for id in "${IDS[@]}"; do
  dir="$RUNS_DIR/$id"
  if [ ! -d "$dir" ]; then
    printf '%-8s %-6s %-22s %-9s %-7s %s\n' "$id" "-" "-" "0/3" "-" "not started"
    continue
  fi

  journal="$dir/journal.md"
  items=0; last="(no journal yet)"; fresh="-"
  if [ -f "$journal" ]; then
    # journal entries start with the schema header "[Week N · <item>]"
    items=$(grep -cE '^\[Week' "$journal" 2>/dev/null || echo 0)
    last=$(grep -E '^\[Week' "$journal" 2>/dev/null | tail -1 | sed 's/^\[//; s/\]$//' | cut -c1-22)
    [ -z "$last" ] && last="(writing…)"
    mt=$(stat -c %Y "$journal" 2>/dev/null || stat -f %m "$journal" 2>/dev/null || echo "$now")
    age=$(( (now - mt) / 60 ))
    fresh="${age}m"
  fi

  # project reports: count the three required report_week*.md and flag short ones
  reports=0; short=0
  if compgen -G "$dir/project/report_week*.md" >/dev/null 2>&1; then
    for r in "$dir"/project/report_week*.md; do
      reports=$((reports + 1))
      w=$(wc -w < "$r" 2>/dev/null || echo 0)
      [ "$w" -lt 1800 ] && short=$((short + 1))
    done
  fi
  rep="${reports}/3"; [ "$short" -gt 0 ] && rep="${rep}!"   # ! = at least one under ~1,800 words

  # status heuristic: done if report.md exists AND 3 full reports; stalled if journal idle >15m
  status="in progress"
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
