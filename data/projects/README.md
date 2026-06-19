# Project datasets

Larger, project-grade synthetic networks for SYSEN 5470 **project case studies**.
Each is bigger and richer than the lab datasets (100–500+ nodes), uniformly
documented, and ready to load in R, Python, or the in-browser playgrounds.

Each dataset folder contains:

| File | What it is |
|---|---|
| `nodes.csv` | The node list (one row per node; a `kind` column when the graph is bipartite/multimodal). |
| `edges.csv` | The edge list (`from`/`to` + weight columns; a `day`/`hour`/`period` column when temporal). |
| `*.csv` (extra) | Optional lookup tables (e.g. `zones.csv`). |
| `README.md` | At-a-glance facts + a **codebook** table for every file. |
| `load.R` / `load.py` | Lightweight loaders that build an `igraph` (R) / `networkx`-or-`igraph` (Python) object. |
| `_generate.py` | The deterministic generator (run it to reproduce the CSVs). |

## Available datasets

| Dataset | Nodes | Edges | Directed | Weighted | Bipartite | Temporal | One-line |
|---|---:|---:|:--:|:--:|:--:|:--:|---|
| [`amazon-last-mile`](amazon-last-mile/) | 313 | 2,142 | ✓ | ✓ | — | ✓ | A week of package flow: hubs → stations → delivery zones. |
| [`uber-manhattan`](uber-manhattan/) | 370 | 3,000 | — | ✓ | ✓ | ✓ | A day of driver↔rider ride-matching across downtown Manhattan. |

*More datasets are on the way (semiconductor & aerospace supply chains, mutual-aid
during a disaster, financial contagion, airline delays, power grid, and more).*

## How to use them

**In R**

```bash
Rscript data/projects/amazon-last-mile/load.R
```

```r
source("data/projects/amazon-last-mile/load.R")
g <- load_amazon()      # a directed, weighted igraph object
```

**In Python**

```bash
python data/projects/amazon-last-mile/load.py
```

```python
import sys; sys.path.insert(0, "data/projects/amazon-last-mile")
from load import load_amazon
g = load_amazon()       # a directed, weighted python-igraph object
```

**In the browser playground** — open the
[R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground and pick
the dataset from the **▾ Load sample** menu (under *Project datasets*).

## A note on the data

Every dataset is **synthetic but not random**. Each has planted, realistic
structure — usually *several* overlapping patterns — that reward genuine analysis.
The patterns are intentionally undocumented: finding and explaining them is the
project. "Bigger places have more activity" is where you start, not where you stop.

## Reproducing / contributing

Each `_generate.py` is deterministic (fixed seed). After regenerating any dataset,
mirror the CSVs into the playground's served folder:

```bash
python data/projects/<name>/_generate.py
python data/projects/_sync_to_playground.py
```

The authoring standard (folder layout, README + codebook format, loader
templates, and the "planted story" design rules) lives in the
`netsci-dataset-builder` skill under `.claude/skills/`.
