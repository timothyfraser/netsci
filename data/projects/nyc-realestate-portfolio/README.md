# nyc-realestate-portfolio

*A New York City commercial-real-estate portfolio as a network: properties linked when they share an equity backer — so you can see where financing is diversified and where it is dangerously concentrated.*

## At a glance

| | |
|---|---|
| **Direction** | Undirected |
| **Weights** | Yes — `co_investment_usd` (shared capital across the tie) |
| **Modality** | Unimodal (properties only) |
| **Temporal** | No (a single cumulative snapshot) |
| **Nodes** | 190 properties |
| **Edges** | 1,155 shared-financing ties |
| **Files** | `nodes.csv`, `edges.csv` |

## What this network is

Each node is a commercial property in NYC. Two properties are connected when they
share **at least one common equity investor** — i.e. they sit inside the same
ownership/financing portfolio and are, in effect, cross-collateralized. Edge
weight (`co_investment_usd`) is how much shared capital ties them together. Debt
lenders (banks) are intentionally **excluded** from the projection: they are
near-ubiquitous and would turn the graph into a hairball, hiding the structure
that matters.

The modeling premise is a real one in portfolio finance: **fewer shared-financing
ties is usually healthier** — a property whose backers are independent of everyone
else's fails alone. Dense, tightly shared clusters mean correlated risk: one
backer in trouble can drag a whole neighborhood of buildings down with it.
Sometimes shared financing reflects healthy diversification; sometimes it reflects
dangerous concentration. Telling those apart is the work.

This dataset is **derived from** `nyc-realestate-capital` and shares its property
`node_id`s exactly, so you can join the two: bring each property's appraised value,
investor mix, and quarterly invested/pledged totals onto these nodes.

Example project questions:
- Which properties are the **most central** in the portfolio (highest degree /
  betweenness)? Are they the most valuable ones, or something else?
- Run **community detection** — do the financing clusters line up with
  neighborhood, borough, or property type? Which cluster is most concentrated?
- If one backer's portfolio failed, **how many properties** and how much value
  would be exposed (knock out a hub, recompute connectivity)?
- Is shared financing **assortative** by building class or borough?

The interesting findings are deliberately undocumented. "Big buildings have more
ties" is the starting point, not a finding.

## `nodes.csv`

One row per property (identical ids and traits to the property rows in
`nyc-realestate-capital`).

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique property key edges reference | string | `P001`, `P059` |
| `label` | Label | Human-readable display name | string | `Astoria Mixed Use 1` |
| `borough` | Borough | NYC borough | string | `Manhattan`, `Brooklyn`, `Queens` |
| `neighborhood` | Neighborhood | NYC neighborhood | string | `Midtown`, `Bushwick`, `South Bronx` |
| `property_type` | Property type | Asset class | string | `office`, `multifamily`, `retail`, `hotel` |
| `building_class` | Building class | CRE quality grade | string | `A`, `B`, `C` |
| `year_built` | Year built | Construction year | integer | `1968`, `2025` |
| `sqft` | Square footage | Gross floor area, ft² | integer | `48821`, `512000` |
| `stories` | Stories | Number of floors | integer | `7`, `42` |
| `appraised_value` | Appraised value | Total appraised value, USD | integer | `30370000`, `423590000` |
| `occupancy_rate` | Occupancy rate | Share of space leased, 0–1 | float | `0.838`, `0.41` |
| `x` | X coordinate | Schematic east–west map position | float | `6.401` |
| `y` | Y coordinate | Schematic north–south map position | float | `9.739` |

## `edges.csv`

One row per shared-financing tie (undirected; `from_id` < `to_id`).

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | Property A | One endpoint property id | string | `P001` |
| `to_id` | Property B | Other endpoint property id | string | `P009` |
| `n_shared_investors` | Shared investors | How many equity investors the two properties share | integer | `1`, `4` |
| `co_investment_usd` | Co-investment (USD) | Shared capital tying the two together, USD | integer | `7279000` |

## Load it

```bash
Rscript data/projects/nyc-realestate-portfolio/load.R
python  data/projects/nyc-realestate-portfolio/load.py
```

In the **R or Python playground** (or the **Visualizer**), pick
`nyc-realestate-portfolio` from the **▾ Load sample** menu. The graph is
undirected and weighted by `co_investment_usd`; color nodes by `borough` or
`property_type`.

## Get this data

<https://github.com/timothyfraser/netsci/tree/main/data/projects/nyc-realestate-portfolio>
