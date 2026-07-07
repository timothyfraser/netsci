// viz2p-clustering.js — PREVIEW ONLY (loaded only by visualizer2.html).
// Clustering (DSM) card + the "matrix" layout renderer.
//
// Ports the DSM-clustering case study (code/10_dsm-clustering + the lab page)
// into the Visualizer: a reorderable dependency-structure matrix, a single-level
// greedy-modularity ("Louvain-style") community finder, block boundaries, a
// failure-cascade tracer, six reactive metrics, and a selected-component subcard.
//
// Temporal networks: the card exposes a Time-basis select. "(all time)" unions
// every edge (aggregate); picking a slice value keeps only edges whose timeRaw
// matches — so clustering can run on one slice or the whole aggregated network.
//
// The module exposes window.NetSciVizClust.drawMatrix(svgEl); the forked core
// (viz2p-core.js) calls it from render() when state.layout === 'matrix'.
(function () {
  'use strict';
  if (!window.NetSciViz2) return;
  const NV = window.NetSciViz2;
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  // ── One-time CSS (self-contained so the live stylesheet is untouched) ──────
  function injectStyle() {
    if ($('viz2-clust-style')) return;
    const st = document.createElement('style');
    st.id = 'viz2-clust-style';
    st.textContent = `
      .viz2-clust-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin: 10px 0; }
      .viz2-clust-tile { background: rgba(5,46,22,0.5); border: 1px solid var(--border-soft);
        border-radius: var(--radius-sm); padding: 9px 10px; }
      .viz2-clust-tile .t-lbl { font-family: var(--font-mono); font-size: 9px; letter-spacing: 0.08em;
        color: var(--grey); text-transform: uppercase; line-height: 1.3; }
      .viz2-clust-tile .t-val { font-family: var(--font-display); font-size: 22px; color: var(--green-bright);
        line-height: 1.1; margin-top: 2px; }
      .viz2-clust-tile .t-val.warn { color: var(--node-4); }
      .viz2-clust-tile .t-val.bad  { color: var(--node-7); }
      .viz2-clust-substats { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 8px; }
      .viz2-clust-sub { background: rgba(5,46,22,0.5); border: 1px solid var(--border-soft);
        border-radius: var(--radius-sm); padding: 9px 11px; }
      .viz2-clust-sub .s-lbl { font-family: var(--font-mono); font-size: 9px; letter-spacing: 0.1em;
        text-transform: uppercase; color: var(--grey); }
      .viz2-clust-sub .s-val { font-family: var(--font-mono); font-size: 19px; color: var(--white); margin-top: 3px; }
      .viz2-clust-sub .s-val.bad { color: var(--node-7); }
      .viz2-clust-btnrow { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }
    `;
    document.head.appendChild(st);
  }

  // ── Module state ──────────────────────────────────────────────────────────
  let clusters = [];        // per-node community id, indexed by nodes[] index
  let order = [];           // display permutation of node indices
  let showBlocks = false;
  let cascadeSource = null;  // nodes[] index or null
  let cascadeSet = new Set();// node indices transitively depending on the source
  let selectedIdx = null;    // selected component (nodes[] index)
  let timeSlice = '';        // '' = all time; else a timeRaw value
  let sig = '';              // structure signature; when it changes, order/clusters reset
  let curCell = 18;          // last drawn cell size (svg units) — used by drag math

  // ── Build the DSM from the current active subgraph ────────────────────────
  function activeEdges() {
    const s = NV.state;
    if (!s.graph) return [];
    const removedN = s.removedNodes || new Set();
    const removedE = s.removedEdges || new Set();
    const key = NV.utils.edgeKey;
    return s.graph.links.filter((l) => {
      const src = typeof l.source === 'object' ? l.source.id : l.source;
      const tgt = typeof l.target === 'object' ? l.target.id : l.target;
      if (removedN.has(src) || removedN.has(tgt)) return false;
      if (removedE.has(key(l))) return false;
      if (timeSlice !== '' && !l.isScenario && String(l.timeRaw) !== String(timeSlice)) return false;
      return true;
    });
  }

  function buildDsm() {
    const nodes = NV.activeNodes().map((n) => ({ id: n.id, label: n.label || n.id }));
    const n = nodes.length;
    const idx = Object.create(null);
    nodes.forEach((nd, i) => { idx[nd.id] = i; });
    const adj = Array.from({ length: n }, () => new Array(n).fill(0));
    // A DSM is inherently directional: cell (i, j) means "i depends on j".
    // Always build a DIRECTED adjacency from the edgelist's from→to so the
    // matrix, off-block marks, and failure cascades are meaningful — even when
    // the Visualizer is rendering the network as undirected. (Louvain still
    // clusters on the symmetrized version; see autoCluster.)
    activeEdges().forEach((l) => {
      const s = typeof l.source === 'object' ? l.source.id : l.source;
      const t = typeof l.target === 'object' ? l.target.id : l.target;
      const a = idx[s], b = idx[t];
      if (a === undefined || b === undefined || a === b) return;
      adj[a][b] = 1;
    });
    return { nodes, adj, n };
  }

  // Rebuild + reset order/clusters/cascade whenever the structure changes.
  function ensureDsm() {
    const dsm = buildDsm();
    const newSig = dsm.nodes.map((x) => x.id).join('|') + '#' + dsm.adj.reduce((a, r) => a + r.reduce((x, y) => x + y, 0), 0) + '#' + timeSlice;
    if (newSig !== sig) {
      sig = newSig;
      order = dsm.nodes.map((_, i) => i);
      clusters = [];
      showBlocks = false;
      cascadeSource = null; cascadeSet = new Set(); selectedIdx = null;
    }
    return dsm;
  }

  // ── Algorithms (ported from the DSM lab) ──────────────────────────────────
  function symmetrize(adj) {
    const n = adj.length;
    const sym = Array.from({ length: n }, () => new Array(n).fill(0));
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) if (i !== j && (adj[i][j] || adj[j][i])) sym[i][j] = 1;
    return sym;
  }
  function modularity(adj, comm) {
    const n = adj.length;
    let m = 0; const deg = new Array(n).fill(0);
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) if (adj[i][j]) { m += 1; deg[i] += 1; }
    m = m / 2; if (m === 0) return 0;
    let Q = 0;
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) if (comm[i] === comm[j]) Q += (adj[i][j] - (deg[i] * deg[j]) / (2 * m));
    return Q / (2 * m);
  }
  function louvain(adj) {
    const n = adj.length;
    let comm = []; for (let i = 0; i < n; i++) comm.push(i);
    let improved = true, iter = 0; const maxIter = 50;
    while (improved && iter < maxIter) {
      improved = false; iter++;
      for (let i = 0; i < n; i++) {
        const orig = comm[i]; let bestC = orig; let bestQ = modularity(adj, comm);
        const tried = new Set([orig]);
        for (let j = 0; j < n; j++) {
          if (adj[i][j] && !tried.has(comm[j])) {
            tried.add(comm[j]); const newC = comm[j];
            comm[i] = newC; const q = modularity(adj, comm);
            if (q > bestQ + 1e-9) { bestQ = q; bestC = newC; }
            comm[i] = orig;
          }
        }
        if (bestC !== orig) { comm[i] = bestC; improved = true; }
      }
    }
    const remap = {}; let next = 0;
    return comm.map((c) => { if (!(c in remap)) remap[c] = next++; return remap[c]; });
  }
  function orderByCommunities(comm) {
    const n = comm.length; const ind = Array.from({ length: n }, (_, i) => i);
    ind.sort((a, b) => (comm[a] !== comm[b] ? comm[a] - comm[b] : a - b));
    return ind;
  }
  // Reverse-reachability: everything that (transitively) depends on sourceIdx.
  function computeCascade(adj, sourceIdx) {
    const n = adj.length; const affected = new Set(); const queue = [sourceIdx];
    while (queue.length) {
      const cur = queue.shift();
      for (let i = 0; i < n; i++) if (i !== cur && adj[i][cur] === 1 && !affected.has(i)) { affected.add(i); queue.push(i); }
    }
    return affected;
  }
  function largestCascadeSize(adj) {
    const n = adj.length; let mx = 0;
    for (let i = 0; i < n; i++) { const c = computeCascade(adj, i); if (c.size > mx) mx = c.size; }
    return mx;
  }
  function computeMetrics(dsm) {
    const { adj, n } = dsm;
    let deps = 0;
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) if (adj[i][j]) deps++;
    const density = n > 1 ? deps / (n * (n - 1)) : 0;
    let offBlock = 0;
    if (clusters.length === n) {
      for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) if (adj[i][j] && clusters[i] !== clusters[j]) offBlock++;
    } else offBlock = deps;
    const numClusters = clusters.length === n ? new Set(clusters).size : 0;
    return { n, deps, density, offBlock, numClusters, largestCascade: largestCascadeSize(adj) };
  }

  // ── Actions ───────────────────────────────────────────────────────────────
  // Flip the layout picker to Matrix (leaving it changeable afterward), so the
  // clustering the user just ran is immediately visible as a DSM.
  function switchToMatrix() {
    if (!NV.state.graph || NV.state.layout === 'matrix') return;
    NV.state.layout = 'matrix';
    document.querySelectorAll('.seg-layout').forEach((b) => b.classList.toggle('active', b.dataset.layout === 'matrix'));
    if (NV.unfix) NV.unfix();
    if (NV.layout) NV.layout();
  }
  function autoCluster() {
    const dsm = ensureDsm(); if (!dsm.n) return;
    clusters = louvain(symmetrize(dsm.adj));
    order = orderByCommunities(clusters);
    showBlocks = true;
    switchToMatrix();
    NV.render(); renderCard();
  }
  function toggleBlocks() { if (clusters.length === 0) { autoCluster(); return; } showBlocks = !showBlocks; NV.render(); renderCard(); }
  function resetOrder() { const dsm = ensureDsm(); order = dsm.nodes.map((_, i) => i); NV.render(); renderCard(); }
  function clearCascade() { cascadeSource = null; cascadeSet = new Set(); selectedIdx = null; NV.render(); renderCard(); }
  function selectComponent(i) {
    const dsm = ensureDsm(); if (i == null || i < 0 || i >= dsm.n) return;
    selectedIdx = i; cascadeSource = i; cascadeSet = computeCascade(dsm.adj, i);
    NV.render(); renderCard();
  }

  // ── Matrix drawing (called by core render() when layout === 'matrix') ─────
  function drawMatrix(svgEl) {
    const dsm = ensureDsm();
    const { nodes, adj, n } = dsm;
    const svg = d3.select(svgEl);
    if (!n) {
      svg.append('text').attr('x', 20).attr('y', 30).attr('fill', '#a3b8a3')
        .attr('font-family', 'Space Mono, monospace').attr('font-size', 13).text('No nodes to draw.');
      return;
    }
    // An n×n matrix is n² cells; past a few hundred nodes it's both unreadable
    // and slow to draw. Steer the user to aggregate first rather than freeze.
    const MATRIX_MAX = 400;
    if (n > MATRIX_MAX) {
      const g0 = svg.append('g').attr('transform', 'translate(30,60)');
      g0.append('text').attr('fill', '#fbbf24').attr('font-family', 'Space Mono, monospace').attr('font-size', 15)
        .text('⚠️  ' + n + ' nodes is too many for a readable matrix.');
      ['A DSM works best on smaller, component-style networks.', 'Use the Aggregate card to collapse this network by a trait',
       '(e.g. region or tier) into a handful of groups, then switch to Matrix.'].forEach((line, i) => {
        g0.append('text').attr('y', 28 + i * 22).attr('fill', '#a3b8a3').attr('font-family', 'Space Mono, monospace').attr('font-size', 12).text(line);
      });
      return;
    }
    const stageW = svgEl.clientWidth || 620, stageH = svgEl.clientHeight || 620;
    const labelW = 112, labelH = 88;
    const gridMax = Math.max(40, Math.min(stageW - labelW - 14, stageH - labelH - 14));
    let cell = Math.floor(gridMax / n);
    cell = Math.max(6, Math.min(34, cell));
    curCell = cell;
    const gridW = n * cell, gridH = n * cell;
    const totalW = labelW + gridW, totalH = labelH + gridH;
    // Draw at the origin; a fit/center zoom transform (applied at the end, on a
    // fresh view) scales the whole matrix to fit the stage — essential on phones
    // where a big matrix would otherwise overflow off-screen. Users can still
    // zoom/pan afterward.
    const offX = 0, offY = 0;
    const fitScale = Math.min(1, (stageW - 10) / totalW, (stageH - 10) / totalH);
    // "Fresh" = no transform yet, or the identity transform the core sets when
    // you switch INTO matrix layout (which arrives as k=1/x=0/y=0, not null).
    const t0 = NV.state.zoomTransform;
    const freshView = !t0 || (Math.abs(t0.k - 1) < 1e-9 && t0.x === 0 && t0.y === 0);
    const root = svg.append('g').attr('class', 'viewport');
    if (t0 && !freshView) root.attr('transform', t0);

    const blocksOn = showBlocks && clusters.length === n;
    const showLabels = cell >= 11;

    // Cells
    for (let r = 0; r < n; r++) {
      for (let c = 0; c < n; c++) {
        const i = order[r], j = order[c];
        const x = offX + labelW + c * cell, y = offY + labelH + r * cell;
        let fill = 'rgba(5,46,22,0.5)';          // empty
        if (i === j) fill = '#6b8170';            // diagonal
        else if (adj[i][j]) {
          fill = '#39FF14';                        // dependency
          if (blocksOn && clusters[i] !== clusters[j]) fill = '#fbbf24'; // off-block mark (amber)
          if (cascadeSource !== null && cascadeSet.has(i) && (j === cascadeSource || cascadeSet.has(j))) fill = '#f97316'; // cascade
        }
        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('x', x); rect.setAttribute('y', y);
        rect.setAttribute('width', cell - 1); rect.setAttribute('height', cell - 1);
        rect.setAttribute('fill', fill);
        rect.setAttribute('stroke', '#050a05'); rect.setAttribute('stroke-width', '0.5');
        if (i !== j) { rect.style.cursor = 'pointer'; rect.addEventListener('click', () => selectComponent(j)); }
        root.node().appendChild(rect);
      }
    }
    // Cascade-source diagonal marker
    if (cascadeSource !== null) {
      const pos = order.indexOf(cascadeSource);
      if (pos >= 0) {
        const rr = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rr.setAttribute('x', offX + labelW + pos * cell); rr.setAttribute('y', offY + labelH + pos * cell);
        rr.setAttribute('width', cell - 1); rr.setAttribute('height', cell - 1);
        rr.setAttribute('fill', '#fbbf24'); rr.setAttribute('stroke', '#f0fdf4'); rr.setAttribute('stroke-width', '2');
        root.node().appendChild(rr);
      }
    }
    // Block boundaries
    if (blocksOn) {
      let start = 0;
      while (start < n) {
        let end = start;
        while (end + 1 < n && clusters[order[end + 1]] === clusters[order[start]]) end++;
        const rr = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rr.setAttribute('x', offX + labelW + start * cell); rr.setAttribute('y', offY + labelH + start * cell);
        rr.setAttribute('width', (end - start + 1) * cell - 1); rr.setAttribute('height', (end - start + 1) * cell - 1);
        rr.setAttribute('fill', 'none'); rr.setAttribute('stroke', '#818cf8');
        rr.setAttribute('stroke-width', '2'); rr.setAttribute('stroke-dasharray', '4 2');
        rr.style.pointerEvents = 'none';
        root.node().appendChild(rr);
        start = end + 1;
      }
    }
    // Labels (with drag-to-reorder)
    if (showLabels) {
      const zk = freshView ? fitScale : ((NV.state.zoomTransform && NV.state.zoomTransform.k) || 1);
      for (let c = 0; c < n; c++) {
        const i = order[c];
        const x = offX + labelW + c * cell + cell / 2, y = offY + labelH - 6;
        const t = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        t.setAttribute('x', x); t.setAttribute('y', y);
        t.setAttribute('transform', `rotate(-55 ${x} ${y})`);
        t.setAttribute('text-anchor', 'start'); t.setAttribute('font-size', Math.min(11, cell));
        t.setAttribute('font-family', 'Space Mono, monospace');
        t.setAttribute('fill', i === cascadeSource ? '#fbbf24' : cascadeSet.has(i) ? '#f97316' : '#a3b8a3');
        t.style.cursor = 'grab'; t.textContent = nodes[i].label;
        attachDrag(t, i, c, 'col', cell * zk);
        root.node().appendChild(t);
      }
      for (let r = 0; r < n; r++) {
        const i = order[r];
        const x = offX + labelW - 8, y = offY + labelH + r * cell + cell / 2 + 4;
        const t = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        t.setAttribute('x', x); t.setAttribute('y', y); t.setAttribute('text-anchor', 'end');
        t.setAttribute('font-size', Math.min(11, cell)); t.setAttribute('font-family', 'Space Mono, monospace');
        t.setAttribute('fill', i === cascadeSource ? '#fbbf24' : cascadeSet.has(i) ? '#f97316' : '#a3b8a3');
        t.style.cursor = 'grab'; t.textContent = nodes[i].label;
        attachDrag(t, i, r, 'row', cell * zk);
        root.node().appendChild(t);
      }
    }
    // On a fresh view, scale+center the whole matrix to fit the stage (via the
    // shared d3.zoom so the +/- buttons stay in sync). Big matrices shrink to
    // fit rather than overflowing off-screen on phones.
    if (freshView && NV.state.zoom) {
      const tx = Math.max(5, (stageW - totalW * fitScale) / 2);
      const ty = Math.max(5, (stageH - totalH * fitScale) / 2);
      d3.select(svgEl).call(NV.state.zoom.transform, d3.zoomIdentity.translate(tx, ty).scale(fitScale));
    }
  }

  // ── Drag-to-reorder (single shared drag state; document listeners once) ────
  let drag = null;
  function attachDrag(textEl, compIdx, pos, axis, screenCell) {
    textEl.addEventListener('mousedown', (e) => {
      e.preventDefault();
      drag = { compIdx, startPos: pos, axis, sx: e.clientX, sy: e.clientY, cell: screenCell || curCell, moved: false };
      textEl.style.cursor = 'grabbing';
    });
  }
  document.addEventListener('mousemove', (e) => {
    if (!drag) return;
    const n = order.length; if (!n) return;
    if (Math.abs(e.clientX - drag.sx) > 5 || Math.abs(e.clientY - drag.sy) > 5) drag.moved = true;
    const delta = drag.axis === 'row' ? (e.clientY - drag.sy) : (e.clientX - drag.sx);
    const newPos = Math.max(0, Math.min(n - 1, Math.round(drag.startPos + delta / drag.cell)));
    const cur = order.indexOf(drag.compIdx);
    if (newPos !== cur && cur >= 0) {
      order.splice(cur, 1); order.splice(newPos, 0, drag.compIdx);
      drag.startPos = newPos; drag.sx = e.clientX; drag.sy = e.clientY;
      NV.render(); renderCard();
    }
  });
  document.addEventListener('mouseup', () => {
    if (drag && !drag.moved) selectComponent(drag.compIdx);
    drag = null;
  });

  // ── The Clustering card ───────────────────────────────────────────────────
  function timeOptions() {
    const s = NV.state;
    if (!s.timeRange || !s.baseGraph) return '';
    const tcol = (s.mapping && s.mapping.time) || 'time';
    const vals = [...new Set(s.baseGraph.links.filter((l) => !l.isScenario).map((l) => l.timeRaw)
      .filter((v) => v !== null && v !== undefined && v !== ''))];
    vals.sort((a, b) => { const na = Number(a), nb = Number(b); return (isFinite(na) && isFinite(nb)) ? na - nb : String(a).localeCompare(String(b)); });
    if (timeSlice !== '' && !vals.some((v) => String(v) === String(timeSlice))) timeSlice = '';
    const opts = `<option value=""${timeSlice === '' ? ' selected' : ''}>(all ${esc(tcol)} — aggregate)</option>` +
      vals.map((v) => `<option value="${esc(v)}"${String(v) === String(timeSlice) ? ' selected' : ''}>${esc(tcol)} = ${esc(v)}</option>`).join('');
    return `<div class="color-by-row" style="margin-bottom:8px;"><label for="viz2-clust-slice">Time basis</label>
      <select id="viz2-clust-slice" class="viz-select">${opts}</select></div>`;
  }

  function renderCard() {
    injectStyle();
    const card = $('viz2-clustering-card'); if (!card) return;
    const host = card.querySelector('.card-body'); if (!host) return;
    const s = NV.state;
    if (!s.graph) { host.innerHTML = '<div class="node-empty">Load a network to enable clustering.</div>'; return; }

    const dsm = ensureDsm();
    const m = computeMetrics(dsm);
    const inMatrix = s.layout === 'matrix';

    // Selected-component options
    const compOpts = ['<option value="">— none —</option>']
      .concat(dsm.nodes.map((nd, i) => `<option value="${i}"${i === selectedIdx ? ' selected' : ''}>${esc(nd.label)}</option>`))
      .join('');

    // Subcard values
    let sub = '<div class="node-empty" style="padding:10px;">Pick a component (or click the matrix) to trace its failure cascade.</div>';
    if (selectedIdx !== null && selectedIdx < dsm.n) {
      let outDeg = 0, inDeg = 0;
      for (let j = 0; j < dsm.n; j++) { if (dsm.adj[selectedIdx][j]) outDeg++; if (dsm.adj[j][selectedIdx]) inDeg++; }
      const casc = cascadeSet.size;
      const pct = dsm.n > 1 ? Math.round(100 * casc / (dsm.n - 1)) : 0;
      const danger = casc >= Math.max(3, Math.ceil((dsm.n - 1) * 0.4));
      sub = `<div class="viz2-clust-substats">
        <div class="viz2-clust-sub"><div class="s-lbl">Depends on</div><div class="s-val">${outDeg}</div></div>
        <div class="viz2-clust-sub"><div class="s-lbl">Depended on by</div><div class="s-val">${inDeg}</div></div>
        <div class="viz2-clust-sub"><div class="s-lbl">Cascade if it fails</div><div class="s-val${danger ? ' bad' : ''}">${casc}</div></div>
        <div class="viz2-clust-sub"><div class="s-lbl">% of system</div><div class="s-val${danger ? ' bad' : ''}">${pct}%</div></div>
      </div>`;
    }

    const offClass = clusters.length ? (m.offBlock < m.deps * 0.4 ? '' : m.offBlock > m.deps * 0.6 ? ' bad' : ' warn') : '';

    host.innerHTML = `
      <p class="formula-note" style="margin:0 0 10px;">A dependency-structure matrix (DSM) with greedy-modularity clustering.
        Cell (row <em>i</em>, col <em>j</em>) is lit when <em>i</em> depends on <em>j</em>.
        <strong>Best for smaller, component-style networks</strong> — dense or giant graphs make an unreadable matrix.
        ${inMatrix ? '' : 'Switch the <strong>Layout</strong> to <strong>Matrix</strong> to see the DSM.'}</p>
      ${timeOptions()}
      <div class="viz2-clust-btnrow">
        <button id="viz2-clust-louvain" class="viz-btn viz-btn-primary">⚡ Cluster (Louvain)</button>
        <button id="viz2-clust-blocks" class="viz-btn">${showBlocks ? 'Hide' : 'Show'} block boundaries</button>
        <button id="viz2-clust-reset" class="viz-btn">Reset order</button>
        <button id="viz2-clust-clear" class="viz-btn">Clear cascade</button>
      </div>
      <div class="viz2-clust-stats">
        <div class="viz2-clust-tile"><div class="t-lbl">📦 Components</div><div class="t-val">${m.n}</div></div>
        <div class="viz2-clust-tile"><div class="t-lbl">🔗 Dependencies</div><div class="t-val">${m.deps}</div></div>
        <div class="viz2-clust-tile"><div class="t-lbl">📊 Coupling Density</div><div class="t-val">${(m.density * 100).toFixed(1)}%</div></div>
        <div class="viz2-clust-tile"><div class="t-lbl">🧩 Clusters Found</div><div class="t-val">${m.numClusters || '—'}</div></div>
        <div class="viz2-clust-tile"><div class="t-lbl">⚠️ Off-Block Marks</div><div class="t-val${offClass}">${clusters.length ? m.offBlock : '—'}</div></div>
        <div class="viz2-clust-tile"><div class="t-lbl">💥 Largest Cascade</div><div class="t-val">${m.largestCascade}</div></div>
      </div>
      <details class="viz2-nested-formulas" data-card="clust-selected" ${selectedIdx !== null ? 'open' : ''} style="margin-top:6px;">
        <summary>🎯 Selected Component</summary>
        <div style="padding-top:8px;">
          <div class="color-by-row" style="margin-bottom:8px;"><label for="viz2-clust-comp">Selected component</label>
            <select id="viz2-clust-comp" class="viz-select">${compOpts}</select></div>
          ${sub}
        </div>
      </details>
      <p class="formula-note" style="margin-top:10px;">Reproduce this in code from the <strong>Export as Code</strong> card below — tick <strong>🧩 Clustering (DSM)</strong> to weave it into the script.</p>`;

    // Wire controls
    const on = (id, ev, fn) => { const el = $(id); if (el) el.addEventListener(ev, fn); };
    on('viz2-clust-louvain', 'click', autoCluster);
    on('viz2-clust-blocks', 'click', toggleBlocks);
    on('viz2-clust-reset', 'click', resetOrder);
    on('viz2-clust-clear', 'click', clearCascade);
    on('viz2-clust-slice', 'change', (e) => { timeSlice = e.target.value; sig = ''; NV.render(); renderCard(); });
    on('viz2-clust-comp', 'change', (e) => { const v = e.target.value; if (v === '') clearCascade(); else selectComponent(parseInt(v, 10)); });
  }

  // Mapped column names for code export (reads NV.state.mapping).
  function exportCtx() {
    const s = NV.state;
    const map = s.mapping || {};
    const key = s.currentDatasetKey || null;
    return {
      key,
      nodesFile: key ? key + '-nodes.csv' : 'nodes.csv',
      edgesFile: key ? key + '-edges.csv' : 'edges.csv',
      fromCol: map.from || 'from',
      toCol: map.to || 'to',
      idCol: map.nodeId || 'node_id',
      slice: timeSlice,
      timeCol: (map.time || 'time'),
    };
  }
  const rStr = (s) => '"' + String(s).replace(/"/g, '\\"') + '"';
  const pyStr = (s) => '"' + String(s).replace(/"/g, '\\"') + '"';

  // Section-form code (woven into the comprehensive Export-as-Code script).
  // Assumes library(igraph) / imports + the `nodes`/`edges` data frames and the
  // pretty_section() helper already exist (the export card's setup provides them).
  // Builds its own DIRECTED graph `gc` so the DSM/cascade are meaningful.
  function exportSectionR() {
    const c = exportCtx(); const L = [];
    L.push('# Clustering (DSM) ###########################################################');
    L.push('');
    L.push('pretty_section("Clustering & DSM")');
    L.push('');
    L.push('# A DSM is directional (row depends on col), so build a directed graph.');
    L.push('edges_c <- edges[, c(' + rStr(c.fromCol) + ', ' + rStr(c.toCol) + ', setdiff(names(edges), c(' + rStr(c.fromCol) + ', ' + rStr(c.toCol) + ')))]');
    if (c.slice !== '') {
      L.push('# Clustering was run on a single time slice in the visualizer — match it here.');
      L.push('edges_c <- edges_c[edges_c[[' + rStr(c.timeCol) + ']] == ' + rStr(c.slice) + ', ]');
    }
    L.push('gc  <- igraph::graph_from_data_frame(edges_c, directed = TRUE, vertices = nodes)');
    L.push('# Louvain needs an undirected graph; collapse reciprocal edges first.');
    L.push('guc <- igraph::as_undirected(gc, mode = "collapse")');
    L.push('set.seed(5470)');
    L.push('lou_c <- igraph::cluster_louvain(guc)');
    L.push('cat(sprintf("🧩 Louvain found %d clusters (modularity %.3f)\\n", length(lou_c), igraph::modularity(lou_c)))');
    L.push('ord   <- order(lou_c$membership)');
    L.push('A     <- as.matrix(igraph::as_adjacency_matrix(gc))');
    L.push('image(t(A[ord, ord])[, nrow(A):1], col = c("white", "black"), axes = FALSE, main = "DSM — reordered by Louvain")');
    L.push('n_c <- igraph::gorder(gc); deps_c <- igraph::gsize(gc)');
    L.push('memb <- lou_c$membership; el <- igraph::as_edgelist(gc, names = FALSE)');
    L.push('cat(sprintf("📊 Coupling density: %.1f%%\\n", 100 * deps_c / (n_c * (n_c - 1))))');
    L.push('cat(sprintf("⚠️  Off-block marks: %d of %d dependencies\\n", sum(memb[el[, 1]] != memb[el[, 2]]), deps_c))');
    L.push('# Failure cascade: who fails if a component fails = everything that can reach');
    L.push('# it along dependency edges (mode = "in").');
    L.push('sizes <- sapply(igraph::V(gc), function(v) length(igraph::subcomponent(gc, v, mode = "in")) - 1)');
    L.push('cat(sprintf("💥 Largest cascade: %d components (from %s)\\n", max(sizes), igraph::V(gc)$name[which.max(sizes)]))');
    L.push('');
    return L.join('\n');
  }
  function exportSectionPy() {
    const c = exportCtx(); const L = [];
    L.push('# Clustering (DSM) ###########################################################');
    L.push('');
    L.push('pretty_section("Clustering & DSM")');
    L.push('');
    L.push('# A DSM is directional (row depends on col), so build a directed graph.');
    L.push('edges_c = edges[[' + pyStr(c.fromCol) + ', ' + pyStr(c.toCol) + '] + [x for x in edges.columns if x not in (' + pyStr(c.fromCol) + ', ' + pyStr(c.toCol) + ')]]');
    if (c.slice !== '') {
      L.push('# Clustering was run on a single time slice in the visualizer — match it here.');
      L.push('edges_c = edges_c[edges_c[' + pyStr(c.timeCol) + '].astype(str) == ' + pyStr(c.slice) + '].copy()');
    }
    L.push('gc = ig.Graph.DataFrame(edges_c, directed=True, vertices=nodes, use_vids=False)');
    L.push('guc = gc.as_undirected(mode="collapse")');
    L.push('import random as _rnd; _rnd.seed(5470)');
    L.push('lou_c = guc.community_multilevel()');
    L.push('print(f"🧩 Louvain found {len(lou_c)} clusters (modularity {lou_c.modularity:.3f})")');
    L.push('memb = np.array(lou_c.membership); order = np.argsort(memb, kind="stable")');
    L.push('A = np.array(gc.get_adjacency().data)');
    L.push('plt.imshow(A[np.ix_(order, order)], cmap="Greys"); plt.title("DSM — reordered by Louvain"); plt.axis("off"); plt.show()');
    L.push('n_c = gc.vcount(); deps_c = gc.ecount()');
    L.push('offblk = sum(1 for e in gc.es if memb[e.source] != memb[e.target])');
    L.push('print(f"📊 Coupling density: {100*deps_c/(n_c*(n_c-1)):.1f}%")');
    L.push('print(f"⚠️  Off-block marks: {offblk} of {deps_c} dependencies")');
    L.push('# Failure cascade: everything that can reach a component (mode="in").');
    L.push('sizes = [len(gc.subcomponent(v.index, mode="in")) - 1 for v in gc.vs]');
    L.push('w = int(np.argmax(sizes))');
    L.push('print(f"💥 Largest cascade: {sizes[w]} components (from {gc.vs[w][\'name\']})")');
    L.push('');
    return L.join('\n');
  }
  function exportSection(lang) { return lang === 'r' ? exportSectionR() : exportSectionPy(); }

  // ── Lifecycle ─────────────────────────────────────────────────────────────
  NV.on('graph-loaded', () => { sig = ''; renderCard(); });
  NV.on('view-rebuilt', () => { sig = ''; renderCard(); });
  NV.on('removed-changed', () => { sig = ''; renderCard(); });
  NV.on('scenario-changed', () => { sig = ''; renderCard(); });
  NV.on('node-selected', (p) => {
    // Sync selection from a graph node click, when that node is in the DSM.
    const dsm = ensureDsm(); const i = dsm.nodes.findIndex((x) => x.id === (p && p.id));
    if (i >= 0) { selectedIdx = i; cascadeSource = i; cascadeSet = computeCascade(dsm.adj, i); }
    renderCard();
  });

  window.NetSciVizClust = { drawMatrix, renderCard, exportSection };

  if (document.readyState !== 'loading') renderCard();
  else document.addEventListener('DOMContentLoaded', renderCard);
})();
