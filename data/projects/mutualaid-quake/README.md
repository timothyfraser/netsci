# mutualaid-quake

*Who helped whom in fictional "Eastvale" before, during, and after an
earthquake: a directed neighborhood mutual-aid network of residents and local
organizations.*

![Preview of the mutualaid-quake network](thumb.png)

## At a glance

| | |
|---|---|
| **Direction** | Directed (aid flows from giver → receiver) |
| **Weights** | Weighted (`amount` of aid per edge; `acts` = number of helping acts) |
| **Modality** | Multimodal — 2 node kinds (`resident`, `org`) |
| **Temporal** | Yes — one row per (giver, receiver, **period**: before / during / after) |
| **Nodes** | 250 (222 residents + 28 orgs) |
| **Edges** | 2,935 (before 325 · during 1,899 · after 711) |
| **Files** | `nodes.csv`, `edges.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

When the ground shook in **Eastvale**, neighbors started helping neighbors. This
network records directed acts of **mutual aid** — food, shelter, information, and
money passed from a giver to a receiver — across three periods: the ordinary days
**before** the quake, the acute shock **during** it, and the **after** recovery.
Nodes are individual **residents** (with block, income, tenure, age, and whether
they were civically active before the quake) and local **organizations** —
churches, schools, nonprofits, community centers. Eight sub-neighborhood blocks
(`B1`–`B8`) carve up the town. Each edge carries how much aid moved and how many
separate helping acts it represents.

This is a network for studying **social capital, brokerage, and recovery**. Some
questions worth chewing on:

- Who becomes a hub when disaster strikes? Are the people and places that carry
  the load *during* the shock the same ones who were central *before*?
- Does the *structure* of a sub-neighborhood predict how it fares afterward? Why
  do some blocks bounce back while one seems to stay starved?
- Money isn't everything. Is the wealthiest block also the best connected — or
  could resources and connectedness pull apart?
- Who sits on the most paths during the crisis? Are the key brokers obvious from
  their pre-quake standing, or do new leaders emerge?
- Does the surge of helping fade completely afterward, or does some of it stick —
  and does it stick evenly everywhere?

> **Note.** The interesting findings here are deliberately *not* documented.
> "Everyone helps more during a disaster" is the starting point, not a finding.
> Push past the obvious densification.

## `nodes.csv`

One row per node. Org rows leave the resident-only demographic columns blank.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique key. `P###` resident, `O###` organization. Referenced by edges. | character | `P001`, `O014` |
| `kind` | Node kind | Whether this node is a person or an organization. | character | `resident`, `org` |
| `block` | Sub-neighborhood block | Which of the eight Eastvale blocks the node sits in. | character | `B1`, `B6`, `B8` |
| `income` | Household income | Resident annual household income, USD (blank for orgs). | integer | `62711`, `143919` |
| `tenure` | Housing tenure | Whether the resident owns or rents (blank for orgs). | character | `homeowner`, `renter` |
| `age` | Age | Resident age in years (blank for orgs). | integer | `26`, `71` |
| `prior_civic` | Prior civic engagement | 1 if active in community orgs before the quake, else 0 (orgs are always 1). | integer | `0`, `1` |
| `label` | Display name | Human-readable label. (`name` is avoided — python-igraph reserves it for the ID.) | character | `Resident 001`, `Nonprofit 01` |

## `edges.csv`

One row per (giver, receiver, period). Directed: aid flows from `from_id` to
`to_id`.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | Giver node ID | Node providing the aid (joins to `nodes.csv`). | character | `P002`, `O014` |
| `to_id` | Receiver node ID | Node receiving the aid (joins to `nodes.csv`). | character | `P211`, `O014` |
| `period` | Period | Phase of the disaster the aid occurred in. | character | `before`, `during`, `after` |
| `amount` | Aid amount | Total aid given on this edge in the period (the edge weight; arbitrary units). | double | `20.9`, `120.8` |
| `acts` | Helping acts | Number of distinct helping acts that make up this edge. | integer | `1`, `2` |
| `aid_type` | Aid type | Dominant kind of aid exchanged. | character | `food`, `shelter`, `info`, `money` |
| `cross_block` | Cross-block flag | 1 if giver and receiver are in different blocks, else 0. | integer | `0`, `1` |

## Load it

```bash
Rscript data/projects/mutualaid-quake/load.R     # R    (igraph)
python  data/projects/mutualaid-quake/load.py     # Python (python-igraph)
```

Both build a directed, weighted `igraph` graph and print a one-screen summary. In
the [R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**mutualaid-quake** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/mutualaid-quake>
