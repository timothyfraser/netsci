# campus-contact

*Four weeks of face-to-face proximity on a university campus, recorded as a
respiratory illness moves through the population.*

![Preview of the campus-contact network](thumb.png)

## At a glance

| | |
|---|---|
| **Direction** | Undirected (a contact links two people who were co-located) |
| **Weights** | Weighted (`contact_minutes` per pair per week) |
| **Modality** | One node kind (`person`) with a `kind` role (student / faculty / staff) |
| **Temporal** | Yes — one row per (person, person, **week** 1–4); `status.csv` is per (person, week) |
| **Nodes** | 300 (252 students + 26 faculty + 22 staff) |
| **Edges** | 3,699 contact-weeks |
| **Files** | `nodes.csv`, `edges.csv`, `status.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

A campus **contact-tracing** network. Wearable proximity sensors logged who spent
time near whom, aggregated into weekly co-location contacts. Each edge carries the
total minutes a pair spent in proximity that week (`contact_minutes`), and edges
are tagged by `week` (1–4). Over the same four weeks a respiratory illness spread
through campus; the companion `status.csv` records, for every person and week,
whether they were infected by then. People carry a role (`kind`), a `unit` (their
dorm or academic department), and — for students — a class `year`.

This is the natural home for **community detection**, **centrality / criticality**,
**network-aware inference**, and **diffusion** questions. Some things worth digging
into:

- The contact graph is far from uniform. Does it break into communities, and do
  those communities line up with anything in `nodes.csv`?
- If you had to name the one person whose removal would most have slowed the spread
  between groups, who is it — and would degree alone have told you?
- Roles are not interchangeable. Do students, faculty, and staff sit in the same
  structural position, or do some of them do something the others don't?
- The four weeks are not the same. Does the contact structure change partway
  through, and does anything about the outbreak change at the same time?
- Who tends to get infected first? Is being infected early random, or is it
  predictable from where you sit in the network?

> **Note.** The interesting findings here are deliberately *not* documented. "People
> in the same dorm see each other a lot" is the starting point, not a finding. Push
> past it.

## `nodes.csv`

One row per person. The `year` column is blank for faculty and staff.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique key. `P###`. Referenced by edges and by `status.csv`. | character | `P001`, `P218`, `P300` |
| `kind` | Role | Which population the person belongs to. | character | `student`, `faculty`, `staff` |
| `unit` | Unit | Dorm (students) or department (faculty/staff) the person belongs to. | character | `West Hall`, `Engineering`, `Annex` |
| `year` | Class year | Student class year 1–4 (blank for faculty/staff). | integer | `1`, `4` |
| `label` | Display name | Human-readable label. (`name` is avoided — python-igraph reserves it for the ID.) | character | `Student 042`, `Faculty 03` |

## `edges.csv`

One row per (person, person, week). Undirected co-location contact.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | First person ID | One endpoint of the contact (joins to `nodes.csv`). | character | `P059` |
| `to_id` | Second person ID | The other endpoint (joins to `nodes.csv`). | character | `P088` |
| `week` | Study week | Week of the study, 1–4. | integer | `1`, `3` |
| `contact_minutes` | Contact minutes | Total minutes the pair spent in proximity that week (the edge weight). | integer | `44`, `19`, `207` |

## `status.csv`

Infection status, one row per (person, week). Not a node list — join it onto
`nodes.csv` on `node_id` (and filter or pivot on `week`).

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Person this status row describes (joins to `nodes.csv`). | character | `P001` |
| `week` | Study week | Week the status was observed, 1–4. | integer | `1`, `4` |
| `infected` | Infected flag | 1 if the person had been infected by this week (cumulative), else 0. | integer | `0`, `1` |

## Load it

```bash
Rscript data/projects/campus-contact/load.R     # R    (igraph)
python  data/projects/campus-contact/load.py     # Python (python-igraph)
```

Both build an undirected, weighted `igraph` graph (edge weight = `contact_minutes`)
and print a one-screen summary. Because the data is temporal, a pair can appear up
to four times (one per week) as parallel edges — filter to one `week` for a simple
graph. In the [R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**campus-contact** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/campus-contact>
