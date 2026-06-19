"""Generate the `reorg-comms` project network (deterministic).

Internal corporate communication (email + chat volume) among ~250 employees of a
fictional company, observed across three periods around a reorganization + layoff:
  - period = "before"  : stable org
  - period = "during"  : reorg announced, layoffs happening (anxiety spike)
  - period = "after"   : new teams settled, headcount reduced

Nodes are employees (kind = "employee"); edges are directed messages
sender -> receiver for a given period, weighted by message_count.

Design parameters (the only record of the planted structure):
  - INFORMAL_BROKER: a long-tenured low-`level` IC who is one of the top brokers
    by betweenness — informal influence the formal org chart (manager_id tree)
    does not show.
  - BOTTLENECK_MGR: one manager who sits on the only communication path between
    two large departments (very high betweenness); most cross-dept info routes
    through them.
  - LOAD_BEARING_LEAVERS: several laid-off employees were high-betweenness
    connectors; removing the laid_off set fragments cross-dept comms far more
    than removing a random equal-size set.
  - SILOING: cross-department edges fall and within-(new-)team edges rise from
    before -> after (modularity by dept rises after the reorg).
  - VOLUME_SPIKE: total message volume peaks DURING (uncertainty / anxiety).

Run:
    python data/projects/reorg-comms/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

PERIODS = ["before", "during", "after"]

N_EMP = 250
DEPTS = ["Engineering", "Product", "Sales", "Marketing",
         "Finance", "Operations", "Support", "HR"]
LOCATIONS = ["HQ", "Remote", "EU Office", "APAC Office"]

# --- planted parameters -----------------------------------------------------
LAYOFF_RATE = 0.18          # fraction of employees laid off
VOLUME_DURING = 1.55        # message-volume multiplier DURING (anxiety spike)
VOLUME_AFTER = 0.82         # message-volume multiplier AFTER (smaller org, calmer)
CROSS_DEPT_BEFORE = 0.32    # share of comms that cross departments BEFORE
CROSS_DEPT_AFTER = 0.14     # share that cross departments AFTER (siloing)
N_LOAD_BEARING = 7          # laid-off employees who were key connectors


def main() -> None:
    rng = np.random.default_rng(SEED)

    # ----- departments & levels -------------------------------------------
    # department sizes (Engineering & Sales are the two big ones the bottleneck
    # manager will sit between).
    dept_sizes = np.array([60, 28, 55, 22, 18, 25, 27, 15])
    dept_sizes = dept_sizes * N_EMP // dept_sizes.sum()
    # fix rounding so they sum to N_EMP
    dept_sizes[0] += N_EMP - dept_sizes.sum()
    dept_of = []
    for d, n in zip(DEPTS, dept_sizes):
        dept_of += [d] * int(n)
    dept_of = np.array(dept_of)
    rng.shuffle(dept_of)

    emp_ids = [f"E{i:03d}" for i in range(1, N_EMP + 1)]

    # levels: mostly ICs, some managers, fewer directors, few VPs
    level = rng.choice(["ic", "manager", "director", "vp"],
                       size=N_EMP, p=[0.70, 0.18, 0.09, 0.03])
    tenure = rng.integers(2, 180, N_EMP)
    location = rng.choice(LOCATIONS, size=N_EMP, p=[0.45, 0.30, 0.15, 0.10])

    # ----- build a formal org chart (manager_id tree) per department -------
    # each dept gets a head (director or vp), managers report to head, ICs report
    # to managers. manager_id is the FORMAL reporting line.
    manager_id = [""] * N_EMP
    idx_by_dept = {d: [i for i in range(N_EMP) if dept_of[i] == d] for d in DEPTS}
    for d in DEPTS:
        members = idx_by_dept[d]
        # head = highest level member (prefer vp, then director, then manager)
        order = {"vp": 0, "director": 1, "manager": 2, "ic": 3}
        members_sorted = sorted(members, key=lambda i: order[level[i]])
        head = members_sorted[0]
        # ensure head is at least director
        if level[head] not in ("director", "vp"):
            level[head] = "director"
        mgrs = [i for i in members if level[i] == "manager" and i != head]
        if not mgrs:
            # promote a couple ICs to manager so there is a middle layer
            cand = [i for i in members if level[i] == "ic" and i != head][:2]
            for c in cand:
                level[c] = "manager"
            mgrs = cand
        for m in mgrs:
            manager_id[m] = emp_ids[head]
        ics = [i for i in members if i not in mgrs and i != head]
        for i in ics:
            manager_id[i] = emp_ids[int(rng.choice(mgrs))] if mgrs else emp_ids[head]
        # head reports to nobody (blank) -> top of the dept

    # ----- planted special people -----------------------------------------
    eng = idx_by_dept["Engineering"]
    sales = idx_by_dept["Sales"]

    # INFORMAL_BROKER: a long-tenured IC in Engineering (low level, high influence)
    eng_ics = [i for i in eng if level[i] == "ic"]
    informal_broker = max(eng_ics, key=lambda i: tenure[i])
    tenure[informal_broker] = max(tenure[informal_broker], 160)  # very senior IC

    # BOTTLENECK_MGR: a manager who alone bridges Engineering <-> Sales.
    eng_mgrs = [i for i in eng if level[i] == "manager"]
    bottleneck_mgr = eng_mgrs[0]

    nodes = pd.DataFrame({
        "node_id": emp_ids,
        "kind": "employee",
        "label": [f"Emp {i:03d}" for i in range(1, N_EMP + 1)],
        "dept": dept_of,
        "level": level,
        "tenure_months": tenure,
        "location": location,
        "manager_id": manager_id,
    })

    # ----- layoffs ---------------------------------------------------------
    n_layoff = int(round(N_EMP * LAYOFF_RATE))
    # LOAD_BEARING_LEAVERS: pick some cross-dept connectors to be laid off, plus
    # the rest at random. (Connectors = people we will wire as cross-dept bridges.)
    # We designate bridge people first, then ensure several are laid off.
    # Cross-dept bridge pool: a handful per department.
    bridge_pool = []
    for d in DEPTS:
        members = [i for i in idx_by_dept[d]
                   if i not in (informal_broker, bottleneck_mgr)]
        bridge_pool += list(rng.choice(members, size=3, replace=False))
    load_bearing = list(rng.choice(bridge_pool, size=N_LOAD_BEARING, replace=False))
    # rest of layoffs random, excluding protected key people we want to keep
    protected = {informal_broker, bottleneck_mgr}
    pool = [i for i in range(N_EMP)
            if i not in load_bearing and i not in protected]
    extra = list(rng.choice(pool, size=n_layoff - len(load_bearing), replace=False))
    laid_off_idx = set(load_bearing) | set(extra)
    nodes["laid_off"] = [1 if i in laid_off_idx else 0 for i in range(N_EMP)]

    # ----- communication generation ---------------------------------------
    # Each employee has an "activity" level; messages flow mostly within dept,
    # a tunable share cross-dept, plus planted bridges.
    activity = rng.lognormal(mean=2.4, sigma=0.5, size=N_EMP)
    # managers/directors a bit more active
    lvl_boost = {"ic": 1.0, "manager": 1.4, "director": 1.6, "vp": 1.8}
    activity = activity * np.array([lvl_boost[level[i]] for i in range(N_EMP)])

    # --- designate cross-department bridges ------------------------------
    # Cross-dept messages must pass THROUGH a bridge employee, so bridges sit on
    # the only cross-dept paths -> high betweenness, and removing them fragments
    # cross-dept communication. Each ordered department pair gets one or more
    # assigned bridge "owners". This is what makes the planted connectors real.
    pair_bridge = {}   # frozenset({deptA, deptB}) -> list of employee idx
    for a in range(len(DEPTS)):
        for b in range(a + 1, len(DEPTS)):
            da, db = DEPTS[a], DEPTS[b]
            key = frozenset({da, db})
            if key == frozenset({"Engineering", "Sales"}):
                pair_bridge[key] = [bottleneck_mgr]   # SOLE bridge -> bottleneck
            else:
                # one owner from each side, drawn from the bridge pool
                opts_a = [i for i in bridge_pool if dept_of[i] == da] or \
                         [i for i in idx_by_dept[da] if level[i] != "ic"][:1] or \
                         [idx_by_dept[da][0]]
                opts_b = [i for i in bridge_pool if dept_of[i] == db] or \
                         [i for i in idx_by_dept[db] if level[i] != "ic"][:1] or \
                         [idx_by_dept[db][0]]
                pair_bridge[key] = [opts_a[0], opts_b[0]]

    # informal broker: make it a bridge owner for MANY dept pairs (across the
    # whole company), giving a low-level IC outsized betweenness.
    for key in list(pair_bridge):
        if "Engineering" in key and frozenset({"Engineering"}) != key:
            if key != frozenset({"Engineering", "Sales"}):
                pair_bridge[key] = list(set(pair_bridge[key]) | {informal_broker})

    edge_rows = []

    def add_through_bridge(pair_counts, s, r, active_set):
        """Route a cross-dept message s->r through an assigned bridge."""
        key = frozenset({dept_of[s], dept_of[r]})
        owners = [b for b in pair_bridge.get(key, []) if b in active_set]
        if not owners:
            return  # no live bridge -> message cannot cross (fragmentation!)
        br = int(rng.choice(owners))
        if br == s or br == r:
            _bump(pair_counts, s, r)
            return
        # model the two-hop path s -> bridge -> r as two directed edges
        _bump(pair_counts, s, br)
        _bump(pair_counts, br, r)

    def gen_period(period):
        if period == "before":
            vol = 1.0; cross = CROSS_DEPT_BEFORE; active = set(range(N_EMP))
        elif period == "during":
            vol = VOLUME_DURING; cross = (CROSS_DEPT_BEFORE + CROSS_DEPT_AFTER) / 2
            active = set(range(N_EMP))  # leavers still present during
        else:  # after
            vol = VOLUME_AFTER; cross = CROSS_DEPT_AFTER
            active = set(i for i in range(N_EMP) if i not in laid_off_idx)

        active = list(active)
        active_set = set(active)
        n_msgs = int(2600 * vol)

        w = np.array([activity[i] for i in active])
        w = w / w.sum()

        pair_counts = {}
        for _ in range(n_msgs):
            s = int(rng.choice(active, p=w))
            if rng.random() < cross:
                # cross-department message -> must go through a bridge
                r = _other_dept_receiver(rng, s, dept_of, active, active_set)
                if dept_of[r] == dept_of[s]:
                    continue
                add_through_bridge(pair_counts, s, r, active_set)
            else:
                # within-department message
                same = [i for i in idx_by_dept[dept_of[s]]
                        if i in active_set and i != s]
                if not same:
                    continue
                r = int(rng.choice(same))
                if r != s:
                    _bump(pair_counts, s, r)

        for (s, r), c in pair_counts.items():
            c2 = max(1, int(round(c * rng.uniform(0.85, 1.15))))
            edge_rows.append({
                "sender_id": emp_ids[s], "receiver_id": emp_ids[r],
                "period": period, "message_count": c2,
            })

    for p in PERIODS:
        gen_period(p)

    edges = pd.DataFrame(edge_rows)
    # collapse any dup (sender, receiver, period)
    edges = (edges.groupby(["sender_id", "receiver_id", "period"], as_index=False)
             .agg(message_count=("message_count", "sum")))

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)

    import os
    if os.environ.get("REORG_DEBUG"):
        print("DEBUG informal_broker:", emp_ids[informal_broker],
              "dept", dept_of[informal_broker], "level", level[informal_broker],
              "tenure", tenure[informal_broker])
        print("DEBUG bottleneck_mgr:", emp_ids[bottleneck_mgr],
              "dept", dept_of[bottleneck_mgr], "level", level[bottleneck_mgr])
        print("DEBUG load_bearing leavers:", [emp_ids[i] for i in load_bearing])
        print("DEBUG n laid_off:", len(laid_off_idx))

    print(f"reorg-comms: {len(nodes)} nodes (employees), {len(edges)} edges "
          f"across {edges['period'].nunique()} periods "
          f"(before={int((edges.period=='before').sum())}, "
          f"during={int((edges.period=='during').sum())}, "
          f"after={int((edges.period=='after').sum())}); "
          f"{int(nodes.laid_off.sum())} laid off.")


def _bump(d, s, r):
    d[(s, r)] = d.get((s, r), 0) + 1


def _other_dept_receiver(rng, s, dept_of, active, active_set):
    for _ in range(8):
        r = int(rng.choice(active))
        if dept_of[r] != dept_of[s]:
            return r
    return int(rng.choice(active))


if __name__ == "__main__":
    main()
