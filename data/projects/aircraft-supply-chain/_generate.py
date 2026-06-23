"""Generate the `aircraft-supply-chain` project network (deterministic).

A multi-tier commercial-aircraft (airplane) manufacturing supply chain spanning
five tiers of nodes:
  - tier 4  material    raw materials (titanium, aluminium, CFRP composite,
                        nickel superalloy, forgings, fasteners, avionics ICs)
  - tier 3  component   parts / line-replaceable units (turbine blades, FADEC,
                        actuators, avionics LRUs, fuel pumps, wiring harnesses)
  - tier 2  system      major systems / structures (engine, avionics suite,
                        flight controls, wing box, fuselage section, landing gear)
  - tier 1  integrator  Tier-1 suppliers / major-section integrators & OEM
                        final assembly
  - tier 0  program     end aircraft programs / fleets (narrowbody, widebody,
                        regional jet, freighter, military transport)

Edges are directed supply flows from upstream (higher tier) to downstream
(lower tier). One row per supply relationship. The edge weight is
`units_per_year` (shipsets / units per year) with a paired `value_musd` and
`lead_time_days`.

Node attributes: kind, tier, region, subtype, capacity, lead_time_days, label.
Regions: USA, Europe, Canada, Japan, Brazil, China.

Design parameters (the only record of the planted structure):
  - HUB_COMPONENT: one USA engine-control unit (FADEC) feeds nearly all
    flight-critical systems (engines, avionics, flight controls). High
    BETWEENNESS but only modest degree -- a genuine single point of failure that
    raw connection-counts miss. Removing it severs most advanced program output.
  - CHOKE_MATERIAL: one nickel-superalloy supplier (tier 4) feeds nearly every
    flight-critical component (turbine blades etc.); a second hidden critical
    node, betweenness >> degree-rank.
  - ADV_REGION: flight-critical systems concentrate in ONE region (USA); a
    regional shock severs many downstream paths.
  - LEADTIME_ON_PATH: the longest lead times cluster ON the critical path (hub
    FADEC, choke superalloy, US flight-critical systems) so the bottleneck is
    also the slowest to recover.
  - COMMODITY decoys: aluminium & fasteners feed almost every standard component
    (highest DEGREE upstream nodes) but are fully substitutable, so they out-rank
    the real choke on degree and hide it.

Run:
    python data/projects/aircraft-supply-chain/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

REGIONS = ["USA", "Europe", "Canada", "Japan", "Brazil", "China"]

# tier population sizes (total ~ 300 nodes)
N_MATERIAL = 64      # tier 4
N_COMPONENT = 86     # tier 3
N_SYSTEM = 58        # tier 2
N_INTEGRATOR = 44    # tier 1
N_PROGRAM = 48       # tier 0

# --- planted parameters -----------------------------------------------------
HUB_SHARE = 0.80          # share of flight-critical system feed via the hub
CHOKE_SHARE = 0.86        # share of flight-critical components the choke feeds
ADV_REGION = "USA"        # where flight-critical systems concentrate
ADV_CONC = 0.80           # share of advanced integrator feed from that region
LEADTIME_PATH_BONUS = 90  # extra lead-time days loaded onto the critical path
NOISE_REGION_FLIP = 0.10  # fraction of nodes whose region is "wrong" (noise)

COMP_ADV = ["turbine_blade", "fadec", "actuator", "avionics_lru", "fuel_pump"]
COMP_STD = ["wiring_harness", "bracket", "skin_panel", "ducting", "bearing"]
SYS_ADV = ["engine", "avionics_suite", "flight_controls"]
SYS_STD = ["wing_box", "fuselage_section", "landing_gear"]


def main() -> None:
    rng = np.random.default_rng(SEED)

    # region sampling weights: airframe world is USA/Europe heavy
    rweights = np.array([0.32, 0.26, 0.10, 0.10, 0.08, 0.14])
    rweights = rweights / rweights.sum()

    def pick_regions(n):
        return rng.choice(REGIONS, size=n, p=rweights)

    rows = []  # node rows

    # ----- tier 4: materials ----------------------------------------------
    mat_kinds = ["titanium", "aluminium", "cfrp_composite", "fastener",
                 "nickel_superalloy", "avionics_ic", "steel_forging", "sealant"]
    mat_region = pick_regions(N_MATERIAL)
    for i in range(N_MATERIAL):
        sub = mat_kinds[i % len(mat_kinds)]
        rows.append({
            "node_id": f"M{i+1:03d}", "kind": "material", "tier": 4,
            "region": mat_region[i], "subtype": sub,
            "capacity": int(rng.integers(200, 4000)),
            "lead_time_days": int(np.clip(rng.normal(90, 24), 21, 200)),
            "label": f"{sub.replace('_',' ').title()} Co {i+1:03d}",
        })

    # ----- tier 3: components ---------------------------------------------
    c_region = pick_regions(N_COMPONENT)
    c_adv = rng.random(N_COMPONENT) < 0.42   # flight-critical parts
    for i in range(N_COMPONENT):
        sub = COMP_ADV[i % len(COMP_ADV)] if c_adv[i] else COMP_STD[i % len(COMP_STD)]
        rows.append({
            "node_id": f"C{i+1:03d}", "kind": "component", "tier": 3,
            "region": c_region[i], "subtype": sub,
            "capacity": int(rng.integers(20, 240) * (2 if c_adv[i] else 1)),
            "lead_time_days": int(np.clip(rng.normal(130, 28), 45, 260)),
            "label": f"{sub.replace('_',' ').title()} Unit {i+1:03d}",
        })

    # ----- tier 2: systems ------------------------------------------------
    s_region = pick_regions(N_SYSTEM)
    s_adv = rng.random(N_SYSTEM) < 0.45      # flight-critical systems
    # advanced systems concentrate in ADV_REGION (~70% relocated there).
    for i in range(N_SYSTEM):
        if s_adv[i] and rng.random() < 0.70:
            s_region[i] = ADV_REGION
    for i in range(N_SYSTEM):
        sub = SYS_ADV[i % len(SYS_ADV)] if s_adv[i] else SYS_STD[i % len(SYS_STD)]
        rows.append({
            "node_id": f"S{i+1:03d}", "kind": "system", "tier": 2,
            "region": s_region[i], "subtype": sub,
            "capacity": int(rng.integers(30, 320)),
            "lead_time_days": int(np.clip(rng.normal(70, 18), 20, 150)),
            "label": f"{sub.replace('_',' ').title()} System {i+1:03d}",
        })

    # ----- tier 1: integrators --------------------------------------------
    i_region = pick_regions(N_INTEGRATOR)
    i_segment = rng.choice(["narrowbody", "widebody", "regional",
                            "business_jet", "cargo"], size=N_INTEGRATOR)
    i_advanced = np.isin(i_segment, ["narrowbody", "widebody", "business_jet"]) \
        & (rng.random(N_INTEGRATOR) < 0.85)
    for i in range(N_INTEGRATOR):
        rows.append({
            "node_id": f"I{i+1:03d}", "kind": "integrator", "tier": 1,
            "region": i_region[i], "subtype": i_segment[i],
            "capacity": int(rng.integers(20, 220)),
            "lead_time_days": int(np.clip(rng.normal(50, 14), 14, 120)),
            "label": f"Integrator {i+1:03d} ({i_segment[i]})",
        })

    # ----- tier 0: programs -----------------------------------------------
    pr_region = pick_regions(N_PROGRAM)
    pr_segment = rng.choice(["narrowbody", "widebody", "regional_jet",
                             "freighter", "military_transport"], size=N_PROGRAM)
    for i in range(N_PROGRAM):
        rows.append({
            "node_id": f"P{i+1:03d}", "kind": "program", "tier": 0,
            "region": pr_region[i], "subtype": pr_segment[i],
            "capacity": int(rng.integers(20, 700)),
            "lead_time_days": int(np.clip(rng.normal(35, 12), 7, 80)),
            "label": f"Program {i+1:03d} ({pr_segment[i]})",
        })

    nodes = pd.DataFrame(rows)

    def ids(kind):
        return nodes.loc[nodes.kind == kind, "node_id"].tolist()
    mat_ids = ids("material")
    comp_ids = ids("component")
    sys_ids = ids("system")
    int_ids = ids("integrator")
    prog_ids = ids("program")
    region_of = dict(zip(nodes.node_id, nodes.region))
    sub_of = dict(zip(nodes.node_id, nodes.subtype))

    adv_comp = [c for c, a in zip(comp_ids, c_adv) if a]
    std_comp = [c for c in comp_ids if c not in set(adv_comp)]
    adv_sys = [s for s, a in zip(sys_ids, s_adv) if a]
    std_sys = [s for s in sys_ids if s not in set(adv_sys)]
    adv_sys_region = [s for s in adv_sys if region_of[s] == ADV_REGION] or adv_sys[:1]

    # ---- planted critical nodes ------------------------------------------
    # HUB_COMPONENT: a USA engine-control unit (FADEC).
    us_fadec = [c for c in adv_comp
                if region_of[c] == "USA" and sub_of[c] == "fadec"]
    HUB_COMPONENT = us_fadec[0] if us_fadec else adv_comp[0]
    # CHOKE_MATERIAL: a nickel-superalloy supplier.
    superalloy_ids = nodes.loc[(nodes.kind == "material") &
                               (nodes.subtype == "nickel_superalloy"), "node_id"].tolist()
    CHOKE_MATERIAL = superalloy_ids[0]

    advanced_integrators = [i for i, a in zip(int_ids, i_advanced) if a]
    adv_int_set = set(advanced_integrators)
    std_integrators = [i for i in int_ids if i not in adv_int_set]

    prog_seg = dict(zip(prog_ids, pr_segment))
    adv_prog = [p for p in prog_ids if prog_seg[p] in
                ("narrowbody", "widebody", "military_transport", "freighter")]
    std_prog = [p for p in prog_ids if p not in set(adv_prog)]

    eds = []  # edge rows

    def add_edge(frm, to, vol, ltd):
        eds.append({
            "from_id": frm, "to_id": to,
            "units_per_year": int(max(vol, 1)),
            "value_musd": round(float(max(vol, 1)) * rng.uniform(0.08, 0.55), 3),
            "lead_time_days": int(ltd),
        })

    def lt_of(n):
        return int(nodes.loc[nodes.node_id == n, "lead_time_days"].iloc[0])

    choke_lt = lt_of(CHOKE_MATERIAL)
    hub_lt = lt_of(HUB_COMPONENT)

    # DECOY commodity materials feeding nearly every standard component: highest
    # DEGREE upstream, but fully substitutable, so removing one cuts almost
    # nothing. They out-rank the real choke on degree and hide it.
    commodity_pool = [m for m in mat_ids
                      if sub_of[m] == "aluminium" and m != CHOKE_MATERIAL]
    COMMODITY = commodity_pool[0]
    commodity2_pool = [m for m in mat_ids if sub_of[m] == "fastener"]
    COMMODITY2 = commodity2_pool[0]

    # ===== FLIGHT-CRITICAL CORRIDOR (the fragile spine) ===================
    # choke superalloy -> flight-critical components (its ONLY upstream input).
    add_edge(CHOKE_MATERIAL, HUB_COMPONENT, int(rng.integers(120, 240)), choke_lt)
    for c in adv_comp:
        if c != HUB_COMPONENT:
            add_edge(CHOKE_MATERIAL, c, int(rng.integers(40, 140)), choke_lt)

    # hub component -> ALL flight-critical systems: sole upstream feeder, hence a
    # genuine cut vertex on every advanced path while touching only a handful of
    # nodes (modest degree). Volume biased toward the US systems.
    for s in adv_sys:
        vol = int(rng.integers(160, 320)) if region_of.get(s) == ADV_REGION \
            else int(rng.integers(30, 100))
        add_edge(HUB_COMPONENT, s, vol, hub_lt)

    # other flight-critical components sell into the STANDARD integrator market
    # (a secondary outlet) -- they do NOT feed advanced systems, giving the
    # advanced corridor no alternative path.
    for c in adv_comp:
        if c != HUB_COMPONENT:
            for it in rng.choice(std_integrators, size=int(rng.integers(1, 3)), replace=False):
                add_edge(c, it, int(rng.integers(15, 80)), lt_of(c))

    # advanced systems -> advanced integrators (concentrated on US houses).
    us_sys = [s for s in adv_sys if region_of.get(s) == ADV_REGION] or adv_sys
    for it in advanced_integrators:
        if rng.random() < ADV_CONC:
            add_edge(rng.choice(us_sys), it, int(rng.integers(70, 260)), lt_of(us_sys[0]))
        else:
            s = rng.choice(adv_sys)
            add_edge(s, it, int(rng.integers(70, 260)), lt_of(s))
    # advanced integrators -> advanced programs
    for p in adv_prog:
        for it in rng.choice(advanced_integrators, size=int(rng.integers(1, 3)), replace=False):
            add_edge(it, p, int(rng.integers(40, 300)), lt_of(it))

    # ===== COMMODITY CORRIDOR (resilient, multi-sourced) ==================
    for c in std_comp:
        add_edge(COMMODITY, c, int(rng.integers(30, 150)), lt_of(COMMODITY))
        if rng.random() < 0.85:
            add_edge(COMMODITY2, c, int(rng.integers(25, 120)), lt_of(COMMODITY2))
        if rng.random() < 0.25:
            add_edge(CHOKE_MATERIAL, c, int(rng.integers(25, 110)), choke_lt)
        excl = (COMMODITY, COMMODITY2, CHOKE_MATERIAL)
        for m in rng.choice([x for x in mat_ids if x not in excl],
                            size=int(rng.integers(2, 5)), replace=False):
            add_edge(m, c, int(rng.integers(5, 80)), lt_of(m))
    # some materials also feed standard systems directly
    for s in std_sys:
        for m in rng.choice([x for x in mat_ids if x != CHOKE_MATERIAL],
                            size=int(rng.integers(1, 3)), replace=False):
            add_edge(m, s, int(rng.integers(5, 60)), lt_of(m))
    # standard components -> standard systems (multi-sourced)
    for s in std_sys:
        for c in rng.choice(std_comp, size=int(rng.integers(2, 4)), replace=False):
            add_edge(c, s, int(rng.integers(18, 120)), lt_of(c))
    # standard systems -> standard integrators
    for it in std_integrators:
        for s in rng.choice(std_sys, size=int(rng.integers(2, 4)), replace=False):
            add_edge(s, it, int(rng.integers(25, 120)), lt_of(s))
    # standard integrators -> standard programs
    for p in std_prog:
        for it in rng.choice(std_integrators, size=int(rng.integers(2, 4)), replace=False):
            add_edge(it, p, int(rng.integers(40, 280)), lt_of(it))

    edges = pd.DataFrame(eds)

    # ---- LEADTIME_ON_PATH: load extra lead time onto the critical path ----
    crit = {HUB_COMPONENT, CHOKE_MATERIAL} | set(adv_sys)
    nodes.loc[nodes.node_id.isin(crit), "lead_time_days"] = (
        nodes.loc[nodes.node_id.isin(crit), "lead_time_days"] + LEADTIME_PATH_BONUS
    ).clip(upper=340)
    edges.loc[edges.from_id.isin(crit), "lead_time_days"] = (
        edges.loc[edges.from_id.isin(crit), "lead_time_days"] + LEADTIME_PATH_BONUS
    ).clip(upper=360)

    # ---- region noise: flip a few regions so region != destiny ------------
    flip = rng.random(len(nodes)) < NOISE_REGION_FLIP
    nodes.loc[flip, "region"] = rng.choice(REGIONS, size=int(flip.sum()))

    nodes = nodes[["node_id", "kind", "tier", "region", "subtype",
                   "capacity", "lead_time_days", "label"]]

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)

    kc = nodes.kind.value_counts()
    print(f"aircraft-supply-chain: {len(nodes)} nodes "
          f"({kc.get('material',0)} material + {kc.get('component',0)} component + "
          f"{kc.get('system',0)} system + {kc.get('integrator',0)} integrator + "
          f"{kc.get('program',0)} program), {len(edges)} edges.")


if __name__ == "__main__":
    main()
