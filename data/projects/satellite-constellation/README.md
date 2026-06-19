# satellite-constellation

*A single-instant snapshot of three operators' low-Earth-orbit (LEO) satellite
broadband networks: satellites linked to each other and down to ground gateways,
each link rated by capacity and latency.*

## At a glance

| | |
|---|---|
| **Direction** | Undirected (a radio/laser link carries traffic either way) |
| **Weights** | Weighted (`capacity_gbps` per link; `latency_ms` attribute) |
| **Modality** | Multimodal — 2 node kinds (`satellite`, `ground_station`) across 3 operators |
| **Temporal** | No — one frozen snapshot of all orbits at instant *t0* |
| **Nodes** | 298 (274 satellites + 24 ground stations) |
| **Edges** | 733 (210 intra-plane ISL + 199 inter-plane ISL + 2 cross-seam + 322 feeder) |
| **Files** | `nodes.csv`, `edges.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

Three fictional broadband operators — **Helios**, **Polaris**, and **Nimbus** —
each fly their own constellation of LEO **satellites**, arranged in orbital
*planes* with several satellites (*slots*) per plane. Some satellites talk
directly to their neighbors in space over **inter-satellite links** (ISLs);
traffic ultimately reaches the internet through **ground stations** (gateways) on
the surface via **feeder** links. A handful of gateways are neutral and shared by
all three operators; the rest belong to one operator. Each link carries a
throughput `capacity_gbps` (the edge weight) and a one-way `latency_ms`.
Satellites carry their orbital geometry (plane, slot, altitude, inclination,
RAAN, sub-satellite lat/lon), radio band, ISL capability, launch year, and
operational status; ground stations carry their region and capacity. This is a
frozen snapshot — every satellite is "parked" at the position its orbit puts it
in at instant *t0*.

This is a criticality, resilience, and equity network. It rewards students who
ask how the *architecture* of each operator changes what happens under stress.
Some questions to chew on:

- The three operators are built differently. If every ground station went dark at
  once, which operators keep talking to themselves in orbit, and which simply fall
  apart — and *why* does the answer differ by operator?
- A few links sit on a structural fault line in the orbital mesh. Can you find the
  links that carry far more routed traffic than their capacity or count suggests?
- Latency to a gateway is not the same everywhere. Is it explained by *where* a
  satellite is, even after you account for how many satellites are around?
- Which ground stations are single points of failure for their operator, and would
  degree, strength, and betweenness point you at the same ones?
- Run community detection. What do the communities correspond to, and which nodes
  end up acting as the bridges between them?
- Not every satellite is in the same shape. Is there a pattern to which ones are
  degraded, and does it line up with anything about the fleet's history?

> **Note.** The interesting findings here are deliberately *not* documented.
> "Bigger constellations have more links" is the starting point, not a finding.
> Push past it.

## `nodes.csv`

One row per node. Satellite rows leave `region` blank; ground-station rows leave
the orbital columns (`plane`, `slot`, `altitude_km`, `inclination_deg`,
`raan_deg`, `band`, `isl_capable`, `launch_year`, `status`) blank.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique key. `SAT####` satellite, `GS###` ground station. Referenced by edges. | character | `SAT0001`, `GS004` |
| `kind` | Node kind | Whether the node is in orbit or on the ground. | character | `satellite`, `ground_station` |
| `operator` | Operator | Owning operator; `neutral` for shared gateways. | character | `Helios`, `Polaris`, `Nimbus`, `neutral` |
| `plane` | Orbital plane | Index of the orbital plane the satellite is in (blank for ground stations). | integer | `0`, `5`, `11` |
| `slot` | Slot in plane | Position of the satellite within its plane (blank for ground stations). | integer | `0`, `6`, `10` |
| `altitude_km` | Altitude | Orbital altitude above the surface, kilometers (blank for ground stations). | double | `546.9`, `780.2`, `1200.4` |
| `inclination_deg` | Inclination | Orbital-plane inclination to the equator, degrees (blank for ground stations). | double | `53.02`, `86.41`, `88.0` |
| `raan_deg` | RAAN | Right ascension of the ascending node — the plane's orientation, degrees (blank for ground stations). | double | `0.0`, `90.0`, `157.5` |
| `region` | Region | Surface region of a ground station (blank for satellites). | character | `North America`, `Europe`, `East Asia` |
| `lat` | Latitude | Sub-satellite latitude (satellite) or site latitude (ground station), degrees. | double | `43.79`, `-29.97`, `50.12` |
| `lon` | Longitude | Sub-satellite longitude (satellite) or site longitude (ground station), degrees. | double | `19.19`, `-94.3`, `125.6` |
| `x` | X coordinate | Map X (= longitude), for plotting. | double | `19.19`, `-94.3` |
| `y` | Y coordinate | Map Y (= latitude), for plotting. | double | `43.79`, `50.12` |
| `band` | Radio/optical band | Primary link band of the satellite (blank for ground stations). | character | `optical`, `Ka`, `Ku` |
| `isl_capable` | ISL capable | 1 if the satellite has inter-satellite links, else 0 (blank for ground stations). | integer | `0`, `1` |
| `launch_year` | Launch year | Year the satellite was launched (blank for ground stations). | integer | `2019`, `2022`, `2025` |
| `status` | Status | Operational state of the satellite (blank for ground stations). | character | `active`, `degraded`, `spare` |
| `capacity_gbps` | Capacity (Gbps) | Per-node throughput capacity (satellite payload, or gateway backhaul). | double | `5.74`, `14.89`, `42.10` |
| `label` | Display name | Human-readable label. (`name` is avoided — python-igraph reserves it for the ID.) | character | `Helios 00-00`, `Europe GW 08` |

## `edges.csv`

One row per link. Undirected (`from_id`/`to_id` ordering is arbitrary).

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | Endpoint node ID | One end of the link. | character | `SAT0001`, `SAT0150` |
| `to_id` | Endpoint node ID | Other end of the link. | character | `SAT0002`, `GS004` |
| `link_type` | Link type | Kind of link: `intra_isl` (fore/aft neighbor in the same plane), `inter_isl` (to an adjacent plane), `crossseam` (spanning the orbital seam), `feeder` (satellite ↔ ground station). | character | `intra_isl`, `inter_isl`, `crossseam`, `feeder` |
| `capacity_gbps` | Link capacity (Gbps) | Throughput capacity of the link (the edge weight). | double | `8.04`, `15.36`, `28.10` |
| `latency_ms` | Latency | One-way link latency, milliseconds. | double | `17.0`, `33.7`, `41.2` |
| `band` | Band | Radio/optical band the link uses. | character | `optical`, `Ka`, `Ku` |

## Load it

```bash
Rscript data/projects/satellite-constellation/load.R     # R    (igraph)
python  data/projects/satellite-constellation/load.py     # Python (python-igraph)
```

Both build an undirected, weighted `igraph` graph and print a one-screen summary.
In the [R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**satellite-constellation** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/satellite-constellation>
