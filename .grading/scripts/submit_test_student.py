"""Submit sample project-1 report as Canvas Test Student for E2E testing."""

from __future__ import annotations

import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))
from env import get_canvas_env

TEST_USER_ID = 212069
ASSIGNMENT_ID = 968727
SAMPLE_PDF = Path(__file__).resolve().parents[2] / "docs" / "assignments" / "sample-report.pdf"

BODY = """SYSEN 5470 — Self-check 2026-06-29
[x] Project report fills at least 5 pages
[x] Report includes the question in one sentence
[x] GitHub repo URL ready to paste

GitHub: https://github.com/timothyfraser/netsci/tree/main/code/04_centrality

What I did this week: Applied centrality analysis to my project network using betweenness and degree.
"""


def upload_file(base: str, token: str, course: str, pdf_path: Path) -> int:
    h = {"Authorization": f"Bearer {token}"}
    init = requests.post(
        f"{base}/api/v1/courses/{course}/files",
        headers=h,
        data={
            "name": pdf_path.name,
            "content_type": "application/pdf",
            "parent_folder_path": "Classbot E2E Tests",
            "published": "true",
        },
        timeout=60,
    )
    init.raise_for_status()
    spec = init.json()
    upload_url = spec["upload_url"]
    with pdf_path.open("rb") as f:
        up = requests.post(
            upload_url,
            data=spec.get("upload_params") or {},
            files={"file": (pdf_path.name, f, "application/pdf")},
            timeout=180,
        )
    up.raise_for_status()
    file_obj = up.json()
    if "id" in file_obj:
        return int(file_obj["id"])
    if "location" in up.headers:
        loc = up.headers["location"]
        meta = requests.get(loc, headers=h, timeout=60)
        meta.raise_for_status()
        return int(meta.json()["id"])
    raise RuntimeError(f"Unexpected upload response: {file_obj}")


def main() -> None:
    base, token, course = get_canvas_env()
    h = {"Authorization": f"Bearer {token}"}
    if not SAMPLE_PDF.is_file():
        raise SystemExit(f"Missing sample PDF: {SAMPLE_PDF}")

    sub_url = f"{base}/api/v1/courses/{course}/assignments/{ASSIGNMENT_ID}/submissions/{TEST_USER_ID}"
    cur = requests.get(sub_url, headers=h, timeout=60)
    cur.raise_for_status()
    cur_data = cur.json()
    if cur_data.get("workflow_state") not in ("unsubmitted", None) and cur_data.get("submitted_at"):
        print("Test Student already has a submission:", cur_data.get("submitted_at"))
        return

    file_id = upload_file(base, token, course, SAMPLE_PDF)
    print("uploaded file", file_id)

    payload = {
        "submission": {
            "submission_type": "online_upload",
            "body": BODY,
            "file_ids": [file_id],
        }
    }
    post_url = f"{base}/api/v1/courses/{course}/assignments/{ASSIGNMENT_ID}/submissions?user_id={TEST_USER_ID}"
    resp = requests.post(post_url, headers=h, json=payload, timeout=120)
    resp.raise_for_status()
    sub = resp.json()
    print(
        "submitted",
        sub.get("workflow_state"),
        sub.get("submitted_at"),
        "attachments",
        len(sub.get("attachments") or []),
    )


if __name__ == "__main__":
    main()
