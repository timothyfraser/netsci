# Case Study 05 — Supply Chain Resilience

> Interactive lab: [`docs/case-studies/supply-chain.html`](../../docs/case-studies/supply-chain.html)
>
> Skill: **Measure** · Data: synthetic 3-tier supply chain (150 suppliers,
> 30 DCs, 400 retailers — 580 nodes, ~900 directed weighted edges)

## What you'll learn

Centrality measures aren't just an academic curiosity — they tell you
which nodes to *defend*. This case study takes the supply-chain
resilience question seriously:

- Defines a domain-specific resilience metric (**supply coverage** =
  fraction of retailers still reachable from any supplier).
- Computes per-tier centralities (in/out degree, weighted in/out
  strength, betweenness) on a directed graph.
- Compares **random**, **high-degree**, and **high-betweenness**
  failure strategies on distribution centers.
- Lands on the qualitative result: targeted attacks (by either
  centrality) damage the network meaningfully faster than random
  attacks, and which centrality wins depends on the graph.

## Prerequisites

- Case study 04 (Centrality).
- The interactive lab.
- R packages: `dplyr`, `tibble`, `tidyr`, `igraph`, `ggplot2`, `here`.
- Python packages: see [`code/requirements.txt`](../requirements.txt).

## Files in this folder

```
05_supply-chain/
├── README.md
├── example.R
├── example.py
├── functions.R           # exposes `supply_coverage()` and `remove_and_score()`
├── functions.py
└── data/
    ├── nodes.csv     # 580 nodes (tier ∈ {1,2,3})
    ├── edges.csv     # ~900 directed edges with capacity
    └── _generate.py
```

## How to run

```bash
Rscript code/05_supply-chain/example.R
python  code/05_supply-chain/example.py
```

## Learning check (submit this number)

> **After removing the 5 highest-betweenness distribution centers,
> what is the supply coverage of the network?** (3 decimal places.)

## Your Project Case Study

If you pick this case study, you'll define a resilience metric on
*your* network and run targeted-vs-random failure simulations.

### Suggested project questions

1. **Which centrality picks the load-bearing nodes?** On your
   network, define a resilience metric, then run two targeted-attack
   strategies side-by-side (e.g. top-k by degree vs top-k by
   betweenness). Plot the damage curve and report which strategy
   degrades the metric faster.

2. **Random baseline.** Compare any targeted strategy against random
   removal. Report the *area between the two curves* (a rough proxy
   for how much being targeted matters).

3. **Tier-specific failures.** If your network has tiers/layers, run
   the failure simulation separately within each tier. Report which
   tier is most fragile.

### Report

- **Question.** One sentence.
- **Network and resilience metric.** What's an edge, what's a node,
  what's "coverage" or "throughput" in your domain.
- **Procedure.** What you ran, in order.
- **Results.** Numbers in prose; at most 2 figures (the damage
  curve is a near-mandatory one) and 1 table.
- **What this tells you, and what it doesn't.** 2-3 sentences.

## Further reading

- The sts course `26C_analytics.R` uses the same vocabulary for
  committee networks.
- Case study 06 ([`06_dsm-clustering`](../06_dsm-clustering)) tackles
  the *modularity* side of the same coin: rather than finding
  critical nodes, finding critical *clusters*.
