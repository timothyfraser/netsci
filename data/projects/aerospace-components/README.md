# aerospace-components

*The bill-of-materials and supplier network behind one commercial aircraft
program — detail parts and firms roll up through sub-assemblies into major
systems.*

![Preview of the aerospace-components network](thumb.png)

## At a glance

| | |
|---|---|
| **Direction** | Directed (supply / build flow: detail parts & suppliers → final assembly) |
| **Weights** | Weighted (`qty_per_aircraft` — units installed per airframe) |
| **Modality** | Multimodal — 2 node kinds (`part` across BOM tiers 1–4, `supplier`) |
| **Temporal** | No — a single program snapshot |
| **Nodes** | 300 (258 part + 42 supplier) |
| **Edges** | 777 (399 `is_part_of` roll-ups + 378 `supplies`) |
| **Files** | `nodes.csv`, `edges.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

"Program X" is a stylized commercial-aircraft bill of materials. There are two
kinds of node:

- **`part`** — components and assemblies, with a `tier` giving BOM depth:
  tier 1 = major system assemblies, tier 2 = sub-assemblies, tier 3 = components,
  tier 4 = detail parts (fasteners, seals, fittings, bushings);
- **`supplier`** — firms that make or provide parts.

Edges are directed and point *up the build* toward the final airframe:

- `supplies` — a firm supplies a part (`supplier → part`);
- `is_part_of` — a deeper part rolls up into the assembly above it
  (`child part → parent part`).

Each edge carries `qty_per_aircraft` (the install quantity, an edge weight).
Parts carry a `system` (engine, avionics, fuselage, landing_gear, hydraulics,
interior), a `safety_critical` flag, a `single_source` flag, a `defect_rate`, and
a `cert_level`. Suppliers carry a `supplier_region` and a `defect_rate`.

This is a dependency-and-risk network. It rewards students who trace
dependencies *through* the BOM rather than counting connections. Some questions
to chew on:

- Which node, if it failed, would ground the most safety-critical assemblies?
  Would degree point you to it, or do you need to trace the build paths and run a
  knock-out / criticality analysis? Are the biggest suppliers the riskiest ones?
- Some safety-critical parts look dual-sourced. Are they *actually* redundant, or
  does the apparent redundancy collapse a hop or two upstream?
- Are defect rates spread evenly, or do they cluster — and if they cluster, by
  what (tier, system, region, a particular broker)? Does the pattern survive
  controlling for tier?
- Where does the heaviest certification burden sit, and is that the same place as
  the program's structural weak point?

> **Note.** The interesting findings here are deliberately *not* documented. "Deep
> parts have more parents" is the starting point, not a finding. Push past it —
> degree and a single sourcing column will both mislead you.

## `nodes.csv`

One row per node. Supplier rows leave the part-only columns (`tier`, `system`,
`cert_level`) blank; part rows leave `supplier_region` blank.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique key. `A1##`/`A2###` assembly parts, `C3###`/`C4###` components & detail parts, `S###` suppliers. Referenced by edges. | character | `A117`, `A2014`, `C4004`, `S031` |
| `kind` | Node kind | Whether the node is a part or a supplier firm. | character | `part`, `supplier` |
| `tier` | BOM tier | Build depth for parts: 1 = major assembly … 4 = detail part. Blank for suppliers. | integer | `1`, `3`, `4` |
| `system` | Aircraft system | Which system the part belongs to (blank for suppliers). | character | `engine`, `hydraulics`, `avionics` |
| `safety_critical` | Safety-critical flag | 1 if failure of this part is flight-safety relevant. | integer | `0`, `1` |
| `single_source` | Single-source flag | 1 if the part has only one qualified supplier. | integer | `0`, `1` |
| `supplier_region` | Supplier region | Home region of the supplier firm (blank for parts). | character | `USA`, `Europe`, `Japan`, `Mexico`, `China`, `India` |
| `defect_rate` | Defect rate | Observed fraction of units rejected / nonconforming. | double | `0.0029`, `0.0271`, `0.0807` |
| `cert_level` | Certification level | Highest certification the part is built to (blank for suppliers). | character | `standard`, `DO-178C`, `AS9100`, `NADCAP` |
| `label` | Display name | Human-readable label. (`name` is avoided — python-igraph reserves it for the ID.) | character | `Hydraulics Major Assy 17`, `Supplier 031 (Europe)` |

## `edges.csv`

One row per supply or roll-up relationship. Directed toward the final assembly.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | Source node ID | The supplier, or the deeper (child) part. | character | `S032`, `C4004` |
| `to_id` | Target node ID | The supplied part, or the parent assembly it rolls into. | character | `A2037`, `C3083` |
| `qty_per_aircraft` | Quantity per aircraft | Units of `from_id` installed per airframe (the edge weight). | integer | `10`, `22`, `120` |
| `relation` | Relation type | `supplies` (firm → part) or `is_part_of` (child part → parent). | character | `supplies`, `is_part_of` |

## Load it

```bash
Rscript data/projects/aerospace-components/load.R     # R    (igraph)
python  data/projects/aerospace-components/load.py     # Python (python-igraph)
```

Both build a directed, weighted `igraph` graph and print a one-screen summary. In
the [R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**aerospace-components** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/aerospace-components>
