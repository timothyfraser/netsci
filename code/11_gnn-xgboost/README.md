# Case Study 11 — GNN + XGBoost

> Interactive lab: [`docs/case-studies/gnn-xgboost.html`](../../docs/case-studies/gnn-xgboost.html)
>
> Skill: **Predict** · Track: **Python = full pipeline · R = XGBoost-only variant**
> · Data: synthetic supplier-disruption panel (500 suppliers × 52 weeks,
> ~1,200 directed dependency edges)

## What you'll learn

How to combine three families of features for a node-level
prediction task:

1. **Raw static features** (per-supplier traits — tier, region,
   capacity, geo-risk).
2. **Lag features** (per-supplier history — trailing 4-week
   disruption rate).
3. **GNN-style structural embeddings** (the lag feature *of your
   neighbors* — and your neighbors' neighbors — averaged over the
   directed in-edges).

XGBoost on all three usually beats XGBoost on any subset. The case
study makes that improvement concrete and lets you read the
feature-importance bars to see *why* the GNN helps.

## Why R is partial

R's `xgboost` package is excellent, so the raw + lag pipeline is
identical in R and Python. But R has no widely-used GNN library, so:

- **Python (`example.py`)**: runs the full pipeline (raw + lag + GNN).
  Final test AUC ≈ 0.66.
- **R (`example.R`)**: runs raw + lag only. Final test AUC ≈ 0.64.

That ~0.02 AUC gap is the value the GNN embedding adds on this
dataset. The Python script demonstrates it; the R script
acknowledges it. The GNN embedding here is a *parameter-free*
GCN-style aggregation (mean of in-neighbors' lag rate over 1 and 2
hops), so there's no torch dependency.

## Prerequisites

- Case study 10 (GNN by Hand) so the embedding step makes sense.
- The interactive lab.
- R packages: `dplyr`, `tidyr`, `readr`, `ggplot2`, `xgboost`, `zoo`,
  `here`.
- Python packages: see [`code/requirements.txt`](../requirements.txt).
  Uses `scikit-learn` for AUC.

## Files in this folder

```
11_gnn-xgboost/
├── README.md
├── example.R              # XGBoost on raw + lag
├── example.py             # XGBoost on raw + lag + GNN embedding
├── functions.R            # lag_rate helper
├── functions.py           # lag_rate, adjacency, GNN-aggregation helpers
└── data/
    ├── suppliers.csv  # 500 suppliers, static features
    ├── edges.csv      # ~1,200 directed dependency edges
    ├── panel.csv      # 26,000 rows: supplier x week x disrupted
    └── _generate.py
```

## How to run

```bash
python code/11_gnn-xgboost/example.py    # full pipeline
Rscript code/11_gnn-xgboost/example.R    # raw + lag variant
```

## Learning check (submit ONE of these)

The two tracks have different LC questions so you don't have to do
the part your track skipped.

- **Python track:** *On the held-out test weeks (40..51), what is the
  ROC AUC of the (raw + lag + GNN 1-hop + GNN 2-hop) XGBoost model?*
  4 decimal places.

- **R track:** *On the held-out test weeks (40..51), what are the
  TOP 3 features by XGBoost gain for the (raw + lag) model?*
  Comma-separated feature names in descending gain order.

You only need to submit your track's answer. If you ran both,
mention both in your submission.

## Your Project Case Study

If you pick this case study, you'll predict a node-level binary
outcome on *your* network using XGBoost (Python track adds GNN
embeddings).

### Suggested project questions

1. **Does network position help?** Train XGBoost on raw features
   only, then on raw + lag, then on raw + lag + GNN (Python only).
   Report the AUC gain at each step. Discuss whether network
   position adds predictive value in your domain.

2. **Feature importance audit.** Train XGBoost on the full feature
   set. Report the top 5 features by gain. Discuss whether the
   ranking matches your domain intuition.

3. **Class imbalance.** If your target is imbalanced (most cases
   are negatives), report AUC AND precision/recall at a sensible
   threshold. Discuss whether the model is useful at the
   operational decision threshold you care about.

### Report

- **Question.** One sentence, ending with "...so we can [act]."
- **Network and panel.** Nodes, edges, target definition, time
  range, train/test split.
- **Procedure.** Feature sets, model hyperparameters, evaluation
  metric.
- **Results.** AUC (and precision/recall if imbalanced) in prose;
  feature-importance plot as 1 figure; results table.
- **What this tells you, and what it doesn't.** 2-3 sentences.
  Note: an XGBoost AUC of 0.65 is real signal but not a deployable
  prediction — be honest about that.

## Further reading

- Kipf & Welling (2017) for the GCN math the embedding step
  approximates.
- Chen & Guestrin (2016) for the XGBoost algorithm.
- For a more sophisticated GNN-feature pipeline (with trained
  weights instead of parameter-free aggregation), see PyTorch
  Geometric's tutorials.
