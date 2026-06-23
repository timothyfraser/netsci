#!/usr/bin/env python3
"""One-off inspection: template overrides + Week 1 baseline snapshot."""

import hashlib
import json
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from canvas_env import get_canvas_env

BASE, TOKEN, COURSE = get_canvas_env()
HEAD = {"Authorization": f"Bearer {TOKEN}"}
API = f"{BASE}/api/v1"


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
    secs = get_all(f"/courses/{COURSE}/sections")
    print("SECTIONS:")
    print(json.dumps(
        [{k: s.get(k) for k in ("id", "name", "sis_section_id")} for s in secs],
        indent=2,
    ))

    lc = assigns["Learning Checks — Build a Network"]
    print("\nLC BUILD A NETWORK:")
    print(json.dumps(
        {k: lc.get(k) for k in ("id", "name", "due_at", "lock_at", "points_possible", "grading_type", "published")},
        indent=2,
    ))
    ov = requests.get(
        f"{API}/courses/{COURSE}/assignments/{lc['id']}/overrides",
        headers=HEAD,
        timeout=60,
    )
    ov.raise_for_status()
    print("\nLC OVERRIDES:")
    print(json.dumps(ov.json(), indent=2))

    targets = [
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
    baseline = {}
    for name in targets:
        a = assigns.get(name)
        if not a:
            print(f"MISSING: {name}")
            continue
        aid = a["id"]
        ovs = requests.get(
            f"{API}/courses/{COURSE}/assignments/{aid}/overrides",
            headers=HEAD,
            timeout=60,
        ).json()
        desc = a.get("description") or ""
        baseline[name] = {
            "id": aid,
            "due_at": a.get("due_at"),
            "points_possible": a.get("points_possible"),
            "grading_type": a.get("grading_type"),
            "published": a.get("published"),
            "description_len": len(desc),
            "description_hash": hashlib.sha256(desc.encode()).hexdigest()[:16],
            "overrides": ovs,
        }
    out = ROOT / "baseline_week1.json"
    out.write_text(json.dumps(baseline, indent=2), encoding="utf-8")
    print(f"\nWrote baseline to {out}")


if __name__ == "__main__":
    main()
