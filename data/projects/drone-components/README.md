# drone-components

*A functional dependency map of a small UAV (drone): which hardware components and
software modules require which others to work.*

## At a glance

| | |
|---|---|
| **Direction** | Directed (`from` requires → `to`) |
| **Weights** | Weighted (`coupling_strength` 1–5 = how tightly `from` is coupled to `to`) |
| **Modality** | Two node kinds (`hardware`, `software`), grouped into `subsystem` |
| **Temporal** | No — a single design snapshot |
| **Nodes** | 183 components (131 hardware, 52 software) |
| **Edges** | 617 "requires to function" relationships |
| **Files** | `nodes.csv`, `edges.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

Every node is a **component** of a drone — either a physical part (`hardware`:
motors, ESCs, battery, autopilot, IMUs, GPS, radios, camera, frame …) or a
`software` module (firmware, flight stack, sensor drivers, the EKF estimator, the
attitude controller, failsafe, telemetry stack …). A directed edge `A → B` means
*A depends on / requires B to function*: if B fails or is removed, A is impaired.
This is a **functional dependency graph** — a Design Structure Matrix view of
"what needs what" — not a supply chain. The edge weight, `coupling_strength`
(1–5), is how tightly A is bound to B. Each component carries its `kind`,
`subsystem`, `component_type`, `vendor`, a 1–5 `criticality` rating, a `redundant`
flag, and (for hardware) `mass_g` and `power_draw_w`.

This is a directed-graph **criticality, reachability, modularity, and
failure-propagation** playground. Some things worth investigating:

- The autopilot is the obvious hub by raw degree. But is the *most* critical node
  the one with the highest degree? Try ranking nodes by how many others can reach
  them *transitively*, or by betweenness, and see whether a different, quieter
  component rises to the top.
- Counterfactual disruption: remove one node and ask how much of the system gets
  stranded (can no longer reach what it needs). Does the biggest blast radius come
  from a high-degree node, or from one that degree analysis underrates?
- Is this graph acyclic? Look for strongly-connected components — feedback loops
  where two modules each depend on the other.
- Some components are flagged `redundant`. Check whether a redundant pair truly
  buys you independence, or whether both ultimately funnel into the same single
  downstream consumer.
- Does the system partition cleanly into `subsystem` modules (high modularity)?
  Which few cross-subsystem edges are the integration seams?
- Combine reach with `vendor` and `criticality`: is there a module the whole stack
  leans on that comes from a single vendor? What happens to a subsystem if you
  remove one vendor's parts entirely?

> **Note.** The interesting findings here are deliberately *not* documented.
> "The autopilot connects to everything" is the starting point, not a finding.
> Look at what raw degree alone hides.

## `nodes.csv`

One row per component.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique key referenced by edges. Spine parts get mnemonic ids; generic parts are `hw###` / `sw###`. | character | `mot1`, `fc`, `ekf`, `hw042`, `sw017` |
| `kind` | Component kind | Whether the node is a physical part or a software module. | character | `hardware`, `software` |
| `subsystem` | Subsystem | Functional group the component belongs to. | character | `propulsion`, `power`, `flight_control`, `navigation`, `software` |
| `component_type` | Component type | Finer-grained type within the subsystem. | character | `motor`, `esc`, `autopilot`, `estimator`, `sensor_driver` |
| `vendor` | Vendor | Supplier of the part / author of the module (~6 vendors). | character | `Aerex`, `Voltspan`, `NaviCore`, `PixHawk` |
| `criticality` | Criticality rating | Designer-assigned importance, 1 (minor) to 5 (flight-critical). | integer | `1`, `3`, `5` |
| `redundant` | Redundant flag | 1 if the part is nominally backed up by a sibling, else 0. | integer | `0`, `1` |
| `mass_g` | Mass (grams) | Component mass; blank for software. | double | `14.3`, `42.0`, `320.0` |
| `power_draw_w` | Power draw (watts) | Typical electrical draw; blank for software. | double | `0.3`, `1.82`, `4.46` |
| `label` | Display name | Human-readable label. (`name` is avoided — python-igraph reserves it for the ID.) | character | `Motor FL`, `Autopilot FC`, `EKF Estimator` |

## `edges.csv`

One row per dependency. Directed: `from_id` requires `to_id` to function.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | Dependent component ID | The component that has the dependency (joins to `nodes.csv`). | character | `esc1`, `ekf`, `mot2` |
| `to_id` | Required component ID | The component being depended on (joins to `nodes.csv`). | character | `pdb`, `imu_a`, `bec5v` |
| `dep_type` | Dependency type | Nature of the coupling. | character | `power`, `data`, `control`, `mechanical`, `software` |
| `coupling_strength` | Coupling strength | How tightly `from_id` is bound to `to_id`, 1 (loose) to 5 (tight). The edge weight. | integer | `1`, `3`, `5` |

## Load it

```bash
Rscript data/projects/drone-components/load.R     # R    (igraph)
python  data/projects/drone-components/load.py     # Python (python-igraph)
```

Both build a directed, weighted `igraph` graph (edge weight =
`coupling_strength`) and print a one-screen summary. In the
[R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**drone-components** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/drone-components>
