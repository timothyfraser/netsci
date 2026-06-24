#' @name functions.R
#' @title Helpers for the DSM Clustering case study

library(readr)
library(dplyr)
library(igraph)
library(here)

.case_dir <- function() here::here("code", "06_dsm-clustering", "data")

load_nodes <- function() readr::read_csv(file.path(.case_dir(), "nodes.csv"),
                                         show_col_types = FALSE)
load_edges <- function() readr::read_csv(file.path(.case_dir(), "edges.csv"),
                                         show_col_types = FALSE)

#' Build the DSM dependency graph (directed).
build_graph <- function(nodes = load_nodes(), edges = load_edges()) {
  igraph::graph_from_data_frame(
    d        = edges,
    directed = TRUE,
    vertices = nodes
  )
}

#' Components that fail within `n_hops` of `seed_node`.
#'
#' Follows outgoing dependency edges. With high inter-module
#' connectivity, an unbounded cascade can reach every component, so
#' we bound to k hops to keep the simulation interpretable.
cascade_bfs <- function(g, seed_node, n_hops = 3) {
  idx <- which(igraph::V(g)$name == seed_node)
  reached <- igraph::ego(g, order = n_hops, nodes = idx, mode = "out")[[1]]
  reached$name
}
