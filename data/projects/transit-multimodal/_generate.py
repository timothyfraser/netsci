"""Generate the `transit-multimodal` project network (deterministic).

A multimodal urban public-transit network for one hypothetical city.
  - ~160 NEIGHBORHOODS (nodes), placed on a 2D city layout with a CBD center
    and concentric outer rings.
Edges are transit links between neighborhoods, in TWO modes (a multiplex):
  - metro: fast, high-frequency, high-capacity, but only serves neighborhoods
    on the rail lines (radial spokes + an inner ring + a partial outer ring).
  - bus: a denser, slower, lower-capacity mesh that covers many more
    neighborhoods, plus feeder routes that bring outer areas to the nearest
    metro station.
The same neighborhood pair can carry BOTH a bus and a metro edge -> parallel
edges (the multiplex). A companion `lines.csv` lists each transit line/route.

Design parameters (the only record of the planted structure):
  - INCOME_PENALTY: job-access travel-time rises as neighborhood income FALLS,
    holding population and distance-to-CBD fixed. We force this by giving
    low-income peripheral areas metro=0 and only sparse, infrequent bus service,
    while planting a few WEALTHY low-population near-metro areas that are
    over-served. So income predicts access AFTER controlling for pop & distance.
  - DESERT_NODES: a planted set of HIGH-population, LOW-income, peripheral
    neighborhoods deliberately left off the metro with thin bus service ->
    bottom-decile closeness/accessibility despite high population (transit
    deserts that are NOT explained by demand).
  - MISSING_LINK: two large adjacent districts (EAST and SOUTH wedges) are NOT
    directly connected; every trip between them detours through the CBD. Adding
    ONE crosstown edge collapses shortest paths for that whole region (the
    counterfactual centerpiece). The single best edge to add is the EAST<->SOUTH
    crosstown link.
  - CBD_HUB: all radial metro lines meet at the CBD interchange -> very high
    betweenness (#1). Removing it sharply raises mean path length, BUT the metro
    ring lines provide partial redundancy so the network does not shatter.
  - MODE_GAP: at matched distance-to-CBD, metro-served neighborhoods get far
    shorter job-access times than bus-only ones.
  - JOBS: jobs concentrate in the CBD plus ONE secondary edge-city center
    (north-west). Peripheral bus-only areas have long job-access despite high
    population.

Run:
    python data/projects/transit-multimodal/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

# --- planted parameters -----------------------------------------------------
N_TARGET = 160              # target neighborhood count (final is close to this)
N_RADIAL = 6               # number of radial metro lines (spokes)
RING_RADIUS = 1.9          # radius of the inner metro ring line
OUTER_RING_RADIUS = 4.2    # radius of the partial outer metro ring
CITY_RADIUS = 6.0          # outer edge of the city
INCOME_PENALTY = 0.85      # how strongly low income thins out transit service
N_DESERTS = 9              # planted high-pop low-income transit deserts
N_OVERSERVED = 7           # planted low-pop wealthy over-served near-metro areas

# metro is fast & frequent; bus is slow & infrequent (per km factors)
METRO_TIME_PER_UNIT = 2.2   # min per layout-unit on metro
BUS_TIME_PER_UNIT = 5.6     # min per layout-unit on bus (much slower)
METRO_FREQ = (10, 24)       # trains/hr range
BUS_FREQ = (1.5, 12)        # buses/hr range (wide: low-income areas near 1.5)
METRO_CAP = (1200, 3000)    # riders/hr
BUS_CAP = (180, 700)        # riders/hr

# the two big districts that are NOT directly connected (the missing link)
WEDGE_EAST = "East"
WEDGE_SOUTH = "South"

DISTRICTS = ["CBD", "North", "NorthEast", "East", "SouthEast",
             "South", "SouthWest", "West", "NorthWest"]


def main() -> None:
    rng = np.random.default_rng(SEED)

    # ------------------------------------------------------------------ NODES
    # Place neighborhoods in concentric rings around a CBD at (0,0).
    # Ring 0 = CBD core; rings grow outward. Angle determines the district wedge.
    nodes_rows = []
    nid = 1

    def wedge_of(angle_deg: float) -> str:
        # 0 deg = East, increasing counter-clockwise.
        a = angle_deg % 360
        # 8 wedges of 45 deg, centered so "East"=0
        sectors = {
            0: "East", 45: "NorthEast", 90: "North", 135: "NorthWest",
            180: "West", 225: "SouthWest", 270: "South", 315: "SouthEast",
        }
        nearest = min(sectors, key=lambda s: min(abs(a - s), 360 - abs(a - s)))
        return sectors[nearest]

    # CBD core: a handful of central neighborhoods (the interchange district)
    n_cbd = 6
    for _ in range(n_cbd):
        r = rng.uniform(0.0, 0.55)
        th = rng.uniform(0, 2 * np.pi)
        x = r * np.cos(th)
        y = r * np.sin(th)
        nodes_rows.append({"px": x, "py": y, "district": "CBD"})

    # rings of neighborhoods outward
    ring_specs = [
        (1.0, 18),   # inner residential
        (1.9, 22),   # at inner ring radius
        (2.8, 26),
        (3.6, 28),
        (4.4, 28),
        (5.2, 24),
    ]
    for radius, count in ring_specs:
        for k in range(count):
            base_ang = (360.0 / count) * k
            ang = base_ang + rng.uniform(-8, 8)
            rr = radius + rng.uniform(-0.28, 0.28)
            th = np.deg2rad(ang)
            x = rr * np.cos(th)
            y = rr * np.sin(th)
            district = wedge_of(ang) if rr > 0.8 else "CBD"
            nodes_rows.append({"px": x, "py": y, "district": district})

    nodes = pd.DataFrame(nodes_rows)
    nodes = nodes.iloc[:N_TARGET].reset_index(drop=True)
    n = len(nodes)
    nodes["node_id"] = [f"N{i:03d}" for i in range(1, n + 1)]

    nodes["x"] = nodes["px"].round(3)
    nodes["y"] = nodes["py"].round(3)
    nodes["dist_cbd"] = np.hypot(nodes["px"], nodes["py"])

    # --- income: spatial gradient (rich near center & in the NW) + noise -----
    # wealth decreases outward overall, but NW wedge is affluent and parts of
    # the periphery vary; add noise so location does not perfectly reveal income.
    ang = np.rad2deg(np.arctan2(nodes["py"], nodes["px"])) % 360
    nw_bonus = np.exp(-((((ang - 135) + 180) % 360 - 180) ** 2) / (2 * 35 ** 2))
    base_income = (
        95000
        - 9000 * nodes["dist_cbd"]
        + 28000 * nw_bonus
        + rng.normal(0, 11000, n)
    )
    nodes["median_income"] = np.clip(base_income, 24000, 210000).round().astype(int)

    # --- population: outer rings hold more people; noise -------------------
    base_pop = (
        4500
        + 1300 * nodes["dist_cbd"]
        + rng.normal(0, 1500, n)
    )
    nodes["population"] = np.clip(base_pop, 800, 30000).round().astype(int)

    # --- jobs: concentrate in CBD + one secondary edge-city center (NW) -----
    # secondary center location
    sec_ang = np.deg2rad(135)
    sec_r = 3.4
    sec_x, sec_y = sec_r * np.cos(sec_ang), sec_r * np.sin(sec_ang)
    d_sec = np.hypot(nodes["px"] - sec_x, nodes["py"] - sec_y)
    jobs = (
        2200 * np.exp(-(nodes["dist_cbd"] ** 2) / (2 * 1.1 ** 2)) * 30   # CBD peak
        + 1400 * np.exp(-(d_sec ** 2) / (2 * 0.9 ** 2)) * 30            # edge city
        + 300
        + rng.normal(0, 600, n)
    )
    nodes["jobs"] = np.clip(jobs, 80, None).round().astype(int)

    pos = {r.node_id: (r.px, r.py) for r in nodes.itertuples()}
    ids = list(nodes.node_id)

    def dist(a: str, b: str) -> float:
        (ax, ay), (bx, by) = pos[a], pos[b]
        return float(np.hypot(ax - bx, ay - by))

    # ---------------------------------------------------- METRO LINE LAYOUT
    # Radial spokes: pick, for each of N_RADIAL angles, a chain of neighborhoods
    # marching outward (nearest to the ideal point at each radius step).
    metro_nodes: set[str] = set()
    metro_edges: list[dict] = []
    lines_rows: list[dict] = []

    # the CBD interchange node: the neighborhood closest to (0,0)
    cbd_hub = min(ids, key=lambda nd: nodes.loc[nodes.node_id == nd, "dist_cbd"].iloc[0])

    def nearest_free(target_xy, pool, used):
        cand = sorted(
            ((np.hypot(pos[p][0] - target_xy[0], pos[p][1] - target_xy[1]), p)
             for p in pool if p not in used),
            key=lambda t: (round(t[0], 6), t[1]),
        )
        return cand[0][1] if cand else None

    radial_angles = [(360.0 / N_RADIAL) * k for k in range(N_RADIAL)]
    radial_steps = [0.0, 1.0, 1.9, 2.8, 3.6, 4.4, 5.2]

    line_idx = 1
    for ang_deg in radial_angles:
        line_id = f"M{line_idx}"
        line_idx += 1
        th = np.deg2rad(ang_deg)
        chain = [cbd_hub]
        used_for_line = {cbd_hub}
        for step in radial_steps[1:]:
            tx, ty = step * np.cos(th), step * np.sin(th)
            # restrict to nodes roughly in this wedge & near this radius
            pool = [p for p in ids
                    if abs(nodes.loc[nodes.node_id == p, "dist_cbd"].iloc[0] - step) < 0.6]
            nd = nearest_free((tx, ty), pool, used_for_line)
            if nd is not None and nd != chain[-1]:
                chain.append(nd)
                used_for_line.add(nd)
        # build consecutive metro edges along the chain
        for a, b in zip(chain[:-1], chain[1:]):
            metro_nodes.update([a, b])
            metro_edges.append({"a": a, "b": b, "line": line_id})
        lines_rows.append({
            "line_id": line_id, "mode": "metro", "kind": "radial",
            "label": f"Metro Line {line_id}", "n_stations": len(chain),
        })

    # inner ring metro line: order the neighborhoods nearest RING_RADIUS by angle
    def ring_chain(radius: str, tol: float):
        ring_pool = [p for p in ids
                     if abs(nodes.loc[nodes.node_id == p, "dist_cbd"].iloc[0] - radius) < tol]
        ring_pool = sorted(
            ring_pool,
            key=lambda p: np.rad2deg(np.arctan2(pos[p][1], pos[p][0])) % 360,
        )
        return ring_pool

    inner_ring = ring_chain(RING_RADIUS, 0.5)
    for a, b in zip(inner_ring, inner_ring[1:] + inner_ring[:1]):  # close the loop
        metro_nodes.update([a, b])
        metro_edges.append({"a": a, "b": b, "line": "Ring"})
    lines_rows.append({
        "line_id": "Ring", "mode": "metro", "kind": "inner_ring",
        "label": "Inner Ring Line", "n_stations": len(inner_ring),
    })

    # PARTIAL outer ring metro line: an arc covering the WEST/NORTH side only,
    # deliberately leaving a GAP on the EAST<->SOUTH side (relevant to the
    # missing link, and giving partial-but-not-full ring redundancy).
    outer_ring_all = ring_chain(OUTER_RING_RADIUS, 0.7)
    # keep only nodes whose angle is in [60, 240] deg (covers N, NW, W, SW),
    # leaving East (0/315) and South (270) unconnected by the outer ring.
    def angle_of(p):
        return np.rad2deg(np.arctan2(pos[p][1], pos[p][0])) % 360
    outer_arc = [p for p in outer_ring_all if 60 <= angle_of(p) <= 240]
    outer_arc = sorted(outer_arc, key=angle_of)
    for a, b in zip(outer_arc[:-1], outer_arc[1:]):  # an OPEN arc (not closed)
        metro_nodes.update([a, b])
        metro_edges.append({"a": a, "b": b, "line": "OuterArc"})
    lines_rows.append({
        "line_id": "OuterArc", "mode": "metro", "kind": "outer_ring_partial",
        "label": "Outer Ring (partial)", "n_stations": len(outer_arc),
    })

    nodes["has_metro"] = nodes["node_id"].isin(metro_nodes).astype(int)

    # ----------------------------------------------- TRANSIT DESERTS / EQUITY
    # Plant high-pop, low-income, peripheral deserts: force metro=0 and mark them
    # for thin bus service. Choose peripheral (dist_cbd large) low-income nodes
    # that are currently bus-territory, biasing toward high population.
    periph = nodes[(nodes.dist_cbd > 3.0) & (nodes.has_metro == 0)].copy()
    # score: want HIGH pop and LOW income -> rank
    periph["desert_score"] = (
        (periph.population - periph.population.mean()) / periph.population.std()
        - (periph.median_income - periph.median_income.mean()) / periph.median_income.std()
    )
    desert_ids = list(
        periph.sort_values(["desert_score", "node_id"], ascending=[False, True])
        .head(N_DESERTS).node_id
    )
    nodes["is_desert_param"] = nodes["node_id"].isin(desert_ids).astype(int)
    # push deserts to be genuinely high-pop & low-income (strengthen the signal)
    for did in desert_ids:
        i = nodes.index[nodes.node_id == did][0]
        nodes.at[i, "population"] = int(min(30000, nodes.at[i, "population"] + 8000))
        nodes.at[i, "median_income"] = int(max(24000, nodes.at[i, "median_income"] - 14000))

    # Over-served wealthy low-pop near-metro nodes (for the equity contrast)
    near_metro = nodes[(nodes.has_metro == 1) & (nodes.dist_cbd > 1.2)].copy()
    near_metro["over_score"] = (
        (near_metro.median_income - near_metro.median_income.mean()) / near_metro.median_income.std()
        - (near_metro.population - near_metro.population.mean()) / near_metro.population.std()
    )
    overserved_ids = list(
        near_metro.sort_values(["over_score", "node_id"], ascending=[False, True])
        .head(N_OVERSERVED).node_id
    )
    nodes["is_overserved_param"] = nodes["node_id"].isin(overserved_ids).astype(int)
    for oid in overserved_ids:
        i = nodes.index[nodes.node_id == oid][0]
        nodes.at[i, "median_income"] = int(min(210000, nodes.at[i, "median_income"] + 18000))
        nodes.at[i, "population"] = int(max(800, nodes.at[i, "population"] - 2500))

    # ------------------------------------------------------------------- BUS
    # Dense mesh: connect spatially-adjacent neighborhoods (k nearest), with
    # service level scaled by income (low-income -> fewer buses) and deserts thin.
    bus_edges: list[dict] = []
    bus_keys: set[tuple[str, str]] = set()
    income_arr = nodes.set_index("node_id")["median_income"]
    inc_min, inc_max = income_arr.min(), income_arr.max()

    def inc_norm(p):
        return float((income_arr[p] - inc_min) / (inc_max - inc_min))

    desert_set = set(desert_ids)

    def k_nearest(node, k, pool=None):
        pool = pool or ids
        cand = sorted(
            ((dist(node, p), p) for p in pool if p != node),
            key=lambda t: (round(t[0], 6), t[1]),
        )
        return [p for _, p in cand[:k]]

    bus_route_idx = 1

    def add_bus(a, b, route_id):
        if a == b:
            return
        key = (a, b) if a < b else (b, a)
        if key in bus_keys:
            return
        bus_keys.add(key)
        d = dist(a, b)
        # service level: richer endpoints get more frequent service; deserts thin
        avg_inc = (inc_norm(a) + inc_norm(b)) / 2
        desert_factor = 0.40 if (a in desert_set or b in desert_set) else 1.0
        freq = BUS_FREQ[0] + (BUS_FREQ[1] - BUS_FREQ[0]) * (
            INCOME_PENALTY * avg_inc + (1 - INCOME_PENALTY) * rng.random()
        )
        freq = float(np.clip(freq * desert_factor, 1.5, BUS_FREQ[1]))
        cap = int(np.clip(
            rng.integers(*BUS_CAP) * (0.6 + 0.8 * avg_inc) * desert_factor,
            120, BUS_CAP[1]))
        # low-income routes are also slightly slower (older, more circuitous)
        slow = 1.0 + 0.30 * (1 - avg_inc) + (0.20 if desert_factor < 1 else 0.0)
        ttime = d * BUS_TIME_PER_UNIT * slow * rng.uniform(0.95, 1.20) + 1.5
        bus_edges.append({
            "a": key[0], "b": key[1], "line": route_id,
            "travel_time_min": round(ttime, 1),
            "frequency_per_hr": round(freq, 1),
            "capacity": cap,
        })

    # local mesh: each neighborhood to its nearest neighbors. Lower-income areas
    # get FEWER bus links (k smaller) -> thinner coverage, independent of pop.
    for p in ids:
        kbase = 4
        # income reduces connectivity: poorest get k=2, richest k=5
        k = int(round(2 + 3 * inc_norm(p)))
        if p in desert_set:
            k = 2
        k = max(2, min(5, k))
        for q in k_nearest(p, max(kbase, k))[:k]:
            add_bus(p, q, f"B{bus_route_idx:03d}")
            bus_route_idx += 1

    # FEEDER routes: every non-metro neighborhood gets a bus to its nearest metro
    # station (brings outer areas to the rail) -- but deserts get a LONG feeder
    # (their nearest metro is far) which we keep, modeling poor access.
    metro_list = sorted(metro_nodes)
    for p in ids:
        if p in metro_nodes:
            continue
        nearest_metro = min(metro_list, key=lambda m: (round(dist(p, m), 6), m))
        add_bus(p, nearest_metro, f"F{bus_route_idx:03d}")
        bus_route_idx += 1

    # ---- ensure the MISSING LINK: isolate the East wedge into a spoke-only ---
    # peninsula. We cut ALL bus links from East-wedge nodes to their two
    # neighbouring wedges (NorthEast and SouthEast), and keep the inner-ring and
    # outer-arc gaps on the East/South side. The result: every trip from East to
    # the South side of the city must detour inward down the East radial metro
    # spoke, through the CBD interchange, and back out -- a long way round.
    # Adding ONE crosstown edge (East <-> SouthEast/South) collapses that detour.
    dist_map = nodes.set_index("node_id")["dist_cbd"]
    district_map = nodes.set_index("node_id")["district"]
    ISOLATE = WEDGE_EAST
    NEIGHBORS = {"NorthEast", "SouthEast"}

    def crosses_cut(p, q):
        dp, dq = district_map[p], district_map[q]
        return (dp == ISOLATE and dq in NEIGHBORS) or (dq == ISOLATE and dp in NEIGHBORS)

    bus_edges = [e for e in bus_edges if not crosses_cut(e["a"], e["b"])]
    bus_keys = {(e["a"], e["b"]) for e in bus_edges}
    # the inner-ring metro must also not bridge East to its neighbours
    metro_edges = [e for e in metro_edges if not crosses_cut(e["a"], e["b"])]

    # repair: cutting cross-wedge links can orphan an East node. Reconnect any
    # now-isolated East node to its nearest East-wedge OR CBD neighbour (never
    # across the cut), so East stays a connected spoke-only peninsula.
    incident = set()
    for e in bus_edges:
        incident.update([e["a"], e["b"]])
    incident.update(metro_nodes)
    east_ids = [p for p in ids if district_map[p] == ISOLATE]
    inward_pool = [p for p in ids if district_map[p] in (ISOLATE, "CBD")]
    for p in east_ids:
        if p in incident:
            continue
        pool = [q for q in inward_pool if q != p]
        parent = min(pool, key=lambda q: (round(dist(p, q), 6), q))
        add_bus(p, parent, f"R{bus_route_idx:03d}")
        bus_route_idx += 1
        incident.add(p)
    bus_keys = {(e["a"], e["b"]) for e in bus_edges}

    # ----------------------------------------- BUILD METRO EDGE ATTRIBUTES
    metro_rows = []
    for e in metro_edges:
        a, b = e["a"], e["b"]
        d = dist(a, b)
        freq = float(rng.integers(*METRO_FREQ))
        cap = int(rng.integers(*METRO_CAP))
        ttime = d * METRO_TIME_PER_UNIT * rng.uniform(0.9, 1.1) + 0.8
        metro_rows.append({
            "from_id": a, "to_id": b, "mode": "metro", "line": e["line"],
            "travel_time_min": round(ttime, 1),
            "frequency_per_hr": round(freq, 1),
            "capacity": cap,
        })

    bus_rows = []
    for e in bus_edges:
        bus_rows.append({
            "from_id": e["a"], "to_id": e["b"], "mode": "bus", "line": e["line"],
            "travel_time_min": e["travel_time_min"],
            "frequency_per_hr": e["frequency_per_hr"],
            "capacity": e["capacity"],
        })

    edges = pd.DataFrame(metro_rows + bus_rows)

    # bus route lines lookup (collapse the many tiny route ids into the table)
    bus_line_ids = sorted({e["line"] for e in bus_edges})
    for lid in bus_line_ids:
        cnt = sum(1 for e in bus_edges if e["line"] == lid)
        lines_rows.append({
            "line_id": lid, "mode": "bus",
            "kind": "feeder" if lid.startswith("F") else "local",
            "label": f"Bus Route {lid}", "n_stations": cnt + 1,
        })
    lines = pd.DataFrame(lines_rows)

    # ------------------------------------------------------------- FINALIZE
    nodes["label"] = nodes["district"] + " " + nodes["node_id"].str[1:]
    out_nodes = nodes[[
        "node_id", "label", "district", "x", "y",
        "population", "median_income", "jobs", "has_metro",
    ]].copy()

    out_nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)
    lines.to_csv(HERE / "lines.csv", index=False)

    n_metro = int((edges["mode"] == "metro").sum())
    n_bus = int((edges["mode"] == "bus").sum())
    print(f"transit-multimodal: {len(out_nodes)} neighborhoods, "
          f"{len(edges)} edges ({n_metro} metro + {n_bus} bus), "
          f"{len(lines)} lines, {out_nodes.has_metro.sum()} metro-served nodes.")


if __name__ == "__main__":
    main()
