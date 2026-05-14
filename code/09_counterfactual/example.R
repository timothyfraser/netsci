#' @name example.R
#' @title Case Study 09 — Counterfactual Monte Carlo
#' @author <your-name-here>
#' @description
#' You propose an intervention in a network (add a station, add an
#' edge, boost an edge's volume) and want to know if it *actually*
#' improves a metric, or if any apparent improvement is within the
#' noise.
#'
#' The answer: bootstrap-style resampling. Re-draw edge weights from a
#' Poisson centered at observed values, R times, and look at the
#' distribution of your metric. Apply the intervention to each
#' replicate and compare distributions. The 95% CI on the difference
#' tells you whether the effect is real.
#'
#' We use a 180-station synthetic bikeshare network. The metric is
#' weighted average path length. The intervention adds a new direct
#' edge between two stations that are currently far apart.


# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

library(dplyr)
library(ggplot2)
library(igraph)
library(here)

## 0.2 Load helpers ##########################################################

source(here::here("code", "09_counterfactual", "functions.R"))

## 0.3 Load data #############################################################

nodes <- load_nodes()
edges <- load_edges()
g     <- build_graph(nodes, edges)
g


# 1. Baseline weighted APL ###################################################

base_apl <- weighted_apl(g)
cat(sprintf("Baseline weighted APL: %.5f\n", base_apl))


# 2. Pick an intervention ####################################################
#
# Find two stations that are far apart in the current network. We'll
# propose adding a high-ridership edge between them.

dist_mat <- igraph::distances(g, weights = igraph::E(g)$cost)
diag(dist_mat) <- -Inf
ij <- which(dist_mat == max(dist_mat), arr.ind = TRUE)[1, ]
station_a <- igraph::V(g)$name[ij[1]]
station_b <- igraph::V(g)$name[ij[2]]
cat(sprintf("farthest-apart pair: %s <-> %s (cost = %.4f)\n",
            station_a, station_b, dist_mat[ij[1], ij[2]]))

intervention <- tibble(
  from = station_a, to = station_b, ridership = 120
)


# 3. Monte Carlo: baseline vs counterfactual #################################

R <- 500
baseline_apls       <- mc_apls(edges, nodes, R = R, extra = NULL,         seed = 1)
counterfactual_apls <- mc_apls(edges, nodes, R = R, extra = intervention, seed = 1)

diffs <- counterfactual_apls - baseline_apls
ci <- quantile(diffs, probs = c(0.025, 0.975))
cat(sprintf("Counterfactual APL change (mean):     %+.5f\n", mean(diffs)))
cat(sprintf("95%% CI on the change:                 [%+.5f, %+.5f]\n",
            ci[[1]], ci[[2]]))
cat(sprintf("Effect significant at 95%%?            %s\n",
            ci[[2]] < 0 || ci[[1]] > 0))


# 4. Visualize ###############################################################

mc_df <- bind_rows(
  tibble(apl = baseline_apls,       version = "Baseline"),
  tibble(apl = counterfactual_apls, version = "With intervention")
)

p1 <- ggplot(mc_df, aes(x = apl, fill = version)) +
  geom_histogram(alpha = 0.55, position = "identity", bins = 30) +
  labs(x = "weighted APL", y = "# of replicates",
       fill = NULL,
       title = paste0("Two distributions, R=", R, " replicates")) +
  theme_classic(base_size = 12)

p2 <- ggplot(tibble(d = diffs), aes(x = d)) +
  geom_histogram(fill = "#7b3ae0", alpha = 0.7, bins = 30) +
  geom_vline(xintercept = 0, linetype = "dashed") +
  geom_vline(xintercept = ci[[1]], color = "red", linetype = "dotted") +
  geom_vline(xintercept = ci[[2]], color = "red", linetype = "dotted") +
  labs(x = "APL change (counterfactual - baseline)",
       y = "# of replicates",
       title = "Difference distribution + 95% CI") +
  theme_classic(base_size = 12)

print(p1)
print(p2)


# 5. Learning Check ##########################################################
#
# QUESTION: For the intervention "add a high-ridership (~120 rides)
# edge between the two currently-farthest-apart stations" on this
# 180-station network, what is the 95% CI on the change in weighted
# APL (counterfactual - baseline), with R=500 replicates and seed=1?
# Report the LOW end of the CI rounded to 4 decimal places (signed).

cat(sprintf("Learning Check answer (CI low): %.4f\n", ci[[1]]))
