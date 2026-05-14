"""Helpers for the Aggregation case study.

Path-resolved loaders for the slim mobility-flow data.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd


def _case_dir() -> Path:
    return Path(__file__).resolve().parent / "data"


def load_edges() -> pd.DataFrame:
    return pd.read_parquet(_case_dir() / "edges.parquet")


def load_stations() -> pd.DataFrame:
    return pd.read_parquet(_case_dir() / "stations.parquet")


def make_enriched(edges: pd.DataFrame | None = None,
                  stations: pd.DataFrame | None = None) -> pd.DataFrame:
    """Edges with start- and end-side traits already joined in."""
    if edges is None:
        edges = load_edges()
    if stations is None:
        stations = load_stations()

    s_start = stations[["code", "neighborhood", "income_quintile"]].rename(
        columns={"code": "start_code",
                 "neighborhood": "start_nbhd",
                 "income_quintile": "start_quintile"})
    s_end = stations[["code", "neighborhood", "income_quintile"]].rename(
        columns={"code": "end_code",
                 "neighborhood": "end_nbhd",
                 "income_quintile": "end_quintile"})

    return edges.merge(s_start, on="start_code", how="left") \
                .merge(s_end,   on="end_code",   how="left")
