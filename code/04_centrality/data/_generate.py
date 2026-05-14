"""Generate the synthetic planted-bridge network for case 04.

We want a graph where degree-centrality and betweenness-centrality
disagree on which nodes matter. The trick: build several dense
clusters, then connect them with a small number of bridge nodes. The
bridge nodes have low degree but high betweenness — exactly the
pattern the case study wants to expose.

Structure:
  - 6 communities of ~80 nodes each (480 transit stops)
  - within-community: Erdos-Renyi p ~ 0.05 (dense-ish)
  - cross-community: a handful of "bridge" nodes, each connected to
    1-3 nodes in TWO communities (so traffic between communities
    must pass through them)
  - 20 extra bridge nodes
  -> ~500 nodes total, ~1500 weighted edges

Edge weight = ridership (Poisson-distributed integer).

Run:
    python code/04_centrality/data/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent
SEED = 42

def main() -> None:
    rng = np.random.default_rng(SEED)

    n_communities = 6
    nodes_per_community = 80
    p_intra = 0.05
    n_bridges = 20

    nodes = []
    edges = []

    # build communities
    for c in range(n_communities):
        start = c * nodes_per_community
        for i in range(nodes_per_community):
            nid = f"N{start + i:04d}"
            nodes.append({"node_id": nid, "community": c, "kind": "regular"})
        # within-community edges
        for i in range(nodes_per_community):
            for j in range(i + 1, nodes_per_community):
                if rng.random() < p_intra:
                    u = f"N{start + i:04d}"
                    v = f"N{start + j:04d}"
                    edges.append({"from": u, "to": v,
                                  "weight": int(rng.poisson(lam=80) + 5)})

    # bridges
    n_total_before = n_communities * nodes_per_community
    for b in range(n_bridges):
        bid = f"B{b:03d}"
        # bridge connects 2 distinct communities
        ca, cb = rng.choice(n_communities, size=2, replace=False)
        nodes.append({"node_id": bid, "community": -1, "kind": "bridge"})
        # bridge links to a few nodes in each community
        for c in [ca, cb]:
            start = c * nodes_per_community
            n_links = int(rng.integers(1, 4))
            picks = rng.choice(nodes_per_community, size=n_links, replace=False)
            for p in picks:
                edges.append({
                    "from": bid,
                    "to":   f"N{start + p:04d}",
                    # bridges carry less ridership in this fake world
                    "weight": int(rng.poisson(lam=30) + 5),
                })

    nodes_df = pd.DataFrame(nodes).sort_values("node_id").reset_index(drop=True)
    edges_df = pd.DataFrame(edges).sort_values(["from", "to"]).reset_index(drop=True)

    # make sure the graph is connected. If not, add a small spanning
    # path between any disconnected components.
    g = ig.Graph.DataFrame(
        edges=edges_df[["from", "to"]],
        directed=False,
        vertices=nodes_df[["node_id"]],
        use_vids=False,
    )
    comps = list(g.connected_components())
    if len(comps) > 1:
        # connect each component to component 0 via the first vertex
        v0 = comps[0][0]
        for comp in comps[1:]:
            v1 = comp[0]
            edges_df.loc[len(edges_df)] = {
                "from":   g.vs[v0]["name"],
                "to":     g.vs[v1]["name"],
                "weight": int(rng.poisson(lam=30) + 5),
            }

    nodes_df.to_csv(HERE / "nodes.csv", index=False)
    edges_df.to_csv(HERE / "edges.csv", index=False)

    print(f"wrote {HERE / 'nodes.csv'}  ({len(nodes_df)} nodes)")
    print(f"wrote {HERE / 'edges.csv'}  ({len(edges_df)} edges)")


if __name__ == "__main__":
    main()
