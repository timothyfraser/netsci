#' @name load.R
#' @title Load the `financial-contagion` project network (R)
#' @description
#'
#' Reads the two CSVs in this folder and builds a directed, weighted igraph
#' object: directed financial exposures (creditor -> debtor) among ~220 firms
#' across three periods of a crisis (before / during / after). Run it straight
#' (`Rscript load.R`) for a quick summary, or `source()` it and call
#' `load_contagion()` to get the graph in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "financial-contagion")

#' Load the node table (one row per firm).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per creditor x debtor x period).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Build the directed, weighted graph.
#'
#' Edges are weighted by `exposure` (dollars at risk). Because the data is
#' temporal (a `period` column: before/during/after), an exposure between the
#' same pair can appear up to 3 times; igraph keeps them as parallel edges, so
#' filter to one `period` first if you want a single-period graph.
load_contagion <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = TRUE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$exposure
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n\U0001F3E6 financial-contagion (R)\n")
  cat("   Directed creditor -> debtor exposures; before / during / after a crisis.\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_contagion(nodes, edges)

  cat(sprintf("✅ Loaded %d nodes (%d banks, %d hedge funds, %d insurers, %d ccps) and %d edges.\n",
              nrow(nodes), sum(nodes$type == "bank"), sum(nodes$type == "hedge_fund"),
              sum(nodes$type == "insurer"), sum(nodes$type == "ccp"), nrow(edges)))
  for (p in c("before", "during", "after")) {
    cat(sprintf("   period %-7s: %d exposures\n", p, sum(edges$period == p)))
  }
  cat(sprintf("\U0001F517 Directed: %s | total exposure: %s\n",
              is_directed(g), format(round(sum(edges$exposure)), big.mark = ",")))
  cat("\U0001F389 Graph ready. Object `g` is a directed, weighted igraph.\n")
}
