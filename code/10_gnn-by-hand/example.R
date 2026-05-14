#' @name example.R
#' @title Case Study 10 — GNN by Hand (R: base-R re-implementation)
#' @author <your-name-here>
#' @description
#' Graph Neural Networks are one of the few cases where the Python
#' ecosystem is meaningfully ahead of R. There is no widely-used,
#' well-maintained R port of PyTorch Geometric. So this case study
#' is **Python-primary** — see `example.py` for the full walkthrough
#' on both the tiny 6-node toy and the 200-node project-scale
#' network.
#'
#' This R file does the *Learning Check math* in base R: ~30 lines of
#' matrix algebra that reproduce the Python script's final embedding
#' for node 4 on the tiny network. It gives you a way to verify the
#' answer without leaving R.
#'
#' For the PROJECT, switch to Python. If you'd like to stay in
#' RStudio, call the Python file via `reticulate`:
#'
#'   library(reticulate)
#'   reticulate::use_python("/usr/bin/python3")  # adjust as needed
#'   reticulate::source_python(here::here("code", "10_gnn-by-hand",
#'                                        "example.py"))


# 0. Setup ###################################################################

# No package dependencies; everything is base R.


# 1. Tiny network from the case study ########################################

# Each node has 2 input features: (daily_output, defect_rate).
X <- matrix(
  c(0.80, 0.10,
    0.60, 0.20,
    0.40, 0.30,
    0.55, 0.15,
    0.70, 0.05,
    0.30, 0.40),
  ncol = 2, byrow = TRUE
)

# Adjacency with self-loops.
# Edges (0-indexed in Python): (0,4), (1,4), (2,4), (3,4), (4,5).
# In 1-indexed R: (1,5), (2,5), (3,5), (4,5), (5,6).
A <- matrix(0, 6, 6)
edges <- rbind(c(1, 5), c(2, 5), c(3, 5), c(4, 5), c(5, 6))
for (k in seq_len(nrow(edges))) {
  i <- edges[k, 1]; j <- edges[k, 2]
  A[i, j] <- 1; A[j, i] <- 1
}
diag(A) <- 1

# Symmetric normalization: D^{-1/2} A D^{-1/2}
d <- rowSums(A)
D_inv_sqrt <- diag(1 / sqrt(d))
A_norm <- D_inv_sqrt %*% A %*% D_inv_sqrt


# 2. Layer weights (same as example.py) ######################################

W1 <- matrix(c(0.5, -0.2, 0.8,
              -0.7, 0.4, 0.3), nrow = 2, byrow = TRUE)
W2 <- matrix(c(0.6, 0.1, -0.4,
               0.2, 0.7, 0.3,
              -0.5, 0.4, 0.6), nrow = 3, byrow = TRUE)


# 3. Two-layer GCN forward pass ##############################################

# `pmax(0, X)` would silently drop the matrix dimensions; the
# element-wise multiply preserves them.
relu <- function(x) x * (x > 0)

H1 <- relu(A_norm %*% X  %*% W1)
H2 <- relu(A_norm %*% H1 %*% W2)


# 4. Learning Check ##########################################################
#
# QUESTION: With the layer weights W1 and W2 above (symmetric
# normalization, ReLU, self-loops), what is the FINAL embedding (3
# numbers) for node 4 on the tiny network? Round each to 4 decimal
# places, comma-separated.
#
# Node 4 is 0-indexed in Python, which is row index 5 in 1-indexed R.

emb_node4 <- round(H2[5, ], 4)
# Collapse IEEE-754 negative zero to positive zero so the printed
# answer matches example.py byte-for-byte.
emb_node4[emb_node4 == 0] <- 0
cat("Learning Check answer:",
    paste(sprintf("%.4f", emb_node4), collapse = ", "), "\n")
