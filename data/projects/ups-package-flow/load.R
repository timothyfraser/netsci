#' @name load.R
#' @title Load the `ups-package-flow` project network (R)
#' @description
#'
#' Reads the two CSVs in this folder and builds a directed, weighted igraph
#' multigraph where the **unit of analysis is the individual package**: one edge
#' per parcel, from its origin plant to its destination plant. Run it straight
#' (`Rscript load.R`) for a quick summary, or `source()` it and call
#' `load_packages()` in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "ups-package-flow")

#' Load the node table (one row per plant: gateway / hub / center).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per package).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Build the directed, weighted multigraph (one edge per package).
#'
#' Edge weight is `weight_kg`. Each package edge also carries `service_level`,
#' `distance_km`, `transit_hours`, `promised_hours`, `on_time`, and `damaged`.
#' Aggregate the edges by (from, to) to recover a lane-level view, or summarise
#' `on_time` by destination plant to compare service across facilities.
load_packages <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = TRUE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$weight_kg
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n📦 ups-package-flow (R)\n")
  cat("   One edge per package: origin plant -> destination plant;",
      "weight = weight_kg.\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_packages(nodes, edges)

  cat(sprintf("✅ Loaded %d plants (%d gateway, %d hub, %d center) and %d packages.\n",
              nrow(nodes), sum(nodes$kind == "gateway"),
              sum(nodes$kind == "hub"), sum(nodes$kind == "center"),
              nrow(edges)))
  cat(sprintf("🔗 Directed: %s | on-time: %.1f%% | damaged: %.1f%% | mean transit: %.1f h\n",
              is_directed(g),
              100 * mean(edges$on_time), 100 * mean(edges$damaged),
              mean(edges$transit_hours)))
  cat("🎉 Graph ready. `g` is a directed, weighted multigraph (weight = weight_kg).\n")
}
