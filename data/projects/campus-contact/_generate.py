"""Generate the `campus-contact` project network (deterministic).

A face-to-face proximity / co-location contact network on a university campus,
recorded over four weeks as a respiratory illness spreads:
  - ~300 people (kind = student / faculty / staff)
  - undirected co-location contacts, one row per (person, person, week)
weighted by `contact_minutes` (time the two spent in proximity that week).
A companion `status.csv` records each person's infection state per week.

Design parameters (the only record of the planted structure):
  - N_UNITS: people belong to ~8 units (dorms for students, departments for
    faculty/staff); contacts cluster strongly WITHIN unit -> high modularity.
  - BRIDGE: faculty are the main inter-unit links between student clusters; ONE
    individual (the "connector") is a cross-unit bridge with extreme betweenness
    relative to their degree, touching the most units.
  - SEED_UNIT: the outbreak seeds inside the connector's unit; it jumps to other
    units mainly THROUGH the connector (their removal would have contained it).
  - INTERVENTION (week 3): the highest-degree contacts are cut sharply (a
    structural change); top contacts' degree drops, and infection growth flattens
    afterward.
  - HUB_EARLY: high-degree hubs get infected earlier than average (degree predicts
    early infection -> negative degree~infection-week correlation).

Run:
    python data/projects/campus-contact/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

N_PEOPLE = 300
WEEKS = [1, 2, 3, 4]

# --- planted parameters -----------------------------------------------------
# units: 6 student residences + 2 academic departments. Faculty/staff sit in the
# two departments; students sit in the dorms. Faculty bridge dorms <-> depts.
DORMS = ["West Hall", "East Hall", "North Hall", "South Hall", "Gradflat", "Annex"]
DEPTS = ["Engineering", "Sciences"]
UNITS = DORMS + DEPTS

WITHIN_BASE = 0.16        # baseline P(contact) within the same unit (high)
BETWEEN_BASE = 0.006      # baseline P(contact) across units (low) -> modularity
FACULTY_CROSS = 0.030     # faculty get extra cross-unit contact probability
CONNECTOR_CROSS = 0.55    # the connector blankets MANY units (bridge)

INTERVENTION_WEEK = 3     # high-degree contacts cut starting this week
TOP_CUT_FRAC = 0.10       # fraction of highest-degree people whose ties get cut
CUT_KEEP_PROB = 0.22      # of a cut person's ties, keep only this share at/after wk3

SEED_INFECTIONS = 12      # initial cases in the connector's seed unit (week 1)


def main() -> None:
    rng = np.random.default_rng(SEED)

    # ----- people ----------------------------------------------------------
    # roles: mostly students, some faculty/staff. Faculty/staff live in depts.
    roles = []
    units = []
    years = []
    # assign first the dept people (faculty + staff), then dorm students
    n_faculty = 26
    n_staff = 22
    n_students = N_PEOPLE - n_faculty - n_staff   # 252
    for _ in range(n_faculty):
        roles.append("faculty")
        units.append(rng.choice(DEPTS))
        years.append(0)                      # 0 = not a student year
    for _ in range(n_staff):
        roles.append("staff")
        units.append(rng.choice(DEPTS))
        years.append(0)
    for _ in range(n_students):
        roles.append("student")
        units.append(rng.choice(DORMS))
        years.append(int(rng.integers(1, 5)))   # class year 1..4

    roles = np.array(roles)
    units = np.array(units)
    years = np.array(years)

    node_id = np.array([f"P{i:03d}" for i in range(1, N_PEOPLE + 1)])
    labels = []
    fac_n = stf_n = stu_n = 0
    for r in roles:
        if r == "faculty":
            fac_n += 1; labels.append(f"Faculty {fac_n:02d}")
        elif r == "staff":
            stf_n += 1; labels.append(f"Staff {stf_n:02d}")
        else:
            stu_n += 1; labels.append(f"Student {stu_n:03d}")
    labels = np.array(labels)

    unit_of = dict(zip(node_id, units))
    role_of = dict(zip(node_id, roles))

    # ----- choose the connector (cross-unit bridge) ------------------------
    # a faculty member who will touch many units.
    faculty_ids = node_id[roles == "faculty"]
    connector = str(rng.choice(faculty_ids))
    seed_unit = unit_of[connector]

    # ----- build per-week contacts -----------------------------------------
    # We construct a base contact propensity per person (sociability) so that
    # hubs exist; then draw weekly edges from a unit-block model plus bridges.
    sociability = rng.lognormal(mean=0.0, sigma=0.5, size=N_PEOPLE)
    sociability = sociability / sociability.mean()
    soc_of = dict(zip(node_id, sociability))

    # identify the eventual top-degree people for the intervention. We estimate
    # expected degree from sociability + role and cut the top fraction.
    # faculty / connector are naturally high; intervention targets the busiest.
    expected_deg = sociability.copy()
    expected_deg[roles == "faculty"] *= 1.5
    expected_deg[node_id == connector] *= 3.0
    # rank by expected degree but EXCLUDE the connector from the cut: the
    # connector's bridging ties persist, so its criticality (and the "removal
    # would have contained it" counterfactual) stays intact through the study.
    order = [int(i) for i in np.argsort(-expected_deg) if node_id[i] != connector]
    n_cut = max(1, int(TOP_CUT_FRAC * N_PEOPLE))
    cut_ids = set(node_id[order[:n_cut]].tolist())

    idx_of = {nid: i for i, nid in enumerate(node_id)}

    edge_rows = []
    for week in WEEKS:
        intervened = week >= INTERVENTION_WEEK
        # draw a fresh set of contacts for the week
        seen = {}
        # within-unit contacts (block model)
        for u in UNITS:
            members = node_id[units == u]
            m = len(members)
            for a in range(m):
                for b in range(a + 1, m):
                    ia, ib = members[a], members[b]
                    p = WITHIN_BASE * np.sqrt(soc_of[ia] * soc_of[ib])
                    if rng.random() < p:
                        _add(seen, ia, ib, rng)
        # the connector is a guaranteed bridge: each week it makes ties into
        # EVERY other unit (a few members each), giving it max units-touched and
        # extreme betweenness relative to its degree. These bridge ties are the
        # only short paths between many unit pairs.
        for u in UNITS:
            if u == unit_of[connector]:
                continue
            cand = node_id[(units == u)]
            k = min(len(cand), int(rng.integers(2, 5)))
            for ib in rng.choice(cand, size=k, replace=False):
                _add(seen, connector, str(ib), rng)

        # cross-unit contacts: rare in general, more for faculty, lots for connector
        all_ids = node_id
        for ia in all_ids:
            # connector reaches across many units
            if ia == connector:
                cross_p = CONNECTOR_CROSS
            elif role_of[ia] == "faculty":
                cross_p = FACULTY_CROSS
            elif role_of[ia] == "staff":
                cross_p = BETWEEN_BASE * 2
            else:
                cross_p = BETWEEN_BASE
            # number of cross attempts scales with sociability
            n_try = rng.poisson(cross_p * 60 * soc_of[ia])
            for _ in range(n_try):
                ib = str(rng.choice(all_ids))
                if ib == ia or unit_of[ib] == unit_of[ia]:
                    continue
                _add(seen, ia, ib, rng)

        # apply intervention (week 3+): (1) cut most ties touching the top-degree
        # people -> their degree collapses; (2) a campus-wide reduction in contact
        # intensity (everyone meets a bit less) -> dampens the contact_minutes that
        # drive transmission, so the outbreak's growth flattens.
        for (ia, ib), mins in list(seen.items()):
            if intervened and (ia in cut_ids or ib in cut_ids):
                if rng.random() > CUT_KEEP_PROB:
                    del seen[(ia, ib)]
        if intervened:
            # the campus restrictions escalate: week 3 is partial, week 4 tighter.
            damp = 0.30 if week == 3 else 0.16
            for key in list(seen.keys()):
                seen[key] = int(max(3, seen[key] * damp))

        for (ia, ib), mins in seen.items():
            edge_rows.append({
                "from_id": ia, "to_id": ib, "week": week,
                "contact_minutes": mins,
            })

    edges = pd.DataFrame(edge_rows)

    # ----- infection dynamics over weeks -----------------------------------
    # SIR-ish on the realized weekly contact graph, seeded in the connector unit.
    infected_week = {nid: 0 for nid in node_id}     # 0 = never infected (within study)
    state = {nid: "S" for nid in node_id}

    # seed: cases in the seed unit, weighted toward more-social members (the
    # outbreak takes hold among the busiest people first -> hubs infected early).
    seed_pool = np.array([n for n in node_id[units == seed_unit] if n != connector])
    w = np.array([soc_of[n] ** 2 for n in seed_pool]); w = w / w.sum()
    seeds = rng.choice(seed_pool, size=min(SEED_INFECTIONS, len(seed_pool)),
                       replace=False, p=w)
    # a few stray introductions campus-wide, weighted to the most-social people,
    # so connectivity (not just being in the seed unit) governs early infection.
    others = np.array([n for n in node_id if n not in set(seeds) and n != connector])
    wo = np.array([soc_of[n] ** 3 for n in others]); wo = wo / wo.sum()
    sparks = rng.choice(others, size=4, replace=False, p=wo)
    for s in list(seeds) + list(sparks):
        state[s] = "I"
        infected_week[s] = 1

    # transmission probability per contact-minute; hubs more exposed naturally
    BETA = 0.0027
    for week in WEEKS:
        wk_edges = edges[edges["week"] == week]
        # build adjacency for this week
        contacts = {}
        for r in wk_edges.itertuples():
            contacts.setdefault(r.from_id, []).append((r.to_id, r.contact_minutes))
            contacts.setdefault(r.to_id, []).append((r.from_id, r.contact_minutes))
        newly = []
        for person, nbrs in contacts.items():
            if state[person] != "S":
                continue
            # force of infection from infected neighbors this week
            foi = 0.0
            for (nb, mins) in nbrs:
                if state[nb] == "I":
                    foi += BETA * mins
            # hubs (high sociability) get strongly extra exposure -> infected
            # earlier than peripheral people (friendship-paradox flavored).
            foi *= (0.10 + 4.0 * soc_of[person])
            if rng.random() < 1 - np.exp(-foi):
                newly.append(person)
        for p in newly:
            state[p] = "I"
            infected_week[p] = week

    # status long table: node_id, week, infected (cumulative 0/1)
    status_rows = []
    for nid in node_id:
        iw = infected_week[nid]
        for week in WEEKS:
            status_rows.append({
                "node_id": nid, "week": week,
                "infected": int(iw != 0 and week >= iw),
            })
    status = pd.DataFrame(status_rows)

    # ----- nodes table -----------------------------------------------------
    nodes = pd.DataFrame({
        "node_id": node_id,
        "kind": roles,
        "unit": units,
        "year": [y if y > 0 else pd.NA for y in years],
        "label": labels,
    })

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)
    status.to_csv(HERE / "status.csv", index=False)
    n_ever = sum(1 for v in infected_week.values() if v != 0)
    print(f"campus-contact: {len(nodes)} nodes "
          f"({(roles=='student').sum()} student + {(roles=='faculty').sum()} faculty + "
          f"{(roles=='staff').sum()} staff), {len(edges)} edge-weeks, "
          f"{len(UNITS)} units, {n_ever} ever-infected.")


def _add(seen, ia, ib, rng):
    """Add an undirected contact with contact-minutes; merge duplicates."""
    key = (ia, ib) if ia < ib else (ib, ia)
    mins = int(np.clip(rng.gamma(shape=2.0, scale=22.0), 3, 600))
    if key in seen:
        seen[key] += mins
    else:
        seen[key] = mins


if __name__ == "__main__":
    main()
