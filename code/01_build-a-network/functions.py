"""Helpers for the Build-a-Network case study.

Tiny wrappers around ``pd.read_csv()`` that resolve paths for us, plus
a single helper that takes the node + edge tables and returns an
``igraph.Graph`` built the "right" way (bipartite, with ``kind`` tagged
on as a vertex attribute).
"""
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


def build_bipartite(nodes: pd.DataFrame | None = None,
                    edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build an igraph bipartite graph from node + edge tables.

    Sets ``type = True`` for components and ``type = False`` for
    suppliers, which is the convention igraph uses to flag a
    bipartite graph.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()

    g = ig.Graph.DataFrame(
        edges=edges[["from_id", "to_id", "volume_units"]],
        directed=False,
        vertices=nodes[["node_id", "kind", "region", "tier", "capacity_units"]],
        use_vids=False,
    )
    g.vs["type"] = [k == "component" for k in g.vs["kind"]]
    return g
