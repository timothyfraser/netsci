#' @name example.R
#' @title Case Study 09 — GNN + XGBoost (R, full pipeline via reticulate)
#' @author <your-name-here>
#' @description
#' The case study lab showed that combining:
#'   - raw static features
#'   - a lag (history) feature
#'   - a GNN-style structural embedding
#' into XGBoost beats any one of them alone. Here we run that full
#' pipeline in R on a synthetic supplier-disruption panel (500 suppliers
#' x 52 weeks).
#'
#' R does almost all of it natively — the loaders, the lag feature, the
#' XGBoost models, and the AUC scoring. The single piece R has no mature
#' library for is the GNN embedding, so we borrow the course's numpy
#' implementation through `reticulate` (see functions.R). The embedding
#' here is a *parameter-free* GCN-style aggregation (mean of in-neighbors'
#' lag_rate, 1 and 2 hops) — same structural signal as a trained GNN, no
#' torch dependency.
#'
#' Pipeline:
#'   1. Load suppliers, edges, and the (supplier, week, disrupted) panel.
#'   2. Add the 4-week lag_rate feature (R).
#'   3. Add 1-hop and 2-hop GNN embeddings of lag_rate (Python via reticulate).
#'   4. Split into train (weeks 0..39) / test (weeks 40..51).
#'   5. Train three XGBoost models on three feature sets; compare AUC.


# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `xgboost` is the model; `dplyr`/`tidyr` wrangle the panel; `ggplot2`
# draws the importance bars; `reticulate` (loaded in functions.R) bridges
# to the GNN embedding.
library(dplyr)
library(tidyr)
library(ggplot2)
library(xgboost)
library(here)

## 0.2 Load helpers ##########################################################

# functions.R gives us the R-native loaders + add_lag_features(), and the
# add_gnn_embeddings() wrapper that calls the Python embedding code.
source(here::here("code", "09_gnn-xgboost", "functions.R"))

cat("\n🚀 Case Study 09 — GNN + XGBoost (R, full pipeline via reticulate)\n")
cat("   Three feature sets stacked. Watch AUC climb as we add structure.\n\n")

## 0.3 Load data #############################################################

suppliers <- load_suppliers()
edges     <- load_edges()
panel     <- load_panel()
print(head(suppliers))
print(head(panel))
cat(sprintf("✅ Loaded %d suppliers, %d dependency edges, %d panel rows.\n",
            nrow(suppliers), nrow(edges), nrow(panel)))


# 1. Add lag feature #########################################################
#
# `lag_rate` is the rolling 4-week disruption rate for each supplier,
# computed BEFORE the current week to avoid label leakage. It's our best
# non-network feature for predicting next week's disruption.

panel <- add_lag_features(panel, window = 4)
cat("✅ Added 4-week lag_rate feature.\n")


# 2. Add GNN embeddings (Python via reticulate) ##############################
#
# This is the one step with no mature R library, so add_gnn_embeddings()
# (in functions.R) reaches across to numpy: it builds the row-normalized
# in-neighbor adjacency A and computes A %*% lag (1-hop neighbor average)
# and A %*% A %*% lag (2-hop), per week. The result is two new columns.
#
# These embeddings are FIXED aggregations (just a matrix multiply), NOT a
# trained GNN: no learned weights, no backprop. Same distinction as case 08
# -- you computed a forward pass, you didn't train one. The structural
# signal is real; the "learning" is not. A torch GNN would learn what to
# aggregate; here we hard-code "average your neighbors' lag_rate."

panel <- add_gnn_embeddings(panel, suppliers, edges)
print(head(panel, 10))
cat("✅ Added 1-hop and 2-hop GNN embeddings of lag_rate.\n")


# 3. Merge static features ###################################################
#
# Join the suppliers table (tier, capacity, region, geo_risk) onto the
# panel and one-hot encode region. XGBoost can take factors directly, but
# we keep the encoding explicit so the feature columns are obvious.
# We deliberately keep ALL region columns (no dropped reference level). A
# linear model would have collinearity here, but tree models like XGBoost
# don't care, and keeping every level makes the importance plot readable.

dat <- panel |>
  left_join(suppliers, by = "supplier_id") |>
  mutate(
    region_MW = as.integer(region == "MW"),
    region_NE = as.integer(region == "NE"),
    region_SE = as.integer(region == "SE"),
    region_W  = as.integer(region == "W")
  )


# 4. Train/test split ########################################################
#
# Train on weeks 0..39 (the first 40 weeks). Test on weeks 40..51 (the
# last 12). This is the canonical time-series holdout: never train on
# data from a week you'll later evaluate on.

train <- dat |> filter(week < 40)
test  <- dat |> filter(week >= 40)
cat(sprintf("📊 train rows: %d   test rows: %d\n", nrow(train), nrow(test)))
cat(sprintf("📊 train positive rate: %.3f\n", mean(train$disrupted)))


# 5. Three feature sets, three models ########################################
#
# Each feature set is a SUPERSET of the previous one, so any AUC
# improvement from raw -> raw+lag -> raw+lag+GNN tells you what adding
# *that piece* contributed.

