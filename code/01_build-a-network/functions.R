#' @name functions.R
#' @title Helpers for the Build-a-Network case study
#' @description
#'
#' Tiny wrappers around `read_csv()` that resolve paths for us, plus a
#' single helper that takes the node + edge tables and returns an
#' `igraph` object built the "right" way (bipartite, with `kind` tagged
#' on as a vertex attribute).

library(readr)
library(dplyr)
library(igraph)
library(here)

.case_dir <- function() here::here("code", "01_build-a-network", "data")

#' Load the node table.
load_nodes <- function() {
  readr::read_csv(file.path(.case_dir(), "nodes.csv"), show_col_types = FALSE)
}

#' Load the edge table.
load_edges <- function() {
  readr::read_csv(file.path(.case_dir(), "edges.csv"), show_col_types = FALSE)
}

#' Build an igraph bipartite graph from node + edge tables.
#'
#' Sets `type = TRUE` for components and `type = FALSE` for suppliers,
#' which is the convention igraph uses to flag a bipartite graph.
build_bipartite <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- igraph::graph_from_data_frame(
    d = edges |> select(from_id, to_id, volume_units),
    directed = FALSE,
    vertices = nodes |> select(node_id, kind, region, tier, capacity_units)
  )
  igraph::V(g)$type <- igraph::V(g)$kind == "component"
  g
}
