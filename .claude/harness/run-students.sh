#!/usr/bin/env bash
# ============================================================================
# run-students.sh — send AI student personas through SYSEN 5470 (headless)
#
# Runs each persona as a one-shot headless Claude Code session that delegates to
# the matching student-<id> subagent. Sequential by default (cheaper, easier to
# keep personas honest). Outputs land in runs/<id>/.
#
# USAGE
#   bash .claude/harness/run-students.sh              # all personas, sequential
#   bash .claude/harness/run-students.sh priya sofia  # just these two
#   PERMISSION_MODE=bypassPermissions bash .claude/harness/run-students.sh   # unattended
#
# PREREQUISITES (see .claude/students/README-ai-students.md)
#   - Run from the repo root, inside an isolated environment / container.
#   - Playwright MCP server configured & reachable (`claude mcp list`).
#   - .claude/settings.json merged with .claude/students/settings.students.json.
#   - R (and Python if any persona uses the Python track) installed.
# ============================================================================
set -uo pipefail

# Resolve this script's own directory so aggregate.R is found no matter where
# the harness lives or where you invoke it from (runs/ and logs/ stay relative
# to your CWD — invoke from the repo root).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---- config (override via env) ---------------------------------------------
MODEL="${MODEL:-sonnet}"                       # sonnet | opus | haiku | full id
PERMISSION_MODE="${PERMISSION_MODE:-acceptEdits}"  # acceptEdits (supervised-ish)
                                               #  | dontAsk (headless, auto-deny extras)
                                               #  | bypassPermissions (container only!)
OUTPUT_FORMAT="${OUTPUT_FORMAT:-stream-json}"  # stream-json | json | text
PARALLEL="${PARALLEL:-1}"                       # 1 = personas run concurrently (default); 0 = series
MAX_JOBS="${MAX_JOBS:-6}"                       # cap on concurrent personas when PARALLEL=1
ALL_PERSONAS=(priya marcus sofia kenji aisha david)

# ---- which personas this run -----------------------------------------------
if [ "$#" -gt 0 ]; then PERSONAS=("$@"); else PERSONAS=("${ALL_PERSONAS[@]}"); fi

mkdir -p runs logs
STAMP="$(date +%Y%m%d-%H%M%S)"

command -v claude >/dev/null 2>&1 || { echo "ERROR: 'claude' CLI not found on PATH."; exit 1; }

MODE=$([ "$PARALLEL" = "1" ] && echo "parallel (max $MAX_JOBS at once)" || echo "series")
echo "=== SYSEN 5470 AI student run $STAMP ==="
echo "model=$MODEL  permission-mode=$PERMISSION_MODE  mode=$MODE  personas=${PERSONAS[*]}"
echo "tip: background this run (append &) and watch with 'bash $SCRIPT_DIR/progress.sh --watch'."
echo

# run_one <id> — drive a single persona's headless session. Self-contained so it
# can be called sequentially or backgrounded for parallel runs.
run_one() {
  local id="$1"
  local agent_file=".claude/agents/student-${id}.md"
  if [ ! -f "$agent_file" ]; then
    echo "!! skipping '$id' — no $agent_file"; return 0
  fi

  mkdir -p "runs/${id}"
  local log="logs/${id}-${STAMP}.log"
  echo ">> $id : starting (log -> $log)"

  local prompt="Use the student-${id} subagent to take SYSEN 5470 in full, exactly per \
its brief (.claude/agents/_shared/student-brief.md). Inhabit the persona's skill \
ceilings honestly. Actually run the example.R/example.py scripts and record real \
outputs and errors. Produce ALL graded deliverables — in particular the project's \
THREE separate 5-page-minimum reports (~1,800+ words of text each, figures excluded), \
one per chosen case study, one per week, as project/report_weekN_caseNN.md; never \
combine them or emit a single short report. Read docs/assignments.html and \
docs/assignments/sample-report.md before drafting, and run the brief's acceptance gate \
(three report_week*.md, each >=~1,800 words) before finishing. Write journal.md, \
report.md, scores.json, and project/ into runs/${id}/. When finished, print only the \
path to runs/${id}/report.md."

  # NOTE on flags:
  #  -p / --print           : non-interactive headless run
  #  --permission-mode      : see config above; 'dontAsk' is the reliable headless
  #                           choice (auto-denies anything not allow-listed instead
  #                           of blocking). 'bypassPermissions' skips all prompts —
  #                           container-only, refuses to run as root.
  #  In -p mode, 3 consecutive / 20 total classifier blocks abort the session, so a
  #  failed run usually means a missing allow-rule or a too-broad action — check the log.
  if claude -p "$prompt" \
        --model "$MODEL" \
        --permission-mode "$PERMISSION_MODE" \
        --output-format "$OUTPUT_FORMAT" \
        > "$log" 2>&1; then
    echo ">> $id : done"
  else
    echo "!! $id : exited non-zero — inspect $log (likely a permission block or overrun)"
  fi
}

if [ "$PARALLEL" = "1" ]; then
  # Each persona is an independent process writing to its own runs/<id>/ and log,
  # so fan them out concurrently and wait for all to finish. MAX_JOBS caps how many
  # run at once (each persona is itself token- and CPU-heavy).
  for id in "${PERSONAS[@]}"; do
    run_one "$id" &
    # throttle: block once MAX_JOBS are already running
    while [ "$(jobs -rp | wc -l)" -ge "$MAX_JOBS" ]; do
      wait -n 2>/dev/null || sleep 2
    done
  done
  wait
else
  for id in "${PERSONAS[@]}"; do run_one "$id"; echo; done
fi

echo "=== all requested personas finished. Aggregating... ==="
if command -v Rscript >/dev/null 2>&1; then
  Rscript "$SCRIPT_DIR/aggregate.R" runs || echo "!! aggregate.R failed — run it manually."
else
  echo "Rscript not found; run 'Rscript .claude/harness/aggregate.R runs' yourself."
fi
echo "=== see runs/_summary.md and runs/_matrix_friction.csv ==="
