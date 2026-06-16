"""Case Study 04 — Centrality & Criticality (Python track).

The case study lab let you click nodes and watch the network
fragment. The point: high-degree nodes ("hubs") are obvious. The
nodes that actually matter for keeping the network connected —
*bridges* — are often invisible at a glance, because they have *low*
degree but *high* betweenness.

This script makes that idea concrete. We have a synthetic 500-node
transit network with planted bridges. We'll compute four centrality
measures (degree, betweenness, closeness, eigenvector), rank-compare
them, and find the bridges hiding in plain sight.
"""

# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `igraph` does the centrality math. `pandas` for the tidy per-node
# results so we can rank-compare them. `matplotlib` for the figure.
import pandas as pd
import numpy as np
import igraph as ig
import matplotlib.pyplot as plt

## 0.2 Load helpers ##########################################################

# `build_graph()` reads the nodes + edges CSVs and returns an undirected,
# weighted igraph graph. Open functions.py if you want to see the seam.
from functions import load_nodes, load_edges, build_graph

print("\n🚀 Case Study 04 — Centrality & Criticality (Python)")
print("   Four centrality measures, ranked. Find the bridges hiding in plain sight.\n")

## 0.3 Load data #############################################################

nodes = load_nodes()
edges = load_edges()
print(nodes.head())
print(edges.head())

g = build_graph(nodes, edges)
print(g.summary())
print(f"✅ Loaded graph: {g.vcount()} vertices, {g.ecount()} edges.")


# 1. Four centrality measures ################################################
#
# "Most central" is meaningless on its own -- central BY WHICH MEASURE,
# FOR WHICH QUESTION? Reach for:
#   - DEGREE: how many neighbors. Local. "Who is busiest right now?"
#   - BETWEENNESS: how often this node sits on a shortest path between
#     others. Global. "Who is a chokepoint / bridge whose loss splits the
#     network?" This is the one that finds load-bearing nodes.
#   - CLOSENESS: 1 / mean distance to everyone. "Who can reach the whole
#     network fastest?" (good for response / diffusion questions).
#   - EIGENVECTOR: a node is central if its neighbors are central
#     (recursive). "Who sits in the well-connected core?" Prefer it over
#     betweenness when you care about being embedded among important
#     nodes, not about controlling the flow between them.

# All four computed in one tidy table, so we can compare them directly.
# Betweenness is the slow one: it needs all-pairs shortest paths, so on
# 500 nodes expect this to take ~30-60s. It has NOT hung.
#
# +-------------------------------------------------------------------------+
# | /!\ WEIGHT DIRECTION -- THE #1 SILENT BUG IN WEIGHTED CENTRALITY         |
# |                                                                         |
# | igraph reads `weights` as DISTANCE: a higher weight means a LONGER,     |
# | harder-to-traverse edge. Our `weight` here is already a distance-like   |
# | cost, so passing it raw is correct.                                     |
# |                                                                         |
# | If YOUR weight is a STRENGTH (ridership, messages, volume -- higher =   |
# | "closer"), pass 1/weight instead, the way case 09 builds                |
# | cost = 1/ridership. Passing strength as-is RUNS WITHOUT ERROR and       |
# | silently computes the wrong thing -- check this before you trust a      |
# | weighted betweenness ranking.                                           |
# +-------------------------------------------------------------------------+
print("🧪 Computing four centralities on 500 nodes (betweenness ~30-60s)...")
cent = pd.DataFrame({
    "node_id":      g.vs["name"],
    "kind":         g.vs["kind"],
    "degree":       g.degree(),
    "betweenness":  g.betweenness(weights="weight"),
    "closeness":    g.closeness(weights="weight"),
    "eigenvector":  g.eigenvector_centrality(weights="weight"),
})

print(cent.head())


