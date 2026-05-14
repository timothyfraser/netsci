# Case Study 04 — Centrality & Criticality

> Interactive lab: [`docs/case-studies/centrality.html`](../../docs/case-studies/centrality.html)
>
> Skill: **Measure** · Data: synthetic 500-node transit network with
> planted bridge nodes

## What you'll learn

How to compute and *compare* four different centrality measures —
degree, betweenness, closeness, eigenvector — and recognize that they
are not interchangeable. Specifically:

- High-degree nodes (hubs) are obvious and usually have redundancy.
- High-betweenness, low-degree nodes (bridges) are the actual
  load-bearing structure — and they're invisible if you only look at
  degree.
- A removal simulation confirms: removing the top-5 by betweenness
  fragments the network much more than removing the top-5 by degree.

## Prerequisites

- The case study lab: [Centrality & Criticality](../../docs/case-studies/centrality.html).
- Case study 01 (Build a Network) so you're comfortable with
  `igraph`.
- R packages: `dplyr`, `tibble`, `igraph`, `ggplot2`, `here`.
- Python packages: see [`code/requirements.txt`](../requirements.txt).

## Files in this folder

```
04_centrality/
├── README.md
├── example.R
├── example.py
├── functions.R
├── functions.py
└── data/
    ├── nodes.csv     # 500 nodes (480 regular + 20 planted bridges)
    ├── edges.csv     # ~1,000 weighted edges
    └── _generate.py
```

## How to run

```bash
Rscript code/04_centrality/example.R
python  code/04_centrality/example.py
```

## Learning check (submit this string)

> **List the 5 nodes whose `betweenness_rank - degree_rank` gap is
> largest. What is the `node_id` of the #1 entry?**

Submit the node ID. The script prints it.

## Your Project Case Study

If you pick this case study for your project, you'll find the bridges
hiding in *your* network.

### Suggested project questions

1. **Bridges in plain sight.** Compute degree and betweenness for
   every node. Find the top-10 nodes by `betweenness_rank −
   degree_rank` gap. Report what they are and why they likely have
   that pattern in your domain.

2. **Removal simulation.** Remove the top-5 nodes by each of two
   centrality measures, one at a time. Report the change in the size
   of the largest connected component (or in average path length).
   Which measure picks the more load-bearing nodes?

3. **Which centrality answers my question?** Pick a *specific*
   real-world question about your network (e.g. "which suppliers
   should we audit first?"). Argue from the question to a single
   centrality measure. Then compute it and report the top 5.

### Report

- **Question.** One sentence.
- **Network.** Nodes, edges, weights, basic sizes.
- **Procedure.** What you computed, in what order.
- **Results.** Quantities of interest as numbers in prose; at most 2
  figures and 1 table.
- **What this tells you, and what it doesn't.** 2-3 sentences. Be
  honest about cases where two centralities pick the same node — that
  doesn't make the metric "right", it just means your network
  doesn't have the bridges-vs-hubs distinction.

## Further reading

- The sts course `26C_analytics.R` runs the same comparison on a
  much larger committee-affiliation network.
- The next case study, [`05_supply-chain`](../05_supply-chain),
  turns centrality into a *resilience* question — what happens to a
  supply chain when critical nodes go offline.
