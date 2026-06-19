"""Load the `campus-contact` project network (Python).

Reads the CSVs in this folder and builds an undirected, weighted python-igraph
object: weekly face-to-face co-location contacts on a campus over four weeks.
Run it straight (``python load.py``) for a quick summary, or import
``load_campus()`` into your own script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per person."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per person x person x week."""
    return pd.read_csv(HERE / "edges.csv")


def load_status() -> pd.DataFrame:
    """Infection-status table: one row per person x week."""
    return pd.read_csv(HERE / "status.csv")


def load_campus(nodes: pd.DataFrame | None = None,
                edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the undirected, weighted contact graph (edge weight = ``contact_minutes``).

    The data is temporal (a ``week`` column), so a pair can appear up to 4 times
    as parallel edges. Filter to one ``week`` first if you want a simple graph.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=False, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["contact_minutes"]
    return g


if __name__ == "__main__":
    print("\n\U0001F9A0 campus-contact (Python)")
    print("   Weekly face-to-face contacts on campus; weighted by contact minutes.\n")

    nodes = load_nodes()
    edges = load_edges()
    status = load_status()
    g = load_campus(nodes, edges)

    kinds = nodes["kind"].value_counts()
    print(f"✅ Loaded {len(nodes)} people "
          f"({kinds.get('student',0)} students, {kinds.get('faculty',0)} faculty, "
          f"{kinds.get('staff',0)} staff) and {len(edges)} contact-weeks.")
    print(f"\U0001F517 Directed: {g.is_directed()} | total contact minutes: "
          f"{edges['contact_minutes'].sum():,}")
    inf = status.groupby("week")["infected"].sum()
    print("\U0001F4C8 Cumulative infected by week: "
          + "  ".join(f"wk{w}={c}" for w, c in inf.items()))
    print("\U0001F389 Graph ready. Object `g` is an undirected, weighted igraph.")
