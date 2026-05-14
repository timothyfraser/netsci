"""Generate the synthetic supplier-disruption panel for case 11.

We build a directed supply network of N suppliers and simulate T
weeks of binary disruption labels per supplier. Each supplier has:

  - static features: tier, region (one-hot), capacity, geographic
    risk score
  - dynamic feature: last-4-weeks disruption rate (a lag feature)
  - network position: who they supply to, who supplies them

Disruption is generated so that BOTH static features AND neighbor
disruptions predict it. This is the signal that lets a GNN
embedding outperform plain features.

Outputs:
  - suppliers.csv (500 rows, static traits)
  - edges.csv    (~1200 directed dependency edges)
  - panel.csv    (500 * 52 = 26000 rows, supplier x week x label)

Run:
    python code/11_gnn-xgboost/data/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

def main() -> None:
    rng = np.random.default_rng(SEED)
    n_suppliers = 500
    n_weeks     = 52

    # --- static features ----------------------------------------------------
    region_levels = np.array(["NE", "SE", "MW", "W"])
    suppliers = pd.DataFrame({
        "supplier_id":    [f"S{i:04d}" for i in range(n_suppliers)],
        "tier":           rng.integers(1, 4, size=n_suppliers),
        "region":         rng.choice(region_levels, size=n_suppliers),
        "capacity":       rng.integers(200, 2000, size=n_suppliers),
        "geo_risk":       rng.beta(2, 5, size=n_suppliers).round(3),
    })

    # --- directed dependency edges (who supplies whom) ----------------------
    rows = []
    for i in range(n_suppliers):
        # each supplier has 1-4 outgoing dependencies
        k = int(rng.integers(1, 5))
        targets = rng.choice(np.delete(np.arange(n_suppliers), i),
                             size=min(k, n_suppliers - 1), replace=False)
        for t in targets:
            rows.append({"from": suppliers["supplier_id"][i],
                         "to":   suppliers["supplier_id"][t]})
    edges = pd.DataFrame(rows).sort_values(["from", "to"]).reset_index(drop=True)

    # --- per-supplier baseline disruption probability ------------------------
    # combines static features (geo_risk + capacity inverse + tier)
    cap_z = (suppliers["capacity"] - suppliers["capacity"].mean()) / suppliers["capacity"].std()
    base_logit = (
        -2.8
        + 1.8 * suppliers["geo_risk"]
        - 0.3 * cap_z
        + 0.3 * (suppliers["tier"] - 1)
        + 0.4 * (suppliers["region"] == "SE").astype(float)
    )

    # --- simulate T weeks of disruption labels ------------------------------
    # at week t, P(disrupt) = sigmoid(base_logit + neighbor_effect)
    # where neighbor_effect = mean of t-1 disruption of in-neighbors
    # (so disruptions cluster temporally and propagate upstream)
    in_neighbors = {s: [] for s in suppliers["supplier_id"]}
    for _, e in edges.iterrows():
        in_neighbors[e["to"]].append(e["from"])

    sup_idx = {s: i for i, s in enumerate(suppliers["supplier_id"])}
    Y = np.zeros((n_suppliers, n_weeks), dtype=np.int8)
    # week 0: pure static baseline
    p0 = 1 / (1 + np.exp(-base_logit.to_numpy()))
    Y[:, 0] = (rng.random(n_suppliers) < p0).astype(np.int8)
    for t in range(1, n_weeks):
        prev = Y[:, t - 1].astype(float)
        neigh_eff = np.zeros(n_suppliers)
        for s, ins in in_neighbors.items():
            if ins:
                neigh_eff[sup_idx[s]] = np.mean([prev[sup_idx[x]] for x in ins])
        logit = base_logit.to_numpy() + 1.5 * neigh_eff
        p = 1 / (1 + np.exp(-logit))
        Y[:, t] = (rng.random(n_suppliers) < p).astype(np.int8)

    # --- build the panel ----------------------------------------------------
    panel_rows = []
    for i, s in enumerate(suppliers["supplier_id"]):
        for t in range(n_weeks):
            panel_rows.append({
                "supplier_id": s,
                "week":        t,
                "disrupted":   int(Y[i, t]),
            })
    panel = pd.DataFrame(panel_rows)

    # --- write --------------------------------------------------------------
    suppliers.sort_values("supplier_id").to_csv(HERE / "suppliers.csv",
                                                    index=False)
    edges.to_csv(HERE / "edges.csv", index=False)
    panel.to_csv(HERE / "panel.csv", index=False)

    print(f"wrote {HERE / 'suppliers.csv'} ({len(suppliers)} suppliers)")
    print(f"wrote {HERE / 'edges.csv'}     ({len(edges):,} edges)")
    print(f"wrote {HERE / 'panel.csv'}     ({len(panel):,} rows = "
          f"{n_suppliers} x {n_weeks})")
    print(f"  overall disruption rate: {panel['disrupted'].mean():.3f}")


if __name__ == "__main__":
    main()
