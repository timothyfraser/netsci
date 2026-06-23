# satellite-supply-chain

*A multi-tier satellite manufacturing supply chain — space-grade materials flow up
through components and subsystems into integrators and finished space programs.*

![Preview of the satellite-supply-chain network](thumb.png)

## At a glance

| | |
|---|---|
| **Direction** | Directed (supply flow: upstream tier → downstream tier) |
| **Weights** | Weighted (`units_per_year`; paired `value_musd` and `lead_time_days`) |
| **Modality** | Multimodal — 5 node kinds across 5 tiers (`material`, `component`, `subsystem`, `integrator`, `program`) |
| **Temporal** | No — a single annual snapshot |
| **Nodes** | 276 (60 material + 72 component + 54 subsystem + 42 integrator + 48 program) |
| **Edges** | 562 supply relationships |
| **Files** | `nodes.csv`, `edges.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

A stylized model of the global spacecraft (satellite) supply chain. Supply flows
from the most upstream tier to the most downstream:

- **tier 4 `material`** — space-grade raw materials: radiation-hardened wafers,
  solar cells, propellant, composite prepreg, battery cells, optics blanks;
- **tier 3 `component`** — units / "black boxes": star trackers, reaction wheels,
  rad-hard on-board computers, TWT amplifiers, harnesses, structure panels;
- **tier 2 `subsystem`** — spacecraft subsystems: ADCS (attitude), comms payload,
  command & data handling, structure, thermal, power;
- **tier 1 `integrator`** — satellite-bus integrators / prime contractors;
- **tier 0 `program`** — end programs / operators (broadband constellations,
  government comsats, navigation, earth observation, deep-space probes).

Each directed edge is a supply relationship weighted by `units_per_year`, with a
dollar `value_musd` and a `lead_time_days`. Nodes carry a `region`, a `tier`, a
`capacity`, a nominal `lead_time_days`, and a `subtype`.

This is a flow-and-criticality network. It rewards students who look past which
nodes have the most connections. Some questions to chew on:

- If you could harden one node against disruption, which would it be — and would
  degree, betweenness, or a knockout/criticality analysis give you the same
  answer? Are the busiest suppliers the most important ones?
- Is the chain's resilience the same everywhere, or are some end programs one bad
  day away from having no viable supply path at all?
- Does geography matter? If a region were embargoed or hit by an export ban, how
  much downstream output would be cut, and through which tier?
- Recovery is not free: when the system is shocked, which nodes are also the
  slowest to come back?

> **Note.** The interesting findings here are deliberately *not* documented. "Big
> suppliers ship more volume" is the starting point, not a finding. Push past it —
> raw degree will mislead you.

## `nodes.csv`

One row per node (supplier, subsystem, integrator, or program). Every node has
every column populated.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique key. `M###` material, `C###` component, `S###` subsystem, `I###` integrator, `P###` program. Referenced by edges. | character | `M001`, `C031`, `S019`, `I012`, `P033` |
| `kind` | Node kind | Tier role of the node. | character | `material`, `component`, `subsystem`, `integrator`, `program` |
| `tier` | Supply tier | Depth in the chain: 4 = most upstream (material) … 0 = end program. | integer | `4`, `3`, `0` |
| `region` | Region | Where the node operates. | character | `USA`, `Europe`, `Japan`, `India`, `China`, `Other` |
| `subtype` | Subtype | Kind-specific detail: material class, component type, subsystem type, integrator/program segment. | character | `radhard_wafer`, `star_tracker`, `adcs`, `broadband_constellation` |
| `capacity` | Capacity | Nominal annual throughput capacity (relative units). | integer | `1870`, `1320`, `33` |
| `lead_time_days` | Lead time | Nominal replenishment / production lead time in days. | integer | `181`, `113`, `47` |
| `label` | Display name | Human-readable label. (`name` is avoided — python-igraph reserves it for the ID.) | character | `Radhard Wafer Co 001`, `ADCS Subsystem 019` |

## `edges.csv`

One row per supply relationship. Directed from the upstream node (`from_id`) to
the downstream node (`to_id`).

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | Upstream node ID | Supplying node (higher tier). | character | `M001`, `C003`, `S027` |
| `to_id` | Downstream node ID | Receiving node (lower tier). | character | `C003`, `S019`, `P033` |
| `units_per_year` | Annual units | Units shipped on this relationship per year (the edge weight). | integer | `164`, `29`, `16` |
| `value_musd` | Annual value | Dollar value of the flow, millions USD. | double | `50.396`, `3.096`, `2.585` |
| `lead_time_days` | Edge lead time | Lead time for deliveries on this relationship, days. | integer | `181`, `120`, `95` |

## Load it

```bash
Rscript data/projects/satellite-supply-chain/load.R     # R    (igraph)
python  data/projects/satellite-supply-chain/load.py     # Python (python-igraph)
```

Both build a directed, weighted `igraph` graph and print a one-screen summary. In
the [R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**satellite-supply-chain** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/satellite-supply-chain>
