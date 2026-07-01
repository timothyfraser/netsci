// ============================================================
// SYSEN 5470 — Network Visualizer v2 (core engine)
// EXPERIMENTAL — used only by docs/visualizer2.html (unlinked).
// Clone of viz.js with: event bus, removed-node awareness, scenario
// nodes/edges in the base graph, and a shared graph-algorithm utility
// namespace (NetSciViz2.utils) that feature modules consume.
// ============================================================
(function (global) {
  'use strict';

  // ── Event bus ───────────────────────────────────────────────
  // Tiny pub/sub so feature modules can react to lifecycle without
  // monkey-patching core functions. Events:
  //   graph-loaded      → after loadGraph + base graph is set
  //   view-rebuilt      → after rebuildView (agg change, group col change, etc.)
  //   metrics-updated   → after computeMetrics
  //   render            → at end of render() (per frame for force layout)
  //   node-selected     → user clicked a node ({id})
  //   stage-clicked     → user clicked empty stage at SVG coords ({sx, sy})
  //   removed-changed   → removal set mutated (by viz2-removal)
  //   scenario-changed  → scenario nodes/edges mutated (by viz2-scenarios)
  const _listeners = Object.create(null);
  function on(event, fn) {
    (_listeners[event] = _listeners[event] || []).push(fn);
  }
  function emit(event, payload) {
    (_listeners[event] || []).slice().forEach((fn) => {
      try { fn(payload); } catch (e) { console.error('[viz2 ' + event + ']', e); }
    });
  }

  // ── State ───────────────────────────────────────────────────
  const state = {
    edgeCsv:  null, nodeCsv:  null,
    edgeCols: [],   nodeCols: [],
    mapping: { from: null, to: null, weight: null, time: null,
               nodeId: null, nodeLabel: null, nodeGroup: null },
    graph: null,
    baseGraph: null,
    aggregateBy: '', aggregateMode: 'sum', aggregateTime: '',
    layout: 'force',
    showEdgeLabels: false, showNodeLabels: true,
    colorBy: 'group',
    groupPalette: {}, groupColors: {},
    dropIsolates: true, showDrift: false, frozen: false,
    nodeScale: 1, edgeThreshold: 0,
    timeFilter: null, timeRange: null,
    selectedNode: null, simulation: null,
    zoom: null, zoomTransform: null,
    palette: 'neon', useWeights: false,
    metrics: {},
    // ── v2 additions ──
    removedNodes: new Set(),          // ids removed by Feature B
    scenarioNodes: [],                // {id,label,group,...,isScenario:true}
    scenarioLinks: [],                // {source,target,weight,isScenario:true}
    selectedHopByEdge: null,          // Map<link_ref, depth 1..6> — set by viz2-removal
    selectedHopFocus: 0,              // 0 = no highlight; K = highlight depth-K edges only
    selectedHopCounts: null,          // { 1: N, 2: N, ... 6: N } tabulation
    stageClickMode: null,             // null | 'add-node' | 'add-edge' (Feature D1)
    addEdgePending: null              // first endpoint id when in 'add-edge' mode
  };

  const NEON = ['#39FF14', '#fbbf24', '#f472b6', '#818cf8',
                '#fb923c', '#a78bfa', '#5eead4', '#f87171'];
  const MAKO_STOPS = ['#0B0405', '#3A2C59', '#395D9C', '#3497A9',
                      '#5CC8A7', '#A5DFB8', '#DEF5E5'];

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
      for (const n of names) { const i = lower.indexOf(n); if (i >= 0) return cols[i]; }
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
      for (const n of names) { const i = lower.indexOf(n); if (i >= 0) return cols[i]; }
      return null;
    };
    return {
      nodeId:    find('node_id', 'id', 'node', 'nodeid', 'name'),
      nodeLabel: find('label', 'name', 'title'),
      nodeGroup: find('group', 'community', 'cluster', 'type', 'category', 'kind', 'tier')
    };
  }

  // ── Build graph from mapped CSV (+ scenario additions) ──────
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
      const tRaw = m.time ? row[m.time] : null;
      let t = tRaw;
      if (t !== null && t !== undefined && t !== '') {
        const tn = Number(t);
        t = isFinite(tn) ? tn : Date.parse(t);
        if (isFinite(t)) times.push(t);
      } else t = null;
      links.push({ source: A.id, target: B.id, weight: w, time: t, timeRaw: (tRaw === undefined ? null : tRaw) });
      A.deg++; B.deg++; A.weighted += w; B.weighted += w;
    });

    if (state.nodeCsv && state.mapping.nodeId) {
      state.nodeCsv.forEach((row) => {
        const id = String(row[state.mapping.nodeId]);
        if (!nodeMap.has(id)) nodeMap.set(id, { id, label: id, group: null, deg: 0, weighted: 0 });
        const n = nodeMap.get(id);
        n.attrs = row;
        if (state.mapping.nodeLabel) n.label = String(row[state.mapping.nodeLabel] ?? id);
        if (state.mapping.nodeGroup) n.group = String(row[state.mapping.nodeGroup] ?? '');
      });
    }

    // v2: fold scenario nodes/edges into the base graph
    state.scenarioNodes.forEach((sn) => {
      if (!nodeMap.has(sn.id)) {
        nodeMap.set(sn.id, Object.assign({ deg: 0, weighted: 0 }, sn));
      }
    });
    state.scenarioLinks.forEach((sl) => {
      const A = ensureNode(sl.source), B = ensureNode(sl.target);
      const w = isFinite(sl.weight) && sl.weight > 0 ? sl.weight : 1;
      links.push({ source: A.id, target: B.id, weight: w, time: null, timeRaw: null, isScenario: true });
      A.deg++; B.deg++; A.weighted += w; B.weighted += w;
    });

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

  // ── Metrics — degree, betweenness, components ───────────────
  // v2: excludes nodes in state.removedNodes (Feature B). Removed nodes
  // get a metrics entry of {degree:0,weighted:0,betweenness:0,component:0}
  // so any caller that looks them up by id sees a zeroed-out node.
  function computeMetrics() {
    const { nodes, links } = state.graph;
    const removed = state.removedNodes;
    const activeNodesArr = nodes.filter((n) => !removed.has(n.id));
    const activeIds = activeNodesArr.map((n) => n.id);
    const isActive = new Set(activeIds);

    const adj = {};
    activeIds.forEach((id) => { adj[id] = []; });
    links.forEach((l) => {
      const s = typeof l.source === 'object' ? l.source.id : l.source;
      const t = typeof l.target === 'object' ? l.target.id : l.target;
      if (!isActive.has(s) || !isActive.has(t)) return;
      adj[s].push(t); adj[t].push(s);
    });

    // recompute per-node deg / weighted on the ACTIVE subgraph
    activeNodesArr.forEach((n) => { n.deg = 0; n.weighted = 0; });
    const wNode = {};
    links.forEach((l) => {
      const s = typeof l.source === 'object' ? l.source.id : l.source;
      const t = typeof l.target === 'object' ? l.target.id : l.target;
      if (!isActive.has(s) || !isActive.has(t)) return;
      wNode[s] = (wNode[s] || 0) + (l.weight || 1);
      wNode[t] = (wNode[t] || 0) + (l.weight || 1);
    });
    activeNodesArr.forEach((n) => {
      n.deg = (adj[n.id] || []).length;
      n.weighted = wNode[n.id] || 0;
    });

    // Components (BFS) over the active subgraph
    const compOf = {}; let cid = 0;
    activeIds.forEach((id) => {
      if (compOf[id] !== undefined) return;
      cid++; const q = [id]; let qi = 0;
      while (qi < q.length) {
        const u = q[qi++];
        if (compOf[u] !== undefined) continue;
        compOf[u] = cid;
        (adj[u] || []).forEach((v) => { if (compOf[v] === undefined) q.push(v); });
      }
    });

    // Brandes betweenness — UNweighted (BFS) or weighted (Dijkstra, dist=1/weight).
    // Normalize by (N-1)(N-2) (Brandes' undirected convention used by the course).
    const N = activeIds.length;
    const betw = {}; activeIds.forEach((id) => { betw[id] = 0; });

    if (N <= 600 && !state.useWeights) {
      activeIds.forEach((s) => {
        const stack = [], pred = {}, sigma = {}, dist = {};
        activeIds.forEach((id) => { pred[id] = []; sigma[id] = 0; dist[id] = -1; });
        sigma[s] = 1; dist[s] = 0;
        const q = [s]; let qi = 0;
        while (qi < q.length) {
          const v = q[qi++]; stack.push(v);
          (adj[v] || []).forEach((w) => {
            if (dist[w] < 0) { q.push(w); dist[w] = dist[v] + 1; }
            if (dist[w] === dist[v] + 1) { sigma[w] += sigma[v]; pred[w].push(v); }
          });
        }
        const delta = {}; activeIds.forEach((id) => { delta[id] = 0; });
        while (stack.length) {
          const w = stack.pop();
          pred[w].forEach((v) => { delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w]); });
          if (w !== s) betw[w] += delta[w];
        }
      });
      const norm = (N - 1) * (N - 2);
      if (norm > 0) activeIds.forEach((id) => { betw[id] = betw[id] / norm; });
    } else if (N <= 600 && state.useWeights) {
      const adjW = {}; activeIds.forEach((id) => { adjW[id] = new Map(); });
      links.forEach((l) => {
        const s = typeof l.source === 'object' ? l.source.id : l.source;
        const t = typeof l.target === 'object' ? l.target.id : l.target;
        if (!isActive.has(s) || !isActive.has(t)) return;
        const d = 1 / (l.weight > 0 ? l.weight : 1);
        if (!adjW[s].has(t) || adjW[s].get(t) > d) adjW[s].set(t, d);
        if (!adjW[t].has(s) || adjW[t].get(s) > d) adjW[t].set(s, d);
      });
      const EPS = 1e-9;
      activeIds.forEach((s) => {
        const dist = {}, sigma = {}, pred = {}, done = {};
        activeIds.forEach((id) => { dist[id] = Infinity; sigma[id] = 0; pred[id] = []; });
        dist[s] = 0; sigma[s] = 1;
        const S = [];
        for (let cnt = 0; cnt < N; cnt++) {
          let u = null, best = Infinity;
          for (const id of activeIds) { if (!done[id] && dist[id] < best) { best = dist[id]; u = id; } }
          if (u === null || best === Infinity) break;
          done[u] = true; S.push(u);
          adjW[u].forEach((dw, w) => {
            const nd = dist[u] + dw;
            if (nd < dist[w] - EPS) { dist[w] = nd; sigma[w] = sigma[u]; pred[w] = [u]; }
            else if (Math.abs(nd - dist[w]) < EPS) { sigma[w] += sigma[u]; pred[w].push(u); }
          });
        }
        const delta = {}; activeIds.forEach((id) => { delta[id] = 0; });
        while (S.length) {
          const w = S.pop();
          pred[w].forEach((v) => { delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w]); });
          if (w !== s) betw[w] += delta[w];
        }
      });
      const norm = (N - 1) * (N - 2);
      if (norm > 0) activeIds.forEach((id) => { betw[id] = betw[id] / norm; });
    }

    state.metrics = {};
    nodes.forEach((n) => {
      if (removed.has(n.id)) {
        state.metrics[n.id] = { degree: 0, weighted: 0, betweenness: 0, component: 0, removed: true };
      } else {
        state.metrics[n.id] = {
          degree: state.useWeights ? n.weighted : n.deg,
          weighted: n.weighted,
          betweenness: betw[n.id] || 0,
          component: compOf[n.id] || 0,
          removed: false
        };
      }
    });
    state.maxCount = activeNodesArr.reduce((m, n) => Math.max(m, n.deg), 0) || 1;
    state.maxWeighted = activeNodesArr.reduce((m, n) => Math.max(m, n.weighted), 0) || 1;
    state.activeCount = N;
    state.activeComponents = cid;

    emit('metrics-updated', { N: N, components: cid });
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
      state.edgeCsv = data; state.edgeCols = cols;
      state.mapping = Object.assign({}, state.mapping, autoMap(cols));
      renderMappers();
      setStatus(`Edges: ${data.length} rows · ${cols.length} columns. Auto-mapped — click Load.`, 'ok');
    });
  }
  function handleNodeFile(file) {
    setStatus('Parsing nodes…');
    parseCsv(file, (data, cols) => {
      state.nodeCsv = data; state.nodeCols = cols;
      Object.assign(state.mapping, autoMapNodes(cols));
      renderMappers();
      setStatus(`Nodes: ${data.length} rows · ${cols.length} columns.`, 'ok');
    });
  }

  function loadGraph() {
    // New graph → reset v2 state (removed + scenarios cleared elsewhere via emit)
    state.removedNodes = new Set();
    if (!buildGraph()) return;
    state.baseGraph = state.graph;
    setStatus(`Graph: ${state.graph.nodes.length} nodes · ${state.graph.links.length} edges.`, 'ok');
    populateAggregateOptions();
    populateAggregateTimeOptions();
    populateGroupColumnOptions();
    state.aggregateBy = '';
    const aggSel = $('aggregate-by'); if (aggSel) aggSel.value = '';
    rebuildView();
    emit('graph-loaded', { nodes: state.graph.nodes.length, edges: state.graph.links.length });
  }

  // ── Aggregation ─────────────────────────────────────────────
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

    const agg = new Map();
    base.links.forEach((l) => {
      if (slice && String(l.timeRaw) !== String(timeSlice)) return;
      const s = typeof l.source === 'object' ? l.source.id : l.source;
      const t = typeof l.target === 'object' ? l.target.id : l.target;
      const gs = gid[s], gt = gid[t];
      if (gs === gt) return;
      const key = gs + '' + gt;
      let rec = agg.get(key);
      if (!rec) { rec = { source: gs, target: gt, sum: 0, count: 0 }; agg.set(key, rec); }
      rec.sum += (l.weight || 0); rec.count += 1;
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

  function rebuildView() {
    if (!state.baseGraph) return;
    if (state.aggregateBy) {
      state.graph = aggregateGraph(state.baseGraph, state.aggregateBy, state.aggregateMode, state.aggregateTime);
      state.timeRange = null; state.timeFilter = null;
    } else {
      state.graph = state.baseGraph;
      const times = state.baseGraph.links.map((l) => l.time).filter((t) => t !== null && t !== undefined && isFinite(t));
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
    emit('view-rebuilt', { aggregated: !!state.aggregateBy });
  }

  function populateAggregateTimeOptions() {
    const sel = $('aggregate-time'); if (!sel) return;
    const row = $('aggregate-time-row');
    state.aggregateTime = '';
    const tcol = state.mapping.time;
    let vals = [];
    if (tcol && state.baseGraph) {
      vals = [...new Set(state.baseGraph.links.map((l) => l.timeRaw).filter((v) => v !== null && v !== undefined && v !== ''))];
      vals.sort((a, b) => {
        const na = Number(a), nb = Number(b);
        return (isFinite(na) && isFinite(nb)) ? na - nb : String(a).localeCompare(String(b));
      });
    }
    if (row) row.style.display = vals.length ? '' : 'none';
    sel.innerHTML = `<option value="">Overall (all ${tcol || 'time'})</option>` +
      vals.map((v) => `<option value="${String(v).replace(/"/g, '&quot;')}">${tcol} = ${v}</option>`).join('');
  }

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

  function populateAggregateOptions() {
    const sel = $('aggregate-by'); if (!sel) return;
    const good = categoricalNodeCols(40);
    const grp = state.mapping.nodeGroup;
    if (grp && good.includes(grp)) { good.splice(good.indexOf(grp), 1); good.unshift(grp); }
    sel.innerHTML = '<option value="">None (raw network)</option>' +
      good.map((c) => `<option value="${String(c).replace(/"/g, '&quot;')}">${c}</option>`).join('');
  }

  // ── Project-dataset loader ──────────────────────────────────
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
    'transit-multimodal':      { weight: 'capacity',                          group: 'district' },
    'satellite-supply-chain':  { weight: 'units_per_year',                    group: 'kind' },
    'aircraft-supply-chain':   { weight: 'units_per_year',                    group: 'kind' },
    'ups-ground-network':      { weight: 'packages',                          group: 'kind' },
    'ups-package-flow':        { weight: 'weight_kg',                         group: 'region' },
    'nyc-realestate-capital':  { weight: 'invested_usd',     time: 'quarter', group: 'kind' },
    'nyc-realestate-portfolio':{ weight: 'co_investment_usd',                 group: 'borough' },
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
    // Record which project dataset is loaded so the code-export module can
    // reference it by key when handing off a reproducer script to the playgrounds.
    state.currentDatasetKey = key;
    // Wipe scenarios from any previous dataset — they reference ids that
    // either don't exist in the new graph or accidentally collide. The
    // bug was that buildGraph would still fold them in, blocking the
    // switch silently.
    state.scenarioNodes = []; state.scenarioLinks = [];
    const base = 'playground-data/';
    const cfg = DATASET_MAPPINGS[key] || {};
    parseCsvUrl(base + key + '-edges.csv', (edata, ecols) => {
      state.edgeCsv = edata; state.edgeCols = ecols;
      const m = autoMap(ecols);
      if (!m.from) m.from = ecols[0];
      if (!m.to)   m.to   = ecols[1];
      if (cfg.weight && ecols.includes(cfg.weight)) m.weight = cfg.weight;
      if (cfg.time && ecols.includes(cfg.time)) m.time = cfg.time;
      state.mapping = Object.assign({}, state.mapping, m);
      parseCsvUrl(base + key + '-nodes.csv', (ndata, ncols) => {
        state.nodeCsv = ndata; state.nodeCols = ncols;
        const nm = autoMapNodes(ncols);
        if (cfg.nodeId && ncols.includes(cfg.nodeId)) nm.nodeId = cfg.nodeId;
        else if (!nm.nodeId) nm.nodeId = ncols[0];
        if (cfg.group && ncols.includes(cfg.group)) nm.nodeGroup = cfg.group;
        Object.assign(state.mapping, nm);
        renderMappers();
        loadGraph();
      }, () => {
        state.nodeCsv = null; state.nodeCols = [];
        renderMappers();
        loadGraph();
      });
    }, () => setStatus('Could not load dataset "' + key + '".', 'err'));
  }

  // ── Layout (unchanged from viz.js) ──────────────────────────
  function stopSim() { if (state.simulation) { state.simulation.stop(); state.simulation = null; } }

  function layout() {
    stopSim();
    const W = $('graph-stage').clientWidth, H = $('graph-stage').clientHeight;
    const nodes = activeNodes();
    const { links } = state.graph;

    if (state.layout === 'force') {
      const N = nodes.length, E = links.length;
      const charge = -180 - 9 * Math.sqrt(E);
      const linkDist = 55 + 260 / Math.sqrt(Math.max(4, N));
      const sim = d3.forceSimulation(nodes)
        .force('link',    d3.forceLink(links.filter((l) => {
          const s = typeof l.source === 'object' ? l.source.id : l.source;
          const t = typeof l.target === 'object' ? l.target.id : l.target;
          return !state.removedNodes.has(s) && !state.removedNodes.has(t);
        })).id((d) => d.id).distance(linkDist).strength(0.4))
        .force('charge',  d3.forceManyBody().strength(charge).distanceMax(700))
        .force('center',  d3.forceCenter(W / 2, H / 2))
        .force('collide', d3.forceCollide().radius((d) => 6 + Math.sqrt(d.deg) * 2.2));
      sim.on('tick', render);
      sim.on('end', () => { state.frozen = true; updateFreezeBtn(); fitToView(); });
      sim.alphaDecay(state.showDrift ? 0.0228 : 0.045);
      state.simulation = sim;
      state.frozen = false;
      updateFreezeBtn();
    } else if (state.layout === 'radial') {
      const comps = {};
      nodes.forEach((n) => { (comps[state.metrics[n.id].component] ||= []).push(n); });
      const compIds = Object.keys(comps);
      compIds.forEach((cid, ci) => {
        const arr = comps[cid]; arr.sort((a, b) => b.deg - a.deg);
        const cx = W * ((ci + 0.5) / compIds.length); const cy = H / 2;
        const R = Math.min(W / (compIds.length * 2.2), H / 2.4);
        arr.forEach((n, i) => {
          if (i === 0) { n.x = n.fx = cx; n.y = n.fy = cy; }
          else {
            const ang = ((i - 1) / Math.max(1, arr.length - 1)) * 2 * Math.PI;
            n.x = n.fx = cx + Math.cos(ang) * R; n.y = n.fy = cy + Math.sin(ang) * R;
          }
        });
      });
      render();
    } else if (state.layout === 'circle') {
      const comps = {};
      nodes.forEach((n) => { (comps[state.metrics[n.id].component] ||= []).push(n); });
      const compIds = Object.keys(comps);
      compIds.forEach((cid, ci) => {
        const arr = comps[cid]; arr.sort((a, b) => b.deg - a.deg);
        const cx = W * ((ci + 0.5) / compIds.length); const cy = H / 2;
        const R = Math.min(W / (compIds.length * 2.2), H / 2.4);
        const n0 = arr.length;
        arr.forEach((n, i) => {
          const ang = (i / Math.max(1, n0)) * 2 * Math.PI - Math.PI / 2;
          n.x = n.fx = cx + Math.cos(ang) * R; n.y = n.fy = cy + Math.sin(ang) * R;
        });
      });
      render();
    } else {
      const adj = {};
      nodes.forEach((n) => { adj[n.id] = []; });
      links.forEach((l) => {
        const s = typeof l.source === 'object' ? l.source.id : l.source;
        const t = typeof l.target === 'object' ? l.target.id : l.target;
        if (state.removedNodes.has(s) || state.removedNodes.has(t)) return;
        adj[s] && adj[s].push(t); adj[t] && adj[t].push(s);
      });
      const comps = {};
      nodes.forEach((n) => { (comps[state.metrics[n.id].component] ||= []).push(n); });
      const compIds = Object.keys(comps);
      const margin = 60;
      compIds.forEach((cid, ci) => {
        const arr = comps[cid].slice().sort((a, b) => b.deg - a.deg);
        const root = arr[0].id;
        const depth = { [root]: 0 };
        const queue = [root];
        while (queue.length) {
          const u = queue.shift();
          (adj[u] || []).forEach((v) => { if (depth[v] === undefined) { depth[v] = depth[u] + 1; queue.push(v); } });
        }
        const layers = {};
        arr.forEach((n) => { const d = depth[n.id] ?? 0; (layers[d] ||= []).push(n); });
        const layerKeys = Object.keys(layers).map(Number).sort((a, b) => a - b);
        const colW = W / compIds.length;
        const cx = colW * ci + colW / 2;
        const usableH = Math.max(120, H - margin * 2);
        const layerGap = layerKeys.length > 1 ? usableH / (layerKeys.length - 1) : 0;
        layerKeys.forEach((d, li) => {
          const row = layers[d]; const rowCount = row.length; const y = margin + li * layerGap;
          row.forEach((n, i) => {
            const slot = (i - (rowCount - 1) / 2);
            const spread = Math.min(colW * 0.85, Math.max(60, rowCount * 60));
            const step = rowCount > 1 ? spread / (rowCount - 1) : 0;
            n.x = n.fx = cx + slot * step; n.y = n.fy = y;
          });
        });
      });
      render();
    }
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

    // v2: stage-click handler for scenario node-add mode (D1)
    svg.on('click', (e) => {
      if (e.target !== svgEl) return; // ignore clicks on nodes
      if (!state.zoomTransform) return;
      const [mx, my] = d3.pointer(e, svgEl);
      const sx = (mx - state.zoomTransform.x) / state.zoomTransform.k;
      const sy = (my - state.zoomTransform.y) / state.zoomTransform.k;
      emit('stage-clicked', { sx, sy });
    });
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
    if (animate) sel.transition().duration(450).on('end', () => render()).call(state.zoom.transform, t);
    else { sel.call(state.zoom.transform, t); render(); }
  }

  function unfix() { state.graph.nodes.forEach((n) => { n.fx = null; n.fy = null; }); }

  function updateFreezeBtn() {
    const b = $('btn-freeze'); if (!b) return;
    b.textContent = state.frozen ? '▶' : '❄';
    b.title = state.frozen ? 'Re-run layout' : 'Freeze layout';
  }
  function toggleFreeze() {
    if (!state.graph) return;
    if (state.frozen) {
      state.frozen = false; layout();
      if (state.simulation) state.simulation.alpha(0.6).restart();
    } else { stopSim(); state.frozen = true; }
    updateFreezeBtn();
  }

  // ── Render ──────────────────────────────────────────────────
  function visibleLinks() {
    const tF = state.timeFilter;
    return state.graph.links.filter((l) => {
      const s = typeof l.source === 'object' ? l.source.id : l.source;
      const t = typeof l.target === 'object' ? l.target.id : l.target;
      if (state.removedNodes.has(s) || state.removedNodes.has(t)) return false;
      if (l.weight < state.edgeThreshold) return false;
      if (tF !== null && l.time !== null && l.time !== undefined && l.time > tF) return false;
      return true;
    });
  }

  function activeNodes() {
    if (!state.graph) return [];
    return state.graph.nodes.filter((n) => {
      if (state.removedNodes.has(n.id)) return false;
      // Scenario nodes are user-placed — keep them visible even before they
      // have edges, otherwise hitting +N produces no visible feedback.
      if (n.isScenario) return true;
      if (state.dropIsolates && (state.metrics[n.id]?.degree || 0) === 0) return false;
      return true;
    });
  }

  // Also expose nodes including removed (for ghost rendering)
  function allRenderableNodes() {
    if (!state.graph) return [];
    return state.graph.nodes.filter((n) => {
      if (state.removedNodes.has(n.id)) return true;
      if (n.isScenario) return true;   // always render scenario nodes (see above)
      if (state.dropIsolates && (state.metrics[n.id]?.degree || 0) === 0) return false;
      return true;
    });
  }

  const UNIFORM_COLOR = '#39FF14';

  function nodeColor(n) {
    if (state.removedNodes.has(n.id)) return '#3b1d05';
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

  function buildGroupPalette() {
    state.groupPalette = {};
    state.commPalette = paletteColors(state.palette, 8);
    if (!state.graph) return;
    const groups = Array.from(new Set(
      state.graph.nodes.map((n) => n.group).filter((g) => g !== null && g !== undefined && g !== '')
    )).sort();
    const cols = paletteColors(state.palette, groups.length);
    groups.forEach((g, i) => { state.groupPalette[g] = cols[i]; });
    updateSwatches();
  }
  function updateSwatches() {
    const dl = $('viz-swatches'); if (!dl) return;
    const swatches = paletteColors(state.palette, 12);
    dl.innerHTML = [...new Set(swatches)].map((c) => `<option value="${c}">`).join('');
  }
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
  function populateGroupColumnOptions() {
    const sel = $('group-col'); if (!sel) return;
    const good = categoricalNodeCols(60);
    const grp = state.mapping.nodeGroup;
    if (grp && !good.includes(grp)) good.unshift(grp);
    sel.innerHTML = '<option value="">(none — uniform)</option>' +
      good.map((c) => `<option value="${String(c).replace(/"/g, '&quot;')}" ${grp === c ? 'selected' : ''}>${c}</option>`).join('');
  }
  function setGroupColumn(col) {
    state.mapping.nodeGroup = col || null;
    if (state.baseGraph) state.baseGraph.nodes.forEach((n) => {
      const v = col && n.attrs ? n.attrs[col] : null;
      n.group = (v === undefined || v === null || v === '') ? null : String(v);
    });
    buildGroupPalette();
    renderGroupLegend();
    render();
    emit('view-rebuilt', { groupColChanged: true });
  }

  function nodeRadius(n) {
    let d = state.metrics[n.id]?.degree || 0;
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

    // id → node map for endpoint resolution. d3.forceLink converts link
    // source/target from strings to node refs the first time the simulation
    // ticks; new scenario links added after the sim has stopped never get
    // converted, so render must look them up explicitly.
    const nodeById = Object.create(null);
    state.graph.nodes.forEach((n) => { nodeById[n.id] = n; });
    const endpointX = (e) => (typeof e === 'object' ? (e.x ?? 0) : (nodeById[e]?.x ?? 0));
    const endpointY = (e) => (typeof e === 'object' ? (e.y ?? 0) : (nodeById[e]?.y ?? 0));

    const root = svg.append('g').attr('class', 'viewport');
    if (state.zoomTransform) root.attr('transform', state.zoomTransform);

    const dens = vlinks.length > 2000 ? 0.4 : vlinks.length > 800 ? 0.6 : 1;
    // Selected Edges hop-highlight: if state.selectedHopFocus > 0 and there's a
    // hop-by-edge map, style edges at that depth with a bright color + thicker
    // stroke so the "cascading influence" out from the selected node is visible.
    const hopMap    = state.selectedHopByEdge;
    const hopFocus  = state.selectedHopFocus || 0;
    const HOP_HL    = '#fef08a';   // bright yellow accent for highlighted-depth edges
    const isHopLit  = (l) => hopFocus > 0 && hopMap && hopMap.get(l) === hopFocus;
    const g = root.append('g').attr('class', 'links');
    g.selectAll('line').data(vlinks).enter().append('line')
      .attr('stroke', (l) => isHopLit(l) ? HOP_HL : (l.isScenario ? '#fbbf24' : 'rgba(57,255,20,0.55)'))
      .attr('stroke-dasharray', (l) => l.isScenario ? '4,3' : null)
      .attr('stroke-width', (l) => {
        const base = (0.6 + (l.weight / maxW) * 3.5) * (dens < 1 ? 0.7 : 1);
        return isHopLit(l) ? base * 2.6 : base;
      })
      .attr('stroke-opacity', (l) => isHopLit(l) ? 0.95 : (0.35 + 0.55 * (l.weight / maxW)) * dens)
      // Resolve endpoints by id: scenario links pushed after the force sim has
      // stopped still hold string ids (the sim never converted them to node
      // refs), so l.source.x would be undefined → 0 and the line would draw
      // from (0,0). Look up the node object explicitly in that case.
      .attr('x1', (l) => endpointX(l.source))
      .attr('y1', (l) => endpointY(l.source))
      .attr('x2', (l) => endpointX(l.target))
      .attr('y2', (l) => endpointY(l.target));

    if (state.showEdgeLabels) {
      root.append('g').selectAll('text').data(vlinks).enter().append('text')
        .attr('x', (l) => (endpointX(l.source) + endpointX(l.target)) / 2)
        .attr('y', (l) => (endpointY(l.source) + endpointY(l.target)) / 2)
        .attr('text-anchor', 'middle')
        .attr('font-family', 'Space Mono, monospace')
        .attr('font-size', '9px')
        .attr('fill', 'rgba(134, 239, 172, 0.85)')
        .text((l) => l.weight.toFixed(0));
    }

    const nodesShown = allRenderableNodes();
    const k = (state.zoomTransform && state.zoomTransform.k) ? state.zoomTransform.k : 1;
    const small = (typeof window !== 'undefined' ? window.innerWidth : 1000) < 700;
    const boost = Math.min(small ? 3.0 : 2.4, Math.max(1, 1 / k));
    const rOf = (n) => nodeRadius(n) * boost;

    let labelIds = null;
    if (state.showNodeLabels) {
      const capN = small ? 28 : 90;
      const live = nodesShown.filter((n) => !state.removedNodes.has(n.id));
      if (live.length > capN) {
        const topK = small ? 12 : 24;
        labelIds = new Set(
          live.slice()
            .sort((a, b) => (state.metrics[b.id]?.degree || 0) - (state.metrics[a.id]?.degree || 0))
            .slice(0, topK).map((n) => n.id));
      }
    }
    const labelFont = (small ? 13 : 10.5) * boost;

    const ng = root.append('g').attr('class', 'nodes');
    const nsel = ng.selectAll('g').data(nodesShown).enter().append('g')
      .attr('class', (n) => 'node-g' + (n.isScenario ? ' scenario-new' : '') + (state.removedNodes.has(n.id) ? ' removed' : ''))
      .attr('transform', (n) => `translate(${n.x ?? 0},${n.y ?? 0})`)
      .style('cursor', 'pointer')
      .style('opacity', (n) => state.removedNodes.has(n.id) ? 0.28 : 1)
      .on('click', (e, n) => {
        e.stopPropagation();
        state.selectedNode = n.id;
        emit('node-selected', { id: n.id });
        updateNodePanel();
        render();
      });

    nsel.filter((n) => state.selectedNode === n.id).append('circle')
      .attr('r', (n) => rOf(n) + 5)
      .attr('fill', 'none')
      .attr('stroke', (n) => nodeColor(n))
      .attr('stroke-width', 2)
      .attr('stroke-dasharray', '4,3').attr('opacity', 0.85);

    nsel.append('circle')
      .attr('class', 'node-body')
      .attr('r', (n) => rOf(n))
      .attr('fill', (n) => nodeColor(n))
      .attr('fill-opacity', (n) => state.removedNodes.has(n.id) ? 0.4 : 0.9)
      .attr('stroke', (n) => state.removedNodes.has(n.id) ? '#fb923c' : (n.isScenario ? '#fbbf24' : '#050a05'))
      .attr('stroke-dasharray', (n) => n.isScenario ? '3,3' : null)
      .attr('stroke-width', (n) => state.removedNodes.has(n.id) ? 2 : 1.2)
      .style('filter', (n) => state.removedNodes.has(n.id) ? null : `drop-shadow(0 0 ${6 * state.nodeScale}px ${nodeColor(n)})`);

    if (state.showNodeLabels) {
      nsel.filter((n) => (!labelIds || labelIds.has(n.id) || n.id === state.selectedNode))
        .append('text')
        .attr('y', (n) => -rOf(n) - 5)
        .attr('text-anchor', 'middle')
        .attr('font-family', 'Space Mono, monospace')
        .attr('font-size', labelFont + 'px')
        .attr('letter-spacing', '0.05em')
        .attr('fill', (n) => state.removedNodes.has(n.id) ? '#fb923c' : '#d1fae5')
        .text((n) => (n.label || n.id).length > 16 ? (n.label || n.id).slice(0, 14) + '…' : (n.label || n.id));
    }

    updateStats(vlinks.length);
    emit('render', {});
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
    if (!n) { wrap.innerHTML = '<div class="node-empty">Selection no longer in graph.</div>'; return; }
    const m = state.metrics[n.id] || {};
    const Nact = state.activeCount || state.graph.nodes.length;
    const normFactor = Math.max(1, (Nact - 1) * (Nact - 2));
    const rawSP = Math.round((m.betweenness || 0) * normFactor);
    const removed = state.removedNodes.has(n.id);
    wrap.innerHTML = `
      <div class="node-card">
        <div class="t-label" style="color: ${nodeColor(n)}">${removed ? 'REMOVED · ' : ''}Selected · Component ${m.component || '—'}</div>
        <h3>${n.label || n.id}</h3>
        <div class="kvs">
          <div class="kv"><span class="k">Degree ${state.useWeights ? '(weighted)' : '(count)'}</span><span class="v">${state.useWeights ? (m.weighted ?? 0).toFixed(1) : (m.degree ?? '—')}<span class="unit">${state.useWeights ? '· Σw' : '· edges'}</span></span></div>
          <div class="kv"><span class="k">Weighted degree</span><span class="v">${(m.weighted ?? 0).toFixed(1)}<span class="unit">· Σw</span></span></div>
          <div class="kv"><span class="k">Betweenness</span><span class="v">${(m.betweenness ?? 0).toFixed(4)}<span class="unit">· norm 0–1</span></span></div>
          <div class="kv"><span class="k">Shortest paths through</span><span class="v">${rawSP.toLocaleString()}<span class="unit">· σ_st(v)</span></span></div>
          <div class="kv"><span class="k">Component</span><span class="v">${m.component || '—'}</span></div>
          ${n.group ? `<div class="kv"><span class="k">Group</span><span class="v">${n.group}</span></div>` : ''}
        </div>
      </div>`;

    // Top-degree mini list
    const liveNodes = state.graph.nodes.filter((nn) => !state.removedNodes.has(nn.id));
    const ranked = liveNodes.slice().sort((a, b) => (state.metrics[b.id].degree - state.metrics[a.id].degree)).slice(0, 6);
    const max = ranked.length ? state.metrics[ranked[0].id].degree || 1 : 1;
    $('top-degree-list').innerHTML = ranked.map((nn) => `
      <div class="bar-row">
        <div class="bn">${(nn.label || nn.id).length > 12 ? (nn.label || nn.id).slice(0, 10) + '…' : (nn.label || nn.id)}</div>
        <div class="br"><div class="bf" style="width:${(state.metrics[nn.id].degree / max) * 100}%"></div></div>
        <div class="bv">${state.useWeights ? state.metrics[nn.id].degree.toFixed(1) : state.metrics[nn.id].degree}</div>
      </div>`).join('');

    const rankedB = liveNodes.slice().sort((a, b) => (state.metrics[b.id].betweenness - state.metrics[a.id].betweenness)).slice(0, 6);
    const maxB = rankedB.length ? state.metrics[rankedB[0].id].betweenness || 1 : 1;
    $('top-betw-list').innerHTML = rankedB.map((nn) => `
      <div class="bar-row">
        <div class="bn">${(nn.label || nn.id).length > 12 ? (nn.label || nn.id).slice(0, 10) + '…' : (nn.label || nn.id)}</div>
        <div class="br"><div class="bf" style="width:${(state.metrics[nn.id].betweenness / Math.max(maxB, 0.0001)) * 100}%"></div></div>
        <div class="bv">${state.metrics[nn.id].betweenness.toFixed(3)}</div>
      </div>`).join('');
  }

  // ── Controls ────────────────────────────────────────────────
  function setupTimeSlider() {
    const wrap = $('time-slider-wrap');
    if (!state.timeRange) { wrap.style.display = 'none'; return; }
    wrap.style.display = 'block';
    const sl = $('time-slider');
    sl.min = state.timeRange[0]; sl.max = state.timeRange[1];
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
      emit('view-rebuilt', { thresholdChanged: true });
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
          if (state.graph) { unfix(); layout(); fitToView(); }
        }
        if (key === 'weights') {
          state.useWeights = on;
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

    const colorBySel = $('color-by');
    if (colorBySel) colorBySel.addEventListener('change', (e) => {
      state.colorBy = e.target.value;
      renderGroupLegend(); render();
    });

    const groupColSel = $('group-col');
    if (groupColSel) groupColSel.addEventListener('change', (e) => setGroupColumn(e.target.value));

    const paletteSel = $('palette');
    if (paletteSel) paletteSel.addEventListener('change', (e) => {
      state.palette = e.target.value;
      state.groupColors = {}; buildGroupPalette(); renderGroupLegend(); render();
    });

    const legend = $('group-legend');
    if (legend) legend.addEventListener('input', (e) => {
      const inp = e.target.closest('input[type=color]');
      if (!inp) return;
      state.groupColors[inp.dataset.group] = inp.value;
      render();
    });

    const aggBy = $('aggregate-by');
    if (aggBy) aggBy.addEventListener('change', (e) => { state.aggregateBy = e.target.value; if (state.baseGraph) rebuildView(); });
    const aggMode = $('aggregate-mode');
    if (aggMode) aggMode.addEventListener('change', (e) => { state.aggregateMode = e.target.value; if (state.baseGraph && state.aggregateBy) rebuildView(); });
    const aggTime = $('aggregate-time');
    if (aggTime) aggTime.addEventListener('change', (e) => { state.aggregateTime = e.target.value; if (state.baseGraph && state.aggregateBy) rebuildView(); });

    $('time-slider').addEventListener('input', (e) => {
      state.timeFilter = +e.target.value;
      $('time-slider-val').textContent = formatTime(state.timeFilter);
      render();
      emit('view-rebuilt', { timeChanged: true });
    });

    $('btn-load').addEventListener('click', () => {
      document.querySelectorAll('#mapper-fields select').forEach((sel) => {
        state.mapping[sel.dataset.key] = sel.value || null;
      });
      loadGraph();
    });
    $('btn-sample').addEventListener('click', () => loadSampleGraph());
    $('btn-png').addEventListener('click', exportPng);
    $('edge-file').addEventListener('change', (e) => { if (e.target.files[0]) handleEdgeFile(e.target.files[0]); });
    $('node-file').addEventListener('change', (e) => { if (e.target.files[0]) handleNodeFile(e.target.files[0]); });
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

  function exportPng() {
    const svgEl = $('graph');
    const W = svgEl.clientWidth, H = svgEl.clientHeight;
    const clone = svgEl.cloneNode(true);
    clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    clone.setAttribute('width', W); clone.setAttribute('height', H);
    const bg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    bg.setAttribute('width', W); bg.setAttribute('height', H); bg.setAttribute('fill', '#050a05');
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
    const nSuppliers = randInt(4, 8), nHubs = randInt(1, 3), nDCs = randInt(2, 4), nRetailers = randInt(4, 9);
    const suppliers = Array.from({ length: nSuppliers }, (_, i) => `Supplier_${String.fromCharCode(65 + i)}`);
    const hubs      = Array.from({ length: nHubs },      (_, i) => nHubs === 1 ? 'Hub_Central' : `Hub_${i + 1}`);
    const dcs       = Array.from({ length: nDCs },       (_, i) => `DC_${['North','South','East','West'][i] || (i + 1)}`);
    const retailers = Array.from({ length: nRetailers }, (_, i) => `Retailer_${i + 1}`);
    const tMax = randInt(4, 7);
    const edges = [];
    suppliers.forEach((s) => {
      const hs = new Set(); const k = randInt(1, Math.min(2, hubs.length));
      while (hs.size < k) hs.add(pick(hubs));
      hs.forEach((h) => edges.push({ from: s, to: h, weight: randInt(2, 8), time: randInt(1, Math.max(1, Math.floor(tMax / 2))) }));
    });
    hubs.forEach((h) => { dcs.forEach((d) => { if (Math.random() < 0.75) edges.push({ from: h, to: d, weight: randInt(3, 9), time: randInt(1, tMax) }); }); });
    retailers.forEach((r) => {
      const ds = new Set(); const k = randInt(1, Math.min(2, dcs.length));
      while (ds.size < k) ds.add(pick(dcs));
      ds.forEach((d) => edges.push({ from: d, to: r, weight: randInt(1, 5), time: randInt(2, tMax) }));
    });
    const sideways = randInt(0, Math.max(0, Math.floor(nRetailers / 3)));
    for (let i = 0; i < sideways; i++) {
      const a = pick(retailers), b = pick(retailers);
      if (a !== b) edges.push({ from: a, to: b, weight: 1, time: randInt(3, tMax) });
    }
    return edges;
  }
  function loadSampleGraph() {
    const edgeCsv = generateSampleGraph();
    // Build a nodelist with TWO grouping columns (tier + region) so the
    // sample graph can demo coverage / permutation / group composition
    // immediately. Derive tier from the id prefix; assign a region randomly
    // so the cross-tabulation has cells in every combination.
    const regions = ['North', 'South', 'East', 'West'];
    const ids = new Set();
    edgeCsv.forEach((e) => { ids.add(e.from); ids.add(e.to); });
    const tierOf = (id) => {
      if (id.startsWith('Supplier_')) return 'supplier';
      if (id.startsWith('Hub'))       return 'hub';
      if (id.startsWith('DC_'))       return 'dc';
      if (id.startsWith('Retailer_')) return 'retailer';
      return 'other';
    };
    const nodeCsv = [...ids].map((id) => ({
      node_id: id, label: id, tier: tierOf(id), region: pick(regions)
    }));
    state.edgeCsv = edgeCsv;
    state.edgeCols = ['from', 'to', 'weight', 'time'];
    state.nodeCsv = nodeCsv;
    state.nodeCols = ['node_id', 'label', 'tier', 'region'];
    state.mapping = { from: 'from', to: 'to', weight: 'weight', time: 'time',
                      nodeId: 'node_id', nodeLabel: 'label', nodeGroup: 'tier' };
    // Not a project dataset — the code-export module inlines the graph
    // instead of trying to read.csv() a file the playground doesn't have.
    state.currentDatasetKey = null;
    // Wipe scenarios — they were keyed to the OLD dataset's node ids and
    // would either silently miss or, worse, half-apply against the new graph.
    state.scenarioNodes = []; state.scenarioLinks = [];
    renderMappers();
    loadGraph();
  }

  // ── Shared graph-algorithm utilities (consumed by feature modules) ──
  const utils = {
    // Build undirected adjacency map from a {nodes, links} graph and a Set of
    // active ids. Returns { id → [{neighborId, weight}, ...] }.
    buildAdj(graph, activeIdsSet) {
      const adj = Object.create(null);
      activeIdsSet.forEach((id) => { adj[id] = []; });
      graph.links.forEach((l) => {
        const s = typeof l.source === 'object' ? l.source.id : l.source;
        const t = typeof l.target === 'object' ? l.target.id : l.target;
        if (!activeIdsSet.has(s) || !activeIdsSet.has(t)) return;
        const w = (l.weight && l.weight > 0) ? l.weight : 1;
        adj[s].push({ to: t, w }); adj[t].push({ to: s, w });
      });
      return adj;
    },
    // BFS distances from source over an undirected adjacency.
    bfs(adj, source) {
      const dist = Object.create(null);
      const ids = Object.keys(adj);
      ids.forEach((id) => { dist[id] = Infinity; });
      dist[source] = 0;
      const q = [source]; let qi = 0;
      while (qi < q.length) {
        const u = q[qi++];
        for (const { to } of adj[u]) {
          if (dist[to] === Infinity) { dist[to] = dist[u] + 1; q.push(to); }
        }
      }
      return dist;
    },
    // Dijkstra with cost = 1 / weight (matches counterfactual case study).
    // Uses a simple binary-heap PQ; ~O((V+E) log V).
    dijkstraInvWeight(adj, source) {
      const dist = Object.create(null);
      const ids = Object.keys(adj);
      ids.forEach((id) => { dist[id] = Infinity; });
      dist[source] = 0;
      const heap = [[0, source]];
      const lt = (a, b) => a[0] < b[0];
      const swap = (i, j) => { const t = heap[i]; heap[i] = heap[j]; heap[j] = t; };
      const up = (i) => { while (i > 0) { const p = (i - 1) >> 1; if (lt(heap[i], heap[p])) { swap(i, p); i = p; } else break; } };
      const down = (i) => {
        const n = heap.length;
        while (true) {
          const l = 2 * i + 1, r = 2 * i + 2; let b = i;
          if (l < n && lt(heap[l], heap[b])) b = l;
          if (r < n && lt(heap[r], heap[b])) b = r;
          if (b === i) break; swap(i, b); i = b;
        }
      };
      const pop = () => { const top = heap[0]; const last = heap.pop(); if (heap.length) { heap[0] = last; down(0); } return top; };
      const push = (x) => { heap.push(x); up(heap.length - 1); };
      while (heap.length) {
        const [d, u] = pop();
        if (d > dist[u]) continue;
        for (const { to, w } of adj[u]) {
          const nd = d + (1 / w);
          if (nd < dist[to]) { dist[to] = nd; push([nd, to]); }
        }
      }
      return dist;
    },
    // Connected components from an adjacency. Returns {id → componentId (1..)}.
    components(adj) {
      const compOf = Object.create(null);
      let cid = 0;
      Object.keys(adj).forEach((id) => {
        if (compOf[id] !== undefined) return;
        cid++; const q = [id]; let qi = 0;
        while (qi < q.length) {
          const u = q[qi++];
          if (compOf[u] !== undefined) continue;
          compOf[u] = cid;
          for (const { to } of adj[u]) if (compOf[to] === undefined) q.push(to);
        }
      });
      return { compOf, count: cid };
    },
    // Knuth/Box-Muller Poisson sampler. λ < 30 → exact; ≥ 30 → normal approx.
    // Matches counterfactual case study's rpois/rng.poisson(lam).
    poisson(lambda) {
      if (lambda <= 0) return 0;
      if (lambda < 30) {
        const L = Math.exp(-lambda);
        let k = 0, p = 1;
        do { k++; p *= Math.random(); } while (p > L);
        return k - 1;
      }
      const u = Math.max(1e-12, Math.random()), v = Math.random();
      const z = Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
      return Math.max(0, Math.round(lambda + Math.sqrt(lambda) * z));
    },
    // Quantile q ∈ [0,1] over a numeric array (NOT sorted in place).
    quantile(arr, q) {
      const a = arr.slice().filter((x) => isFinite(x)).sort((x, y) => x - y);
      if (!a.length) return NaN;
      const pos = (a.length - 1) * q;
      const lo = Math.floor(pos), hi = Math.ceil(pos);
      if (lo === hi) return a[lo];
      return a[lo] + (a[hi] - a[lo]) * (pos - lo);
    },
    // Fisher-Yates shuffle in place.
    shuffleInPlace(a) {
      for (let i = a.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        const t = a[i]; a[i] = a[j]; a[j] = t;
      }
      return a;
    },
    // Newman's nominal assortativity coefficient r ∈ [-1, 1] over an undirected
    // graph. nodes carry `.attrs[attr]` (or `.group` if attr === '__group__').
    nominalAssortativity(graph, attr, activeIdsSet) {
      const attrOf = (n) => {
        if (attr === '__group__') return n.group;
        return n.attrs ? n.attrs[attr] : undefined;
      };
      const idVal = Object.create(null);
      graph.nodes.forEach((n) => {
        if (activeIdsSet && !activeIdsSet.has(n.id)) return;
        const v = attrOf(n);
        if (v !== undefined && v !== null && v !== '') idVal[n.id] = String(v);
      });
      const e = new Map();   // 'a||b' → fraction of edges
      let M = 0;
      graph.links.forEach((l) => {
        const s = typeof l.source === 'object' ? l.source.id : l.source;
        const t = typeof l.target === 'object' ? l.target.id : l.target;
        if (activeIdsSet && (!activeIdsSet.has(s) || !activeIdsSet.has(t))) return;
        const a = idVal[s], b = idVal[t];
        if (a === undefined || b === undefined) return;
        const key = a < b ? a + '||' + b : b + '||' + a;
        e.set(key, (e.get(key) || 0) + 1); M++;
      });
      if (M === 0) return { r: NaN, M: 0 };
      const a = Object.create(null);   // a_i = fraction of edge ENDPOINTS of type i
      e.forEach((cnt, key) => {
        const [x, y] = key.split('||');
        const frac = cnt / M;
        if (x === y) { a[x] = (a[x] || 0) + frac * 2; }
        else         { a[x] = (a[x] || 0) + frac; a[y] = (a[y] || 0) + frac; }
      });
      // r = (Σ_ii e_ii - Σ_i a_i²) / (1 - Σ_i a_i²)
      let sumEii = 0;
      e.forEach((cnt, key) => {
        const [x, y] = key.split('||');
        if (x === y) sumEii += cnt / M;
      });
      let sumAi2 = 0;
      Object.values(a).forEach((v) => { sumAi2 += v * v / 4; });
      // ^ a was double-counted on the diagonal above; correct by halving on square
      const r = (sumEii - sumAi2) / Math.max(1e-12, 1 - sumAi2);
      return { r, M };
    },
    // Course "Similarity Index" (docs/case-studies/permutation.html:582),
    // generalized from binary (high/low) to K groups:
    //   index = (K² / (2(K²-1))) · Σ_{i,j} |p_ij - 1/K²|
    // where p_ij = fraction of total edge weight on ordered cell (i→j).
    //   0 = perfectly heterogeneous (uniform mixing)
    //   1 = all weight in a single cell (fully concentrated)
    // Drops the 2/3 → 1 scaling factor at K=2 (matches the lab exactly).
    // Pass attr === '__group__' to use the live n.group; otherwise n.attrs[attr].
    similarityIndex(graph, attr, activeIdsSet) {
      const attrOf = (n) => attr === '__group__' ? n.group : (n.attrs ? n.attrs[attr] : undefined);
      const groupOf = Object.create(null);
      const groupSet = new Set();
      graph.nodes.forEach((n) => {
        if (activeIdsSet && !activeIdsSet.has(n.id)) return;
        const v = attrOf(n);
        if (v !== undefined && v !== null && v !== '') {
          const s = String(v);
          groupOf[n.id] = s;
          groupSet.add(s);
        }
      });
      const groups = Array.from(groupSet);
      const K = groups.length;
      if (K < 2) return { index: NaN, K, total: 0 };

      const cells = new Map();   // 'a||b' → summed weight (ordered)
      let total = 0;
      graph.links.forEach((l) => {
        const s = typeof l.source === 'object' ? l.source.id : l.source;
        const t = typeof l.target === 'object' ? l.target.id : l.target;
        if (activeIdsSet && (!activeIdsSet.has(s) || !activeIdsSet.has(t))) return;
        const a = groupOf[s], b = groupOf[t];
        if (a === undefined || b === undefined) return;
        const w = (l.weight && l.weight > 0) ? l.weight : 1;
        const key = a + '||' + b;
        cells.set(key, (cells.get(key) || 0) + w);
        total += w;
      });
      if (total === 0) return { index: NaN, K, total: 0 };

      const uniform = 1 / (K * K);
      let absDev = 0;
      for (const x of groups) for (const y of groups) {
        const w = cells.get(x + '||' + y) || 0;
        absDev += Math.abs((w / total) - uniform);
      }
      const norm = (K * K) / Math.max(1e-12, 2 * (K * K - 1));
      return { index: norm * absDev, K, total };
    }
  };

  // ── Init ────────────────────────────────────────────────────
  function init() {
    setupZoom();
    wireControls();
    renderControls();
    renderGroupLegend();
    emit('init', {});
  }
  document.addEventListener('DOMContentLoaded', init);

  // ── Public API ──────────────────────────────────────────────
  global.NetSciViz2 = {
    state,
    on, emit,
    utils,
    // lifecycle
    loadSampleGraph, loadGraph, loadProjectDataset,
    rebuildView, render, computeMetrics, layout,
    fitToView, unfix,
    // selectors
    activeNodes, allRenderableNodes, visibleLinks, nodeColor, nodeRadius,
    // helpers
    setStatus, updateNodePanel,
    setGroupColumn,
    // viz helpers
    paletteColors
  };
})(window);
