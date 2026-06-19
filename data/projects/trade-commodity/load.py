"""Load the `trade-commodity` project network (Python).

Reads the two CSVs in this folder and builds a directed, weighted python-igraph
object: export flows of a single strategic commodity between countries, recorded
across three periods (``before`` / ``during`` / ``after`` a supply shock). Run it
straight (``python load.py``) for a quick summary, or import ``load_trade()``
into your own script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per country."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per exporter x importer x period."""
    return pd.read_csv(HERE / "edges.csv")


def load_trade(nodes: pd.DataFrame | None = None,
               edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the directed, weighted graph (edge weight = ``tonnes``).

    The data is temporal (a ``period`` column), so an exporter->importer pair can
    appear up to three times (once per period) as parallel edges. Filter to one
    ``period`` first if you want a simple graph, e.g.
    ``edges[edges.period == "before"]``.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=True, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["tonnes"]
    return g


if __name__ == "__main__":
    print("\n\U0001F310 trade-commodity (Python)")
    print("   Country-to-country commodity export flows; weighted by tonnes,")
    print("   across before / during / after a supply shock.\n")

    nodes = load_nodes()
    edges = load_edges()
    g = load_trade(nodes, edges)

    print(f"✅ Loaded {len(nodes)} countries and {len(edges)} edges across "
          f"{edges['period'].nunique()} periods.")
    print(f"\U0001F517 Directed: {g.is_directed()} | total tonnes traded: "
          f"{edges['tonnes'].sum():,}")
    per = edges.groupby('period')['tonnes'].sum()
    print("\U0001F4E6 Tonnes by period: " +
          " | ".join(f"{k}={v:,}" for k, v in per.items()))
    print("\U0001F389 Graph ready. Object `g` is a directed, weighted igraph.")
