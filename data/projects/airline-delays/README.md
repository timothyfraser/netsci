# airline-delays

*One operating day of a domestic carrier's route network, sliced into four time
blocks: directed flights between airports, each carrying a flight count and an
average departure delay.*

## At a glance

| | |
|---|---|
| **Direction** | Directed (flights fly origin → destination) |
| **Weights** | Weighted (`number_of_flights` per edge; `delay_min` quality field) |
| **Modality** | Unimodal — one node kind (`airport`) |
| **Temporal** | Yes — one row per (origin, destination, **block**: morning/midday/afternoon/evening) |
| **Nodes** | 200 airports (6 hubs) |
| **Edges** | 2,244 (561 directed routes × 4 blocks) |
| **Files** | `nodes.csv`, `edges.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

"Meridian Air" flies a domestic schedule across five regions. Each **airport** is
a node; each directed **flight route** is an edge, recorded in four time blocks
across one day (morning → midday → afternoon → evening). An edge's weight is the
number of flights on that leg in that block, and each edge also carries the
average departure `delay_min` for that leg and block. Airports carry a hub flag,
region, runway count, a weather-exposure score, and rough map coordinates.

This is a flow-and-resilience network with a temporal dimension. It rewards
students who track how disruption moves through a system. Some questions to chew
on:

- The day is not uniform. Does delay stay put, or does a bad block at one airport
  show up somewhere else in the *next* block?
- Are all the big hubs equally fragile, or does one shrug off trouble that
  flattens another?
- If you had to protect one airport to keep regions reachable, which would it be —
  and would flight volume, degree, or betweenness point you to the same node?
- When delays correlate between two airports, is it because they are close
  together on the map, or because they are wired together by routes?
- Which airports are big because they are *busy* versus big because they are
  *structurally important*?

> **Note.** The interesting findings here are deliberately *not* documented.
> "Busy hubs handle more flights" is the starting point, not a finding. Push past
> it.

## `nodes.csv`

One row per airport.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique 3-letter airport code (fictional). Referenced by edges. | character | `ABK`, `AGC`, `AAY` |
| `kind` | Node kind | Always `airport` (single-mode network). | character | `airport` |
| `label` | Display name | Human-readable label. (`name` is avoided — python-igraph reserves it for the ID.) | character | `ABK International`, `AFO Regional` |
| `region` | Region | Geographic region the airport sits in. | character | `Northeast`, `Midwest`, `West` |
| `hub` | Hub flag | 1 if the airport is a hub, else 0. | integer | `0`, `1` |
| `runways` | Runways | Number of runways (capacity proxy). | integer | `2`, `5` |
| `weather_exposure` | Weather exposure | Propensity to weather disruption, 0–1. | double | `0.31`, `0.74` |
| `x` | X coordinate | Horizontal position on a 0–100 map grid. | double | `54.12`, `13.88` |
| `y` | Y coordinate | Vertical position on a 0–100 map grid. | double | `60.40`, `49.07` |

## `edges.csv`

One row per (origin, destination, block). Directed.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | Origin airport ID | Departing airport. | character | `ABK`, `AGC` |
| `to_id` | Destination airport ID | Arriving airport. | character | `AAB`, `AEZ` |
| `block` | Time block | Part of the operating day: `morning`, `midday`, `afternoon`, `evening`. | character | `midday`, `evening` |
| `number_of_flights` | Number of flights | Flights on that leg in that block (the edge weight). | integer | `3`, `11` |
| `seats` | Seats | Total scheduled seats on that leg in that block. | integer | `412`, `1830` |
| `delay_min` | Average departure delay | Mean departure delay on that leg in that block, minutes. | double | `8.4`, `61.2` |

## Load it

```bash
Rscript data/projects/airline-delays/load.R     # R    (igraph)
python  data/projects/airline-delays/load.py     # Python (python-igraph)
```

Both build a directed, weighted `igraph` graph and print a one-screen summary. In
the [R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**airline-delays** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/airline-delays>
