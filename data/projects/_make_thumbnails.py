"""Render a small preview thumbnail (thumb.png) for each project dataset.

Deterministic and self-contained. For each data/projects/<name>/ folder it loads
nodes.csv + edges.csv, lays the graph out (real x/y when present, else a
seeded spring layout), colors nodes by the first categorical attribute it finds
(kind / operator / subsystem / district / type), and writes a compact PNG that
matches the course's dark-green aesthetic. Parallel edges (temporal/multiplex)
are collapsed for the drawing only.

Run after (re)generating datasets:
    python data/projects/_make_thumbnails.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import networkx as nx

PROJECTS = Path(__file__).resolve().parent
SEED = 42
BG = "#08160c"
EDGE = "#39FF14"
PALETTE = ["#39FF14", "#38bdf8", "#fbbf24", "#f472b6", "#a78bfa",
           "#fb923c", "#86efac", "#e879f9", "#facc15", "#2dd4bf"]
CAT_COLS = ["operator", "subsystem", "type", "district", "ecosystem_area",
            "dept", "kind", "region", "neighborhood", "system"]


def _positions(nodes: pd.DataFrame, edges: pd.DataFrame, ids: list) -> dict:
    """Real coordinates if the node table has usable x/y, else seeded spring."""
    if {"x", "y"}.issubset(nodes.columns) and nodes[["x", "y"]].notna().all(axis=1).mean() > 0.9:
        return {r.node_id: (float(r.x), float(r.y)) for r in nodes.itertuples()}
    g = nx.Graph()
    g.add_nodes_from(ids)
    g.add_edges_from(edges.iloc[:, :2].itertuples(index=False, name=None))
    return nx.spring_layout(g, seed=SEED, k=1.0 / np.sqrt(max(len(ids), 1)))


def _make(ds: Path) -> None:
    nodes = pd.read_csv(ds / "nodes.csv")
    edges = pd.read_csv(ds / "edges.csv")
    ids = nodes["node_id"].tolist()
    pos = _positions(nodes, edges, ids)

    # color by the first categorical attribute available
    cat = next((c for c in CAT_COLS if c in nodes.columns and nodes[c].nunique() > 1), None)
    if cat:
        cats = sorted(map(str, nodes[cat].fillna("·").unique()))
        cmap = {c: PALETTE[i % len(PALETTE)] for i, c in enumerate(cats)}
        ncolors = [cmap[str(v) if pd.notna(v) else "·"] for v in nodes[cat]]
    else:
        ncolors = [EDGE] * len(nodes)

    # node size scales gently with degree
    deg = pd.Series(0, index=ids)
    vc = pd.concat([edges.iloc[:, 0], edges.iloc[:, 1]]).value_counts()
    deg = deg.add(vc, fill_value=0).reindex(ids).fillna(0)
    dmax = max(deg.max(), 1)
    sizes = 4 + 26 * (deg.values / dmax)

    # collapse parallel edges for drawing
    segs = []
    seen = set()
    for u, v in edges.iloc[:, :2].itertuples(index=False, name=None):
        key = (u, v) if str(u) <= str(v) else (v, u)
        if key in seen or u not in pos or v not in pos:
            continue
        seen.add(key)
        segs.append([pos[u], pos[v]])

    fig, ax = plt.subplots(figsize=(6.4, 4.2), dpi=100)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.add_collection(LineCollection(segs, colors=EDGE, linewidths=0.35, alpha=0.16, zorder=1))
    xs = [pos[i][0] for i in ids if i in pos]
    ys = [pos[i][1] for i in ids if i in pos]
    ax.scatter(xs, ys, s=sizes, c=ncolors, edgecolors="none", alpha=0.95, zorder=2)
    ax.set_title(f"{ds.name}  ·  {len(nodes)} nodes / {len(edges)} edges",
                 color="#d1fae5", fontsize=10, fontfamily="monospace", pad=8)
    ax.axis("off")
    ax.margins(0.04)
    fig.tight_layout()
    fig.savefig(ds / "thumb.png", facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    print(f"  {ds.name}/thumb.png  ({len(nodes)} nodes, {len(edges)} edges, color={cat or 'none'})")


def main() -> None:
    for ds in sorted(p for p in PROJECTS.iterdir() if p.is_dir()):
        if (ds / "nodes.csv").exists() and (ds / "edges.csv").exists():
            _make(ds)


if __name__ == "__main__":
    main()
