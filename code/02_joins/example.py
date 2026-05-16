"""Case Study 02 — Network Joins (Python track).

You've worked through the Network Joins lab in the browser. Now let's
run the same idea on real(ish) data: a slim, Bluebikes-flavored
AM-rush-hour-trips edge list (~50,000 rows) and a stations node table
(~500 rows) that's been annotated with a demographic flag from the
census block group each station sits in.

The whole point of this case study: when you have edges and nodes in
two separate tables, the way you JOIN them dictates what you can say
about the network. We'll do a single-node join, then a double-node
join (start *and* end), then aggregate the result to get a quantity of
interest. Pay attention to the *renames* — they are not optional
polish, they are the thing that keeps you from silently shooting
yourself in the foot.
"""

# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `pandas` is the workhorse for joins. `seaborn` + `matplotlib` for the
# heatmap at the end.
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

## 0.2 Load helpers ##########################################################

# Tiny wrappers around pd.read_csv that resolve paths from the repo root.
from functions import load_edges, load_stations

print("\n🚀 Case Study 02 — Network Joins (Python)")
print("   Edges + stations -> single join, then double join, then a quantity of interest.\n")

## 0.3 Load data #############################################################

# Two tables: one for edges (one row per trip aggregate), one for
# nodes (one row per station, with demographic annotation).
edges    = load_edges()
stations = load_stations()

# Get used to running .head() before doing anything else. The columns:
#   start_code: where the trip started (station ID)
#   end_code:   where the trip ended (station ID)
#   day:        the day the trip happened (YYYY-MM-DD)
#   rush:       "am" — we've already filtered to AM rush
#   count:      number of trips matching this start/end/day combination
print(edges.head())

# Stations table columns:
#   code:      station ID (merges to start_code / end_code in edges)
#   cluster:   neighborhood cluster (block group)
#   maj_black: "yes"/"no" — is the station in a majority-Black block group?
#   x, y:      longitude / latitude
print(stations.head())

# How big is each table?
print(len(edges), "edges")
print(len(stations), "stations")
print(f"✅ Loaded {len(edges)} trip rows and {len(stations)} stations.")


# 1. Single-Node Join ########################################################
#
# Goal: tag each edge with a TRAIT of its START station — was it in a
# majority-Black block group or not?

## 1.1 The basic merge #######################################################

# The key insight: the ID variable has a different NAME in each table.
#   - in `edges` it's called `start_code`
#   - in `stations` it's called `code`
# In pandas we say  left_on="start_code", right_on="code"  (or rename
# `code` -> `start_code` first, which is what most pipelines do).
print(
    edges
    .merge(stations, left_on="start_code", right_on="code", how="left")
    .head()
)

# That joined in EVERY column from stations. Usually too much.
# Better: subset stations to just what you need BEFORE joining. Easier
# to read AND saves memory on big joins.
print(
    edges
    .merge(stations[["code", "maj_black"]],
           left_on="start_code", right_on="code", how="left")
    .head()
)

## 1.2 Rename on the way in ##################################################

# After the merge above, `maj_black` is still ambiguous — is it the
# start station's demographic or the end station's? Rename it to
# `start_black` *as part of* the merge. This habit will save you 20
# minutes of "wait, which side was this?" confusion later.

edges_with_start = edges.merge(
    stations[["code", "maj_black"]].rename(
        columns={"code": "start_code", "maj_black": "start_black"}),
    on="start_code", how="left")

print(edges_with_start.head())

## 1.3 A first quantity of interest ##########################################

# Of all AM rush rides in 2021, how many started in a majority-Black
# block group?
print(
    edges_with_start
    .groupby("start_black", dropna=False)["count"]
    .sum()
    .reset_index(name="trips")
)
# Rows where `start_black` is NaN mean the START station wasn't in
# our stations table — i.e. it's outside Boston proper. In the real
# Bluebikes data these are Cambridge / Somerville stations.


# 2. Double-Node Join ########################################################
#
# Now we want to know about BOTH ends of the trip. We do a SECOND merge
# on `end_code`, and we rename again so the two demographics don't
# clobber each other.

## 2.1 Two merges, two renames ###############################################

data = (
    edges
    # join in the START station's trait...
    .merge(stations[["code", "maj_black"]].rename(
        columns={"code": "start_code", "maj_black": "start_black"}),
        on="start_code", how="left")
    # ...then join in the END station's trait.
    .merge(stations[["code", "maj_black"]].rename(
        columns={"code": "end_code",   "maj_black": "end_black"}),
        on="end_code", how="left")
    # Drop rows where either side is NaN — these are stations not in
    # our stations table (out-of-area).
    .dropna(subset=["start_black", "end_black"])
    .reset_index(drop=True)
)

print(data.head())
print(f"✅ After double-join + NaN drop: {len(data)} rows.")

## 2.2 An aggregate quantity of interest #####################################

# How many trips happened between EACH of the four demographic
# combinations (yes->yes, yes->no, no->yes, no->no)?
stat = (
    data
    .groupby(["start_black", "end_black"], dropna=False)["count"]
    .sum()
    .reset_index(name="trips")
)
total = stat["trips"].sum()
stat["total"]   = total
stat["percent"] = (100 * stat["trips"] / total).round(1)

print(stat)
print(f"📊 Total trips across all four cells: {int(stat['trips'].sum())}")


# 3. A quick visual ##########################################################
#
# A 2x2 heatmap of trips by start-demographic x end-demographic. This
# is the simplest possible "network communication" visualization, and
# it's often the most honest one.

pivot = stat.pivot(index="end_black", columns="start_black", values="percent")

fig, ax = plt.subplots(figsize=(5.2, 4.5))
sns.heatmap(pivot, annot=True, fmt=".1f", cmap="mako",
            cbar_kws={"label": "% of trips"}, ax=ax)
ax.set_xlabel("Starting station\nin majority-Black block group?")
ax.set_ylabel("Ending station\nin majority-Black block group?")
ax.set_title("AM rush 2021 — slim Bluebikes-flavored sample", loc="left")
fig.tight_layout()
fig.savefig("joins_heatmap.png", dpi=120)
plt.close(fig)
print("💾 Saved joins_heatmap.png")


# 4. Why renames matter (the silent-bug demo) ################################
#
# To drive the point home: try the same double-merge WITHOUT renaming
# `maj_black`. What does pandas do? It auto-suffixes them as `_x` and
# `_y`, which (a) is ugly, and (b) means you can't tell at a glance
# which side is which.

bad = (
    edges
    .merge(stations[["code", "maj_black"]],
           left_on="start_code", right_on="code", how="left")
    .merge(stations[["code", "maj_black"]],
           left_on="end_code", right_on="code", how="left")
)
print(bad.head())
# Notice `maj_black_x` and `maj_black_y`. You can survive this, but
# in any non-trivial pipeline it's a recipe for misreading your own
# code in two weeks. Rename on the way in.


# 5. Learning Check ##########################################################
#
# QUESTION: Of AM rush rides in 2021 in this slim dataset, how many
# trips started in a majority-Black block group AND ended in a
# majority-Black block group?
#
# HINT: you've already computed `stat` above. Find the row where
# start_black == "yes" and end_black == "yes" and read off `trips`.

answer = int(
    stat.loc[(stat["start_black"] == "yes") &
             (stat["end_black"]   == "yes"), "trips"].iloc[0]
)

print(f"\n📝 Learning Check answer: {answer}")

# Reminder: this is a synthetic-but-deterministic dataset. Your answer
# should be the SAME as your classmates'. If it isn't, your random
# seed has drifted somewhere.

print("\n🎉 Done. Move on to the case study report when you're ready.")
