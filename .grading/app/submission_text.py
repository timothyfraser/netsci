"""Read submission / Classbot context text for display and LLM review."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def read_cached_submission_text(row: dict[str, Any]) -> str:
    """Plain text extracted from Canvas sync (cached file only)."""
    path = Path(row.get("cached_text_path", ""))
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def read_submission_text(row: dict[str, Any]) -> str:
    """Classbot context: instructor override if set, else cached Canvas extraction."""
    override = (row.get("report_text_override") or "").strip()
    if override:
        return override
    return read_cached_submission_text(row)


def has_report_override(row: dict[str, Any]) -> bool:
    return bool((row.get("report_text_override") or "").strip())
