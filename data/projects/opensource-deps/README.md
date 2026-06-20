# opensource-deps

*A snapshot of an open-source software ecosystem's dependency graph: which
packages depend on which, and how heavily.*

![Preview of the opensource-deps network](thumb.png)

## At a glance

| | |
|---|---|
| **Direction** | Directed (`from` depends on → `to`) |
| **Weights** | Weighted (`import_count` = how heavily the dependency is used) |
| **Modality** | One node kind (`package`) |
| **Temporal** | No — a single snapshot |
| **Nodes** | 400 packages |
| **Edges** | 2,251 "depends on" relationships |
| **Files** | `nodes.csv`, `edges.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

Every node is a software **package**; a directed edge `A → B` means *package A
depends on package B* (A imports and calls into B). The edge weight,
`import_count`, is how many call sites in A reach into B — a proxy for how heavily
A leans on that dependency. Each package carries its `ecosystem_area` (web, data,
build, test, crypto), its number of `maintainers`, its `weekly_downloads`, and how
many `months_since_update` it has gone without a release.

This is a directed-graph **criticality, reachability, and reverse-dependency**
playground. Some things worth investigating:

- Direct in-degree (how many packages name you as a dependency) is the obvious
  importance measure. But is it the *right* one? What happens if you count how many
  packages can reach you *transitively* — and does that change who looks critical?
- If one package were compromised or yanked, how much of the ecosystem would feel
  it? Is the biggest blast radius attached to a big, well-known library — or
  something small?
- Risk is not just about reach. Combine reach with `maintainers` and
  `months_since_update`: is there a package the whole ecosystem leans on that
  almost nobody is maintaining?
- Out-degree tells a different story than in-degree. Is any package unusually
  fragile because it depends on a huge number of others?
- Look for packages that look almost identical and sit at the same depth, each
  with a large but *different* set of dependents. What would happen if a project
  needed both?

> **Note.** The interesting findings here are deliberately *not* documented.
> "Popular libraries are depended on a lot" is the starting point, not a finding.
> Look at what direct degree alone hides.

## `nodes.csv`

One row per package.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique key. `pkg###`. Referenced by edges. | character | `pkg001`, `pkg007`, `pkg400` |
| `ecosystem_area` | Ecosystem area | Functional area the package serves. | character | `web`, `data`, `crypto` |
| `maintainers` | Maintainer count | Number of active maintainers on the package. | integer | `1`, `4`, `10` |
| `weekly_downloads` | Weekly downloads | Registry downloads in a typical week. | integer | `8532`, `154618` |
| `months_since_update` | Months since update | Months since the last release. | double | `0.1`, `12.4`, `57.0` |
| `label` | Display name | Human-readable label. (`name` is avoided — python-igraph reserves it for the ID.) | character | `web-lib-001`, `tiny-pad` |

## `edges.csv`

One row per dependency. Directed: `from_id` depends on `to_id`.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | Dependent package ID | The package that has the dependency (joins to `nodes.csv`). | character | `pkg042` |
| `to_id` | Dependency package ID | The package being depended on (joins to `nodes.csv`). | character | `pkg007` |
| `import_count` | Import count | Number of call sites through which `from_id` uses `to_id` (the edge weight). | integer | `1`, `7`, `30` |

## Load it

```bash
Rscript data/projects/opensource-deps/load.R     # R    (igraph)
python  data/projects/opensource-deps/load.py     # Python (python-igraph)
```

Both build a directed, weighted `igraph` graph (edge weight = `import_count`) and
print a one-screen summary. In the
[R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**opensource-deps** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/opensource-deps>
