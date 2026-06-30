"""Load rubric and compute scores from accepted deductions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from env import GRADING_ROOT

RUBRIC_PATH = GRADING_ROOT / "config" / "rubric.json"
ASSIGNMENTS_PATH = GRADING_ROOT / "config" / "assignments.json"


def load_rubric() -> dict[str, Any]:
    return json.loads(RUBRIC_PATH.read_text(encoding="utf-8"))


def load_assignments() -> list[dict[str, Any]]:
    data = json.loads(ASSIGNMENTS_PATH.read_text(encoding="utf-8"))
    return data.get("assignments", data if isinstance(data, list) else [])


def load_assignment_types() -> dict[str, Any]:
    data = json.loads(ASSIGNMENTS_PATH.read_text(encoding="utf-8"))
    return data.get("assignment_types", {})


def assignment_type(key: str) -> str:
    a = get_assignment(key)
    return (a or {}).get("type", "project_case_study")


def points_possible(key: str) -> int:
    a = get_assignment(key)
    if not a:
        return 100
    return int(a.get("points_possible", 100))


def get_assignment(key: str) -> dict[str, Any] | None:
    for a in load_assignments():
        if a["key"] == key:
            return a
    return None


def max_deduction_map() -> dict[str, int]:
    rubric = load_rubric()
    return {r["id"]: int(r["max_deduction"]) for r in rubric["requirements"]}


def compute_score(
    accepted_deductions: list[dict[str, Any]],
    starting_score: int | None = None,
) -> int:
    rubric = load_rubric()
    start = starting_score if starting_score is not None else int(rubric["starting_score"])
    caps = max_deduction_map()
    total = 0
    for item in accepted_deductions:
        if not item.get("accepted"):
            continue
        req_id = item.get("id", "")
        amount = int(item.get("deduction", item.get("proposed_deduction", 0)) or 0)
        cap = caps.get(req_id, amount)
        total += min(max(amount, 0), cap)
    return max(0, min(start, start - total))
