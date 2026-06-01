#!/usr/bin/env python3
"""
sync_contract.py — keep a local "contract" of due dates / points / group
weights in sync with a Canvas course, BOTH directions.

The contract (canvas_contract.json) is the durable, human-editable source of
truth for *intent*: when each assignment is due, how many points it's worth,
and the weight + drop rule of each assignment group. Canvas-specific facts
(object ids, html links) are recorded too, but are course-scoped and refreshed
on every pull.

WORKFLOWS
  (A) You edited assignments ON CANVAS  → pull Canvas state into the contract:
          python scripts/sync_contract.py --pull
  (B) You edited the CONTRACT           → push it to Canvas:
          python scripts/sync_contract.py --apply --dry-run   # preview
          python scripts/sync_contract.py --apply             # do it
  Build/refresh the human-readable handoff any time:
          python scripts/sync_contract.py --render
  First-time build (after push_to_canvas.py):
          python scripts/sync_contract.py --pull --seed --render

MODES (combine freely; they run in this order: pull, seed, apply, render)
  --pull            Canvas → contract. Match by NAME, record canvas_id,
                    html_url, points_possible, due_at, grading_type (groups:
                    group_weight, position, drop_lowest). Canvas wins.
  --pull --ids-only Refresh ONLY canvas_id + html_url (preserve dates/points/
                    weights). Use when porting to a new course id.
  --seed            Fill BLANK due_at values from the manifest week mapping.
                    Never overwrites an existing date.
  --apply           Contract → Canvas. PUT due_at + points_possible per
                    assignment, group_weight + drop_lowest per group.
  --render          Write HANDOFF_DUEDATES.md (links + proposed dates table).
  --dry-run         With --apply: print the PUTs, change nothing.
  --force           With --apply: skip the course-id safety guard.

ENVIRONMENT (same as push_to_canvas.py)
  CANVAS_BASE_URL   e.g. https://canvas.cornell.edu   (no trailing /api)
  CANVAS_API_TOKEN  a user access token
  CANVAS_COURSE_ID  the numeric course id
"""

import os
import sys
import json
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("This script needs `requests`.  Run:  pip install requests")

ROOT = Path(__file__).resolve().parent.parent
PLAN = json.loads((ROOT / "canvas_plan.json").read_text(encoding="utf-8"))
MANIFEST = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
CONTRACT_PATH = ROOT / "canvas_contract.json"
HANDOFF_PATH = ROOT / "HANDOFF_DUEDATES.md"

BASE = os.environ.get("CANVAS_BASE_URL", "").rstrip("/")
TOKEN = os.environ.get("CANVAS_API_TOKEN", "")
COURSE = os.environ.get("CANVAS_COURSE_ID", "")

ARGS = set(sys.argv[1:])
DO_PULL = "--pull" in ARGS
DO_SEED = "--seed" in ARGS
DO_APPLY = "--apply" in ARGS
DO_RENDER = "--render" in ARGS
IDS_ONLY = "--ids-only" in ARGS
DRY = "--dry-run" in ARGS
FORCE = "--force" in ARGS

if not (DO_PULL or DO_SEED or DO_APPLY or DO_RENDER):
    sys.exit("Nothing to do. Pass at least one of --pull --seed --apply --render "
             "(see --help in the file header).")

API = f"{BASE}/api/v1"
HEAD = {"Authorization": f"Bearer {TOKEN}"}

# A network call is needed for pull/apply; render+seed are purely local.
NEEDS_NET = DO_PULL or DO_APPLY
if NEEDS_NET and not (BASE and TOKEN and COURSE):
    sys.exit("Set CANVAS_BASE_URL, CANVAS_API_TOKEN, CANVAS_COURSE_ID for "
             "--pull/--apply.")


# ---------------------------------------------------------------------------
# thin REST helpers (mirrors push_to_canvas.py: pagination + rate-limit backoff)
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
    out, url = [], f"{API}{path}"
    p = {"per_page": 100, **params}
    while url:
        r = requests.get(url, headers=HEAD, params=p, timeout=60)
        if not r.ok:
            sys.exit(f"✗ GET {url} -> {r.status_code}\n{r.text[:400]}")
        out.extend(r.json())
        url, p = r.links.get("next", {}).get("url"), {}
    return out


