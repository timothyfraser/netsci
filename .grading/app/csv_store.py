"""Atomic CSV persistence for grade metadata."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from env import GRADING_ROOT

DATA_DIR = GRADING_ROOT / "data"
CSV_PATH = DATA_DIR / "grades.csv"

FIELDNAMES = [
    "submission_key",
    "student_name",
    "student_netid",
    "canvas_user_id",
    "canvas_submission_id",
    "assignment_key",
    "assignment_name",
    "canvas_assignment_id",
    "submitted_at",
    "attempt_number",
    "late",
    "workflow_state",
    "cached_dir",
    "cached_report_path",
    "cached_text_path",
    "llm_review_path",
    "llm_model",
    "llm_run_at",
    "llm_status",
    "proposed_score",
    "final_grade",
    "accepted_deductions_json",
    "status",
    "instructor_comment",
    "classbot_comment",
    "published_at",
    "published_grade",
    "publish_error",
]


def _empty_row() -> dict[str, str]:
    return {k: "" for k in FIELDNAMES}


def ensure_csv() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not CSV_PATH.is_file():
        with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
    return CSV_PATH


def read_rows() -> list[dict[str, str]]:
    ensure_csv()
    with CSV_PATH.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_rows(rows: list[dict[str, str]]) -> None:
    ensure_csv()
    tmp = CSV_PATH.with_suffix(".csv.tmp")
    with tmp.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            out = _empty_row()
            out.update({k: str(row.get(k, "") or "") for k in FIELDNAMES})
            writer.writerow(out)
    tmp.replace(CSV_PATH)


def get_row(submission_key: str) -> dict[str, str] | None:
    for row in read_rows():
        if row.get("submission_key") == submission_key:
            return row
    return None


def upsert_row(row: dict[str, Any]) -> dict[str, str]:
    rows = read_rows()
    key = str(row["submission_key"])
    updated = _empty_row()
    existing = get_row(key)
    if existing:
        updated.update(existing)
    updated.update({k: str(row.get(k, updated.get(k, "")) or "") for k in FIELDNAMES})
    updated["submission_key"] = key
    found = False
    for i, r in enumerate(rows):
        if r.get("submission_key") == key:
            rows[i] = updated
            found = True
            break
    if not found:
        rows.append(updated)
    write_rows(rows)
    return updated


def patch_row(submission_key: str, updates: dict[str, Any]) -> dict[str, str]:
    existing = get_row(submission_key)
    if not existing:
        raise KeyError(f"Unknown submission_key: {submission_key}")
    existing.update({k: str(v) if v is not None else "" for k, v in updates.items()})
    return upsert_row(existing)


def parse_deductions_json(raw: str) -> list[dict[str, Any]]:
    if not raw:
        return []
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []
