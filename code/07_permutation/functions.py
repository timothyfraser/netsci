"""Helpers for the Permutation case study."""
from __future__ import annotations

from pathlib import Path
import numpy as np
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
    """Build the graph (undirected, weighted) from node + edge tables."""
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    return ig.Graph.DataFrame(
        edges=edges, directed=False, vertices=nodes, use_vids=False
    )


def assort_by(g: ig.Graph, attr_name: str) -> float:
    """Nominal assortativity by ``attr_name`` (e.g. ``demo``).

    Returns a single number; +1 = perfectly assortative, 0 = random,
    -1 = perfectly disassortative.
    """
    types = pd.Categorical(g.vs[attr_name]).codes.tolist()
    return float(g.assortativity_nominal(types=types, directed=False))


def permute_labels(g: ig.Graph, attr_name: str,
                   block_by: str | None = None,
                   rng: np.random.Generator | None = None) -> ig.Graph:
    """Return a copy of ``g`` with node ``attr_name`` shuffled.

    ``block_by=None`` shuffles labels across ALL nodes; otherwise
    shuffles labels WITHIN each block (preserves the block-level
    composition).
    """
    if rng is None:
        rng = np.random.default_rng()
    labels = np.array(g.vs[attr_name])
    if block_by is None:
        new_labels = rng.permutation(labels)
    else:
        blocks = np.array(g.vs[block_by])
        new_labels = labels.copy()
        for b in np.unique(blocks):
            mask = blocks == b
            new_labels[mask] = rng.permutation(labels[mask])
    g2 = g.copy()
    g2.vs[attr_name] = new_labels.tolist()
    return g2
