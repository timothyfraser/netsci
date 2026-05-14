"""Case Study 01 — Build a Network (Python track).

You've used the interactive lab to drag nodes and draw edges. Now we
build a network from *real tables* and let the code do the rest.

Our data is a synthetic bipartite supply network:
  - 80 suppliers (nodes of kind "supplier")
  - 120 components (nodes of kind "component")
  - 577 ship-relationships (a supplier ships a component, weighted by volume)

The goal:

  1. Get the node table and the edge table into shape.
  2. Turn them into a real graph object.
  3. Inspect basic structure (sizes, degree distribution).
  4. Project the bipartite graph to a one-mode supplier-by-supplier graph
     (two suppliers connected if they share a component) — this is
     where bipartite networks earn their keep.
  5. Find supplier-level structural patterns.
"""

# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

import pandas as pd
import numpy as np
import igraph as ig
import matplotlib.pyplot as plt

## 0.2 Load helpers ##########################################################

from functions import load_nodes, load_edges, build_bipartite

## 0.3 Load data #############################################################

nodes = load_nodes()
edges = load_edges()

print(nodes.head())
print(edges.head())

# How many of each kind of node? How many edges?
print(nodes["kind"].value_counts())
print(f"{len(edges):,} edges")


# 1. Build the graph #########################################################
#
# A graph is just a set of vertices and a set of edges connecting them.
# The data is already in that shape; we just need to hand the two
# tables to igraph and ask it to wire them up.

## 1.1 The naive way (suppliers and components mixed) ########################

# We use functions.py's helper, which sets the bipartite `type`
# attribute for us.
g = build_bipartite(nodes, edges)
print(g.summary())

# `summary()` reports: <number of vertices> nodes, <number of edges>,
# directed=False, plus the attributes we attached.

## 1.2 Bipartite check #######################################################

# igraph has a quick test for whether our graph is bipartite, given
# the `type` attribute we set in the helper.
is_bip, _types = g.is_bipartite(return_types=True)
print("Is bipartite?", is_bip)


# 2. Inspect basic structure #################################################

## 2.1 Degree distribution by kind ###########################################

degrees = pd.DataFrame({
    "node_id": g.vs["name"],
    "kind":    g.vs["kind"],
    "degree":  g.degree(),
})

# Suppliers tend to touch ~5-10 components; components are touched by
# anywhere from 1 to ~20 suppliers. Look at the summary stats.
print(degrees.groupby("kind")["degree"].describe())

## 2.2 Top-degree components (the "shared" ones) #############################

# Which components have the most suppliers shipping them? These are
# the structural pivot points in a one-mode projection.
top_shared = (
    degrees.query("kind == 'component'")
    .sort_values("degree", ascending=False)
    .head(10)
)
print(top_shared)


# 3. Bipartite projection ####################################################
#
# The interesting question in a bipartite supply network usually isn't
# "which supplier ships which component" — it's "which suppliers are
# co-exposed because they share a component." If component C037 goes
# offline, every supplier that depends on it is in trouble together.
#
# A bipartite projection answers exactly that. It produces two graphs:
#   - supplier-by-supplier: two suppliers linked if they share >=1 component
#   - component-by-component: two components linked if they share >=1 supplier

proj_suppliers, proj_components = g.bipartite_projection()
print("Suppliers projection:",  proj_suppliers.summary())
print("Components projection:", proj_components.summary())

# Each edge in the suppliers projection has a `weight` attribute equal
# to the NUMBER OF SHARED COMPONENTS between those two suppliers. That
# weight is the closest thing to a "shared-fate" score.

## 3.1 Top supplier-supplier exposures #######################################

proj_edges = pd.DataFrame({
    "from": [proj_suppliers.vs[e.source]["name"] for e in proj_suppliers.es],
    "to":   [proj_suppliers.vs[e.target]["name"] for e in proj_suppliers.es],
    "shared_components": proj_suppliers.es["weight"],
})
print(proj_edges.sort_values("shared_components", ascending=False).head(10))


# 4. Visualize ###############################################################
#
# A bipartite layout puts suppliers on one side, components on the
# other. It's not always the prettiest, but it's the most honest
# rendering of a bipartite graph.

layout = g.layout_bipartite(types=g.vs["type"])
fig, ax = plt.subplots(figsize=(11, 7))
node_color = ["#1f77b4" if k == "supplier" else "#d62728" for k in g.vs["kind"]]
node_size  = [40 if k == "supplier" else 20 for k in g.vs["kind"]]
xs = [pt[0] for pt in layout.coords]
ys = [pt[1] for pt in layout.coords]
for e in g.es:
    x0, y0 = layout.coords[e.source]
    x1, y1 = layout.coords[e.target]
    ax.plot([x0, x1], [y0, y1], color="grey", alpha=0.15, linewidth=0.4)
ax.scatter(xs, ys, c=node_color, s=node_size, edgecolors="white", linewidths=0.3)
ax.set_axis_off()
ax.set_title("Bipartite supplier <-> component network")
fig.tight_layout()
fig.savefig("build_bipartite.png", dpi=120)
plt.close(fig)


# 5. Learning Check ##########################################################
#
# QUESTION: In the supplier-supplier projection (where two suppliers are
# linked if they share at least one component), what is the degree of
# supplier "S017"? Put differently: how many *other* suppliers share at
# least one component with S017?

s017_idx = proj_suppliers.vs.find(name="S017").index
answer = proj_suppliers.degree(s017_idx)
print("Learning Check answer:", answer)
