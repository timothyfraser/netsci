"""Generate the `nyc-realestate-capital` project network (deterministic).

A temporal, multi-mode commercial-real-estate capital network for a single metro
(New York City), tracked quarter-by-quarter across three years (2024Q1–2026Q4).

Three node kinds:
  - property : individual CRE assets across the five boroughs (~190)
  - investor : equity capital providers, typed (local, poc_led, corporate,
               multinational, institutional, family_office, reit, sovereign,
               nonprofit) (~64)
  - bank     : debt / portfolio-company lenders (commercial, investment,
               community_dev/CDFI, gse, private_credit) (~16)

Edges are funding relationships provider -> property, in long temporal format
(one row per provider-property-quarter once the relationship is active). Each row
carries capital ALREADY deployed (`invested_usd`) vs capital pledged-but-not-yet
deployed (`pledged_usd`), plus the `instrument` (equity/debt/mezzanine).

This generator is the single source of truth: it writes this folder's CSVs AND
derives the companion `nyc-realestate-portfolio` projection (properties linked by
shared equity financing), so the two datasets share property `node_id`s exactly.

Design parameters (the only record of the planted structure):
  - TYPE_SORTING: equity *type* sorts by neighborhood prestige — multinational /
    sovereign / institutional capital concentrates in prime Manhattan; local /
    POC-led / community (CDFI) capital concentrates in lower-prestige outer
    neighborhoods. (Capital-source segregation, ~orthogonal to deal size.)
  - PLEDGE_GAP: in low-prestige neighborhoods, large *external* capital pledges
    but is slow to deploy (pledged lingers, invested lags) — a disinvestment gap
    in the invested/(invested+pledged) ratio that survives controlling for value;
    local/CDFI capital deploys normally.
  - OVERLEVERAGE: one REIT cross-collateralizes a cluster of ~24 gentrifying
    Brooklyn properties -> a dense over-shared community in the portfolio
    projection (concentration / single-point-of-failure).
  - SHOCK_Q: a mid-period rate shock (2025Q2) freezes new debt deployment and
    withdraws pledged capital, hitting the over-leveraged cluster + outer-borough
    assets hardest.

Run:
    python data/projects/nyc-realestate-capital/_generate.py
"""
from __future__ import annotations

from pathlib import Path
from itertools import combinations
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
PORTFOLIO_DIR = HERE.parent / "nyc-realestate-portfolio"
SEED = 42

N_PROPERTIES = 190
N_INVESTORS = 64
N_BANKS = 16
QUARTERS = [f"{y}Q{q}" for y in (2024, 2025, 2026) for q in (1, 2, 3, 4)]  # 12

# --- planted parameters -----------------------------------------------------
TYPE_SORTING = 1.0       # strength of capital-type sorting by neighborhood prime
PLEDGE_GAP = 0.78        # how much external-capital deployment slows in low-prime areas
OVERLEVERAGE_N = 24      # properties cross-collateralized by the one big REIT
SHOCK_Q = 5              # index into QUARTERS (2025Q2): rate shock
SHOCK_DEBT_SLOW = 0.45   # post-shock multiplier on new debt deployment
SHOCK_PLEDGE_WITHDRAW = 0.30  # fraction of remaining pledge withdrawn for exposed deals

# neighborhood: (name, borough, prime 0..1, x, y)  — prime = prestige/value tier
NEIGH = [
    ("Midtown",          "Manhattan",     0.97, 5.0, 9.2),
    ("FiDi",             "Manhattan",     0.93, 4.7, 7.4),
    ("Hudson Yards",     "Manhattan",     0.95, 4.3, 9.0),
    ("SoHo",             "Manhattan",     0.96, 4.8, 8.2),
    ("Upper East Side",  "Manhattan",     0.90, 5.4, 10.1),
    ("Harlem",           "Manhattan",     0.46, 5.2, 11.4),
    ("Washington Hts",   "Manhattan",     0.40, 5.0, 12.3),
    ("Williamsburg",     "Brooklyn",      0.74, 6.4, 8.0),
    ("DUMBO",            "Brooklyn",      0.82, 6.0, 7.7),
    ("Downtown Bklyn",   "Brooklyn",      0.70, 6.2, 7.2),
    ("Bushwick",         "Brooklyn",      0.52, 7.1, 8.1),
    ("Bed-Stuy",         "Brooklyn",      0.50, 6.8, 7.6),
    ("Brownsville",      "Brooklyn",      0.24, 7.6, 6.6),
    ("Sunset Park",      "Brooklyn",      0.44, 6.1, 6.2),
    ("Long Island City", "Queens",        0.72, 6.6, 9.1),
    ("Astoria",          "Queens",        0.60, 6.6, 9.9),
    ("Flushing",         "Queens",        0.55, 8.4, 9.6),
    ("Jamaica",          "Queens",        0.34, 8.6, 7.6),
    ("South Bronx",      "Bronx",         0.22, 5.7, 12.9),
    ("Fordham",          "Bronx",         0.30, 5.6, 13.6),
    ("St. George",       "Staten Island", 0.42, 4.0, 5.0),
]
PROP_TYPES = ["office", "multifamily", "retail", "industrial", "mixed_use", "hotel"]
INV_TYPES = ["local", "poc_led", "corporate", "multinational", "institutional",
             "family_office", "reit", "sovereign", "nonprofit"]
