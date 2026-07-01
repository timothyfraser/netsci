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
//   • Attribute to permute  — categorical node column whose labels we shuffle
//   • Block by              — multi-select checkbox panel (zero or more):
//                             • Node attribute: <c>  → shuffles within node levels
//                             • Edge attribute: <c>  → shuffles edge weights within
//                             When multiple are selected, permutations occur within
//                             the JOINT (tuple) levels of all chosen blocks.
//   • Time slice            — (all time) or a single timeRaw value; stats + perms
//                             operate on the time-filtered subgraph.
//   • Test statistic        — similarity (course default) | Newman r | APL | diameter
//   • # replicates          — 100/500/1000 (quick / solid / defensible)
//   • 🔀 Run Permutation    — runs in 25-rep chunks, yields between chunks
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
  // blockSet entries are tokens 'node:<col>' or 'edge:<col>'.
  const ui = {
    testAttr:  null,
    blockSet:  new Set(),
    stat:      'similarity',
    reps:      100,
    nBins:     24,        // histogram bin count — driven by the N bins dropdown
    timeSlice: ''         // '' = all time
  };
  let running = false;
  let blockPickerOpen = false;
  let blockCloser = null;   // currently-registered document click-away handler
  // Last result so the histogram persists across unrelated rerenders.
  let lastResult = null; // {observed, samples, pval, stat, attr, blockList, timeSlice, reps, oneSided:true}

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

  // ── Time-slice view ─────────────────────────────────────────
  // If ui.timeSlice is set, build a shallow view of state.graph with the same
  // node objects but only links whose String(timeRaw) matches. Stat functions
  // accept any {nodes, links} so they read straight from this view.
  function sliceMatches(l, slice) {
    return String(l.timeRaw) === String(slice);
  }
  function viewGraph() {
    const g = NV.state.graph;
    if (!g) return null;
    if (!ui.timeSlice) return g;
    return { nodes: g.nodes, links: g.links.filter((l) => sliceMatches(l, ui.timeSlice)) };
  }

  // ── Test statistics (run against the time-sliced view) ──────
  function statSimilarity(attr) {
    const g = viewGraph(); if (!g) return NaN;
    const ids = activeIdSet();
    const { index } = NV.utils.similarityIndex(g, attr, ids);
    return isFinite(index) ? index : NaN;
  }
  function statAssort(attr) {
    const g = viewGraph(); if (!g) return NaN;
    const ids = activeIdSet();
    const { r } = NV.utils.nominalAssortativity(g, attr, ids);
    return isFinite(r) ? r : NaN;
  }
  function statAplDiam(which) {
    const g = viewGraph(); if (!g) return NaN;
    const ids = Array.from(activeIdSet());
    const n = ids.length;
    if (n < 2) return NaN;
    const idSet = new Set(ids);
    const adj = NV.utils.buildAdj(g, idSet);
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

  // ── Block-set helpers ───────────────────────────────────────
  // Tokens are 'node:<col>' or 'edge:<col>'. Split into the two lists.
  function splitBlocks() {
    const nodeBlocks = [], edgeBlocks = [];
    ui.blockSet.forEach((tok) => {
      if (tok.startsWith('node:'))      nodeBlocks.push(tok.slice(5));
      else if (tok.startsWith('edge:')) edgeBlocks.push(tok.slice(5));
    });
    return { nodeBlocks, edgeBlocks };
  }

  // ── Permutation modes ───────────────────────────────────────
  // unblocked   : shuffle attr across all active nodes
  // node-blocks : partition by the TUPLE of all selected node-block cols and
  //               shuffle attr inside each cell. Generalises the prior single-
  //               column "blocked by node" case study mode.
  // edge-blocks : partition active links by the TUPLE of all selected edge-
  //               block cols and shuffle weights inside each cell.
  function permuteAttrUnblocked(nodes, attr) {
    const vals = nodes.map((n) => n.attrs ? n.attrs[attr] : undefined);
    NV.utils.shuffleInPlace(vals);
    nodes.forEach((n, i) => {
      if (!n.attrs) n.attrs = {};
      n.attrs[attr] = vals[i];
    });
  }
  function permuteAttrBlockedByNode(nodes, attr, blockCols) {
    // partition active nodes by the tuple of their block-col values
    const buckets = new Map();
    nodes.forEach((n) => {
      const k = blockCols.map((c) => {
        const v = n.attrs ? n.attrs[c] : undefined;
        return (v === undefined || v === null || v === '') ? '__missing__' : String(v);
      }).join('');
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
  function permuteWeightsBlockedByEdge(links, blockCols) {
    // group links by the tuple of all _blockVal_<col> tags, shuffle weights
    const buckets = new Map();
    links.forEach((l, i) => {
      const k = blockCols.map((c) => {
        const v = l._blockVals ? l._blockVals[c] : undefined;
        return (v === undefined || v === null || v === '') ? '__missing__' : String(v);
      }).join('');
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
  // Tag each link with a parallel object of {col → value} for every selected edge-block col.
  function tagLinksWithBlockVals(edgeBlockCols) {
    const s = NV.state;
    const rows = s.edgeCsv || [];
    const m = s.mapping, links = s.graph.links;
    let li = 0;
    rows.forEach((row) => {
      const a = row[m.from], b = row[m.to];
      if (a === undefined || a === null || a === '' || b === undefined || b === null || b === '') return;
      if (li < links.length) {
        const tag = {};
        edgeBlockCols.forEach((c) => { tag[c] = row[c]; });
        links[li]._blockVals = tag;
        li++;
      }
    });
  }
  function untagLinks() {
    const s = NV.state;
    if (!s.graph) return;
    s.graph.links.forEach((l) => { delete l._blockVals; });
  }

  // ── Time-slice options (distinct timeRaw values from baseGraph) ──
  function timeSliceValues() {
    const s = NV.state;
    if (!s.timeRange || !s.baseGraph) return [];
    const vals = [...new Set(s.baseGraph.links.map((l) => l.timeRaw)
      .filter((v) => v !== null && v !== undefined && v !== ''))];
    vals.sort((a, b) => {
      const na = Number(a), nb = Number(b);
      return (isFinite(na) && isFinite(nb)) ? na - nb : String(a).localeCompare(String(b));
    });
    return vals;
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

    // Drop stale block tokens whose columns no longer exist.
    Array.from(ui.blockSet).forEach((tok) => {
      const isEdge = tok.startsWith('edge:');
      const col = tok.slice(5);
      const pool = isEdge ? edgeCats : nodeCats;
      if (!pool.includes(col)) ui.blockSet.delete(tok);
    });

    // Time-slice options (only if graph has a temporal column)
    const tVals = timeSliceValues();
    if (ui.timeSlice && !tVals.includes(ui.timeSlice) &&
        !tVals.map(String).includes(String(ui.timeSlice))) ui.timeSlice = '';

    // Build block-picker checkbox rows
    const blockRows = [];
    nodeCats.forEach((c) => {
      const tok = 'node:' + c;
      const checked = ui.blockSet.has(tok) ? ' checked' : '';
      blockRows.push(
        `<label class="viz2-block-opt"><input type="checkbox" data-tok="${esc(tok)}"${checked}>` +
        `<span>${esc(c)}</span></label>`);
    });
    edgeCats.forEach((c) => {
      const tok = 'edge:' + c;
      const checked = ui.blockSet.has(tok) ? ' checked' : '';
      // Suffix only edge cols (since they shuffle weights, not labels) so the
      // user can tell apart a column name that happens to live on both sides.
      blockRows.push(
        `<label class="viz2-block-opt"><input type="checkbox" data-tok="${esc(tok)}"${checked}>` +
        `<span>${esc(c)} <em>(edge weights)</em></span></label>`);
    });
    if (!blockRows.length) {
      blockRows.push('<div class="viz2-block-empty">No categorical attributes available for blocking.</div>');
    }
    const blockSummary = (() => {
      if (!ui.blockSet.size) return '(none)';
      const labels = Array.from(ui.blockSet).map((tok) => tok.slice(5));
      return labels.join(', ');
    })();
    const blockBtnLabel = `Block by: ${blockSummary}`;
    const pickerDisplay = blockPickerOpen ? '' : 'display:none;';

    // Test-statistic dropdown — option text substitutes the chosen attr name
    // so users see WHICH attribute is being tested instead of abstract phrasing.
    const attrShow = esc(ui.testAttr || 'attribute');
    const statOpts = [
      `<option value="similarity"${ui.stat === 'similarity' ? ' selected' : ''}>Similarity Index over ${attrShow}</option>`,
      `<option value="assort"${ui.stat === 'assort' ? ' selected' : ''}>Newman assortativity over ${attrShow}</option>`,
      `<option value="apl"${ui.stat   === 'apl'    ? ' selected' : ''}>Avg shortest path length (graph-level)</option>`,
      `<option value="diam"${ui.stat  === 'diam'   ? ' selected' : ''}>Network diameter (graph-level)</option>`
    ];

    // Test-attribute dropdown
    const attrOpts = nodeCats.map((c) =>
      `<option value="${esc(c)}"${ui.testAttr === c ? ' selected' : ''}>${esc(c)}</option>`
    ).join('');

    // Time-slice dropdown (only rendered if temporal column exists)
    let timeBlock = '';
    if (tVals.length) {
      const tcol = s.mapping.time || 'time';
      const opts = [`<option value=""${ui.timeSlice === '' ? ' selected' : ''}>(all time)</option>`]
        .concat(tVals.map((v) => `<option value="${esc(v)}"${String(ui.timeSlice) === String(v) ? ' selected' : ''}>${esc(tcol)} = ${esc(v)}</option>`))
        .join('');
      timeBlock = `
      <div class="color-by-row">
        <label for="viz2-perm-time">Time slice</label>
        <select id="viz2-perm-time" class="viz-select">${opts}</select>
        <div class="formula-note" style="margin:-4px 0 0;">Stats &amp; permutations run on the time-filtered subgraph.</div>
      </div>`;
    }

    const { edgeBlocks } = splitBlocks();
    const hasEdgeBlocks = edgeBlocks.length > 0;

    const attrHint = `<div class="formula-note" style="margin:-4px 0 0;">Each replicate randomly reassigns this attribute across nodes, then recomputes the test statistic. The null distribution shows what the statistic looks like when this attribute is decoupled from the network.</div>`;
    const edgeNote = hasEdgeBlocks
      ? `<div class="formula-note" style="margin:-4px 0 0;">An edge-attribute block is selected — edge weights will also be shuffled within those blocks each replicate.</div>`
      : '';

    const pvalTip = 'p-value is one-sided: #{null_i ≥ observed} / R. No continuity correction — matches mean(null >= observed) in code/06_permutation/example.R.';

    body.innerHTML = `
      <div class="color-by-row">
        <label for="viz2-perm-attr">Attribute to permute <span style="color:var(--grey-dim); text-transform:none; letter-spacing:0;">(the column whose labels we shuffle)</span></label>
        <select id="viz2-perm-attr" class="viz-select">${attrOpts}</select>
        ${attrHint}
      </div>
      <div class="color-by-row">
        <label>Block by</label>
        <div class="viz2-block-wrap" style="position:relative;">
          <button type="button" id="viz2-perm-block-btn" class="viz2-block-btn">${esc(blockBtnLabel)}<span class="viz2-block-caret">▾</span></button>
          <div id="viz2-perm-block-picker" class="viz2-block-picker" style="${pickerDisplay}">
            ${blockRows.join('')}
          </div>
        </div>
        ${edgeNote}
      </div>
      ${timeBlock}
      <div class="color-by-row">
        <label for="viz2-perm-stat">Test statistic
          <span class="viz2-info-icon" title="${esc(pvalTip)}" aria-label="p-value details">ⓘ</span>
        </label>
        <select id="viz2-perm-stat" class="viz-select">${statOpts.join('')}</select>
      </div>
      <div class="color-by-row" style="display:flex; gap:12px; align-items:center;">
        <label for="viz2-perm-reps" style="min-width:80px;"># replicates</label>
        <select id="viz2-perm-reps" class="viz-select" style="flex:1;">
          <option value="100"${ui.reps === 100  ? ' selected' : ''}>100 (quick check)</option>
          <option value="500"${ui.reps === 500  ? ' selected' : ''}>500 (solid)</option>
          <option value="1000"${ui.reps === 1000 ? ' selected' : ''}>1000 (defensible p-value)</option>
        </select>
        <label for="viz2-perm-bins" style="margin-left:6px;">N bins</label>
        <select id="viz2-perm-bins" class="viz-select" style="flex:0 0 auto;">
          <option value="12"${ui.nBins === 12 ? ' selected' : ''}>12</option>
          <option value="24"${ui.nBins === 24 ? ' selected' : ''}>24</option>
          <option value="48"${ui.nBins === 48 ? ' selected' : ''}>48</option>
          <option value="80"${ui.nBins === 80 ? ' selected' : ''}>80</option>
        </select>
      </div>
      <div class="btn-row" style="margin-top: 4px;">
        <button class="viz-btn viz-btn-primary" id="viz2-perm-run" style="flex:1;"${running ? ' disabled' : ''}>
          ${running ? '⌛ Running…' : '🔀 Run Permutation'}
        </button>
      </div>
      <div id="viz2-perm-progress" class="formula-note" style="display:none;"></div>
      <div class="viz2-dist-wrap" style="position:relative;">
        <svg class="dist" id="viz2-perm-dist"></svg>
        <button type="button" id="viz2-perm-png" class="viz2-dist-png" title="Download chart as PNG" aria-label="Download chart">💾</button>
      </div>
      <div id="viz2-perm-summary" class="formula-note" style="font-size:11px;">
        ${lastResult ? formatSummary(lastResult) : 'Pick controls and run to compute a null distribution and one-sided p-value.'}
      </div>`;

    // Inject scoped styles for the multi-select picker, dist tooltip, and PNG btn,
    // but only once per page lifetime.
    injectPermStyles();

    // Wire controls
    const attrSel = $('viz2-perm-attr');
    if (attrSel) attrSel.addEventListener('change', (e) => { ui.testAttr = e.target.value || null; render(); });

    const blockBtn = $('viz2-perm-block-btn');
    if (blockBtn) blockBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      blockPickerOpen = !blockPickerOpen;
      const p = $('viz2-perm-block-picker');
      if (p) p.style.display = blockPickerOpen ? '' : 'none';
    });
    const picker = $('viz2-perm-block-picker');
    if (picker) {
      picker.addEventListener('click', (e) => e.stopPropagation());
      picker.querySelectorAll('input[type=checkbox]').forEach((cb) => {
        cb.addEventListener('change', (e) => {
          const tok = e.target.getAttribute('data-tok');
          if (e.target.checked) ui.blockSet.add(tok); else ui.blockSet.delete(tok);
          // Keep picker open across toggles by remembering state, then re-render
          // (the panel will re-open because blockPickerOpen is still true).
          render();
        });
      });
    }
    // Click-away closes the picker. Tear down any prior listener first so
    // re-renders (each checkbox toggle re-renders) don't stack handlers.
    if (blockCloser) { document.removeEventListener('click', blockCloser); blockCloser = null; }
    if (blockPickerOpen) {
      blockCloser = (e) => {
        const w = card.querySelector('.viz2-block-wrap');
        if (w && !w.contains(e.target)) {
          blockPickerOpen = false;
          const p = $('viz2-perm-block-picker'); if (p) p.style.display = 'none';
          document.removeEventListener('click', blockCloser);
          blockCloser = null;
        }
      };
      // defer so the current click that opened it doesn't immediately close it
      setTimeout(() => document.addEventListener('click', blockCloser), 0);
    }

    const timeSel = $('viz2-perm-time');
    if (timeSel) timeSel.addEventListener('change', (e) => { ui.timeSlice = e.target.value || ''; render(); });

    const statSel = $('viz2-perm-stat');
    if (statSel) statSel.addEventListener('change', (e) => { ui.stat = e.target.value || 'similarity'; render(); });
    const repsInp = $('viz2-perm-reps');
    if (repsInp) repsInp.addEventListener('change', (e) => {
      const v = parseInt(e.target.value, 10);
      if (v === 100 || v === 500 || v === 1000) ui.reps = v;
    });
    // N bins re-renders the LAST run's histogram (if any) so the new bin
    // count takes effect immediately without forcing a re-run.
    const binsSel = $('viz2-perm-bins');
    if (binsSel) binsSel.addEventListener('change', (e) => {
      ui.nBins = parseInt(e.target.value, 10) || 24;
      if (lastResult) drawDist(lastResult);
    });
    const runBtn = $('viz2-perm-run');
    if (runBtn) runBtn.addEventListener('click', () => { runPermutation().catch((err) => {
      console.error('[viz2 permutation]', err);
      running = false;
      render();
    }); });

    const pngBtn = $('viz2-perm-png');
    if (pngBtn) pngBtn.addEventListener('click', exportDistPng);

    // (Re)draw histogram from persisted lastResult, if any.
    if (lastResult) drawDist(lastResult);
  }

  // One-time stylesheet injection for the controls + chart adornments unique to
  // this card. Keeps the change scoped to this file (no other-file edits).
  function injectPermStyles() {
    if (document.getElementById('viz2-perm-styles')) return;
    const css = `
      .viz2-block-btn {
        width: 100%; text-align: left; padding: 8px 9px;
        font-family: var(--font-mono); font-size: 11px;
        background: rgba(5,46,22,0.55); color: var(--green-mint);
        border: 1px solid var(--green-bright); border-radius: var(--radius-sm);
        cursor: pointer; display: flex; justify-content: space-between; align-items: center;
      }
      .viz2-block-btn:hover { background: rgba(5,46,22,0.75); }
      .viz2-block-caret { color: var(--green-bright); margin-left: 8px; }
      .viz2-block-picker {
        position: absolute; top: 100%; left: 0; right: 0; z-index: 50;
        margin-top: 4px; max-height: 220px; overflow-y: auto;
        background: rgba(5,12,8,0.96); border: 1px solid var(--green-bright);
        border-radius: var(--radius-sm); padding: 6px;
        font-family: var(--font-mono); font-size: 11px; color: var(--green-mint);
        box-shadow: 0 4px 14px rgba(0,0,0,0.5);
      }
      .viz2-block-opt {
        display: flex; align-items: flex-start; gap: 8px;
        padding: 5px 6px; border-radius: 3px; cursor: pointer; line-height: 1.4;
      }
      .viz2-block-opt:hover { background: rgba(57,255,20,0.08); }
      .viz2-block-opt input[type=checkbox] { margin-top: 2px; accent-color: var(--green-bright); flex: none; }
      .viz2-block-opt em { color: var(--grey); font-style: normal; font-size: 10px; }
      .viz2-block-empty { color: var(--grey-dim); padding: 6px; font-size: 11px; }

      .viz2-dist-wrap { width: 100%; }
      .viz2-dist-png {
        position: absolute; top: 4px; right: 6px;
        width: 22px; height: 22px; padding: 0; line-height: 1;
        font-family: var(--font-mono); font-size: 14px; font-weight: 700;
        background: rgba(5,12,8,0.7); color: var(--green-bright);
        border: 1px solid var(--green-bright); border-radius: 3px;
        cursor: pointer; display: flex; align-items: center; justify-content: center;
      }
      .viz2-dist-png:hover { background: rgba(57,255,20,0.18); }

      .viz2-dist-tip {
        position: fixed; z-index: 200; pointer-events: none;
        font-family: var(--font-mono); font-size: 11px; color: var(--green-mint);
        background: rgba(5,12,8,0.95); border: 1px solid var(--green-bright);
        border-radius: 3px; padding: 5px 8px; max-width: 240px; line-height: 1.4;
        box-shadow: 0 2px 8px rgba(0,0,0,0.5);
        display: none;
      }
    `;
    const el = document.createElement('style');
    el.id = 'viz2-perm-styles';
    el.textContent = css;
    document.head.appendChild(el);
  }

  // ── Summary formatting ─────────────────────────────────────
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
    const blocks = res.blockList || [];
    const nodeB = blocks.filter((t) => t.startsWith('node:')).map((t) => esc(t.slice(5)));
    const edgeB = blocks.filter((t) => t.startsWith('edge:')).map((t) => esc(t.slice(5)));
    const blockLbl = blocks.length === 0
      ? 'unblocked'
      : 'blocked by ' + [
          nodeB.length ? `node attr ${nodeB.join(' × ')}` : null,
          edgeB.length ? `edge attr ${edgeB.join(' × ')} (weights shuffled)` : null
        ].filter(Boolean).join(' + ');
    const tLbl = res.timeSlice ? ` · time = ${esc(res.timeSlice)}` : '';
    return `Observed = <strong>${obsTxt}</strong> · Null mean = <strong>${muTxt}</strong> · p = <strong>${pTxt}</strong> (one-sided, ≥ observed) · ${blockLbl}${tLbl} · R = ${res.reps} · stat: ${statLbl}.`;
  }

  // ── Histogram (matches case-study colors: indigo unblocked / cyan blocked,
  // amber observed dashed line). Adds hover tooltip on bars + obs line. ──
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

    // User's N bins from the dropdown. Was previously a data-size heuristic;
    // now the dropdown ("Fewer / Normal / More" via 12 / 24 / 48 / 80) drives it.
    const bins = d3.bin().domain(x.domain()).thresholds(x.ticks(ui.nBins))(samples);
    const maxC = Math.max(1, ...bins.map((b) => b.length));
    const y = d3.scaleLinear().domain([0, maxC]).range([iH, 0]);

    // Color by blocking mode: any block selected → cyan, else indigo.
    const hasBlocks = (res.blockList && res.blockList.length > 0);
    const col = hasBlocks ? '#5eead4' : '#818cf8';

    // Shared tooltip element
    const tip = ensureTip();
    const showTip = (html, ev) => {
      tip.innerHTML = html;
      tip.style.display = 'block';
      const px = ev.clientX + 12, py = ev.clientY + 12;
      tip.style.left = px + 'px';
      tip.style.top  = py + 'px';
    };
    const hideTip = () => { tip.style.display = 'none'; };

    g.selectAll('rect').data(bins).enter().append('rect')
      .attr('x', (b) => x(b.x0) + 1)
      .attr('width', (b) => Math.max(0, x(b.x1) - x(b.x0) - 2))
      .attr('y', (b) => y(b.length))
      .attr('height', (b) => iH - y(b.length))
      .attr('fill', col).attr('opacity', 0.6).attr('rx', 2)
      .style('pointer-events', 'all')
      .on('mousemove', (ev, b) => {
        const html = `Null bin: [${b.x0.toFixed(3)}, ${b.x1.toFixed(3)}) — ${b.length} replicate${b.length === 1 ? '' : 's'}`;
        showTip(html, ev);
      })
      .on('mouseleave', hideTip);

    if (observed !== null) {
      // wider invisible hit-line for easier hovering on the thin dashed line
      g.append('line')
        .attr('x1', x(observed)).attr('x2', x(observed))
        .attr('y1', 0).attr('y2', iH)
        .attr('stroke', 'transparent').attr('stroke-width', 10)
        .style('pointer-events', 'stroke')
        .on('mousemove', (ev) => {
          showTip(`Observed (real network): ${observed.toFixed(3)}`, ev);
        })
        .on('mouseleave', hideTip);
      g.append('line')
        .attr('x1', x(observed)).attr('x2', x(observed))
        .attr('y1', 0).attr('y2', iH)
        .attr('stroke', '#e8a045').attr('stroke-width', 2).attr('stroke-dasharray', '5,3')
        .style('pointer-events', 'none');
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
    const legend = hasBlocks ? 'Blocked null' : 'Unblocked null';
    g.append('text').attr('x', 13).attr('y', -4)
      .attr('fill', '#a3b8a3').attr('font-size', '9px')
      .attr('font-family', 'Space Mono, monospace').text(legend);
  }

  function ensureTip() {
    let tip = document.getElementById('viz2-perm-tip');
    if (!tip) {
      tip = document.createElement('div');
      tip.id = 'viz2-perm-tip';
      tip.className = 'viz2-dist-tip';
      document.body.appendChild(tip);
    }
    return tip;
  }

  // ── Chart export (mirrors viz2-core.js exportPng) ──────────
  function exportDistPng() {
    const svgEl = $('viz2-perm-dist'); if (!svgEl) return;
    const W = svgEl.clientWidth || 400, H = svgEl.clientHeight || 160;
    const clone = svgEl.cloneNode(true);
    clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    clone.setAttribute('width', W); clone.setAttribute('height', H);
    const bg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    bg.setAttribute('width', W); bg.setAttribute('height', H); bg.setAttribute('fill', '#050a05');
    clone.insertBefore(bg, clone.firstChild);
    const data = new XMLSerializer().serializeToString(clone);
    const blob = new Blob([data], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const img = new Image();
    img.onload = () => {
      const c = document.createElement('canvas');
      const scale = 2; c.width = W * scale; c.height = H * scale;
      const ctx = c.getContext('2d');
      ctx.scale(scale, scale);
      ctx.drawImage(img, 0, 0);
      URL.revokeObjectURL(url);
      c.toBlob((b) => {
        const a = document.createElement('a');
        a.href = URL.createObjectURL(b); a.download = 'permutation-null.png';
        document.body.appendChild(a); a.click(); a.remove();
      });
    };
    img.src = url;
  }

  // ── The run loop ────────────────────────────────────────────
  async function runPermutation() {
    if (running) return;
    const s = NV.state;
    if (!s.graph) return;

    const attr   = ui.testAttr;
    const blockList = Array.from(ui.blockSet);
    const { nodeBlocks, edgeBlocks } = splitBlocks();
    const statK  = ui.stat;
    const reps   = Math.max(20, Math.min(2000, ui.reps | 0));
    const timeSlice = ui.timeSlice || '';

    // Snapshot live state we're about to mutate. We restore in finally{}.
    const activeNodesArr = NV.activeNodes();
    const origAttrs = activeNodesArr.map((n) => (n.attrs ? n.attrs[attr] : undefined));
    const origGroups = activeNodesArr.map((n) => n.group);   // re-mirror group in assort case
    const origWeights = s.graph.links.map((l) => l.weight);

    // For edge-block mode: tag links with parallel block-val maps (kept inside
    // try/finally so we always untag).
    if (edgeBlocks.length) tagLinksWithBlockVals(edgeBlocks);

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

    // Always compute observed on the UNPERMUTED graph BEFORE shuffling (note:
    // evalStat respects ui.timeSlice via viewGraph()).
    const observed = evalStat(statK, statAttrKey || attr);

    const samples = new Array(reps);
    let i = 0;
    const CHUNK = 25;

    try {
      while (i < reps) {
        const upto = Math.min(reps, i + CHUNK);
        for (; i < upto; i++) {
          // 1) permute (in place on the live graph)
          if (nodeBlocks.length) {
            permuteAttrBlockedByNode(activeNodesArr, attr, nodeBlocks);
          } else {
            permuteAttrUnblocked(activeNodesArr, attr);
          }
          if (edgeBlocks.length) {
            permuteWeightsBlockedByEdge(s.graph.links, edgeBlocks);
          }
          // mirror group if needed
          if (attrIsGroupCol) {
            activeNodesArr.forEach((n) => {
              const v = n.attrs ? n.attrs[attr] : undefined;
              n.group = (v === undefined || v === null || v === '') ? null : String(v);
            });
          }
          // 2) compute statistic (on the time-sliced view, if any)
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
      if (edgeBlocks.length) untagLinks();
      running = false;
    }

    // One-sided p-value with AUTO-DIRECTION: report the smaller tail. The
    // course default `mean(null >= observed)` (right-tail) is wrong when the
    // observed sits LEFT of the null — it would report ~0.95 when the real
    // answer is ~0.05. Compute the right-tail fraction first, then flip if
    // the observed is on the left side of the distribution.
    const finite = samples.filter((v) => isFinite(v));
    const obsForP = isFinite(observed) ? observed : 0;
    let pval = NaN;
    if (finite.length) {
      const pRight = finite.filter((v) => v >= obsForP).length / finite.length;
      pval = pRight > 0.5 ? (1 - pRight) : pRight;
    }

    lastResult = {
      observed, samples, pval,
      stat: statK, attr, blockList, timeSlice, reps, oneSided: true
    };

    // Re-render the card to show summary + reset button state, then redraw dist.
    render();
  }

  // ── Wiring ──────────────────────────────────────────────────
  NV.on('graph-loaded', () => { lastResult = null; ui.testAttr = null; ui.blockSet = new Set(); ui.timeSlice = ''; render(); });
  NV.on('view-rebuilt', () => { lastResult = null; ui.timeSlice = ''; render(); });
  NV.on('removed-changed', render);

  // First paint
  if (document.readyState !== 'loading') render();
  else document.addEventListener('DOMContentLoaded', render);
})();
