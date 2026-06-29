"""End-to-end test: Canvas sync + Classbot + Playwright UI."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import requests
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))
from canvas_client import sync_assignment
from env import get_canvas_env, mock_llm_enabled
from litellm_client import run_classbot_for_row
from csv_store import get_row, read_rows

BASE = "http://127.0.0.1:8765"
TEST_STUDENT_ID = "212069"


def api(method: str, path: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Content-Type": "application/json"} if body is not None else {}
    r = requests.request(method, BASE + path, data=data, headers=headers, timeout=300)
    r.raise_for_status()
    return r.json() if r.content else {}


def canvas_test_student_state() -> dict:
    base, token, course = get_canvas_env()
    h = {"Authorization": f"Bearer {token}"}
    r = requests.get(
        f"{base}/api/v1/courses/{course}/assignments/968727/submissions/{TEST_STUDENT_ID}",
        headers=h,
        params={"include[]": ["user"]},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


def pick_target_row(rows: list[dict[str, str]]) -> dict[str, str]:
    for row in rows:
        if row.get("canvas_user_id") == TEST_STUDENT_ID and row.get("cached_text_path"):
            return row
    for row in rows:
        if row.get("cached_report_path") and row.get("cached_text_path"):
            return row
    for row in rows:
        if row.get("cached_text_path"):
            return row
    raise RuntimeError("No synced row with cached text found")


def main() -> None:
    print("=== Canvas Test Student state ===")
    ts = canvas_test_student_state()
    user = ts.get("user") or {}
    print(
        f"Test Student ({user.get('name')}): workflow={ts.get('workflow_state')}, "
        f"attachments={len(ts.get('attachments') or [])}"
    )

    print("\n=== Sync project-1 from Canvas ===")
    rows = sync_assignment("project-1", force=False)
    print(f"synced {len(rows)} rows")
    test_rows = [r for r in rows if r.get("canvas_user_id") == TEST_STUDENT_ID]
    if test_rows:
        target = test_rows[0]
        print("Test Student row in CSV:", target.get("submission_key"))
    else:
        target = pick_target_row(rows)
        print(
            "Test Student unsubmitted — using real submission:",
            target.get("student_name"),
            target.get("submission_key"),
        )

    key = target["submission_key"]
    text_path = Path(target.get("cached_text_path", ""))
    assert text_path.is_file(), f"Missing cached text: {text_path}"
    assert len(text_path.read_text(encoding="utf-8")) > 100, "Cached text too short"

    print("\n=== Classbot review ===")
    if mock_llm_enabled():
        print("MOCK_LLM=1 — using fixture")
    else:
        print("Calling Cornell AI Gateway (Haiku)...")
    result = run_classbot_for_row(target, model="claude-haiku-4-5", mode="text")
    from csv_store import patch_row

    patch_row(key, {k: v for k, v in result.items() if k != "review"})
    row = get_row(key)
    assert row["llm_status"] == "done", row.get("llm_status")
    assert row.get("classbot_comment"), "missing classbot comment"
    print("proposed_score", row.get("proposed_score"))

    print("\n=== Playwright UI ===")
    errors: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(BASE + "/", wait_until="networkidle")
        page.select_option("#filter-assignment", "project-1")
        page.wait_for_timeout(500)
        # click row matching student name
        name = row["student_name"].split(",")[0].strip()
        item = page.locator(".queue-item", has_text=name).first
        assert item.count() > 0, f"Queue item not found for {name}"
        item.click()
        page.wait_for_selector("#btn-save")
        preview = page.locator("#report-preview").inner_text()
        assert len(preview) > 50, "Report preview empty"
        assert page.locator(".req-row").count() >= 1, "No requirement rows"
        page.fill("#instructor-comment", "E2E test comment from Playwright.")
        page.click("#btn-save")
        page.wait_for_timeout(1000)
        detail = api("GET", f"/api/rows/{key}")
        assert detail["row"]["status"] == "reviewed"
        assert "E2E test comment" in detail["row"]["instructor_comment"]
        page.click("#btn-publish")
        page.wait_for_selector("#modal-preview")
        modal = page.locator("#modal-preview").inner_text()
        assert "AI API Gateway" in modal
        page.click("#modal-cancel")
        browser.close()

    assert not errors, errors
    print("\nE2E PASS")


if __name__ == "__main__":
    main()
