"""Regenerate config/assignments.json from .canvas/canvas_contract.json + manifest."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parent
CONTRACT = REPO / ".canvas" / "canvas_contract.json"
MANIFEST = REPO / ".canvas" / "manifest.json"
OUT = ROOT / "config" / "assignments.json"

PROJECT_KEYS = ("project-1", "project-2", "project-3")


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cs_by_key = {c["key"]: c for c in manifest["case_studies"]}
    contract_by_key = {a["key"]: a for a in contract["assignments"]}

    assignments: list[dict] = []
    for key in PROJECT_KEYS:
        ca = contract_by_key.get(key)
        if not ca:
            continue
        assignments.append(
            {
                "key": key,
                "type": "project_case_study",
                "name": ca["name"],
                "canvas_assignment_id": ca["canvas_id"],
                "points_possible": ca.get("points_possible", 100),
            }
        )

    for cs in manifest["case_studies"]:
        lc_key = f"lc-{cs['key']}"
        ca = contract_by_key.get(lc_key)
        if not ca:
            print(f"skip missing contract entry: {lc_key}")
            continue
        assignments.append(
            {
                "key": lc_key,
                "type": "learning_checks",
                "name": ca["name"],
                "canvas_assignment_id": ca["canvas_id"],
                "points_possible": ca.get("points_possible", 1),
                "case_study_key": cs["key"],
                "lab_path": f"docs/{cs['lab']}",
                "code_path": cs["code"],
            }
        )

    payload = {
        "assignment_types": {
            "project_case_study": {
                "label": "Project case study report",
                "points_max": 100,
                "rubric": "rubric.json",
            },
            "learning_checks": {
                "label": "Learning checks (completion)",
                "points_max": 1,
            },
            "poster": {
                "label": "Final poster presentation",
                "points_max": 100,
                "status": "planned",
            },
        },
        "assignments": assignments,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(assignments)} assignments -> {OUT}")


if __name__ == "__main__":
    main()
