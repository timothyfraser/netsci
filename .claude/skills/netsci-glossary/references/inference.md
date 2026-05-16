# Inference & Resampling — Full Reference

Statistical inference on networks is hard because observations aren't independent. Edges share nodes; nodes share neighborhoods. Standard SE formulas are wrong by default.

## The core idea

Network-aware inference asks: *Given the structure of the network, would this pattern arise by chance?* The "chance" is defined by a null hypothesis enforced through resampling or permutation.

This is **Skill 2** in the course: network-aware inference vs. naive correlation.

## Permutation tests

### Generic permutation test
- **Procedure:** under the null, shuffle some label or structure. Recompute the statistic. Repeat *B* times (typically 1000–10000). The p-value is the fraction of null statistics at least as extreme as observed.
- **Key choice:** what gets shuffled defines the null.

### Node attribute permutation
- **Procedure:** keep graph structure fixed; shuffle a node attribute (e.g., gender, geography) across nodes.
- **Null tested:** the attribute is unrelated to graph position.
- **Engineer's use:** does information flow more between same-region suppliers than chance, given the existing trade network?
- **Donor 29C** and Skill 2 use variants of this.

### Edge permutation
- **Procedure:** shuffle edges while preserving some property (often degree sequence). See configuration model in `null_models.md`.
- **Null tested:** the structural pattern (e.g., triangle count) exceeds what the degree sequence alone would produce.

### QAP — Quadratic Assignment Procedure
- **Procedure:** for matrix-on-matrix correlation. Shuffle rows *and* columns of one matrix together (preserves matrix structure). Compute correlation with the other matrix. Repeat.
- **Null tested:** the row/column labels of one matrix are unrelated to the other.
- **Engineer's use:** does trade volume correlate with shared language, given network autocorrelation?
- **R:** `sna::qaptest()`, `asnipe::mrqap.dsp()`.

### MRQAP — Multiple Regression QAP
- **Procedure:** linear regression with dyadic predictors; standard errors obtained via QAP-style permutation.
- **Variants:**
  - **Y-permutation:** shuffle the outcome matrix; biased when predictors are correlated.
  - **Double semi-partialling (DSP) / Dekker semi-partialling:** residualize each predictor against the others, permute residuals. Reduces inflation. Tim has noted experience with this.
- **Engineer's use:** modeling dyadic outcomes (trade volume, communication frequency) with multiple correlated network covariates.

## Resampling for uncertainty

### Jackknife
- **Primary purpose:** variance estimation (Quenouille/Tukey; predecessor to the bootstrap). Per-node influence diagnostics fall out as a side effect.
- **Node jackknife:** leave one node out at a time, recompute statistic θ̂_(i). *n* recomputations total.
- **Jackknife SE:** SE_jack = √[(n−1)/n · Σ_i (θ̂_(i) − θ̂_(·))²], where θ̂_(·) is the mean of the leave-one-out estimates.
- **Edge jackknife:** leave one edge out at a time.
- **Strengths:** deterministic; fixed at *n* recomputations (vs. bootstrap's *B*, often *B* > *n*); the leave-one-out estimates also reveal which nodes/edges drive the result.
- **Weaknesses:** assumes a smooth functional. Famously fails for the median and other non-smooth statistics; delete-*d* jackknife is the standard fix. On large graphs, "*n* recomputations" may not be cheap — full-graph betweenness recomputed *n* times is expensive.
- **Use when:** you want a deterministic variance estimate, or want to identify influential observations.

### Bootstrap variants

Bootstrap on networks is hazardous because resampled networks usually have *different density* than the original. Always specify what is resampled and why.

- **Naive node bootstrap:** sample *n* nodes with replacement; induced subgraph as bootstrap sample. Density typically too low (many sampled pairs were not connected in the original). Biased.
- **Edge bootstrap:** sample *m* edges with replacement. Better for edge-level statistics; node set may shrink.
- **Snowball bootstrap:** respects the wave structure of the original snowball sample. Bhattacharyya & Bickel; Thompson.
- **Vertex / patchwork bootstrap (Snijders–Borgatti):** block-bootstrap idea — resample local neighborhoods, stitch together. Preserves more local structure.
- **Subsampling (m-out-of-n):** sample *m* < *n* nodes without replacement, recompute, rescale. More defensible asymptotically for network statistics than naive bootstrap.

### Permutation vs. bootstrap vs. jackknife — what each distribution represents

The cleanest distinction is *what the resampling distribution approximates*, not what you do with it. There is overlap (you can invert a permutation test to get a CI; you can use the bootstrap for testing) but the canonical pairing is:

| Procedure | Resampling distribution approximates | Canonical use |
|---|---|---|
| Permutation | Distribution of statistic under H₀ | p-value against a specific null |
| Bootstrap | Sampling distribution of θ̂ | CI, SE |
| Jackknife | Sampling distribution of θ̂ (smooth case) | SE, influence diagnostics |

Typical pairings in this course:
- Test "is this network pattern more than chance given degrees?" → permutation against configuration model.
- Need SE on a centrality measure → jackknife (deterministic) or subsampling (asymptotically safer than naive bootstrap on networks).
- Need CI on a dyadic regression coefficient → MRQAP with DSP (permutation), since the bootstrap on dyads is fraught.

## Models (lower priority in v1; vocabulary reference)

### ERGM — Exponential Random Graph Model
- Models the probability of observing the entire graph as exp(Σ θ_i s_i(g)) / κ, where s_i are network statistics (edge count, triangle count, degree distribution moments) and θ_i are estimated coefficients.
- Interpretation: log-odds of an edge given the rest of the graph.
- R: `statnet`/`ergm`.

### TERGM — Temporal ERGM
- ERGM for sequences of graphs over time; current graph depends on previous.
- R: `tergm`.

### SAOM — Stochastic Actor-Oriented Model (SIENA)
- Ties evolve through actor-level utility maximization. Continuous-time Markov process.
- R: `RSiena`.

### Latent space model
- Each node has coordinates in a low-dimensional space; edge probability decreases with distance.
- R: `latentnet`.

### Stochastic Block Model (SBM)
- Generative model: nodes assigned to blocks; edge probability depends on block pair. Degree-corrected variant handles heterogeneous degrees.

## When to reach for what

| Question | Tool |
|---|---|
| Is this dyadic correlation > chance? | QAP |
| Does this regression coefficient survive network autocorrelation? | MRQAP (DSP) |
| Is this node-attribute pattern > chance given topology? | Node permutation |
| Is this triangle count > chance given degrees? | Configuration-model permutation |
| What is the SE of my centrality estimate? | Jackknife (deterministic; cost = *n* recomputations) or subsampling |
| Which nodes drive this estimate? | Jackknife |
| Probabilistic model of edge formation | ERGM |
| Edge dynamics over time | TERGM or SAOM |

## Common mistakes

- Reporting "p < 0.05" without specifying what was permuted.
- Using OLS standard errors on dyadic regressions (network autocorrelation violates iid).
- Bootstrapping nodes naively and reporting the result as "the SE" — naive node bootstrap on networks is biased; use subsampling or jackknife.
- Using ER as the null when the question is "more than expected given degree distribution" — use configuration model.
- Confusing jackknife (deterministic) with bootstrap (stochastic).
- Treating QAP and ERGM as substitutes — different goals (correlation vs. generative model).
