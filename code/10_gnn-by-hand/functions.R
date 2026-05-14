#' @name functions.R
#' @title Helpers for the GNN-by-Hand case study (R stub)
#'
#' GNN-by-Hand is Python-primary. This file is here so the folder is
#' consistent with the others, but the actual `gcn_layer()` / `relu()`
#' / `normalize()` functions live in `functions.py`. Use
#' `reticulate::source_python()` if you want to call them from R.
#'
#' See `example.R` for a base-R re-implementation of the Learning
#' Check math.

library(here)

.case_dir <- function() here::here("code", "10_gnn-by-hand", "data")

#' Load the 6-node toy network as a list of two tibbles.
load_tiny <- function() {
  list(
    nodes = readr::read_csv(file.path(.case_dir(), "tiny_nodes.csv"),
                            show_col_types = FALSE),
    edges = readr::read_csv(file.path(.case_dir(), "tiny_edges.csv"),
                            show_col_types = FALSE)
  )
}

#' Load the 200-node project-scale network.
load_large <- function() {
  list(
    nodes = readr::read_csv(file.path(.case_dir(), "large_nodes.csv"),
                            show_col_types = FALSE),
    edges = readr::read_csv(file.path(.case_dir(), "large_edges.csv"),
                            show_col_types = FALSE)
  )
}
