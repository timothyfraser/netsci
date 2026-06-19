"""Generate the `satellite-constellation` project network (deterministic).

A single-instant snapshot of a multi-operator low-Earth-orbit (LEO) satellite
communications network. Three fictional operators fly distinct constellation
architectures, plus a set of ground stations (gateways) on the surface:

  - satellites    (kind = "satellite")  ~274 across three operators
  - ground_station(kind = "ground_station")  ~24 gateways

Operators (each a real-world architecture in disguise):
  - "Helios"  : Walker-Delta, i~53 deg, ~550 km, dense LASER inter-satellite
                links (a connected mesh); needs few gateways.   12 x 12 = 144
  - "Polaris" : Walker-Star near-polar i~88 deg, ~1200 km, BENT-PIPE: NO
                inter-satellite links at all -- every satellite depends on
                reaching a ground gateway.                       8 x  8 =  64
  - "Nimbus"  : Walker-Star polar i~86.4 deg, ~780 km, Ka-band crosslinks
                including a few cross-seam links.                 6 x 11 =  66

Edges (undirected), `link_type`:
  - intra_isl  : sat <-> fore/aft neighbor in the SAME plane (a ring)
  - inter_isl  : sat <-> nearest sat in an adjacent plane
  - crossseam  : the rare ISL spanning the Walker-Star ascending/descending seam
  - feeder     : sat <-> ground_station (the only way bent-pipe sats reach the net)
weighted by `capacity_gbps`, with `latency_ms` and `band`.

Design parameters (the only record of the planted structure):
  - BENTPIPE_OPERATOR = "Polaris": has zero ISLs, so removing all ground
    stations shatters it into isolated satellites while Helios's ISL mesh
    barely changes its largest component (architecture-divide resilience).
  - SEAM_LINK_FRACTION: in Walker-Star operators only a few planes bridge the
    ascending/descending seam; those crossseam links carry outsized betweenness.
  - GATEWAY_REGIONS: gateways cluster in NA/EU/E-Asia; sats over oceans / the
    global south / poles must hop far to a gateway -> FEEDER_LAT_PENALTY raises
    feeder latency with |lat| and ocean-ness, independent of satellite count.
  - GATEWAY_HUB_FRACTION: a few gateways absorb most feeders -> high strength /
    betweenness, single points of failure.
  - Operator + plane structure is recoverable by community detection; the few
    NEUTRAL shared gateways are the bridges between operator clusters.
  - AGING: early launch_year -> higher P(degraded) and lower capacity, and the
    earliest-launched satellites sit in the lowest-numbered planes.

Run:
    python data/projects/satellite-constellation/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

EARTH_R_KM = 6371.0

# --- constellation geometry -------------------------------------------------
# operator -> (n_planes, sats_per_plane, inclination_deg, altitude_km, has_isl)
OPERATORS = {
    "Helios":  dict(planes=12, per_plane=12, inc=53.0,  alt=550.0,  isl=True,
                    walker="delta", band="optical"),
    "Polaris": dict(planes=8,  per_plane=8,  inc=88.0,  alt=1200.0, isl=False,
                    walker="star",  band="Ku"),
    "Nimbus":  dict(planes=6,  per_plane=11, inc=86.4,  alt=780.0,  isl=True,
                    walker="star",  band="Ka"),
}

# --- planted parameters -----------------------------------------------------
BENTPIPE_OPERATOR = "Polaris"   # the operator with NO inter-satellite links
SEAM_LINK_FRACTION = 0.18       # frac of seam-adjacent planes that bridge seam
GATEWAY_HUB_FRACTION = 0.25     # frac of gateways that soak up most feeders
FEEDER_LAT_PENALTY = 26.0       # extra feeder latency (ms) at the poles/oceans
AGING_DEGRADE = 0.55            # max P(degraded) for the oldest satellites
N_NEUTRAL_GATEWAYS = 4          # shared gateways that bridge operator clusters

# gateway clusters: (name, lat, lon, n, radius_deg). Dense in NA/EU/E-Asia.
GATEWAY_REGIONS = [
    ("North America", 40.0,  -95.0, 6, 9.0),
    ("Europe",        50.0,   10.0, 6, 7.0),
    ("East Asia",     35.0,  125.0, 5, 8.0),
    ("South America", -20.0, -55.0, 2, 9.0),
    ("Oceania",       -30.0, 145.0, 2, 8.0),
    ("Africa",         5.0,   25.0, 1, 9.0),
    ("Mid-Ocean",     10.0,  -40.0, 2, 6.0),   # sparse, near nothing
]

# launch-year window
YEAR_MIN, YEAR_MAX = 2019, 2025


def subsatellite_latlon(inc_deg, raan_deg, anomaly_deg):
    """Sub-satellite latitude/longitude for a circular orbit at one instant.

    Standard spherical relations: given inclination i, RAAN, and argument of
    latitude u (here the true anomaly from the ascending node), the geocentric
    latitude and longitude of the sub-satellite point are
        lat = asin(sin i * sin u)
        lon = raan + atan2(cos i * sin u, cos u)
    (Earth rotation / GMST is folded into RAAN for this snapshot.)
    """
    i = np.radians(inc_deg)
    u = np.radians(anomaly_deg)
    raan = np.radians(raan_deg)
    lat = np.arcsin(np.sin(i) * np.sin(u))
    lon = raan + np.arctan2(np.cos(i) * np.sin(u), np.cos(u))
    lat_d = np.degrees(lat)
    lon_d = (np.degrees(lon) + 180.0) % 360.0 - 180.0
    return lat_d, lon_d


def haversine_km(lat1, lon1, lat2, lon2):
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dl = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * EARTH_R_KM * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def ocean_ness(lat, lon):
    """Crude 0..1 'how oceanic / underserved' score for a sub-satellite point.

    High over open ocean and the polar/southern reaches, low over the
    well-served NA/EU/E-Asia land masses. Not physical -- just a coverage proxy.
    """
    land_centers = [(40, -95), (50, 10), (35, 125), (-10, -55), (0, 20)]
    best = min(haversine_km(lat, lon, la, lo) for la, lo in land_centers)
    land_score = np.clip(best / 5000.0, 0, 1)         # far from land -> oceanic
    polar = np.clip((abs(lat) - 35) / 55.0, 0, 1)     # high |lat| underserved
    return float(np.clip(0.55 * land_score + 0.45 * polar, 0, 1))


def main() -> None:
    rng = np.random.default_rng(SEED)

    # ===== 1. satellites ===================================================
    sat_rows = []
    # per-operator record of (node_id, plane, slot, lat, lon) for edge building
    sat_index: dict[str, list[dict]] = {op: [] for op in OPERATORS}

    sid = 1
    for op in sorted(OPERATORS):                      # deterministic op order
        cfg = OPERATORS[op]
        nP, nS = cfg["planes"], cfg["per_plane"]
        # Walker-Star spreads RAAN over 180 deg; Walker-Delta over 360 deg.
        raan_span = 180.0 if cfg["walker"] == "star" else 360.0
        for p in range(nP):
            raan = (raan_span * p / nP) % 360.0
            # phasing offset between planes (Walker phase factor), small jitter
            phase = (360.0 / (nP * nS)) * p
            for s in range(nS):
                anomaly = (360.0 * s / nS + phase) % 360.0
                inc = cfg["inc"] + float(rng.normal(0, 0.05))
                alt = cfg["alt"] + float(rng.normal(0, 3.0))
                lat, lon = subsatellite_latlon(inc, raan, anomaly)

                # AGING: earliest planes launched first; year rises with plane.
                yr_frac = p / max(nP - 1, 1)
                launch_year = int(round(YEAR_MIN + yr_frac * (YEAR_MAX - YEAR_MIN)
                                        + rng.normal(0, 0.4)))
                launch_year = int(np.clip(launch_year, YEAR_MIN, YEAR_MAX))
                age_frac = (YEAR_MAX - launch_year) / (YEAR_MAX - YEAR_MIN)
                p_deg = AGING_DEGRADE * age_frac
                roll = rng.random()
                if roll < 0.04:
                    status = "spare"
                elif roll < 0.04 + p_deg:
                    status = "degraded"
                else:
                    status = "active"

                # capacity: optical/Ka fast; bent-pipe Ku slower; degraded lower
                base_cap = {"optical": 20.0, "Ka": 12.0, "Ku": 8.0}[cfg["band"]]
                cap = base_cap * (1.0 - 0.45 * age_frac) * (1 + rng.normal(0, 0.06))
                if status == "degraded":
                    cap *= 0.55
                cap = float(np.clip(cap, 1.0, 30.0))

                node_id = f"SAT{sid:04d}"
                rec = dict(
                    node_id=node_id, kind="satellite", operator=op,
                    plane=p, slot=s,
                    altitude_km=round(alt, 1), inclination_deg=round(inc, 2),
                    raan_deg=round(raan, 2),
                    lat=round(lat, 4), lon=round(lon, 4),
                    x=round(lon, 4), y=round(lat, 4),
                    band=cfg["band"], isl_capable=int(cfg["isl"]),
                    launch_year=launch_year, status=status,
                    capacity_gbps=round(cap, 2),
                    label=f"{op} {p:02d}-{s:02d}",
                )
                sat_rows.append(rec)
                sat_index[op].append(rec)
                sid += 1

    # ===== 2. ground stations =============================================
    gs_rows = []
    gs_all = []
    gid = 1
    # build a flat, ordered list of gateway positions first
    gw_positions = []
    for region, clat, clon, n, radius in GATEWAY_REGIONS:
        for _ in range(n):
            la = float(np.clip(clat + rng.normal(0, radius), -85, 85))
            lo = (clon + rng.normal(0, radius) + 180) % 360 - 180
            gw_positions.append((region, la, lo))

    n_gw = len(gw_positions)
    # decide which gateways are NEUTRAL (shared) vs operator-specific.
    # neutral ones are chosen by index (sorted) for determinism.
    neutral_idx = set(sorted(range(n_gw))[:N_NEUTRAL_GATEWAYS])
    ops_cycle = sorted(OPERATORS)
    for k, (region, la, lo) in enumerate(gw_positions):
        if k in neutral_idx:
            operator = "neutral"
        else:
            operator = ops_cycle[k % len(ops_cycle)]
        capacity = float(np.clip(40 + rng.normal(0, 12), 8, 90))
        rec = dict(
            node_id=f"GS{gid:03d}", kind="ground_station", operator=operator,
            region=region, lat=round(la, 4), lon=round(lo, 4),
            x=round(lo, 4), y=round(la, 4),
            capacity_gbps=round(capacity, 2),
            label=f"{region} GW {gid:02d}",
        )
        gs_rows.append(rec)
        gs_all.append(rec)
        gid += 1

    # ===== 3. edges ========================================================
    edges = []
    seen = set()

    def add_edge(a, b, link_type, cap, lat_ms, band):
        if a == b:
            return
        key = (a, b) if a < b else (b, a)
        if key in seen:
            return
        seen.add(key)
        edges.append(dict(
            from_id=key[0], to_id=key[1], link_type=link_type,
            capacity_gbps=round(float(cap), 2), latency_ms=round(float(lat_ms), 2),
            band=band,
        ))

    # ---- inter/intra ISL for operators that have ISL ----------------------
    for op in sorted(OPERATORS):
        cfg = OPERATORS[op]
        if not cfg["isl"]:
            continue
        nP, nS = cfg["planes"], cfg["per_plane"]
        recs = sat_index[op]
        # index by (plane, slot)
        by_ps = {(r["plane"], r["slot"]): r for r in recs}

        # intra-plane ring: fore/aft neighbors in the same plane
        for p in range(nP):
            for s in range(nS):
                a = by_ps[(p, s)]
                b = by_ps[(p, (s + 1) % nS)]
                d = haversine_km(a["lat"], a["lon"], b["lat"], b["lon"])
                lat_ms = d / 200.0 + rng.uniform(0.1, 0.6)   # light-speed-ish
                cap = min(a["capacity_gbps"], b["capacity_gbps"]) * 1.4
                add_edge(a["node_id"], b["node_id"], "intra_isl",
                         cap, lat_ms, cfg["band"])

        # inter-plane: each sat links to nearest sat in the next plane.
        # Walker-Star has a SEAM between plane (nP-1) and plane 0 (ascending vs
        # descending side); only a few planes bridge it (crossseam links).
        seam_pairs = {(nP - 1, 0)}
        for p in range(nP):
            q = (p + 1) % nP
            is_seam = (p, q) in seam_pairs or (q, p) in seam_pairs
            if cfg["walker"] == "star" and is_seam:
                # only a small fraction of slots bridge the seam
                n_bridge = max(1, int(round(nS * SEAM_LINK_FRACTION)))
                bridge_slots = sorted(range(nS))[:n_bridge]
            else:
                bridge_slots = list(range(nS))
            for s in bridge_slots:
                a = by_ps[(p, s)]
                # nearest slot in plane q
                cands = [by_ps[(q, s2)] for s2 in range(nS)]
                dists = [haversine_km(a["lat"], a["lon"], c["lat"], c["lon"])
                         for c in cands]
                b = cands[int(np.argmin(dists))]
                d = min(dists)
                if d > 4000:           # too far to close a link
                    continue
                lat_ms = d / 200.0 + rng.uniform(0.2, 0.8)
                if cfg["walker"] == "star" and is_seam:
                    lt = "crossseam"
                    # seam crossings are bandwidth-starved (sats cross at high
                    # relative velocity): low capacity -> a weighted bottleneck.
                    cap = min(a["capacity_gbps"], b["capacity_gbps"]) * 0.35
                else:
                    lt = "inter_isl"
                    cap = min(a["capacity_gbps"], b["capacity_gbps"]) * 1.1
                add_edge(a["node_id"], b["node_id"], lt, cap, lat_ms, cfg["band"])

    # ---- feeder links: satellites <-> ground stations ---------------------
    # A satellite can reach a gateway it is "over" (within an elevation mask).
    # Hub gateways soak up most feeders. Bent-pipe sats depend ENTIRELY on these.
    # Visibility footprint half-angle grows with altitude (rough proxy).
    gw_by_op: dict[str, list[dict]] = {op: [] for op in OPERATORS}
    neutral_gws = [g for g in gs_all if g["operator"] == "neutral"]
    for g in gs_all:
        if g["operator"] in gw_by_op:
            gw_by_op[g["operator"]].append(g)

    # choose hub gateways (deterministic: first fraction by node_id order)
    sorted_gw_ids = sorted(g["node_id"] for g in gs_all)
    n_hub = max(1, int(round(len(sorted_gw_ids) * GATEWAY_HUB_FRACTION)))
    hub_ids = set(sorted_gw_ids[:n_hub])

    for op in sorted(OPERATORS):
        cfg = OPERATORS[op]
        # gateways this operator can use: its own + neutral
        usable = sorted(gw_by_op[op] + neutral_gws, key=lambda g: g["node_id"])
        # footprint radius (km) on the ground; higher altitude sees farther
        footprint = 2500.0 + cfg["alt"] * 1.4
        for sat in sat_index[op]:
            # distances to all usable gateways
            ds = [(haversine_km(sat["lat"], sat["lon"], g["lat"], g["lon"]), g)
                  for g in usable]
            ds.sort(key=lambda t: (t[0], t[1]["node_id"]))
            # link to gateways within footprint; bias toward hub gateways
            linked = 0
            target = 2 if cfg["isl"] else 3   # bent-pipe craves more feeders
            for d, g in ds:
                if d > footprint and linked >= 1:
                    break
                if d > footprint * 1.6:
                    break
                # hubs win: non-hub gateways links are probabilistically dropped
                if g["node_id"] not in hub_ids and rng.random() < 0.5 and linked >= 1:
                    continue
                # feeder latency: distance + penalty for oceanic/polar coverage
                oc = ocean_ness(sat["lat"], sat["lon"])
                lat_ms = (d / 200.0) + FEEDER_LAT_PENALTY * oc + rng.uniform(0.2, 1.0)
                cap = min(sat["capacity_gbps"], g["capacity_gbps"]) * 0.8
                add_edge(sat["node_id"], g["node_id"], "feeder",
                         cap, lat_ms, sat["band"])
                linked += 1
                if linked >= target:
                    break
            # guarantee bent-pipe sats are not totally isolated: if none in
            # range, attach to the single nearest usable gateway (long hop).
            if linked == 0 and ds:
                d, g = ds[0]
                oc = ocean_ness(sat["lat"], sat["lon"])
                lat_ms = (d / 200.0) + FEEDER_LAT_PENALTY * oc + rng.uniform(0.2, 1.0)
                cap = min(sat["capacity_gbps"], g["capacity_gbps"]) * 0.8
                add_edge(sat["node_id"], g["node_id"], "feeder",
                         cap, lat_ms, sat["band"])

    # ===== 4. assemble & write ============================================
    sat_df = pd.DataFrame(sat_rows)
    gs_df = pd.DataFrame(gs_rows)

    # unified column order; satellite-only cols blank for ground stations
    cols = ["node_id", "kind", "operator", "plane", "slot", "altitude_km",
            "inclination_deg", "raan_deg", "region", "lat", "lon", "x", "y",
            "band", "isl_capable", "launch_year", "status", "capacity_gbps",
            "label"]
    for c in cols:
        if c not in sat_df.columns:
            sat_df[c] = pd.NA
        if c not in gs_df.columns:
            gs_df[c] = pd.NA
    nodes = pd.concat([sat_df[cols], gs_df[cols]], ignore_index=True)

    edges_df = pd.DataFrame(edges, columns=[
        "from_id", "to_id", "link_type", "capacity_gbps", "latency_ms", "band"])

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges_df.to_csv(HERE / "edges.csv", index=False)

    nsat = (nodes.kind == "satellite").sum()
    ngs = (nodes.kind == "ground_station").sum()
    lc = edges_df.link_type.value_counts()
    print(f"satellite-constellation: {len(nodes)} nodes "
          f"({nsat} satellites + {ngs} ground_stations), {len(edges_df)} edges "
          f"(intra_isl={lc.get('intra_isl',0)}, inter_isl={lc.get('inter_isl',0)}, "
          f"crossseam={lc.get('crossseam',0)}, feeder={lc.get('feeder',0)}).")


if __name__ == "__main__":
    main()
