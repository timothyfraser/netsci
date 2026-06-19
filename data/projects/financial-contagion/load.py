"""Load the `financial-contagion` project network (Python).

Reads the two CSVs in this folder and builds a directed, weighted python-igraph
object: directed financial exposures (creditor -> debtor) among ~220 firms across
three periods of a crisis (before / during / after). Run it straight
(``python load.py``) for a quick summary, or import ``load_contagion()`` into
your own script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per firm."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per creditor x debtor x period."""
    return pd.read_csv(HERE / "edges.csv")


def load_contagion(nodes: pd.DataFrame | None = None,
                   edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the directed, weighted graph (edge weight = ``exposure``).

    The data is temporal (a ``period`` column: before/during/after), so an
    exposure between the same pair can appear up to 3 times as parallel edges.
    Filter to one ``period`` first if you want a single-period graph.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=True, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["exposure"]
    return g


if __name__ == "__main__":
    print("\n\U0001F3E6 financial-contagion (Python)")
    print("   Directed creditor -> debtor exposures; before / during / after a crisis.\n")

    nodes = load_nodes()
    edges = load_edges()
    g = load_contagion(nodes, edges)

    t = nodes["type"].value_counts()
    print(f"✅ Loaded {len(nodes)} nodes "
          f"({t.get('bank',0)} banks, {t.get('hedge_fund',0)} hedge funds, "
          f"{t.get('insurer',0)} insurers, {t.get('ccp',0)} ccps) "
          f"and {len(edges)} edges.")
    for p in ("before", "during", "after"):
        print(f"   period {p:<7}: {(edges['period']==p).sum()} exposures")
    print(f"\U0001F517 Directed: {g.is_directed()} | total exposure: "
          f"{round(edges['exposure'].sum()):,}")
    print("\U0001F389 Graph ready. Object `g` is a directed, weighted igraph.")
