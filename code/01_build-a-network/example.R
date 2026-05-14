#' @name example.R
#' @title Case Study 01 — Build a Network
#' @author <your-name-here>
#' @description
#'
#' You've used the interactive lab to drag nodes and draw edges. Now we
#' build a network from *real tables* and let the code do the rest.
#'
#' Our data is a synthetic bipartite supply network:
#'   - 80 suppliers (nodes of kind "supplier")
#'   - 120 components (nodes of kind "component")
#'   - ~577 ship-relationships (a supplier ships a component, weighted by volume)
#'
#' The goal:
#'   1. Get the node table and the edge table into shape.
#'   2. Turn them into a real graph object.
#'   3. Inspect basic structure (sizes, degree distribution).
#'   4. Project the bipartite graph to a one-mode supplier-by-supplier graph
#'      (two suppliers connected if they share a component).
#'   5. Find supplier-level structural patterns.


# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

library(dplyr)
library(readr)
library(tibble)
library(igraph)
library(ggplot2)
library(here)

## 0.2 Load helpers ##########################################################

source(here::here("code", "01_build-a-network", "functions.R"))

## 0.3 Load data #############################################################

nodes <- load_nodes()
edges <- load_edges()

nodes |> head()
edges |> head()

# How many of each kind of node? How many edges?
nodes |> count(kind)
nrow(edges)


# 1. Build the graph #########################################################
#
# A graph is just a set of vertices and a set of edges connecting them.
# The data is already in that shape; we just need to hand the two
# tables to igraph and ask it to wire them up.

## 1.1 The naive way (suppliers and components mixed) ########################

# functions.R's build_bipartite() does graph_from_data_frame() and sets
# the bipartite `type` attribute for us.
g <- build_bipartite(nodes, edges)
g
# That summary line tells us: <number of vertices>, <number of edges>,
# directed flag, attributes.

## 1.2 Bipartite check #######################################################

# igraph has a quick test for whether our graph is bipartite, given
# the `type` attribute we set in the helper.
igraph::bipartite_mapping(g)$res


# 2. Inspect basic structure #################################################

## 2.1 Degree distribution by kind ###########################################

degrees <- tibble::tibble(
  node_id = igraph::V(g)$name,
  kind    = igraph::V(g)$kind,
  degree  = igraph::degree(g)
)

# Suppliers tend to touch ~5-10 components; components are touched by
# anywhere from 1 to ~20 suppliers. Look at the summary stats.
degrees |>
  group_by(kind) |>
  summarize(
    n       = n(),
    mean    = mean(degree),
    median  = median(degree),
    min     = min(degree),
    max     = max(degree),
    .groups = "drop"
  )

## 2.2 Top-degree components (the "shared" ones) #############################

# Which components have the most suppliers shipping them? These are
# the structural pivot points in a one-mode projection.
degrees |>
  filter(kind == "component") |>
  arrange(desc(degree)) |>
  head(10)


# 3. Bipartite projection ####################################################
#
# The interesting question in a bipartite supply network usually isn't
# "which supplier ships which component" — it's "which suppliers are
# co-exposed because they share a component." If component C037 goes
# offline, every supplier that depends on it is in trouble together.
#
# A bipartite projection answers exactly that. It produces two graphs:
#   - supplier-by-supplier: two suppliers linked if they share >=1 component
#   - component-by-component: two components linked if they share >=1 supplier

proj <- igraph::bipartite_projection(g)
proj_suppliers  <- proj$proj1   # the "FALSE" side — suppliers
proj_components <- proj$proj2   # the "TRUE"  side — components
proj_suppliers
proj_components

# Each edge in the suppliers projection has a `weight` attribute equal
# to the NUMBER OF SHARED COMPONENTS between those two suppliers. That
# weight is the closest thing to a "shared-fate" score.

## 3.1 Top supplier-supplier exposures #######################################

proj_edges <- igraph::as_data_frame(proj_suppliers, what = "edges") |>
  as_tibble() |>
  rename(shared_components = weight) |>
  arrange(desc(shared_components))

proj_edges |> head(10)


# 4. Visualize ###############################################################
#
# A bipartite layout puts suppliers on one side, components on the
# other. It's not always the prettiest, but it's the most honest
# rendering of a bipartite graph.

# Run inside an RStudio session for an interactive plot.
plot(
  g,
  layout      = igraph::layout_as_bipartite(g),
  vertex.size = ifelse(igraph::V(g)$kind == "supplier", 4, 2.5),
  vertex.color = ifelse(igraph::V(g)$kind == "supplier", "#1f77b4", "#d62728"),
  vertex.label = NA,
  edge.color   = "#cccccc",
  edge.width   = 0.4,
  main         = "Bipartite supplier <-> component network"
)


# 5. Learning Check ##########################################################
#
# QUESTION: In the supplier-supplier projection (where two suppliers are
# linked if they share at least one component), what is the degree of
# supplier "S017"? Put differently: how many *other* suppliers share at
# least one component with S017?

s017 <- which(igraph::V(proj_suppliers)$name == "S017")
answer <- igraph::degree(proj_suppliers, v = s017)
answer
