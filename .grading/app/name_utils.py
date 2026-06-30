"""Format Canvas sortable names (Last, First) for display and prompts."""

from __future__ import annotations


def parse_sortable_name(raw: str) -> tuple[str, str]:
    """Return (first_name, last_name) from 'Last, First' or plain 'First Last'."""
    raw = (raw or "").strip()
    if not raw:
        return "", ""
    if "," in raw:
        last, first = raw.split(",", 1)
        return first.strip(), last.strip()
    parts = raw.split()
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


def first_name(raw: str) -> str:
    first, _ = parse_sortable_name(raw)
    return first or raw.strip()


def display_name(raw: str) -> str:
    """'Smith, Jane' -> 'Jane Smith'; fallback to raw."""
    first, last = parse_sortable_name(raw)
    if first and last:
        return f"{first} {last}"
    return raw.strip() or "Unknown"
