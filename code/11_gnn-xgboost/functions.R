#' @name functions.R
#' @title Helpers for the GNN + XGBoost case study (R track)
#'
#' R does the same pipeline as Python, EXCEPT the GNN-embedding step.
#' R's `xgboost` package is excellent, but there is no widely-used R
#' GNN library. So this helper builds the static + lag features and
#' leaves the embeddings to the Python track. The README explains the
#' AUC gap.

library(dplyr)
library(readr)
library(here)

.case_dir <- function() here::here("code", "11_gnn-xgboost", "data")

load_suppliers <- function() readr::read_csv(file.path(.case_dir(), "suppliers.csv"))
load_edges     <- function() readr::read_csv(file.path(.case_dir(), "edges.csv"))
load_panel     <- function() readr::read_csv(file.path(.case_dir(), "panel.csv"))

#' Add a `lag_rate` column: trailing `window`-week disruption rate
#' per supplier. Uses a rolling mean over the previous `window` weeks
#' (not including the current week, to avoid leakage).
add_lag_features <- function(panel, window = 4) {
  panel <- panel |>
    arrange(supplier_id, week)
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
