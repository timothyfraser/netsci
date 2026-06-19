"""Generate the `uber-manhattan` project network (deterministic).

A bipartite ride-matching network for one day in downtown Manhattan:
  - ~120 drivers   (kind = "driver")
  - ~250 riders    (kind = "rider")   -> ~370 nodes total
Edges are individual rides (driver served rider), so the same driver-rider pair
can appear several times (parallel edges = repeat customers). Each ride carries
pickup/dropoff zone, hour, wait time, distance, fare, surge multiplier, and tip.
A companion `zones.csv` is the lookup table for the Manhattan zone grid.

Design parameters (the only record of the planted structure):
  - DESERT_PENALTY: pickups in low-income zones wait longer and are served less
    (a spatial service gap that is NOT explained by demand).
  - PRO_DRIVERS: a small clique of high-tenure drivers monopolize airport runs
    and the high-fare long trips -> extreme earnings concentration.
  - SURGE: evening surge concentrates in nightlife zones; tips fall as surge
    rises (riders tip less when they feel gouged).
  - LOYAL_PAIRS: a set of commuter rider-driver pairs ride together repeatedly
    in the morning peak (a planted bipartite community).

Run:
    python data/projects/uber-manhattan/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

N_DRIVERS = 120
N_RIDERS = 250
N_RIDES = 3000

# --- planted parameters -----------------------------------------------------
N_PRO = 10            # pro drivers who corner the airport / long-haul market
N_LOYAL_PAIRS = 28    # commuter rider-driver pairs that repeat
DESERT_PENALTY = 6.5  # extra wait-minutes in the lowest-income pickup zones
NIGHTLIFE = {"Lower East Side", "East Village", "West Village",
             "Meatpacking", "Nolita"}

# downtown-Manhattan zone grid: (name, neighborhood, avenue col, street row,
# income tier 0..1). Income is a *tier*; dollars get jittered below.
ZONE_DEFS = [
    ("FiDi",          "Financial District", 3, 1, 0.85),
    ("Battery Park",  "Battery Park City",  1, 1, 0.90),
    ("Tribeca",       "Tribeca",            2, 2, 0.97),
    ("Civic Center",  "Civic Center",       4, 2, 0.55),
    ("Chinatown",     "Chinatown",          5, 3, 0.28),
    ("Two Bridges",   "Two Bridges",        6, 2, 0.22),
    ("Lower East Side", "Lower East Side",  6, 4, 0.30),
    ("SoHo",          "SoHo",               3, 4, 0.92),
    ("Little Italy",  "Little Italy",       4, 4, 0.60),
    ("Nolita",        "Nolita",             5, 4, 0.78),
    ("Hudson Square", "Hudson Square",      2, 5, 0.80),
    ("Greenwich Vlg", "Greenwich Village",  3, 6, 0.88),
    ("West Village",  "West Village",       2, 6, 0.95),
    ("East Village",  "East Village",       6, 6, 0.45),
    ("NoHo",          "NoHo",               4, 6, 0.82),
    ("Bowery",        "Bowery",             5, 5, 0.50),
    ("Meatpacking",   "Meatpacking",        1, 7, 0.93),
    ("Chelsea",       "Chelsea",            2, 8, 0.84),
    ("Flatiron",      "Flatiron",           4, 8, 0.86),
    ("Union Square",  "Union Square",       4, 7, 0.80),
    ("Gramercy",      "Gramercy",           5, 8, 0.83),
    ("Kips Bay",      "Kips Bay",           6, 8, 0.62),
    ("Murray Hill",   "Murray Hill",        6, 9, 0.74),
    ("Stuy Town",     "Stuyvesant Town",    7, 7, 0.58),
]


def main() -> None:
    rng = np.random.default_rng(SEED)

    # ----- zones -----------------------------------------------------------
    zrows = []
    for i, (name, nbhd, ave, st, tier) in enumerate(ZONE_DEFS, start=1):
        income = int(np.clip(35000 + tier * 140000 + rng.normal(0, 8000), 22000, 220000))
        zrows.append({
            "zone_id": f"Z{i:02d}", "name": name, "neighborhood": nbhd,
            "avenue": ave, "street": st,
            "x": round(ave * 1.0 + rng.normal(0, 0.12), 2),
            "y": round(st * 1.0 + rng.normal(0, 0.12), 2),
            "median_income": income,
            "nightlife": int(nbhd in NIGHTLIFE),
        })
    # airport pseudo-zone, far to the southeast
    zrows.append({"zone_id": "ZJFK", "name": "JFK Airport", "neighborhood": "JFK Airport",
                  "avenue": 12, "street": -6, "x": 14.0, "y": -6.0,
                  "median_income": pd.NA, "nightlife": 0})
    zones = pd.DataFrame(zrows)
    zpos = {r.zone_id: (r.x, r.y) for r in zones.itertuples()}
    z_ids = [z for z in zones.zone_id if z != "ZJFK"]
    z_income = {r.zone_id: r.median_income for r in zones.itertuples()}
    inc_vals = np.array([z_income[z] for z in z_ids], dtype=float)
    inc_norm = {z: (z_income[z] - inc_vals.min()) / (inc_vals.max() - inc_vals.min())
                for z in z_ids}
    nightlife_z = set(zones.loc[zones.nightlife == 1, "zone_id"])

    # ----- drivers ---------------------------------------------------------
    veh = rng.choice(["uberx", "xl", "black"], size=N_DRIVERS, p=[0.72, 0.18, 0.10])
    tenure = rng.integers(1, 84, N_DRIVERS)
    # pros = the 10 longest-tenured; bump them to premium vehicles.
    pro_idx = np.argsort(-tenure)[:N_PRO]
    for p in pro_idx:
        veh[p] = "black" if rng.random() < 0.6 else "xl"
    drivers = pd.DataFrame({
        "node_id": [f"D{i:03d}" for i in range(1, N_DRIVERS + 1)],
        "kind": "driver",
        "home_zone": rng.choice(z_ids, N_DRIVERS),
        "vehicle_type": veh,
        "tenure_months": tenure,
        "rating": np.round(np.clip(rng.normal(4.85, 0.12, N_DRIVERS), 4.2, 5.0), 2),
        "income_bracket": pd.NA,
    })
    pro_ids = set(drivers.node_id.iloc[pro_idx])

    # ----- riders ----------------------------------------------------------
    # riders live disproportionately in residential (mid/low income) zones
    res_w = np.array([1.4 - 0.5 * inc_norm[z] for z in z_ids]); res_w /= res_w.sum()
    rider_home = rng.choice(z_ids, N_RIDERS, p=res_w)
    rbrack = []
    for z in rider_home:
        pr = inc_norm[z]
        w = np.array([max(0.05, 0.6 - 0.5 * pr), 0.4, max(0.05, 0.05 + 0.5 * pr)])
        rbrack.append(rng.choice(["low", "mid", "high"], p=w / w.sum()))
    riders = pd.DataFrame({
        "node_id": [f"R{i:03d}" for i in range(1, N_RIDERS + 1)],
        "kind": "rider",
        "home_zone": rider_home,
        "vehicle_type": pd.NA,
        "tenure_months": pd.NA,
        "rating": np.round(np.clip(rng.normal(4.9, 0.1, N_RIDERS), 4.3, 5.0), 2),
        "income_bracket": rbrack,
    })
    rider_ids = list(riders.node_id)
    rider_home_map = dict(zip(riders.node_id, riders.home_zone))
    rider_brack_map = dict(zip(riders.node_id, riders.income_bracket))

    nodes = pd.concat([drivers, riders], ignore_index=True)

    # planted loyal commuter pairs
    loyal = list(zip(rng.choice(rider_ids, N_LOYAL_PAIRS, replace=False),
                     rng.choice(list(drivers.node_id), N_LOYAL_PAIRS, replace=False)))

    def dist(a, b):
        (ax, ay), (bx, by) = zpos[a], zpos[b]
        return float(np.hypot(ax - bx, ay - by))

    # ----- rides -----------------------------------------------------------
    rows = []
    # each commuter pair rides together repeatedly across the (implied) week:
    # 3 morning commutes out + 3 evening commutes home.
    loyal_cycles = 3
    n_loyal_rides = N_LOYAL_PAIRS * 2 * loyal_cycles
    for rid, did in loyal:
        work = rng.choice(z_ids)               # the rider's steady workplace zone
        for _ in range(loyal_cycles):
            for hour in (8, 18):               # morning out, evening back
                pu = rider_home_map[rid] if hour == 8 else work
                do = work if hour == 8 else rider_home_map[rid]
                rows.append(_ride(rng, did, rid, hour, pu, do, dist, inc_norm,
                                  nightlife_z, pro_ids, rider_brack_map, DESERT_PENALTY))

    for _ in range(N_RIDES - n_loyal_rides):
        rid = rng.choice(rider_ids)
        roll = rng.random()
        if roll < 0.08:                        # airport run
            pu = rng.choice(z_ids); do = "ZJFK"
            hour = int(rng.choice([5, 6, 7, 15, 16, 17]))
            did = rng.choice(sorted(pro_ids)) if rng.random() < 0.8 else rng.choice(list(drivers.node_id))
        elif roll < 0.34:                      # nightlife
            pu = rng.choice(z_ids)
            do = rng.choice(sorted(nightlife_z))
            hour = int(rng.choice([19, 20, 21, 22, 23, 0, 1, 2]))
            did = rng.choice(list(drivers.node_id))
        else:                                  # ordinary daytime
            pu = rider_home_map[rid] if rng.random() < 0.5 else rng.choice(z_ids)
            do = rng.choice(z_ids)
            hour = int(rng.integers(7, 20))
            # pros skip low-income pickups; regulars take them (and wait longer)
            if inc_norm[pu] < 0.4 and rng.random() < 0.85:
                pool = [d for d in drivers.node_id if d not in pro_ids]
                did = rng.choice(pool)
            else:
                did = rng.choice(list(drivers.node_id))
        rows.append(_ride(rng, did, rid, hour, pu, do, dist, inc_norm,
                          nightlife_z, pro_ids, rider_brack_map, DESERT_PENALTY))

    edges = pd.DataFrame(rows)

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)
    zones.to_csv(HERE / "zones.csv", index=False)
    print(f"uber-manhattan: {len(nodes)} nodes ({N_DRIVERS} drivers + {N_RIDERS} riders), "
          f"{len(edges)} rides, {len(zones)} zones.")


def _ride(rng, did, rid, hour, pu, do, dist, inc_norm, nightlife_z, pro_ids,
          rider_brack_map, desert_penalty):
    d_km = dist(pu, do) * 0.9 + 0.4
    evening = hour >= 19 or hour <= 2
    surge = 1.0
    if pu in nightlife_z and evening:
        surge = round(float(np.clip(rng.normal(1.9, 0.4), 1.1, 3.2)), 2)
    elif evening:
        surge = round(float(np.clip(rng.normal(1.25, 0.2), 1.0, 2.0)), 2)
    elif do == "ZJFK":
        surge = round(float(np.clip(rng.normal(1.15, 0.15), 1.0, 1.8)), 2)

    desert = desert_penalty * (1 - inc_norm.get(pu, 0.6)) if pu != "ZJFK" else 0.0
    wait = float(np.clip(rng.normal(3.5, 1.0) + desert + (2.0 if evening else 0), 0.5, 28))

    base = 2.6 + 1.85 * d_km * surge + (9.0 if do == "ZJFK" else 0.0)
    fare = round(float(base + rng.normal(0, 1.2)), 2)
    rb = rider_brack_map.get(rid, "mid")
    rb_norm = {"low": 0.0, "mid": 0.5, "high": 1.0}[rb]
    tip = round(float(max(0.0, fare * (0.16 + 0.10 * rb_norm - 0.09 * (surge - 1))
                          + rng.normal(0, 0.6))), 2)
    return {
        "driver_id": did, "rider_id": rid, "hour": hour,
        "pickup_zone": pu, "dropoff_zone": do,
        "wait_min": round(wait, 1), "distance_km": round(d_km, 2),
        "fare": fare, "surge_mult": surge, "tip": tip,
    }


if __name__ == "__main__":
    main()
