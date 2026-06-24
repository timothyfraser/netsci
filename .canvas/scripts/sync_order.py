#!/usr/bin/env python3
"""
sync_order.py — position-only Canvas reorder for 4/3/4 module layout.
"""

import json
import re
import sys
import time
from pathlib import Path

# Windows consoles may not support emoji in module titles.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    import requests
except ImportError:
    sys.exit("This script needs `requests`.  Run:  pip install requests")

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
PLAN = json.loads((ROOT / "canvas_plan.json").read_text(encoding="utf-8"))
CONTRACT_PATH = ROOT / "canvas_contract.json"

sys.path.insert(0, str(ROOT / "scripts"))
from canvas_env import get_canvas_env

BASE, TOKEN, COURSE = get_canvas_env()

FLAGS = set(a for a in sys.argv[1:] if a.startswith("--"))
DRY = "--dry-run" in FLAGS
PILOT = "--pilot" in FLAGS
ONLY = None
argv = sys.argv[1:]
for i, a in enumerate(argv):
    if a == "--only-module" and i + 1 < len(argv):
        ONLY = argv[i + 1].lower()

API = f"{BASE}/api/v1"
HEAD = {"Authorization": f"Bearer {TOKEN}"}

WEEK_TITLES = MANIFEST["modules"]["week_titles"]
CS_BY_WEEK = {}
CS_WEEK = {}
for c in MANIFEST["case_studies"]:
    CS_BY_WEEK.setdefault(c["week"], []).append(c["key"])
    CS_WEEK[c["key"]] = c["week"]

WEEK_MODULE_NAMES = {int(w): WEEK_TITLES[str(w)] for w in (1, 2, 3)}
LAB_URL_RE = re.compile(r"case-studies/([a-z0-9-]+)\.html")
PREFIX_REFS = {
    "intro-survey", "office-week-1", "office-week-2", "office-week-3",
    "ed-week-1", "ed-week-2", "ed-week-3",
}


def _req(method, path, **kw):
    if DRY:
        data = kw.get("data")
        if isinstance(data, list):
            data = {k: v for k, v in data}
        print(f"  [dry-run] {method} {path}  {data or ''}")
        return {"id": 0}
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


def fetch_modules():
    mods = []
    for m in get_all(f"/courses/{COURSE}/modules"):
        items = get_all(f"/courses/{COURSE}/modules/{m['id']}/items")
        mods.append({**m, "items": items})
    return mods


def cs_key_from_item(item, id_to_key):
    typ = item.get("type")
    cid = item.get("content_id")
    if typ == "Assignment" and cid in id_to_key:
        ref = id_to_key[cid]
        for prefix in ("drawing-", "lc-"):
            if ref.startswith(prefix):
                return ref[len(prefix):]
    if typ == "ExternalUrl":
        m = LAB_URL_RE.search(item.get("external_url") or "")
        if m:
            return m.group(1)
    return None


def is_triplet_component(item, id_to_key):
    return cs_key_from_item(item, id_to_key) is not None


def split_sections(items):
    act_i = rem_i = None
    for i, it in enumerate(items):
        if it.get("type") == "SubHeader" and it.get("title") == "ACTIVITIES":
            act_i = i
        if it.get("type") == "SubHeader" and it.get("title") == "REMINDERS":
            rem_i = i
    if act_i is None:
        return items, [], []
    before = items[: act_i + 1]
    if rem_i is None:
        return before, items[act_i + 1 :], []
    return before, items[act_i + 1 : rem_i], items[rem_i:]


def collect_triplets(modules, id_to_key):
    triplets = {}
    for mod in modules:
        mid = mod["id"]
        for it in mod["items"]:
            key = cs_key_from_item(it, id_to_key)
            if not key:
                continue
            slot = triplets.setdefault(key, {})
            typ = it.get("type")
            cid = it.get("content_id")
            entry = {**it, "module_id": mid}
            if typ == "ExternalUrl":
                slot["lab"] = entry
            elif typ == "Assignment" and cid in id_to_key:
                ref = id_to_key[cid]
                if ref == f"drawing-{key}":
                    slot["drawing"] = entry
                elif ref == f"lc-{key}":
                    slot["lc"] = entry
    return triplets


def build_activities(week, activities, triplets, id_to_key):
    frozen = [it for it in activities if not is_triplet_component(it, id_to_key)]
    insert_at = 0
    for i, it in enumerate(frozen):
        if it.get("type") != "Assignment":
            continue
        ref = id_to_key.get(it.get("content_id"), "")
        if ref in PREFIX_REFS:
            insert_at = i + 1

    triplet_items = []
    for key in CS_BY_WEEK.get(week, []):
        t = triplets.get(key, {})
        for part in ("lab", "drawing", "lc"):
            if t.get(part):
                triplet_items.append(t[part])
            else:
                print(f"  ! missing {part} for {key}")

    return frozen[:insert_at] + triplet_items + frozen[insert_at:]


def item_identity(item, id_to_key):
    typ = item.get("type")
    if typ == "SubHeader":
        return ("header", item.get("title"))
    if typ == "Assignment":
        return ("asg", id_to_key.get(item.get("content_id"), item.get("title")))
    if typ == "ExternalUrl":
        key = cs_key_from_item(item, id_to_key)
        if key:
            return ("lab", key)
        return ("url", item.get("external_url") or item.get("title"))
    return ("other", item.get("title"))


