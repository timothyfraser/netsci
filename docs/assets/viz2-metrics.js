// ============================================================
// SYSEN 5470 — Network Visualizer v2 · Feature A: Metric Clarity
// Mounts: #viz2-network-stats-body, #viz2-formulas-body
// Network Stats: min/mean/median/max for degree, weighted-degree,
// betweenness, plus active-node/component counts + raw σ_st(v) max.
// Formulas: plain-text explainer for what those numbers actually mean.
// ============================================================
(function () {
  'use strict';
  if (!window.NetSciViz2) return;
  const NV = window.NetSciViz2;

  const $ = (id) => document.getElementById(id);
  const fmtInt = (n) => Number.isFinite(n) ? Math.round(n).toLocaleString() : '—';
  const fmtNum = (n, d) => Number.isFinite(n) ? n.toFixed(d) : '—';

  // Active-only views — removed nodes don't count toward stats or normalization.
  function activeMetricArrays() {
    const s = NV.state;
    if (!s.graph) return null;
    const deg = [], w = [], betw = [];
    s.graph.nodes.forEach((n) => {
      if (s.removedNodes.has(n.id)) return;
      const m = s.metrics[n.id]; if (!m) return;
      // m.degree mirrors weighted vs count by toggle; n.deg is always the raw count.
      deg.push(n.deg || 0);
      w.push(m.weighted || 0);
      betw.push(m.betweenness || 0);
    });
    return { deg, w, betw };
  }

  // Build one <tr> row of stat cells: min / mean / median / max
  function statRowHtml(label, arr, decimals) {
    if (!arr || !arr.length) {
      return `<tr><td>${label}</td><td colspan="4" class="num">—</td></tr>`;
    }
    const min = Math.min.apply(null, arr);
    const max = Math.max.apply(null, arr);
    const mean = arr.reduce((s, x) => s + x, 0) / arr.length;
    const med = NV.utils.quantile(arr, 0.5);
    return `
      <tr>
        <td>${label}</td>
        <td class="num">${fmtNum(min, decimals)}</td>
        <td class="num">${fmtNum(mean, decimals)}</td>
        <td class="num">${fmtNum(med, decimals)}</td>
        <td class="num">${fmtNum(max, decimals)}</td>
      </tr>`;
  }

  function renderNetworkStats() {
    const host = $('viz2-network-stats-body'); if (!host) return;
    const s = NV.state;
    if (!s.graph) {
      host.innerHTML = '<div class="node-empty">Load a network to see stats.</div>';
      return;
    }
    const arrs = activeMetricArrays();
    const total = s.graph.nodes.length;
    const active = s.activeCount ?? (arrs ? arrs.deg.length : 0);
    const comps = s.activeComponents ?? 0;
    const wUnit = s.useWeights ? '· Σw' : '· count';

    // Raw σ_st(v) max recovered from normalized betweenness (Brandes' undirected norm).
    const norm = Math.max(1, (active - 1) * (active - 2));
    const maxB = arrs && arrs.betw.length ? Math.max.apply(null, arrs.betw) : 0;
    const rawSPmax = Math.round(maxB * norm);

    // Header line: a one-row summary (active nodes, components, max σ_st(v))
    // followed by a compact table of distribution stats.
    host.innerHTML = `
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:8px;">
        <div>
          <div style="font-family:var(--font-display);font-size:18px;color:var(--green-bright);line-height:1;">${fmtInt(active)}<span style="font-size:12px;color:var(--grey-dim);"> / ${fmtInt(total)}</span></div>
          <div style="font-family:var(--font-mono);font-size:9px;color:var(--grey);letter-spacing:0.12em;text-transform:uppercase;margin-top:3px;">Active / total</div>
        </div>
        <div>
          <div style="font-family:var(--font-display);font-size:18px;color:var(--green-bright);line-height:1;">${fmtInt(comps)}</div>
          <div style="font-family:var(--font-mono);font-size:9px;color:var(--grey);letter-spacing:0.12em;text-transform:uppercase;margin-top:3px;">Components</div>
        </div>
        <div>
          <div style="font-family:var(--font-display);font-size:18px;color:var(--green-bright);line-height:1;">${fmtInt(rawSPmax)}</div>
          <div style="font-family:var(--font-mono);font-size:9px;color:var(--grey);letter-spacing:0.12em;text-transform:uppercase;margin-top:3px;">Max σ<sub>st</sub>(v)</div>
        </div>
      </div>
      <table class="group-table" style="margin-top:4px;">
        <thead><tr>
          <th>Distribution</th><th class="gv" style="text-align:right;">Min</th><th class="gv" style="text-align:right;">Mean</th><th class="gv" style="text-align:right;">Median</th><th class="gv" style="text-align:right;">Max</th>
        </tr></thead>
        <tbody style="font-family:var(--font-mono);">
          ${statRowHtml('Degree <span class="unit">· count</span>', arrs && arrs.deg, 1)}
          ${statRowHtml('Weighted degree <span class="unit">· Σw</span>', arrs && arrs.w, 1)}
          ${statRowHtml('Betweenness <span class="unit">· norm 0–1</span>', arrs && arrs.betw, 4)}
        </tbody>
      </table>
      <div class="formula-note" style="margin-top:8px;">
        Over the <strong>${fmtInt(active)}</strong> active node(s); removed nodes excluded.
        Toggle <em>Weight degree &amp; betweenness</em> to switch the selected-node
        Degree row between ${wUnit}.
      </div>`;
  }

  function renderFormulas() {
    const host = $('viz2-formulas-body'); if (!host) return;
    const s = NV.state;
    const N = s.graph ? (s.activeCount || 0) : 0;
    const norm = Math.max(0, (N - 1) * (N - 2));
    const liveN = N ? `<code>(N−1)(N−2) = (${N}−1)(${N}−2) = ${norm.toLocaleString()}</code>`
                    : '<code>(N−1)(N−2)</code> <span class="formula-note" style="display:inline;">— load a network to see the live value</span>';

    host.innerHTML = `
      <div class="formula-note">
        These are the exact formulas v2 uses. <em>N</em> = number of <strong>active</strong>
        nodes (i.e. <code>state.activeCount</code> — removed nodes don't count).
      </div>

      <div class="formula-block">
        <strong>Degree (unweighted)</strong><br>
        <code>deg(v) = |N(v)|</code><br>
        Number of edges incident to <em>v</em>. Units: <em>edges</em>.
      </div>

      <div class="formula-block">
        <strong>Weighted degree</strong><br>
        <code>w(v) = Σ<sub>e ∈ incident(v)</sub> weight(e)</code><br>
        Sum of weights on incident edges. Units: <em>Σw</em> (same units as the
        weight column you mapped).
      </div>

      <div class="formula-block">
        <strong>Betweenness (normalized)</strong><br>
        <code>B(v) = [ Σ<sub>s ≠ v ≠ t</sub> σ<sub>st</sub>(v) / σ<sub>st</sub> ] / [(N−1)(N−2)]</code><br>
        Fraction of shortest <em>s–t</em> paths that pass through <em>v</em>,
        averaged over all ordered pairs. Range: <em>0–1</em>.
        <div class="formula-note" style="margin-top:6px;">
          v2 uses <strong>Brandes' algorithm</strong>: BFS by default
          (unweighted shortest paths). When <em>Weight degree &amp; betweenness</em>
          is on, it switches to Dijkstra with edge cost <code>1 / weight</code>,
          so heavier edges are "shorter."
          For the current graph, ${liveN}.
        </div>
      </div>

      <div class="formula-block">
        <strong>Number of shortest paths through node v (raw σ<sub>st</sub>(v))</strong><br>
        <code>σ<sub>st</sub>(v) = B(v) × (N−1)(N−2)</code> &nbsp;(rounded)<br>
        Recovered from the normalized B(v). This is the absolute count students
        usually picture when they hear "betweenness," and it scales with the
        network. Watch it drop sharply when you remove a node and N shrinks —
        that's the normalization at work.
      </div>`;
  }

  function renderAll() { renderNetworkStats(); renderFormulas(); }

  // Re-render on every event that could change metrics or graph shape.
  NV.on('init', renderAll);
  NV.on('graph-loaded', renderAll);
  NV.on('metrics-updated', renderAll);
  NV.on('view-rebuilt', renderAll);
  NV.on('removed-changed', renderAll);

  // First paint in case init already fired before this module loaded.
  if (document.readyState !== 'loading') renderAll();
  else document.addEventListener('DOMContentLoaded', renderAll);
})();
