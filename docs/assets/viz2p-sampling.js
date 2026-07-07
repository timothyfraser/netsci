// viz2p-sampling.js — PREVIEW ONLY (loaded only by visualizer2.html).
// Sampling card: draw a sample from the current network, highlight it in the
// graph, report coverage/triangle/degree stats vs the true population, and run
// many samples to build a sampling distribution of a chosen statistic — then
// compare the true population parameter to that distribution.
//
// Ports docs/case-studies/sampling.html (random-node, ego 1-hop, snowball
// 2-hop, random-edge) and adds the repeated-sampling distribution the lab
// lacked, plus runnable R/Python export.
(function () {
  'use strict';
  if (!window.NetSciViz2) return;
  const NV = window.NetSciViz2;
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const ek = (a, b) => (a < b ? a + '|' + b : b + '|' + a);

  // Linear-interpolated quantile.
  function quantile(arr, p) {
    const s = arr.filter((x) => isFinite(x)).slice().sort((a, b) => a - b);
    if (!s.length) return NaN;
    const idx = p * (s.length - 1), lo = Math.floor(idx), hi = Math.ceil(idx);
    return lo === hi ? s[lo] : s[lo] + (s[hi] - s[lo]) * (idx - lo);
  }
  const fmtN = (v, dp) => (isFinite(v) ? Number(v).toFixed(dp) : '—');

  // Shared tooltip (one div, reused).
  function tipEl() {
    let t = $('viz2-samp-tip');
    if (!t) {
      t = document.createElement('div'); t.id = 'viz2-samp-tip';
      t.style.cssText = 'position:fixed;z-index:9999;pointer-events:none;display:none;background:rgba(5,10,5,0.95);' +
        'border:1px solid var(--green-bright);border-radius:6px;padding:5px 8px;font-family:var(--font-mono);' +
        'font-size:11px;color:var(--green-mint);max-width:240px;box-shadow:0 2px 10px rgba(0,0,0,0.5);';
      document.body.appendChild(t);
    }
    return t;
  }
  function showTip(html, ev) { const t = tipEl(); t.innerHTML = html; t.style.display = 'block'; t.style.left = (ev.clientX + 12) + 'px'; t.style.top = (ev.clientY + 12) + 'px'; }
  function hideTip() { const t = $('viz2-samp-tip'); if (t) t.style.display = 'none'; }

  function injectStyle() {
    if ($('viz2-samp-style')) return;
    const st = document.createElement('style');
    st.id = 'viz2-samp-style';
    st.textContent = `
      .viz2-samp-stats { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin: 10px 0; }
      .viz2-samp-tile { background: rgba(5,46,22,0.5); border: 1px solid var(--border-soft);
        border-radius: var(--radius-sm); padding: 9px 11px; }
      .viz2-samp-tile .t-lbl { font-family: var(--font-mono); font-size: 9px; letter-spacing: 0.08em;
        color: var(--grey); text-transform: uppercase; }
      .viz2-samp-tile .t-val { font-family: var(--font-mono); font-size: 18px; color: var(--white); margin-top: 3px; }
      .viz2-samp-tile .t-val.good { color: var(--green-bright); }
      .viz2-samp-tile .t-val.warn { color: var(--node-4); }
      .viz2-samp-tile .t-val.bad  { color: var(--node-7); }
      .viz2-samp-tile .t-sub { font-family: var(--font-mono); font-size: 10px; color: var(--grey); margin-top: 1px; }
      .viz2-samp-btnrow { display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0; }
      svg.viz2-samp-dist { width: 100%; height: 150px; display: block; background: var(--black);
        border: 1px solid var(--border); border-radius: var(--radius-sm); margin-top: 8px; }
      .viz2-samp-sig { font-family: var(--font-mono); font-size: 12px; color: var(--green-mint);
        line-height: 1.6; margin-top: 8px; }
      .viz2-samp-sig strong { color: var(--white); }
    `;
    document.head.appendChild(st);
  }

  // ── State ─────────────────────────────────────────────────────────────────
  const METHODS = {
    random_node: 'Random node',
    ego: 'Ego-centric (1-hop)',
    snowball: 'Snowball (2-hop)',
    random_edge: 'Random edge',
  };
  let method = 'random_node';
  let sizeCount = null;      // absolute size (nodes for node methods, edges for edge method); null = derive 25%
  let userSetSize = false;
  let sampled = { nodes: new Set(), edges: new Set(), seeds: new Set() };
  let hasSample = false;
  let simN = 100;
  let simStat = 'mean_degree';
  let lastSim = null;        // { samples:[], trueVal, statLabel }

  // ── Population (current active network) ────────────────────────────────────
  function population() {
    const nodes = NV.activeNodes().map((n) => ({ id: n.id, label: n.label || n.id }));
    const ids = new Set(nodes.map((n) => n.id));
    const em = new Map();
    NV.visibleLinks().forEach((l) => {
      const s = typeof l.source === 'object' ? l.source.id : l.source;
      const t = typeof l.target === 'object' ? l.target.id : l.target;
      if (!ids.has(s) || !ids.has(t) || s === t) return;
      const k = ek(s, t);
      if (!em.has(k)) em.set(k, { source: s, target: t, weight: l.weight || 1 });
    });
    return { nodes, ids, edges: [...em.values()], edgeKeys: new Set(em.keys()) };
  }

  // ── Sampling primitives (ported from the sampling lab) ────────────────────
  function shuffle(a) { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; }
  function fullAdj(pop) {
    const adj = Object.create(null); pop.nodes.forEach((n) => { adj[n.id] = []; });
    pop.edges.forEach((e) => { adj[e.source].push(e.target); adj[e.target].push(e.source); });
    return adj;
  }
  function sampleRandomNode(pop, k) {
    const picked = shuffle(pop.nodes).slice(0, k).map((n) => n.id);
    const nodeSet = new Set(picked); const edgeSet = new Set();
    pop.edges.forEach((e) => { if (nodeSet.has(e.source) && nodeSet.has(e.target)) edgeSet.add(ek(e.source, e.target)); });
    return { nodes: nodeSet, edges: edgeSet, seeds: new Set() };
  }
  function sampleEgo(pop, k, hops) {
    const seeds = shuffle(pop.nodes).slice(0, k).map((n) => n.id);
    const seedSet = new Set(seeds); const nodeSet = new Set(seeds);
    const adj = fullAdj(pop);
    let frontier = new Set(seeds);
    for (let h = 0; h < hops; h++) {
      const next = new Set();
      frontier.forEach((id) => (adj[id] || []).forEach((nb) => { if (!nodeSet.has(nb)) { nodeSet.add(nb); next.add(nb); } }));
      frontier = next;
    }
    const edgeSet = new Set();
    pop.edges.forEach((e) => {
      const k2 = ek(e.source, e.target);
      if (hops === 1) { if (seedSet.has(e.source) || seedSet.has(e.target)) edgeSet.add(k2); }
      else { if (nodeSet.has(e.source) && nodeSet.has(e.target)) edgeSet.add(k2); }
    });
    return { nodes: nodeSet, edges: edgeSet, seeds: seedSet };
  }
  function sampleRandomEdge(pop, k) {
    const picked = shuffle(pop.edges).slice(0, k);
    const nodeSet = new Set(); const edgeSet = new Set();
    picked.forEach((e) => { nodeSet.add(e.source); nodeSet.add(e.target); edgeSet.add(ek(e.source, e.target)); });
    return { nodes: nodeSet, edges: edgeSet, seeds: new Set() };
  }
  function edgeMethod() { return method === 'random_edge'; }
  function defaultSize(pop) { return Math.max(1, Math.round(0.25 * (edgeMethod() ? pop.edges.length : pop.nodes.length))); }
  function drawSample(pop, k) {
    if (method === 'random_node') return sampleRandomNode(pop, k);
    if (method === 'ego') return sampleEgo(pop, k, 1);
    if (method === 'snowball') return sampleEgo(pop, k, 2);
    return sampleRandomEdge(pop, k);
  }

  // ── Stats on a (nodeSet, edgeSet) ─────────────────────────────────────────
  function buildAdj(pop, nodeSet, edgeSet) {
    const adj = Object.create(null); nodeSet.forEach((id) => { adj[id] = []; });
    pop.edges.forEach((e) => {
      const k = ek(e.source, e.target);
      if ((!edgeSet || edgeSet.has(k)) && nodeSet.has(e.source) && nodeSet.has(e.target)) { adj[e.source].push(e.target); adj[e.target].push(e.source); }
    });
    return adj;
  }
  function countTriangles(pop, nodeSet, edgeSet) {
    const adj = buildAdj(pop, nodeSet, edgeSet);
    const ids = [...nodeSet].sort(); const idx = {}; ids.forEach((id, i) => { idx[id] = i; });
    const nb = {}; ids.forEach((id) => { nb[id] = new Set(adj[id]); });
    let c = 0;
    for (let i = 0; i < ids.length; i++) { const u = ids[i]; for (const v of adj[u]) { if (idx[v] <= idx[u]) continue; for (const w of adj[v]) { if (idx[w] <= idx[v]) continue; if (nb[u].has(w)) c++; } } }
    return c;
  }
  function meanDegree(pop, nodeSet, edgeSet) {
    if (nodeSet.size === 0) return 0;
    const adj = buildAdj(pop, nodeSet, edgeSet); let s = 0; nodeSet.forEach((id) => { s += adj[id].length; }); return s / nodeSet.size;
  }
  function density(pop, nodeSet, edgeSet) {
    const n = nodeSet.size; if (n < 2) return 0; let e = 0; nodeSet.forEach((id) => {}); // edge count = edgeSet size intersect induced
    edgeSet.forEach((k) => { const [a, b] = k.split('|'); if (nodeSet.has(a) && nodeSet.has(b)) e++; });
    return 2 * e / (n * (n - 1));
  }
  function transitivity(pop, nodeSet, edgeSet) {
    const adj = buildAdj(pop, nodeSet, edgeSet);
    const tri = countTriangles(pop, nodeSet, edgeSet);
    let triples = 0; nodeSet.forEach((id) => { const d = adj[id].length; triples += d * (d - 1) / 2; });
    return triples === 0 ? 0 : (3 * tri) / triples;
  }
  function apl(pop, nodeSet, edgeSet) {
    const adj = buildAdj(pop, nodeSet, edgeSet); const ids = [...nodeSet];
    let total = 0, count = 0;
    ids.forEach((src) => {
      const dist = { [src]: 0 }; const q = [src];
      while (q.length) { const u = q.shift(); (adj[u] || []).forEach((v) => { if (dist[v] === undefined) { dist[v] = dist[u] + 1; q.push(v); } }); }
      ids.forEach((t) => { if (t !== src && dist[t] !== undefined) { total += dist[t]; count++; } });
    });
    return count ? total / count : 0;
  }
  // Degree + weighted degree (strength) over the induced sampled edges.
  function degMaps(pop, nodeSet, edgeSet) {
    const deg = Object.create(null), wdeg = Object.create(null);
    nodeSet.forEach((id) => { deg[id] = 0; wdeg[id] = 0; });
    pop.edges.forEach((e) => {
      const k = ek(e.source, e.target);
      if ((!edgeSet || edgeSet.has(k)) && nodeSet.has(e.source) && nodeSet.has(e.target)) {
        deg[e.source]++; deg[e.target]++;
        wdeg[e.source] += e.weight; wdeg[e.target] += e.weight;
      }
    });
    return { deg, wdeg };
  }
  function meanOfMap(m, ids) { if (!ids.length) return 0; let s = 0; ids.forEach((id) => { s += m[id]; }); return s / ids.length; }
  function sdOfMap(m, ids) { const n = ids.length; if (n < 2) return 0; const mu = meanOfMap(m, ids); let v = 0; ids.forEach((id) => { const d = m[id] - mu; v += d * d; }); return Math.sqrt(v / (n - 1)); }
  function meanWDegree(pop, nodeSet, edgeSet) { const { wdeg } = degMaps(pop, nodeSet, edgeSet); return meanOfMap(wdeg, [...nodeSet]); }
  function sdDegree(pop, nodeSet, edgeSet) { const { deg } = degMaps(pop, nodeSet, edgeSet); return sdOfMap(deg, [...nodeSet]); }
  function sdWDegree(pop, nodeSet, edgeSet) { const { wdeg } = degMaps(pop, nodeSet, edgeSet); return sdOfMap(wdeg, [...nodeSet]); }

  // ── Node-level stats for the currently-selected node ──────────────────────
  // The focal node is kept in every sample (unioned in) so its centrality is
  // always defined; stats are measured on the induced subgraph of the sample.
  function inducedFocal(pop, nodeSet, focal) {
    const nset = new Set(nodeSet); if (focal) nset.add(focal);
    return { nset, ids: [...nset], adj: buildAdj(pop, nset, null) };
  }
  function betweennessOf(adj, ids, focal) {
    // Brandes' algorithm (unweighted). Undirected → halve the accumulation.
    const CB = Object.create(null); ids.forEach((id) => { CB[id] = 0; });
    ids.forEach((s) => {
      const S = [], P = {}, sigma = {}, d = {};
      ids.forEach((t) => { P[t] = []; sigma[t] = 0; d[t] = -1; });
      sigma[s] = 1; d[s] = 0; const Q = [s];
      while (Q.length) { const v = Q.shift(); S.push(v); (adj[v] || []).forEach((w) => { if (d[w] < 0) { d[w] = d[v] + 1; Q.push(w); } if (d[w] === d[v] + 1) { sigma[w] += sigma[v]; P[w].push(v); } }); }
      const delta = {}; ids.forEach((t) => { delta[t] = 0; });
      while (S.length) { const w = S.pop(); P[w].forEach((v) => { delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w]); }); if (w !== s) CB[w] += delta[w]; }
    });
    return CB[focal] === undefined ? 0 : CB[focal] / 2;
  }
  function nodeAplFrom(adj, focal) {
    const dist = { [focal]: 0 }; const q = [focal];
    while (q.length) { const u = q.shift(); (adj[u] || []).forEach((v) => { if (dist[v] === undefined) { dist[v] = dist[u] + 1; q.push(v); } }); }
    let tot = 0, c = 0; for (const k in dist) { if (k !== String(focal)) { tot += dist[k]; c++; } }
    return c ? tot / c : 0;
  }
  function nodeDegree(pop, nodeSet, focal) { if (!focal || !pop.ids.has(focal)) return NaN; const { adj } = inducedFocal(pop, nodeSet, focal); return (adj[focal] || []).length; }
  function nodeWDegree(pop, nodeSet, focal) {
    if (!focal || !pop.ids.has(focal)) return NaN;
    const nset = new Set(nodeSet); nset.add(focal); let s = 0;
    pop.edges.forEach((e) => { if (nset.has(e.source) && nset.has(e.target) && (e.source === focal || e.target === focal)) s += e.weight; });
    return s;
  }
  function nodeBetween(pop, nodeSet, focal) { if (!focal || !pop.ids.has(focal)) return NaN; const { ids, adj } = inducedFocal(pop, nodeSet, focal); return betweennessOf(adj, ids, focal); }
  function nodeApl(pop, nodeSet, focal) { if (!focal || !pop.ids.has(focal)) return NaN; const { adj } = inducedFocal(pop, nodeSet, focal); return nodeAplFrom(adj, focal); }
  // Number of nodes exactly k hops from the focal node (k=1 is plain degree).
  function nodeKHop(pop, nodeSet, focal, k) {
    if (!focal || !pop.ids.has(focal)) return NaN;
    const { adj } = inducedFocal(pop, nodeSet, focal);
    const dist = { [focal]: 0 }; const q = [focal];
    while (q.length) { const u = q.shift(); (adj[u] || []).forEach((v) => { if (dist[v] === undefined) { dist[v] = dist[u] + 1; q.push(v); } }); }
    let c = 0; for (const id in dist) if (dist[id] === k) c++;
    return c;
  }

  const STATS = {
    mean_degree:  { label: 'Mean degree', fn: (p, n, e) => meanDegree(p, n, e), dp: 2 },
    mean_wdegree: { label: 'Mean weighted degree', fn: (p, n, e) => meanWDegree(p, n, e), dp: 2 },
    sd_degree:    { label: 'SD of degree', fn: (p, n, e) => sdDegree(p, n, e), dp: 2 },
    sd_wdegree:   { label: 'SD of weighted degree', fn: (p, n, e) => sdWDegree(p, n, e), dp: 2 },
    triangles:    { label: 'Number of triangles', fn: (p, n, e) => countTriangles(p, n, e), dp: 0 },
    transitivity: { label: 'Transitivity (clustering)', fn: (p, n, e) => transitivity(p, n, e), dp: 3 },
    apl:          { label: 'Average path length', fn: (p, n, e) => apl(p, n, e), dp: 2 },
    density:      { label: 'Density', fn: (p, n, e) => density(p, n, e), dp: 3 },
    node_cov:     { label: 'Node count', fn: (p, n, e) => n.size, dp: 0 },
    node_degree:  { label: 'Selected node — degree', node: true, fn: (p, n, e, f) => nodeDegree(p, n, f), dp: 1 },
    node_wdegree: { label: 'Selected node — weighted degree', node: true, fn: (p, n, e, f) => nodeWDegree(p, n, f), dp: 1 },
    node_betw:    { label: 'Selected node — betweenness', node: true, fn: (p, n, e, f) => nodeBetween(p, n, f), dp: 1 },
    node_apl:     { label: 'Selected node — avg path length', node: true, fn: (p, n, e, f) => nodeApl(p, n, f), dp: 2 },
    node_deg2:    { label: 'Selected node — 2nd-degree neighbors', node: true, fn: (p, n, e, f) => nodeKHop(p, n, f, 2), dp: 0 },
    node_deg3:    { label: 'Selected node — 3rd-degree neighbors', node: true, fn: (p, n, e, f) => nodeKHop(p, n, f, 3), dp: 0 },
  };
  function nodeStatsAvailable() { const f = NV.state.selectedNode; return f && population().ids.has(f); }

  // ── Highlight the sample in the graph (runs on every core render) ─────────
  function decorate() {
    if (!hasSample || NV.state.layout === 'matrix') return;
    const svg = $('graph'); if (!svg) return;
    const nodeSel = svg.querySelectorAll('g.nodes > g.node-g');
    nodeSel.forEach((g) => {
      const d = g.__data__; if (!d) return;
      const inS = sampled.nodes.has(d.id), seed = sampled.seeds.has(d.id);
      const body = g.querySelector('circle.node-body'); if (!body) return;
      const fill = inS ? (seed ? '#fbbf24' : '#39FF14') : '#1f3d28';
      body.setAttribute('fill', fill);
      body.setAttribute('fill-opacity', inS ? '0.95' : '0.35');
      body.style.filter = inS ? `drop-shadow(0 0 6px ${fill})` : 'none';
      g.style.opacity = inS ? '1' : '0.5';
    });
    const lineSel = svg.querySelectorAll('g.links > line');
    lineSel.forEach((ln) => {
      const d = ln.__data__; if (!d) return;
      const s = typeof d.source === 'object' ? d.source.id : d.source;
      const t = typeof d.target === 'object' ? d.target.id : d.target;
      const inS = sampled.edges.has(ek(s, t));
      ln.setAttribute('stroke', inS ? '#39FF14' : '#1f3d28');
      ln.setAttribute('stroke-opacity', inS ? '0.75' : '0.18');
    });
  }

  // ── Take one sample ───────────────────────────────────────────────────────
  function resample() {
    const pop = population(); if (!pop.nodes.length) return;
    const k = (userSetSize && sizeCount) ? sizeCount : defaultSize(pop);
    sampled = drawSample(pop, Math.max(1, Math.min(k, edgeMethod() ? pop.edges.length : pop.nodes.length)));
    hasSample = true;
    NV.render();       // redraws graph; decorate() runs on the 'render' event
    renderCard();
  }
  function clearSample() { hasSample = false; sampled = { nodes: new Set(), edges: new Set(), seeds: new Set() }; NV.render(); renderCard(); }

  // ── Simulation: N samples → distribution vs true ──────────────────────────
  async function runSim() {
    const pop = population(); if (!pop.nodes.length) return;
    const stat = STATS[simStat]; if (!stat) return;
    const status = $('viz2-samp-simstatus');
    // Node-level stats need a selected node that's in the population.
    const focal = NV.state.selectedNode;
    if (stat.node && (!focal || !pop.ids.has(focal))) {
      if (status) status.textContent = 'Select a node in the graph first.';
      return;
    }
    const trueVal = stat.fn(pop, pop.ids, pop.edgeKeys, focal);
    const k = (userSetSize && sizeCount) ? sizeCount : defaultSize(pop);
    const kClamped = Math.max(1, Math.min(k, edgeMethod() ? pop.edges.length : pop.nodes.length));
    const btn = $('viz2-samp-run'); if (btn) btn.disabled = true;
    const samples = [];
    let i = 0; const BATCH = 20;
    while (i < simN) {
      const end = Math.min(i + BATCH, simN);
      for (; i < end; i++) { const s = drawSample(pop, kClamped); samples.push(stat.fn(pop, s.nodes, s.edges, focal)); }
      if (status) status.textContent = `Sampling… ${i}/${simN}`;
      await new Promise((r) => setTimeout(r, 0));
    }
    if (btn) btn.disabled = false;
    if (status) status.textContent = '';
    const focalLabel = stat.node ? (NV.activeNodes().find((x) => x.id === focal) || {}).label || focal : null;
    lastSim = { samples, trueVal, statLabel: stat.label, dp: stat.dp, focalLabel };
    renderCard();
  }

  function drawDist(svg, samples, trueVal, dp) {
    svg.innerHTML = ''; hideTip();
    dp = dp == null ? 2 : dp;
    const finite = samples.filter((x) => isFinite(x)); if (!finite.length) return;
    const W = svg.clientWidth || 320, H = svg.clientHeight || 150; const mL = 8, mR = 8, mT = 10, mB = 30;
    let lo = Math.min(...finite, trueVal), hi = Math.max(...finite, trueVal);
    if (lo === hi) { lo -= 1; hi += 1; } const pad = (hi - lo) * 0.05; lo -= pad; hi += pad;
    const x = d3.scaleLinear().domain([lo, hi]).range([mL, W - mR]);
    const bins = d3.bin().domain([lo, hi]).thresholds(22)(finite);
    const maxC = d3.max(bins, (b) => b.length) || 1;
    const y = d3.scaleLinear().domain([0, maxC]).range([H - mB, mT]);
    const root = d3.select(svg);

    // Histogram bars (hover → bin range + count)
    root.append('g').selectAll('rect').data(bins).enter().append('rect')
      .attr('x', (b) => x(b.x0) + 0.5).attr('y', (b) => y(b.length))
      .attr('width', (b) => Math.max(0, x(b.x1) - x(b.x0) - 1)).attr('height', (b) => (H - mB) - y(b.length))
      .attr('fill', '#39FF14').attr('fill-opacity', 0.5).attr('stroke', '#39FF14').attr('stroke-opacity', 0.5)
      .style('cursor', 'crosshair')
      .on('mousemove', function (ev, b) { showTip(`<strong>[${fmtN(b.x0, dp)}, ${fmtN(b.x1, dp)})</strong><br>${b.length} of ${finite.length} samples`, ev); })
      .on('mouseout', hideTip);

    // X axis: baseline + ~5 ticks with values
    root.append('line').attr('x1', mL).attr('x2', W - mR).attr('y1', H - mB).attr('y2', H - mB).attr('stroke', '#6b8170').attr('stroke-width', 1);
    x.ticks(5).forEach((tv) => {
      const xp = x(tv);
      root.append('line').attr('x1', xp).attr('x2', xp).attr('y1', H - mB).attr('y2', H - mB + 4).attr('stroke', '#6b8170');
      root.append('text').attr('x', xp).attr('y', H - mB + 15).attr('text-anchor', 'middle')
        .attr('font-family', 'Space Mono, monospace').attr('font-size', '8.5px').attr('fill', '#a3b8a3').text(fmtN(tv, dp));
    });

    // Reference lines: 2.5% / 97.5% percentiles (grey), sample mean (indigo), true (amber)
    const mean = finite.reduce((a, b) => a + b, 0) / finite.length;
    const p025 = quantile(finite, 0.025), p975 = quantile(finite, 0.975);
    const lines = [
      { v: p025, c: '#6b8170', lbl: '2.5%', tip: '2.5th percentile of the sampling distribution', dash: '2,2', w: 1.2 },
      { v: p975, c: '#6b8170', lbl: '97.5%', tip: '97.5th percentile of the sampling distribution', dash: '2,2', w: 1.2 },
      { v: mean, c: '#818cf8', lbl: 'mean', tip: 'Mean of the sampling distribution', dash: '3,2', w: 1.6 },
      { v: trueVal, c: '#fbbf24', lbl: 'true', tip: 'True population value', dash: null, w: 2.6 },
    ];
    // Assign each label a stacked level so close-together lines don't overlap.
    const placed = [];
    const withX = lines.filter((r) => isFinite(r.v)).map((r) => ({ ...r, xp: x(r.v) })).sort((a, b) => a.xp - b.xp);
    withX.forEach((r) => {
      let level = 0;
      while (placed.some((p) => p.level === level && Math.abs(p.xp - r.xp) < 30)) level++;
      placed.push({ xp: r.xp, level }); r.level = level;
    });
    withX.forEach((r) => {
      const xp = r.xp;
      root.append('line').attr('x1', xp).attr('x2', xp).attr('y1', mT).attr('y2', H - mB)
        .attr('stroke', r.c).attr('stroke-width', r.w).attr('stroke-dasharray', r.dash).style('cursor', 'help')
        .on('mousemove', function (ev) { showTip(`<strong>${r.tip}:</strong> ${fmtN(r.v, dp)}`, ev); })
        .on('mouseout', hideTip);
      // Flip the label to the left of the line if it would run off the right edge.
      const leftSide = xp > W - 34;
      root.append('text').attr('x', xp + (leftSide ? -2 : 2)).attr('y', mT + 8 + r.level * 10)
        .attr('text-anchor', leftSide ? 'end' : 'start')
        .attr('font-family', 'Space Mono, monospace').attr('font-size', '8.5px')
        .attr('fill', r.c).attr('font-weight', r.dash ? 400 : 700).text(r.lbl);
    });
  }

  // ── The Sampling card ─────────────────────────────────────────────────────
  function renderCard() {
    injectStyle();
    const card = $('viz2-sampling-card'); if (!card) return;
    const host = card.querySelector('.card-body'); if (!host) return;
    const s = NV.state;
    if (!s.graph) { host.innerHTML = '<div class="node-empty">Load a network to enable sampling.</div>'; return; }
    const pop = population();
    const focalNode = NV.activeNodes().find((x) => x.id === s.selectedNode);
    // If a per-node stat is selected but no node is (still) selected, fall back.
    if (STATS[simStat] && STATS[simStat].node && !focalNode) simStat = 'mean_degree';
    const unit = edgeMethod() ? 'edges' : 'nodes';
    const popCount = edgeMethod() ? pop.edges.length : pop.nodes.length;
    const curSize = (userSetSize && sizeCount) ? sizeCount : defaultSize(pop);
    const pct = popCount ? Math.round(100 * curSize / popCount) : 0;

    // Live single-sample stats
    let statsHtml = '<div class="node-empty" style="padding:10px;">Draw a sample to see coverage stats.</div>';
    if (hasSample) {
      const trueTri = countTriangles(pop, pop.ids, pop.edgeKeys);
      const trueMd = meanDegree(pop, pop.ids, pop.edgeKeys);
      const nodeCovPct = pop.nodes.length ? Math.round(100 * sampled.nodes.size / pop.nodes.length) : 0;
      const edgeCovPct = pop.edges.length ? Math.round(100 * sampled.edges.size / pop.edges.length) : 0;
      const triCount = countTriangles(pop, sampled.nodes, sampled.edges);
      const triPres = trueTri === 0 ? 0 : Math.round(100 * triCount / trueTri);
      const md = meanDegree(pop, sampled.nodes, sampled.edges);
      const triCls = triPres >= 70 ? 'good' : triPres >= 30 ? 'warn' : 'bad';
      const ratio = trueMd ? md / trueMd : 1; const mdCls = (ratio > 1.4 || ratio < 0.6) ? 'bad' : (ratio > 1.15 || ratio < 0.85) ? 'warn' : 'good';
      statsHtml = `<div class="viz2-samp-stats">
        <div class="viz2-samp-tile"><div class="t-lbl">Node coverage</div><div class="t-val good">${sampled.nodes.size}/${pop.nodes.length} · ${nodeCovPct}%</div></div>
        <div class="viz2-samp-tile"><div class="t-lbl">Edge coverage</div><div class="t-val good">${sampled.edges.size}/${pop.edges.length} · ${edgeCovPct}%</div></div>
        <div class="viz2-samp-tile"><div class="t-lbl">△ Triangles</div><div class="t-val">${triCount} / ${trueTri}</div></div>
        <div class="viz2-samp-tile"><div class="t-lbl">Triangle preservation</div><div class="t-val ${triCls}">${triPres}%</div></div>
        <div class="viz2-samp-tile"><div class="t-lbl">Mean degree (sample)</div><div class="t-val ${mdCls}">${md.toFixed(2)}</div><div class="t-sub">true: ${trueMd.toFixed(2)}</div></div>
        <div class="viz2-samp-tile"><div class="t-lbl">Seeds</div><div class="t-val">${sampled.seeds.size || '—'}</div></div>
      </div>`;
    }

    // Simulation panel
    let simHtml = '';
    if (lastSim) {
      const N = lastSim.samples.length; const tv = lastSim.trueVal;
      const gt = lastSim.samples.filter((x) => x > tv).length;
      const lt = lastSim.samples.filter((x) => x < tv).length;
      const eqp = N - gt - lt;
      const mean = lastSim.samples.reduce((a, b) => a + b, 0) / N;
      const bias = mean - tv;
      const pctG = Math.round(100 * gt / N), pctL = Math.round(100 * lt / N);
      // Significance is about MAGNITUDE, not just direction: the sample is only
      // "significantly" biased if the true value lands outside the central 95%
      // of the sampling distribution (below 2.5% or above 97.5%).
      const p025 = quantile(lastSim.samples, 0.025), p975 = quantile(lastSim.samples, 0.975);
      let verdict;
      if (tv > p975) verdict = 'The true value sits <strong>above the 97.5th percentile</strong> of the sampling distribution, so the sample <strong>significantly under-estimates</strong> it.';
      else if (tv < p025) verdict = 'The true value sits <strong>below the 2.5th percentile</strong> of the sampling distribution, so the sample <strong>significantly over-estimates</strong> it.';
      else verdict = 'The true value falls <strong>within the central 95%</strong> (2.5–97.5%) of the sampling distribution, so the sample is <strong>not significantly biased</strong> for this statistic.';
      const statName = lastSim.focalLabel ? `${lastSim.statLabel} of <strong>${esc(lastSim.focalLabel)}</strong>` : lastSim.statLabel;
      simHtml = `
        <svg class="viz2-samp-dist" id="viz2-samp-distsvg"></svg>
        <div class="viz2-samp-sig">
          Over <strong>${N}</strong> samples of ${statName}, the true value is <strong>${tv.toFixed(lastSim.dp)}</strong>;
          the sample mean is <strong>${mean.toFixed(lastSim.dp)}</strong> (bias ${bias >= 0 ? '+' : ''}${bias.toFixed(lastSim.dp)}), central 95% = [${fmtN(p025, lastSim.dp)}, ${fmtN(p975, lastSim.dp)}].<br>
          <strong>${pctG}%</strong> of samples exceeded the true value, <strong>${pctL}%</strong> fell below${eqp ? `, ${100 - pctG - pctL}% tied` : ''}. ${verdict}
        </div>`;
    }

    host.innerHTML = `
      <p class="formula-note" style="margin:0 0 10px;">Draw a sample from the current network and see it highlighted in the graph.
        Sampled nodes glow <span style="color:#39FF14;">green</span>, seeds <span style="color:#fbbf24;">amber</span>, the rest dim.</p>
      <div class="color-by-row" style="margin-bottom:8px;"><label for="viz2-samp-method">Method</label>
        <select id="viz2-samp-method" class="viz-select">${Object.entries(METHODS).map(([k, v]) => `<option value="${k}"${k === method ? ' selected' : ''}>${v}</option>`).join('')}</select></div>
      <div class="color-by-row" style="margin-bottom:8px;"><label for="viz2-samp-size">Sample size (${unit}) — default 25%</label>
        <input id="viz2-samp-size" type="number" min="1" max="${popCount}" value="${curSize}" class="viz-select" style="width:100%;">
        <span class="t-sub" style="font-family:var(--font-mono);font-size:10px;color:var(--grey);">= ${pct}% of ${popCount} ${unit}</span></div>
      <div class="viz2-samp-btnrow">
        <button id="viz2-samp-draw" class="viz-btn viz-btn-primary">🎯 Draw sample</button>
        <button id="viz2-samp-clear" class="viz-btn">Clear</button>
      </div>
      ${statsHtml}
      <details class="viz2-nested-formulas" data-card="samp-sim" ${lastSim ? 'open' : ''} style="margin-top:6px;">
        <summary>📈 Sampling distribution (many samples)</summary>
        <div style="padding-top:8px;">
          <div class="color-by-row" style="margin-bottom:8px;"><label for="viz2-samp-stat">Statistic of interest</label>
            <select id="viz2-samp-stat" class="viz-select">${Object.entries(STATS).map(([k, v]) => {
              const dis = v.node && !focalNode ? ' disabled' : '';
              const lbl = v.node && !focalNode ? v.label + ' (select a node)' : v.label;
              return `<option value="${k}"${k === simStat ? ' selected' : ''}${dis}>${lbl}</option>`;
            }).join('')}</select></div>
          <p class="formula-note" style="margin:-2px 0 8px;">${focalNode
            ? `Per-node metrics measure the selected node <strong>${esc(focalNode.label)}</strong> (kept in every sample).`
            : `Click a node in the graph to unlock per-node metrics (degree, weighted degree, betweenness, path length).`}</p>
          <div class="color-by-row" style="margin-bottom:8px;"><label for="viz2-samp-n"># samples</label>
            <select id="viz2-samp-n" class="viz-select">
              <option value="100"${simN === 100 ? ' selected' : ''}>100 (quick)</option>
              <option value="200"${simN === 200 ? ' selected' : ''}>200</option>
              <option value="500"${simN === 500 ? ' selected' : ''}>500 (solid)</option>
              <option value="1000"${simN === 1000 ? ' selected' : ''}>1000</option>
            </select></div>
          <div class="viz2-samp-btnrow"><button id="viz2-samp-run" class="viz-btn">📈 Run ${simN} samples</button>
            <span id="viz2-samp-simstatus" class="formula-note" style="margin:0;flex:1;"></span></div>
          ${simHtml}
        </div>
      </details>
      <div style="margin-top:10px;display:flex;gap:6px;flex-wrap:wrap;">
        <button id="viz2-samp-export-r" class="viz-btn">▶ R in playground</button>
        <button id="viz2-samp-export-py" class="viz-btn">▶ Python in playground</button>
      </div>
      <div id="viz2-samp-exportmsg" class="formula-note" style="margin-top:6px;"></div>`;

    // Draw the distribution after the DOM exists
    if (lastSim) { const svg = $('viz2-samp-distsvg'); if (svg) drawDist(svg, lastSim.samples, lastSim.trueVal, lastSim.dp); }

    const on = (id, ev, fn) => { const el = $(id); if (el) el.addEventListener(ev, fn); };
    on('viz2-samp-method', 'change', (e) => { method = e.target.value; userSetSize = false; sizeCount = null; renderCard(); });
    on('viz2-samp-size', 'change', (e) => { const v = parseInt(e.target.value, 10); if (v > 0) { sizeCount = v; userSetSize = true; } renderCard(); });
    on('viz2-samp-draw', 'click', resample);
    on('viz2-samp-clear', 'click', clearSample);
    on('viz2-samp-stat', 'change', (e) => { simStat = e.target.value; });
    on('viz2-samp-n', 'change', (e) => { simN = parseInt(e.target.value, 10) || 200; const b = $('viz2-samp-run'); if (b) b.textContent = `📈 Run ${simN} samples`; });
    on('viz2-samp-run', 'click', runSim);
    on('viz2-samp-export-r', 'click', () => exportCode('r'));
    on('viz2-samp-export-py', 'click', () => exportCode('py'));
  }

  // ── Code export ───────────────────────────────────────────────────────────
  function exportCtx() {
    const s = NV.state; const map = s.mapping || {}; const key = s.currentDatasetKey || null;
    return { key, nodesFile: key ? key + '-nodes.csv' : 'nodes.csv', edgesFile: key ? key + '-edges.csv' : 'edges.csv',
      fromCol: map.from || 'from', toCol: map.to || 'to', idCol: map.nodeId || 'node_id',
      weightCol: map.weight || null, focal: s.selectedNode || null };
  }
  const rStr = (s) => '"' + String(s).replace(/"/g, '\\"') + '"';
  const pyStr = (s) => '"' + String(s).replace(/"/g, '\\"') + '"';
  function exportCode(lang) {
    const stat = STATS[simStat];
    if (stat.node && !(NV.state.selectedNode && population().ids.has(NV.state.selectedNode))) {
      const m = $('viz2-samp-exportmsg'); if (m) m.textContent = 'Select a node in the graph before exporting a per-node metric.'; return;
    }
    const code = lang === 'r' ? genR() : genPy();
    try { localStorage.setItem('netsci-playground-handoff', JSON.stringify({ lang: lang === 'r' ? 'r' : 'python', code, datasetKey: NV.state.currentDatasetKey || null, ts: Date.now(), source: 'visualizer' })); }
    catch (e) { const m = $('viz2-samp-exportmsg'); if (m) m.textContent = 'Could not save handoff.'; return; }
    window.open(lang === 'r' ? 'playground-r.html' : 'playground-py.html', '_blank');
    const m = $('viz2-samp-exportmsg'); if (m) m.textContent = 'Opened the ' + (lang === 'r' ? 'R' : 'Python') + ' playground — it runs the sampling simulation when it finishes loading.';
  }
  function genR() {
    const c = exportCtx(); const isEdge = edgeMethod(); const stat = STATS[simStat]; const isNode = !!stat.node;
    const pop = population(); const k = (userSetSize && sizeCount) ? sizeCount : defaultSize(pop);
    const L = [];
    L.push('#\' @name sampling.R');
    L.push('#\' @title Network sampling — from the Network Visualizer');
    L.push('#\' @description Draw ' + simN + ' ' + METHODS[method] + ' samples, build a sampling');
    L.push('#\' distribution of ' + stat.label + ', and compare it to the true value.');
    L.push('');
    L.push('# 0. Setup ###################################################################');
    L.push('library(igraph)');
    L.push('cat("\\n🚀 Network sampling (R)\\n")');
    L.push('');
    L.push('# 1. Build the graph ########################################################');
    L.push('nodes <- read.csv(' + rStr(c.nodesFile) + ', stringsAsFactors = FALSE)');
    L.push('edges <- read.csv(' + rStr(c.edgesFile) + ', stringsAsFactors = FALSE)');
    L.push('edges <- edges[, c(' + rStr(c.fromCol) + ', ' + rStr(c.toCol) + ', setdiff(names(edges), c(' + rStr(c.fromCol) + ', ' + rStr(c.toCol) + ')))]');
    L.push('nodes <- nodes[, c(' + rStr(c.idCol) + ', setdiff(names(nodes), ' + rStr(c.idCol) + '))]');
    L.push('g <- igraph::simplify(igraph::graph_from_data_frame(edges, directed = FALSE, vertices = nodes), edge.attr.comb = "first")');
    L.push('cat(sprintf("✅ Population: %d nodes, %d edges.\\n", igraph::gorder(g), igraph::gsize(g)))');
    L.push('');
    L.push('SIZE <- ' + k + '   # ' + (isEdge ? 'edges' : 'nodes') + ' per sample');
    if (isNode) L.push('FOCAL <- ' + rStr(c.focal) + '   # the selected node (kept in every sample)');
    L.push('');
    L.push('# 2. The statistic + one sampler #############################################');
    if (isNode) {
      L.push('stat_fn <- function(sg) {');
      L.push('  if (!(FOCAL %in% igraph::V(sg)$name)) return(NA_real_)');
      L.push('  ' + rNodeStatExpr(simStat, c));
      L.push('}');
      L.push('draw_sample <- function(g) {');
      L.push(rNodeSampler(method));
      L.push('}');
    } else {
      L.push('stat_fn <- function(sg) ' + rStatExpr(simStat, c));
      L.push('draw_sample <- function(g) {');
      L.push(rSamplerBody(method));
      L.push('}');
    }
    L.push('true_val <- stat_fn(g)');
    L.push('');
    L.push('# 3. Many samples → sampling distribution ###################################');
    L.push('set.seed(5470)');
    L.push('sims <- replicate(' + simN + ', stat_fn(draw_sample(g)))');
    L.push('sims <- sims[is.finite(sims)]');
    L.push('q <- quantile(sims, c(0.025, 0.975))');
    L.push('cat(sprintf("📊 True %s: %.4f\\n", ' + rStr(stat.label) + ', true_val))');
    L.push('cat(sprintf("📊 Sample mean: %.4f (bias %+.4f)\\n", mean(sims), mean(sims) - true_val))');
    L.push('cat(sprintf("📊 Central 95%%: [%.4f, %.4f]\\n", q[1], q[2]))');
    L.push('verdict <- if (true_val > q[2]) "significantly under-estimates it" else if (true_val < q[1]) "significantly over-estimates it" else "is not significantly biased"');
    L.push('cat(sprintf("📝 %.0f%% above / %.0f%% below true. Sampling %s.\\n",');
    L.push('            100 * mean(sims > true_val), 100 * mean(sims < true_val), verdict))');
    L.push('hist(sims, breaks = 22, col = "#39FF14", border = "white",');
    L.push('     main = "Sampling distribution", xlab = ' + rStr(stat.label) + ')');
    L.push('abline(v = true_val, col = "#fbbf24", lwd = 3)');
    L.push('abline(v = q, col = "#6b8170", lwd = 1, lty = 2)');
    L.push('');
    L.push('cat("\\n🎉 Done.\\n")');
    return L.join('\n');
  }
  function rStatExpr(key, c) {
    const w = c.weightCol ? 'igraph::E(sg)$' + c.weightCol : null;
    switch (key) {
      case 'mean_degree': return 'mean(igraph::degree(sg))';
      case 'mean_wdegree': return w ? 'mean(igraph::strength(sg, weights = ' + w + '))' : 'mean(igraph::degree(sg))';
      case 'sd_degree': return 'sd(igraph::degree(sg))';
      case 'sd_wdegree': return w ? 'sd(igraph::strength(sg, weights = ' + w + '))' : 'sd(igraph::degree(sg))';
      case 'triangles': return 'sum(igraph::count_triangles(sg)) / 3';
      case 'transitivity': return 'igraph::transitivity(sg, type = "global")';
      case 'apl': return 'igraph::mean_distance(sg, directed = FALSE)';
      case 'density': return 'igraph::edge_density(sg)';
      default: return 'igraph::gorder(sg)';
    }
  }
  function rNodeStatExpr(key, c) {
    const w = c.weightCol ? 'igraph::E(sg)$' + c.weightCol : null;
    switch (key) {
      case 'node_degree': return 'igraph::degree(sg, v = FOCAL)';
      case 'node_wdegree': return w ? 'igraph::strength(sg, vids = FOCAL, weights = ' + w + ')' : 'igraph::degree(sg, v = FOCAL)';
      case 'node_betw': return 'igraph::betweenness(sg, v = FOCAL)';
      case 'node_apl': return 'd <- igraph::distances(sg, v = FOCAL); d <- d[is.finite(d) & d > 0]; if (length(d)) mean(d) else NA_real_';
      case 'node_deg2': return 'sum(igraph::distances(sg, v = FOCAL) == 2)';
      case 'node_deg3': return 'sum(igraph::distances(sg, v = FOCAL) == 3)';
      default: return 'igraph::degree(sg, v = FOCAL)';
    }
  }
  function rSamplerBody(m) {
    if (m === 'random_node') return '  vs <- sample(seq_len(igraph::vcount(g)), SIZE)\n  igraph::induced_subgraph(g, vs)';
    if (m === 'random_edge') return '  es <- sample(seq_len(igraph::ecount(g)), min(SIZE, igraph::ecount(g)))\n  igraph::subgraph_from_edges(g, es, delete.vertices = TRUE)';
    if (m === 'ego') return '  seeds <- sample(seq_len(igraph::vcount(g)), SIZE)\n  vs <- unique(unlist(igraph::ego(g, order = 1, nodes = seeds)))\n  igraph::induced_subgraph(g, vs)';
    return '  seeds <- sample(seq_len(igraph::vcount(g)), SIZE)\n  vs <- unique(unlist(igraph::ego(g, order = 2, nodes = seeds)))\n  igraph::induced_subgraph(g, vs)';
  }
  // Node-stat samplers: build a vertex set, then union the focal node in.
  function rNodeSampler(m) {
    const tail = '\n  vs <- union(vs, which(igraph::V(g)$name == FOCAL))\n  igraph::induced_subgraph(g, vs)';
    if (m === 'random_node') return '  vs <- sample(seq_len(igraph::vcount(g)), SIZE)' + tail;
    if (m === 'random_edge') return '  es <- sample(seq_len(igraph::ecount(g)), min(SIZE, igraph::ecount(g)))\n  vs <- unique(as.vector(igraph::ends(g, es, names = FALSE)))' + tail;
    if (m === 'ego') return '  seeds <- sample(seq_len(igraph::vcount(g)), SIZE)\n  vs <- unique(unlist(igraph::ego(g, order = 1, nodes = seeds)))' + tail;
    return '  seeds <- sample(seq_len(igraph::vcount(g)), SIZE)\n  vs <- unique(unlist(igraph::ego(g, order = 2, nodes = seeds)))' + tail;
  }
  function genPy() {
    const c = exportCtx(); const isEdge = edgeMethod(); const stat = STATS[simStat]; const isNode = !!stat.node;
    const pop = population(); const k = (userSetSize && sizeCount) ? sizeCount : defaultSize(pop);
    const L = [];
    L.push('# sampling.py');
    L.push('# Network sampling — from the Network Visualizer');
    L.push('# Draw ' + simN + ' ' + METHODS[method] + ' samples, build a sampling distribution of');
    L.push('# ' + stat.label + ', and compare it to the true value.');
    L.push('');
    L.push('# 0. Setup ###################################################################');
    L.push('import numpy as np');
    L.push('import pandas as pd');
    L.push('import igraph as ig');
    L.push('import matplotlib.pyplot as plt');
    L.push('import random');
    L.push('print("\\n🚀 Network sampling (Python)")');
    L.push('');
    L.push('# 1. Build the graph ########################################################');
    L.push('nodes = pd.read_csv(' + pyStr(c.nodesFile) + ')');
    L.push('edges = pd.read_csv(' + pyStr(c.edgesFile) + ')');
    L.push('edges = edges[[' + pyStr(c.fromCol) + ', ' + pyStr(c.toCol) + '] + [x for x in edges.columns if x not in (' + pyStr(c.fromCol) + ', ' + pyStr(c.toCol) + ')]]');
    L.push('nodes = nodes[[' + pyStr(c.idCol) + '] + [x for x in nodes.columns if x != ' + pyStr(c.idCol) + ']]');
    L.push('g = ig.Graph.DataFrame(edges, directed=False, vertices=nodes, use_vids=False).simplify(combine_edges="first")');
    L.push('print(f"✅ Population: {g.vcount()} nodes, {g.ecount()} edges.")');
    L.push('');
    L.push('SIZE = ' + k + '   # ' + (isEdge ? 'edges' : 'nodes') + ' per sample');
    if (isNode) { L.push('FOCAL = ' + pyStr(c.focal) + '   # the selected node (kept in every sample)'); L.push('FIDX = g.vs.find(name=FOCAL).index'); }
    L.push('');
    L.push('# 2. The statistic + one sampler #############################################');
    if (isNode) {
      L.push('def stat_fn(sg):');
      L.push('    try: fi = sg.vs.find(name=FOCAL).index');
      L.push('    except (ValueError, KeyError): return float("nan")');
      L.push('    ' + pyNodeStatExpr(simStat, c));
      L.push('def draw_sample(g):');
      L.push(pyNodeSampler(method));
    } else {
      L.push('def stat_fn(sg):');
      L.push('    return ' + pyStatExpr(simStat, c));
      L.push('def draw_sample(g):');
      L.push(pySamplerBody(method));
    }
    L.push('true_val = stat_fn(g)');
    L.push('');
    L.push('# 3. Many samples → sampling distribution ###################################');
    L.push('random.seed(5470)');
    L.push('sims = np.array([stat_fn(draw_sample(g)) for _ in range(' + simN + ')])');
    L.push('sims = sims[np.isfinite(sims)]');
    L.push('q = np.quantile(sims, [0.025, 0.975])');
    L.push('stat_label = ' + pyStr(stat.label));
    L.push('print(f"📊 True {stat_label}: {true_val:.4f}")');
    L.push('print(f"📊 Sample mean: {sims.mean():.4f} (bias {sims.mean()-true_val:+.4f})")');
    L.push('print(f"📊 Central 95%: [{q[0]:.4f}, {q[1]:.4f}]")');
    L.push('verdict = "significantly under-estimates it" if true_val > q[1] else "significantly over-estimates it" if true_val < q[0] else "is not significantly biased"');
    L.push('print(f"📝 {100*np.mean(sims>true_val):.0f}% above / {100*np.mean(sims<true_val):.0f}% below true. Sampling {verdict}.")');
    L.push('plt.hist(sims, bins=22, color="#39FF14", edgecolor="white")');
    L.push('plt.axvline(true_val, color="#fbbf24", linewidth=3)');
    L.push('for qq in q: plt.axvline(qq, color="#6b8170", linewidth=1, linestyle="--")');
    L.push('plt.title("Sampling distribution"); plt.xlabel(stat_label); plt.show()');
    L.push('');
    L.push('print("\\n🎉 Done.")');
    return L.join('\n');
  }
  function pyStatExpr(key, c) {
    const w = c.weightCol ? 'weights=' + pyStr(c.weightCol) : null;
    switch (key) {
      case 'mean_degree': return 'float(np.mean(sg.degree()))';
      case 'mean_wdegree': return w ? 'float(np.mean(sg.strength(' + w + ')))' : 'float(np.mean(sg.degree()))';
      case 'sd_degree': return 'float(np.std(sg.degree(), ddof=1)) if sg.vcount() > 1 else 0.0';
      case 'sd_wdegree': return w ? 'float(np.std(sg.strength(' + w + '), ddof=1)) if sg.vcount() > 1 else 0.0' : 'float(np.std(sg.degree(), ddof=1)) if sg.vcount() > 1 else 0.0';
      case 'triangles': return 'sum(sg.count_triangles()) / 3';
      case 'transitivity': return 'sg.transitivity_undirected(mode="zero")';
      case 'apl': return 'sg.average_path_length()';
      case 'density': return 'sg.density()';
      default: return 'sg.vcount()';
    }
  }
  function pyNodeStatExpr(key, c) {
    const w = c.weightCol ? ', weights=' + pyStr(c.weightCol) : '';
    switch (key) {
      case 'node_degree': return 'return sg.degree(fi)';
      case 'node_wdegree': return c.weightCol ? 'return sg.strength(fi' + w + ')' : 'return sg.degree(fi)';
      case 'node_betw': return 'return sg.betweenness(fi)';
      case 'node_apl': return 'ds = [d for d in sg.distances(source=fi)[0] if d > 0 and np.isfinite(d)]; return (sum(ds)/len(ds)) if ds else float("nan")';
      case 'node_deg2': return 'return sum(1 for d in sg.distances(source=fi)[0] if d == 2)';
      case 'node_deg3': return 'return sum(1 for d in sg.distances(source=fi)[0] if d == 3)';
      default: return 'return sg.degree(fi)';
    }
  }
  function pySamplerBody(m) {
    if (m === 'random_node') return '    vs = random.sample(range(g.vcount()), SIZE)\n    return g.induced_subgraph(vs)';
    if (m === 'random_edge') return '    es = random.sample(range(g.ecount()), min(SIZE, g.ecount()))\n    return g.subgraph_edges(es, delete_vertices=True)';
    if (m === 'ego') return '    seeds = random.sample(range(g.vcount()), SIZE)\n    vs = set(seeds)\n    for v in seeds: vs.update(g.neighborhood(v, order=1))\n    return g.induced_subgraph(list(vs))';
    return '    seeds = random.sample(range(g.vcount()), SIZE)\n    vs = set(seeds)\n    for v in seeds: vs.update(g.neighborhood(v, order=2))\n    return g.induced_subgraph(list(vs))';
  }
  function pyNodeSampler(m) {
    const tail = '\n    vs.add(FIDX)\n    return g.induced_subgraph(list(vs))';
    if (m === 'random_node') return '    vs = set(random.sample(range(g.vcount()), SIZE))' + tail;
    if (m === 'random_edge') return '    es = random.sample(range(g.ecount()), min(SIZE, g.ecount()))\n    vs = set()\n    for e in es: vs.update(g.es[e].tuple)' + tail;
    if (m === 'ego') return '    seeds = random.sample(range(g.vcount()), SIZE)\n    vs = set(seeds)\n    for v in seeds: vs.update(g.neighborhood(v, order=1))' + tail;
    return '    seeds = random.sample(range(g.vcount()), SIZE)\n    vs = set(seeds)\n    for v in seeds: vs.update(g.neighborhood(v, order=2))' + tail;
  }

  // ── Lifecycle ─────────────────────────────────────────────────────────────
  NV.on('render', decorate);
  NV.on('graph-loaded', () => { hasSample = false; lastSim = null; userSetSize = false; sizeCount = null; renderCard(); });
  NV.on('view-rebuilt', () => { renderCard(); });
  NV.on('removed-changed', () => { renderCard(); });
  NV.on('node-selected', () => { renderCard(); });   // refresh the per-node stat options

  window.NetSciVizSample = { renderCard };
  if (document.readyState !== 'loading') renderCard();
  else document.addEventListener('DOMContentLoaded', renderCard);
})();
