"""Helpers for the Network Joins case study.

Small helper functions used by ``example.py``:

- ``load_edges()``    — read the slim rush-hour trips parquet.
- ``load_stations()`` — read the slim stations parquet (with demographic flag).
- ``make_joined()``   — convenience wrapper that does the standard
                        start-side + end-side double merge, with renames.

We keep the functions tiny on purpose. The teaching happens in
``example.py``; this file is so you can call ``load_edges()`` instead of
remembering the parquet path.
"""

from pathlib import Path
import pandas as pd

# ----- paths -----------------------------------------------------------------

# Resolve paths relative to THIS file's folder, so the script works no matter
# where you run it from.
def _case_dir() -> Path:
    return Path(__file__).resolve().parent / "data"


# ----- data loaders ----------------------------------------------------------

def load_edges() -> pd.DataFrame:
    """Load the slim trips edge list.

    One row per (start_station, end_station, day, rush) combination, with
    ``count`` = number of trips. Already filtered to AM rush + 2021.
    """
    return pd.read_csv(_case_dir() / "edges.csv")


def load_stations() -> pd.DataFrame:
    """Load the slim stations node table.

    One row per station, with a ``maj_black`` flag ("yes"/"no") from the
    census block group the station sits in.
    """
    return pd.read_csv(_case_dir() / "stations.csv")


# ----- the reference join ----------------------------------------------------

def make_joined(edges: pd.DataFrame | None = None,
                stations: pd.DataFrame | None = None) -> pd.DataFrame:
    """The "standard" double-side join used as a sanity check.

    Renames demographics to ``start_black`` and ``end_black``, then drops
    any edge whose start *or* end station is missing from the stations
    table (these correspond to stations outside Boston proper).
    """
    if edges is None:
        edges = load_edges()
    if stations is None:
        stations = load_stations()

    out = (
        edges
        .merge(
            stations[["code", "maj_black"]].rename(
                columns={"code": "start_code", "maj_black": "start_black"}),
            on="start_code", how="left")
        .merge(
            stations[["code", "maj_black"]].rename(
                columns={"code": "end_code", "maj_black": "end_black"}),
            on="end_code", how="left")
    )
    return out.dropna(subset=["start_black", "end_black"]).reset_index(drop=True)
