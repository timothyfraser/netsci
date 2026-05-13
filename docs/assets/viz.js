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
    layout: 'force',  // force | radial | hierarchical
    showEdgeLabels: false,
    showNodeLabels: true,
    showCommunity: false,
    showDrift: true,
    nodeScale: 1,
    edgeThreshold: 0,
    timeFilter: null, // null = no filter, otherwise upper bound
    timeRange: null,  // [min, max]
    selectedNode: null,
    simulation: null,
    metrics: {}       // per-node { degree, weighted, betweenness, component }
  };

  const PALETTE = [
    '#39FF14', '#86efac', '#5eead4', '#fbbf24',
    '#f472b6', '#818cf8', '#f97316', '#e2e8f0'
  ];

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
      nodeId:    find('id', 'node', 'name', 'label'),
      nodeLabel: find('label', 'name', 'title'),
      nodeGroup: find('group', 'community', 'cluster', 'type', 'category')
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
      let t = m.time ? row[m.time] : null;
      if (t !== null && t !== undefined && t !== '') {
        const tn = Number(t);
        t = isFinite(tn) ? tn : Date.parse(t);
        if (isFinite(t)) times.push(t);
      } else t = null;
      links.push({ source: A.id, target: B.id, weight: w, time: t });
      A.deg++; B.deg++;
      A.weighted += w; B.weighted += w;
    });

    if (state.nodeCsv && state.mapping.nodeId) {
      state.nodeCsv.forEach((row) => {
        const id = String(row[state.mapping.nodeId]);
        if (!nodeMap.has(id)) nodeMap.set(id, { id, label: id, group: null, deg: 0, weighted: 0 });
        const n = nodeMap.get(id);
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

    // Brandes betweenness (unweighted, undirected) — bounded by N for performance
    const N = nodes.length;
    const ids = nodes.map((n) => n.id);
    const betw = {};
    ids.forEach((id) => { betw[id] = 0; });
    if (N <= 600) {
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
    }

    state.metrics = {};
    nodes.forEach((n) => {
      state.metrics[n.id] = {
        degree: n.deg, weighted: n.weighted,
        betweenness: betw[n.id] || 0,
        component: compOf[n.id]
      };
    });
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
        { key: 'nodeLabel', label: 'Node label column', options: state.nodeCols },
        { key: 'nodeGroup', label: 'Node group column', options: state.nodeCols }
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
    setStatus(`Graph: ${state.graph.nodes.length} nodes · ${state.graph.links.length} edges.`, 'ok');
    setupTimeSlider();
    renderControls();
    layout();
    render();
  }

  // ── Layout ──────────────────────────────────────────────────
  function stopSim() {
    if (state.simulation) { state.simulation.stop(); state.simulation = null; }
  }

  function layout() {
    stopSim();
    const W = $('graph-stage').clientWidth, H = $('graph-stage').clientHeight;
    const { nodes, links } = state.graph;

    if (state.layout === 'force') {
      const sim = d3.forceSimulation(nodes)
        .force('link',    d3.forceLink(links).id((d) => d.id).distance(70).strength(0.5))
        .force('charge',  d3.forceManyBody().strength(-180))
        .force('center',  d3.forceCenter(W / 2, H / 2))
        .force('collide', d3.forceCollide().radius((d) => 6 + Math.sqrt(d.deg) * 2.2));
      sim.on('tick', render);
      if (!state.showDrift) sim.alphaDecay(0.05); else sim.alphaDecay(0.018);
      state.simulation = sim;
    } else if (state.layout === 'radial') {
      // Group by component, place each component as concentric ring
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
          if (i === 0) { n.fx = cx; n.fy = cy; }
          else {
            const ang = ((i - 1) / Math.max(1, arr.length - 1)) * 2 * Math.PI;
            n.fx = cx + Math.cos(ang) * R;
            n.fy = cy + Math.sin(ang) * R;
          }
        });
      });
      const sim = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links).id((d) => d.id).distance(50).strength(0.2));
      sim.on('tick', render);
      sim.alphaDecay(0.1);
      state.simulation = sim;
    } else {
      // Hierarchical — layered by component then by degree desc
      const comps = {};
      nodes.forEach((n) => { (comps[state.metrics[n.id].component] ||= []).push(n); });
      const compIds = Object.keys(comps);
      compIds.forEach((cid, ci) => {
        const arr = comps[cid].slice().sort((a, b) => b.deg - a.deg);
        const cx = W * ((ci + 0.5) / compIds.length);
        const layers = Math.min(6, Math.ceil(Math.sqrt(arr.length)));
        arr.forEach((n, i) => {
          const layer = i % layers;
          const colIdx = Math.floor(i / layers);
          const cols = Math.ceil(arr.length / layers);
          n.fx = cx + (colIdx - cols / 2) * 32;
          n.fy = 60 + layer * ((H - 120) / Math.max(1, layers - 1));
        });
      });
      render();
    }
  }

  // Release fixed positions when switching layouts
  function unfix() {
    state.graph.nodes.forEach((n) => { n.fx = null; n.fy = null; });
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

  function nodeColor(n) {
    if (state.showCommunity && state.metrics[n.id]) {
      const c = state.metrics[n.id].component || 0;
      return PALETTE[(c - 1) % PALETTE.length];
    }
    if (n.group && state.showCommunity) {
      // hash group string → palette
      let h = 0; for (let i = 0; i < n.group.length; i++) h = (h * 31 + n.group.charCodeAt(i)) | 0;
      return PALETTE[Math.abs(h) % PALETTE.length];
    }
    return '#39FF14';
  }

  function nodeRadius(n) {
    const d = state.metrics[n.id]?.degree || 0;
    return (4 + Math.sqrt(d) * 2.2) * state.nodeScale;
  }

  function render() {
    const svgEl = $('graph');
    const svg = d3.select(svgEl);
    svg.selectAll('*').remove();
    if (!state.graph) return;

    const maxW = d3.max(state.graph.links, (l) => l.weight) || 1;
    const vlinks = visibleLinks();

    // Edges
    const g = svg.append('g').attr('class', 'links');
    g.selectAll('line').data(vlinks).enter().append('line')
      .attr('stroke', 'rgba(57,255,20,0.55)')
      .attr('stroke-width', (l) => 0.6 + (l.weight / maxW) * 3.5)
      .attr('stroke-opacity', (l) => 0.35 + 0.55 * (l.weight / maxW))
      .attr('x1', (l) => (l.source.x ?? 0))
      .attr('y1', (l) => (l.source.y ?? 0))
      .attr('x2', (l) => (l.target.x ?? 0))
      .attr('y2', (l) => (l.target.y ?? 0));

    if (state.showEdgeLabels) {
      svg.append('g').selectAll('text').data(vlinks).enter().append('text')
        .attr('x', (l) => ((l.source.x ?? 0) + (l.target.x ?? 0)) / 2)
        .attr('y', (l) => ((l.source.y ?? 0) + (l.target.y ?? 0)) / 2)
        .attr('text-anchor', 'middle')
        .attr('font-family', 'Space Mono, monospace')
        .attr('font-size', '9px')
        .attr('fill', 'rgba(134, 239, 172, 0.85)')
        .text((l) => l.weight.toFixed(0));
    }

    // Nodes
    const ng = svg.append('g').attr('class', 'nodes');
    const nsel = ng.selectAll('g').data(state.graph.nodes).enter().append('g')
      .attr('transform', (n) => `translate(${n.x ?? 0},${n.y ?? 0})`)
      .style('cursor', 'pointer')
      .on('click', (_e, n) => { state.selectedNode = n.id; updateNodePanel(); render(); });

    nsel.filter((n) => state.selectedNode === n.id).append('circle')
      .attr('r', (n) => nodeRadius(n) + 5)
      .attr('fill', 'none')
      .attr('stroke', (n) => nodeColor(n))
      .attr('stroke-width', 2)
      .attr('stroke-dasharray', '4,3').attr('opacity', 0.85);

    nsel.append('circle')
      .attr('r', (n) => nodeRadius(n))
      .attr('fill', (n) => nodeColor(n))
      .attr('fill-opacity', 0.9)
      .attr('stroke', '#050a05')
      .attr('stroke-width', 1.2)
      .style('filter', (n) => `drop-shadow(0 0 ${6 * state.nodeScale}px ${nodeColor(n)})`);

    if (state.showNodeLabels) {
      nsel.append('text')
        .attr('y', (n) => -nodeRadius(n) - 5)
        .attr('text-anchor', 'middle')
        .attr('font-family', 'Space Mono, monospace')
        .attr('font-size', '10px')
        .attr('letter-spacing', '0.05em')
        .attr('fill', '#d1fae5')
        .text((n) => n.label.length > 14 ? n.label.slice(0, 12) + '…' : n.label);
    }

    updateStats(vlinks.length);
  }

  // ── Stats overlay + node panel ──────────────────────────────
  function updateStats(visibleEdges) {
    if (!state.graph) return;
    const N = state.graph.nodes.length;
    const E = visibleEdges ?? state.graph.links.length;
    $('stat-nodes').textContent = N.toLocaleString();
    $('stat-edges').textContent = E.toLocaleString();
    const comps = new Set(state.graph.nodes.map((n) => state.metrics[n.id]?.component)).size;
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
        if (key === 'community')  state.showCommunity  = on;
        if (key === 'labels')     state.showNodeLabels = on;
        if (key === 'drift') {
          state.showDrift = on;
          if (state.simulation) state.simulation.alphaDecay(on ? 0.018 : 0.1);
        }
        render();
      });
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

    window.addEventListener('resize', () => { if (state.graph) { layout(); } });
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
  function loadSampleGraph() {
    // Simple toy supply-chain inspired by the lab data
    const edgeCsv = [
      { from: 'Supplier_A', to: 'Hub_Central', weight: 5, time: 1 },
      { from: 'Supplier_B', to: 'Hub_Central', weight: 4, time: 1 },
      { from: 'Supplier_C', to: 'Hub_Central', weight: 3, time: 2 },
      { from: 'Hub_Central', to: 'DC_North', weight: 7, time: 2 },
      { from: 'Hub_Central', to: 'DC_South', weight: 6, time: 3 },
      { from: 'DC_North',  to: 'Retailer_1', weight: 3, time: 3 },
      { from: 'DC_North',  to: 'Retailer_2', weight: 2, time: 3 },
      { from: 'DC_South',  to: 'Retailer_3', weight: 4, time: 4 },
      { from: 'DC_South',  to: 'Retailer_4', weight: 3, time: 4 },
      { from: 'Mesa_Consolidator', to: 'DC_North', weight: 4, time: 2 },
      { from: 'Mesa_Consolidator', to: 'Retailer_5', weight: 2, time: 5 },
      { from: 'Supplier_D', to: 'Mesa_Consolidator', weight: 4, time: 1 },
      { from: 'Supplier_E', to: 'Mesa_Consolidator', weight: 3, time: 2 },
      { from: 'Retailer_2', to: 'Retailer_3', weight: 1, time: 5 }
    ];
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
    wireControls();
    renderControls();
  }
  document.addEventListener('DOMContentLoaded', init);

  global.NetSciViz = { state, loadSampleGraph, loadGraph };
})(window);
