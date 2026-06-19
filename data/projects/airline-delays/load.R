#' @name load.R
#' @title Load the `airline-delays` project network (R)
#' @description
#'
#' Reads the two CSVs in this folder and builds a directed, weighted igraph
#' object: one day of scheduled flights between airports, sliced into four time
#' blocks. Run it straight (`Rscript load.R`) for a quick summary, or `source()`
#' it and call `load_airline()` to get the graph in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "airline-delays")

#' Load the node table (one row per airport).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per origin x destination x block).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Build the directed, weighted graph.
#'
#' Edges are weighted by `number_of_flights`. Because the data is temporal (a
#' `block` column), an edge between the same pair appears up to 4 times; igraph
#' keeps them as parallel edges, so filter to one `block` first if you want a
#' simple graph.
load_airline <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = TRUE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$number_of_flights
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n✈️  airline-delays (R)\n")
  cat("   Directed flights between airports, weighted by flights, in 4 time blocks.\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_airline(nodes, edges)

  cat(sprintf("✅ Loaded %d airports (%d hubs) and %d edges (%d routes x 4 blocks).\n",
              nrow(nodes), sum(nodes$hub == 1), nrow(edges),
              nrow(unique(edges[, c("from_id", "to_id")]))))
  cat(sprintf("\U0001F517 Directed: %s | total flights: %s\n",
              is_directed(g), format(sum(edges$number_of_flights), big.mark = ",")))
  cat("\U0001F389 Graph ready. Object `g` is a directed, weighted igraph.\n")
}
