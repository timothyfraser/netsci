#!/usr/bin/env python3
"""
build_sample_report_figures.py — generate the two figures embedded in the
project sample report (docs/assignments/sample-report.md).

Outputs (committed, served by the site, embedded in the PDF):
  docs/assignments/sample-report-fig1.png   bar chart — routing damage by strategy
  docs/assignments/sample-report-fig2.png   network — the cross-river bridge cut

These are *illustrative* graphics for an exemplar report; the numbers mirror the
report's Table 1. Deterministic (fixed seed). Needs matplotlib + networkx + numpy.

Run:  python3 scripts/build_sample_report_figures.py
"""

from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import networkx as nx

OUT = Path(__file__).resolve().parent.parent / "docs" / "assignments"

# course palette (print-friendly)
GREEN_DARK = "#166534"
GREEN = "#22C55E"
GREEN_LINE = "#16a34a"
AMBER = "#d97706"
AMBER_FILL = "#fbbf24"
GREY = "#94a3b8"
GREY_LIGHT = "#cbd5e1"
INK = "#1f2937"
RIVER = "#bfdbfe"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.edgecolor": "#334155",
    "text.color": INK,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
})


# ---------------------------------------------------------------------------
# Figure 1 — bar chart of routing damage by removal strategy (mirrors Table 1)
# ---------------------------------------------------------------------------
def figure_one():
    labels = ["Intact\nnetwork", "Random 10", "Top-10\nby degree",
              "Top-10 by\nbetweenness"]
    asp = [4.12, 4.15, 4.34, 6.81]
    colors = [GREY, GREY, GREEN, AMBER_FILL]
    edges = ["#64748b", "#64748b", GREEN_DARK, AMBER]

    fig, ax = plt.subplots(figsize=(6.6, 3.7))
    x = np.arange(len(labels))
    bars = ax.bar(x, asp, width=0.62, color=colors, edgecolor=edges, linewidth=1.4, zorder=3)

    # baseline reference line at the intact level
    ax.axhline(asp[0], color="#94a3b8", lw=1, ls=(0, (4, 3)), zorder=1)
    ax.text(3.45, asp[0] + 0.06, "intact baseline", ha="right", va="bottom",
            fontsize=8.5, color="#64748b")

    # value labels
    for xi, v in zip(x, asp):
        ax.text(xi, v + 0.12, f"{v:.2f}", ha="center", va="bottom",
                fontsize=10, fontweight="bold", color=INK)

    # callout on the betweenness bar
    ax.annotate("+65% routing distance\nlargest component 437 → 402",
                xy=(3, 6.81), xytext=(2.15, 6.55),
                fontsize=9, color=AMBER, fontweight="bold", ha="center",
                arrowprops=dict(arrowstyle="-|>", color=AMBER, lw=1.4))

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9.5)
    ax.set_ylabel("Average shortest path (steps)")
    ax.set_ylim(0, 7.7)
    ax.set_title("Routing damage by removal strategy", fontsize=12.5,
                 fontweight="bold", pad=10, loc="left")
    ax.yaxis.grid(True, color="#e2e8f0", lw=0.9, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    fig.tight_layout()
    fig.savefig(OUT / "sample-report-fig1.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 2 — the cross-river network and the bridge cut (before / after)
# ---------------------------------------------------------------------------
def _build_network():
    """Two geographic clusters (Cambridge / Boston) joined only by bridges."""
    rng = np.random.default_rng(5470)
    G = nx.Graph()
    pos = {}

    def blob(prefix, cx, cy, n, spread=0.62):
        ids = []
        for i in range(n):
            nid = f"{prefix}{i}"
            px = cx + rng.normal(0, spread)
            # keep clusters off the river channel (|x| > 0.7)
            if prefix == "C":
                px = min(px, -0.75)
            else:
                px = max(px, 0.75)
            py = cy + rng.normal(0, 0.85)
            pos[nid] = (px, py)
            G.add_node(nid)
            ids.append(nid)
        return ids

    cambridge = blob("C", -1.7, 0.0, 34)
    boston = blob("B", 1.7, 0.0, 34)

    # intra-cluster edges by proximity (geometric)
    def connect(ids, r):
        P = np.array([pos[i] for i in ids])
        for a in range(len(ids)):
            d = np.hypot(P[:, 0] - P[a, 0], P[:, 1] - P[a, 1])
            for b in np.argsort(d)[1:4]:        # ~3 nearest neighbours
                if d[b] < r:
                    G.add_edge(ids[a], ids[b])
    def force_connect(ids):
        """Guarantee the cluster is one connected component (MST-style stitch)."""
        comps = list(nx.connected_components(G.subgraph(ids)))
        while len(comps) > 1:
            c0 = list(comps[0])
            rest = list(set(ids) - set(comps[0]))
            best, bestd = None, 1e9
            for a in c0:
                for b in rest:
                    d = np.hypot(pos[a][0] - pos[b][0], pos[a][1] - pos[b][1])
                    if d < bestd:
                        bestd, best = d, (a, b)
            G.add_edge(*best)
            comps = list(nx.connected_components(G.subgraph(ids)))

    connect(cambridge, 1.1)
    connect(boston, 1.1)
    force_connect(cambridge)
    force_connect(boston)

    # two bridge stations spanning the river: b1 central (short crossing),
    # b2 north (long detour)
    pos["b1"] = (0.0, -0.2); G.add_node("b1")
    pos["b2"] = (0.0, 2.4);  G.add_node("b2")

    def nearest(ids, point, k):
        P = np.array([pos[i] for i in ids])
        d = np.hypot(P[:, 0] - point[0], P[:, 1] - point[1])
        return [ids[i] for i in np.argsort(d)[:k]]

    for nb in nearest(cambridge, pos["b1"], 3) + nearest(boston, pos["b1"], 3):
        G.add_edge("b1", nb)
    for nb in nearest(cambridge, pos["b2"], 2) + nearest(boston, pos["b2"], 2):
        G.add_edge("b2", nb)

    # a small pocket that reaches the rest ONLY through b1 -> stranded when cut
    pocket = []
    for i in range(3):
        nid = f"P{i}"
        pos[nid] = (-0.15 + rng.normal(0, 0.12), -0.9 - 0.32 * i)
        G.add_node(nid); pocket.append(nid)
    G.add_edge("b1", "P0"); G.add_edge("P0", "P1"); G.add_edge("P1", "P2")

    return G, pos, cambridge, boston, pocket


def _draw(ax, G, pos, path_edges, removed, stranded, title):
    # river channel
    ax.axvspan(-0.7, 0.7, color=RIVER, alpha=0.55, zorder=0)
    ax.text(0.0, -3.15, "Charles River", ha="center", va="center",
            fontsize=8.5, style="italic", color="#3b82f6", zorder=1)

    pe = set(map(frozenset, path_edges))
    for u, v in G.edges():
        if u in removed or v in removed:
            continue
        on_path = frozenset((u, v)) in pe
        ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]],
                color=(GREEN_LINE if on_path else "#cbd5e1"),
                lw=(2.8 if on_path else 0.9),
                zorder=(4 if on_path else 2), solid_capstyle="round")

    for n in G.nodes():
        x, y = pos[n]
        if n in removed:
            ax.scatter(x, y, s=200, marker="X", color=AMBER, edgecolor="#7c2d12",
                       linewidths=1.4, zorder=6)
            continue
        if n in ("b1", "b2"):
            ax.scatter(x, y, s=110, color=AMBER_FILL, edgecolor=AMBER,
                       linewidths=1.6, zorder=5)
        elif n in stranded:
            ax.scatter(x, y, s=34, color=GREY_LIGHT, edgecolor="#94a3b8",
                       linewidths=0.6, zorder=3)
        else:
            ax.scatter(x, y, s=34, color=GREEN, edgecolor=GREEN_DARK,
                       linewidths=0.6, zorder=3)

    # removed nodes are no longer in G, so draw them from stored positions
    for n in removed:
        x, y = pos[n]
        ax.scatter(x, y, s=210, marker="X", color=AMBER, edgecolor="#7c2d12",
                   linewidths=1.5, zorder=7)
        ax.annotate("closed", xy=(x, y), xytext=(x + 0.05, y - 0.7),
                    ha="center", fontsize=8.5, color="#7c2d12", fontweight="bold")

    ax.set_title(title, fontsize=10.5, fontweight="bold", pad=8, loc="center")
    ax.set_xlim(-3.4, 3.4); ax.set_ylim(-3.4, 3.4)
    ax.set_aspect("equal"); ax.axis("off")


