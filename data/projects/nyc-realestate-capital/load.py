"""Load the `nyc-realestate-capital` project network (Python).

Reads the CSVs in this folder and builds a directed, weighted, temporal funding
network with python-igraph: capital providers (investors + banks) -> NYC
properties. Edges are provider-property-quarter rows carrying capital already
deployed (``invested_usd``) vs pledged-but-not-deployed (``pledged_usd``). Run it
straight (``python load.py``) for a summary, or import ``load_capital()``.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: properties + investors + banks (see the ``kind`` column)."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per provider-property-quarter."""
    return pd.read_csv(HERE / "edges.csv")


def load_capital(nodes: pd.DataFrame | None = None,
                 edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the directed, weighted funding graph (edge weight = ``invested_usd``).

    The graph is bipartite in structure (providers connect only to properties);
    ``vs['type']`` is True for properties, False for capital providers. Edges stay
    in long temporal form: filter ``es['quarter']`` (e.g. "2025Q2") for one slice.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=True, vertices=nodes, use_vids=False)
    g.vs["type"] = [k == "property" for k in g.vs["kind"]]
    g.es["weight"] = g.es["invested_usd"]
    return g


if __name__ == "__main__":
    print("\n🏙️  nyc-realestate-capital (Python)")
    print("   Investors + banks -> NYC properties; quarterly invested vs pledged.\n")

    nodes = load_nodes(); edges = load_edges(); g = load_capital(nodes, edges)
    k = nodes["kind"].value_counts()
    print(f"✅ Loaded {len(nodes)} nodes ({k.get('property',0)} properties + "
          f"{k.get('investor',0)} investors + {k.get('bank',0)} banks) and "
          f"{len(edges)} funding rows.")
    print(f"🔗 Quarters: {edges['quarter'].nunique()} | total invested: "
          f"${edges['invested_usd'].sum()/1e9:,.1f}B | total pledged (open): "
          f"${edges['pledged_usd'].sum()/1e9:,.1f}B")
    print("🎉 Graph ready. Directed providers -> properties; weight = invested_usd; filter es['quarter'].")
