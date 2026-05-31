#!/usr/bin/env python3
"""
push_to_canvas.py — publish the SYSEN 5470 scaffolding to a Canvas course.

It reads canvas_plan.json (produced by generate_html.py) plus the HTML
fragments in pages/ and assignments/, and creates — IDEMPOTENTLY — the
assignment groups, the front page, all 43 assignments, and the 5 modules.

  • Idempotent: every object is matched by NAME first. Re-running updates the
    existing object instead of creating a duplicate, so it is safe to run
    repeatedly while you tweak content.
  • --dry-run prints every API call it WOULD make and changes nothing.

------------------------------------------------------------------------------
REQUIRED ENVIRONMENT (do NOT hard-code your token):
    CANVAS_BASE_URL   e.g.  https://canvas.cornell.edu     (no trailing /api)
    CANVAS_API_TOKEN  a user token: Account → Settings → "+ New Access Token"
    CANVAS_COURSE_ID  the numeric id in the course URL .../courses/<ID>

USAGE:
    pip install requests
    export CANVAS_BASE_URL=https://canvas.cornell.edu
    export CANVAS_API_TOKEN=xxxxx
    export CANVAS_COURSE_ID=123456
    python3 scripts/push_to_canvas.py --dry-run     # preview the plan
    python3 scripts/push_to_canvas.py               # actually publish

See HANDOFF.md for the exact endpoint reference and order of operations.
------------------------------------------------------------------------------
"""

import os
import sys
import json
import time
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("This script needs `requests`.  Run:  pip install requests")

ROOT = Path(__file__).resolve().parent.parent
PLAN = json.loads((ROOT / "canvas_plan.json").read_text())

BASE = os.environ.get("CANVAS_BASE_URL", "").rstrip("/")
TOKEN = os.environ.get("CANVAS_API_TOKEN", "")
COURSE = os.environ.get("CANVAS_COURSE_ID", "")
DRY = "--dry-run" in sys.argv

if not DRY and not (BASE and TOKEN and COURSE):
    sys.exit("Set CANVAS_BASE_URL, CANVAS_API_TOKEN, CANVAS_COURSE_ID "
             "(or pass --dry-run).")

API = f"{BASE}/api/v1"
HEAD = {"Authorization": f"Bearer {TOKEN}"}
GRADING_TYPE = {"completion": "pass_fail", "points": "points"}


# ---------------------------------------------------------------------------
# thin REST helpers (with pagination + gentle rate-limit backoff)
# ---------------------------------------------------------------------------
def _req(method, path, **kw):
    if DRY:
        print(f"  [dry-run] {method} {path}  "
              f"{ {k: v for k, v in kw.get('data', [])} if isinstance(kw.get('data'), list) else kw.get('data', '')}")
        return {}
    for attempt in range(5):
        r = requests.request(method, f"{API}{path}", headers=HEAD, timeout=60, **kw)
        if r.status_code == 403 and "Rate" in r.text:
            time.sleep(2 ** attempt)
            continue
        if not r.ok:
            sys.exit(f"\n✗ {method} {path} -> {r.status_code}\n{r.text[:600]}")
        return r.json() if r.text else {}
    sys.exit(f"✗ rate-limited repeatedly on {method} {path}")


def get_all(path, **params):
    """GET with Canvas link-header pagination."""
    if DRY:
        return []
    out, url = [], f"{API}{path}"
    p = {"per_page": 100, **params}
    while url:
        r = requests.get(url, headers=HEAD, params=p, timeout=60)
        if not r.ok:
            sys.exit(f"✗ GET {url} -> {r.status_code}\n{r.text[:400]}")
        out.extend(r.json())
        url, p = r.links.get("next", {}).get("url"), {}
    return out


def read_html(rel):
    return (ROOT / rel).read_text()


# ---------------------------------------------------------------------------
# 1. course-level settings: turn on weighted groups + (later) wiki home
# ---------------------------------------------------------------------------
def set_course_settings():
    print("• Course settings: apply_assignment_group_weights = true")
    _req("PUT", f"/courses/{COURSE}",
         data=[("course[apply_assignment_group_weights]", "true")])


# ---------------------------------------------------------------------------
# 2. assignment groups  (match by name → update or create)
# ---------------------------------------------------------------------------
def ensure_groups():
    existing = {g["name"]: g for g in get_all(f"/courses/{COURSE}/assignment_groups")}
    key_to_id = {}
    for g in PLAN["assignment_groups"]:
        data = [("name", g["name"]),
                ("group_weight", str(g["group_weight"])),
                ("position", str(g["position"]))]
        if g["name"] in existing:
            gid = existing[g["name"]]["id"]
            print(f"• Group (update) {g['name']}  ({g['group_weight']}%)")
            _req("PUT", f"/courses/{COURSE}/assignment_groups/{gid}", data=data)
        else:
            print(f"• Group (create) {g['name']}  ({g['group_weight']}%)")
            res = _req("POST", f"/courses/{COURSE}/assignment_groups", data=data)
            gid = res.get("id", f"NEW_{g['key']}")
        key_to_id[g["key"]] = gid
    return key_to_id


