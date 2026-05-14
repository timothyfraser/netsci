#' @name functions.R
#' @title Helpers for the Sampling case study

library(dplyr)
library(sf)
library(here)

.case_dir <- function() here::here("code", "08_sampling", "data")

load_nodes <- function() {
  readr::read_csv(
    file.path(.case_dir(), "nodes.csv"),
    # geoid is a numeric-looking string; keep it as character so
    # comparisons like `geoid == "1208692158"` work.
    col_types = readr::cols(geoid = readr::col_character(),
                            .default = readr::col_guess())
  )
}
load_edges <- function() {
  readr::read_csv(
    file.path(.case_dir(), "edges.csv"),
    show_col_types = FALSE
  )
}
load_subdivisions <- function() {
  sf::st_read(file.path(.case_dir(), "county_subdivisions.geojson"),
              quiet = TRUE)
}

#' Compute normalized network statistics per time slice.
#'
#' Mirrors the workshop helper from 29C_databases.R: edge weight,
#' edge count, node count, # linked nodes, density, % linked, edges
#' per node, average edgeweight per node.
slice_stats <- function(edges, n_total_nodes) {
  edges |>
    group_by(date_time) |>
    summarize(
      edgeweight     = sum(evacuation, na.rm = TRUE),
      n_edges        = dplyr::n(),
      n_nodes        = n_total_nodes,
      n_nodes_linked = length(unique(c(from, to))),
      .groups        = "drop"
    ) |>
    mutate(
      density          = 2 * n_edges / (n_nodes * (n_nodes - 1)),
      pc_nodes_linked  = n_nodes_linked / n_nodes,
      edge_ratio       = n_edges / n_nodes,
      avg_edgeweight   = edgeweight / n_nodes
    )
}