# ---------------------------------------------------------------------------
# week → due-date mapping, derived from manifest.json (proposal seed only)
# ---------------------------------------------------------------------------
DUE_DATES = {k: v for k, v in MANIFEST["due_dates"].items() if not k.startswith("_")}
CS_WEEK = {c["key"]: c["week"] for c in MANIFEST["case_studies"]}
PROJ_DUE = {p["n"]: p["due"] for p in MANIFEST["extras"]["projects"]}
FINAL_DUE = MANIFEST["extras"]["final_presentation"]["due"]
SURVEY_WEEK = {s["key"]: s.get("week") for s in MANIFEST.get("surveys", [])}


def week_of(key):
    """Integer week (1/2/3) for a plan assignment key, or None."""
    if key in SURVEY_WEEK:
        return SURVEY_WEEK[key]
    for prefix in ("drawing-", "lc-"):
        if key.startswith(prefix):
            return CS_WEEK.get(key[len(prefix):])
    if key.startswith("ed-week-") or key.startswith("office-week-"):
        return int(key.rsplit("-", 1)[1])
    if key.startswith("project-"):
        due = PROJ_DUE.get(int(key.rsplit("-", 1)[1]))
        return int(due.replace("week", "")) if due else None
    if key == "final-presentation":
        return int(FINAL_DUE.replace("week", "")) if FINAL_DUE else None
    return None


def due_for_week(w):
    return DUE_DATES.get(f"week{w}") if w else None


GRADING_TYPE = {"completion": "pass_fail", "points": "points"}


# ---------------------------------------------------------------------------
# contract load / build-skeleton
# ---------------------------------------------------------------------------
def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_skeleton():
    """Fresh contract from the plan (no Canvas ids/dates yet)."""
    groups = []
    for g in PLAN["assignment_groups"]:
        groups.append({
            "key": g["key"],
            "name": g["name"],
            "canvas_id": 0,
            "group_weight": g["group_weight"],
            "position": g["position"],
            "drop_lowest": g.get("drop_lowest", 0),
        })
    assignments = []
    for a in PLAN["assignments"]:
        assignments.append({
            "key": a["key"],
            "name": a["name"],
            "group": a["group"],
            "grading_type": GRADING_TYPE[a["grading"]],
            "points_possible": a["points"],
            "week": week_of(a["key"]),
            "due_at": None,
            "canvas_id": 0,
            "html_url": "",
        })
    return {
        "meta": {
            "course_id": COURSE,
            "base_url": BASE,
            "last_pull": None,
            "note": ("Edit due_at (ISO 8601, e.g. 2026-06-29T13:00:00Z), "
                     "points_possible, and group weight/drop_lowest here, then "
                     "run: sync_contract.py --apply. Or edit on Canvas and run "
                     "--pull. Set due_at to null to leave a date unset."),
        },
        "assignment_groups": groups,
        "assignments": assignments,
    }


def load_contract():
    if CONTRACT_PATH.exists():
        return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    return build_skeleton()


def reconcile_with_plan(contract):
    """Make the contract track the current plan: add any plan assignments/groups
    that aren't in the contract yet, and refresh STRUCTURAL fields (name, group,
    grading_type, week) on existing entries. Intent/state (due_at, points_possible,
    canvas_id, html_url, group weights) is preserved. Keeps plan order."""
    skel = build_skeleton()
    by_key = {a["key"]: a for a in contract["assignments"]}
    added = 0
    for sa in skel["assignments"]:
        if sa["key"] in by_key:
            ca = by_key[sa["key"]]
            for f in ("name", "group", "grading_type", "week"):
                ca[f] = sa[f]
        else:
            contract["assignments"].append(sa)
            added += 1
    gk = {g["key"]: g for g in contract["assignment_groups"]}
    for sg in skel["assignment_groups"]:
        if sg["key"] in gk:
            gk[sg["key"]]["name"] = sg["name"]
        else:
            contract["assignment_groups"].append(sg)
            added += 1
    order_a = {a["key"]: i for i, a in enumerate(skel["assignments"])}
    order_g = {g["key"]: i for i, g in enumerate(skel["assignment_groups"])}
    contract["assignments"].sort(key=lambda a: order_a.get(a["key"], 10 ** 9))
    contract["assignment_groups"].sort(key=lambda g: order_g.get(g["key"], 10 ** 9))
    if added:
        print(f"• reconcile: added {added} new plan item(s) to the contract")


