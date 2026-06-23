#' @name load.R
#' @title Load the `satellite-supply-chain` project network (R)
#' @description
#'
#' Reads the two CSVs in this folder and builds a directed, weighted igraph
#' object: a multi-tier satellite manufacturing supply chain (materials ->
#' components -> subsystems -> integrators -> programs). Run it straight
#' (`Rscript load.R`) for a quick summary, or `source()` it and call
#' `load_satellite()` in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "satellite-supply-chain")

#' Load the node table (one row per supplier / subsystem / program).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per supply relationship).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Build the directed, weighted graph.
#'
#' Edges are weighted by `units_per_year` and flow from the upstream node to the
#' downstream node. Use `subcomponent(g, v, mode = "out")` to trace everything
#' downstream of a node, or knock a node out (`delete_vertices`) to test how much
#' end-program output it carries.
load_satellite <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = TRUE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$units_per_year
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n🛰️  satellite-supply-chain (R)\n")
  cat("   Materials -> components -> subsystems -> integrators -> programs;",
      "weighted by units per year.\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_satellite(nodes, edges)

  cat(sprintf("✅ Loaded %d nodes (%d material, %d component, %d subsystem, %d integrator, %d program) and %d edges.\n",
              nrow(nodes), sum(nodes$kind == "material"),
              sum(nodes$kind == "component"), sum(nodes$kind == "subsystem"),
              sum(nodes$kind == "integrator"), sum(nodes$kind == "program"),
              nrow(edges)))
  cat(sprintf("🔗 Directed: %s | total units/year: %s | total value: $%s M\n",
              is_directed(g),
              format(sum(edges$units_per_year), big.mark = ","),
              format(round(sum(edges$value_musd)), big.mark = ",")))
  cat("🎉 Graph ready. `g` is a directed, weighted igraph (weight = units_per_year).\n")
}
