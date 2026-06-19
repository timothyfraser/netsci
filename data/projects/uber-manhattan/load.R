#' @name load.R
#' @title Load the `uber-manhattan` project network (R)
#' @description
#'
#' Reads the CSVs in this folder and builds a bipartite, weighted igraph object:
#' drivers on one side, riders on the other, edges are rides (weighted by fare).
#' Run it straight (`Rscript load.R`) for a quick summary, or `source()` it and
#' call `load_uber()` in your own script. `load_zones()` returns the zone lookup.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "uber-manhattan")

#' Load the node table (drivers + riders).
load_nodes <- function() read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)

#' Load the edge table (one row per ride).
load_edges <- function() read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)

#' Load the zone lookup table (join onto pickup/dropoff/home zones).
load_zones <- function() read.csv(file.path(.dir(), "zones.csv"), stringsAsFactors = FALSE)

#' Build the bipartite, weighted graph.
#'
#' Edges are weighted by `fare`. The vertex attribute `type` is the igraph
#' bipartite flag: TRUE for riders, FALSE for drivers. Repeat rider-driver pairs
#' stay as parallel edges; collapse with `simplify(g, edge.attr.comb = "sum")`
#' if you want a single weighted edge per pair.
load_uber <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = FALSE, vertices = nodes)
  igraph::V(g)$type <- igraph::V(g)$kind == "rider"
  igraph::E(g)$weight <- igraph::E(g)$fare
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n🚕 uber-manhattan (R)\n")
  cat("   Bipartite drivers <-> riders; edges are rides weighted by fare.\n\n")

  nodes <- load_nodes(); edges <- load_edges(); g <- load_uber(nodes, edges)

  cat(sprintf("✅ Loaded %d nodes (%d drivers + %d riders) and %d rides.\n",
              nrow(nodes), sum(nodes$kind == "driver"),
              sum(nodes$kind == "rider"), nrow(edges)))
  cat(sprintf("🔗 Bipartite: %s | total fares: $%s | total tips: $%s\n",
              igraph::is_bipartite(g),
              format(round(sum(edges$fare)), big.mark = ","),
              format(round(sum(edges$tip)), big.mark = ",")))
  cat("🎉 Graph ready. `g` is bipartite (V(g)$type: rider = TRUE), weighted by fare.\n")
}
