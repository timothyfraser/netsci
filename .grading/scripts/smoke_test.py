"""Headless UI smoke test for Classbot dashboard (MOCK_LLM=1)."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request


BASE = "http://127.0.0.1:8765"


def req(method: str, path: str, body: dict | None = None) -> dict:
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    r = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    cfg = req("GET", "/api/config")
    assert cfg.get("mock_llm") is True, "MOCK_LLM should be enabled for smoke test"
    req("POST", "/api/seed-demo")
    req("POST", "/api/classbot/project-1_99999_a1", {"model": "claude-haiku-4-5", "mode": "text"})
    detail = req("GET", "/api/rows/project-1_99999_a1")
    deductions = detail["deductions"]
    assert deductions, "expected deductions from classbot"
    for d in deductions:
        d["accepted"] = not d.get("accepted", False)
    patched = req(
        "PATCH",
        "/api/rows/project-1_99999_a1",
        {
            "accepted_deductions_json": json.dumps(deductions),
            "instructor_comment": "Nice operationalization.",
            "status": "reviewed",
        },
    )
    assert patched["status"] == "reviewed"
    assert patched["instructor_comment"] == "Nice operationalization."
    html = urllib.request.urlopen(BASE + "/", timeout=30).read().decode("utf-8")
    assert "Classbot Grading" in html
    assert "/static/app.js" in html
    print("smoke_test OK")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except urllib.error.URLError as exc:
        print(f"Server not reachable at {BASE}: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
