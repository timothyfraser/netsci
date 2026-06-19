"""Load the `satellite-constellation` project network (Python).

Reads the two CSVs in this folder and builds an undirected, weighted
python-igraph object: a one-instant snapshot of three operators' LEO satellite
broadband networks (satellites + ground stations, joined by ISL and feeder
links). Run it straight (``python load.py``) for a quick summary, or import
``load_constellation()`` into your own script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per satellite / ground station."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per link."""
    return pd.read_csv(HERE / "edges.csv")


def load_constellation(nodes: pd.DataFrame | None = None,
                       edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the undirected, weighted constellation graph.

    Edges are weighted by link ``capacity_gbps``. The graph is a single frozen
    snapshot of all orbits at one instant (no time dimension).
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=False, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["capacity_gbps"]
    return g


if __name__ == "__main__":
    print("\n🛰️  satellite-constellation (Python)")
    print("   Undirected LEO network; links weighted by capacity (Gbps).\n")

    nodes = load_nodes()
    edges = load_edges()
    g = load_constellation(nodes, edges)

    kinds = nodes["kind"].value_counts()
    print(f"✅ Loaded {len(nodes)} nodes "
          f"({kinds.get('satellite',0)} satellites, "
          f"{kinds.get('ground_station',0)} ground stations) and {len(edges)} links.")
    print(f"🔗 Directed: {g.is_directed()} | total link capacity: "
          f"{round(edges['capacity_gbps'].sum()):,} Gbps")
    print("🎉 Graph ready. Object `g` is an undirected, weighted igraph.")
