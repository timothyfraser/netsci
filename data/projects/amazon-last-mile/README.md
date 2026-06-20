# amazon-last-mile

*One week of package flow through a fictional metro's last-mile delivery network:
fulfillment hubs → delivery stations → neighborhood zones.*

![Preview of the amazon-last-mile network](thumb.png)

## At a glance

| | |
|---|---|
| **Direction** | Directed (package flow: hub → station → zone) |
| **Weights** | Weighted (`packages` per edge; `on_time_rate` quality field) |
| **Modality** | Multimodal — 3 node kinds (`hub`, `station`, `zone`) |
| **Temporal** | Yes — one row per (origin, destination, **day** 1–7) |
| **Nodes** | 313 (4 hubs + 24 stations + 285 zones) |
| **Edges** | 2,142 (147 line-haul + 1,995 last-mile) |
| **Files** | `nodes.csv`, `edges.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

"Cascadia Logistics" runs a metro delivery operation. Bulk freight moves overnight
from **fulfillment hubs** to local **delivery stations** (the *line-haul* leg), then
vans fan out from each station to the **neighborhood zones** it serves (the
*last-mile* leg). Every delivery edge carries a package count and an on-time
delivery rate, recorded daily across one week. Zones carry demographic attributes
(median income, population, Prime-membership rate); stations and hubs carry
throughput capacity.

This is a flow-and-criticality network with a temporal dimension. It rewards
students who look past raw volume. Some questions to chew on:

- Who actually bears delivery risk? Is on-time performance explained by distance,
  or by *something about the neighborhoods themselves*?
- Is any single station carrying more than its share of the network — and what
  happens to it under stress?
- The week is not uniform. Does the network behave the same on every day, or does
  a demand surge expose a weak point?
- Does the *structure* of who-serves-whom stay fixed across the week, or does it
  change partway through?
- If you had to harden this system against a one-day outage, which node would you
  protect first — and would degree, betweenness, or load tell you the same answer?

> **Note.** The interesting findings here are deliberately *not* documented. "Busier
> zones get more packages" is the starting point, not a finding. Push past it.

## `nodes.csv`

One row per node. Hub/station rows leave the zone-only demographic columns blank;
zone rows leave `capacity_pkgs` blank.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique key. `H##` hub, `S##` station, `Z###` zone. Referenced by edges. | character | `H03`, `S14`, `Z001` |
| `kind` | Node kind | Tier of the network this node sits in. | character | `hub`, `station`, `zone` |
| `label` | Display name | Human-readable label. (`name` is avoided — python-igraph reserves it for the ID.) | character | `Cascadia FC C`, `DS-14`, `Zone 001` |
| `x` | X coordinate | Horizontal position on a 0–100 metro grid. | double | `21.59`, `69.18` |
| `y` | Y coordinate | Vertical position on a 0–100 metro grid. | double | `83.29`, `40.85` |
| `region` | Region | Metro quadrant the node falls in. | character | `North`, `South`, `East`, `West` |
| `median_income` | Median household income | Zone median income in USD (blank for hubs/stations). | integer | `79554`, `41220` |
| `population` | Population | Residents served by the zone (blank for hubs/stations). | integer | `7665`, `2310` |
| `prime_rate` | Prime membership rate | Fraction of the zone that are Prime members (blank for hubs/stations). | double | `0.39`, `0.71` |
| `capacity_pkgs` | Daily package capacity | Nominal throughput capacity (blank for zones). | integer | `50264`, `2740` |

## `edges.csv`

One row per (origin, destination, day). Directed. `line_haul` rows have no
`on_time_rate` (it is a quality measure of last-mile delivery only).

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | Origin node ID | Sending node (`H##` for line-haul, `S##` for last-mile). | character | `H03`, `S08` |
| `to_id` | Destination node ID | Receiving node (`S##` for line-haul, `Z###` for last-mile). | character | `S01`, `Z002` |
| `day` | Day of week | 1 = Monday … 7 = Sunday. | integer | `1`, `6` |
| `packages` | Packages | Number of packages moved on that edge that day (the edge weight). | integer | `3827`, `131` |
| `on_time_rate` | On-time delivery rate | Share of last-mile packages delivered on time (blank for line-haul). | double | `0.865`, `0.724` |
| `distance_km` | Distance | Road distance between the two nodes, kilometers. | double | `15.79`, `9.29` |
| `service` | Service type | `line_haul`, or last-mile `standard` / `same_day`. | character | `line_haul`, `standard`, `same_day` |

## Load it

```bash
Rscript data/projects/amazon-last-mile/load.R     # R    (igraph)
python  data/projects/amazon-last-mile/load.py     # Python (python-igraph)
```

Both build a directed, weighted `igraph` graph and print a one-screen summary. In
the [R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**amazon-last-mile** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/amazon-last-mile>
