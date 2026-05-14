"""Generate the tiny + larger toy supply chain networks for case 10.

Two networks are produced:
  - tiny.{nodes,edges}.csv: 6-node hand-toy network mirroring the
    case study lab. Each node has 2 input features.
  - large.{nodes,edges}.csv: 200-node project-scale network with
    planted bottlenecks; same 2 features.

Both are deterministic.

Run:
    python code/10_gnn-by-hand/data/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

def main() -> None:
    rng = np.random.default_rng(SEED)

    # --- tiny --------------------------------------------------------------
    # Six nodes in a small DAG. Node 4 is a bottleneck: many things
    # converge on it. Features = (daily_output, defect_rate) in [0, 1].
    tiny_nodes = pd.DataFrame({
        "node_id":      [0, 1, 2, 3, 4, 5],
        "daily_output": [0.80, 0.60, 0.40, 0.55, 0.70, 0.30],
        "defect_rate":  [0.10, 0.20, 0.30, 0.15, 0.05, 0.40],
    })
    tiny_edges = pd.DataFrame([
        {"from": 0, "to": 4}, {"from": 1, "to": 4}, {"from": 2, "to": 4},
        {"from": 3, "to": 4}, {"from": 4, "to": 5},
    ])
    tiny_nodes.to_csv(HERE / "tiny_nodes.csv", index=False)
    tiny_edges.to_csv(HERE / "tiny_edges.csv", index=False)
    print("wrote tiny_nodes.csv / tiny_edges.csv (6 nodes)")

    # --- larger ------------------------------------------------------------
    # 200 nodes; planted bottlenecks every 25 nodes.
    n = 200
    large_nodes = pd.DataFrame({
        "node_id":      np.arange(n),
        "daily_output": rng.beta(2, 2, size=n).round(3),
        "defect_rate":  rng.beta(2, 5, size=n).round(3),
    })
    rows = []
    bottlenecks = [25 * i for i in range(1, 8)]
    for src in range(n):
        # connect to nearest bottleneck downstream
        downstream = [b for b in bottlenecks if b > src]
        if downstream:
            tgt = downstream[0]
            rows.append({"from": src, "to": tgt})
    # connect bottlenecks linearly
    for a, b in zip(bottlenecks, bottlenecks[1:]):
        rows.append({"from": a, "to": b})
    large_edges = pd.DataFrame(rows)
    large_nodes.to_csv(HERE / "large_nodes.csv", index=False)
    large_edges.to_csv(HERE / "large_edges.csv", index=False)
    print(f"wrote large_nodes.csv ({n} nodes) / large_edges.csv ({len(large_edges)} edges)")


if __name__ == "__main__":
    main()
