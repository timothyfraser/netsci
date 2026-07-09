"""Recover report_text_override cross-contamination in grades.csv.

Clears overrides only when:
  1. The same override text appears on multiple submission_keys, AND
  2. That row's cached_text_path content does not match the override (not the owner).

Dry-run by default; pass --apply to write grades.csv.

  python scripts/recover_report_overrides.py
  python scripts/recover_report_overrides.py --apply
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from csv_store import CSV_PATH, read_rows, write_rows  # noqa: E402


def _normalize(text: str) -> str:
    return " ".join(text.split())


def read_cached(row: dict[str, str]) -> str:
    path = Path(row.get("cached_text_path", ""))
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Write cleared overrides to grades.csv")
    args = parser.parse_args()

    rows = read_rows()
    by_override: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        override = (row.get("report_text_override") or "").strip()
        if override:
            by_override[override].append(row)

    duplicate_groups = {text: group for text, group in by_override.items() if len(group) > 1}
    to_clear: list[tuple[str, str]] = []

    for override, group in duplicate_groups.items():
        norm_override = _normalize(override)
        for row in group:
            cached = read_cached(row).strip()
            if cached and _normalize(cached) == norm_override:
                continue  # this row owns the override (matches its Canvas cache)
            to_clear.append((row["submission_key"], row.get("student_name", "")))

    print(f"Duplicate override groups: {len(duplicate_groups)}")
    print(f"Rows to clear (cross-contaminated): {len(to_clear)} / {len(rows)}")
    for key, name in to_clear:
        print(f"  {name} ({key})")

    if not to_clear:
        return
    if not args.apply:
        print("\nDry run only. Re-run with --apply to clear these overrides.")
        return

    clear_keys = {key for key, _ in to_clear}
    for row in rows:
        if row["submission_key"] in clear_keys:
            row["report_text_override"] = ""
    write_rows(rows)
    print(f"\nCleared report_text_override on {len(clear_keys)} row(s) in {CSV_PATH}")


if __name__ == "__main__":
    main()
