#' @name example.R
#' @title Case Study 10 — GNN by Hand (R via reticulate)
#' @author <your-name-here>
#' @description
#' First, what are we even producing? An EMBEDDING. Where centrality
#' (case 04) gave each node a single number, an embedding gives each node
#' a *vector* — a bundle of several numbers — that captures the node's
#' structural neighborhood. Why not just use betweenness? Because a
#' bundle of numbers carries far more about a node's surroundings than
#' any one score, and it drops straight into a machine-learning model as
#' features (exactly what case 11 does to predict disruptions).
#'
#' The case study lab walked you through a hand-computed forward pass.
#' Here we do it on the same 6-node toy network — but from R. R has no
#' mature Graph Neural Network library, so rather than re-derive the math
#' we borrow the course's canonical numpy implementation (`functions.py`)
#' through `reticulate`. R drives the workflow and does the data loading,
#' plotting, and reporting; Python does the four lines of GCN matrix
#' algebra. Because the numbers run through the exact same code as
#' `example.py`, the Learning Check comes out byte-for-byte identical.
#'
#' Step by step:
#'   1. Build the adjacency matrix (with self-loops).
#'   2. Symmetric-normalize it (D^{-1/2} A D^{-1/2}).
#'   3. Apply a single GCN layer: H = ReLU(A_norm %*% X %*% W).
#'   4. Stack a second layer.
#'   5. Read off the embedding for the bottleneck node (node 4).
#'
#' Then we run the same pipeline on a 200-node project-scale network so
#' you can see GNN embeddings at non-toy scale.


# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `reticulate` is the bridge to the Python GCN functions; `ggplot2` draws
# the embedding scatter; `here` keeps file paths robust.
library(reticulate)
library(ggplot2)
library(here)

## 0.2 Load helpers ##########################################################

# PRE-FLIGHT CHECK (read this if you've never used reticulate). This is the
# one lab that drives Python from R, so the only thing that can go wrong is
# Python not being reachable. We check BEFORE sourcing functions.R (which
# triggers the Python setup) so you get a friendly message instead of a
# cryptic import error halfway through.
#
# If this stops with "Python not found":
#   - reticulate::install_python()         # installs a private Python, or
#   - Sys.setenv(RETICULATE_PYTHON = "/path/to/python-with-numpy")
#   then restart R and re-run. On a current reticulate (>= 1.41) the numpy +
#   pandas requirements are provisioned automatically (see functions.R).
if (!reticulate::py_available(initialize = TRUE)) {
  stop("Python not found for reticulate. Run reticulate::install_python() ",
       "or set RETICULATE_PYTHON to a Python that has numpy + pandas, ",
       "then restart R and re-run this script.")
}
cat("✅ reticulate found Python — bridging to the numpy GCN code.\n")

# functions.R gives us the R-native loaders (load_tiny / load_large) and
# the `gcn` Python module handle (gcn$adjacency / gcn$normalize /
# gcn$gcn_layer). Sourcing it triggers the one-time Python setup.
source(here::here("code", "10_gnn-by-hand", "functions.R"))

cat("\n🚀 Case Study 10 — GNN by Hand (R via reticulate)\n")
cat("   Two-layer GCN, no native R GNN lib. We drive numpy's functions.py from R.\n\n")

## 0.3 Load data #############################################################

tiny  <- load_tiny()
nodes <- tiny$nodes
edges <- tiny$edges
print(nodes)
print(edges)
cat(sprintf("✅ Loaded tiny network: %d nodes, %d edges.\n",
            nrow(nodes), nrow(edges)))


# 1. Adjacency and normalization #############################################
#
# Self-loops let each node "send a message to itself" so its own
# features survive into the next layer. Symmetric normalization
# D^{-1/2} A D^{-1/2} stops high-degree nodes from dominating their
# neighbors -- same intuition as degree-normalizing a count in stats:
# divide out how connected a node is so the average isn't swamped by a
# few hubs. Despite the scary notation it's just a rescaling trick.
# These steps are the heart of a GCN -- both come straight from
# functions.py via the `gcn` handle.

A <- gcn$adjacency(nodes, edges, add_self_loops = TRUE)
cat("A (with self-loops):\n")
print(A)

A_norm <- gcn$normalize(A)
cat("A_norm (symmetric-normalized):\n")
print(round(A_norm, 3))


# 2. Feature matrix and weight matrices ######################################
#
# Each node has 2 input features: (daily_output, defect_rate).
# Layer 1 maps 2 -> 3 hidden dims; layer 2 maps 3 -> 3.

