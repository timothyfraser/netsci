#' @name functions.R
#' @title Helpers for the GNN-by-Hand case study (R, reticulate bridge)
#' @author <your-name-here>
#' @description
#' Graph Neural Networks are the one spot in this course where R has no
#' mature native library, so the GCN math itself lives in Python
#' (`functions.py`). This file handles the half R is great at — reading
#' the toy and project-scale networks from CSV — and then reaches across
#' to Python with `reticulate` to borrow the GCN building blocks
#' (`adjacency`, `normalize`, `gcn_layer`). The Python module is loaded
#' once here and exposed as the object `gcn`, so `example.R` can call
#' `gcn$gcn_layer(...)` and friends directly.


# 0. R-native data loaders ###################################################
#
# Reading CSVs is something R does perfectly well, so we keep it on this
# side of the bridge. Each loader returns a named list of two tibbles.

library(here)
library(reticulate)

.case_dir <- function() here::here("code", "08_gnn-by-hand", "data")

#' Load the 6-node toy network as a list of two tibbles.
load_tiny <- function() {
  list(
    nodes = readr::read_csv(file.path(.case_dir(), "tiny_nodes.csv"),
                            show_col_types = FALSE),
    edges = readr::read_csv(file.path(.case_dir(), "tiny_edges.csv"),
                            show_col_types = FALSE)
  )
}

#' Load the 200-node project-scale network as a list of two tibbles.
load_large <- function() {
  list(
    nodes = readr::read_csv(file.path(.case_dir(), "large_nodes.csv"),
                            show_col_types = FALSE),
    edges = readr::read_csv(file.path(.case_dir(), "large_edges.csv"),
                            show_col_types = FALSE)
  )
}


# 1. The GNN half: borrow the numpy GCN functions from functions.py ##########
#
# We only need numpy + pandas on the Python side. On a current reticulate
# (>= 1.41) py_require() records those requirements and provisions them in
# an ephemeral environment the first time Python is touched -- the same
# one-liner used in dsai/07_rag/05_embed.R. (On an older reticulate, point
# it at a Python that already has numpy + pandas via RETICULATE_PYTHON.)
# import_from_path() then hands us the module as the R object `gcn` WITHOUT
# dumping its functions into the global namespace, so our R loaders above
# keep their names.

if (utils::packageVersion("reticulate") >= "1.41") {
  reticulate::py_require(c("numpy", "pandas"))
}

gcn <- reticulate::import_from_path(
  "functions",
  path    = here::here("code", "08_gnn-by-hand"),
  convert = TRUE  # numpy arrays come back as R matrices, automatically
)
