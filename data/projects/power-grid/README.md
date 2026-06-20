# power-grid

*A regional electrical transmission grid: buses (generators, substations, loads)
wired together by undirected transmission lines, each rated by capacity.*

![Preview of the power-grid network](thumb.png)

## At a glance

| | |
|---|---|
| **Direction** | Undirected (a transmission line carries power either way) |
| **Weights** | Weighted (`capacity_mw` per line; `length_km` attribute) |
| **Modality** | Single mode (`bus`), with a `kind` tag — `generator` / `substation` / `load` |
| **Temporal** | No — a single static snapshot of the grid |
| **Nodes** | 300 buses (57 generators + 101 substations + 142 loads) |
| **Edges** | 422 transmission lines |
| **Files** | `nodes.csv`, `edges.csv`, `regions.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

This is the transmission grid of a fictional utility split into three control
areas. Each **bus** is a node — a generating plant, a switching substation, or a
load center that draws power. Each undirected **transmission line** is an edge,
rated by its MW carrying `capacity_mw` and tagged with a `length_km`. Buses carry
a `capacity_mw` field (generation nameplate for generators, peak draw for loads),
a `voltage_kv` level, a region, and map coordinates. A companion `regions.csv`
names the three control areas.

This is a criticality-and-resilience network. It rewards students who ask what
happens when a piece fails. Some questions to chew on:

- If exactly one line went out, which one would hurt the most — and does line
  capacity, line length, or its position in the network tell you which?
- Where is the power *made* versus where is it *used*? Does the geography line up,
  and if not, what carries the difference?
- Is the whole grid built the same way, or are some areas looped-and-redundant
  while others hang off a single feed?
- Which bus is more important than it looks — central to the flow of power without
  being one of the biggest or most-connected nodes?
- If you had a maintenance budget for exactly one upgrade, where would betweenness,
  degree, and capacity each tell you to spend it — and would they agree?

> **Note.** The interesting findings here are deliberately *not* documented. "Big
> substations have more lines" is the starting point, not a finding. Push past it.

## `nodes.csv`

One row per bus.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique bus key. Referenced by edges. | character | `BUS0001`, `BUS0252` |
| `kind` | Bus kind | Role of the bus on the grid. | character | `generator`, `substation`, `load` |
| `region` | Control area | Which of the three control areas the bus sits in (join to `regions.csv`). | character | `A`, `B`, `C` |
| `label` | Display name | Human-readable label. (`name` is avoided — python-igraph reserves it for the ID.) | character | `Load 0001`, `Generator 0252` |
| `x` | X coordinate | Horizontal position on a 0–100 map grid. | double | `16.56`, `90.12` |
| `y` | Y coordinate | Vertical position on a 0–100 map grid. | double | `63.25`, `70.40` |
| `capacity_mw` | Capacity (MW) | Generation nameplate for generators, peak load draw for loads; ~0 for pass-through substations. | integer | `64`, `235`, `812` |
| `voltage_kv` | Voltage level | Nominal operating voltage of the bus, kilovolts. | integer | `69`, `230`, `500` |

## `edges.csv`

One row per transmission line. Undirected (`from_id`/`to_id` ordering is arbitrary).

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | Endpoint bus ID | One end of the line. | character | `BUS0092`, `BUS0023` |
| `to_id` | Endpoint bus ID | Other end of the line. | character | `BUS0098`, `BUS0092` |
| `capacity_mw` | Line capacity (MW) | Thermal carrying capacity of the line (the edge weight). | integer | `202`, `1500`, `1800` |
| `length_km` | Line length | Physical length of the line, kilometers. | double | `14.04`, `3.53` |

## `regions.csv`

Lookup table for the three control areas. Not a node list — join it onto
`nodes.csv` on `region`.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `region` | Region code | Control-area code, matches `nodes.region`. | character | `A`, `B`, `C` |
| `name` | Region name | Human-readable control-area name. | character | `Metro East Control Area`, `High Plains Control Area` |
| `center_x` | Center X | Approximate map-grid X of the area's center. | integer | `28`, `90` |
| `center_y` | Center Y | Approximate map-grid Y of the area's center. | integer | `55`, `70` |

## Load it

```bash
Rscript data/projects/power-grid/load.R     # R    (igraph)
python  data/projects/power-grid/load.py     # Python (python-igraph)
```

Both build an undirected, weighted `igraph` graph and print a one-screen summary.
In the [R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**power-grid** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/power-grid>
