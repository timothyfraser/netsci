# Case Study 08 — Sampling Big Networks

> Interactive lab: [`docs/case-studies/sampling.html`](../../docs/case-studies/sampling.html)
>
> Skill: **Identify** · Data: trimmed Hurricane Dorian evacuation
> flow network (316 Florida county subdivisions, ~33,000 weighted
> edges across 8-hour time slices in the Aug 28 - Sep 10 crisis
> window)

## What you'll learn

When a network is too big to fit in memory or in your head, you
sample. But each sampling strategy preserves *different* properties:

- **Ego-centric**: pick N seed nodes, keep edges touching them.
  Preserves node-attribute distributions; can over-sample hubs.
- **Edgewise**: sample edges uniformly. Preserves edge-attribute
  distributions; may miss components.
- **Spatial buffer**: keep nodes within R km of a point of
  interest. Preserves local structure; deeply biased by where you
  drew the circle.

We measure how well each strategy reproduces a *time series* of a
normalized metric — `avg_edgeweight` per node — across the
two-week crisis window.

## Prerequisites

- Case study 02 (Joins).
- The interactive lab.
- R packages: `dplyr`, `tidyr`, `readr`, `ggplot2`, `sf`, `here`.
- Python packages: see [`code/requirements.txt`](../requirements.txt).
  Spatial operations need `geopandas` and `shapely`.

## Files in this folder

```
08_sampling/
├── README.md
├── example.R
├── example.py
├── functions.R                       # `slice_stats()` + loaders
├── functions.py
└── data/
    ├── nodes.csv                  # 316 FL county subdivisions w/ centroid x,y
    ├── edges.csv                  # ~33k 8-hour-slice evacuation flows
    ├── county_subdivisions.geojson    # FL only, simplified polygons
    └── _generate.py                   # trims the raw sts data
```

## How to run

```bash
Rscript code/08_sampling/example.R
python  code/08_sampling/example.py
```

## Learning check (submit this string)

> **Of the three sampling strategies above (`ego_centric`,
> `edgewise`, `spatial_buffer`), which one best preserves the
> population's `avg_edgeweight` time series — measured by the
> smallest max-absolute-deviation across time slices?**

Submit one of: `ego_centric`, `edgewise`, `spatial_buffer`.

## Your Project Case Study

If you pick this case study, you'll sample *your* large network
under at least two strategies and report which network properties
each one preserves vs distorts.

### Suggested project questions

1. **Strategy showdown.** Sample your network ego-centrically and
   edgewise to the same edge count. Compute normalized metrics
   (density, share of nodes linked, edge ratio, mean edge weight)
   on each. Report which metric each strategy preserves best.

2. **Sample-size convergence.** Pick one strategy. Vary the sample
   size from very small to as-large-as-the-population. Report the
   sample size at which density (or another metric you care about)
   stabilizes to within 5% of the population value.

3. **Spatial / temporal targeting.** If your network has a spatial
   or temporal structure, filter by a meaningful region or window
   *before* sampling. Compare the filtered-then-sampled network's
   properties against an unfiltered sample of the same size.

### Report

- **Question.** One sentence.
- **Network.** Nodes, edges, weight semantics, size.
- **Procedure.** Strategy/strategies, sample sizes, RNG seed.
- **Results.** Numbers in prose; at most 2 figures (the over-time
  comparison plot is the strongest); 1 table of preservation
  metrics by strategy.
- **What this tells you, and what it doesn't.** 2-3 sentences,
  including: sampling strategies are not generic — they trade off
  properties, and the right strategy depends on which property
  your question depends on.

## Further reading

- The sts course `29C_databases.R` is the parent workshop. It
  covers the same network at Gulf-states scale and develops more
  sampling strategies (random-walk, snowball).
- For a deeper dive on sampling theory in networks, see Leskovec &
  Faloutsos (2006) "Sampling from large graphs."
