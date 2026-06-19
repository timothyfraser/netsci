"""Load the `amazon-last-mile` project network (Python).

Reads the two CSVs in this folder and builds a directed, weighted python-igraph
object: package flow through hubs -> stations -> zones over one week. Run it
straight (``python load.py``) for a quick summary, or import ``load_amazon()``
into your own script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per hub / station / zone."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per origin x destination x day."""
    return pd.read_csv(HERE / "edges.csv")


def load_amazon(nodes: pd.DataFrame | None = None,
                edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the directed, weighted graph (edge weight = ``packages``).

    The data is temporal (a ``day`` column), so an edge between the same pair of
    nodes appears up to 7 times as parallel edges. Filter to one ``day`` first if
    you want a simple graph.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=True, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["packages"]
    return g


if __name__ == "__main__":
    print("\n📦 amazon-last-mile (Python)")
    print("   Hubs -> stations -> zones; weighted by packages, daily for one week.\n")

    nodes = load_nodes()
    edges = load_edges()
    g = load_amazon(nodes, edges)

    kinds = nodes["kind"].value_counts()
    print(f"✅ Loaded {len(nodes)} nodes "
          f"({kinds.get('hub',0)} hubs, {kinds.get('station',0)} stations, "
          f"{kinds.get('zone',0)} zones) and {len(edges)} edges.")
    print(f"🔗 Directed: {g.is_directed()} | total packages moved: "
          f"{edges['packages'].sum():,}")
    print("🎉 Graph ready. Object `g` is a directed, weighted igraph.")
