# Centrality — Full Reference

Each centrality answers a different question. Always pair the measure with the question.

## Degree centrality
- **Definition:** number of edges incident to a node. Directed: in-degree, out-degree, total.
- **Weighted variant ("strength"):** sum of incident edge weights.
- **Question answered:** Who is locally busy / well-connected?
- **R:** `centrality_degree(mode = "all" | "in" | "out", weights = .E()$weight, loops = FALSE)`
- **Engineer's use:** Bluebikes — which stations have the most trips? Supply chain — which suppliers serve the most customers?
- **Edge cases:** Sensitive to self-loops (control with `loops` argument). On bipartite graphs, degree is measured against the *other* mode.
- **Floor:** count neighbors. **Ceiling:** weighted vs. unweighted; in vs. out; normalization by *n*−1.

## Betweenness centrality
- **Definition:** Σ over node pairs (s,t) of (σ_st(v) / σ_st), where σ_st is the number of shortest paths and σ_st(v) is the number passing through v.
- **Question answered:** Who is a chokepoint / broker for shortest-path traffic?
- **R:** `centrality_betweenness(directed = TRUE/FALSE, weights = .E()$weight, normalized = FALSE)`
- **Engineer's use:** Hurricane Dorian — which counties relay evacuation flows? Power grid — which substations are cut-vertex-adjacent?
- **Edge cases:** Computationally expensive on large graphs (O(nm) for unweighted, worse for weighted). Brandes' algorithm is the standard. Approximate via random pivots for large graphs.
- **Floor:** "on many shortest paths." **Ceiling:** the σ_st(v)/σ_st ratio; group betweenness; flow betweenness as alternative.

## Closeness centrality
- **Definition:** (n−1) / Σ d(v, u) over all other nodes u.
- **Question answered:** Who can reach all others quickly on average?
- **R:** `centrality_closeness(mode = "all", weights = .E()$weight, normalized = TRUE)`
- **Engineer's use:** Logistics hub siting — which warehouse minimizes mean distance to all customers?
- **Edge cases:** Undefined on disconnected graphs (infinite distances). Use harmonic centrality instead.

## Harmonic centrality
- **Definition:** Σ 1/d(v, u) over u ≠ v (with 1/∞ = 0).
- **Question answered:** Closeness, but handles disconnected components gracefully.
- **R:** `centrality_harmonic()`
- **Engineer's use:** Sparse / fragmented networks where standard closeness blows up.

## Eigenvector centrality
- **Definition:** v's score is proportional to the sum of its neighbors' scores. Leading eigenvector of the adjacency matrix.
- **Question answered:** Who is connected to other well-connected nodes?
- **R:** `centrality_eigen(weights = .E()$weight, directed = FALSE)`
- **Engineer's use:** Identifying tightly coupled core of a supply network. Reputation systems.
- **Edge cases:** Poorly defined on directed acyclic graphs and disconnected graphs. Use PageRank or Katz instead.

## PageRank
- **Definition:** Stationary distribution of a random walker that, with probability (1−d), restarts at a random node. Damping factor d typically 0.85.
- **Question answered:** Where does random-walk flow accumulate?
- **R:** `centrality_pagerank(damping = 0.85, weights = .E()$weight, directed = TRUE)`
- **Engineer's use:** Webgraph importance; transit flow accumulation; influence in directed citation/communication networks.
- **Edge cases:** Sensitive to damping factor; sink nodes (no out-edges) handled by teleportation.

## Katz centrality
- **Definition:** Eigenvector centrality + attenuation factor α applied to walks of length k. Sum_{k=1}^∞ α^k A^k 1.
- **Question answered:** Importance via all paths, with longer paths discounted.
- **R:** Less common in tidygraph; use `igraph::alpha_centrality()`.
- **Edge cases:** Requires α < 1/(largest eigenvalue) for convergence. Largely superseded by PageRank in practice.

## Hub & Authority (HITS)
- **Definition:** Hubs point to authorities; authorities are pointed to by hubs. Coupled eigenvector computation.
- **Question answered:** In a directed graph, who curates (hub) vs. who is the destination (authority)?
- **R:** `centrality_hub()`, `centrality_authority()`
- **Engineer's use:** Citation networks; web link graphs; broker vs. expert in advice networks.

## Edge betweenness
- **Definition:** Same as node betweenness, but the fraction of shortest paths through an *edge*.
- **Question answered:** Which edges are critical to remove for fragmentation?
- **R:** `centrality_edge_betweenness()`
- **Engineer's use:** Counterfactual disruption — which edge removal does the most damage? Direct link to course Skill 3.

## Less common but worth knowing

- **Subgraph centrality:** weighted sum of closed walks of all lengths, exponentially damped.
- **Information centrality:** based on all paths weighted by inverse length.
- **Percolation centrality:** time-varying betweenness during a percolation/contagion process.
- **Random walk betweenness:** like betweenness, but flow follows random walks, not shortest paths.

## How to choose

| Question | Measure |
|---|---|
| Who is locally busy? | Degree |
| Who handles the most flow? | Weighted degree |
| Who is a chokepoint for traffic? | Betweenness |
| Whose removal most fragments the network? | Edge betweenness, betweenness |
| Who can reach everyone fastest? | Closeness (harmonic if disconnected) |
| Who is in the well-connected core? | Eigenvector |
| Where does random-walk flow concentrate? | PageRank |
| Hubs vs. authorities (directed)? | HITS |
