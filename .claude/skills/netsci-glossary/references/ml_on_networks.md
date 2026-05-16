# ML on Networks — Full Reference

The course's ML arc: heuristic baselines → node embeddings → GNNs → temporal GNNs. This file covers the vocabulary; Tim's course materials cover the pedagogical sequencing.

## The two outputs to keep straight

1. **Embeddings** — vector representations of nodes (or edges, or graphs). The *output* of representation learning. Not predictions.
2. **Predictions** — outputs of a task head applied to embeddings (or to raw features). Node class, link probability, regression value.

A GNN with no task head produces embeddings. Treating embeddings as predictions is a category error (see `red_flags.md` #10).

## Shallow embedding methods

### DeepWalk
- **How:** generate random walks from each node; treat walks as "sentences" of node IDs; run Word2Vec (skip-gram) on them.
- **Output:** d-dimensional vector per node.
- **Interpretation:** nodes appearing in similar walk contexts get similar vectors.

### Node2Vec (Grover & Leskovec)
- **How:** DeepWalk + biased random walks controlled by two parameters:
  - *p* (return parameter) — likelihood of revisiting the previous node.
  - *q* (in-out parameter) — likelihood of moving away from vs. staying near the source.
- **Effect:** low *q* → DFS-like exploration (community structure); high *q* → BFS-like (structural roles).
- **Output:** d-dimensional embeddings.
- **Not a GNN.** No message passing, no convolution. Shallow.

### LINE — Large-scale Information Network Embedding
- Preserves 1st-order (direct neighbors) and 2nd-order (shared neighbors) proximity separately, then concatenates.

### Spectral embedding
- Eigenvectors of the (normalized) Laplacian as coordinates. Mathematically clean; doesn't scale to massive graphs.

## Graph Neural Networks

The defining operation is **message passing**: each node updates its representation by aggregating transformed messages from its neighbors. Stacking layers expands the receptive field — *k* layers → information from *k*-hop neighborhood.

### GCN — Graph Convolutional Network (Kipf & Welling)
- **Update rule:** h_v^{l+1} = σ(Σ_{u ∈ N(v) ∪ {v}} (1/√(d_u d_v)) W^l h_u^l)
- **Aggregation:** symmetric-normalized sum.
- **Strengths:** simple, well-studied; good baseline.
- **Weaknesses:** oversmoothing with many layers; same weight for all neighbors.

### GraphSAGE (Hamilton et al.)
- **Update rule:** h_v^{l+1} = σ(W · CONCAT(h_v^l, AGG({h_u^l : u ∈ N(v)})))
- **Aggregation:** mean, max-pool, or LSTM over a sampled neighborhood.
- **Strengths:** inductive (can handle unseen nodes); scales to large graphs via neighborhood sampling.

### GAT — Graph Attention Network (Veličković et al.)
- **Update rule:** uses learned attention weights α_uv over neighbors u of v.
- **Strengths:** different neighbors can have different importance; interpretable attention weights.
- **Weaknesses:** more parameters, slower.

### GIN — Graph Isomorphism Network
- Maximally expressive within the Weisfeiler–Lehman test hierarchy. Often a strong baseline for graph-level tasks.

### Temporal GNNs
- **EvolveGCN:** GCN weights evolve over time via an RNN.
- **TGN:** memory module updated per event; popular for streaming graphs.
- **DySAT, GCRN, etc.** — many variants. Used when the graph itself changes over time, not just node features.

## Tasks

| Task | What you predict | Example |
|---|---|---|
| Node classification | Class label per node | Is this supplier high-risk? |
| Node regression | Continuous value per node | Expected delivery delay |
| Link prediction | Edge exists / will exist | Will these two firms transact? |
| Edge classification | Type/attribute of known edge | Trade vs. financing relationship |
| Graph classification | Label for whole graph | Is this molecule toxic? |
| Graph regression | Value for whole graph | Solubility |
| Community detection | Cluster assignment | (often unsupervised) |

## The hybrid pipeline (course's running example)

GNN-as-feature-extractor + XGBoost-as-predictor:

1. Train a GNN on the supply chain network with some auxiliary task (or use unsupervised embeddings).
2. Extract node embeddings from a hidden layer.
3. Feed embeddings (+ tabular features) into XGBoost for the actual prediction.

**Why this is honest:** GNNs are sample-hungry and easy to overfit on small graphs. XGBoost on extracted features is more interpretable and often performs as well or better at lab scale.

## When to reach for what

| Situation | Try |
|---|---|
| Tabular features per node, no graph structure used | XGBoost on features |
| Want graph structure as features for prediction | Node2Vec embeddings + XGBoost |
| Want end-to-end learning with structure | GCN or GraphSAGE |
| Different neighbors matter differently | GAT |
| Large graph, can't fit in memory | GraphSAGE (with sampling) |
| Time-varying graph | Temporal GNN |
| Need probabilistic / generative model | Latent space model, SBM (not a GNN) |

## Statistical vs. ML domains (course principle)

- **ML dominates:** prediction tasks, large-feature regimes, when you don't need to interpret coefficients.
- **Statistics retains primacy:** uncertainty quantification, causal inference, when β coefficients are the deliverable.
- **Trees are assumption-free** about residual variance. Classical diagnostics (heteroskedasticity, residual normality) largely irrelevant for XGBoost.
- **Emerging frontier:** causal inference under network interference. Mostly statistical.

## Common mistakes

- Calling Node2Vec a GNN. It's not.
- Treating embeddings as predictions.
- Stacking too many GNN layers — oversmoothing collapses node representations.
- Reporting GNN accuracy without comparing to a simple baseline (degree centrality + XGBoost often wins on small graphs).
- Using a transductive method (vanilla GCN) when new nodes will appear at test time — need an inductive method (GraphSAGE, GAT).
- Forgetting that link prediction is severely class-imbalanced (most node pairs are not connected). Don't report accuracy; report AUC or PR-AUC.
