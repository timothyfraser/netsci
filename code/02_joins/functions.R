#' @name functions.R
#' @title Helpers for the Network Joins case study
#' @description
#'
#' Small helper functions used by `example.R`:
#'
#' - `load_edges()`   — read the slim rush-hour trips parquet.
#' - `load_stations()` — read the slim stations parquet (with demographic flag).
#' - `make_joined()`  — convenience wrapper that does the standard
#'                       start-side + end-side double join, with renames,
#'                       so we can sanity-check the example.
#'
#' We intentionally keep the functions tiny. The teaching happens in
#' `example.R`; this file is just so you can call `load_edges()` instead
#' of remembering the parquet path.

library(dplyr)
library(readr)
library(arrow)
library(here)

# ----- paths -----------------------------------------------------------------

# Resolve paths relative to THIS file's folder, so the script works no matter
# where you run it from.
.case_dir <- function() {
  here::here("code", "02_joins", "data")
}

# ----- data loaders ----------------------------------------------------------

#' Load the slim trips edge list.
#'
#' One row per (start_station, end_station, day, rush) combination, with
#' `count` = number of trips. Already filtered to AM rush + 2021.
load_edges <- function() {
  arrow::read_parquet(file.path(.case_dir(), "edges.parquet"))
}

#' Load the slim stations node table.
#'
#' One row per station, with a `maj_black` flag ("yes"/"no") from the
#' census block group the station sits in.
load_stations <- function() {
  arrow::read_parquet(file.path(.case_dir(), "stations.parquet"))
}

# ----- the reference join ----------------------------------------------------

#' The "standard" double-side join used as a sanity check in the example.
#'
#' Renames demographics to `start_black` and `end_black`, then drops any
#' edge whose start *or* end station is missing from the stations table
#' (these correspond to stations outside Boston proper).
make_joined <- function(edges = load_edges(), stations = load_stations()) {
  edges |>
    left_join(
      by = c("start_code" = "code"),
      y  = stations |> select(code, start_black = maj_black)
    ) |>
    left_join(
      by = c("end_code" = "code"),
      y  = stations |> select(code, end_black = maj_black)
    ) |>
    filter(!is.na(start_black), !is.na(end_black))
}
