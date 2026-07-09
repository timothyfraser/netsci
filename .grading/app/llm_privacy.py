"""Remove student-identifying fields before Cornell AI Gateway calls."""

from __future__ import annotations

import re
from typing import Any

from name_utils import display_name, parse_sortable_name

REDACT_PLACEHOLDER = "[student]"

# Keys that must never be sent to the LLM (Canvas / roster identifiers).
_PII_KEYS = frozenset(
    {
        "student_name",
        "student_display_name",
        "student_first_name",
        "student_netid",
        "student_email",
        "canvas_user_id",
        "canvas_submission_id",
        "submission_key",
        "cached_dir",
        "cached_report_path",
        "cached_text_path",
        "llm_review_path",
        "instructor_comment",
        "classbot_comment",
        "report_text_override",
        "published_at",
        "published_grade",
        "publish_error",
        "accepted_deductions_json",
    }
)

_CORNELL_EMAIL = re.compile(r"\b[\w.-]+@cornell\.edu\b", re.IGNORECASE)


def _pii_strings(row: dict[str, Any]) -> list[str]:
    """Name/netid variants from the grade row, longest first for greedy replacement."""
    tokens: set[str] = set()
    name = (row.get("student_name") or "").strip()
    if name:
        tokens.add(name)
        disp = display_name(name)
        if disp and disp != "Unknown":
            tokens.add(disp)
        first, last = parse_sortable_name(name)
        if first and last:
            tokens.add(f"{last}, {first}")
            tokens.add(f"{first} {last}")
            if len(last) >= 2:
                tokens.add(last)
        elif len(name) >= 3:
            tokens.add(name)
    netid = (row.get("student_netid") or "").strip()
    if netid:
        tokens.add(netid)
        tokens.add(f"{netid}@cornell.edu")
    return sorted((t for t in tokens if len(t) >= 2), key=len, reverse=True)


def anonymize_submission_text(text: str, row: dict[str, Any]) -> str:
    """Redact roster names, netids, and Cornell emails from submission body text."""
    if not text:
        return text
    out = text
    for token in _pii_strings(row):
        out = re.sub(re.escape(token), REDACT_PLACEHOLDER, out, flags=re.IGNORECASE)
    out = _CORNELL_EMAIL.sub(REDACT_PLACEHOLDER, out)
    netid = (row.get("student_netid") or "").strip()
    if netid:
        out = re.sub(
            rf"\b{re.escape(netid)}@[\w.-]+\b",
            REDACT_PLACEHOLDER,
            out,
            flags=re.IGNORECASE,
        )
    return out


def anonymize_llm_metadata(row: dict[str, Any]) -> dict[str, str]:
    """Assignment context only — no student names, netids, or Canvas ids."""
    out: dict[str, str] = {}
    assignment = (row.get("assignment_name") or row.get("assignment") or "").strip()
    if assignment:
        out["assignment"] = assignment
    for key in ("assignment_key", "assignment_type", "submitted_at", "attempt_number", "late"):
        val = row.get(key)
        if val is not None and str(val).strip():
            out[key if key != "attempt_number" else "attempt"] = str(val).strip()
    return out


def strip_pii_fields(data: dict[str, Any]) -> dict[str, Any]:
    """Drop known PII keys from an arbitrary metadata dict."""
    return {k: v for k, v in data.items() if k not in _PII_KEYS}