raw_cols <- c("tier", "capacity", "geo_risk",
              "region_MW", "region_NE", "region_SE", "region_W")
lag_cols <- c(raw_cols, "lag_rate")
gnn_cols <- c(lag_cols, "gnn_1hop", "gnn_2hop")

# Rank-based AUC (no extra package needed). For each (positive, negative)
# score pair we count how often the positive scored higher — that is the
# ROC AUC by definition (the Mann-Whitney identity), so it matches what
# sklearn's roc_auc_score would report for the same predictions.
auc_rank <- function(scores, labels) {
  pos <- scores[labels == 1]
  neg <- scores[labels == 0]
  if (length(pos) == 0 || length(neg) == 0) return(NA_real_)
  mean(outer(pos, neg, ">")) + 0.5 * mean(outer(pos, neg, "=="))
}

# Fit one XGBoost model on a feature set and return its test AUC + the
# feature-importance table. Same hyperparameters as the Python track. We
# use the low-level xgb.train() + xgb.DMatrix() API because it is stable
# across xgboost versions (the high-level xgboost() signature changed in 3.x).
fit_and_score <- function(features) {
  set.seed(42)  # XGBoost's RNG; keeps runs reproducible
  dtrain <- xgboost::xgb.DMatrix(as.matrix(train[, features]),
                                 label = train$disrupted)
  dtest  <- xgboost::xgb.DMatrix(as.matrix(test[, features]),
                                 label = test$disrupted)
  model  <- xgboost::xgb.train(
    params  = list(max_depth = 4, eta = 0.05,
                   objective = "binary:logistic", eval_metric = "auc"),
    data    = dtrain, nrounds = 200, verbose = 0
  )
  preds <- predict(model, dtest)
  imp   <- xgboost::xgb.importance(model = model, feature_names = features) |>
    arrange(desc(Gain))
  list(model = model, auc = auc_rank(preds, test$disrupted), imp = imp)
}

raw_fit <- fit_and_score(raw_cols)
lag_fit <- fit_and_score(lag_cols)
gnn_fit <- fit_and_score(gnn_cols)

cat(sprintf("🧪 AUC, raw features only:           %.4f\n", raw_fit$auc))
cat(sprintf("🧪 AUC, raw + lag:                   %.4f\n", lag_fit$auc))
cat(sprintf("🧪 AUC, raw + lag + GNN (1+2 hop):   %.4f\n", gnn_fit$auc))

# AUC in plain English: the probability the model scores a truly disrupted
# supplier higher than a healthy one. 0.5 = coin flip, 1.0 = perfect.
# How to read these: the raw-only model is your NON-NETWORK baseline.
# Watch AUC climb as lag (history) and then GNN (structure) features are
# added. For rare-event, noisy disruption prediction ~0.65+ is competitive
# -- don't expect the 0.80+ you'd see on a clean churn model.


# 6. Feature importance ######################################################
#
# What does the full model think the most important features are? A high
# gain on `gnn_1hop` or `gnn_2hop` is the visible signature of the GNN
# piece earning its keep.
#
# Heads-up: a feature can rank LOW here yet still raise AUC. Importance
# counts how often the model splits on a feature; a GNN feature that adds
# weak but INDEPENDENT signal can lift predictions without being split on
# often. Low importance + real AUC lift = exactly that situation.
#
# Connecting back to Week 2 (Case 04): the gnn_1hop / gnn_2hop columns play
# the same role betweenness/centrality did — they summarize a node's
# structural position — except here that signal is LEARNED from the
# neighbors' data (their lag_rate) rather than COMPUTED from pure topology.
# A high gnn_1hop gain means "knowing your neighbors' recent disruption
# rate helps predict your own."

# Reading THIS table: individual-supplier features (capacity, geo_risk)
# usually top it -- a supplier's own characteristics predict its own
# disruption more than its neighbors' do. And gnn_1hop typically outranks
# gnn_2hop, because 2-hop averages in more distant, noisier neighbors and
# dilutes the signal. Structure helps; individual features still dominate.
print(gnn_fit$imp)

p <- ggplot(gnn_fit$imp, aes(x = Gain, y = reorder(Feature, Gain))) +
  geom_col(fill = "#3a8bc6") +
  labs(x = "XGBoost feature importance (gain)", y = NULL,
       title = "Which features matter? (raw + lag + GNN model)") +
  theme_minimal()

ggsave(here::here("code", "09_gnn-xgboost", "xgboost_importance.png"),
       p, width = 7, height = 4.5, dpi = 120)
cat("💾 Saved xgboost_importance.png\n")


# 7. Learning Check ##########################################################
#
# QUESTION: On the held-out test weeks (40..51), what is the ROC AUC of
# the (raw + lag + GNN 1-hop + GNN 2-hop) XGBoost model?
# Report to 4 decimal places.
#
# NOTE: this asks the same question as the Python track. The embedding is
# computed by the same numpy code, but the model is trained by R's own
# xgboost, so the value can differ from Python's in the last digits —
# implementations and their defaults are not bit-for-bit identical.

cat(sprintf("\n📝 Learning Check answer: %.4f\n", gnn_fit$auc))

cat("\n🎉 Done. Move on to the case study report when you're ready.\n")
