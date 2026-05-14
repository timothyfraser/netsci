"""Generate the synthetic bipartite supplier <-> component network.

We want a deterministic small-but-not-tiny bipartite network so the
Build-a-Network case study has signal: ~80 suppliers, ~120 components,
~600 edges, with planted "shared supplier" patterns so the one-mode
projection (supplier x supplier via shared component) has interesting
structure.

Run once to regenerate the CSVs:

    python code/01_build-a-network/data/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

def main() -> None:
    rng = np.random.default_rng(SEED)

    n_suppliers  = 80
    n_components = 120

    # Suppliers belong to one of 4 regions; that biases which components
    # they ship (some components are regional specialties).
    suppliers = pd.DataFrame({
        "node_id": [f"S{i:03d}" for i in range(n_suppliers)],
        "kind":    "supplier",
        "region":  rng.choice(["NE", "SE", "MW", "W"], size=n_suppliers,
                              p=[0.35, 0.25, 0.25, 0.15]),
        "tier":    rng.choice([1, 2, 3], size=n_suppliers, p=[0.30, 0.45, 0.25]),
        "capacity_units": rng.integers(200, 2000, size=n_suppliers),
    })

    components = pd.DataFrame({
        "node_id": [f"C{i:03d}" for i in range(n_components)],
        "kind":    "component",
        "region":  rng.choice(["NE", "SE", "MW", "W", "ANY"],
                              size=n_components,
                              p=[0.15, 0.15, 0.15, 0.10, 0.45]),
        "tier":    pd.NA,
        "capacity_units": pd.NA,
    })

    nodes = pd.concat([suppliers, components], ignore_index=True)

    # Edges: for each supplier, pick K components to ship, biased toward
    # the supplier's region (or "ANY" region, which any supplier might
    # touch). This gives a planted block structure.
    edges_rows = []
    for _, sup in suppliers.iterrows():
        # how many components this supplier touches
        k = max(1, int(rng.normal(loc=7.5, scale=2.5)))
        # eligible components: same region OR "ANY"
        eligible = components.loc[
            (components["region"] == sup["region"]) |
            (components["region"] == "ANY"),
            "node_id"
        ].to_numpy()
        if len(eligible) < k:
            k = len(eligible)
        picks = rng.choice(eligible, size=k, replace=False)
        for c in picks:
            edges_rows.append({
                "from_id":      sup["node_id"],
                "to_id":        c,
                "volume_units": int(rng.integers(50, 400)),
            })

    edges = pd.DataFrame(edges_rows).sort_values(
        ["from_id", "to_id"]).reset_index(drop=True)

    nodes = nodes.sort_values("node_id").reset_index(drop=True)

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)

    print(f"wrote {HERE / 'nodes.csv'} ({len(nodes)} nodes)")
    print(f"wrote {HERE / 'edges.csv'} ({len(edges)} edges)")


if __name__ == "__main__":
    main()
