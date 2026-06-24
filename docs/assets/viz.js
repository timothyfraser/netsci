// ============================================================
// SYSEN 5470 — Network Visualizer
// Browser-only edgelist + nodelist explorer
// Loads PapaParse + D3 v7 from CDN (declared in visualizer.html).
// ============================================================
(function (global) {
  'use strict';

  // ── State ───────────────────────────────────────────────────
  const state = {
    edgeCsv:  null,   // raw parsed edges (array of objects)
    nodeCsv:  null,   // raw parsed nodes (array of objects) — optional
    edgeCols: [],     // header names
    nodeCols: [],
    mapping: {
      from: null, to: null, weight: null, time: null,
      nodeId: null, nodeLabel: null, nodeGroup: null
    },
    graph: null,      // { nodes: [{id, label, group, x, y, deg, weighted}], links: [{source, target, weight, time}] }
    baseGraph: null,  // the un-aggregated graph; `graph` may be an aggregated view of it
    aggregateBy: '',  // node-trait column to collapse on ('' = raw network)
    aggregateMode: 'sum',  // how to combine the edge weight: 'sum' | 'mean'
    aggregateTime: '',  // '' = overall (all time); else a single time-slice value
    layout: 'force',  // force | radial | hierarchical
    showEdgeLabels: false,
    showNodeLabels: true,
    colorBy: 'group',     // 'group' (node attribute) | 'community' (component) | 'uniform'
    groupPalette: {},     // group value -> default course-palette color
    groupColors: {},      // group value -> user-overridden color
    dropIsolates: true,   // hide nodes that never appear in the edgelist (degree 0)
    showDrift: false,     // off = settle then stop (default); on = keep gently moving
    frozen: false,        // true once the layout has settled / been frozen
    nodeScale: 1,
    edgeThreshold: 0,
    timeFilter: null, // null = no filter, otherwise upper bound
    timeRange: null,  // [min, max]
    selectedNode: null,
    simulation: null,
    zoom: null,            // d3.zoom behavior
    zoomTransform: null,   // current pan/zoom transform (persists across renders)
    palette: 'neon',       // categorical color palette: neon | viridis | plasma | mako
    useWeights: false,     // weight degree/betweenness by edge weight when true
    metrics: {}       // per-node { degree, weighted, betweenness, component }
  };

  // Improved neon set: green primary, then a yellow/amber secondary (NOT the
  // teal, which sits too close to the green); the teal still appears later.
  const NEON = ['#39FF14', '#fbbf24', '#f472b6', '#818cf8',
                '#fb923c', '#a78bfa', '#5eead4', '#f87171'];
  // Mako control points (seaborn) for a d3 basis interpolator (teal-forward).
  const MAKO_STOPS = ['#0B0405', '#3A2C59', '#395D9C', '#3497A9',
                      '#5CC8A7', '#A5DFB8', '#DEF5E5'];

  // Categorical colors sampled from the chosen palette. Continuous palettes are
  // sampled over [0.30, 0.98] to skip their darkest end (low contrast on the
  // dark stage) and returned as hex (so <input type=color> swatches accept them).
  function paletteColors(name, n) {
    n = Math.max(1, n);
    if (name === 'neon') return Array.from({ length: n }, (_, i) => NEON[i % NEON.length]);
    const interp = name === 'plasma' ? d3.interpolatePlasma
                 : name === 'mako'   ? d3.interpolateRgbBasis(MAKO_STOPS)
                 : d3.interpolateViridis;
    const lo = 0.30, hi = 0.98;
    return Array.from({ length: n }, (_, i) => {
      const t = n === 1 ? 0.6 : lo + (hi - lo) * (i / (n - 1));
      return d3.color(interp(t)).formatHex();
    });
  }

  // ── DOM helpers ─────────────────────────────────────────────
  const $ = (id) => document.getElementById(id);

  function setStatus(msg, kind) {
    const el = $('viz-status'); if (!el) return;
    el.textContent = msg;
    el.style.color = kind === 'err' ? 'var(--danger)'
                    : kind === 'ok' ? 'var(--green-bright)'
                    : 'var(--grey)';
  }

  // ── CSV parsing ─────────────────────────────────────────────
  function parseCsv(file, cb) {
    Papa.parse(file, {
      header: true, dynamicTyping: true, skipEmptyLines: true,
      complete: (res) => cb(res.data, res.meta.fields || [])
    });
  }

  function autoMap(cols) {
    const lower = cols.map((c) => String(c).toLowerCase());
    const find = (...names) => {
      for (const n of names) {
        const i = lower.indexOf(n);
        if (i >= 0) return cols[i];
      }
      return null;
    };
    return {
      from:   find('from', 'source', 'src', 'a', 'origin'),
      to:     find('to', 'target', 'tgt', 'b', 'destination', 'dest'),
      weight: find('weight', 'value', 'w', 'count', 'flow'),
      time:   find('time', 'date', 'timestamp', 'month', 'year', 't')
    };
  }
  function autoMapNodes(cols) {
    const lower = cols.map((c) => String(c).toLowerCase());
    const find = (...names) => {
      for (const n of names) {
        const i = lower.indexOf(n);
        if (i >= 0) return cols[i];
      }
      return null;
    };
    return {
      // NB: do NOT treat 'label' as the id — many node files have a 'label'
      // display column distinct from the id key, which would mis-key nodes.
      nodeId:    find('node_id', 'id', 'node', 'nodeid', 'name'),
      nodeLabel: find('label', 'name', 'title'),
      nodeGroup: find('group', 'community', 'cluster', 'type', 'category', 'kind', 'tier')
    };
  }

  // ── Build graph from mapped CSV ─────────────────────────────
  function buildGraph() {
    const m = state.mapping;
    if (!m.from || !m.to) { setStatus('Map both From and To columns to load.', 'err'); return false; }
    if (!state.edgeCsv || !state.edgeCsv.length) { setStatus('No edges parsed.', 'err'); return false; }

    const nodeMap = new Map();
    const ensureNode = (rawId) => {
      const id = String(rawId);
      if (!nodeMap.has(id)) {
        nodeMap.set(id, { id, label: id, group: null, deg: 0, weighted: 0 });
      }
      return nodeMap.get(id);
    };

    const links = [];
    const times = [];
    state.edgeCsv.forEach((row) => {
      const a = row[m.from], b = row[m.to];
      if (a === undefined || a === null || a === '' || b === undefined || b === null || b === '') return;
      const A = ensureNode(a), B = ensureNode(b);
      let w = m.weight ? Number(row[m.weight]) : 1;
      if (!isFinite(w) || w <= 0) w = 1;
      const tRaw = m.time ? row[m.time] : null;   // keep raw value (e.g. string periods) for time-slice aggregation
      let t = tRaw;
      if (t !== null && t !== undefined && t !== '') {
        const tn = Number(t);
        t = isFinite(tn) ? tn : Date.parse(t);
        if (isFinite(t)) times.push(t);
      } else t = null;
      links.push({ source: A.id, target: B.id, weight: w, time: t, timeRaw: (tRaw === undefined ? null : tRaw) });
      A.deg++; B.deg++;
      A.weighted += w; B.weighted += w;
    });

    if (state.nodeCsv && state.mapping.nodeId) {
      state.nodeCsv.forEach((row) => {
        const id = String(row[state.mapping.nodeId]);
        if (!nodeMap.has(id)) nodeMap.set(id, { id, label: id, group: null, deg: 0, weighted: 0 });
        const n = nodeMap.get(id);
        n.attrs = row;   // keep the raw node columns so we can aggregate by any trait
        if (state.mapping.nodeLabel) n.label = String(row[state.mapping.nodeLabel] ?? id);
        if (state.mapping.nodeGroup) n.group = String(row[state.mapping.nodeGroup] ?? '');
      });
    }

    state.graph = { nodes: Array.from(nodeMap.values()), links };
    if (times.length) {
      state.timeRange = [Math.min(...times), Math.max(...times)];
      state.timeFilter = state.timeRange[1];
    } else {
      state.timeRange = null;
      state.timeFilter = null;
    }
    computeMetrics();
    return true;
  }

  // ── Metrics: degree, betweenness, components ────────────────
  function computeMetrics() {
    const { nodes, links } = state.graph;
    const adj = {};
    nodes.forEach((n) => { adj[n.id] = []; });
    links.forEach((l) => {
      const s = typeof l.source === 'object' ? l.source.id : l.source;
      const t = typeof l.target === 'object' ? l.target.id : l.target;
      adj[s].push(t); adj[t].push(s);
    });

    // Components (BFS)
    const compOf = {}; let cid = 0;
    nodes.forEach((n) => {
      if (compOf[n.id] !== undefined) return;
      cid++; const q = [n.id]; let qi = 0;
      while (qi < q.length) {
        const u = q[qi++];
        if (compOf[u] !== undefined) continue;
        compOf[u] = cid;
        (adj[u] || []).forEach((v) => { if (compOf[v] === undefined) q.push(v); });
      }
    });

    // Brandes betweenness (undirected) — bounded by N for performance. With
    // state.useWeights, shortest paths use edge weights (Dijkstra, distance =
    // 1/weight so stronger ties are "closer"); otherwise hop-count (BFS).
    const N = nodes.length;
    const ids = nodes.map((n) => n.id);
    const betw = {};
    ids.forEach((id) => { betw[id] = 0; });

    if (N <= 600 && !state.useWeights) {
      ids.forEach((s) => {
        const stack = [], pred = {}, sigma = {}, dist = {};
        ids.forEach((id) => { pred[id] = []; sigma[id] = 0; dist[id] = -1; });
        sigma[s] = 1; dist[s] = 0;
        const q = [s]; let qi = 0;
        while (qi < q.length) {
          const v = q[qi++]; stack.push(v);
          (adj[v] || []).forEach((w) => {
            if (dist[w] < 0) { q.push(w); dist[w] = dist[v] + 1; }
            if (dist[w] === dist[v] + 1) { sigma[w] += sigma[v]; pred[w].push(v); }
          });
        }
        const delta = {}; ids.forEach((id) => { delta[id] = 0; });
        while (stack.length) {
          const w = stack.pop();
          pred[w].forEach((v) => { delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w]); });
          if (w !== s) betw[w] += delta[w];
        }
      });
      const norm = (N - 1) * (N - 2);
      if (norm > 0) ids.forEach((id) => { betw[id] = betw[id] / norm; });
    } else if (N <= 600 && state.useWeights) {
      // weighted adjacency (undirected; keep the strongest parallel edge)
      const adjW = {}; ids.forEach((id) => { adjW[id] = new Map(); });
      links.forEach((l) => {
        const s = typeof l.source === 'object' ? l.source.id : l.source;
        const t = typeof l.target === 'object' ? l.target.id : l.target;
        const d = 1 / (l.weight > 0 ? l.weight : 1);
        if (!adjW[s].has(t) || adjW[s].get(t) > d) adjW[s].set(t, d);
        if (!adjW[t].has(s) || adjW[t].get(s) > d) adjW[t].set(s, d);
      });
      const EPS = 1e-9;
      ids.forEach((s) => {
        const dist = {}, sigma = {}, pred = {}, done = {};
        ids.forEach((id) => { dist[id] = Infinity; sigma[id] = 0; pred[id] = []; });
        dist[s] = 0; sigma[s] = 1;
        const S = [];
        for (let cnt = 0; cnt < N; cnt++) {
          let u = null, best = Infinity;
          for (const id of ids) { if (!done[id] && dist[id] < best) { best = dist[id]; u = id; } }
          if (u === null || best === Infinity) break;
          done[u] = true; S.push(u);
          adjW[u].forEach((dw, w) => {
            const nd = dist[u] + dw;
            if (nd < dist[w] - EPS) { dist[w] = nd; sigma[w] = sigma[u]; pred[w] = [u]; }
            else if (Math.abs(nd - dist[w]) < EPS) { sigma[w] += sigma[u]; pred[w].push(u); }
          });
        }
        const delta = {}; ids.forEach((id) => { delta[id] = 0; });
        while (S.length) {
          const w = S.pop();
          pred[w].forEach((v) => { delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w]); });
          if (w !== s) betw[w] += delta[w];
        }
      });
      const norm = (N - 1) * (N - 2);
      if (norm > 0) ids.forEach((id) => { betw[id] = betw[id] / norm; });
    }

    state.metrics = {};
    nodes.forEach((n) => {
      state.metrics[n.id] = {
        degree: state.useWeights ? n.weighted : n.deg, weighted: n.weighted,
        betweenness: betw[n.id] || 0,
        component: compOf[n.id]
      };
    });
    // size references so node radius stays sane whether degree is a count or a
    // (much larger) weighted sum
    state.maxCount = nodes.reduce((m, n) => Math.max(m, n.deg), 0) || 1;
    state.maxWeighted = nodes.reduce((m, n) => Math.max(m, n.weighted), 0) || 1;
  }

  // ── UI: column-mapper dropdowns ─────────────────────────────
  function renderMappers() {
    const wrap = $('mapper-fields'); wrap.innerHTML = '';
    const cols = state.edgeCols;
    const fields = [
      { key: 'from',   label: 'From column',   req: true,  options: cols },
      { key: 'to',     label: 'To column',     req: true,  options: cols },
      { key: 'weight', label: 'Weight column', req: false, options: cols },
      { key: 'time',   label: 'Time column',   req: false, options: cols }
    ];
    fields.forEach((f) => {
      const row = document.createElement('div');
      row.className = 'mapper-row';
      row.innerHTML = `
        <label>${f.label}${f.req ? '' : ' <span class="opt">opt.</span>'}</label>
        <select data-key="${f.key}">
          <option value="">— none —</option>
          ${f.options.map((c) => `<option value="${c}" ${state.mapping[f.key] === c ? 'selected' : ''}>${c}</option>`).join('')}
        </select>`;
      wrap.appendChild(row);
    });
    wrap.querySelectorAll('select').forEach((sel) => {
      sel.addEventListener('change', (e) => {
        state.mapping[e.target.dataset.key] = e.target.value || null;
      });
    });

    if (state.nodeCsv && state.nodeCols.length) {
      // Node group column lives in the Display panel (it drives coloring); keep
      // only the structural id/label mapping here.
      const nf = [
        { key: 'nodeId',    label: 'Node ID column',    options: state.nodeCols },
        { key: 'nodeLabel', label: 'Node label column', options: state.nodeCols }
      ];
      const div = document.createElement('div');
      div.className = 'mapper-divider';
      div.textContent = 'Nodelist columns';
      wrap.appendChild(div);
      nf.forEach((f) => {
        const row = document.createElement('div');
        row.className = 'mapper-row';
        row.innerHTML = `
          <label>${f.label}</label>
          <select data-key="${f.key}">
            <option value="">— none —</option>
            ${f.options.map((c) => `<option value="${c}" ${state.mapping[f.key] === c ? 'selected' : ''}>${c}</option>`).join('')}
          </select>`;
        wrap.appendChild(row);
      });
      wrap.querySelectorAll('select[data-key^="node"]').forEach((sel) => {
        sel.addEventListener('change', (e) => {
          state.mapping[e.target.dataset.key] = e.target.value || null;
        });
      });
    }
  }

  // ── File handlers ───────────────────────────────────────────
  function handleEdgeFile(file) {
    setStatus('Parsing edges…');
    parseCsv(file, (data, cols) => {
      state.edgeCsv = data;
      state.edgeCols = cols;
      state.mapping = Object.assign({}, state.mapping, autoMap(cols));
      renderMappers();
      setStatus(`Edges: ${data.length} rows · ${cols.length} columns. Auto-mapped — click Load.`, 'ok');
    });
  }
  function handleNodeFile(file) {
    setStatus('Parsing nodes…');
    parseCsv(file, (data, cols) => {
      state.nodeCsv = data;
      state.nodeCols = cols;
      Object.assign(state.mapping, autoMapNodes(cols));
      renderMappers();
      setStatus(`Nodes: ${data.length} rows · ${cols.length} columns.`, 'ok');
    });
  }

  function loadGraph() {
    if (!buildGraph()) return;
    state.baseGraph = state.graph;
    setStatus(`Graph: ${state.graph.nodes.length} nodes · ${state.graph.links.length} edges.`, 'ok');
    populateAggregateOptions();
    populateAggregateTimeOptions();
    populateGroupColumnOptions();
    state.aggregateBy = '';
    const aggSel = $('aggregate-by'); if (aggSel) aggSel.value = '';
    rebuildView();
  }

  // ── Experimental aggregation ────────────────────────────────
  // Collapse the base graph by a node trait: every edge is re-pointed to the
  // trait group of its endpoints, and parallel edges are combined (sum/mean of
  // the weight). Intra-group edges (same trait on both ends) are dropped.
  function aggregateGraph(base, trait, mode, timeSlice) {
    const slice = (timeSlice !== undefined && timeSlice !== null && timeSlice !== '');
    const groupOf = (n) => {
      const a = n.attrs ? n.attrs[trait] : undefined;
      return (a === undefined || a === null || a === '') ? '(none)' : String(a);
    };
    const gid = {};
    base.nodes.forEach((n) => { gid[n.id] = groupOf(n); });

    const nodeMap = new Map();
    base.nodes.forEach((n) => {
      const g = gid[n.id];
      if (!nodeMap.has(g)) {
        nodeMap.set(g, { id: g, label: g, group: g, deg: 0, weighted: 0,
                         attrs: { [trait]: g }, members: 0 });
      }
      nodeMap.get(g).members += 1;
    });

    const agg = new Map();   // "gsgt" -> { source, target, sum, count }
    base.links.forEach((l) => {
      if (slice && String(l.timeRaw) !== String(timeSlice)) return;   // single time slice only
      const s = typeof l.source === 'object' ? l.source.id : l.source;
      const t = typeof l.target === 'object' ? l.target.id : l.target;
      const gs = gid[s], gt = gid[t];
      if (gs === gt) return;                       // drop intra-group self-loops
      const key = gs + '' + gt;
      let rec = agg.get(key);
      if (!rec) { rec = { source: gs, target: gt, sum: 0, count: 0 }; agg.set(key, rec); }
      rec.sum += (l.weight || 0);
      rec.count += 1;
    });

    const links = [];
    agg.forEach((rec) => {
      const w = mode === 'mean' ? rec.sum / rec.count : rec.sum;
      links.push({ source: rec.source, target: rec.target, weight: w, count: rec.count, time: null });
      const A = nodeMap.get(rec.source), B = nodeMap.get(rec.target);
      A.deg += 1; B.deg += 1; A.weighted += w; B.weighted += w;
    });

    return { nodes: Array.from(nodeMap.values()), links };
  }

  // Build the displayed graph from the base graph + current aggregation choice,
  // then recompute metrics/palette/time-slider and redraw. Called on load and
  // whenever the aggregation controls change.
  function rebuildView() {
    if (!state.baseGraph) return;
    if (state.aggregateBy) {
      state.graph = aggregateGraph(state.baseGraph, state.aggregateBy, state.aggregateMode, state.aggregateTime);
      state.timeRange = null;
      state.timeFilter = null;
    } else {
      state.graph = state.baseGraph;
      const times = state.baseGraph.links
        .map((l) => l.time).filter((t) => t !== null && t !== undefined && isFinite(t));
      state.timeRange = times.length ? [Math.min(...times), Math.max(...times)] : null;
      state.timeFilter = state.timeRange ? state.timeRange[1] : null;
    }
    state.selectedNode = null;
    state.edgeThreshold = 0;
    const th = $('edge-thresh'); if (th) th.value = 0;
    const tv = $('thresh-val'); if (tv) tv.textContent = '0.0';

    computeMetrics();
    state.groupColors = {};
    buildGroupPalette();
    renderGroupLegend();
    setupTimeSlider();
    renderControls();
    updateNodePanel();
    unfix();
    layout();
    fitToView();
    render();

    const n = state.graph.nodes.length, e = state.graph.links.length;
    if (state.aggregateBy) {
      const when = state.aggregateTime ? ` @ ${state.mapping.time}=${state.aggregateTime}` : '';
      setStatus(`Aggregated by ${state.aggregateBy} (${state.aggregateMode})${when}: ${n} groups · ${e} edges.`, 'ok');
    }
  }

  // Fill the aggregate "Time slice" dropdown from the mapped time column's
  // distinct values (Overall by default). Hidden when there's no time variable.
  function populateAggregateTimeOptions() {
    const sel = $('aggregate-time'); if (!sel) return;
    const row = $('aggregate-time-row');
    state.aggregateTime = '';
    const tcol = state.mapping.time;
    let vals = [];
    if (tcol && state.baseGraph) {
      vals = [...new Set(state.baseGraph.links.map((l) => l.timeRaw)
        .filter((v) => v !== null && v !== undefined && v !== ''))];
      vals.sort((a, b) => {
        const na = Number(a), nb = Number(b);
        return (isFinite(na) && isFinite(nb)) ? na - nb : String(a).localeCompare(String(b));
      });
    }
    if (row) row.style.display = vals.length ? '' : 'none';
    sel.innerHTML = `<option value="">Overall (all ${tcol || 'time'})</option>` +
      vals.map((v) => `<option value="${String(v).replace(/"/g, '&quot;')}">${tcol} = ${v}</option>`).join('');
  }

  // Categorical-ish node columns only: skip the id/label and the high-cardinality
  // /continuous columns (coords, counts). Used by both the aggregate and the
  // group-color dropdowns so neither offers nonsense like node_id or x/y.
  function categoricalNodeCols(maxCap) {
    const cols = state.nodeCols || [];
    const rows = state.nodeCsv || [];
    const N = rows.length || 1;
    const skip = new Set([state.mapping.nodeId, state.mapping.nodeLabel].filter(Boolean));
    const cap = Math.max(2, Math.min(maxCap, Math.floor(N * 0.6)));
    return cols.filter((c) => {
      if (skip.has(c)) return false;
      const distinct = new Set(rows.map((r) => r[c])).size;
      return distinct >= 2 && distinct <= cap;
    });
  }

  // Fill the "Aggregate by" dropdown (mapped group column first).
  function populateAggregateOptions() {
    const sel = $('aggregate-by'); if (!sel) return;
    const good = categoricalNodeCols(40);
    const grp = state.mapping.nodeGroup;
    if (grp && good.includes(grp)) { good.splice(good.indexOf(grp), 1); good.unshift(grp); }
    sel.innerHTML = '<option value="">None (raw network)</option>' +
      good.map((c) => `<option value="${String(c).replace(/"/g, '&quot;')}">${c}</option>`).join('');
  }

  // ── Project-dataset loader (fetch CSVs from playground-data/) ───
  // Endpoint columns are always the first two columns of each edges.csv;
  // node id is the first column of each nodes.csv. We fall back to those when
  // the name-based auto-mapper doesn't recognize the headers. DATASET_MAPPINGS
  // pins the right column to each aesthetic for our hardcoded sample networks
  // (esp. time columns that aren't called "time", and group columns the auto-
  // mapper doesn't know about, e.g. ecosystem_area / district / operator).
  const DATASET_MAPPINGS = {
    'amazon-last-mile':        { weight: 'packages',          time: 'day',    group: 'kind' },
    'uber-manhattan':          { weight: 'fare',              time: 'hour',   group: 'kind' },
    'semiconductor-supply':    { weight: 'annual_volume',                     group: 'kind' },
    'aerospace-components':    { weight: 'qty_per_aircraft',                  group: 'kind' },
    'mutualaid-quake':         { weight: 'amount',            time: 'period', group: 'kind' },
    'financial-contagion':     { weight: 'exposure',          time: 'period', group: 'type' },
    'airline-delays':          { weight: 'number_of_flights', time: 'block',  group: 'kind' },
    'power-grid':              { weight: 'capacity_mw',                       group: 'kind' },
    'campus-contact':          { weight: 'contact_minutes',   time: 'week',   group: 'kind' },
    'opensource-deps':         { weight: 'import_count',                      group: 'ecosystem_area' },
    'trade-commodity':         { weight: 'tonnes',            time: 'period', group: 'region' },
    'reorg-comms':             { weight: 'message_count',     time: 'period', group: 'dept' },
    'satellite-constellation': { weight: 'capacity_gbps',                     group: 'operator' },
    'drone-components':        { weight: 'coupling_strength',                 group: 'kind' },
    'transit-multimodal':      { weight: 'capacity',                         group: 'district' },
    'satellite-supply-chain':  { weight: 'units_per_year',                    group: 'kind' },
    'aircraft-supply-chain':   { weight: 'units_per_year',                    group: 'kind' },
    'ups-ground-network':      { weight: 'packages',                         group: 'kind' },
    'ups-package-flow':        { weight: 'weight_kg',                        group: 'region' },
    'nyc-realestate-capital':  { weight: 'invested_usd', time: 'quarter',   group: 'kind' },
    'nyc-realestate-portfolio':{ weight: 'co_investment_usd',               group: 'borough' },
  };

  function parseCsvUrl(url, cb, err) {
    Papa.parse(url, {
      download: true, header: true, dynamicTyping: true, skipEmptyLines: true,
      complete: (res) => cb(res.data, res.meta.fields || []),
      error: err || (() => {})
    });
  }

  function loadProjectDataset(key) {
    if (!key) return;
    setStatus('Loading ' + key + '…');
    const base = 'playground-data/';
    const cfg = DATASET_MAPPINGS[key] || {};
    parseCsvUrl(base + key + '-edges.csv', (edata, ecols) => {
      state.edgeCsv = edata;
      state.edgeCols = ecols;
      const m = autoMap(ecols);
      if (!m.from) m.from = ecols[0];
      if (!m.to)   m.to   = ecols[1];
      if (cfg.weight && ecols.includes(cfg.weight)) m.weight = cfg.weight;
      if (cfg.time && ecols.includes(cfg.time)) m.time = cfg.time;   // map non-"time" temporal cols
      state.mapping = Object.assign({}, state.mapping, m);
      parseCsvUrl(base + key + '-nodes.csv', (ndata, ncols) => {
        state.nodeCsv = ndata;
        state.nodeCols = ncols;
        const nm = autoMapNodes(ncols);
        if (cfg.nodeId && ncols.includes(cfg.nodeId)) nm.nodeId = cfg.nodeId;
        else if (!nm.nodeId) nm.nodeId = ncols[0];
        if (cfg.group && ncols.includes(cfg.group)) nm.nodeGroup = cfg.group;
        Object.assign(state.mapping, nm);
        renderMappers();
        loadGraph();
      }, () => {           // nodes file optional — build from edges alone
        state.nodeCsv = null;
        state.nodeCols = [];
        renderMappers();
        loadGraph();
      });
    }, () => setStatus('Could not load dataset "' + key + '".', 'err'));
  }

  // ── Layout ──────────────────────────────────────────────────
  function stopSim() {
    if (state.simulation) { state.simulation.stop(); state.simulation = null; }
  }

  function layout() {
    stopSim();
    const W = $('graph-stage').clientWidth, H = $('graph-stage').clientHeight;
    const nodes = activeNodes();
    const { links } = state.graph;

    if (state.layout === 'force') {
      // Scale forces with graph size so dense graphs spread out instead of
      // collapsing into a blob; cap long-range repulsion for performance.
      const N = nodes.length, E = links.length;
      const charge = -180 - 9 * Math.sqrt(E);
      const linkDist = 55 + 260 / Math.sqrt(Math.max(4, N));
      const sim = d3.forceSimulation(nodes)
        .force('link',    d3.forceLink(links).id((d) => d.id).distance(linkDist).strength(0.4))
        .force('charge',  d3.forceManyBody().strength(charge).distanceMax(700))
        .force('center',  d3.forceCenter(W / 2, H / 2))
        .force('collide', d3.forceCollide().radius((d) => 6 + Math.sqrt(d.deg) * 2.2));
      sim.on('tick', render);
      sim.on('end', () => { state.frozen = true; updateFreezeBtn(); fitToView(); });
      // Settle quickly and stop by default; "Live drift" keeps it gently moving.
      sim.alphaDecay(state.showDrift ? 0.0228 : 0.045);
      state.simulation = sim;
      state.frozen = false;
      updateFreezeBtn();
    } else if (state.layout === 'radial') {
      // Group by component, place each component as a hub-and-spoke (highest-degree node at center)
      const comps = {};
      nodes.forEach((n) => { (comps[state.metrics[n.id].component] ||= []).push(n); });
      const compIds = Object.keys(comps);
      compIds.forEach((cid, ci) => {
        const arr = comps[cid];
        arr.sort((a, b) => b.deg - a.deg);
        const cx = W * ((ci + 0.5) / compIds.length);
        const cy = H / 2;
        const R = Math.min(W / (compIds.length * 2.2), H / 2.4);
        arr.forEach((n, i) => {
          if (i === 0) { n.x = n.fx = cx; n.y = n.fy = cy; }
          else {
            const ang = ((i - 1) / Math.max(1, arr.length - 1)) * 2 * Math.PI;
            n.x = n.fx = cx + Math.cos(ang) * R;
            n.y = n.fy = cy + Math.sin(ang) * R;
          }
        });
      });
      render();
    } else if (state.layout === 'circle') {
      // Single circle per component — all nodes on the perimeter, no center hub
      const comps = {};
      nodes.forEach((n) => { (comps[state.metrics[n.id].component] ||= []).push(n); });
      const compIds = Object.keys(comps);
      compIds.forEach((cid, ci) => {
        const arr = comps[cid];
        arr.sort((a, b) => b.deg - a.deg);
        const cx = W * ((ci + 0.5) / compIds.length);
        const cy = H / 2;
        const R = Math.min(W / (compIds.length * 2.2), H / 2.4);
        const n0 = arr.length;
        arr.forEach((n, i) => {
          const ang = (i / Math.max(1, n0)) * 2 * Math.PI - Math.PI / 2;
          n.x = n.fx = cx + Math.cos(ang) * R;
          n.y = n.fy = cy + Math.sin(ang) * R;
        });
      });
      render();
    } else {
      // Hierarchical — layered top-to-bottom by BFS depth from highest-degree root per component
      const adj = {};
      nodes.forEach((n) => { adj[n.id] = []; });
      links.forEach((l) => {
        const s = typeof l.source === 'object' ? l.source.id : l.source;
        const t = typeof l.target === 'object' ? l.target.id : l.target;
        adj[s].push(t); adj[t].push(s);
      });
      const comps = {};
      nodes.forEach((n) => { (comps[state.metrics[n.id].component] ||= []).push(n); });
      const compIds = Object.keys(comps);
      const margin = 60;
      compIds.forEach((cid, ci) => {
        const arr = comps[cid].slice().sort((a, b) => b.deg - a.deg);
        const root = arr[0].id;
        // BFS depth from root
        const depth = { [root]: 0 };
        const queue = [root];
        while (queue.length) {
          const u = queue.shift();
          (adj[u] || []).forEach((v) => {
            if (depth[v] === undefined) { depth[v] = depth[u] + 1; queue.push(v); }
          });
        }
        // Group by depth layer
        const layers = {};
        arr.forEach((n) => {
          const d = depth[n.id] ?? 0;
          (layers[d] ||= []).push(n);
        });
        const layerKeys = Object.keys(layers).map(Number).sort((a, b) => a - b);
        const colW = W / compIds.length;
        const cx = colW * ci + colW / 2;
        const usableH = Math.max(120, H - margin * 2);
        const layerGap = layerKeys.length > 1 ? usableH / (layerKeys.length - 1) : 0;
        layerKeys.forEach((d, li) => {
          const row = layers[d];
          const rowCount = row.length;
          const y = margin + li * layerGap;
          row.forEach((n, i) => {
            const slot = (i - (rowCount - 1) / 2);
            const spread = Math.min(colW * 0.85, Math.max(60, rowCount * 60));
            const step = rowCount > 1 ? spread / (rowCount - 1) : 0;
            n.x = n.fx = cx + slot * step;
            n.y = n.fy = y;
          });
        });
      });
      render();
    }
    // Static layouts are positioned synchronously — fit them right away.
    if (state.layout !== 'force') fitToView(false);
  }

  // ── Zoom / pan / fit-to-view ────────────────────────────────
  function setupZoom() {
    const svgEl = $('graph'); if (!svgEl) return;
    const svg = d3.select(svgEl);
    state.zoom = d3.zoom().scaleExtent([0.05, 8]).on('zoom', (e) => {
      state.zoomTransform = e.transform;
      svg.select('g.viewport').attr('transform', e.transform);
    });
    svg.call(state.zoom).on('dblclick.zoom', null);
  }

  function fitToView(animate = true) {
    if (!state.graph || !state.graph.nodes.length || !state.zoom) return;
    const svgEl = $('graph');
    const W = svgEl.clientWidth, H = svgEl.clientHeight;
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    activeNodes().forEach((n) => {
      if (!isFinite(n.x) || !isFinite(n.y)) return;
      if (n.x < minX) minX = n.x; if (n.x > maxX) maxX = n.x;
      if (n.y < minY) minY = n.y; if (n.y > maxY) maxY = n.y;
    });
    if (!isFinite(minX)) return;
    const pad = 50;
    const cw = Math.max(1, maxX - minX), ch = Math.max(1, maxY - minY);
    let scale = Math.min((W - 2 * pad) / cw, (H - 2 * pad) / ch);
    scale = Math.max(0.05, Math.min(scale, 4));
    const cx = (minX + maxX) / 2, cy = (minY + maxY) / 2;
    const t = d3.zoomIdentity.translate(W / 2 - scale * cx, H / 2 - scale * cy).scale(scale);
    const sel = d3.select(svgEl);
    // Re-render once the fit settles so node/label counter-scaling uses the
    // final zoom level (keeps markers legible when a big graph is zoomed out).
    if (animate) sel.transition().duration(450).on('end', () => render()).call(state.zoom.transform, t);
    else { sel.call(state.zoom.transform, t); render(); }
  }

  // Release fixed positions when switching layouts
  function unfix() {
    state.graph.nodes.forEach((n) => { n.fx = null; n.fy = null; });
  }

  // ── Freeze / re-run layout ──────────────────────────────────
  function updateFreezeBtn() {
    const b = $('btn-freeze'); if (!b) return;
    b.textContent = state.frozen ? '▶' : '❄';
    b.title = state.frozen ? 'Re-run layout' : 'Freeze layout';
  }

  function toggleFreeze() {
    if (!state.graph) return;
    if (state.frozen) {            // re-run the layout from current positions
      state.frozen = false;
      layout();
      if (state.simulation) state.simulation.alpha(0.6).restart();
    } else {                        // stop now — pin nodes where they are
      stopSim();
      state.frozen = true;
    }
    updateFreezeBtn();
  }

  // ── Render ──────────────────────────────────────────────────
  function visibleLinks() {
    const tF = state.timeFilter;
    return state.graph.links.filter((l) => {
      if (l.weight < state.edgeThreshold) return false;
      if (tF !== null && l.time !== null && l.time !== undefined && l.time > tF) return false;
      return true;
    });
  }

  // Nodes to display/lay out. With dropIsolates on (default), nodes that never
  // appear in the edgelist (degree 0) are hidden — only edge-connected plants show.
  function activeNodes() {
    if (!state.graph) return [];
    return state.dropIsolates
      ? state.graph.nodes.filter((n) => n.deg > 0)
      : state.graph.nodes;
  }

  const UNIFORM_COLOR = '#39FF14';

  function nodeColor(n) {
    if (state.colorBy === 'community' && state.metrics[n.id]) {
      const c = state.metrics[n.id].component || 0;
      const pal = state.commPalette || [UNIFORM_COLOR];
      return pal[(c - 1 + pal.length) % pal.length];
    }
    if (state.colorBy === 'group' && n.group) {
      return state.groupColors[n.group] || state.groupPalette[n.group] || UNIFORM_COLOR;
    }
    return UNIFORM_COLOR;
  }

  // Assign each distinct group value a color from the chosen palette. Rebuilt
  // per loaded graph / palette change; user overrides live in state.groupColors.
  function buildGroupPalette() {
    state.groupPalette = {};
    state.commPalette = paletteColors(state.palette, 8);   // for community coloring
    if (!state.graph) return;
    const groups = Array.from(new Set(
      state.graph.nodes.map((n) => n.group).filter((g) => g !== null && g !== undefined && g !== '')
    )).sort();
    const cols = paletteColors(state.palette, groups.length);
    groups.forEach((g, i) => { state.groupPalette[g] = cols[i]; });
    updateSwatches();
  }

  // Populate the <datalist> that the per-group color pickers suggest, so the
  // swatch presets match the chosen palette (Chromium shows these in the picker)
  // instead of the browser's default red/blue/green/black set.
  function updateSwatches() {
    const dl = $('viz-swatches'); if (!dl) return;
    const swatches = paletteColors(state.palette, 12);
    dl.innerHTML = [...new Set(swatches)].map((c) => `<option value="${c}">`).join('');
  }

  // Render the per-group legend with a color picker for each group value.
  function renderGroupLegend() {
    const box = $('group-legend'); if (!box) return;
    if (state.colorBy !== 'group') { box.style.display = 'none'; box.innerHTML = ''; return; }
    box.style.display = 'flex';
    const groups = Object.keys(state.groupPalette);
    if (!groups.length) {
      box.innerHTML = '<div class="lg-empty">No group attribute set. Pick a <strong>Group column</strong> above.</div>';
      return;
    }
    box.innerHTML = groups.map((g) => {
      const color = state.groupColors[g] || state.groupPalette[g];
      const safe = String(g).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');
      return `<div class="lg-row"><input type="color" list="viz-swatches" value="${color}" data-group="${safe}" title="Recolor ${safe}"><span class="lg-name" title="${safe}">${safe}</span></div>`;
    }).join('');
  }

  // Fill the Display-panel "Group column" dropdown with categorical node columns
  // (coloring tolerates a few more groups than aggregation). Always include the
  // currently-mapped group even if it would otherwise be filtered out.
  function populateGroupColumnOptions() {
    const sel = $('group-col'); if (!sel) return;
    const good = categoricalNodeCols(60);
    const grp = state.mapping.nodeGroup;
    if (grp && !good.includes(grp)) good.unshift(grp);
    sel.innerHTML = '<option value="">(none — uniform)</option>' +
      good.map((c) => `<option value="${String(c).replace(/"/g, '&quot;')}" ${grp === c ? 'selected' : ''}>${c}</option>`).join('');
  }

  // Live-change the node group column: recompute each node's group from its raw
  // attributes, rebuild the palette/legend, and recolor — no reload needed.
  function setGroupColumn(col) {
    state.mapping.nodeGroup = col || null;
    if (state.baseGraph) state.baseGraph.nodes.forEach((n) => {
      const v = col && n.attrs ? n.attrs[col] : null;
      n.group = (v === undefined || v === null || v === '') ? null : String(v);
    });
    buildGroupPalette();
    renderGroupLegend();
    render();
  }

  function nodeRadius(n) {
    let d = state.metrics[n.id]?.degree || 0;
    // weighted degree is on a far larger scale than a count — map it back onto
    // the count range so radii stay comparable.
    if (state.useWeights && state.maxWeighted > 0) d = (d / state.maxWeighted) * (state.maxCount || 10);
    return (4 + Math.sqrt(d) * 2.2) * state.nodeScale;
  }

  function render() {
    const svgEl = $('graph');
    const svg = d3.select(svgEl);
    svg.selectAll('*').remove();
    if (!state.graph) return;

    const maxW = d3.max(state.graph.links, (l) => l.weight) || 1;
    const vlinks = visibleLinks();

    // Zoomable / pannable viewport — everything draws inside this group so the
    // d3.zoom transform pans and scales the whole network together.
    const root = svg.append('g').attr('class', 'viewport');
    if (state.zoomTransform) root.attr('transform', state.zoomTransform);

    // Edges — fade and thin them on dense graphs so structure shows through.
    const dens = vlinks.length > 2000 ? 0.4 : vlinks.length > 800 ? 0.6 : 1;
    const g = root.append('g').attr('class', 'links');
    g.selectAll('line').data(vlinks).enter().append('line')
      .attr('stroke', 'rgba(57,255,20,0.55)')
      .attr('stroke-width', (l) => (0.6 + (l.weight / maxW) * 3.5) * (dens < 1 ? 0.7 : 1))
      .attr('stroke-opacity', (l) => (0.35 + 0.55 * (l.weight / maxW)) * dens)
      .attr('x1', (l) => (l.source.x ?? 0))
      .attr('y1', (l) => (l.source.y ?? 0))
      .attr('x2', (l) => (l.target.x ?? 0))
      .attr('y2', (l) => (l.target.y ?? 0));

    if (state.showEdgeLabels) {
      root.append('g').selectAll('text').data(vlinks).enter().append('text')
        .attr('x', (l) => ((l.source.x ?? 0) + (l.target.x ?? 0)) / 2)
        .attr('y', (l) => ((l.source.y ?? 0) + (l.target.y ?? 0)) / 2)
        .attr('text-anchor', 'middle')
        .attr('font-family', 'Space Mono, monospace')
        .attr('font-size', '9px')
        .attr('fill', 'rgba(134, 239, 172, 0.85)')
        .text((l) => l.weight.toFixed(0));
    }

    // Nodes
    const nodesShown = activeNodes();
    // Keep markers/labels legible when fit-to-view zooms a big network out:
    // counter-scale by the inverse zoom (with a cap), and bump sizes on phones.
    const k = (state.zoomTransform && state.zoomTransform.k) ? state.zoomTransform.k : 1;
    const small = (typeof window !== 'undefined' ? window.innerWidth : 1000) < 700;
    const boost = Math.min(small ? 3.0 : 2.4, Math.max(1, 1 / k));
    const rOf = (n) => nodeRadius(n) * boost;

    // On big graphs / small screens, only label the most-connected nodes
    // (plus the selected one) — a wall of overlapping labels helps no one.
    let labelIds = null;
    if (state.showNodeLabels) {
      const capN = small ? 28 : 90;
      if (nodesShown.length > capN) {
        const topK = small ? 12 : 24;
        labelIds = new Set(
          nodesShown.slice()
            .sort((a, b) => (state.metrics[b.id]?.degree || 0) - (state.metrics[a.id]?.degree || 0))
            .slice(0, topK).map((n) => n.id));
      }
    }
    const labelFont = (small ? 13 : 10.5) * boost;

    const ng = root.append('g').attr('class', 'nodes');
    const nsel = ng.selectAll('g').data(nodesShown).enter().append('g')
      .attr('transform', (n) => `translate(${n.x ?? 0},${n.y ?? 0})`)
      .style('cursor', 'pointer')
      .on('click', (_e, n) => { state.selectedNode = n.id; updateNodePanel(); render(); });

    nsel.filter((n) => state.selectedNode === n.id).append('circle')
      .attr('r', (n) => rOf(n) + 5)
      .attr('fill', 'none')
      .attr('stroke', (n) => nodeColor(n))
      .attr('stroke-width', 2)
      .attr('stroke-dasharray', '4,3').attr('opacity', 0.85);

    nsel.append('circle')
      .attr('r', (n) => rOf(n))
      .attr('fill', (n) => nodeColor(n))
      .attr('fill-opacity', 0.9)
      .attr('stroke', '#050a05')
      .attr('stroke-width', 1.2)
      .style('filter', (n) => `drop-shadow(0 0 ${6 * state.nodeScale}px ${nodeColor(n)})`);

    if (state.showNodeLabels) {
      nsel.filter((n) => (!labelIds || labelIds.has(n.id) || n.id === state.selectedNode))
        .append('text')
        .attr('y', (n) => -rOf(n) - 5)
        .attr('text-anchor', 'middle')
        .attr('font-family', 'Space Mono, monospace')
        .attr('font-size', labelFont + 'px')
        .attr('letter-spacing', '0.05em')
        .attr('fill', '#d1fae5')
        .text((n) => n.label.length > 16 ? n.label.slice(0, 14) + '…' : n.label);
    }

    updateStats(vlinks.length);
  }

  // ── Stats overlay + node panel ──────────────────────────────
  function updateStats(visibleEdges) {
    if (!state.graph) return;
    const shown = activeNodes();
    const N = shown.length;
    const E = visibleEdges ?? state.graph.links.length;
    $('stat-nodes').textContent = N.toLocaleString();
    $('stat-edges').textContent = E.toLocaleString();
    const comps = new Set(shown.map((n) => state.metrics[n.id]?.component)).size;
    $('stat-comps').textContent = comps;
    const density = N > 1 ? (2 * E / (N * (N - 1))).toFixed(3) : '0';
    $('stat-density').textContent = density;
  }

  function updateNodePanel() {
    const wrap = $('node-card-wrap');
    if (!state.selectedNode) { wrap.innerHTML = '<div class="node-empty">Click any node to inspect.</div>'; return; }
    const n = state.graph.nodes.find((x) => x.id === state.selectedNode);
    const m = state.metrics[n.id] || {};
    wrap.innerHTML = `
      <div class="node-card">
        <div class="t-label" style="color: ${nodeColor(n)}">Selected · Component ${m.component}</div>
        <h3>${n.label}</h3>
        <div class="kvs">
          <div class="kv"><span class="k">Degree</span><span class="v">${m.degree ?? '—'}</span></div>
          <div class="kv"><span class="k">Weighted degree</span><span class="v">${(m.weighted ?? 0).toFixed(1)}</span></div>
          <div class="kv"><span class="k">Betweenness</span><span class="v">${(m.betweenness ?? 0).toFixed(3)}</span></div>
          <div class="kv"><span class="k">Component</span><span class="v">${m.component}</span></div>
          ${n.group ? `<div class="kv"><span class="k">Group</span><span class="v">${n.group}</span></div>` : ''}
        </div>
      </div>`;

    // Top-degree mini list
    const ranked = state.graph.nodes.slice()
      .sort((a, b) => (state.metrics[b.id].degree - state.metrics[a.id].degree))
      .slice(0, 6);
    const max = state.metrics[ranked[0].id].degree || 1;
    $('top-degree-list').innerHTML = ranked.map((nn) => `
      <div class="bar-row">
        <div class="bn">${nn.label.length > 12 ? nn.label.slice(0, 10) + '…' : nn.label}</div>
        <div class="br"><div class="bf" style="width:${(state.metrics[nn.id].degree / max) * 100}%"></div></div>
        <div class="bv">${state.metrics[nn.id].degree}</div>
      </div>`).join('');

    const rankedB = state.graph.nodes.slice()
      .sort((a, b) => (state.metrics[b.id].betweenness - state.metrics[a.id].betweenness))
      .slice(0, 6);
    const maxB = state.metrics[rankedB[0].id].betweenness || 1;
    $('top-betw-list').innerHTML = rankedB.map((nn) => `
      <div class="bar-row">
        <div class="bn">${nn.label.length > 12 ? nn.label.slice(0, 10) + '…' : nn.label}</div>
        <div class="br"><div class="bf" style="width:${(state.metrics[nn.id].betweenness / Math.max(maxB, 0.0001)) * 100}%"></div></div>
        <div class="bv">${state.metrics[nn.id].betweenness.toFixed(2)}</div>
      </div>`).join('');
  }

  // ── Controls ────────────────────────────────────────────────
  function setupTimeSlider() {
    const wrap = $('time-slider-wrap');
    if (!state.timeRange) { wrap.style.display = 'none'; return; }
    wrap.style.display = 'block';
    const sl = $('time-slider');
    sl.min = state.timeRange[0];
    sl.max = state.timeRange[1];
    sl.step = Math.max(1, (state.timeRange[1] - state.timeRange[0]) / 200);
    sl.value = state.timeRange[1];
    state.timeFilter = state.timeRange[1];
    $('time-slider-val').textContent = formatTime(state.timeRange[1]);
  }
  function formatTime(t) {
    if (!isFinite(t)) return String(t);
    if (t > 1e11) return new Date(t).toISOString().slice(0, 10);
    return Math.round(t).toString();
  }

  function renderControls() {
    // Set node-scale slider label
    $('node-scale-val').textContent = state.nodeScale.toFixed(1) + 'x';
    $('thresh-val').textContent = state.edgeThreshold.toFixed(1);
  }

  function wireControls() {
    document.querySelectorAll('.seg-layout').forEach((b) => {
      b.addEventListener('click', () => {
        document.querySelectorAll('.seg-layout').forEach((s) => s.classList.remove('active'));
        b.classList.add('active');
        state.layout = b.dataset.layout;
        if (state.graph) { unfix(); layout(); render(); }
      });
    });

    $('node-scale').addEventListener('input', (e) => {
      state.nodeScale = (+e.target.value) / 100;
      $('node-scale-val').textContent = state.nodeScale.toFixed(1) + 'x';
      render();
    });
    $('edge-thresh').addEventListener('input', (e) => {
      const max = d3.max(state.graph?.links || [], (l) => l.weight) || 1;
      state.edgeThreshold = (+e.target.value) / 100 * max;
      $('thresh-val').textContent = state.edgeThreshold.toFixed(1);
      render();
    });

    document.querySelectorAll('[data-toggle]').forEach((row) => {
      row.addEventListener('click', () => {
        const t = row.querySelector('.toggle');
        t.classList.toggle('on');
        const on = t.classList.contains('on');
        const key = row.dataset.toggle;
        if (key === 'edges')      state.showEdgeLabels = on;
        if (key === 'labels')     state.showNodeLabels = on;
        if (key === 'isolates') {
          state.dropIsolates = on;
          // the displayed node set changed — re-lay out, refit, and redraw
          if (state.graph) { unfix(); layout(); fitToView(); }
        }
        if (key === 'weights') {
          state.useWeights = on;
          // degree & betweenness definitions changed — recompute and refresh
          if (state.graph) { computeMetrics(); updateNodePanel(); }
        }
        if (key === 'drift') {
          state.showDrift = on;
          if (state.simulation) {
            state.simulation.alphaDecay(on ? 0.0228 : 0.045);
            if (on) { state.frozen = false; updateFreezeBtn(); state.simulation.alpha(0.4).restart(); }
          }
        }
        render();
      });
    });

    // Color-nodes-by selector
    const colorBySel = $('color-by');
    if (colorBySel) colorBySel.addEventListener('change', (e) => {
      state.colorBy = e.target.value;
      renderGroupLegend();
      render();
    });

    const groupColSel = $('group-col');
    if (groupColSel) groupColSel.addEventListener('change', (e) => setGroupColumn(e.target.value));

    const paletteSel = $('palette');
    if (paletteSel) paletteSel.addEventListener('change', (e) => {
      state.palette = e.target.value;
      state.groupColors = {};       // palette changed → drop per-group overrides
      buildGroupPalette();
      renderGroupLegend();
      render();
    });

    // Per-group color overrides (event-delegated; the legend is rebuilt on load)
    const legend = $('group-legend');
    if (legend) legend.addEventListener('input', (e) => {
      const inp = e.target.closest('input[type=color]');
      if (!inp) return;
      state.groupColors[inp.dataset.group] = inp.value;
      render();
    });

    // Experimental aggregation
    const aggBy = $('aggregate-by');
    if (aggBy) aggBy.addEventListener('change', (e) => {
      state.aggregateBy = e.target.value;
      if (state.baseGraph) rebuildView();
    });
    const aggMode = $('aggregate-mode');
    if (aggMode) aggMode.addEventListener('change', (e) => {
      state.aggregateMode = e.target.value;
      if (state.baseGraph && state.aggregateBy) rebuildView();
    });
    const aggTime = $('aggregate-time');
    if (aggTime) aggTime.addEventListener('change', (e) => {
      state.aggregateTime = e.target.value;
      if (state.baseGraph && state.aggregateBy) rebuildView();
    });

    $('time-slider').addEventListener('input', (e) => {
      state.timeFilter = +e.target.value;
      $('time-slider-val').textContent = formatTime(state.timeFilter);
      render();
    });

    $('btn-load').addEventListener('click', () => {
      // Pick up dropdown values just in case
      document.querySelectorAll('#mapper-fields select').forEach((sel) => {
        state.mapping[sel.dataset.key] = sel.value || null;
      });
      loadGraph();
    });

    $('btn-sample').addEventListener('click', () => loadSampleGraph());
    $('btn-png').addEventListener('click', exportPng);

    $('edge-file').addEventListener('change', (e) => {
      if (e.target.files[0]) handleEdgeFile(e.target.files[0]);
    });
    $('node-file').addEventListener('change', (e) => {
      if (e.target.files[0]) handleNodeFile(e.target.files[0]);
    });

    const sampleSel = $('sample-select');
    if (sampleSel) sampleSel.addEventListener('change', (e) => loadProjectDataset(e.target.value));

    const svgSel = () => d3.select($('graph'));
    const zin = $('btn-zoom-in'), zout = $('btn-zoom-out'), zfit = $('btn-fit');
    if (zin)  zin.addEventListener('click',  () => state.zoom && svgSel().transition().duration(180).call(state.zoom.scaleBy, 1.4));
    if (zout) zout.addEventListener('click', () => state.zoom && svgSel().transition().duration(180).call(state.zoom.scaleBy, 1 / 1.4));
    if (zfit) zfit.addEventListener('click', () => fitToView());
    const zfreeze = $('btn-freeze');
    if (zfreeze) zfreeze.addEventListener('click', () => toggleFreeze());

    window.addEventListener('resize', () => { if (state.graph && !state.frozen) layout(); });
  }

  // ── PNG export ──────────────────────────────────────────────
  function exportPng() {
    const svgEl = $('graph');
    const W = svgEl.clientWidth, H = svgEl.clientHeight;
    const clone = svgEl.cloneNode(true);
    clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    clone.setAttribute('width', W); clone.setAttribute('height', H);
    // Inline background
    const bg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    bg.setAttribute('width', W); bg.setAttribute('height', H);
    bg.setAttribute('fill', '#050a05');
    clone.insertBefore(bg, clone.firstChild);

    const data = new XMLSerializer().serializeToString(clone);
    const blob = new Blob([data], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const img = new Image();
    img.onload = () => {
      const c = document.createElement('canvas');
      const scale = 2; c.width = W * scale; c.height = H * scale;
      const ctx = c.getContext('2d');
      ctx.scale(scale, scale);
      ctx.drawImage(img, 0, 0);
      URL.revokeObjectURL(url);
      c.toBlob((b) => {
        const a = document.createElement('a');
        a.href = URL.createObjectURL(b); a.download = 'network.png';
        document.body.appendChild(a); a.click(); a.remove();
      });
    };
    img.src = url;
  }

  // ── Sample / demo graph ─────────────────────────────────────
  function randInt(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }
  function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }

  function generateSampleGraph() {
    // Build a randomized 3-tier supply-chain-like network.
    // Tiers: Suppliers → Hubs/Consolidators → Distribution Centers → Retailers.
    const nSuppliers  = randInt(4, 8);
    const nHubs       = randInt(1, 3);
    const nDCs        = randInt(2, 4);
    const nRetailers  = randInt(4, 9);

    const suppliers = Array.from({ length: nSuppliers }, (_, i) => `Supplier_${String.fromCharCode(65 + i)}`);
    const hubs      = Array.from({ length: nHubs },      (_, i) => nHubs === 1 ? 'Hub_Central' : `Hub_${i + 1}`);
    const dcs       = Array.from({ length: nDCs },       (_, i) => `DC_${['North','South','East','West'][i] || (i + 1)}`);
    const retailers = Array.from({ length: nRetailers }, (_, i) => `Retailer_${i + 1}`);

    const tMax = randInt(4, 7);
    const edges = [];

    // Each supplier connects to 1–2 hubs
    suppliers.forEach((s) => {
      const hs = new Set();
      const k = randInt(1, Math.min(2, hubs.length));
      while (hs.size < k) hs.add(pick(hubs));
      hs.forEach((h) => edges.push({ from: s, to: h, weight: randInt(2, 8), time: randInt(1, Math.max(1, Math.floor(tMax / 2))) }));
    });

    // Each hub connects to most DCs
    hubs.forEach((h) => {
      dcs.forEach((d) => {
        if (Math.random() < 0.75) edges.push({ from: h, to: d, weight: randInt(3, 9), time: randInt(1, tMax) });
      });
    });

    // Each retailer pulls from 1–2 DCs
    retailers.forEach((r) => {
      const ds = new Set();
      const k = randInt(1, Math.min(2, dcs.length));
      while (ds.size < k) ds.add(pick(dcs));
      ds.forEach((d) => edges.push({ from: d, to: r, weight: randInt(1, 5), time: randInt(2, tMax) }));
    });

    // A few sideways retailer-to-retailer links
    const sideways = randInt(0, Math.max(0, Math.floor(nRetailers / 3)));
    for (let i = 0; i < sideways; i++) {
      const a = pick(retailers), b = pick(retailers);
      if (a !== b) edges.push({ from: a, to: b, weight: 1, time: randInt(3, tMax) });
    }

    return edges;
  }

  function loadSampleGraph() {
    const edgeCsv = generateSampleGraph();
    state.edgeCsv = edgeCsv;
    state.edgeCols = ['from', 'to', 'weight', 'time'];
    state.nodeCsv = null;
    state.nodeCols = [];
    state.mapping = { from: 'from', to: 'to', weight: 'weight', time: 'time', nodeId: null, nodeLabel: null, nodeGroup: null };
    renderMappers();
    loadGraph();
  }

  // ── Init ────────────────────────────────────────────────────
  function init() {
    setupZoom();
    wireControls();
    renderControls();
    renderGroupLegend();
  }
  document.addEventListener('DOMContentLoaded', init);

  global.NetSciViz = { state, loadSampleGraph, loadGraph, loadProjectDataset, paletteColors };
})(window);