X <- as.matrix(nodes[, c("daily_output", "defect_rate")])
cat("X (input features):\n")
print(X)

# Fixed weights for reproducibility — identical to example.py. In a real
# GNN these are learned via gradient descent on an objective; here we
# hard-code them so the whole pipeline is one chain of matrix multiplies.
W1 <- matrix(c( 0.5, -0.2,  0.8,
               -0.7,  0.4,  0.3), nrow = 2, byrow = TRUE)
W2 <- matrix(c( 0.6,  0.1, -0.4,
                0.2,  0.7,  0.3,
               -0.5,  0.4,  0.6), nrow = 3, byrow = TRUE)


# 3. Forward pass ############################################################
#
# H_{l+1} = ReLU(A_norm %*% H_l %*% W_l). The matmul-and-activate happens
# inside gcn$gcn_layer(), the same numpy function example.py calls.
# Why two layers? One layer mixes in each node's IMMEDIATE neighbors
# (1 hop). Stacking a second layer mixes in neighbors-of-neighbors
# (2 hops), so node 4 below can "see" both clusters it sits between.

H1 <- gcn$gcn_layer(A_norm, X,  W1, activation = "relu")
cat("H1 (after layer 1, ReLU):\n")
print(round(H1, 4))

H2 <- gcn$gcn_layer(A_norm, H1, W2, activation = "relu")
cat("H2 (after layer 2, ReLU):\n")
print(round(H2, 4))


# 4. What does node 4 (the bottleneck) end up looking like? ##################
#
# Node 4 sits between two clusters in our 6-node toy. After two GCN
# layers its embedding has absorbed features from both sides. Node 4 is
# 0-indexed in Python, which is row 5 in 1-indexed R.

emb_node4 <- H2[5, ]
cat("Final embedding for node 4 (the bottleneck):\n")
print(round(emb_node4, 4))
cat(sprintf("🧪 Node 4 embedding norm: %.4f\n",
            sqrt(sum(emb_node4^2))))


# 5. The same pipeline on a 200-node project-scale network ###################

large <- load_large()
A_l   <- gcn$normalize(gcn$adjacency(large$nodes, large$edges, add_self_loops = TRUE))
X_l   <- as.matrix(large$nodes[, c("daily_output", "defect_rate")])

H1_l <- gcn$gcn_layer(A_l,  X_l,  W1, activation = "relu")
H2_l <- gcn$gcn_layer(A_l,  H1_l, W2, activation = "relu")
cat(sprintf("📊 Large network embedding shape: %d x %d\n",
            nrow(H2_l), ncol(H2_l)))

# Plot the first two embedding dimensions, colored by whether the node is
# a planted bottleneck (every 25th node), so we can see whether the
# bottlenecks cluster separately after two GCN layers.
bottlenecks <- 25 * 1:7
plot_df <- data.frame(
  dim0  = H2_l[, 1],
  dim1  = H2_l[, 2],
  group = ifelse(large$nodes$node_id %in% bottlenecks,
                 "planted bottlenecks", "regular nodes")
)

p <- ggplot(plot_df, aes(dim0, dim1, color = group, size = group)) +
  geom_point(alpha = 0.7) +
  scale_color_manual(values = c("planted bottlenecks" = "#d62728",
                                "regular nodes"        = "#999999")) +
  scale_size_manual(values = c("planted bottlenecks" = 3, "regular nodes" = 1.4)) +
  labs(x = "embedding dim 0", y = "embedding dim 1",
       title = "After 2 GCN layers, do bottlenecks separate?",
       color = NULL, size = NULL) +
  theme_minimal()

ggsave(here::here("code", "10_gnn-by-hand", "gnn_embeddings.png"),
       p, width = 7, height = 5, dpi = 120)
cat("💾 Saved gnn_embeddings.png\n")


# 6. Learning Check ##########################################################
#
# QUESTION: With the layer weights W1 and W2 defined above (symmetric
# normalization, ReLU, self-loops), what is the FINAL embedding (3
# numbers) for node 4 on the tiny network?
#
# Round each to 4 decimal places. Submit as a comma-separated string.

emb <- round(emb_node4, 4)
# Collapse IEEE-754 negative zero to positive zero so the printed answer
# matches example.py byte-for-byte.
emb[emb == 0] <- 0
answer <- paste(sprintf("%.4f", emb), collapse = ", ")

cat(sprintf("\n📝 Learning Check answer: %s\n", answer))

cat("\n🎉 Done. Move on to the case study report when you're ready.\n")