def recreate_item(module_id, item):
    typ = item.get("type")
    data = []
    if typ == "Assignment":
        data = [
            ("module_item[type]", "Assignment"),
            ("module_item[content_id]", str(item["content_id"])),
            ("module_item[indent]", str(item.get("indent", 1))),
        ]
    elif typ == "ExternalUrl":
        data = [
            ("module_item[type]", "ExternalUrl"),
            ("module_item[title]", item.get("title", "")),
            ("module_item[external_url]", item.get("external_url", "")),
            ("module_item[indent]", str(item.get("indent", 1))),
            ("module_item[new_tab]", "true"),
        ]
    else:
        return None
    return _req("POST", f"/courses/{COURSE}/modules/{module_id}/items", data=data)


def ensure_all_triplets_placed(modules, id_to_key):
    """Move every lab triplet into its manifest week module."""
    mod_by_week = {}
    for w in (1, 2, 3):
        name = WEEK_MODULE_NAMES[w]
        mod = next((m for m in modules if m.get("name") == name), None)
        if mod:
            mod_by_week[w] = mod["id"]

    triplets = collect_triplets(modules, id_to_key)
    for key, week in CS_WEEK.items():
        target_mid = mod_by_week.get(week)
        if not target_mid:
            continue
        t = triplets.get(key, {})
        for part in ("lab", "drawing", "lc"):
            it = t.get(part)
            if not it or it.get("module_id") == target_mid:
                continue
            old_mid = it["module_id"]
            iid = it["id"]
            print(f"    move {key}/{part}: module {old_mid} -> {target_mid}")
            _req("DELETE", f"/courses/{COURSE}/modules/{old_mid}/items/{iid}")
            res = recreate_item(target_mid, it)
            if res:
                it["id"] = res.get("id", iid)
                it["module_id"] = target_mid
    return fetch_modules()


def reorder_positions(module_id, live_items, target_identities, id_to_key):
    """Reorder module items to match target_identities sequence."""
    pool = list(live_items)
    matched = []
    for ident in target_identities:
        found = None
        for i, it in enumerate(pool):
            if item_identity(it, id_to_key) == ident:
                found = pool.pop(i)
                break
        if found:
            matched.append(found)
        else:
            print(f"    ! could not match {ident}")

    for pos, it in enumerate(matched, start=1):
        if it.get("position") != pos:
            print(f"    position {it.get('position')} -> {pos}: {it.get('title')}")
            _req("PUT", f"/courses/{COURSE}/modules/{module_id}/items/{it['id']}",
                 data=[("module_item[position]", str(pos))])


def reorder_modules(weeks, contract):
    id_to_key = {a["canvas_id"]: a["key"]
                  for a in contract["assignments"] if a.get("canvas_id")}

    modules = fetch_modules()
    modules = ensure_all_triplets_placed(modules, id_to_key)
    triplets = collect_triplets(modules, id_to_key)

    for week in weeks:
        name = WEEK_MODULE_NAMES[week]
        mod = next((m for m in modules if m.get("name") == name), None)
        if not mod:
            print(f"! module not found: {name}")
            continue
        mid = mod["id"]
        print(f"\n=== {name} ===")

        mod["items"] = get_all(f"/courses/{COURSE}/modules/{mid}/items")
        triplets = collect_triplets(fetch_modules(), id_to_key)

        overview_urls = [it for it in mod["items"]
                         if it.get("type") == "ExternalUrl"
                         and not is_triplet_component(it, id_to_key)]
        print(f"  frozen OVERVIEW/custom urls: {len(overview_urls)}")
        for u in overview_urls:
            print(f"    - {u.get('title')}")

        before, activities, after = split_sections(mod["items"])
        new_activities = build_activities(week, activities, triplets, id_to_key)
        print(f"  activities lab order: {CS_BY_WEEK.get(week, [])}")

        target_identities = (
            [item_identity(it, id_to_key) for it in before]
            + [item_identity(it, id_to_key) for it in new_activities]
            + [item_identity(it, id_to_key) for it in after]
        )
        reorder_positions(mid, mod["items"], target_identities, id_to_key)


def reorder_assignment_groups(contract, keys_only=None):
    plan_order = {a["key"]: i for i, a in enumerate(PLAN["assignments"])}
    for gkey in ("drawings", "casestudies"):
        items = [a for a in contract["assignments"] if a["group"] == gkey]
        if keys_only:
            items = [a for a in items if a["key"] in keys_only]
        items.sort(key=lambda a: plan_order.get(a["key"], 10 ** 9))
        print(f"\n=== assignment group: {gkey} ({len(items)} items) ===")
        for pos, a in enumerate(items, start=1):
            aid = a.get("canvas_id")
            if not aid:
                print(f"  ! skip (no id): {a['key']}")
                continue
            print(f"  position {pos}: {a['name']}")
            _req("PUT", f"/courses/{COURSE}/assignments/{aid}",
                 data=[("assignment[position]", str(pos))])


def main():
    if not (BASE and TOKEN and COURSE):
        sys.exit("Set CANVAS_BASE_URL, CANVAS_API_TOKEN, CANVAS_COURSE_ID")

    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    if PILOT:
        weeks = [1]
    elif ONLY in ("week1", "1"):
        weeks = [1]
    elif ONLY in ("week2", "2"):
        weeks = [2]
    elif ONLY in ("week3", "3"):
        weeks = [3]
    else:
        weeks = [1, 2, 3]

    print(f"sync_order: weeks={weeks} dry_run={DRY} pilot={PILOT}")
    reorder_modules(weeks, contract)

    w1_draw = {f"drawing-{k}" for k in CS_BY_WEEK[1]}
    w1_lc = {f"lc-{k}" for k in CS_BY_WEEK[1]}
    if PILOT:
        reorder_assignment_groups(contract, keys_only=w1_draw | w1_lc)
    elif ONLY is None:
        reorder_assignment_groups(contract)

    print("\ndone.")


if __name__ == "__main__":
    main()
