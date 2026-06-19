#' @name load.R
#' @title Load the `trade-commodity` project network (R)
#' @description
#'
#' Reads the two CSVs in this folder and builds a directed, weighted igraph
#' object: export flows of a single strategic commodity between countries,
#' recorded across three periods (`before` / `during` / `after` a supply shock).
#' Run it straight (`Rscript load.R`) for a quick summary, or `source()` it and
#' call `load_trade()` to get the graph in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "trade-commodity")

#' Load the node table (one row per country).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per exporter x importer x period).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Build the directed, weighted graph.
#'
#' Edges are weighted by `tonnes`. Because the data is temporal (a `period`
#' column), an exporter->importer pair can appear up to three times (once per
#' period) as parallel edges. Filter to one `period` first if you want a simple
#' graph, e.g. `edges <- subset(load_edges(), period == "before")`.
load_trade <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = TRUE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$tonnes
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n\U0001F310 trade-commodity (R)\n")
  cat("   Country-to-country commodity export flows; weighted by tonnes,\n")
  cat("   across before / during / after a supply shock.\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_trade(nodes, edges)

  cat(sprintf("✅ Loaded %d countries and %d edges across %d periods.\n",
              nrow(nodes), nrow(edges), length(unique(edges$period))))
  cat(sprintf("\U0001F517 Directed: %s | total tonnes traded: %s\n",
              is_directed(g), format(sum(edges$tonnes), big.mark = ",")))
  per <- tapply(edges$tonnes, edges$period, sum)
  cat("\U0001F4E6 Tonnes by period: ",
      paste(sprintf("%s=%s", names(per), format(per, big.mark = ",")),
            collapse = " | "), "\n")
  cat("\U0001F389 Graph ready. Object `g` is a directed, weighted igraph.\n")
}