def save_contract(c):
    CONTRACT_PATH.write_text(json.dumps(c, indent=2, ensure_ascii=False) + "\n",
                             encoding="utf-8")


# ---------------------------------------------------------------------------
# --pull : Canvas → contract
# ---------------------------------------------------------------------------
def pull(contract):
    c_assigns = {a["name"]: a for a in get_all(f"/courses/{COURSE}/assignments")}
    c_groups = {g["name"]: g for g in get_all(f"/courses/{COURSE}/assignment_groups")}

    matched_a = matched_g = 0
    for a in contract["assignments"]:
        ca = c_assigns.get(a["name"])
        if not ca:
            print(f"  ! no Canvas match for assignment: {a['name']}")
            continue
        matched_a += 1
        a["canvas_id"] = ca["id"]
        a["html_url"] = ca.get("html_url", "")
        if not IDS_ONLY:
            a["due_at"] = ca.get("due_at")  # ISO string or None
            if ca.get("points_possible") is not None:
                pp = ca["points_possible"]
                a["points_possible"] = int(pp) if float(pp).is_integer() else pp
            if ca.get("grading_type"):
                a["grading_type"] = ca["grading_type"]

    for g in contract["assignment_groups"]:
        cg = c_groups.get(g["name"])
        if not cg:
            print(f"  ! no Canvas match for group: {g['name']}")
            continue
        matched_g += 1
        g["canvas_id"] = cg["id"]
        if not IDS_ONLY:
            if cg.get("group_weight") is not None:
                g["group_weight"] = cg["group_weight"]
            if cg.get("position") is not None:
                g["position"] = cg["position"]
            g["drop_lowest"] = (cg.get("rules") or {}).get("drop_lowest", 0)

    contract["meta"]["course_id"] = COURSE
    contract["meta"]["base_url"] = BASE
    contract["meta"]["last_pull"] = now_iso()
    mode = " (ids only)" if IDS_ONLY else ""
    print(f"• pull{mode}: matched {matched_a}/{len(contract['assignments'])} "
          f"assignments, {matched_g}/{len(contract['assignment_groups'])} groups")


# ---------------------------------------------------------------------------
# --seed : fill blank due_at from the manifest week mapping
# ---------------------------------------------------------------------------
def seed(contract):
    filled = 0
    for a in contract["assignments"]:
        if a.get("due_at"):
            continue
        due = due_for_week(a.get("week"))
        if due:
            a["due_at"] = due
            filled += 1
    print(f"• seed: filled {filled} blank due dates from manifest week mapping")


# ---------------------------------------------------------------------------
# --apply : contract → Canvas
# ---------------------------------------------------------------------------
def apply(contract):
    meta_course = str(contract.get("meta", {}).get("course_id") or "")
    if not FORCE and meta_course and meta_course != str(COURSE):
        sys.exit(f"✗ contract was last pulled for course {meta_course} but "
                 f"CANVAS_COURSE_ID={COURSE}. Refusing to apply (use --force, "
                 f"or run --pull --ids-only first when porting).")

    n_a = n_g = 0
    for a in contract["assignments"]:
        if not a.get("canvas_id"):
            print(f"  ! skip (no canvas_id): {a['name']} — run --pull first")
            continue
        data = [("assignment[points_possible]", str(a["points_possible"]))]
        if a.get("due_at"):
            data.append(("assignment[due_at]", a["due_at"]))
        print(f"  - apply assignment: {a['name']}  "
              f"due={a.get('due_at') or '—'}  pts={a['points_possible']}")
        _req("PUT", f"/courses/{COURSE}/assignments/{a['canvas_id']}", data=data)
        n_a += 1

    for g in contract["assignment_groups"]:
        if not g.get("canvas_id"):
            print(f"  ! skip group (no canvas_id): {g['name']} — run --pull first")
            continue
        data = [("group_weight", str(g["group_weight"]))]
        # drop_lowest must not exceed the group's assignment count; Canvas
        # validates this. 0 means "no rule" — send it to clear if needed.
        data.append(("rules[drop_lowest]", str(g.get("drop_lowest", 0) or 0)))
        print(f"  - apply group: {g['name']}  weight={g['group_weight']}%  "
              f"drop_lowest={g.get('drop_lowest', 0)}")
        _req("PUT", f"/courses/{COURSE}/assignment_groups/{g['canvas_id']}", data=data)
        n_g += 1

    verb = "would apply" if DRY else "applied"
    print(f"• {verb}: {n_a} assignments, {n_g} groups")


