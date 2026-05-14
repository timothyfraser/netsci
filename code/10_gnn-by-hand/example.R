#' @name example.R
#' @title Case Study 10 — GNN by Hand (R stub)
#' @author <your-name-here>
#' @description
#'
#' Graph Neural Networks are one of the cases where the Python
#' ecosystem is meaningfully ahead of R. There is no widely-used,
#' well-maintained R port of PyTorch Geometric, and rolling your own
#' GCN in pure R for teaching is awkward (matrix ops are fine; the
#' surrounding tooling is not).
#'
#' So this case study is **Python-primary**. See `example.py` in this
#' folder for the full forward-pass walkthrough.
#'
#' If you'd like to stay in RStudio while running the Python script,
#' you can call it via `reticulate`:
#'
#'   library(reticulate)
#'   reticulate::use_python("/usr/bin/python3")  # adjust as needed
#'   reticulate::source_python(here::here("code", "10_gnn-by-hand",
#'                                        "example.py"))
#'
#' That will execute `example.py` in your R session and import the
#' resulting numpy arrays / pandas DataFrames as R objects.
#'
#' For the LEARNING CHECK and the PROJECT, use the Python version.
#' The Python script prints the answer at the end.

stop(
  "Case 10 (GNN by hand) is Python-primary. Run `example.py` instead. ",
  "See the head of this file for a reticulate snippet if you want ",
  "to call the Python from R."
)
