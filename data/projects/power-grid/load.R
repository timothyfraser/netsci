#' @name load.R
#' @title Load the `power-grid` project network (R)
#' @description
#'
#' Reads the CSVs in this folder and builds an undirected, weighted igraph
#' object: a regional electrical transmission grid of buses and lines. Run it
#' straight (`Rscript load.R`) for a quick summary, or `source()` it and call
#' `load_grid()` to get the graph in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "power-grid")

#' Load the node table (one row per bus).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per transmission line).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Load the control-area lookup table (join onto nodes by `region`).
load_regions <- function() {
  read.csv(file.path(.dir(), "regions.csv"), stringsAsFactors = FALSE)
}

#' Build the undirected, weighted grid graph.
#'
#' Edges are weighted by line `capacity_mw`. The graph is a single static
#' snapshot (no time dimension).
load_grid <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = FALSE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$capacity_mw
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n\U0001F50C power-grid (R)\n")
  cat("   Undirected transmission grid; lines weighted by capacity (MW).\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_grid(nodes, edges)

  cat(sprintf("✅ Loaded %d buses (%d generators, %d substations, %d loads) and %d lines.\n",
              nrow(nodes), sum(nodes$kind == "generator"),
              sum(nodes$kind == "substation"), sum(nodes$kind == "load"), nrow(edges)))
  cat(sprintf("\U0001F517 Directed: %s | total line capacity: %s MW\n",
              is_directed(g), format(sum(edges$capacity_mw), big.mark = ",")))
  cat("\U0001F389 Graph ready. Object `g` is an undirected, weighted igraph.\n")
}
