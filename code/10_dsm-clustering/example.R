#' @name example.R
#' @title Case Study 10 — DSM Clustering
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
source(here::here("code", "10_dsm-clustering", "functions.R"))

cat("\n🚀 Case Study 10 — DSM Clustering (R)\n")
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
# Louvain and fast-greedy both want an undirected graph, so we collapse
# each directed dependency "A depends on B" into a plain "A and B are
# linked." Why it's OK here: community detection asks "which components
# clump together?", and two parts that depend on each other belong in the
# same cluster regardless of which way the arrow points. What we give up:
# the direction itself -- we can no longer tell driver from dependent
# within a cluster. Fine for grouping; keep direction if you cared about
# what cascades when one part fails.

g_undirected <- igraph::as_undirected(g, mode = "collapse")
g_undirected

# A quick word on MODULARITY, the score both algorithms maximize: it
# measures how much more edge weight falls inside communities than you'd
# expect at random. It runs roughly -0.5 to 1; ~0 means "no more clustered
# than random", and > ~0.3 is usually a meaningful community structure.
# We planted 8 modules, so recovering 8 at a healthy modularity is the win.

# Louvain (igraph's `cluster_louvain`): greedy modularity optimization,
# moves nodes between communities to maximize modularity score.
#
# Louvain is STOCHASTIC -- it visits nodes in a randomized order, so an
# unseeded run usually recovers the 8 planted modules (modularity 0.470)
# but occasionally merges two and reports 7 (~0.454). We seed for a
# reproducible Learning Check; expect your own data to wobble by a module
# or two between runs if you don't.
set.seed(5470)
louvain <- igraph::cluster_louvain(g_undirected)
cat(sprintf("📊 Louvain found %d modules. Modularity: %.3f\n",
            length(louvain), igraph::modularity(louvain)))

# Fast-greedy: agglomerative — start with each node in its own community,
# repeatedly merge the pair whose merge most increases modularity. It often
# recovers FEWER modules than Louvain on dense graphs: once it has merged
# greedily it never splits back, so adjacent planted modules get fused into
# one and the recovered count comes in under the truth. That's an algorithm
# property, not randomness — Louvain's node-moving phase avoids it here.
fg <- igraph::cluster_fast_greedy(g_undirected)
cat(sprintf("📊 Fast-greedy found %d modules. Modularity: %.3f\n",
            length(fg), igraph::modularity(fg)))


# 2. Compare to ground truth #################################################
#
# Our synthetic data planted 8 modules. The Adjusted Rand Index (ARI)
# measures how well two clusterings agree, corrected for chance:
# 1.0 = perfect agreement, 0.0 = chance, < 0 = worse than chance.
# Rough field convention for "how good is this recovery?": ARI > 0.8 is a
# strong match, 0.5–0.8 partial, < 0.5 weak. So Louvain's 1.0 is a perfect
# recovery; fast-greedy's lower score reflects the merged modules above.

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
# at the top, like an actual matrix. Wrapped in a function so we can draw
# it both to the screen and to a PNG (Rscript otherwise hides it in
# Rplots.pdf).
draw_dsm <- function() {
  par(mfrow = c(1, 2))
  image(t(A)[, nrow(A):1], col = c("white", "black"), axes = FALSE,
        main = "DSM — original order")
  image(t(A_sorted)[, nrow(A_sorted):1], col = c("white", "black"), axes = FALSE,
        main = "DSM — reordered by Louvain")
  par(mfrow = c(1, 1))
}

# Show interactively...
draw_dsm()

# ...and save a copy for terminal / Rscript users.
png(here::here("code", "10_dsm-clustering", "dsm_reordering.png"),
    width = 9, height = 5, units = "in", res = 120)
draw_dsm()
invisible(dev.off())
cat("💾 Saved dsm_reordering.png\n")


# 4. Cascade simulation ######################################################
#
# When component C037 fails, every component that depends on it can
# fail too. We bound to k hops because in a densely-coupled DSM an
# unbounded cascade reaches everything. The interesting question:
# how many fall in the FIRST FEW HOPS?
#
# Why can a cascade reach far beyond C037's own module even though Louvain
# found clean modules? Because a cascade follows EDGES, not module walls.
# Community detection only says edges are DENSER within modules, not that
# none cross. C037 has a few cross-module dependency edges, and BFS happily
# traverses them -- so a single hub failure jumps boundaries the clustering
# drew.

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
