"""Case Study 07 — Network Permutation Testing (Python track).

The lab walked you through a key idea: when you compute a network
statistic (homophily, assortativity, mean within-group edge weight),
you need a NULL MODEL to know if the value you saw is "real" or just
noise. The null model says "what would we expect if labels were
random?"

But — and this is the crucial part — *random with respect to what?*
If your network has community structure that you're not controlling
for, shuffling labels everywhere can give you a too-easy null. The
right comparison is often a **block permutation**: shuffle labels
within community.

We'll do both, on a synthetic network with planted demographic
homophily AND planted neighborhood-demo correlation.
"""

# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

import pandas as pd
import numpy as np
import igraph as ig
import matplotlib.pyplot as plt

## 0.2 Load helpers ##########################################################

from functions import (
    load_nodes, load_edges, build_graph, assort_by, permute_labels
)

## 0.3 Load data #############################################################

nodes = load_nodes()
edges = load_edges()
g     = build_graph(nodes, edges)
print(g.summary())
print(nodes.head())


# 1. Observed assortativity ###################################################
#
# We computed the nominal assortativity coefficient on the "demo"
# attribute. Positive = same-demo edges are over-represented;
# 0 = random; negative = disassortative.

observed = assort_by(g, "demo")
print(f"Observed assortativity by `demo`: {observed:.4f}")


# 2. Null model 1: UNBLOCKED permutation ######################################
#
# Shuffle the `demo` label across ALL nodes, recompute, repeat.

rng = np.random.default_rng(42)
n_perm = 500
null_unblocked = np.empty(n_perm)
for i in range(n_perm):
    g_perm = permute_labels(g, "demo", block_by=None, rng=rng)
    null_unblocked[i] = assort_by(g_perm, "demo")

p_unblocked = float(np.mean(null_unblocked >= observed))
print(f"Unblocked null:    mean = {null_unblocked.mean():+.4f}  "
      f"sd = {null_unblocked.std():.4f}  p = {p_unblocked:.3f}")


# 3. Null model 2: BLOCK permutation by neighborhood ##########################
#
# Shuffle `demo` ONLY within neighborhood. This preserves the
# neighborhood-level composition. It's a more conservative null,
# because some of the apparent "homophily" comes from the fact that
# neighborhoods are themselves demo-segregated.

null_blocked = np.empty(n_perm)
for i in range(n_perm):
    g_perm = permute_labels(g, "demo", block_by="neighborhood", rng=rng)
    null_blocked[i] = assort_by(g_perm, "demo")

p_blocked = float(np.mean(null_blocked >= observed))
print(f"Block-permuted null: mean = {null_blocked.mean():+.4f}  "
      f"sd = {null_blocked.std():.4f}  p = {p_blocked:.3f}")


# 4. Visualize the two null distributions vs the observed #####################

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.hist(null_unblocked, bins=30, alpha=0.55, label="Unblocked null",
        color="#3a8bc6")
ax.hist(null_blocked,   bins=30, alpha=0.55, label="Block-permuted null",
        color="#e07b3a")
ax.axvline(observed, color="black", linestyle="--", label=f"Observed = {observed:.3f}")
ax.set_xlabel("Nominal assortativity by `demo`")
ax.set_ylabel("# of permutations")
ax.set_title("Two null models, two p-values")
ax.legend()
fig.tight_layout()
fig.savefig("permutation_nulls.png", dpi=120)
plt.close(fig)


# 5. The take-home ###########################################################
#
# Compare the two p-values. The UNBLOCKED null is centered well
# below the observed — so unblocked says "very significant homophily".
# The BLOCKED null is centered MUCH CLOSER to observed — so blocked
# says "okay, much of the apparent homophily was just because A's
# and B's live in different neighborhoods; the *additional* homophily
# beyond that is smaller."
#
# This is the canonical mistake the case study warns against. If you
# fit the wrong null model, you get the wrong answer with great
# confidence.


# 6. Learning Check ##########################################################
#
# QUESTION: What is the *block-permuted* p-value for assortativity by
# `demo`? (Use neighborhood as the block. 500 permutations.) Report
# to 3 decimal places.

print(f"Learning Check answer: {p_blocked:.3f}")
