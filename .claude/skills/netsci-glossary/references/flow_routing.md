# Flow and Routing — Full Reference

The course's optimization module. Problems on networks where the goal is to move something — packets, packages, people, power — through edges subject to constraints.

## Shortest path

- **Definition:** minimum-weight path between two nodes. On unweighted graphs, shortest = fewest hops.
- **Algorithms:**
  - **Dijkstra** — non-negative weights. O((n + m) log n) with a heap.
  - **Bellman–Ford** — allows negative weights; detects negative cycles. O(nm).
  - **A\*** — Dijkstra with a heuristic to guide search; needs admissible heuristic. Used in routing on geographic networks.
  - **Floyd–Warshall** — all-pairs shortest paths. O(n³). Use for small/medium graphs.
- **R:** `igraph::shortest_paths()`, `igraph::distances()`, `igraph::all_shortest_paths()`.
- **Engineer's use:** evacuation routing (Hurricane Dorian), package delivery, fastest transit route.

### Geodesic
- The shortest path. A graph may have many geodesics between the same pair.
- **Distance** = length of *any* geodesic between two nodes.

### Path vs. walk vs. trail
See `red_flags.md` for the distinction. Routing usually wants simple paths (no repeated nodes).

## Max flow / min cut

- **Definition:** given source *s*, sink *t*, and edge capacities, find the maximum flow from *s* to *t*. By Ford–Fulkerson / max-flow min-cut theorem, max flow = capacity of minimum *s-t* cut.
- **Algorithms:**
  - **Ford–Fulkerson** with augmenting paths. O(max_flow · m) in worst case.
  - **Edmonds–Karp** — Ford–Fulkerson with BFS for augmenting paths. O(nm²).
  - **Push-relabel** — faster in practice. O(n²√m).
- **R:** `igraph::max_flow(graph, source, target, capacity)`. Returns flow value, edge flows, and the min cut.
- **Engineer's use:**
  - Supply chain throughput from source to demand point.
  - Pipeline capacity through a refinery network.
  - **Skill 3 (counterfactual disruption):** min cut identifies the bottleneck set to attack/protect.

### Min-cost flow
- **Definition:** max flow subject to per-edge cost minimization.
- **Algorithms:** network simplex, successive shortest paths.
- **Engineer's use:** logistics with capacity *and* cost; transportation problem.

## Minimum spanning tree (MST)

- **Definition:** subgraph that is a tree, connects all nodes, minimizes total edge weight.
- **Algorithms:**
  - **Kruskal** — sort edges, greedily add if no cycle. O(m log m).
  - **Prim** — grow tree from a seed, always adding cheapest crossing edge. O(m + n log n).
- **R:** `igraph::mst(graph, weights = E(graph)$weight, algorithm = "prim")`.
- **Engineer's use:** infrastructure layout (power, water, fiber) — connect everyone with minimum cable.

## Traveling Salesman Problem (TSP)

- **Definition:** visit every node exactly once, return to start, minimize total cost.
- **Complexity:** NP-hard.
- **Approaches:**
  - **Exact:** Held–Karp dynamic programming (O(n² 2ⁿ)) — only for n ≲ 20.
  - **Integer programming:** branch-and-cut (Concorde solver); handles thousands of cities.
  - **Approximation:** Christofides (1.5-approx for metric TSP).
  - **Heuristic:** nearest neighbor, 2-opt, Lin–Kernighan, simulated annealing, genetic algorithms.
- **R:** `TSP` package.
- **Engineer's use:** delivery routes, drilling order, manufacturing tool path.

## Vehicle Routing Problem (VRP)

- **Definition:** TSP with multiple vehicles, capacity constraints, time windows, depots.
- **Complexity:** NP-hard; harder than TSP.
- **Variants:** CVRP (capacitated), VRPTW (time windows), MDVRP (multi-depot), pickup-and-delivery.
- **Approaches:** mostly heuristic / metaheuristic at realistic sizes; OR-Tools, Gurobi, CPLEX for exact on moderate instances.
- **R:** Less mature ecosystem; OR-Tools via Python bindings is more common.
- **Engineer's use:** courier fleet routing, school bus routing, waste collection.

## Chinese Postman Problem (CPP)

- **Definition:** traverse every *edge* at least once, return to start, minimize cost.
- **Complexity:** polynomial for undirected; NP-hard for mixed graphs.
- **Engineer's use:** street sweeping, snow plowing, mail delivery, network inspection.

## Steiner tree

- **Definition:** minimum-weight tree connecting a *subset* of "terminal" nodes (Steiner nodes may be added).
- **Complexity:** NP-hard.
- **Engineer's use:** efficient connector layout when only certain endpoints matter (e.g., connect these 10 substations, intermediate routing free).

## Flow betweenness

- **Definition:** like betweenness centrality, but flow follows max-flow paths (or random walks), not just shortest paths.
- **Engineer's use:** when network usage isn't constrained to shortest path (info diffusion, financial contagion).

## Other relevant concepts

- **k-shortest paths:** find the top-k shortest, not just the single shortest. Useful for resilience analysis.
- **Edge-disjoint paths:** how many s-t paths share no edges? Equals min edge cut.
- **Vertex-disjoint paths:** Menger's theorem analog for nodes.
- **Network reliability:** probability the network remains connected (or s-t connected) given edge failure probabilities. NP-hard.
- **Percolation:** what fraction of edges (or nodes) must fail before the giant component dissolves?

## Connection to Skill 3 (counterfactual disruption)

The course's third skill — counterfactual disruption simulation — is largely a flow/routing question framed structurally:

- Remove a node or edge.
- Recompute shortest paths, max flow, connected components, or reachability.
- Aggregate over many removals (Monte Carlo) to estimate resilience.
- Compare to a random-removal null (which nodes are *specifically* critical, not just structurally important on average?).

Min cut and edge betweenness directly identify the "attack first" candidates. Random removal gives the resilience baseline.

## When to reach for what

| Problem | Method |
|---|---|
| Fastest path between two points | Dijkstra |
| All pairwise distances | Floyd–Warshall (small) or BFS/Dijkstra repeated |
| Throughput between source and sink | Max flow |
| Find the bottleneck | Min cut (from max flow) |
| Minimum-cost connection of all nodes | MST |
| Visit-every-node tour | TSP |
| Multi-vehicle delivery | VRP |
| Traverse-every-edge route | Chinese postman |
| Connect specific nodes minimally | Steiner tree |
| Resilience to node failure | Component / reachability + Monte Carlo removal |
| Resilience to edge failure | Same, plus min cut analysis |

## Common mistakes

- Treating "shortest path" on a social network as a meaningful distance (it's hop count; may not reflect actual flow).
- Using max flow when min-cost flow is the real problem (capacity + cost both matter).
- Reporting MST as "the network's structure" — it's a tree, you've thrown away most edges.
- Tackling realistic VRP with off-the-shelf TSP code — different problem.
- Forgetting that TSP and VRP are NP-hard. Exact solutions don't scale; heuristics are the norm.
- Conflating betweenness centrality with flow betweenness — different flow models.
