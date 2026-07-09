"""Build gitignored LC answer keys from case-study HTML (+ code metadata).

Output: .grading/cache/lc_answer_keys.json

Run after editing docs/case-studies/*.html:
  python scripts/build_lc_answer_keys.py

Also run scripts/build_lc_code_keys.py for numeric "I ran the code" answers.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app"
if str(APP) not in sys.path:
    sys.path.insert(0, str(APP))

from lc_sources import build_lc_reference, validate_lc_reference  # noqa: E402

CONFIG = ROOT / "config" / "assignments.json"
OUT = ROOT / "cache" / "lc_answer_keys.json"


def main() -> int:
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    assignments: dict[str, object] = {}
    all_errors: list[str] = []

    for assignment in cfg.get("assignments", []):
        if assignment.get("type") != "learning_checks":
            continue
        akey = assignment["key"]
        ref = build_lc_reference(assignment)
        errors = validate_lc_reference(ref)
        if errors:
            all_errors.extend(errors)
        assignments[akey] = ref
        n = len(ref.get("learning_checks") or [])
        print(f"OK {akey}: {n} learning check(s)")

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "assignments": assignments,
    }
    if all_errors:
        payload["validation_errors"] = all_errors

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {OUT} ({len(assignments)} assignments)")

    if all_errors:
        print("\nValidation errors:", file=sys.stderr)
        for err in all_errors:
            print(f"  {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
