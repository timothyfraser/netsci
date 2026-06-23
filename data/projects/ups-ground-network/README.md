# ups-ground-network

*A UPS-style ground line-haul network — large trucks move parcels between package
plants, from local centers up through regional hubs to national sort gateways.*

![Preview of the ups-ground-network network](thumb.png)

## At a glance

| | |
|---|---|
| **Direction** | Directed (a lane is one origin plant → one destination plant) |
| **Weights** | Weighted (`packages`; each lane also carries `trucks`, `distance_km`, `transit_hours`) |
| **Modality** | Multimodal — 3 plant kinds (`gateway`, `hub`, `center`) across the continental US |
| **Temporal** | No — a single daily snapshot (aggregated per lane) |
| **Nodes** | 149 plants (5 gateway + 36 hub + 108 center) |
| **Edges** | 347 directed lanes (one row per source-plant → destination-plant) |
| **Files** | `nodes.csv`, `edges.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

A stylized model of a parcel carrier's ground (truck) distribution network across
the continental US. Three kinds of plant:

- **`gateway`** — national sort hubs (the long-haul backbone, e.g. Louisville,
  Chicago, Dallas, Atlanta, Ontario CA);
- **`hub`** — regional metro hubs;
- **`center`** — local package centers (the origin / destination plants).

Each **edge is a lane aggregated at the source-plant → destination-plant level**:
one row per ordered pair (e.g. *Ithaca → Syracuse* moves 2,000-odd packages on a
couple of trucks). The lane weight is `packages`; the lane also records how many
`trucks` it takes, the `distance_km` between the two plants, and the
`transit_hours` in transit. Plants carry their coordinates (`x` = longitude,
`y` = latitude), a `region`, and a `daily_packages` throughput.

This is a flow-and-**resilience** network. Some questions to chew on:

- If one plant went dark for a day, which one would hurt the network most — and
  would degree, betweenness, or a knockout/criticality analysis agree? Is the
  busiest plant the most critical one?
- Are some regions one bad day away from being cut off from the rest of the
  country entirely? Which single closure would isolate the most plants?
- When a lane fails, how much longer (km and hours) is the next-best route? Where
  is rerouting cheap, and where is it ruinous?
- Trucks are finite. Which lanes are already running near full and have no slack
  to absorb a surge or a reroute?
- Does geography decide everything, or do some lanes carry far more than distance
  alone would predict?

> **Note.** The interesting findings here are deliberately *not* documented. "Big
> hubs move more packages" is the starting point, not a finding. Push past it —
> raw degree and raw volume will both mislead you.

## `nodes.csv`

One row per plant. Every node has every column populated.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique key. `G##` gateway, `H###` hub, `C###` center. Referenced by edges. | character | `G01`, `H001`, `C040` |
| `kind` | Plant kind | Role in the network. | character | `gateway`, `hub`, `center` |
| `region` | Region | US region the plant sits in. | character | `Northeast`, `Mid-Atlantic`, `Southeast`, `Midwest`, `South`, `Mountain`, `West` |
| `x` | Longitude | Plant longitude (decimal degrees). | double | `-85.76`, `-71.06` |
| `y` | Latitude | Plant latitude (decimal degrees). | double | `38.25`, `42.36` |
| `daily_packages` | Daily throughput | Nominal parcels handled per day at this plant. | integer | `130710`, `71515`, `29913` |
| `label` | Display name | Self-describing plant name: `<city> Gateway` / `<city> Hub` / `<town> Center`. (`name` is avoided — python-igraph reserves it for the ID.) | character | `Louisville KY Gateway`, `Syracuse NY Hub`, `Ithaca NY Center` |

## `edges.csv`

One row per **lane**, directed from the origin plant (`from_id`) to the
destination plant (`to_id`), aggregated over a day.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | Origin plant ID | Sending plant. | character | `C001`, `H001`, `G01` |
| `to_id` | Destination plant ID | Receiving plant. | character | `H001`, `C001`, `G04` |
| `packages` | Packages per day | Parcels moved on this lane per day (the edge weight). | integer | `5299`, `26493`, `4545` |
| `trucks` | Trucks per day | Large trucks dispatched on this lane per day. | integer | `8`, `25`, `7` |
| `distance_km` | Distance | Lane distance between the two plants, kilometres. | double | `56.7`, `3120.1`, `17.6` |
| `transit_hours` | Transit time | Door-to-door time in transit on the lane, hours. | double | `4.6`, `45.68`, `2.71` |

A useful derived quantity is **packages ÷ trucks** (parcels per truck): lanes near
the trailer's capacity have little slack to absorb a disruption.

## Load it

```bash
Rscript data/projects/ups-ground-network/load.R     # R    (igraph)
python  data/projects/ups-ground-network/load.py     # Python (python-igraph)
```

Both build a directed, weighted `igraph` graph and print a one-screen summary. In
the [R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**ups-ground-network** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/ups-ground-network>
