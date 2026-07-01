// ============================================================
// SYSEN 5470 — Network Visualizer v2 · Feature B: Node Removal
// Mounts: #viz2-selected-actions, #viz2-disruption-card .card-body
// Adds: remove/restore button on selected node, list of removed nodes,
// "Restore All" button, and a Disruption Stats card with active/comp/APL/diam.
// CRITICAL: removal must NOT trigger layout re-run (positions persist).
// We only mutate state.removedNodes, call computeMetrics(), updateNodePanel(),
// and render(). We never call layout(), unfix(), or touch state.simulation —
// so n.x / n.y / n.fx / n.fy stay byte-identical across remove/restore.
// ============================================================
(function () {
  'use strict';
  if (!window.NetSciViz2) return;

  const V = window.NetSciViz2;
  const state = V.state;
  const on = V.on, emit = V.emit;
  const utils = V.utils;

  // Baseline disruption stats — computed once per graph-loaded / view-rebuilt.
  // Avoids paying APL/diameter cost twice on every refresh.
  let baseline = null;

  // ── HTML escape (labels can contain &, <, ", etc.) ──────────
  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // ── APL + diameter + components on a given active-id set ────
  // Mean over reachable pairs only. If ANY pair is unreachable → ∞.
  // (Matches docs/case-studies/centrality.html convention.)
  function computeDisruption(activeIds) {
    const n = activeIds.length;
    if (n === 0) {
      return { active: 0, components: 0, apl: 0, diameter: 0, disconnected: false };
    }
    const idSet = new Set(activeIds);
    const adj = utils.buildAdj(state.graph, idSet);
    const { count: components } = utils.components(adj);

    let totalDist = 0;
    let reachablePairs = 0;
    let maxDist = 0;
    // Each ordered pair counted once via BFS-from-source; we sum t != s
    // distances and divide by reachablePairs (so each unordered pair
    // contributes twice to totalDist AND twice to reachablePairs — the
    // mean is the same as the unordered-pair mean).
    for (const s of activeIds) {
      const dist = utils.bfs(adj, s);
      for (const t of activeIds) {
        if (t === s) continue;
        const d = dist[t];
        if (d === Infinity) continue;
        totalDist += d;
        reachablePairs += 1;
        if (d > maxDist) maxDist = d;
      }
    }
    // ANY unreachable pair (excluding s==s) → disconnected.
    const expectedPairs = n * (n - 1);
    const disconnected = reachablePairs < expectedPairs;
    const apl = reachablePairs > 0 ? totalDist / reachablePairs : 0;
    return {
      active: n,
      components: components,
      apl: disconnected ? Infinity : apl,
      diameter: disconnected ? Infinity : maxDist,
      disconnected: disconnected
    };
  }

  // Compute baseline (no removals). Temporarily empties state.removedNodes
  // for the adjacency build, then restores. We do NOT call computeMetrics()
  // because that has the side-effect of mutating n.deg / n.weighted on the
  // graph nodes; baseline disruption only needs APL/diameter/components.
  function computeBaseline() {
    if (!state.graph) return null;
    const saved = state.removedNodes;
    state.removedNodes = new Set();
    const ids = state.graph.nodes
      .filter((nn) => !(state.dropIsolates && (state.metrics[nn.id]?.degree || 0) === 0))
      .map((nn) => nn.id);
    // For baseline, "active" means every node in the (un-removed) graph that
    // isn't a structural isolate under the current dropIsolates setting.
    // To stay faithful to the baseline regardless of removed-driven isolates,
    // include all non-isolate nodes ignoring removals.
    state.removedNodes = saved;
    return computeDisruption(ids);
  }

  function computeLive() {
    if (!state.graph) return null;
    const ids = V.activeNodes().map((nn) => nn.id);
    return computeDisruption(ids);
  }

  // ── Formatters ──────────────────────────────────────────────
  function fmtVal(v) {
    if (v === Infinity) return '∞ <span class="unit">(disconnected)</span>';
    if (typeof v === 'number' && !Number.isInteger(v)) return v.toFixed(2);
    return String(v);
  }

  // Render a delta cell comparing live to baseline.
  function fmtDelta(live, base, opts) {
    opts = opts || {};
    const intOnly = !!opts.intOnly;
    const bothInf = live === Infinity && base === Infinity;
    if (bothInf) return '<span class="mv delta-none">—</span>';
    if (live === Infinity && base !== Infinity) {
      return '<span class="mv delta-up">→ ∞</span>';
    }
    if (base === Infinity && live !== Infinity) {
      return '<span class="mv delta-down">↓ from ∞</span>';
    }
    const d = live - base;
    if (Math.abs(d) < (intOnly ? 0.5 : 0.005)) {
      return '<span class="mv delta-none">±0</span>';
    }
    const sign = d > 0 ? '+' : '';
    const txt = intOnly ? (sign + Math.round(d)) : (sign + d.toFixed(2));
    // For disruption metrics, "up" (worse — longer paths, more components) → orange,
    // "down" (better) → green. Active-nodes is the exception: down means damage.
    let cls;
    if (opts.invert) cls = d > 0 ? 'delta-down' : 'delta-up';
    else             cls = d > 0 ? 'delta-up'   : 'delta-down';
    return `<span class="mv ${cls}">${txt}</span>`;
  }

  // ── Selected-node remove/restore action ─────────────────────
  function renderSelectedActions() {
    const slot = document.getElementById('viz2-selected-actions');
    if (!slot) return;
    const id = state.selectedNode;
    if (!id || !state.graph) { slot.innerHTML = ''; return; }
    const n = state.graph.nodes.find((x) => x.id === id);
    if (!n) { slot.innerHTML = ''; return; }
    const isRemoved = state.removedNodes.has(id);
    const btnCls = isRemoved ? 'viz-btn viz-btn-ghost' : 'viz-btn viz-btn-danger';
    const btnTxt = isRemoved ? '➕ Restore node' : '➖ Remove from network';
    const hint = isRemoved
      ? 'Restoring keeps the node where it was — no layout re-run.'
      : 'Removing keeps coordinates pinned for before/after comparison.';
    // Selected-Edges dropdown + tabulation of edges by hop-distance from the
    // selected node. Hop classification is computed by computeSelectedHops();
    // the dropdown just picks which single depth to highlight (0 = None).
    const hopFocus = state.selectedHopFocus || 0;
    const counts   = state.selectedHopCounts || {};
    // Total active edges (excludes edges with a removed endpoint).
    let totalEdges = 0;
    state.graph.links.forEach((l) => {
      const s = typeof l.source === 'object' ? l.source.id : l.source;
      const t = typeof l.target === 'object' ? l.target.id : l.target;
      if (!state.removedNodes.has(s) && !state.removedNodes.has(t)) totalEdges++;
    });
    const hopOpts = [0, 1, 2, 3, 4, 5, 6].map((k) => {
      const label = k === 0 ? 'None' : (k + '° · ' + (counts[k] || 0) + ' edge' + ((counts[k] || 0) === 1 ? '' : 's'));
      return `<option value="${k}"${k === hopFocus ? ' selected' : ''}>${label}</option>`;
    }).join('');
    const rowsHtml = [1, 2, 3, 4, 5, 6].map((k) => {
      const c = counts[k] || 0;
      const pct = totalEdges > 0 ? (100 * c / totalEdges).toFixed(1) : '0.0';
      const activeCls = k === hopFocus ? ' style="color:#fef08a;"' : '';
      return `<div${activeCls}><span style="color:var(--grey-dim);">${k}°</span> ${c} <span style="color:var(--grey-dim);">(${pct}%)</span></div>`;
    }).join('');

    slot.innerHTML = `
      <div class="btn-row" style="margin-top: 10px;">
        <button class="${btnCls}" id="viz2-removal-toggle" style="flex:1;">${btnTxt}</button>
        <button class="viz-btn viz-btn-ghost" id="viz2-zoom-to-node" title="Zoom to this node + its 1st-degree neighbors">🔍 Zoom</button>
      </div>
      <div class="color-by-row" style="margin-top: 10px; margin-bottom: 0;">
        <label for="viz2-selected-hop">Selected Edges</label>
        <select id="viz2-selected-hop" class="viz-select">${hopOpts}</select>
      </div>
      <div style="display:grid; grid-template-columns:repeat(6, 1fr); gap:6px;
                  font-family: var(--font-mono); font-size: 10.5px;
                  color: var(--green-mint); margin-top: 6px;">
        ${rowsHtml}
      </div>
      <div style="font-family: var(--font-mono); font-size: 10px; color: var(--grey-dim);
                  line-height: 1.5; margin-top: 6px; letter-spacing: 0.04em;">
        ${esc(hint)}
      </div>`;
    const btn = document.getElementById('viz2-removal-toggle');
    if (btn) btn.addEventListener('click', () => toggleRemoval(id));
    const zoomBtn = document.getElementById('viz2-zoom-to-node');
    if (zoomBtn) zoomBtn.addEventListener('click', () => zoomToNode(id));
    const hopSel = document.getElementById('viz2-selected-hop');
    if (hopSel) hopSel.addEventListener('change', (e) => {
      state.selectedHopFocus = Number(e.target.value) || 0;
      renderSelectedActions();
      V.render();
    });
  }

  // Compute hop distances from `id` (BFS up to depth MAX_HOP) and classify
  // every active edge by max(dist(u), dist(v)). Cached in state so both the
  // tabulation and the render-time highlight can read the same map.
  const MAX_HOP = 6;
  function computeSelectedHops() {
    if (!state.graph || !state.selectedNode) {
      state.selectedHopByEdge = null;
      state.selectedHopCounts = null;
      return;
    }
    const id = state.selectedNode;
    // Active id set + BFS adjacency
    const activeIds = new Set();
    state.graph.nodes.forEach((n) => { if (!state.removedNodes.has(n.id)) activeIds.add(n.id); });
    if (!activeIds.has(id)) {
      state.selectedHopByEdge = null;
      state.selectedHopCounts = null;
      return;
    }
    const adj = Object.create(null);
    activeIds.forEach((nid) => { adj[nid] = []; });
    state.graph.links.forEach((l) => {
      const s = typeof l.source === 'object' ? l.source.id : l.source;
      const t = typeof l.target === 'object' ? l.target.id : l.target;
      if (!activeIds.has(s) || !activeIds.has(t)) return;
      adj[s].push(t); adj[t].push(s);
    });
    // BFS up to MAX_HOP
    const dist = Object.create(null);
    dist[id] = 0;
    const q = [id]; let qi = 0;
    while (qi < q.length) {
      const u = q[qi++];
      if (dist[u] >= MAX_HOP) continue;
      for (const v of adj[u]) {
        if (dist[v] === undefined) {
          dist[v] = dist[u] + 1;
          q.push(v);
        }
      }
    }
    // Classify each active edge by max(dist(u), dist(v)); an edge with either
    // endpoint further than MAX_HOP is unclassified and ignored.
    const byEdge = new Map();
    const counts = {}; for (let d = 1; d <= MAX_HOP; d++) counts[d] = 0;
    state.graph.links.forEach((l) => {
      const s = typeof l.source === 'object' ? l.source.id : l.source;
      const t = typeof l.target === 'object' ? l.target.id : l.target;
      if (!activeIds.has(s) || !activeIds.has(t)) return;
      const du = dist[s], dv = dist[t];
      if (du === undefined || dv === undefined) return;
      const d = Math.max(du, dv);
      if (d < 1 || d > MAX_HOP) return;
      byEdge.set(l, d);
      counts[d]++;
    });
    state.selectedHopByEdge = byEdge;
    state.selectedHopCounts = counts;
  }

  // Zoom the SVG viewport to fit the selected node + its FIRST-degree
  // neighbors (immediate neighbors only). Useful when the user picked a
  // row from Browse Nodes on a dense graph — they need a way to actually
  // SEE which dot got selected without pulling in half the network.
  function zoomToNode(id) {
    if (!state.graph || !state.zoom) return;
    const svgEl = document.getElementById('graph'); if (!svgEl) return;
    const W = svgEl.clientWidth, H = svgEl.clientHeight;

    // Collect id + every node it's directly connected to over the active
    // subgraph (removed nodes' edges are skipped). One pass, no BFS needed
    // for a 1-hop neighborhood.
    const ids = new Set([id]);
    state.graph.links.forEach((l) => {
      const s = typeof l.source === 'object' ? l.source.id : l.source;
      const t = typeof l.target === 'object' ? l.target.id : l.target;
      if (state.removedNodes.has(s) || state.removedNodes.has(t)) return;
      if (s === id) ids.add(t);
      else if (t === id) ids.add(s);
    });

    // Bounding box of those nodes' x/y; pad and fit.
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    state.graph.nodes.forEach((nn) => {
      if (!ids.has(nn.id)) return;
      if (!isFinite(nn.x) || !isFinite(nn.y)) return;
      if (nn.x < minX) minX = nn.x; if (nn.x > maxX) maxX = nn.x;
      if (nn.y < minY) minY = nn.y; if (nn.y > maxY) maxY = nn.y;
    });
    if (!isFinite(minX)) return;
    const pad = 80;
    const cw = Math.max(40, maxX - minX), ch = Math.max(40, maxY - minY);
    let scale = Math.min((W - 2 * pad) / cw, (H - 2 * pad) / ch);
    scale = Math.max(0.5, Math.min(scale, 4));
    const cx = (minX + maxX) / 2, cy = (minY + maxY) / 2;
    const d3sel = window.d3 ? window.d3.select(svgEl) : null;
    if (!d3sel) return;
    const t = window.d3.zoomIdentity.translate(W / 2 - scale * cx, H / 2 - scale * cy).scale(scale);
    d3sel.transition().duration(450).call(state.zoom.transform, t);
  }

  // The core mutation. CRITICAL: no layout(), no unfix(), no simulation touch.
  function toggleRemoval(id) {
    if (!state.graph) return;
    if (state.removedNodes.has(id)) state.removedNodes.delete(id);
    else state.removedNodes.add(id);
    V.computeMetrics();
    emit('removed-changed', { id, removed: state.removedNodes.has(id) });
    V.updateNodePanel();
    renderSelectedActions();
    renderDisruptionCard();
    V.render();
  }

  function restoreAll() {
    if (!state.graph || state.removedNodes.size === 0) return;
    state.removedNodes = new Set();
    V.computeMetrics();
    emit('removed-changed', { restoreAll: true });
    V.updateNodePanel();
    renderSelectedActions();
    renderDisruptionCard();
    V.render();
  }

  // ── Disruption Stats card ───────────────────────────────────
  function renderDisruptionCard() {
    const card = document.getElementById('viz2-disruption-card');
    if (!card) return;
    const body = card.querySelector('.card-body');
    if (!body) return;
    if (!state.graph) {
      body.innerHTML = '<div class="node-empty">Load a network to see disruption stats.</div>';
      return;
    }
    if (!baseline) baseline = computeBaseline();
    const live = computeLive();
    if (!baseline || !live) {
      body.innerHTML = '<div class="node-empty">Computing…</div>';
      return;
    }

    const rows = [
      { label: 'Active nodes',           base: baseline.active,     live: live.active,     intOnly: true,  invert: true },
      { label: 'Components',             base: baseline.components, live: live.components, intOnly: true,  invert: false },
      { label: 'Avg shortest path',      base: baseline.apl,        live: live.apl,        intOnly: false, invert: false },
      { label: 'Network diameter',       base: baseline.diameter,   live: live.diameter,   intOnly: true,  invert: false }
    ];

    const tableHtml = `
      <table class="group-table" style="margin-top: 4px;">
        <thead>
          <tr>
            <th>Metric</th>
            <th class="gv" style="text-align:right;">Original</th>
            <th class="gv" style="text-align:right;">Live</th>
            <th class="gv" style="text-align:right;">Δ</th>
          </tr>
        </thead>
        <tbody>
          ${rows.map((r) => `
            <tr>
              <td>${esc(r.label)}</td>
              <td class="gv" style="text-align:right;">${fmtVal(r.base)}</td>
              <td class="gv" style="text-align:right;">${fmtVal(r.live)}</td>
              <td class="gv" style="text-align:right;">${fmtDelta(r.live, r.base, { intOnly: r.intOnly, invert: r.invert })}</td>
            </tr>`).join('')}
        </tbody>
      </table>`;

    const removedIds = Array.from(state.removedNodes);
    const removedHtml = removedIds.length === 0
      ? `<div style="font-family: var(--font-mono); font-size: 10.5px; color: var(--grey-dim);
                    margin-top: 10px; letter-spacing: 0.04em;">
           No nodes removed yet. Click a node in the graph, then hit
           <span style="color:#fb923c;">➖ Remove from network</span>.
         </div>`
      : `<div style="margin-top: 12px;">
           <div style="font-family: var(--font-mono); font-size: 9.5px; color: var(--grey);
                       letter-spacing: 0.14em; text-transform: uppercase; margin-bottom: 6px;">
             Removed (${removedIds.length}) — click to restore
           </div>
           <div>${removedIds.map((id) => {
             const node = state.graph.nodes.find((x) => x.id === id);
             const label = node ? (node.label || node.id) : id;
             const short = String(label).length > 22 ? String(label).slice(0, 20) + '…' : label;
             return `<span class="removed-tag" data-id="${esc(id)}" title="${esc(label)} — click to restore">${esc(short)}</span>`;
           }).join('')}</div>
           <div class="btn-row" style="margin-top: 10px;">
             <button class="viz-btn viz-btn-ghost" id="viz2-restore-all" style="flex:1;">🔄 Restore All</button>
           </div>
         </div>`;

    const warnHtml = live.disconnected
      ? `<div class="warn" style="margin-top: 10px;">
           ⚠ Network is fragmented — some pairs are unreachable, so APL and diameter are ∞.
         </div>`
      : '';

    body.innerHTML = tableHtml + warnHtml + removedHtml;

    // Wire restore-tag clicks
    body.querySelectorAll('.removed-tag').forEach((tag) => {
      tag.addEventListener('click', () => {
        const id = tag.getAttribute('data-id');
        if (id) toggleRemoval(id);
      });
    });
    const restoreBtn = document.getElementById('viz2-restore-all');
    if (restoreBtn) restoreBtn.addEventListener('click', restoreAll);
  }

  // ── Event wiring ────────────────────────────────────────────
  // Cache baseline only when the underlying graph / view changes, not on
  // every removal toggle.
  on('graph-loaded', () => {
    state.removedNodes = new Set();
    state.selectedHopFocus = 0;  // reset the Selected-Edges dropdown too
    baseline = null;             // force recompute on next render
    computeSelectedHops();
    renderSelectedActions();
    renderDisruptionCard();
  });
  on('view-rebuilt', () => {
    baseline = null;             // aggregation / group-col / threshold may shift things
    computeSelectedHops();
    renderSelectedActions();
    renderDisruptionCard();
  });
  on('node-selected', () => {
    computeSelectedHops();       // BFS from the newly-selected node
    renderSelectedActions();
    // if the user had a Selected-Edges depth focus set, the render also needs
    // the new hop map — the caller (viz2-core's click handler) already calls
    // render(), so we don't need to re-render here.
  });
  on('removed-changed', () => {
    computeSelectedHops();       // active subgraph changed → reclassify edges
    renderSelectedActions();
  });
  // metrics-updated fires from computeMetrics(). If WE triggered it via
  // toggleRemoval, the disruption card was already re-rendered. But weight
  // toggles or other callers also fire metrics-updated, so refresh the
  // baseline-dependent card view here.
  on('metrics-updated', () => {
    if (!state.graph) return;
    renderDisruptionCard();
  });

  // Initial paint (in case graph already loaded before this module attached)
  if (state.graph) {
    renderSelectedActions();
    renderDisruptionCard();
  }
})();
