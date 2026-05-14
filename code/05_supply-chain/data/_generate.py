"""Generate the synthetic 3-tier supply chain for case 05.

Tiers:
  - 150 suppliers (Tier 1)
  - 30 distribution centers (Tier 2)
  - 400 retailers (Tier 3)
  -> 580 nodes total, ~3000 directed weighted edges

Edge weight = capacity (units per week). Each retailer needs at least
some weekly supply; we keep the network connected by routing each
retailer through at least one DC and each DC through at least one
supplier.

Run:
    python code/05_supply-chain/data/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

def main() -> None:
    rng = np.random.default_rng(SEED)

    n_suppliers = 150
    n_dcs       = 30
    n_retailers = 400

    sup_ids = [f"S{i:03d}" for i in range(n_suppliers)]
    dc_ids  = [f"D{i:03d}" for i in range(n_dcs)]
    ret_ids = [f"R{i:03d}" for i in range(n_retailers)]

    nodes = pd.DataFrame({
        "node_id": sup_ids + dc_ids + ret_ids,
        "tier":    ([1] * n_suppliers) + ([2] * n_dcs) + ([3] * n_retailers),
    })

    edges = []

    # S -> D: every DC gets supplied by 2-5 suppliers
    for d in dc_ids:
        n_links = int(rng.integers(2, 6))
        supplier_picks = rng.choice(sup_ids, size=n_links, replace=False)
        for s in supplier_picks:
            edges.append({"from": s, "to": d,
                          "capacity": int(rng.integers(200, 1500))})

    # D -> R: every retailer gets supplied by 1-3 DCs
    for r in ret_ids:
        n_links = int(rng.integers(1, 4))
        dc_picks = rng.choice(dc_ids, size=n_links, replace=False)
        for d in dc_picks:
            edges.append({"from": d, "to": r,
                          "capacity": int(rng.integers(50, 300))})

    edges_df = pd.DataFrame(edges).sort_values(["from", "to"]).reset_index(drop=True)
    nodes_df = nodes.sort_values("node_id").reset_index(drop=True)

    nodes_df.to_csv(HERE / "nodes.csv", index=False)
    edges_df.to_csv(HERE / "edges.csv", index=False)
    print(f"wrote {HERE / 'nodes.csv'}  ({len(nodes_df)} nodes)")
    print(f"wrote {HERE / 'edges.csv'}  ({len(edges_df)} edges)")


if __name__ == "__main__":
    main()
