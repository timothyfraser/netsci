#' @name load.R
#' @title Load the `ups-ground-network` project network (R)
#' @description
#'
#' Reads the two CSVs in this folder and builds a directed, weighted igraph
#' object: a UPS-style ground line-haul network of large trucks moving parcels
#' between package plants (centers -> regional hubs -> national gateways). Run it
#' straight (`Rscript load.R`) for a quick summary, or `source()` it and call
#' `load_ups()` in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "ups-ground-network")

#' Load the node table (one row per plant: gateway / hub / center).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per source-plant -> destination-plant lane).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Build the directed, weighted graph.
#'
#' Lanes are weighted by `packages` and flow from the origin plant to the
#' destination plant. Each lane also carries `trucks`, `distance_km`, and
#' `transit_hours`. Knock a node out (`delete_vertices`) to test how much flow it
#' carries, or use `distances()` to see how reroutes lengthen transit time.
load_ups <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = TRUE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$packages
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n🚛 ups-ground-network (R)\n")
  cat("   Centers -> regional hubs -> national gateways;",
      "lanes weighted by packages, with trucks / distance / transit time.\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_ups(nodes, edges)

  cat(sprintf("✅ Loaded %d nodes (%d gateway, %d hub, %d center) and %d lanes.\n",
              nrow(nodes), sum(nodes$kind == "gateway"),
              sum(nodes$kind == "hub"), sum(nodes$kind == "center"),
              nrow(edges)))
  cat(sprintf("🔗 Directed: %s | total packages/day: %s on %s trucks | mean lane: %.0f km, %.1f h\n",
              is_directed(g),
              format(sum(edges$packages), big.mark = ","),
              format(sum(edges$trucks), big.mark = ","),
              mean(edges$distance_km), mean(edges$transit_hours)))
  cat("🎉 Graph ready. `g` is a directed, weighted igraph (weight = packages).\n")
}
