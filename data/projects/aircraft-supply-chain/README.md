# aircraft-supply-chain

*A multi-tier commercial-aircraft supply chain — raw materials flow up through
components and major systems into integrators and finished aircraft programs.*

![Preview of the aircraft-supply-chain network](thumb.png)

## At a glance

| | |
|---|---|
| **Direction** | Directed (supply flow: upstream tier → downstream tier) |
| **Weights** | Weighted (`units_per_year`; paired `value_musd` and `lead_time_days`) |
| **Modality** | Multimodal — 5 node kinds across 5 tiers (`material`, `component`, `system`, `integrator`, `program`) |
| **Temporal** | No — a single annual snapshot |
| **Nodes** | 300 (64 material + 86 component + 58 system + 44 integrator + 48 program) |
| **Edges** | 624 supply relationships |
| **Files** | `nodes.csv`, `edges.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

A stylized model of the commercial-aircraft (airplane) supply chain. Supply flows
from the most upstream tier to the most downstream:

- **tier 4 `material`** — raw materials: titanium, aluminium, CFRP composite,
  nickel superalloy, forgings, fasteners, avionics ICs;
- **tier 3 `component`** — parts / line-replaceable units: turbine blades, FADEC,
  actuators, avionics LRUs, fuel pumps, wiring harnesses, brackets;
- **tier 2 `system`** — major systems / structures: engine, avionics suite,
  flight controls, wing box, fuselage section, landing gear;
- **tier 1 `integrator`** — Tier-1 suppliers / major-section integrators & OEM
  final assembly;
- **tier 0 `program`** — end aircraft programs / fleets (narrowbody, widebody,
  regional jet, freighter, military transport).

Each directed edge is a supply relationship weighted by `units_per_year`
(shipsets / units per year), with a dollar `value_musd` and a `lead_time_days`.
Nodes carry a `region`, a `tier`, a `capacity`, a nominal `lead_time_days`, and a
`subtype`.

This is a flow-and-criticality network. It rewards students who look past which
nodes have the most connections. Some questions to chew on:

- If you could harden one node against disruption, which would it be — and would
  degree, betweenness, or a knockout/criticality analysis give you the same
  answer? Are the busiest suppliers the most important ones?
- Is the chain's resilience the same everywhere, or are some aircraft programs one
  bad day away from having no viable supply path at all?
- Does geography matter? If a region were hit by an export ban or a strike, how
  much downstream output would be cut, and through which tier?
- Recovery is not free: when the system is shocked, which nodes are also the
  slowest to come back?

> **Note.** The interesting findings here are deliberately *not* documented. "Big
> suppliers ship more volume" is the starting point, not a finding. Push past it —
> raw degree will mislead you.

## `nodes.csv`

One row per node (supplier, system, integrator, or program). Every node has every
column populated.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique key. `M###` material, `C###` component, `S###` system, `I###` integrator, `P###` program. Referenced by edges. | character | `M005`, `C027`, `S001`, `I023`, `P009` |
| `kind` | Node kind | Tier role of the node. | character | `material`, `component`, `system`, `integrator`, `program` |
| `tier` | Supply tier | Depth in the chain: 4 = most upstream (material) … 0 = end program. | integer | `4`, `3`, `0` |
| `region` | Region | Where the node operates. | character | `USA`, `Europe`, `Canada`, `Japan`, `Brazil`, `China` |
| `subtype` | Subtype | Kind-specific detail: material class, component type, system type, integrator/program segment. | character | `nickel_superalloy`, `turbine_blade`, `engine`, `narrowbody` |
| `capacity` | Capacity | Nominal annual throughput capacity (relative units). | integer | `2383`, `446`, `163` |
| `lead_time_days` | Lead time | Nominal replenishment / production lead time in days. | integer | `172`, `137`, `104` |
| `label` | Display name | Human-readable label. (`name` is avoided — python-igraph reserves it for the ID.) | character | `Titanium Co 001`, `Engine System 001` |

## `edges.csv`

One row per supply relationship. Directed from the upstream node (`from_id`) to
the downstream node (`to_id`).

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | Upstream node ID | Supplying node (higher tier). | character | `M005`, `C002`, `S014` |
| `to_id` | Downstream node ID | Receiving node (lower tier). | character | `C002`, `S001`, `P009` |
| `units_per_year` | Annual units | Shipsets / units shipped on this relationship per year (the edge weight). | integer | `238`, `82`, `63` |
| `value_musd` | Annual value | Dollar value of the flow, millions USD. | double | `40.611`, `29.573`, `23.543` |
| `lead_time_days` | Edge lead time | Lead time for deliveries on this relationship, days. | integer | `175`, `166`, `78` |

## Load it

```bash
Rscript data/projects/aircraft-supply-chain/load.R     # R    (igraph)
python  data/projects/aircraft-supply-chain/load.py     # Python (python-igraph)
```

Both build a directed, weighted `igraph` graph and print a one-screen summary. In
the [R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**aircraft-supply-chain** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/aircraft-supply-chain>
