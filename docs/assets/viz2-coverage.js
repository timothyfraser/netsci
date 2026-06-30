// ============================================================
// SYSEN 5470 — Network Visualizer v2 · Feature C: Group Coverage + Assortativity
// Mounts: #viz2-coverage-body, #viz2-assortativity-card .card-body
// Coverage: % of each group reachable from a user-chosen reference group
// (or, if none chosen, % in the giant component). Generalized from
// supply_coverage() in code/05_supply-chain/functions.{R,py}.
// Assortativity: Newman's nominal r over the active subgraph's group column.
// ============================================================
(function () {
  'use strict';
  if (!window.NetSciViz2) return;
  const NV = window.NetSciViz2;

  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
                              .replace(/>/g, '&gt;').replace(/"/g, '&quot;');

  // Remember the user's reference-group pick across re-renders.
  let refChoice = '';   // '' = giant component, else a group value

  // ── Active node ids (Set), excluding removed ────────────────
  function activeIdSet() {
    const s = NV.state;
    const set = new Set();
    if (!s.graph) return set;
    s.graph.nodes.forEach((n) => { if (!s.removedNodes.has(n.id)) set.add(n.id); });
    return set;
  }

  // ── Coverage: group → {members, reached, frac} ──────────────
  function computeCoverage(refGroup) {
    const s = NV.state;
    if (!s.graph) return null;
    const col = s.mapping.nodeGroup;
    if (!col) return null;

    const activeIds = activeIdSet();
    if (!activeIds.size) return null;

    // Bucket active nodes by group; skip null/empty groups.
    const groups = Object.create(null);  // group → [id, id, …]
    s.graph.nodes.forEach((n) => {
      if (!activeIds.has(n.id)) return;
      const g = n.group;
      if (g === null || g === undefined || g === '') return;
      (groups[g] = groups[g] || []).push(n.id);
    });
    const groupKeys = Object.keys(groups);
    if (!groupKeys.length) return null;

    let reached;   // Set of active ids that count as "covered"
    if (refGroup === '' || refGroup === null) {
      // No reference → use the giant component (mode of component ids over
      // active nodes). Ties broken by lowest component id (deterministic).
      const counts = Object.create(null);
      activeIds.forEach((id) => {
        const c = s.metrics[id] && s.metrics[id].component;
        if (c) counts[c] = (counts[c] || 0) + 1;
      });
      let gcId = null, best = -1;
      Object.keys(counts).forEach((c) => {
        const n = counts[c];
        if (n > best || (n === best && (gcId === null || +c < +gcId))) {
          best = n; gcId = +c;
        }
      });
      reached = new Set();
      activeIds.forEach((id) => {
        const c = s.metrics[id] && s.metrics[id].component;
        if (c === gcId) reached.add(id);
      });
    } else {
      // Reference group given → BFS from every ref member, union the reached.
      const refIds = groups[refGroup] || [];
      const adj = NV.utils.buildAdj(s.graph, activeIds);
      reached = new Set();
      refIds.forEach((rid) => {
        reached.add(rid);
        const dist = NV.utils.bfs(adj, rid);
        for (const id in dist) if (dist[id] !== Infinity) reached.add(id);
      });
    }

    // Per-group coverage = |V_X ∩ reached| / |V_X_active|.
    const rows = groupKeys.map((g) => {
      const members = groups[g];
      let hit = 0;
      members.forEach((id) => { if (reached.has(id)) hit++; });
      return { group: g, members: members.length, reached: hit,
               frac: members.length ? hit / members.length : 0 };
    });
    rows.sort((a, b) => a.frac - b.frac);   // most-vulnerable first
    return rows;
  }

  // ── Coverage panel render ───────────────────────────────────
  function renderCoverage() {
    const host = $('viz2-coverage-body'); if (!host) return;
    const s = NV.state;
    if (!s.graph || !s.mapping.nodeGroup) {
      host.innerHTML = '<div class="node-empty">Pick a group column to see coverage.</div>';
      return;
    }
    // Build dropdown options from groupPalette keys (sorted), plus the
    // "no reference" option. If the previously-chosen ref disappears (e.g.
    // group column changed), reset to '' silently.
    const groupOpts = Object.keys(s.groupPalette || {}).sort();
    if (refChoice && groupOpts.indexOf(refChoice) < 0) refChoice = '';
    if (!groupOpts.length) {
      host.innerHTML = '<div class="node-empty">No groups in the active subgraph.</div>';
      return;
    }

    const rows = computeCoverage(refChoice);
    if (!rows || !rows.length) {
      host.innerHTML = '<div class="node-empty">No groups in the active subgraph.</div>';
      return;
    }

    const col = s.mapping.nodeGroup;
    const refLabel = refChoice === ''
      ? `giant component of <code>${esc(col)}</code>`
      : `reached from group <code>${esc(refChoice)}</code>`;
    const denomNote = refChoice === ''
      ? 'Coverage = share of each group that lives in the largest connected component (after removals).'
      : `Coverage = share of each group reachable (any path) from at least one <em>${esc(refChoice)}</em> node in the active subgraph.`;

    host.innerHTML = `
      <div class="color-by-row" style="margin-bottom:8px;">
        <label for="viz2-cov-ref">Reference group</label>
        <select id="viz2-cov-ref" class="viz-select">
          <option value="">(no reference — use giant component)</option>
          ${groupOpts.map((g) => `<option value="${esc(g)}"${g === refChoice ? ' selected' : ''}>${esc(g)}</option>`).join('')}
        </select>
      </div>
      <div class="formula-note" style="margin:4px 0 6px;">${denomNote}</div>
      <table class="group-table">
        <thead><tr>
          <th>Group</th><th>Members</th><th>Reached</th><th style="text-align:right;">Coverage</th>
        </tr></thead>
        <tbody>
          ${rows.map((r) => `
            <tr>
              <td>${esc(r.group)}</td>
              <td class="gv">${r.members}</td>
              <td class="gv">${r.reached}</td>
              <td class="gv">${(r.frac * 100).toFixed(1)}%</td>
            </tr>`).join('')}
        </tbody>
      </table>
      <div class="formula-note" style="margin-top:6px;">
        Showing ${rows.length} group(s) · ${refLabel} · most-vulnerable first.
      </div>`;

    const sel = $('viz2-cov-ref');
    if (sel) sel.addEventListener('change', (e) => {
      refChoice = e.target.value || '';
      renderCoverage();
    });
  }

  // ── Similarity Index gauge render ───────────────────────────
  // Uses the COURSE'S formula from docs/case-studies/permutation.html (not
  // Newman's r — that wasn't taught). Generalized to K groups in viz2-core
  // utils.similarityIndex. Range: 0 = perfectly heterogeneous (uniform
  // mixing), 1 = all edge weight on a single group-pair cell.
  function renderAssort() {
    const card = $('viz2-assortativity-card'); if (!card) return;
    const host = card.querySelector('.card-body'); if (!host) return;
    const s = NV.state;
    if (!s.graph || !s.mapping.nodeGroup) {
      host.innerHTML = '<div class="node-empty">Pick a group column to see the similarity index.</div>';
      return;
    }
    const col = s.mapping.nodeGroup;
    const { index, K, total } = NV.utils.similarityIndex(s.graph, '__group__', activeIdSet());

    let val, lbl;
    if (!isFinite(index)) {
      val = 'index = NaN';
      lbl = total === 0
        ? 'No edges with two-sided group attrs in the active subgraph.'
        : 'Need at least 2 distinct groups to compute.';
    } else {
      val = 'index = ' + index.toFixed(3);
      if      (index < 0.10) lbl = 'Mixing is close to uniform across groups';
      else if (index < 0.30) lbl = 'Some group concentration, but mostly mixed';
      else if (index < 0.60) lbl = 'Clear within-group concentration';
      else                    lbl = 'Heavily concentrated within a few group pairs';
    }

    host.innerHTML = `
      <div class="gauge-wrap">
        <div class="gauge-val">${val}</div>
        <div class="gauge-lbl">${esc(lbl)}</div>
      </div>
      <div class="formula-note">
        Course Similarity Index over <code>${esc(col)}</code> (${K} groups). Range
        <strong>0</strong> = perfectly heterogeneous (every cell at <code>1/K²</code>),
        <strong>1</strong> = all edge weight on a single group-pair cell.
        Formula: <code>(K²/(2(K²−1))) · Σ_{i,j} |p_ij − 1/K²|</code>.
        Counted ${total.toLocaleString()} unit(s) of edge weight.
      </div>`;
  }

  function renderAll() { renderCoverage(); renderAssort(); }

  // Re-render on every lifecycle event that could change the answer.
  NV.on('graph-loaded',    renderAll);
  NV.on('view-rebuilt',    renderAll);
  NV.on('metrics-updated', renderAll);
  NV.on('removed-changed', renderAll);

  // First paint if init already fired before this module loaded.
  if (document.readyState !== 'loading') renderAll();
  else document.addEventListener('DOMContentLoaded', renderAll);
})();
