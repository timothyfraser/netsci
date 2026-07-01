# Case Study 01 — Build a Network

> Interactive lab: [`docs/case-studies/build-a-network.html`](../../docs/case-studies/build-a-network.html)
>
> Skill: **Identify** · Data: synthetic bipartite supplier ↔ component
> network (200 nodes, 577 edges)

**New to "bipartite"?** It just means the network has **two kinds of nodes**, and
edges only run *between* the kinds, never within. Here the kinds are suppliers and
components: a supplier links to the components it makes, but suppliers never link
directly to suppliers. The "one-mode projection" (below) collapses that into a
supplier-to-supplier network where two suppliers connect if they share a component.

## What you'll learn

How to take node and edge data sitting in two tables and turn them
into a real graph object you can compute on. Specifically:

- Load a node table and an edge table.
- Build an `igraph` object from them, in either R or Python.
- Check basic properties (number of vertices, edges, degree
  distribution).
- For a bipartite network (two kinds of nodes — suppliers and
  components), do a **one-mode projection** so you can ask
  "which suppliers are exposed to the same components."

This case is the *foundation* for every other case study in the
course. If you understand it, the rest are about *what to do once
you have a graph*.

## Prerequisites

- The case study lab: [Build a Network](../../docs/case-studies/build-a-network.html).
- R packages: `dplyr`, `readr`, `tibble`, `igraph`, `ggplot2`, `here`.
- Python packages: see [`code/requirements.txt`](../requirements.txt).

## Files in this folder

```
01_build-a-network/
├── README.md
├── example.R
├── example.py
├── functions.R
├── functions.py
└── data/
    ├── nodes.csv     # 200 nodes (80 suppliers + 120 components)
    ├── edges.csv     # 577 supplier->component ship-relationships
    └── _generate.py  # how the CSVs are made (deterministic, seeded)
```

## How to run

R:
```bash
Rscript code/01_build-a-network/example.R
```

Python:
```bash
python code/01_build-a-network/example.py
```

> **Run from the repo root.** These scripts resolve their data files with
> `here::here()` (R) and repo-relative paths (Python), so they behave the
> same on every machine — but only if your working directory is the repo
> root. A "file not found" error almost always means you're inside `code/`
> instead of at the top. (That's *why* the course uses `here::here()`: it
> pins paths to the project root instead of wherever you happened to launch.)

### Python note: building a graph from *string* node IDs

`igraph`'s `Graph.DataFrame()` expects **integer** vertex IDs. If your own
project data uses string names (e.g. `"E0004"`), it raises
`TypeError: ... must be 0-based integers`. Map names to integers first, then
keep the names as a vertex attribute:

```python
import igraph as ig

names = nodes["node_id"].tolist()
idx   = {name: i for i, name in enumerate(names)}      # string -> 0-based int
g = ig.Graph(
    n=len(names),
    edges=[(idx[a], idx[b]) for a, b in zip(edges["from_id"], edges["to_id"])],
    directed=False,
)
g.vs["name"] = names   # restore the original string IDs as a vertex attribute
```

(The lab's own `example.py` sidesteps this inside `functions.py`; you'll hit
it the first time you build *your own* network for the project.)

## Learning check (submit this number)

> **In the supplier-supplier one-mode projection, what is the degree of
> supplier `S017`?** (i.e. how many other suppliers share at least one
> component with `S017`?)

The number is printed at the bottom of either `example.R` or
`example.py`.

## Your Project Case Study

If you pick this case study as one of your project case studies, you'll
build a graph from *your own* data (≥ 100 nodes, ≥ 1,000 strongly
preferred), inspect basic structure, and — if your network has two
kinds of nodes — do a one-mode projection.

You'll submit:

1. `project.R` or `project.py` with the full pipeline.
2. A short report (5 pages minimum of text — figures and tables don't
   count; your own words, not AI-generated) stating the question, the
   network's operationalization, the procedure, and results as numeric
   quantities of interest in prose with supporting tables/figures.

### Suggested project questions

Pick one.

1. **From data to graph.** Take a tabular dataset from your field
   that *isn't* obviously a graph (e.g. coauthorships, shipments,
   support tickets). Define what a node is, what an edge is, what
   the edge weight should be, and justify each choice in prose.
   Build the graph and report basic properties: N, E, density,
   degree distribution.

2. **Bipartite projection in your domain.** Find a real bipartite
   structure in your field (people↔projects, firms↔contracts,
   reviewers↔papers, doctors↔procedures). Build the bipartite
   graph; project it both ways; report what the projection reveals
   that the bipartite graph alone does not.

3. **Two encodings, two stories.** Take the same underlying data and
   build it as a graph in two different ways (e.g. directed vs
   undirected, weighted vs binary, thresholded at two different
   weights). Report which structural conclusions change and which
   are robust.

### What goes in the report

- **Question.** One sentence.
- **Network.** Nodes, edges, weights, where the data came from, basic
  size statistics.
- **Procedure.** What you did, in order, in plain language.
- **Results.** Quantities of interest as numbers in prose, supported
  by at most 2 figures and 1 table.
- **What this tells you, and what it doesn't.** 2-3 sentences.

## Further reading

- The next case study, [`02_joins`](../02_joins), assumes you already
  have edges and nodes in a graph and asks what to *do* with them.
- The sts course `24C_analytics.R` extends this idea into much
  larger committee-affiliation networks with `tidygraph`.
