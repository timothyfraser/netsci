# Playground Sample Networks

Small network datasets bundled with the coding playgrounds. Each network is a
pair of CSV files: one for nodes (with attributes), one for edges (with
weights). Designed to be small enough to fit comfortably in WebR or Pyodide's
in-browser memory and to load instantly.

Both `playground-r.html` and `playground-py.html` fetch these CSVs into the
WASM virtual filesystem when you pick a sample from the loader dropdown.

| key | nodes | edges | description |
|---|---|---|---|
| `karate` | 34 | 78 | Zachary's karate club (1977). Faction = `instructor` / `officer`. The canonical small social network. |
| `lakeside` | 15 | 19 | The 15-station Lakeside Bikeshare network from the **Counterfactual Monte Carlo** lab. Edges weighted by Q1 ridership. |
| `riverdale` | 18 | 21 | The 18-station Riverdale Metro & Bus network from the **Centrality & Criticality** lab. Edges weighted by typical riders/day. |
| `supply-chain` | 16 | 30 | The 16-factory supply chain from the **Network Joins** lab. Three tiers (Tier 1 final assembly, Tier 2 subassembly, Tier 3 raw). Volume-weighted shipment lanes. |
| `amazon-last-mile` | 313 | 2,142 | **Project dataset.** One week of package flow, hubs → stations → zones. Directed, weighted (`packages`), temporal (`day`). Mirrored from `data/projects/amazon-last-mile/`. |
| `uber-manhattan` | 370 | 3,000 | **Project dataset.** Bipartite drivers ↔ riders for one day downtown. Weighted by `fare`; ships a `zones.csv` lookup. Mirrored from `data/projects/uber-manhattan/`. |
| `semiconductor-supply` | 368 | 739 | **Project dataset.** Multi-tier chip supply chain (material→foundry→packaging→designer→product), weighted by `annual_volume`. |
| `aerospace-components` | 300 | 777 | **Project dataset.** Aircraft BOM + suppliers, weighted by `qty_per_aircraft`. |
| `mutualaid-quake` | 250 | 2,935 | **Project dataset.** Neighborhood mutual aid across `before`/`during`/`after` a quake, weighted by `amount`. |
| `financial-contagion` | 220 | 1,701 | **Project dataset.** Interbank exposures across a crisis (`period`), weighted by `exposure`. |
| `airline-delays` | 200 | 2,244 | **Project dataset.** Route network with delay propagation across time `block`s, weighted by `number_of_flights`. |
| `power-grid` | 300 | 422 | **Project dataset.** Undirected transmission grid, weighted by `capacity_mw`; ships a `regions.csv` lookup. |
| `campus-contact` | 300 | 3,699 | **Project dataset.** Undirected weekly contact network during an outbreak, weighted by `contact_minutes`; ships a `status.csv` lookup. |
| `opensource-deps` | 400 | 2,251 | **Project dataset.** Package dependency graph, weighted by `import_count`. |
| `trade-commodity` | 140 | 1,210 | **Project dataset.** Country-to-country commodity trade across a shock (`period`), weighted by `tonnes`. |
| `reorg-comms` | 250 | 7,926 | **Project dataset.** Corporate messaging across `before`/`during`/`after` a reorg, weighted by `message_count`. |

All `*-project` datasets above are mirrored from `data/projects/<name>/` by
`data/projects/_sync_to_playground.py`.

## Columns

### Nodes

- `karate`: `id, name, faction`
- `lakeside`: `id, label, zone, type`
- `riverdale`: `id, label, zone, type`
- `supply-chain`: `node_id, name, region, tier, capacity_units`

### Edges

- `karate`: `source, target, weight` (weight is always 1 — Zachary's network is unweighted)
- `lakeside`: `source, target, weight` (ridership)
- `riverdale`: `source, target, line, weight` (line ∈ red/blue/green/yellow/bus; weight = ridership)
- `supply-chain`: `from_id, to_id, lane, volume_units`

## Provenance

All datasets are synthetic or public:

- **Karate** is the canonical Zachary (1977) edge list.
- **Lakeside, Riverdale, Supply-chain** are the toy networks used in our own labs. They are not real data.
