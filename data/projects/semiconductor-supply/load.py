"""Load the `semiconductor-supply` project network (Python).

Reads the two CSVs in this folder and builds a directed, weighted python-igraph
object: a multi-tier semiconductor supply chain (materials -> foundries ->
packaging -> designers -> products). Run it straight (``python load.py``) for a
quick summary, or import ``load_semi()`` into your own script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per supplier / product."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per supply relationship."""
    return pd.read_csv(HERE / "edges.csv")


def load_semi(nodes: pd.DataFrame | None = None,
              edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the directed, weighted graph (edge weight = ``annual_volume``).

    Edges flow from the upstream node to the downstream node. Use
    ``g.subcomponent(v, mode="out")`` to trace everything downstream of a node,
    or delete a vertex to test how much end-product output it carries.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=True, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["annual_volume"]
    return g


if __name__ == "__main__":
    print("\n🔌 semiconductor-supply (Python)")
    print("   Materials -> foundries -> packaging -> designers -> products; "
          "weighted by annual volume.\n")

    nodes = load_nodes()
    edges = load_edges()
    g = load_semi(nodes, edges)

    kinds = nodes["kind"].value_counts()
    print(f"✅ Loaded {len(nodes)} nodes "
          f"({kinds.get('material',0)} material, {kinds.get('foundry',0)} foundry, "
          f"{kinds.get('packaging',0)} packaging, {kinds.get('designer',0)} designer, "
          f"{kinds.get('product',0)} product) and {len(edges)} edges.")
    print(f"🔗 Directed: {g.is_directed()} | total annual volume: "
          f"{edges['annual_volume'].sum():,} | total value: "
          f"${round(edges['value_musd'].sum()):,} M")
    print("🎉 Graph ready. Object `g` is a directed, weighted igraph "
          "(weight = annual_volume).")
