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
  agents/
    _shared/student-brief.md   ← protocol + journal/report/scores schemas (read by all)
    student-priya.md           ← stellar coder, Python track (the ceiling)
    student-marcus.md          ← strong Python, new to R, shaky inference theory
    student-sofia.md           ← new coder, stats-anxious, R track (retention cliff)
    student-kenji.md           ← stats-strong, tidyverse-naive, demands rigor (R)
    student-aisha.md           ← fluent R, new to Python AND to graphs (Python track)
    student-david.md           ← rusty, time-poor manager (async promise stress test)
    _student-template.md       ← copy to add more personas
  settings.students.json       ← permissions to MERGE into .claude/settings.json
harness/
  run-students.sh              ← headless loop: each persona → its subagent → runs/<id>/
  aggregate.R                  ← builds the cross-persona matrix + summary
orchestrate-students.md        ← prompt to drive the cohort from a main CC session instead
```

Outputs land in `runs/<id>/` (`journal.md`, `report.md`, `scores.json`, `project/`) plus
`runs/_summary.md`, `runs/_matrix_friction.csv`, `runs/_matrix_clarity.csv`.

## Install (one time)

1. Copy `.claude/agents/` and `harness/` into the repo root.
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

**Option B — headless batch.** All six, sequential, then auto-aggregate:
```
bash harness/run-students.sh
# or a subset:
bash harness/run-students.sh sofia priya
```
Key env vars: `MODEL` (default `sonnet`), `PERMISSION_MODE`
(`acceptEdits` default → `dontAsk` for headless → `bypassPermissions` for fully
unattended, **container only**), `OUTPUT_FORMAT`.

**Option C — orchestrated from a main session.** Paste `orchestrate-students.md` into a
main Claude Code session; it runs preflight, dispatches all six, aggregates, and writes
a synthesis (`runs/_registrar-notes.md`).

Then read `runs/_summary.md`. A friction row red across *many* personas = a course
problem (fix the lab); red for *one* = a fit problem for that learner type.

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
