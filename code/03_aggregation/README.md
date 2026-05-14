# Case Study 03 — Aggregation

> Interactive lab: [`docs/case-studies/aggregation.html`](../../docs/case-studies/aggregation.html)
>
> Skill: **Identify** · Data: slim mobility-flow sample with neighborhood
> + income-quintile annotations (500 stations, 40,000 trip rows)

## What you'll learn

Aggregation isn't a chore — it's a way of *finding the question*. The
same network looked at at three different resolutions tells three
different stories. This case walks you through:

- viewing 500-station traffic at the raw station-pair resolution
  (a hairball; the only honest visual is a distribution),
- aggregating to the neighborhood resolution (12×12, a heatmap with
  visible diagonal stickiness),
- aggregating to the income quintile resolution (4×4, where the
  equity question becomes legible).

## Prerequisites

- The case study lab: [Aggregation](../../docs/case-studies/aggregation.html).
- Case study 02 (Joins) — this one assumes you're comfortable with
  double-side joins.
- R packages: `dplyr`, `tidyr`, `readr`, `ggplot2`, `viridis`, `here`.
- Python packages: see [`code/requirements.txt`](../requirements.txt).

## Files in this folder

```
03_aggregation/
├── README.md
├── example.R
├── example.py
├── functions.R
├── functions.py
└── data/
    ├── edges.csv     # 40,000 AM rush 2021 trip rows
    ├── stations.csv  # 500 stations with neighborhood + income_quintile
    └── _generate.py
```

## How to run

```bash
Rscript code/03_aggregation/example.R
python  code/03_aggregation/example.py
```

## Learning check (submit this number)

> **What percentage of all AM rush 2021 trips stay within the *top*
> income quintile (Q4 → Q4)?**

The number is printed at the bottom of either example script.

## Your Project Case Study

If you pick this case study, you'll view your own network at multiple
resolutions and report which one reveals signal. Submission:
`project.R`/`project.py` + a 2-page-minimum report in your own words.

### Suggested project questions

1. **At what resolution does my network become legible?** View your
   network at the raw, mid-resolution, and high-resolution levels.
   Report which resolution best supports the question you actually
   care about, and why.

2. **Diagonal stickiness.** Aggregate your network by a categorical
   node attribute. Compute the fraction of edge weight on the
   diagonal vs off-diagonal. State the number in prose and discuss
   what it means in your domain.

3. **Two competing aggregations.** Aggregate your network by two
   different node attributes (e.g. tier vs region). Report which
   aggregation makes the structural pattern clearer.

### What goes in the report

- **Question.** One sentence.
- **Network.** Nodes, edges, attribute(s) you aggregated by.
- **Procedure.** What you did at each resolution, in order.
- **Results.** Numbers in prose, plus at most 2 figures and 1 table.
- **What this tells you, and what it doesn't.** 2-3 sentences.

## Further reading

- This is the descriptive-statistics complement to case studies on
  centrality (case 04) and community detection (case 06). The sts
  course `22C_datacom.R` makes the same point on the real (multi-GB)
  Bluebikes data.
