"""Case Study 08 — Sampling Big Networks (Python track).

You can't analyze every node in a million-node network on a laptop.
So we sample. But sampling is not neutral — each strategy preserves
some properties and distorts others. This case study shows you which.

Data: Hurricane Dorian evacuation flows over Florida county
subdivisions, Aug 28 - Sep 10, 2019. Each edge is a (from, to,
date_time, evacuation) tuple where `evacuation` is how many MORE
local Facebook users moved between two cities in that 8-hour window
than usual. The original sts workshop 29C_databases.R covers the
same network at a Gulf scale; we trim to Florida and to the crisis
weeks.

We will:
  1. Compute baseline per-time-slice network statistics on the full
     filtered network.
  2. Take three sampling strategies (ego-centric, edgewise, spatial
     buffer around Miami).
  3. Compare each sample's stats against the population over time.
"""

# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point

## 0.2 Load helpers ##########################################################

from functions import (
    load_nodes, load_edges, load_subdivisions, slice_stats,
)

## 0.3 Load data #############################################################

nodes = load_nodes()
edges = load_edges()
print(f"nodes: {len(nodes):,}  edges: {len(edges):,}")
print(edges.head())


# 1. Baseline (population) statistics over time ##############################

n_total = len(nodes)
stats = slice_stats(edges, n_total)
print(stats.head())


# 2. Sampling strategies #####################################################

rng = np.random.default_rng(42)

## 2.1 Ego-centric: sample N nodes, keep edges that touch any sampled node ###

ego_nodes = nodes.sample(n=50, random_state=42)["node"].to_numpy()
ego_edges = edges[edges["from"].isin(ego_nodes) | edges["to"].isin(ego_nodes)]
print(f"ego sample: {len(ego_nodes)} seed nodes, {len(ego_edges):,} edges")
ego_stats = slice_stats(ego_edges, n_total)

## 2.2 Edgewise: sample edges uniformly #######################################

edge_sample = edges.sample(n=10_000, random_state=42)
edge_stats  = slice_stats(edge_sample, n_total)
print(f"edge sample: {len(edge_sample):,} edges")

## 2.3 Spatial buffer: keep edges where BOTH endpoints are within 200 km of Miami

# Miami-area geoid; we use this node's centroid as the point of interest.
miami_geoid = "1208692158"
miami_row = nodes[nodes["geoid"] == miami_geoid].iloc[0]
poi = gpd.GeoSeries([Point(miami_row["x"], miami_row["y"])], crs="EPSG:4326")
# Reproject to a meter-based CRS for buffering, then back to lat/lon.
poi_m   = poi.to_crs("EPSG:3857")
buf_m   = poi_m.buffer(200_000)              # 200 km
buf_ll  = gpd.GeoSeries(buf_m, crs="EPSG:3857").to_crs("EPSG:4326")

node_pts = gpd.GeoDataFrame(
    nodes,
    geometry=[Point(xy) for xy in zip(nodes["x"], nodes["y"])],
    crs="EPSG:4326",
)
nodes_in_buf = node_pts[node_pts.within(buf_ll.iloc[0])]
print(f"buffer sample: {len(nodes_in_buf)} nodes within 200 km of Miami")

ids_in = set(nodes_in_buf["node"].to_numpy())
buf_edges = edges[edges["from"].isin(ids_in) & edges["to"].isin(ids_in)]
buf_stats = slice_stats(buf_edges, n_total)


# 3. Compare samples vs population ###########################################

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharex=True)

ax = axes[0]
ax.plot(stats["date_time"],     stats["avg_edgeweight"],     label="Population",     color="black")
ax.plot(ego_stats["date_time"], ego_stats["avg_edgeweight"], label="Ego-centric",     color="#3a8bc6")
ax.plot(edge_stats["date_time"],edge_stats["avg_edgeweight"],label="Edgewise",        color="#e07b3a")
ax.plot(buf_stats["date_time"], buf_stats["avg_edgeweight"], label="Spatial buffer", color="#7b3ae0")
ax.set_ylabel("avg_edgeweight (per node)")
ax.legend(fontsize=8)
ax.set_title("avg edgeweight per node")

ax = axes[1]
ax.plot(stats["date_time"],     stats["pc_nodes_linked"],     label="Population",     color="black")
ax.plot(ego_stats["date_time"], ego_stats["pc_nodes_linked"], label="Ego-centric",     color="#3a8bc6")
ax.plot(edge_stats["date_time"],edge_stats["pc_nodes_linked"],label="Edgewise",        color="#e07b3a")
ax.plot(buf_stats["date_time"], buf_stats["pc_nodes_linked"], label="Spatial buffer", color="#7b3ae0")
ax.set_ylabel("pc_nodes_linked")
ax.set_title("share of nodes touched by any edge")

for ax in axes:
    ax.tick_params(axis="x", rotation=30)
fig.tight_layout()
fig.savefig("sampling_compare.png", dpi=120)
plt.close(fig)


# 4. Which strategy best preserves average edgeweight? #######################
#
# We measure preservation as the *maximum absolute deviation* from
# the population time series. Smaller = better preservation.

def max_abs_dev(sample_stats):
    merged = stats[["date_time", "avg_edgeweight"]].merge(
        sample_stats[["date_time", "avg_edgeweight"]],
        on="date_time", suffixes=("_pop", "_samp"))
    return float((merged["avg_edgeweight_pop"]
                  - merged["avg_edgeweight_samp"]).abs().max())

mad = {
    "ego_centric":     max_abs_dev(ego_stats),
    "edgewise":        max_abs_dev(edge_stats),
    "spatial_buffer":  max_abs_dev(buf_stats),
}
print("Max |population - sample| in avg_edgeweight by strategy:")
for k, v in mad.items():
    print(f"  {k:16s}: {v:.3f}")

winner = min(mad, key=mad.get)
print(f"Best preservation: {winner}")


# 5. Learning Check ##########################################################
#
# QUESTION: Of the three sampling strategies above (ego-centric,
# edgewise, spatial buffer around Miami), which one best preserves
# the population's `avg_edgeweight` time series — measured by the
# smallest max-absolute-deviation? Submit the strategy name.

print(f"Learning Check answer: {winner}")
