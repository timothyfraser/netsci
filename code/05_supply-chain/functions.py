"""Helpers for the Supply Chain Resilience case study."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable
import pandas as pd
import igraph as ig


def _case_dir() -> Path:
    return Path(__file__).resolve().parent / "data"


def load_nodes() -> pd.DataFrame:
    return pd.read_csv(_case_dir() / "nodes.csv")


def load_edges() -> pd.DataFrame:
    return pd.read_csv(_case_dir() / "edges.csv")


def build_graph(nodes: pd.DataFrame | None = None,
                edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the directed supply-chain graph."""
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    return ig.Graph.DataFrame(
        edges=edges,
        directed=True,
        vertices=nodes,
        use_vids=False,
    )


def supply_coverage(g: ig.Graph) -> float:
    """Fraction of retailers (tier 3) reachable from any supplier (tier 1)."""
    suppliers = [v.index for v in g.vs if v["tier"] == 1]
    retailers = [v.index for v in g.vs if v["tier"] == 3]
    if not retailers:
        return float("nan")
    retailer_set = set(retailers)
    reachable: set[int] = set()
    for s in suppliers:
        reachable.update(g.subcomponent(s, mode="out"))
        if retailer_set.issubset(reachable):
            break
    return len(reachable & retailer_set) / len(retailer_set)


def remove_and_score(g: ig.Graph, victims: Iterable[str]) -> float:
    """Remove a set of nodes by name and report supply coverage."""
    victims = set(victims)
    g2 = g.copy()
    to_delete = [v.index for v in g2.vs if v["name"] in victims]
    g2.delete_vertices(to_delete)
    return supply_coverage(g2)
