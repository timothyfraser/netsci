"""Generate the synthetic data for case 07 (permutation testing).

We want a network where:
  - nodes have a categorical attribute (`demo` in {A, B})
  - edges have a planted homophily: more A-A and B-B than A-B
  - nodes also have a neighborhood, and demographics correlate with
    neighborhood (so a naive "shuffle labels everywhere" null model
    is too permissive — a *block* permutation that shuffles labels
    only within neighborhood is the right null)

400 nodes, 12 neighborhoods, ~25,000 weighted edges.

Run:
    python code/07_permutation/data/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

def main() -> None:
    rng = np.random.default_rng(SEED)

    n_nodes = 400
    n_nbhds = 12

    # neighborhood for each node
    nbhd = rng.integers(0, n_nbhds, size=n_nodes)
    # demographic prob varies by neighborhood (some are mostly A, some mostly B)
    nbhd_p_A = rng.uniform(0.1, 0.9, size=n_nbhds)
    p_A = nbhd_p_A[nbhd]
    demo = np.where(rng.random(n_nodes) < p_A, "A", "B")

    nodes = pd.DataFrame({
        "node_id":      [f"V{i:04d}" for i in range(n_nodes)],
        "neighborhood": [f"N{n:02d}" for n in nbhd],
        "demo":         demo,
    })

    # build edges: NO planted edge-level homophily on `demo`. Instead,
    # we plant strong same-NEIGHBORHOOD bias. Because `demo` correlates
    # with neighborhood, the network will LOOK demo-homophilous when
    # you ignore neighborhood — but if you condition on neighborhood
    # (block permutation), the extra homophily is roughly zero.
    #
    # This is the canonical "wrong null model gives wrong answer"
    # demonstration the case study is built around.
    n_edges = 25_000

    start_idx = rng.integers(0, n_nodes, size=n_edges)
    same_nbhd = rng.random(n_edges) < 0.65  # 65% within-neighborhood
    end_idx = np.empty(n_edges, dtype=np.int64)
    for i in range(n_edges):
        if same_nbhd[i]:
            pool = np.flatnonzero(nbhd == nbhd[start_idx[i]])
        else:
            pool = np.flatnonzero(nbhd != nbhd[start_idx[i]])
        pool = pool[pool != start_idx[i]]
        end_idx[i] = rng.choice(pool)

    edges = pd.DataFrame({
        "from":   nodes["node_id"].to_numpy()[start_idx],
        "to":     nodes["node_id"].to_numpy()[end_idx],
        "weight": rng.integers(1, 8, size=n_edges),
    })
    # aggregate duplicate edges (same start, same end)
    edges = (edges.groupby(["from", "to"], as_index=False)["weight"].sum()
                  .sort_values(["from", "to"]).reset_index(drop=True))

    nodes = nodes.sort_values("node_id").reset_index(drop=True)

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)
    print(f"wrote {HERE / 'nodes.csv'} ({len(nodes)} nodes)")
    print(f"wrote {HERE / 'edges.csv'} ({len(edges)} unique edges)")


if __name__ == "__main__":
    main()
