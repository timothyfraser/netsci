# financial-contagion

*A directed interbank exposure network across three periods of a financial
crisis: who lent to whom, before the storm, during the crash, and in the calmer
aftermath.*

![Preview of the financial-contagion network](thumb.png)

## At a glance

| | |
|---|---|
| **Direction** | Directed (exposure runs creditor → debtor) |
| **Weights** | Weighted (`exposure` = dollars at risk on each link) |
| **Modality** | Single-mode — one node kind (firms), typed by `type` |
| **Temporal** | Yes — one row per (creditor, debtor, **period**: before / during / after) |
| **Nodes** | 220 firms (111 banks, 71 hedge funds, 34 insurers, 4 CCPs) |
| **Edges** | 1,701 (before 838 · during 609 · after 254) |
| **Files** | `nodes.csv`, `edges.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

Banks, hedge funds, insurers, and central counterparties (**CCPs**) lend to and
borrow from one another, forming a web of **financial exposures**. Each directed
edge points from a **creditor** to a **debtor** and carries the dollar size of
the exposure — the amount the lender stands to lose if the borrower can't pay.
The network is recorded across three periods: a calm, densely interlinked
**before**; the **during** of a crisis as positions unwind; and the sparser
**after** of a tentative recovery. Each firm carries its size (`assets`), its
`leverage`, its `type`, and its home `region`.

This is a network for **systemic risk, criticality, and cascade** questions.
Some things worth investigating:

- If one firm fails, who is exposed — and does the damage stop there, or ripple
  outward? Can you measure how far a shock travels?
- Degree tells you who has the most counterparties. But who actually sits *between*
  everyone else — whose failure would sever the most connections? Are those the
  same firms?
- Exposures look fine one firm at a time. Do they look fine in aggregate? Are
  lots of firms quietly crowded into the same handful of borrowers?
- Did everyone get caught off guard, or did some firms pull back *before* the
  crash? How would you tell who saw it coming?
- How does the network reshape itself afterward? Is recovery a return to the old
  structure, or a flight toward something safer?

> **Note.** The interesting findings here are deliberately *not* documented. "Big
> firms have more exposures" is the starting point, not a finding. Look for the
> structure that size and volume don't explain.

## `nodes.csv`

One row per firm.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique firm key. Referenced by edges. | character | `F001`, `F063` |
| `type` | Firm type | Kind of financial institution. | character | `bank`, `hedge_fund`, `insurer`, `ccp` |
| `assets` | Total assets | Balance-sheet size in $ billions (firm "size"). | double | `6.71`, `39.82` |
| `leverage` | Leverage ratio | Assets-to-equity ratio; higher = more fragile. | double | `10.07`, `38.0` |
| `region` | Region | Home region of the firm. | character | `NorthAm`, `Europe`, `Asia`, `LatAm` |
| `label` | Display name | Human-readable label. (`name` is avoided — python-igraph reserves it for the ID.) | character | `Bank 002`, `CCP 029` |

## `edges.csv`

One row per (creditor, debtor, period). Directed: exposure runs from `from_id`
(the creditor / lender) to `to_id` (the debtor / borrower).

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | Creditor node ID | The lending firm (bears the loss if the debtor fails; joins to `nodes.csv`). | character | `F001`, `F108` |
| `to_id` | Debtor node ID | The borrowing firm (joins to `nodes.csv`). | character | `F062`, `F079` |
| `period` | Period | Phase of the crisis the exposure was recorded in. | character | `before`, `during`, `after` |
| `exposure` | Exposure | Dollars at risk on this link (the edge weight; arbitrary units). | double | `4.34`, `2.30` |

## Load it

```bash
Rscript data/projects/financial-contagion/load.R     # R    (igraph)
python  data/projects/financial-contagion/load.py     # Python (python-igraph)
```

Both build a directed, weighted `igraph` graph and print a one-screen summary. In
the [R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**financial-contagion** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/financial-contagion>