def figure_two():
    G, pos, camb, bost, pocket = _build_network()
    src = min(camb, key=lambda n: pos[n][1])      # deep south Cambridge
    dst = min(bost, key=lambda n: pos[n][1])       # deep south Boston

    before = nx.shortest_path(G, src, dst)
    before_edges = list(zip(before[:-1], before[1:]))

    G2 = G.copy(); G2.remove_node("b1")
    comp = nx.node_connected_component(G2, src)
    stranded = set(G2.nodes()) - comp                 # now unreachable from src
    try:
        after = nx.shortest_path(G2, src, dst)
        after_edges = list(zip(after[:-1], after[1:]))
    except nx.NetworkXNoPath:
        after_edges = []

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(7.6, 4.0))
    fig.subplots_adjust(wspace=0.10)
    _draw(axL, G, pos, before_edges, removed=set(), stranded=set(),
          title="Before: path crosses at the central bridge")
    _draw(axR, G2, pos, after_edges, removed={"b1"}, stranded=stranded,
          title="After: central bridge closed")

    # shared legend
    from matplotlib.lines import Line2D
    handles = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=GREEN,
               markeredgecolor=GREEN_DARK, markersize=8, label="station"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=AMBER_FILL,
               markeredgecolor=AMBER, markersize=10, label="bridge station (high betweenness)"),
        Line2D([0], [0], marker="x", color=AMBER, markersize=9, lw=0,
               markeredgewidth=2.4, label="closed station"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=GREY_LIGHT,
               markeredgecolor="#94a3b8", markersize=8, label="stranded (now unreachable)"),
        Line2D([0], [0], color=GREEN_LINE, lw=2.8, label="shortest path, Cambridge → Boston"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False,
               fontsize=8.6, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle("Closing one low-traffic bridge station reshapes the whole network",
                 fontsize=12.5, fontweight="bold", x=0.012, ha="left", y=1.02)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(OUT / "sample-report-fig2.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    figure_one()
    figure_two()
    print("✓ Wrote sample-report-fig1.png and sample-report-fig2.png to", OUT)
