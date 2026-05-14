# `code/` — Teaching scripts for the eleven case studies

This folder is where the *interactive case studies* on the website become
*real, runnable code*.

Every case study on the [Case Studies page](../docs/case-studies.html) lives
in two places:

1. **An interactive HTML lab** under `docs/case-studies/<name>.html`. You
   click, drag, and toggle through the analysis to build intuition.
2. **A code folder here** under `code/NN_<name>/` containing parallel **R**
   and **Python** scripts that run the *same analysis as plain code*.

The pattern across every case folder is identical, so you can move between
case studies (and between R and Python) without losing your footing.

```
code/NN_<name>/
├── README.md       # the case in 2 minutes — what, why, what you'll submit
├── example.R       # the analysis, in R, with tidyverse + igraph + ggraph
├── example.py      # the analysis, in Python, with pandas + igraph + matplotlib
├── functions.R     # helpers: data loaders, synthetic-network generators, sims
├── functions.py    # the Python counterparts
└── data/           # slim, bundled data files (CSV / Parquet / GeoJSON, < few MB)
```

Both `example.R` and `example.py` use **identical section headers in identical
order**, so if you started a case in one language and want to switch, the
section you were on is in the same place in the other file.

## How to install

### R

R packages (run once at the top of the repo):

```r
install.packages(c(
  # core wrangling
  "dplyr", "readr", "tidyr", "purrr", "stringr", "tibble", "here",
  # networks
  "igraph", "tidygraph", "ggraph",
  # viz
  "ggplot2", "viridis", "patchwork", "scales",
  # spatial (case 08 only)
  "sf",
  # case 11 only
  "xgboost", "zoo"
))
```

If your repo uses `renv`, prefer `renv::install(...)` instead of
`install.packages(...)`.

We use the **base pipe `|>`** (not magrittr `%>%`) throughout. We use
`here::here()` to resolve paths. Run any script with:

```bash
Rscript code/NN_<name>/example.R
```

### Python

Python deps (run once):

```bash
pip install -r code/requirements.txt
```

Run any script with:

```bash
python code/NN_<name>/example.py
```

## The case studies

Each row pairs an interactive lab with its code folder. The lab is for
exploring; the code folder is for *doing the same thing on your own data*.

| #  | Case study               | Skill    | Lab                                                         | Code folder                                  |
|----|--------------------------|----------|-------------------------------------------------------------|----------------------------------------------|
| 01 | Build a Network          | Identify | [lab](../docs/case-studies/build-a-network.html)            | [`01_build-a-network`](01_build-a-network/)  |
| 02 | Network Joins            | Identify | [lab](../docs/case-studies/joins.html)                      | [`02_joins`](02_joins/)                      |
| 03 | Aggregation              | Identify | [lab](../docs/case-studies/aggregation.html)                | [`03_aggregation`](03_aggregation/)          |
| 04 | Centrality & Criticality | Measure  | [lab](../docs/case-studies/centrality.html)                 | [`04_centrality`](04_centrality/)            |
| 05 | Supply Chain Resilience  | Measure  | [lab](../docs/case-studies/supply-chain.html)               | [`05_supply-chain`](05_supply-chain/)        |
| 06 | DSM Clustering           | Measure  | [lab](../docs/case-studies/dsm-clustering.html)             | [`06_dsm-clustering`](06_dsm-clustering/)    |
| 07 | Network Permutation      | Infer    | [lab](../docs/case-studies/permutation.html)                | [`07_permutation`](07_permutation/)          |
| 08 | Sampling Big Networks    | Identify | [lab](../docs/case-studies/sampling.html)                   | [`08_sampling`](08_sampling/)                |
| 09 | Counterfactual MC        | Predict  | [lab](../docs/case-studies/counterfactual.html)             | [`09_counterfactual`](09_counterfactual/)    |
| 10 | GNN by Hand              | Predict  | [lab](../docs/case-studies/gnn-by-hand.html)                | [`10_gnn-by-hand`](10_gnn-by-hand/)          |
| 11 | GNN + XGBoost            | Predict  | [lab](../docs/case-studies/gnn-xgboost.html)                | [`11_gnn-xgboost`](11_gnn-xgboost/)          |

## What you submit (the short version)

Every week of the course, by Monday at 9 a.m. you submit:

1. The **sketchpad** assignments for that week.
2. The **case study learning checks** for the *previous* week's case studies.
3. The **code learning checks** for the *previous* week's `example.R` /
   `example.py` (one per case study completed).
4. The **project code + report** for whichever case study you are using as
   *your* project case study that week.

See the [Assignments page](../docs/assignments.html) for full details.

## A note on R and Python parity

We try to keep the two scripts as close as possible:

- Same section headers, in the same order.
- Same intermediate variables (so a student following along in either
  language can sanity-check against the other).
- Same Learning Check numeric answer.

A few unavoidable differences:

- **GNN-by-hand (case 10)** is Python-primary. R is hard to use for
  Graph Neural Networks. The R file is a stub that points to the Python
  one and shows how to call it from R via `reticulate` if you want.
- **GNN + XGBoost (case 11)** is split: Python does the full GNN +
  XGBoost pipeline; R does an XGBoost-only variant on raw + lag features
  (no GNN embeddings). This lets R users still complete the case study;
  the README documents the AUC gap.

Everything else is parallel.
