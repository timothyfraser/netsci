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
library(arrow)
library(here)

.case_dir <- function() here::here("code", "11_gnn-xgboost", "data")

load_suppliers <- function() arrow::read_parquet(file.path(.case_dir(), "suppliers.parquet"))
load_edges     <- function() arrow::read_parquet(file.path(.case_dir(), "edges.parquet"))
load_panel     <- function() arrow::read_parquet(file.path(.case_dir(), "panel.parquet"))

#' Add a `lag_rate` column: trailing `window`-week disruption rate
#' per supplier. Uses a rolling mean over the previous `window` weeks
#' (not including the current week, to avoid leakage).
add_lag_features <- function(panel, window = 4) {
  panel <- panel |>
    arrange(supplier_id, week)
  panel |>
    group_by(supplier_id) |>
    mutate(
      prev = lag(disrupted, n = 1, default = NA_real_),
      lag_rate = zoo::rollapply(
        prev, width = window, FUN = function(x) mean(x, na.rm = TRUE),
        fill = NA, align = "right", partial = TRUE
      ),
      lag_rate = tidyr::replace_na(lag_rate, 0)
    ) |>
    select(-prev) |>
    ungroup()
}
