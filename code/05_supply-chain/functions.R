#' @name functions.R
#' @title Helpers for the Supply Chain Resilience case study

library(readr)
library(dplyr)
library(igraph)
library(here)

.case_dir <- function() here::here("code", "05_supply-chain", "data")

load_nodes <- function() readr::read_csv(file.path(.case_dir(), "nodes.csv"),
                                         show_col_types = FALSE)
load_edges <- function() readr::read_csv(file.path(.case_dir(), "edges.csv"),
                                         show_col_types = FALSE)

#' Build the directed supply-chain graph.
build_graph <- function(nodes = load_nodes(), edges = load_edges()) {
  igraph::graph_from_data_frame(
    d        = edges,
    directed = TRUE,
    vertices = nodes
  )
}

#' Supply coverage = fraction of retailers (tier-3 nodes) that are
#' still reachable from at least one supplier (tier-1 node) in the
#' graph passed in. This is the resilience metric the case study uses.
supply_coverage <- function(g) {
  v_tier <- igraph::V(g)$tier
  suppliers <- igraph::V(g)[v_tier == 1]
  retailers <- igraph::V(g)[v_tier == 3]
  if (length(retailers) == 0) return(NA_real_)

  # For each retailer, check if any supplier can reach it via directed paths.
  # `subcomponent(mode = "out")` from a supplier gives every vertex it can reach.
  reachable <- rep(FALSE, length(retailers))
  ret_names <- retailers$name
  for (s in suppliers) {
    reachable_from_s <- igraph::subcomponent(g, s, mode = "out")$name
    reachable <- reachable | (ret_names %in% reachable_from_s)
    if (all(reachable)) break
  }
  mean(reachable)
}

#' Simulate removing a set of nodes and report supply coverage.
remove_and_score <- function(g, victims) {
  g2 <- igraph::delete_vertices(g, victims)
  supply_coverage(g2)
}
