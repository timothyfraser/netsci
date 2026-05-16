# Community Detection — Full Reference

"Do nodes form groups?" — but every algorithm returns *something*, even on random graphs. Picking and justifying matters more than picking.

## Modularity (Q)

Not an algorithm. An objective.

- **Definition:** Q = (1/2m) Σ_{ij} [A_ij − k_i k_j / 2m] δ(c_i, c_j)
- **Interpretation:** fraction of edges within communities, minus what you'd expect under a configuration-model null with the same degree sequence.
- **Range:** roughly −0.5 to 1. Empirical "good" partitions often Q ≈ 0.3–0.7.
- **Resolution limit:** modularity cannot detect communities smaller than √(2m). Real, well-defined small communities can be missed.
- **R:** `modularity()` in igraph; many `group_*` functions optimize Q.

## Algorithms

### Fast-greedy (Clauset–Newman–Moore)
- **How:** agglomerative merging of node pairs that maximally increase Q.
- **Speed:** fast, O((m+n)n log n) typical.
- **Strengths:** deterministic, scalable.
- **Weaknesses:** can produce highly unequal community sizes; greedy local optima.
- **R:** `group_fast_greedy(weights = .E()$weight, n_groups = NULL)`. `n_groups` cuts the dendrogram.
- **Used in donor 26C.**

### Louvain (Blondel et al.)
- **How:** two-phase greedy modularity — local move + community aggregation, iterated.
- **Speed:** very fast, near-linear.
- **Strengths:** widely used default; multi-resolution.
- **Weaknesses:** can produce badly-connected communities (a "community" may be internally disconnected).
- **R:** `group_louvain(weights = .E()$weight)`.

### Leiden (Traag et al.)
- **How:** Louvain + refinement step + guarantees on connectivity.
- **Strengths:** fixes Louvain's disconnected-community problem; faster in practice.
- **R:** `group_leiden(resolution_parameter = 1, objective_function = "modularity")`.
- **Recommendation:** prefer over Louvain when available.

### Infomap (Rosvall–Bergstrom)
- **How:** minimizes the description length of random walks on the graph (map equation).
- **Best for:** flow-like networks where community = "where a random walker lingers." Transit, information diffusion, evacuation flows.
- **Strengths:** principled, handles directed and weighted graphs natively.
- **R:** `group_infomap()`. Used in donor 26C.

### Walktrap (Pons–Latapy)
- **How:** short random walks tend to stay within communities; cluster nodes by walk-derived distance.
- **Speed:** moderate.
- **R:** `group_walktrap(weights = .E()$weight, steps = 4)`.

### Label propagation (Raghavan et al.)
- **How:** each node adopts the most frequent label among its neighbors, iteratively.
- **Speed:** near-linear, very fast.
- **Weaknesses:** stochastic; can produce degenerate partitions (one giant community).
- **R:** `group_label_prop()`.

### Spectral clustering
- **How:** k-means on the leading eigenvectors of the (normalized) Laplacian.
- **Strengths:** theoretical grounding.
- **Weaknesses:** requires k specified in advance; expensive for large graphs.
- **R:** not directly in tidygraph; use `igraph::cluster_spinglass()` or external (`kernlab::specc`).

### Girvan–Newman (edge betweenness)
- **How:** iteratively remove edge with highest betweenness; communities emerge from the splits.
- **Speed:** slow, O(m²n).
- **Why it's still taught:** clean conceptual link between centrality and community.
- **R:** `group_edge_betweenness()`.

### Stochastic Block Model (SBM)
- **How:** generative model — nodes assigned to blocks, edge probability depends on block pair.
- **Strengths:** principled inference; degree-corrected variant handles heterogeneous degrees.
- **Weaknesses:** requires choosing number of blocks (or use nonparametric variants).
- **R:** packages `blockmodels`, `sbm`, `latentnet` for various flavors.

## How to choose

| Situation | Try |
|---|---|
| First-pass, want something reasonable | Leiden (or Louvain) |
| Flow-like network (transit, info) | Infomap |
| Need deterministic + fast | Fast-greedy |
| Need principled model + uncertainty | SBM |
| Want to teach the centrality–community link | Girvan–Newman |
| Bipartite | Bipartite-specific algorithms (BRIM, bipartite SBM) — not the one-mode ones |

## Validation

A clustering algorithm without justification is not useful (donor 26C, line 259). Ways to defend a partition:

- **Stability under resampling:** rerun on bootstrapped/jackknifed versions; how often do the same nodes co-cluster?
- **Stability across algorithms:** do multiple algorithms produce similar partitions? Use Adjusted Rand Index (ARI), Normalized Mutual Information (NMI).
- **External validation:** does the partition correlate with known attributes (geography, function)?
- **Modularity comparison to null:** is Q higher than Q on configuration-model nulls?

## Common mistakes

- Treating community labels as ground-truth groups.
- Reporting modularity without comparison to a null.
- Using one-mode algorithms on bipartite graphs.
- Picking an algorithm by which produced the prettiest plot.
- Ignoring resolution limit — claiming "no small communities exist" when modularity cannot detect them.
