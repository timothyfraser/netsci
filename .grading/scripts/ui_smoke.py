"""Playwright browser smoke test for dashboard UI."""

from playwright.sync_api import sync_playwright


def main() -> None:
    errors: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.on("pageerror", lambda e: errors.append(f"PAGE: {e}"))
        page.on("console", lambda m: errors.append(f"CONSOLE: {m.text}") if m.type == "error" else None)
        page.goto("http://127.0.0.1:8765/", wait_until="networkidle")
        page.wait_for_selector("#queue-list .queue-item, #queue-list .placeholder")
        if page.locator(".queue-item").count() == 0:
            page.click("#btn-seed")
            page.wait_for_selector(".queue-item")
        page.locator(".queue-item").first.click()
        page.wait_for_selector("#btn-save")
        grade_before = page.locator("#final-grade").input_value()
        first = page.locator(".req-accept").first
        first.set_checked(not first.is_checked())
        page.click("#btn-save")
        page.wait_for_timeout(1200)
        row = page.evaluate(
            """async () => {
            const r = await fetch('/api/rows/project-1_99999_a1');
            return r.json();
        }"""
        )
        page.fill("#issue-search", "github")
        page.wait_for_timeout(200)
        issue_count = page.locator(".issue-card").count()
        page.click("#btn-publish")
        page.wait_for_selector("#modal-preview")
        modal = page.locator("#modal-preview").text_content() or ""
        page.click("#modal-cancel")
        title = page.title()
        browser.close()

    assert "Classbot" in (title or ""), "unexpected page title"
    assert row["row"]["status"] == "reviewed", "row should be reviewed after save"
    assert issue_count >= 1, "issue search should show github issue"
    assert "AI API Gateway" in modal, "publish modal missing disclosure"
    assert not errors, f"browser errors: {errors}"
    print("ui_smoke OK", {"grade_before": grade_before, "final_grade": row["row"]["final_grade"]})


if __name__ == "__main__":
    main()
