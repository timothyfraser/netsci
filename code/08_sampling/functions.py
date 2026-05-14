"""Helpers for the Sampling case study."""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import geopandas as gpd


def _case_dir() -> Path:
    return Path(__file__).resolve().parent / "data"


def load_nodes() -> pd.DataFrame:
    # geoid is a numeric-looking string ("1208692158"); force string read
    # so equality comparisons against literal "1208692158" succeed.
    return pd.read_csv(_case_dir() / "nodes.csv", dtype={"geoid": "string"})


def load_edges() -> pd.DataFrame:
    # date_time is ISO-8601 in CSV; parse to Timestamps so groupby
    # gives an ordered time series.
    return pd.read_csv(_case_dir() / "edges.csv", parse_dates=["date_time"])


def load_subdivisions() -> gpd.GeoDataFrame:
    return gpd.read_file(_case_dir() / "county_subdivisions.geojson")


def slice_stats(edges: pd.DataFrame, n_total_nodes: int) -> pd.DataFrame:
    """Per-time-slice network statistics, mirrors the sts 29C workshop.

    Columns: edgeweight, n_edges, n_nodes, n_nodes_linked, density,
    pc_nodes_linked, edge_ratio, avg_edgeweight.
    """
    out = (
        edges
        .groupby("date_time", as_index=False)
        .agg(
            edgeweight=("evacuation", "sum"),
            n_edges=("evacuation", "size"),
            from_set=("from", lambda s: set(s)),
            to_set=("to",   lambda s: set(s)),
        )
    )
    out["n_nodes"] = n_total_nodes
    out["n_nodes_linked"] = out.apply(
        lambda r: len(r["from_set"] | r["to_set"]), axis=1)
    out = out.drop(columns=["from_set", "to_set"])
    out["density"] = 2 * out["n_edges"] / (out["n_nodes"] * (out["n_nodes"] - 1))
    out["pc_nodes_linked"] = out["n_nodes_linked"] / out["n_nodes"]
    out["edge_ratio"]      = out["n_edges"]       / out["n_nodes"]
    out["avg_edgeweight"]  = out["edgeweight"]    / out["n_nodes"]
    return out
