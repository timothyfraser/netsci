// ============================================================
// SYSEN 5470 — Network Visualizer v2 · Feature D2: Monte Carlo Sim
// Mounts: #viz2-montecarlo-card .card-body
// Poisson-resamples edge weights and reports a 95% CI on the chosen
// metric. Mirrors the procedure in code/07_counterfactual/example.R
// and the chunked runner in docs/case-studies/counterfactual.html.
// Metrics: graph-level (APL hops, APL weighted, diameter, worst-
// served weighted) and node-level (degree, weighted degree,
// betweenness) when a node is selected.
// ============================================================
(function () {
  'use strict';
  if (!window.NetSciViz2) return;
  const NV = window.NetSciViz2;

  const $  = (id) => document.getElementById(id);
  const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
                              .replace(/>/g, '&gt;').replace(/"/g, '&quot;');

  // ── Metric registry ─────────────────────────────────────────
  // Each entry: { label, scope: 'graph'|'node', compute(adj, ids, opts) }.
  // `adj` is built by NV.utils.buildAdj over the active id set; `ids` is
  // the array form. opts carries { selectedNode } for node-level metrics.
  const METRICS = {
    apl_hops: {
      label: 'Avg path length (hops)',
      scope: 'graph',
      compute(adj, ids) {
        let sum = 0, count = 0;
        ids.forEach((s) => {
          const d = NV.utils.bfs(adj, s);
          ids.forEach((t) => {
            if (t === s) return;
            const v = d[t];
            if (isFinite(v)) { sum += v; count++; }
          });
        });
        return count ? sum / count : Infinity;
      }
    },
    apl_weighted: {
      label: 'Avg path length (weighted, cost = 1/w)',
      scope: 'graph',
      compute(adj, ids) {
        let sum = 0, count = 0;
        ids.forEach((s) => {
          const d = NV.utils.dijkstraInvWeight(adj, s);
          ids.forEach((t) => {
            if (t === s) return;
            const v = d[t];
            if (isFinite(v)) { sum += v; count++; }
          });
        });
        return count ? sum / count : Infinity;
      }
    },
    diameter_hops: {
      label: 'Network diameter (hops)',
      scope: 'graph',
      compute(adj, ids) {
        let mx = 0;
        ids.forEach((s) => {
          const d = NV.utils.bfs(adj, s);
          ids.forEach((t) => {
            if (t === s) return;
            const v = d[t];
            if (isFinite(v) && v > mx) mx = v;
          });
        });
        return mx;
      }
    },
    worst_served_weighted: {
      label: 'Worst-served node distance (weighted)',
      scope: 'graph',
      compute(adj, ids) {
        let worst = 0;
        ids.forEach((s) => {
          const d = NV.utils.dijkstraInvWeight(adj, s);
          let sum = 0, count = 0;
          ids.forEach((t) => {
            if (t === s) return;
            const v = d[t];
            if (isFinite(v)) { sum += v; count++; }
          });
          const mean = count ? sum / count : Infinity;
          if (isFinite(mean) && mean > worst) worst = mean;
        });
        return worst;
      }
    },
    node_degree: {
      label: 'Selected node — degree (count)',
      scope: 'node',
      compute(adj, ids, opts) {
        const nid = opts.selectedNode;
        return (adj[nid] || []).length;
      }
    },
    node_wdegree: {
      label: 'Selected node — weighted degree (Σw)',
      scope: 'node',
      compute(adj, ids, opts) {
        const nid = opts.selectedNode;
        let s = 0;
        (adj[nid] || []).forEach((e) => { s += e.w; });
        return s;
      }
    },
    node_betweenness: {
      label: 'Selected node — betweenness (normalized)',
      scope: 'node',
      compute(adj, ids, opts) {
        // Brandes' unweighted BFS-based betweenness; normalize by (N-1)(N-2).
        // Only return the score for the selected node — runs every replicate.
        const nid = opts.selectedNode;
        const N = ids.length;
        if (N < 3 || !adj[nid]) return 0;
        let betw = 0;
        for (const s of ids) {
          const stack = [], pred = Object.create(null), sigma = Object.create(null), dist = Object.create(null);
          ids.forEach((id) => { pred[id] = []; sigma[id] = 0; dist[id] = -1; });
          sigma[s] = 1; dist[s] = 0;
          const q = [s]; let qi = 0;
          while (qi < q.length) {
            const v = q[qi++]; stack.push(v);
            for (const { to } of adj[v]) {
              if (dist[to] < 0) { q.push(to); dist[to] = dist[v] + 1; }
              if (dist[to] === dist[v] + 1) { sigma[to] += sigma[v]; pred[to].push(v); }
            }
          }
          const delta = Object.create(null); ids.forEach((id) => { delta[id] = 0; });
          while (stack.length) {
            const w = stack.pop();
            pred[w].forEach((v) => { delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w]); });
            if (w !== s && w === nid) betw += delta[w];
          }
        }
        const norm = (N - 1) * (N - 2);
        return norm > 0 ? betw / norm : 0;
      }
    }
  };

  // ── Local UI state ──────────────────────────────────────────
  let chosenMetric = 'apl_weighted';
  let replicates   = 100;
  let running      = false;

  // ── Helpers ─────────────────────────────────────────────────
  function activeIdsArray() {
    const s = NV.state;
    if (!s.graph) return [];
    const out = [];
    s.graph.nodes.forEach((n) => { if (!s.removedNodes.has(n.id)) out.push(n.id); });
    return out;
  }

  // Build a synthetic graph with Poisson-perturbed link weights. Endpoints
  // and node list are reused (no need to clone); only weight is jittered.
  // Clamp to ≥1 to keep Dijkstra (cost = 1/w) sane — exactly the same
  // safeguard the counterfactual code uses (max(1, rpois(w))).
  function perturbGraph(graph) {
    const links = graph.links.map((l) => {
      const w = l.weight || 0;
      if (w <= 0) return { source: l.source, target: l.target, weight: 0 };
      return { source: l.source, target: l.target, weight: Math.max(1, NV.utils.poisson(w)) };
    });
    return { nodes: graph.nodes, links };
  }

  function fmt(v) {
    if (!isFinite(v)) return '∞';
    if (Math.abs(v) >= 1000) return v.toFixed(1);
    if (Math.abs(v) >= 10)   return v.toFixed(2);
    return v.toFixed(4);
  }

  // ── Card render ─────────────────────────────────────────────
  function render() {
    const card = $('viz2-montecarlo-card'); if (!card) return;
    const host = card.querySelector('.card-body'); if (!host) return;
    const s = NV.state;
    if (!s.graph) {
      host.innerHTML = '<div class="node-empty">Load a network to enable Monte Carlo.</div>';
      return;
    }

    const sel = s.selectedNode;
    const opts = Object.keys(METRICS).map((k) => {
      const m = METRICS[k];
      const needsNode = m.scope === 'node';
      const disabled  = needsNode && !sel;
      const label = needsNode && !sel ? `${m.label} (select a node)` : m.label;
      return `<option value="${k}"${disabled ? ' disabled' : ''}${k === chosenMetric ? ' selected' : ''}>${esc(label)}</option>`;
    }).join('');

    // If user previously picked a node-scoped metric and then deselected the
    // node, silently fall back to the weighted APL graph metric so the run
    // button isn't pointing at a disabled option.
    if (METRICS[chosenMetric].scope === 'node' && !sel) {
      chosenMetric = 'apl_weighted';
    }

    host.innerHTML = `
      <div class="color-by-row" style="margin-bottom:8px;">
        <label for="viz2-mc-metric">Metric</label>
        <select id="viz2-mc-metric" class="viz-select">${opts}</select>
      </div>
      <div class="color-by-row" style="margin-bottom:4px;">
        <label for="viz2-mc-reps"># replicates</label>
        <input type="number" id="viz2-mc-reps" class="viz-select"
               min="20" max="2000" step="10" value="${replicates}"
               style="width:90px;">
      </div>
      <div class="warn">100 is fine for a quick check; ≥500 ideally 1000 for a publishable CI.</div>
      <div style="display:flex; gap:8px; align-items:center; margin-top:6px;">
        <button id="viz2-mc-run" class="viz-btn">🎲 Run Monte Carlo</button>
        <div id="viz2-mc-status" class="formula-note" style="margin:0;flex:1;"></div>
      </div>
      <svg class="dist" id="viz2-mc-svg"></svg>
      <div id="viz2-mc-summary" class="formula-note" style="margin-top:4px;"></div>
      <div class="formula-note" style="margin-top:2px;">
        Poisson(λ = observed weight) per edge, ${replicates} replicates,
        95% CI = quantiles [0.025, 0.975]. Matches code/07_counterfactual.
      </div>`;

    $('viz2-mc-metric').addEventListener('change', (e) => { chosenMetric = e.target.value; });
    $('viz2-mc-reps').addEventListener('change', (e) => {
      const v = Math.max(20, Math.min(2000, Math.round(+e.target.value || 100)));
      replicates = v; e.target.value = v;
    });
    $('viz2-mc-run').addEventListener('click', run);
  }

  // ── Histogram ───────────────────────────────────────────────
  function drawHistogram(samples, observed, qLo, qHi) {
    const svg = $('viz2-mc-svg'); if (!svg) return;
    svg.innerHTML = '';
    if (!samples.length) return;
    const W = svg.clientWidth || 320, H = svg.clientHeight || 160;
    const mL = 8, mR = 8, mT = 8, mB = 16;
    const finite = samples.filter(isFinite);
    if (!finite.length) return;

    // Pad the domain so vertical reference lines stay inside the view.
    let lo = Math.min(...finite, observed, qLo);
    let hi = Math.max(...finite, observed, qHi);
    if (lo === hi) { lo -= 1; hi += 1; }
    const pad = (hi - lo) * 0.04;
    lo -= pad; hi += pad;

    const x = d3.scaleLinear().domain([lo, hi]).range([mL, W - mR]);
    const binner = d3.bin().domain([lo, hi]).thresholds(24);
    const bins = binner(finite);
    const maxC = d3.max(bins, (b) => b.length) || 1;
    const y = d3.scaleLinear().domain([0, maxC]).range([H - mB, mT]);

    const root = d3.select(svg);
    root.append('g').selectAll('rect').data(bins).enter().append('rect')
      .attr('x', (b) => x(b.x0) + 0.5)
      .attr('y', (b) => y(b.length))
      .attr('width', (b) => Math.max(0, x(b.x1) - x(b.x0) - 1))
      .attr('height', (b) => (H - mB) - y(b.length))
      .attr('fill', 'rgba(57,255,20,0.55)')
      .attr('stroke', '#39FF14').attr('stroke-opacity', 0.6);

    const vline = (xv, color, dash, label) => {
      const xp = x(xv);
      root.append('line')
        .attr('x1', xp).attr('x2', xp).attr('y1', mT).attr('y2', H - mB)
        .attr('stroke', color).attr('stroke-width', 1.4)
        .attr('stroke-dasharray', dash || null);
      root.append('text')
        .attr('x', xp + 3).attr('y', mT + 9)
        .attr('font-family', 'Space Mono, monospace').attr('font-size', '9px')
        .attr('fill', color).text(label);
    };
    if (isFinite(qLo))     vline(qLo,     '#fbbf24', '3,2', '2.5%');
    if (isFinite(qHi))     vline(qHi,     '#fbbf24', '3,2', '97.5%');
    if (isFinite(observed)) vline(observed,'#f472b6', null,  'obs');

    // Axis: just min / max ticks to stay terse.
    root.append('text').attr('x', mL).attr('y', H - 4)
      .attr('font-family', 'Space Mono, monospace').attr('font-size', '9px')
      .attr('fill', '#6b7280').text(fmt(lo));
    root.append('text').attr('x', W - mR).attr('y', H - 4).attr('text-anchor', 'end')
      .attr('font-family', 'Space Mono, monospace').attr('font-size', '9px')
      .attr('fill', '#6b7280').text(fmt(hi));
  }

  // ── Run the simulation (chunked, yields every 25 reps) ──────
  async function run() {
    if (running) return;
    const s = NV.state;
    if (!s.graph) return;
    const ids = activeIdsArray();
    if (ids.length < 2) {
      $('viz2-mc-status').textContent = 'Need ≥ 2 active nodes.';
      return;
    }
    const metric = METRICS[chosenMetric];
    if (!metric) return;
    if (metric.scope === 'node' && !s.selectedNode) {
      $('viz2-mc-status').textContent = 'Select a node first.';
      return;
    }

    running = true;
    const btn = $('viz2-mc-run'); if (btn) btn.disabled = true;
    const statusEl = $('viz2-mc-status');
    const idSet = new Set(ids);
    const R = replicates;
    const samples = [];
    const opts = { selectedNode: s.selectedNode };

    // Observed = same metric on the unperturbed graph (no Poisson draw).
    const observedAdj = NV.utils.buildAdj(s.graph, idSet);
    const observed = metric.compute(observedAdj, ids, opts);

    const t0 = performance.now();
    let i = 0;
    const BATCH = 25;
    while (i < R) {
      const end = Math.min(i + BATCH, R);
      for (; i < end; i++) {
        const perturbed = perturbGraph(s.graph);
        const adj = NV.utils.buildAdj(perturbed, idSet);
        samples.push(metric.compute(adj, ids, opts));
      }
      if (statusEl) statusEl.textContent = `Running… ${i}/${R}`;
      // Yield to the event loop so the page stays responsive (same trick
      // the counterfactual case study uses for its 500-rep batch runner).
      await new Promise((r) => setTimeout(r, 0));
    }

    const finite = samples.filter(isFinite);
    const mean = finite.length ? finite.reduce((a, b) => a + b, 0) / finite.length : NaN;
    const qLo = NV.utils.quantile(samples, 0.025);
    const qHi = NV.utils.quantile(samples, 0.975);
    const dtMs = Math.round(performance.now() - t0);

    drawHistogram(samples, observed, qLo, qHi);
    const summary = $('viz2-mc-summary');
    if (summary) {
      summary.innerHTML = `<strong style="color:#d1fae5;">Observed = ${fmt(observed)} · Mean = ${fmt(mean)} · 95% CI = [${fmt(qLo)}, ${fmt(qHi)}]</strong>`;
    }
    if (statusEl) statusEl.textContent = `Done — ${R} reps in ${(dtMs / 1000).toFixed(1)}s · metric: ${metric.label}`;

    running = false;
    if (btn) btn.disabled = false;
  }

  // ── Lifecycle wiring ────────────────────────────────────────
  // Re-render the card whenever the active subgraph, selection, or
  // removal set changes — those flip which metrics are eligible.
  NV.on('graph-loaded',    render);
  NV.on('view-rebuilt',    render);
  NV.on('node-selected',   render);
  NV.on('removed-changed', render);

  if (document.readyState !== 'loading') render();
  else document.addEventListener('DOMContentLoaded', render);
})();
