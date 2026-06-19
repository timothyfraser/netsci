"""Generate the `amazon-last-mile` project network (deterministic).

A one-week last-mile delivery network for a fictional metro area "Cascadia":
  - 4 fulfillment hubs        (kind = "hub")
  - 24 delivery stations      (kind = "station")
  - ~285 delivery zones       (kind = "zone")  -> ~313 nodes total

Edges are directed package flows, one row per (origin, destination, day):
  - line-haul   hub  -> station   (trucks moving bulk freight overnight)
  - last-mile   station -> zone   (vans delivering to neighborhoods)
weighted by `packages`, with a delivery-quality field `on_time_rate`.

Design parameters (the only record of the planted structure):
  - INCOME_PENALTY: on-time rate falls with zone income, *independent of
    distance*; same-day eligibility tracks income too.
  - OVERLOAD_STATION: one station is assigned far more zones than its
    capacity; its on-time rate is depressed and degrades hardest on the
    demand-spike day.
  - SPIKE_DAY (day 6): a ~2x volume surge ("Prime Day").
  - REASSIGN: a cluster of zones is moved from the overloaded station to a
    neighbor starting on day 4 (a structural rewiring mid-week).

Run:
    python data/projects/amazon-last-mile/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

N_HUBS = 4
N_STATIONS = 24
N_ZONES = 285
DAYS = list(range(1, 8))            # 1=Mon ... 7=Sun
SPIKE_DAY = 6
REGIONS = ["North", "South", "East", "West"]

# --- planted parameters -----------------------------------------------------
INCOME_PENALTY = 0.16     # max on-time reduction for the lowest-income zones
OVERLOAD_IDX = 7          # which station (0-based) is silently over capacity
OVERLOAD_PENALTY = 0.10   # on-time reduction at the overloaded station
SPIKE_PENALTY = 0.07      # extra on-time reduction on the spike day
REASSIGN_FROM = 7         # zones leave this station ...
REASSIGN_TO = 8           # ... and join this one, starting day 4
REASSIGN_DAY = 4


def main() -> None:
    rng = np.random.default_rng(SEED)

    # ----- hubs ------------------------------------------------------------
    hub_xy = rng.uniform(15, 85, size=(N_HUBS, 2))
    hubs = pd.DataFrame({
        "node_id": [f"H{i:02d}" for i in range(1, N_HUBS + 1)],
        "kind": "hub",
        "label": [f"Cascadia FC {chr(65+i)}" for i in range(N_HUBS)],
        "x": hub_xy[:, 0].round(2),
        "y": hub_xy[:, 1].round(2),
        "region": [REGIONS[i % 4] for i in range(N_HUBS)],
        "median_income": pd.NA,
        "population": pd.NA,
        "prime_rate": pd.NA,
        "capacity_pkgs": rng.integers(40000, 60000, N_HUBS),
    })

    # ----- stations --------------------------------------------------------
    st_xy = rng.uniform(5, 95, size=(N_STATIONS, 2))
    stations = pd.DataFrame({
        "node_id": [f"S{i:02d}" for i in range(1, N_STATIONS + 1)],
        "kind": "station",
        "label": [f"DS-{i:02d}" for i in range(1, N_STATIONS + 1)],
        "x": st_xy[:, 0].round(2),
        "y": st_xy[:, 1].round(2),
        "region": [REGIONS[int(y // 25.0001)] for y in st_xy[:, 1]],
        "median_income": pd.NA,
        "population": pd.NA,
        "prime_rate": pd.NA,
        # nominal daily capacity; the overloaded station gets the same cap but
        # far more demand than the rest.
        "capacity_pkgs": rng.integers(2200, 3200, N_STATIONS),
    })

    # ----- zones -----------------------------------------------------------
    z_xy = rng.uniform(0, 100, size=(N_ZONES, 2))
    # Income has a spatial gradient (richer to the west/north) PLUS noise, so
    # income is not perfectly readable from location.
    grad = 38000 + 520 * (100 - z_xy[:, 0]) + 300 * z_xy[:, 1]
    income = np.clip(grad + rng.normal(0, 9000, N_ZONES), 22000, 165000)
    income_norm = (income - income.min()) / (income.max() - income.min())
    population = rng.integers(900, 9000, N_ZONES)
    # Prime membership rises with income but is noisy.
    prime_rate = np.clip(0.25 + 0.45 * income_norm + rng.normal(0, 0.07, N_ZONES), 0.05, 0.95)

    zones = pd.DataFrame({
        "node_id": [f"Z{i:03d}" for i in range(1, N_ZONES + 1)],
        "kind": "zone",
        "label": [f"Zone {i:03d}" for i in range(1, N_ZONES + 1)],
        "x": z_xy[:, 0].round(2),
        "y": z_xy[:, 1].round(2),
        "region": [REGIONS[int(y // 25.0001)] for y in z_xy[:, 1]],
        "median_income": income.round(0).astype(int),
        "population": population,
        "prime_rate": prime_rate.round(3),
        "capacity_pkgs": pd.NA,
    })

    nodes = pd.concat([hubs, stations, zones], ignore_index=True)

    # ----- assign each zone to a station -----------------------------------
    # Nearest station, but the overloaded station "wins" any zone within a
    # generous radius -> it ends up with far more zones than its peers.
    st_pos = st_xy
    assign = np.empty(N_ZONES, dtype=int)
    for zi in range(N_ZONES):
        d = np.hypot(st_pos[:, 0] - z_xy[zi, 0], st_pos[:, 1] - z_xy[zi, 1])
        nearest = int(np.argmin(d))
        if d[OVERLOAD_IDX] < d[nearest] + 22:   # greedy land-grab
            nearest = OVERLOAD_IDX
        assign[zi] = nearest

    # zones to reassign to a neighbor partway through the week
    overload_zones = np.where(assign == REASSIGN_FROM)[0]
    reassigned = set(overload_zones[: max(1, len(overload_zones) // 3)].tolist())

    # ----- hub feeding each station ----------------------------------------
    hub_of_station = np.empty(N_STATIONS, dtype=int)
    for si in range(N_STATIONS):
        d = np.hypot(hub_xy[:, 0] - st_pos[si, 0], hub_xy[:, 1] - st_pos[si, 1])
        hub_of_station[si] = int(np.argmin(d))

    # ----- build edges -----------------------------------------------------
    DOW_FACTOR = {1: 1.05, 2: 1.00, 3: 1.00, 4: 1.02, 5: 1.10, 6: 2.0, 7: 0.7}
    last_mile_rows = []
    for day in DAYS:
        for zi in range(N_ZONES):
            # which station serves this zone today?
            st = assign[zi]
            if zi in reassigned and day >= REASSIGN_DAY:
                st = REASSIGN_TO

            dist = float(np.hypot(st_pos[st, 0] - z_xy[zi, 0], st_pos[st, 1] - z_xy[zi, 1]))
            base_demand = population[zi] * (0.012 + 0.05 * prime_rate[zi])
            lam = base_demand * DOW_FACTOR[day]
            pkgs = int(rng.poisson(max(lam, 1)))
            if pkgs == 0:
                continue

            # on-time rate: distance hurts a little; LOW INCOME hurts a lot
            # (independent of distance); overloaded station + spike day hurt.
            ot = 0.985 - 0.0011 * dist - INCOME_PENALTY * (1 - income_norm[zi])
            if st == OVERLOAD_IDX:
                ot -= OVERLOAD_PENALTY
            if day == SPIKE_DAY:
                ot -= SPIKE_PENALTY
                if st == OVERLOAD_IDX:
                    ot -= 0.05      # the overloaded station buckles hardest
            ot = float(np.clip(ot + rng.normal(0, 0.015), 0.40, 0.999))

            # same-day service offered mainly where income & prime are high
            same_day = (income_norm[zi] > 0.55 and prime_rate[zi] > 0.55)
            service = "same_day" if same_day else "standard"

            last_mile_rows.append({
                "from_id": f"S{st+1:02d}",
                "to_id": zones.at[zi, "node_id"],
                "day": day,
                "packages": pkgs,
                "on_time_rate": round(ot, 3),
                "distance_km": round(dist * 0.9, 2),
                "service": service,
            })

    last_mile = pd.DataFrame(last_mile_rows)

    # line-haul: hub -> station, weight = packages that station pushed that day
    haul_rows = []
    pushed = (last_mile.assign(st=last_mile["from_id"])
              .groupby(["st", "day"])["packages"].sum().reset_index())
    for _, r in pushed.iterrows():
        si = int(r["st"][1:]) - 1
        hub = hub_of_station[si]
        haul_rows.append({
            "from_id": f"H{hub+1:02d}",
            "to_id": r["st"],
            "day": int(r["day"]),
            "packages": int(r["packages"]),
            "on_time_rate": pd.NA,
            "distance_km": round(float(np.hypot(
                hub_xy[hub, 0] - st_pos[si, 0], hub_xy[hub, 1] - st_pos[si, 1])) * 0.9, 2),
            "service": "line_haul",
        })
    haul = pd.DataFrame(haul_rows)

    edges = pd.concat([haul, last_mile], ignore_index=True)

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)
    print(f"amazon-last-mile: {len(nodes)} nodes "
          f"({(nodes.kind=='hub').sum()} hubs + {(nodes.kind=='station').sum()} stations + "
          f"{(nodes.kind=='zone').sum()} zones), {len(edges)} edges "
          f"({len(haul)} line-haul + {len(last_mile)} last-mile).")


if __name__ == "__main__":
    main()
