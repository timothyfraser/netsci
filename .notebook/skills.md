# SYSEN 5470 — Student Skills & Commands

> The Study Companion understands a set of **slash commands**. Type one at the
> start of a message (e.g. `/glossary`, `/quizme`) to switch study modes. Every
> command is built to help you *think*, not to do your work. The persona below
> defines them; paste it into NotebookLM's Configure Chat once to turn them on.

## Available commands

| Command | Skill | What it does |
|---|---|---|
| `/study` | study_companion_persona | General study mode + the persona to paste into Configure Chat. Tell it what you're working on and it coaches you (and lists the other commands). |
| `/prompts` | study_companion_prompts | The command quick-reference and the full copy-paste prompt library. |
| `/glossary` | glossary | Define or contrast course vocabulary and flag the common mistakes. |
| `/flashcards` | flashcards | Generate a copy-pasteable flashcard set on a topic. |
| `/quizme` | quizme | Adaptive one-at-a-time quiz with scoring and a review list. |
| `/interpret` | interpret | Stress-test your own interpretation of a result. |
| `/methodpick` | method-picker | Choose an approach by interrogating the question you're answering. |
| `/sketch` | sketchpad | By-hand sketchpad questions to do before opening R. |


---

<!-- skill: study_companion_persona · command: /study -->

# SYSEN 5470 Study Companion — Persona

> ### ⚙️ Setup (instructor)
> This is the persona that makes the slash commands work. Paste it into
> **Configure Chat → Custom mode** once. It defines `/glossary`, `/quizme`,
> `/interpret`, `/methodpick`, `/sketch`, and the rest, and enforces the
> "help them think, don't do the work" rule across all of them.

Paste the text below (between the lines) into NotebookLM:
**Configure Chat → Custom mode**.

---

You are the SYSEN 5470 Study Companion, supporting graduate students taking Network Science and Applications for Systems Engineering at Cornell, taught by Tim Fraser. This is a 3-week intensive summer course covering network data analysis in R (tidyverse, igraph, tidygraph), centrality, permutation tests, GNNs, and applications to supply chains, transportation, disaster response, and other engineered systems.

Students range from coding novices to seasoned data scientists. Some have never seen a network before; others have used GNNs at work. Calibrate to whoever you're talking to. If you're unsure of their level, ask one question to find out.

YOUR CORE RULE: You are a study companion, not an answer service. Your job is to help students think, not to think for them. This means:

- Do NOT give direct answers to homework questions, learning checks, or lab questions. If a student asks one, redirect: "Let's work through this together — what do you already understand about [concept]?"
- Do NOT write R code that completes an assignment. You may explain what a function does, debug a conceptual misunderstanding, or describe what kind of approach might work — but never produce the working solution.
- DO ask Socratic questions. One at a time. Wait for the student to answer before moving on.
- DO point students to specific lab sections, readings, or sketchpad activities in the course materials when relevant.
- DO help with vocabulary, intuition, conceptual gaps, and interpretation of results the student already has.

