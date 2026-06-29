"""Compare Canvas submitted rows vs CSV and text cache coverage."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

from canvas_client import _api_paginated
from csv_store import read_rows
from env import get_canvas_env


def main() -> None:
    _, _, course = get_canvas_env()
    aid = 968727
    subs = _api_paginated(
        f"/courses/{course}/assignments/{aid}/submissions",
        {"include[]": ["user"], "per_page": 100},
    )
    submitted = [s for s in subs if s.get("workflow_state") not in ("unsubmitted", "deleted")]
    csv = {r["canvas_user_id"]: r for r in read_rows() if r.get("assignment_key") == "project-1"}

    print(f"Canvas submitted: {len(submitted)}")
    print(f"CSV project-1 rows: {len(csv)}")
    print()

    for s in sorted(submitted, key=lambda x: ((x.get("user") or {}).get("sortable_name") or "")):
        u = s.get("user") or {}
        uid = str(s.get("user_id"))
        name = u.get("sortable_name") or u.get("name")
        row = csv.get(uid)
        atts = s.get("attachments") or []
        fnames = [a.get("filename") for a in atts]
        ws = s.get("workflow_state")
        sat = s.get("submitted_at")
        if not row:
            print(f"MISSING CSV  {name} ({uid}) ws={ws} files={fnames}")
            continue
        has_text = bool(row.get("cached_text_path") and Path(row["cached_text_path"]).is_file())
        if not has_text:
            print(f"NO TEXT      {name} ({uid}) ws={ws} at={sat} files={fnames}")
        else:
            print(f"OK           {name} ws={ws}")

    extra = set(csv) - {str(s.get("user_id")) for s in submitted}
    for uid in extra:
        print(f"CSV ONLY     {csv[uid].get('student_name')} ({uid})")


if __name__ == "__main__":
    main()
