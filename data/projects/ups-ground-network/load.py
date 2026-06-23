"""Load the `ups-ground-network` project network (Python).

Reads the two CSVs in this folder and builds a directed, weighted python-igraph
object: a UPS-style ground line-haul network of large trucks moving parcels
between package plants (centers -> regional hubs -> national gateways). Run it
straight (``python load.py``) for a quick summary, or import ``load_ups()`` into
your own script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per plant (gateway / hub / center)."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per source-plant -> destination-plant lane."""
    return pd.read_csv(HERE / "edges.csv")


def load_ups(nodes: pd.DataFrame | None = None,
             edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the directed, weighted graph (edge weight = ``packages``).

    Lanes flow from the origin plant to the destination plant and also carry
    ``trucks``, ``distance_km``, and ``transit_hours``. Delete a vertex to test
    how much flow it carries, or use ``g.distances()`` to see how reroutes
    lengthen transit time after a disruption.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=True, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["packages"]
    return g


if __name__ == "__main__":
    print("\n🚛 ups-ground-network (Python)")
    print("   Centers -> regional hubs -> national gateways; "
          "lanes weighted by packages, with trucks / distance / transit time.\n")

    nodes = load_nodes()
    edges = load_edges()
    g = load_ups(nodes, edges)

    kinds = nodes["kind"].value_counts()
    print(f"✅ Loaded {len(nodes)} nodes "
          f"({kinds.get('gateway',0)} gateway, {kinds.get('hub',0)} hub, "
          f"{kinds.get('center',0)} center) and {len(edges)} lanes.")
    print(f"🔗 Directed: {g.is_directed()} | total packages/day: "
          f"{edges['packages'].sum():,} on {edges['trucks'].sum():,} trucks | "
          f"mean lane: {edges['distance_km'].mean():.0f} km, "
          f"{edges['transit_hours'].mean():.1f} h")
    print("🎉 Graph ready. Object `g` is a directed, weighted igraph "
          "(weight = packages).")
