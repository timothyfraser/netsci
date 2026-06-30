// ============================================================
// SYSEN 5470 — Network Visualizer v2 · Feature D2: Monte Carlo Sim
// Mounts: #viz2-montecarlo-card .card-body
// Poisson-resamples edge weights on BOTH a baseline graph (raw load,
// no scenarios, no removals) and the live "treated" graph (scenarios +
// removals applied), then reports their per-replicate difference + 95%
// CI. Mirrors code/07_counterfactual/example.R and the chunked dual-
// histogram pattern in docs/case-studies/counterfactual.html.
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

  // Brand palette (match counterfactual.html dual histogram).
  const COLOR_BASE  = '#818cf8';   // indigo — baseline distribution
  const COLOR_TREAT = '#39FF14';   // neon green — treated distribution
  const COLOR_DIFF  = '#fbbf24';   // amber — difference distribution + CI lines
  const COLOR_OBS   = '#f472b6';   // pink — observed (unperturbed) reference

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
  let timeSlice    = '';           // '' = all time
  let running      = false;

  // ── Shared tooltip (Change 4) ───────────────────────────────
  // One DIV in <body>, reused for every chart hover. Mono font + neon-
  // green border matches the rest of the visualizer.
  let tipEl = null;
  function ensureTooltip() {
    if (tipEl) return tipEl;
    tipEl = document.createElement('div');
    tipEl.id = 'viz2-mc-tooltip';
    tipEl.style.cssText = [
      'position:fixed', 'pointer-events:none', 'z-index:9999',
      'display:none', 'padding:6px 8px', 'border-radius:4px',
      'background:rgba(5,10,5,0.92)', 'border:1px solid #39FF14',
      'color:#d1fae5', 'font:11px "Space Mono", monospace',
      'box-shadow:0 4px 12px rgba(0,0,0,0.5)', 'max-width:240px'
    ].join(';');
    document.body.appendChild(tipEl);
    return tipEl;
  }
  function showTip(html, ev) {
    const el = ensureTooltip();
    el.innerHTML = html;
    el.style.display = 'block';
    const pad = 12;
    let x = ev.clientX + pad, y = ev.clientY + pad;
    // Keep on-screen — flip if we'd run off the right/bottom edge.
    const r = el.getBoundingClientRect();
    if (x + r.width  > window.innerWidth)  x = ev.clientX - r.width  - pad;
    if (y + r.height > window.innerHeight) y = ev.clientY - r.height - pad;
    el.style.left = x + 'px'; el.style.top = y + 'px';
  }
  function hideTip() { if (tipEl) tipEl.style.display = 'none'; }

  // ── Helpers ─────────────────────────────────────────────────
  // Build the BASELINE graph: raw loaded data, scenario items stripped,
  // removed nodes IGNORED (baseline is the unperturbed world).
  function buildBaselineGraph() {
    const s = NV.state;
    if (!s.baseGraph) return null;
    const nodes = s.baseGraph.nodes
      .filter((n) => !n.isScenario)
      .map((n) => ({ id: n.id, label: n.label, group: n.group }));
    const validIds = new Set(nodes.map((n) => n.id));
    const links = s.baseGraph.links
      .filter((l) => !l.isScenario)
      .filter((l) => timeSlice === '' || String(l.timeRaw) === String(timeSlice))
      .map((l) => {
        const src = typeof l.source === 'object' ? l.source.id : l.source;
        const tgt = typeof l.target === 'object' ? l.target.id : l.target;
        return { source: src, target: tgt, weight: l.weight || 0 };
      })
      .filter((l) => validIds.has(l.source) && validIds.has(l.target));
    return { nodes, links };
  }

  // Build the TREATED graph: live state.graph with scenarios applied,
  // minus removed nodes. Also honors the time-slice dropdown.
  function buildTreatedGraph() {
    const s = NV.state;
    if (!s.graph) return null;
    const removed = s.removedNodes;
    const nodes = s.graph.nodes
      .filter((n) => !removed.has(n.id))
      .map((n) => ({ id: n.id, label: n.label, group: n.group }));
    const validIds = new Set(nodes.map((n) => n.id));
    const links = s.graph.links
      .filter((l) => {
        if (timeSlice === '' || l.isScenario) return true; // scenarios have no time
        return String(l.timeRaw) === String(timeSlice);
      })
      .map((l) => {
        const src = typeof l.source === 'object' ? l.source.id : l.source;
        const tgt = typeof l.target === 'object' ? l.target.id : l.target;
        return { source: src, target: tgt, weight: l.weight || 0 };
      })
      .filter((l) => validIds.has(l.source) && validIds.has(l.target));
    return { nodes, links };
  }

  // Are baseline and treated graphs equivalent? Same node ids + same
  // edge multiset (by endpoint pair + weight). If so we skip dual mode.
  function graphsEquivalent(a, b) {
    if (!a || !b) return false;
    if (a.nodes.length !== b.nodes.length) return false;
    if (a.links.length !== b.links.length) return false;
    const aIds = new Set(a.nodes.map((n) => n.id));
    for (const n of b.nodes) if (!aIds.has(n.id)) return false;
    const key = (l) => {
      const lo = l.source < l.target ? l.source : l.target;
      const hi = l.source < l.target ? l.target : l.source;
      return lo + '|' + hi + '|' + l.weight;
    };
    const aBag = new Map();
    a.links.forEach((l) => { const k = key(l); aBag.set(k, (aBag.get(k) || 0) + 1); });
    for (const l of b.links) {
      const k = key(l); const c = aBag.get(k);
      if (!c) return false;
      if (c === 1) aBag.delete(k); else aBag.set(k, c - 1);
    }
    return aBag.size === 0;
  }

  // Poisson-jitter every positive weight; clamp to ≥1 so Dijkstra
  // (cost = 1/w) stays sane. Mirrors max(1, rpois(w)) from R.
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
  function signedFmt(v) {
    if (!isFinite(v)) return '∞';
    const s = fmt(Math.abs(v));
    return (v >= 0 ? '+' : '−') + s;
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
    // If user previously picked a node-scoped metric and then deselected the
    // node, silently fall back to the weighted APL graph metric so the run
    // button isn't pointing at a disabled option.
    if (METRICS[chosenMetric].scope === 'node' && !sel) {
      chosenMetric = 'apl_weighted';
    }
    const opts = Object.keys(METRICS).map((k) => {
      const m = METRICS[k];
      const needsNode = m.scope === 'node';
      const disabled  = needsNode && !sel;
      const label = needsNode && !sel ? `${m.label} (select a node)` : m.label;
      return `<option value="${k}"${disabled ? ' disabled' : ''}${k === chosenMetric ? ' selected' : ''}>${esc(label)}</option>`;
    }).join('');

    // Change 2: temporal slice options — only if the loaded graph has a time column.
    let timeRowHtml = '';
    if (s.timeRange && s.baseGraph) {
      const tcol = s.mapping.time || 'time';
      const vals = [...new Set(s.baseGraph.links
        .filter((l) => !l.isScenario)
        .map((l) => l.timeRaw)
        .filter((v) => v !== null && v !== undefined && v !== ''))];
      vals.sort((a, b) => {
        const na = Number(a), nb = Number(b);
        return (isFinite(na) && isFinite(nb)) ? na - nb : String(a).localeCompare(String(b));
      });
      // Drop stale slice value if the underlying graph changed.
      if (timeSlice !== '' && !vals.some((v) => String(v) === String(timeSlice))) timeSlice = '';
      const tOpts = `<option value=""${timeSlice === '' ? ' selected' : ''}>(all ${esc(tcol)})</option>` +
        vals.map((v) => `<option value="${esc(v)}"${String(v) === String(timeSlice) ? ' selected' : ''}>${esc(tcol)} = ${esc(v)}</option>`).join('');
      timeRowHtml = `
        <div class="color-by-row" style="margin-bottom:8px;">
          <label for="viz2-mc-slice">Time slice</label>
          <select id="viz2-mc-slice" class="viz-select">${tOpts}</select>
        </div>`;
    }

    // Tech-note tooltip — what we previously inlined as a wall of text.
    const methodTip = 'Monte Carlo: each replicate Poisson-resamples every edge weight from Poisson(λ = observed) and recomputes the metric on BOTH the baseline (raw) and treated (scenarios + removals) graphs. 95% CI on Δ = quantiles [0.025, 0.975] of (treated − baseline). Mirrors code/07_counterfactual/example.R.';

    host.innerHTML = `
      <div class="formula-note" style="margin:0 0 8px;">
        <strong style="color:var(--green-bright);">Monte Carlo simulation</strong>
        <span class="viz2-info-icon" title="${esc(methodTip)}" aria-label="Method details">ⓘ</span>
        — re-runs the metric on weight-perturbed networks to bracket its uncertainty, comparing baseline vs treated.
      </div>
      <div class="color-by-row" style="margin-bottom:8px;">
        <label for="viz2-mc-metric">Metric</label>
        <select id="viz2-mc-metric" class="viz-select">${opts}</select>
      </div>
      ${timeRowHtml}
      <div class="color-by-row" style="margin-bottom:8px;">
        <label for="viz2-mc-reps"># replicates</label>
        <select id="viz2-mc-reps" class="viz-select">
          <option value="100"${replicates === 100  ? ' selected' : ''}>100 (quick check)</option>
          <option value="500"${replicates === 500  ? ' selected' : ''}>500 (solid)</option>
          <option value="1000"${replicates === 1000 ? ' selected' : ''}>1000 (publishable)</option>
        </select>
      </div>
      <div style="display:flex; gap:8px; align-items:center; margin-top:6px;">
        <button id="viz2-mc-run" class="viz-btn">🎲 Run</button>
        <div id="viz2-mc-status" class="formula-note" style="margin:0;flex:1;"></div>
      </div>
      <div id="viz2-mc-chart-wrap" style="position:relative; margin-top:4px;">
        <button id="viz2-mc-png" class="viz-zoom-btn"
                style="position:absolute; top:4px; right:4px; width:24px; height:24px; font-size:13px; z-index:2;"
                title="Download chart as PNG" aria-label="Download chart as PNG">💾</button>
        <svg class="dist" id="viz2-mc-svg-dist"></svg>
        <svg class="dist" id="viz2-mc-svg-diff" style="display:none;"></svg>
      </div>
      <div id="viz2-mc-summary" class="formula-note" style="margin-top:4px;"></div>
      <div id="viz2-mc-hint" class="formula-note" style="margin-top:4px; color:#fbbf24; display:none;"></div>`;

    $('viz2-mc-metric').addEventListener('change', (e) => { chosenMetric = e.target.value; });
    $('viz2-mc-reps').addEventListener('change', (e) => {
      const v = parseInt(e.target.value, 10);
      if (v === 100 || v === 500 || v === 1000) replicates = v;
    });
    const slice = $('viz2-mc-slice');
    if (slice) slice.addEventListener('change', (e) => { timeSlice = e.target.value; });
    $('viz2-mc-run').addEventListener('click', run);
    $('viz2-mc-png').addEventListener('click', exportChartPng);
  }

  // ── Histogram (dual or single) ──────────────────────────────
  // mode='single' draws only `baseline`; mode='dual' overlays baseline + treated.
  function drawDistribution(svgId, mode, baseline, treated, observed, refLines) {
    const svg = $(svgId); if (!svg) return;
    svg.innerHTML = '';
    const baseFinite    = (baseline || []).filter(isFinite);
    const treatedFinite = (treated  || []).filter(isFinite);
    if (!baseFinite.length && !treatedFinite.length) return;

    const W = svg.clientWidth || 320, H = svg.clientHeight || 160;
    const mL = 8, mR = 8, mT = 8, mB = 16;

    const all = baseFinite.concat(treatedFinite);
    let lo = Math.min(...all, isFinite(observed) ? observed : Infinity);
    let hi = Math.max(...all, isFinite(observed) ? observed : -Infinity);
    (refLines || []).forEach((r) => {
      if (isFinite(r.x)) { lo = Math.min(lo, r.x); hi = Math.max(hi, r.x); }
    });
    if (!isFinite(lo) || !isFinite(hi) || lo === hi) { lo = (lo || 0) - 1; hi = (hi || 0) + 1; }
    const pad = (hi - lo) * 0.04;
    lo -= pad; hi += pad;

    const x = d3.scaleLinear().domain([lo, hi]).range([mL, W - mR]);
    const binner = d3.bin().domain([lo, hi]).thresholds(24);
    const baseBins    = baseFinite.length    ? binner(baseFinite)    : [];
    const treatedBins = treatedFinite.length ? binner(treatedFinite) : [];
    const maxC = Math.max(
      d3.max(baseBins,    (b) => b.length) || 0,
      d3.max(treatedBins, (b) => b.length) || 0,
      1
    );
    const y = d3.scaleLinear().domain([0, maxC]).range([H - mB, mT]);

    const root = d3.select(svg);

    const drawBars = (bins, fill, stroke, kind) => {
      root.append('g').selectAll('rect').data(bins).enter().append('rect')
        .attr('x', (b) => x(b.x0) + 0.5)
        .attr('y', (b) => y(b.length))
        .attr('width', (b) => Math.max(0, x(b.x1) - x(b.x0) - 1))
        .attr('height', (b) => (H - mB) - y(b.length))
        .attr('fill', fill).attr('fill-opacity', 0.55)
        .attr('stroke', stroke).attr('stroke-opacity', 0.6)
        .on('mouseover', function (ev, b) {
          const html = `<strong>${esc(kind)} bin:</strong> [${fmt(b.x0)}, ${fmt(b.x1)}) — ${b.length} replicates`;
          this.__tipHtml = html;
          showTip(html, ev);
        })
        .on('mousemove', function (ev) { if (this.__tipHtml) showTip(this.__tipHtml, ev); })
        .on('mouseout', hideTip);
    };

    if (mode === 'dual') {
      drawBars(baseBins,    COLOR_BASE,  COLOR_BASE,  'Baseline');
      drawBars(treatedBins, COLOR_TREAT, COLOR_TREAT, 'Treated');
    } else if (mode === 'diff') {
      drawBars(baseBins, COLOR_DIFF, COLOR_DIFF, 'Δ');
    } else {
      drawBars(baseBins, COLOR_TREAT, COLOR_TREAT, 'Treated');
    }

    // Reference vertical lines (CI bounds, observed). Each gets its own
    // tooltip describing what it represents.
    (refLines || []).forEach((r) => {
      if (!isFinite(r.x)) return;
      const xp = x(r.x);
      root.append('line')
        .attr('x1', xp).attr('x2', xp).attr('y1', mT).attr('y2', H - mB)
        .attr('stroke', r.color).attr('stroke-width', 1.4)
        .attr('stroke-dasharray', r.dash || null)
        .style('cursor', 'help')
        .on('mouseover', function (ev) { showTip(`<strong>${esc(r.tipLabel)}:</strong> ${fmt(r.x)}`, ev); })
        .on('mousemove', function (ev) { showTip(`<strong>${esc(r.tipLabel)}:</strong> ${fmt(r.x)}`, ev); })
        .on('mouseout', hideTip);
      root.append('text')
        .attr('x', xp + 3).attr('y', mT + 9)
        .attr('font-family', 'Space Mono, monospace').attr('font-size', '9px')
        .attr('fill', r.color).text(r.label);
    });

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

    const metric = METRICS[chosenMetric];
    if (!metric) return;
    if (metric.scope === 'node' && !s.selectedNode) {
      $('viz2-mc-status').textContent = 'Select a node first.';
      return;
    }

    // Build the two graphs ONCE — perturbation only jitters weights.
    const baselineG = buildBaselineGraph();
    const treatedG  = buildTreatedGraph();
    if (!baselineG || !treatedG) return;

    const baseIds  = baselineG.nodes.map((n) => n.id);
    const treatIds = treatedG.nodes.map((n) => n.id);
    if (treatIds.length < 2) {
      $('viz2-mc-status').textContent = 'Need ≥ 2 active nodes (in treated graph).';
      return;
    }
    // Node-scoped metric needs the selected node present in BOTH graphs.
    if (metric.scope === 'node') {
      const inBase  = baseIds.includes(s.selectedNode);
      const inTreat = treatIds.includes(s.selectedNode);
      if (!inTreat) { $('viz2-mc-status').textContent = 'Selected node is removed from treated graph.'; return; }
      if (!inBase)  { $('viz2-mc-status').textContent = 'Selected node only exists in treated graph — node-level diff undefined.'; return; }
    }

    const isDual = !graphsEquivalent(baselineG, treatedG);

    running = true;
    const btn = $('viz2-mc-run'); if (btn) btn.disabled = true;
    const statusEl = $('viz2-mc-status');
    const opts = { selectedNode: s.selectedNode };
    const R = replicates;

    // Observed = same metric on the unperturbed treated graph (no Poisson).
    // For dual mode we also record observed on the unperturbed baseline so the
    // diff chart can show "observed Δ" too.
    const baseIdSet  = new Set(baseIds);
    const treatIdSet = new Set(treatIds);
    const observedTreated  = metric.compute(NV.utils.buildAdj(treatedG,  treatIdSet), treatIds,  opts);
    const observedBaseline = isDual ? metric.compute(NV.utils.buildAdj(baselineG, baseIdSet), baseIds, opts) : observedTreated;

    const baseSamples  = [];   // metric on perturbed baseline (dual only)
    const treatSamples = [];   // metric on perturbed treated
    const diffSamples  = [];   // treated − baseline per replicate (dual only)

    const t0 = performance.now();
    let i = 0;
    const BATCH = 25;
    while (i < R) {
      const end = Math.min(i + BATCH, R);
      for (; i < end; i++) {
        const pT = perturbGraph(treatedG);
        const vT = metric.compute(NV.utils.buildAdj(pT, treatIdSet), treatIds, opts);
        treatSamples.push(vT);
        if (isDual) {
          const pB = perturbGraph(baselineG);
          const vB = metric.compute(NV.utils.buildAdj(pB, baseIdSet), baseIds, opts);
          baseSamples.push(vB);
          diffSamples.push(vT - vB);
        }
      }
      if (statusEl) statusEl.textContent = `Running… ${i}/${R}${isDual ? ' (×2 graphs)' : ''}`;
      // Yield to the event loop so the page stays responsive (same trick
      // the counterfactual case study uses for its 500-rep batch runner).
      await new Promise((r) => setTimeout(r, 0));
    }

    const dtMs = Math.round(performance.now() - t0);
    const meanOf = (a) => { const f = a.filter(isFinite); return f.length ? f.reduce((x, y) => x + y, 0) / f.length : NaN; };
    const treatMean = meanOf(treatSamples);
    const baseMean  = isDual ? meanOf(baseSamples) : NaN;
    const diffMean  = isDual ? meanOf(diffSamples) : NaN;
    const tqLo = NV.utils.quantile(treatSamples, 0.025);
    const tqHi = NV.utils.quantile(treatSamples, 0.975);
    const bqLo = isDual ? NV.utils.quantile(baseSamples, 0.025) : NaN;
    const bqHi = isDual ? NV.utils.quantile(baseSamples, 0.975) : NaN;
    const dqLo = isDual ? NV.utils.quantile(diffSamples, 0.025) : NaN;
    const dqHi = isDual ? NV.utils.quantile(diffSamples, 0.975) : NaN;

    // Render charts. Single mode hides the diff chart entirely.
    const diffSvg = $('viz2-mc-svg-diff');
    const hintEl  = $('viz2-mc-hint');
    if (isDual) {
      if (diffSvg) diffSvg.style.display = '';
      const distRefs = [
        { x: bqLo,            color: COLOR_BASE,  dash: '3,2', label: 'B 2.5%',  tipLabel: 'Baseline 95% CI lower bound' },
        { x: bqHi,            color: COLOR_BASE,  dash: '3,2', label: 'B 97.5%', tipLabel: 'Baseline 95% CI upper bound' },
        { x: tqLo,            color: COLOR_TREAT, dash: '3,2', label: 'T 2.5%',  tipLabel: 'Treated 95% CI lower bound' },
        { x: tqHi,            color: COLOR_TREAT, dash: '3,2', label: 'T 97.5%', tipLabel: 'Treated 95% CI upper bound' },
        { x: observedTreated, color: COLOR_OBS,   dash: null,  label: 'obs(T)',  tipLabel: 'Observed treated (no perturbation)' },
        { x: observedBaseline,color: COLOR_OBS,   dash: '1,2', label: 'obs(B)',  tipLabel: 'Observed baseline (no perturbation)' }
      ];
      drawDistribution('viz2-mc-svg-dist', 'dual', baseSamples, treatSamples, observedTreated, distRefs);

      const obsDiff = observedTreated - observedBaseline;
      const diffRefs = [
        { x: dqLo,    color: COLOR_DIFF,  dash: '3,2', label: '2.5%',  tipLabel: 'Δ 95% CI lower bound' },
        { x: dqHi,    color: COLOR_DIFF,  dash: '3,2', label: '97.5%', tipLabel: 'Δ 95% CI upper bound' },
        { x: 0,       color: '#9ca3af',   dash: '2,3', label: '0',     tipLabel: 'Zero (no effect)' },
        { x: obsDiff, color: COLOR_OBS,   dash: null,  label: 'obsΔ',  tipLabel: 'Observed Δ (no perturbation)' }
      ];
      drawDistribution('viz2-mc-svg-diff', 'diff', diffSamples, null, obsDiff, diffRefs);

      const sig = (dqLo > 0) || (dqHi < 0);
      const summary = $('viz2-mc-summary');
      if (summary) {
        summary.innerHTML = `<strong style="color:#d1fae5;">` +
          `Baseline mean = ${fmt(baseMean)} · Treated mean = ${fmt(treatMean)} · ` +
          `Mean Δ = ${signedFmt(diffMean)} · 95% CI on Δ = [${signedFmt(dqLo)}, ${signedFmt(dqHi)}] · ` +
          `Verdict: <span style="color:${sig ? COLOR_TREAT : COLOR_DIFF};">${sig ? 'significant' : 'non-significant'}</span>` +
          `</strong>`;
      }
      if (hintEl) hintEl.style.display = 'none';
    } else {
      if (diffSvg) diffSvg.style.display = 'none';
      const distRefs = [
        { x: tqLo, color: COLOR_DIFF, dash: '3,2', label: '2.5%',  tipLabel: 'Treated 95% CI lower bound' },
        { x: tqHi, color: COLOR_DIFF, dash: '3,2', label: '97.5%', tipLabel: 'Treated 95% CI upper bound' },
        { x: observedTreated, color: COLOR_OBS, dash: null, label: 'obs', tipLabel: 'Observed (no perturbation)' }
      ];
      drawDistribution('viz2-mc-svg-dist', 'single', treatSamples, null, observedTreated, distRefs);

      const summary = $('viz2-mc-summary');
      if (summary) {
        summary.innerHTML = `<strong style="color:#d1fae5;">Observed = ${fmt(observedTreated)} · Mean = ${fmt(treatMean)} · 95% CI = [${fmt(tqLo)}, ${fmt(tqHi)}]</strong>`;
      }
      if (hintEl) {
        hintEl.style.display = '';
        hintEl.textContent = 'No treatment — add scenarios or remove nodes to enable a counterfactual comparison.';
      }
    }
    if (statusEl) statusEl.textContent = `Done — ${R} reps in ${(dtMs / 1000).toFixed(1)}s · metric: ${metric.label}${isDual ? ' · dual' : ' · single'}`;

    running = false;
    if (btn) btn.disabled = false;
  }

  // ── Change 5: chart PNG download ────────────────────────────
  // Serializes whichever charts are visible into a single canvas (stacked
  // vertically) and triggers a download. Mirrors viz2-core.js exportPng.
  function exportChartPng() {
    const distSvg = $('viz2-mc-svg-dist');
    const diffSvg = $('viz2-mc-svg-diff');
    if (!distSvg) return;
    const showDiff = diffSvg && diffSvg.style.display !== 'none';
    const W = distSvg.clientWidth || 320;
    const H1 = distSvg.clientHeight || 160;
    const H2 = showDiff ? (diffSvg.clientHeight || 160) : 0;
    const GAP = showDiff ? 12 : 0;
    const totalH = H1 + H2 + GAP;

    const prep = (svgEl, w, h) => {
      const clone = svgEl.cloneNode(true);
      clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
      clone.setAttribute('width', w); clone.setAttribute('height', h);
      return new XMLSerializer().serializeToString(clone);
    };
    const distData = prep(distSvg, W, H1);
    const diffData = showDiff ? prep(diffSvg, W, H2) : null;

    const loadImg = (data) => new Promise((resolve) => {
      const url = URL.createObjectURL(new Blob([data], { type: 'image/svg+xml;charset=utf-8' }));
      const img = new Image();
      img.onload = () => { URL.revokeObjectURL(url); resolve(img); };
      img.src = url;
    });

    Promise.all([loadImg(distData), diffData ? loadImg(diffData) : null]).then(([imgD, imgF]) => {
      const c = document.createElement('canvas');
      const scale = 2;
      c.width = W * scale; c.height = totalH * scale;
      const ctx = c.getContext('2d');
      ctx.scale(scale, scale);
      ctx.fillStyle = '#050a05';
      ctx.fillRect(0, 0, W, totalH);
      ctx.drawImage(imgD, 0, 0);
      if (imgF) ctx.drawImage(imgF, 0, H1 + GAP);
      c.toBlob((b) => {
        const a = document.createElement('a');
        a.href = URL.createObjectURL(b);
        a.download = 'counterfactual-distribution.png';
        document.body.appendChild(a); a.click(); a.remove();
      });
    });
  }

  // ── Lifecycle wiring ────────────────────────────────────────
  // Re-render the card whenever the active subgraph, selection,
  // removal set, or scenario set changes — they all flip which
  // metrics or graphs are eligible.
  NV.on('graph-loaded',     render);
  NV.on('view-rebuilt',     render);
  NV.on('node-selected',    render);
  NV.on('removed-changed',  render);
  NV.on('scenario-changed', render);

  if (document.readyState !== 'loading') render();
  else document.addEventListener('DOMContentLoaded', render);
})();
