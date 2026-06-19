"""Generate the `airline-delays` project network (deterministic).

A domestic airline route network for a fictional carrier "Meridian Air" across
one operating day, sliced into four time blocks:
  - ~200 airport nodes (kind = "airport")
Edges are directed scheduled flights origin -> destination, one row per
(origin, destination, block), weighted by `number_of_flights`, each carrying an
average departure `delay_min` for that leg in that block.

Design parameters (the only record of the planted structure):
  - WX_HUB: one major hub suffers a weather event in the MIDDAY block; its
    outbound delay_min spikes that block and PROPAGATES downstream -- airports
    directly fed by it show elevated delay in the NEXT (afternoon) block
    (a measurable temporal lag), then it partially clears by evening.
  - RESILIENT_HUB: a second major hub absorbs/reroutes and shows little
    propagation, so hubs are not equally fragile.
  - CONNECTOR: a mid-size airport with few flights but high betweenness; it is
    the only bridge between two regional clusters, so removing it disconnects
    regional pairs more than removing a high-flight point-to-point airport.
  - DELAY_ALONG_EDGES: delay travels along routes, not by raw geography -- the
    propagation coupling is via the directed edges, with noise added so distance
    does not predict delay correlation.

Run:
    python data/projects/airline-delays/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

N_AIRPORTS = 200
BLOCKS = ["morning", "midday", "afternoon", "evening"]
REGIONS = ["Northeast", "Southeast", "Midwest", "West", "Mountain"]

# --- planted parameters -----------------------------------------------------
N_HUBS = 6                 # designated hubs (high degree)
WX_HUB_IDX = 0             # the fragile hub hit by weather at midday
RESILIENT_HUB_IDX = 1      # the hub that absorbs the shock
WX_DELAY_SPIKE = 58.0      # extra outbound delay (min) at WX hub during midday
PROPAGATE_FRAC = 0.62      # share of WX-hub outbound delay inherited next block
RESILIENT_ABSORB = 0.88    # resilient hub damps its own propagated delay
BASE_DELAY = 7.0           # baseline avg delay (min) on a normal leg
BLOCK_LOAD = {"morning": 0.9, "midday": 1.0, "afternoon": 1.15, "evening": 1.05}


def main() -> None:
    rng = np.random.default_rng(SEED)

    # ----- airport positions & regions -------------------------------------
    # Five regional clusters laid out across a 0-100 map, each a Gaussian blob.
    centers = {
        "Northeast": (82, 78),
        "Southeast": (74, 22),
        "Midwest":   (54, 60),
        "West":      (14, 50),
        "Mountain":  (34, 40),
    }
    region_of = rng.choice(REGIONS, size=N_AIRPORTS,
                           p=[0.22, 0.20, 0.22, 0.20, 0.16])
    xs = np.empty(N_AIRPORTS)
    ys = np.empty(N_AIRPORTS)
    for i in range(N_AIRPORTS):
        cx, cy = centers[region_of[i]]
        xs[i] = np.clip(cx + rng.normal(0, 9), 0, 100)
        ys[i] = np.clip(cy + rng.normal(0, 9), 0, 100)

    # ----- pick hubs & the connector ---------------------------------------
    # Hubs: one per region plus an extra, chosen as the most central within
    # their own region blob so they read as natural hubs.
    hub_idx = []
    for r in REGIONS:
        members = np.where(region_of == r)[0]
        cx, cy = centers[r]
        d = np.hypot(xs[members] - cx, ys[members] - cy)
        hub_idx.append(int(members[np.argmin(d)]))
    # one extra hub in the busiest region (Midwest)
    mid_members = np.where(region_of == "Midwest")[0]
    extra = int(mid_members[np.argsort(np.hypot(
        xs[mid_members] - centers["Midwest"][0],
        ys[mid_members] - centers["Midwest"][1]))[1]])
    hub_idx.append(extra)
    hub_idx = list(dict.fromkeys(hub_idx))[:N_HUBS]
    hub_set = set(hub_idx)

    wx_hub = hub_idx[WX_HUB_IDX]
    resilient_hub = hub_idx[RESILIENT_HUB_IDX]

    # The connector: a non-hub airport that we will MAKE the sole bridge between
    # two regions (West <-> Mountain). Pick a modest airport near the gap.
    west_members = np.where(region_of == "West")[0]
    # closest West airport to the Mountain center, but not a hub
    cand = [m for m in west_members if m not in hub_set]
    cand = sorted(cand, key=lambda m: np.hypot(
        xs[m] - centers["Mountain"][0], ys[m] - centers["Mountain"][1]))
    connector = int(cand[0])

    is_hub = np.zeros(N_AIRPORTS, dtype=int)
    for h in hub_idx:
        is_hub[h] = 1

    runways = np.where(is_hub == 1,
                       rng.integers(4, 7, N_AIRPORTS),
                       rng.integers(1, 4, N_AIRPORTS))
    # weather exposure: spatial gradient (more in the West/Mountain) + noise
    wx_grad = 0.30 + 0.004 * (100 - xs) + 0.002 * ys
    weather_exposure = np.clip(wx_grad + rng.normal(0, 0.08, N_AIRPORTS), 0.02, 0.98)

    codes = _airport_codes(N_AIRPORTS)
    nodes = pd.DataFrame({
        "node_id": codes,
        "kind": "airport",
        "label": [f"{codes[i]} Regional" if not is_hub[i] else f"{codes[i]} International"
                  for i in range(N_AIRPORTS)],
        "region": region_of,
        "hub": is_hub,
        "runways": runways,
        "weather_exposure": weather_exposure.round(3),
        "x": xs.round(2),
        "y": ys.round(2),
    })

    # ----- build the directed route topology -------------------------------
    # Routes: (a) hub-and-spoke within region, (b) hub-to-hub trunk routes,
    # (c) some point-to-point, (d) the connector as the ONLY West<->Mountain link.
    route_pairs: set[tuple[int, int]] = set()

    def add(a, b):
        if a != b:
            route_pairs.add((a, b))

    # (a) each non-hub connects to the 1-2 nearest hubs in its own region
    for i in range(N_AIRPORTS):
        if is_hub[i]:
            continue
        same = [h for h in hub_idx if region_of[h] == region_of[i]]
        if not same:
            same = hub_idx
        same = sorted(same, key=lambda h: np.hypot(xs[h] - xs[i], ys[h] - ys[i]))
        for h in same[:2]:
            add(i, h)
            add(h, i)

    # (b) hub-to-hub trunk routes among the "core" hubs (every region EXCEPT
    # West). The West hub is deliberately NOT trunked to the core -- the whole
    # West region reaches the rest of the network ONLY through the connector.
    west_hub = [h for h in hub_idx if region_of[h] == "West"][0]
    mtn_hub = [h for h in hub_idx if region_of[h] == "Mountain"][0]
    core_hubs = [h for h in hub_idx if h != west_hub]
    for a in core_hubs:
        for b in core_hubs:
            add(a, b)

    # (c) point-to-point: a high-volume non-hub "big P2P airport" with many
    # direct spokes. Its spokes ALSO attach to the regional hub, so removing the
    # big airport does NOT fragment the network -- it just removes volume.
    nonhub = [i for i in range(N_AIRPORTS)
              if not is_hub[i] and i != connector and region_of[i] != "West"]
    big_p2p = int(max(nonhub, key=lambda i: runways[i] * 1.0 + rng.random()))
    bp_hub = [h for h in hub_idx if region_of[h] == region_of[big_p2p]][0]
    same_region = [i for i in range(N_AIRPORTS)
                   if region_of[i] == region_of[big_p2p] and i != big_p2p
                   and not is_hub[i]]
    for j in rng.choice(same_region, size=min(14, len(same_region)), replace=False):
        add(big_p2p, int(j))
        add(int(j), big_p2p)
        add(bp_hub, int(j))          # also reachable via the hub (redundant)
        add(int(j), bp_hub)

    # scattered intra-region P2P (never crosses into/out of West)
    for i in range(N_AIRPORTS):
        if region_of[i] == "West":
            continue
        if rng.random() < 0.25:
            same = [j for j in range(N_AIRPORTS)
                    if region_of[j] == region_of[i] and j != i
                    and region_of[j] != "West"]
            if same:
                j = int(rng.choice(same))
                add(i, j)

    # (d) the connector: the SOLE gateway in/out of the West region. West hub
    # <-> connector <-> Mountain hub (the Mountain hub is part of the core mesh).
    # The connector itself sits in the West region with modest degree.
    add(west_hub, connector)
    add(connector, west_hub)
    add(mtn_hub, connector)
    add(connector, mtn_hub)
    # a couple of West spokes also feed the connector so it has some local degree
    west_spokes = [i for i in np.where(region_of == "West")[0]
                   if not is_hub[i] and i != connector]
    for j in rng.choice(west_spokes, size=min(3, len(west_spokes)), replace=False):
        add(connector, int(j))
        add(int(j), connector)

    # ----- assign per-block delays -----------------------------------------
    # First pass: baseline delays per (edge, block) with weather noise.
    # Then a SECOND pass propagates the WX hub's midday outbound spike to its
    # downstream airports' delays in the AFTERNOON block.
    edges_list = sorted(route_pairs)

    # outbound delay contributed to each origin airport, per block (we average
    # over its outgoing legs to get an airport-level "delay state").
    # Build base edge delays first.
    base_delay = {}  # (a,b,block) -> delay
    for (a, b) in edges_list:
        for blk in BLOCKS:
            d = (BASE_DELAY * BLOCK_LOAD[blk]
                 + 9.0 * weather_exposure[a]            # exposed origins delay more
                 + rng.normal(0, 4.0))
            base_delay[(a, b, blk)] = max(0.0, d)

    # WX hub weather event at MIDDAY: spike all its outbound legs.
    for (a, b) in edges_list:
        if a == wx_hub:
            base_delay[(a, b, "midday")] += WX_DELAY_SPIKE + rng.normal(0, 5)

    # airport-level midday outbound delay state (mean of outgoing legs)
    def airport_block_delay(node, blk):
        outs = [base_delay[(a, b, blk)] for (a, b) in edges_list if a == node]
        return float(np.mean(outs)) if outs else 0.0

    wx_midday_state = airport_block_delay(wx_hub, "midday")

    # downstream set of the WX hub (direct successors)
    downstream = sorted({b for (a, b) in edges_list if a == wx_hub})

    # PROPAGATION: each downstream airport inherits a fraction of the WX hub's
    # midday delay into the AFTERNOON block, scaled by edge flow share. The
    # resilient hub damps it heavily.
    for node in downstream:
        absorb = RESILIENT_ABSORB if node == resilient_hub else 0.0
        inherited = PROPAGATE_FRAC * (1 - absorb) * wx_midday_state
        # apply to that airport's OWN outbound legs in the afternoon
        for (a, b) in edges_list:
            if a == node:
                base_delay[(a, b, "afternoon")] += inherited + rng.normal(0, 3)
        # WX hub itself partially clears by afternoon (storm passing)
    # WX hub clears: afternoon outbound returns toward normal, evening normal.
    for (a, b) in edges_list:
        if a == wx_hub:
            # afternoon still somewhat elevated, evening near-normal
            base_delay[(a, b, "afternoon")] = (
                base_delay[(a, b, "afternoon")] * 0.35
                + BASE_DELAY * BLOCK_LOAD["afternoon"])

    # ----- flight volumes ---------------------------------------------------
    rows = []
    for (a, b) in edges_list:
        # base flights scale with whether endpoints are hubs and runways
        base_flights = 1 + (3 if is_hub[a] else 0) + (3 if is_hub[b] else 0)
        base_flights += runways[a] // 2
        if a == big_p2p or b == big_p2p:
            base_flights += 6           # the big point-to-point airport is busy
        if a == connector or b == connector:
            base_flights = max(1, base_flights - 2)   # connector is LOW volume
        for blk in BLOCKS:
            nf = max(1, int(round(base_flights * BLOCK_LOAD[blk]
                                  + rng.normal(0, 1.0))))
            dly = round(base_delay[(a, b, blk)] + rng.normal(0, 1.5), 1)
            dly = max(0.0, dly)
            seats = int(nf * rng.integers(70, 200))
            rows.append({
                "from_id": codes[a],
                "to_id": codes[b],
                "block": blk,
                "number_of_flights": nf,
                "seats": seats,
                "delay_min": dly,
            })

    edges = pd.DataFrame(rows)
    # order blocks chronologically for readability
    blk_order = {b: i for i, b in enumerate(BLOCKS)}
    edges["_o"] = edges["block"].map(blk_order)
    edges = edges.sort_values(["from_id", "to_id", "_o"]).drop(columns="_o").reset_index(drop=True)

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)
    print(f"airline-delays: {len(nodes)} nodes "
          f"({int(nodes.hub.sum())} hubs), {len(edges)} edges "
          f"({len(edges_list)} directed routes x {len(BLOCKS)} blocks).")


def _airport_codes(n: int) -> list[str]:
    """Deterministic unique 3-letter airport codes AAA, AAB, ... (not real)."""
    codes = []
    i = 0
    while len(codes) < n:
        a = i // (26 * 26)
        b = (i // 26) % 26
        c = i % 26
        codes.append(chr(65 + a) + chr(65 + b) + chr(65 + c))
        i += 1
    return codes


if __name__ == "__main__":
    main()
