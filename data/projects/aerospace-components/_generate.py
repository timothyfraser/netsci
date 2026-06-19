"""Generate the `aerospace-components` project network (deterministic).

A bill-of-materials + supplier network for one commercial aircraft program.
Two node kinds:
  - part      components and assemblies, with a tier 1..4 BOM depth
              (1 = final-assembly-level, 4 = small detail parts/fasteners/seals)
  - supplier  firms that make / provide parts

Edges are directed `supplies` / `is-part-of` relations pointing UP the build
toward the final assembly:
  - supplier -> part   (a firm supplies a part)
  - part(child, deeper tier) -> part(parent, shallower tier)  (sub-assembly
    rolls up into its parent assembly)
The edge weight is `qty_per_aircraft` (units installed per airframe).

Node attributes: kind, tier, system, safety_critical, single_source,
supplier_region, defect_rate, cert_level, label.

Design parameters (the only record of the planted structure):
  - NAIL_SUPPLIER: a tiny tier-3/4 fastener/seal supplier sits on the build path
    of MULTIPLE safety-critical assemblies. Low degree, high betweenness, and
    single_source -- the "for want of a nail" hidden critical path.
  - FAKE_DUAL: a safety-critical part has TWO apparent direct suppliers, but
    BOTH draw their key sub-part from the SAME upstream sub-supplier, so the
    redundancy is an illusion (visible only 2 hops up).
  - COUNTERFEIT_BROKER: parts sourced through one broker/region carry an
    elevated defect_rate and fan out across several systems.
  - CERT_ON_PATH: high cert_level concentrates on the critical (nail) path.

Run:
    python data/projects/aerospace-components/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

SYSTEMS = ["engine", "avionics", "fuselage", "landing_gear", "hydraulics", "interior"]
REGIONS = ["USA", "Europe", "Japan", "Mexico", "China", "India"]
CERTS = ["standard", "DO-178C", "AS9100", "NADCAP"]

# BOM shape: counts of parts per tier (tier1 shallow .. tier4 deep)
N_T1 = 18     # major assemblies (one+ per system)
N_T2 = 60     # sub-assemblies
N_T3 = 110    # components
N_T4 = 70     # detail parts (fasteners, seals, fittings)
N_SUPPLIERS = 42

# --- planted parameters -----------------------------------------------------
COUNTERFEIT_REGION = "China"     # broker region with elevated defect rate
COUNTERFEIT_BROKER_EXTRA = 0.045  # added mean defect_rate for broker parts
BASE_DEFECT = 0.012
CERT_PATH_BONUS = 2              # cert-level steps added on the critical path
N_SAFETY_VIA_NAIL = 7           # how many safety-critical assemblies the nail feeds


def main() -> None:
    rng = np.random.default_rng(SEED)

    rows = []   # node rows

    # ----- tier-1 major assemblies (one per system, then extras) -----------
    t1 = []
    for i in range(N_T1):
        sysn = SYSTEMS[i % len(SYSTEMS)]
        pid = f"A1{i+1:02d}"
        t1.append(pid)
        rows.append({"node_id": pid, "kind": "part", "tier": 1, "system": sysn,
                     "safety_critical": int(sysn in ("engine", "landing_gear", "hydraulics")),
                     "single_source": 0, "supplier_region": pd.NA,
                     "defect_rate": pd.NA, "cert_level": pd.NA,
                     "label": f"{sysn.title()} Major Assy {i+1:02d}"})

    # ----- tier-2 sub-assemblies -------------------------------------------
    t2 = []
    for i in range(N_T2):
        sysn = SYSTEMS[rng.integers(0, len(SYSTEMS))]
        pid = f"A2{i+1:03d}"
        t2.append(pid)
        rows.append({"node_id": pid, "kind": "part", "tier": 2, "system": sysn,
                     "safety_critical": int(rng.random() < 0.35 and
                                            sysn in ("engine", "landing_gear", "hydraulics", "avionics")),
                     "single_source": 0, "supplier_region": pd.NA,
                     "defect_rate": pd.NA, "cert_level": pd.NA,
                     "label": f"{sysn.title()} Sub-Assy {i+1:03d}"})

    # ----- tier-3 components ------------------------------------------------
    t3 = []
    for i in range(N_T3):
        sysn = SYSTEMS[rng.integers(0, len(SYSTEMS))]
        pid = f"C3{i+1:03d}"
        t3.append(pid)
        rows.append({"node_id": pid, "kind": "part", "tier": 3, "system": sysn,
                     "safety_critical": int(rng.random() < 0.25),
                     "single_source": 0, "supplier_region": pd.NA,
                     "defect_rate": pd.NA, "cert_level": pd.NA,
                     "label": f"{sysn.title()} Component {i+1:03d}"})

    # ----- tier-4 detail parts (fasteners, seals, fittings) ----------------
    t4 = []
    detail_kinds = ["fastener", "seal", "fitting", "bushing", "o_ring", "bolt", "rivet"]
    for i in range(N_T4):
        sysn = SYSTEMS[rng.integers(0, len(SYSTEMS))]
        pid = f"C4{i+1:03d}"
        t4.append(pid)
        dk = detail_kinds[i % len(detail_kinds)]
        rows.append({"node_id": pid, "kind": "part", "tier": 4, "system": sysn,
                     "safety_critical": int(rng.random() < 0.15),
                     "single_source": int(rng.random() < 0.45),
                     "supplier_region": pd.NA, "defect_rate": pd.NA,
                     "cert_level": pd.NA, "label": f"{dk.title()} {i+1:03d}"})

    # ----- suppliers --------------------------------------------------------
    sup = []
    for i in range(N_SUPPLIERS):
        reg = rng.choice(REGIONS, p=np.array([0.34, 0.26, 0.12, 0.12, 0.10, 0.06]))
        sid = f"S{i+1:03d}"
        sup.append(sid)
        rows.append({"node_id": sid, "kind": "supplier", "tier": pd.NA,
                     "system": pd.NA, "safety_critical": 0,
                     "single_source": 0, "supplier_region": reg,
                     "defect_rate": pd.NA, "cert_level": pd.NA,
                     "label": f"Supplier {i+1:03d} ({reg})"})

    nodes = pd.DataFrame(rows)
    region_of = dict(zip(nodes.node_id, nodes.supplier_region))
    sysd = dict(zip(nodes.node_id, nodes.system))
    sc = dict(zip(nodes.node_id, nodes.safety_critical))

    eds = []

    def add_edge(frm, to, qty, rel):
        eds.append({"from_id": frm, "to_id": to,
                    "qty_per_aircraft": int(max(qty, 1)), "relation": rel})

    # ---- BOM roll-up: deeper tier -> shallower tier -----------------------
    # each tier-2 rolls into 1 tier-1 (prefer same system)
    for p in t2:
        parents = [a for a in t1 if sysd[a] == sysd[p]] or t1
        add_edge(p, rng.choice(parents), rng.integers(1, 6), "is_part_of")
    # each tier-3 rolls into 1-2 tier-2
    for p in t3:
        cand = [a for a in t2 if sysd[a] == sysd[p]] or t2
        for par in rng.choice(cand, size=int(rng.integers(1, 3)), replace=False):
            add_edge(p, par, rng.integers(1, 12), "is_part_of")
    # each tier-4 rolls into 1-3 tier-3
    for p in t4:
        cand = [a for a in t3 if sysd[a] == sysd[p]] or t3
        for par in rng.choice(cand, size=int(rng.integers(1, 4)), replace=False):
            add_edge(p, par, rng.integers(2, 40), "is_part_of")

    # reserve the four planted suppliers so the default wiring never touches
    # them (keeps the nail tiny and the fake-dual pair clean).
    nail_supplier = sup[0]
    sup_a, sup_b, shared_subsupplier = sup[1], sup[2], sup[3]
    reserved = {nail_supplier, sup_a, sup_b, shared_subsupplier}
    open_sup = [s for s in sup if s not in reserved]
    # the nail supplier is deliberately NOT in the broker region (keep stories
    # separable); give it an ordinary region.
    nodes.loc[nodes.node_id == nail_supplier, "supplier_region"] = "USA"
    region_of[nail_supplier] = "USA"

    # ---- suppliers -> parts (who makes what) ------------------------------
    # default: each non-trivial part has 1-2 suppliers (dual-source common)
    part_ids = t1 + t2 + t3 + t4
    supplied_by = {}
    for p in part_ids:
        n_sup = 1 if rng.random() < 0.5 else 2
        chosen = list(rng.choice(open_sup, size=n_sup, replace=False))
        supplied_by[p] = chosen
        for s in chosen:
            add_edge(s, p, rng.integers(1, 20), "supplies")

    # =========================================================================
    # PLANTED (a): the "nail" -- a tiny tier-4 supplier on many critical paths
    # =========================================================================
    # pick a small tier-4 seal/fastener part and make ONE supplier its sole
    # source; that part rolls up into several safety-critical assemblies.
    nail_part = t4[3]                         # a single detail part
    nodes.loc[nodes.node_id == nail_part, "single_source"] = 1
    # the nail supplier ONLY makes the nail part (low degree). Clear any prior
    # suppliers of the nail part, then set the sole source.
    eds = [e for e in eds if not (e["relation"] == "supplies" and e["to_id"] == nail_part)]
    add_edge(nail_supplier, nail_part, 120, "supplies")
    supplied_by[nail_part] = [nail_supplier]
    # route the nail part up into N safety-critical tier-3 components that each
    # belong to a DIFFERENT safety-critical assembly chain
    # ensure targets are (or become) safety_critical and roll into sc tier-2/1
    targets = list(rng.choice(t3, size=N_SAFETY_VIA_NAIL, replace=False))
    for c in targets:
        nodes.loc[nodes.node_id == c, "safety_critical"] = 1
        add_edge(nail_part, c, rng.integers(8, 30), "is_part_of")
        # make sure c rolls into a safety-critical tier-2 -> tier-1 path
        par2 = rng.choice(t2)
        nodes.loc[nodes.node_id == par2, "safety_critical"] = 1
        add_edge(c, par2, rng.integers(1, 6), "is_part_of")
        par1 = rng.choice(t1)
        nodes.loc[nodes.node_id == par1, "safety_critical"] = 1
        add_edge(par2, par1, rng.integers(1, 4), "is_part_of")

    # =========================================================================
    # PLANTED (b): fake dual-sourcing -- a safety-critical part with two
    # apparent suppliers that BOTH depend on the same upstream sub-supplier.
    # =========================================================================
    dual_part = t2[5]
    nodes.loc[nodes.node_id == dual_part, "safety_critical"] = 1
    # clear any existing suppliers of dual_part, set exactly two (sup_a, sup_b
    # were reserved above)
    eds = [e for e in eds if not (e["relation"] == "supplies" and e["to_id"] == dual_part)]
    add_edge(sup_a, dual_part, 4, "supplies")
    add_edge(sup_b, dual_part, 4, "supplies")
    supplied_by[dual_part] = [sup_a, sup_b]
    # both sup_a and sup_b draw a key sub-component from the SAME tier-3 part,
    # which is itself single-sourced from one hidden sub-supplier.
    shared_subpart = t3[7]
    nodes.loc[nodes.node_id == shared_subpart, "single_source"] = 1
    eds = [e for e in eds if not (e["relation"] == "supplies" and e["to_id"] == shared_subpart)]
    add_edge(shared_subsupplier, shared_subpart, 16, "supplies")
    # the shared sub-part feeds parts that sup_a and sup_b make. Represent the
    # supplier dependence as: shared_subpart -> two intermediate parts, each of
    # which is_part_of the dual_part, and each made by sup_a / sup_b.
    int_a, int_b = t3[8], t3[9]
    # sup_a is the sole supplier of int_a, sup_b of int_b: drop any prior
    # suppliers of these two intermediates first, then set the sole sources.
    eds = [e for e in eds if not (e["relation"] == "supplies"
                                  and e["to_id"] in (int_a, int_b))]
    nodes.loc[nodes.node_id.isin([int_a, int_b]), "single_source"] = 1
    add_edge(shared_subpart, int_a, 6, "is_part_of")
    add_edge(shared_subpart, int_b, 6, "is_part_of")
    add_edge(int_a, dual_part, 2, "is_part_of")
    add_edge(int_b, dual_part, 2, "is_part_of")
    add_edge(sup_a, int_a, 3, "supplies")
    add_edge(sup_b, int_b, 3, "supplies")

    # =========================================================================
    # PLANTED (c): counterfeit-risk cluster -- one broker region's parts have
    # elevated defect rates and fan out across several systems.
    # =========================================================================
    broker_suppliers = [s for s in sup if region_of[s] == COUNTERFEIT_REGION]
    if not broker_suppliers:
        broker_suppliers = [sup[-1]]
        nodes.loc[nodes.node_id == sup[-1], "supplier_region"] = COUNTERFEIT_REGION
        region_of[sup[-1]] = COUNTERFEIT_REGION

    # ---- assign defect_rate & cert_level to PARTS -------------------------
    # a part's defect_rate reflects (mainly) its supplier region + part tier +
    # noise. Parts sourced from the broker region carry the planted bump.
    edge_df = pd.DataFrame(eds)
    sup_edges = edge_df[edge_df.relation == "supplies"]
    part_to_sups = sup_edges.groupby("to_id")["from_id"].apply(list).to_dict()

    for p in part_ids:
        srcs = part_to_sups.get(p, [])
        regs = [region_of[s] for s in srcs if pd.notna(region_of.get(s))]
        broker = any(r == COUNTERFEIT_REGION for r in regs)
        tier = int(nodes.loc[nodes.node_id == p, "tier"].iloc[0])
        base = BASE_DEFECT + 0.004 * (tier - 1)
        if broker:
            base += COUNTERFEIT_BROKER_EXTRA
        dr = float(np.clip(base + rng.normal(0, 0.010), 0.001, 0.20))
        nodes.loc[nodes.node_id == p, "defect_rate"] = round(dr, 4)
        # cert level: higher for safety-critical & shallow tiers, plus noise
        base_cert = 0
        if sc.get(p, 0) or nodes.loc[nodes.node_id == p, "safety_critical"].iloc[0]:
            base_cert += 1
        if tier <= 2:
            base_cert += 1
        base_cert += int(rng.random() < 0.3)
        nodes.loc[nodes.node_id == p, "cert_level"] = CERTS[min(base_cert, len(CERTS) - 1)]

    # suppliers carry the mean defect_rate of what they ship (noisy proxy)
    for s in sup:
        myparts = sup_edges[sup_edges.from_id == s]["to_id"].tolist()
        if myparts:
            mdr = nodes.loc[nodes.node_id.isin(myparts), "defect_rate"].astype(float).mean()
            nodes.loc[nodes.node_id == s, "defect_rate"] = round(float(mdr), 4)

    # =========================================================================
    # PLANTED (d): certification bottleneck -- bump cert on the nail path.
    # =========================================================================
    crit_path = {nail_part} | set(targets)
    for c in crit_path:
        cur = nodes.loc[nodes.node_id == c, "cert_level"].iloc[0]
        i0 = CERTS.index(cur) if cur in CERTS else 0
        nodes.loc[nodes.node_id == c, "cert_level"] = CERTS[min(i0 + CERT_PATH_BONUS, len(CERTS) - 1)]

    edges = pd.DataFrame(eds)

    # final column order
    nodes = nodes[["node_id", "kind", "tier", "system", "safety_critical",
                   "single_source", "supplier_region", "defect_rate",
                   "cert_level", "label"]]
    edges = edges[["from_id", "to_id", "qty_per_aircraft", "relation"]]

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)

    kc = nodes.kind.value_counts()
    print(f"aerospace-components: {len(nodes)} nodes "
          f"({kc.get('part',0)} part + {kc.get('supplier',0)} supplier), "
          f"{len(edges)} edges.")


if __name__ == "__main__":
    main()
