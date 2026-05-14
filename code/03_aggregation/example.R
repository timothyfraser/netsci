#' @name example.R
#' @title Case Study 03 — Aggregation
#' @author <your-name-here>
#' @description
#' The interactive lab showed you the same network at three
#' resolutions: raw stations, neighborhood, income quintile. Each
#' resolution tells a different story. This script does the same in code.
#'
#' Data:
#'   - 500 stations, each tagged with a neighborhood (1 of 12) and an
#'     income quintile (1..4, 4 = wealthiest).
#'   - 40,000 AM rush 2021 trip rows.


# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

library(dplyr)
library(tidyr)
library(ggplot2)
library(viridis)
library(here)
library(arrow)

## 0.2 Load helpers ##########################################################

source(here::here("code", "03_aggregation", "functions.R"))

## 0.3 Load data #############################################################

edges    <- load_edges()
stations <- load_stations()
edges    |> head()
stations |> head()


# 1. Enrich edges with both-side traits ######################################

enriched <- make_enriched(edges, stations)
enriched |> head()
nrow(enriched)


# 2. Three resolutions #######################################################

## 2.1 Resolution A — raw station x station ##################################

station_pairs <- enriched |>
  group_by(start_code, end_code) |>
  summarize(trips = sum(count, na.rm = TRUE), .groups = "drop") |>
  arrange(desc(trips))

# 500 x 500 -> up to 250,000 cells. In practice much sparser, but
# still too fine to visualize as a heatmap.
nrow(station_pairs)

## 2.2 Resolution B — neighborhood x neighborhood ############################

nbhd_pairs <- enriched |>
  group_by(start_nbhd, end_nbhd) |>
  summarize(trips = sum(count, na.rm = TRUE), .groups = "drop")
# 12 x 12 = up to 144 cells. Now we can actually visualize it.
nrow(nbhd_pairs)

## 2.3 Resolution C — income quintile x income quintile ######################

q_pairs <- enriched |>
  group_by(start_quintile, end_quintile) |>
  summarize(trips = sum(count, na.rm = TRUE), .groups = "drop") |>
  mutate(
    total   = sum(trips),
    percent = round(100 * trips / total, 2)
  )

q_pairs


# 3. Visualize each resolution ###############################################

# Resolution A: degree-like distribution (only honest view at 500 nodes).
station_totals <- bind_rows(
  station_pairs |> group_by(code = start_code) |> summarize(trips = sum(trips)),
  station_pairs |> group_by(code = end_code)   |> summarize(trips = sum(trips))
) |>
  group_by(code) |>
  summarize(trips = sum(trips), .groups = "drop")

ggplot(station_totals, aes(x = trips)) +
  geom_histogram(bins = 40, fill = "#3a8bc6") +
  labs(x = "trips touching this station (in or out)",
       y = "# stations",
       title = "Resolution A — station-level trip volume") +
  theme_classic(base_size = 13)

# Resolution B: 12x12 heatmap
ggplot(nbhd_pairs,
       aes(x = start_nbhd, y = end_nbhd, fill = trips)) +
  geom_tile(color = "white") +
  scale_fill_viridis(option = "mako") +
  labs(title = "Resolution B — neighborhood x neighborhood",
       x = "Starting neighborhood",
       y = "Ending neighborhood") +
  theme_classic(base_size = 12) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

# Resolution C: 4x4 heatmap with percentages
ggplot(q_pairs,
       aes(x = factor(start_quintile), y = factor(end_quintile),
           fill = percent)) +
  geom_tile(color = "white") +
  geom_text(aes(label = percent), color = "white", size = 5) +
  scale_fill_viridis(option = "mako", begin = 0.2, end = 0.8) +
  labs(x = "Starting station's income quintile",
       y = "Ending station's income quintile",
       fill = "% of trips",
       title = "Resolution C — trips between income quintiles") +
  theme_classic(base_size = 13)


# 4. The point ###############################################################
#
# Resolution A is a hairball. Resolution B (12x12) shows
# neighborhood stickiness — the diagonal is heavier. Resolution C
# (4x4) makes the equity question legible: how much ridership stays
# in-quintile vs crosses quintiles.
#
# Visualization is partly a tool for finding the question. The case
# study calls this "aggregation reveals signal."


# 5. Learning Check ##########################################################
#
# QUESTION: What percentage of all AM rush 2021 trips in this dataset
# stay within the *top* income quintile (Q4 -> Q4)?

answer <- q_pairs |>
  filter(start_quintile == 4, end_quintile == 4) |>
  pull(percent)

answer
