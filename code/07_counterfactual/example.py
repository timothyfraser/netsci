"""Case Study 09 — Counterfactual Monte Carlo (Python track).

The lab walked you through this problem: you propose an intervention
in a network (add a station, add an edge, boost an edge's volume)
and want to know if it *actually* improves a metric, or if any
apparent improvement is within the noise.

The answer: bootstrap-style resampling. Re-draw edge weights from a
Poisson centered at observed values, R times, and look at the
distribution of your metric. Apply the intervention to each replicate
and compare distributions. The 95% CI on the difference tells you
whether the effect is real.

Why Poisson? Edge weights here are COUNTS (rides), and Poisson is the
natural noise model for counts: its variance equals its mean, and it
never goes negative the way a Normal draw could. Caveat worth knowing:
if your counts are overdispersed (variance > mean, common in real data),
Poisson understates uncertainty and a negative-binomial draw is better.

We use a 180-station synthetic bikeshare network. The metric is
weighted average path length (lower is better — fewer "hops" between
stations, weighted by ridership). The intervention is adding a new
direct edge between two stations that are currently far apart.
"""

# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `igraph` for distances + APL math. `pandas` for tidy result tables.
# `matplotlib` for the side-by-side distribution + difference plots.
import pandas as pd
import numpy as np
import igraph as ig
import matplotlib.pyplot as plt

## 0.2 Load helpers ##########################################################

# `weighted_apl()` computes the weighted average path length;
# `mc_apls()` runs R Poisson-resampled APL computations, optionally
# with an extra edge appended. Both live in functions.py.
from functions import (
    load_nodes, load_edges, build_graph, weighted_apl, mc_apls,
)

print("\n🚀 Case Study 09 — Counterfactual Monte Carlo (Python)")
print("   Add one edge to a bikeshare network. Does APL really improve?\n")

## 0.3 Load data #############################################################

nodes = load_nodes()
edges = load_edges()
g     = build_graph(nodes, edges)
print(g.summary())
print(f"✅ Loaded network: {g.vcount()} stations, {g.ecount()} edges.")


# 1. Baseline weighted APL ###################################################
#
# APL = average over all (i, j) of the shortest-path *cost* between
# i and j. Cost is 1/ridership, so a high-ridership edge counts as
# "short" — it's a "well-traveled" path between its endpoints.

base_apl = weighted_apl(g)
print(f"📊 Baseline weighted APL: {base_apl:.5f}")

# Quick overdispersion check before trusting Poisson. Poisson assumes
# variance == mean. If the ratio is ~1, Poisson is a fair noise model; if
# it's >> 1 the counts are overdispersed and Poisson understates
# uncertainty (a negative-binomial draw would be better).
vmr = float(np.var(edges["ridership"]) / np.mean(edges["ridership"]))
note = "≈1, Poisson is reasonable" if vmr < 1.5 else "overdispersed — consider negative binomial"
print(f"🧪 Edge-weight variance/mean ratio: {vmr:.2f}  ({note})")


# 2. Pick an intervention ####################################################
#
# Find two stations that are far apart in the current network. We'll
# propose adding a high-ridership (~120 rides) edge between them and
# see if that pulls the APL down meaningfully.

dists = np.array(g.distances(weights="cost"))
np.fill_diagonal(dists, -np.inf)
i, j = np.unravel_index(np.argmax(dists), dists.shape)
station_a = g.vs[i]["name"]
station_b = g.vs[j]["name"]
print(f"🔗 farthest-apart pair: {station_a} <-> {station_b}  (cost = {dists[i, j]:.4f})")

intervention = pd.DataFrame({
    "from":     [station_a],
    "to":       [station_b],
    "ridership":[120],  # the proposed connector has decent ridership
})


# 3. Monte Carlo: baseline vs counterfactual #################################
#
# For each of R = 500 replicates: Poisson-resample every edge's
# ridership around its observed value, rebuild the graph, and compute
# APL. Do this once WITHOUT the new edge (baseline) and once WITH it
# (counterfactual). The element-wise difference is the per-replicate
# treatment effect.

R = 500
baseline_apls       = mc_apls(edges, nodes, R=R, extra=None,         seed=1)
counterfactual_apls = mc_apls(edges, nodes, R=R, extra=intervention, seed=1)

diffs = counterfactual_apls - baseline_apls
ci_low, ci_high = np.quantile(diffs, [0.025, 0.975])

# Significance is not magnitude. A CI that misses zero says the effect is
# real, not that it's big. Always read the change against the baseline APL
# so a tiny absolute number (e.g. -0.001) becomes interpretable as a %.
base_mean = baseline_apls.mean()
print(f"📊 Baseline weighted APL:                {base_mean:.4f}")
print(f"🧪 Counterfactual APL change (mean):     {diffs.mean():+.5f}  "
      f"({100 * diffs.mean() / base_mean:+.2f}% of baseline)")
print(f"🧪 95% CI on the change:                 [{ci_low:+.5f}, {ci_high:+.5f}]")
sig = ci_high < 0 or ci_low > 0
print(f"📊 Effect significant at 95%?            {'True' if sig else 'False'}")

# What does the verdict MEAN? A CI that MISSES zero says the effect's
# direction is real (still read the magnitude separately). A CI that
# INCLUDES zero does NOT say "the intervention does nothing" — it says we
# can't distinguish the effect from zero with this many replicates. "We
# can't tell" is itself a finding: gather more data before committing.
if sig:
    print("ℹ️  Interpretation: CI misses zero — the change is directionally "
          "real (check size vs baseline).")
else:
    print("ℹ️  Interpretation: CI includes zero — can't distinguish from no "
          "effect (NOT proof of 'no effect').")


# 4. Visualize the two distributions and the difference ######################

fig, axes = plt.subplots(1, 2, figsize=(11, 4))

ax = axes[0]
ax.hist(baseline_apls,        bins=30, alpha=0.55, label="Baseline",         color="#3a8bc6")
ax.hist(counterfactual_apls, bins=30, alpha=0.55, label="With intervention", color="#e07b3a")
ax.set_xlabel("weighted APL")
ax.set_ylabel("# of replicates")
ax.legend()
ax.set_title("Two distributions, R=500 replicates")

ax = axes[1]
ax.hist(diffs, bins=30, color="#7b3ae0", alpha=0.7)
ax.axvline(0,        color="black", linestyle="--", linewidth=1)
ax.axvline(ci_low,   color="red",   linestyle=":",  linewidth=1)
ax.axvline(ci_high,  color="red",   linestyle=":",  linewidth=1)
ax.set_xlabel("APL change (counterfactual - baseline)")
ax.set_ylabel("# of replicates")
ax.set_title("Difference distribution + 95% CI")

fig.tight_layout()
fig.savefig("counterfactual_ci.png", dpi=120)
plt.close(fig)
print("💾 Saved counterfactual_ci.png")


# 5. Learning Check ##########################################################
#
# QUESTION: For the intervention "add a high-ridership (~120 rides)
# edge between the two currently-farthest-apart stations" on this
# 180-station network, what is the 95% CI on the change in weighted
# APL (counterfactual - baseline), with R=500 replicates and seed=1?
# Report the LOW end of the CI rounded to 4 decimal places (signed).

print(f"\n📝 Learning Check answer (CI low): {ci_low:.4f}")

print("\n🎉 Done. Move on to the case study report when you're ready.")
