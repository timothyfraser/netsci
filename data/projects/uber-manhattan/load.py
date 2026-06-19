"""Load the `uber-manhattan` project network (Python).

Reads the CSVs in this folder and builds a bipartite, weighted python-igraph
object: drivers on one side, riders on the other, edges are rides (weighted by
fare). Run it straight (``python load.py``) for a quick summary, or import
``load_uber()`` / ``load_zones()`` into your own script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: drivers + riders."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per ride."""
    return pd.read_csv(HERE / "edges.csv")


def load_zones() -> pd.DataFrame:
    """Zone lookup table (join onto pickup/dropoff/home zones)."""
    return pd.read_csv(HERE / "zones.csv")


def load_uber(nodes: pd.DataFrame | None = None,
              edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the bipartite, weighted graph (edge weight = ``fare``).

    The vertex attribute ``type`` is the bipartite flag: True for riders, False
    for drivers. Repeat rider-driver pairs stay as parallel edges; collapse with
    ``g.simplify(combine_edges={'weight': 'sum'})`` for one edge per pair.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=False, vertices=nodes, use_vids=False)
    g.vs["type"] = [k == "rider" for k in g.vs["kind"]]
    g.es["weight"] = g.es["fare"]
    return g


if __name__ == "__main__":
    print("\n🚕 uber-manhattan (Python)")
    print("   Bipartite drivers <-> riders; edges are rides weighted by fare.\n")

    nodes = load_nodes(); edges = load_edges(); g = load_uber(nodes, edges)
    kinds = nodes["kind"].value_counts()
    print(f"✅ Loaded {len(nodes)} nodes ({kinds.get('driver',0)} drivers + "
          f"{kinds.get('rider',0)} riders) and {len(edges)} rides.")
    print(f"🔗 Bipartite: {g.is_bipartite()} | total fares: "
          f"${edges['fare'].sum():,.0f} | total tips: ${edges['tip'].sum():,.0f}")
    print("🎉 Graph ready. `g` is bipartite (vs['type']: rider = True), weighted by fare.")
