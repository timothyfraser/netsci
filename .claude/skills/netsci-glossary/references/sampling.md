# Sampling Networks — Full Reference

You rarely observe the whole network. The sampling strategy determines what biases you inherit.

## Census
- Observe all nodes and all edges. The Japanese Disaster Recovery Committees dataset is effectively a census of the bounded population.
- "No sampling" still requires defending the *boundary* — who counts as in scope?

## Ego-centric sample
- **Procedure:** (1) sample a set of nodes (egos) by some scheme; (2) collect all edges incident to the egos (and often their alters' identities).
- **Two-stage.** Donor 29C uses this on Hurricane Dorian.
- **Strengths:** preserves local structure around egos; you actually know each ego's full neighborhood.
- **Biases:** over-represents edges incident to high-degree nodes (more chances to appear as someone's alter). Alter–alter ties may be undersampled unless explicitly collected.
- **Use case:** mobility flows where origin counties are the egos.

## Edgewise / random edge sample
- **Procedure:** sample edges directly from the edgelist; nodes are whichever endpoints appear.
- **Biases:** high-degree nodes appear more often (many edges to be sampled). Average degree of sampled nodes > population average. Donor 29C contrasts this with ego-centric sampling on the same Dorian data.
- **Use case:** when edges, not nodes, are the natural sampling unit (e.g., logged transactions).

## Snowball sample
- **Procedure:** start with seed nodes (wave 0). Wave 1 = their neighbors. Wave 2 = wave-1 neighbors' neighbors. Continue for *k* waves.
- **Strengths:** good for hidden populations (criminal networks, undocumented workers) where there is no sampling frame.
- **Biases:** strongly favors high-degree nodes and nodes in the seed's component. Sample size grows roughly as average-degree^k.
- **Variants:** respondent-driven sampling (RDS) — snowball with weighting to correct biases.

## Random walk sample
- **Procedure:** start at a node, move to a random neighbor (possibly weighted), record visited nodes.
- **Bias:** sampling probability proportional to degree in the long run (stationary distribution).
- **Strengths:** scalable to massive graphs (Twitter-style); only needs local access.
- **Variants:** Metropolis–Hastings random walk for uniform sampling; PageRank-style with restart.

## Induced subgraph sample
- **Procedure:** sample a node set S. Keep only edges where *both* endpoints are in S.
- **Bias:** drops many edges; preserves degree distribution badly (sampled degree ≪ true degree).
- **Use case:** when you can only observe relations among a known group.

## Star sample
- **Procedure:** one focal node + its neighbors. No neighbor–neighbor edges collected.
- **Limited.** A degenerate ego sample. Good for degree distribution estimation only.

## Time-slice sample
- **Procedure:** for temporal networks, sample by time window.
- **Donor 29C** examines a few time slices of Hurricane Dorian.
- **Bias:** depends on time-window length and event timing.

## Comparing strategies

| Strategy | Preserves degree dist? | Preserves clustering? | Use when |
|---|---|---|---|
| Census | Yes | Yes | You can afford it |
| Ego-centric | Locally yes | Yes (around egos) | Local structure matters |
| Edgewise | No (biased high) | No | Edges are the natural unit |
| Snowball | No (biased high) | Yes (within waves) | No frame; hidden population |
| Random walk | No (biased ∝ degree) | Partial | Massive graphs; local access |
| Induced subgraph | No (biased low) | No | Bounded group |

## Sampling vs. resampling

These are different:
- **Sampling:** how you got your data. Once, from a population.
- **Resampling:** how you assess uncertainty from your data. Repeated, from your sample.

Conflating them is a common error. See `references/inference.md` for resampling.

## Common pitfalls

- Reporting "average degree" from an edgewise sample as if it were the population mean.
- Using bootstrap on a snowball sample without respecting the snowball structure.
- Comparing two networks sampled by *different* strategies without correction.
- Forgetting that sampled networks rarely capture true diameter or true components.
