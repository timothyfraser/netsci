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

library(dplyr)
library(tibble)
library(igraph)
library(ggplot2)
library(here)

## 0.2 Load helpers ##########################################################

source(here::here("code", "04_centrality", "functions.R"))

## 0.3 Load data #############################################################

nodes <- load_nodes()
edges <- load_edges()
g     <- build_graph(nodes, edges)

g
# ~500 vertices, ~1000 edges, undirected, weight on each edge.


# 1. Four centrality measures ################################################
#
# Each one captures a different intuition for "important".
#   - DEGREE: how many neighbors. Local. Hub-detection.
#   - BETWEENNESS: how often this node lies on a shortest path
#     between two other nodes. Global. Bridge-detection.
#   - CLOSENESS: 1 / mean distance to every other node. Reach.
#   - EIGENVECTOR: central if your neighbors are central. Influence.

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

cent |>
  select(degree, betweenness, closeness, eigenvector) |>
  as.matrix() |>
  cor(method = "spearman") |>
  round(3)


# 3. Bridges hiding in plain sight ###########################################
#
# We want nodes that are HIGH BETWEENNESS but LOW DEGREE. Rank each
# metric (1 = highest), then compute the GAP: betweenness rank minus
# degree rank. Big positive gap = "matters more for connectivity
# than its degree would suggest."

cent <- cent |>
  mutate(
    deg_rank  = rank(-degree),
    btwn_rank = rank(-betweenness),
    gap       = deg_rank - btwn_rank
  )

bridges <- cent |>
  arrange(desc(gap)) |>
  head(10)

bridges


# 4. Visualize: size by betweenness ##########################################

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

lcc_size <- function(g_in) {
  cs <- igraph::components(g_in)$csize
  if (length(cs) == 0) 0L else max(cs)
}

cat("Original largest component:", lcc_size(g), "\n")

for (metric in c("degree", "betweenness", "closeness", "eigenvector")) {
  top5 <- cent |>
    arrange(desc(.data[[metric]])) |>
    head(5) |>
    pull(node_id)
  g_test <- igraph::delete_vertices(g, top5)
  cat(sprintf("  remove top-5 by %-12s -> LCC = %d\n",
              metric, lcc_size(g_test)))
}


# 6. Learning Check ##########################################################
#
# QUESTION: List the 5 nodes whose betweenness-rank minus degree-rank
# gap is largest. What is the node_id of the #1 entry?

answer <- bridges |> slice(1) |> pull(node_id)
answer
