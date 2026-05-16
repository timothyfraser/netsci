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
#'
#' The point: visualization is partly a tool for *finding the question*.
#' Aggregation reveals signal.


# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `dplyr` and `tidyr` for the grouping pipeline, `ggplot2` + `viridis`
# for the three figures, `here` for path resolution.
library(dplyr)
library(tidyr)
library(ggplot2)
library(viridis)
library(here)

## 0.2 Load helpers ##########################################################

# `make_enriched()` does the double join from Case 02 in one call so we
# can focus on aggregation here.
source(here::here("code", "03_aggregation", "functions.R"))

cat("\n🚀 Case Study 03 — Aggregation (R)\n")
cat("   Same network at three resolutions: station -> neighborhood -> quintile.\n\n")

## 0.3 Load data #############################################################

edges    <- load_edges()
stations <- load_stations()
edges    |> head()
stations |> head()
cat(sprintf("✅ Loaded %d trip rows and %d stations.\n",
            nrow(edges), nrow(stations)))


# 1. Enrich edges with both-side traits ######################################
#
# The helper joins each edge with the start-station's traits AND the
# end-station's traits (renaming to start_nbhd / end_nbhd, etc.). This
# is exactly the "double join, with renames" lesson from case 02.

enriched <- make_enriched(edges, stations)
enriched |> head()
nrow(enriched)
cat(sprintf("✅ Built enriched edge table: %d rows.\n", nrow(enriched)))


# 2. Three resolutions #######################################################

## 2.1 Resolution A — raw station x station ##################################

# Sum trips for each (start, end) station pair. With 500 stations the
# space of possible pairs is 250,000 cells — way too fine to plot as a
# heatmap. The aggregation gives a hairball, useful for nothing but a
# degree histogram.
station_pairs <- enriched |>
  group_by(start_code, end_code) |>
  summarize(trips = sum(count, na.rm = TRUE), .groups = "drop") |>
  arrange(desc(trips))
nrow(station_pairs)
cat(sprintf("📊 Resolution A: %d station pairs.\n", nrow(station_pairs)))

## 2.2 Resolution B — neighborhood x neighborhood ############################

# Now sum trips by START neighborhood and END neighborhood. 12 x 12 =
# 144 cells max. Visualizable as a heatmap. This is where structure
# begins to appear (the diagonal is heavier than the off-diagonal).
nbhd_pairs <- enriched |>
  group_by(start_nbhd, end_nbhd) |>
  summarize(trips = sum(count, na.rm = TRUE), .groups = "drop")
nrow(nbhd_pairs)
cat(sprintf("📊 Resolution B: %d neighborhood pairs.\n", nrow(nbhd_pairs)))

## 2.3 Resolution C — income quintile x income quintile ######################

# Finally, aggregate to 4 x 4 income-quintile cells and compute a
# percent column so we can read the equity question directly off the
# matrix.
q_pairs <- enriched |>
  group_by(start_quintile, end_quintile) |>
  summarize(trips = sum(count, na.rm = TRUE), .groups = "drop") |>
  mutate(
    total   = sum(trips),
    percent = round(100 * trips / total, 2)
  )

print(q_pairs)
cat(sprintf("📊 Resolution C: 4x4 quintile pairs.\n"))


# 3. Visualize each resolution ###############################################

# Resolution A: degree-like distribution (only honest view at 500 nodes).
# Each station's "trip volume" = sum of trips out + sum of trips in.
station_totals <- bind_rows(
  station_pairs |> group_by(code = start_code) |> summarize(trips = sum(trips)),
  station_pairs |> group_by(code = end_code)   |> summarize(trips = sum(trips))
) |>
  group_by(code) |>
  summarize(trips = sum(trips), .groups = "drop")

ggplot(station_totals, aes(x = trips)) +
  geom_histogram(bins = 40, fill = "#3a8bc6") +
  labs(x     = "trips touching this station (in or out)",
       y     = "# stations",
       title = "Resolution A — station-level trip volume") +
  theme_classic(base_size = 13)

# Resolution B: 12x12 heatmap. Diagonal heavier = neighborhood stickiness.
ggplot(nbhd_pairs,
       aes(x = start_nbhd, y = end_nbhd, fill = trips)) +
  geom_tile(color = "white") +
  scale_fill_viridis(option = "mako") +
  labs(title = "Resolution B — neighborhood x neighborhood",
       x     = "Starting neighborhood",
       y     = "Ending neighborhood") +
  theme_classic(base_size = 12) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

# Resolution C: 4x4 heatmap with the percentages drawn ON the cells.
ggplot(q_pairs,
       aes(x = factor(start_quintile), y = factor(end_quintile),
           fill = percent)) +
  geom_tile(color = "white") +
  geom_text(aes(label = percent), color = "white", size = 5) +
  scale_fill_viridis(option = "mako", begin = 0.2, end = 0.8) +
  labs(x     = "Starting station's income quintile",
       y     = "Ending station's income quintile",
       fill  = "% of trips",
       title = "Resolution C — trips between income quintiles") +
  theme_classic(base_size = 13)


# 4. The point ###############################################################
#
# Resolution A is a hairball. Resolution B (12x12) shows neighborhood
# stickiness — the diagonal is heavier. Resolution C (4x4) makes the
# equity question legible: how much ridership stays in-quintile vs
# crosses quintiles.
#
# Visualization is partly a tool for finding the question. The case
# study calls this "aggregation reveals signal."


# 5. Learning Check ##########################################################
#
# QUESTION: What percentage of all AM rush 2021 trips in this dataset
# stay within the *top* income quintile (Q4 -> Q4)?
#
# HINT: pull from `q_pairs` directly — start_quintile == 4 AND
# end_quintile == 4.

answer <- q_pairs |>
  filter(start_quintile == 4, end_quintile == 4) |>
  pull(percent)

cat(sprintf("\n📝 Learning Check answer (%%): %.2f\n", answer))

cat("\n🎉 Done. Move on to the case study report when you're ready.\n")