# ---------------------------------------------------------------------------
# --render : human-readable HANDOFF_DUEDATES.md
# ---------------------------------------------------------------------------
def fmt_due(iso):
    if not iso:
        return "—"
    try:
        dt = datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        return dt.strftime("%a %Y-%m-%d %H:%M UTC")
    except ValueError:
        return iso


def link(a):
    return f"[{a['name']}]({a['html_url']})" if a.get("html_url") else a["name"]


def render(contract):
    meta = contract["meta"]
    groups = {g["key"]: g for g in contract["assignment_groups"]}
    by_week = {}
    for a in contract["assignments"]:
        by_week.setdefault(a.get("week") or 0, []).append(a)

    lines = []
    lines.append("# SYSEN 5470 — Due Dates & Points (Canvas contract handoff)\n")
    lines.append(f"- **Course:** `{meta.get('course_id')}` @ {meta.get('base_url')}")
    lines.append(f"- **Last pulled from Canvas:** {meta.get('last_pull') or '(never)'}")
    lines.append(f"- **Generated:** {now_iso()}\n")
    lines.append("> **Dates below are a PROPOSAL** seeded from the course "
                 "calendar (each week's Monday 9 AM ET). Edit them — in "
                 "`canvas_contract.json` or by replying in chat — then they get "
                 "pushed to Canvas.\n")
    lines.append("**How we keep this in sync**")
    lines.append("- *You changed something on Canvas* → run "
                 "`python scripts/sync_contract.py --pull` (Canvas → this file).")
    lines.append("- *You changed this contract* → run "
                 "`python scripts/sync_contract.py --apply --dry-run` then "
                 "`--apply` (this file → Canvas).\n")

    # group weights
    lines.append("## Assignment group weights\n")
    lines.append("| Group | Weight | Drop lowest |")
    lines.append("|---|---|---|")
    total = 0
    for g in contract["assignment_groups"]:
        total += g.get("group_weight", 0)
        drop = g.get("drop_lowest", 0)
        lines.append(f"| {g['name']} | {g['group_weight']}% | "
                     f"{drop if drop else '—'} |")
    lines.append(f"| **Total** | **{total}%** | |\n")

    # assignments by week
    week_titles = {1: "Week 1", 2: "Week 2", 3: "Week 3", 0: "Unscheduled"}
    for w in sorted(by_week):
        lines.append(f"## {week_titles.get(w, f'Week {w}')}\n")
        lines.append("| Assignment | Group | Grading | Points | Proposed due |")
        lines.append("|---|---|---|---|---|")
        for a in by_week[w]:
            gname = groups.get(a["group"], {}).get("name", a["group"])
            grading = "Completion" if a["grading_type"] == "pass_fail" else "Points"
            lines.append(f"| {link(a)} | {gname} | {grading} | "
                         f"{a['points_possible']} | {fmt_due(a.get('due_at'))} |")
        lines.append("")

    HANDOFF_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"• render: wrote {HANDOFF_PATH.name} "
          f"({len(contract['assignments'])} assignments)")


# ---------------------------------------------------------------------------
def main():
    contract = load_contract()
    reconcile_with_plan(contract)
    if DO_PULL:
        pull(contract)
    if DO_SEED:
        seed(contract)
    if DO_APPLY:
        apply(contract)
    # Persist contract unless this was a pure dry-run apply (no other mutation).
    if not (DRY and DO_APPLY and not (DO_PULL or DO_SEED)):
        save_contract(contract)
    if DO_RENDER:
        render(contract)
    print("✓ done.")


if __name__ == "__main__":
    main()
