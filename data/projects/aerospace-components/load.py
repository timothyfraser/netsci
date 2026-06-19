"""Load the `aerospace-components` project network (Python).

Reads the two CSVs in this folder and builds a directed, weighted python-igraph
object: the bill-of-materials + supplier network for a commercial aircraft
program (detail parts & suppliers roll up toward the final assembly). Run it
straight (``python load.py``) for a quick summary, or import ``load_aero()`` into
your own script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per part / supplier."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per supply / roll-up relationship."""
    return pd.read_csv(HERE / "edges.csv")


def load_aero(nodes: pd.DataFrame | None = None,
              edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the directed, weighted graph (edge weight = ``qty_per_aircraft``).

    Edges point up the build toward the final assembly. The ``relation`` edge
    attribute is ``supplies`` (firm -> part) or ``is_part_of`` (child part ->
    parent). Trace what depends on a node with ``g.subcomponent(v, mode="out")``,
    or delete a supplier to see how many safety-critical assemblies lose supply.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=True, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["qty_per_aircraft"]
    return g


if __name__ == "__main__":
    print("\n✈️  aerospace-components (Python)")
    print("   Parts & suppliers roll up toward final assembly; "
          "weighted by qty/aircraft.\n")

    nodes = load_nodes()
    edges = load_edges()
    g = load_aero(nodes, edges)

    kinds = nodes["kind"].value_counts()
    print(f"✅ Loaded {len(nodes)} nodes "
          f"({kinds.get('part',0)} parts + {kinds.get('supplier',0)} suppliers) "
          f"and {len(edges)} edges.")
    print(f"🔗 Directed: {g.is_directed()} | "
          f"safety-critical parts: {int(nodes['safety_critical'].fillna(0).sum())} | "
          f"single-source parts: {int(nodes['single_source'].fillna(0).sum())}")
    rel = edges["relation"].value_counts()
    print(f"🧩 Relations: {rel.get('supplies',0)} supplies + "
          f"{rel.get('is_part_of',0)} is_part_of")
    print("🎉 Graph ready. Object `g` is a directed, weighted igraph "
          "(weight = qty_per_aircraft).")
