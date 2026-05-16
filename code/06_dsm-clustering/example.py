"""Case Study 06 — DSM Clustering (Python track).

A Design Structure Matrix (DSM) is just an adjacency matrix where row
i to column j means "component i depends on j." Reordering rows and
columns so that dense blocks fall on the diagonal reveals the *modular
structure* of the system. The case study lab had you drag rows around
by hand; here we let an algorithm do it.

Steps:
  1. Build the DSM graph from a 200-component synthetic system with
     8 planted modules.
  2. Run two community-detection algorithms (Louvain and fast-greedy)
     on the undirected projection.
  3. Reorder the DSM matrix by recovered modules and verify the
     block-diagonal structure visually.
  4. Simulate a cascade: which components fail when component C037
     fails (BFS along outgoing dependency edges).
"""

# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `igraph` for community detection + matrix conversion. `numpy` for
# matrix reordering. `matplotlib.imshow` for the DSM heatmap.
import pandas as pd
import numpy as np
import igraph as ig
import matplotlib.pyplot as plt

## 0.2 Load helpers ##########################################################

# `cascade_bfs()` does a bounded BFS from a starting node along the
# directed dependency edges. It's the cascade simulator we use at the
# end of the script.
from functions import load_nodes, load_edges, build_graph, cascade_bfs

print("\n🚀 Case Study 06 — DSM Clustering (Python)")
print("   200 components, 8 planted modules. Can community detection recover them?\n")

## 0.3 Load data #############################################################

nodes = load_nodes()
edges = load_edges()
g     = build_graph(nodes, edges)
print(g.summary())
print(f"✅ Loaded DSM: {g.vcount()} components, {g.ecount()} dependency edges.")


# 1. Community detection #####################################################
#
# Louvain and fast-greedy both want an undirected graph. We make an
# undirected copy whose edges represent "i and j depend on each other,
# in either direction." This is the standard DSM preprocessing.

g_undirected = g.as_undirected(mode="collapse")
print(g_undirected.summary())

# Louvain (igraph's `community_multilevel`): greedy modularity
# optimization, moves nodes between communities to maximize modularity.
louvain = g_undirected.community_multilevel()
print(f"📊 Louvain found {len(louvain)} modules. Modularity: {louvain.modularity:.3f}")

# Fast-greedy: agglomerative — start with each node in its own community,
# repeatedly merge the pair whose merge most increases modularity.
fg = g_undirected.community_fastgreedy().as_clustering()
print(f"📊 Fast-greedy found {len(fg)} modules. Modularity: {fg.modularity:.3f}")


# 2. Compare to ground truth #################################################
#
# Our synthetic data planted 8 modules. The Adjusted Rand Index (ARI)
# measures how well two clusterings agree, corrected for chance:
# 1.0 = perfect agreement, 0.0 = chance, < 0 = worse than chance.

from sklearn.metrics import adjusted_rand_score
true_module = np.array(g.vs["true_module"])
louvain_lbl = np.array(louvain.membership)
fg_lbl      = np.array(fg.membership)

print(f"🧪 Louvain    ARI vs truth: {adjusted_rand_score(true_module, louvain_lbl):.3f}")
print(f"🧪 FastGreedy ARI vs truth: {adjusted_rand_score(true_module, fg_lbl):.3f}")


# 3. Reorder the DSM by recovered module #####################################
#
# Sort node indices by Louvain module ID. Then build the n x n
# adjacency matrix in that order. Dense blocks should land on the
# diagonal — that's what "modular structure" *looks like*.

order = np.argsort(louvain_lbl, kind="stable")
A = np.array(g.get_adjacency().data)
A_sorted = A[np.ix_(order, order)]

# Side-by-side imshow plots: original ordering vs reordered.
fig, axes = plt.subplots(1, 2, figsize=(10, 5))
axes[0].imshow(A, cmap="Greys", aspect="equal")
axes[0].set_title("DSM — original order")
axes[1].imshow(A_sorted, cmap="Greys", aspect="equal")
axes[1].set_title("DSM — reordered by Louvain module")
for ax in axes:
    ax.set_xticks([]); ax.set_yticks([])
fig.tight_layout()
fig.savefig("dsm_reorder.png", dpi=120)
plt.close(fig)
print("💾 Saved dsm_reorder.png")


# 4. Cascade simulation ######################################################
#
# When component C037 fails, every component that depends on it can
# fail too. We bound to k hops because in a densely-coupled DSM an
# unbounded cascade reaches everything. The interesting question:
# how many components fall in the FIRST FEW HOPS?

seed = "C037"
for k in [1, 2, 3]:
    failed = cascade_bfs(g, seed, n_hops=k)
    print(f"🔗 Cascade from {seed} in {k} hop(s): {len(failed)} components")


# 5. Learning Check ##########################################################
#
# QUESTION: How many modules does Louvain find in this DSM, and what
# is the modularity score (to 3 decimal places)?
# Submit BOTH numbers, separated by a comma.
# Example answer format: "8, 0.612"

n_modules = len(louvain)
modularity = round(louvain.modularity, 3)

print(f"\n📝 Learning Check answer: {n_modules}, {modularity:.3f}")

print("\n🎉 Done. Move on to the case study report when you're ready.")
