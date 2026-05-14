# Case Study 02 — Network Joins

> Interactive lab: [`docs/case-studies/joins.html`](../../docs/case-studies/joins.html)
>
> Skill: **Identify** · Data: slim Bluebikes-flavored sample (synthetic but
> deterministic — same answer for everyone)

## What you'll learn

When a network's edges live in one table and its node traits live in
another, the JOIN is where the real analysis happens. This case walks
you through:

- a **single-node join** (tagging each edge with a trait of its *start*
  node),
- a **double-node join** (start *and* end, with proper renames so the
  two attributes don't collide),
- aggregating the joined edges to a small 2×2 quantity of interest,
- and a 2×2 heatmap that communicates the result honestly.

If you can do this fluently, you can do 80% of all network analysis on
big tabular data without reaching for anything fancier.

## Prerequisites

- The case study lab: [Network Joins](../../docs/case-studies/joins.html).
- R packages: `dplyr`, `readr`, `ggplot2`, `here`.
- Python packages: see [`code/requirements.txt`](../requirements.txt) —
  you need `pandas`, `pyarrow`, `matplotlib`, `seaborn`.

## Files in this folder

```
02_joins/
├── README.md         # this file
├── example.R         # R track: do the joins with dplyr
├── example.py        # Python track: do the joins with pandas
├── functions.R       # tiny path-resolved data loaders for R
├── functions.py      # tiny path-resolved data loaders for Python
└── data/
    ├── edges.csv     # ~50,000 AM rush 2021 trip rows
    ├── stations.csv  # ~500 stations with a maj_black flag
    └── _generate.py      # how the parquet files are made (deterministic)
```

## How to run

R:
```bash
Rscript code/02_joins/example.R
```

Python:
```bash
python code/02_joins/example.py
```

Both should finish in well under 10 seconds and produce the same
Learning Check answer.

## Learning check (submit this number)

> **How many AM rush rides in 2021 in this slim sample started AND
> ended in a majority-Black block group?**

The number is printed at the bottom of either `example.R` or
`example.py`. Put it into the learning-check form on the website.

## Your Project Case Study

If you pick this case study as one of your project case studies, you'll
apply the join-and-aggregate pattern to **your own network** (≥ 100
nodes, ≥ 1,000 strongly preferred). You'll submit:

1. A `project.R` *or* `project.py` that runs your full analysis,
2. A short report (2 pages minimum, your own words — not AI-generated)
   that states the question, your operationalization of the network,
   the procedure, and the results as numeric quantities of interest in
   prose, with supporting tables/figures.

### Suggested project questions

Pick one. Each is a real question this method can answer.

1. **Attribute homophily on edges.** Take a categorical node attribute
   that matters in your domain (firm tier, region, race, department,
   product line). Do a double-node join, then compute the 2×2 (or
   n×n) "what % of edge weight stays within-group vs crosses
   groups." Report the four/N² percentages with a heatmap.

2. **Aggregate-before-join vs join-before-aggregate.** Demonstrate the
   speed and memory difference between (a) joining all node traits
   onto every edge and *then* aggregating, vs (b) aggregating first
   and joining a small result. Report wall-clock time and peak rows
   in memory for each pipeline.

3. **Silent collision audit.** Take an edge table and join it with two
   different node attributes from the same node table. Show what
   happens when you forget to rename. Then show the renamed version
   side-by-side. Report which one you'd want to debug a year from
   now.

You don't have to write all three. Pick the one that fits your
network best.

### What goes in the report

- **Question.** One sentence stating what you set out to learn.
- **Network.** What are the nodes? What are the edges? Where did
  the data come from? How many nodes, how many edges, how dense?
- **Procedure.** The steps you ran, in plain language. Why those
  steps, in that order.
- **Results.** State the quantities of interest *as numbers, in
  prose*. Support with at most 2 figures and 1 table.
- **What this tells you, and what it doesn't.** Two-three sentences.

## Further reading

- The sts course `21C_databases.R` script extends this idea to a
  multi-million-row SQLite database with `dbplyr`. If your network
  data lives in SQL, that's worth reading.
- The next case study, [`03_aggregation`](../03_aggregation), reuses
  this exact dataset to show how the same joined table can be viewed
  at three resolutions.
