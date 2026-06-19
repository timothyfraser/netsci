"""Generate the `trade-commodity` project network (deterministic).

International trade in a single strategic commodity ("refined metal", measured in
tonnes) among ~140 countries, observed across three periods around a supply
shock:
  - period = "before"  : normal market
  - period = "during"  : a dominant exporter goes offline
  - period = "after"   : partial, costlier rewiring

Nodes are countries (kind = "country"); edges are directed export flows
exporter -> importer for a given period, weighted by tonnes traded.

Design parameters (the only record of the planted structure):
  - DOMINANT_EXPORTERS: a few large exporters supply most of the world. One of
    them (the SHOCKED exporter) collapses to ~0 out-strength DURING and recovers
    only partially AFTER.
  - DEPENDENT_IMPORTERS: a handful of importers draw the large majority of their
    supply from ONE or TWO dominant exporters (very high top-2 supply share).
    When their dominant source goes offline they scramble: in-strength collapses
    DURING and partially rewires to costlier sources AFTER (some never recover).
  - REEXPORTER: one mid-size country imports heavily and re-exports most of it
    (import ~= export, high throughput, high betweenness) — a transshipment hub
    that brokers flow and masks origin.
  - BLOCS: trade clusters strongly within region/bloc (high modularity) with a
    few inter-bloc broker countries.
  - BROKERS: a few structurally critical countries sit on the only supply path
    into otherwise peripheral importer groups (high betweenness vs degree).

Run:
    python data/projects/trade-commodity/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

PERIODS = ["before", "during", "after"]

# blocs (region label, count, base gdp-per-capita tier 0..1)
BLOCS = [
    ("North America", 18, 0.82),
    ("South America", 20, 0.45),
    ("Europe", 30, 0.78),
    ("Africa", 28, 0.30),
    ("Middle East", 16, 0.55),
    ("Asia-Pacific", 28, 0.50),
]

# --- planted parameters -----------------------------------------------------
N_DOMINANT = 6          # big exporters that supply most of the market
SHOCK_OFFSET = 0        # index (within dominant list) of the exporter that fails
SHOCK_RECOVERY = 0.35   # AFTER out-strength as fraction of BEFORE for shocked exporter
N_DEPENDENT = 9         # importers concentrated on one/two dominant sources
DEP_SHARE = 0.86        # share of a dependent importer's supply from its top source(s)
DEP_RECOVERY = 0.55     # AFTER in-strength as fraction of BEFORE for dependents
N_PERIPHERAL_GROUPS = 4 # importer groups reachable only via a broker
COST_PREMIUM = 1.0      # AFTER price premium added when rewiring to new sources


def main() -> None:
    rng = np.random.default_rng(SEED)

    # ----- countries -------------------------------------------------------
    rows = []
    cid = 1
    bloc_of = {}
    for region, n, tier in BLOCS:
        for _ in range(n):
            gdp = int(np.clip(2500 + tier * 60000 + rng.normal(0, 9000), 800, 110000))
            # latent production / consumption capacity (tonnes), noisy
            prod = float(np.clip(rng.lognormal(mean=10.0, sigma=1.1), 2e3, 5e6))
            cons = float(np.clip(rng.lognormal(mean=10.2, sigma=0.9), 5e3, 4e6))
            node_id = f"C{cid:03d}"
            bloc_of[node_id] = region
            rows.append({
                "node_id": node_id,
                "kind": "country",
                "label": f"{region[:3].upper()}-{cid:03d}",
                "region": region,
                "gdp_per_capita": gdp,
                "production": round(prod, 0),
                "consumption": round(cons, 0),
            })
            cid += 1
    nodes = pd.DataFrame(rows)
    ids = list(nodes.node_id)
    n_countries = len(ids)
    region_arr = nodes["region"].to_numpy()
    prod_arr = nodes["production"].to_numpy().astype(float).copy()
    cons_arr = nodes["consumption"].to_numpy().astype(float).copy()

    idx_of = {nid: i for i, nid in enumerate(ids)}

    # ----- choose dominant exporters --------------------------------------
    # the highest-production countries become dominant exporters; give them a
    # large production bump so the market really concentrates on them.
    dominant = list(np.argsort(-prod_arr)[:N_DOMINANT])
    for d in dominant:
        prod_arr[d] *= 4.0
    nodes.loc[:, "production"] = prod_arr.round(0)
    shocked = dominant[SHOCK_OFFSET]

    # ----- choose dependent importers -------------------------------------
    # high-consumption, low-production countries that lean on dominant sources.
    deficit = cons_arr - prod_arr
    cand = [i for i in np.argsort(-deficit) if i not in dominant]
    dependent = cand[:N_DEPENDENT]
    # each dependent importer is pinned to 1-2 dominant sources, and the SHOCKED
    # exporter is the primary source for several of them.
    dep_sources = {}
    for k, di in enumerate(dependent):
        if k < 5:
            primary = shocked
        else:
            primary = dominant[(k % (N_DOMINANT - 1)) + 1]
        secondary = dominant[(dominant.index(primary) + 2) % N_DOMINANT]
        dep_sources[di] = (primary, secondary)

    # ----- re-exporter (transshipment hub) --------------------------------
    # a mid-size country (mid production, mid consumption) that brokers flow.
    mid = [i for i in range(n_countries)
           if i not in dominant and i not in dependent]
    # pick a mid-size country with genuine demand capacity so it can sustain a
    # high import + re-export throughput.
    mid_sorted = sorted(mid, key=lambda i: -(prod_arr[i] + cons_arr[i]))
    reexporter = mid_sorted[8]   # not a top producer, but well-connected & sizeable

    # ----- peripheral importer groups reachable only via a broker ---------
    # pick a few brokers; behind each, a cluster of small importers that buy ONLY
    # from the broker (so the broker sits on their only supply path).
    broker_pool = [i for i in mid if i != reexporter]
    rng.shuffle(broker_pool)
    brokers = broker_pool[:N_PERIPHERAL_GROUPS]
    periph = {}
    used = set(brokers) | {reexporter} | set(dominant) | set(dependent)
    remaining = [i for i in range(n_countries) if i not in used]
    rng.shuffle(remaining)
    cur = 0
    for b in brokers:
        grp = remaining[cur:cur + 4]
        cur += 4
        periph[b] = grp
        used.update(grp)

    # supplier of each broker = a NON-shocked dominant exporter (so the broker's
    # downstream group keeps a stable single supply path: dom -> broker -> periph)
    nonshock_dom = [d for d in dominant if d != shocked]
    broker_src = {b: nonshock_dom[j % len(nonshock_dom)]
                  for j, b in enumerate(brokers)}
    periph_members = {g for grp in periph.values() for g in grp}

    # ----- helper: base trade volume for a pair ---------------------------
    def base_volume(src, dst):
        # gravity-ish: bigger exporter * bigger importer, same-bloc bonus
        s = prod_arr[src] ** 0.5
        d = cons_arr[dst] ** 0.5
        bloc_bonus = 1.6 if region_arr[src] == region_arr[dst] else 1.0
        return s * d * 1e-3 * bloc_bonus

    edge_rows = []

    by_region = {}
    for r in {region_arr[i] for i in range(n_countries)}:
        by_region[r] = [i for i in range(n_countries) if region_arr[i] == r]

    # producers within each bloc, ranked by production (bloc background trade
    # routes mostly through these regional suppliers -> tight communities).
    # Exclude brokers and the re-exporter so their degree stays low and their
    # betweenness (structural role) stands out against degree.
    _excl = set(brokers) | {reexporter}
    bloc_suppliers = {r: [i for i in sorted(members, key=lambda i: -prod_arr[i])
                          if i not in _excl][:8]
                      for r, members in by_region.items()}

    # ----- build BEFORE flows ---------------------------------------------
    # 1) within-bloc background trade: every country buys from several same-bloc
    #    suppliers (dense, high-volume -> creates modular community structure).
    def background_flows(period, scale=1.0):
        out = []
        for dst in range(n_countries):
            if dst in periph_members:
                continue  # peripheral importers buy ONLY via their broker
            r = region_arr[dst]
            same = [i for i in bloc_suppliers[r] if i != dst]
            if not same:
                continue
            k = rng.integers(3, min(7, len(same) + 1))
            picks = rng.choice(same, size=min(k, len(same)), replace=False)
            for s in picks:
                vol = base_volume(s, dst) * rng.uniform(0.45, 1.1) * scale
                out.append((s, dst, vol))
        return out

    # 2) dominant exporters sell broadly across blocs (big inter-bloc ties)
    def dominant_flows(period, shocked_factor):
        out = []
        for d in dominant:
            factor = shocked_factor if d == shocked else 1.0
            buyers = rng.choice(n_countries, size=20, replace=False)
            for b in buyers:
                if b == d or b in periph_members:
                    continue
                vol = base_volume(d, b) * rng.uniform(0.20, 0.45) * factor
                out.append((d, b, vol))
        return out

    # 3) dependent importers: concentrate supply on 1-2 dominant sources, but
    #    keep a small surviving non-dominant tail that persists through the shock
    #    (so in-strength collapses DURING then partially recovers AFTER).
    def dependent_flows(period, shocked_factor):
        out = []
        for di in dependent:
            primary, secondary = dep_sources[di]
            need = cons_arr[di] * 0.9
            p_factor = shocked_factor if primary == shocked else 1.0
            s_factor = shocked_factor if secondary == shocked else 1.0
            out.append((primary, di, need * DEP_SHARE * 0.78 * p_factor))
            out.append((secondary, di, need * DEP_SHARE * 0.22 * s_factor))
            # surviving tail of non-dominant suppliers (unaffected by the shock);
            # AFTER, this tail grows as the importer rewires to costlier sources.
            r = region_arr[di]
            tail = [i for i in bloc_suppliers[r]
                    if i not in (primary, secondary, di)][:3]
            rewire = 1.0 + (2.2 if period == "after" else 0.0)
            for o in tail:
                out.append((o, di, need * (1 - DEP_SHARE) * 0.5 * rewire))
        return out

    # 4) re-exporter: imports a lot from dominants, re-exports most to many
    #    (import ~= export, very high throughput & betweenness).
    def reexport_flows(period, shocked_factor):
        out = []
        re = reexporter
        srcs = dominant[1:4]   # avoid the shocked one as sole source
        total_in = 0.0
        # large absolute imports so the hub has real throughput regardless of its
        # own small domestic consumption.
        per_src = 40000
        for s in srcs:
            f = shocked_factor if s == shocked else 1.0
            vol = per_src * rng.uniform(0.85, 1.15) * f
            out.append((s, re, vol))
            total_in += vol
        # re-export ~90% of imports to many buyers across blocs (import ~= export)
        buyers = rng.choice(n_countries, size=22, replace=False)
        buyers = [b for b in buyers if b != re and b not in periph_members]
        per = (total_in * 0.9) / max(len(buyers), 1)
        for b in buyers:
            out.append((re, b, per * rng.uniform(0.7, 1.3)))
        return out

    # 5) broker -> peripheral groups (broker is the SOLE supplier of its group,
    #    so it sits on the only supply path -> high betweenness vs degree).
    def broker_flows(period, shocked_factor):
        out = []
        for b in brokers:
            src = broker_src[b]
            f = shocked_factor if src == shocked else 1.0
            vol_in = base_volume(src, b) * 1.8 * f + 4000 * f
            out.append((src, b, vol_in))
            grp = periph[b]
            per = (vol_in * 0.85) / max(len(grp), 1)
            for g in grp:
                out.append((b, g, per * rng.uniform(0.8, 1.2)))
        return out

    def assemble(period, shocked_factor, premium):
        flows = []
        flows += [(s, d, v, "bloc") for (s, d, v) in background_flows(period)]
        flows += [(s, d, v, "major") for (s, d, v) in dominant_flows(period, shocked_factor)]
        flows += [(s, d, v, "dependency") for (s, d, v) in dependent_flows(period, shocked_factor)]
        flows += [(s, d, v, "reexport") for (s, d, v) in reexport_flows(period, shocked_factor)]
        flows += [(s, d, v, "broker") for (s, d, v) in broker_flows(period, shocked_factor)]
        for (s, d, v, kind) in flows:
            if s == d:
                continue
            noise = rng.lognormal(mean=0.0, sigma=0.25)
            tonnes = max(v * noise, 0.0)
            row = {
                "exporter_id": ids[s], "importer_id": ids[d], "period": period,
                "tonnes": int(round(tonnes)), "flow_type": kind,
            }
            # price: base + distance/scarcity; AFTER rewired flows cost more
            base_price = 900 + (0 if region_arr[s] == region_arr[d] else 220)
            base_price += premium * 180 if kind in ("dependency", "broker") else 0
            base_price *= rng.uniform(0.92, 1.10)
            row["price_usd_per_t"] = int(round(base_price))
            if row["tonnes"] >= 50:
                edge_rows.append(row)

    # BEFORE: normal
    assemble("before", shocked_factor=1.0, premium=0.0)
    # DURING: shocked exporter collapses to ~0; dependents scramble; brokers/reexport
    # drained; market does NOT fully replace the lost supply.
    assemble("during", shocked_factor=0.04, premium=0.4)
    # AFTER: shocked exporter partially recovers; dependents partially rewire to
    # costlier sources (premium up); some never recover (handled by recovery<1).
    assemble("after", shocked_factor=SHOCK_RECOVERY, premium=COST_PREMIUM)

    edges = pd.DataFrame(edge_rows)
    # collapse duplicate (exporter, importer, period) rows by summing tonnes and
    # taking a tonnes-weighted mean price. `flow_type` is an INTERNAL design tag
    # only — it is deliberately NOT written out (it would reveal the planted
    # structure). Different flow mechanisms between the same pair merge here.
    edges["_pt"] = edges["price_usd_per_t"] * edges["tonnes"]
    edges = (edges.groupby(["exporter_id", "importer_id", "period"],
                           as_index=False)
             .agg(tonnes=("tonnes", "sum"), _pt=("_pt", "sum")))
    edges["price_usd_per_t"] = (edges["_pt"] / edges["tonnes"]).round(0).astype(int)
    edges = edges[["exporter_id", "importer_id", "period", "tonnes",
                   "price_usd_per_t"]]

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)

    # Optional debug dump of planted identities (only when explicitly requested,
    # so the normal run prints just the one-line summary and never leaks the
    # story into stdout that students would see).
    import os
    if os.environ.get("TRADE_DEBUG"):
        print("DEBUG shocked_exporter:", ids[shocked])
        print("DEBUG dominant:", [ids[d] for d in dominant])
        print("DEBUG dependents:", [ids[d] for d in dependent])
        print("DEBUG reexporter:", ids[reexporter])
        print("DEBUG brokers:", [ids[b] for b in brokers])
        print("DEBUG periph:", {ids[b]: [ids[g] for g in grp]
                                 for b, grp in periph.items()})

    print(f"trade-commodity: {len(nodes)} nodes (countries), {len(edges)} edges "
          f"across {edges['period'].nunique()} periods "
          f"(before={int((edges.period=='before').sum())}, "
          f"during={int((edges.period=='during').sum())}, "
          f"after={int((edges.period=='after').sum())}).")


if __name__ == "__main__":
    main()
