"""Case Study 03 — Aggregation (Python track).

The interactive lab showed you the same network at three resolutions:
raw stations, neighborhood, income quintile. Each resolution tells a
different story. This script does the same thing in code.

The data is a slim mobility-flow dataset:
  - 500 stations, each tagged with a neighborhood (1 of 12)
    and an income quintile (1..4, 4 = wealthiest).
  - 40,000 AM rush 2021 trip rows (start_code, end_code, day, count).

We will:
  1. Enrich the edges with start- and end-side traits.
  2. View the data at three resolutions (raw, neighborhood, quintile).
  3. At each resolution, render the obvious visual.
  4. Land on a single number — what % of trips stay within the
     top income quintile.
"""

# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `pandas` for the grouping pipeline, `seaborn` + `matplotlib` for the
# three figures.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

## 0.2 Load helpers ##########################################################

# `make_enriched()` does the double join from Case 02 in one call so
# we can focus on aggregation here.
from functions import load_edges, load_stations, make_enriched

print("\n🚀 Case Study 03 — Aggregation (Python)")
print("   Same network at three resolutions: station -> neighborhood -> quintile.\n")

## 0.3 Load data #############################################################

edges    = load_edges()
stations = load_stations()
print(edges.head())
print(stations.head())
print(f"✅ Loaded {len(edges)} trip rows and {len(stations)} stations.")


# 1. Enrich edges with both-side traits ######################################
#
# The helper joins each edge with the start-station's traits AND the
# end-station's traits (renaming to start_nbhd / end_nbhd, etc.). This
# is exactly the "double join, with renames" lesson from case 02.

enriched = make_enriched(edges, stations)
print(enriched.head())
print(f"{len(enriched):,} enriched edge rows")
print(f"✅ Built enriched edge table: {len(enriched)} rows.")


# 2. Three resolutions #######################################################

## 2.1 Resolution A — raw station x station ##################################

# Sum trips for each (start, end) station pair. With 500 stations the
# space of possible pairs is 250,000 cells — way too fine to plot as a
# heatmap. The aggregation gives a hairball, useful for nothing but a
# degree histogram.
station_pairs = (
    enriched
    .groupby(["start_code", "end_code"], as_index=False)["count"]
    .sum()
    .rename(columns={"count": "trips"})
    .sort_values("trips", ascending=False)
)
print(f"📊 Resolution A: {len(station_pairs)} station pairs.")
print(station_pairs.head())

## 2.2 Resolution B — neighborhood x neighborhood ############################

# Now sum trips by START neighborhood and END neighborhood. 12 x 12 =
# 144 cells max. Visualizable as a heatmap. This is where structure
# begins to appear (the diagonal is heavier than the off-diagonal).
nbhd_pairs = (
    enriched
    .groupby(["start_nbhd", "end_nbhd"], as_index=False)["count"]
    .sum()
    .rename(columns={"count": "trips"})
)
print(f"📊 Resolution B: {len(nbhd_pairs)} neighborhood pairs.")
print(nbhd_pairs.head())

## 2.3 Resolution C — income quintile x income quintile ######################

# Finally, aggregate to 4 x 4 income-quintile cells and compute a
# percent column so we can read the equity question directly off the
# matrix.
q_pairs = (
    enriched
    .groupby(["start_quintile", "end_quintile"], as_index=False)["count"]
    .sum()
    .rename(columns={"count": "trips"})
)
total = q_pairs["trips"].sum()
q_pairs["percent"] = (100 * q_pairs["trips"] / total).round(2)
print("Resolution C — 4x4 income quintile pairs")
print(q_pairs)
print(f"📊 Resolution C: 4x4 quintile pairs.")


# 3. Visualize each resolution ###############################################

# Resolution A: degree distribution (the only honest view at 500 nodes).
# Each station's "trip volume" = sum of trips out + sum of trips in.
station_totals = (
    pd.concat([
        station_pairs.groupby("start_code")["trips"].sum(),
        station_pairs.groupby("end_code")["trips"].sum(),
    ]).groupby(level=0).sum().reset_index(name="trips")
)
fig, ax = plt.subplots(figsize=(6, 4))
ax.hist(station_totals["trips"], bins=40, color="#3a8bc6")
ax.set_xlabel("trips touching this station (in or out)")
ax.set_ylabel("# stations")
ax.set_title("Resolution A — station-level trip volume")
fig.tight_layout()
fig.savefig("agg_A_station.png", dpi=120)
plt.close(fig)

# Resolution B: neighborhood x neighborhood heatmap
pivot_b = nbhd_pairs.pivot(index="end_nbhd", columns="start_nbhd", values="trips")
fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(pivot_b, cmap="mako", ax=ax)
ax.set_title("Resolution B — neighborhood x neighborhood")
fig.tight_layout()
fig.savefig("agg_B_neighborhood.png", dpi=120)
plt.close(fig)

# Resolution C: 4 x 4 quintile heatmap with percentages drawn on the cells.
pivot_c = q_pairs.pivot(index="end_quintile", columns="start_quintile",
                       values="percent")
fig, ax = plt.subplots(figsize=(5.2, 4.5))
sns.heatmap(pivot_c, annot=True, fmt=".1f", cmap="mako",
            cbar_kws={"label": "% of trips"}, ax=ax)
ax.invert_yaxis()  # so quintile 1 is bottom-left
ax.set_xlabel("Starting station's income quintile")
ax.set_ylabel("Ending station's income quintile")
ax.set_title("Resolution C — trips between income quintiles")
fig.tight_layout()
fig.savefig("agg_C_quintile.png", dpi=120)
plt.close(fig)
print("💾 Saved agg_A_station.png, agg_B_neighborhood.png, agg_C_quintile.png")


# 4. The point ###############################################################
#
# Resolution A is a hairball: ~13,500 station pairs, no obvious
# structure to a heatmap. Resolution B (12x12) shows neighborhood
# stickiness — the diagonal is heavier. Resolution C (4x4) makes the
# *equity* question legible: how much ridership stays in-quintile vs
# crosses quintiles.
#
# Visualization is partly a tool for finding the question. The case
# study calls this "aggregation reveals signal."


# 5. Learning Check ##########################################################
#
# QUESTION: What percentage of all AM rush 2021 trips in this dataset
# stay within the *top* income quintile (Q4 -> Q4)?
#
# HINT: pull from `q_pairs` directly — start_quintile == 4 AND
# end_quintile == 4.

answer = float(
    q_pairs.loc[(q_pairs["start_quintile"] == 4) &
                (q_pairs["end_quintile"]   == 4), "percent"].iloc[0]
)

print(f"\n📝 Learning Check answer (%): {answer:.2f}")

print("\n🎉 Done. Move on to the case study report when you're ready.")
