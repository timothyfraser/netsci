"""Classbot LLM review with structured JSON output."""

from __future__ import annotations

import base64
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from env import GRADING_ROOT, mock_llm_enabled
from gateway_client import get_client
from name_utils import display_name, first_name
from prompts import build_classbot_comment_from_review, build_system_prompt, build_user_prompt
from rubric import compute_score, load_rubric, max_deduction_map

LLM_CACHE = GRADING_ROOT / "cache" / "llm"
FIXTURE_PATH = GRADING_ROOT / "app" / "fixtures" / "mock_review.json"

DEFAULT_MODEL = "claude-haiku-4-5"
SONNET_MODEL = "claude-sonnet-4-6"
PDF_MODEL = "google.gemini-2.5-pro"


class RequirementReview(BaseModel):
    id: str
    status: Literal["met", "partial", "missing", "not_assessable"]
    evidence: str = ""
    location: str = ""
    proposed_deduction: int = 0
    search_hint: str = ""

    @field_validator("search_hint")
    @classmethod
    def three_words(cls, v: str) -> str:
        v = v.strip()
        if not v:
            return ""
        words = v.split()
        if len(words) != 3:
            raise ValueError(f"search_hint must be exactly 3 words, got {len(words)}")
        return " ".join(words)


class TopIssue(BaseModel):
    rank: int
    title: str
    description: str = ""
    location: str = ""
    search_hint: str = ""

    @field_validator("search_hint")
    @classmethod
    def three_words(cls, v: str) -> str:
        v = v.strip()
        if not v:
            return ""
        words = v.split()
        if len(words) != 3:
            raise ValueError(f"search_hint must be exactly 3 words, got {len(words)}")
        return " ".join(words)


class ClassbotReview(BaseModel):
    requirements: list[RequirementReview]
    top_issues: list[TopIssue] = Field(min_length=0, max_length=5)
    classbot_summary: str = ""
    confidence: Literal["low", "medium", "high"] = "medium"


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    return json.loads(text)


def _mock_review() -> dict[str, Any]:
    if FIXTURE_PATH.is_file():
        return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return {
        "requirements": [
            {
                "id": "results_prose",
                "status": "partial",
                "evidence": "Results section references figures without numeric summaries.",
                "location": "Results, paragraph 2",
                "proposed_deduction": 8,
                "search_hint": "numbers prose missing",
            },
            {
                "id": "question",
                "status": "met",
                "evidence": "Clear one-sentence question in opening.",
                "location": "Question section",
                "proposed_deduction": 0,
                "search_hint": "question sentence clear",
            },
        ],
        "top_issues": [
            {
                "rank": 1,
                "title": "Results are figure-only",
                "description": "No centrality values stated in prose.",
                "location": "Results section",
                "search_hint": "figure only results",
            }
        ],
        "classbot_summary": "Solid network operationalization; push on numeric results in prose.",
        "confidence": "medium",
    }


def _validate_review(data: dict[str, Any]) -> ClassbotReview:
    return ClassbotReview.model_validate(data)


def _chat_text(model: str, system: str, user: str) -> str:
    client = get_client()
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    return resp.choices[0].message.content or "{}"


def _chat_pdf(model: str, system: str, user: str, pdf_path: Path) -> str:
    client = get_client()
    b64 = base64.standard_b64encode(pdf_path.read_bytes()).decode("ascii")
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user},
                    {
                        "type": "file",
                        "file": {
                            "filename": pdf_path.name,
                            "file_data": f"data:application/pdf;base64,{b64}",
                        },
                    },
                ],
            },
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content or "{}"


def review_submission(
    report_text: str,
    metadata: dict[str, Any],
    *,
    model: str = DEFAULT_MODEL,
    mode: Literal["text", "pdf"] = "text",
    pdf_path: Path | None = None,
) -> dict[str, Any]:
    if mock_llm_enabled():
        review = _validate_review(_mock_review())
        return review.model_dump()

    system = build_system_prompt()
    user = build_user_prompt(report_text, metadata)
    raw = ""
    last_err: Exception | None = None
    for attempt in range(2):
        try:
            if mode == "pdf" and pdf_path and pdf_path.is_file():
                raw = _chat_pdf(model or PDF_MODEL, system, user, pdf_path)
            else:
                raw = _chat_text(model, system, user)
            data = _extract_json(raw)
            review = _validate_review(data)
            return review.model_dump()
        except Exception as exc:
            last_err = exc
            user = user + "\n\nYour previous JSON was invalid. Return ONLY valid JSON with exact schema and 3-word search_hints."
    raise RuntimeError(f"Classbot review failed: {last_err}") from last_err


def proposed_deductions_from_review(review: dict[str, Any]) -> list[dict[str, Any]]:
    caps = max_deduction_map()
    out: list[dict[str, Any]] = []
    for req in review.get("requirements", []):
        rid = req.get("id", "")
        prop = int(req.get("proposed_deduction", 0) or 0)
        cap = caps.get(rid, prop)
        accepted = req.get("status") in ("partial", "missing") and prop > 0
        out.append(
            {
                "id": rid,
                "accepted": accepted,
                "deduction": min(prop, cap),
                "proposed_deduction": min(prop, cap),
                "status": req.get("status"),
                "evidence": req.get("evidence", ""),
                "location": req.get("location", ""),
                "search_hint": req.get("search_hint", ""),
            }
        )
    return out


def save_review(submission_key: str, review: dict[str, Any]) -> Path:
    LLM_CACHE.mkdir(parents=True, exist_ok=True)
    path = LLM_CACHE / f"{submission_key}.json"
    path.write_text(json.dumps(review, indent=2), encoding="utf-8")
    return path


def load_review(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def run_classbot_for_row(
    row: dict[str, str],
    *,
    model: str = DEFAULT_MODEL,
    mode: Literal["text", "pdf"] = "text",
) -> dict[str, Any]:
    text_path = Path(row.get("cached_text_path", ""))
    report_text = text_path.read_text(encoding="utf-8") if text_path.is_file() else ""
    pdf_path = Path(row.get("cached_report_path", "")) if row.get("cached_report_path") else None
    metadata = {
        "student_name": row.get("student_name"),
        "student_display_name": display_name(row.get("student_name", "")),
        "student_first_name": first_name(row.get("student_name", "")),
        "assignment": row.get("assignment_name"),
        "submitted_at": row.get("submitted_at"),
        "attempt": row.get("attempt_number"),
    }
    review = review_submission(
        report_text,
        metadata,
        model=model,
        mode=mode,
        pdf_path=pdf_path if pdf_path and pdf_path.suffix.lower() == ".pdf" else None,
    )
    key = row["submission_key"]
    llm_path = save_review(key, review)
    deductions = proposed_deductions_from_review(review)
    score = compute_score(deductions)
    classbot_comment = build_classbot_comment_from_review(review)
    now = datetime.now(timezone.utc).isoformat()
    return {
        "llm_review_path": str(llm_path),
        "llm_model": model,
        "llm_run_at": now,
        "llm_status": "done",
        "proposed_score": str(score),
        "final_grade": str(score),
        "accepted_deductions_json": json.dumps(deductions),
        "classbot_comment": classbot_comment,
        "status": "synced",
        "review": review,
    }