# 2. Rank-compare ############################################################
#
# Different measures rank the SAME node differently. The Spearman
# correlation between two centrality vectors tells you how much they
# agree on the *order* of nodes (not their magnitudes). The printed
# matrix is symmetric, with rows and columns in the SAME order (degree,
# betweenness, closeness, eigenvector) -- read cell (i, j) as "how much
# measures i and j agree on the ranking."

corr = cent[["degree", "betweenness", "closeness", "eigenvector"]].corr(method="spearman")
print(corr.round(3))
print(f"📊 Degree vs betweenness Spearman: {corr.loc['degree', 'betweenness']:.3f}")


# 3. Bridges hiding in plain sight ###########################################
#
# We want nodes that are HIGH BETWEENNESS but LOW DEGREE. To compare
# them on an equal footing, we rank each metric (1 = highest) and
# compute the GAP: betweenness rank minus degree rank. Big positive
# gap = "matters more for connectivity than its degree would suggest."
#
# In our synthetic data we planted some "bridge" nodes — let's see if
# this gap statistic recovers them.

cent["deg_rank"]  = cent["degree"].rank(ascending=False)
cent["btwn_rank"] = cent["betweenness"].rank(ascending=False)
cent["gap"] = cent["deg_rank"] - cent["btwn_rank"]

bridges = cent.sort_values("gap", ascending=False).head(10)
print(bridges)
# Notice how many of the top-gap nodes are tagged kind == "bridge"
# in our synthetic data. That's not a coincidence.
print(f"📝 #1 hidden bridge: {bridges.iloc[0]['node_id']} (gap = {bridges.iloc[0]['gap']:.0f})")


# 4. Visualize: size by betweenness ##########################################

fig, ax = plt.subplots(figsize=(10, 8))
layout = g.layout_fruchterman_reingold(weights="weight", niter=200)
xs = [p[0] for p in layout.coords]
ys = [p[1] for p in layout.coords]
# scale node size with betweenness
btwn = np.array(cent["betweenness"])
sizes = 6 + 90 * (btwn / btwn.max()) if btwn.max() > 0 else np.full_like(btwn, 6)
colors = ["#d62728" if k == "bridge" else "#1f77b4" for k in g.vs["kind"]]
for e in g.es:
    x0, y0 = layout.coords[e.source]
    x1, y1 = layout.coords[e.target]
    ax.plot([x0, x1], [y0, y1], color="grey", alpha=0.10, linewidth=0.3)
ax.scatter(xs, ys, c=colors, s=sizes, edgecolors="white", linewidths=0.3)
ax.set_axis_off()
ax.set_title("Node size = betweenness. Red = planted bridges.")
fig.tight_layout()
fig.savefig("centrality_bridges.png", dpi=120)
plt.close(fig)
print("💾 Saved centrality_bridges.png")


# 5. Simulate: remove the top-5 by each metric ###############################
#
# To confirm betweenness picks the *load-bearing* nodes, remove the
# top-5 nodes by each metric and see what happens to the size of the
# largest connected component. The metric whose top-5 removal
# fragments the network MOST is the one most attuned to network
# criticality.

def lcc_size(g_in):
    return max(len(c) for c in g_in.connected_components())

original_lcc = lcc_size(g)
print(f"\n🧪 Original largest component: {original_lcc}")

for metric in ["degree", "betweenness", "closeness", "eigenvector"]:
    top5 = cent.sort_values(metric, ascending=False).head(5)["node_id"].tolist()
    g_test = g.copy()
    g_test.delete_vertices([v.index for v in g_test.vs if v["name"] in top5])
    print(f"   remove top-5 by {metric:12s} -> LCC = {lcc_size(g_test)}")


# 6. Learning Check ##########################################################
#
# QUESTION: List the 5 nodes whose betweenness-rank minus degree-rank
# gap is largest (the "bridges hiding in plain sight"). What is the
# node_id of the #1 entry?

answer = bridges.iloc[0]["node_id"]

print(f"\n📝 Learning Check answer: {answer}")

print("\n🎉 Done. Move on to the case study report when you're ready.")
