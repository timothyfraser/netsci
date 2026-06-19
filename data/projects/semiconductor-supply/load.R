#' @name load.R
#' @title Load the `semiconductor-supply` project network (R)
#' @description
#'
#' Reads the two CSVs in this folder and builds a directed, weighted igraph
#' object: a multi-tier semiconductor supply chain (materials -> foundries ->
#' packaging -> designers -> products). Run it straight (`Rscript load.R`) for a
#' quick summary, or `source()` it and call `load_semi()` in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "semiconductor-supply")

#' Load the node table (one row per supplier / product).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per supply relationship).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Build the directed, weighted graph.
#'
#' Edges are weighted by `annual_volume` and flow from the upstream node to the
#' downstream node. Use `subcomponent(g, v, mode = "out")` to trace everything
#' downstream of a node, or knock a node out (`delete_vertices`) to test how
#' much end-product output it carries.
load_semi <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = TRUE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$annual_volume
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n🔌 semiconductor-supply (R)\n")
  cat("   Materials -> foundries -> packaging -> designers -> products;",
      "weighted by annual volume.\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_semi(nodes, edges)

  cat(sprintf("✅ Loaded %d nodes (%d material, %d foundry, %d packaging, %d designer, %d product) and %d edges.\n",
              nrow(nodes), sum(nodes$kind == "material"),
              sum(nodes$kind == "foundry"), sum(nodes$kind == "packaging"),
              sum(nodes$kind == "designer"), sum(nodes$kind == "product"),
              nrow(edges)))
  cat(sprintf("🔗 Directed: %s | total annual volume: %s | total value: $%s M\n",
              is_directed(g),
              format(sum(edges$annual_volume), big.mark = ","),
              format(round(sum(edges$value_musd)), big.mark = ",")))
  cat("🎉 Graph ready. `g` is a directed, weighted igraph (weight = annual_volume).\n")
}
