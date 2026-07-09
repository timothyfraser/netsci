"""Derive filterable queue tags from a grade row."""

from __future__ import annotations

from typing import Any


def row_tags(row: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    status = (row.get("status") or "synced").strip() or "synced"
    tags.append(status)

    if row.get("late") == "true":
        tags.append("late")

    has_text = bool((row.get("cached_text_path") or "").strip())
    if not has_text:
        tags.append("no-text")
    else:
        tags.append("has-text")

    llm = (row.get("llm_status") or "pending").strip() or "pending"
    if llm == "pending" or (has_text and not (row.get("llm_review_path") or "").strip()):
        tags.append("classbot-pending")
    elif llm == "done":
        tags.append("classbot-done")
    elif llm == "error":
        tags.append("classbot-error")

    return tags


def row_matches_tag_filters(
    row: dict[str, Any],
    *,
    exclude_tags: set[str] | None = None,
    require_tag: str | None = None,
) -> bool:
    tags = set(row_tags(row))
    if exclude_tags and tags & exclude_tags:
        return False
    if require_tag and require_tag not in tags:
        return False
    return True
