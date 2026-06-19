"""Load the `reorg-comms` project network (Python).

Reads the two CSVs in this folder and builds a directed, weighted python-igraph
object: internal message volume between employees, recorded across three periods
(``before`` / ``during`` / ``after`` a reorganization + layoff). Run it straight
(``python load.py``) for a quick summary, or import ``load_reorg()`` into your own
script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per employee.

    ``manager_id`` is read as a string (it is a node id, blank for department
    heads).
    """
    return pd.read_csv(HERE / "nodes.csv", dtype={"manager_id": "string"})


def load_edges() -> pd.DataFrame:
    """Edge table: one row per sender x receiver x period."""
    return pd.read_csv(HERE / "edges.csv")


def load_reorg(nodes: pd.DataFrame | None = None,
               edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the directed, weighted graph (edge weight = ``message_count``).

    The data is temporal (a ``period`` column), so a sender->receiver pair can
    appear up to three times (once per period) as parallel edges. Filter to one
    ``period`` first if you want a simple graph, e.g.
    ``edges[edges.period == "before"]``.

    Note: ``manager_id`` on the node table is the FORMAL org-chart reporting line
    (blank for department heads), separate from who actually messages whom.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    # igraph dislikes pandas <NA> in vertex attributes; blank out missing managers.
    nodes = nodes.copy()
    nodes["manager_id"] = nodes["manager_id"].fillna("").astype(str)
    g = ig.Graph.DataFrame(edges, directed=True, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["message_count"]
    return g


if __name__ == "__main__":
    print("\n\U0001F4AC reorg-comms (Python)")
    print("   Employee-to-employee message volume; weighted by message_count,")
    print("   across before / during / after a reorganization + layoff.\n")

    nodes = load_nodes()
    edges = load_edges()
    g = load_reorg(nodes, edges)

    print(f"✅ Loaded {len(nodes)} employees ({int((nodes.laid_off==1).sum())} laid off) "
          f"and {len(edges)} edges across {edges['period'].nunique()} periods.")
    print(f"\U0001F517 Directed: {g.is_directed()} | total messages: "
          f"{edges['message_count'].sum():,}")
    per = edges.groupby('period')['message_count'].sum()
    print("\U0001F4E8 Messages by period: " +
          " | ".join(f"{k}={v:,}" for k, v in per.items()))
    print("\U0001F389 Graph ready. Object `g` is a directed, weighted igraph.")
