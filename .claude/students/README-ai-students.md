# SYSEN 5470 — AI Student Walkthrough (Claude Code)

Send hypothetical AI "students" through the live course, have them run the real code,
do the homeworks/project on a network they choose, and report their experience — so you
can find where the course confuses, overloads, or loses people **before** a human cohort does.

This is the Claude Code implementation of the design handoff. It slots into the existing
`timothyfraser/netsci` repo conventions (R SessionStart hook, `code/01_…11_` folders,
tidyverse + base-pipe `CLAUDE.md`, Playwright MCP already configured).

## What's here

```
.claude/
  agents/                      ← MUST stay here (Claude Code only discovers subagents in .claude/agents/)
    _shared/student-brief.md   ← protocol + journal/report/scores schemas (read by all)
    student-priya.md           ← stellar coder, Python track (the ceiling)
    student-marcus.md          ← strong Python, new to R, shaky inference theory
    student-sofia.md           ← new coder, stats-anxious, R track (retention cliff)
    student-kenji.md           ← stats-strong, tidyverse-naive, demands rigor (R)
    student-aisha.md           ← fluent R, new to Python AND to graphs (Python track)
    student-david.md           ← rusty, time-poor manager (async promise stress test)
    _student-template.md       ← copy to add more personas
  harness/
    run-students.sh            ← headless loop: each persona → its subagent → runs/<id>/
    aggregate.R                ← builds the cross-persona matrix + summary
  students/                    ← docs & references (kept out of the student personas' way)
    README-ai-students.md      ← this file
    orchestrate-students.md    ← prompt to drive the cohort from a main CC session instead
    SETUP-AGENT-HANDOFF.md     ← original install handoff (historical)
    MERGE-ME.md                ← permission-merge notes (already applied)
    NETWORK-ALLOWLIST.md       ← custom network allowlist for cloud sessions
    settings.students.json     ← permissions reference (already merged into settings.json)
  harness/
    progress.sh                ← peek at how far each persona has gotten, mid-run
    prepare-env.sh             ← one-time, flock-guarded env prep (R, pkgs, Chromium)
```

> The whole AI-student system lives under `.claude/` on purpose — it's a hidden config
> dir the simulated student personas don't browse, so the evaluation scaffolding stays
> out of their way. Output still lands at the repo root under `runs/` and `logs/`.

Outputs land in `runs/<id>/` (`journal.md`, `report.md`, `scores.json`, `project/`) plus
`runs/_summary.md`, `runs/_matrix_friction.csv`, `runs/_matrix_clarity.csv`. The
`project/` folder holds the graded homework: **three separate `report_weekN_caseNN.md`
files (one per case study, one per week, 5-page / ~1,800+ words each)** alongside each
runnable `project_weekN_caseNN.R`/`.py`.

## Install (one time)

1. Files are already in place under `.claude/` (`agents/`, `harness/`, `students/`).
2. **Merge permissions.** Add the `allow` and `deny` entries from
   `.claude/settings.students.json` into your existing `.claude/settings.json`
   `permissions` block. The repo's current allow-list only has *read-only* Playwright
   tools; the students need `browser_navigate`, `browser_click`, `browser_type`, etc.,
   plus Python/file-write — without these, an unattended run stalls on prompts.
   Confirm the Playwright tool names match your installed server with `claude mcp list`.
3. Ensure Python is available (the Python-track personas use it). R is handled by the
   repo's `session-start.sh`.

## Run

**Option A — pilot one persona, supervised (do this first).** Validates that a persona
actually stays in character and runs the code, while you watch:
```
claude
> Use the student-sofia subagent to take SYSEN 5470 in full per its brief,
  run the real code, and write outputs to runs/sofia/.
```

