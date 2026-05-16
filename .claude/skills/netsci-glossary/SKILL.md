---
name: netsci-glossary
description: Authoritative vocabulary reference for network science work in SYSEN 5470 (Cornell graduate course on Network Science for Systems Engineering). Use this skill whenever the conversation touches network analysis concepts — centrality, community detection, sampling, permutation tests, bootstraps, jackknifes, null models, GNNs, node embeddings, bipartite projection, routing/flow, ERGMs, or any tidygraph/igraph function. Trigger this skill aggressively, not just when terms are defined explicitly — also when Claude is about to recommend a method, map a concept to R code, draft a learning check, or compare two approaches. The skill exists because (a) network science vocabulary is dense and error-prone, (b) the course has its own conceptual emphasis (network-aware inference, counterfactual disruption, GNN-based prediction, graph framing), and (c) drift in terminology between Claude and the instructor wastes both their time. If the user mentions networks, graphs, nodes, edges, ties, centrality, communities, paths, flows, or resampling on networks — load this skill before responding.
---

# Network Science Glossary — SYSEN 5470

This is a shared dictionary between Claude and the instructor (Tim Fraser) for designing the network science course. Its job is to **prevent terminology drift**, not to teach network science from scratch.

## How to use this skill

1. **Skim this file first.** It contains tight definitions for every concept that comes up in the donor scripts (21C–29C) and the course modules.
2. **Read the relevant `references/` file** when going deep on a topic — when drafting a learning check, comparing methods, mapping to R code, or when the user asks for nuance.
3. **Check `references/red_flags.md`** before recommending a method or writing a definition — Claude has well-known failure modes in this domain.
4. **Use the R-function mapping** (inline in each section below) — the donor course uses `tidygraph` + `igraph` idioms; do not invent function names.

## Reference files

- `references/centrality.md` — Full centrality measures with formulas, edge cases, engineer's use
- `references/community.md` — Clustering/community algorithms, modularity, when each fails
- `references/sampling.md` — Ego-centric, edgewise, snowball, random walk; bias profiles
- `references/inference.md` — Permutation tests, QAP/MRQAP, jackknife, bootstrap variants
- `references/null_models.md` — Erdős–Rényi, configuration model, rewiring strategies
- `references/ml_on_networks.md` — Node2Vec, GNN/GCN/GAT, link prediction, embeddings
- `references/bipartite.md` — Two-mode, projection, coaffiliation, weighted projections
- `references/flow_routing.md` — Shortest path, max flow, min cut, TSP, VRP
- `references/red_flags.md` — Common terminology mistakes Claude makes; check before answering

---

## 1. Node and edge basics

The atomic vocabulary. Misusing any of these contaminates everything downstream.

- **Node / vertex** — an entity. *Engineer's use:* a station, a factory, a substation, a person.
- **Edge / tie / link** — a relationship between two nodes. *Engineer's use:* a trip, a shipment, a power line.
- **Directed vs. undirected** — does the edge have a sender and receiver? *Engineer's use:* shipments are directed; co-membership is undirected.
- **Weighted vs. unweighted** — does the edge carry a magnitude? *Engineer's use:* edge weight = riders, dollars, MW, packets/sec.
- **Self-loop** — edge from a node to itself. Many algorithms (e.g. `centrality_degree`) need an explicit decision about whether to include them.
- **Multi-edge / multigraph** — multiple distinct edges between the same node pair. Often collapsed to a weighted single edge.
- **Bipartite / two-mode** — nodes belong to two disjoint types; edges only run between types (members ↔ committees). See `references/bipartite.md`.
- **Multiplex / multilayer** — multiple edge *types* on the same node set (e.g. friendship + advice).
- **Signed** — edges carry +/− (alliance/conflict).
- **Temporal / dynamic** — edges have timestamps. The Hurricane Dorian and Bluebikes datasets are both temporal.
- **Ego network** — one focal node plus its neighbors and the ties among them. Distinct from *ego-centric sample* (see sampling).
- **Order-*k* neighborhood** — all nodes within *k* hops. `tidygraph::local_members(order = k)` in donor 24C.
- **Path** — sequence of edges connecting two nodes. **Geodesic** = shortest path.
- **Component** — maximally connected subgraph. **Giant component** = the dominant one.
- **Density** — fraction of possible edges that exist. *Engineer's use:* a dense supply chain has redundancy; a sparse one has chokepoints.
- **Degree** — number of edges incident to a node (in-, out-, total for directed).

