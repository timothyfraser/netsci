"""Helpers for the GNN + XGBoost case study.

The pipeline:
  - load static features per supplier + dependency edges + disruption panel
  - build a lag feature: 4-week trailing disruption rate per supplier
  - build a structural-GNN embedding: mean of in-neighbors' lag rate
    (1 hop), plus mean of in-neighbors' in-neighbors' lag rate (2 hop).
    This is a parameter-free GCN-style aggregation; no torch needed.
  - train XGBoost on different feature sets and report ROC AUC.
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd


def _case_dir() -> Path:
    return Path(__file__).resolve().parent / "data"


def load_suppliers() -> pd.DataFrame:
    return pd.read_csv(_case_dir() / "suppliers.csv")


def load_edges() -> pd.DataFrame:
    return pd.read_csv(_case_dir() / "edges.csv")


def load_panel() -> pd.DataFrame:
    return pd.read_csv(_case_dir() / "panel.csv")


def add_lag_features(panel: pd.DataFrame, window: int = 4) -> pd.DataFrame:
    """Add a `lag_rate` column: trailing `window`-week disruption rate per supplier.

    Week 0..window-1 use the available history so far.
    """
    panel = panel.sort_values(["supplier_id", "week"]).copy()
    panel["lag_rate"] = (
        panel.groupby("supplier_id")["disrupted"]
        .shift(1)
        .rolling(window, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
    )
    panel["lag_rate"] = panel["lag_rate"].fillna(0.0)
    return panel


def build_adjacency(suppliers: pd.DataFrame, edges: pd.DataFrame) -> np.ndarray:
    """N x N row-normalized in-neighbor matrix (rows sum to 1 or 0)."""
    n = len(suppliers)
    idx = {s: i for i, s in enumerate(suppliers["supplier_id"].to_numpy())}
    A = np.zeros((n, n))
    for _, e in edges.iterrows():
        A[idx[e["to"]], idx[e["from"]]] = 1
    row_sums = A.sum(axis=1, keepdims=True)
    A = np.divide(A, row_sums, out=np.zeros_like(A), where=row_sums > 0)
    return A


def add_gnn_embeddings(panel: pd.DataFrame, suppliers: pd.DataFrame,
                       A: np.ndarray) -> pd.DataFrame:
    """Add 1-hop and 2-hop neighbor-averaged lag-rate features per week.

    These play the role of GNN embedding dimensions; the math is the
    "A_norm @ x" piece of a GCN layer, parameter-free.
    """
    panel = panel.copy()
    idx = {s: i for i, s in enumerate(suppliers["supplier_id"].to_numpy())}
    panel["_idx"] = panel["supplier_id"].map(idx)

    out_1hop = np.empty(len(panel))
    out_2hop = np.empty(len(panel))
    A2 = A @ A
    for week, sub in panel.groupby("week"):
        # vector of lag_rate per supplier index for this week
        lag = np.zeros(len(suppliers))
        lag[sub["_idx"].to_numpy()] = sub["lag_rate"].to_numpy()
        h1 = A @ lag
        h2 = A2 @ lag
        out_1hop[sub.index] = h1[sub["_idx"].to_numpy()]
        out_2hop[sub.index] = h2[sub["_idx"].to_numpy()]
    panel["gnn_1hop"] = out_1hop
    panel["gnn_2hop"] = out_2hop
    return panel.drop(columns=["_idx"])
