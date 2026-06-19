"""Generate the `mutualaid-quake` project network (deterministic).

A neighborhood mutual-aid network in fictional "Eastvale" spanning three periods
of an earthquake disaster:
  - period = "before"   (ordinary times, sparse helping)
  - period = "during"   (the shock; helping surges)
  - period = "after"    (recovery; partly persistent)

Nodes are people and organizations across eight sub-neighborhood blocks (B1..B8):
  - ~residents (kind = "resident")
  - ~orgs      (kind = "org") churches, schools, nonprofits, community centers
  -> ~250 nodes total.

Edges are directed acts of aid GIVEN from giver to receiver (food / shelter /
info / money), weighted by amount/frequency, one row per (giver, receiver,
period).

Design parameters (the only record of the planted structure):
  - CIVIC_ACTIVATION: orgs and prior-civic residents are ordinary "before" but
    their out/in strength jumps far more than others "during" (latent social
    capital activates) and decays only partly "after".
  - BRIDGE_RECOVERY: blocks with more cross-block bridging ties receive more aid
    "after" (bridging predicts recovery); STARVED_BLOCK has almost no bridges and
    stays starved.
  - ENCLAVE_BLOCK: one high-income block is internally cohesive but barely linked
    to the rest (external-tie share low despite high income).
  - BROKERS: a few residents with low "before" centrality have the highest
    betweenness "during" (emergent informal leaders / brokers).
  - DENSIFY/PERSIST: edge counts rise "during" then partly persist "after"
    (new ties formed = social capital), non-uniformly across blocks.

Run:
    python data/projects/mutualaid-quake/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

N_RESIDENTS = 222
N_ORGS = 28                       # -> 250 nodes
BLOCKS = [f"B{i}" for i in range(1, 9)]
PERIODS = ["before", "during", "after"]
AID_TYPES = ["food", "shelter", "info", "money"]

# --- planted parameters -----------------------------------------------------
PRIOR_CIVIC_RATE = 0.20          # share of residents civically active pre-quake
CIVIC_ACTIVATION = 3.4           # multiplier on "during" giving for orgs/civic
CIVIC_PERSIST = 1.6              # residual "after" multiplier for them
ENCLAVE_BLOCK = "B6"             # affluent, internally cohesive, externally sparse
ENCLAVE_EXTERNAL_DAMP = 0.12     # enclave cross-block ties scaled way down
STARVED_BLOCK = "B8"             # isolated; almost no bridges; recovers poorly
N_BROKERS = 9                    # emergent informal leaders during the shock
DENSIFY = {"before": 1.0, "during": 3.2, "after": 1.7}  # base tie-rate by period

# per-block "bridging propensity": how readily a block forms cross-block ties.
# High-bridge blocks recover better "after"; enclave & starved are low.
BRIDGE_PROPENSITY = {
    "B1": 1.30, "B2": 1.15, "B3": 1.45, "B4": 1.00,
    "B5": 0.85, "B6": 0.25, "B7": 1.20, "B8": 0.18,
}
# block base income centers (USD), gives a spatial-ish gradient + noise
BLOCK_INCOME = {
    "B1": 62000, "B2": 54000, "B3": 71000, "B4": 48000,
    "B5": 58000, "B6": 138000, "B7": 66000, "B8": 41000,
}


def _gini(x: np.ndarray) -> float:
    x = np.sort(np.asarray(x, dtype=float))
    n = len(x)
    if n == 0 or x.sum() == 0:
        return 0.0
    idx = np.arange(1, n + 1)
    return float((2 * (idx * x).sum() - (n + 1) * x.sum()) / (n * x.sum()))


def main() -> None:
    rng = np.random.default_rng(SEED)

    # ----- residents -------------------------------------------------------
    # assign residents to blocks (enclave & starved a bit smaller)
    block_w = np.array([1.0, 1.0, 1.0, 1.1, 1.0, 0.75, 1.0, 0.7])
    block_w /= block_w.sum()
    res_block = rng.choice(BLOCKS, N_RESIDENTS, p=block_w)

    income = np.array([
        np.clip(BLOCK_INCOME[b] + rng.normal(0, 11000), 18000, 240000)
        for b in res_block
    ])
    tenure = np.where(
        rng.random(N_RESIDENTS) < (0.35 + 0.0000035 * (income - 40000)),
        "homeowner", "renter")
    age = np.clip(rng.normal(44, 16, N_RESIDENTS), 18, 92).round(0).astype(int)
    # prior civic engagement: more likely for homeowners & longer-lived; noisy.
    civic_p = np.clip(
        PRIOR_CIVIC_RATE
        + 0.10 * (tenure == "homeowner")
        + 0.004 * (age - 44)
        + rng.normal(0, 0.05, N_RESIDENTS),
        0.02, 0.85)
    prior_civic = (rng.random(N_RESIDENTS) < civic_p).astype(int)

    residents = pd.DataFrame({
        "node_id": [f"P{i:03d}" for i in range(1, N_RESIDENTS + 1)],
        "kind": "resident",
        "block": res_block,
        "income": income.round(0).astype(int),
        "tenure": tenure,
        "age": age,
        "prior_civic": prior_civic,
        "label": [f"Resident {i:03d}" for i in range(1, N_RESIDENTS + 1)],
    })

    # ----- orgs ------------------------------------------------------------
    org_kinds = ["church", "school", "nonprofit", "community_center"]
    org_block = rng.choice(BLOCKS, N_ORGS)
    org_type = rng.choice(org_kinds, N_ORGS)
    orgs = pd.DataFrame({
        "node_id": [f"O{i:03d}" for i in range(1, N_ORGS + 1)],
        "kind": "org",
        "block": org_block,
        "income": pd.NA,
        "tenure": pd.NA,
        "age": pd.NA,
        "prior_civic": 1,            # orgs are civic by definition
        "label": [f"{t.replace('_', ' ').title()} {i:02d}"
                  for i, t in zip(range(1, N_ORGS + 1), org_type)],
    })

    nodes = pd.concat([residents, orgs], ignore_index=True)
    node_ids = list(nodes.node_id)
    block_of = dict(zip(nodes.node_id, nodes.block))
    is_org = dict(zip(nodes.node_id, nodes.kind == "org"))
    civic_of = dict(zip(nodes.node_id, nodes.prior_civic.fillna(0).astype(int)))

    # "latent capacity" = how central a node becomes during the shock.
    # orgs and prior-civic residents have high latent capacity (the planted hubs).
    by_block = {b: [n for n in node_ids if block_of[n] == b] for b in BLOCKS}

    # emergent brokers: pick low-civic ordinary residents (not orgs, not civic)
    ordinary = [n for n in node_ids
                if not is_org[n] and civic_of[n] == 0]
    broker_set = set(rng.choice(ordinary, N_BROKERS, replace=False))

    latent = {}
    for n in node_ids:
        base = rng.gamma(2.0, 0.5)
        if is_org[n]:
            base *= CIVIC_ACTIVATION
        elif civic_of[n] == 1:
            base *= (CIVIC_ACTIVATION * 0.7)
        latent[n] = base

    # per-node small "popularity" used to weight who receives aid generally
    popularity = {n: rng.gamma(2.0, 1.0) for n in node_ids}

    # ----- build edges -----------------------------------------------------
    # We sample directed giver->receiver ties per period. The number of ties a
    # node initiates scales with its period-specific "giving capacity".
    rows = []

    def giving_capacity(n, period):
        # baseline ordinary capacity (small, gamma) + activation during shock
        base = 0.6 + 0.5 * rng.gamma(1.5, 1.0)
        cap = base
        if period == "during":
            if is_org[n] or civic_of[n] == 1:
                cap *= CIVIC_ACTIVATION
            else:
                cap *= 1.5            # general densification for everyone
        elif period == "after":
            if is_org[n] or civic_of[n] == 1:
                cap *= CIVIC_PERSIST
            else:
                cap *= 1.05
        return cap

    def pick_receiver(giver, period):
        gb = block_of[giver]
        # decide same-block vs cross-block (a "bridge")
        bridge_pref = BRIDGE_PROPENSITY[gb]
        # enclave gives almost no external ties
        if gb == ENCLAVE_BLOCK:
            bridge_pref *= ENCLAVE_EXTERNAL_DAMP
        p_bridge = np.clip(0.35 * bridge_pref, 0.02, 0.85)
        cross = rng.random() < p_bridge
        if cross:
            others = [b for b in BLOCKS if b != gb]
            # starved block is rarely chosen as a bridge target (few bridges in)
            w = np.array([0.2 if b == STARVED_BLOCK else 1.0 for b in others])
            tb = rng.choice(others, p=w / w.sum())
            pool = by_block[tb]
        else:
            pool = [x for x in by_block[gb] if x != giver]
        if not pool:
            return None
        # receivers weighted by popularity; brokers attract more flow DURING
        wts = np.array([popularity[x] for x in pool], dtype=float)
        if period == "during":
            for k, x in enumerate(pool):
                if x in broker_set:
                    wts[k] *= 4.0      # brokers sit on many during-shock paths
        wts /= wts.sum()
        return str(rng.choice(pool, p=wts))

    for period in PERIODS:
        rate = DENSIFY[period]
        for giver in node_ids:
            cap = giving_capacity(giver, period) * rate
            n_ties = rng.poisson(max(cap, 0.05))
            # brokers initiate extra bridging ties during the shock
            if period == "during" and giver in broker_set:
                n_ties += rng.poisson(4.0)
            seen = {}
            for _ in range(int(n_ties)):
                recv = pick_receiver(giver, period)
                if recv is None or recv == giver:
                    continue
                key = recv
                # amount of aid (weight): orgs/civic give larger amounts during
                amt = rng.gamma(2.0, 18.0)
                if period == "during" and (is_org[giver] or civic_of[giver] == 1):
                    amt *= 1.5
                aid = rng.choice(AID_TYPES, p=[0.4, 0.2, 0.25, 0.15])
                if key in seen:
                    seen[key]["amount"] += amt
                    seen[key]["acts"] += 1
                else:
                    seen[key] = {"amount": amt, "acts": 1, "aid_type": aid}
            for recv, d in seen.items():
                rows.append({
                    "from_id": giver,
                    "to_id": recv,
                    "period": period,
                    "amount": round(float(d["amount"]), 1),
                    "acts": int(d["acts"]),
                    "aid_type": d["aid_type"],
                    "cross_block": int(block_of[giver] != block_of[recv]),
                })

    edges = pd.DataFrame(rows)

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)
    by_p = edges.period.value_counts().to_dict()
    print(f"mutualaid-quake: {len(nodes)} nodes "
          f"({(nodes.kind=='resident').sum()} residents + {(nodes.kind=='org').sum()} orgs), "
          f"{len(edges)} edges "
          f"(before={by_p.get('before',0)}, during={by_p.get('during',0)}, "
          f"after={by_p.get('after',0)}); aid Gini(during)="
          f"{_gini(edges[edges.period=='during'].groupby('to_id').amount.sum().values):.2f}.")


if __name__ == "__main__":
    main()