**Option B — headless batch.** All six **in parallel** (default), then auto-aggregate:
```
bash .claude/harness/run-students.sh
# or a subset:
bash .claude/harness/run-students.sh sofia priya
```
Each persona is an independent process with its own `runs/<id>/` and log, so they run
concurrently. Key env vars: `MODEL` (default `sonnet`), `PERMISSION_MODE`
(`acceptEdits` default → `dontAsk` for headless → `bypassPermissions` for fully
unattended, **container only**), `OUTPUT_FORMAT` (default `text` — deliverables are
files, so stdout format is irrelevant; if you set `stream-json` the harness auto-adds
the `--verbose` that `claude -p` requires or it dies at launch), **`PARALLEL`** (`1`
default = run concurrently; `0` = series), **`MAX_JOBS`** (default `3` = how many
personas run at once when parallel — raise/lower for your box and token budget),
**`SKIP_PREPARE`** (`1` to skip the one-time env warm-up if you've already prepared).

`run-students.sh` **warms the environment once** (via `prepare-env.sh`) before fanning
out, so the personas don't each trigger a heavy install in parallel. You can also run it
yourself ahead of time:
```
bash .claude/harness/prepare-env.sh   # R + packages + Chromium, once (flock-guarded)
```

**Option C — orchestrated from a main session.** Paste `.claude/students/orchestrate-students.md` into a
main Claude Code session; it runs preflight, dispatches all six, aggregates, and writes
a synthesis (`runs/_registrar-notes.md`).

Then read `runs/_summary.md`. A friction row red across *many* personas = a course
problem (fix the lab); red for *one* = a fit problem for that learner type.

## Watch progress (while it runs unattended)

The headless batch already runs the **whole cohort start-to-finish on its own** — all
six personas, sequentially, no per-week prompting. The only catch is visibility: a
foreground run blocks the session and shows nothing until it's done. So **run it in the
background and poll the monitor.**

```
# kick off the full cohort, unattended, in the background:
PERMISSION_MODE=dontAsk bash .claude/harness/run-students.sh &

# then watch progress whenever — it keeps working on its own:
bash .claude/harness/progress.sh            # one-shot snapshot
bash .claude/harness/progress.sh --watch    # self-refresh every 30s
bash .claude/harness/progress.sh --watch 10 # every 10s
```

The dashboard shows, per persona: journal entries logged, the last entry (which
week/lab they're on), project reports done (`n/3`, `!` = one under ~1,800 words),
**LIVE** = whether that persona's `claude -p` process is actually running right now,
**FRESH** = minutes since `journal.md` last changed (a rising number = idle/stalled),
and a status (`DONE ✓` when `report.md` + three full-length reports exist). The LIVE
column means a session that **crashed at launch** shows `✗ likely failed (check log)`
rather than being indistinguishable from one that just started — always trust LIVE over
ITEMS when deciding if something died. A persona that's LIVE with 0 items shows
`⏳ env preparing (shared setup)` until the one-time `prepare-env.sh` marker exists, so
you can tell "still installing R/Chromium" apart from "stuck." It only reads files +
`ps`, so it's safe anytime.
Per-persona logs also stream to `logs/<id>-<stamp>.log` for the raw play-by-play
(`tail -f`).

**Stopping / restarting (two footguns):**
- Killing the wrapper (`pkill -f run-students.sh`) does **not** stop the personas — the
  child `claude -p` processes get reparented and keep running. Kill those directly:
  `pkill -f 'claude -p'` (or target one: `pkill -f 'student-sofia subagent'`).
- Backgrounded commands don't reliably inherit your `cd`. Start every launch/poll
  command with `cd /path/to/netsci` (or use absolute paths), or they'll run from the
  wrong directory and write `runs/` somewhere you won't find it.

`PERMISSION_MODE=dontAsk` is what keeps it unattended — it auto-denies anything not in
the allow-list instead of stopping to ask (so it never blocks waiting on you). Use it in
an isolated container; `bypassPermissions` also works but refuses to run as root.

**Driving this from one web session (phone):** tell the session to *start the run in the
background and report progress periodically* — e.g. *"Run the cohort unattended in the
background with `PERMISSION_MODE=dontAsk`, then run `progress.sh` every few minutes and
show me the dashboard until every persona says DONE."* The run keeps moving on its own;
the session just re-reads the on-disk progress and relays it. You never have to nudge it
forward.

> Why background matters: while a subagent (or a blocking foreground command) runs, the
> parent session is frozen and can't show you anything. Backgrounding the harness frees
> the session to read `runs/` and surface progress while the work continues. (The
> per-week dispatch in `orchestrate-students.md` is only needed if you deliberately want
> manual checkpoints — you don't, so skip it.)

## Honest caveats

- **Tokens.** Subagent-heavy / parallel runs can cost several times a single-thread
  session. Pilot one persona before launching all six.
- **Headless permission gotchas.** In `-p` mode, 3 consecutive or 20 total safety-blocks
  abort the run — a failed run usually means a missing allow-rule or a too-broad action;
  check `logs/`. `--dangerously-skip-permissions` can still prompt on first use and
  refuses to run as root; `--permission-mode dontAsk` is the cleaner headless choice.
  Run unattended batches in an isolated container.
- **Stats-aversion is performed, not felt.** The model knows the statistics, so Sofia's
  "struggle" is a simulation. Weight the *coding-friction* findings (authentic) above the
  *stats-anxiety* findings, and treat the latter as directional.
- **Sketches are simulated** — you get a judgment about whether sketching *would* help,
  not the real hand-drawing experience.
- **The project report is a simulation artifact, not a submission.** Your AI-use policy
  forbids AI-written report prose; the agent writes report-shaped text only to surface
  the project *experience*. Don't reuse it.
- **Run each persona 2–3× if you can.** Single runs are noisy; stable findings are the
  ones that repeat. AI personas are cheap pre-testing, not a substitute for real students.
