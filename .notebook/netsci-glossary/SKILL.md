# Network Science Reference — SYSEN 5470

A reference glossary for **Network Science and Applications for Systems Engineering** (Cornell, summer 2026, Tim Fraser). This document is intended for use as a student reference and as source material for NotebookLM or similar tools. It defines the vocabulary used throughout the course and flags common conceptual mistakes.

Use it as a **dictionary**, not a textbook. When you encounter an unfamiliar term in a lab or lecture, look it up here. When you're about to recommend a method on a project, scan the "common mistakes" lists.

---

## Table of Contents

1. [Node and Edge Basics](#1-node-and-edge-basics)
2. [Centrality](#2-centrality)
3. [Community Detection](#3-community-detection)
4. [Sampling Networks](#4-sampling-networks)
5. [Inference and Resampling](#5-inference-and-resampling)
6. [Null Models](#6-null-models)
7. [Machine Learning on Networks](#7-machine-learning-on-networks)
8. [Bipartite Networks](#8-bipartite-networks)
9. [Flow and Routing](#9-flow-and-routing)
10. [Common Terminology Mistakes](#10-common-terminology-mistakes)

---

## 1. Node and Edge Basics

These are the atomic terms. Misusing them contaminates everything downstream.

- **Node / vertex** — an entity. *Engineer's use:* a station, a factory, a substation, a person.
- **Edge / tie / link** — a relationship between two nodes. *Engineer's use:* a trip, a shipment, a power line.
- **Directed vs. undirected** — does the edge have a sender and receiver? Shipments are directed; co-membership is undirected.
- **Weighted vs. unweighted** — does the edge carry a magnitude? Edge weight = riders, dollars, MW, packets/sec.
- **Self-loop** — edge from a node to itself.
- **Multi-edge / multigraph** — multiple distinct edges between the same node pair. Often collapsed to a weighted single edge.
- **Bipartite / two-mode** — nodes belong to two disjoint types; edges only run between types (members ↔ committees). See Section 8.
- **Multiplex / multilayer** — multiple edge *types* on the same node set (e.g., friendship + advice).
- **Signed** — edges carry +/− (alliance/conflict).
- **Temporal / dynamic** — edges have timestamps.
- **Ego network** — one focal node plus its neighbors and the ties among them.
- **Order-*k* neighborhood** — all nodes within *k* hops.
- **Path** — sequence of edges connecting two nodes. **Geodesic** = shortest path.
- **Walk vs. trail vs. path:**
  - *Walk:* any sequence of edges (repeats allowed)
  - *Trail:* walk with no repeated edge
  - *Path:* walk with no repeated node
- **Component** — maximally connected subgraph. **Giant component** = the dominant one.
- **Density** — fraction of possible edges that exist. *Engineer's use:* a dense supply chain has redundancy; a sparse one has chokepoints.
- **Degree** — number of edges incident to a node (in-, out-, total for directed).

---

## 2. Centrality

"Which nodes matter?" — but *matter for what?* Each centrality answers a different question. **Never use a centrality without naming the question it answers.**

### Degree centrality
- **Definition:** number of edges incident to a node.
- **Weighted variant ("strength"):** sum of incident edge weights.
- **Question:** Who is locally busy / well-connected?
- **Engineer's use:** Which stations have the most trips? Which suppliers serve the most customers?
- **Edge cases:** Sensitive to self-loops. On bipartite graphs, degree is measured against the *other* mode.

### Betweenness centrality
- **Definition:** Σ over node pairs (s,t) of σ_st(v) / σ_st, where σ_st is the number of shortest paths and σ_st(v) is the number passing through v.
- **Question:** Who is a chokepoint / broker for shortest-path traffic?
- **Engineer's use:** Which counties relay evacuation flows? Which substations are critical for power transfer?
- **Edge cases:** Computationally expensive on large graphs. Approximate via random pivots when scale demands.

### Closeness centrality
- **Definition:** (n−1) / Σ d(v, u) over all other nodes u.
- **Question:** Who can reach all others quickly on average?
- **Engineer's use:** Logistics hub siting — which warehouse minimizes mean distance to all customers?
- **Edge cases:** Undefined on disconnected graphs. Use harmonic centrality instead.

### Harmonic centrality
- **Definition:** Σ 1/d(v, u) over u ≠ v (with 1/∞ = 0).
- **Question:** Closeness, but handles disconnected components.

### Eigenvector centrality
- **Definition:** v's score is proportional to the sum of its neighbors' scores. Leading eigenvector of the adjacency matrix.
- **Question:** Who is connected to other well-connected nodes?
- **Engineer's use:** Identifying the tightly coupled core of a supply network.
- **Edge cases:** Poorly defined on directed acyclic graphs and disconnected graphs.

### PageRank
- **Definition:** Stationary distribution of a random walker that, with probability (1−d), restarts at a random node. Damping factor d typically 0.85.
- **Question:** Where does random-walk flow accumulate?
- **Engineer's use:** Webgraph importance; transit flow accumulation; influence in directed communication networks.

### Katz centrality
- **Definition:** Eigenvector centrality + attenuation factor α applied to walks of length k.
- **Question:** Importance via all paths, with longer paths discounted.
- Largely superseded by PageRank in practice.

### Hub and Authority (HITS)
- **Definition:** Hubs point to authorities; authorities are pointed to by hubs. Coupled eigenvector computation.
- **Question:** In a directed graph, who curates (hub) vs. who is the destination (authority)?
- **Engineer's use:** Citation networks; broker vs. expert in advice networks.

### Edge betweenness
- **Definition:** Same as node betweenness, but the fraction of shortest paths through an *edge*.
- **Question:** Which edges are critical to remove for fragmentation?
- **Engineer's use:** Counterfactual disruption — which edge removal does the most damage?

### How to choose

| Question | Measure |
|---|---|
| Who is locally busy? | Degree |
| Who handles the most flow? | Weighted degree |
| Who is a chokepoint? | Betweenness |
| Whose removal most fragments the network? | Edge betweenness, betweenness |
| Who can reach everyone fastest? | Closeness (harmonic if disconnected) |
| Who is in the well-connected core? | Eigenvector |
| Where does random-walk flow concentrate? | PageRank |
| Hubs vs. authorities (directed)? | HITS |

---

## 3. Community Detection

"Do nodes form groups?" — but every algorithm returns *something*, even on random graphs. Picking and *justifying* matters more than picking.

### Modularity (Q)

Not an algorithm. An objective.

- **Definition:** Q = (1/2m) Σ_{ij} [A_ij − k_i k_j / 2m] δ(c_i, c_j)
- **Interpretation:** fraction of edges within communities, minus what you'd expect under a configuration-model null with the same degree sequence.
- **Range:** roughly −0.5 to 1. Empirical "good" partitions often Q ≈ 0.3–0.7.
- **Resolution limit:** modularity cannot detect communities smaller than √(2m). Real, well-defined small communities can be missed.

### Algorithms

- **Fast-greedy (Clauset–Newman–Moore):** agglomerative merging of node pairs that maximally increase Q. Fast, deterministic, can produce uneven community sizes.

- **Louvain (Blondel et al.):** two-phase greedy modularity — local move + community aggregation, iterated. Widely used default. Can produce internally disconnected communities.

- **Leiden (Traag et al.):** Louvain + refinement step + guarantees on connectivity. Prefer over Louvain when available.

- **Infomap (Rosvall–Bergstrom):** minimizes the description length of random walks on the graph. Best for flow-like networks (transit, information diffusion, evacuation).

- **Walktrap (Pons–Latapy):** short random walks tend to stay within communities; cluster nodes by walk-derived distance.

- **Label propagation:** each node adopts the most frequent label among its neighbors, iteratively. Very fast, but stochastic and can produce degenerate partitions.

- **Spectral clustering:** k-means on the leading eigenvectors of the (normalized) Laplacian. Requires k specified in advance.

- **Girvan–Newman (edge betweenness):** iteratively remove edge with highest betweenness; communities emerge from the splits. Slow but conceptually elegant.

- **Stochastic Block Model (SBM):** generative model — nodes assigned to blocks, edge probability depends on block pair. Degree-corrected variant handles heterogeneous degrees.

### How to choose

| Situation | Try |
|---|---|
| First-pass, want something reasonable | Leiden (or Louvain) |
| Flow-like network (transit, info) | Infomap |
| Need deterministic + fast | Fast-greedy |
| Need principled model + uncertainty | SBM |
| Bipartite | Bipartite-specific (BRIM, bipartite SBM) |

### Validating a partition

- **Stability under resampling:** rerun on bootstrapped/jackknifed versions; how often do the same nodes co-cluster?
- **Stability across algorithms:** do multiple algorithms produce similar partitions? Use Adjusted Rand Index (ARI), Normalized Mutual Information (NMI).
- **External validation:** does the partition correlate with known attributes (geography, function)?
- **Modularity comparison to null:** is Q higher than Q on configuration-model nulls?

---

## 4. Sampling Networks

You rarely observe the whole network. The sampling strategy determines what biases you inherit.

- **Census** — observe all nodes and all edges.

- **Ego-centric sample** — (1) sample a set of nodes (egos) by some scheme; (2) collect all edges incident to the egos. Two-stage. Preserves local structure around egos; over-represents edges incident to high-degree nodes.

- **Edgewise / random edge sample** — sample edges directly. High-degree nodes appear more often (many edges to be sampled). Average degree of sampled nodes > population average.

- **Snowball sample** — start with seed nodes (wave 0). Wave 1 = their neighbors. Wave 2 = wave-1 neighbors' neighbors. Continue for *k* waves. Good for hidden populations (criminal networks). Strongly favors high-degree nodes.

- **Random walk sample** — walk the graph and record visited nodes. Long-run sampling probability ≈ proportional to degree.

- **Induced subgraph sample** — sample a node set S. Keep only edges where *both* endpoints are in S. Drops many edges.

- **Star sample** — one focal node + its neighbors only (no neighbor-of-neighbor ties).

- **Time-slice sample** — for temporal nets, sample by time window.

### Comparing strategies

| Strategy | Preserves degree dist? | Preserves clustering? |
|---|---|---|
| Census | Yes | Yes |
| Ego-centric | Locally yes | Yes (around egos) |
| Edgewise | No (biased high) | No |
| Snowball | No (biased high) | Yes (within waves) |
| Random walk | No (biased ∝ degree) | Partial |
| Induced subgraph | No (biased low) | No |

### Sampling vs. resampling

These are **different**:
- **Sampling:** how you got your data. Once, from a population.
- **Resampling:** how you assess uncertainty from your data. Repeated, from your sample.

---

## 5. Inference and Resampling

Statistical inference on networks is hard because observations aren't independent. Edges share nodes; nodes share neighborhoods. Standard standard-error formulas are wrong by default.

### The core idea

Network-aware inference asks: *Given the structure of the network, would this pattern arise by chance?* The "chance" is defined by a null hypothesis enforced through resampling or permutation.

### Permutation tests

**Generic permutation test:** under the null, shuffle some label or structure. Recompute the statistic. Repeat *B* times (typically 1000–10000). The p-value is the fraction of null statistics at least as extreme as observed. **Key choice:** what gets shuffled defines the null.

**Node attribute permutation:** keep graph structure fixed; shuffle a node attribute (e.g., gender, geography) across nodes. Tests whether the attribute is unrelated to graph position.

**Edge permutation:** shuffle edges while preserving some property (often the degree sequence — see configuration model in Section 6).

**QAP — Quadratic Assignment Procedure:** permutation test for matrix-on-matrix correlation. Shuffles rows *and* columns of one matrix together (preserves matrix structure). Used for testing whether two relational matrices (e.g., trade and shared language) are associated.

**MRQAP — Multiple Regression QAP:** linear regression with dyadic predictors; standard errors via QAP-style permutation. Variants:
- **Y-permutation:** shuffle the outcome matrix; biased when predictors are correlated.
- **Double semi-partialling (DSP):** residualize each predictor against the others, permute residuals. Reduces inflation. Standard for modeling dyadic outcomes (trade, communication) with correlated network covariates.

### Resampling for uncertainty

#### Jackknife
- **Primary purpose:** variance estimation (Quenouille/Tukey; predecessor to the bootstrap). Per-node influence diagnostics fall out as a side effect.
- **Node jackknife:** leave one node out at a time, recompute statistic θ̂_(i). *n* recomputations total.
- **Jackknife SE:** SE_jack = √[(n−1)/n · Σ_i (θ̂_(i) − θ̂_(·))²], where θ̂_(·) is the mean of the leave-one-out estimates.
- **Edge jackknife:** leave one edge out at a time.
- **Strengths:** deterministic; fixed at *n* recomputations; the leave-one-out estimates also reveal which nodes/edges drive the result.
- **Weaknesses:** assumes a smooth functional. Famously fails for the median and other non-smooth statistics; delete-*d* jackknife is the standard fix. On large graphs, *n* recomputations may not be cheap.

#### Bootstrap variants

Bootstrap on networks is hazardous because resampled networks usually have *different density* than the original. Always specify what is resampled and why.

- **Naive node bootstrap:** sample *n* nodes with replacement; induced subgraph as bootstrap sample. Density typically too low. Biased.
- **Edge bootstrap:** sample *m* edges with replacement. Better for edge-level statistics; node set may shrink.
- **Snowball bootstrap:** respects the wave structure of the original snowball sample.
- **Vertex / patchwork bootstrap (Snijders–Borgatti):** block-bootstrap idea — resample local neighborhoods, stitch together.
- **Subsampling (m-out-of-n):** sample *m* < *n* nodes without replacement, recompute, rescale. More defensible asymptotically for network statistics than naive bootstrap.

#### Permutation vs. bootstrap vs. jackknife — what each distribution represents

The cleanest distinction is *what the resampling distribution approximates*, not what you do with it. There is overlap (you can invert a permutation test to get a CI; you can use the bootstrap for testing) but the canonical pairing is:

| Procedure | Resampling distribution approximates | Canonical use |
|---|---|---|
| Permutation | Distribution of statistic under H₀ | p-value against a specific null |
| Bootstrap | Sampling distribution of θ̂ | CI, SE |
| Jackknife | Sampling distribution of θ̂ (smooth case) | SE, influence diagnostics |

Typical pairings:
- Test "is this pattern more than chance given degrees?" → permutation against configuration model.
- SE on a centrality measure → jackknife (deterministic) or subsampling.
- CI on a dyadic regression coefficient → MRQAP with DSP (permutation).

### Generative models (vocabulary reference)

- **ERGM (Exponential Random Graph Model):** models the probability of observing the entire graph as exp(Σ θ_i s_i(g)) / κ. Interpretation: log-odds of an edge given the rest of the graph.
- **TERGM (Temporal ERGM):** ERGM for sequences of graphs over time.
- **SAOM / SIENA (Stochastic Actor-Oriented Model):** ties evolve through actor-level utility maximization. Continuous-time Markov process.
- **Latent space model:** nodes have coordinates in a low-dimensional space; edge probability decreases with distance.
- **SBM (Stochastic Block Model):** nodes assigned to blocks; edge probability depends on block pair.

---

## 6. Null Models

"More than expected" requires specifying *expected under what*. The null model is the comparison baseline.

- **Erdős–Rényi G(n, p):** every possible edge exists independently with probability *p*. Preserves *n*, expected edge count. **Use sparingly** — real networks have skewed degree distributions and ER nulls declare almost everything significant.

- **Erdős–Rényi G(n, m):** *n* nodes, exactly *m* edges placed uniformly at random.

- **Configuration model:** preserves the degree sequence exactly; edges otherwise random. Mechanism: stub-matching — give each node *k_i* "half-edges," pair them up uniformly. **The standard null for "more than expected given the degree distribution."**

- **Degree-preserving rewiring (Maslov–Sneppen):** randomly pick two edges (a→b) and (c→d); rewire to (a→d) and (c→b). Preserves every node's degree. Markov-chain way to sample from the configuration model.

- **Bipartite configuration model:** preserves both row degrees (mode-1 node degrees) and column degrees (mode-2 node degrees). The right null for bipartite projections.

- **Stochastic Block Model as null:** preserves block structure as well as within/between block edge probabilities. Degree-corrected variant preserves both.

- **Spatial / geographic null:** edge probability constrained by spatial distance. In spatial networks, most ties are short-range by geography alone — without controlling for this, any spatial pattern looks "significant." Variants: gravity model (P(edge) ∝ pop_i · pop_j / d^α), radiation model.

### Choosing a null

| Question | Null |
|---|---|
| Given degree distribution, is there more clustering than expected? | Configuration model |
| Given degree + community structure, is there more X than expected? | Degree-corrected SBM |
| In a bipartite graph, is this projection's structure > chance? | Bipartite configuration model |
| In a spatial network, is this non-spatial pattern > chance? | Spatial null (gravity, distance-binned) |

### Practical workflow

1. State the question precisely.
2. Pick the null that holds fixed exactly what you're *not* trying to test.
3. Sample *B* networks from the null (B ≥ 1000 typical).
4. Compute the statistic on each.
5. Compare observed to null distribution.

---

## 7. Machine Learning on Networks

The course's ML arc: heuristic baselines → node embeddings → GNNs → temporal GNNs.

### Two outputs to keep straight

1. **Embeddings** — vector representations of nodes (or edges, or graphs). The *output* of representation learning. Not predictions.
2. **Predictions** — outputs of a task head applied to embeddings (or to raw features).

A GNN with no task head produces embeddings. Treating embeddings as predictions is a category error.

### Shallow embedding methods

- **DeepWalk:** generate random walks; treat as "sentences" of node IDs; run Word2Vec (skip-gram). Output: d-dimensional vector per node.
- **Node2Vec (Grover & Leskovec):** DeepWalk + biased random walks controlled by parameters *p* (return) and *q* (in-out). Low *q* → DFS-like (communities); high *q* → BFS-like (structural roles). **Not a GNN** — no message passing.
- **LINE:** preserves 1st-order (direct neighbors) and 2nd-order (shared neighbors) proximity separately.
- **Spectral embedding:** eigenvectors of the normalized Laplacian as coordinates.

### Graph Neural Networks

The defining operation is **message passing**: each node updates its representation by aggregating transformed messages from its neighbors. Stacking *k* layers expands the receptive field to *k*-hop neighborhood.

- **GCN (Graph Convolutional Network, Kipf & Welling):** symmetric-normalized neighborhood averaging. Simple baseline. Susceptible to oversmoothing with many layers.

- **GraphSAGE (Hamilton et al.):** sample neighbors, aggregate (mean/max-pool/LSTM). Inductive (handles unseen nodes); scales via neighborhood sampling.

- **GAT (Graph Attention Network):** learnable