#' @name load.R
#' @title Load the `opensource-deps` project network (R)
#' @description
#'
#' Reads the two CSVs in this folder and builds a directed, weighted igraph
#' object: a software-package dependency graph (`A -> B` means A depends on B).
#' Run it straight (`Rscript load.R`) for a quick summary, or `source()` it and
#' call `load_deps()` to get the graph in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "opensource-deps")

#' Load the node table (one row per package).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per dependency).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Build the directed, weighted dependency graph.
#'
#' Edges are weighted by `import_count`. Direction is `from_id -> to_id`,
#' i.e. `from_id` depends on `to_id`.
load_deps <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = TRUE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$import_count
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n\U0001F4E6 opensource-deps (R)\n")
  cat("   Package dependency graph; A -> B means A depends on B, weighted by imports.\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_deps(nodes, edges)

  cat(sprintf("✅ Loaded %d packages and %d dependency edges.\n",
              nrow(nodes), nrow(edges)))
  cat(sprintf("\U0001F517 Directed: %s | total import call-sites: %s\n",
              is_directed(g), format(sum(edges$import_count), big.mark = ",")))
  ind <- igraph::degree(g, mode = "in")
  outd <- igraph::degree(g, mode = "out")
  cat(sprintf("\U0001F4CA Max direct in-degree: %d (%s) | max out-degree: %d (%s)\n",
              max(ind), names(which.max(ind)), max(outd), names(which.max(outd))))
  cat("\U0001F389 Graph ready. Object `g` is a directed, weighted igraph.\n")
}
