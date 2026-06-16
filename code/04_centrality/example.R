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
# "Most central" is meaningless on its own -- central BY WHICH MEASURE,
# FOR WHICH QUESTION? Reach for:
#   - DEGREE: how many neighbors. Local. "Who is busiest right now?"
#   - BETWEENNESS: how often this node sits on a shortest path between
#     others. Global. "Who is a chokepoint / bridge whose loss splits the
#     network?" This is the one that finds load-bearing nodes.
#   - CLOSENESS: 1 / mean distance to everyone. "Who can reach the whole
#     network fastest?" (good for response / diffusion questions).
#   - EIGENVECTOR: central if your neighbors are central (recursive).
#     "Who sits in the well-connected core?" Prefer it over betweenness
#     when you care about being embedded among important nodes, not about
#     controlling the flow between them.

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
# | "closer"), pass 1 / weight instead, the way case 09 builds              |
# | cost = 1 / ridership. Passing strength as-is RUNS WITHOUT ERROR and     |
# | silently computes the wrong thing -- check this before you trust a      |
# | weighted betweenness ranking.                                           |
# +-------------------------------------------------------------------------+
cat("🧪 Computing four centralities on 500 nodes (betweenness ~30-60s)...\n")
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
# The printed matrix is symmetric, with rows and columns in the SAME
# order (degree, betweenness, closeness, eigenvector) -- read cell
# (i, j) as "how much measures i and j agree on the ranking."

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
#
# Read the gap as RELATIVE, not absolute: it's a difference of ranks, so
# it only means "this node climbs N places when you rank by betweenness
# instead of degree." A gap of 400 in a 500-node graph is dramatic; the
# same 400 in a 50,000-node graph is mild. Always read it against n.

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

# Wrap the plot so we can both show it interactively AND save a copy to PNG
# (Rscript otherwise sends it to Rplots.pdf). Fix the layout once so the
# screen and file versions are identical.
lay <- igraph::layout_with_fr(g, weights = E(g)$weight, niter = 200)
draw_centrality <- function() {
  plot(
    g,
    layout       = lay,
    vertex.size  = 1 + 8 * (V(g)$btwn / max(V(g)$btwn)),
    vertex.color = V(g)$col,
    vertex.label = NA,
    edge.color   = adjustcolor("grey50", alpha.f = 0.2),
    edge.width   = 0.4,
    main         = "Node size = betweenness. Red = planted bridges."
  )
}

# Show interactively (RStudio / in-browser R session)...
draw_centrality()

# ...and save a copy for terminal / Rscript users.
png(here::here("code", "04_centrality", "centrality_network.png"),
    width = 7, height = 6, units = "in", res = 120)
draw_centrality()
invisible(dev.off())
cat("💾 Saved centrality_network.png\n")


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

lcc_after <- sapply(c("degree", "betweenness", "closeness", "eigenvector"),
                    function(metric) {
  top5 <- cent |>
    arrange(desc(.data[[metric]])) |>
    head(5) |>
    pull(node_id)
  g_test <- igraph::delete_vertices(g, top5)
  size   <- lcc_size(g_test)
  cat(sprintf("   remove top-5 by %-12s -> LCC = %d\n", metric, size))
  size
})

# Land the takeaway so it isn't lost in the four lines above: the SMALLEST
# surviving largest-component is the most damaging attack, i.e. the metric
# most attuned to network criticality.
worst <- names(which.min(lcc_after))
cat(sprintf("📝 Most fragmenting metric: top-5 by %s (LCC = %d). %s\n",
            worst, min(lcc_after),
            if (worst == "betweenness")
              "Betweenness finds the load-bearing bridges degree misses."
            else
              "Compare against betweenness — bridges aren't always the busiest nodes."))


# 6. Learning Check ##########################################################
#
# QUESTION: List the 5 nodes whose betweenness-rank minus degree-rank
# gap is largest. What is the node_id of the #1 entry?

answer <- bridges |> slice(1) |> pull(node_id)

cat(sprintf("\n📝 Learning Check answer: %s\n", answer))

cat("\n🎉 Done. Move on to the case study report when you're ready.\n")
