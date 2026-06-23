# ups-package-flow

*The package-level companion to `ups-ground-network` — one row per individual
parcel, origin plant → destination plant, with its service, weight, distance, and
whether it arrived on time.*

![Preview of the ups-package-flow network](thumb.png)

## At a glance

| | |
|---|---|
| **Direction** | Directed (a parcel goes from its origin plant to its destination plant) |
| **Weights** | Weighted (`weight_kg`; each parcel also carries distance, transit, promise, on-time) |
| **Unit of analysis** | **The individual package** — one edge per parcel (a directed multigraph) |
| **Modality** | Multimodal plants (`gateway`, `hub`, `center`) across the continental US |
| **Temporal** | No — a single day of shipments |
| **Nodes** | 149 plants (5 gateway + 36 hub + 108 center) |
| **Edges** | 5,200 packages |
| **Files** | `nodes.csv`, `edges.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

This is the **disaggregated** view of the same parcel system as
[`ups-ground-network`](../ups-ground-network/). There, each row is a truck *lane*
(the unit of analysis is the truck). **Here, each row is a single package** — its
origin plant, its destination plant, and what happened to it. Group the package
rows by `(from_id, to_id)` and you get back a lane-level view; that round trip is
half the point.

Each parcel records its `service_level` (ground / two-day / overnight), its
`weight_kg`, the `distance_km` between origin and destination, the actual
`transit_hours`, the `promised_hours` for its service, whether it was `on_time`,
and whether it was `damaged`. Plants carry coordinates (`x` = longitude,
`y` = latitude), a `region`, and a daily throughput.

This is a service-performance and inference network. Some questions to chew on:

- Which plants are the worst to *ship to*? Rank destinations by on-time rate — and
  check whether that ranking just reflects how far away they are, or something
  else.
- Is there a service gap that survives controlling for distance and service level?
  Who eats it?
- Do cross-region parcels arrive late more often than within-region ones the same
  distance apart? Is the penalty the same for every service tier?
- Aggregate to lanes (sum packages, average transit) — does the busy-lane picture
  match the package-level one, or does aggregation hide who is being failed?
- Build a model to predict `on_time` from package + network features. What carries
  the signal — distance, service, destination, region crossing?

> **Note.** The interesting findings here are deliberately *not* documented.
> "Farther parcels take longer" is the starting point, not a finding. Push past it
> — control for the obvious things and see what's left.

## `nodes.csv`

One row per plant. Every node has every column populated.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique key. `G##` gateway, `H###` hub, `C###` center. Referenced by edges. | character | `G01`, `H001`, `C054` |
| `kind` | Plant kind | Role in the network. | character | `gateway`, `hub`, `center` |
| `region` | Region | US region the plant sits in. | character | `Northeast`, `Mid-Atlantic`, `Southeast`, `Midwest`, `South`, `Mountain`, `West` |
| `x` | Longitude | Plant longitude (decimal degrees). | double | `-85.76`, `-71.06` |
| `y` | Latitude | Plant latitude (decimal degrees). | double | `38.25`, `42.36` |
| `daily_packages` | Daily throughput | Nominal parcels handled per day at this plant. | integer | `130710`, `71515`, `4820` |
| `label` | Display name | Self-describing plant name: `<city> Gateway` / `<city> Hub` / `<town> Center`. (`name` is avoided — python-igraph reserves it for the ID.) | character | `Louisville KY Gateway`, `Boston MA Hub`, `Cambridge MA Center` |

## `edges.csv`

One row per **package**, directed from the origin plant (`from_id`) to the
destination plant (`to_id`).

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | Origin plant ID | Where the parcel was inducted. | character | `C054`, `C052`, `C092` |
| `to_id` | Destination plant ID | Where the parcel is delivered. | character | `C010`, `C047`, `C058` |
| `package_id` | Package ID | Unique parcel identifier. | character | `PKG000001`, `PKG005200` |
| `service_level` | Service level | Service tier purchased. | character | `ground`, `two_day`, `overnight` |
| `weight_kg` | Weight | Parcel weight, kilograms. | double | `1.21`, `3.18`, `12.4` |
| `distance_km` | Distance | Great-circle distance origin → destination, kilometres. | double | `361.4`, `2441.2` |
| `transit_hours` | Transit time | Actual time in transit, hours. | double | `30.23`, `32.08` |
| `promised_hours` | Promised time | Service commitment for this parcel, hours. | double | `30.6`, `48.0` |
| `on_time` | On time | 1 if `transit_hours <= promised_hours`, else 0. | integer | `1`, `0` |
| `damaged` | Damaged | 1 if the parcel was damaged in transit, else 0. | integer | `0`, `1` |

## Load it

```bash
Rscript data/projects/ups-package-flow/load.R     # R    (igraph)
python  data/projects/ups-package-flow/load.py     # Python (python-igraph)
```

Both build a directed, weighted `igraph` **multigraph** (one edge per package) and
print a one-screen summary. In the
[R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**ups-package-flow** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/ups-package-flow>