# ---------------------------------------------------------------------------
# 3. front page + set it as the course home
# ---------------------------------------------------------------------------
def ensure_front_page():
    fp = PLAN["front_page"]
    body = read_html(fp["html_file"])
    data = [("wiki_page[title]", fp["title"]),
            ("wiki_page[body]", body),
            ("wiki_page[published]", "true"),
            ("wiki_page[front_page]", "true")]
    pages = {p["title"]: p for p in get_all(f"/courses/{COURSE}/pages",
                                            search_term=fp["title"])}
    if fp["title"] in pages:
        slug = pages[fp["title"]]["url"]
        print(f"• Front page (update) '{fp['title']}'")
        _req("PUT", f"/courses/{COURSE}/pages/{slug}", data=data)
    else:
        print(f"• Front page (create) '{fp['title']}'")
        _req("POST", f"/courses/{COURSE}/pages", data=data)
    print("• Course home → wiki front page")
    _req("PUT", f"/courses/{COURSE}", data=[("course[default_view]", "wiki")])


# ---------------------------------------------------------------------------
# 4. assignments  (match by name → update or create)
# ---------------------------------------------------------------------------
def ensure_assignments(group_ids):
    existing = {a["name"]: a for a in get_all(f"/courses/{COURSE}/assignments")}
    for a in PLAN["assignments"]:
        gid = group_ids.get(a["group"])
        data = [
            ("assignment[name]", a["name"]),
            ("assignment[description]", read_html(a["html_file"])),
            ("assignment[points_possible]", str(a["points"])),
            ("assignment[grading_type]", GRADING_TYPE[a["grading"]]),
            ("assignment[assignment_group_id]", str(gid)),
            ("assignment[due_at]", a["due"]),
            ("assignment[published]", "true"),
        ]
        for st in a["submission_types"]:
            data.append(("assignment[submission_types][]", st))
        if a["name"] in existing:
            aid = existing[a["name"]]["id"]
            print(f"  - assignment (update) {a['name']}")
            _req("PUT", f"/courses/{COURSE}/assignments/{aid}", data=data)
        else:
            print(f"  - assignment (create) {a['name']}")
            _req("POST", f"/courses/{COURSE}/assignments", data=data)


# ---------------------------------------------------------------------------
# 5. modules + items  (match by name; add only missing items)
# ---------------------------------------------------------------------------
def site_url(item):
    if "url" in item:
        return item["url"]
    return PLAN["site_base"] + item["path"].lstrip("/")


def ensure_modules():
    existing = {m["name"]: m for m in get_all(f"/courses/{COURSE}/modules")}
    for pos, mod in enumerate(PLAN["modules"], start=1):
        if mod["name"] in existing:
            mid = existing[mod["name"]]["id"]
            print(f"• Module (exists) {mod['name']}")
            _req("PUT", f"/courses/{COURSE}/modules/{mid}",
                 data=[("module[published]", "true"), ("module[position]", str(pos))])
        else:
            print(f"• Module (create) {mod['name']}")
            res = _req("POST", f"/courses/{COURSE}/modules",
                       data=[("module[name]", mod["name"]),
                             ("module[position]", str(pos)),
                             ("module[published]", "true")])
            mid = res.get("id", f"NEW_{pos}")
        have = {i.get("title") for i in get_all(f"/courses/{COURSE}/modules/{mid}/items")} \
            if not str(mid).startswith("NEW_") else set()
        for ipos, item in enumerate(mod["items"], start=1):
            if item["title"] in have:
                continue
            data = [("module_item[type]", item["type"]),
                    ("module_item[title]", item["title"]),
                    ("module_item[position]", str(ipos))]
            if item["type"] == "ExternalUrl":
                data += [("module_item[external_url]", site_url(item)),
                         ("module_item[new_tab]", "true"),
                         ("module_item[indent]", "1")]
            print(f"    · item {item['type']}: {item['title']}")
            _req("POST", f"/courses/{COURSE}/modules/{mid}/items", data=data)


# ---------------------------------------------------------------------------
def main():
    mode = "DRY-RUN (no changes)" if DRY else f"course {COURSE} @ {BASE}"
    print(f"\n=== SYSEN 5470 → Canvas  [{mode}] ===\n")
    set_course_settings()
    group_ids = ensure_groups()
    ensure_front_page()
    ensure_assignments(group_ids)
    ensure_modules()
    print("\n✅ Done. Open the course in Canvas and verify the home page, the "
          "Assignments index (grouped + weighted), and Modules.\n")


if __name__ == "__main__":
    main()
