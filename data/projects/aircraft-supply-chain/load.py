"""Load the `aircraft-supply-chain` project network (Python).

Reads the two CSVs in this folder and builds a directed, weighted python-igraph
object: a multi-tier commercial-aircraft supply chain (materials -> components ->
systems -> integrators -> programs). Run it straight (``python load.py``) for a
quick summary, or import ``load_aircraft()`` into your own script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per supplier / system / program."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per supply relationship."""
    return pd.read_csv(HERE / "edges.csv")


def load_aircraft(nodes: pd.DataFrame | None = None,
                  edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the directed, weighted graph (edge weight = ``units_per_year``).

    Edges flow from the upstream node to the downstream node. Use
    ``g.subcomponent(v, mode="out")`` to trace everything downstream of a node,
    or delete a vertex to test how much end-program output it carries.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=True, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["units_per_year"]
    return g


if __name__ == "__main__":
    print("\n✈️  aircraft-supply-chain (Python)")
    print("   Materials -> components -> systems -> integrators -> programs; "
          "weighted by units per year.\n")

    nodes = load_nodes()
    edges = load_edges()
    g = load_aircraft(nodes, edges)

    kinds = nodes["kind"].value_counts()
    print(f"✅ Loaded {len(nodes)} nodes "
          f"({kinds.get('material',0)} material, {kinds.get('component',0)} component, "
          f"{kinds.get('system',0)} system, {kinds.get('integrator',0)} integrator, "
          f"{kinds.get('program',0)} program) and {len(edges)} edges.")
    print(f"🔗 Directed: {g.is_directed()} | total units/year: "
          f"{edges['units_per_year'].sum():,} | total value: "
          f"${round(edges['value_musd'].sum()):,} M")
    print("🎉 Graph ready. Object `g` is a directed, weighted igraph "
          "(weight = units_per_year).")
