"""Generate the slim Hurricane Dorian evacuation dataset for case 08.

We start from the full Gulf-states evacuation network at
https://github.com/timothyfraser/sts (3week branch) and trim:

  - keep only Florida nodes (state FIPS = "12")
  - keep only the columns we use: node, geoid, pop, median_income
  - precompute x/y centroids from the geojson and store on the node
    table, so neither R nor Python needs sf/geopandas just to load
  - keep only edges with evacuation > 0 within Aug 28 - Sep 10, 2019
  - bundle a slimmed florida-only county_subdivisions.geojson

The source .rds files come from:
  https://raw.githubusercontent.com/timothyfraser/sts/3week/data/evacuation/

This script expects them to have been fetched to /tmp/sts_data/:

    mkdir -p /tmp/sts_data && cd /tmp/sts_data
    for f in nodes.rds edges.rds county_subdivisions.geojson states.geojson; do
      curl -sLO "https://raw.githubusercontent.com/timothyfraser/sts/3week/data/evacuation/$f"
    done

Run:
    python code/08_sampling/data/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import pyreadr
import geopandas as gpd

HERE = Path(__file__).resolve().parent
SRC = Path("/tmp/sts_data")

def main() -> None:
    if not SRC.exists():
        raise SystemExit(
            f"expected sts source data at {SRC}; see the docstring at the "
            "top of this script for the curl commands."
        )

    # --- nodes ----------------------------------------------------------------
    n = pyreadr.read_r(str(SRC / "nodes.rds"))[None]
    n = n.assign(state=n["geoid"].str[:2]).loc[lambda d: d["state"] == "12"]
    n = n[["node", "geoid", "pop", "median_income"]].reset_index(drop=True)
    n["node"] = n["node"].astype(int)

    # --- subdivisions polygons (filter to FL, dissolve to centroids) ----------
    cs = gpd.read_file(SRC / "county_subdivisions.geojson")
    cs = cs[cs["geoid"].astype(str).str[:2] == "12"].copy()
    # add x,y centroid to nodes via merge
    centroids = cs.set_geometry(cs.geometry.centroid)
    cs["x"] = centroids.geometry.x.to_numpy()
    cs["y"] = centroids.geometry.y.to_numpy()
    n = n.merge(cs[["geoid", "x", "y"]], on="geoid", how="left")

    # --- edges ----------------------------------------------------------------
    e = pyreadr.read_r(str(SRC / "edges.rds"))[None]
    e = e[["from", "to", "date_time", "evacuation", "km"]].copy()
    e["from"] = e["from"].astype(int)
    e["to"]   = e["to"].astype(int)
    e["date_time"] = pd.to_datetime(e["date_time"])

    # Filter to Florida nodes
    fl_nodes = set(n["node"].astype(int))
    e = e[e["from"].isin(fl_nodes) & e["to"].isin(fl_nodes)]
    # Filter to evacuation > 0 in the crisis window
    start = pd.Timestamp("2019-08-28")
    end   = pd.Timestamp("2019-09-11")
    e = e[(e["evacuation"] > 0) & (e["date_time"] >= start) & (e["date_time"] < end)]
    e = e.reset_index(drop=True)

    # --- write outputs --------------------------------------------------------
    n.to_csv(HERE / "nodes.csv", index=False)
    e.to_csv(HERE / "edges.csv", index=False)

    # Trim subdivisions geojson: drop attribute columns and simplify
    # geometry to keep the file small enough to bundle in a repo.
    cs_slim = cs[["geoid", "geometry"]].copy()
    cs_slim["geometry"] = cs_slim.geometry.simplify(tolerance=0.005,
                                                    preserve_topology=True)
    cs_slim.to_file(HERE / "county_subdivisions.geojson", driver="GeoJSON")

    print(f"wrote {HERE / 'nodes.csv'} ({len(n)} nodes)")
    print(f"wrote {HERE / 'edges.csv'} ({len(e):,} edges)")
    print(f"wrote {HERE / 'county_subdivisions.geojson'} (FL only)")


if __name__ == "__main__":
    main()
