#' @name functions.R
#' @title Helpers for the Aggregation case study
#' @description
#' Path-resolved loaders for the slim mobility-flow data.

library(dplyr)
library(here)

.case_dir <- function() here::here("code", "03_aggregation", "data")

load_edges    <- function() readr::read_csv(file.path(.case_dir(), "edges.csv"))
load_stations <- function() readr::read_csv(file.path(.case_dir(), "stations.csv"))

#' Edges with start- and end-side traits already joined in.
make_enriched <- function(edges = load_edges(), stations = load_stations()) {
  edges |>
    left_join(
      by = c("start_code" = "code"),
      y  = stations |> select(code,
                              start_nbhd     = neighborhood,
                              start_quintile = income_quintile)
    ) |>
    left_join(
      by = c("end_code" = "code"),
      y  = stations |> select(code,
                              end_nbhd     = neighborhood,
                              end_quintile = income_quintile)
    )
}
