"""Generate the slim Bluebikes-flavored data files for case 02 (joins).

This produces a small but realistic stand-in for the real Bluebikes SQLite
that lessons 21C/22C of the sts course use. We don't ship the multi-GB
SQLite in this repo; instead, we generate ~500 stations and ~50,000 AM
rush-hour trip rows, deterministically, so the join exercise has signal.

Run once to regenerate the parquet files:

    python code/02_joins/data/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

def main() -> None:
    rng = np.random.default_rng(SEED)

    # ----- stations -----------------------------------------------------------
    # 500 stations spread across 5 "neighborhood clusters" (block groups).
    # We give some clusters higher Black-majority probability and others
    # lower, so the demographic join produces non-trivial cross-class counts.
    n_stations = 500
    cluster_id = rng.integers(0, 5, size=n_stations)
    # cluster 0,1: majority Black; cluster 2,3,4: not
    p_maj_black = np.array([0.85, 0.65, 0.10, 0.05, 0.02])[cluster_id]
    maj_black = np.where(rng.random(n_stations) < p_maj_black, "yes", "no")

    stations = pd.DataFrame({
        "code":      [f"S{idx:04d}" for idx in range(n_stations)],
        "cluster":   cluster_id,
        "maj_black": maj_black,
        # rough Boston-area lat/lon, jittered per cluster
        "x": (-71.10 + (cluster_id - 2) * 0.02
              + rng.normal(0, 0.01, n_stations)),
        "y": (42.34 + (cluster_id - 2) * 0.01
              + rng.normal(0, 0.008, n_stations)),
    })

    # ----- edges --------------------------------------------------------------
    # AM rush, year 2021. We sample 50,000 (start, end, day) triples
    # with assortative bias: trips are more likely within the same cluster.
    n_edges = 50_000

    # day strings YYYY-MM-DD across 2021
    days = pd.date_range("2021-01-01", "2021-12-31", freq="D").strftime("%Y-%m-%d").to_numpy()

    # pick a start station uniformly
    start_idx = rng.integers(0, n_stations, size=n_edges)
    # pick an end station with bias toward the same cluster
    same_cluster = rng.random(n_edges) < 0.70  # 70% within-cluster
    end_idx = np.where(
        same_cluster,
        # within-cluster: sample uniformly among stations in the same cluster
        np.array([rng.choice(np.flatnonzero(cluster_id == cluster_id[s]))
                  for s in start_idx]),
        # across-cluster: pick any
        rng.integers(0, n_stations, size=n_edges),
    )

    edges = pd.DataFrame({
        "start_code": stations["code"].to_numpy()[start_idx],
        "end_code":   stations["code"].to_numpy()[end_idx],
        "day":        rng.choice(days, size=n_edges),
        "rush":       "am",
        "count":      rng.integers(1, 8, size=n_edges),
    })

    # sort for nicer git diffs
    edges = edges.sort_values(["day", "start_code", "end_code"]).reset_index(drop=True)
    stations = stations.sort_values("code").reset_index(drop=True)

    edges.to_csv(HERE / "edges.csv", index=False)
    stations.to_csv(HERE / "stations.csv", index=False)

    print(f"wrote {HERE / 'edges.csv'}  ({len(edges):,} rows)")
    print(f"wrote {HERE / 'stations.csv'} ({len(stations):,} rows)")


if __name__ == "__main__":
    main()
