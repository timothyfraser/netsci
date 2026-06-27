"""Case Study 06 — Network Permutation Testing (Python track).

The lab walked you through a key idea: when you compute a network
statistic (homophily, assortativity, mean within-group edge weight),
you need a NULL MODEL to know if the value you saw is "real" or just
noise.

What is a null model? It asks: what values would our statistic take if
the effect we're testing did NOT exist? We build that "no-effect" world
by shuffling labels many times and recomputing the statistic each time;
that spread of shuffled values is the null distribution. If our real,
observed value sits comfortably inside that spread, we can't tell it
apart from chance ("fail to reject"); if it sits far out in the tail,
we can.

But — and this is the crucial part — *random with respect to what?*
If your network has community structure that you're not controlling
for, shuffling labels everywhere can give you a too-easy null. The
right comparison is often a **block permutation**: shuffle labels
within community.

If you know regression, a blocking variable is just a covariate you
control for. Block permutation holds that confounder fixed (it shuffles
labels only WITHIN each block) so you test the within-block signal you
actually care about; the unblocked null controls for nothing, which is
exactly why it looks "too significant" when neighborhoods are segregated.

We'll do both, on a synthetic network with planted demographic
homophily AND planted neighborhood-demo correlation.
"""

# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `igraph` for assortativity. `numpy` for the per-permutation array,
# `matplotlib` for the two-null distribution plot.
import pandas as pd
import numpy as np
import igraph as ig
import matplotlib.pyplot as plt

## 0.2 Load helpers ##########################################################

# `assort_by()` wraps `igraph.assortativity_nominal`; `permute_labels()`
# shuffles a vertex attribute, optionally within blocks defined by
# another attribute. Both live in functions.py.
from functions import (
    load_nodes, load_edges, build_graph, assort_by, permute_labels
)

print("\n🚀 Case Study 06 — Network Permutation Testing (Python)")
print("   Same observed stat, two null models. Watch the p-value change.\n")

## 0.3 Load data #############################################################

nodes = load_nodes()
edges = load_edges()
g     = build_graph(nodes, edges)
print(g.summary())
print(nodes.head())
print(f"✅ Loaded graph: {g.vcount()} nodes (demos A vs B in 10 neighborhoods).")


# 1. Observed assortativity ##################################################
#
# Nominal assortativity: positive = same-demo edges over-represented;
# 0 = random; negative = disassortative. This is the number we'll test.

observed = assort_by(g, "demo")
print(f"📊 Observed assortativity by `demo`: {observed:.4f}")


# 2. Null model 1: UNBLOCKED permutation #####################################
#
# Shuffle the `demo` label across ALL nodes, recompute assortativity,
# repeat 500 times. The unblocked null breaks BOTH any demo-edge link
# AND any demo-neighborhood link — it's the "everything is random"
# baseline.

rng = np.random.default_rng(42)
n_perm = 500
null_unblocked = np.empty(n_perm)
for i in range(n_perm):
    g_perm = permute_labels(g, "demo", block_by=None, rng=rng)
    null_unblocked[i] = assort_by(g_perm, "demo")

p_unblocked = float(np.mean(null_unblocked >= observed))
print(f"🧪 Unblocked null: mean = {null_unblocked.mean():+.4f}  "
      f"sd = {null_unblocked.std():.4f}  p = {p_unblocked:.3f}")


# 3. Null model 2: BLOCK permutation by neighborhood #########################
#
# Shuffle `demo` ONLY within neighborhood. This preserves the
# neighborhood-level composition. A more conservative null, because
# some apparent "homophily" comes from the fact that A's and B's
# already live in different neighborhoods.
#
# Stats analogy: `block_by="neighborhood"` == "control for neighborhood".
# We destroy only the within-neighborhood demo signal (what we're testing)
# while holding the neighborhood composition (the confounder) fixed.

null_blocked = np.empty(n_perm)
for i in range(n_perm):
    g_perm = permute_labels(g, "demo", block_by="neighborhood", rng=rng)
    null_blocked[i] = assort_by(g_perm, "demo")

p_blocked = float(np.mean(null_blocked >= observed))
print(f"🧪 Block-permuted null: mean = {null_blocked.mean():+.4f}  "
      f"sd = {null_blocked.std():.4f}  p = {p_blocked:.3f}")

# Which direction is "good"? A LARGE p-value means FAIL TO REJECT — the
# observed value is unremarkable under this null. A SMALL one means REJECT.
if p_blocked > 0.05:
    print(f"ℹ️  p = {p_blocked:.3f} is LARGE -> FAIL TO REJECT: the observed "
          f"assortativity is ordinary once neighborhood is held fixed.")
else:
    print(f"ℹ️  p = {p_blocked:.3f} is SMALL -> REJECT: homophily remains "
          f"beyond what neighborhood explains.")


# 4. Visualize the two null distributions vs the observed ####################

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
print("💾 Saved permutation_nulls.png")


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
#
# WHY does the blocked null land so close to the observed value? Within a
# segregated neighborhood almost everyone shares the same demo label, so
# shuffling labels WITHIN a neighborhood barely changes the graph -- each
# permuted network looks almost like the real one, and the null piles up
# right around the observed statistic (so the observed looks ordinary). The
# unblocked null also scrambles geography, destroying the segregation that
# produced most of the assortativity in the first place -- so its null sits
# far below the observed value and the observed looks extreme. Same number,
# two nulls, opposite verdicts.
#
# WHICH NULL DO I REACH FOR ON MY OWN DATA? Decision rule:
#   - Use a BLOCKED null when a known structural variable (here:
#     neighborhood) already explains part of how the labels are
#     distributed, and you want the signal that REMAINS after accounting
#     for it. Block on the confounder.
#   - Use the UNBLOCKED null only when no such confounder exists.
# If in doubt, ask: "Would I be fooled by ecological sorting?" If your
# groups cluster in space/teams/departments, block on that variable.


# 6. Learning Check ##########################################################
#
# QUESTION: What is the *block-permuted* p-value for assortativity by
# `demo`? (Use neighborhood as the block. 500 permutations.) Report
# to 3 decimal places.

print(f"\n📝 Learning Check answer: {p_blocked:.3f}")

print("\n🎉 Done. Move on to the case study report when you're ready.")
