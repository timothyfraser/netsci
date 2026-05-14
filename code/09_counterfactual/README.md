# Case Study 09 — Counterfactual Monte Carlo

> Interactive lab: [`docs/case-studies/counterfactual.html`](../../docs/case-studies/counterfactual.html)
>
> Skill: **Predict** · Data: synthetic 180-station bikeshare-like
> network (Watts-Strogatz topology with Poisson-weighted edges)

## What you'll learn

How to ask "would this intervention *actually* help?" with
statistical honesty. The technique:

1. Re-draw every edge's weight from `Poisson(λ = observed_weight)`,
   R times, to get a *distribution* of plausible networks consistent
   with what you observed.
2. Apply your intervention to each replicate; recompute the metric.
3. Look at the distribution of `metric_intervention − metric_baseline`.
4. The 95% CI of that distribution tells you whether the
   intervention's effect is meaningfully different from zero.

In this case study, the baseline metric is weighted average path
length (APL), and the intervention is adding a high-ridership direct
edge between the two currently-farthest-apart stations.

## Prerequisites

- Case study 04 (Centrality) so you know what APL is and why it
  matters.
- The interactive lab.
- R packages: `dplyr`, `ggplot2`, `igraph`, `here`.
- Python packages: see [`code/requirements.txt`](../requirements.txt).

## Files in this folder

```
09_counterfactual/
├── README.md
├── example.R
├── example.py
├── functions.R    # `weighted_apl()`, `mc_apls()`
├── functions.py
└── data/
    ├── nodes.csv   # 180 stations
    ├── edges.csv   # 720 weighted undirected edges
    └── _generate.py
```

## How to run

```bash
Rscript code/09_counterfactual/example.R
python  code/09_counterfactual/example.py
```

## Learning check (submit this number)

> **For the intervention "add a high-ridership (~120 rides) edge
> between the two currently-farthest-apart stations" with R=500
> Monte Carlo replicates and seed=1, what is the LOW end of the 95%
> CI on the change in weighted APL?** (4 decimal places, signed.)

## Your Project Case Study

If you pick this case study, you'll propose an intervention on
*your* network and report whether the 95% CI on its effect crosses
zero.

### Suggested project questions

1. **Is this intervention real?** Pick an intervention that matters
   in your domain (add an edge, boost a weight, remove a node).
   Compute the 95% CI on its effect on a relevant metric. State in
   prose whether the effect is robust.

2. **Two interventions, one budget.** Propose two competing
   interventions. Compute each one's CI on the same metric. Report
   which is more reliably beneficial.

3. **Sensitivity to R.** Vary the number of Monte Carlo replicates
   (e.g. R = 100, 500, 2000). Report how the CI width shrinks. Find
   the smallest R that gives a CI within 10% of the R=2000 width.

### Report

- **Question.** One sentence: the intervention and the metric.
- **Network and baseline.** Nodes, edges, baseline metric value.
- **Procedure.** Resampling distribution, R, seed.
- **Results.** Numbers in prose: baseline metric, intervention
  mean, 95% CI. The two-distribution histogram is a strong figure.
- **What this tells you, and what it doesn't.** 2-3 sentences,
  particularly: a CI containing zero is *not* "the intervention
  doesn't work" — it's "you don't have enough evidence either way."

## Further reading

- The bootstrap (Efron 1979) and Monte Carlo simulation are the
  ancestors of this technique; if you want a deeper treatment,
  Davison & Hinkley's *Bootstrap Methods and their Application* is
  the canonical reference.
- The case study's framing (Lakeside Bikeshare) is fictional, but
  the workflow is widely used in transit and infrastructure
  planning to evaluate proposed changes before construction.
