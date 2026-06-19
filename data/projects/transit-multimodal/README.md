# transit-multimodal

*A hypothetical city's public-transit network: neighborhoods linked by metro and
bus, with travel times, service frequency, and capacity on every link.*

## At a glance

| | |
|---|---|
| **Direction** | Undirected (a transit link runs both ways) |
| **Weights** | Weighted (`capacity` riders/hr; also `travel_time_min`, `frequency_per_hr`) |
| **Modality** | Multimodal / multiplex — two edge `mode`s (`metro`, `bus`); a pair may carry BOTH (parallel edges). `lines.csv` is a route lookup |
| **Temporal** | No — a single service snapshot (typical weekday) |
| **Nodes** | 152 neighborhoods |
| **Edges** | 384 links (81 metro + 303 bus) |
| **Files** | `nodes.csv`, `edges.csv`, `lines.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

Nodes are **neighborhoods** laid out on a 2D city map with a central business
district (CBD) at the middle and concentric rings of neighborhoods outward.
Edges are **transit links** between neighborhoods in two modes: a fast,
high-frequency, high-capacity **metro** that runs on a set of radial lines plus
ring lines, and a slower, lower-capacity **bus** mesh that covers many more
neighborhoods and feeds outer areas to the rail. Because the same pair of
neighborhoods can be connected by both a metro and a bus link, the graph is a
**multiplex** with parallel edges (use the `mode` attribute to tell them apart).
Each link records its travel time, how many vehicles run per hour, and its
hourly seat capacity (the primary edge weight). Each neighborhood records its
district, map position, population, median income, jobs, and whether it has a
metro station.

This is a natural home for **criticality**, **accessibility/equity**, and
**counterfactual ("what if we add a link?")** questions. Some things worth
investigating:

- Which neighborhoods are interchange **hubs**, and how fragile is the network if
  one of them goes down? Do the ring lines change the answer?
- Is access to jobs evenly distributed? Compute a job-access travel time or a
  gravity-accessibility score per neighborhood. Is what you see explained by
  population and distance from the center — or by *something about the
  neighborhoods*?
- Some neighborhoods are far better served than others at the same distance from
  downtown. What separates them?
- **Counterfactual:** if you could add a single new transit link anywhere, which
  one would most improve travel times for an underserved part of the city — and
  how does that compare to adding a random link?
- Project or partition the network: do districts behave as communities? Where are
  the structural gaps between them?

> **Note.** The interesting findings are deliberately undocumented. "Busy central
> neighborhoods have more service" is the starting point, not an answer. Look for
> the structure — and the gaps — underneath.

## `nodes.csv`

One row per neighborhood.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique key (`N###`). Referenced by edges. | character | `N003`, `N025`, `N127` |
| `label` | Label | Human-readable display name (district + number). | character | `CBD 003`, `East 025` |
| `district` | District | Which wedge of the city the neighborhood sits in. | character | `CBD`, `East`, `NorthWest` |
| `x` | X coordinate | Map x position (CBD is near the origin). | double | `0.051`, `-0.395` |
| `y` | Y coordinate | Map y position. | double | `-0.008`, `0.159` |
| `population` | Population | Residents in the neighborhood. | integer | `4539`, `22073` |
| `median_income` | Median household income | Neighborhood median income, USD. | integer | `129919`, `24000` |
| `jobs` | Jobs | Number of jobs located in the neighborhood. | integer | `66400`, `80` |
| `has_metro` | Has metro station | 1 if a metro line stops here, else 0. | integer | `1`, `0` |

## `edges.csv`

One row per transit link. Undirected link between `from_id` and `to_id`. The same
pair may appear twice with different `mode` (parallel edges = the multiplex).

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | From node ID | One endpoint neighborhood (joins to `nodes.csv`). | character | `N003`, `N025` |
| `to_id` | To node ID | Other endpoint neighborhood (joins to `nodes.csv`). | character | `N007`, `N047` |
| `mode` | Mode | Transit mode of the link. | character | `metro`, `bus` |
| `line` | Line / route | Line or route id this link belongs to (joins to `lines.csv`). | character | `M1`, `Ring`, `B045`, `F570` |
| `travel_time_min` | In-vehicle travel time | Minutes to ride this link (metro is faster than bus). | double | `2.0`, `3.5`, `17.8` |
| `frequency_per_hr` | Service frequency | Vehicles per hour on this link (higher = shorter wait). | double | `12.0`, `1.5`, `23.0` |
| `capacity` | Capacity | Seats offered per hour — the primary edge weight. | integer | `2544`, `120` |

## `lines.csv`

Lookup table for transit lines and bus routes (one row per line). Not a node
list — join it onto the `line` column in `edges.csv`.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `line_id` | Line ID | Unique line/route key. | character | `M1`, `Ring`, `OuterArc`, `B045` |
| `mode` | Mode | Mode the line operates. | character | `metro`, `bus` |
| `kind` | Line kind | Structural role of the line. | character | `radial`, `inner_ring`, `outer_ring_partial`, `local`, `feeder` |
| `label` | Label | Human-readable line name. | character | `Metro Line M1`, `Bus Route F570` |
| `n_stations` | Station count | Number of stops/stations on the line. | integer | `7`, `2` |

## Load it

```bash
Rscript data/projects/transit-multimodal/load.R     # R    (igraph, multimodal)
python  data/projects/transit-multimodal/load.py     # Python (python-igraph, multimodal)
```

Both build an undirected, weighted, multimodal `igraph` graph (edge weight =
`capacity`; `mode` distinguishes metro vs bus parallel edges) and print a
one-screen summary. In the
[R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**transit-multimodal** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/transit-multimodal>
