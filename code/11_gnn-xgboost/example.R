#' @name example.R
#' @title Case Study 11 — GNN + XGBoost (R track: feature-engineering variant)
#' @author <your-name-here>
#' @description
#' The full case study lab combines:
#'   - raw static features
#'   - a lag (history) feature
#'   - a GNN-style structural embedding
#' into XGBoost, and shows that the combination beats any one piece
#' alone.
#'
#' R can do the static-features and lag pieces fine. There is no
#' widely-used R GNN library, so the **GNN embedding step is
#' Python-only**.
#'
#' This R script compares two feature sets on the same train/test
#' split: raw vs raw+lag. It prefers `xgboost` if installed (the
#' canonical case-study tool), and falls back to base R `glm()` so
#' the script always runs.


# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `zoo` provides the rolling-mean function we use for the lag feature.
# `xgboost` is preferred but optional — we detect it and fall back to
# base R `glm()` if it isn't installed (e.g. in a CRAN-blocked sandbox).
library(dplyr)
library(tidyr)
library(ggplot2)
library(zoo)
library(here)

# xgboost is optional. Detect once and report which backend we're using.
HAS_XGB <- requireNamespace("xgboost", quietly = TRUE)

cat("\n🚀 Case Study 11 — GNN + XGBoost (R, feature-engineering variant)\n")
cat(sprintf("   Model backend: %s\n",
            if (HAS_XGB) "xgboost" else "base R glm() fallback"))
cat("   Compare raw vs raw+lag features on a 500-supplier disruption panel.\n\n")

## 0.2 Load helpers ##########################################################

source(here::here("code", "11_gnn-xgboost", "functions.R"))

## 0.3 Load data #############################################################

suppliers <- load_suppliers()
edges     <- load_edges()
panel     <- load_panel()
cat(sprintf("✅ Loaded %d suppliers, %d dependency edges, %d panel rows.\n",
            nrow(suppliers), nrow(edges), nrow(panel)))


# 1. Add lag feature #########################################################
#
# `lag_rate` is the rolling 4-week disruption rate for each supplier,
# computed BEFORE the current week to avoid label leakage. It's our
# best non-network feature for predicting next week's disruption.

panel <- add_lag_features(panel, window = 4)
cat(sprintf("✅ Added 4-week lag_rate feature.\n"))


# 2. Merge static features ###################################################
#
# Join the suppliers table (tier, capacity, region, geo_risk) onto
# the panel. Region is categorical, so we one-hot encode it explicitly
# — xgboost can handle factors directly but glm() needs numeric matrices.

dat <- panel |>
  left_join(suppliers, by = "supplier_id") |>
  mutate(
    region_MW = as.integer(region == "MW"),
    region_NE = as.integer(region == "NE"),
    region_SE = as.integer(region == "SE"),
    region_W  = as.integer(region == "W")
  )


# 3. Train/test split ########################################################
#
# Train on weeks 0..39 (the first 40 weeks). Test on weeks 40..51
# (the last 12). This is the canonical time-series holdout: never
# train on data from a week you'll later evaluate on.

train <- dat |> filter(week < 40)
test  <- dat |> filter(week >= 40)
cat(sprintf("📊 train rows: %d   test rows: %d\n", nrow(train), nrow(test)))


# 4. Two feature sets, two models ############################################

raw_cols <- c("tier", "capacity", "geo_risk",
              "region_MW", "region_NE", "region_SE", "region_W")
lag_cols <- c(raw_cols, "lag_rate")

# Rank-based AUC (no extra package needed). For each pair of
# (positive_score, negative_score) we count how often the positive
# scored higher — that's the AUC by definition.
auc_rank <- function(scores, labels) {
  pos <- scores[labels == 1]
  neg <- scores[labels == 0]
  if (length(pos) == 0 || length(neg) == 0) return(NA_real_)
  mean(outer(pos, neg, ">")) + 0.5 * mean(outer(pos, neg, "=="))
}

fit_and_score <- function(features) {
  if (HAS_XGB) {
    dtrain <- xgboost::xgb.DMatrix(
      data  = as.matrix(train[, features]),
      label = train$disrupted
    )
    dtest <- xgboost::xgb.DMatrix(
      data  = as.matrix(test[, features]),
      label = test$disrupted
    )
    model <- xgboost::xgboost(
      data        = dtrain,
      nrounds     = 200,
      max_depth   = 4,
      eta         = 0.05,
      objective   = "binary:logistic",
      eval_metric = "auc",
      verbose     = 0
    )
    preds <- predict(model, dtest)
    imp <- xgboost::xgb.importance(model = model,
                                   feature_names = features) |>
      arrange(desc(Gain))
  } else {
    # base R logistic regression fallback. We use |z-value| as the
    # rough analog of XGBoost feature importance — a feature with
    # a big standardized coefficient is "important" in either model.
    f <- as.formula(paste("disrupted ~", paste(features, collapse = " + ")))
    model <- glm(f, data = train, family = binomial())
    preds <- predict(model, newdata = test, type = "response")
    co <- summary(model)$coefficients
    co <- co[rownames(co) != "(Intercept)", , drop = FALSE]
    imp <- tibble::tibble(
      Feature = rownames(co),
      Gain    = abs(co[, "z value"])
    ) |> arrange(desc(Gain))
  }
  list(model = model, auc = auc_rank(preds, test$disrupted), imp = imp)
}

raw_fit <- fit_and_score(raw_cols)
lag_fit <- fit_and_score(lag_cols)

cat(sprintf("🧪 AUC, raw features only: %.4f\n", raw_fit$auc))
cat(sprintf("🧪 AUC, raw + lag:         %.4f\n", lag_fit$auc))


# 5. Feature importance (or |z| if using glm) ################################
#
# What does the (raw + lag) model think the most important features
# are? The top of this list answers the R-track Learning Check.

print(lag_fit$imp)


# 6. Learning Check (R track) ################################################
#
# QUESTION: On the held-out test weeks (40..51), what are the top 3
# features by gain (xgboost) or by |z| value (glm fallback) for the
# (raw + lag) model? Submit the three feature names, comma-separated,
# in descending order.
#
# Note: the *order* may be the same across both backends even when the
# underlying scores differ.

top3 <- lag_fit$imp |> slice(1:3) |> pull(Feature)
answer <- paste(top3, collapse = ", ")

cat(sprintf("\n📝 Learning Check answer (R track): %s\n", answer))

# NOTE: the Python LC asks for AUC of the (raw + lag + GNN) model on
# the same test split. The two LC answers are intentionally different
# — they test different pieces of the case-study pipeline.

cat("\n🎉 Done. Move on to the case study report when you're ready.\n")
