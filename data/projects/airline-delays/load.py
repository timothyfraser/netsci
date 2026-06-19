"""Load the `airline-delays` project network (Python).

Reads the two CSVs in this folder and builds a directed, weighted python-igraph
object: one day of scheduled flights between airports, sliced into four time
blocks. Run it straight (``python load.py``) for a quick summary, or import
``load_airline()`` into your own script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per airport."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per origin x destination x block."""
    return pd.read_csv(HERE / "edges.csv")


def load_airline(nodes: pd.DataFrame | None = None,
                 edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the directed, weighted graph (edge weight = ``number_of_flights``).

    The data is temporal (a ``block`` column), so an edge between the same pair of
    airports appears up to 4 times as parallel edges. Filter to one ``block``
    first if you want a simple graph.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=True, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["number_of_flights"]
    return g


if __name__ == "__main__":
    print("\n✈️  airline-delays (Python)")
    print("   Directed flights between airports, weighted by flights, in 4 time blocks.\n")

    nodes = load_nodes()
    edges = load_edges()
    g = load_airline(nodes, edges)

    n_routes = edges[["from_id", "to_id"]].drop_duplicates().shape[0]
    print(f"✅ Loaded {len(nodes)} airports ({int(nodes['hub'].sum())} hubs) "
          f"and {len(edges)} edges ({n_routes} routes x 4 blocks).")
    print(f"🔗 Directed: {g.is_directed()} | total flights: "
          f"{edges['number_of_flights'].sum():,}")
    print("🎉 Graph ready. Object `g` is a directed, weighted igraph.")
