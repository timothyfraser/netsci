"""Load the `mutualaid-quake` project network (Python).

Reads the two CSVs in this folder and builds a directed, weighted python-igraph
object: acts of mutual aid given between residents and organizations in fictional
"Eastvale" across three periods of an earthquake. Run it straight
(``python load.py``) for a quick summary, or import ``load_mutualaid()`` into
your own script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per resident / org."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per giver x receiver x period."""
    return pd.read_csv(HERE / "edges.csv")


def load_mutualaid(nodes: pd.DataFrame | None = None,
                   edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the directed, weighted graph (edge weight = ``amount``).

    The data is temporal (a ``period`` column: before/during/after), so an edge
    between the same pair can appear up to 3 times as parallel edges. Filter to
    one ``period`` first if you want a single-period graph.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=True, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["amount"]
    return g


if __name__ == "__main__":
    print("\n\U0001F91D mutualaid-quake (Python)")
    print("   Directed aid between residents & orgs; before / during / after a quake.\n")

    nodes = load_nodes()
    edges = load_edges()
    g = load_mutualaid(nodes, edges)

    kinds = nodes["kind"].value_counts()
    print(f"✅ Loaded {len(nodes)} nodes "
          f"({kinds.get('resident',0)} residents, {kinds.get('org',0)} orgs) "
          f"and {len(edges)} edges.")
    for p in ("before", "during", "after"):
        print(f"   period {p:<7}: {(edges['period']==p).sum()} ties")
    print(f"\U0001F517 Directed: {g.is_directed()} | total aid given: "
          f"{round(edges['amount'].sum()):,}")
    print("\U0001F389 Graph ready. Object `g` is a directed, weighted igraph.")
