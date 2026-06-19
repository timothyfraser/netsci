"""Generate the `drone-components` project network (deterministic).

A FUNCTIONAL dependency graph for a small UAV (drone): hardware components and
software modules, and which one *requires* which to function. This is a
dependency-type graph (a Design Structure Matrix / "what needs what to work"),
NOT a supply chain. A directed edge ``A -> B`` means *A depends on / requires B
to function* (if B fails, A is impaired). Edges are weighted by
``coupling_strength`` (1-5). Nodes are multimodal: ``kind`` in {hardware,
software}, grouped into a ``subsystem``.

Design parameters (the ONLY record of the planted structure; parameter-level):
  - HIDDEN_SPOF = the power-distribution board ("pdb"). It has only MODERATE
    direct degree, but an outsized share of nodes transitively depend on it
    (high transitive in-reach + betweenness), so degree alone misses it.
    Knocking it out strands a large fraction of the system.
  - FUSION_NODE = the single sensor-fusion / EKF estimator. Two "redundant"
    sensor pairs (dual IMUs, and GPS+RTK) BOTH feed this one node -> the
    redundancy is fake (common single downstream dependent).
  - CYCLE: the flight controller <-> ESC telemetry and estimator <-> controller
    form real cyclic dependencies, so the graph is NOT a clean DAG (SCC size>1).
  - MODULARITY: components cluster by subsystem (dense within, sparse across),
    with a few cross-subsystem couplings = integration risk seams.
  - LEGACY_MODULE = a critical legacy software module ("sensor driver core")
    with high downstream reach and a single vendor = bus-factor risk.
  - VENDOR_LOCKIN: one vendor's parts depend tightly on each other through a
    proprietary protocol; removing that vendor fragments its subsystem.

Run:
    python data/projects/drone-components/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

VENDORS = ["Aerex", "Voltspan", "NaviCore", "PixHawk", "SkyLink", "GimbalWorks"]

# --- planted parameters -----------------------------------------------------
N_FILLER_HW = 90        # extra generic hardware components (noise)
N_FILLER_SW = 40        # extra generic software modules (noise)
CROSS_LINK_P = 0.06     # base prob of a cross-subsystem coupling (integration seam)
WITHIN_LINK_P = 0.34    # prob of a within-subsystem coupling (modularity)
SPOF_FANIN = 34         # how many nodes the power board ultimately feeds (reach)
LEGACY_REACH = 30       # downstream consumers of the legacy driver core
VENDOR_LOCK_VENDOR = "NaviCore"   # the lock-in vendor (navigation/comms parts)


def main() -> None:
    rng = np.random.default_rng(SEED)

    # ----- the named "spine" components (the realistic UAV skeleton) --------
    # Each tuple: (node_id, kind, subsystem, component_type, label)
    spine = [
        # propulsion (4 motors + 4 ESCs + 4 props + mounts)
        ("mot1", "hardware", "propulsion", "motor", "Motor FL"),
        ("mot2", "hardware", "propulsion", "motor", "Motor FR"),
        ("mot3", "hardware", "propulsion", "motor", "Motor RL"),
        ("mot4", "hardware", "propulsion", "motor", "Motor RR"),
        ("esc1", "hardware", "propulsion", "esc", "ESC FL"),
        ("esc2", "hardware", "propulsion", "esc", "ESC FR"),
        ("esc3", "hardware", "propulsion", "esc", "ESC RL"),
        ("esc4", "hardware", "propulsion", "esc", "ESC RR"),
        ("prop1", "hardware", "propulsion", "propeller", "Prop FL"),
        ("prop2", "hardware", "propulsion", "propeller", "Prop FR"),
        ("prop3", "hardware", "propulsion", "propeller", "Prop RL"),
        ("prop4", "hardware", "propulsion", "propeller", "Prop RR"),
        ("mount1", "hardware", "propulsion", "motor_mount", "Mount FL"),
        ("mount2", "hardware", "propulsion", "motor_mount", "Mount FR"),
        ("mount3", "hardware", "propulsion", "motor_mount", "Mount RL"),
        ("mount4", "hardware", "propulsion", "motor_mount", "Mount RR"),
        # power
        ("battery", "hardware", "power", "battery", "LiPo Battery"),
        ("pdb", "hardware", "power", "power_distribution", "Power Dist Board"),
        ("bec5v", "hardware", "power", "regulator", "BEC 5V Rail"),
        ("bec12v", "hardware", "power", "regulator", "BEC 12V Rail"),
        ("harness", "hardware", "power", "wiring_harness", "Wiring Harness"),
        # flight_control
        ("fc", "hardware", "flight_control", "autopilot", "Autopilot FC"),
        ("imu_a", "hardware", "flight_control", "imu", "IMU A"),
        ("imu_b", "hardware", "flight_control", "imu", "IMU B"),
        ("accel", "hardware", "flight_control", "accelerometer", "Accelerometer"),
        ("gyro", "hardware", "flight_control", "gyroscope", "Gyroscope"),
        ("baro", "hardware", "flight_control", "barometer", "Barometer"),
        ("mag", "hardware", "flight_control", "magnetometer", "Compass"),
        # navigation
        ("gps", "hardware", "navigation", "gps", "GPS Receiver"),
        ("rtk", "hardware", "navigation", "rtk", "RTK Module"),
        ("optflow", "hardware", "navigation", "optical_flow", "Optical Flow"),
        # comms
        ("rx", "hardware", "comms", "rc_receiver", "RC Receiver"),
        ("telem", "hardware", "comms", "telemetry_radio", "Telemetry Radio"),
        ("ant_rc", "hardware", "comms", "antenna", "RC Antenna"),
        ("ant_telem", "hardware", "comms", "antenna", "Telem Antenna"),
        ("datalink", "hardware", "comms", "datalink", "Datalink Unit"),
        # payload
        ("camera", "hardware", "payload", "camera", "Camera"),
        ("gimbal", "hardware", "payload", "gimbal", "Gimbal"),
        ("lidar", "hardware", "payload", "lidar", "Lidar"),
        # airframe
        ("frame", "hardware", "airframe", "frame", "Airframe"),
        ("gear", "hardware", "airframe", "landing_gear", "Landing Gear"),
        # software
        ("firmware", "software", "software", "firmware", "Bootloader/Firmware"),
        ("flightstack", "software", "software", "flight_stack", "Flight Stack Scheduler"),
        ("drv_core", "software", "software", "sensor_driver", "Sensor Driver Core"),
        ("drv_imu", "software", "software", "sensor_driver", "IMU Driver"),
        ("drv_gps", "software", "software", "sensor_driver", "GPS Driver"),
        ("drv_baro", "software", "software", "sensor_driver", "Baro Driver"),
        ("ekf", "software", "software", "estimator", "EKF Estimator"),
        ("controller", "software", "software", "controller", "Attitude Controller"),
        ("mixer", "software", "software", "motor_mixer", "Motor Mixer"),
        ("failsafe", "software", "software", "failsafe", "Failsafe/Geofence"),
        ("telemstack", "software", "software", "telemetry_stack", "Telemetry Stack"),
        ("paramstore", "software", "software", "parameter_store", "Parameter Store"),
    ]

    spine_ids = [s[0] for s in spine]
    spine_set = set(spine_ids)

    # ----- generic filler nodes (noise) ------------------------------------
    hw_subsystems = ["propulsion", "power", "flight_control", "navigation",
                     "comms", "payload", "airframe"]
    hw_types = {
        "propulsion": ["motor", "esc", "propeller", "motor_mount", "fastener"],
        "power": ["regulator", "wiring_harness", "connector", "fuse", "capacitor"],
        "flight_control": ["sensor", "io_expander", "buzzer", "led", "switch"],
        "navigation": ["gps", "antenna", "ground_marker", "beacon"],
        "comms": ["antenna", "filter", "amplifier", "connector"],
        "payload": ["camera", "mount", "cable", "lens"],
        "airframe": ["arm", "standoff", "cover", "damper", "bracket"],
    }

    filler = []
    # sort the subsystem pool first so rng.choice ordering is deterministic
    for i in range(1, N_FILLER_HW + 1):
        sub = str(rng.choice(sorted(hw_subsystems)))
        ctype = str(rng.choice(sorted(hw_types[sub])))
        nid = f"hw{i:03d}"
        filler.append((nid, "hardware", sub, ctype, f"{ctype.title()} {i:03d}"))

    sw_types = ["sensor_driver", "service", "library", "logger", "watchdog",
                "calibration", "interface"]
    for i in range(1, N_FILLER_SW + 1):
        ctype = str(rng.choice(sorted(sw_types)))
        nid = f"sw{i:03d}"
        filler.append((nid, "software", "software", ctype, f"{ctype.title()} {i:03d}"))

    all_nodes = spine + filler
    node_id = np.array([n[0] for n in all_nodes])
    kind = np.array([n[1] for n in all_nodes])
    subsystem = np.array([n[2] for n in all_nodes])
    component_type = np.array([n[3] for n in all_nodes])
    label = np.array([n[4] for n in all_nodes])
    n = len(node_id)
    idx = {nid: i for i, nid in enumerate(node_id)}

    # ----- node attributes -------------------------------------------------
    vendor = rng.choice(VENDORS, size=n)
    criticality = rng.integers(1, 6, size=n)
    redundant = (rng.random(n) < 0.12).astype(int)

    mass_g = np.where(kind == "hardware",
                      np.clip(rng.gamma(2.0, 18.0, size=n), 1, 600).round(1),
                      np.nan)
    power_draw_w = np.where(kind == "hardware",
                            np.clip(rng.gamma(1.6, 1.4, size=n), 0.0, 60.0).round(2),
                            np.nan)

    # force realistic attributes for the named spine + planted nodes
    def setattrs(nid, **kw):
        i = idx[nid]
        for k, v in kw.items():
            if k == "vendor":
                vendor[i] = v
            elif k == "criticality":
                criticality[i] = v
            elif k == "redundant":
                redundant[i] = v
            elif k == "mass_g":
                mass_g[i] = v
            elif k == "power_draw_w":
                power_draw_w[i] = v

    # power board: moderate criticality LABEL on attributes (don't reveal SPOF)
    setattrs("pdb", vendor="Voltspan", criticality=3, redundant=0,
             mass_g=42.0, power_draw_w=1.2)
    setattrs("battery", vendor="Voltspan", criticality=5, redundant=0,
             mass_g=320.0, power_draw_w=0.0)
    setattrs("fc", vendor="PixHawk", criticality=5, redundant=0,
             mass_g=38.0, power_draw_w=2.5)
    setattrs("ekf", vendor="PixHawk", criticality=4, redundant=0)
    setattrs("controller", vendor="PixHawk", criticality=5, redundant=0)
    # dual IMUs marked redundant (the redundancy illusion)
    setattrs("imu_a", vendor="PixHawk", criticality=4, redundant=1,
             mass_g=4.0, power_draw_w=0.3)
    setattrs("imu_b", vendor="Aerex", criticality=4, redundant=1,
             mass_g=4.0, power_draw_w=0.3)
    # GPS + RTK also "redundant" position sources
    setattrs("gps", vendor="NaviCore", criticality=3, redundant=1)
    setattrs("rtk", vendor="NaviCore", criticality=3, redundant=1)
    # legacy driver core: single vendor, moderate criticality flag
    setattrs("drv_core", vendor="Aerex", criticality=3, redundant=0)
    # vendor lock-in cluster
    setattrs("datalink", vendor=VENDOR_LOCK_VENDOR)
    setattrs("telem", vendor=VENDOR_LOCK_VENDOR)
    setattrs("ant_telem", vendor=VENDOR_LOCK_VENDOR)
    setattrs("optflow", vendor=VENDOR_LOCK_VENDOR)

    # ----- build dependency edges ------------------------------------------
    edges = {}   # (src, dst) -> coupling_strength

    def add_edge(src, dst, w=None):
        if src == dst:
            return
        key = (src, dst)
        if w is None:
            w = int(np.clip(rng.integers(1, 6), 1, 5))
        # keep the strongest coupling if duplicated
        edges[key] = max(edges.get(key, 0), w)

    # ---- (1) realistic spine dependencies (domain-true) -------------------
    spine_edges = [
        # propulsion: motor needs ESC + mount + prop; ESC needs power + mixer
        ("mot1", "esc1", 5), ("mot2", "esc2", 5), ("mot3", "esc3", 5), ("mot4", "esc4", 5),
        ("mot1", "mount1", 4), ("mot2", "mount2", 4), ("mot3", "mount3", 4), ("mot4", "mount4", 4),
        ("mot1", "prop1", 3), ("mot2", "prop2", 3), ("mot3", "prop3", 3), ("mot4", "prop4", 3),
        ("esc1", "pdb", 5), ("esc2", "pdb", 5), ("esc3", "pdb", 5), ("esc4", "pdb", 5),
        ("esc1", "mixer", 4), ("esc2", "mixer", 4), ("esc3", "mixer", 4), ("esc4", "mixer", 4),
        # power chain
        ("pdb", "battery", 5),
        ("bec5v", "pdb", 5), ("bec12v", "pdb", 5),
        ("harness", "pdb", 3),
        ("pdb", "harness", 4),
        # flight control hardware powered via the 5V rail (-> pdb transitively)
        ("fc", "bec5v", 5),
        ("imu_a", "bec5v", 4), ("imu_b", "bec5v", 4),
        ("accel", "bec5v", 3), ("gyro", "bec5v", 3),
        ("baro", "bec5v", 3), ("mag", "bec5v", 3),
        ("fc", "firmware", 5),
        ("fc", "flightstack", 5),
        # sensors feed the FC / drivers
        ("imu_a", "drv_imu", 3), ("imu_b", "drv_imu", 3),
        ("accel", "imu_a", 2), ("gyro", "imu_a", 2),
        ("baro", "drv_baro", 3),
        ("mag", "drv_core", 2),
        # navigation hardware
        ("gps", "bec5v", 3), ("rtk", "bec5v", 3), ("optflow", "bec5v", 3),
        ("rtk", "gps", 4),
        ("gps", "drv_gps", 3), ("rtk", "drv_gps", 3),
        # comms
        ("rx", "bec5v", 3), ("telem", "bec5v", 3),
        ("rx", "ant_rc", 4), ("telem", "ant_telem", 4),
        ("datalink", "telem", 4),
        ("fc", "rx", 4),
        # payload
        ("camera", "bec12v", 4), ("gimbal", "bec12v", 4), ("lidar", "bec12v", 4),
        ("gimbal", "camera", 3),
        ("camera", "frame", 2), ("gimbal", "frame", 2),
        # airframe
        ("frame", "gear", 1),
        ("mount1", "frame", 3), ("mount2", "frame", 3),
        ("mount3", "frame", 3), ("mount4", "frame", 3),
        # ---- software stack ----
        ("flightstack", "firmware", 5),
        ("drv_imu", "drv_core", 5),
        ("drv_gps", "drv_core", 5),
        ("drv_baro", "drv_core", 5),
        ("drv_core", "firmware", 4),
        ("ekf", "drv_imu", 5),
        ("ekf", "drv_gps", 4),
        ("ekf", "drv_baro", 3),
        ("controller", "ekf", 5),
        ("mixer", "controller", 5),
        ("failsafe", "ekf", 4),
        ("failsafe", "rx", 3),
        ("failsafe", "controller", 3),
        ("telemstack", "telem", 4),
        ("telemstack", "ekf", 3),
        ("flightstack", "paramstore", 3),
        ("controller", "paramstore", 2),
        ("ekf", "paramstore", 2),
        ("mixer", "paramstore", 2),
        # FC software depends on FC hardware abstraction
        ("flightstack", "drv_core", 3),
    ]
    for s, d, w in spine_edges:
        add_edge(s, d, w)

    # ---- (2) REDUNDANCY ILLUSION: dual IMUs + GPS/RTK both feed single EKF -
    add_edge("ekf", "imu_a", 5)
    add_edge("ekf", "imu_b", 5)       # both IMUs -> same single EKF
    add_edge("ekf", "gps", 4)
    add_edge("ekf", "rtk", 4)         # both position sources -> same single EKF
    add_edge("ekf", "optflow", 3)

    # ---- (3) FEEDBACK LOOPS / CYCLES (graph is not a DAG) -----------------
    # controller <-> ekf (estimator uses control input feedforward)
    add_edge("ekf", "controller", 3)         # closes controller<->ekf loop
    # fc <-> esc telemetry: ESCs report back rpm/temp to the FC
    add_edge("fc", "esc1", 2)
    add_edge("esc1", "fc", 2)                 # closes fc<->esc1 loop
    # mixer -> esc -> ... and fc consumes mixer output via flightstack
    add_edge("flightstack", "mixer", 3)
    add_edge("mixer", "flightstack", 2)       # small scheduler<->mixer loop

    # ---- (4) HIDDEN SPOF: route a large share of nodes to power via pdb ----
    # Many hardware components draw power; we wire them to a rail (bec5v/bec12v/
    # harness) -> all rails depend on pdb -> pdb gets huge TRANSITIVE in-reach
    # while its DIRECT in-degree stays moderate (only the rails + escs touch it).
    rails = ["bec5v", "bec12v", "harness"]
    hw_idx = [i for i in range(n) if kind[i] == "hardware"
              and node_id[i] not in {"pdb", "battery"}]
    # choose ~SPOF_FANIN hardware nodes to draw from a rail (sorted for determinism)
    hw_pool = sorted(node_id[i] for i in hw_idx)
    chosen = rng.choice(hw_pool, size=min(SPOF_FANIN, len(hw_pool)), replace=False)
    for nid in chosen:
        rail = str(rng.choice(rails))
        add_edge(str(nid), rail, w=int(rng.integers(2, 5)))

    # ---- (5) LEGACY MODULE: drv_core gets high downstream reach -----------
    sw_pool = sorted(node_id[i] for i in range(n)
                     if kind[i] == "software" and node_id[i] != "drv_core")
    legacy_consumers = rng.choice(sw_pool, size=min(LEGACY_REACH, len(sw_pool)),
                                  replace=False)
    for nid in legacy_consumers:
        add_edge(str(nid), "drv_core", w=int(rng.integers(2, 6)))

    # ---- (6) VENDOR LOCK-IN: NaviCore parts depend on each other tightly --
    lock_nodes = [node_id[i] for i in range(n) if vendor[i] == VENDOR_LOCK_VENDOR
                  and subsystem[i] in {"navigation", "comms"}]
    lock_nodes = sorted(lock_nodes)
    # a proprietary datalink protocol: chain + mutual coupling within the vendor
    for a in range(len(lock_nodes)):
        for b in range(len(lock_nodes)):
            if a == b:
                continue
            if rng.random() < 0.45:
                add_edge(lock_nodes[a], lock_nodes[b], w=int(rng.integers(3, 6)))

    # Power-sink nodes: power flows strictly DOWN into them, so they must never
    # be the SOURCE of a noise edge (this keeps pdb the sole gateway to battery
    # = a genuine articulation point for power).
    POWER_SINKS = {"battery", "pdb", "bec5v", "bec12v", "harness"}

    # ---- (7) MODULARITY: dense within-subsystem, sparse cross-subsystem ----
    by_sub = {}
    for i in range(n):
        by_sub.setdefault(subsystem[i], []).append(node_id[i])
    for sub, members in by_sub.items():
        members = sorted(members)
        for a in members:
            for b in members:
                if a == b:
                    continue
                if rng.random() < WITHIN_LINK_P * 0.18:
                    if a in POWER_SINKS:
                        continue
                    add_edge(a, b, w=int(rng.integers(1, 4)))
    # sparse cross-subsystem integration seams
    all_sorted = sorted(node_id.tolist())
    for a in all_sorted:
        if rng.random() < CROSS_LINK_P:
            if a in POWER_SINKS:
                continue
            # pick a target in a DIFFERENT subsystem
            sa = subsystem[idx[a]]
            others = [x for x in all_sorted
                      if subsystem[idx[x]] != sa and x != a]
            if others:
                b = str(rng.choice(others))
                add_edge(a, b, w=int(rng.integers(1, 4)))

    # ---- (8) connect filler software to spine so they aren't isolated ------
    spine_sw = ["firmware", "flightstack", "drv_core", "ekf", "controller",
                "paramstore"]
    for i in range(n):
        if kind[i] == "software" and node_id[i].startswith("sw"):
            if rng.random() < 0.85:
                add_edge(node_id[i], str(rng.choice(sorted(spine_sw))),
                         w=int(rng.integers(1, 4)))
    # connect filler hardware to its subsystem spine anchor or a rail
    anchors = {"propulsion": "frame", "power": "bec5v", "flight_control": "fc",
               "navigation": "gps", "comms": "telem", "payload": "frame",
               "airframe": "frame"}
    for i in range(n):
        if kind[i] == "hardware" and node_id[i].startswith("hw"):
            if rng.random() < 0.80:
                anchor = anchors.get(subsystem[i], "frame")
                add_edge(node_id[i], anchor, w=int(rng.integers(1, 4)))

    # ----- emit ------------------------------------------------------------
    edge_rows = [{"from_id": s, "to_id": d, "dep_type": _dep_type(s, d, kind, idx,
                                                                  subsystem),
                  "coupling_strength": w}
                 for (s, d), w in edges.items()]
    edges_df = pd.DataFrame(edge_rows)
    # stable ordering
    edges_df = edges_df.sort_values(["from_id", "to_id"]).reset_index(drop=True)

    nodes = pd.DataFrame({
        "node_id": node_id,
        "kind": kind,
        "subsystem": subsystem,
        "component_type": component_type,
        "vendor": vendor,
        "criticality": criticality,
        "redundant": redundant,
        "mass_g": mass_g,
        "power_draw_w": power_draw_w,
        "label": label,
    })

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges_df.to_csv(HERE / "edges.csv", index=False)

    kinds = dict(pd.Series(kind).value_counts())
    print(f"drone-components: {len(nodes)} nodes "
          f"({kinds.get('hardware', 0)} hardware, {kinds.get('software', 0)} software), "
          f"{len(edges_df)} dependency edges.")


def _dep_type(src, dst, kind, idx, subsystem):
    """Infer a plausible dependency type for an edge (power/data/control/
    mechanical/software). Deterministic from the endpoints' kind/subsystem."""
    ks, kd = kind[idx[src]], kind[idx[dst]]
    ss, sd = subsystem[idx[src]], subsystem[idx[dst]]
    if dst in {"pdb", "battery", "bec5v", "bec12v", "harness"}:
        return "power"
    if ks == "software" and kd == "software":
        return "software"
    if kd == "software" or ks == "software":
        return "data"
    if sd == "propulsion" and dst.startswith(("esc", "mixer", "mot")):
        return "control"
    if dst in {"frame", "gear"} or dst.startswith("mount"):
        return "mechanical"
    if ss == "propulsion" or sd == "propulsion":
        return "control"
    return "data"


if __name__ == "__main__":
    main()
