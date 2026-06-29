# Classbot Grading Dashboard

Local instructor tool for SYSEN 5470 project case study reports. **Classbot** runs a Cornell AI Gateway first pass; you review, toggle deductions, and publish to Canvas.

## Setup

1. Ensure keys are in [`.canvas/.env`](../.canvas/.env) (see [`.env.example`](.env.example)).
2. Install and run:

```powershell
cd .grading
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\run.ps1
```

3. Open http://127.0.0.1:8765

## Data safety

- `data/grades.csv` and `cache/` are **gitignored** — never commit student work.
- App source under `app/` and `config/` may be committed on the `instructor` branch only.
- **`main` never receives `.grading/`** — the `publish-student-subset` workflow whitelists only student paths (`data`, `code`, etc.).
- Before committing: `python scripts/verify_commit_safe.py`
- Uses Chat Completions API only (prompts/completions not stored by gateway).

## Workflow

1. **Sync from Canvas** — downloads submissions once into `cache/submissions/`.
2. **Run Classbot** — structured JSON review via LiteLLM (Haiku default).
3. Toggle proposed deductions, add instructor comment.
4. **Publish to Canvas** — grade + delineated Instructor / Classbot comment.

Set `MOCK_LLM=1` for offline UI tests without API calls.

## E2E testing (Canvas + Playwright)

```powershell
cd .grading
# Real gateway + Canvas (uses .canvas/.env)
.\.venv\Scripts\python scripts\e2e_canvas_test.py
.\.venv\Scripts\python scripts\e2e_playwright_mcp.py
```

**Canvas Test Student:** The Student View account (`Test Student`, user id 212069) exists but cannot receive submissions via the instructor API (403). Sync skips unsubmitted rows. E2E uses a real submitted project-1 row (cached PDF + text) after `sync project-1`.

Probe Canvas state: `python scripts/canvas_probe.py`
