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

# `pandas` for tidy data wrangling, `igraph` is the workhorse network
# library for both R and Python. `matplotlib` for the static figure
# (we save it to PNG so users without a display can still see it).
import pandas as pd
import numpy as np
import igraph as ig
import matplotlib.pyplot as plt

## 0.2 Load helpers ##########################################################

# `functions.py` sits next to this script. Open it once so you know
# what each loader is doing — they're tiny wrappers around `read_csv`.
from functions import load_nodes, load_edges, build_bipartite

# Friendly opening banner so you know the script is doing what it should.
print("\n🚀 Case Study 01 — Build a Network (Python)")
print("   Two CSVs in -> one bipartite igraph object out -> a supplier projection.\n")

## 0.3 Load data #############################################################

# Two tables: a node list (one row per entity) and an edge list (one row
# per "this supplier ships that component" relationship).
nodes = load_nodes()
edges = load_edges()

# Always glance at the first few rows of any table before trusting it.
print(nodes.head())
print(edges.head())

# How many of each kind of node? How many edges?
print(nodes["kind"].value_counts())
print(f"{len(edges):,} edges")

print(
    f"✅ Loaded {len(nodes)} nodes "
    f"({(nodes['kind']=='supplier').sum()} suppliers + "
    f"{(nodes['kind']=='component').sum()} components) and {len(edges)} edges."
)


# 1. Build the graph #########################################################
#
# A graph is just a set of vertices and a set of edges connecting them.
# Our data is already in that shape; we just need to hand the two
# tables to igraph and ask it to wire them up.

## 1.1 The naive way (suppliers and components mixed) ########################

# `build_bipartite()` (defined in functions.py) does two things:
#   (a) builds the graph from the edge list, and
#   (b) sets the bipartite `type` attribute on every vertex (False for
#       suppliers, True for components), which is what igraph needs to
#       know later that this graph is bipartite.
g = build_bipartite(nodes, edges)

# `summary()` gives a one-line dump: <number of vertices>, <number of
# edges>, directed flag, plus the attribute names.
print(g.summary())

## 1.2 Bipartite check #######################################################

# A quick sanity check that igraph agrees with our manual labeling.
is_bip, _types = g.is_bipartite(return_types=True)
print(f"✅ Bipartite? {is_bip}")


# 2. Inspect basic structure #################################################

## 2.1 Degree distribution by kind ###########################################

# Each node's degree is just "how many edges touch it." We bundle the
# three vertex attributes into one tidy DataFrame for easy summarizing.
degrees = pd.DataFrame({
    "node_id": g.vs["name"],
    "kind":    g.vs["kind"],
    "degree":  g.degree(),
})

# Suppliers tend to touch ~5-10 components; components are touched by
# anywhere from 1 to ~20 suppliers. Compare the two distributions.
print(degrees.groupby("kind")["degree"].describe())
sup_mean = degrees.loc[degrees["kind"] == "supplier",  "degree"].mean()
cmp_mean = degrees.loc[degrees["kind"] == "component", "degree"].mean()
print(f"📊 Mean supplier degree: {sup_mean:.1f}   Mean component degree: {cmp_mean:.1f}")

## 2.2 Top-degree components (the "shared" ones) #############################

# Which components have the most suppliers shipping them? These are
# the structural pivot points in a one-mode projection — when they
# go offline, many suppliers go offline together.
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
print(f"🔗 Supplier projection:  {proj_suppliers.vcount()} nodes, {proj_suppliers.ecount()} edges")
print(f"🔗 Component projection: {proj_components.vcount()} nodes, {proj_components.ecount()} edges")

# Each edge in the suppliers projection has a `weight` attribute equal
# to the NUMBER OF SHARED COMPONENTS between those two suppliers. That
# weight is the closest thing to a "shared-fate" score we get here.

## 3.1 Top supplier-supplier exposures #######################################

# Convert the projection back to a tidy edge-list so we can sort and
# explore it like any other DataFrame.
proj_edges = pd.DataFrame({
    "from": [proj_suppliers.vs[e.source]["name"] for e in proj_suppliers.es],
    "to":   [proj_suppliers.vs[e.target]["name"] for e in proj_suppliers.es],
    "shared_components": proj_suppliers.es["weight"],
})

# The top of this list is the pair of suppliers most exposed to each
# other — if one is disrupted, the other is most likely to be co-disrupted.
print(proj_edges.sort_values("shared_components", ascending=False).head(10))


# 4. Visualize ###############################################################
#
# A bipartite layout puts suppliers on one side, components on the
# other. It's not always the prettiest layout, but it's the most honest
# rendering of a bipartite graph: you can read off the structure
# without thinking about it.

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
print("💾 Saved build_bipartite.png")


# 5. Learning Check ##########################################################
#
# QUESTION: In the supplier-supplier projection (where two suppliers are
# linked if they share at least one component), what is the degree of
# supplier "S017"? Put differently: how many *other* suppliers share at
# least one component with S017?

s017_idx = proj_suppliers.vs.find(name="S017").index
answer = proj_suppliers.degree(s017_idx)

print(f"\n📝 Learning Check answer: {answer}")

print("\n🎉 Done. Move on to the case study report when you're ready.")