**R mapping:** `tbl_graph()`, `as_tbl_graph()`, `activate("nodes"|"edges")`, `centrality_degree()`, `node_is_isolated()`, `local_members()`.

---

## 2. Centrality

"Which nodes matter?" — but *matter for what?* Each centrality answers a different question. **Never recommend a centrality without naming the question it answers.** Full treatment in `references/centrality.md`.

- **Degree centrality** — how many neighbors. *Q: who is locally busy?* `centrality_degree()`.
- **Weighted degree (strength)** — sum of incident edge weights. *Q: who handles the most volume?* `centrality_degree(weights = .E()$weight)`.
- **Betweenness centrality** — fraction of shortest paths passing through this node. *Q: who is a chokepoint / broker?* `centrality_betweenness()`.
- **Closeness centrality** — inverse of mean distance to all others. *Q: who can reach everyone fastest?* `centrality_closeness()`.
- **Eigenvector centrality** — recursive: connected to important nodes makes you important. *Q: who is in the well-connected core?* `centrality_eigen()`.
- **PageRank** — eigenvector variant with damping; handles directed graphs gracefully. *Q: who accumulates flow under random walks?* `centrality_pagerank()`.
- **Katz centrality** — eigenvector with attenuated long paths. Rare in this course.
- **Harmonic centrality** — closeness variant that handles disconnected graphs. `centrality_harmonic()`.
- **Hub & Authority (HITS)** — directed; hubs point to authorities. *Q: who curates vs. who is cited?* `centrality_hub()`, `centrality_authority()`.
- **Edge betweenness** — same idea, for edges. *Q: which edges are critical to cut?* `centrality_edge_betweenness()`.

**Pitfall:** "Most central" alone is meaningless. Always: *central by which measure, for which question?*

---

## 5. Community detection / clustering

"Do the nodes form groups?" — the algorithms disagree, often dramatically. Full treatment in `references/community.md`.

- **Modularity** — scalar measure of how much edges concentrate within groups vs. a random baseline. *Not* an algorithm; an objective some algorithms optimize.
- **Fast-greedy** — agglomerative modularity maximization. Fast, deterministic, can produce uneven sizes. `group_fast_greedy()`.
- **Louvain** — greedy modularity at multiple resolutions. Common default. `group_louvain()`.
- **Leiden** — improved Louvain; fixes badly-connected community problem.
- **Infomap** — minimizes description length of a random walk. Good for flow-like networks (transit, info diffusion). `group_infomap()`.
- **Walktrap** — short random walks tend to stay in communities. `group_walktrap()`.
- **Label propagation** — fast, stochastic, sometimes degenerate. `group_label_prop()`.
- **Spectral clustering** — eigenvectors of Laplacian; needs *k* specified.
- **Edge betweenness (Girvan–Newman)** — iteratively remove high-betweenness edges. Slow, historically important. `group_edge_betweenness()`.

**Pitfall:** clustering always returns *something*. Picking an algorithm without justification, or treating community labels as ground truth, is a category error.

---

## 6. Sampling networks

You rarely observe the whole network. *How* you sample biases *what* you see. Full treatment in `references/sampling.md`.

- **Census** — observe every node and edge. The Japanese committees dataset is a census.
- **Ego-centric sample** — sample nodes, then collect all their incident edges. **Two-stage.** Preserves local structure; over-represents high-degree neighbors. Donor 29C.
- **Edgewise / random edge sample** — sample edges directly. Biased *toward* high-degree nodes (more chances to be picked). Donor 29C.
- **Snowball sample** — start with seeds, follow their ties, then those nodes' ties, *k* waves. Good for hidden populations; size grows fast.
- **Random walk sample** — walk the graph and record nodes visited. Biased toward stationary distribution (≈ proportional to degree).
- **Induced subgraph** — sample a node set, keep only edges where *both* endpoints are sampled. Loses many edges.
- **Star sample** — one focal node + its neighbors only (no neighbor-of-neighbor ties).
- **Time-slice sample** — for temporal nets, sample by time window. Used in Hurricane Dorian analysis.

**Pitfall:** sampling strategy and inference strategy must match. Edgewise samples cannot give unbiased estimates of node-level properties without correction.

---

## 7. Network inference & resampling

How do you do statistics when observations aren't independent? Full treatment in `references/inference.md`.

