"""Classbot review for learning-check (completion) assignments."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from env import GRADING_ROOT, mock_llm_enabled
from gateway_client import get_client
from lc_prompts import build_lc_comment_html, build_lc_system_prompt, build_lc_user_prompt
from lc_sources import load_lc_reference
from name_utils import display_name, first_name
from litellm_client import DEFAULT_MODEL, _extract_json, save_review
from rubric import get_assignment

LC_FIXTURE = GRADING_ROOT / "app" / "fixtures" / "mock_lc_review.json"


class LcCheck(BaseModel):
    id: str
    label: str = ""
    student_answer: str = ""
    correct_answer: str = ""
    verdict: Literal["correct", "incorrect", "missing", "unclear"]
    feedback: str = ""


class LcCodeAnswer(BaseModel):
    student_value: str = ""
    expected_summary: str = ""
    verdict: Literal["correct", "incorrect", "missing", "unclear"]
    feedback: str = ""


class LcReview(BaseModel):
    checks: list[LcCheck] = Field(default_factory=list)
    code_answer: LcCodeAnswer
    format_ok: bool = True
    proposed_grade: Literal["0", "1"]
    classbot_summary: str = ""
    confidence: Literal["low", "medium", "high"] = "medium"


def _mock_lc_review() -> dict[str, Any]:
    if LC_FIXTURE.is_file():
        return json.loads(LC_FIXTURE.read_text(encoding="utf-8"))
    return {
        "checks": [
            {
                "id": "lc01",
                "label": "LC 01",
                "student_answer": "B",
                "correct_answer": "B",
                "verdict": "correct",
                "feedback": "👍 Matrix vs node-link — nailed it.",
            },
            {
                "id": "lc02",
                "label": "LC 02",
                "student_answer": "B",
                "correct_answer": "B",
                "verdict": "correct",
                "feedback": "👍 Circular layout shows shortcuts.",
            },
            {
                "id": "lc03",
                "label": "LC 03",
                "student_answer": "C",
                "correct_answer": "C",
                "verdict": "correct",
                "feedback": "👍 Bipartite projection reasoning.",
            },
        ],
        "code_answer": {
            "student_value": "3",
            "expected_summary": "Degree of S017 in supplier projection",
            "verdict": "correct",
            "feedback": "👍 Matches code output.",
        },
        "format_ok": True,
        "proposed_grade": "1",
        "classbot_summary": "All three LCs and code line look good — completion ✅",
        "confidence": "high",
    }


def review_lc_submission(
    submission_text: str,
    assignment: dict[str, Any],
    metadata: dict[str, Any],
    *,
    model: str = DEFAULT_MODEL,
) -> dict[str, Any]:
    reference = load_lc_reference(assignment)
    if mock_llm_enabled():
        return LcReview.model_validate(_mock_lc_review()).model_dump()

    system = build_lc_system_prompt()
    user = build_lc_user_prompt(submission_text, reference, metadata)
    client = get_client()
    last_err: Exception | None = None
    for _ in range(2):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            raw = resp.choices[0].message.content or "{}"
            data = _extract_json(raw)
            return LcReview.model_validate(data).model_dump()
        except Exception as exc:
            last_err = exc
            user += "\n\nReturn ONLY valid JSON matching the schema."
    raise RuntimeError(f"LC Classbot failed: {last_err}") from last_err


def run_lc_classbot_for_row(
    row: dict[str, str],
    *,
    model: str = DEFAULT_MODEL,
) -> dict[str, Any]:
    assignment = get_assignment(row.get("assignment_key", ""))
    if not assignment:
        raise ValueError(f"Unknown assignment: {row.get('assignment_key')}")
    text_path = Path(row.get("cached_text_path", ""))
    submission_text = text_path.read_text(encoding="utf-8") if text_path.is_file() else ""
    metadata = {
        "student_name": row.get("student_name"),
        "student_display_name": display_name(row.get("student_name", "")),
        "student_first_name": first_name(row.get("student_name", "")),
        "assignment": row.get("assignment_name"),
        "assignment_key": row.get("assignment_key"),
        "submitted_at": row.get("submitted_at"),
    }
    review = review_lc_submission(submission_text, assignment, metadata, model=model)
    key = row["submission_key"]
    llm_path = save_review(key, review)
    grade = review.get("proposed_grade", "1")
    classbot_comment = build_lc_comment_html(review)
    now = datetime.now(timezone.utc).isoformat()
    return {
        "llm_review_path": str(llm_path),
        "llm_model": model,
        "llm_run_at": now,
        "llm_status": "done",
        "proposed_score": grade,
        "final_grade": grade,
        "accepted_deductions_json": "[]",
        "classbot_comment": classbot_comment,
        "status": "synced",
        "review": review,
    }
