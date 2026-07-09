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
                "classbot": {
                    "context_label": "Context for Classbot",
                    "context_hint": (
                        "Editable — add report text or notes the student gave outside Canvas. "
                        "Saved with this row; Re-run Classbot reviews this text (anonymized), "
                        "not the cached PDF extraction alone."
                    ),
                    "context_placeholder": "Paste or edit the report text Classbot should review…",
                    "show_report_checklist": True,
                    "show_requirements": True,
                    "show_top_issues": True,
                    "show_lc_checks": False,
                },
            },
            "learning_checks": {
                "label": "Learning checks (completion)",
                "points_max": 1,
                "classbot": {
                    "context_label": "Context for Classbot",
                    "context_hint": (
                        "Editable — correct or supplement the student's LC answers if Canvas "
                        "extraction missed anything. Saved with this row; Re-run Classbot uses this text."
                    ),
                    "context_placeholder": "LC1: B\nLC2: …\nCode output: 3",
                    "show_report_checklist": False,
                    "show_requirements": False,
                    "show_top_issues": False,
                    "show_lc_checks": True,
                },
            },
            "poster": {
                "label": "Final poster presentation",
                "points_max": 100,
                "status": "planned",
                "classbot": {
                    "context_label": "Context for Classbot",
                    "context_hint": "Editable — add poster notes or submission context for Classbot.",
                    "context_placeholder": "Paste submission context for Classbot…",
                    "show_report_checklist": False,
                    "show_requirements": False,
                    "show_top_issues": False,
                    "show_lc_checks": False,
                },
            },
        },
        "assignments": assignments,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(assignments)} assignments -> {OUT}")


if __name__ == "__main__":
    main()
