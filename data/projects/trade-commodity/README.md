# trade-commodity

*World trade in a single strategic commodity ("refined metal", in tonnes) among
~140 countries, observed before, during, and after a major supply disruption.*

## At a glance

| | |
|---|---|
| **Direction** | Directed (export flow: exporter → importer) |
| **Weights** | Weighted (`tonnes` per edge; `price_usd_per_t` companion field) |
| **Modality** | Unimodal — one node kind (`country`) |
| **Temporal** | Yes — one row per (exporter, importer, **period**): `before` / `during` / `after` |
| **Nodes** | 140 (countries across 6 regional blocs) |
| **Edges** | 1,210 (≈422 before + ≈378 during + ≈410 after) |
| **Files** | `nodes.csv`, `edges.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

A directed, weighted trade network for one strategic commodity. Each **country**
both produces and consumes the commodity; a directed **export flow** carries
`tonnes` from an exporting country to an importing country, with a per-tonne
trade price attached. The world is observed across three **periods** — a normal
market (`before`), a market disrupted by a supply shock (`during`), and a
partially recovered market (`after`). Countries carry attributes for region/bloc,
GDP per capita, and domestic production and consumption capacity.

This is a flow, criticality, and community network with a built-in shock you can
study as a natural experiment. Some questions to chew on:

- Which importers are most exposed if a single supplier disappears? Is exposure
  about *how much* a country trades, or *how concentrated* its sources are?
- Does the trade map break into regional communities, and who are the few
  countries that bridge between blocs?
- If you ranked countries by how much trade *passes through* them, would that
  match a ranking by raw trade volume — or would different countries top each?
- The three periods are not the same world. What changed between them, who was
  hurt, and did anyone fail to recover?
- Whose removal would cut some group of countries off from supply entirely?

> **Note.** The interesting findings here are deliberately *not* documented.
> "Bigger economies trade more" is the starting point, not a finding. Push past it.

## `nodes.csv`

One row per country.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique country key (`C###`). Referenced by edges. | character | `C001`, `C047`, `C140` |
| `kind` | Node kind | Node type (all countries in this network). | character | `country` |
| `label` | Display name | Human-readable label (region prefix + index). (`name` is avoided — python-igraph reserves it for the ID.) | character | `NOR-001`, `SOU-031`, `EUR-061` |
| `region` | Region / bloc | Continental trade bloc the country belongs to. | character | `North America`, `Africa`, `Asia-Pacific` |
| `gdp_per_capita` | GDP per capita | National income per person, USD. | integer | `54442`, `43966`, `14354` |
| `production` | Production | Domestic output capacity of the commodity, tonnes. | double | `7016`, `33045`, `15239` |
| `consumption` | Consumption | Domestic demand for the commodity, tonnes. | double | `52860`, `11350`, `31147` |

## `edges.csv`

One row per (exporter, importer, period). Directed; a pair can appear up to three
times (once per period).

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `exporter_id` | Exporter node ID | Country sending the commodity. | character | `C004`, `C047` |
| `importer_id` | Importer node ID | Country receiving the commodity. | character | `C001`, `C007` |
| `period` | Period | Market era: `before`, `during`, or `after` the supply disruption. | character | `before`, `during`, `after` |
| `tonnes` | Tonnes traded | Quantity moved on that edge in that period (the edge weight). | integer | `78`, `1340`, `40285` |
| `price_usd_per_t` | Price per tonne | Trade price for that flow, USD per tonne. | integer | `889`, `974`, `1183` |

## Load it

```bash
Rscript data/projects/trade-commodity/load.R     # R    (igraph)
python  data/projects/trade-commodity/load.py     # Python (python-igraph)
```

Both build a directed, weighted `igraph` graph and print a one-screen summary. In
the [R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**trade-commodity** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/trade-commodity>
