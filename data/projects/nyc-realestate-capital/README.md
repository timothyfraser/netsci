# nyc-realestate-capital

*Who is funding New York City's commercial real estate — and how much of the promised money actually shows up — tracked quarter by quarter for three years.*

## At a glance

| | |
|---|---|
| **Direction** | Directed (capital provider → property) |
| **Weights** | Yes — `invested_usd` (capital deployed); also `pledged_usd` |
| **Modality** | Multi-mode: `property` · `investor` · `bank` (bipartite providers → properties) |
| **Temporal** | Yes — 12 quarterly slices, `2024Q1` … `2026Q4` (long format) |
| **Nodes** | 270 (190 properties · 64 investors · 16 banks) |
| **Edges** | 5,044 provider–property–quarter funding rows |
| **Files** | `nodes.csv`, `edges.csv` |

## What this network is

A capital-flow network for commercial real estate (CRE) in New York City. Two
kinds of **capital providers** fund individual **properties**: `investor` nodes
supply equity (typed by who they are — local, POC-led, corporate, multinational,
institutional, family office, REIT, sovereign, nonprofit) and `bank` nodes supply
debt (commercial, investment, community-development/CDFI, GSE, private credit). An
edge is a funding relationship in a given quarter; it records capital **already
deployed** (`invested_usd`) versus capital **pledged but not yet deployed**
(`pledged_usd`). The same provider→property pair recurs across quarters, so the
network grows and shifts over the three years.

It pairs with **`nyc-realestate-portfolio`**, which shares the property `node_id`s
exactly: that companion projects this bipartite network down to property↔property
shared-financing ties.

Example project questions:
- For each property, what **share of investment** comes from local vs.
  multinational capital? From equity vs. debt? (`invested_usd` by provider type.)
- Is a property's **deployment ratio** — `invested / (invested + pledged)` —
  related to its neighborhood, *after* controlling for appraised value?
- Which providers are **systemically central** (fund many properties, or bridge
  otherwise-separate portfolios)? What happens to the network at `2025Q2`?
- Predict which properties end the period **under-funded** (deployed far below
  appraised value) from their funding mix and neighborhood.

The genuinely interesting findings here are deliberately undocumented. "Prime
buildings attract more capital" is the *starting point*, not a finding — look for
what is true once you hold size, value, and location constant.

## `nodes.csv`

One row per node. `kind` selects which columns apply; provider-only or
property-only columns are blank where they don't apply.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique key edges reference (`P###` property, `I###` investor, `B##` bank) | string | `P001`, `I001`, `B01` |
| `kind` | Node kind | Which mode this node is | string | `property`, `investor`, `bank` |
| `label` | Label | Human-readable display name | string | `Astoria Mixed Use 1`, `Reit Capital 1` |
| `borough` | Borough | Property borough (property rows) | string | `Manhattan`, `Brooklyn`, `Bronx` |
| `neighborhood` | Neighborhood | Property neighborhood (property rows) | string | `Midtown`, `Bushwick`, `South Bronx` |
| `property_type` | Property type | Asset class (property rows) | string | `office`, `multifamily`, `retail`, `hotel` |
| `building_class` | Building class | CRE quality grade (property rows) | string | `A`, `B`, `C` |
| `year_built` | Year built | Construction year (property rows) | integer | `1968`, `2025` |
| `sqft` | Square footage | Gross floor area, ft² (property rows) | integer | `48821`, `512000` |
| `stories` | Stories | Number of floors (property rows) | integer | `7`, `42` |
| `appraised_value` | Appraised value | Total appraised value, USD (property rows) | integer | `30370000`, `423590000` |
| `occupancy_rate` | Occupancy rate | Share of space leased, 0–1 (property rows) | float | `0.838`, `0.41` |
| `investor_type` | Investor type | Equity-investor category (investor rows) | string | `local`, `poc_led`, `multinational`, `reit` |
| `capital_scale` | Capital scale | Rough size of the investor (investor rows) | string | `small`, `mid`, `large` |
| `lender_type` | Lender type | Debt-provider category (bank rows) | string | `commercial`, `investment`, `community_dev`, `gse`, `private_credit` |
| `hq_location` | Headquarters | Provider HQ city (provider rows) | string | `New York`, `London`, `Abu Dhabi` |
| `founded_year` | Founded year | Year the provider was founded (provider rows) | integer | `1981`, `1920` |
| `x` | X coordinate | Schematic east–west map position (property rows) | float | `6.401` |
| `y` | Y coordinate | Schematic north–south map position (property rows) | float | `9.739` |

## `edges.csv`

One row per (provider, property, quarter) once the relationship is active.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | Provider ID | Capital provider (`I###` investor or `B##` bank) | string | `I006`, `B01` |
| `to_id` | Property ID | Property receiving capital (`P###`) | string | `P001` |
| `quarter` | Quarter | Calendar quarter of this slice | string | `2024Q1`, `2025Q2`, `2026Q4` |
| `instrument` | Instrument | Type of capital | string | `equity`, `debt`, `mezzanine` |
| `invested_usd` | Invested (USD) | Capital actually deployed to date, USD | integer | `2679000`, `4379000` |
| `pledged_usd` | Pledged (USD) | Committed capital not yet deployed, USD | integer | `7862000`, `5029000` |

## Load it

```bash
Rscript data/projects/nyc-realestate-capital/load.R
python  data/projects/nyc-realestate-capital/load.py
```

In the **R or Python playground** (or the **Visualizer**), pick
`nyc-realestate-capital` from the **▾ Load sample** menu. The graph is directed
(provider → property), weighted by `invested_usd`, and bipartite in structure
(`type` = TRUE for properties). Filter the `quarter` column for one temporal
slice, or aggregate by it.

## Get this data

<https://github.com/timothyfraser/netsci/tree/main/data/projects/nyc-realestate-capital>
