#!/usr/bin/env Rscript
# ============================================================================
# aggregate.R — turn per-student scores.json files into a cross-persona view.
#
#   Rscript harness/aggregate.R runs
#
# Reads runs/<id>/scores.json for every persona and writes:
#   runs/_matrix_friction.csv   lab x student friction (1-5)
#   runs/_matrix_clarity.csv    lab x student clarity  (1-5)
#   runs/_summary.md            overall ratings, retention cliffs, tallied fixes
#
# Style: tidyverse, base pipe |>, per the repo CLAUDE.md.
# ============================================================================
suppressPackageStartupMessages({
  library(jsonlite); library(dplyr); library(tidyr)
  library(purrr); library(readr); library(stringr); library(tibble)
})

`%||%` <- function(a, b) if (is.null(a) || length(a) == 0) b else a

args <- commandArgs(trailingOnly = TRUE)
runs_dir <- if (length(args) >= 1) args[[1]] else "runs"

score_files <- list.files(runs_dir, pattern = "^scores\\.json$",
                          recursive = TRUE, full.names = TRUE)
if (length(score_files) == 0) stop("No scores.json found under ", runs_dir)

students <- map(score_files, ~ fromJSON(.x, simplifyVector = FALSE))
ids <- map_chr(students, ~ .x$student %||% "unknown")
message("Found ", length(students), " students: ", paste(ids, collapse = ", "))

# ---- per-lab long table ----------------------------------------------------
labs_long <- map_dfr(students, function(s) {
  if (is.null(s$labs) || length(s$labs) == 0) return(tibble())
  map_dfr(s$labs, function(l) {
    tibble(
      student  = s$student %||% NA_character_,
      lab      = str_c(l$id %||% "??", "_", l$name %||% ""),
      friction = as.numeric(l$friction %||% NA),
      clarity  = as.numeric(l$clarity  %||% NA),
      minutes  = as.numeric(l$minutes  %||% NA),
      ran      = l$ran %||% NA_character_
    )
  })
})
if (nrow(labs_long) == 0)
  stop("No per-lab entries found in any scores.json (check the 'labs' arrays).")

write_matrix <- function(df, value_col, path) {
  m <- df |>
    select(lab, student, all_of(value_col)) |>
    pivot_wider(names_from = student, values_from = all_of(value_col)) |>
    arrange(lab)
  write_csv(m, path)
  m
}
fric_mat <- write_matrix(labs_long, "friction", file.path(runs_dir, "_matrix_friction.csv"))
clar_mat <- write_matrix(labs_long, "clarity",  file.path(runs_dir, "_matrix_clarity.csv"))

# ---- overall per-student table ---------------------------------------------
overall <- map_dfr(students, function(s) {
  tibble(
    student        = s$student %||% NA_character_,
    track          = s$track %||% NA_character_,
    setup_friction = as.numeric(s$setup_friction %||% NA),
    almost_dropped = s$almost_dropped %||% NA_character_,
    recommend      = as.numeric(s$recommend %||% NA),
    job_ready      = as.numeric(s$job_ready %||% NA),
    total_hours    = sum(as.numeric(unlist(s$weekly_hours %||% list())), na.rm = TRUE)
  )
})

# ---- retention cliffs: labs where >=2 students hit friction >=4 ------------
cliffs <- labs_long |>
  filter(!is.na(friction)) |>
  group_by(lab) |>
  summarise(n_high = sum(friction >= 4), who = str_c(student[friction >= 4], collapse = ", "),
            .groups = "drop") |>
  filter(n_high >= 2) |>
  arrange(desc(n_high))

dropped <- overall |>
  filter(!is.na(almost_dropped) & almost_dropped != "null" & almost_dropped != "") |>
  select(student, almost_dropped)

# ---- tally fixes named by >=2 students (loose normalized match) ------------
fixes <- map_dfr(students, function(s) {
  fx <- unlist(s$top_fixes %||% list())
  if (length(fx) == 0) return(tibble(student = character(), fix = character()))
  tibble(student = s$student %||% NA_character_, fix = fx)
})
if (nrow(fixes) == 0) fixes <- tibble(student = character(), fix = character(), key = character())
fixes <- fixes |>
  filter(!is.na(fix), str_trim(fix) != "") |>
  mutate(key = fix |> str_to_lower() |> str_replace_all("[^a-z0-9 ]", "") |> str_squish())

fix_tally <- fixes |>
  group_by(key) |>
  summarise(n = n_distinct(student),
            example = first(fix),
            who = str_c(unique(student), collapse = ", "), .groups = "drop") |>
  filter(n >= 2) |>
  arrange(desc(n))

# ---- write summary.md ------------------------------------------------------
overall_rows <- overall |>
  mutate(across(everything(), as.character)) |>
  pmap_chr(function(student, track, setup_friction, almost_dropped, recommend, job_ready, total_hours)
    str_glue("| {student} | {track} | {setup_friction} | {recommend} | {job_ready} | {total_hours} | {almost_dropped} |"))
overall_tbl <- c(
  "| student | track | setup_friction | recommend | job_ready | total_hrs | almost_dropped |",
  "|---|---|---|---|---|---|---|", overall_rows)

md <- c(
  "# SYSEN 5470 — AI Student Run Summary", "",
  str_glue("_{length(students)} personas: {paste(ids, collapse = ', ')}_"), "",
  "## Overall ratings", "",
  overall_tbl, "",
  "## Retention cliffs (labs where 2+ students hit friction >= 4)", "",
  if (nrow(cliffs) == 0) "_None — no lab tripped up 2+ students._" else
    c("| lab | # high-friction | who |", "|---|---|---|",
      pmap_chr(cliffs, function(lab, n_high, who) str_glue("| {lab} | {n_high} | {who} |"))),
  "",
  "## 'Almost dropped' moments", "",
  if (nrow(dropped) == 0) "_No persona reported almost dropping._" else
    c("| student | lab |", "|---|---|",
      pmap_chr(dropped, function(student, almost_dropped) str_glue("| {student} | {almost_dropped} |"))),
  "",
  "## Highest-ROI fixes (named by 2+ different students)", "",
  if (nrow(fix_tally) == 0) "_No fix was independently named by 2+ students._" else
    c("| # students | fix (example wording) | who |", "|---|---|---|",
      pmap_chr(fix_tally, function(key, n, example, who) str_glue("| {n} | {example} | {who} |"))),
  "",
  "## How to read this", "",
  "- A **friction row red across many personas** (see `_matrix_friction.csv`) = a course problem; fix the lab.",
  "- A row red for **one** persona = a fit problem for that learner type; add an optional on-ramp, don't rebuild.",
  "- Compare **stats-strong** (kenji, priya) vs **stats-averse** (sofia, marcus) on labs 07 & 09 to locate the inference-scaffolding gap.",
  "- Compare **Python track** (priya, marcus, aisha) vs **R track** (sofia, kenji, david) on shared labs to catch track-parity gaps.",
  ""
)
writeLines(unlist(md), file.path(runs_dir, "_summary.md"))

message("Wrote: ",
        file.path(runs_dir, "_summary.md"), ", _matrix_friction.csv, _matrix_clarity.csv")
