# Case Study 06 — DSM Clustering

> Interactive lab: [`docs/case-studies/dsm-clustering.html`](../../docs/case-studies/dsm-clustering.html)
>
> Skill: **Measure** · Data: synthetic engineered-system DSM with 200
> components and 8 planted modules

## What you'll learn

How to find modular structure in a Design Structure Matrix
automatically. Specifically:

- Build a DSM as a directed graph from a long-format edge list.
- Apply two community-detection algorithms (Louvain and fast-greedy)
  on the undirected collapse.
- Compare the recovered partition against ground truth using the
  adjusted Rand index.
- Reorder the adjacency matrix by module membership and inspect the
  block-diagonal structure visually.
- Run a k-hop cascade simulation from a chosen component.

## Prerequisites

- Case study 01 (Build a Network).
- The interactive lab.
- R packages: `dplyr`, `tibble`, `igraph`, `ggplot2`, `here`.
- Python packages: see [`code/requirements.txt`](../requirements.txt).
  This case uses `scikit-learn`'s `adjusted_rand_score`.

## Files in this folder

```
06_dsm-clustering/
├── README.md
├── example.R
├── example.py
├── functions.R
├── functions.py
└── data/
    ├── nodes.csv    # 200 components, with `true_module` label for verification
    ├── edges.csv    # ~2,900 directed dependency edges
    └── _generate.py
```

## How to run

```bash
Rscript code/06_dsm-clustering/example.R
python  code/06_dsm-clustering/example.py
```

## Learning check (submit this answer)

> **How many modules does Louvain find in this DSM, and what is the
> modularity score (to 3 decimal places)?**  
> Submit BOTH, separated by a comma. Example: `8, 0.612`.

## Your Project Case Study

If you pick this case study, you'll apply Louvain to *your* network
and discuss what the recovered modules mean in your domain.

### Suggested project questions

1. **What are the modules in my network?** Apply Louvain. Report
   the number of modules, the modularity score, and qualitatively
   describe what 2-3 of the modules represent.

2. **Two clustering algorithms, two stories.** Run Louvain AND
   fast-greedy (or Leiden, walktrap — your choice). Report the
   modularity and number of modules for each, and discuss
   meaningful disagreements between them.

3. **Cascade analysis.** If your network has a meaningful dependency
   direction, simulate k-hop cascades from a few interesting seed
   nodes. Report which seeds produce the largest 1-hop and 2-hop
   cascades.

### Report

- **Question.** One sentence.
- **Network.** Nodes, edges, whether your dependencies are directed.
- **Procedure.** Algorithm(s) run, parameters, any preprocessing.
- **Results.** Numbers in prose; the reordered DSM is a powerful
  figure; at most 2 figures and 1 table.
- **What this tells you, and what it doesn't.** 2-3 sentences.

## Further reading

- The sts course `26C_analytics.R` runs Louvain on a much larger
  committee-affiliation network and uses the modules to make
  geographic comparisons.
- Case study 05 ([`05_supply-chain`](../05_supply-chain)) attacks the
  same question from the other side: which *individual* nodes break
  the network.
