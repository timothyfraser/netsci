"""Case Study 11 — Sampling Big Networks (Python track).

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

# `pandas`/`numpy` for the per-slice aggregations, `geopandas`/`shapely`
# for the spatial buffer (the only part of this script that needs
# spatial libraries), `matplotlib` for the comparison figure.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point

## 0.2 Load helpers ##########################################################

# `slice_stats()` computes the per-time-slice network statistics
# (edgeweight, share of nodes touched, etc.) for any edge subset.
# That's the workhorse we'll reuse on every sample.
from functions import (
    load_nodes, load_edges, load_subdivisions, slice_stats,
)

print("\n🚀 Case Study 11 — Sampling Big Networks (Python)")
print("   Three sampling strategies vs population. Which one preserves the truth?\n")

## 0.3 Load data #############################################################

nodes = load_nodes()
edges = load_edges()
print(f"nodes: {len(nodes):,}  edges: {len(edges):,}")
print(edges.head())
print(f"✅ Loaded {len(nodes)} nodes, {len(edges)} edges.")


# 1. Baseline (population) statistics over time ##############################
#
# We compute four numbers per 8-hour slice: total edgeweight, share of
# nodes touched, edge ratio, average edgeweight per node. The figure
# at the end compares each sample's time series to this baseline.

n_total = len(nodes)
stats = slice_stats(edges, n_total)
print(stats.head())
print(f"📊 Baseline: {len(stats)} time slices computed.")


# 2. Sampling strategies #####################################################

rng = np.random.default_rng(42)  # deterministic samples across runs

## 2.1 Ego-centric: sample N nodes, keep edges that touch any sampled node ###

# An ego sample is biased toward whatever the seeds are. With random
# seeds, the bias averages out, but small samples are still noisy.
ego_nodes = nodes.sample(n=50, random_state=42)["node"].to_numpy()
ego_edges = edges[edges["from"].isin(ego_nodes) | edges["to"].isin(ego_nodes)]
print(f"ego sample: {len(ego_nodes)} seed nodes, {len(ego_edges):,} edges")
ego_stats = slice_stats(ego_edges, n_total)
print(f"✅ Ego sample: {len(ego_nodes)} seeds, {len(ego_edges)} edges retained.")

## 2.2 Edgewise: sample edges uniformly ######################################

# Uniform random sampling of edges. Preserves the marginal edge-weight
# distribution well but tends to leave nodes with low degree under-sampled.
edge_sample = edges.sample(n=10_000, random_state=42)
edge_stats  = slice_stats(edge_sample, n_total)
print(f"edge sample: {len(edge_sample):,} edges")
print(f"✅ Edge sample: {len(edge_sample)} edges.")

## 2.3 Spatial buffer: keep edges where BOTH endpoints are within 200 km of Miami

# Use Miami as our point of interest (POI). Why the projection dance?
# EPSG:4326 is lat/lon in DEGREES, so a "200 km" buffer in degrees is
# meaningless (a degree is a different distance at the equator vs Maine).
# EPSG:3857 is in METERS, so we project there to draw the 200 km circle,
# then project back to 4326 to match the node coordinates. Non-GIS
# readers: switch to a meter ruler, measure, switch back.
miami_geoid = "1208692158"
miami_row = nodes[nodes["geoid"] == miami_geoid].iloc[0]
poi = gpd.GeoSeries([Point(miami_row["x"], miami_row["y"])], crs="EPSG:4326")
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

# Keep only edges where BOTH endpoints are inside the buffer.
ids_in = set(nodes_in_buf["node"].to_numpy())
buf_edges = edges[edges["from"].isin(ids_in) & edges["to"].isin(ids_in)]
buf_stats = slice_stats(buf_edges, n_total)
print(f"✅ Buffer sample: {len(nodes_in_buf)} nodes within 200 km of Miami, "
      f"{len(buf_edges)} edges.")


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
print("💾 Saved sampling_compare.png")


# 4. Which strategy best preserves average edgeweight? #######################
#
# What makes one sample "better"? It tracks the true population most
# closely. We score that as the *maximum absolute deviation*: over the
# whole time series, the largest gap between the sample's average edge
# weight and the population's. Smaller = better. (Worst-case gap is a
# simple, strict choice; you could instead use mean-squared error or
# correlation if you cared about average rather than worst-case fit.)

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
print(f"📊 Best preservation (smallest max-absolute-deviation): {winner}")

# WHY does the spatial buffer usually win for this network? Evacuation flow
# is spatially structured -- neighboring subdivisions surge together -- so a
# geographic buffer captures a coherent, internally-intact subnetwork whose
# per-node averages track the population. Ego and edgewise sampling slice
# the graph arbitrarily, fragmenting that local structure.


# 5. Learning Check ##########################################################
#
# QUESTION: Of the three sampling strategies above (ego-centric,
# edgewise, spatial buffer around Miami), which one best preserves
# the population's `avg_edgeweight` time series — measured by the
# smallest max-absolute-deviation? Submit the strategy name.

print(f"\n📝 Learning Check answer: {winner}")

print("\n🎉 Done. Move on to the case study report when you're ready.")
