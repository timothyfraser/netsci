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
#' the removals.
#'
#' The point of this case: random failures, high-degree failures, and
#' high-betweenness failures cause DIFFERENT amounts of damage.


# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

library(dplyr)
library(tibble)
library(tidyr)
library(igraph)
library(ggplot2)
library(here)

## 0.2 Load helpers ##########################################################

source(here::here("code", "05_supply-chain", "functions.R"))

## 0.3 Load data #############################################################

nodes <- load_nodes()
edges <- load_edges()
g     <- build_graph(nodes, edges)

nodes |> count(tier)
g


# 1. Baseline supply coverage ################################################

base <- supply_coverage(g)
cat(sprintf("Baseline supply coverage: %.3f\n", base))


# 2. Centrality per tier #####################################################

cent <- tibble(
  node_id     = igraph::V(g)$name,
  tier        = igraph::V(g)$tier,
  in_degree   = igraph::degree(g, mode = "in"),
  out_degree  = igraph::degree(g, mode = "out"),
  w_in        = igraph::strength(g, mode = "in",  weights = igraph::E(g)$capacity),
  w_out       = igraph::strength(g, mode = "out", weights = igraph::E(g)$capacity),
  betweenness = igraph::betweenness(g, directed = TRUE)
)

# Most-critical DC by betweenness:
cent |>
  filter(tier == 2) |>
  arrange(desc(betweenness)) |>
  head(5)


# 3. Targeted vs random attacks ##############################################

dcs <- cent |> filter(tier == 2)
set.seed(42)

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

results |> mutate(across(-k, ~round(., 3)))


# 4. Visualize ###############################################################

results_long <- results |>
  pivot_longer(-k, names_to = "strategy", values_to = "coverage")

ggplot(results_long,
       aes(x = k, y = coverage, color = strategy, shape = strategy)) +
  geom_line() +
  geom_point(size = 2.5) +
  scale_y_continuous(limits = c(0, 1.02)) +
  labs(x = "# of distribution centers removed (k)",
       y = "supply coverage (fraction of retailers reachable)",
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
round(answer, 3)
