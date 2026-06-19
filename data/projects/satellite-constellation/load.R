#' @name load.R
#' @title Load the `satellite-constellation` project network (R)
#' @description
#'
#' Reads the two CSVs in this folder and builds an undirected, weighted igraph
#' object: a one-instant snapshot of three operators' LEO satellite broadband
#' networks (satellites + ground stations, joined by ISL and feeder links). Run
#' it straight (`Rscript load.R`) for a quick summary, or `source()` it and call
#' `load_constellation()` to get the graph in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "satellite-constellation")

#' Load the node table (one row per satellite / ground station).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per link).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Build the undirected, weighted constellation graph.
#'
#' Edges are weighted by link `capacity_gbps`. The graph is a single frozen
#' snapshot of all orbits at one instant (no time dimension).
load_constellation <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = FALSE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$capacity_gbps
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n\U0001F6F0\UFE0F  satellite-constellation (R)\n")
  cat("   Undirected LEO network; links weighted by capacity (Gbps).\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_constellation(nodes, edges)

  cat(sprintf("✅ Loaded %d nodes (%d satellites, %d ground stations) and %d links.\n",
              nrow(nodes), sum(nodes$kind == "satellite"),
              sum(nodes$kind == "ground_station"), nrow(edges)))
  cat(sprintf("\U0001F517 Directed: %s | total link capacity: %s Gbps\n",
              is_directed(g),
              format(round(sum(edges$capacity_gbps)), big.mark = ",")))
  cat("\U0001F389 Graph ready. Object `g` is an undirected, weighted igraph.\n")
}
