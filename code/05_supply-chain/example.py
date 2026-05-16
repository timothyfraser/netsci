"""Case Study 05 — Supply Chain Resilience (Python track).

The interactive lab let you click nodes to "fail" them and watched
supply coverage collapse. Here we do the same in code, on a synthetic
580-node 3-tier supply chain.

The resilience metric: SUPPLY COVERAGE = fraction of retailers
(tier 3) still reachable from at least one supplier (tier 1) after
the removals. 1.00 = nothing broken. 0.50 = half of all retailers
have lost their last incoming path from a supplier.

The point of this case: random failures, high-degree failures, and
high-betweenness failures cause DIFFERENT amounts of damage.
"""

# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `igraph` for graph + centrality, `pandas`/`numpy` to keep the
# per-strategy attack results tidy and easy to plot.
import pandas as pd
import numpy as np
import igraph as ig
import matplotlib.pyplot as plt

## 0.2 Load helpers ##########################################################

# `supply_coverage()` and `remove_and_score()` live in functions.py.
# They compute the % of retailers still reachable from any supplier,
# before and after a list of victims is deleted.
from functions import (
    load_nodes, load_edges, build_graph,
    supply_coverage, remove_and_score,
)

print("\n🚀 Case Study 05 — Supply Chain Resilience (Python)")
print("   Three attack strategies on a 580-node 3-tier chain. Which one hurts most?\n")

## 0.3 Load data #############################################################

nodes = load_nodes()
edges = load_edges()
# Tier composition: tier 1 = suppliers, tier 2 = DCs, tier 3 = retailers
print(nodes["tier"].value_counts().sort_index())

g = build_graph(nodes, edges)
print(g.summary())
n1 = int((nodes['tier'] == 1).sum())
n2 = int((nodes['tier'] == 2).sum())
n3 = int((nodes['tier'] == 3).sum())
print(f"✅ Loaded chain: {g.vcount()} nodes ({n1} suppliers, {n2} DCs, {n3} retailers).")


# 1. Baseline supply coverage ################################################
#
# Before we break anything, what fraction of retailers are reachable
# from at least one supplier? That's our denominator.

base = supply_coverage(g)
print(f"📊 Baseline supply coverage: {base:.3f}")


# 2. Centrality per tier #####################################################
#
# To target the right nodes we need per-node centrality. For a
# directed network we use both weighted degree (capacity) and
# betweenness. We hold these in a tidy table so the attack loop
# below stays one-liner-clean.

cent = pd.DataFrame({
    "node_id":     g.vs["name"],
    "tier":        g.vs["tier"],
    "in_degree":   g.degree(mode="in"),
    "out_degree":  g.degree(mode="out"),
    "w_in":        g.strength(mode="in",  weights="capacity"),
    "w_out":       g.strength(mode="out", weights="capacity"),
    "betweenness": g.betweenness(directed=True),
})

# Most-critical DC by betweenness. These are the candidates an attacker
# would target if they understood the network structure.
print(
    cent.query("tier == 2").sort_values("betweenness", ascending=False).head(5)
)


# 3. Targeted vs random attacks ##############################################
#
# We remove k nodes from tier 2 (DCs) under three strategies:
#   - random
#   - top-k by out-degree (volume hubs)
#   - top-k by betweenness (bridges)
# and track supply coverage as k grows from 0 to 15.

dcs = cent.query("tier == 2").copy()
rng = np.random.default_rng(42)

def run_strategy(strategy: str, ks: list[int]) -> list[float]:
    out = []
    for k in ks:
        if k == 0:
            out.append(base)
            continue
        if strategy == "random":
            victims = rng.choice(dcs["node_id"].to_numpy(), size=k, replace=False)
        elif strategy == "out_degree":
            victims = dcs.sort_values("out_degree", ascending=False).head(k)["node_id"]
        elif strategy == "betweenness":
            victims = dcs.sort_values("betweenness", ascending=False).head(k)["node_id"]
        else:
            raise ValueError(strategy)
        out.append(remove_and_score(g, victims))
    return out

ks = list(range(0, 16))
results = pd.DataFrame({
    "k":            ks,
    "random":       run_strategy("random", ks),
    "out_degree":   run_strategy("out_degree", ks),
    "betweenness":  run_strategy("betweenness", ks),
})

print(results.round(3))
row10 = results.loc[results["k"] == 10].iloc[0]
print(f"🧪 At k=10: random={row10['random']:.3f}  out_degree={row10['out_degree']:.3f}"
      f"  betweenness={row10['betweenness']:.3f}")


# 4. Visualize ###############################################################

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.plot(results["k"], results["random"],      marker="o", label="random DCs")
ax.plot(results["k"], results["out_degree"],  marker="s", label="top-k by out-degree")
ax.plot(results["k"], results["betweenness"], marker="^", label="top-k by betweenness")
ax.set_xlabel("# of distribution centers removed (k)")
ax.set_ylabel("supply coverage (fraction of retailers reachable)")
ax.set_title("Targeted vs random DC failures")
ax.set_ylim(0, 1.02)
ax.legend()
fig.tight_layout()
fig.savefig("supply_attack_curve.png", dpi=120)
plt.close(fig)
print("💾 Saved supply_attack_curve.png")


# 5. Learning Check ##########################################################
#
# QUESTION: After removing the 5 highest-betweenness distribution
# centers, what is the supply coverage of this network? Report to 3
# decimal places.

top5_btwn = dcs.sort_values("betweenness", ascending=False).head(5)["node_id"]
answer = remove_and_score(g, top5_btwn)

print(f"\n📝 Learning Check answer: {answer:.3f}")

print("\n🎉 Done. Move on to the case study report when you're ready.")
