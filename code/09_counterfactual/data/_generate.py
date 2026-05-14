"""Generate the synthetic bikeshare network for case 09.

We want:
  - ~180 stations
  - undirected, weighted by typical daily riders (Poisson-distributed
    integers between 5 and 200)
  - small-world topology so APL is meaningful

We use a Watts-Strogatz model (ring lattice + rewiring) then assign
Poisson edge weights. APL of the unweighted graph is ~5; weighted APL
(using inverse weight as cost) gives a meaningful counterfactual
target.

Run:
    python code/09_counterfactual/data/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent
SEED = 42

def main() -> None:
    rng = np.random.default_rng(SEED)

    n = 180
    g = ig.Graph.Watts_Strogatz(dim=1, size=n, nei=4, p=0.08)
    edges = g.get_edgelist()

    rows = []
    for u, v in edges:
        rows.append({
            "from":    f"ST{u:03d}",
            "to":      f"ST{v:03d}",
            "ridership": int(rng.poisson(lam=60)) + 5,
        })
    edges_df = pd.DataFrame(rows).sort_values(["from", "to"]).reset_index(drop=True)

    nodes_df = pd.DataFrame({
        "node_id": [f"ST{i:03d}" for i in range(n)],
        "zone":    rng.choice(["downtown", "midtown", "east", "west"],
                              size=n, p=[0.3, 0.3, 0.2, 0.2]),
    })
    nodes_df = nodes_df.sort_values("node_id").reset_index(drop=True)

    nodes_df.to_csv(HERE / "nodes.csv", index=False)
    edges_df.to_csv(HERE / "edges.csv", index=False)
    print(f"wrote {HERE / 'nodes.csv'} ({len(nodes_df)} stations)")
    print(f"wrote {HERE / 'edges.csv'} ({len(edges_df)} weighted edges)")


if __name__ == "__main__":
    main()