### Permutation tests (the core network-aware inference tool)

- **Permutation test (generic)** — shuffle labels under the null and recompute the statistic many times; compare observed to null distribution.
- **Node permutation** — shuffle node attributes while holding graph structure fixed. Tests whether an attribute–attribute association exceeds chance given the topology. *This is the workhorse for SYSEN 5470 Skill 2.*
- **Edge permutation** — shuffle edges while preserving something (often the degree sequence; see configuration model).
- **QAP (Quadratic Assignment Procedure)** — permutation test for matrix-on-matrix correlation. Shuffles rows *and* columns of one matrix together.
- **MRQAP (Multiple Regression QAP)** — QAP for multiple-regression coefficients. Standard for dyadic regression with network autocorrelation.
- **Semi-partialling** — variant of MRQAP that residualizes predictors against each other before permuting; reduces inflation when predictors are correlated.

### Resampling (uncertainty quantification)

- **Jackknife (node-deletion)** — leave one node out at a time; *n* recomputations. Primary purpose: variance estimation (Quenouille/Tukey). Influence diagnostics are a side effect. Deterministic. Cost depends on the statistic — *n* full-graph betweenness recomputations is not cheap.
- **Edge jackknife** — leave-one-edge-out. Useful when edges are the sampling unit.
- **Bootstrap (naive node bootstrap)** — resample nodes with replacement. **Generally biased** for network statistics because resampled subgraph density ≠ original density.
- **Edge bootstrap** — resample edges with replacement; reconstruct node set from endpoints. Better for edge-level statistics.
- **Snowball bootstrap** — bootstrap that respects the snowball structure of the original sample.
- **Subsampling (m-out-of-n)** — sample *m* < *n* without replacement; rescale. Sometimes more defensible than bootstrap on networks.
- **Vertex bootstrap of Snijders & Borgatti** — block-bootstrap variant for networks; preserves more local structure.

**Pitfall:** "bootstrap a network" is ambiguous — always specify *what* is being resampled (nodes? edges? dyads? snowball waves?) and *why* that is the right unit.

### Models (mentioned in user memory; lower priority in v1 but vocabulary matters)

- **ERGM** — Exponential Random Graph Model. Logistic-regression-style model for whether an edge exists, conditional on graph statistics.
- **TERGM** — Temporal ERGM; ERGM for sequences of graphs over time.
- **SAOM / SIENA** — Stochastic Actor-Oriented Model; ties evolve through actor choices.
- **Latent space model** — embed nodes in low-dim space; edge probability decreases with distance.
- **SBM** — Stochastic Block Model; nodes belong to blocks, edge probability depends on block pair.

---

## 8. Null models

You can't say "more than expected" without specifying *expected under what.* Full treatment in `references/null_models.md`.

- **Erdős–Rényi G(n, p)** — every possible edge exists with probability *p*. Preserves *n* and expected edge count only.
- **Erdős–Rényi G(n, m)** — *n* nodes, exactly *m* edges placed uniformly at random.
- **Configuration model** — preserves the degree sequence exactly; edges otherwise random. **The standard null for "is this more than expected given the degree distribution?"**
- **Degree-preserving rewiring (Maslov–Sneppen)** — randomly swap edge endpoints while preserving each node's degree. Markov-chain way to sample from configuration model.
- **Bipartite configuration model** — preserves both row and column sums (degree on each side). Standard null for bipartite projections.
- **Stub-matching** — algorithmic recipe behind the configuration model; can produce self-loops and multi-edges unless explicitly avoided.
- **Stochastic Block Model (as null)** — preserves block structure as well as degrees.
- **Geographic / spatial null** — for spatial networks, edges constrained by distance (Bluebikes, Dorian).

**Pitfall:** Erdős–Rényi is rarely the right null — real networks have skewed degree distributions, and ER will declare almost anything "significant." Default to configuration model.

---

## 10. ML on networks

The course's GNN module. Full treatment in `references/ml_on_networks.md`.

### Embeddings (representation learning)

- **Node embedding** — a vector representation of each node such that structurally similar nodes have similar vectors. Output, not prediction.
- **DeepWalk** — generates random walks, treats them as sentences, runs Word2Vec.
- **Node2Vec** — DeepWalk + biased random walks (parameters *p* and *q* trade off BFS-like vs. DFS-like exploration).
- **LINE** — Large-scale Information Network Embedding; preserves 1st- and 2nd-order proximity.
- **Spectral embedding** — eigenvectors of Laplacian as coordinates.

