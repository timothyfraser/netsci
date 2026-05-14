"""Generate a synthetic engineered-system DSM for case 06.

A Design Structure Matrix (DSM) is just an adjacency matrix where
component i depends on component j. We plant K dense modules so the
clustering algorithm has something to recover.

  - 200 components
  - 8 modules of 25 components each
  - intra-module edge probability: 0.40
  - inter-module edge probability: 0.03 (the "residual marks")

Outputs:
  - dsm.csv: long-format edge list (from, to)
  - nodes.csv: node_id + true module label (for verification)

Run:
    python code/06_dsm-clustering/data/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

def main() -> None:
    rng = np.random.default_rng(SEED)

    n = 200
    n_modules = 8
    per_module = n // n_modules
    p_intra = 0.40
    p_inter = 0.03

    # assign each component to a module
    module = np.repeat(np.arange(n_modules), per_module)
    rng.shuffle(module)

    nodes = pd.DataFrame({
        "node_id":   [f"C{i:03d}" for i in range(n)],
        "true_module": module,
    })

    # build directed edges (DSM dependencies)
    rows = []
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            p = p_intra if module[i] == module[j] else p_inter
            if rng.random() < p:
                rows.append({
                    "from": f"C{i:03d}",
                    "to":   f"C{j:03d}",
                })
    edges = pd.DataFrame(rows).sort_values(["from", "to"]).reset_index(drop=True)

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)
    print(f"wrote {HERE / 'nodes.csv'} ({len(nodes)} nodes)")
    print(f"wrote {HERE / 'edges.csv'} ({len(edges)} edges)")


if __name__ == "__main__":
    main()
