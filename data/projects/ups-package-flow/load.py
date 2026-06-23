"""Load the `ups-package-flow` project network (Python).

Reads the two CSVs in this folder and builds a directed, weighted python-igraph
multigraph where the **unit of analysis is the individual package**: one edge per
parcel, from its origin plant to its destination plant. Run it straight
(``python load.py``) for a quick summary, or import ``load_packages()`` into your
own script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per plant (gateway / hub / center)."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per package."""
    return pd.read_csv(HERE / "edges.csv")


def load_packages(nodes: pd.DataFrame | None = None,
                  edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the directed, weighted multigraph (one edge per package).

    Edge weight is ``weight_kg``. Each package edge also carries
    ``service_level``, ``distance_km``, ``transit_hours``, ``promised_hours``,
    ``on_time``, and ``damaged``. Aggregate the edges by (from, to) to recover a
    lane-level view, or summarise ``on_time`` by destination plant to compare
    service across facilities.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=True, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["weight_kg"]
    return g


if __name__ == "__main__":
    print("\n📦 ups-package-flow (Python)")
    print("   One edge per package: origin plant -> destination plant; "
          "weight = weight_kg.\n")

    nodes = load_nodes()
    edges = load_edges()
    g = load_packages(nodes, edges)

    kinds = nodes["kind"].value_counts()
    print(f"✅ Loaded {len(nodes)} plants "
          f"({kinds.get('gateway',0)} gateway, {kinds.get('hub',0)} hub, "
          f"{kinds.get('center',0)} center) and {len(edges)} packages.")
    print(f"🔗 Directed: {g.is_directed()} | on-time: "
          f"{100 * edges['on_time'].mean():.1f}% | damaged: "
          f"{100 * edges['damaged'].mean():.1f}% | mean transit: "
          f"{edges['transit_hours'].mean():.1f} h")
    print("🎉 Graph ready. Object `g` is a directed, weighted multigraph "
          "(weight = weight_kg).")
