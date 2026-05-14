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

library(dplyr)        # for left_join, group_by, summarize
library(readr)        # for any csv work
library(readr)        # for read_csv
library(tibble)
library(ggplot2)
library(here)
library(stringr)

## 0.2 Load helpers ##########################################################

# These are tiny wrappers around `read_parquet()` that resolve paths for us.
source(here::here("code", "02_joins", "functions.R"))

## 0.3 Load data #############################################################

# Two tables: one for edges, one for nodes.
edges    <- load_edges()
stations <- load_stations()

# Take a look — get used to running head() before doing anything else.
edges |> head()
# start_code: where the trip started (station ID)
# end_code:   where the trip ended (station ID)
# day:        the day the trip happened (YYYY-MM-DD)
# rush:       "am" — we've already filtered to AM rush
# count:      how many trips matched this start/end/day combination

stations |> head()
# code:      station ID (joins to start_code / end_code in edges)
# cluster:   which neighborhood cluster (block group) the station is in
# maj_black: "yes"/"no" — is the station in a majority-Black block group?
# x, y:      longitude / latitude

# How big is each table?
nrow(edges)
nrow(stations)


# 1. Single-Node Join ########################################################
#
# Goal: tag each edge with a TRAIT of its START station — was it in a
# majority-Black block group or not?

## 1.1 The basic left_join ####################################################

# The key insight: the ID variable has a different NAME in each table.
#   - in `edges` it's called `start_code`
#   - in `stations` it's called `code`
# In dplyr we say `by = c("start_code" = "code")`.
edges |>
  left_join(by = c("start_code" = "code"), y = stations) |>
  head()

# That joined in EVERY column from stations. That's usually too much.
# Better: subset stations down to just what you need before joining.

edges |>
  left_join(
    by = c("start_code" = "code"),
    y  = stations |> select(code, maj_black)
  ) |>
  head()

## 1.2 Rename on the way in ##################################################

# It's still ambiguous what `maj_black` means after this join — is it
# the start station's demographic or the end station's? Rename to make
# it explicit. This habit will save you 20 minutes of confusion later.

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
# Note: rows where `start_black` is NA mean the START station wasn't
# in our stations table — i.e. the station is outside Boston proper.
# In the real Bluebikes data these are Cambridge / Somerville stations.


# 2. Double-Node Join ########################################################
#
# Now we want to know about BOTH ends of the trip. We do a second join
# on `end_code`, and we rename again so we don't clobber the first one.

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

stat


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
    x = "Starting station\nin majority-Black block group?",
    y = "Ending station\nin majority-Black block group?",
    fill = "% of trips",
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
# Write the dplyr code that returns a single number. Then put that
# number into the learning-check form on the website.
#
# HINT: you've already computed `stat` above. Find the row where
# start_black == "yes" and end_black == "yes" and read off `trips`.

answer <- stat |>
  filter(start_black == "yes", end_black == "yes") |>
  pull(trips)

answer

# (Reminder: this is a synthetic-but-deterministic dataset — your
# answer should be the SAME as your classmates'. If it isn't, your
# random seed has drifted somewhere.)
