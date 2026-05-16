#' @name example.R
#' @title Case Study 05 — Supply Chain Resilience
#' @author <your-name-here>
#' @description
#' The interactive lab let you click nodes to "fail" them and watched
#' supply coverage collapse. Here we do the same in code, on a
#' synthetic 580-node 3-tier supply chain.
#'
#' The resilience metric: SUPPLY COVERAGE = fraction of retailers
#' (tier 3) still reachable from at least one supplier (tier 1) after
#' the removals. 1.00 = nothing broken. 0.50 = half of all retailers
#' have lost their last incoming path from a supplier.
#'
#' The point of this case: random failures, high-degree failures, and
#' high-betweenness failures cause DIFFERENT amounts of damage.


# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `igraph` for graph + centrality, `dplyr`/`tidyr` to keep the
# per-strategy attack results tidy and easy to plot.
library(dplyr)
library(tibble)
library(tidyr)
library(igraph)
library(ggplot2)
library(here)

## 0.2 Load helpers ##########################################################

# `supply_coverage()` and `remove_and_score()` live in functions.R.
# They compute the % of retailers still reachable from any supplier,
# before and after a list of victims is deleted.
source(here::here("code", "05_supply-chain", "functions.R"))

cat("\n🚀 Case Study 05 — Supply Chain Resilience (R)\n")
cat("   Three attack strategies on a 580-node 3-tier chain. Which one hurts most?\n\n")

## 0.3 Load data #############################################################

nodes <- load_nodes()
edges <- load_edges()
g     <- build_graph(nodes, edges)

# Tier composition: tier 1 = suppliers, tier 2 = DCs, tier 3 = retailers
nodes |> count(tier)
g
cat(sprintf("✅ Loaded chain: %d nodes (%d suppliers, %d DCs, %d retailers).\n",
            igraph::vcount(g),
            sum(nodes$tier == 1), sum(nodes$tier == 2), sum(nodes$tier == 3)))


# 1. Baseline supply coverage ################################################
#
# Before we break anything, what fraction of retailers are reachable
# from at least one supplier? That's our denominator.

base <- supply_coverage(g)
cat(sprintf("📊 Baseline supply coverage: %.3f\n", base))


# 2. Centrality per tier #####################################################
#
# To target the right nodes we need per-node centrality. For a
# directed network we use both weighted degree (capacity) and
# betweenness. We hold these in a tidy table so the attack loop
# below stays one-liner-clean.

cent <- tibble(
  node_id     = igraph::V(g)$name,
  tier        = igraph::V(g)$tier,
  in_degree   = igraph::degree(g, mode = "in"),
  out_degree  = igraph::degree(g, mode = "out"),
  w_in        = igraph::strength(g, mode = "in",  weights = igraph::E(g)$capacity),
  w_out       = igraph::strength(g, mode = "out", weights = igraph::E(g)$capacity),
  betweenness = igraph::betweenness(g, directed = TRUE)
)

# Most-critical DC by betweenness. These are the candidates an attacker
# would target if they understood the network structure.
top_btwn_dcs <- cent |>
  filter(tier == 2) |>
  arrange(desc(betweenness)) |>
  head(5)
print(top_btwn_dcs)


# 3. Targeted vs random attacks ##############################################
#
# We remove k nodes from tier 2 (DCs) under three strategies:
#   - random
#   - top-k by out-degree (volume hubs)
#   - top-k by betweenness (bridges)
# and track supply coverage as k grows from 0 to 15.

dcs <- cent |> filter(tier == 2)
set.seed(42)  # deterministic random-attack ordering

run_strategy <- function(strategy, ks) {
  vapply(ks, function(k) {
    if (k == 0) return(base)
    if (strategy == "random") {
      victims <- sample(dcs$node_id, size = k)
    } else if (strategy == "out_degree") {
      victims <- dcs |> arrange(desc(out_degree)) |> head(k) |> pull(node_id)
    } else if (strategy == "betweenness") {
      victims <- dcs |> arrange(desc(betweenness)) |> head(k) |> pull(node_id)
    } else {
      stop("unknown strategy")
    }
    remove_and_score(g, victims)
  }, numeric(1))
}

ks      <- 0:15
results <- tibble(
  k           = ks,
  random      = run_strategy("random", ks),
  out_degree  = run_strategy("out_degree", ks),
  betweenness = run_strategy("betweenness", ks)
)

results |> mutate(across(-k, ~round(., 3))) |> print()
cat(sprintf("🧪 At k=10: random=%.3f  out_degree=%.3f  betweenness=%.3f\n",
            results$random[results$k == 10],
            results$out_degree[results$k == 10],
            results$betweenness[results$k == 10]))


# 4. Visualize ###############################################################

results_long <- results |>
  pivot_longer(-k, names_to = "strategy", values_to = "coverage")

ggplot(results_long,
       aes(x = k, y = coverage, color = strategy, shape = strategy)) +
  geom_line() +
  geom_point(size = 2.5) +
  scale_y_continuous(limits = c(0, 1.02)) +
  labs(x     = "# of distribution centers removed (k)",
       y     = "supply coverage (fraction of retailers reachable)",
       title = "Targeted vs random DC failures") +
  theme_classic(base_size = 13)


# 5. Learning Check ##########################################################
#
# QUESTION: After removing the 5 highest-betweenness distribution
# centers, what is the supply coverage? Report to 3 decimal places.

top5_btwn <- dcs |>
  arrange(desc(betweenness)) |>
  head(5) |>
  pull(node_id)

answer <- remove_and_score(g, top5_btwn)

cat(sprintf("\n📝 Learning Check answer: %.3f\n", answer))

cat("\n🎉 Done. Move on to the case study report when you're ready.\n")
