#' @name functions.R
#' @title Helpers for the GNN + XGBoost case study (R, reticulate bridge)
#' @author <your-name-here>
#' @description
#' R handles almost this entire pipeline natively: loading the supplier
#' tables, engineering the lag feature, training XGBoost, and scoring AUC.
#' The ONE piece with no mature R library is the GNN-style structural
#' embedding, so for that step we reach across to the course's canonical
#' numpy implementation (`functions.py`) through `reticulate`. This file
#' exposes the R-native loaders + `add_lag_features()`, plus a thin
#' `add_gnn_embeddings()` wrapper that drives the Python embedding code.


# 0. R-native loaders and lag feature ########################################

library(dplyr)
library(readr)
library(zoo)
library(here)
library(reticulate)

.case_dir <- function() here::here("code", "09_gnn-xgboost", "data")

load_suppliers <- function() readr::read_csv(file.path(.case_dir(), "suppliers.csv"),
                                             show_col_types = FALSE)
load_edges     <- function() readr::read_csv(file.path(.case_dir(), "edges.csv"),
                                             show_col_types = FALSE)
load_panel     <- function() readr::read_csv(file.path(.case_dir(), "panel.csv"),
                                             show_col_types = FALSE)

#' Add a `lag_rate` column: trailing `window`-week disruption rate per
#' supplier, computed from weeks BEFORE the current one (no leakage).
add_lag_features <- function(panel, window = 4) {
  panel <- panel |> arrange(supplier_id, week)
  panel |>
    group_by(supplier_id) |>
    mutate(
      # week 0 has no history; treat absent history as 0 disruption
      prev = dplyr::lag(disrupted, n = 1, default = 0),
      lag_rate = zoo::rollapply(
        prev, width = window, FUN = mean,
        fill = 0, align = "right", partial = TRUE
      )
    ) |>
    select(-prev) |>
    ungroup()
}


# 1. The GNN half: borrow the embedding from functions.py ####################
#
# The structural embedding is the "A %*% x" piece of a GCN layer applied to
# each week's lag_rate (1-hop = neighbor average, 2-hop = neighbors'
# neighbors). There's no maintained R GNN library, so we call the course's
# numpy implementation. We only need numpy + pandas on the Python side;
# py_require() provisions them on a current reticulate (same idiom as
# dsai/07_rag/05_embed.R), and import_from_path() hands us the module as
# `.gnn_py` without polluting the global namespace.

if (utils::packageVersion("reticulate") >= "1.41") {
  reticulate::py_require(c("numpy", "pandas"))
}

.gnn_py <- reticulate::import_from_path(
  "functions",
  path    = here::here("code", "09_gnn-xgboost"),
  convert = TRUE
)

#' Add `gnn_1hop` and `gnn_2hop` columns to the panel.
#'
#' Builds the row-normalized in-neighbor adjacency from the edge list,
#' then averages each supplier's neighbors' (and 2-hop neighbors')
#' lag_rate, per week. Both steps run in numpy via reticulate.
add_gnn_embeddings <- function(panel, suppliers, edges) {
  A <- .gnn_py$build_adjacency(suppliers, edges)
  .gnn_py$add_gnn_embeddings(panel, suppliers, A)
}
