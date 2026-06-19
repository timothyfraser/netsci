"""Load the `transit-multimodal` project network (Python).

Reads the CSVs in this folder and builds an undirected, weighted, multimodal
python-igraph object: neighborhoods are nodes; edges are transit links in two
modes (``metro`` and ``bus``). Because the same neighborhood pair can carry both
a metro and a bus link, the graph is a multiplex with parallel edges. The edge
weight is ``capacity`` (riders/hr). Run it straight (``python load.py``) for a
quick summary, or import ``load_transit()`` / ``load_lines()`` into your script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per neighborhood."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per transit link (metro or bus)."""
    return pd.read_csv(HERE / "edges.csv")


def load_lines() -> pd.DataFrame:
    """Line/route lookup table (join onto edges by ``line``)."""
    return pd.read_csv(HERE / "lines.csv")


def load_transit(nodes: pd.DataFrame | None = None,
                 edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the undirected, weighted, multimodal graph (weight = ``capacity``).

    The same neighborhood pair may appear twice (a metro edge AND a bus edge) ->
    parallel edges. The ``mode`` edge attribute distinguishes them. To analyze a
    single mode, filter edges first; to collapse to one link per pair, use
    ``g.simplify(combine_edges={'weight': 'sum'})``.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=False, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["capacity"]
    return g


if __name__ == "__main__":
    print("\n🚇 transit-multimodal (Python)")
    print("   Undirected multimodal transit; neighborhoods linked by metro & bus.\n")

    nodes = load_nodes()
    edges = load_edges()
    g = load_transit(nodes, edges)

    modes = edges["mode"].value_counts()
    print(f"✅ Loaded {len(nodes)} neighborhoods and {len(edges)} edges "
          f"({modes.get('metro', 0)} metro + {modes.get('bus', 0)} bus).")
    print(f"🔗 Directed: {g.is_directed()} | metro-served neighborhoods: "
          f"{int(nodes['has_metro'].sum())} | total seat capacity: "
          f"{edges['capacity'].sum():,} riders/hr")
    print("🎉 Graph ready. Object `g` is an undirected, weighted, multimodal igraph.")
