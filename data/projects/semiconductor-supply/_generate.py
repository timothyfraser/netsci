"""Generate the `semiconductor-supply` project network (deterministic).

A multi-tier global semiconductor supply chain spanning five tiers of nodes:
  - tier 4  material   raw materials, specialty gases, wafers, photoresist
  - tier 3  foundry    wafer fabrication plants ("fabs")
  - tier 2  packaging  assembly / test / advanced packaging houses (OSATs)
  - tier 1  designer   chip designers and IDMs (place orders for silicon)
  - tier 0  product    end OEM products (phones, GPUs, cars, servers)

Edges are directed supply flows from upstream (higher tier number) to
downstream (lower tier number). One row per supply relationship. The edge
weight is `annual_volume` (millions of units / wafer-starts) with a paired
`value_musd` ($ value) and `lead_time_days`.

Node attributes: kind, tier, region, capacity, lead_time_days, label.
Regions: Taiwan, South Korea, USA, Japan, China, Europe.

Design parameters (the only record of the planted structure):
  - HUB_FOUNDRY: one advanced Taiwan foundry takes a dominant share of all
    *advanced-node* demand. Many tier-1 designers route advanced parts through
    it, so it has high BETWEENNESS but only modest in-degree (a few fat edges,
    not many edges). Removing it severs most advanced product output.
  - ADV_PACK_REGION: advanced `packaging` is concentrated in ONE region
    (Taiwan); a regional shock severs many advanced downstream paths.
  - CHOKE_MATERIAL: one tier-4 specialty-gas supplier feeds nearly every
    foundry (a second hidden critical node, again betweenness >> degree-rank).
  - LEADTIME_ON_PATH: the longest lead times cluster ON the critical path
    (hub foundry, choke material, advanced packaging) so the bottleneck is
    also the slowest to recover.

Run:
    python data/projects/semiconductor-supply/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

REGIONS = ["Taiwan", "South Korea", "USA", "Japan", "China", "Europe"]

# tier population sizes (total ~ 360 nodes)
N_MATERIAL = 70     # tier 4
N_FOUNDRY = 46      # tier 3
N_PACKAGING = 60    # tier 2
N_DESIGNER = 96     # tier 1
N_PRODUCT = 96      # tier 0

# --- planted parameters -----------------------------------------------------
HUB_SHARE = 0.78          # share of advanced-node demand the hub foundry takes
CHOKE_SHARE = 0.88        # share of foundries the choke material feeds
ADV_PACK_REGION = "Taiwan"
ADV_PACK_CONC = 0.80      # share of advanced packaging routed to that region
LEADTIME_PATH_BONUS = 70  # extra lead-time days loaded onto the critical path
NOISE_REGION_FLIP = 0.10  # fraction of nodes whose region is "wrong" (noise)


def main() -> None:
    rng = np.random.default_rng(SEED)

    # region sampling weights: chip world is Asia-heavy
    rweights = np.array([0.26, 0.16, 0.18, 0.14, 0.16, 0.10])
    rweights = rweights / rweights.sum()

    def pick_regions(n):
        return rng.choice(REGIONS, size=n, p=rweights)

    rows = []  # node rows

    # ----- tier 4: materials ----------------------------------------------
    mat_kinds = ["specialty_gas", "silicon_wafer", "photoresist", "rare_earth",
                 "sputter_target", "cmp_slurry", "lead_frame", "bonding_wire"]
    mat_region = pick_regions(N_MATERIAL)
    for i in range(N_MATERIAL):
        sub = mat_kinds[i % len(mat_kinds)]
        rows.append({
            "node_id": f"M{i+1:03d}", "kind": "material", "tier": 4,
            "region": mat_region[i], "subtype": sub,
            "capacity": int(rng.integers(200, 4000)),
            "lead_time_days": int(np.clip(rng.normal(60, 18), 14, 140)),
            "label": f"{sub.replace('_',' ').title()} Co {i+1:03d}",
        })

    # ----- tier 3: foundries ----------------------------------------------
    f_region = pick_regions(N_FOUNDRY)
    # node tier (process node, nm); a minority are "advanced" (<= 7nm)
    f_node_nm = rng.choice([28, 14, 10, 7, 5, 3], size=N_FOUNDRY,
                           p=[0.30, 0.18, 0.14, 0.16, 0.14, 0.08])
    for i in range(N_FOUNDRY):
        adv = f_node_nm[i] <= 7
        rows.append({
            "node_id": f"F{i+1:03d}", "kind": "foundry", "tier": 3,
            "region": f_region[i], "subtype": f"{int(f_node_nm[i])}nm",
            "capacity": int(rng.integers(20, 220) * (3 if adv else 1)),
            "lead_time_days": int(np.clip(rng.normal(95, 22), 40, 200)),
            "label": f"Fab {i+1:03d} ({int(f_node_nm[i])}nm)",
        })

    # ----- tier 2: packaging ----------------------------------------------
    p_region = pick_regions(N_PACKAGING)
    p_adv = rng.random(N_PACKAGING) < 0.40  # advanced packaging (2.5D/3D/CoWoS)
    # advanced packaging is geographically concentrated: ~70% of the advanced
    # houses sit in ADV_PACK_REGION (a planted single-region dependence).
    for i in range(N_PACKAGING):
        if p_adv[i] and rng.random() < 0.70:
            p_region[i] = ADV_PACK_REGION
    for i in range(N_PACKAGING):
        sub = "advanced" if p_adv[i] else "standard"
        rows.append({
            "node_id": f"P{i+1:03d}", "kind": "packaging", "tier": 2,
            "region": p_region[i], "subtype": sub,
            "capacity": int(rng.integers(30, 300)),
            "lead_time_days": int(np.clip(rng.normal(40, 12), 12, 90)),
            "label": f"OSAT {i+1:03d} ({sub})",
        })

    # ----- tier 1: designers ----------------------------------------------
    d_region = pick_regions(N_DESIGNER)
    d_segment = rng.choice(["mobile", "gpu", "cpu", "auto", "iot", "network"],
                           size=N_DESIGNER)
    # designers that need advanced nodes (high-performance silicon)
    d_advanced = np.isin(d_segment, ["gpu", "cpu", "mobile"]) & (rng.random(N_DESIGNER) < 0.85)
    for i in range(N_DESIGNER):
        rows.append({
            "node_id": f"D{i+1:03d}", "kind": "designer", "tier": 1,
            "region": d_region[i], "subtype": d_segment[i],
            "capacity": int(rng.integers(50, 600)),
            "lead_time_days": int(np.clip(rng.normal(30, 10), 7, 70)),
            "label": f"Designer {i+1:03d} ({d_segment[i]})",
        })

    # ----- tier 0: products -----------------------------------------------
    pr_region = pick_regions(N_PRODUCT)
    pr_segment = rng.choice(["phone", "gpu_card", "server", "vehicle", "iot_device",
                             "router"], size=N_PRODUCT)
    for i in range(N_PRODUCT):
        rows.append({
            "node_id": f"E{i+1:03d}", "kind": "product", "tier": 0,
            "region": pr_region[i], "subtype": pr_segment[i],
            "capacity": int(rng.integers(100, 2000)),
            "lead_time_days": int(np.clip(rng.normal(20, 8), 5, 50)),
            "label": f"Product {i+1:03d} ({pr_segment[i]})",
        })

    nodes = pd.DataFrame(rows)

    # convenient id pools / lookups
    def ids(kind):
        return nodes.loc[nodes.kind == kind, "node_id"].tolist()
    mat_ids = ids("material")
    fou_ids = ids("foundry")
    pack_ids = ids("packaging")
    des_ids = ids("designer")
    prod_ids = ids("product")
    region_of = dict(zip(nodes.node_id, nodes.region))
    sub_of = dict(zip(nodes.node_id, nodes.subtype))

    adv_fou = [f for f in fou_ids if int(sub_of[f].replace("nm", "")) <= 7]
    std_fou = [f for f in fou_ids if f not in adv_fou]
    adv_pack = [p for p in pack_ids if sub_of[p] == "advanced"]
    std_pack = [p for p in pack_ids if p not in adv_pack]
    adv_pack_region = [p for p in adv_pack if region_of[p] == ADV_PACK_REGION]
    if not adv_pack_region:  # safety
        adv_pack_region = adv_pack[:1]

    # ---- pick the planted critical nodes ---------------------------------
    # HUB_FOUNDRY: a Taiwan advanced foundry
    tw_adv = [f for f in adv_fou if region_of[f] == "Taiwan"]
    HUB_FOUNDRY = tw_adv[0] if tw_adv else adv_fou[0]
    # CHOKE_MATERIAL: a specialty-gas material supplier (feeds foundries)
    gas_ids = nodes.loc[(nodes.kind == "material") &
                        (nodes.subtype == "specialty_gas"), "node_id"].tolist()
    CHOKE_MATERIAL = gas_ids[0]

    advanced_designers = [d for d, a in zip(des_ids, d_advanced) if a]
    adv_designers_set = set(advanced_designers)
    std_designers = [d for d in des_ids if d not in adv_designers_set]

    # advanced products (high-performance) vs mature products
    prod_seg = dict(zip(prod_ids, pr_segment))
    adv_prod = [e for e in prod_ids if prod_seg[e] in ("gpu_card", "server", "phone")]
    std_prod = [e for e in prod_ids if e not in set(adv_prod)]

    eds = []  # edge rows

    def add_edge(frm, to, vol, ltd):
        eds.append({
            "from_id": frm, "to_id": to,
            "annual_volume": int(max(vol, 1)),
            "value_musd": round(float(max(vol, 1)) * rng.uniform(0.02, 0.18), 3),
            "lead_time_days": int(ltd),
        })

    def lt_of(n):
        return int(nodes.loc[nodes.node_id == n, "lead_time_days"].iloc[0])

    choke_lt = lt_of(CHOKE_MATERIAL)
    hub_lt = lt_of(HUB_FOUNDRY)

    # DECOY commodity materials that feed almost every mature foundry. They are
    # the highest-DEGREE upstream nodes, but fully substitutable (mature
    # foundries have many suppliers), so removing one cuts almost nothing.
    # Their job is to out-rank the real choke on degree, hiding the choke.
    commodity_pool = [m for m in mat_ids
                      if sub_of[m] == "silicon_wafer" and m != CHOKE_MATERIAL]
    COMMODITY = commodity_pool[0]
    COMMODITY2 = commodity_pool[1]

    # Strict tier order: material(4) -> foundry(3) -> packaging(2)
    #                    -> designer(1) -> product(0).
    #
    # Two weakly separable corridors:
    #   * a MATURE corridor that is richly multi-sourced (resilient), and
    #   * an ADVANCED corridor that funnels through the choke material, the hub
    #     foundry, and Taiwan advanced packaging (fragile single points).
    # The advanced corridor never borrows resilience from the mature side, so
    # the hub & choke are genuine cut vertices for advanced product output --
    # findable by criticality/betweenness but NOT by raw degree.

    # ===== ADVANCED CORRIDOR (the fragile spine) ==========================
    # choke material -> the advanced foundries (its ONLY upstream input).
    add_edge(CHOKE_MATERIAL, HUB_FOUNDRY, int(rng.integers(150, 260)), choke_lt)
    for f in adv_fou:
        if f != HUB_FOUNDRY:
            add_edge(CHOKE_MATERIAL, f, int(rng.integers(60, 160)), choke_lt)

    # hub foundry -> advanced packaging corridor (the Taiwan-led set).
    # The hub is the SOLE upstream feeder of every advanced packaging house,
    # so it lies on every path to the advanced products beyond them -- a genuine
    # cut vertex -- while touching only a handful of nodes (modest degree).
    corridor_pack = list(adv_pack)              # ALL advanced packaging
    # bias volume toward the Taiwan houses so the geographic concentration is
    # real but not a giveaway (noise on the non-Taiwan houses).
    for p in corridor_pack:
        vol = int(rng.integers(180, 360)) if region_of.get(p) == ADV_PACK_REGION \
            else int(rng.integers(40, 110))
        add_edge(HUB_FOUNDRY, p, vol, hub_lt)

    # the other advanced fabs exist but sell into the MATURE designer market
    # (a secondary outlet) -- they do NOT feed advanced packaging, so they give
    # the advanced corridor no alternative path.
    for f in adv_fou:
        if f != HUB_FOUNDRY:
            for d in rng.choice(std_designers, size=int(rng.integers(1, 3)), replace=False):
                add_edge(f, d, int(rng.integers(20, 90)), lt_of(f))

    # advanced packaging -> advanced designers. Each designer draws mostly from
    # the Taiwan corridor houses (concentration) plus occasionally another.
    tw_pack = [p for p in corridor_pack if region_of.get(p) == ADV_PACK_REGION] or corridor_pack
    for d in advanced_designers:
        if rng.random() < ADV_PACK_CONC:
            add_edge(rng.choice(tw_pack), d, int(rng.integers(80, 300)), lt_of(tw_pack[0]))
        else:
            p = rng.choice(corridor_pack)
            add_edge(p, d, int(rng.integers(80, 300)), lt_of(p))
    # advanced designers -> advanced products
    for e in adv_prod:
        for d in rng.choice(advanced_designers, size=int(rng.integers(1, 3)), replace=False):
            add_edge(d, e, int(rng.integers(60, 400)), lt_of(d))

    # ===== MATURE CORRIDOR (resilient, multi-sourced) =====================
    # materials -> mature foundries. The COMMODITY feeds nearly all of them
    # (highest degree, but substitutable); a moderate share also draw the
    # choke gas; everyone has 2-4 ordinary suppliers.
    for f in std_fou:
        add_edge(COMMODITY, f, int(rng.integers(40, 160)), lt_of(COMMODITY))
        # a SECOND commodity wafer line feeds most mature foundries too, so the
        # commodity suppliers (not the choke gas) dominate raw degree.
        if rng.random() < 0.85:
            add_edge(COMMODITY2, f, int(rng.integers(30, 120)), lt_of(COMMODITY2))
        if rng.random() < 0.25:
            add_edge(CHOKE_MATERIAL, f, int(rng.integers(30, 120)), choke_lt)
        excl = (COMMODITY, COMMODITY2, CHOKE_MATERIAL)
        for m in rng.choice([x for x in mat_ids if x not in excl],
                            size=int(rng.integers(2, 5)), replace=False):
            add_edge(m, f, int(rng.integers(5, 80)), lt_of(m))
    # some materials also feed standard packaging directly
    for p in std_pack:
        for m in rng.choice([x for x in mat_ids if x != CHOKE_MATERIAL],
                            size=int(rng.integers(1, 3)), replace=False):
            add_edge(m, p, int(rng.integers(5, 60)), lt_of(m))
    # mature foundries -> standard packaging (multi-sourced)
    for p in std_pack:
        for f in rng.choice(std_fou, size=int(rng.integers(2, 4)), replace=False):
            add_edge(f, p, int(rng.integers(20, 120)), lt_of(f))
    # standard packaging -> mature designers
    for d in std_designers:
        for p in rng.choice(std_pack, size=int(rng.integers(2, 4)), replace=False):
            add_edge(p, d, int(rng.integers(30, 120)), lt_of(p))
    # mature designers -> mature products
    for e in std_prod:
        for d in rng.choice(std_designers, size=int(rng.integers(2, 4)), replace=False):
            add_edge(d, e, int(rng.integers(50, 300)), lt_of(d))

    corridor_pack = list(dict.fromkeys(corridor_pack))
    edges = pd.DataFrame(eds)

    # ---- LEADTIME_ON_PATH: load extra lead time onto the critical path ----
    crit = {HUB_FOUNDRY, CHOKE_MATERIAL}
    crit |= set(corridor_pack)
    nodes.loc[nodes.node_id.isin(crit), "lead_time_days"] = (
        nodes.loc[nodes.node_id.isin(crit), "lead_time_days"] + LEADTIME_PATH_BONUS
    ).clip(upper=300)
    # reflect onto edges that originate from those critical nodes
    edges.loc[edges.from_id.isin(crit), "lead_time_days"] = (
        edges.loc[edges.from_id.isin(crit), "lead_time_days"] + LEADTIME_PATH_BONUS
    ).clip(upper=320)

    # ---- region noise: flip a few regions so region != destiny ------------
    flip = rng.random(len(nodes)) < NOISE_REGION_FLIP
    nodes.loc[flip, "region"] = rng.choice(REGIONS, size=int(flip.sum()))

    nodes = nodes[["node_id", "kind", "tier", "region", "subtype",
                   "capacity", "lead_time_days", "label"]]

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)

    kc = nodes.kind.value_counts()
    print(f"semiconductor-supply: {len(nodes)} nodes "
          f"({kc.get('material',0)} material + {kc.get('foundry',0)} foundry + "
          f"{kc.get('packaging',0)} packaging + {kc.get('designer',0)} designer + "
          f"{kc.get('product',0)} product), {len(edges)} edges.")


if __name__ == "__main__":
    main()
