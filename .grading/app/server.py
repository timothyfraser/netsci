"""Classbot grading dashboard — FastAPI server."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from canvas_client import publish_grade, sync_assignment
from csv_store import get_row, parse_deductions_json, patch_row, read_rows, upsert_row
from env import GRADING_ROOT, mock_llm_enabled
from litellm_client import (
    DEFAULT_MODEL,
    load_review,
    run_classbot_for_row,
)
from prompts import compose_canvas_comment, compose_canvas_comment_plain_preview
from rubric import compute_score, load_assignments, load_rubric

STATIC_DIR = APP_DIR / "static"
app = FastAPI(title="Classbot Grading Dashboard")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8765", "http://localhost:8765"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class PatchRowBody(BaseModel):
    accepted_deductions_json: str | None = None
    final_grade: str | None = None
    instructor_comment: str | None = None
    classbot_comment: str | None = None
    status: str | None = None


class SyncBody(BaseModel):
    assignment_key: str
    force: bool = False


class ClassbotBody(BaseModel):
    model: str = DEFAULT_MODEL
    mode: str = "text"


class BatchClassbotBody(BaseModel):
    submission_keys: list[str] = Field(default_factory=list)
    model: str = DEFAULT_MODEL
    mode: str = "text"


class PublishBody(BaseModel):
    final_grade: str | None = None


@app.get("/api/config")
def api_config() -> dict[str, Any]:
    return {
        "rubric": load_rubric(),
        "assignments": load_assignments(),
        "mock_llm": mock_llm_enabled(),
    }


@app.get("/api/rows")
def api_rows(
    assignment_key: str | None = None,
    status: str | None = None,
    late: str | None = None,
    has_report: bool | None = None,
) -> list[dict[str, str]]:
    rows = read_rows()
    if assignment_key:
        rows = [r for r in rows if r.get("assignment_key") == assignment_key]
    if status:
        rows = [r for r in rows if r.get("status") == status]
    if late is not None:
        rows = [r for r in rows if r.get("late") == late]
    if has_report is True:
        rows = [r for r in rows if r.get("cached_text_path")]
    elif has_report is False:
        rows = [r for r in rows if not r.get("cached_text_path")]
    return rows


@app.get("/api/rows/{submission_key}")
def api_row_detail(submission_key: str) -> dict[str, Any]:
    row = get_row(submission_key)
    if not row:
        raise HTTPException(404, "Row not found")
    review = None
    llm_path = row.get("llm_review_path", "")
    if llm_path:
        review = load_review(Path(llm_path))
    deductions = parse_deductions_json(row.get("accepted_deductions_json", ""))
    return {"row": row, "review": review, "deductions": deductions}


@app.patch("/api/rows/{submission_key}")
def api_patch_row(submission_key: str, body: PatchRowBody) -> dict[str, str]:
    row = get_row(submission_key)
    if not row:
        raise HTTPException(404, "Row not found")
    updates: dict[str, Any] = {}
    if body.accepted_deductions_json is not None:
        deductions = parse_deductions_json(body.accepted_deductions_json)
        score = compute_score(deductions)
        updates["accepted_deductions_json"] = json.dumps(deductions)
        updates["final_grade"] = str(score)
        updates["proposed_score"] = str(score)
    if body.final_grade is not None:
        updates["final_grade"] = body.final_grade
    if body.instructor_comment is not None:
        updates["instructor_comment"] = body.instructor_comment
    if body.classbot_comment is not None:
        updates["classbot_comment"] = body.classbot_comment
    if body.status is not None:
        updates["status"] = body.status
    elif body.accepted_deductions_json is not None or body.instructor_comment is not None:
        updates["status"] = "reviewed"
    return patch_row(submission_key, updates)


@app.post("/api/sync")
def api_sync(body: SyncBody) -> dict[str, Any]:
    rows = sync_assignment(body.assignment_key, force=body.force)
    return {"count": len(rows), "rows": rows}


@app.post("/api/sync-all")
def api_sync_all(body: SyncBody | None = None) -> dict[str, Any]:
    from rubric import load_assignments

    force = body.force if body else False
    rows: list[dict[str, str]] = []
    for assignment in load_assignments():
        rows.extend(sync_assignment(assignment["key"], force=force))
    return {"count": len(rows), "rows": rows}


@app.post("/api/classbot/{submission_key}")
def api_classbot(submission_key: str, body: ClassbotBody) -> dict[str, Any]:
    row = get_row(submission_key)
    if not row:
        raise HTTPException(404, "Row not found")
    try:
        result = run_classbot_for_row(row, model=body.model, mode=body.mode)  # type: ignore[arg-type]
    except Exception as exc:
        patch_row(submission_key, {"llm_status": "error", "publish_error": str(exc)})
        raise HTTPException(502, str(exc)) from exc
    review = result.pop("review", None)
    updated = patch_row(submission_key, result)
    return {"row": updated, "review": review}


@app.post("/api/classbot/batch")
def api_classbot_batch(body: BatchClassbotBody) -> dict[str, Any]:
    results = []
    errors = []
    for key in body.submission_keys:
        row = get_row(key)
        if not row:
            errors.append({"key": key, "error": "not found"})
            continue
        try:
            result = run_classbot_for_row(row, model=body.model, mode=body.mode)  # type: ignore[arg-type]
            result.pop("review", None)
            patch_row(key, result)
            results.append(key)
        except Exception as exc:
            patch_row(key, {"llm_status": "error", "publish_error": str(exc)})
            errors.append({"key": key, "error": str(exc)})
    return {"ok": results, "errors": errors}


@app.get("/api/report-text/{submission_key}")
def api_report_text(submission_key: str) -> dict[str, str]:
    row = get_row(submission_key)
    if not row:
        raise HTTPException(404, "Row not found")
    path = Path(row.get("cached_text_path", ""))
    if not path.is_file():
        return {"text": ""}
    return {"text": path.read_text(encoding="utf-8", errors="replace")}


class ComposePreviewBody(BaseModel):
    instructor_comment: str = ""
    classbot_comment: str = ""


@app.post("/api/compose-preview")
def api_compose_preview(body: ComposePreviewBody) -> dict[str, str]:
    html_comment = compose_canvas_comment(body.instructor_comment, body.classbot_comment)
    return {
        "html": html_comment,
        "plain": compose_canvas_comment_plain_preview(body.instructor_comment, body.classbot_comment),
    }


@app.post("/api/publish/{submission_key}")
def api_publish(submission_key: str, body: PublishBody) -> dict[str, Any]:
    row = get_row(submission_key)
    if not row:
        raise HTTPException(404, "Row not found")
    grade = body.final_grade or row.get("final_grade") or row.get("proposed_score") or "0"
    comment = compose_canvas_comment(
        row.get("instructor_comment", ""),
        row.get("classbot_comment", ""),
    )
    try:
        publish_grade(row, grade, comment)
        from datetime import datetime, timezone

        updated = patch_row(
            submission_key,
            {
                "published_at": datetime.now(timezone.utc).isoformat(),
                "published_grade": grade,
                "publish_error": "",
                "status": "published",
                "final_grade": grade,
            },
        )
        return {"row": updated, "comment_preview": comment}
    except Exception as exc:
        patch_row(submission_key, {"publish_error": str(exc)})
        raise HTTPException(502, str(exc)) from exc


@app.post("/api/seed-demo")
def api_seed_demo() -> dict[str, Any]:
    """Seed one demo row for Playwright / offline testing."""
    cache_dir = GRADING_ROOT / "cache" / "submissions" / "project-1" / "99999"
    cache_dir.mkdir(parents=True, exist_ok=True)
    text_path = cache_dir / "report.txt"
    sample = """# Question
Which distribution hubs have the highest betweenness in the UPS ground network?

# Network
Nodes are plants and hubs; edges are truck lanes weighted by weekly package volume.

# Procedure
I computed degree and betweenness centrality in igraph.

# Results
The highest betweenness node had score 0.142. See Figure 1.

# What this tells me, and what it doesn't
Hub X is a chokepoint; this does not prove causal disruption impact.
"""
    text_path.write_text(sample, encoding="utf-8")
    row = upsert_row(
        {
            "submission_key": "project-1_99999_a1",
            "student_name": "Demo, Student",
            "student_netid": "sd999",
            "canvas_user_id": "99999",
            "canvas_submission_id": "0",
            "assignment_key": "project-1",
            "assignment_name": "Project Case Study — Submission 1",
            "canvas_assignment_id": "968727",
            "submitted_at": "2026-06-29T12:00:00Z",
            "attempt_number": "1",
            "late": "false",
            "workflow_state": "submitted",
            "cached_dir": str(cache_dir),
            "cached_report_path": "",
            "cached_text_path": str(text_path),
            "llm_status": "pending",
            "status": "synced",
        }
    )
    return {"row": row}


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="info")


if __name__ == "__main__":
    main()
