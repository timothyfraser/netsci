"""Helpers for the GNN-by-Hand case study.

We implement the forward pass of a simple Graph Convolutional
Network (GCN) layer from scratch in numpy. No torch, no
torch_geometric. The point is to see the math.
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd


def _case_dir() -> Path:
    return Path(__file__).resolve().parent / "data"


def load_tiny() -> tuple[pd.DataFrame, pd.DataFrame]:
    n = pd.read_csv(_case_dir() / "tiny_nodes.csv")
    e = pd.read_csv(_case_dir() / "tiny_edges.csv")
    return n, e


def load_large() -> tuple[pd.DataFrame, pd.DataFrame]:
    n = pd.read_csv(_case_dir() / "large_nodes.csv")
    e = pd.read_csv(_case_dir() / "large_edges.csv")
    return n, e


def adjacency(nodes: pd.DataFrame, edges: pd.DataFrame,
              add_self_loops: bool = True) -> np.ndarray:
    """Return an N x N adjacency matrix (undirected) from edges."""
    n = len(nodes)
    idx = {nid: i for i, nid in enumerate(nodes["node_id"].to_numpy())}
    A = np.zeros((n, n))
    for _, r in edges.iterrows():
        i, j = idx[int(r["from"])], idx[int(r["to"])]
        A[i, j] = 1
        A[j, i] = 1
    if add_self_loops:
        np.fill_diagonal(A, 1)
    return A


def normalize(A: np.ndarray) -> np.ndarray:
    """Symmetric normalization: D^{-1/2} A D^{-1/2}.

    This is the GCN normalization (Kipf & Welling 2017).
    """
    d = A.sum(axis=1)
    d_inv_sqrt = 1.0 / np.sqrt(np.where(d == 0, 1, d))
    D_inv_sqrt = np.diag(d_inv_sqrt)
    return D_inv_sqrt @ A @ D_inv_sqrt


def relu(x: np.ndarray) -> np.ndarray:
    return np.maximum(0, x)


def gcn_layer(A_norm: np.ndarray, X: np.ndarray, W: np.ndarray,
              activation: str = "relu") -> np.ndarray:
    """One GCN layer: H = sigma(A_norm @ X @ W).

    Args:
        A_norm: N x N normalized adjacency.
        X: N x F input features.
        W: F x F_out weight matrix.
        activation: "relu" or "none".
    """
    H = A_norm @ X @ W
    if activation == "relu":
        H = relu(H)
    return H
