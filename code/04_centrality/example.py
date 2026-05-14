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

import pandas as pd
import numpy as np
import igraph as ig
import matplotlib.pyplot as plt

## 0.2 Load helpers ##########################################################

from functions import load_nodes, load_edges, build_graph

## 0.3 Load data #############################################################

nodes = load_nodes()
edges = load_edges()
print(nodes.head())
print(edges.head())

g = build_graph(nodes, edges)
print(g.summary())
# ~500 vertices, ~1000 edges, undirected, weight on each edge.


# 1. Four centrality measures ################################################
#
# Each one captures a different intuition for "important".
#   - DEGREE: how many neighbors. Local. Hub-detection.
#   - BETWEENNESS: how often this node lies on a shortest path
#     between two other nodes. Global. Bridge-detection.
#   - CLOSENESS: 1 / mean distance to every other node. Global.
#     Reach.
#   - EIGENVECTOR: a node is central if its neighbors are central.
#     Recursive. Influence.

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
# agree.

corr = cent[["degree", "betweenness", "closeness", "eigenvector"]].corr(method="spearman")
print(corr.round(3))


# 3. Bridges hiding in plain sight ###########################################
#
# We want nodes that are HIGH BETWEENNESS but LOW DEGREE. To compare
# them on an equal footing, we rank each metric (1 = highest) and
# compute the GAP: betweenness rank minus degree rank. Big positive
# gap = "matters more for connectivity than its degree would suggest."

cent["deg_rank"]  = cent["degree"].rank(ascending=False)
cent["btwn_rank"] = cent["betweenness"].rank(ascending=False)
cent["gap"] = cent["deg_rank"] - cent["btwn_rank"]
# (positive gap = better betweenness rank than degree rank)

bridges = cent.sort_values("gap", ascending=False).head(10)
print(bridges)
# Notice how many of the top-gap nodes are tagged kind == "bridge"
# in our synthetic data. That's not a coincidence.


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


# 5. Simulate: remove the top-5 by each metric ###############################
#
# To confirm betweenness picks the *load-bearing* nodes, remove the
# top-5 nodes by each metric and see what happens to the size of the
# largest connected component.

def lcc_size(g_in):
    return max(len(c) for c in g_in.connected_components())

original_lcc = lcc_size(g)
print("Original largest component:", original_lcc)

for metric in ["degree", "betweenness", "closeness", "eigenvector"]:
    top5 = cent.sort_values(metric, ascending=False).head(5)["node_id"].tolist()
    g_test = g.copy()
    g_test.delete_vertices([v.index for v in g_test.vs if v["name"] in top5])
    print(f"  remove top-5 by {metric:12s} -> LCC = {lcc_size(g_test)}")


# 6. Learning Check ##########################################################
#
# QUESTION: List the 5 nodes whose betweenness-rank minus degree-rank
# gap is largest (the "bridges hiding in plain sight"). What is the
# node_id of the #1 entry?

answer = bridges.iloc[0]["node_id"]
print("Learning Check answer:", answer)