# which equity types are "big external" capital (slow to deploy in low-prime areas)
EXTERNAL = {"multinational", "institutional", "sovereign", "corporate"}
# which are place-based / mission capital (deploy regardless of prime)
LOCAL_CAP = {"local", "poc_led", "nonprofit"}
BANK_TYPES = ["commercial", "investment", "community_dev", "gse", "private_credit"]


def main() -> None:
    rng = np.random.default_rng(SEED)
    neigh = pd.DataFrame(NEIGH, columns=["neighborhood", "borough", "prime", "x", "y"])
    prime = dict(zip(neigh.neighborhood, neigh.prime))

    # ----- properties ------------------------------------------------------
    # more properties in prime + mid neighborhoods, but every neighborhood gets some
    nw = (0.5 + neigh.prime.values)
    nw = nw / nw.sum()
    p_neigh = rng.choice(neigh.neighborhood.values, N_PROPERTIES, p=nw)
    prows = []
    for i, nb in enumerate(p_neigh, start=1):
        pr = prime[nb]
        ptype = rng.choice(PROP_TYPES, p=[0.26, 0.30, 0.16, 0.12, 0.12, 0.04])
        sqft = int(np.clip(rng.lognormal(11.0 + 0.8 * pr, 0.5), 8000, 1_800_000))
        year = int(np.clip(rng.normal(1968 + 30 * pr, 26), 1900, 2025))
        bclass = rng.choice(["A", "B", "C"],
                            p=[max(0.05, pr - 0.05), 0.45, max(0.05, 0.85 - pr)]
                              / np.sum([max(0.05, pr - 0.05), 0.45, max(0.05, 0.85 - pr)]))
        # appraised value: prime + size + type premium + noise (psf * sqft)
        type_prem = {"office": 1.15, "multifamily": 1.0, "retail": 0.95,
                     "industrial": 0.7, "mixed_use": 1.05, "hotel": 1.2}[ptype]
        psf = (180 + 720 * pr) * type_prem * np.exp(rng.normal(0, 0.18))
        value = int(round(sqft * psf, -4))
        occ = float(np.clip(rng.normal(0.78 + 0.16 * pr, 0.1), 0.25, 0.99))
        nbr = neigh.loc[neigh.neighborhood == nb].iloc[0]
        prows.append({
            "node_id": f"P{i:03d}", "kind": "property",
            "label": f"{nb} {ptype.replace('_', ' ').title()} {i}",
            "borough": nbr.borough, "neighborhood": nb, "property_type": ptype,
            "building_class": bclass, "year_built": year, "sqft": sqft,
            "stories": int(np.clip(round(sqft / 18000 + rng.normal(0, 3)), 1, 95)),
            "appraised_value": value, "occupancy_rate": round(occ, 3),
            "x": round(float(nbr.x + rng.normal(0, 0.18)), 3),
            "y": round(float(nbr.y + rng.normal(0, 0.18)), 3),
        })
    props = pd.DataFrame(prows)

    # ----- investors (equity) ----------------------------------------------
    itype = rng.choice(INV_TYPES, N_INVESTORS,
                       p=[0.16, 0.12, 0.12, 0.10, 0.12, 0.10, 0.08, 0.05, 0.15])
    # ensure exactly one dominant REIT (the over-leverager): make investor I001 a reit
    itype[0] = "reit"
    inv_scale = []
    irows = []
    for i, t in enumerate(itype, start=1):
        scale = {"local": "small", "poc_led": "small", "nonprofit": "small",
                 "family_office": "mid", "corporate": "mid", "reit": "large",
                 "institutional": "large", "multinational": "large",
                 "sovereign": "large"}[t]
        if i == 1:
            scale = "large"
        inv_scale.append(scale)
        hq = rng.choice(["New York", "New York", "Boston", "London", "Toronto",
                         "Singapore", "Abu Dhabi", "Los Angeles", "Chicago"])
        if t in LOCAL_CAP:
            hq = "New York"
        irows.append({
            "node_id": f"I{i:03d}", "kind": "investor",
            "label": f"{t.replace('_', ' ').title()} Capital {i}",
            "investor_type": t, "capital_scale": scale, "hq_location": hq,
            "founded_year": int(np.clip(rng.normal(1995, 18), 1950, 2022)),
        })
    investors = pd.DataFrame(irows)
    inv_type = dict(zip(investors.node_id, investors.investor_type))
    reit_id = "I001"

    # ----- banks / portfolio-company lenders (debt) ------------------------
    btype = rng.choice(BANK_TYPES, N_BANKS, p=[0.34, 0.18, 0.18, 0.12, 0.18])
    brows = []
    for i, t in enumerate(btype, start=1):
        hq = rng.choice(["New York", "New York", "Charlotte", "London", "San Francisco"])
        if t in ("community_dev", "gse"):
            hq = "New York"
        brows.append({
            "node_id": f"B{i:02d}", "kind": "bank",
            "label": f"{t.replace('_', ' ').title()} Lender {i}",
            "lender_type": t, "hq_location": hq,
            "founded_year": int(np.clip(rng.normal(1975, 30), 1850, 2018)),
        })
    banks = pd.DataFrame(brows)
    bank_type = dict(zip(banks.node_id, banks.lender_type))

    # ----- assign providers to each property (homophily by neighborhood prime)
    inv_ids = list(investors.node_id)
    bank_ids = list(banks.node_id)

    def equity_weight(iid, pr):
        t = inv_type[iid]
        if t in EXTERNAL:                       # big external -> chase prime
            return 0.12 + TYPE_SORTING * pr
        if t in LOCAL_CAP:                      # place-based -> chase non-prime
            return 0.12 + TYPE_SORTING * (1 - pr)
        return 0.5                              # reit / family_office: neutral-ish

    def debt_weight(bid, pr):
        t = bank_type[bid]
        if t == "community_dev":
            return 0.15 + (1 - pr)              # CDFIs lend outer-borough
        if t in ("investment", "private_credit"):
            return 0.15 + pr                    # IBs / private credit chase prime
        return 0.5                              # commercial / gse: broad

    # planted over-leveraged cluster: 24 gentrifying Brooklyn props all share the REIT
    cluster_pool = props[props.neighborhood.isin(["Bushwick", "Bed-Stuy", "Williamsburg"])]
    cluster_ids = list(cluster_pool.sample(n=min(OVERLEVERAGE_N, len(cluster_pool)),
                                           random_state=7).node_id)

    rels = []   # (provider_id, property_id, instrument, commitment)
    for r in props.itertuples():
        pr = prime[r.neighborhood]
        val = r.appraised_value
        # equity syndicate (1-3 investors)
        n_eq = int(rng.choice([1, 2, 3], p=[0.45, 0.4, 0.15]))
        ew = np.array([equity_weight(i, pr) for i in inv_ids]); ew = ew / ew.sum()
        eq_pick = list(rng.choice(inv_ids, size=n_eq, replace=False, p=ew))
        if r.node_id in cluster_ids and reit_id not in eq_pick:
            eq_pick[0] = reit_id                # force the REIT into the cluster
        equity_total = val * float(np.clip(rng.normal(0.32, 0.07), 0.12, 0.5))
        shares = rng.dirichlet(np.ones(len(eq_pick)))
        for iid, s in zip(eq_pick, shares):
            instr = "mezzanine" if (inv_type[iid] == "private_credit") else "equity"
            rels.append((iid, r.node_id, instr, float(equity_total * s)))
        # debt stack (1-2 banks)
        n_db = int(rng.choice([1, 2], p=[0.6, 0.4]))
        bw = np.array([debt_weight(b, pr) for b in bank_ids]); bw = bw / bw.sum()
        db_pick = list(rng.choice(bank_ids, size=n_db, replace=False, p=bw))
        debt_total = val * float(np.clip(rng.normal(0.55, 0.08), 0.2, 0.75))
        dshares = rng.dirichlet(np.ones(len(db_pick)))
        for bid, s in zip(db_pick, dshares):
            d_instr = "mezzanine" if bank_type[bid] == "private_credit" else "debt"
            rels.append((bid, r.node_id, d_instr, float(debt_total * s)))

    # ----- simulate quarterly deployment (invested vs pledged) -------------
    # Capital ramps toward a *ceiling* fraction of its commitment; the rest is
    # pledged that never deploys. The ceiling falls in low-prestige neighborhoods
    # (a persistent disinvestment gap that survives controlling for deal value),
    # softened for place-based / mission capital that actually shows up. A mid-
    # period shock freezes deployment and withdraws pledges on exposed deals.
    prop_prime = dict(zip(props.node_id, [prime[n] for n in props.neighborhood]))

    def deploy_ceiling(prov, pr):
        base = 0.55 + 0.40 * pr                      # neighborhood disinvestment gradient
        if prov.startswith("I"):
            t = inv_type[prov]
            if t in LOCAL_CAP:
                base += 0.18 * PLEDGE_GAP            # mission capital deploys
            elif t in EXTERNAL:
                base -= 0.12 * PLEDGE_GAP            # external capital pledges, lingers
        else:
            bt = bank_type[prov]
            if bt in ("commercial", "gse"):
                base += 0.10
            elif bt == "community_dev":
                base += 0.15
        return float(np.clip(base, 0.40, 0.99))

    erows = []
    for prov, pid, instr, commit in rels:
        pr = prop_prime[pid]
        ceiling = deploy_ceiling(prov, pr)
        rate = {"debt": 0.70, "equity": 0.45, "mezzanine": 0.52}[instr]
        start_q = int(rng.integers(0, 8))
        exposed = (pid in cluster_ids) or (pr < 0.4)
        for qi in range(start_q, len(QUARTERS)):
            t = qi - start_q
            # exposed deals freeze their deployment progress at the shock
            t_eff = t
            if exposed and qi >= SHOCK_Q:
                t_eff = max(0, (SHOCK_Q - 1) - start_q)
            # debt deployment slows for everyone after the rate shock
            r_eff = rate * (SHOCK_DEBT_SLOW if (instr in ("debt", "mezzanine") and qi >= SHOCK_Q) else 1.0)
            ramp = 1 - np.exp(-r_eff * (t_eff + 1))
            invested = ceiling * commit * ramp * float(np.clip(1 + rng.normal(0, 0.02), 0.9, 1.1))
            pledged = max(0.0, commit - invested)
            if exposed and qi >= SHOCK_Q:            # pledges pulled at the shock
                pledged *= (1 - SHOCK_PLEDGE_WITHDRAW)
            erows.append({
                "from_id": prov, "to_id": pid, "quarter": QUARTERS[qi],
                "instrument": instr,
                "invested_usd": int(round(invested, -3)),
                "pledged_usd": int(round(pledged, -3)),
            })
    edges = pd.DataFrame(erows)

    # ----- assemble + write capital ----------------------------------------
    nodes = pd.concat([props, investors, banks], ignore_index=True)
    # stable column order (union; blanks where N/A)
    col_order = ["node_id", "kind", "label", "borough", "neighborhood",
                 "property_type", "building_class", "year_built", "sqft", "stories",
                 "appraised_value", "occupancy_rate", "investor_type", "capital_scale",
                 "lender_type", "hq_location", "founded_year", "x", "y"]
    for c in col_order:
        if c not in nodes.columns:
            nodes[c] = pd.NA
    nodes = nodes[col_order]
    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)

    # ----- derive portfolio projection (shared EQUITY financing only) ------
    # banks (ubiquitous debt) are excluded so the projection stays sparse and the
    # over-leveraged equity clusters stand out.
    eq_rel = [(prov, pid) for (prov, pid, instr, _c) in rels
              if prov.startswith("I")]
    by_inv: dict[str, list[str]] = {}
    invested_pp: dict[tuple, float] = {}
    tot_inv = edges.groupby(["from_id", "to_id"])["invested_usd"].max()
    for prov, pid in eq_rel:
        by_inv.setdefault(prov, []).append(pid)
        invested_pp[(prov, pid)] = float(tot_inv.get((prov, pid), 0.0))
    pair_shared: dict[tuple, int] = {}
    pair_co: dict[tuple, float] = {}
    for prov, plist in by_inv.items():
        plist = sorted(set(plist))
        for a, b in combinations(plist, 2):
            key = (a, b)
            pair_shared[key] = pair_shared.get(key, 0) + 1
            pair_co[key] = pair_co.get(key, 0.0) + min(invested_pp[(prov, a)],
                                                       invested_pp[(prov, b)])
    prows2 = [{
        "from_id": a, "to_id": b,
        "n_shared_investors": pair_shared[(a, b)],
        "co_investment_usd": int(round(pair_co[(a, b)], -3)),
    } for (a, b) in pair_shared]
    pedges = pd.DataFrame(prows2).sort_values(["from_id", "to_id"]).reset_index(drop=True)
    # portfolio nodes = properties only (same ids/traits, drop the 'kind' column)
    pnodes = props.drop(columns=["kind"]).reset_index(drop=True)

    PORTFOLIO_DIR.mkdir(parents=True, exist_ok=True)
    pnodes.to_csv(PORTFOLIO_DIR / "nodes.csv", index=False)
    pedges.to_csv(PORTFOLIO_DIR / "edges.csv", index=False)

    print(f"nyc-realestate-capital: {len(nodes)} nodes "
          f"({len(props)} properties + {len(investors)} investors + {len(banks)} banks), "
          f"{len(edges)} funding rows over {len(QUARTERS)} quarters.")
    print(f"nyc-realestate-portfolio: {len(pnodes)} properties, {len(pedges)} "
          f"shared-financing edges (over-leveraged cluster = {len(cluster_ids)} props).")


if __name__ == "__main__":
    main()
