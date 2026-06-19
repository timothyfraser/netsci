#' @name load.R
#' @title Load the `reorg-comms` project network (R)
#' @description
#'
#' Reads the two CSVs in this folder and builds a directed, weighted igraph
#' object: internal message volume between employees, recorded across three
#' periods (`before` / `during` / `after` a reorganization + layoff). Run it
#' straight (`Rscript load.R`) for a quick summary, or `source()` it and call
#' `load_reorg()` to get the graph in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "reorg-comms")

#' Load the node table (one row per employee).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE,
           colClasses = c(manager_id = "character"))
}

#' Load the edge table (one row per sender x receiver x period).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Build the directed, weighted graph.
#'
#' Edges are weighted by `message_count`. Because the data is temporal (a
#' `period` column), a sender->receiver pair can appear up to three times (once
#' per period) as parallel edges. Filter to one `period` first if you want a
#' simple graph, e.g. `edges <- subset(load_edges(), period == "before")`.
#'
#' Note: `manager_id` on the node table is the FORMAL org-chart reporting line
#' (blank for department heads), separate from who actually messages whom.
load_reorg <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = TRUE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$message_count
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n\U0001F4AC reorg-comms (R)\n")
  cat("   Employee-to-employee message volume; weighted by message_count,\n")
  cat("   across before / during / after a reorganization + layoff.\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_reorg(nodes, edges)

  cat(sprintf("✅ Loaded %d employees (%d laid off) and %d edges across %d periods.\n",
              nrow(nodes), sum(nodes$laid_off == 1), nrow(edges),
              length(unique(edges$period))))
  cat(sprintf("\U0001F517 Directed: %s | total messages: %s\n",
              is_directed(g), format(sum(edges$message_count), big.mark = ",")))
  per <- tapply(edges$message_count, edges$period, sum)
  cat("\U0001F4E8 Messages by period: ",
      paste(sprintf("%s=%s", names(per), format(per, big.mark = ",")),
            collapse = " | "), "\n")
  cat("\U0001F389 Graph ready. Object `g` is a directed, weighted igraph.\n")
}
