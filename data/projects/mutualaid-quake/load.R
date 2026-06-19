#' @name load.R
#' @title Load the `mutualaid-quake` project network (R)
#' @description
#'
#' Reads the two CSVs in this folder and builds a directed, weighted igraph
#' object: acts of mutual aid given between residents and organizations in
#' fictional "Eastvale" across three periods of an earthquake. Run it straight
#' (`Rscript load.R`) for a quick summary, or `source()` it and call
#' `load_mutualaid()` to get the graph in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "mutualaid-quake")

#' Load the node table (one row per resident / org).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per giver x receiver x period).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Build the directed, weighted graph.
#'
#' Edges are weighted by `amount` (aid given). Because the data is temporal (a
#' `period` column with before/during/after), an edge between the same pair can
#' appear up to 3 times; igraph keeps them as parallel edges, so filter to one
#' `period` first if you want a single-period graph.
load_mutualaid <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = TRUE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$amount
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n\U0001F91D mutualaid-quake (R)\n")
  cat("   Directed aid between residents & orgs; before / during / after a quake.\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_mutualaid(nodes, edges)

  cat(sprintf("✅ Loaded %d nodes (%d residents, %d orgs) and %d edges.\n",
              nrow(nodes), sum(nodes$kind == "resident"),
              sum(nodes$kind == "org"), nrow(edges)))
  for (p in c("before", "during", "after")) {
    cat(sprintf("   period %-7s: %d ties\n", p, sum(edges$period == p)))
  }
  cat(sprintf("\U0001F517 Directed: %s | total aid given: %s\n",
              is_directed(g), format(round(sum(edges$amount)), big.mark = ",")))
  cat("\U0001F389 Graph ready. Object `g` is a directed, weighted igraph.\n")
}
