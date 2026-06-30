"""Submit sample Learning Check text as Canvas Test Student."""

from __future__ import annotations

import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))
from env import get_canvas_env

TEST_USER_ID = 212069
ASSIGNMENT_ID = 968700  # lc-build-a-network

BODY = """LC1: B
LC2: B
LC3: C

Learning Check answer: 3
"""


def main() -> None:
    base, token, course = get_canvas_env()
    h = {"Authorization": f"Bearer {token}"}
    sub_url = f"{base}/api/v1/courses/{course}/assignments/{ASSIGNMENT_ID}/submissions/{TEST_USER_ID}"
    cur = requests.get(sub_url, headers=h, timeout=60)
    cur.raise_for_status()
    cur_data = cur.json()
    if cur_data.get("workflow_state") not in ("unsubmitted", None) and cur_data.get("submitted_at"):
        print("Test Student already submitted LC:", cur_data.get("submitted_at"))
        print((cur_data.get("body") or "")[:300])
        return

    post_url = f"{base}/api/v1/courses/{course}/assignments/{ASSIGNMENT_ID}/submissions?user_id={TEST_USER_ID}"
    payload = {
        "submission": {
            "submission_type": "online_text_entry",
            "body": BODY,
        }
    }
    resp = requests.post(post_url, headers=h, json=payload, timeout=120)
    resp.raise_for_status()
    sub = resp.json()
    print("submitted", sub.get("workflow_state"), sub.get("submitted_at"))
    print("body preview:", (sub.get("body") or "")[:200])


if __name__ == "__main__":
    main()
