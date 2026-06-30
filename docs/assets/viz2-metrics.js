// ============================================================
// SYSEN 5470 — Network Visualizer v2 · Feature A: Metric Clarity
// Mounts: #viz2-network-stats-body, #viz2-formulas-body
// Adds: unit labels on Selected Node + Top-N panels (already done in
// core), plus a Network Stats panel (min/max/mean for degree &
// betweenness, both unweighted/weighted) and a Formulas explainer.
// STUB — replaced by subagent.
// ============================================================
(function () {
  'use strict';
  if (!window.NetSciViz2) return;
  // Stub: a feature subagent will implement this.
  const NV = window.NetSciViz2;
  NV.on('init', () => {
    const f = document.getElementById('viz2-formulas-body');
    if (f) f.innerHTML = '<div class="formula-note">Formulas module loading…</div>';
  });
})();
