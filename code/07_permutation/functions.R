#' @name functions.R
#' @title Helpers for the Permutation case study

library(readr)
library(dplyr)
library(igraph)
library(here)

.case_dir <- function() here::here("code", "07_permutation", "data")

load_nodes <- function() readr::read_csv(file.path(.case_dir(), "nodes.csv"),
                                         show_col_types = FALSE)
load_edges <- function() readr::read_csv(file.path(.case_dir(), "edges.csv"),
                                         show_col_types = FALSE)

#' Build the graph (undirected, weighted) from node + edge tables.
build_graph <- function(nodes = load_nodes(), edges = load_edges()) {
  igraph::graph_from_data_frame(
    d = edges, directed = FALSE, vertices = nodes
  )
}

#' Nominal assortativity by `attr_name` (e.g. "demo").
#'
#' Uses igraph's built-in `assortativity_nominal()`. Returns a single
#' number; +1 = perfectly assortative, 0 = random, -1 = perfectly
#' disassortative.
assort_by <- function(g, attr_name) {
  igraph::assortativity_nominal(
    g,
    types = as.integer(factor(igraph::vertex_attr(g, attr_name)))
  )
}

#' Permute node labels (the column you name) and return a *new* graph
#' with the permuted labels. `block_by` = NULL means shuffle labels
#' across ALL nodes; otherwise shuffle labels WITHIN each block.
permute_labels <- function(g, attr_name, block_by = NULL) {
  labels <- igraph::vertex_attr(g, attr_name)
  if (is.null(block_by)) {
    new_labels <- sample(labels)
  } else {
    blocks <- igraph::vertex_attr(g, block_by)
    new_labels <- labels
    for (b in unique(blocks)) {
      mask <- blocks == b
      new_labels[mask] <- sample(labels[mask])
    }
  }
  g2 <- g
  g2 <- igraph::set_vertex_attr(g2, attr_name, value = new_labels)
  g2
}
