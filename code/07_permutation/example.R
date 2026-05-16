#' @name example.R
#' @title Case Study 07 — Network Permutation Testing
#' @author <your-name-here>
#' @description
#' The lab walked you through a key idea: when you compute a network
#' statistic (homophily, assortativity, mean within-group edge
#' weight), you need a NULL MODEL to know if the value you saw is
#' "real" or just noise.
#'
#' But — *random with respect to what?* If your network has community
#' structure that you're not controlling for, shuffling labels
#' everywhere gives you a too-easy null. The right comparison is
#' often a BLOCK permutation: shuffle labels within community.
#'
#' We'll do both, on a synthetic network engineered to make the two
#' nulls disagree dramatically.


# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `igraph` for assortativity. `dplyr`/`tibble` for tidy results, ggplot
# for the two-null distribution plot.
library(dplyr)
library(tibble)
library(ggplot2)
library(igraph)
library(here)

## 0.2 Load helpers ##########################################################

# `assort_by()` wraps `igraph::assortativity_nominal()`; `permute_labels()`
# shuffles a vertex attribute, optionally within blocks defined by
# another attribute. Both live in functions.R.
source(here::here("code", "07_permutation", "functions.R"))

cat("\n🚀 Case Study 07 — Network Permutation Testing (R)\n")
cat("   Same observed stat, two null models. Watch the p-value change.\n\n")

## 0.3 Load data #############################################################

nodes <- load_nodes()
edges <- load_edges()
g     <- build_graph(nodes, edges)
g
nodes |> head()
cat(sprintf("✅ Loaded graph: %d nodes (demos A vs B in 10 neighborhoods).\n",
            igraph::vcount(g)))


# 1. Observed assortativity ##################################################
#
# Nominal assortativity: positive = same-demo edges over-represented;
# 0 = random; negative = disassortative. This is the number we'll test.

observed <- assort_by(g, "demo")
cat(sprintf("📊 Observed assortativity by `demo`: %.4f\n", observed))


# 2. Null model 1: UNBLOCKED permutation #####################################
#
# Shuffle the `demo` label across ALL nodes, recompute assortativity,
# repeat 500 times. The unblocked null breaks BOTH any demo-edge link
# AND any demo-neighborhood link — it's the "everything is random"
# baseline.

set.seed(42)
n_perm <- 500
null_unblocked <- numeric(n_perm)
for (i in seq_len(n_perm)) {
  g_perm <- permute_labels(g, "demo", block_by = NULL)
  null_unblocked[i] <- assort_by(g_perm, "demo")
}
p_unblocked <- mean(null_unblocked >= observed)
cat(sprintf("🧪 Unblocked null: mean = %+.4f  sd = %.4f  p = %.3f\n",
            mean(null_unblocked), sd(null_unblocked), p_unblocked))


# 3. Null model 2: BLOCK permutation by neighborhood #########################
#
# Shuffle `demo` ONLY within neighborhood. This preserves the
# neighborhood-level composition. A more conservative null, because
# some apparent "homophily" comes from the fact that A's and B's
# already live in different neighborhoods.

null_blocked <- numeric(n_perm)
for (i in seq_len(n_perm)) {
  g_perm <- permute_labels(g, "demo", block_by = "neighborhood")
  null_blocked[i] <- assort_by(g_perm, "demo")
}
p_blocked <- mean(null_blocked >= observed)
cat(sprintf("🧪 Block-permuted null: mean = %+.4f  sd = %.4f  p = %.3f\n",
            mean(null_blocked), sd(null_blocked), p_blocked))


# 4. Visualize ###############################################################

null_df <- bind_rows(
  tibble(null = "Unblocked",      value = null_unblocked),
  tibble(null = "Block-permuted", value = null_blocked)
)

ggplot(null_df, aes(x = value, fill = null)) +
  geom_histogram(alpha = 0.6, position = "identity", bins = 30) +
  geom_vline(xintercept = observed, linetype = "dashed") +
  scale_fill_manual(values = c("Unblocked"      = "#3a8bc6",
                               "Block-permuted" = "#e07b3a")) +
  labs(x     = "Nominal assortativity by `demo`",
       y     = "# of permutations",
       title = "Two null models, two p-values",
       fill  = "Null model") +
  theme_classic(base_size = 13)


# 5. The take-home ###########################################################
#
# Compare the two p-values. The UNBLOCKED null is centered well below
# the observed — so unblocked says "very significant homophily". The
# BLOCKED null is centered AT OR ABOVE the observed — so blocked says
# "actually, this network is no more demographically homophilous than
# you'd expect from the fact that A's and B's already live in
# different neighborhoods."
#
# This is the canonical mistake the case study warns against. If you
# fit the wrong null model, you get the wrong answer with great
# confidence.


# 6. Learning Check ##########################################################
#
# QUESTION: What is the *block-permuted* p-value for assortativity by
# `demo`? (Use neighborhood as the block. 500 permutations, seed 42.)
# Report to 3 decimal places.

cat(sprintf("\n📝 Learning Check answer: %.3f\n", p_blocked))

cat("\n🎉 Done. Move on to the case study report when you're ready.\n")
