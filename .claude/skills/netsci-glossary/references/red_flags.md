# Red Flags — Common Network Science Terminology Mistakes

Check this file before defining a method, recommending an approach, or drafting a learning check. These are failure modes Claude is known to fall into.

## Conceptual conflations

**1. "Bootstrap a network."**
Meaningless without specifying the unit. Resampling nodes ≠ resampling edges ≠ resampling dyads. Each has different bias properties. Always force the question: *what is the sampling unit?*

**2. Centrality without a question.**
"This node has high centrality" is not a finding. The four common centralities answer four different questions:
- Degree → who is locally busy
- Betweenness → who is a chokepoint
- Closeness → who can reach everyone fastest
- Eigenvector/PageRank → who is in the well-connected core

Never recommend a centrality without naming the question.

**3. Modularity vs. clustering coefficient.**
- Modularity = how much edges concentrate within communities vs. a random baseline. A *partition-level* metric.
- Clustering coefficient = how often a node's neighbors are also connected to each other. A *node-level* (or graph-averaged) metric measuring local triangle density.

These are not synonyms. Claude conflates them often.

**4. Community detection vs. clique-finding.**
- Community detection = partition the graph by some objective (modularity, description length, etc.). Always returns a partition, even on random graphs.
- Clique = a *fully connected* subgraph. A structural definition with no algorithm choice.

A community is not a clique.

**5. QAP vs. permutation test (general).**
QAP is a *specific* permutation test for matrix-on-matrix correlation that shuffles rows and columns of one matrix *together*. A node-attribute permutation test is *not* QAP. Don't use the terms interchangeably.

**6. MRQAP vs. ordinary regression with bootstrap SEs.**
MRQAP corrects standard errors for network autocorrelation via permutation. Bootstrapping residuals does not address network autocorrelation. Different problems.

**7. Erdős–Rényi as default null.**
Almost always wrong. Real networks have skewed degree distributions; ER nulls declare everything significant. Default to configuration model unless there's a specific reason ER is the right comparison.

**8. "Random graph."**
Ambiguous. G(n,p)? G(n,m)? Configuration model? Rewired version of the observed graph? Always specify.

**9. Bipartite confusion.**
Running one-mode clustering coefficient, triangle counts, or transitivity on a bipartite graph yields zero or near-zero *by construction*, not as a finding. Use bipartite-specific definitions or project to one mode first (with care).

**10. GNN output ≠ prediction.**
A GNN layer produces node embeddings. A *task head* on top of the embeddings produces predictions. Node2Vec, GraphSAGE without a head, and untrained GNNs produce vectors, not predictions. Treating embeddings as predictions is a category error.

**11. Node2Vec is not a GNN.**
Node2Vec is a shallow embedding method (random walks + Word2Vec). It has no message passing, no convolution, no learned aggregation. GCN/GAT/GraphSAGE are GNNs; Node2Vec is not. Both produce embeddings.

**12. Link prediction vs. edge classification.**
- Link prediction = predict whether an edge will / does exist between two nodes (binary, often imbalanced).
- Edge classification = predict the *type* or *attribute* of a known edge.

Different tasks, different evaluation.

**13. "Significant" without a null.**
A *p*-value from a permutation test is meaningful only against a specified null. "Centrality is significantly high" requires "compared to a [configuration model / ER / degree-preserving rewiring] null." Always name the null.

**14. Jackknife vs. bootstrap.**
- Jackknife: leave-one-out, deterministic, *n* recomputations. Primary purpose: variance estimation (Quenouille/Tukey). Influence diagnostics are a side effect.
- Bootstrap: resample with replacement, stochastic, typically *B* = 1000+ recomputations. Primary purpose: approximate the sampling distribution of θ̂.

Both target the sampling distribution of θ̂; they're alternatives, not for different jobs. Jackknife is older, deterministic, and fails on non-smooth statistics (e.g., median). Bootstrap is more flexible but stochastic and on networks needs care about *what* is being resampled.

**15. Sampling vs. resampling.**
- Sampling = how you got the data in the first place (ego-centric, edgewise, snowball).
- Resampling = how you assess uncertainty from the data you have (bootstrap, jackknife, permutation).

The two can be confused, especially when someone says "I sampled my data."

## Vocabulary precision

**"Network" vs. "graph"**
Practically interchangeable in this course. Mathematicians prefer "graph"; applied folks prefer "network." No correction needed either way.

**"Tie" vs. "edge" vs. "link"**
All synonyms. "Tie" is sociology-flavored; "edge" is graph-theory-flavored; "link" is web/network-engineering-flavored. Use whichever matches the user's register.

**"Node" vs. "vertex" vs. "actor"**
Synonyms. "Actor" implies social context.

**"Path" vs. "walk" vs. "trail"**
Not synonyms:
- Walk: any sequence of edges (repeats allowed)
- Trail: walk with no repeated edge (nodes may repeat)
- Path: walk with no repeated node (and therefore no repeated edge)

**"Distance" vs. "path length"**
Distance = length of the *shortest* path (a geodesic). Path length = length of *some* path. Don't conflate.

**"Density" vs. "degree"**
- Density = graph-level (fraction of possible edges present)
- Degree = node-level (count of incident edges)

**"Hub" (HITS) vs. "hub" (colloquial)**
- HITS hub: a directed node that points to many authorities.
- Colloquial hub: just a high-degree node.

If a user says "hub," check which they mean.

## R-ecosystem hazards

**Function name hallucinations to avoid.**
- It's `centrality_degree()`, not `degree_centrality()` (in tidygraph).
- It's `group_fast_greedy()`, not `cluster_fast_greedy()` (that's the igraph form; tidygraph uses `group_*`).
- It's `node_is_isolated()`, not `is_isolated_node()`.
- `.E()` and `.N()` accessors retrieve edge and node tables inside `mutate()` calls on a tbl_graph. Used heavily in donor scripts.

**`igraph` vs. `tidygraph` namespace.**
- `igraph::degree()` returns a vector
- `tidygraph::centrality_degree()` is a node-table verb usable inside `mutate()`

Don't mix them in code recommendations unless explicitly bridging the two.

**`ggraph` vs. `ggplot2`.**
- `ggraph()` is the network analog of `ggplot()` — takes a tbl_graph and uses `geom_node_*` / `geom_edge_*`.
- You cannot plot a tbl_graph with plain `ggplot()` without first extracting tables.

## Pedagogical red flags (specific to SYSEN 5470)

**Don't pitch the most sophisticated method.**
Tim prefers the simpler, defensible option. If a problem can be done with a permutation test, don't pitch ERGM. If a problem can be done with degree centrality, don't pitch eigenvector centrality.

**Don't recommend GNN as the default ML approach.**
GNNs are the *last* method in the ML arc (heuristic → embedding → GNN → temporal GNN). For most lab-scale problems, Node2Vec + XGBoost is more honest.

**Don't write R Markdown or code unprompted.**
The user wants concepts nailed down before implementation. Hold the code unless asked.

**Don't recommend ER as the comparison null.**
See #7 above. Configuration model or rewiring is almost always the right default in this course.

**Don't claim a metric is "the standard" without checking.**
Network science has many local conventions. "Standard" varies by subfield. Phrase as "common choice" or "frequent default."
