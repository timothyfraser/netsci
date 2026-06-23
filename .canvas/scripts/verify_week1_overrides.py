#!/usr/bin/env python3
"""Verify all 9 Week 1 assignments have SYSEN-5940 override."""

import sys

import requests

sys.path.insert(0, "scripts")
from canvas_env import get_canvas_env

BASE, TOKEN, COURSE = get_canvas_env()
HEAD = {"Authorization": f"Bearer {TOKEN}"}
API = f"{BASE}/api/v1"

NAMES = [
    "Learning Checks — Build a Network",
    "Drawing — Build a Network",
    "Learning Checks — Network Statistics",
    "Drawing — Network Statistics",
    "Learning Checks — Centrality",
    "Drawing — Centrality",
    "Ed Discussion — Week 1",
    "Office Hours — Week 1",
    "Project Case Study — Submission 1",
]
EXPECTED = "2026-07-02T13:00:00Z"
SECTION_ID = 139822


def main():
    assigns = {
        a["name"]: a
        for a in requests.get(
            f"{API}/courses/{COURSE}/assignments",
            headers=HEAD,
            params={"per_page": 100},
            timeout=60,
        ).json()
    }
    ok = 0
    for name in NAMES:
        a = assigns[name]
        ovs = requests.get(
            f"{API}/courses/{COURSE}/assignments/{a['id']}/overrides",
            headers=HEAD,
            timeout=60,
        ).json()
        match = next(
            (o for o in ovs if o.get("course_section_id") == SECTION_ID),
            None,
        )
        if match and match.get("due_at") == EXPECTED:
            print(f"OK  {name}")
            ok += 1
        else:
            print(f"FAIL {name}  overrides={ovs}")
    print(f"\n{ok}/{len(NAMES)} assignments have SYSEN-5940 due {EXPECTED}")
    sys.exit(0 if ok == len(NAMES) else 1)


if __name__ == "__main__":
    main()
