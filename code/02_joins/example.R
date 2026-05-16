#' @name example.R
#' @title Case Study 02 — Network Joins
#' @author <your-name-here>
#' @description
#'
#' You've worked through the Network Joins lab in the browser. Now
#' let's run the same idea on real(ish) data: a slim, Bluebikes-flavored
#' AM-rush-hour-trips edge list (~50,000 rows) and a stations node table
#' (~500 rows) that's been annotated with a demographic flag from the
#' census block group each station sits in.
#'
#' The whole point of this case study: when you have edges and nodes
#' in two separate tables, the way you JOIN them dictates what you can
#' say about the network. We'll do a single-node join, then a
#' double-node join (start *and* end), then aggregate the result to
#' get a quantity of interest. Pay attention to the *renames* — they
#' are not optional polish, they are the thing that keeps you from
#' silently shooting yourself in the foot.


# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `dplyr` is the workhorse for joins. `readr` reads the CSVs (with
# better defaults than base `read.csv`). The rest are visuals and paths.
library(dplyr)
library(readr)
library(tibble)
library(ggplot2)
library(here)
library(stringr)

## 0.2 Load helpers ##########################################################

# Tiny `load_edges()` / `load_stations()` wrappers that resolve paths
# from the repo root so the script runs from anywhere.
source(here::here("code", "02_joins", "functions.R"))

cat("\n🚀 Case Study 02 — Network Joins (R)\n")
cat("   Edges + stations -> single join, then double join, then a quantity of interest.\n\n")

## 0.3 Load data #############################################################

# Two tables: one for edges (one row per trip aggregate) and one for
# nodes (one row per station, with demographic annotation).
edges    <- load_edges()
stations <- load_stations()

# Get used to running head() before doing anything else. The columns:
#   start_code: where the trip started (station ID)
#   end_code:   where the trip ended (station ID)
#   day:        the day the trip happened (YYYY-MM-DD)
#   rush:       "am" — we've already filtered to AM rush
#   count:      number of trips matching this start/end/day combination
edges |> head()

# Stations table columns:
#   code:      station ID (joins to start_code / end_code in edges)
#   cluster:   neighborhood cluster (block group)
#   maj_black: "yes"/"no" — is the station in a majority-Black block group?
#   x, y:      longitude / latitude
stations |> head()

# How big is each table?
nrow(edges)
nrow(stations)
cat(sprintf("✅ Loaded %d trip rows and %d stations.\n", nrow(edges), nrow(stations)))


# 1. Single-Node Join ########################################################
#
# Goal: tag each edge with a TRAIT of its START station — was it in a
# majority-Black block group or not?

## 1.1 The basic left_join ###################################################

# The key insight: the ID variable has a different NAME in each table.
#   - in `edges` it's called `start_code`
#   - in `stations` it's called `code`
# In dplyr we say `by = c("start_code" = "code")`.
edges |>
  left_join(by = c("start_code" = "code"), y = stations) |>
  head()

# That joined in EVERY column from stations. Usually too much.
# Better: subset stations to just what you need BEFORE joining. It
# makes the result table easier to read and saves memory on big joins.
edges |>
  left_join(
    by = c("start_code" = "code"),
    y  = stations |> select(code, maj_black)
  ) |>
  head()

## 1.2 Rename on the way in ##################################################

# After the join above, `maj_black` is still ambiguous — is it the
# start station's demographic or the end station's? Rename it to
# `start_black` *as part of* the select() inside the join. This
# habit will save you 20 minutes of "wait, which side was this?"
# confusion later.

edges_with_start <- edges |>
  left_join(
    by = c("start_code" = "code"),
    y  = stations |> select(code, start_black = maj_black)
  )

edges_with_start |> head()

## 1.3 A first quantity of interest ##########################################

# Of all AM rush rides in 2021, how many started in a majority-Black
# block group?
edges_with_start |>
  group_by(start_black) |>
  summarize(trips = sum(count, na.rm = TRUE)) |>
  ungroup()
# Rows where `start_black` is NA mean the START station wasn't in our
# stations table — i.e. it's outside Boston proper. In the real
# Bluebikes data these are Cambridge / Somerville stations.


# 2. Double-Node Join ########################################################
#
# Now we want to know about BOTH ends of the trip. We do a SECOND join
# on `end_code`, and we rename again so the two demographics don't
# clobber each other.

## 2.1 Two joins, two renames ################################################

data <- edges |>
  # join in the START station's trait...
  left_join(
    by = c("start_code" = "code"),
    y  = stations |> select(code, start_black = maj_black)
  ) |>
  # ...then join in the END station's trait.
  left_join(
    by = c("end_code" = "code"),
    y  = stations |> select(code, end_black = maj_black)
  ) |>
  # Drop rows where either side is NA — these are stations not in
  # our stations table (out-of-area).
  filter(!is.na(start_black), !is.na(end_black))

data |> head()
cat(sprintf("✅ After double-join + NA drop: %d rows.\n", nrow(data)))

## 2.2 An aggregate quantity of interest #####################################

# How many trips happened between EACH of the four demographic
# combinations (yes->yes, yes->no, no->yes, no->no)?
stat <- data |>
  group_by(start_black, end_black) |>
  summarize(trips = sum(count, na.rm = TRUE), .groups = "drop") |>
  mutate(
    total   = sum(trips),
    percent = round(100 * trips / total, 1)
  )

print(stat)
cat(sprintf("📊 Total trips across all four cells: %d\n", sum(stat$trips)))


# 3. A quick visual ##########################################################
#
# A 2x2 heatmap of trips by start-demographic x end-demographic. This
# is the simplest possible "network communication" visualization, and
# it's often the most honest one.

ggplot(stat, aes(x = start_black, y = end_black, fill = percent)) +
  geom_tile(color = "white") +
  geom_text(aes(label = percent), color = "white", size = 6) +
  scale_fill_viridis_c(option = "mako", begin = 0.2, end = 0.8) +
  labs(
    x        = "Starting station\nin majority-Black block group?",
    y        = "Ending station\nin majority-Black block group?",
    fill     = "% of trips",
    subtitle = "AM rush 2021 — slim Bluebikes-flavored sample"
  ) +
  theme_classic(base_size = 13)


# 4. Why renames matter (the silent-bug demo) ################################
#
# To drive the point home: try the same double-join WITHOUT renaming
# `maj_black`. What does dplyr do? It auto-suffixes them as `.x` and `.y`,
# which (a) is ugly, and (b) means you can't tell at a glance which side
# is which.

bad <- edges |>
  left_join(stations |> select(code, maj_black),
            by = c("start_code" = "code")) |>
  left_join(stations |> select(code, maj_black),
            by = c("end_code"   = "code"))

bad |> head()
# Notice `maj_black.x` and `maj_black.y`. You can survive this, but
# in any non-trivial pipeline it's a recipe for misreading your own
# code in two weeks. Rename on the way in.


# 5. Learning Check ##########################################################
#
# QUESTION: Of AM rush rides in 2021 in this slim dataset, how many
# trips started in a majority-Black block group AND ended in a
# majority-Black block group?
#
# HINT: you've already computed `stat` above. Find the row where
# start_black == "yes" and end_black == "yes" and read off `trips`.

answer <- stat |>
  filter(start_black == "yes", end_black == "yes") |>
  pull(trips)

cat(sprintf("\n📝 Learning Check answer: %d\n", answer))

# Reminder: this is a synthetic-but-deterministic dataset. Your answer
# should be the SAME as your classmates'. If it isn't, your random
# seed has drifted somewhere.

cat("\n🎉 Done. Move on to the case study report when you're ready.\n")
