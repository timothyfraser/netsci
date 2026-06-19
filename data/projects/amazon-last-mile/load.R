#' @name load.R
#' @title Load the `amazon-last-mile` project network (R)
#' @description
#'
#' Reads the two CSVs in this folder and builds a directed, weighted igraph
#' object: package flow through hubs -> stations -> zones over one week. Run it
#' straight (`Rscript load.R`) for a quick summary, or `source()` it and call
#' `load_amazon()` to get the graph in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "amazon-last-mile")

#' Load the node table (one row per hub / station / zone).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per origin x destination x day).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Build the directed, weighted graph.
#'
#' Edges are weighted by `packages`. Because the data is temporal (a `day`
#' column), an edge between the same pair appears up to 7 times; igraph keeps
#' them as parallel edges, so filter to one `day` first if you want a simple
#' graph.
load_amazon <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = TRUE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$packages
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n📦 amazon-last-mile (R)\n")
  cat("   Hubs -> stations -> zones; weighted by packages, daily for one week.\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_amazon(nodes, edges)

  cat(sprintf("✅ Loaded %d nodes (%d hubs, %d stations, %d zones) and %d edges.\n",
              nrow(nodes), sum(nodes$kind == "hub"),
              sum(nodes$kind == "station"), sum(nodes$kind == "zone"), nrow(edges)))
  cat(sprintf("🔗 Directed: %s | total packages moved: %s\n",
              is_directed(g), format(sum(edges$packages), big.mark = ",")))
  cat("🎉 Graph ready. Object `g` is a directed, weighted igraph.\n")
}
