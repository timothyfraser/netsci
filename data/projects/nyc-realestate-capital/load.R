#' @name load.R
#' @title Load the `nyc-realestate-capital` project network (R)
#' @description
#'
#' Reads the CSVs in this folder and builds a directed, weighted, temporal funding
#' network: capital providers (investors + banks) -> NYC properties. Edges are
#' provider-property-quarter rows carrying capital already deployed (`invested_usd`)
#' vs pledged-but-not-yet-deployed (`pledged_usd`). Run it straight
#' (`Rscript load.R`) for a summary, or `source()` it and call `load_capital()`.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "nyc-realestate-capital")

#' Load the node table (properties + investors + banks; see the `kind` column).
load_nodes <- function() read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)

#' Load the edge table (one row per provider-property-quarter).
load_edges <- function() read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)

#' Build the directed, weighted funding graph (edge weight = `invested_usd`).
#'
#' The graph is bipartite in structure (providers connect only to properties);
#' `V(g)$type` is TRUE for properties, FALSE for capital providers. Edges are kept
#' in long temporal form: filter `E(g)$quarter` (e.g. "2025Q2") for one slice, or
#' `subgraph.edges()` it. Collapse repeat quarters with
#' `simplify(g, edge.attr.comb = list(invested_usd = "sum", weight = "sum"))`.
load_capital <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = TRUE, vertices = nodes)
  igraph::V(g)$type <- igraph::V(g)$kind == "property"
  igraph::E(g)$weight <- igraph::E(g)$invested_usd
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n🏙️  nyc-realestate-capital (R)\n")
  cat("   Investors + banks -> NYC properties; quarterly invested vs pledged.\n\n")

  nodes <- load_nodes(); edges <- load_edges(); g <- load_capital(nodes, edges)

  cat(sprintf("✅ Loaded %d nodes (%d properties + %d investors + %d banks) and %d funding rows.\n",
              nrow(nodes), sum(nodes$kind == "property"),
              sum(nodes$kind == "investor"), sum(nodes$kind == "bank"), nrow(edges)))
  cat(sprintf("🔗 Quarters: %s | total invested: $%sB | total pledged (open): $%sB\n",
              length(unique(edges$quarter)),
              format(round(sum(edges$invested_usd) / 1e9, 1), nsmall = 1),
              format(round(sum(edges$pledged_usd) / 1e9, 1), nsmall = 1)))
  cat("🎉 Graph ready. Directed providers -> properties; weight = invested_usd; filter E(g)$quarter.\n")
}
