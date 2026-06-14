# SETUP-AGENT HANDOFF — install the SYSEN 5470 AI-student system

> **Historical note (relocated):** this doc describes the original install, which placed
> `harness/` and the student docs at the **repo root**. The system was later moved under
> `.claude/` (`.claude/harness/`, `.claude/students/`; subagents stay in `.claude/agents/`)
> so the scaffolding stays out of the student personas' way. Paths below reflect the
> original layout — see `.claude/students/README-ai-students.md` for the current one.

**You are a setup agent (Claude Code) working at the root of the `timothyfraser/netsci`
repository.** Your job is to install the AI-student walkthrough system from this bundle
into the repo, verify the environment, and stage the one human-review step — then stop
and report. A human (Tim) will do the final permission merge and run the cohort in a
fresh session.

This automates the "Install" section of `README-ai-students.md`, stopping short of the
permission merge.

---

## Hard guardrails — do NOT cross these

- ❌ **Do not modify `.claude/settings.json`.** You will *stage* a proposed merge to a
  side file. The human applies it.
- ❌ **Do not run a student cohort** (no `run-students.sh`, no invoking `student-*`
  subagents). Setup only. The first real run happens later, in a fresh session.
- ❌ **Do not `git commit`, `git push`, or alter git history.**
- ❌ **Do not read, print, copy, or echo `.env` or any secret.**
- ✅ Everything you do is additive and reversible. If a step is ambiguous, stop and ask.

---

## Step 0 — Confirm inputs

1. Confirm you are at the repo root: it should contain `.claude/`, `code/`, and `CLAUDE.md`.
   If not, stop and ask for the repo path.
2. Locate the unzipped bundle. Default expected path: `./netsci-ai-students/`. If it's
   elsewhere, ask the human for the path and use it as `$BUNDLE` below.
3. Print what you found (repo root path, bundle path) and proceed only if both exist.

## Step 1 — Place files (additive)

From `$BUNDLE`, copy into the repo:

- `.claude/agents/`  → repo `.claude/agents/`  (new directory; if it already exists, do
  **not** overwrite any file — list collisions and ask).
- `harness/`         → repo `harness/`
- `orchestrate-students.md`, `README-ai-students.md`, `SETUP-AGENT-HANDOFF.md` → repo root
- `.claude/settings.students.json` → repo `.claude/settings.students.json`  (staged, not merged)

Then make the script executable: `chmod +x harness/run-students.sh`.

Confirm by listing `.claude/agents/` (expect `_shared/student-brief.md`, six
`student-*.md`, `_student-template.md`) and `harness/` (expect `run-students.sh`,
`aggregate.R`).

## Step 2 — Stage the settings merge (DO NOT APPLY)

Produce a reviewed-ready proposal without touching `.claude/settings.json`:

```bash
python3 - <<'PY'
import json
base = json.load(open('.claude/settings.json'))
add  = json.load(open('.claude/settings.students.json'))
base.setdefault('permissions', {})
added = {}
for key in ('allow','deny'):
    cur = base['permissions'].get(key, [])
    new = add.get('permissions', {}).get(key, [])
    merged = list(dict.fromkeys([*cur, *new]))     # dedup, preserve order
    added[key] = [x for x in new if x not in cur]
    base['permissions'][key] = merged
json.dump(base, open('.claude/settings.proposed.json','w'), indent=2)
print("ADDED allow:", *added['allow'], sep="\n  ")
print("ADDED deny:",  *added['deny'],  sep="\n  ")
PY
```

This writes `.claude/settings.proposed.json` (existing hooks and all other keys
preserved). Then write a `MERGE-ME.md` at repo root containing:
- The exact list of `allow` and `deny` entries that would be **added** (from the output above).
- This instruction for the human: *"Review `.claude/settings.proposed.json`; if it looks
  right, replace `.claude/settings.json` with it (or hand-add the listed entries). These
  grant the student agents Python, file-writes, and Playwright navigate/click/type."*

