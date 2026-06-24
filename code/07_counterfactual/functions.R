#' @name functions.R
#' @title Helpers for the Counterfactual Monte Carlo case study

library(readr)
library(dplyr)
library(igraph)
library(here)

.case_dir <- function() here::here("code", "09_counterfactual", "data")

load_nodes <- function() readr::read_csv(file.path(.case_dir(), "nodes.csv"),
                                         show_col_types = FALSE)
load_edges <- function() readr::read_csv(file.path(.case_dir(), "edges.csv"),
                                         show_col_types = FALSE)

#' Build the bikeshare graph (undirected) with a `cost` edge attribute.
#'
#' For weighted APL, cost = 1 / ridership so that higher-ridership
#' edges are "shorter."
build_graph <- function(nodes = load_nodes(), edges = load_edges(),
                        with_extra = NULL) {
  if (!is.null(with_extra)) edges <- bind_rows(edges, with_extra)
  edges <- edges |>
    mutate(cost = 1 / pmax(ridership, 1))
  igraph::graph_from_data_frame(
    d = edges, directed = FALSE, vertices = nodes
  )
}

#' Weighted APL using `cost` as edge weight.
weighted_apl <- function(g) {
  igraph::mean_distance(g, weights = igraph::E(g)$cost, directed = FALSE)
}

#' Monte Carlo: draw `R` replicates of the network where each edge's
#' ridership is resampled from Poisson(lambda = observed_ridership),
#' rebuild, and return a vector of weighted APLs.
mc_apls <- function(edges, nodes, R = 500, extra = NULL,
                    seed = 1L) {
  set.seed(seed)
  out <- numeric(R)
  base_ridership <- edges$ridership
  for (i in seq_len(R)) {
    new_ridership <- rpois(length(base_ridership), lambda = base_ridership)
    new_edges <- edges
    new_edges$ridership <- new_ridership
    if (!is.null(extra)) {
      e_extra <- extra
      e_extra$ridership <- rpois(nrow(extra), lambda = extra$ridership)
      new_edges <- bind_rows(new_edges, e_extra)
    }
    g <- build_graph(nodes, new_edges)
    out[i] <- weighted_apl(g)
  }
  out
}
