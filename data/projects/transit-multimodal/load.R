#' @name load.R
#' @title Load the `transit-multimodal` project network (R)
#' @description
#'
#' Reads the CSVs in this folder and builds an undirected, weighted, multimodal
#' igraph object: neighborhoods are nodes; edges are transit links in two modes
#' (`metro` and `bus`). The same neighborhood pair can carry both a metro and a
#' bus link, so the graph is a multiplex with parallel edges. The edge weight is
#' `capacity` (riders/hr). Run it straight (`Rscript load.R`) for a quick
#' summary, or `source()` it and call `load_transit()` in your own script.
#' `load_lines()` returns the line/route lookup table.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "transit-multimodal")

#' Load the node table (one row per neighborhood).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per transit link: metro or bus).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Load the line/route lookup table (join onto edges by `line`).
load_lines <- function() {
  read.csv(file.path(.dir(), "lines.csv"), stringsAsFactors = FALSE)
}

#' Build the undirected, weighted, multimodal transit graph.
#'
#' Edges are weighted by `capacity` (riders/hr). The `mode` edge attribute is
#' either `"metro"` or `"bus"`; the same neighborhood pair may appear as both
#' (parallel edges). Filter edges to analyze a single mode, or collapse with
#' `simplify(g, edge.attr.comb = list(weight = "sum"))`.
load_transit <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = FALSE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$capacity
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n\U0001F687 transit-multimodal (R)\n")
  cat("   Undirected multimodal transit; neighborhoods linked by metro & bus.\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_transit(nodes, edges)

  cat(sprintf("✅ Loaded %d neighborhoods and %d edges (%d metro + %d bus).\n",
              nrow(nodes), nrow(edges),
              sum(edges$mode == "metro"), sum(edges$mode == "bus")))
  cat(sprintf("\U0001F517 Directed: %s | metro-served neighborhoods: %d | total seat capacity: %s riders/hr\n",
              is_directed(g), sum(nodes$has_metro),
              format(sum(edges$capacity), big.mark = ",")))
  cat("\U0001F389 Graph ready. Object `g` is an undirected, weighted, multimodal igraph.\n")
}
