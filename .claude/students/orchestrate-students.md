# Orchestration prompt — run the AI student cohort

Paste the block below into a **main Claude Code session at the repo root** when you'd
rather drive the cohort interactively than via the headless `run-students.sh` harness.
The main session acts as **registrar**: it dispatches each persona subagent, then
synthesizes across their reports.

> Sequential dispatch is recommended (cheaper, and easier to keep each persona honest).
> To parallelize, tell the session to run them concurrently — but expect roughly several
> times the token cost, and noisier fidelity.

---

```
You are the registrar for an AI-student evaluation of SYSEN 5470. Six student
personas are defined as subagents in .claude/agents/ (student-priya, student-marcus,
student-sofia, student-kenji, student-aisha, student-david). Each reads the shared
brief at .claude/agents/_shared/student-brief.md and inhabits a fixed skill profile.

Do this:

1. PREFLIGHT. Confirm the environment is ready and report a short checklist:
   - Playwright MCP reachable (the students browse https://timothyfraser.com/netsci).
   - R available (Rscript runs); Python available if any persona uses the Python track
     (priya, marcus, aisha do).
   - .claude/settings.json includes the student allow-list (Bash python/pip, file
     writes, Playwright navigate/click/type). If navigation tools aren't permitted,
     STOP and tell me what to add — otherwise the runs will stall.
   - A runs/ directory exists (create it).
   If anything's missing, list exactly what I need to fix before proceeding.

2. DISPATCH, one persona at a time, in this order: sofia, david, marcus, kenji,
   aisha, priya (struggling students first, so problems surface early). For each:
   "Use the student-<id> subagent to take SYSEN 5470 in full per its brief, run the
   real code, and write journal.md, report.md, scores.json, and project/ into
   runs/<id>/." Wait for it to finish and confirm runs/<id>/report.md exists before
   starting the next. If a persona fails or breaks character, note it and continue.

3. AGGREGATE. After all six finish, run: Rscript .claude/harness/aggregate.R runs
   Then read runs/_summary.md and the two matrix CSVs.

4. SYNTHESIZE. Write runs/_registrar-notes.md with:
   - The 3–5 labs that are COURSE problems (red across multiple, different personas),
     each with the specific friction quoted from the relevant report.md.
   - The issues that are FIT problems (one persona only) — and which persona type.
   - The inference-scaffolding verdict: compare labs 07 (permutation) and 09
     (counterfactual MC) across stats-averse (sofia, marcus) vs stats-strong
     (kenji, priya).
   - The track-parity verdict: Python (priya, marcus, aisha) vs R (sofia, kenji,
     david) on shared labs.
   - The retention cliff: where did anyone "almost drop," and is it clustered?
   - A ranked, deduplicated list of the highest-ROI fixes (those named by 2+ students),
     each tagged with which personas asked for it.
   Keep it concrete and quote the students. Do not soften the criticism — blunt is useful.

Begin with the PREFLIGHT checklist and wait for my go-ahead before dispatching.
```

---

**Resilience tip.** A full 3-week walkthrough is a long task for one subagent. The
brief already has each student append to `journal.md` as they go, so progress survives.
If a persona's single run is too long, dispatch it **once per course-week** instead
("...do Week 1 only; resume from your journal"), three calls per persona.
