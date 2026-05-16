---
title: "Where the Bluebikes network gets fragile"
subtitle: "SYSEN 5470 · Project Case Study · Centrality & Criticality"
author: "Sample Student"
date: "2026-06-15"
geometry: margin=1in
fontsize: 11pt
---

## Question

**Which Bluebikes stations, if knocked offline, would do the most
damage to Boston's bike-share network — and does picking by degree get
me the same answer as picking by betweenness?**

I'm asking because Bluebikes operations announces planned station
closures all the time (kiosk swaps, sidewalk construction, snow
removal). The internal heuristic is "swap the busiest first." Busy is
not the same as load-bearing in a network sense, and I want a
defensible answer to which it should be.

## Network

- **Nodes:** 437 Bluebikes stations active in May 2026, one row per
  station, plus latitude / longitude / docks / neighborhood.
- **Edges:** 18,402 weighted directed edges. An edge from station A
  to station B has weight equal to the number of trips taken from A
  to B in May 2026.
- **Data source:** [Bluebikes System Data](https://www.bluebikes.com/system-data),
  May 2026 monthly trip file plus the May station snapshot. Filtered
  to stations with at least 30 trips in the month so I'm not chasing
  noise from a kiosk that opened on the 28th.
- **Size:** N = 437, E = 18,402, density = 0.097. The largest
  weakly-connected component is the whole network — Bluebikes is one
  connected system.

## Procedure

1. Loaded the May 2026 trip data with `tidyverse`, kept rides with
   a recorded start and end station, summarised to a directed
   edge table (one row per ordered station pair with a trip count).
2. Built the network with `tidygraph::as_tbl_graph()` on the edge
   list with weights.
3. Computed three centralities on every node: weighted in-degree,
   weighted betweenness, weighted eigenvector. Weighting matters
   here — an unweighted version would treat a quiet South End
   station the same as Government Center.
4. For each of degree and betweenness, took the top-10 stations,
   then ran a removal simulation: removed those 10 stations and
   recorded the size of the largest weakly-connected component and
   the average shortest-path length on the remaining graph.
5. Repeated the removal simulation against a baseline of 10
   randomly-chosen stations (1,000 random draws, took the mean).

## Results

The three centralities pick **two distinct groups of stations**. Of
the top-10 by weighted in-degree, only **four overlap** with the
top-10 by weighted betweenness. The degree top-10 is dominated by
**Cambridge tourist clusters** (MIT at Mass Ave, Charles Circle,
Kendall/MIT — high-traffic but redundant: trips can route around
any one of them through the others). The betweenness top-10 includes
**three bridge stations on the Longfellow and Harvard bridges** —
stations with fewer absolute trips but that sit on the only short
route between Cambridge and Boston for a meaningful share of the
network.

Removing the **top-10 by betweenness** broke the largest weakly-
connected component from 437 stations to 402 stations and inflated
the average shortest path from 4.12 to 6.81 steps — a **65% increase
in routing distance** even before considering the trips that simply
can't route at all. Removing the **top-10 by degree** kept the largest
component at 437 and increased average shortest path only to 4.34.
Removing **10 random stations** (mean of 1,000 draws) kept the largest
component at 436.8 and average shortest path at 4.15.

Table 1 reports the LCC and shortest-path numbers for the three
removal strategies side-by-side.

| Removal strategy | Largest component | Avg shortest path | Δ vs intact |
|---|---:|---:|---:|
| None (intact network) | 437 | 4.12 | — |
| Top-10 by random | 436.8 | 4.15 | +0.7% |
| Top-10 by weighted degree | 437 | 4.34 | +5.3% |
| Top-10 by weighted betweenness | 402 | 6.81 | +65.3% |

Figure 1 shows the degree-vs-betweenness scatter colored by which
of the three top-10 lists the station appears in. The three bridge
stations sit far above the regression line — high betweenness, low
degree. That gap is exactly where the heuristic "swap the busiest
first" fails.

## What this tells me, and what it doesn't

The takeaway is **operational**: if Bluebikes needs to close a
station for an afternoon, the worst choice is one of the bridge
stations on the Longfellow or Harvard, even though those aren't the
busiest. The cheapest insurance against a network-wide routing
failure is a temporary dock at the next-nearest station on the
*other* side of the bridge, not at the busy hub itself.

It does not tell me that betweenness is "the right" centrality in
general. The result depends on Bluebikes being a routing network —
edges represent flows, not associations. On a coauthorship network
the same betweenness calculation would identify connective scholars,
which is a useful but different thing. I'd also expect the bridge
stations' criticality to shrink in winter, when bike traffic across
the Charles drops sharply; this analysis is May-only and probably
overstates summer bridges' year-round importance.
