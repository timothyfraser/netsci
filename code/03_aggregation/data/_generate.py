"""Generate the slim mobility-flow data for case 03 (aggregation).

Mirrors case 02 in flavor, but adds two extra columns on the stations
table — `neighborhood` (one of 12) and `income_quintile` (1..4 where 4
is wealthiest). This lets the example.* scripts demonstrate the
*aggregation-by-resolution* idea: same network, viewed at 3 zoom
levels.

Run once to regenerate:

    python code/03_aggregation/data/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

def main() -> None:
    rng = np.random.default_rng(SEED)

    n_stations = 500
    n_neighborhoods = 12
    # assign stations to neighborhoods
    nbhd = rng.integers(0, n_neighborhoods, size=n_stations)
    # each neighborhood has a "wealth" score; from that we'll derive a
    # 1..4 quintile (we say "quintile" loosely but use 4 buckets to
    # match the case study's 4-quartile heatmap).
    nbhd_wealth = rng.uniform(size=n_neighborhoods)
    station_wealth = nbhd_wealth[nbhd] + rng.normal(0, 0.05, n_stations)
    quintile = pd.qcut(station_wealth, q=4, labels=[1, 2, 3, 4]).astype(int)

    stations = pd.DataFrame({
        "code": [f"S{i:04d}" for i in range(n_stations)],
        "neighborhood": [f"N{n:02d}" for n in nbhd],
        "income_quintile": quintile,
        "x": (-71.10 + (nbhd - 6) * 0.01 + rng.normal(0, 0.005, n_stations)),
        "y": (42.34 + (nbhd - 6) * 0.005 + rng.normal(0, 0.004, n_stations)),
    })

    # ~40k AM-rush 2021 trip rows. Bias trips to stay within neighborhood.
    n_edges = 40_000
    days = pd.date_range("2021-01-01", "2021-12-31", freq="D").strftime("%Y-%m-%d").to_numpy()

    start_idx = rng.integers(0, n_stations, size=n_edges)
    same_nbhd = rng.random(n_edges) < 0.55
    end_idx = np.where(
        same_nbhd,
        np.array([rng.choice(np.flatnonzero(nbhd == nbhd[s])) for s in start_idx]),
        rng.integers(0, n_stations, size=n_edges),
    )

    edges = pd.DataFrame({
        "start_code": stations["code"].to_numpy()[start_idx],
        "end_code":   stations["code"].to_numpy()[end_idx],
        "day":        rng.choice(days, size=n_edges),
        "rush":       "am",
        "count":      rng.integers(1, 6, size=n_edges),
    }).sort_values(["day", "start_code", "end_code"]).reset_index(drop=True)

    stations = stations.sort_values("code").reset_index(drop=True)

    edges.to_parquet(HERE / "edges.parquet", index=False)
    stations.to_parquet(HERE / "stations.parquet", index=False)

    print(f"wrote {HERE / 'edges.parquet'} ({len(edges):,} rows)")
    print(f"wrote {HERE / 'stations.parquet'} ({len(stations):,} rows)")


if __name__ == "__main__":
    main()
