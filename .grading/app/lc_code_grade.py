"""Deterministic grading for LC 'I ran the code' numeric answers."""

from __future__ import annotations

import math
import re
from typing import Any

# Relative slack for Monte Carlo / stochastic labs (different set.seed).
DEFAULT_RTOL = 0.06
# Absolute slack for small magnitudes (e.g. p-values, correlations near 0–1).
DEFAULT_ATOL = 0.02

_NUMERIC_TOKEN = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")
_LC_ANSWER_LINE = re.compile(
    r"Learning Check answer[^:\n]*:\s*(.+?)(?:\n|$)",
    re.IGNORECASE,
)


def parse_numeric_tokens(value: str) -> list[float]:
    return [float(m) for m in _NUMERIC_TOKEN.findall(value or "")]


def extract_student_code_value(submission_text: str) -> str:
    """Best-effort parse of the student's printed code answer from Canvas text."""
    text = submission_text or ""
    match = _LC_ANSWER_LINE.search(text)
    if match:
        return match.group(1).strip()
    # Fallback: line after "ran the code" / "code output"
    for line in text.splitlines():
        low = line.lower()
        if "ran the code" in low or "code output" in low:
            nums = _NUMERIC_TOKEN.findall(line)
            if nums:
                return nums[-1]
            parts = line.split(":", 1)
            if len(parts) == 2 and parts[1].strip():
                return parts[1].strip()
    return ""


def numeric_tokens_close(
    student_tokens: list[float],
    expected_tokens: list[float],
    *,
    rtol: float = DEFAULT_RTOL,
    atol: float = DEFAULT_ATOL,
) -> bool:
    if not student_tokens or not expected_tokens:
        return False
    if len(student_tokens) == len(expected_tokens):
        return all(math.isclose(a, b, rel_tol=rtol, abs_tol=atol) for a, b in zip(student_tokens, expected_tokens))
    # Student pasted one number; key has one number buried in prose.
    if len(student_tokens) == 1 and len(expected_tokens) == 1:
        return math.isclose(student_tokens[0], expected_tokens[0], rel_tol=rtol, abs_tol=atol)
    if len(student_tokens) == 1 and len(expected_tokens) > 1:
        return any(math.isclose(student_tokens[0], b, rel_tol=rtol, abs_tol=atol) for b in expected_tokens)
    return False


def code_values_match(student: str, expected: str) -> bool:
    """True when student code output matches expected (format-tolerant, seed-tolerant)."""
    student = (student or "").strip()
    expected = (expected or "").strip()
    if not student or not expected:
        return False

    s_nums = parse_numeric_tokens(student)
    e_nums = parse_numeric_tokens(expected)
    if s_nums and e_nums:
        return numeric_tokens_close(s_nums, e_nums)
    return student.lower() == expected.lower()


def normalize_lc_code_answer(
    review: dict[str, Any],
    reference: dict[str, Any],
    submission_text: str,
) -> dict[str, Any]:
    """Override LLM code verdict when numeric comparison says the answer is close enough."""
    code_check = reference.get("code_check") or {}
    expected = str(code_check.get("expected_value") or "").strip()
    if not expected:
        return review

    code = dict(review.get("code_answer") or {})
    student = str(code.get("student_value") or "").strip()
    if not student:
        student = extract_student_code_value(submission_text)
        if student:
            code["student_value"] = student

    if not student:
        return review

    if code_values_match(student, expected):
        was_incorrect = code.get("verdict") == "incorrect"
        code["verdict"] = "correct"
        if not code.get("expected_summary"):
            code["expected_summary"] = expected
        if was_incorrect or "❌" in str(code.get("feedback", "")):
            code["feedback"] = (
                "👍 Matches expected output within tolerance "
                "(small differences from set.seed / formatting are OK)."
            )
        review["code_answer"] = code
        _maybe_restore_completion_grade(review)
    return review


def _maybe_restore_completion_grade(review: dict[str, Any]) -> None:
    """Completion LC: don't withhold 1pt when only code was wrongly marked incorrect."""
    checks = review.get("checks") or []
    wrong_checks = sum(1 for c in checks if c.get("verdict") == "incorrect")
    code = (review.get("code_answer") or {}).get("verdict")
    if wrong_checks <= 1 and code == "correct":
        review["proposed_grade"] = "1"
