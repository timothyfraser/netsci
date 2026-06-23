#!/usr/bin/env python3
"""Compare live Canvas Week 1 state against pre-pilot snapshot."""

import hashlib
import json
import sys

import requests

ROOT = __file__
sys.path.insert(0, "scripts")
from canvas_env import get_canvas_env

BASE, TOKEN, COURSE = get_canvas_env()
HEAD = {"Authorization": f"Bearer {TOKEN}"}
API = f"{BASE}/api/v1"

# Captured before pilot apply (2026-06-23)
PRE_PILOT = {
    "Learning Checks — Build a Network": {
        "due_at": "2026-07-02T13:00:00Z",
        "description_hash": "b11b6e350aa546dc",
        "override_count": 1,
    },
    "Drawing — Build a Network": {
        "due_at": "2026-06-29T13:00:00Z",
        "description_hash": "8a3456f205c1d9d1",
        "override_count": 0,
    },
    "Learning Checks — Network Statistics": {
        "due_at": "2026-07-02T13:00:00Z",
        "description_hash": "499b0b86cbf535d5",
        "override_count": 1,
    },
    "Drawing — Network Statistics": {
        "due_at": "2026-06-29T13:00:00Z",
        "description_hash": "abfc50780eaac332",
        "override_count": 0,
    },
    "Learning Checks — Centrality": {
        "due_at": "2026-06-29T13:00:00Z",
        "description_hash": "d852a8396f68ac2c",
        "override_count": 0,
    },
    "Drawing — Centrality": {
        "due_at": "2026-06-29T13:00:00Z",
        "description_hash": "6c8d0320a2122f97",
        "override_count": 0,
    },
    "Ed Discussion — Week 1": {
        "due_at": "2026-06-29T13:00:00Z",
        "description_hash": "8feb32cfdf35ee29",
        "override_count": 0,
    },
    "Office Hours — Week 1": {
        "due_at": "2026-06-25T03:59:59Z",
        "description_hash": "3bb4cd098b246a41",
        "override_count": 0,
    },
    "Project Case Study — Submission 1": {
        "due_at": "2026-06-29T13:00:00Z",
        "description_hash": "fa3c3a47f9124a06",
        "override_count": 0,
    },
}


def get_all(path, **params):
    out, url = [], f"{API}{path}"
    p = {"per_page": 100, **params}
    while url:
        r = requests.get(url, headers=HEAD, params=p, timeout=60)
        r.raise_for_status()
        out.extend(r.json())
        url, p = r.links.get("next", {}).get("url"), {}
    return out


def main():
    assigns = {a["name"]: a for a in get_all(f"/courses/{COURSE}/assignments")}
    issues = []
    for name, base in PRE_PILOT.items():
        a = assigns.get(name)
        if not a:
            issues.append(f"MISSING: {name}")
            continue
        desc = a.get("description") or ""
        h = hashlib.sha256(desc.encode()).hexdigest()[:16]
        ovs = requests.get(
            f"{API}/courses/{COURSE}/assignments/{a['id']}/overrides",
            headers=HEAD,
            timeout=60,
        ).json()
        if h != base["description_hash"]:
            issues.append(f"{name}: description changed")
        if a.get("points_possible") != 1.0 and "Project" not in name:
            issues.append(f"{name}: points changed")
        if name == "Project Case Study — Submission 1" and a.get("points_possible") != 100.0:
            issues.append(f"{name}: points changed")
        if name == "Drawing — Build a Network":
            if len(ovs) != 1:
                issues.append(f"{name}: expected 1 override, got {len(ovs)}")
            elif ovs[0].get("course_section_id") != 139822:
                issues.append(f"{name}: wrong section")
            elif ovs[0].get("due_at") != "2026-07-02T13:00:00Z":
                issues.append(f"{name}: wrong override due")
            if a.get("due_at") != "2026-07-02T13:00:00Z":
                issues.append(f"{name}: assignment due_at {a.get('due_at')}")
        else:
            if len(ovs) != base["override_count"]:
                issues.append(f"{name}: overrides {base['override_count']} -> {len(ovs)}")
            if a.get("due_at") != base["due_at"]:
                issues.append(f"{name}: due_at {base['due_at']} -> {a.get('due_at')}")

    if issues:
        print("PILOT VERIFICATION FAILED:")
        for i in issues:
            print(f"  - {i}")
        sys.exit(1)
    print("PILOT VERIFICATION PASSED")
    print("  Drawing — Build a Network: SYSEN-5940 override added (matches LC template)")
    print("  All other Week 1 targets unchanged")


if __name__ == "__main__":
    main()
