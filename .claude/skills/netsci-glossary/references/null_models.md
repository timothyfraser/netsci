# Null Models — Full Reference

"More than expected" requires specifying *expected under what*. The null model is the comparison baseline.

## Erdős–Rényi G(n, p)
- **Definition:** every possible edge exists independently with probability *p*.
- **Preserves:** *n*, expected edge count = p·n(n−1)/2.
- **R:** `igraph::sample_gnp(n, p)`.
- **Use sparingly.** Real networks have skewed degree distributions; ER nulls declare almost everything significant.

## Erdős–Rényi G(n, m)
- **Definition:** *n* nodes, exactly *m* edges placed uniformly at random.
- **Preserves:** *n*, exact edge count.
- **R:** `igraph::sample_gnm(n, m)`.
- **Use case:** comparing structure when total edge count is the only thing you want to hold fixed.

## Configuration model
- **Definition:** preserves the degree sequence exactly; edges otherwise random.
- **Mechanism:** stub-matching — give each node *k_i* "half-edges," pair them up uniformly at random.
- **Side effects:** can produce self-loops and multi-edges; in practice these are removed or rejected.
- **R:** `igraph::sample_degseq(out.deg, in.deg, method = "vl")` for simple graphs.
- **Use case:** **the standard null for "more than expected given the degree distribution."** Default in this course.

## Degree-preserving rewiring (Maslov–Sneppen)
- **Definition:** randomly pick two edges (a→b) and (c→d); rewire to (a→d) and (c→b). Preserves every node's degree.
- **Why it matters:** Markov-chain way to sample from the configuration model when stub-matching is awkward (e.g., directed networks, bipartite networks).
- **R:** `igraph::rewire(g, with = keeping_degseq(niter = ...))`.

## Bipartite configuration model
- **Definition:** preserves both row degrees (mode-1 node degrees) and column degrees (mode-2 node degrees).
- **Why it matters:** for bipartite projections, ER and one-mode configuration models are both wrong. Need to preserve both marginals.
- **R:** `igraph::sample_bipartite()` for ER bipartite; rewiring for configuration version.

## Stochastic Block Model (as null)
- **Definition:** preserves block (community) structure as well as within/between block edge probabilities.
- **Use case:** "more than expected given the community structure."
- **Degree-corrected SBM:** preserves both block structure and degree heterogeneity.

## Spatial / geographic null
- **Definition:** edge probability constrained by spatial distance between nodes.
- **Why it matters:** in spatial networks (Bluebikes, Hurricane Dorian), most ties are short-range by geography alone. Without controlling for this, any spatial pattern looks "significant."
- **Variants:** gravity model (P(edge) ∝ pop_i · pop_j / d^α), radiation model.

## Choosing a null

| Question | Null |
|---|---|
| Is there *any* structure? | ER G(n,m) — but rarely useful |
| Given the degree distribution, is there more clustering than expected? | Configuration model |
| Given degree + community structure, is there more X than expected? | Degree-corrected SBM |
| In a bipartite graph, is this projection's structure > chance? | Bipartite configuration model |
| In a spatial network, is this non-spatial pattern > chance? | Spatial null (gravity, distance-binned) |

## Common pitfalls

- **ER as default.** Almost always wrong. Default to configuration model unless ER is specifically motivated.
- **Comparing a real network to "a random network" without saying which random.** "Random" is not a model.
- **Forgetting to remove self-loops / multi-edges** after stub-matching when the original was a simple graph.
- **Using one-mode configuration model on bipartite data** — preserves the wrong margins.
- **Sampling once from the null** and comparing — need a distribution, typically *B* ≥ 1000 draws.

## Practical workflow

1. State the question precisely. ("Is observed triangle count > what degree distribution alone would produce?")
2. Pick the null that holds fixed exactly what you're not trying to test.
3. Sample *B* networks from the null (B ≥ 1000 typical).
4. Compute the statistic on each.
5. Compare observed to null distribution. Report p-value or how many SDs out.

## How this connects to the course

- **Skill 2 (network-aware inference):** the null model is half the story; the permutation procedure (in `inference.md`) is the other.
- **Skill 3 (counterfactual disruption):** can also be framed as a null — "what does the network look like if random nodes/edges are removed?" — though here the "null" is the disrupted state, not the unperturbed observation.
