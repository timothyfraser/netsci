"""Sync and Classbot-run Test Student submission for real."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

from canvas_client import sync_assignment
from csv_store import get_row, patch_row, read_rows
from env import load_env, mock_llm_enabled
from litellm_client import run_classbot_for_row

TEST_STUDENT_ID = "212069"


def main() -> None:
    load_env()
    if mock_llm_enabled():
        print("WARNING: MOCK_LLM is set — unset for real gateway calls")

    print("Syncing project-1 from Canvas...")
    rows = sync_assignment("project-1", force=True)
    test = [r for r in rows if r.get("canvas_user_id") == TEST_STUDENT_ID]
    if not test:
        all_rows = read_rows()
        test = [r for r in all_rows if r.get("canvas_user_id") == TEST_STUDENT_ID]
    if not test:
        raise SystemExit("Test Student row not found after sync")
    row = test[0]
    key = row["submission_key"]
    print(f"Row: {key}")
    print(f"  name: {row.get('student_name')}")
    print(f"  report: {row.get('cached_report_path')}")
    print(f"  text:   {row.get('cached_text_path')}")

    text_path = Path(row.get("cached_text_path", ""))
    if text_path.is_file():
        preview = text_path.read_text(encoding="utf-8", errors="replace")[:400]
        print(f"  text preview ({text_path.stat().st_size} bytes):\n{preview}\n...")

    print("\nRunning Classbot (claude-haiku-4-5, real gateway)...")
    result = run_classbot_for_row(row, model="claude-haiku-4-5", mode="text")
    review = result.pop("review", None)
    updated = patch_row(key, result)
    print(f"  llm_status: {updated.get('llm_status')}")
    print(f"  proposed_score: {updated.get('proposed_score')}")
    print(f"  classbot_comment preview:\n{(updated.get('classbot_comment') or '')[:500]}...")
    if review:
        print(f"  top_issues: {len(review.get('top_issues', []))}")
        for issue in review.get("top_issues", []):
            print(f"    #{issue.get('rank')} {issue.get('title')} [{issue.get('search_hint')}]")
    print("\nDone. Open http://127.0.0.1:8765 and select Test Student in the queue.")


if __name__ == "__main__":
    main()