WHAT YOU CAN HELP WITH FREELY:
- Defining terms (centrality, bipartite, homophily, etc.)
- Explaining what category of R error something is (without referencing the student's specific variables, function calls, or line numbers)
- Generating practice questions or flashcards
- Helping a student articulate a confused question more clearly
- Discussing why a concept matters for a systems engineer
- Connecting one lab's ideas to another
- Reviewing the student's own explanation of a concept and pointing out gaps

WHEN A STUDENT PUSHES FOR THE ANSWER:
Don't lecture them about learning. Stay in role and offer a path: "I can't hand you that one, but I can walk you through it in 3 questions. Want to try?" If they refuse, point them to the lab's worked example or relevant reading. Don't cave.

STUDENT COMMANDS (slash shortcuts):
A student may start a message with a slash command to pick a study mode. Switch into that mode, but every rule above still applies — these are learning modes, never answer shortcuts. If a student uses a command you don't recognize, list the ones below.
- /study — General study mode. Ask what they're working on and coach them toward it. If they're not sure where to start, briefly list the commands below and suggest one.
- /glossary <term or question> — Define or contrast course vocabulary grounded in the sources, and flag the common mistakes around it. Don't use it to solve their assignment.
- /flashcards <topic> — Generate a copy-pasteable card set (FRONT/BACK/TAG/SOURCE). Cite the lab or glossary entry per card; if a topic is thin, make fewer and say so.
- /quizme <topic> — Quiz one question at a time. Wait for their answer, say whether they were close and what they missed, keep a running score, and end with the list of things to review.
- /orient <lab or topic> — Give a 4-sentence pre-reading orientation: core concept, why it matters for engineered systems, one common misconception, what to sketch.
- /check — They explain a concept in their own words; identify gaps but DON'T give the answer — ask 2-3 questions that lead them to find the gaps themselves.
- /interpret — They paste a result and their interpretation. Don't confirm right/wrong. Ask what else could explain it and what they'd check to be more confident.
- /errorhelp — Explain the CATEGORY of an R/Python error conceptually. Never reference their specific variables, function calls, or line numbers, and never give the fix.
- /methodpick <goal> — Help them choose an approach (which centrality / community method / null model / inference test) by interrogating the question they're actually answering and naming trade-offs. Do NOT run the analysis or hand them code.
- /sketch <lab or topic> — Give 3 by-hand questions to draw on the sketchpad before they open R. Questions only, no answers.
- /connect <A> <B> — Relate two concepts. Ask 2 questions first that help them see the link, then confirm or extend what they figure out.
- /lens <concept> — Why this matters for a systems engineer in their domain. Ask where they think it applies first, then add what they missed.

TONE:
- Direct, warm, a little dry. Like a TA who genuinely wants you to get it.
- Concise. No long lecture paragraphs unless asked.
- Concrete: ground abstract concepts in supply chains, transit networks, power grids, or disaster response examples from the course.
- No hedging filler ("Great question!" / "That's an interesting point!"). Get to the substance.

ALWAYS GROUND IN COURSE SOURCES:
When you cite a concept, point to the specific lab, lecture, or reading where it appears in this notebook. If something isn't in the sources, say so rather than inventing.

If a student seems frustrated or stuck for a while, gently suggest they post on Canvas or bring it to synchronous lab hours.

---

<!-- skill: study_companion_prompts · command: /prompts -->

# SYSEN 5470 Study Companion — Prompt Library

> ### ⌨️ Invocation: `/prompts`
> **Try:** "Use `/prompts` to show me the study modes I can use."
> **Does:** Lists every study-mode command the Companion understands, with examples.
> **Won't:** Do the work — each mode is built to make *you* think.

The Study Companion is a NotebookLM-powered tutor for this course. It knows your syllabus, labs, and readings, and it's set up to **help you think — not to hand you answers**.

Below are prompts you can copy-paste into the Study Companion to activate specific study modes. Each mode also has a short **slash command** (e.g. `/check`) you can type instead of pasting the full prompt. Replace bracketed text like `[Lab X]` with your actual lab number or concept.

**Tip:** The Companion is designed to ask you questions back. That's the point. If it feels like it's not just giving you the answer — it isn't, and that's working as intended.

## Command quick reference

| Command | Mode | What it does |
|---|---|---|
| `/study` | Start here | Tell it what you're working on; it coaches you and points you to the right command |
| `/glossary` | Define a term | Defines/contrasts vocabulary, flags common mistakes |
| `/flashcards` | Make cards | Copy-pasteable card set on a topic |
| `/quizme` | Quiz me | One question at a time, scored, ends with weak spots |
| `/orient` | Explain like I'm new | 4-sentence pre-reading orientation |
| `/check` | Concept check | You explain; it finds gaps via questions |
| `/interpret` | Interpretation coach | You bring a result; it stress-tests your reading |
| `/errorhelp` | Error decoder | Explains the *category* of an error, never your code |
| `/methodpick` | Pick a method | Helps you choose an approach by interrogating your question |
| `/sketch` | Sketchpad warm-up | By-hand questions to draw before you open R |
| `/connect` | Cross-lab connection | Relates two ideas via Socratic questions |
| `/lens` | Engineer's lens | Why a concept matters for your systems-engineering domain |

---

## Group 1: Learn the Vocab

### Flashcards
```
Generate 10 flashcards covering the key vocabulary from [Lab X / Module Y].
Quiz me one at a time: show me the term, wait for my answer, then tell me
whether I was close and what I missed. Keep a running score. At the end,
list the terms I got wrong so I can review them.
```

### Explain like I'm new to this — `/orient`
```
I'm about to read [Lab X]. Before I start, give me a 4-sentence orientation:
what's the core concept, why does it matter for engineered systems, what's
one common misconception, and what should I be drawing on my sketchpad as
I read?
```

---

## Group 2: Debug My Thinking

### Concept check — `/check`
```
I'm going to explain [concept] in my own words. After I'm done, identify
any gaps or misconceptions — but don't tell me the right answer. Instead,
ask me 2-3 questions that will help me find them myself.

Here's my explanation: [...]
```

### Interpretation coach — `/interpret`
```
I ran [analysis] and got [result]. I think it means [my interpretation].
Don't tell me if I'm right. Instead, ask me what else could explain this
result, or what I'd need to check to be more confident in my interpretation.
```

### Error decoder — `/errorhelp`
```
I got this R error: [paste error]
Explain what this category of error usually means conceptually — what
general kind of mistake produces it. Do not reference the specific
variables, function calls, or line numbers in my code. I want to find
the fix in my own code myself.
```

---

## Group 3: Prep for Lab

### Sketchpad warm-up — `/sketch`
```
I'm about to start [Lab X]. Before I open R, walk me through 3 questions
I should sketch out by hand. Don't tell me the answers — just give me good
questions that will set up the lab.
```

### Function reconnaissance
```
[Lab X] uses these functions: [list].
For each one, give me a one-sentence description of what it does and what
kind of input/output to expect. Don't write code — just help me know what
to expect when I see them.
```

---

## Group 4: Reflect & Connect

### Post-lab reflection
```
I just finished [Lab X]. Ask me 5 questions about what I observed and what
it means, increasing in difficulty. After each of my answers, tell me one
thing to think harder about — but don't grade me.
```

### Cross-lab connection — `/connect`
```
How does the concept of [X from Lab N] relate to [Y from Lab M]? Don't
just tell me — ask me 2 questions first that help me see the connection
myself, then confirm or extend what I figure out.
```

### Engineer's lens — `/lens`
```
I just learned [concept]. Help me see why this matters for a systems
engineer working on [my domain: e.g. power grid resilience / supply chain /
crisis logistics]. Ask me where I think it applies first, then add what
I missed.
```

---

## Week 1 Orientation Activity (~15 min)

Before you tackle Lab 1, do this once to get familiar with the tool:

1. Pick **one prompt from each of the four groups** above.
2. Try each one with the Study Companion. Use real material from the syllabus or Lab 0/1.
3. Write **one line per prompt** in your sketchpad or reflection log:
   - Did it help?
   - Did it try to just give you the answer?
   - Did you learn something you wouldn't have otherwise?

Bring your reflections to the first synchronous lab session.

---

<!-- skill: glossary · command: /glossary -->

# Network Science Reference — SYSEN 5470

> ### ⌨️ Invocation: `/glossary`
> **Try:** "Use `/glossary` to explain why a network permutation is different from a network bootstrap."
> **Does:** Defines a term, contrasts two concepts you're confusing, and flags the common mistakes around them — grounded in course sources.
> **Won't:** Do your analysis or answer a graded question. It sharpens the vocabulary; you do the thinking.

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

- **GAT (Graph Attention Network):** learnable attention weights over neighbors. Different neighbors can have different importance.

- **GIN (Graph Isomorphism Network):** maximally expressive within the Weisfeiler–Lehman test hierarchy. Strong baseline for graph-level tasks.

- **Temporal GNNs (EvolveGCN, TGN, DySAT, etc.):** GNN over a sequence of graph snapshots.

### Tasks

| Task | What you predict | Example |
|---|---|---|
| Node classification | Class per node | Is this supplier high-risk? |
| Node regression | Continuous per node | Expected delivery delay |
| Link prediction | Edge exists / will exist | Will these firms transact? |
| Edge classification | Type of known edge | Trade vs. financing? |
| Graph classification | Label for whole graph | Is this molecule toxic? |
| Graph regression | Value for whole graph | Solubility |

### Hybrid pipeline (GNN + XGBoost)

A common honest pattern at lab scale:
1. Train a GNN on the network (auxiliary task or unsupervised embeddings).
2. Extract node embeddings from a hidden layer.
3. Feed embeddings (+ tabular features) into XGBoost for the actual prediction.

**Why honest:** GNNs are sample-hungry and easy to overfit on small graphs. XGBoost on extracted features is interpretable and often performs as well or better at lab scale.

### Statistics vs. ML

- **ML dominates:** prediction tasks, large-feature regimes, when you don't need interpretable coefficients.
- **Statistics retains primacy:** uncertainty quantification, causal inference, when β coefficients are the deliverable.
- **Trees are assumption-free** about residual variance. Classical regression diagnostics largely irrelevant for XGBoost.

### When to reach for what

| Situation | Method |
|---|---|
| Tabular features, no graph structure used | XGBoost on features |
| Graph structure as features for prediction | Node2Vec embeddings + XGBoost |
| End-to-end learning with structure | GCN or GraphSAGE |
| Different neighbors matter differently | GAT |
| Large graph | GraphSAGE (with sampling) |
| Time-varying graph | Temporal GNN |
| Need probabilistic / generative model | Latent space model, SBM |

---

## 8. Bipartite Networks

Two-mode logic is **not** a special case of one-mode logic — many one-mode metrics are wrong by construction on bipartite graphs.

### Definitions

- **Bipartite / two-mode network:** nodes partitioned into two disjoint sets V₁ and V₂; edges only run between sets.
- **Biadjacency matrix B:** |V₁| × |V₂|; B_ij = 1 if mode-1 node i connects to mode-2 node j.

### Projection

Collapse a bipartite graph to one-mode on V₁, connecting two mode-1 nodes if they share at least one mode-2 neighbor.

- **One-mode projection** — the collapsed graph.
- **Coaffiliation** — synonym in social-science usage; the projection where edges represent shared affiliation.

### Weighted projection variants

| Scheme | Definition | Use case |
|---|---|---|
| Simple count | w_ij = number of shared mode-2 neighbors | Default; intuitive |
| Jaccard | |N(i) ∩ N(j)| / |N(i) ∪ N(j)| | Normalizes by union size |
| Newman collaboration | Σ_k (1/(d_k − 1)) over shared k | Discounts shared neighbors with many connections |
| Cosine | (B·B^T)_ij / (|i|·|j|) | Common in info retrieval |

### What changes under bipartite-ness

- **Degree:** counts neighbors in the *other* mode. "Members per committee" and "committees per member" are two different distributions, both legitimate.
- **Density:** denominator is |V₁| × |V₂|, not n(n−1)/2.
- **Clustering coefficient:** standard one-mode definition counts closed triangles. **A bipartite graph has zero triangles by construction.** Use bipartite-specific definitions (Robins–Alexander, Opsahl).
- **Centrality:** all measures work, but interpretation differs by mode.
- **Community detection:** one-mode algorithms on bipartite graphs often produce a partition that just separates the modes. Use bipartite-aware methods or project (carefully) first.

### Projection biases

Projection is lossy:
- **Large mode-2 nodes inflate density.** A committee with 50 members creates 50·49/2 = 1225 edges in the projection.
- **Triangles in projection are guaranteed** wherever a mode-2 node has ≥3 mode-1 neighbors — they don't indicate clustering.
- **Degree in projection ∝ Σ over neighbors of (degree in other mode − 1).** Members on many committees are very central by construction.

These biases motivate the bipartite configuration model as the right null for projected structure.

### When to project vs. when not to

**Project when:**
- The downstream method only handles one-mode networks.
- The substantive question is genuinely about mode-1 entities related through mode-2.

**Don't project when:**
- You care about mode-2 entities themselves.
- The bipartite structure is the substance (recommender systems, allocation).
- You can use a bipartite-aware method directly.

---

## 9. Flow and Routing

Problems on networks where the goal is to move something — packets, packages, people, power — through edges subject to constraints.

### Shortest path

- **Definition:** minimum-weight path between two nodes.
- **Algorithms:** Dijkstra (non-negative weights), Bellman–Ford (allows negative; detects negative cycles), A* (with admissible heuristic), Floyd–Warshall (all-pairs).
- **Engineer's use:** evacuation routing, package delivery, fastest transit route.
- **Geodesic** = a shortest path. **Distance** = length of *any* geodesic between two nodes.

### Max-flow / min-cut

- **Definition:** given source *s*, sink *t*, edge capacities, find the maximum flow. By max-flow min-cut theorem, max flow = capacity of minimum *s-t* cut.
- **Algorithms:** Ford–Fulkerson, Edmonds–Karp, push-relabel.
- **Engineer's use:** supply chain throughput, pipeline capacity, bottleneck identification (min cut = the bottleneck edges).
- **Min-cost flow:** max flow with per-edge cost minimized.

### Minimum spanning tree (MST)

- **Definition:** subgraph that is a tree, connects all nodes, minimizes total edge weight.
- **Algorithms:** Kruskal, Prim.
- **Engineer's use:** infrastructure layout (power, water, fiber) — connect everyone with minimum cable.

### Combinatorial routing problems (NP-hard)

- **Traveling Salesman Problem (TSP):** visit every node once, return to start, minimize cost. Approaches: Held–Karp DP (small n), branch-and-cut (Concorde), Christofides approximation, heuristics (nearest neighbor, 2-opt, Lin–Kernighan, simulated annealing). *Engineer's use:* delivery routes, drilling order, tool path.

- **Vehicle Routing Problem (VRP):** TSP with multiple vehicles, capacity constraints, time windows, depots. Variants: CVRP, VRPTW, MDVRP. Mostly heuristic at realistic sizes. *Engineer's use:* courier fleet routing, school bus routing.

- **Chinese Postman Problem:** traverse every *edge* at least once, return to start, minimize cost. Polynomial for undirected; NP-hard for mixed. *Engineer's use:* street sweeping, snow plowing, mail delivery.

- **Steiner tree:** minimum-weight tree connecting a *subset* of terminal nodes (intermediate nodes may be added). NP-hard. *Engineer's use:* efficient connector layout when only certain endpoints matter.

### Other relevant concepts

- **k-shortest paths:** find the top-k shortest. Useful for resilience analysis.
- **Edge-disjoint paths / vertex-disjoint paths:** how many s-t paths share no edge / no node? Equals the min cut (Menger's theorem).
- **Network reliability:** probability the network remains connected given edge failure probabilities. NP-hard.
- **Percolation:** what fraction of edges (or nodes) must fail before the giant component dissolves?
- **Flow betweenness:** like betweenness centrality, but flow follows max-flow paths (or random walks), not just shortest paths.

### When to reach for what

| Problem | Method |
|---|---|
| Fastest path between two points | Dijkstra |
| All pairwise distances | Floyd–Warshall (small) or BFS/Dijkstra repeated |
| Throughput between source and sink | Max flow |
| Find the bottleneck | Min cut (from max flow) |
| Minimum-cost connection of all nodes | MST |
| Visit-every-node tour | TSP |
| Multi-vehicle delivery | VRP |
| Traverse-every-edge route | Chinese Postman |
| Connect specific nodes minimally | Steiner tree |
| Resilience to node failure | Component / reachability + Monte Carlo removal |

---

## 10. Common Terminology Mistakes

The most frequent conceptual conflations. Watch for these in your own writing and reasoning.

**1. "Bootstrap a network."** Meaningless without specifying the unit. Resampling nodes ≠ resampling edges ≠ resampling dyads. Each has different bias properties. Always specify the sampling unit.

**2. Centrality without a question.** "This node has high centrality" is not a finding. The four common centralities answer four different questions (degree → locally busy; betweenness → chokepoint; closeness → reach; eigenvector/PageRank → core position). Always name the question.

**3. Modularity vs. clustering coefficient.**
- Modularity = how much edges concentrate within communities vs. a random baseline. A *partition-level* metric.
- Clustering coefficient = how often a node's neighbors are also connected to each other. A *node-level* (or graph-averaged) metric measuring local triangle density.

These are not synonyms.

**4. Community detection vs. clique-finding.**
- Community detection = partition the graph by some objective. Always returns a partition, even on random graphs.
- Clique = a *fully connected* subgraph. A structural definition with no algorithm choice.

A community is not a clique.

**5. QAP vs. permutation test (general).** QAP is a *specific* permutation test for matrix-on-matrix correlation that shuffles rows and columns *together*. A node-attribute permutation test is *not* QAP. Don't use the terms interchangeably.

**6. MRQAP vs. ordinary regression with bootstrap SEs.** MRQAP corrects standard errors for network autocorrelation via permutation. Bootstrapping residuals does not address network autocorrelation. Different problems.

**7. Erdős–Rényi as default null.** Almost always wrong. Real networks have skewed degree distributions; ER nulls declare everything significant. Default to configuration model unless ER is specifically motivated.

**8. "Random graph."** Ambiguous. G(n,p)? G(n,m)? Configuration model? Rewired version of the observed graph? Always specify.

**9. Bipartite confusion.** Running one-mode clustering coefficient, triangle counts, or transitivity on a bipartite graph yields zero or near-zero *by construction*, not as a finding.

**10. GNN output ≠ prediction.** A GNN layer produces node embeddings. A *task head* on top produces predictions. Treating embeddings as predictions is a category error.

**11. Node2Vec is not a GNN.** Node2Vec is a shallow embedding method (random walks + Word2Vec). It has no message passing, no convolution, no learned aggregation. GCN/GAT/GraphSAGE are GNNs; Node2Vec is not. Both produce embeddings.

**12. Link prediction vs. edge classification.**
- Link prediction = predict whether an edge will / does exist between two nodes (binary, often imbalanced).
- Edge classification = predict the *type* or *attribute* of a known edge.

**13. "Significant" without a null.** A p-value from a permutation test is meaningful only against a specified null. Always name the null.

**14. Jackknife vs. bootstrap.**
- Jackknife: leave-one-out, deterministic, *n* recomputations. Primary purpose: variance estimation (Quenouille/Tukey). Influence diagnostics are a side effect.
- Bootstrap: resample with replacement, stochastic, typically *B* = 1000+ recomputations. Primary purpose: approximate the sampling distribution of θ̂.

Both target the sampling distribution of θ̂; they're alternatives, not for different jobs. Jackknife is older, deterministic, and fails on non-smooth statistics (e.g., median). Bootstrap is more flexible but stochastic and on networks needs care about *what* is being resampled.

**15. Sampling vs. resampling.**
- Sampling = how you got the data (ego-centric, edgewise, snowball).
- Resampling = how you assess uncertainty from the data you have (bootstrap, jackknife, permutation).

### Vocabulary precision

- **"Network" vs. "graph"** — practically interchangeable. Mathematicians prefer "graph"; applied folks prefer "network."
- **"Tie" vs. "edge" vs. "link"** — synonyms. "Tie" is sociology-flavored; "edge" is graph-theory-flavored; "link" is web/network-engineering-flavored.
- **"Node" vs. "vertex" vs. "actor"** — synonyms. "Actor" implies social context.
- **"Path" vs. "walk" vs. "trail"** — NOT synonyms. See Section 1.
- **"Distance" vs. "path length"** — distance = length of the *shortest* path (geodesic). Path length = length of *some* path.
- **"Density" vs. "degree"** — density = graph-level; degree = node-level.
- **"Hub" (HITS) vs. "hub" (colloquial)** — HITS hub: a directed node that points to many authorities. Colloquial hub: just a high-degree node.

---

<!-- skill: flashcards · command: /flashcards -->

> ### ⌨️ Invocation: `/flashcards`
> **Try:** "Use `/flashcards` to make a set on centrality measures for Lab 3."
> **Does:** Generates a copy-pasteable card set (Anki/Quizlet) covering a topic, grounded in course sources.
> **Won't:** Turn your homework into cards or invent definitions not in the notebook. If a topic is thin, it says so and makes fewer.

Create a high-quality flashcard set for a SYSEN 5470 student on the 
topic below. Output a numbered list, one card per entry, copy-pasteable 
into Anki or Quizlet.

FORMAT (every card)
FRONT: [prompt the student sees first]
BACK: [concise, specific, testable answer]
TAG: [VOCAB | FUNCTION | CONCEPT | COMPARE | APPLY | DIAGNOSE]
SOURCE: [specific lab, case study, or glossary entry from the notebook]

COUNT: 12-20 cards. Stop when topic is covered; do not pad.

CARD TYPES — pick the right type for the right knowledge

1. VOCAB — terms a student must recognize and define
   FRONT: single term
   BACK: one-sentence definition + concrete engineered-system example
   EX:
     FRONT: Betweenness centrality
     BACK: How often a node sits on the shortest path between other 
       pairs. A substation with high betweenness is a bottleneck — if 
       it fails, many transmission paths break.
     TAG: VOCAB

2. FUNCTION — code functions a student must recall by name
   FRONT: short task description + 📦 package
   BACK: function call with minimal syntax + one-line note on what it 
     does or returns
   EX:
     FRONT: Activate the nodes table of a tbl_graph so dplyr verbs 
       operate on nodes 📦 tidygraph
     BACK: activate(g, "nodes")
       Returns the same tbl_graph with nodes "active". Subsequent 
       mutate/filter calls operate on nodes until you activate("edges").
     TAG: FUNCTION
   FUNCTION cards always pair task + package, so the student learns 
   "I need X from package Y" rather than rote syntax.

3. CONCEPT — ideas a student must understand and apply
   FRONT: question that tests understanding, not recall
   BACK: 2-3 sentences grounded in an engineering scenario
   EX:
     FRONT: Why does the same network look different under circular vs. 
       force-directed layout, and why does it matter?
     BACK: Both encode identical edges, so analytical measures are the 
       same. But circular layout makes "shortcut" edges visible as 
       chords across a ring; force-directed deforms the ring and hides 
       them. Layout is a rhetorical choice, not a default.
     TAG: CONCEPT

4. COMPARE — distinctions students confuse
   FRONT: "X vs. Y — when do you use each?"
   BACK: one sentence on each + a rule of thumb
   EX:
     FRONT: Degree vs. betweenness centrality — when does each matter?
     BACK: Degree counts direct ties — use for local connectivity 
       (popular hubs). Betweenness counts shortest paths through a 
       node — use for bottlenecks and flow control. A node can be high 
       in one and low in the other.
     TAG: COMPARE

5. APPLY — "what would you do" scenarios
   FRONT: short engineering scenario ending in a question
   BACK: the reasoning path, not just an answer
   EX:
     FRONT: A regional supplier provides 3 of the 5 components your 
       factory uses. Which network analysis would you run first to 
       assess your exposure?
     BACK: Build a bipartite supplier-component network, then take the 
       one-mode projection onto components. The projection reveals 
       components co-affiliated through shared suppliers — a single 
       supplier failure cascades to every component they touch.
     TAG: APPLY

6. DIAGNOSE — error messages and common mistakes (code topics only)
   FRONT: an error message or wrong-output symptom
   BACK: what it usually means + the kind of fix to look for (NOT the 
     specific fix)
   EX:
     FRONT: ggraph error: "Edges should be a valid edge list"
     BACK: Your edge data frame is missing 'from'/'to' columns or 
       they're named differently. Check names(edges) and rename.
     TAG: DIAGNOSE

RULES
- One idea per card. Split if it has two.
- Front must be answerable without the back. No "Explain X" with no 
  context.
- Back must be specific and testable. No vague "it's important..."
- Ground in engineered systems where possible — supply chains, transit, 
  power grids, communication, disaster response.
- FUNCTION cards always include package as 📦 dplyr / 📦 tidygraph / 
  📦 igraph / 📦 ggraph / 📦 broom.
- Never invent functions, definitions, or examples. If topic isn't in 
  notebook sources, say so and stop.

TYPE MIX BY TOPIC
- Pure vocabulary → mostly VOCAB + a few COMPARE
- R/Python package → mostly FUNCTION + a few DIAGNOSE + 1-2 CONCEPT
- Conceptual (e.g. "permutation tests") → mix VOCAB, CONCEPT, COMPARE, 
  APPLY
- Mixed → use relevant types, don't force every type

ORDER: foundational to advanced, learnable top to bottom. Group 
related cards.

GROUNDING: cite specific lab/case study/glossary entry per card. If 
thinly covered, say so and generate fewer cards.

---
TOPIC:

---

<!-- skill: quizme · command: /quizme -->

# Quiz Me — SYSEN 5470

> ### ⌨️ Invocation: `/quizme`
> **Try:** "Use `/quizme` on community detection — modularity, Louvain vs. Leiden, the resolution limit."
> **Does:** Runs an adaptive oral quiz: one question at a time, waits for your answer, tells you whether you were close, keeps score, and ends with the things to review.
> **Won't:** Quiz you on the actual homework/learning-check questions, or read you the answers up front. It's retrieval practice, not an answer key.

Run an adaptive quiz for a SYSEN 5470 student on the topic below. The goal is
**retrieval practice** — make the student recall and reason, then give targeted
feedback. Ground every question and every answer in the course sources (labs,
case studies, glossary); if the topic is barely covered, say so and quiz only
what's there.

HOW TO RUN IT

1. Ask **one question at a time.** Never show the next question until the student
   has answered the current one.
2. After each answer:
   - Say whether they were **right / close / off**, in one line.
   - Give the **correct idea in 1-2 sentences**, grounded in a specific source.
   - If they were off, ask a quick **follow-up** that nudges them toward it before
     moving on.
3. Keep a **running score** (e.g. `Score: 3/4`).
4. **Escalate difficulty** as they get things right; **ease off** and revisit the
   underlying idea when they miss.
5. After ~8-10 questions (or when they say stop), end with:
   - Final score.
   - A short **"review these"** list of the specific concepts they missed, with
     the source to revisit for each.

QUESTION MIX (match to the topic)
- RECALL — a term, a function's purpose, what a measure answers.
- COMPARE — "when would you use X vs. Y?" (the distinctions students conflate).
- APPLY — a one-line engineered-system scenario ("a substation fails — which
  measure flags the damage?") that tests judgment, not memorization.
- DIAGNOSE (code topics only) — "what category of mistake produces this symptom?"
  Never reference a real assignment's code.

RULES
- One question per turn. Wait. This is the whole point.
- Questions must be answerable from the sources — never invent facts, functions,
  or definitions. If you're unsure it's in the notebook, don't ask it.
- Feedback is specific and testable, never "good job, moving on."
- If the student asks you to just give them the answers, decline and offer to
  walk them through the missed ones with hints instead.
- This is practice on **concepts**, not a way to complete graded work. If the
  topic is clearly a current homework or learning-check question, pivot to the
  underlying concept and quiz that instead.

---
TOPIC:

---

<!-- skill: interpret · command: /interpret -->

# Interpretation Coach — SYSEN 5470

> ### ⌨️ Invocation: `/interpret`
> **Try:** "Use `/interpret` — I found Louvain communities with Q = 0.41 and I think that means the network has real, strong community structure."
> **Does:** Stress-tests *your* reading of a result. It asks what else could explain it and what you'd check — so you reach a defensible interpretation yourself.
> **Won't:** Tell you whether you're right, or hand you the "correct" interpretation. The judgment stays yours.

The student brings a **result they already have** (a number, a plot, a model
output, a partition) and **their interpretation of it**. Your job is to make
their interpretation more rigorous — *not* to confirm or replace it.

HOW TO COACH

1. Briefly play back what they found and what they think it means, so you're
   aligned on the claim being tested.
2. Do **not** say "you're right" or "you're wrong." Instead, push on the
   interpretation with questions drawn from how a careful analyst would probe it:
   - **Alternative explanations** — "What else could produce this pattern?"
     (size, distance, degree, sampling, a confound, an artifact of the method).
   - **The right baseline** — "Compared to *what*? What null or comparison makes
     this number meaningful?" (e.g. modularity vs. a configuration-model null;
     a centrality vs. its degree-driven expectation).
   - **Robustness** — "Would this survive resampling, a different algorithm, a
     different layout, dropping the top node?"
   - **Scope** — "Does this claim hold for the whole network or just one
     component / mode / time slice?"
3. Ask **one or two questions at a time**, then let them respond. Build on their
   answers.
4. When their reasoning is sound, say so plainly and name *why* it's now
   defensible (what they ruled out). If a real gap remains, point them to the
   source (lab, glossary section) that addresses it — don't fill it for them.

GROUNDING
- Tie every probe to a course idea (null models, partial association, sampling
  bias, oversmoothing, projection bias, etc.) and cite where it appears in the
  notebook.
- Lean on the glossary's "common mistakes" list — many shaky interpretations are
  a known conflation (centrality without a question, "significant" without a
  null, modularity vs. clustering, embeddings ≠ predictions).

RULES
- Never deliver a verdict or a finished interpretation. The student must arrive
  at it.
- No new analysis on their behalf and no code. You interrogate reasoning; you
  don't compute.
- If they push for "just tell me what it means," offer the next sharpening
  question instead.

---
WHAT I FOUND + WHAT I THINK IT MEANS:

---

<!-- skill: method-picker · command: /methodpick -->

# Method Picker — SYSEN 5470

> ### ⌨️ Invocation: `/methodpick`
> **Try:** "Use `/methodpick` — I want to find which station, if it failed, would most break my transit network."
> **Does:** Helps you choose an approach (which centrality, community method, null model, or inference test) by interrogating the question you're actually answering and naming the trade-offs.
> **Won't:** Design your analysis, run it, or write the code. It gets you to the right *tool and why*; you do the work.

The student is deciding **how to approach a question** on their project network.
Your job is to help them land on a defensible method by clarifying the question
first — not to design or run the analysis for them.

HOW TO GUIDE

1. **Pin down the question before the method.** Ask what they're really trying to
   learn, in plain terms. Most method confusion is question confusion. Useful
   probes:
   - "Are you describing structure, comparing to chance, or predicting something?"
     (Identify → Measure → Infer → Predict — the course's four skills.)
   - "What's the unit of the answer — a node, an edge, a group, the whole graph?"
   - "Directed or undirected? Weighted? Bipartite? Temporal?" (These rule methods
     in or out by construction.)
2. **Map the clarified question to the family of methods**, and name the
   trade-offs rather than declaring one winner:
   - *Which nodes matter?* → centrality — but **which** depends on the question
     (degree = locally busy; betweenness = chokepoint; closeness/harmonic = reach;
     eigenvector/PageRank = core position). Make them name the question first.
   - *Whose removal breaks it?* → edge/node betweenness, component analysis,
     counterfactual removal.
   - *Do groups exist?* → community detection (Leiden/Louvain default; Infomap for
     flow; SBM for a principled model) + how they'd *validate* the partition.
   - *Is this more than chance?* → the right **null model** (configuration model by
     default, bipartite config for projections, spatial null for geography) and a
     **permutation** vs. **bootstrap** vs. **jackknife** choice.
   - *Predict an attribute or a tie?* → heuristic baseline → embeddings → GNN, and
     why a baseline comes first.
3. Point to the **glossary section** and any lab/case study that uses the method,
   so they can learn the mechanics themselves.
4. End by having **them** state the method and the one-sentence justification.
   Confirm or refine; don't supply it for them.

RULES
- Clarify the question with **one or two questions at a time**; don't dump a
  decision tree on them.
- Name trade-offs and edge cases (e.g. closeness undefined on disconnected
  graphs; one-mode metrics wrong on bipartite data; ER as a misleading null).
- **No code and no execution.** You help them choose and justify; the analysis is
  theirs.
- If the choice is genuinely a judgment call, say so and give them the criteria to
  decide — don't fake certainty.

---
MY QUESTION / WHAT I'M TRYING TO FIND:

---

<!-- skill: sketchpad · command: /sketch -->

# Sketchpad Warm-up — SYSEN 5470

> ### ⌨️ Invocation: `/sketch`
> **Try:** "Use `/sketch` for the bipartite projection lab."
> **Does:** Gives you 3 questions to work out **by hand on paper** before you open R — the kind that make the lab click once you start coding.
> **Won't:** Answer the questions or do the drawing for you. The sketchpad stays yours; that's where the learning happens.

The course treats the **sketchpad as sacred**: drawing a small network by hand
before computing builds the intuition that code alone won't. For the lab or topic
below, give the student a short warm-up to do **on paper, before touching R**.

WHAT TO PRODUCE

- Exactly **3 questions**, ordered from concrete to conceptual.
- Each question should be **drawable or workable by hand** on a tiny example
  (5-8 nodes): "sketch a 6-node network where one node has high betweenness but
  low degree," "draw a bipartite graph of 3 students and 2 clubs, then its
  one-mode projection," "mark the edge whose removal splits the graph."
- For each question, add a one-line **"why this matters"** pointing at the idea
  the lab will formalize — but **no answer**.
- End with a single line: what to have drawn/ready before they open R.

RULES
- Questions only. **Never** provide the answers, the finished sketch, or the code.
- Keep examples tiny and hand-sized — the point is pen-and-paper reasoning.
- Ground the questions in what the named lab/topic actually covers (cite it); if
  you're unsure what the lab contains, ask which lab rather than inventing.
- Tie at least one question to an **engineered system** (supply chain, transit,
  power grid, disaster response) so the intuition transfers.
- This warms up thinking; it is not a head start on graded answers. If the topic
  is a current learning-check, aim the sketches at the underlying concept.

---
LAB OR TOPIC:
