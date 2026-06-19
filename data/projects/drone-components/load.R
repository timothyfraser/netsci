#' @name load.R
#' @title Load the `drone-components` project network (R)
#' @description
#'
#' Reads the two CSVs in this folder and builds a directed, weighted igraph
#' object: a UAV functional dependency graph (`A -> B` means *A depends on /
#' requires B to function*). Run it straight (`Rscript load.R`) for a quick
#' summary, or `source()` it and call `load_drone()` in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "drone-components")

#' Load the node table (one row per component).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per dependency).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Build the directed, weighted dependency graph.
#'
#' Edges are weighted by `coupling_strength`. Direction is `from_id -> to_id`,
#' i.e. `from_id` depends on / requires `to_id` to function. The graph is
#' intentionally NOT a clean DAG.
load_drone <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = TRUE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$coupling_strength
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n\U0001F681 drone-components (R)\n")
  cat("   UAV functional dependency graph; A -> B means A requires B to function.\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_drone(nodes, edges)

  nh <- sum(nodes$kind == "hardware")
  ns <- sum(nodes$kind == "software")
  cat(sprintf("✅ Loaded %d components (%d hardware, %d software) and %d dependency edges.\n",
              nrow(nodes), nh, ns, nrow(edges)))
  cat(sprintf("\U0001F517 Directed: %s | is DAG: %s | total coupling: %s\n",
              is_directed(g), is_dag(g),
              format(sum(edges$coupling_strength), big.mark = ",")))
  ind <- igraph::degree(g, mode = "in")
  outd <- igraph::degree(g, mode = "out")
  cat(sprintf("\U0001F4CA Max in-degree: %d (%s) | max out-degree: %d (%s)\n",
              max(ind), names(which.max(ind)), max(outd), names(which.max(outd))))
  cat("\U0001F389 Graph ready. Object `g` is a directed, weighted igraph.\n")
}
