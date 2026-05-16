#' @name example.R
#' @title Case Study 06 — DSM Clustering
#' @author <your-name-here>
#' @description
#' A Design Structure Matrix (DSM) is just an adjacency matrix where
#' row i to column j means "component i depends on j." Reordering
#' rows and columns so that dense blocks fall on the diagonal reveals
#' the *modular structure* of the system. The case study lab had you
#' drag rows around by hand; here we let an algorithm do it.
#'
#' Steps:
#'   1. Build the DSM graph from a 200-component synthetic system
#'      with 8 planted modules.
#'   2. Run two community-detection algorithms (Louvain and
#'      fast-greedy) on the undirected projection.
#'   3. Reorder the DSM matrix by recovered modules and verify the
#'      block-diagonal structure visually.
#'   4. Simulate a k-hop cascade from a chosen component.


# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `igraph` carries the community-detection algorithms and the matrix
# conversion. `dplyr` + `tibble` for tidy summaries. Base R `image()`
# does the DSM heatmap (no ggplot needed).
library(dplyr)
library(tibble)
library(igraph)
library(ggplot2)
library(here)

## 0.2 Load helpers ##########################################################

# `cascade_bfs()` does a bounded BFS from a starting node along the
# directed dependency edges. It's the cascade simulator we use at the
# end of the script.
source(here::here("code", "06_dsm-clustering", "functions.R"))

cat("\n🚀 Case Study 06 — DSM Clustering (R)\n")
cat("   200 components, 8 planted modules. Can community detection recover them?\n\n")

## 0.3 Load data #############################################################

nodes <- load_nodes()
edges <- load_edges()
g     <- build_graph(nodes, edges)
g
cat(sprintf("✅ Loaded DSM: %d components, %d dependency edges.\n",
            igraph::vcount(g), igraph::ecount(g)))


# 1. Community detection #####################################################
#
# Louvain and fast-greedy both want an undirected graph. We make an
# undirected copy whose edges mean "i and j depend on each other,
# in either direction." Standard DSM preprocessing.

g_undirected <- igraph::as.undirected(g, mode = "collapse")
g_undirected

# Louvain (igraph's `cluster_louvain`): greedy modularity optimization,
# moves nodes between communities to maximize modularity score.
louvain <- igraph::cluster_louvain(g_undirected)
cat(sprintf("📊 Louvain found %d modules. Modularity: %.3f\n",
            length(louvain), igraph::modularity(louvain)))

# Fast-greedy: agglomerative — start with each node in its own community,
# repeatedly merge the pair whose merge most increases modularity.
fg <- igraph::cluster_fast_greedy(g_undirected)
cat(sprintf("📊 Fast-greedy found %d modules. Modularity: %.3f\n",
            length(fg), igraph::modularity(fg)))


# 2. Compare to ground truth #################################################
#
# Our synthetic data planted 8 modules. The Adjusted Rand Index (ARI)
# measures how well two clusterings agree, corrected for chance:
# 1.0 = perfect agreement, 0.0 = chance, < 0 = worse than chance.

true_mod <- igraph::V(g)$true_module
ari_louv <- igraph::compare(true_mod, louvain$membership, method = "adjusted.rand")
ari_fg   <- igraph::compare(true_mod, fg$membership,     method = "adjusted.rand")
cat(sprintf("🧪 Louvain    ARI vs truth: %.3f\n", ari_louv))
cat(sprintf("🧪 FastGreedy ARI vs truth: %.3f\n", ari_fg))


# 3. Reorder the DSM by recovered module #####################################
#
# Sort node indices by Louvain module ID. Then build the n x n
# adjacency matrix in that order. Dense blocks should land on the
# diagonal — that's what "modular structure" *looks like*.

ord      <- order(louvain$membership)
A        <- as.matrix(igraph::as_adjacency_matrix(g))
A_sorted <- A[ord, ord]

# Side-by-side base-R image() plots. Reverse the y-axis so row 1 lands
# at the top, like an actual matrix.
par(mfrow = c(1, 2))
image(t(A)[, nrow(A):1], col = c("white", "black"), axes = FALSE,
      main = "DSM — original order")
image(t(A_sorted)[, nrow(A_sorted):1], col = c("white", "black"), axes = FALSE,
      main = "DSM — reordered by Louvain")
par(mfrow = c(1, 1))


# 4. Cascade simulation ######################################################
#
# When component C037 fails, every component that depends on it can
# fail too. We bound to k hops because in a densely-coupled DSM an
# unbounded cascade reaches everything. The interesting question:
# how many fall in the FIRST FEW HOPS?

seed <- "C037"
for (k in c(1, 2, 3)) {
  cat(sprintf("🔗 Cascade from %s in %d hop(s): %d components\n",
              seed, k, length(cascade_bfs(g, seed, n_hops = k))))
}


# 5. Learning Check ##########################################################
#
# QUESTION: How many modules does Louvain find in this DSM, and what
# is the modularity score (to 3 decimal places)? Submit BOTH numbers,
# separated by a comma. Example: "8, 0.612"

n_modules  <- length(louvain)
modularity <- round(igraph::modularity(louvain), 3)

cat(sprintf("\n📝 Learning Check answer: %d, %.3f\n", n_modules, modularity))

cat("\n🎉 Done. Move on to the case study report when you're ready.\n")
