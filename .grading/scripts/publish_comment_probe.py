"""Verify Canvas accepts grade + HTML comment on Test Student submission."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

from canvas_client import publish_grade
from csv_store import get_row, read_rows
from prompts import compose_canvas_comment

TEST_STUDENT = "212069"


def main() -> None:
    rows = read_rows()
    row = next(
        (r for r in rows if r.get("canvas_user_id") == TEST_STUDENT and r.get("assignment_key") == "project-1"),
        None,
    )
    if not row:
        raise SystemExit("No project-1 row for Test Student — sync Canvas first")

    comment = compose_canvas_comment(
        "🧪 Probe: instructor line from dashboard.",
        "<p><strong>🤖 Classbot probe</strong></p><ul><li>✅ HTML renders</li><li>📍 Location test</li></ul>",
    )
    grade = row.get("final_grade") or row.get("proposed_score") or "88"
    print(f"Publishing grade={grade} comment_len={len(comment)} to {row['student_name']}...")
    result = publish_grade(row, grade, comment)
    comments = result.get("submission_comments") or []
    print(f"submission_comments count: {len(comments)}")
    if comments:
        latest = comments[-1]
        body = latest.get("comment") or latest.get("body") or ""
        print("Latest comment preview:", body[:200].encode("ascii", "replace").decode())
    else:
        raise SystemExit("FAIL: no submission_comments in Canvas response")

    key = row["submission_key"]
    refreshed = get_row(key)
    print("Row status:", refreshed.get("status") if refreshed else "n/a")
    print("PASS")


if __name__ == "__main__":
    main()
