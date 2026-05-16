#' @name example.R
#' @title Case Study 08 — Sampling Big Networks
#' @author <your-name-here>
#' @description
#' You can't analyze every node in a million-node network on a laptop.
#' So we sample. But sampling is not neutral — each strategy preserves
#' some properties and distorts others.
#'
#' Data: Hurricane Dorian evacuation flows over Florida county
#' subdivisions, Aug 28 - Sep 10, 2019. Each edge is a (from, to,
#' date_time, evacuation) row where `evacuation` is how many MORE
#' local Facebook users moved between two cities in that 8-hour
#' window than usual. The original sts workshop 29C_databases.R
#' covers this at the Gulf-states scale; we trim to Florida and the
#' crisis weeks.
#'
#' We will:
#'   1. Compute baseline per-time-slice stats on the full network.
#'   2. Apply three sampling strategies (ego, edgewise, spatial buffer).
#'   3. Compare each against the population over time.


# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `dplyr`/`tidyr` for the per-slice aggregations, `sf` for the spatial
# buffer (the only part of this script that needs spatial libraries),
# `ggplot2` for the comparison figure.
library(dplyr)
library(tidyr)
library(ggplot2)
library(sf)
library(here)

## 0.2 Load helpers ##########################################################

# `slice_stats()` computes the per-time-slice network statistics
# (edgeweight, share of nodes touched, etc.) for any edge subset.
# That's the workhorse we'll reuse on every sample.
source(here::here("code", "08_sampling", "functions.R"))

cat("\n🚀 Case Study 08 — Sampling Big Networks (R)\n")
cat("   Three sampling strategies vs population. Which one preserves the truth?\n\n")

## 0.3 Load data #############################################################

nodes <- load_nodes()
edges <- load_edges()
cs    <- load_subdivisions()
cat(sprintf("✅ Loaded %d nodes, %d edges, %d subdivisions.\n",
            nrow(nodes), nrow(edges), nrow(cs)))


# 1. Baseline (population) statistics over time ##############################
#
# We compute four numbers per 8-hour slice: total edgeweight, share of
# nodes touched, edge ratio, average edgeweight per node. The figure
# at the end compares each sample's time series to this baseline.

n_total <- nrow(nodes)
stats   <- slice_stats(edges, n_total)
stats |> head()
cat(sprintf("📊 Baseline: %d time slices computed.\n", nrow(stats)))


# 2. Sampling strategies ######################################################

set.seed(42)  # deterministic samples across runs

## 2.1 Ego-centric: 50 random seed nodes, keep edges touching any of them ####

# An ego sample is biased toward whatever the seeds are. With random
# seeds, the bias averages out, but small samples are still noisy.
ego_nodes <- nodes |> slice_sample(n = 50) |> pull(node)
ego_edges <- edges |> filter(from %in% ego_nodes | to %in% ego_nodes)
ego_stats <- slice_stats(ego_edges, n_total)
cat(sprintf("✅ Ego sample: %d seeds, %d edges retained.\n",
            length(ego_nodes), nrow(ego_edges)))

## 2.2 Edgewise: 10,000 random edges #########################################

# Uniform random sampling of edges. Preserves the marginal edge-weight
# distribution well but tends to leave nodes with low degree under-sampled.
edge_sample <- edges |> slice_sample(n = 10000)
edge_stats  <- slice_stats(edge_sample, n_total)
cat(sprintf("✅ Edge sample: %d edges.\n", nrow(edge_sample)))

## 2.3 Spatial buffer: nodes within 200 km of Miami ##########################

# Drop the handful of nodes whose centroid couldn't be computed (a
# subdivision present in the node table but missing from the trimmed
# geojson). sf is strict about NAs in coordinates.
nodes_geo <- nodes |> filter(!is.na(x), !is.na(y))

# Use Miami as our point of interest (POI). Project to a meter-based
# CRS so the 200 km buffer is geometrically meaningful, then back.
miami <- nodes_geo |> filter(geoid == "1208692158") |> slice(1)
poi <- sf::st_as_sf(
  data.frame(x = miami$x, y = miami$y),
  coords = c("x", "y"), crs = 4326
)
buf <- poi |>
  sf::st_transform(3857) |>
  sf::st_buffer(dist = 200 * 1000) |>
  sf::st_transform(4326)

node_pts     <- sf::st_as_sf(nodes_geo, coords = c("x", "y"), crs = 4326)
nodes_in_buf <- sf::st_join(node_pts, buf, join = sf::st_within, left = FALSE)
ids_in       <- nodes_in_buf$node

# Keep only edges where BOTH endpoints are inside the buffer.
buf_edges <- edges |> filter(from %in% ids_in & to %in% ids_in)
buf_stats <- slice_stats(buf_edges, n_total)
cat(sprintf("✅ Buffer sample: %d nodes within 200 km of Miami, %d edges.\n",
            length(ids_in), nrow(buf_edges)))


# 3. Compare ##################################################################

bind_rows(
  stats     |> mutate(strategy = "Population"),
  ego_stats |> mutate(strategy = "Ego-centric"),
  edge_stats|> mutate(strategy = "Edgewise"),
  buf_stats |> mutate(strategy = "Spatial buffer")
) |>
  ggplot(aes(x = date_time, y = avg_edgeweight, color = strategy)) +
  geom_line() +
  labs(y     = "avg edgeweight per node",
       title = "Sample vs population — avg edgeweight per node",
       x     = NULL) +
  theme_classic(base_size = 12) +
  theme(axis.text.x = element_text(angle = 30, hjust = 1))


# 4. Which strategy best preserves avg_edgeweight? ###########################
#
# Preservation = max absolute deviation from the population time
# series. Smaller deviation = better preservation. We pick the winner
# by which strategy minimizes that max.

max_abs_dev <- function(sample_stats) {
  merged <- inner_join(
    stats        |> select(date_time, pop  = avg_edgeweight),
    sample_stats |> select(date_time, samp = avg_edgeweight),
    by = "date_time"
  )
  max(abs(merged$pop - merged$samp))
}

mad <- c(
  ego_centric    = max_abs_dev(ego_stats),
  edgewise       = max_abs_dev(edge_stats),
  spatial_buffer = max_abs_dev(buf_stats)
)
print(mad)
winner <- names(which.min(mad))
cat(sprintf("📊 Best preservation: %s\n", winner))


# 5. Learning Check ##########################################################
#
# QUESTION: Of the three sampling strategies above (ego-centric,
# edgewise, spatial buffer around Miami), which one best preserves
# the population's `avg_edgeweight` time series — measured by the
# smallest max-absolute-deviation? Submit the strategy name.

cat(sprintf("\n📝 Learning Check answer: %s\n", winner))

cat("\n🎉 Done. Move on to the case study report when you're ready.\n")
