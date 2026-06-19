"""Generate the `financial-contagion` project network (deterministic).

A directed interbank / financial-exposure network across three periods of a
crisis:
  - period = "before"   (calm; dense interlinked exposures)
  - period = "during"   (the crash; one firm fails and a cascade unwinds)
  - period = "after"    (recovery; sparser, flight-to-quality star structure)

Nodes are financial firms; an edge is a directed exposure (a loan / credit line)
from a creditor to a debtor, weighted by exposure dollars, one row per
(creditor, debtor, period).

Node attributes: type (bank / hedge_fund / insurer / ccp), assets (size),
leverage, region, label.

Design parameters (the only record of the planted structure):
  - FAIL_NODE: one over-leveraged, mid-size firm fails DURING. Its creditor
    edges vanish, and several of THOSE creditors then drop edges too (a
    measurable cascade radius around it).
  - CCP_HUB: a central counterparty has modest degree but the highest
    betweenness (a hidden systemic hub intermediating most flows).
  - HERD: a large cluster of firms all lend to the same handful of debtors
    (correlated / overlapping common exposure).
  - FRONT_RUNNERS: a few firms sharply cut outgoing exposure before->during
    (they saw it coming) while everyone else stays exposed until the crash.
  - FLIGHT: surviving firms rewire toward low-leverage bank/ccp nodes AFTER;
    the network is sparser and more star-like.

Run:
    python data/projects/financial-contagion/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

N_FIRMS = 220
PERIODS = ["before", "during", "after"]
REGIONS = ["NorthAm", "Europe", "Asia", "LatAm"]
TYPES = ["bank", "hedge_fund", "insurer", "ccp"]

# --- planted parameters -----------------------------------------------------
N_CCP = 4                       # central counterparties (systemic intermediaries)
N_HERD = 55                     # firms in the common-exposure herd
N_HERD_TARGETS = 5              # the handful of debtors the herd all lends to
N_FRONT_RUNNERS = 8             # firms that cut exposure pre-crash
FRONT_RUNNER_CUT = 0.20         # they keep only ~20% of out-exposure during
FAIL_LEVERAGE = 38.0            # leverage of the firm that fails (top-decile)
CASCADE_DROP = 0.55            # share of failed-firm creditors who then cut too
DENSIFY = {"before": 1.0, "during": 0.72, "after": 0.40}  # tie-rate by period


def _gini(x: np.ndarray) -> float:
    x = np.sort(np.asarray(x, dtype=float))
    n = len(x)
    if n == 0 or x.sum() == 0:
        return 0.0
    idx = np.arange(1, n + 1)
    return float((2 * (idx * x).sum() - (n + 1) * x.sum()) / (n * x.sum()))


def main() -> None:
    rng = np.random.default_rng(SEED)

    # ----- firms -----------------------------------------------------------
    ftype = rng.choice(["bank", "hedge_fund", "insurer"],
                       size=N_FIRMS, p=[0.5, 0.32, 0.18])
    # designate the central counterparties
    ccp_idx = rng.choice(N_FIRMS, N_CCP, replace=False)
    ftype = ftype.astype(object)
    for c in ccp_idx:
        ftype[c] = "ccp"

    # assets (size, $B), log-normalish; banks & ccp larger on average
    base_assets = rng.lognormal(mean=2.4, sigma=0.9, size=N_FIRMS)
    for i in range(N_FIRMS):
        if ftype[i] == "bank":
            base_assets[i] *= 1.8
        elif ftype[i] == "ccp":
            base_assets[i] *= 2.4
        elif ftype[i] == "hedge_fund":
            base_assets[i] *= 0.7
    assets = np.clip(base_assets, 0.5, None)

    # leverage: hedge funds high, banks moderate, insurers/ccp low; noisy.
    lev = np.empty(N_FIRMS)
    for i in range(N_FIRMS):
        if ftype[i] == "hedge_fund":
            lev[i] = np.clip(rng.normal(14, 6), 3, 45)
        elif ftype[i] == "bank":
            lev[i] = np.clip(rng.normal(9, 3), 2, 22)
        elif ftype[i] == "insurer":
            lev[i] = np.clip(rng.normal(6, 2), 1.5, 14)
        else:  # ccp
            lev[i] = np.clip(rng.normal(3, 1), 1.2, 6)

    region = rng.choice(REGIONS, N_FIRMS)

    firms = pd.DataFrame({
        "node_id": [f"F{i:03d}" for i in range(1, N_FIRMS + 1)],
        "type": ftype,
        "assets": assets.round(2),
        "leverage": lev.round(2),
        "region": region,
        "label": [f"{('CCP' if t == 'ccp' else str(t).replace('_', ' ').title())} {i:03d}"
                  for i, t in zip(range(1, N_FIRMS + 1), ftype)],
    })
    node_ids = list(firms.node_id)
    idx_of = {n: i for i, n in enumerate(node_ids)}
    ccp_ids = [node_ids[c] for c in ccp_idx]

    # ----- choose the failing firm: mid-size, top-decile leverage ----------
    mid_mask = (assets > np.quantile(assets, 0.35)) & (assets < np.quantile(assets, 0.65))
    cand = np.where(mid_mask & (ftype == "hedge_fund"))[0]
    if len(cand) == 0:
        cand = np.where(mid_mask)[0]
    fail_i = int(cand[np.argmax(lev[cand])])
    # force its leverage to the planted top-decile value
    lev[fail_i] = FAIL_LEVERAGE
    firms.loc[fail_i, "leverage"] = FAIL_LEVERAGE
    fail_id = node_ids[fail_i]

    # ----- structural sets -------------------------------------------------
    # herd: a cluster of firms all lending to the same few debtors
    herd_ids = list(rng.choice([n for n in node_ids if n != fail_id],
                               N_HERD, replace=False))
    herd_targets = list(rng.choice([n for n in node_ids
                                    if n not in herd_ids and n != fail_id],
                                   N_HERD_TARGETS, replace=False))
    # front-runners: firms that cut outgoing exposure pre-crash
    front_runners = set(rng.choice([n for n in node_ids if n != fail_id],
                                   N_FRONT_RUNNERS, replace=False))
    # low-leverage "quality" nodes (flight destinations after the crash)
    quality_ids = [n for n in node_ids
                   if firms.at[idx_of[n], "type"] in ("bank", "ccp")
                   and firms.at[idx_of[n], "leverage"] <= 7]

    # ----- systemic hub design --------------------------------------------
    # One CCP is the SYSTEMIC bridge: firms split into two camps, and almost the
    # only path between them runs through this CCP. That gives it the highest
    # betweenness while its degree stays modest (a hidden systemic hub).
    systemic_ccp = ccp_ids[0]
    sys_i = idx_of[systemic_ccp]
    camp = rng.integers(0, 2, N_FIRMS)        # camp 0 / camp 1
    camp[sys_i] = -1                          # the hub belongs to neither camp
    camp_of = {n: int(camp[idx_of[n]]) for n in node_ids}
    # a modest set of "gateway" firms in each camp connect to the systemic CCP
    camp0 = [n for n in node_ids if camp_of[n] == 0]
    camp1 = [n for n in node_ids if camp_of[n] == 1]
    gateways0 = list(rng.choice(camp0, min(9, len(camp0)), replace=False))
    gateways1 = list(rng.choice(camp1, min(9, len(camp1)), replace=False))
    gateways = set(gateways0 + gateways1)

    # base "connectivity" per node ~ assets (bigger firms have more links)
    connect = assets / assets.mean()

    def exposure_amt(creditor, debtor):
        a = assets[idx_of[creditor]]
        return float(rng.gamma(2.0, 1.0) * (1.0 + 0.15 * a))

    rows = []

    def add_edge(seen, creditor, debtor, period, scale=1.0):
        if creditor == debtor:
            return
        # the failed firm has no exposures (in OR out) once it fails
        if period in ("during", "after") and debtor == fail_id:
            return
        amt = exposure_amt(creditor, debtor) * scale
        key = debtor
        if key in seen:
            seen[key] += amt
        else:
            seen[key] = amt

    # who lent TO the failed firm "before" (its creditors) -> needed for cascade
    fail_creditors_before = []

    for period in PERIODS:
        rate = DENSIFY[period]
        for creditor in node_ids:
            # the failed firm has NO outgoing/incoming edges during & after
            if period in ("during", "after") and creditor == fail_id:
                continue

            base_deg = max(0.4, 2.6 * connect[idx_of[creditor]] * rate)

            # front-runners slash their out-exposure during the crash
            if period == "during" and creditor in front_runners:
                base_deg *= FRONT_RUNNER_CUT

            n_ties = rng.poisson(base_deg)
            seen = {}

            # ---- systemic CCP as the bridge between the two camps -----------
            # gateways route exposure THROUGH the systemic CCP; the CCP re-lends
            # into the OTHER camp. Few links, but it sits on most cross-camp
            # paths -> highest betweenness, modest degree.
            if period in ("before", "during"):
                if creditor in gateways:
                    add_edge(seen, creditor, systemic_ccp, period)
                if creditor == systemic_ccp:
                    # lend a modest amount into both camps' gateways
                    for t in (gateways0 + gateways1):
                        if rng.random() < 0.55:
                            add_edge(seen, creditor, t, period)

            # other (non-systemic) CCPs are ordinary clearing nodes
            if creditor in ccp_ids and creditor != systemic_ccp:
                targets = rng.choice([n for n in node_ids if n != creditor],
                                     size=min(6, n_ties + 3), replace=False)
                for t in targets:
                    add_edge(seen, creditor, t, period)

            # ---- herd: herd members lend to the shared targets --------------
            if creditor in herd_ids and period in ("before", "during"):
                for t in herd_targets:
                    if rng.random() < 0.75:
                        add_edge(seen, creditor, t, period, scale=1.3)

            # ---- ordinary exposures (mostly within one's own camp) ----------
            my_camp = camp_of[creditor]
            same_camp = camp0 if my_camp == 0 else (camp1 if my_camp == 1
                                                    else node_ids)
            for _ in range(int(n_ties)):
                if period == "after":
                    # FLIGHT TO QUALITY: route toward low-leverage bank/ccp
                    if quality_ids and rng.random() < 0.7:
                        debtor = str(rng.choice(quality_ids))
                    else:
                        debtor = str(rng.choice(node_ids))
                else:
                    # before/during: lend mostly within camp (keeps the systemic
                    # CCP as the scarce cross-camp bridge), weighted by size
                    pool = same_camp if rng.random() < 0.9 else node_ids
                    w = np.array([connect[idx_of[n]] for n in pool], dtype=float)
                    debtor = str(rng.choice(pool, p=w / w.sum()))
                add_edge(seen, creditor, debtor, period)

            # before: some firms lend to the failing firm (its creditors)
            if period == "before" and creditor != fail_id and rng.random() < 0.18:
                add_edge(seen, creditor, fail_id, period, scale=1.4)
                fail_creditors_before.append(creditor)

            for debtor, amt in seen.items():
                rows.append({
                    "from_id": creditor,       # creditor (lender)
                    "to_id": debtor,           # debtor (borrower)
                    "period": period,
                    "exposure": round(amt, 2),
                })

    # ---- cascade: a share of the failed firm's creditors DROP edges during -
    # We model this by removing a fraction of those creditors' DURING out-edges.
    edges = pd.DataFrame(rows)
    fail_creditors_before = list(dict.fromkeys(fail_creditors_before))
    cascade_hit = set(rng.choice(
        fail_creditors_before,
        max(1, int(len(fail_creditors_before) * CASCADE_DROP)),
        replace=False)) if fail_creditors_before else set()

    keep = np.ones(len(edges), dtype=bool)
    for i, r in edges.iterrows():
        if r["period"] == "during" and r["from_id"] in cascade_hit:
            # each cascade-hit creditor drops ~60% of its during edges
            if rng.random() < 0.6:
                keep[i] = False
    edges = edges[keep].reset_index(drop=True)

    firms.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)
    by_p = edges.period.value_counts().to_dict()
    print(f"financial-contagion: {len(firms)} nodes "
          f"({(firms.type=='bank').sum()} banks, {(firms.type=='hedge_fund').sum()} hedge funds, "
          f"{(firms.type=='insurer').sum()} insurers, {(firms.type=='ccp').sum()} ccps), "
          f"{len(edges)} edges "
          f"(before={by_p.get('before',0)}, during={by_p.get('during',0)}, "
          f"after={by_p.get('after',0)}); exposure Gini(before)="
          f"{_gini(edges[edges.period=='before'].groupby('to_id').exposure.sum().values):.2f}.")


if __name__ == "__main__":
    main()
