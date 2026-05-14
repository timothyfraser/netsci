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
