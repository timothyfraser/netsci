#' @name load.R
#' @title Load the `campus-contact` project network (R)
#' @description
#'
#' Reads the CSVs in this folder and builds an undirected, weighted igraph
#' object: weekly face-to-face co-location contacts on a campus over four weeks.
#' Run it straight (`Rscript load.R`) for a quick summary, or `source()` it and
#' call `load_campus()` to get the graph in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "campus-contact")

#' Load the node table (one row per person).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per person x person x week).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Load the infection-status table (one row per person x week).
load_status <- function() {
  read.csv(file.path(.dir(), "status.csv"), stringsAsFactors = FALSE)
}

#' Build the undirected, weighted contact graph.
#'
#' Edges are weighted by `contact_minutes`. Because the data is temporal (a
#' `week` column), a pair can appear up to 4 times as parallel edges; filter to
#' one `week` first if you want a simple graph.
load_campus <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = FALSE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$contact_minutes
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n\U0001F9A0 campus-contact (R)\n")
  cat("   Weekly face-to-face contacts on campus; weighted by contact minutes.\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  status <- load_status()
  g <- load_campus(nodes, edges)

  cat(sprintf("✅ Loaded %d people (%d students, %d faculty, %d staff) and %d contact-weeks.\n",
              nrow(nodes), sum(nodes$kind == "student"),
              sum(nodes$kind == "faculty"), sum(nodes$kind == "staff"), nrow(edges)))
  cat(sprintf("\U0001F517 Directed: %s | total contact minutes: %s\n",
              is_directed(g), format(sum(edges$contact_minutes), big.mark = ",")))
  inf <- tapply(status$infected, status$week, sum)
  cat(sprintf("\U0001F4C8 Cumulative infected by week: %s\n",
              paste(sprintf("wk%d=%d", as.integer(names(inf)), inf), collapse = "  ")))
  cat("\U0001F389 Graph ready. Object `g` is an undirected, weighted igraph.\n")
}
