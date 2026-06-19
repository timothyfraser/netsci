---
name: netsci-dataset-builder
description: |
  Standard for authoring project-grade synthetic network datasets for SYSEN 5470,
  stored under `data/projects/<name>/`. Use this whenever creating, editing, or
  reviewing a project dataset: the folder layout, the deterministic generator
  pattern, the README + per-file "codebook" format, the R/Python loader templates,
  the playground sync + registration steps, and — most importantly — the "planted
  story" design principles that make a dataset worth analyzing. Trigger it when the
  user asks for a new dataset, a bigger network for student projects, or changes to
  anything in `data/projects/`.
---

# netsci-dataset-builder

How to build a project dataset that is **specific, reproducible, uniformly
documented, and quietly full of discoverable structure.** Follow this exactly so
every dataset feels the same to students and to the playgrounds.

## 1. Folder layout (`data/projects/<name>/`)

```
data/projects/<name>/
├── _generate.py     # deterministic generator; writes the CSVs into this folder
├── nodes.csv        # node list (one row per node)
├── edges.csv        # edge list
├── <lookup>.csv     # OPTIONAL extra table(s), e.g. zones.csv
├── README.md        # at-a-glance facts + a codebook per file (see §4)
├── load.R           # lightweight igraph loader (see §5)
└── load.py          # lightweight loader (see §5)
```

`<name>` is lowercase-hyphenated and domain-specific (`amazon-last-mile`,
`uber-manhattan`, `semiconductor-supply`). Aim for **100–500+ nodes**.

## 2. The generator (`_generate.py`)

- Deterministic: `rng = np.random.default_rng(42)` at the top; **one seed**, no
  unseeded calls. Re-running must byte-reproduce the CSVs.
- Self-contained: `pandas` + `numpy` only (igraph optional for graph-based
  construction). Resolve output with `HERE = Path(__file__).resolve().parent`.
- A module docstring lists what the network is and a short, factual list of the
  **planted parameters** (this file is the only record of the hidden design — keep
  it parameter-level, e.g. `INCOME_PENALTY = 0.16`, not a prose "the answer is…").
- Prints a one-line summary of counts at the end.
- Keep total CSV size small (well under ~5 MB) so it loads instantly in WASM.

## 3. Column conventions (so loaders & playgrounds Just Work)

- **First node column is `node_id`** (the unique key edges reference).
- **Do NOT use a node column named `name`** — `python-igraph` reserves `name` for
  the vertex id and will raise a "Vertex attribute conflict". Use `label` for a
  display name.
- Bipartite / multimodal: a single `nodes.csv` with a `kind` column
  (`driver`/`rider`, `hub`/`station`/`zone`); leave type-specific columns blank
  for rows where they don't apply.
- Edges: put the two endpoint columns **first** (`from`/`to`, `from_id`/`to_id`,
  or domain ids like `driver_id`/`rider_id`) so `graph_from_data_frame` /
  `nx.from_pandas_edgelist` pick them up. Add a clear numeric **weight** column.
- Temporal: encode time as a column (`day`, `hour`, `period`) in long format —
  one row per (edge, time) — rather than separate files per period.
- Lookup tables (e.g. `zones.csv`) are NOT node lists; document them as their own
  codebook section and have students join them on.

## 4. README format (uniform — copy this shape)

1. `# <name>` + one-italic-line tagline.
2. **## At a glance** — a 2-col table: Direction · Weights · Modality · Temporal ·
   Nodes · Edges · Files.
3. **## What this network is** — one paragraph on what nodes/edges/weights mean,
   then a short bulleted list of *example project questions*. Include a one-line
   note that the interesting findings are deliberately undocumented and that
   "busy places have more activity" is the starting point, not a finding.
4. **## `<file>.csv`** — one section per file, each a **codebook** table with
   columns exactly: `Variable | Full name | Description | Class | Example values`
   (give 2–3 real example values pulled from the data).
5. **## Load it** — the `Rscript …/load.R` and `python …/load.py` commands + the
   playground "Load sample" pointer.
6. **## Get this data** — the GitHub folder URL.

## 5. Loader templates

Match the course teaching style (see the `netsci-teaching-style` skill): roxygen
header in R / module docstring in Python, tiny `load_nodes()` / `load_edges()`
wrappers, one `load_<name>()` that returns the graph, and a `if __name__`/`if
sys.nframe()==0` demo block that prints an emoji banner + a one-screen summary so
the file runs standalone.

- **R uses `igraph`** — this is the course standard (every `code/NN_*/example.R`
  uses igraph; nothing uses tidygraph, though it's pre-installed). Build with
  `igraph::graph_from_data_frame(edges, directed=, vertices=nodes)`; set
  `E(g)$weight` and, for bipartite, `V(g)$type`. Resolve paths with
  `here::here("data","projects","<name>")`.
- **Python**: `load.py` uses `igraph.Graph.DataFrame(edges, directed=, vertices=nodes,
  use_vids=False)` (matches `code/NN_*/functions.py`). The browser **Python
  playground uses networkx**, so the playground *snippet* for the dataset uses
  `nx.from_pandas_edgelist(...)` — keep these consistent with the schema.

Always verify BOTH languages actually run: `Rscript load.R` and `python load.py`.
(R lives behind `.claude/harness/prepare-env.sh`; run it if `Rscript` is missing.)

## 6. Playground wiring

1. `python data/projects/_sync_to_playground.py` copies every dataset's CSVs into
   `docs/playground-data/<name>-<file>.csv` (flat, prefixed).
2. In **both** `docs/playground-r.html` and `docs/playground-py.html`:
   - add an `<option>` under the `<optgroup label="Project datasets (larger)">`
     in the `#sample-select` dropdown;
   - add an entry to `SAMPLE_CONFIGS` (`files`, `title`, `directed`);
   - add a `key`-matched branch to `sampleSnippet()` (igraph in -r, networkx in
     -py) that reads the prefixed CSVs and builds the graph with the right
     `directed` flag, weight, and (if bipartite) `type`.
3. Document the sample in `docs/playground-data/README.md`.
4. Update the catalog table in `data/projects/README.md`.

## 7. The planted story (the part that matters)

A project dataset is only good if it has **non-random, domain-true structure that
tells a story — and ideally several overlapping stories — that students must
discover.** Rules:

- **More volume between bigger nodes is NOT a story.** Degree∝size is the trivial
  baseline. Plant signal that *survives controlling for size/distance*: e.g.
  delivery on-time rate that drops with neighborhood income **independent of
  distance**; wait times that rise in low-income pickup zones.
- **Layer 2–4 independent stories** so different students find different things:
  an equity gradient, a hidden over-capacity node, a temporal shock that exposes a
  weak point, a mid-period structural rewiring, an earnings/attention
  concentration (high Gini), a planted community/loyalty cluster.
- **Make it falsifiable and checkable.** After generating, write a quick script
  that confirms each planted effect is present and is distinguishable from noise
  (group means by quantile, a partial correlation controlling for the obvious
  confounder, a Gini, a count of repeat ties vs chance). If you can't measure it,
  students can't either.
- **Add realistic noise** so signals aren't trivially perfect, and so location/size
  don't perfectly reveal latent attributes (e.g. income = spatial gradient + noise).
- **Never tell students the story** — not in the README, not in obvious column
  names. The `_generate.py` parameters are the only record.
- Tie the story to the course's four skills (Identify / Measure / Infer / Predict):
  a good dataset supports a centrality/criticality question, a community/projection
  question, a network-aware inference (permutation/null-model) question, and a
  prediction question.
