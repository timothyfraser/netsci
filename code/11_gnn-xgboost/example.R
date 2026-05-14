#' @name example.R
#' @title Case Study 11 — GNN + XGBoost (R track: XGBoost-only variant)
#' @author <your-name-here>
#' @description
#' The full case study lab combines:
#'   - raw static features
#'   - a lag (history) feature
#'   - a GNN-style structural embedding
#' into XGBoost, and shows that the combination beats any one piece
#' alone.
#'
#' R can do the static-features and lag pieces just fine via the
#' `xgboost` package. But there is no widely-used R GNN library, so
#' the **GNN embedding step is Python-only**.
#'
#' This R script trains XGBoost on (raw + lag) features and reports
#' the AUC. The Python script (`example.py`) trains XGBoost on
#' (raw + lag + GNN). The README documents the AUC gap.


# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

library(dplyr)
library(tidyr)
library(ggplot2)
library(arrow)
library(xgboost)
library(zoo)        # for rolling-mean lag feature
library(here)

## 0.2 Load helpers ##########################################################

source(here::here("code", "11_gnn-xgboost", "functions.R"))

## 0.3 Load data #############################################################

suppliers <- load_suppliers()
edges     <- load_edges()
panel     <- load_panel()

suppliers |> head()
panel |> head()


# 1. Add lag feature ##########################################################

panel <- add_lag_features(panel, window = 4)
panel |> head(10)


# 2. Merge static features ###################################################

dat <- panel |>
  left_join(suppliers, by = "supplier_id") |>
  # one-hot region
  mutate(
    region_MW = as.integer(region == "MW"),
    region_NE = as.integer(region == "NE"),
    region_SE = as.integer(region == "SE"),
    region_W  = as.integer(region == "W")
  )


# 3. Train/test split #########################################################

train <- dat |> filter(week < 40)
test  <- dat |> filter(week >= 40)
cat(sprintf("train rows: %d   test rows: %d\n", nrow(train), nrow(test)))


# 4. Two feature sets, two models ############################################

raw_cols <- c("tier", "capacity", "geo_risk",
              "region_MW", "region_NE", "region_SE", "region_W")
lag_cols <- c(raw_cols, "lag_rate")

fit_and_auc <- function(features) {
  dtrain <- xgb.DMatrix(
    data  = as.matrix(train[, features]),
    label = train$disrupted
  )
  dtest <- xgb.DMatrix(
    data  = as.matrix(test[, features]),
    label = test$disrupted
  )
  model <- xgboost::xgboost(
    data            = dtrain,
    nrounds         = 200,
    max_depth       = 4,
    eta             = 0.05,
    objective       = "binary:logistic",
    eval_metric     = "auc",
    verbose         = 0
  )
  preds <- predict(model, dtest)
  # AUC: rank-based
  pos <- preds[test$disrupted == 1]
  neg <- preds[test$disrupted == 0]
  auc <- mean(outer(pos, neg, ">")) + 0.5 * mean(outer(pos, neg, "=="))
  list(model = model, auc = auc)
}

raw_fit <- fit_and_auc(raw_cols)
lag_fit <- fit_and_auc(lag_cols)

cat(sprintf("AUC, raw features only: %.4f\n", raw_fit$auc))
cat(sprintf("AUC, raw + lag:         %.4f\n", lag_fit$auc))

cat("\nFor the GNN embedding pipeline that pushes AUC higher,\n",
    "switch to example.py. (Or call it from here via reticulate.)\n")


# 5. Feature importance ######################################################

imp <- xgboost::xgb.importance(model = lag_fit$model,
                               feature_names = lag_cols) |>
  arrange(desc(Gain))
print(imp)


# 6. Learning Check (R track) ###############################################
#
# QUESTION: On the held-out test weeks (40..51), what are the top 3
# features by XGBoost gain for the (raw + lag) model? Submit the
# three feature names, comma-separated, in descending gain order.

top3 <- imp |> slice(1:3) |> pull(Feature)
cat(sprintf("Learning Check answer (R track): %s\n",
            paste(top3, collapse = ", ")))


# NOTE on the Python LC: the Python script reports the AUC of the
# (raw + lag + GNN) model on the same test split. Those two LC
# answers are intentionally different — they test different pieces
# of the case-study pipeline.
