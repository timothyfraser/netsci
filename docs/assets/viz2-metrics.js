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

  function statRow(label, arr, decimals, unit) {
    if (!arr || !arr.length) {
      return `<div class="metric-row"><span class="ml">${label}</span><span class="mv">—</span></div>`;
    }
    const min = Math.min.apply(null, arr);
    const max = Math.max.apply(null, arr);
    const mean = arr.reduce((s, x) => s + x, 0) / arr.length;
    const med = NV.utils.quantile(arr, 0.5);
    const u = unit ? `<span class="unit">${unit}</span>` : '';
    return `
      <div class="metric-row">
        <span class="ml">${label}</span>
        <span class="mv">${fmtNum(min, decimals)} / ${fmtNum(mean, decimals)} / ${fmtNum(med, decimals)} / ${fmtNum(max, decimals)}${u}</span>
      </div>`;
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

    host.innerHTML = `
      <div class="metric-row">
        <span class="ml">Active / total nodes</span>
        <span class="mv">${fmtInt(active)} / ${fmtInt(total)}</span>
      </div>
      <div class="metric-row">
        <span class="ml">Active components</span>
        <span class="mv">${fmtInt(comps)}</span>
      </div>
      <div class="metric-row" style="border-bottom:none;padding-bottom:0;">
        <span class="ml" style="color:var(--green-bright);font-family:var(--font-mono);font-size:9.5px;letter-spacing:0.12em;text-transform:uppercase;">min / mean / median / max</span>
        <span class="mv"></span>
      </div>
      ${statRow('Degree', arrs && arrs.deg, 1, '· count')}
      ${statRow('Weighted degree', arrs && arrs.w, 1, '· Σw')}
      ${statRow('Betweenness', arrs && arrs.betw, 4, '· norm 0–1')}
      <div class="metric-row">
        <span class="ml"># Shortest paths through (max)</span>
        <span class="mv">${fmtInt(rawSPmax)}<span class="unit">· σ_st(v)</span></span>
      </div>
      <div class="formula-note" style="margin-top:8px;">
        Distributions are over the <strong>${fmtInt(active)}</strong> active node(s);
        removed nodes are excluded. Toggle <em>Weight degree &amp; betweenness</em>
        to switch the selected-node "Degree" line between ${wUnit}.
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
        <strong># Shortest paths through node v (raw σ<sub>st</sub>(v))</strong><br>
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
