# Case Study 10 — GNN by Hand

> Interactive lab: [`docs/case-studies/gnn-by-hand.html`](../../docs/case-studies/gnn-by-hand.html)
>
> Skill: **Predict** · Data: 6-node toy supply chain (in lockstep
> with the case study lab) + 200-node project-scale variant with
> planted bottlenecks

## What you'll learn

A Graph Neural Network's "magic" is one specific arithmetic step:
**neighborhood aggregation**. This case strips a GCN down to its
forward pass in numpy and walks through it node by node. You will:

- Build the adjacency matrix with self-loops.
- Symmetric-normalize it (Kipf & Welling 2017).
- Apply a single GCN layer: `H = ReLU(A_norm @ X @ W)`.
- Stack a second layer.
- See that the *bottleneck* node — which has no special features but
  many converging neighbors — ends up with the largest embedding
  values. That's GNN aggregation showing up exactly where you'd hope.

## Track note: this case is Python-primary

R doesn't have a widely-used, well-maintained Graph Neural Network
library. The R file in this folder (`example.R`) is a stub pointing
at `example.py` and showing how to call the Python script from R via
`reticulate`. For both the learning check and the project, use the
Python version.

## Prerequisites

- The interactive lab.
- Case study 04 (Centrality) so you've seen what "neighborhood"
  means structurally.
- Python packages: see [`code/requirements.txt`](../requirements.txt).
  This case uses only `numpy`, `pandas`, and `matplotlib`.

## Files in this folder

```
10_gnn-by-hand/
├── README.md
├── example.R           # stub pointing to example.py
├── example.py          # the actual content
├── functions.py        # adjacency(), normalize(), gcn_layer()
└── data/
    ├── tiny_nodes.csv  / tiny_edges.csv   # 6-node toy
    ├── large_nodes.csv / large_edges.csv  # 200-node project-scale
    └── _generate.py
```

## How to run

```bash
python code/10_gnn-by-hand/example.py
```

## Learning check (submit this string)

> **With the layer weights `W1` and `W2` defined in `example.py`
> (symmetric normalization, ReLU, self-loops), what is the final
> embedding (3 numbers) for node 4 on the *tiny* network?**

Submit a comma-separated string of three numbers rounded to 4
decimal places. Example format: `0.1234, -0.5678, 0.9012`.

## Your Project Case Study

If you pick this case study, you'll implement the GNN forward pass
on a slice of *your* network and discuss what the embeddings encode.

### Suggested project questions

1. **Embed your nodes.** Build a 2-feature input matrix from any
   two node attributes in your network. Run a 1-layer GCN with
   sensible random or hand-picked weights. Report the top 5 nodes
   by L2 norm of the embedding, and discuss what they have in
   common structurally.

2. **Aggregation choices.** Implement the GCN with three different
   aggregations: sum, mean, and max-pool over neighbors. Report
   the top-5 nodes by embedding-L2 under each, and discuss why
   different aggregations highlight different nodes.

3. **Depth matters.** Run 1-, 2-, and 3-layer GCNs on the same
   features. Report how the embedding's "receptive field" grows
   with depth. Find a node whose embedding *changes most* between
   1 layer and 3 layers.

### Report

- **Question.** One sentence.
- **Network.** Nodes, edges, input features (and where they came
  from), N, E.
- **Procedure.** Layer dims, weights (fixed or random with seed),
  activation, normalization.
- **Results.** Numbers in prose; a 2-D embedding scatter colored by
  some structural property is a strong figure.
- **What this tells you, and what it doesn't.** 2-3 sentences,
  especially: hand-built GCNs with non-learned weights are useful
  for *intuition*, not for prediction; for prediction you'd train
  the weights against a label.

## Further reading

- Kipf & Welling (2017) "Semi-Supervised Classification with Graph
  Convolutional Networks" — the original GCN paper.
- The next case study, [`11_gnn-xgboost`](../11_gnn-xgboost),
  combines GNN embeddings with classical gradient-boosted trees
  for actual prediction.
