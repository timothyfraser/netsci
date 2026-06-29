"""Probe Canvas for test student and submissions."""

import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))
from env import get_canvas_env

base, token, course = get_canvas_env()
h = {"Authorization": f"Bearer {token}"}


def paginate(path: str, params: dict | None = None) -> list:
    url = f"{base}/api/v1{path}"
    out: list = []
    p = params
    while url:
        r = requests.get(url, headers=h, params=p, timeout=60)
        r.raise_for_status()
        out.extend(r.json())
        url = ""
        p = None
        for part in r.headers.get("Link", "").split(","):
            if 'rel="next"' in part:
                url = part[part.find("<") + 1 : part.find(">")]
                break
    return out


users = paginate(f"/courses/{course}/users", {"enrollment_type[]": "student", "per_page": 100})
print(f"total students: {len(users)}")
for u in users:
    name = (u.get("name") or "").lower()
    login = (u.get("login_id") or "").lower()
    sortable = (u.get("sortable_name") or "").lower()
    if any(k in name or k in login or k in sortable for k in ("test", "demo", "sample", "fraser")):
        print("MATCH", u.get("id"), u.get("name"), u.get("login_id"), u.get("sis_user_id"))

all_users = paginate(f"/courses/{course}/users", {"per_page": 100})
print(f"all enrollments: {len(all_users)}")
for u in all_users:
    name = (u.get("name") or "")
    if "test" in name.lower():
        print("ALL", u.get("id"), name, u.get("login_id"), u.get("enrollments"))

for aid, label in [(968727, "project-1"), (968728, "project-2"), (968729, "project-3")]:
    subs = paginate(
        f"/courses/{course}/assignments/{aid}/submissions",
        {"include[]": ["user"], "per_page": 100},
    )
    submitted = [s for s in subs if s.get("workflow_state") not in ("unsubmitted", "deleted")]
    print(f"\n{label} ({aid}): {len(submitted)} submitted / {len(subs)} total")
    for s in submitted:
        u = s.get("user") or {}
        print(
            " ",
            s.get("user_id"),
            u.get("name"),
            u.get("login_id"),
            s.get("workflow_state"),
            s.get("submitted_at"),
            "attachments",
            len(s.get("attachments") or []),
        )
