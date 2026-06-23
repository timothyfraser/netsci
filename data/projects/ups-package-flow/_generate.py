"""Generate the `ups-package-flow` project network (deterministic).

The PACKAGE-LEVEL companion to `ups-ground-network`: where that dataset
aggregates flow to one row per truck lane, here the **unit of analysis is the
individual package** -- one row per parcel. Each parcel is a directed edge from
its origin plant to its destination plant, so the edge list is a directed
multigraph over the same plant universe (gateways / hubs / centers). Aggregating
the package rows by (from_id, to_id) reproduces a lane-level view.

Per-package attributes: service_level, weight_kg, distance_km, transit_hours,
promised_hours, on_time, damaged.

Node attributes: kind, region, x (lon), y (lat), daily_packages, label.

Design parameters (the only record of the planted structure):
  - SERVICE mix drives the promise: `overnight` < `two_day` < `ground` lead time;
    on_time = (transit_hours <= promised_hours).
  - CROSS_REGION_PENALTY: parcels whose origin and destination are in different
    regions take extra hours (more hand-offs across the backbone) *independent of
    distance*, so their on-time rate is worse even after controlling for distance.
  - RURAL_DEST_PENALTY: parcels delivered to low-throughput (rural) destination
    plants run slower *controlling for distance* -- a planted service-equity gap.
  - WEIGHT effects: heavier parcels are a little slower and a little more likely
    to be `damaged`.
  - Distance is real (haversine of plant coordinates).

Run:
    python data/projects/ups-package-flow/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import math
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42
N_PACKAGES = 5200
CENTERS_PER_HUB = 3

# planted effect sizes (hours unless noted)
CROSS_REGION_PENALTY = (5.0, 16.0)   # uniform extra hours for inter-region parcels
RURAL_DEST_MAX = 13.0                 # max extra hours for the smallest dest plant
HEAVY_PENALTY_PER_KG = 0.25          # extra hours per kg over 5 kg
DAMAGE_BASE = 0.012

# (city, region, lat, lon)
GATEWAYS = [
    ("Louisville KY", "Midwest", 38.25, -85.76),
    ("Chicago IL", "Midwest", 41.88, -87.63),
    ("Dallas TX", "South", 32.78, -96.80),
    ("Atlanta GA", "Southeast", 33.75, -84.39),
    ("Ontario CA", "West", 34.06, -117.65),
]
HUBS = [
    ("Boston MA", "Northeast", 42.36, -71.06), ("Syracuse NY", "Northeast", 43.05, -76.15),
    ("Albany NY", "Northeast", 42.65, -73.76), ("Buffalo NY", "Northeast", 42.89, -78.88),
    ("Hartford CT", "Northeast", 41.76, -72.69),
    ("New York NY", "Mid-Atlantic", 40.71, -74.01), ("Philadelphia PA", "Mid-Atlantic", 39.95, -75.17),
    ("Pittsburgh PA", "Mid-Atlantic", 40.44, -79.99), ("Baltimore MD", "Mid-Atlantic", 39.29, -76.61),
    ("Richmond VA", "Mid-Atlantic", 37.54, -77.44),
    ("Charlotte NC", "Southeast", 35.23, -80.84), ("Nashville TN", "Southeast", 36.16, -86.78),
    ("Orlando FL", "Southeast", 28.54, -81.38), ("Miami FL", "Southeast", 25.76, -80.19),
    ("Memphis TN", "Southeast", 35.15, -90.05),
    ("Indianapolis IN", "Midwest", 39.77, -86.16), ("Columbus OH", "Midwest", 39.96, -82.99),
    ("Detroit MI", "Midwest", 42.33, -83.05), ("Minneapolis MN", "Midwest", 44.98, -93.27),
    ("St Louis MO", "Midwest", 38.63, -90.20), ("Kansas City MO", "Midwest", 39.10, -94.58),
    ("Houston TX", "South", 29.76, -95.37), ("San Antonio TX", "South", 29.42, -98.49),
    ("Austin TX", "South", 30.27, -97.74), ("New Orleans LA", "South", 29.95, -90.07),
    ("Oklahoma City OK", "South", 35.47, -97.52),
    ("Denver CO", "Mountain", 39.74, -104.99), ("Salt Lake City UT", "Mountain", 40.76, -111.89),
    ("Phoenix AZ", "Mountain", 33.45, -112.07), ("Albuquerque NM", "Mountain", 35.08, -106.65),
    ("Los Angeles CA", "West", 34.05, -118.24), ("San Francisco CA", "West", 37.77, -122.42),
    ("Seattle WA", "West", 47.61, -122.33), ("Portland OR", "West", 45.52, -122.68),
    ("Las Vegas NV", "West", 36.17, -115.14), ("Sacramento CA", "West", 38.58, -121.49),
]
CENTER_TOWNS = {
    "Boston MA": ["Cambridge MA", "Worcester MA", "Providence RI"],
    "Syracuse NY": ["Ithaca NY", "Utica NY", "Binghamton NY"],
    "Albany NY": ["Schenectady NY", "Troy NY", "Saratoga Springs NY"],
    "Buffalo NY": ["Niagara Falls NY", "Rochester NY", "Jamestown NY"],
    "Hartford CT": ["New Haven CT", "Springfield MA", "Waterbury CT"],
    "New York NY": ["Newark NJ", "Yonkers NY", "Jersey City NJ"],
    "Philadelphia PA": ["Camden NJ", "Wilmington DE", "Allentown PA"],
    "Pittsburgh PA": ["Greensburg PA", "Washington PA", "Altoona PA"],
    "Baltimore MD": ["Annapolis MD", "Towson MD", "Frederick MD"],
    "Richmond VA": ["Petersburg VA", "Charlottesville VA", "Fredericksburg VA"],
    "Charlotte NC": ["Gastonia NC", "Concord NC", "Rock Hill SC"],
    "Nashville TN": ["Murfreesboro TN", "Franklin TN", "Clarksville TN"],
    "Orlando FL": ["Kissimmee FL", "Sanford FL", "Lakeland FL"],
    "Miami FL": ["Fort Lauderdale FL", "Hialeah FL", "West Palm Beach FL"],
    "Memphis TN": ["Southaven MS", "Jackson TN", "West Memphis AR"],
    "Indianapolis IN": ["Carmel IN", "Bloomington IN", "Lafayette IN"],
    "Columbus OH": ["Dublin OH", "Newark OH", "Lancaster OH"],
    "Detroit MI": ["Ann Arbor MI", "Warren MI", "Dearborn MI"],
    "Minneapolis MN": ["St Paul MN", "Bloomington MN", "Rochester MN"],
    "St Louis MO": ["St Charles MO", "Florissant MO", "Belleville IL"],
    "Kansas City MO": ["Overland Park KS", "Independence MO", "Olathe KS"],
    "Houston TX": ["Pasadena TX", "Sugar Land TX", "Galveston TX"],
    "San Antonio TX": ["New Braunfels TX", "Schertz TX", "Seguin TX"],
    "Austin TX": ["Round Rock TX", "San Marcos TX", "Georgetown TX"],
    "New Orleans LA": ["Metairie LA", "Baton Rouge LA", "Slidell LA"],
    "Oklahoma City OK": ["Norman OK", "Edmond OK", "Moore OK"],
    "Denver CO": ["Boulder CO", "Aurora CO", "Fort Collins CO"],
    "Salt Lake City UT": ["Provo UT", "Ogden UT", "Orem UT"],
    "Phoenix AZ": ["Mesa AZ", "Tempe AZ", "Scottsdale AZ"],
    "Albuquerque NM": ["Santa Fe NM", "Rio Rancho NM", "Los Lunas NM"],
    "Los Angeles CA": ["Long Beach CA", "Anaheim CA", "Pasadena CA"],
    "San Francisco CA": ["Oakland CA", "San Jose CA", "Berkeley CA"],
    "Seattle WA": ["Tacoma WA", "Bellevue WA", "Everett WA"],
    "Portland OR": ["Beaverton OR", "Gresham OR", "Salem OR"],
    "Las Vegas NV": ["Henderson NV", "North Las Vegas NV", "Pahrump NV"],
    "Sacramento CA": ["Roseville CA", "Elk Grove CA", "Davis CA"],
}
SERVICES = ["ground", "two_day", "overnight"]
SERVICE_P = [0.62, 0.26, 0.12]


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
    coord = {}
    for i, (city, region, lat, lon) in enumerate(GATEWAYS):
        nid = f"G{i+1:02d}"; coord[nid] = (lat, lon)
        rows.append({"node_id": nid, "kind": "gateway", "region": region,
                     "x": round(lon, 3), "y": round(lat, 3),
                     "daily_packages": int(rng.integers(120000, 240000)),
                     "label": f"{city} Gateway"})
    hub_ids, hub_city = [], {}
    for i, (city, region, lat, lon) in enumerate(HUBS):
        nid = f"H{i+1:03d}"; hub_ids.append(nid); hub_city[nid] = city; coord[nid] = (lat, lon)
        rows.append({"node_id": nid, "kind": "hub", "region": region,
                     "x": round(lon, 3), "y": round(lat, 3),
                     "daily_packages": int(rng.integers(20000, 80000)),
                     "label": f"{city} Hub"})
    center_ids = []
    cidx = 0
    for h in hub_ids:
        city = hub_city[h]; hlat, hlon = coord[h]
        for k in range(CENTERS_PER_HUB):
            cidx += 1; nid = f"C{cidx:03d}"; center_ids.append(nid)
            clat = hlat + rng.normal(0, 0.45); clon = hlon + rng.normal(0, 0.45)
            coord[nid] = (clat, clon)
            rows.append({"node_id": nid, "kind": "center",
                         "region": next(r for c, r, *_ in HUBS if c == city),
                         "x": round(clon, 3), "y": round(clat, 3),
                         "daily_packages": int(rng.integers(1500, 9000)),
                         "label": f"{CENTER_TOWNS[city][k]} Center"})

    nodes = pd.DataFrame(rows)
    region_of = dict(zip(nodes.node_id, nodes.region))
    size_of = dict(zip(nodes.node_id, nodes.daily_packages))

    # parcels originate and terminate at local centers
    centers = np.array(center_ids)
    csize = np.array([size_of[c] for c in centers], dtype=float)
    p_origin = csize / csize.sum()
    # destination size normaliser for the rural-dest penalty (0 = smallest)
    smin, smax = csize.min(), csize.max()
    size_norm = {c: (size_of[c] - smin) / (smax - smin) for c in center_ids}
    clat = {c: coord[c][0] for c in center_ids}
    clon = {c: coord[c][1] for c in center_ids}

    origins = rng.choice(centers, size=N_PACKAGES, p=p_origin)
    services = rng.choice(SERVICES, size=N_PACKAGES, p=SERVICE_P)

    eds = []
    for i in range(N_PACKAGES):
        o = origins[i]
        # destination: distance-decayed, size-weighted, not the origin
        olat, olon = coord[o]
        d_to = np.array([haversine_km(olat, olon, clat[c], clon[c]) for c in centers])
        w = csize / (1.0 + (d_to / 800.0) ** 2)
        w[centers == o] = 0.0
        w = w / w.sum()
        dest = centers[rng.choice(len(centers), p=w)]
        dist = haversine_km(olat, olon, clat[dest], clon[dest])

        svc = services[i]
        wkg = float(np.clip(rng.lognormal(0.6, 0.8), 0.1, 40.0))

        if svc == "ground":
            transit = dist / 80.0 + rng.uniform(8, 20)
            promised = 24.0 + dist / 55.0
            pscale = 1.0                  # ground rides the full hand-off chain
        elif svc == "two_day":
            transit = dist / 280.0 + rng.uniform(14, 26)
            promised = 48.0
            pscale = 0.6
        else:  # overnight (air) — bypasses most ground hand-off delay
            transit = dist / 650.0 + rng.uniform(9, 16)
            promised = 30.0
            pscale = 0.3

        # planted penalties (independent of distance), scaled by service mode
        pen = 0.0
        if region_of[o] != region_of[dest]:
            pen += rng.uniform(*CROSS_REGION_PENALTY)                 # cross-region hand-offs
        pen += RURAL_DEST_MAX * (1.0 - size_norm[dest])              # rural dest gap
        if wkg > 5.0:
            pen += (wkg - 5.0) * HEAVY_PENALTY_PER_KG
        transit += pen * pscale + rng.normal(0, 3.0)                  # + noise
        transit = max(1.0, round(transit, 2))
        promised = round(promised, 1)

        on_time = int(transit <= promised)
        p_damage = DAMAGE_BASE + max(0.0, (wkg - 10.0)) * 0.004 + \
            (0.01 if region_of[o] != region_of[dest] else 0.0)
        damaged = int(rng.random() < p_damage)

        eds.append({
            "from_id": o, "to_id": dest, "package_id": f"PKG{i+1:06d}",
            "service_level": svc, "weight_kg": round(wkg, 2),
            "distance_km": round(dist, 1), "transit_hours": round(transit, 2),
            "promised_hours": round(promised, 1), "on_time": on_time,
            "damaged": damaged,
        })

    edges = pd.DataFrame(eds)
    nodes = nodes[["node_id", "kind", "region", "x", "y", "daily_packages", "label"]]

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)

    kc = nodes.kind.value_counts()
    print(f"ups-package-flow: {len(nodes)} plants "
          f"({kc.get('gateway',0)} gateway + {kc.get('hub',0)} hub + "
          f"{kc.get('center',0)} center), {len(edges)} packages. "
          f"on-time {edges.on_time.mean():.1%}, damaged {edges.damaged.mean():.1%}.")


if __name__ == "__main__":
    main()
