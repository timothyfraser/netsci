"""Dispatch Classbot review by assignment type."""

from __future__ import annotations

from typing import Any, Literal

from lc_client import run_lc_classbot_for_row
from litellm_client import DEFAULT_MODEL, run_classbot_for_row
from rubric import assignment_type


def run_classbot_for_row_typed(
    row: dict[str, str],
    *,
    model: str = DEFAULT_MODEL,
    mode: Literal["text", "pdf"] = "text",
) -> dict[str, Any]:
    atype = assignment_type(row.get("assignment_key", ""))
    if atype == "learning_checks":
        return run_lc_classbot_for_row(row, model=model)
    if atype == "project_case_study":
        return run_classbot_for_row(row, model=model, mode=mode)
    raise ValueError(f"Unsupported assignment type for Classbot: {atype}")
