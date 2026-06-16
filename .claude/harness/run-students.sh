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
#   JOURNAL_ONLY=1 bash .claude/harness/run-students.sh sofia   # cheap single run:
#     ONE persona, journal-only (skips the 3 project reports + acceptance gate),
#     journal flushed to disk per item. The path for "run one, grab the journal,
#     hand it to a repo-fixing session." This is the budget-safe mode.
#
# PREREQUISITES (see .claude/students/README-ai-students.md)
#   - Run from the repo root, inside an isolated environment / container.
#   - Playwright MCP server configured & reachable (`claude mcp list`).
#   - .claude/settings.json merged with .claude/students/settings.students.json.
#   - R (and Python if any persona uses the Python track) installed.
# ============================================================================
set -uo pipefail

# Stop cleanly: a plain `pkill -f run-students.sh` kills this wrapper but orphans the
# child `claude -p` processes (they reparent to PID 1 and keep burning tokens). This
# trap forwards a stop to the whole process group so the children die with the wrapper.
# To stop from outside, signal the wrapper (kill <pid>) rather than pkill-ing the name,
# or kill the children directly: pkill -f 'claude -p'.
trap 'echo; echo ">> stop received — terminating persona processes…"; kill 0 2>/dev/null; exit 130' INT TERM

# Resolve this script's own directory so aggregate.R is found no matter where
# the harness lives or where you invoke it from (runs/ and logs/ stay relative
# to your CWD — invoke from the repo root).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---- config (override via env) ---------------------------------------------
MODEL="${MODEL:-sonnet}"                       # sonnet | opus | haiku | full id
PERMISSION_MODE="${PERMISSION_MODE:-acceptEdits}"  # acceptEdits (supervised-ish)
                                               #  | dontAsk (headless, auto-deny extras)
                                               #  | bypassPermissions (container only!)
OUTPUT_FORMAT="${OUTPUT_FORMAT:-text}"          # text (default) | json | stream-json
                                               #  Deliverables are FILES under runs/<id>/,
                                               #  so stdout format is irrelevant — 'text'
                                               #  is the safe default. NOTE: stream-json
                                               #  with `claude -p` REQUIRES --verbose or
                                               #  it dies at launch; we add it below if you
                                               #  opt into stream-json.
PARALLEL="${PARALLEL:-1}"                       # 1 = personas run concurrently (default); 0 = series
MAX_JOBS="${MAX_JOBS:-3}"                       # cap on concurrent personas when PARALLEL=1
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

# Warm the shared environment ONCE before fanning out. Otherwise each persona's
# SessionStart hook would try to install R/packages/Chromium concurrently, racing
# the same R library. prepare-env.sh is flock-guarded + idempotent, so this is a
# fast no-op if the env is already prepared. Skip with SKIP_PREPARE=1.
if [ "${SKIP_PREPARE:-0}" != "1" ]; then
  echo ">> warming shared environment (one-time prepare-env.sh)…"
  bash "$SCRIPT_DIR/prepare-env.sh" || echo "!! prepare-env.sh reported issues — continuing anyway"
  echo
fi

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

  local prompt
  if [ "${JOURNAL_ONLY:-0}" = "1" ]; then
    # Journal-focused run: the cheapest reliable path to a usable student-experience
    # log. SKIPS the three 1,800+ word project reports and the acceptance gate — the
    # largest token sink and the phase where full runs stall — because the JOURNAL is
    # the deliverable handed to the repo-fixing session. The journal is flushed to disk
    # after every item, so a stopped or stalled run still yields usable results.
    prompt="Use the student-${id} subagent to take SYSEN 5470 per its brief \
(.claude/agents/_shared/student-brief.md), inhabiting the persona's skill ceilings \
honestly — fumble where a real student like you would. Do Orientation and all three \
weeks of labs: ACTUALLY run each example.R/example.py and record the real printed \
Learning Check answer (or the verbatim error and how you recovered), do the sketch \
prompts, and browse the interactive labs top-to-bottom. THE JOURNAL IS THE ONLY \
REQUIRED DELIVERABLE: after EVERY single item, IMMEDIATELY append its entry to \
runs/${id}/journal.md ON DISK using the brief's journal schema, BEFORE starting the \
next item — never hold journal content in memory, so the journal survives an early \
stop. Do NOT write the three project/report_weekN_caseNN.md reports and do NOT run the \
acceptance gate; skip those project deliverables entirely for this run. Write \
scores.json when you finish. Print only the path to runs/${id}/journal.md when done."
  else
    prompt="Use the student-${id} subagent to take SYSEN 5470 in full, exactly per \
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
  fi

  # NOTE on flags:
  #  -p / --print           : non-interactive headless run
  #  --permission-mode      : see config above; 'dontAsk' is the reliable headless
  #                           choice (auto-denies anything not allow-listed instead
  #                           of blocking). 'bypassPermissions' skips all prompts —
  #                           container-only, refuses to run as root.
  #  In -p mode, 3 consecutive / 20 total classifier blocks abort the session, so a
  #  failed run usually means a missing allow-rule or a too-broad action — check the log.
  #  stream-json + --print requires --verbose, else claude exits immediately — add it.
  local fmt_args=(--output-format "$OUTPUT_FORMAT")
  [ "$OUTPUT_FORMAT" = "stream-json" ] && fmt_args+=(--verbose)

  if claude -p "$prompt" \
        --model "$MODEL" \
        --permission-mode "$PERMISSION_MODE" \
        "${fmt_args[@]}" \
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
