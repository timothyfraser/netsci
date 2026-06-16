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
#   BUNDLE=1 bash .claude/harness/run-students.sh sofia   # recommended single run:
#     ONE persona -> ONE markdown file (runs/<id>/journal.md) holding the per-item
#     journal AND the full text of the three project reports, flushed to disk as it
#     goes. The "run one, grab the bundle, hand it to a repo-fixing session" path.
#   JOURNAL_ONLY=1 bash .claude/harness/run-students.sh sofia   # cheapest fallback:
#     journal only, no project reports. Use when budget is very tight.
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
  if [ "${BUNDLE:-0}" = "1" ]; then
    # Bundled single-file run: ONE markdown file (runs/<id>/journal.md) that holds the
    # per-item journal AND the full text of the three project reports, INTERSPERSED in
    # the course's real weekly cadence (one project report per week, due each Monday —
    # NOT batched at the end). Two hard rules lead the prompt: (1) CONTAINMENT — all
    # output stays under runs/<id>/ and the rest of the repo is read-only, so a persona
    # can never scatter files into tracked course dirs (a cheating/academic-integrity
    # risk, since their output is a full term of student work); (2) JOURNAL-FIRST — the
    # journal is created first and flushed per item, never written compute-first at the
    # end, so an abrupt stop still leaves everything completed so far on disk.
    prompt="Use the student-${id} subagent to take SYSEN 5470 per its brief \
(.claude/agents/_shared/student-brief.md), inhabiting the persona's skill ceilings \
honestly — fumble where a real student like you would. \
TWO HARD RULES, obey above all else: \
(1) CONTAINMENT — every file you create or edit MUST live under runs/${id}/ and NOWHERE \
else. Your journal is runs/${id}/journal.md; project code, data, and figures go under \
runs/${id}/project/. NEVER write or edit anything outside runs/${id}/ — not the repo \
root, not code/, docs/, or .claude/. You MAY read and RUN the course's code/ scripts, \
but treat everything outside runs/${id}/ as strictly read-only. \
(2) JOURNAL-FIRST, INCREMENTALLY — create runs/${id}/journal.md as your VERY FIRST \
action, then append each item's entry to it ON DISK the moment you finish that item, \
BEFORE starting the next (append with Edit or a shell >> append). Do NOT do all the \
computation first and write the journal at the end, and never hold journal content in \
memory — the file must survive an abrupt stop with everything done so far already in it. \
NOW TAKE THE COURSE IN ITS REAL WEEKLY CADENCE — do NOT batch the project reports at the \
end. Three Monday-to-Monday weeks; every Monday 9am you submit that week's sketch, \
case-study + code Learning Checks, AND that week's ONE project case-study report. Up \
front pick 3 of the 11 case studies (one per week) and a project network (100+ nodes), \
then work WEEK BY WEEK. FOR EACH WEEK (1, then 2, then 3): (a) do that week's labs — \
ACTUALLY run each example.R/example.py and record the real printed Learning Check answer \
(or the verbatim error and how you recovered), do the week's sketch prompts, browse the \
interactive labs; append each item's entry to journal.md immediately using the brief's \
journal schema; then (b) write THAT WEEK'S project case-study report and append its FULL \
TEXT into the same journal.md under a '## Project Report — Week N · Case NN' heading \
BEFORE moving on to the next week. Each report follows the sample-report structure \
(Question / Network / Procedure / Results in prose / What this tells me and what it \
doesn't) — a substantial write-up in your own words (aim ~1,200-1,800 words; completeness \
over padding). Log the real deadline pressure of producing a report alongside that week's \
labs. Do NOT create separate report files and do NOT run the strict acceptance gate. \
Write runs/${id}/scores.json when finished. Print only the path to runs/${id}/journal.md \
when done."
  elif [ "${JOURNAL_ONLY:-0}" = "1" ]; then
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
