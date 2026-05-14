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

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score
import xgboost as xgb

## 0.2 Load helpers ##########################################################

from functions import (
    load_suppliers, load_edges, load_panel,
    add_lag_features, build_adjacency, add_gnn_embeddings,
)

## 0.3 Load data #############################################################

suppliers = load_suppliers()
edges     = load_edges()
panel     = load_panel()
print(suppliers.head())
print(panel.head())


# 1. Add lag feature ##########################################################

panel = add_lag_features(panel, window=4)
print(panel.head(10))


# 2. Build adjacency & add GNN embeddings ####################################

A = build_adjacency(suppliers, edges)
print(f"Adjacency: {A.shape}, row-sum max = {A.sum(axis=1).max():.2f}")

panel = add_gnn_embeddings(panel, suppliers, A)
print(panel.head(10))


# 3. Merge static features ###################################################

panel = panel.merge(suppliers, on="supplier_id", how="left")
# one-hot region (XGBoost can handle this directly but we keep it explicit)
panel = pd.concat([panel, pd.get_dummies(panel["region"], prefix="region")],
                  axis=1)


# 4. Train/test split ########################################################

train = panel[panel["week"] < 40].copy()
test  = panel[panel["week"] >= 40].copy()
print(f"train rows: {len(train):,}   test rows: {len(test):,}")
print(f"train positive rate: {train['disrupted'].mean():.3f}")


# 5. Three feature sets, three models ########################################

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

print(f"AUC, raw features only:           {auc_raw:.4f}")
print(f"AUC, raw + lag:                   {auc_lag:.4f}")
print(f"AUC, raw + lag + GNN (1+2 hop):   {auc_gnn:.4f}")


# 6. Feature importance ######################################################

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


# 7. Learning Check ##########################################################
#
# QUESTION: On the held-out test weeks (40..51), what is the ROC AUC
# of the (raw + lag + GNN 1-hop + GNN 2-hop) XGBoost model?
# Report to 4 decimal places.

print(f"Learning Check answer: {auc_gnn:.4f}")