## Step 3 — Verify the environment (report, don't force-fix)

Run each check and record ✅ / ⚠️ / ❌:

1. **Playwright MCP** — `claude mcp list`. Confirm a server named exactly **`playwright`**
   is present/connected. The allow-list uses the prefix `mcp__playwright__browser_*`; if
   the server has a different name, the prefix won't match — note the correct name in
   `MERGE-ME.md` so the human can fix the allow entries.
2. **R** — `Rscript --version` (present?). Packages are otherwise handled by
   `.claude/session-start.sh`.
3. **Python** — `python3 --version` and `pip3 --version` (the Python-track personas need them).
4. **Course code** — confirm `code/01_*` … `code/11_*` exist and each contains an
   `example.R` and/or `example.py`.
5. **Course site reachable** — `curl -sI https://timothyfraser.com/netsci | head -1`.

## Step 4 — Close the aggregator's dependency gap

`harness/aggregate.R` needs **`jsonlite`** and **`purrr`**, which are NOT in the repo's
`session-start.sh` baseline. Install them if missing:

```bash
Rscript -e 'p <- c("jsonlite","purrr"); m <- setdiff(p, rownames(installed.packages())); if (length(m)) install.packages(m, repos="https://cloud.r-project.org"); cat("ok\n")'
```

(If the network blocks CRAN in your environment, skip and list `jsonlite`, `purrr` as a
TODO for the human in your final report.)

## Step 5 — Validate the dropped-in files parse

1. **Subagents** — each `.claude/agents/student-*.md` and `_student-template.md` must have
   YAML frontmatter with a `name:`. Confirm the six names are unique:
   `student-priya/marcus/sofia/kenji/aisha/david`.
2. **aggregate.R** — syntax-only check (do **not** execute):
   `Rscript -e 'invisible(parse("harness/aggregate.R")); cat("parse ok\n")'`
3. **run-students.sh** — `bash -n harness/run-students.sh && echo "sh ok"`.

## Step 6 — Create runtime dirs and ignore outputs

```bash
mkdir -p runs logs
# keep generated student outputs/logs out of version control
grep -qxF 'runs/'  .gitignore 2>/dev/null || echo 'runs/'  >> .gitignore
grep -qxF 'logs/'  .gitignore 2>/dev/null || echo 'logs/'  >> .gitignore
grep -qxF '.claude/settings.proposed.json' .gitignore 2>/dev/null || echo '.claude/settings.proposed.json' >> .gitignore
```

## Step 7 — Final report (and then stop)

Print a checklist and the handoff back to the human. Use this shape:

```
SETUP COMPLETE — review before merging.

Placed:        .claude/agents/ (7 files), harness/ (2 files), docs at root  [✅/❌]
Settings:      staged .claude/settings.proposed.json (NOT applied)          [✅/❌]
Playwright MCP: server 'playwright' connected                              [✅/⚠️/❌ + note]
R / Rscript:                                                               [✅/❌]
Python / pip:                                                              [✅/❌]
code/01..11 with example scripts:                                         [✅/❌]
Course site reachable:                                                    [✅/❌]
jsonlite + purrr installed:                                               [✅/⚠️/❌]
Files parse (subagents / aggregate.R / run-students.sh):                  [✅/❌]
runs/ logs/ created, .gitignore updated:                                  [✅/❌]

YOUR TURN, TIM:
1. Review .claude/settings.proposed.json against MERGE-ME.md, then make it your
   .claude/settings.json.
2. (If flagged) install missing R packages / fix the Playwright server-name prefix.
3. In a FRESH session, pilot one persona first:
     claude
     > Use the student-sofia subagent to take SYSEN 5470 in full per its brief and
       write outputs to runs/sofia/.
   Then run the full cohort:  bash harness/run-students.sh
```

Do not proceed past this report. Do not start a cohort run.
