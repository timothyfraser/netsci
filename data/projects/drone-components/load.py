"""Load the `drone-components` project network (Python).

Reads the two CSVs in this folder and builds a directed, weighted python-igraph
object: a UAV functional dependency graph (``A -> B`` means *A depends on / requires
B to function*). Run it straight (``python load.py``) for a quick summary, or
import ``load_drone()`` into your own script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per component (hardware or software module)."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per dependency (from_id requires to_id)."""
    return pd.read_csv(HERE / "edges.csv")


def load_drone(nodes: pd.DataFrame | None = None,
               edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the directed, weighted dependency graph (weight = ``coupling_strength``).

    Direction is ``from_id -> to_id``: ``from_id`` depends on / requires
    ``to_id`` to function. The graph is intentionally NOT a clean DAG.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=True, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["coupling_strength"]
    return g


if __name__ == "__main__":
    print("\n\U0001F681 drone-components (Python)")
    print("   UAV functional dependency graph; A -> B means A requires B to function.\n")

    nodes = load_nodes()
    edges = load_edges()
    g = load_drone(nodes, edges)

    kinds = nodes["kind"].value_counts()
    print(f"✅ Loaded {len(nodes)} components "
          f"({kinds.get('hardware', 0)} hardware, {kinds.get('software', 0)} software) "
          f"and {len(edges)} dependency edges.")
    print(f"\U0001F517 Directed: {g.is_directed()} | is DAG: {g.is_dag()} | "
          f"total coupling: {edges['coupling_strength'].sum():,}")
    indeg = g.indegree()
    outdeg = g.outdegree()
    names = g.vs["name"]
    i_max = max(range(len(indeg)), key=lambda i: indeg[i])
    o_max = max(range(len(outdeg)), key=lambda i: outdeg[i])
    print(f"\U0001F4CA Max in-degree: {indeg[i_max]} ({names[i_max]}) | "
          f"max out-degree: {outdeg[o_max]} ({names[o_max]})")
    print("\U0001F389 Graph ready. Object `g` is a directed, weighted igraph.")
