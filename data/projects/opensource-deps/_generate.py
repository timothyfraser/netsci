"""Generate the `opensource-deps` project network (deterministic).

A package dependency graph for a fictional open-source ecosystem:
  - ~400 packages (kind = "package")
  - directed "depends on" edges (package -> the dependency it imports)
weighted by `import_count` (how many call sites use that dependency = how
heavily it is used).

Design parameters (the only record of the planted structure):
  - LEFTPAD: one tiny utility package has LOW direct in-degree relative to the
    big libraries, but a HUGE transitive in-degree (almost the whole ecosystem
    can reach it) -> the hidden critical supply-chain node.
  - ABANDONED: a package with very high downstream reach has months_since_update
    in the top decile AND maintainers == 1 (bus-factor risk on a critical node).
  - GOD_PKG: one package depends on an unusually large number of others (huge
    out-degree) -> fragile, breaks if any dependency breaks.
  - DIAMOND: a popular lower-level library exists as TWO version nodes (v1 / v2);
    many packages depend on one or the other -> a version-conflict hotspot.

Run:
    python data/projects/opensource-deps/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

N_PACKAGES = 400
AREAS = ["web", "data", "build", "test", "crypto"]

# --- planted parameters -----------------------------------------------------
N_FOUNDATION = 8       # a few low-level libraries everyone leans on
GOD_OUT_DEGREE = 55    # the "god package" depends on this many others (outlier)
DIAMOND_DEPENDENTS = 70  # how many packages point at each version of the diamond lib
LEFTPAD_DIRECT = 6     # the left-pad node's small DIRECT in-degree (looks minor)


def main() -> None:
    rng = np.random.default_rng(SEED)

    # ----- packages --------------------------------------------------------
    area = rng.choice(AREAS, size=N_PACKAGES, p=[0.34, 0.26, 0.16, 0.16, 0.08])
    node_id = np.array([f"pkg{i:03d}" for i in range(1, N_PACKAGES + 1)])

    # a "level" 0..3: lower levels are more foundational (depended on more).
    # foundation libs are level 0; leaves (apps) are level 3.
    level = rng.choice([0, 1, 2, 3], size=N_PACKAGES, p=[0.06, 0.24, 0.40, 0.30])

    # popularity (weekly downloads) is heavy-tailed and higher for low levels.
    base_pop = rng.lognormal(mean=9.0, sigma=1.6, size=N_PACKAGES)
    pop_mult = np.array([4.0, 2.2, 1.2, 0.7])[level]
    weekly_downloads = (base_pop * pop_mult).astype(int)

    maintainers = np.clip(rng.poisson(2.4, N_PACKAGES) + 1, 1, 18)
    months_since_update = np.clip(rng.gamma(2.0, 4.0, N_PACKAGES), 0, 60).round(1)

    labels = np.array([f"{a}-lib-{i:03d}" for i, a in zip(range(1, N_PACKAGES + 1), area)])

    # ----- pick the special nodes ------------------------------------------
    foundation = node_id[level == 0]
    # left-pad: a tiny utility, force it to look like a low-level helper but we
    # will route nearly everything through it transitively while keeping its
    # DIRECT in-degree small.
    leftpad = "pkg007"
    god_pkg = "pkg400"            # the god package (will get huge out-degree)
    # diamond: two version nodes of one popular library
    diamond_v1 = "pkg010"
    diamond_v2 = "pkg011"
    abandoned = "pkg015"         # high-reach + stale + single maintainer

    idx = {nid: i for i, nid in enumerate(node_id)}

    # force attributes for the planted nodes
    level[idx[leftpad]] = 0
    area[idx[leftpad]] = "build"
    maintainers[idx[leftpad]] = 2
    months_since_update[idx[leftpad]] = 7.0
    weekly_downloads[idx[leftpad]] = int(weekly_downloads.mean() * 0.6)  # modest!
    labels[idx[leftpad]] = "tiny-pad"

    level[idx[diamond_v1]] = 0
    level[idx[diamond_v2]] = 0
    area[idx[diamond_v1]] = "data"
    area[idx[diamond_v2]] = "data"
    labels[idx[diamond_v1]] = "coreutil-v1"
    labels[idx[diamond_v2]] = "coreutil-v2"
    weekly_downloads[idx[diamond_v1]] = int(weekly_downloads.mean() * 3.5)
    weekly_downloads[idx[diamond_v2]] = int(weekly_downloads.mean() * 3.0)

    level[idx[god_pkg]] = 3
    area[idx[god_pkg]] = "web"
    labels[idx[god_pkg]] = "kitchen-sink"

    # abandoned-but-critical: stale + single maintainer + (high reach engineered below)
    level[idx[abandoned]] = 0
    maintainers[idx[abandoned]] = 1
    months_since_update[idx[abandoned]] = 57.0
    area[idx[abandoned]] = "crypto"
    weekly_downloads[idx[abandoned]] = int(weekly_downloads.mean() * 2.0)
    labels[idx[abandoned]] = "oldcrypto"

    # ----- build dependency edges ------------------------------------------
    # General rule: a package depends mostly on packages at a LOWER level
    # (more foundational), a few at the same level, weighted by popularity.
    edges = {}   # (src,dst) -> import_count

    def add_edge(src, dst, w=None):
        if src == dst:
            return
        key = (src, dst)
        if w is None:
            w = int(np.clip(rng.gamma(2.0, 3.0), 1, 60))
        edges[key] = edges.get(key, 0) + w

    pop_norm = weekly_downloads / weekly_downloads.max()

    for i in range(N_PACKAGES):
        src = node_id[i]
        if src in (leftpad, god_pkg):
            continue   # handled specially
        lv = level[i]
        # number of direct dependencies grows with level (apps depend on more)
        n_deps = {0: rng.integers(0, 3), 1: rng.integers(1, 5),
                  2: rng.integers(2, 8), 3: rng.integers(3, 11)}[lv]
        # candidate targets: lower or equal level
        cand_mask = (level <= lv) & (node_id != src)
        cand = node_id[cand_mask]
        if len(cand) == 0:
            continue
        cand_pop = pop_norm[cand_mask] + 0.02
        w = cand_pop / cand_pop.sum()
        chosen = rng.choice(cand, size=min(n_deps, len(cand)), replace=False, p=w)
        for dst in chosen:
            add_edge(src, str(dst))

    # ----- LEFT-PAD: keep direct in-degree small, transitive in-degree huge --
    # Strategy: make the FOUNDATION libraries (which everything reaches) all
    # depend on left-pad. So anyone who depends on a foundation lib transitively
    # reaches left-pad, but left-pad's own direct dependents are just the few
    # foundation libs + a handful -> small direct in-degree.
    foundation_deps = [f for f in foundation if f not in (leftpad,)]
    # pick a small set of direct dependents = the foundation libs (a handful)
    direct_dependents = list(rng.choice(foundation_deps,
                                        size=min(LEFTPAD_DIRECT, len(foundation_deps)),
                                        replace=False))
    for d in direct_dependents:
        add_edge(str(d), leftpad, w=int(rng.integers(2, 8)))
    # ensure the diamond version libs (which sit at the top of reachability) also
    # depend on left-pad, so left-pad inherits all of THEIR ancestors too. This
    # pushes left-pad's TRANSITIVE in-degree above every other node while its
    # DIRECT in-degree stays small.
    for d in (diamond_v1, diamond_v2):
        add_edge(d, leftpad, w=int(rng.integers(2, 8)))
    # to make transitive reach huge, ensure MOST mid/high-level packages depend
    # (directly) on at least one of these foundation libs -> they all reach
    # left-pad through it.
    midhigh = node_id[level >= 1]
    for src in midhigh:
        if src in (leftpad, god_pkg):
            continue
        # 80% of mid/high packages get wired to a foundation lib (the conduit)
        if rng.random() < 0.80:
            dst = str(rng.choice(direct_dependents))
            add_edge(str(src), dst)

    # ----- GOD PACKAGE: depends on a huge number of others -----------------
    god_targets = rng.choice([n for n in node_id if n != god_pkg],
                             size=GOD_OUT_DEGREE, replace=False)
    for dst in god_targets:
        add_edge(god_pkg, str(dst))

    # ----- DIAMOND: two versions, each with many distinct dependents --------
    pool = [n for n in node_id if n not in (diamond_v1, diamond_v2, leftpad, god_pkg)]
    rng.shuffle(pool)
    v1_dependents = pool[:DIAMOND_DEPENDENTS]
    v2_dependents = pool[DIAMOND_DEPENDENTS:2 * DIAMOND_DEPENDENTS]
    for s in v1_dependents:
        add_edge(str(s), diamond_v1, w=int(rng.integers(1, 20)))
    for s in v2_dependents:
        add_edge(str(s), diamond_v2, w=int(rng.integers(1, 20)))

    # ----- ABANDONED-but-critical: give it high downstream reach -----------
    # make many mid-level libs depend on it so a large fraction reaches it.
    abandoned_direct = rng.choice([n for n in node_id[level >= 1]
                                   if n not in (abandoned, god_pkg)],
                                  size=45, replace=False)
    for s in abandoned_direct:
        add_edge(str(s), abandoned, w=int(rng.integers(1, 12)))

    # ----- guarantee LEFT-PAD tops transitive in-degree --------------------
    # Build the directed graph, find the few nodes with reach above left-pad, and
    # make THEM depend on left-pad: left-pad then inherits all their ancestors and
    # ends up with the single largest transitive in-degree, while its direct
    # in-degree stays an order of magnitude below the big libraries.
    import igraph as _ig
    _erows = [(s, d) for (s, d) in edges.keys()]
    _g = _ig.Graph(directed=True)
    _g.add_vertices(list(node_id))
    _g.add_edges([(s, d) for (s, d) in _erows])
    def _trans_in(graph, name):
        return len(graph.subcomponent(name, mode="in")) - 1
    lp_reach = _trans_in(_g, leftpad)
    # nodes whose reach >= left-pad's (excluding itself); make them depend on it
    above = []
    for nm in node_id:
        if nm == leftpad:
            continue
        if _trans_in(_g, nm) >= lp_reach:
            above.append(nm)
    for nm in above:
        add_edge(str(nm), leftpad, w=int(rng.integers(1, 5)))

    # ----- emit ------------------------------------------------------------
    edge_rows = [{"from_id": s, "to_id": d, "import_count": w}
                 for (s, d), w in edges.items()]
    edges_df = pd.DataFrame(edge_rows)

    nodes = pd.DataFrame({
        "node_id": node_id,
        "ecosystem_area": area,
        "maintainers": maintainers,
        "weekly_downloads": weekly_downloads,
        "months_since_update": months_since_update,
        "label": labels,
    })

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges_df.to_csv(HERE / "edges.csv", index=False)
    print(f"opensource-deps: {len(nodes)} packages, {len(edges_df)} dependency edges "
          f"(areas: {dict(pd.Series(area).value_counts())}).")


if __name__ == "__main__":
    main()
