"""Helpers for the DSM Clustering case study."""
from __future__ import annotations

from pathlib import Path
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
    """Build the DSM dependency graph (directed)."""
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


def cascade_bfs(g: ig.Graph, seed_node: str, n_hops: int = 3) -> list[str]:
    """Components that fail within ``n_hops`` of ``seed_node``.

    Follows outgoing dependency edges. With high inter-module
    connectivity, an unbounded cascade can reach every component, so
    we bound to k hops to keep the simulation interpretable.
    """
    seed = g.vs.find(name=seed_node).index
    reached = g.neighborhood(seed, order=n_hops, mode="out")
    return [g.vs[i]["name"] for i in reached]
