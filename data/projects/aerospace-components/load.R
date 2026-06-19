#' @name load.R
#' @title Load the `aerospace-components` project network (R)
#' @description
#'
#' Reads the two CSVs in this folder and builds a directed, weighted igraph
#' object: the bill-of-materials + supplier network for a commercial aircraft
#' program (detail parts & suppliers roll up toward the final assembly). Run it
#' straight (`Rscript load.R`) for a quick summary, or `source()` it and call
#' `load_aero()` in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "aerospace-components")

#' Load the node table (one row per part / supplier).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per supply / roll-up relationship).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Build the directed, weighted graph.
#'
#' Edges are weighted by `qty_per_aircraft` and point up the build toward the
#' final assembly. The `relation` edge attribute is `supplies` (firm -> part) or
#' `is_part_of` (child part -> parent). Trace what depends on a node with
#' `subcomponent(g, v, mode = "out")`, or knock a supplier out to see how many
#' safety-critical assemblies lose their supply.
load_aero <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = TRUE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$qty_per_aircraft
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n✈️  aerospace-components (R)\n")
  cat("   Parts & suppliers roll up toward final assembly; weighted by qty/aircraft.\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_aero(nodes, edges)

  cat(sprintf("✅ Loaded %d nodes (%d parts + %d suppliers) and %d edges.\n",
              nrow(nodes), sum(nodes$kind == "part"),
              sum(nodes$kind == "supplier"), nrow(edges)))
  cat(sprintf("🔗 Directed: %s | safety-critical parts: %d | single-source parts: %d\n",
              is_directed(g), sum(nodes$safety_critical == 1, na.rm = TRUE),
              sum(nodes$single_source == 1, na.rm = TRUE)))
  cat(sprintf("🧩 Relations: %d supplies + %d is_part_of\n",
              sum(edges$relation == "supplies"), sum(edges$relation == "is_part_of")))
  cat("🎉 Graph ready. `g` is a directed, weighted igraph (weight = qty_per_aircraft).\n")
}
