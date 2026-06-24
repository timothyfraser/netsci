#' @name load.R
#' @title Load the `nyc-realestate-portfolio` project network (R)
#' @description
#'
#' Reads the CSVs in this folder and builds an undirected, weighted property
#' portfolio network: nodes are NYC properties, an edge links two properties that
#' share at least one common equity investor (co-ownership / cross-collateral).
#' Edge weight is `co_investment_usd`. Run it straight (`Rscript load.R`) for a
#' summary, or `source()` it and call `load_portfolio()`. Shares property
#' `node_id`s with the companion `nyc-realestate-capital` dataset.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "nyc-realestate-portfolio")

#' Load the node table (one row per property).
load_nodes <- function() read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)

#' Load the edge table (one row per shared-financing tie).
load_edges <- function() read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)

#' Build the undirected, weighted portfolio graph (weight = `co_investment_usd`).
load_portfolio <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = FALSE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$co_investment_usd
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n🏢 nyc-realestate-portfolio (R)\n")
  cat("   Properties linked by shared equity financing; weight = co_investment_usd.\n\n")

  nodes <- load_nodes(); edges <- load_edges(); g <- load_portfolio(nodes, edges)

  cat(sprintf("✅ Loaded %d properties and %d shared-financing edges.\n",
              nrow(nodes), nrow(edges)))
  cat(sprintf("🔗 Components: %d | mean degree: %.1f | densest cluster hints at concentration risk.\n",
              igraph::components(g)$no, mean(igraph::degree(g))))
  cat("🎉 Graph ready. Undirected; weight = co_investment_usd; group by borough / property_type.\n")
}
