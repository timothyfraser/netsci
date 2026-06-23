"""Generate the `ups-ground-network` project network (deterministic).

A stylized UPS-style ground line-haul network: large trucks move parcels between
package plants (facilities) across the continental US. Three kinds of node:
  - gateway  national sort hubs (e.g., Louisville, Chicago, Dallas, Atlanta,
             Ontario CA) -- the long-haul backbone;
  - hub      regional metro hubs;
  - center   local package centers (origin/destination plants).

Edges are DIRECTED lanes aggregated at the **source-plant -> destination-plant**
level: one row per ordered (from_id, to_id) pair (e.g., Ithaca -> Syracuse sends
N packages on T trucks). Lane attributes are the things you track about trucks:
`packages` (the weight), `trucks`, `distance_km`, and `transit_hours`.

Node attributes: kind, region, x (lon), y (lat), daily_packages, label.

Design parameters (the only record of the planted structure):
  - GATEWAYS form a fully-meshed long-haul backbone; almost all cross-region
    flow passes through them, so they have very high BETWEENNESS and are the real
    single points of failure for resilience.
  - DOMINANT_GATEWAY (Louisville): a national hub that most regional hubs also
    feed directly, so it concentrates the most cross-region paths.
  - SINGLE_HOMED_REGION (Southeast): its hubs connect to the backbone ONLY through
    ATLANTA. Removing Atlanta disconnects the whole region -- a genuine cut vertex
    a degree ranking will under-rate.
  - DECOY_HUB (Los Angeles): a busy regional metro hub that is NOT on the
    cross-region backbone, so removing it barely dents national connectivity --
    a reminder that a locally busy plant is not automatically a critical one.
  - TIGHT_BACKBONE: backbone & single-homed lanes run near truck capacity
    (high packages-per-truck, little slack); regional lanes carry slack. So the
    fragile lanes are the ones with the least spare capacity to absorb a surge.
  - Distance is real (haversine of coordinates); transit time = drive time at a
    lane-type speed + per-stop dwell + congestion noise.

Run:
    python data/projects/ups-ground-network/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import math
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

TRUCK_CAP = 1200          # max parcels a single line-haul trailer carries
DOMINANT_GATEWAY = "Louisville KY"
SINGLE_HOMED_REGION = "Southeast"
SINGLE_HOME_GATEWAY = "Atlanta GA"
DECOY_CITY = "Los Angeles CA"
MULTIHOME_SHARE = 0.60    # share of (non-single-homed) hubs that also feed Louisville
CENTERS_PER_HUB = 3

# (city, region, lat, lon)
GATEWAYS = [
    ("Louisville KY", "Midwest", 38.25, -85.76),
    ("Chicago IL", "Midwest", 41.88, -87.63),
    ("Dallas TX", "South", 32.78, -96.80),
    ("Atlanta GA", "Southeast", 33.75, -84.39),
    ("Ontario CA", "West", 34.06, -117.65),
]

HUBS = [
    # Northeast
    ("Boston MA", "Northeast", 42.36, -71.06),
    ("Syracuse NY", "Northeast", 43.05, -76.15),
    ("Albany NY", "Northeast", 42.65, -73.76),
    ("Buffalo NY", "Northeast", 42.89, -78.88),
    ("Hartford CT", "Northeast", 41.76, -72.69),
    # Mid-Atlantic
    ("New York NY", "Mid-Atlantic", 40.71, -74.01),
    ("Philadelphia PA", "Mid-Atlantic", 39.95, -75.17),
    ("Pittsburgh PA", "Mid-Atlantic", 40.44, -79.99),
    ("Baltimore MD", "Mid-Atlantic", 39.29, -76.61),
    ("Richmond VA", "Mid-Atlantic", 37.54, -77.44),
    # Southeast
    ("Charlotte NC", "Southeast", 35.23, -80.84),
    ("Nashville TN", "Southeast", 36.16, -86.78),
    ("Orlando FL", "Southeast", 28.54, -81.38),
    ("Miami FL", "Southeast", 25.76, -80.19),
    ("Memphis TN", "Southeast", 35.15, -90.05),
    # Midwest
    ("Indianapolis IN", "Midwest", 39.77, -86.16),
    ("Columbus OH", "Midwest", 39.96, -82.99),
    ("Detroit MI", "Midwest", 42.33, -83.05),
    ("Minneapolis MN", "Midwest", 44.98, -93.27),
    ("St Louis MO", "Midwest", 38.63, -90.20),
    ("Kansas City MO", "Midwest", 39.10, -94.58),
    # South
    ("Houston TX", "South", 29.76, -95.37),
    ("San Antonio TX", "South", 29.42, -98.49),
    ("Austin TX", "South", 30.27, -97.74),
    ("New Orleans LA", "South", 29.95, -90.07),
    ("Oklahoma City OK", "South", 35.47, -97.52),
    # Mountain
    ("Denver CO", "Mountain", 39.74, -104.99),
    ("Salt Lake City UT", "Mountain", 40.76, -111.89),
    ("Phoenix AZ", "Mountain", 33.45, -112.07),
    ("Albuquerque NM", "Mountain", 35.08, -106.65),
    # West
    ("Los Angeles CA", "West", 34.05, -118.24),
    ("San Francisco CA", "West", 37.77, -122.42),
    ("Seattle WA", "West", 47.61, -122.33),
    ("Portland OR", "West", 45.52, -122.68),
    ("Las Vegas NV", "West", 36.17, -115.14),
    ("Sacramento CA", "West", 38.58, -121.49),
]

# A few real satellite towns so the feeder lanes read true (e.g., Ithaca ->
# Syracuse). Any hub not listed gets generic "<City> Ctr N" centers.
REAL_CENTERS = {
    "Syracuse NY": ["Ithaca NY", "Utica NY", "Binghamton NY"],
    "Boston MA": ["Worcester MA", "Providence RI", "Manchester NH"],
    "Denver CO": ["Boulder CO", "Fort Collins CO", "Colorado Springs CO"],
    "Charlotte NC": ["Greensboro NC", "Asheville NC", "Columbia SC"],
    "Dallas TX": ["Fort Worth TX", "Waco TX", "Tyler TX"],
}


def haversine_km(a_lat, a_lon, b_lat, b_lon):
    R = 6371.0
    p1, p2 = math.radians(a_lat), math.radians(b_lat)
    dphi = math.radians(b_lat - a_lat)
    dlmb = math.radians(b_lon - a_lon)
    h = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def main() -> None:
    rng = np.random.default_rng(SEED)

    rows = []
    coord = {}    # node_id -> (lat, lon)
    region_of = {}
    kind_of = {}

    # ----- gateways -------------------------------------------------------
    gateway_ids = []
    for i, (city, region, lat, lon) in enumerate(GATEWAYS):
        nid = f"G{i+1:02d}"
        gateway_ids.append(nid)
        coord[nid] = (lat, lon); region_of[nid] = region; kind_of[nid] = "gateway"
        rows.append({"node_id": nid, "kind": "gateway", "region": region,
                     "x": round(lon, 3), "y": round(lat, 3),
                     "daily_packages": int(rng.integers(120000, 240000)),
                     "label": city})
    gw_by_city = {GATEWAYS[i][0]: gateway_ids[i] for i in range(len(GATEWAYS))}

    # ----- hubs -----------------------------------------------------------
    hub_ids = []
    hub_city = {}
    for i, (city, region, lat, lon) in enumerate(HUBS):
        nid = f"H{i+1:03d}"
        hub_ids.append(nid)
        hub_city[nid] = city
        coord[nid] = (lat, lon); region_of[nid] = region; kind_of[nid] = "hub"
        rows.append({"node_id": nid, "kind": "hub", "region": region,
                     "x": round(lon, 3), "y": round(lat, 3),
                     "daily_packages": int(rng.integers(20000, 80000)),
                     "label": city})

    # ----- centers (origin/destination plants) ----------------------------
    center_ids = []
    centers_of_hub = {h: [] for h in hub_ids}
    cidx = 0
    for h in hub_ids:
        city = hub_city[h]
        hlat, hlon = coord[h]
        names = REAL_CENTERS.get(city)
        for k in range(CENTERS_PER_HUB):
            cidx += 1
            nid = f"C{cidx:03d}"
            center_ids.append(nid)
            centers_of_hub[h].append(nid)
            if names and k < len(names):
                lbl = names[k]
                # nudge coords toward a plausible nearby spot
                clat = hlat + rng.normal(0, 0.5)
                clon = hlon + rng.normal(0, 0.5)
            else:
                lbl = f"{city} Ctr {k+1}"
                clat = hlat + rng.normal(0, 0.45)
                clon = hlon + rng.normal(0, 0.45)
            coord[nid] = (clat, clon); region_of[nid] = region_of[h]; kind_of[nid] = "center"
            rows.append({"node_id": nid, "kind": "center", "region": region_of[h],
                         "x": round(clon, 3), "y": round(clat, 3),
                         "daily_packages": int(rng.integers(1500, 9000)),
                         "label": lbl})

    nodes = pd.DataFrame(rows)
    size = dict(zip(nodes.node_id, nodes.daily_packages))

    # nearest gateway for each hub (by great-circle distance)
    def nearest_gateway(h):
        hlat, hlon = coord[h]
        return min(gateway_ids,
                   key=lambda g: haversine_km(hlat, hlon, *coord[g]))

    eds = []

    def add_lane(frm, to, packages, critical=False):
        d = haversine_km(*coord[frm], *coord[to])
        # speed by lane type: long backbone faster cruising; short regional slower
        base_speed = 88.0 if d > 600 else (78.0 if d > 200 else 64.0)
        speed = base_speed * rng.uniform(0.92, 1.06)
        dwell = rng.uniform(1.5, 4.0)                 # sort/handling hours
        congest = rng.uniform(0.0, 0.25) * (d / 100)  # mild distance-scaled noise
        transit = d / speed + dwell + congest
        packages = int(max(packages, 1))
        # capacity: tight on critical lanes (little slack), looser on regional
        per_truck = rng.uniform(1050, 1180) if critical else rng.uniform(560, 950)
        trucks = int(max(1, math.ceil(packages / per_truck)))
        eds.append({
            "from_id": frm, "to_id": to,
            "packages": packages,
            "trucks": trucks,
            "distance_km": round(d, 1),
            "transit_hours": round(transit, 2),
        })

    # ===== feeder + delivery: center <-> regional hub =====================
    for h in hub_ids:
        for c in centers_of_hub[h]:
            # origin plant -> hub (induction)
            add_lane(c, h, int(size[c] * rng.uniform(0.55, 0.9)))
            # hub -> destination plant (delivery)
            add_lane(h, c, int(size[c] * rng.uniform(0.55, 0.9)))

    # ===== line-haul: hub <-> gateway =====================================
    for h in hub_ids:
        region = region_of[h]
        if region == SINGLE_HOMED_REGION:
            gws = [gw_by_city[SINGLE_HOME_GATEWAY]]      # single-homed: Atlanta only
        else:
            gws = [nearest_gateway(h)]
            louis = gw_by_city[DOMINANT_GATEWAY]
            if louis not in gws and rng.random() < MULTIHOME_SHARE:
                gws.append(louis)                         # most also feed Louisville
        for g in gws:
            crit = (region == SINGLE_HOMED_REGION) or (g == gw_by_city[DOMINANT_GATEWAY])
            vol = int(size[h] * rng.uniform(0.35, 0.7))
            add_lane(h, g, vol, critical=crit)            # outbound to backbone
            add_lane(g, h, int(vol * rng.uniform(0.8, 1.15)), critical=crit)  # inbound

    # ===== trunk: gateway <-> gateway (full mesh) =========================
    for a in gateway_ids:
        for b in gateway_ids:
            if a == b:
                continue
            vol = int(min(size[a], size[b]) * rng.uniform(0.20, 0.45))
            add_lane(a, b, vol, critical=True)

    # ===== a few direct intra-region hub <-> hub lanes ====================
    by_region = {}
    for h in hub_ids:
        by_region.setdefault(region_of[h], []).append(h)
    for region, hs in by_region.items():
        if len(hs) < 2:
            continue
        n_direct = min(len(hs), int(rng.integers(2, 5)))
        for _ in range(n_direct):
            a, b = rng.choice(hs, size=2, replace=False)
            vol = int(min(size[a], size[b]) * rng.uniform(0.12, 0.3))
            add_lane(a, b, vol)

    edges = pd.DataFrame(eds)
    nodes = nodes[["node_id", "kind", "region", "x", "y", "daily_packages", "label"]]

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)

    kc = nodes.kind.value_counts()
    print(f"ups-ground-network: {len(nodes)} nodes "
          f"({kc.get('gateway',0)} gateway + {kc.get('hub',0)} hub + "
          f"{kc.get('center',0)} center), {len(edges)} lanes. "
          f"{edges.packages.sum():,} packages/day on {edges.trucks.sum():,} trucks.")


if __name__ == "__main__":
    main()