### Graph Neural Networks

- **GNN** — umbrella term for neural networks operating on graph-structured data.
- **Message passing** — the core GNN operation: each node updates its representation by aggregating transformed messages from its neighbors. **The primary output of a GNN layer is an embedding; a prediction head on top is optional and swappable.** (Tim's noted conceptual insight.)
- **GCN (Graph Convolutional Network)** — Kipf & Welling; symmetric-normalized neighborhood averaging.
- **GraphSAGE** — sample neighbors, aggregate (mean/max/LSTM), useful for large/inductive settings.
- **GAT (Graph Attention Network)** — learnable attention weights over neighbors.
- **Temporal GNN** — GNN over a sequence of graph snapshots; e.g. EvolveGCN, TGN.

### Tasks

- **Node classification** — predict a label per node.
- **Link prediction** — predict whether an edge exists / will exist. Standard task for evaluating embeddings.
- **Graph classification** — one label per whole graph (e.g. is this molecule toxic?).
- **Node regression** — predict a continuous outcome per node. The course's GNN + XGBoost hybrid uses GNN embeddings as features for an XGBoost regressor.

**Pitfall:** GNN embeddings are not predictions. A GNN with no task head produces vectors; a GNN with a head produces predictions. Treating Node2Vec output as a "prediction" is a category error.

---

## 11. Bipartite networks

Donor 24C, 26C, 27C are bipartite-heavy. Full treatment in `references/bipartite.md`.

- **Two-mode network** — synonym for bipartite. Two node types; edges only between types.
- **One-mode projection** — collapse a bipartite graph to one node type, with edges between nodes that share at least one neighbor of the other type.
- **Coaffiliation** — the one-mode projection where edges represent shared affiliations (e.g., two members on the same committee). Donor course uses `coaffiliate()` helper.
- **Weighted projection** — edge weight = number (or function) of shared neighbors. Common variants: simple count, Jaccard, Newman's collaboration weight (1/(k−1) per shared affiliation), hyperbolic.
- **Bipartite degree** — careful: a node's degree is in the other mode. "Members per committee" is a degree distribution.
- **Bipartite density** — denominator is *n₁ × n₂*, not *n choose 2*.
- **Bipartite clustering** — standard clustering coefficient is zero by construction; use bipartite-specific definitions (Robins–Alexander, Opsahl).

**Pitfall:** running one-mode algorithms (clustering coefficient, triangle counts) directly on a bipartite graph is almost always wrong.

---

## 12. Flow and routing

The course's optimization module. Full treatment in `references/flow_routing.md`.

- **Shortest path** — minimum-weight path between two nodes. Dijkstra (non-negative weights), Bellman–Ford (allows negative), A* (with heuristic). `igraph::shortest_paths()`.
- **All-pairs shortest paths** — Floyd–Warshall; *O(n³)*. `igraph::distances()`.
- **Max-flow / min-cut** — maximum flow from source to sink equals capacity of minimum cut. *Engineer's use:* throughput of a supply network, bottleneck identification. `igraph::max_flow()`.
- **Min-cost flow** — max flow with per-edge cost minimized.
- **Minimum spanning tree (MST)** — connect all nodes with minimum total edge weight, no cycles. Kruskal, Prim. *Engineer's use:* infrastructure layout.
- **Traveling Salesman Problem (TSP)** — visit every node once, return to start, minimize cost. NP-hard.
- **Vehicle Routing Problem (VRP)** — TSP with multiple vehicles, capacity constraints, time windows. NP-hard.
- **Chinese Postman Problem** — traverse every *edge* at least once. Solvable in polynomial time.
- **Steiner tree** — minimum tree connecting a *subset* of nodes (may use intermediates). NP-hard.
- **Betweenness flow** — variant of betweenness using flow rather than shortest paths.

**Pitfall:** "shortest path" assumes a meaningful distance metric. On unweighted social networks, it's hop count and may not mean what the user wants.

---

## Final reminders

- **Always** name the question a metric answers, not just the metric.
- **Always** specify the unit being resampled (node? edge? dyad?).
- **Always** match the null model to the question.
- **Never** treat clustering output as ground truth.
- **Never** invent R function names — check the inline mappings or `references/`.
- **Before recommending a method**, consult `references/red_flags.md`.
