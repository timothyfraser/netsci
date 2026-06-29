"""Playwright MCP-equivalent UI test against live dashboard + Canvas-synced data."""

from __future__ import annotations

import json
import urllib.request

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8765"


def api_get(path: str) -> dict:
    with urllib.request.urlopen(BASE + path, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> None:
    errors: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(BASE + "/", wait_until="networkidle")
        page.select_option("#filter-assignment", "project-1")
        page.wait_for_timeout(800)
        queue_text = page.locator("#queue-list").inner_text()
        has_test_student = "Test Student" in queue_text
        rows = api_get("/api/rows?assignment_key=project-1")
        target = next(
            (r for r in rows if r.get("cached_text_path") and r.get("llm_status") == "done"),
            rows[0] if rows else None,
        )
        assert target, "no rows in queue"
        name = (target.get("student_name") or "").split(",")[0].strip()
        page.locator(".queue-item", has_text=name).first.click()
        page.wait_for_selector("#btn-save")
        assert len(page.locator("#report-preview").inner_text()) > 100
        assert page.locator(".req-row").count() >= 1
        assert int(page.locator("#final-grade").input_value() or "0") > 0
        assert len(page.locator("#classbot-comment").input_value()) > 20
        page.fill("#issue-search", "github")
        page.wait_for_timeout(300)
        page.fill("#instructor-comment", "Playwright MCP verification comment.")
        page.click("#btn-save")
        page.wait_for_timeout(1200)
        detail = api_get(f"/api/rows/{target['submission_key']}")
        assert detail["row"]["status"] == "reviewed"
        page.click("#btn-publish")
        page.wait_for_selector("#modal-preview")
        modal = page.locator("#modal-preview").inner_text()
        assert "AI API Gateway" in modal
        page.click("#modal-cancel")
        browser.close()

    cfg = api_get("/api/config")
    print(
        json.dumps(
            {
                "pass": True,
                "mock_llm_server_flag": cfg.get("mock_llm"),
                "test_student_in_queue": has_test_student,
                "test_student_note": "Canvas Test Student (id 212069) is unsubmitted; queue uses real synced submissions.",
                "reviewed_row": detail["row"]["student_name"],
                "final_grade": detail["row"]["final_grade"],
                "llm_status": detail["row"]["llm_status"],
                "errors": errors,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
