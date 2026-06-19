# semiconductor-supply

*A multi-tier global semiconductor supply chain — raw materials and gases flow up
through fabs, packaging houses, and chip designers into finished electronic
products.*

## At a glance

| | |
|---|---|
| **Direction** | Directed (supply flow: upstream tier → downstream tier) |
| **Weights** | Weighted (`annual_volume`; paired `value_musd` and `lead_time_days`) |
| **Modality** | Multimodal — 5 node kinds across 5 tiers (`material`, `foundry`, `packaging`, `designer`, `product`) |
| **Temporal** | No — a single annual snapshot |
| **Nodes** | 368 (70 material + 46 foundry + 60 packaging + 96 designer + 96 product) |
| **Edges** | 739 supply relationships |
| **Files** | `nodes.csv`, `edges.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

"GlobalFab" is a stylized model of the world semiconductor supply chain. Supply
flows from the most upstream tier to the most downstream:

- **tier 4 `material`** — raw materials, specialty gases, silicon wafers,
  photoresist, sputter targets, bonding wire;
- **tier 3 `foundry`** — wafer fabrication plants ("fabs"), at process nodes from
  mature (28 nm) to leading-edge (3 nm);
- **tier 2 `packaging`** — assembly / test houses (OSATs), standard or advanced
  (2.5D/3D) packaging;
- **tier 1 `designer`** — chip designers and IDMs that place silicon orders;
- **tier 0 `product`** — end OEM products (phones, GPUs, servers, vehicles).

Each directed edge is a supply relationship weighted by `annual_volume` (units or
wafer-starts), with a dollar `value_musd` and a `lead_time_days`. Nodes carry a
`region`, a `tier`, a `capacity`, a nominal `lead_time_days`, and a `subtype`.

This is a flow-and-criticality network. It rewards students who look past which
nodes have the most connections. Some questions to chew on:

- If you could harden one node against disruption, which would it be — and would
  degree, betweenness, or a knockout/criticality analysis give you the same
  answer? Are the busiest suppliers the most important ones?
- Is the chain's resilience the same everywhere, or are some end products one bad
  day away from having no viable supply path at all?
- Does geography matter? If a region were embargoed or hit by a quake, how much
  downstream output would be cut, and through which tier?
- Recovery is not free: when the system is shocked, which nodes are also the
  slowest to come back?

> **Note.** The interesting findings here are deliberately *not* documented. "Big
> suppliers ship more volume" is the starting point, not a finding. Push past it —
> raw degree will mislead you.

## `nodes.csv`

One row per node (supplier or product). Every node has every column populated.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique key. `M###` material, `F###` foundry, `P###` packaging, `D###` designer, `E###` product. Referenced by edges. | character | `M001`, `F016`, `P007`, `D053`, `E030` |
| `kind` | Node kind | Tier role of the node. | character | `material`, `foundry`, `packaging`, `designer`, `product` |
| `tier` | Supply tier | Depth in the chain: 4 = most upstream (material) … 0 = end product. | integer | `4`, `3`, `0` |
| `region` | Region | Where the node operates. | character | `Taiwan`, `South Korea`, `USA`, `Japan`, `China`, `Europe` |
| `subtype` | Subtype | Kind-specific detail: material class, fab process node, packaging grade, designer/product segment. | character | `specialty_gas`, `5nm`, `advanced`, `gpu`, `router` |
| `capacity` | Capacity | Nominal annual throughput capacity (relative units). | integer | `3967`, `310`, `196` |
| `lead_time_days` | Lead time | Nominal replenishment / production lead time in days. | integer | `126`, `35`, `18` |
| `label` | Display name | Human-readable label. (`name` is avoided — python-igraph reserves it for the ID.) | character | `Specialty Gas Co 001`, `OSAT 007 (standard)` |

## `edges.csv`

One row per supply relationship. Directed from the upstream node (`from_id`) to
the downstream node (`to_id`).

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | Upstream node ID | Supplying node (higher tier). | character | `M001`, `D038`, `P039` |
| `to_id` | Downstream node ID | Receiving node (lower tier). | character | `F016`, `E049`, `D053` |
| `annual_volume` | Annual volume | Units / wafer-starts shipped on this relationship per year (the edge weight). | integer | `153`, `227`, `30` |
| `value_musd` | Annual value | Dollar value of the flow, millions USD. | double | `5.504`, `16.824` |
| `lead_time_days` | Edge lead time | Lead time for deliveries on this relationship, days. | integer | `126`, `49`, `29` |

## Load it

```bash
Rscript data/projects/semiconductor-supply/load.R     # R    (igraph)
python  data/projects/semiconductor-supply/load.py     # Python (python-igraph)
```

Both build a directed, weighted `igraph` graph and print a one-screen summary. In
the [R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**semiconductor-supply** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/semiconductor-supply>
