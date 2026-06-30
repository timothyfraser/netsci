"""Sync LC assignment for Test Student, run Classbot, print draft grade + comment."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

from canvas_client import sync_assignment
from csv_store import get_row, patch_row, upsert_row
from env import GRADING_ROOT, mock_llm_enabled
from lc_prompts import compose_lc_canvas_comment
from review_runner import run_classbot_for_row_typed
from rubric import get_assignment

TEST_STUDENT = "212069"
ASSIGNMENT = "lc-build-a-network"
SAMPLE_BODY = """LC1: B
LC2: B
LC3: C

Learning Check answer: 3
"""


def seed_demo_row() -> dict[str, str]:
    assignment = get_assignment(ASSIGNMENT)
    if not assignment:
        raise SystemExit(f"Missing assignment config: {ASSIGNMENT}")
    cache_dir = GRADING_ROOT / "cache" / "submissions" / ASSIGNMENT / TEST_STUDENT
    cache_dir.mkdir(parents=True, exist_ok=True)
    text_path = cache_dir / "report.txt"
    text_path.write_text(SAMPLE_BODY, encoding="utf-8")
    return upsert_row(
        {
            "submission_key": f"{ASSIGNMENT}_{TEST_STUDENT}_a1",
            "student_name": "Student, Test",
            "student_netid": "teststudent",
            "canvas_user_id": TEST_STUDENT,
            "canvas_submission_id": "demo",
            "assignment_key": ASSIGNMENT,
            "assignment_name": assignment["name"],
            "assignment_type": "learning_checks",
            "canvas_assignment_id": str(assignment["canvas_assignment_id"]),
            "submitted_at": "2026-06-29T18:00:00Z",
            "attempt_number": "1",
            "late": "false",
            "workflow_state": "submitted",
            "cached_dir": str(cache_dir),
            "cached_report_path": "",
            "cached_text_path": str(text_path),
            "llm_status": "pending",
            "status": "synced",
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="Use local demo row (Canvas Test Student cannot submit via API)")
    args = parser.parse_args()

    target = None
    if not args.demo:
        print("=== Sync", ASSIGNMENT, "===")
        rows = sync_assignment(ASSIGNMENT, force=True)
        target = next((r for r in rows if r.get("canvas_user_id") == TEST_STUDENT), None)

    if not target:
        print("Using local demo row (Test Student API submit returns 403).")
        target = seed_demo_row()

    key = target["submission_key"]
    text = Path(target.get("cached_text_path", ""))
    print("submission_key:", key)
    print("cached text len:", len(text.read_text(encoding="utf-8")) if text.is_file() else 0)
    if text.is_file():
        print("--- submission preview ---")
        print(text.read_text(encoding="utf-8")[:500])
        print("---")

    print("\n=== Classbot LC review ===")
    if mock_llm_enabled():
        print("(MOCK_LLM=1 — fixture)")
    result = run_classbot_for_row_typed(target, model="claude-haiku-4-5", mode="text")
    review = result.pop("review", None)
    patch_row(key, {k: v for k, v in result.items() if k != "review"})
    row = get_row(key) or target

    grade = row.get("final_grade") or row.get("proposed_score") or "?"
    comment_html = row.get("classbot_comment") or ""
    full = compose_lc_canvas_comment("", comment_html)

    def safe_print(s: str) -> None:
        sys.stdout.buffer.write((s + "\n").encode("utf-8", errors="replace"))

    safe_print("\n=== DRAFT (Test Student) ===")
    safe_print(f"Grade: {grade} / 1")
    safe_print("\nClassbot HTML comment:\n" + comment_html)
    safe_print("\n--- Full Canvas comment preview ---")
    plain = re.sub(r"<[^>]+>", "", full)
    plain = plain.replace("&nbsp;", " ")
    safe_print(plain[:2000])
    if review:
        print("\n--- Review JSON ---")
        print(json.dumps(review, indent=2)[:1500])


if __name__ == "__main__":
    main()
