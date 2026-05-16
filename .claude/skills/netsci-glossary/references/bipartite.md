# Bipartite Networks — Full Reference

Donor 24C, 26C, 27C are bipartite-heavy. Two-mode logic is *not* a special case of one-mode logic — many one-mode metrics are wrong by construction.

## Definitions

- **Bipartite / two-mode network:** nodes partitioned into two disjoint sets V₁ and V₂; edges only run between sets.
- **Mode-1 / mode-2:** the two node types (members & committees; users & products; firms & locations).
- **Biadjacency matrix B:** |V₁| × |V₂| matrix; B_ij = 1 if node i in mode 1 connects to node j in mode 2.
- **In `tidygraph`:** the graph reports itself as bipartite when a `type` attribute (logical or 0/1) is present on nodes. Donor 24C line 161.

## Projection

Collapse a bipartite graph to a one-mode graph on V₁ (or V₂), connecting two mode-1 nodes if they share at least one mode-2 neighbor.

- **One-mode projection** — the collapsed graph.
- **Coaffiliation** — synonym in social-science usage; the projection where edges represent shared affiliation. Donor 24C uses `coaffiliate()`.

### Weighted projection variants

| Weight scheme | Definition | Use case |
|---|---|---|
| **Simple count** | w_ij = number of shared mode-2 neighbors | Default; intuitive |
| **Jaccard** | |N(i) ∩ N(j)| / |N(i) ∪ N(j)| | Normalizes by union size |
| **Newman collaboration** | Σ_k (1/(d_k − 1)) over shared k | Discounts shared neighbors with many connections |
| **Hyperbolic** | Σ_k (1/(d_k − 1)) | Newman's original variant |
| **Cosine** | (B·B^T)_ij / (|i|·|j|) | Common in info retrieval |

Donor course's `coaffiliate()` function accepts a `weight` argument; default is simple count.

## What changes under bipartite-ness

### Degree
- A node's degree counts neighbors in the *other* mode.
- "Members per committee" = degree distribution of committee nodes.
- "Committees per member" = degree distribution of member nodes.
- These are **two different distributions**, both legitimate.

### Density
- Denominator is |V₁| × |V₂|, **not** n(n−1)/2.
- Using one-mode density on bipartite gives systematically wrong (lower) values.

### Clustering coefficient
- Standard one-mode definition counts closed triangles. **A bipartite graph has zero triangles by construction.**
- Bipartite-specific definitions exist:
  - **Robins–Alexander clustering:** based on 4-cycles (the bipartite analog of triangles).
  - **Opsahl clustering:** ratio of 4-paths that close into 6-cycles.
- `tnet` package implements these.

### Centrality
- All centrality measures work, but interpretation differs by mode.
- Betweenness on a member node measures brokerage *between committees via that member*.
- Don't mix interpretations across modes without flagging.

### Community detection
- One-mode algorithms applied directly to a bipartite graph often produce a partition that simply separates the two modes. Useless.
- Use bipartite-specific algorithms (BRIM, bipartite SBM) or run community detection on a projected one-mode graph (and be honest about the projection's biases).

## Projection biases

Projection is lossy. A few systematic distortions:

- **Large mode-2 nodes inflate density.** A committee with 50 members creates 50·49/2 = 1225 edges in the projection. Big nodes dominate.
- **Triangles in projection are guaranteed** wherever a mode-2 node has ≥3 mode-1 neighbors — they don't indicate clustering, just shared affiliation.
- **Degree in projection ∝ Σ over neighbors of (degree in other mode − 1).** High-degree mode-1 nodes (members on many committees) are *very* central in the projection by construction.

These biases motivate the bipartite configuration model (preserves both row and column sums) as the right null for projected structure.

## When to project vs. when not to

**Project when:**
- The downstream method only handles one-mode networks (most clustering, centrality, GNNs without bipartite-awareness).
- The substantive question is genuinely about mode-1 entities related through mode-2 ("members connected by shared committees").

**Don't project when:**
- You care about mode-2 entities themselves.
- The bipartite structure is the substance (recommender systems, allocation problems).
- You can use a bipartite-aware method directly.

## Common mistakes

- Reporting one-mode density / clustering on a bipartite graph.
- Projecting and running community detection without comparing to a bipartite null.
- Forgetting that "high centrality" in the projection often reflects high mode-2 degree, not anything sociologically meaningful.
- Treating the bipartite graph as directed because affiliations "go from" members "to" committees. Affiliations are undirected; the bipartite structure already captures the relevant asymmetry.

## R workflow (for reference)

- Build: `tbl_graph(nodes, edges)` where nodes have a `type` column.
- Check: `igraph::is_bipartite(g)`.
- Project: course uses custom `coaffiliate()` (donor 24C/26C); igraph offers `bipartite_projection()`.
- Bipartite null: `igraph::sample_bipartite()` for ER; degree-preserving rewiring for configuration version.
