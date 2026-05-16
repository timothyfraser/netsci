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
#'      (two suppliers connected if they share a component) — this is
#'      where bipartite networks earn their keep.
#'   5. Find supplier-level structural patterns.


# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `dplyr` and `tibble` for tidy data wrangling. `igraph` is the workhorse
# network library for both R and Python. `here` resolves paths from the
# repo root so the script works no matter where you run it from.
library(dplyr)
library(readr)
library(tibble)
library(igraph)
library(ggplot2)
library(here)

## 0.2 Load helpers ##########################################################

# `functions.R` lives next to this script and contains tiny wrappers
# around `read_csv()` plus a `build_bipartite()` helper. Open it once
# so you know what's behind each loader.
source(here::here("code", "01_build-a-network", "functions.R"))

# Friendly opening banner so you know the script is doing what it should.
cat("\n🚀 Case Study 01 — Build a Network (R)\n")
cat("   Two CSVs in -> one bipartite igraph object out -> a supplier projection.\n\n")

## 0.3 Load data #############################################################

# Two tables: a node list (one row per entity) and an edge list (one row
# per "this supplier ships that component" relationship).
nodes <- load_nodes()
edges <- load_edges()

# Always glance at the first few rows of any table before trusting it.
nodes |> head()
edges |> head()

# How many of each kind of node? How many edges? The `count()` shortcut
# is the dplyr way to do `group_by() |> summarize(n = n())` in one line.
nodes |> count(kind)
nrow(edges)

cat(sprintf("✅ Loaded %d nodes (%d suppliers + %d components) and %d edges.\n",
            nrow(nodes),
            sum(nodes$kind == "supplier"),
            sum(nodes$kind == "component"),
            nrow(edges)))


# 1. Build the graph #########################################################
#
# A graph is just a set of vertices and a set of edges connecting them.
# Our data is already in that shape; we just need to hand the two
# tables to igraph and ask it to wire them up.

## 1.1 The naive way (suppliers and components mixed) ########################

# `build_bipartite()` (defined in functions.R) does two things:
#   (a) calls `igraph::graph_from_data_frame()` to wire up the edges, and
#   (b) sets the bipartite `type` attribute on every vertex (FALSE for
#       suppliers, TRUE for components), which is what igraph needs to
#       know later that this graph is bipartite.
g <- build_bipartite(nodes, edges)

# Printing an igraph object gives you a one-line summary: vertex count,
# edge count, whether it's directed, and which attributes are attached.
g

## 1.2 Bipartite check #######################################################

# `bipartite_mapping()` returns `$res = TRUE` if igraph agrees with our
# manual labeling. A good sanity check.
is_bip <- igraph::bipartite_mapping(g)$res
cat(sprintf("✅ Bipartite? %s\n", if (is_bip) "True" else "False"))


# 2. Inspect basic structure #################################################

## 2.1 Degree distribution by kind ###########################################

# Each node's degree is just "how many edges touch it." We bundle the
# three vertex attributes into one tidy tibble for easy summarizing.
degrees <- tibble::tibble(
  node_id = igraph::V(g)$name,
  kind    = igraph::V(g)$kind,
  degree  = igraph::degree(g)
)

# Suppliers tend to touch ~5-10 components; components are touched by
# anywhere from 1 to ~20 suppliers. Compare the two distributions.
deg_summary <- degrees |>
  group_by(kind) |>
  summarize(
    n      = n(),
    mean   = mean(degree),
    median = median(degree),
    min    = min(degree),
    max    = max(degree),
    .groups = "drop"
  )
print(deg_summary)
cat(sprintf("📊 Mean supplier degree: %.1f   Mean component degree: %.1f\n",
            mean(degrees$degree[degrees$kind == "supplier"]),
            mean(degrees$degree[degrees$kind == "component"])))

## 2.2 Top-degree components (the "shared" ones) #############################

# Which components have the most suppliers shipping them? These are
# the structural pivot points in a one-mode projection — when they
# go offline, many suppliers go offline together.
top_shared <- degrees |>
  filter(kind == "component") |>
  arrange(desc(degree)) |>
  head(10)
print(top_shared)


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

cat(sprintf("🔗 Supplier projection:  %d nodes, %d edges\n",
            igraph::vcount(proj_suppliers),  igraph::ecount(proj_suppliers)))
cat(sprintf("🔗 Component projection: %d nodes, %d edges\n",
            igraph::vcount(proj_components), igraph::ecount(proj_components)))

# Each edge in the suppliers projection has a `weight` attribute equal
# to the NUMBER OF SHARED COMPONENTS between those two suppliers. That
# weight is the closest thing to a "shared-fate" score we get here.

## 3.1 Top supplier-supplier exposures #######################################

# Convert the projection back to a tidy edge-list so we can sort and
# explore it like any other dataframe.
proj_edges <- igraph::as_data_frame(proj_suppliers, what = "edges") |>
  as_tibble() |>
  rename(shared_components = weight) |>
  arrange(desc(shared_components))

# The top of this list is the pair of suppliers most exposed to each
# other — if one is disrupted, the other is most likely to be co-disrupted.
print(proj_edges |> head(10))


# 4. Visualize ###############################################################
#
# A bipartite layout puts suppliers on one side, components on the
# other. It's not always the prettiest layout, but it's the most honest
# rendering of a bipartite graph: you can read off the structure
# without thinking about it.

# Run inside an RStudio session to see the plot interactively; from
# Rscript it goes to the default device.
plot(
  g,
  layout       = igraph::layout_as_bipartite(g),
  vertex.size  = ifelse(igraph::V(g)$kind == "supplier", 4, 2.5),
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

# `V(g)$name == "S017"` returns a logical vector; `which()` gives us
# the integer index igraph needs.
s017   <- which(igraph::V(proj_suppliers)$name == "S017")
answer <- igraph::degree(proj_suppliers, v = s017)

cat(sprintf("\n📝 Learning Check answer: %d\n", answer))

cat("\n🎉 Done. Move on to the case study report when you're ready.\n")
