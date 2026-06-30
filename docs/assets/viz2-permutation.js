// ============================================================
// SYSEN 5470 — Network Visualizer v2 · Feature E: Permutation Test
// Mounts: #viz2-permutation-card .card-body
//
// Replicates the permutation case study (docs/case-studies/permutation.html,
// code/06_permutation/example.R/.py): shuffle a node attribute (or, for an
// edge-attr block, shuffle edge weights within blocks), recompute a test
// statistic each replicate, build a null distribution, and report a
// one-sided p-value: p = #{null_i >= observed} / R  (no continuity
// correction — matches `mean(null >= observed)` in example.R).
//
// Controls
//   • Test attribute     — categorical node column to permute
//   • Block by           — (unblocked) | Node attr: <c> | Edge attr: <c>
//   • Test statistic     — assortativity over test attr (default) | APL | diameter
//   • # replicates       — 20…2000, default 100
//   • 🔀 Run Permutation — runs in 25-rep chunks, yields between chunks
//
// CRITICAL: original node attrs (and link weights, for edge-block mode) are
// SNAPSHOTTED before any shuffling and RESTORED in finally{} so the live
// graph display is never left scrambled, even if the run errors mid-way.
// ============================================================
(function () {
  'use strict';
  if (!window.NetSciViz2) return;
  const NV = window.NetSciViz2;

  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');

  // Persist UI choices across re-renders so a graph reload doesn't wipe them.
  const ui = {
    testAttr:  null,   // node col being permuted ('__group__' === active group col proxy)
    blockMode: '',     // '' | 'node:<col>' | 'edge:<col>'
    stat:      'similarity',
    reps:      100
  };
  let running = false;
  // Last result so the histogram persists across unrelated rerenders.
  let lastResult = null; // {observed, samples, pval, stat, attr, blockMode, reps, oneSided:true}

  // ── Categorical-column detection (mirrors viz2-core categoricalNodeCols
  // for node cols and adds an edge-side analogue) ─────────────
  function categoricalNodeColsLocal(maxCap) {
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
  function categoricalEdgeCols(maxCap) {
    const s = NV.state;
    const cols = s.edgeCols || [];
    const rows = s.edgeCsv || [];
    const N = rows.length || 1;
    const skip = new Set([s.mapping.from, s.mapping.to, s.mapping.weight, s.mapping.time].filter(Boolean));
    const cap = Math.max(2, Math.min(maxCap, Math.floor(N * 0.6)));
    return cols.filter((c) => {
      if (skip.has(c)) return false;
      const distinct = new Set(rows.map((r) => r[c])).size;
      return distinct >= 2 && distinct <= cap;
    });
  }

  // Active-id Set, excluding removed nodes.
  function activeIdSet() {
    const s = NV.state, set = new Set();
    if (!s.graph) return set;
    s.graph.nodes.forEach((n) => { if (!s.removedNodes.has(n.id)) set.add(n.id); });
    return set;
  }

  // ── Test statistics ─────────────────────────────────────────
  // similarity → COURSE statistic from docs/case-studies/permutation.html
  //              (NOT Newman r — that wasn't taught). 0 = uniform mixing,
  //              1 = all weight on a single group-pair cell.
  // assort     → kept as an alternative for power-user comparison.
  // APL/diam   → graph-level distance metrics; less interesting under label
  //              permutation but offered for parity with the MC card.
  function statSimilarity(attr) {
    const s = NV.state;
    const ids = activeIdSet();
    const { index } = NV.utils.similarityIndex(s.graph, attr, ids);
    return isFinite(index) ? index : NaN;
  }
  function statAssort(attr) {
    const s = NV.state;
    const ids = activeIdSet();
    const { r } = NV.utils.nominalAssortativity(s.graph, attr, ids);
    return isFinite(r) ? r : NaN;
  }
  function statAplDiam(which) {
    const s = NV.state;
    const ids = Array.from(activeIdSet());
    const n = ids.length;
    if (n < 2) return NaN;
    const idSet = new Set(ids);
    const adj = NV.utils.buildAdj(s.graph, idSet);
    let total = 0, pairs = 0, maxD = 0;
    for (const src of ids) {
      const d = NV.utils.bfs(adj, src);
      for (const t of ids) {
        if (t === src) continue;
        const v = d[t];
        if (v === Infinity) continue;
        total += v; pairs += 1;
        if (v > maxD) maxD = v;
      }
    }
    const expected = n * (n - 1);
    if (pairs < expected) return Infinity;     // disconnected
    return which === 'diam' ? maxD : (total / pairs);
  }
  function evalStat(statKey, attr) {
    if (statKey === 'similarity') return statSimilarity(attr);
    if (statKey === 'assort')     return statAssort(attr);
    if (statKey === 'apl')        return statAplDiam('apl');
    if (statKey === 'diam')       return statAplDiam('diam');
    return NaN;
  }

  // ── Permutation modes ───────────────────────────────────────
  // unblocked   : shuffle attr across all active nodes
  // blockNode   : within each level of blockCol (node attr), shuffle attr
  // blockEdge   : ignore attr; within each level of blockCol (edge attr),
  //               shuffle link.weight (alternative null for edge-based stats)
  function permuteAttrUnblocked(nodes, attr) {
    const vals = nodes.map((n) => n.attrs ? n.attrs[attr] : undefined);
    NV.utils.shuffleInPlace(vals);
    nodes.forEach((n, i) => {
      if (!n.attrs) n.attrs = {};
      n.attrs[attr] = vals[i];
    });
  }
  function permuteAttrBlockedByNode(nodes, attr, blockCol) {
    // partition active nodes by their blockCol value (null/empty bucket allowed)
    const buckets = new Map();
    nodes.forEach((n) => {
      const k = (n.attrs && n.attrs[blockCol] !== undefined && n.attrs[blockCol] !== null && n.attrs[blockCol] !== '')
        ? String(n.attrs[blockCol]) : '__missing__';
      if (!buckets.has(k)) buckets.set(k, []);
      buckets.get(k).push(n);
    });
    buckets.forEach((arr) => {
      const vals = arr.map((n) => n.attrs ? n.attrs[attr] : undefined);
      NV.utils.shuffleInPlace(vals);
      arr.forEach((n, i) => {
        if (!n.attrs) n.attrs = {};
        n.attrs[attr] = vals[i];
      });
    });
  }
  function permuteWeightsBlockedByEdge(links, blockCol, idxIsActive) {
    // group active links by their edge-attribute value, shuffle weights within.
    // We pull blockCol from link itself or from the raw edge row if attrs not on link.
    // viz2-core doesn't stash edge attrs on link objects; we must reach into
    // state.edgeCsv via a paired index. Easiest: tag links with `_eIdx` (row index).
    const buckets = new Map();
    links.forEach((l, i) => {
      if (!idxIsActive(i)) return;
      const v = l._blockVal;
      const k = (v !== undefined && v !== null && v !== '') ? String(v) : '__missing__';
      if (!buckets.has(k)) buckets.set(k, []);
      buckets.get(k).push(i);
    });
    buckets.forEach((idxs) => {
      const ws = idxs.map((i) => links[i].weight);
      NV.utils.shuffleInPlace(ws);
      idxs.forEach((i, k) => { links[i].weight = ws[k]; });
    });
  }

  // For mapping the active-link indices into csv rows (so we can read block values),
  // we use the edge-CSV row order: links built in buildGraph() preserve that order.
  // Tag each link with the block value from the parallel CSV row.
  function tagLinksWithBlockVal(blockCol) {
    const s = NV.state;
    const rows = s.edgeCsv || [];
    // base graph links == raw rows (after the from/to filter). To stay safe
    // we rebuild a parallel value array by scanning rows for valid (from,to).
    const m = s.mapping, links = s.graph.links;
    let li = 0;
    rows.forEach((row) => {
      const a = row[m.from], b = row[m.to];
      if (a === undefined || a === null || a === '' || b === undefined || b === null || b === '') return;
      if (li < links.length) {
        links[li]._blockVal = row[blockCol];
        li++;
      }
    });
  }
  function untagLinks() {
    const s = NV.state;
    if (!s.graph) return;
    s.graph.links.forEach((l) => { delete l._blockVal; });
  }

  // ── UI render ───────────────────────────────────────────────
  function render() {
    const card = $('viz2-permutation-card'); if (!card) return;
    const body = card.querySelector('.card-body'); if (!body) return;
    const s = NV.state;

    if (!s.graph) {
      body.innerHTML = '<div class="node-empty">Load a network with a group column to enable permutation tests.</div>';
      return;
    }

    const nodeCats = categoricalNodeColsLocal(60);
    if (!nodeCats.length) {
      body.innerHTML = '<div class="node-empty">No categorical node attributes available to permute. Load a nodelist with at least one categorical column.</div>';
      return;
    }

    // default test attr → current group col, else first categorical
    if (!ui.testAttr || !nodeCats.includes(ui.testAttr)) {
      ui.testAttr = s.mapping.nodeGroup && nodeCats.includes(s.mapping.nodeGroup)
        ? s.mapping.nodeGroup : nodeCats[0];
    }

    const edgeCats = categoricalEdgeCols(40);

    // Build block-mode options
    const blockOpts = [
      `<option value=""${ui.blockMode === '' ? ' selected' : ''}>(unblocked) — shuffle freely across all nodes</option>`
    ];
    nodeCats.forEach((c) => {
      const v = 'node:' + c;
      blockOpts.push(`<option value="${esc(v)}"${ui.blockMode === v ? ' selected' : ''}>Node attribute: ${esc(c)}</option>`);
    });
    edgeCats.forEach((c) => {
      const v = 'edge:' + c;
      blockOpts.push(`<option value="${esc(v)}"${ui.blockMode === v ? ' selected' : ''}>Edge attribute: ${esc(c)} (shuffles edge weights within blocks)</option>`);
    });

    // Validate persisted block mode against current cols.
    if (ui.blockMode) {
      const isEdge = ui.blockMode.startsWith('edge:');
      const col = ui.blockMode.slice(isEdge ? 5 : 5); // both prefixes are 5 chars
      const pool = isEdge ? edgeCats : nodeCats;
      if (!pool.includes(col)) ui.blockMode = '';
    }

    const isEdgeBlock = ui.blockMode.startsWith('edge:');

    // Test-statistic dropdown — similarity index (course default) uses the test attr;
    // APL/diam are graph-level. Newman assortativity is kept as an alternative.
    const statOpts = [
      `<option value="similarity"${ui.stat === 'similarity' ? ' selected' : ''}>Similarity Index over test attribute (course default)</option>`,
      `<option value="assort"${ui.stat === 'assort' ? ' selected' : ''}>Newman assortativity over test attribute</option>`,
      `<option value="apl"${ui.stat   === 'apl'    ? ' selected' : ''}>Avg shortest path length (graph-level)</option>`,
      `<option value="diam"${ui.stat  === 'diam'   ? ' selected' : ''}>Network diameter (graph-level)</option>`
    ];

    // Test-attribute dropdown
    const attrOpts = nodeCats.map((c) =>
      `<option value="${esc(c)}"${ui.testAttr === c ? ' selected' : ''}>${esc(c)}</option>`
    ).join('');

    const attrDisabledAttr = isEdgeBlock ? ' disabled' : '';
    const attrDisabledNote = isEdgeBlock
      ? `<div class="formula-note" style="margin:-4px 0 0;">Edge-attribute blocking permutes <em>edge weights</em> — the test attribute is irrelevant in this mode.</div>`
      : '';

    const warnReps = `<div class="warn">100 = quick look · 500 = solid · 1000 = defensible p-value.</div>`;
    const pvalTip = 'p-value is one-sided: #{null_i ≥ observed} / R. No continuity correction — matches mean(null >= observed) in code/06_permutation/example.R.';

    body.innerHTML = `
      <div class="color-by-row">
        <label for="viz2-perm-attr">Test attribute</label>
        <select id="viz2-perm-attr" class="viz-select"${attrDisabledAttr}>${attrOpts}</select>
        ${attrDisabledNote}
      </div>
      <div class="color-by-row">
        <label for="viz2-perm-block">Block by</label>
        <select id="viz2-perm-block" class="viz-select">${blockOpts.join('')}</select>
      </div>
      <div class="color-by-row">
        <label for="viz2-perm-stat">Test statistic
          <span class="viz2-info-icon" title="${esc(pvalTip)}" aria-label="p-value details">ⓘ</span>
        </label>
        <select id="viz2-perm-stat" class="viz-select">${statOpts.join('')}</select>
      </div>
      <div class="color-by-row">
        <label for="viz2-perm-reps"># replicates</label>
        <select id="viz2-perm-reps" class="viz-select">
          ${[100, 500, 1000].map((r) => `<option value="${r}"${r === ui.reps ? ' selected' : ''}>${r}</option>`).join('')}
        </select>
        ${warnReps}
      </div>
      <div class="btn-row" style="margin-top: 4px;">
        <button class="viz-btn viz-btn-primary" id="viz2-perm-run" style="flex:1;"${running ? ' disabled' : ''}>
          ${running ? '⌛ Running…' : '🔀 Run Permutation'}
        </button>
      </div>
      <div id="viz2-perm-progress" class="formula-note" style="display:none;"></div>
      <svg class="dist" id="viz2-perm-dist"></svg>
      <div id="viz2-perm-summary" class="formula-note" style="font-size:11px;">
        ${lastResult ? formatSummary(lastResult) : 'Pick controls and run to compute a null distribution and one-sided p-value.'}
      </div>`;

    // Wire controls
    const attrSel = $('viz2-perm-attr');
    if (attrSel) attrSel.addEventListener('change', (e) => { ui.testAttr = e.target.value || null; render(); });
    const blockSel = $('viz2-perm-block');
    if (blockSel) blockSel.addEventListener('change', (e) => { ui.blockMode = e.target.value || ''; render(); });
    const statSel = $('viz2-perm-stat');
    if (statSel) statSel.addEventListener('change', (e) => { ui.stat = e.target.value || 'similarity'; render(); });
    const repsInp = $('viz2-perm-reps');
    if (repsInp) repsInp.addEventListener('change', (e) => {
      const v = parseInt(e.target.value, 10);
      if (v === 100 || v === 500 || v === 1000) ui.reps = v;
    });
    const runBtn = $('viz2-perm-run');
    if (runBtn) runBtn.addEventListener('click', () => { runPermutation().catch((err) => {
      console.error('[viz2 permutation]', err);
      running = false;
      render();
    }); });

    // (Re)draw histogram from persisted lastResult, if any.
    if (lastResult) drawDist(lastResult);
  }

  function formatSummary(res) {
    const finite = res.samples.filter((x) => isFinite(x));
    const mean = finite.length ? finite.reduce((a, b) => a + b, 0) / finite.length : NaN;
    const fmt = (x) => isFinite(x) ? x.toFixed(3) : (x === Infinity ? '∞' : 'NaN');
    const obsTxt = fmt(res.observed);
    const muTxt  = fmt(mean);
    const pTxt   = res.pval < 0.001 ? '< 0.001' : res.pval.toFixed(3);
    const statLbl = res.stat === 'similarity' ? `Similarity Index by ${esc(res.attr)}`
                  : res.stat === 'assort' ? `assortativity by ${esc(res.attr)}`
                  : res.stat === 'apl'    ? 'avg shortest path length'
                  :                         'network diameter';
    const blockLbl = !res.blockMode ? 'unblocked'
                   : res.blockMode.startsWith('node:') ? `blocked by node attr ${esc(res.blockMode.slice(5))}`
                   :                                     `blocked by edge attr ${esc(res.blockMode.slice(5))} (weights shuffled)`;
    return `Observed = <strong>${obsTxt}</strong> · Null mean = <strong>${muTxt}</strong> · p = <strong>${pTxt}</strong> (one-sided, ≥ observed) · ${blockLbl} · R = ${res.reps} · stat: ${statLbl}.`;
  }

  // ── Histogram (matches case-study colors: indigo unblocked / cyan blocked,
  // amber observed dashed line) ──────────────────────────────
  function drawDist(res) {
    const svgEl = $('viz2-perm-dist'); if (!svgEl) return;
    const svg = d3.select(svgEl);
    svg.selectAll('*').remove();
    const samples = res.samples.filter((x) => isFinite(x));
    if (!samples.length) return;

    const W = svgEl.clientWidth || 400;
    const H = svgEl.clientHeight || 160;
    const mg = { top: 14, right: 12, bottom: 28, left: 12 };
    const iW = W - mg.left - mg.right, iH = H - mg.top - mg.bottom;
    const g = svg.append('g').attr('transform', `translate(${mg.left},${mg.top})`);

    const observed = isFinite(res.observed) ? res.observed : null;
    let lo = samples[0], hi = samples[0];
    for (const v of samples) { if (v < lo) lo = v; if (v > hi) hi = v; }
    if (observed !== null) { if (observed < lo) lo = observed; if (observed > hi) hi = observed; }
    const pad = (hi - lo) * 0.06 || (Math.abs(hi) || 1) * 0.02;
    const x = d3.scaleLinear().domain([lo - pad, hi + pad]).range([0, iW]);

    const nBins = Math.min(28, Math.max(8, Math.floor(samples.length / 8)));
    const bins = d3.bin().domain(x.domain()).thresholds(x.ticks(nBins))(samples);
    const maxC = Math.max(1, ...bins.map((b) => b.length));
    const y = d3.scaleLinear().domain([0, maxC]).range([iH, 0]);

    // Color by blocking mode: unblocked → indigo (#818cf8), any blocked mode → cyan (#5eead4).
    const col = res.blockMode ? '#5eead4' : '#818cf8';

    g.selectAll('rect').data(bins).enter().append('rect')
      .attr('x', (b) => x(b.x0) + 1)
      .attr('width', (b) => Math.max(0, x(b.x1) - x(b.x0) - 2))
      .attr('y', (b) => y(b.length))
      .attr('height', (b) => iH - y(b.length))
      .attr('fill', col).attr('opacity', 0.6).attr('rx', 2);

    if (observed !== null) {
      g.append('line')
        .attr('x1', x(observed)).attr('x2', x(observed))
        .attr('y1', 0).attr('y2', iH)
        .attr('stroke', '#e8a045').attr('stroke-width', 2).attr('stroke-dasharray', '5,3');
      g.append('text')
        .attr('x', Math.min(iW - 24, x(observed) + 4)).attr('y', 10)
        .attr('fill', '#e8a045').attr('font-size', '9px')
        .attr('font-family', 'Space Mono, monospace').text('obs');
    }

    g.append('g').attr('transform', `translate(0,${iH})`)
      .call(d3.axisBottom(x).ticks(5).tickFormat((d) => d.toFixed(2)).tickSize(3))
      .call((sel) => sel.select('.domain').attr('stroke', '#2e3352'))
      .selectAll('text').attr('fill', '#a3b8a3').attr('font-size', '9px')
      .attr('font-family', 'Space Mono, monospace');

    // legend dot
    g.append('rect').attr('x', 0).attr('y', -10).attr('width', 10).attr('height', 7)
      .attr('fill', col).attr('opacity', 0.75).attr('rx', 2);
    const legend = res.blockMode ? 'Blocked null' : 'Unblocked null';
    g.append('text').attr('x', 13).attr('y', -4)
      .attr('fill', '#a3b8a3').attr('font-size', '9px')
      .attr('font-family', 'Space Mono, monospace').text(legend);
  }

  // ── The run loop ────────────────────────────────────────────
  async function runPermutation() {
    if (running) return;
    const s = NV.state;
    if (!s.graph) return;

    const attr   = ui.testAttr;
    const block  = ui.blockMode;
    const statK  = ui.stat;
    const reps   = Math.max(20, Math.min(2000, ui.reps | 0));
    const isEdgeBlock = block.startsWith('edge:');
    const blockCol    = block ? block.slice(5) : null;

    // Snapshot live state we're about to mutate. We restore in finally{}.
    const activeNodesArr = NV.activeNodes();
    const origAttrs = activeNodesArr.map((n) => (n.attrs ? n.attrs[attr] : undefined));
    const origGroups = activeNodesArr.map((n) => n.group);   // re-mirror group in assort case
    const origWeights = s.graph.links.map((l) => l.weight);

    // For edge-block mode: tag links with their block value (no-op for the
    // node-block / unblocked modes — kept inside try/finally to ensure untag).
    if (isEdgeBlock) tagLinksWithBlockVal(blockCol);

    // For the attribute-based stats (similarity / assort) we ask the utils
    // function to read either the named attr or '__group__'. If the test attr
    // IS the active group column, mirror n.group as we permute so live colors
    // don't drift between renders.
    const attrIsGroupCol = (attr === s.mapping.nodeGroup);
    const statAttrKey = (statK === 'similarity' || statK === 'assort')
      ? (attrIsGroupCol ? '__group__' : attr)
      : null;

    const progress = $('viz2-perm-progress');
    const runBtn   = $('viz2-perm-run');
    if (runBtn)   { runBtn.disabled = true; runBtn.textContent = '⌛ Running…'; }
    if (progress) { progress.style.display = ''; progress.textContent = `Running 0 / ${reps}…`; }
    running = true;

    // Always compute observed on the UNPERMUTED graph BEFORE shuffling.
    const observed = evalStat(statK, statAttrKey || attr);

    const samples = new Array(reps);
    let i = 0;
    const CHUNK = 25;

    try {
      while (i < reps) {
        const upto = Math.min(reps, i + CHUNK);
        for (; i < upto; i++) {
          // 1) permute (in place on the live graph)
          if (isEdgeBlock) {
            permuteWeightsBlockedByEdge(s.graph.links, blockCol, () => true);
          } else if (block.startsWith('node:')) {
            permuteAttrBlockedByNode(activeNodesArr, attr, blockCol);
          } else {
            permuteAttrUnblocked(activeNodesArr, attr);
          }
          // mirror group if needed
          if (!isEdgeBlock && attrIsGroupCol) {
            activeNodesArr.forEach((n) => {
              const v = n.attrs ? n.attrs[attr] : undefined;
              n.group = (v === undefined || v === null || v === '') ? null : String(v);
            });
          }
          // 2) compute statistic
          samples[i] = evalStat(statK, statAttrKey || attr);
        }
        if (progress) progress.textContent = `Running ${i} / ${reps}…`;
        // yield to the event loop
        await new Promise((r) => setTimeout(r, 0));
      }
    } finally {
      // ── RESTORE original state ───────────────────────────────
      activeNodesArr.forEach((n, k) => {
        if (n.attrs) n.attrs[attr] = origAttrs[k];
        n.group = origGroups[k];
      });
      s.graph.links.forEach((l, k) => { l.weight = origWeights[k]; });
      if (isEdgeBlock) untagLinks();
      running = false;
    }

    // p-value: one-sided, no continuity correction.
    const finite = samples.filter((v) => isFinite(v));
    const obsForP = isFinite(observed) ? observed : 0;
    const pval = finite.length
      ? finite.filter((v) => v >= obsForP).length / finite.length
      : NaN;

    lastResult = {
      observed, samples, pval,
      stat: statK, attr, blockMode: block, reps, oneSided: true
    };

    // Re-render the card to show summary + reset button state, then redraw dist.
    render();
  }

  // ── Wiring ──────────────────────────────────────────────────
  NV.on('graph-loaded', () => { lastResult = null; ui.testAttr = null; render(); });
  NV.on('view-rebuilt', () => { lastResult = null; render(); });
  NV.on('removed-changed', render);

  // First paint
  if (document.readyState !== 'loading') render();
  else document.addEventListener('DOMContentLoaded', render);
})();
