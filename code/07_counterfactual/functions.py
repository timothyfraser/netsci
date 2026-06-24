"""Helpers for the Counterfactual Monte Carlo case study."""
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


def build_graph(nodes: pd.DataFrame, edges: pd.DataFrame,
                with_extra: pd.DataFrame | None = None) -> ig.Graph:
    """Build the bikeshare graph (undirected) with a ``cost`` edge attr.

    For weighted APL, cost = 1 / max(ridership, 1) so that
    higher-ridership edges are "shorter."
    """
    e = edges.copy()
    if with_extra is not None and len(with_extra) > 0:
        e = pd.concat([e, with_extra], ignore_index=True)
    e["cost"] = 1.0 / np.maximum(e["ridership"].to_numpy(), 1)
    return ig.Graph.DataFrame(edges=e, directed=False, vertices=nodes,
                              use_vids=False)


def weighted_apl(g: ig.Graph) -> float:
    """Weighted APL using ``cost`` as edge weight."""
    return float(g.average_path_length(weights="cost", directed=False))


def mc_apls(edges: pd.DataFrame, nodes: pd.DataFrame,
            R: int = 500,
            extra: pd.DataFrame | None = None,
            seed: int = 1) -> np.ndarray:
    """Monte Carlo: ``R`` replicates of the network where each edge's
    ridership is resampled from Poisson(lambda = observed_ridership),
    rebuild, and return a vector of weighted APLs.
    """
    rng = np.random.default_rng(seed)
    out = np.empty(R)
    base_ridership = edges["ridership"].to_numpy()
    for i in range(R):
        new_r = rng.poisson(lam=base_ridership)
        new_edges = edges.copy()
        new_edges["ridership"] = new_r
        extra_resampled = None
        if extra is not None and len(extra) > 0:
            ex = extra.copy()
            ex["ridership"] = rng.poisson(lam=ex["ridership"].to_numpy())
            extra_resampled = ex
        g = build_graph(nodes, new_edges, with_extra=extra_resampled)
        out[i] = weighted_apl(g)
    return out
