"""Case Study 11 — GNN + XGBoost (Python track, full pipeline).

The case study lab showed you that combining:
  - raw static features
  - a lag (history) feature
  - a GNN-style structural embedding

into XGBoost beats any one of them alone. Here we do that in code on
a synthetic supplier-disruption panel (500 suppliers x 52 weeks).

The GNN embedding here is a *parameter-free* GCN-style aggregation
(mean of in-neighbors' lag_rate, then mean of 2-hop in-neighbors').
This isn't a *trained* GNN — but it carries the same structural
signal, and it lets us avoid a torch dependency for teaching.

Pipeline:
  1. Load suppliers, edges, and the (supplier, week, disrupted) panel.
  2. Add the 4-week lag_rate feature.
  3. Build the row-normalized in-neighbor adjacency.
  4. Add 1-hop and 2-hop GNN embeddings of lag_rate.
  5. Split into train (weeks 0..39) / test (weeks 40..51).
  6. Train three XGBoost models on three feature sets; compare AUC.
"""

# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `xgboost` for the gradient-boosted trees, `sklearn` just for the AUC
# scorer, `numpy`/`pandas` for the feature engineering.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score
import xgboost as xgb

## 0.2 Load helpers ##########################################################

# All the data + feature-engineering plumbing lives in functions.py.
# `add_gnn_embeddings()` does the matrix-multiply that gives us the
# 1-hop and 2-hop neighbor lag_rate averages.
from functions import (
    load_suppliers, load_edges, load_panel,
    add_lag_features, build_adjacency, add_gnn_embeddings,
)

print("\n🚀 Case Study 11 — GNN + XGBoost (Python, full pipeline)")
print("   Three feature sets stacked. Watch AUC climb as we add structure.\n")

## 0.3 Load data #############################################################

suppliers = load_suppliers()
edges     = load_edges()
panel     = load_panel()
print(suppliers.head())
print(panel.head())
print(f"✅ Loaded {len(suppliers)} suppliers, {len(edges)} dependency edges, "
      f"{len(panel)} panel rows.")


# 1. Add lag feature #########################################################
#
# `lag_rate` is the rolling 4-week disruption rate for each supplier,
# computed BEFORE the current week to avoid label leakage. It's our
# best non-network feature for predicting next week's disruption.

panel = add_lag_features(panel, window=4)
print(panel.head(10))
print(f"✅ Added 4-week lag_rate feature.")


# 2. Build adjacency & add GNN embeddings ####################################
#
# The row-normalized in-neighbor adjacency A turns "compute average of
# my in-neighbors' lag_rate" into a single matrix product: A @ x.
# Applying A twice gives the 2-hop average. This is the simplest
# possible "graph convolution" — no learned weights, no nonlinearity.

A = build_adjacency(suppliers, edges)
print(f"📊 Adjacency: {A.shape}, row-sum max = {A.sum(axis=1).max():.2f}")

panel = add_gnn_embeddings(panel, suppliers, A)
print(panel.head(10))
print("✅ Added 1-hop and 2-hop GNN embeddings of lag_rate.")


# 3. Merge static features ###################################################

panel = panel.merge(suppliers, on="supplier_id", how="left")
# one-hot region (XGBoost can handle this directly but we keep it explicit)
panel = pd.concat([panel, pd.get_dummies(panel["region"], prefix="region")],
                  axis=1)


# 4. Train/test split ########################################################
#
# Train on weeks 0..39 (the first 40 weeks). Test on weeks 40..51
# (the last 12). This is the canonical time-series holdout: never
# train on data from a week you'll later evaluate on.

train = panel[panel["week"] < 40].copy()
test  = panel[panel["week"] >= 40].copy()
print(f"📊 train rows: {len(train):,}   test rows: {len(test):,}")
print(f"📊 train positive rate: {train['disrupted'].mean():.3f}")


# 5. Three feature sets, three models ########################################
#
# Each feature set is a SUPERSET of the previous one. So any AUC
# improvement from raw -> raw+lag -> raw+lag+GNN tells you what
# adding *that piece* contributed.

raw_cols  = ["tier", "capacity", "geo_risk",
             "region_MW", "region_NE", "region_SE", "region_W"]
lag_cols  = raw_cols + ["lag_rate"]
gnn_cols  = lag_cols + ["gnn_1hop", "gnn_2hop"]

def fit_and_auc(features):
    model = xgb.XGBClassifier(
        n_estimators=200, max_depth=4, learning_rate=0.05,
        random_state=42, verbosity=0,
        eval_metric="auc",
    )
    model.fit(train[features], train["disrupted"])
    preds = model.predict_proba(test[features])[:, 1]
    return roc_auc_score(test["disrupted"], preds), model

auc_raw,  _    = fit_and_auc(raw_cols)
auc_lag,  _    = fit_and_auc(lag_cols)
auc_gnn,  m_gnn = fit_and_auc(gnn_cols)

print(f"🧪 AUC, raw features only:           {auc_raw:.4f}")
print(f"🧪 AUC, raw + lag:                   {auc_lag:.4f}")
print(f"🧪 AUC, raw + lag + GNN (1+2 hop):   {auc_gnn:.4f}")


# 6. Feature importance ######################################################
#
# What does the full model think the most important features are?
# A high gain on `gnn_1hop` or `gnn_2hop` is the visible signature
# of the GNN piece earning its keep.

imp = pd.DataFrame({
    "feature":    gnn_cols,
    "importance": m_gnn.feature_importances_,
}).sort_values("importance", ascending=False)
print(imp)

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.barh(imp["feature"], imp["importance"], color="#3a8bc6")
ax.invert_yaxis()
ax.set_xlabel("XGBoost feature importance (gain)")
ax.set_title("Which features matter? (raw + lag + GNN model)")
fig.tight_layout()
fig.savefig("xgboost_importance.png", dpi=120)
plt.close(fig)
print("💾 Saved xgboost_importance.png")


# 7. Learning Check ##########################################################
#
# QUESTION: On the held-out test weeks (40..51), what is the ROC AUC
# of the (raw + lag + GNN 1-hop + GNN 2-hop) XGBoost model?
# Report to 4 decimal places.

print(f"\n📝 Learning Check answer: {auc_gnn:.4f}")

print("\n🎉 Done. Move on to the case study report when you're ready.")
