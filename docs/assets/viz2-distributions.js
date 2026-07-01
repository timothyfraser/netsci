// ============================================================
// SYSEN 5470 — Network Visualizer · Centrality Distributions
// A collapsible sub-card nested inside 📈 Network Stats.
//   • Metric dropdown: degree · weighted degree · betweenness · closeness (if present)
//   • Group-by dropdown: (none) + any categorical node attribute
//   • Histogram — stacked-by-group when a grouping is picked; otherwise the neon
//     "treated" color that the other v2 charts use.
//   • Vertical line for the currently-selected node's observed value.
//   • 💾 PNG download (mirrors the MC / Permutation download buttons).
// Only reads existing state.metrics + state.graph — no expensive recompute.
// Mount point: #viz2-distributions-body (declared in visualizer.html).
// ============================================================
(function () {
  'use strict';
  if (!window.NetSciViz2) return;
  const NV = window.NetSciViz2;

  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  const COLOR_UNGROUPED = '#39FF14'; // neon green — matches other charts
  const COLOR_OBSERVED  = '#f472b6'; // pink — observed selected-node reference

  // Metrics registry. `pull(node, metric)` returns the value for that node
  // from state.metrics; falls back to attributes on the node object where
  // needed. `formatDecimals` controls the axis-label precision.
  const METRICS = {
    degree:           { label: 'Degree (count)',           decimals: 0, pull: (n, m) => (n.deg || 0) },
    weighted_degree:  { label: 'Weighted degree (Σw)',     decimals: 1, pull: (n, m) => (m ? (m.weighted || 0) : 0) },
    betweenness:      { label: 'Betweenness (normalized)', decimals: 4, pull: (n, m) => (m ? (m.betweenness || 0) : 0) },
    closeness:        { label: 'Closeness (normalized)',   decimals: 4, pull: (n, m) => (m ? (m.closeness || 0) : 0) },
  };
  // Only surface closeness if any node actually has it — the current metrics
  // pipeline doesn't compute closeness, so this option stays hidden unless a
  // future pipeline adds it (kept in the registry so wiring is future-proof).
  function metricsAvailable() {
    const s = NV.state;
    const anyMetrics = s.metrics && Object.keys(s.metrics).length > 0;
    const keys = ['degree', 'weighted_degree', 'betweenness'];
    if (anyMetrics) {
      const first = s.metrics[Object.keys(s.metrics)[0]] || {};
      if (Object.prototype.hasOwnProperty.call(first, 'closeness')) keys.push('closeness');
    }
    return keys;
  }

  // Which node attributes are worth grouping by? Reuse the same filtering
  // logic as the permutation module: categorical, 2..cap distinct values,
  // skip identifier columns.
  function groupCandidates() {
    const s = NV.state;
    const cols = s.nodeCols || [];
    const rows = s.nodeCsv || [];
    if (!cols.length || !rows.length) return [];
    const N = rows.length;
    const skip = new Set([s.mapping.nodeId, s.mapping.nodeLabel].filter(Boolean));
    const cap = Math.max(2, Math.min(24, Math.floor(N * 0.6)));
    return cols.filter((c) => {
      if (skip.has(c)) return false;
      const distinct = new Set(rows.map((r) => r[c])).size;
      return distinct >= 2 && distinct <= cap;
    });
  }

  // ── UI state (persists across rerenders) ────────────────────
  const ui = {
    metric: 'degree',
    groupBy: '',                    // '' = ungrouped
  };

  // ── Tooltip (isolated from the MC tooltip so it can outlive rerenders) ─
  let tipEl = null;
  function ensureTip() {
    if (tipEl) return tipEl;
    tipEl = document.createElement('div');
    tipEl.id = 'viz2-dist-tooltip';
    tipEl.style.cssText = [
      'position:fixed', 'pointer-events:none', 'z-index:9999',
      'display:none', 'padding:6px 8px', 'border-radius:4px',
      'background:rgba(5,10,5,0.92)', 'border:1px solid #39FF14',
      'color:#d1fae5', 'font:11px "Space Mono", monospace',
      'box-shadow:0 4px 12px rgba(0,0,0,0.5)', 'max-width:260px'
    ].join(';');
    document.body.appendChild(tipEl);
    return tipEl;
  }
  function showTip(html, ev) {
    const el = ensureTip();
    el.innerHTML = html;
    el.style.display = 'block';
    const pad = 12;
    let x = ev.clientX + pad, y = ev.clientY + pad;
    const r = el.getBoundingClientRect();
    if (x + r.width  > window.innerWidth)  x = ev.clientX - r.width  - pad;
    if (y + r.height > window.innerHeight) y = ev.clientY - r.height - pad;
    el.style.left = x + 'px'; el.style.top = y + 'px';
  }
  function hideTip() { if (tipEl) tipEl.style.display = 'none'; }

  // ── Value gather + selected-node lookup ─────────────────────
  // Returns { values: [{v, group}], selectedValue|null }.
  function gather() {
    const s = NV.state;
    if (!s.graph) return { values: [], selectedValue: null };
    const met = METRICS[ui.metric];
    if (!met) return { values: [], selectedValue: null };
    const grpKey = ui.groupBy;
    const nodeAttrs = s.nodeCsv || [];
    const idAttrCol = s.mapping.nodeId;
    // Map id → nodes.csv row so we can look up arbitrary columns.
    const attrById = {};
    if (idAttrCol) nodeAttrs.forEach((row) => { attrById[String(row[idAttrCol])] = row; });

    const values = [];
    let selectedValue = null;
    s.graph.nodes.forEach((n) => {
      if (s.removedNodes.has(n.id)) return;
      const m = s.metrics[n.id] || {};
      const v = met.pull(n, m);
      if (!Number.isFinite(v)) return;
      let group = '';
      if (grpKey) {
        const row = attrById[String(n.id)];
        group = String((row && row[grpKey] != null) ? row[grpKey] : (n.attrs ? n.attrs[grpKey] : '') || '—');
      }
      values.push({ v: v, group: group });
      if (s.selectedNode && String(n.id) === String(s.selectedNode)) selectedValue = v;
    });
    return { values, selectedValue };
  }

  // Bin an array of numeric values into `nBins` equal-width bins over [lo, hi].
  // Returns bins with .x0, .x1, plus a `by` map { groupLabel: count }.
  function bin(values, lo, hi, nBins) {
    const bins = [];
    if (!(hi > lo)) hi = lo + 1;
    const step = (hi - lo) / nBins;
    for (let i = 0; i < nBins; i++) {
      bins.push({ x0: lo + i * step, x1: lo + (i + 1) * step, total: 0, by: {} });
    }
    values.forEach(({ v, group }) => {
      let idx = Math.floor((v - lo) / step);
      if (idx >= nBins) idx = nBins - 1;
      if (idx < 0) idx = 0;
      const b = bins[idx];
      b.total += 1;
      b.by[group] = (b.by[group] || 0) + 1;
    });
    return bins;
  }

  function groupColorFor(group) {
    const s = NV.state;
    if (!group) return COLOR_UNGROUPED;
    // Prefer any explicit user color for the group, falling back to the palette.
    // When grouping by a column other than the current mapping.nodeGroup, the
    // palette isn't keyed to it — fall back to a deterministic hash color.
    const explicit = (s.groupColors && s.groupColors[group]) || (s.groupPalette && s.groupPalette[group]);
    if (explicit) return explicit;
    // Deterministic 6-hue palette so multi-run renders look stable.
    const palette = ['#39FF14', '#818cf8', '#fbbf24', '#f472b6', '#22d3ee', '#a78bfa'];
    let h = 0;
    for (let i = 0; i < group.length; i++) h = (h * 31 + group.charCodeAt(i)) | 0;
    return palette[Math.abs(h) % palette.length];
  }

  // ── Draw ────────────────────────────────────────────────────
  function draw() {
    const svg = $('viz2-dist-svg'); if (!svg) return;
    svg.innerHTML = '';
    const s = NV.state;
    if (!s.graph || !Object.keys(s.metrics).length) return;

    const gathered = gather();
    const values = gathered.values;
    if (!values.length) return;
    const met = METRICS[ui.metric];

    const W = svg.clientWidth || 320;
    const H = svg.clientHeight || 180;
    const mL = 10, mR = 10, mT = 8, mB = 20;

    let lo = Math.min.apply(null, values.map((d) => d.v));
    let hi = Math.max.apply(null, values.map((d) => d.v));
    if (Number.isFinite(gathered.selectedValue)) {
      lo = Math.min(lo, gathered.selectedValue);
      hi = Math.max(hi, gathered.selectedValue);
    }
    if (!Number.isFinite(lo) || !Number.isFinite(hi) || lo === hi) {
      lo = (lo || 0) - 1; hi = (hi || 0) + 1;
    }
    const pad = (hi - lo) * 0.04;
    lo -= pad; hi += pad;

    const nBins = 24;
    const bins = bin(values, lo, hi, nBins);
    const maxC = Math.max(1, ...bins.map((b) => b.total));

    const x = d3.scaleLinear().domain([lo, hi]).range([mL, W - mR]);
    const y = d3.scaleLinear().domain([0, maxC]).range([H - mB, mT]);
    const root = d3.select(svg);

    // Determine group render order — largest group last so its color caps the stack.
    const groupCounts = {};
    values.forEach((d) => { groupCounts[d.group] = (groupCounts[d.group] || 0) + 1; });
    const groups = Object.keys(groupCounts).sort((a, b) => groupCounts[a] - groupCounts[b]);
    if (!ui.groupBy) groups.length = 0; // ungrouped → single-color path below

    bins.forEach((b) => {
      const bw = Math.max(0, x(b.x1) - x(b.x0) - 1);
      const bx = x(b.x0) + 0.5;
      if (!ui.groupBy || !groups.length) {
        const h0 = (H - mB) - y(b.total);
        if (h0 <= 0) return;
        root.append('rect')
          .attr('x', bx).attr('y', y(b.total))
          .attr('width', bw).attr('height', h0)
          .attr('fill', COLOR_UNGROUPED).attr('fill-opacity', 0.55)
          .attr('stroke', COLOR_UNGROUPED).attr('stroke-opacity', 0.6)
          .on('mouseover', (ev) => showTip(
            `<strong>Bin:</strong> [${fmt(b.x0, met.decimals)}, ${fmt(b.x1, met.decimals)})<br>${b.total} node(s)`, ev))
          .on('mousemove', (ev) => showTip(
            `<strong>Bin:</strong> [${fmt(b.x0, met.decimals)}, ${fmt(b.x1, met.decimals)})<br>${b.total} node(s)`, ev))
          .on('mouseout', hideTip);
      } else {
        // Stacked by group. Draw smallest at top of stack (visually bottom).
        let yCursor = y(b.total);
        // We stack from bottom-up (rendered highest count last so the biggest
        // group sits on the baseline). Iterate reverse so first-drawn is bottom-most.
        for (let i = groups.length - 1; i >= 0; i--) {
          const g = groups[i];
          const c = b.by[g] || 0;
          if (!c) continue;
          const yTop  = y(yBase(b, groups, i));
          const yNext = y(yBase(b, groups, i) - c);
          const h0 = yNext - yTop;
          if (h0 <= 0) continue;
          root.append('rect')
            .attr('x', bx).attr('y', yTop)
            .attr('width', bw).attr('height', h0)
            .attr('fill', groupColorFor(g)).attr('fill-opacity', 0.72)
            .attr('stroke', groupColorFor(g)).attr('stroke-opacity', 0.55)
            .on('mouseover', (ev) => showTip(
              `<strong>${esc(ui.groupBy)}:</strong> ${esc(g)}<br><strong>Bin:</strong> [${fmt(b.x0, met.decimals)}, ${fmt(b.x1, met.decimals)})<br>${c} of ${b.total} node(s)`, ev))
            .on('mousemove', (ev) => showTip(
              `<strong>${esc(ui.groupBy)}:</strong> ${esc(g)}<br><strong>Bin:</strong> [${fmt(b.x0, met.decimals)}, ${fmt(b.x1, met.decimals)})<br>${c} of ${b.total} node(s)`, ev))
            .on('mouseout', hideTip);
          yCursor = yNext;
        }
      }
    });

    // Observed selected-node vertical line.
    if (Number.isFinite(gathered.selectedValue)) {
      const xp = x(gathered.selectedValue);
      root.append('line')
        .attr('x1', xp).attr('x2', xp).attr('y1', mT).attr('y2', H - mB)
        .attr('stroke', COLOR_OBSERVED).attr('stroke-width', 1.4)
        .attr('stroke-dasharray', '4,3')
        .style('cursor', 'help')
        .on('mouseover', (ev) => showTip(
          `<strong>Selected node</strong> (${esc(s.selectedNode)}): ${fmt(gathered.selectedValue, met.decimals)}`, ev))
        .on('mousemove', (ev) => showTip(
          `<strong>Selected node</strong> (${esc(s.selectedNode)}): ${fmt(gathered.selectedValue, met.decimals)}`, ev))
        .on('mouseout', hideTip);
      root.append('text')
        .attr('x', xp + 3).attr('y', mT + 9)
        .attr('font-family', 'Space Mono, monospace').attr('font-size', '9px')
        .attr('fill', COLOR_OBSERVED).text('selected');
    }

    // Axis ticks: just min / max so the chart stays terse.
    root.append('text').attr('x', mL).attr('y', H - 5)
      .attr('font-family', 'Space Mono, monospace').attr('font-size', '9px')
      .attr('fill', '#6b7280').text(fmt(lo, met.decimals));
    root.append('text').attr('x', W - mR).attr('y', H - 5).attr('text-anchor', 'end')
      .attr('font-family', 'Space Mono, monospace').attr('font-size', '9px')
      .attr('fill', '#6b7280').text(fmt(hi, met.decimals));

    // Legend when grouped. Small chips under the chart.
    const legendHost = $('viz2-dist-legend');
    if (legendHost) {
      if (ui.groupBy && groups.length) {
        legendHost.innerHTML = groups.slice().reverse().map((g) => `
          <span style="display:inline-flex;align-items:center;gap:4px;margin-right:8px;font:10px 'Space Mono',monospace;color:var(--grey);">
            <span style="display:inline-block;width:9px;height:9px;background:${groupColorFor(g)};border-radius:2px;"></span>${esc(g)} <span style="color:var(--grey-dim);">(${groupCounts[g]})</span>
          </span>`).join('');
      } else {
        legendHost.innerHTML = '';
      }
    }
  }

  // Running sum of counts across the ordered `groups` list for stacking math.
  // yBase(b, [g0,g1,g2], 1) = counts of g1 + g2 (i.e. everything above index 1).
  function yBase(b, groups, idx) {
    let s = 0;
    for (let i = idx; i < groups.length; i++) s += (b.by[groups[i]] || 0);
    return s;
  }

  function fmt(v, decimals) {
    if (!Number.isFinite(v)) return '—';
    const d = decimals != null ? decimals : 2;
    // Only truncate to integers when decimals=0 (degree). Otherwise keep the
    // precision the metric asked for, but strip trailing zeros for readability.
    return d === 0 ? Math.round(v).toLocaleString() : v.toFixed(d).replace(/\.?0+$/, '') || '0';
  }

  // ── Full render (dropdowns + chart) ─────────────────────────
  function render() {
    const host = $('viz2-distributions-body'); if (!host) return;
    const s = NV.state;
    if (!s.graph) {
      host.innerHTML = '<div class="node-empty">Load a network to see distributions.</div>';
      return;
    }
    const metricKeys = metricsAvailable();
    if (!metricKeys.includes(ui.metric)) ui.metric = metricKeys[0];
    const groupCols = groupCandidates();
    if (ui.groupBy && !groupCols.includes(ui.groupBy)) ui.groupBy = '';

    const metricOpts = metricKeys.map((k) =>
      `<option value="${k}"${k === ui.metric ? ' selected' : ''}>${esc(METRICS[k].label)}</option>`).join('');
    const groupOpts = ['<option value=""' + (ui.groupBy ? '' : ' selected') + '>(none)</option>']
      .concat(groupCols.map((c) => `<option value="${esc(c)}"${c === ui.groupBy ? ' selected' : ''}>${esc(c)}</option>`))
      .join('');

    host.innerHTML = `
      <div class="color-by-row" style="margin-bottom:6px;">
        <label for="viz2-dist-metric">Metric</label>
        <select id="viz2-dist-metric" class="viz-select">${metricOpts}</select>
      </div>
      <div class="color-by-row" style="margin-bottom:8px;">
        <label for="viz2-dist-groupby">Group by</label>
        <select id="viz2-dist-groupby" class="viz-select">${groupOpts}</select>
      </div>
      <div id="viz2-dist-chart-wrap" style="position:relative;">
        <button id="viz2-dist-png" class="viz-zoom-btn"
                style="position:absolute; top:4px; right:4px; width:24px; height:24px; font-size:13px; z-index:2;"
                title="Download chart as PNG" aria-label="Download chart as PNG">💾</button>
        <svg class="dist" id="viz2-dist-svg" style="width:100%; height:180px;"></svg>
      </div>
      <div id="viz2-dist-legend" style="margin-top:4px;"></div>
      <div class="formula-note" style="margin-top:6px;">
        ${s.selectedNode
          ? `Pink dashed line = the selected node (<code>${esc(s.selectedNode)}</code>). Click any node on the graph to move it.`
          : `Click any node on the graph to overlay its observed value as a pink dashed line.`}
      </div>`;

    const mSel = $('viz2-dist-metric');
    const gSel = $('viz2-dist-groupby');
    if (mSel) mSel.addEventListener('change', (e) => { ui.metric = e.target.value; draw(); });
    if (gSel) gSel.addEventListener('change', (e) => { ui.groupBy = e.target.value; draw(); });
    const png = $('viz2-dist-png');
    if (png) png.addEventListener('click', exportPng);

    draw();
  }

  // ── PNG export (same recipe as viz2-montecarlo.js:614) ──────
  function exportPng() {
    const svg = $('viz2-dist-svg'); if (!svg) return;
    const W = svg.clientWidth || 320;
    const H = svg.clientHeight || 180;
    const clone = svg.cloneNode(true);
    clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    clone.setAttribute('width', W); clone.setAttribute('height', H);
    const data = new XMLSerializer().serializeToString(clone);
    const url = URL.createObjectURL(new Blob([data], { type: 'image/svg+xml;charset=utf-8' }));
    const img = new Image();
    img.onload = () => {
      URL.revokeObjectURL(url);
      const c = document.createElement('canvas');
      const scale = 2;
      c.width = W * scale; c.height = H * scale;
      const ctx = c.getContext('2d');
      ctx.scale(scale, scale);
      ctx.fillStyle = '#050a05';
      ctx.fillRect(0, 0, W, H);
      ctx.drawImage(img, 0, 0);
      c.toBlob((b) => {
        const a = document.createElement('a');
        a.href = URL.createObjectURL(b);
        a.download = `centrality-distribution-${ui.metric}.png`;
        document.body.appendChild(a); a.click(); a.remove();
      });
    };
    img.src = url;
  }

  // Re-render whenever anything that could affect the chart changes.
  NV.on('init',            render);
  NV.on('graph-loaded',    render);
  NV.on('metrics-updated', render);
  NV.on('view-rebuilt',    render);
  NV.on('removed-changed', render);
  NV.on('node-selected',   render);

  if (document.readyState !== 'loading') render();
  else document.addEventListener('DOMContentLoaded', render);
})();
