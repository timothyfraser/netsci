// ============================================================
// SYSEN 5470 — Network Visualizer v2 · Group Composition
// Mounts: #viz2-group-composition-body
// Replaces the standalone Similarity Index card. Shows:
//   • dropdown to choose the grouping variable (mirrors to viz2-core's
//     setGroupColumn so the WHOLE network recolors and every other card
//     re-keys to the new grouping)
//   • per-group bar chart of edge-weight share (like the permutation
//     chapter's bar chart in docs/case-studies/permutation.html)
//   • Similarity Index footer line (uses NV.utils.similarityIndex)
// ============================================================
(function () {
  'use strict';
  if (!window.NetSciViz2) return;
  const NV = window.NetSciViz2;

  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
                              .replace(/>/g, '&gt;').replace(/"/g, '&quot;');

  // Active node ids (Set), excluding removed.
  function activeIdSet() {
    const s = NV.state;
    const set = new Set();
    if (!s.graph) return set;
    s.graph.nodes.forEach((n) => { if (!s.removedNodes.has(n.id)) set.add(n.id); });
    return set;
  }

  // Mirror of core's private categoricalNodeCols — pick categorical-ish
  // columns to offer as grouping candidates. Skip id/label columns and
  // anything with >cap distinct values (free-text fields, unique ids).
  function categoricalCols(maxCap) {
    const s = NV.state;
    const cols = s.nodeCols || [];
    const rows = s.nodeCsv || [];
    const N = rows.length || 1;
    const skip = new Set([s.mapping.nodeId, s.mapping.nodeLabel].filter(Boolean));
    const cap = Math.max(2, Math.min(maxCap, Math.floor(N * 0.6)));
    return cols.filter((c) => {
      if (skip.has(c)) return false;
      const distinct = new Set(rows.map((r) => r[c])).size;
      return distinct >= 2 && distinct <= cap;
    });
  }

  // Per-group edge-weight stats over the ACTIVE subgraph.
  // Returns:
  //   groups   – sorted list of distinct group values
  //   members  – { g → #nodes }
  //   incident – { g → Σ weight on edges with at least one endpoint in g }
  //   cells    – ordered (i→j) edge-weight totals, as [{from, to, w, frac}, …]
  //   totalEnd – Σ weight × 2 (denominator for incident share)
  //   totalDir – Σ weight (denominator for ordered-cell share)
  function computeStats() {
    const s = NV.state;
    if (!s.graph || !s.mapping.nodeGroup) return null;
    const active = activeIdSet();
    if (!active.size) return null;

    const groupOf = Object.create(null);
    const members = Object.create(null);
    s.graph.nodes.forEach((n) => {
      if (!active.has(n.id)) return;
      const g = n.group;
      if (g === null || g === undefined || g === '') return;
      groupOf[n.id] = g;
      members[g] = (members[g] || 0) + 1;
    });
    const groups = Object.keys(members).sort();
    if (!groups.length) return null;

    const incident = Object.create(null);
    groups.forEach((g) => { incident[g] = 0; });
    const cellMap = new Map();           // 'a||b' → weight
    let totalDir = 0;

    s.graph.links.forEach((l) => {
      const sId = typeof l.source === 'object' ? l.source.id : l.source;
      const tId = typeof l.target === 'object' ? l.target.id : l.target;
      if (!active.has(sId) || !active.has(tId)) return;
      const a = groupOf[sId], b = groupOf[tId];
      if (a === undefined || b === undefined) return;
      const w = (l.weight && l.weight > 0) ? l.weight : 1;
      incident[a] += w; incident[b] += w;
      const k = a + '||' + b;
      cellMap.set(k, (cellMap.get(k) || 0) + w);
      totalDir += w;
    });

    const totalEnd = totalDir * 2;
    // Order cells lexicographically by (from, to) — gives a stable read.
    const cells = [];
    for (const from of groups) for (const to of groups) {
      const w = cellMap.get(from + '||' + to) || 0;
      if (w > 0) cells.push({ from, to, w, frac: totalDir ? w / totalDir : 0 });
    }
    return { groups, members, incident, cells, totalDir, totalEnd };
  }

  // ── Stacked cell-share bar (one horizontal bar split by ordered cell) ──
  function renderCellBar(svgSel, stats, palette, width) {
    const H = 22;
    svgSel.attr('width', width).attr('height', H).selectAll('*').remove();
    if (!stats.totalDir) return;
    let x = 0;
    stats.cells.forEach((c) => {
      const w = c.frac * width;
      svgSel.append('rect')
        .attr('x', x).attr('y', 0).attr('width', Math.max(0.5, w)).attr('height', H)
        .attr('fill', palette[c.from] || '#39FF14')
        .attr('fill-opacity', 0.85)
        .attr('stroke', '#050a05').attr('stroke-width', 0.5)
        .append('title').text(`${c.from} → ${c.to}: ${(c.frac * 100).toFixed(1)}%`);
      x += w;
    });
  }

  // ── Per-group bar chart (D3): incident share with colored bars ─────
  function renderGroupBars(svgSel, stats, palette, width) {
    const groups = stats.groups;
    const rowH = 22, gap = 4;
    const H = groups.length * (rowH + gap) + 4;
    svgSel.attr('width', width).attr('height', H).selectAll('*').remove();

    const labelW = Math.min(90, Math.max(40, d3.max(groups, (g) => String(g).length) * 7));
    const valW = 52;
    const barX = labelW + 6;
    const barW = Math.max(20, width - barX - valW - 4);

    const maxFrac = d3.max(groups, (g) => stats.incident[g] / Math.max(1, stats.totalEnd)) || 1;

    const row = svgSel.selectAll('g').data(groups).enter().append('g')
      .attr('transform', (_, i) => `translate(0, ${i * (rowH + gap)})`);

    row.append('text')
      .attr('x', labelW).attr('y', rowH / 2 + 4)
      .attr('text-anchor', 'end')
      .attr('font-family', 'Space Mono, monospace').attr('font-size', '10px')
      .attr('fill', '#d1fae5')
      .text((g) => String(g).length > 14 ? String(g).slice(0, 13) + '…' : String(g))
      .append('title').text((g) => `${g} · ${stats.members[g]} members`);

    // Track behind bar so empty groups still show a slot.
    row.append('rect')
      .attr('x', barX).attr('y', 4)
      .attr('width', barW).attr('height', rowH - 8)
      .attr('fill', 'rgba(255,255,255,0.04)')
      .attr('stroke', 'rgba(57,255,20,0.18)').attr('stroke-width', 0.5);

    row.append('rect')
      .attr('x', barX).attr('y', 4)
      .attr('width', (g) => {
        const f = stats.incident[g] / Math.max(1, stats.totalEnd);
        return Math.max(0, (f / maxFrac) * barW);
      })
      .attr('height', rowH - 8)
      .attr('fill', (g) => palette[g] || '#39FF14')
      .attr('fill-opacity', 0.85)
      .append('title').text((g) => {
        const f = stats.incident[g] / Math.max(1, stats.totalEnd);
        return `${g}: ${(f * 100).toFixed(1)}% of edge-endpoint weight (${stats.members[g]} members)`;
      });

    row.append('text')
      .attr('x', width - 2).attr('y', rowH / 2 + 4)
      .attr('text-anchor', 'end')
      .attr('font-family', 'Space Mono, monospace').attr('font-size', '10px')
      .attr('fill', '#ffffff')
      .text((g) => {
        const f = stats.incident[g] / Math.max(1, stats.totalEnd);
        return (f * 100).toFixed(1) + '%';
      });
  }

  // ── Main render ─────────────────────────────────────────────
  function render() {
    const host = $('viz2-group-composition-body'); if (!host) return;
    const s = NV.state;

    if (!s.graph) {
      host.innerHTML = '<div class="node-empty">Load a network to see group composition.</div>';
      return;
    }

    // Dropdown options: categorical node columns + a "none" option.
    const opts = categoricalCols(60);
    const current = s.mapping.nodeGroup || '';
    if (current && !opts.includes(current)) opts.unshift(current);

    const optionHtml = '<option value="">(none — uniform)</option>' +
      opts.map((c) => `<option value="${esc(c)}"${c === current ? ' selected' : ''}>${esc(c)}</option>`).join('');

    // Frame skeleton (always present so the dropdown stays mounted even when
    // no group is chosen — otherwise the user has no way to pick one here).
    host.innerHTML = `
      <div class="color-by-row" style="margin-bottom:8px;">
        <label for="viz2-grouping-col">Grouping variable</label>
        <select id="viz2-grouping-col" class="viz-select">${optionHtml}</select>
      </div>
      <div id="viz2-grouping-swatches" style="display:flex;flex-wrap:wrap;gap:4px;margin:0 0 10px;"></div>
      <div id="viz2-grouping-cellbar" style="margin-bottom:4px;"></div>
      <div id="viz2-grouping-celllegend" style="font-family:var(--font-mono);font-size:10px;color:var(--grey);margin-bottom:12px;line-height:1.5;"></div>
      <div style="font-family:var(--font-mono);font-size:9.5px;color:var(--grey);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px;">Per-group share of edge endpoints</div>
      <div id="viz2-grouping-bars"></div>
      <div id="viz2-grouping-sim" style="margin-top:10px;padding-top:8px;border-top:1px solid var(--border-soft);font-family:var(--font-mono);font-size:11px;color:var(--green-mint);"></div>`;

    // Wire dropdown → setGroupColumn (mirrors to Display panel + recolors).
    const sel = $('viz2-grouping-col');
    if (sel) sel.addEventListener('change', (e) => {
      NV.setGroupColumn(e.target.value || null);
      // setGroupColumn emits 'view-rebuilt' which calls render() again.
    });

    if (!current) {
      $('viz2-grouping-cellbar').innerHTML =
        '<div class="formula-note">Pick a grouping variable above to see edge-weight breakdown.</div>';
      $('viz2-grouping-bars').innerHTML = '';
      $('viz2-grouping-sim').innerHTML = '';
      return;
    }

    const stats = computeStats();
    if (!stats) {
      $('viz2-grouping-cellbar').innerHTML =
        '<div class="node-empty">No edges with two-sided group values in the active subgraph.</div>';
      return;
    }

    // Palette swatches — make the color↔group mapping legible at a glance.
    const palette = s.groupColors && Object.keys(s.groupColors).length
      ? Object.assign({}, s.groupPalette, s.groupColors)
      : (s.groupPalette || {});
    const swatchHost = $('viz2-grouping-swatches');
    swatchHost.innerHTML = stats.groups.map((g) => {
      const c = palette[g] || '#39FF14';
      return `<span title="${esc(g)}" style="display:inline-flex;align-items:center;gap:4px;font-family:var(--font-mono);font-size:10px;color:var(--green-mint);">
        <span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:${c};border:1px solid #050a05;"></span>${esc(g)}
      </span>`;
    }).join('');

    // Width: host's inner width (the panel's .agg-body has its own padding).
    const W = Math.max(180, host.clientWidth - 2);

    // Stacked cell bar + textual legend underneath.
    const cellSvg = d3.select($('viz2-grouping-cellbar')).append('svg');
    renderCellBar(cellSvg, stats, palette, W);

    // Top-3 cells + total — keeps the legend readable for K=10 cases where
    // K² cells would overwhelm. Hover the bar segments for the full list.
    const sorted = stats.cells.slice().sort((a, b) => b.frac - a.frac);
    const topN = Math.min(4, sorted.length);
    const legendBits = sorted.slice(0, topN).map((c) => {
      const sw = palette[c.from] || '#39FF14';
      return `<span style="display:inline-flex;align-items:center;gap:3px;margin-right:8px;">
        <span style="display:inline-block;width:8px;height:8px;background:${sw};border-radius:1px;"></span>
        ${esc(c.from)}→${esc(c.to)}: <strong style="color:var(--white);">${(c.frac * 100).toFixed(0)}%</strong>
      </span>`;
    });
    const rest = sorted.length - topN;
    $('viz2-grouping-celllegend').innerHTML = legendBits.join('') +
      (rest > 0 ? `<span style="color:var(--grey-dim);">+${rest} more (hover bar)</span>` : '');

    // Per-group bar chart.
    const barSvg = d3.select($('viz2-grouping-bars')).append('svg');
    renderGroupBars(barSvg, stats, palette, W);

    // Similarity Index footer.
    const sim = NV.utils.similarityIndex(s.graph, '__group__', activeIdSet());
    const idxTxt = isFinite(sim.index) ? sim.index.toFixed(3) : 'NaN';
    const interp = !isFinite(sim.index)
      ? 'Need ≥2 groups with two-sided edges.'
      : sim.index < 0.10 ? 'Mixing is close to uniform across groups.'
      : sim.index < 0.30 ? 'Some group concentration, but mostly mixed.'
      : sim.index < 0.60 ? 'Clear within-group concentration.'
      : 'Heavily concentrated within a few group pairs.';

    const tipText = 'Course Similarity Index over K groups: (K²/(2(K²−1))) · Σ_{i,j} |p_ij − 1/K²|. ' +
      '0 = uniform mixing across all K² ordered cells; 1 = all weight on a single cell. ' +
      'Generalized from the binary high/low formula in the Permutation case study.';

    $('viz2-grouping-sim').innerHTML = `
      <div style="display:flex;align-items:baseline;gap:6px;">
        <span style="color:var(--grey);text-transform:uppercase;letter-spacing:0.08em;font-size:9.5px;">Similarity Index</span>
        <span style="color:var(--green-bright);font-family:var(--font-display);font-size:18px;">${idxTxt}</span>
        <span class="viz2-info-icon" title="${esc(tipText)}">i</span>
      </div>
      <div style="color:var(--grey);font-size:10.5px;margin-top:2px;">
        K = ${sim.K} group${sim.K === 1 ? '' : 's'} · ${interp}
      </div>`;
  }

  // Re-render on every lifecycle event that could change the answer.
  NV.on('graph-loaded',    render);
  NV.on('view-rebuilt',    render);
  NV.on('metrics-updated', render);
  NV.on('removed-changed', render);

  // First paint if init already fired before this module loaded.
  if (document.readyState !== 'loading') render();
  else document.addEventListener('DOMContentLoaded', render);
})();
