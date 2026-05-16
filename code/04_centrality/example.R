#' @name example.R
#' @title Case Study 04 — Centrality & Criticality
#' @author <your-name-here>
#' @description
#' The case study lab let you click nodes and watch the network
#' fragment. The point: high-degree nodes ("hubs") are obvious. The
#' nodes that actually matter for keeping the network connected —
#' *bridges* — are often invisible at a glance, because they have low
#' degree but high betweenness.
#'
#' This script makes that idea concrete. We have a synthetic 500-node
#' transit network with planted bridges. We compute four centrality
#' measures, rank-compare them, and find the bridges hiding in plain
#' sight.


# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `igraph` does the centrality math. `dplyr` + `tibble` keep the
# per-node results tidy so we can rank-compare them easily.
library(dplyr)
library(tibble)
library(igraph)
library(ggplot2)
library(here)

## 0.2 Load helpers ##########################################################

# `build_graph()` reads the nodes + edges CSVs and returns an undirected,
# weighted igraph graph. Open functions.R if you want to see the seam.
source(here::here("code", "04_centrality", "functions.R"))

cat("\n🚀 Case Study 04 — Centrality & Criticality (R)\n")
cat("   Four centrality measures, ranked. Find the bridges hiding in plain sight.\n\n")

## 0.3 Load data #############################################################

nodes <- load_nodes()
edges <- load_edges()
g     <- build_graph(nodes, edges)

# Inspecting the graph: ~500 vertices, ~1000 edges, undirected, with a
# weight attribute on every edge.
g
cat(sprintf("✅ Loaded graph: %d vertices, %d edges.\n",
            igraph::vcount(g), igraph::ecount(g)))


# 1. Four centrality measures ################################################
#
# Each one captures a DIFFERENT intuition for "important":
#   - DEGREE: how many neighbors. Local. Hub-detection.
#   - BETWEENNESS: how often this node lies on a shortest path between
#     two other nodes. Global. Bridge-detection.
#   - CLOSENESS: 1 / mean distance to every other node. Reach.
#   - EIGENVECTOR: central if your neighbors are central. Influence.

# All four computed in one tidy table, so we can compare them directly.
cent <- tibble(
  node_id     = igraph::V(g)$name,
  kind        = igraph::V(g)$kind,
  degree      = igraph::degree(g),
  betweenness = igraph::betweenness(g, weights = igraph::E(g)$weight),
  closeness   = igraph::closeness(g,   weights = igraph::E(g)$weight),
  eigenvector = igraph::eigen_centrality(g, weights = igraph::E(g)$weight)$vector
)

cent |> head()


# 2. Rank-compare ############################################################
#
# Different measures rank the SAME node differently. The Spearman
# correlation between two centrality vectors tells you how much the
# two measures agree on the *order* of nodes (not their magnitudes).

corr_mat <- cent |>
  select(degree, betweenness, closeness, eigenvector) |>
  as.matrix() |>
  cor(method = "spearman") |>
  round(3)
print(corr_mat)
cat(sprintf("📊 Degree vs betweenness Spearman: %.3f\n",
            corr_mat["degree", "betweenness"]))


# 3. Bridges hiding in plain sight ###########################################
#
# We want nodes that are HIGH BETWEENNESS but LOW DEGREE. Rank each
# metric (1 = highest), then compute the GAP: betweenness rank minus
# degree rank. Big positive gap = "matters more for connectivity
# than its degree would suggest."
#
# In our synthetic data we planted some "bridge" nodes — let's see if
# this gap statistic recovers them.

cent <- cent |>
  mutate(
    deg_rank  = rank(-degree),
    btwn_rank = rank(-betweenness),
    gap       = deg_rank - btwn_rank
  )

bridges <- cent |>
  arrange(desc(gap)) |>
  head(10)
print(bridges)
cat(sprintf("📝 #1 hidden bridge: %s (gap = %.0f)\n",
            bridges$node_id[1], bridges$gap[1]))


# 4. Visualize: size by betweenness ##########################################

# Attach the betweenness value AND a color flag back onto the graph,
# so the plotting call below is just one igraph::plot().
V(g)$btwn <- cent$betweenness
V(g)$col  <- ifelse(V(g)$kind == "bridge", "#d62728", "#1f77b4")

plot(
  g,
  layout       = igraph::layout_with_fr(g, weights = E(g)$weight, niter = 200),
  vertex.size  = 1 + 8 * (V(g)$btwn / max(V(g)$btwn)),
  vertex.color = V(g)$col,
  vertex.label = NA,
  edge.color   = adjustcolor("grey50", alpha.f = 0.2),
  edge.width   = 0.4,
  main         = "Node size = betweenness. Red = planted bridges."
)


# 5. Simulate: remove the top-5 by each metric ###############################
#
# To confirm betweenness picks the *load-bearing* nodes, remove the
# top-5 by each metric and see what happens to the size of the largest
# connected component. The metric whose top-5 removal fragments the
# network MOST is the one most attuned to network criticality.

lcc_size <- function(g_in) {
  cs <- igraph::components(g_in)$csize
  if (length(cs) == 0) 0L else max(cs)
}

cat(sprintf("\n🧪 Original largest component: %d\n", lcc_size(g)))

for (metric in c("degree", "betweenness", "closeness", "eigenvector")) {
  top5 <- cent |>
    arrange(desc(.data[[metric]])) |>
    head(5) |>
    pull(node_id)
  g_test <- igraph::delete_vertices(g, top5)
  cat(sprintf("   remove top-5 by %-12s -> LCC = %d\n",
              metric, lcc_size(g_test)))
}


# 6. Learning Check ##########################################################
#
# QUESTION: List the 5 nodes whose betweenness-rank minus degree-rank
# gap is largest. What is the node_id of the #1 entry?

answer <- bridges |> slice(1) |> pull(node_id)

cat(sprintf("\n📝 Learning Check answer: %s\n", answer))

cat("\n🎉 Done. Move on to the case study report when you're ready.\n")
