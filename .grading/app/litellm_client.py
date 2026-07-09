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
from llm_privacy import anonymize_llm_metadata, anonymize_submission_text
from submission_text import read_submission_text
from prompts import build_classbot_comment_from_review, build_system_prompt, build_user_prompt
from rubric import compute_score, load_rubric, max_deduction_map

LLM_CACHE = GRADING_ROOT / "cache" / "llm"
FIXTURE_PATH = GRADING_ROOT / "app" / "fixtures" / "mock_review.json"

DEFAULT_MODEL = "claude-haiku-4-5"
SONNET_MODEL = "claude-sonnet-4-6"
PDF_MODEL = "google.gemini-2.5-pro"

CHECKLIST_IDS = (
    "research_question",
    "dataset_assumptions",
    "methods_client_language",
    "results_statistics_in_text",
    "discussion_limitations",
)


def _normalize_search_hint(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""
    words = text.split()
    if len(words) >= 3:
        return " ".join(words[:3])
    pad = ("check", "report", "section")
    while len(words) < 3:
        words.append(pad[len(words) % len(pad)])
    return " ".join(words[:3])


def _normalize_checklist_id(raw: Any) -> str | None:
    if raw is None:
        return None
    text = str(raw).strip().lower()
    text = re.sub(r"^\d+\.\s*", "", text)
    slug = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    for cid in CHECKLIST_IDS:
        if slug == cid or slug.startswith(cid) or cid in slug:
            return cid
    if "research" in text and "question" in text:
        return "research_question"
    if "dataset" in text or "assumption" in text:
        return "dataset_assumptions"
    if "method" in text and ("client" in text or "language" in text or "jargon" in text):
        return "methods_client_language"
    if "result" in text and ("statistic" in text or "prose" in text or "number" in text):
        return "results_statistics_in_text"
    if "discussion" in text or "limitation" in text:
        return "discussion_limitations"
    return None


def _normalize_rating(value: Any, *, allowed: tuple[str, ...], default: str) -> str:
    rating = str(value or default).strip().lower()
    return rating if rating in allowed else default


def _normalize_review_data(data: dict[str, Any]) -> dict[str, Any]:
    out = dict(data)
    for req in out.get("requirements", []):
        if isinstance(req, dict):
            req["search_hint"] = _normalize_search_hint(req.get("search_hint"))
    for issue in out.get("top_issues", []):
        if isinstance(issue, dict):
            issue["search_hint"] = _normalize_search_hint(issue.get("search_hint"))
    checklist: list[dict[str, Any]] = []
    for item in out.get("report_checklist", []) or []:
        if not isinstance(item, dict):
            continue
        entry = dict(item)
        cid = entry.get("id") or entry.get("item") or entry.get("name") or entry.get("label")
        norm_id = _normalize_checklist_id(cid)
        if not norm_id:
            continue
        entry["id"] = norm_id
        for drop in ("item", "name", "label"):
            entry.pop(drop, None)
        entry["rating"] = _normalize_rating(
            entry.get("rating"),
            allowed=("strong", "partial", "weak"),
            default="partial",
        )
        checklist.append(entry)
    out["report_checklist"] = checklist[:5]
    ai = out.get("client_ai_likelihood")
    if isinstance(ai, dict):
        rating = _normalize_rating(ai.get("rating"), allowed=("low", "medium", "high"), default="")
        if not rating:
            out["client_ai_likelihood"] = None
        else:
            ai = dict(ai)
            ai["rating"] = rating
            patterns = ai.get("patterns")
            ai["patterns"] = [str(p) for p in patterns[:6]] if isinstance(patterns, list) else []
            out["client_ai_likelihood"] = ai
    else:
        out["client_ai_likelihood"] = None
    return out


class RequirementReview(BaseModel):
    id: str
    status: Literal["met", "partial", "missing", "not_assessable"]
    evidence: str = ""
    location: str = ""
    proposed_deduction: int = 0
    search_hint: str = ""

    @field_validator("search_hint", mode="before")
    @classmethod
    def three_words(cls, v: Any) -> str:
        return _normalize_search_hint(v)


class TopIssue(BaseModel):
    rank: int
    title: str
    description: str = ""
    location: str = ""
    search_hint: str = ""

    @field_validator("search_hint", mode="before")
    @classmethod
    def three_words(cls, v: Any) -> str:
        return _normalize_search_hint(v)


class ReportChecklistItem(BaseModel):
    id: Literal[
        "research_question",
        "dataset_assumptions",
        "methods_client_language",
        "results_statistics_in_text",
        "discussion_limitations",
    ]
    rating: Literal["strong", "partial", "weak"]
    evidence: str = ""
    location: str = ""


class ClientAiLikelihood(BaseModel):
    rating: Literal["low", "medium", "high"]
    rationale: str = ""
    patterns: list[str] = Field(default_factory=list, max_length=6)


class ClassbotReview(BaseModel):
    requirements: list[RequirementReview]
    top_issues: list[TopIssue] = Field(min_length=0, max_length=5)
    report_checklist: list[ReportChecklistItem] = Field(default_factory=list, min_length=0, max_length=5)
    client_ai_likelihood: ClientAiLikelihood | None = None
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


def _normalize_hygiene_review(data: dict[str, Any]) -> dict[str, Any]:
    """Cap GitHub noise; script not assessable from extracted text."""
    for req in data.get("requirements", []):
        rid = req.get("id")
        if rid == "project_script":
            req["status"] = "not_assessable"
            req["proposed_deduction"] = 0
            if not req.get("evidence"):
                req["evidence"] = "Check Canvas attachments; not verifiable from report text alone."
        elif rid == "github_link" and req.get("status") == "missing":
            prop = int(req.get("proposed_deduction", 0) or 0)
            req["proposed_deduction"] = min(prop, 2)
    return data


def _validate_review(data: dict[str, Any]) -> ClassbotReview:
    return ClassbotReview.model_validate(_normalize_hygiene_review(_normalize_review_data(data)))


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
        review = _validate_review(_normalize_hygiene_review(_mock_review()))
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
            user = (
                user
                + "\n\nYour previous JSON was invalid. Return ONLY valid JSON matching the schema: "
                "use `id` (not `item`) in report_checklist entries "
                "(research_question, dataset_assumptions, methods_client_language, "
                "results_statistics_in_text, discussion_limitations); "
                "search_hint must be exactly three words."
            )
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
    raw_text = read_submission_text(row)
    report_text = anonymize_submission_text(raw_text, row)
    pdf_path = Path(row.get("cached_report_path", "")) if row.get("cached_report_path") else None
    metadata = anonymize_llm_metadata(row)
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
