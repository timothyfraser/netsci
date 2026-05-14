# Case Study 07 — Network Permutation Testing

> Interactive lab: [`docs/case-studies/permutation.html`](../../docs/case-studies/permutation.html)
>
> Skill: **Infer** · Data: 400-node synthetic mobility network with
> planted neighborhood-demo correlation (no direct edge-level
> homophily — the homophily comes from where people live)

## What you'll learn

When you compute a network statistic (homophily, assortativity,
mean within-group edge weight) you need a **null model** to decide
whether the value you saw could have happened by chance. This case
makes the point that the null model is *not* obvious:

- An **unblocked** permutation (shuffle labels across all nodes)
  ignores community structure. It will tell you anything is
  "significant" if neighborhoods are themselves segregated.
- A **block** permutation (shuffle labels only within community)
  controls for that. It's the right null when the question is
  "additional homophily beyond what neighborhood structure
  explains."

The dataset is engineered so the two nulls disagree dramatically:
unblocked p < 0.001, block-permuted p ≈ 0.89.

## Prerequisites

- The interactive lab.
- Case study 02 (Joins) and case study 03 (Aggregation).
- R packages: `dplyr`, `tibble`, `ggplot2`, `igraph`, `here`.
- Python packages: see [`code/requirements.txt`](../requirements.txt).

## Files in this folder

```
07_permutation/
├── README.md
├── example.R
├── example.py
├── functions.R   # `assort_by()`, `permute_labels()`
├── functions.py
└── data/
    ├── nodes.csv  # 400 nodes with neighborhood + demo labels
    ├── edges.csv  # ~18,000 weighted undirected edges
    └── _generate.py
```

## How to run

```bash
Rscript code/07_permutation/example.R
python  code/07_permutation/example.py
```

## Learning check (submit this number)

> **What is the *block-permuted* p-value for nominal assortativity
> by `demo`, using `neighborhood` as the block, with 500
> permutations and seed 42?** (3 decimal places.)

## Your Project Case Study

If you pick this case study, you'll test a homophily claim on *your*
network using two different null models and report when they
disagree.

### Suggested project questions

1. **Two nulls, two stories.** Pick a categorical node attribute in
   your network. Compute observed assortativity. Compute the
   unblocked-permutation null and a block-permutation null on a
   meaningful blocking variable. Report both p-values and discuss.

2. **What's the right block?** Find at least two plausible blocking
   variables. Compute the block-permuted p-value under each.
   Report which choice you prefer and why, given your question.

3. **Beyond assortativity.** Replace nominal assortativity with a
   different network statistic (mean within-group edge weight,
   share of edges that are within-group). Show the same
   blocked/unblocked comparison still applies.

### Report

- **Question.** One sentence.
- **Network and attribute.** Nodes, edges, the attribute you're
  testing homophily on, plus the blocking variable and why.
- **Procedure.** Number of permutations, seed, statistic.
- **Results.** Both p-values in prose, with one histogram of the
  null distributions and the observed.
- **What this tells you, and what it doesn't.** 2-3 sentences.
  Specifically: when you have only two nulls and they disagree,
  which one is "right" depends on the question you set out to ask.

## Further reading

- The classic intro to network permutation testing is Newman's
  *Networks* (Chapter 7). The block-permutation idea is sometimes
  called a "stratified" permutation.
- The case study's "Bluebikes" framing is a real-world example of
  this trap: AM ridership looks racially segregated even when
  controlling for income, but the right null can disagree.
