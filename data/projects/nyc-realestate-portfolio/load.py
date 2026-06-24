"""Load the `nyc-realestate-portfolio` project network (Python).

Reads the CSVs in this folder and builds an undirected, weighted property
portfolio network with python-igraph: nodes are NYC properties, an edge links two
properties that share at least one common equity investor (co-ownership /
cross-collateral). Edge weight is ``co_investment_usd``. Run it straight
(``python load.py``) for a summary, or import ``load_portfolio()``. Shares
property ``node_id``s with the companion ``nyc-realestate-capital`` dataset.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per property."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per shared-financing tie."""
    return pd.read_csv(HERE / "edges.csv")


def load_portfolio(nodes: pd.DataFrame | None = None,
                   edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the undirected, weighted portfolio graph (weight = ``co_investment_usd``)."""
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=False, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["co_investment_usd"]
    return g


if __name__ == "__main__":
    print("\n🏢 nyc-realestate-portfolio (Python)")
    print("   Properties linked by shared equity financing; weight = co_investment_usd.\n")

    nodes = load_nodes(); edges = load_edges(); g = load_portfolio(nodes, edges)
    comps = g.connected_components()
    deg = g.degree()
    print(f"✅ Loaded {len(nodes)} properties and {len(edges)} shared-financing edges.")
    print(f"🔗 Components: {len(comps)} | mean degree: {sum(deg)/len(deg):.1f} | "
          f"densest cluster hints at concentration risk.")
    print("🎉 Graph ready. Undirected; weight = co_investment_usd; group by borough / property_type.")
