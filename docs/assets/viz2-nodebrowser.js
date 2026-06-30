// ============================================================
// SYSEN 5470 — Network Visualizer v2 · Browse Nodes
// Mounts: #viz2-node-browser-body
// Search input + sortable table (id / label / group / degree / betweenness)
// of every node in the active subgraph. Clicking a row sets state.selectedNode
// — same effect as clicking on the graph. Re-renders on metrics-updated.
// ============================================================
(function () {
  'use strict';
  if (!window.NetSciViz2) return;

  const V = window.NetSciViz2;
  const DEBOUNCE_MS = 80;

  // Local UI state — kept inside the IIFE so other modules can't trip on it.
  const ui = {
    query: '',
    sortKey: 'deg',
    sortDir: 'desc',
    debounceTimer: null,
    mounted: false
  };

  // Escape minimal HTML so user-supplied ids/labels can't break the table.
  function esc(s) {
    return String(s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  // Build the row list: filter + sort. O(N log N) with N = active nodes.
  function buildRows() {
    const g = V.state.graph;
    if (!g || !g.nodes) return { rows: [], totalActive: 0 };
    const removed = V.state.removedNodes;
    const metrics = V.state.metrics || {};
    const q = ui.query.trim().toLowerCase();

    const active = [];
    for (const n of g.nodes) {
      if (removed.has(n.id)) continue;
      active.push(n);
    }
    const totalActive = active.length;

    const filtered = q
      ? active.filter((n) => {
          const id    = String(n.id || '').toLowerCase();
          const label = String(n.label || '').toLowerCase();
          const group = String(n.group || '').toLowerCase();
          return id.indexOf(q) >= 0 || label.indexOf(q) >= 0 || group.indexOf(q) >= 0;
        })
      : active.slice();

    const dir = ui.sortDir === 'asc' ? 1 : -1;
    const key = ui.sortKey;
    filtered.sort((a, b) => {
      let va, vb;
      if (key === 'deg') {
        va = metrics[a.id]?.degree ?? 0;
        vb = metrics[b.id]?.degree ?? 0;
        return (va - vb) * dir;
      }
      if (key === 'betw') {
        va = metrics[a.id]?.betweenness ?? 0;
        vb = metrics[b.id]?.betweenness ?? 0;
        return (va - vb) * dir;
      }
      // string keys: id / label / group
      va = String(a[key] ?? '');
      vb = String(b[key] ?? '');
      return va.localeCompare(vb, undefined, { numeric: true, sensitivity: 'base' }) * dir;
    });

    return { rows: filtered, totalActive };
  }

  // Header cell with sort indicator.
  function th(key, label, num) {
    const active = ui.sortKey === key;
    const arrow = active ? (ui.sortDir === 'asc' ? ' ▲' : ' ▼') : '';
    const cls = num ? ' class="num"' : '';
    return `<th data-sortkey="${key}"${cls}>${label}${arrow}</th>`;
  }

  // Render the full panel. Cheap enough to re-do wholesale (≤100 rows).
  function renderBrowser() {
    const root = document.getElementById('viz2-node-browser-body');
    if (!root) return;
    ui.mounted = true;

    const g = V.state.graph;
    if (!g || !g.nodes || !g.nodes.length) {
      root.innerHTML = '<div class="node-empty">Load a network to browse nodes.</div>';
      return;
    }

    const { rows, totalActive } = buildRows();
    // Render every match; the .viz2-node-table-wrap caps height with a
    // scrollbar so the table doesn't blow out the card vertically.
    const shown = rows;
    const selected = V.state.selectedNode;
    const metrics = V.state.metrics || {};

    const headerRow =
      th('id', 'ID') +
      th('label', 'Label') +
      th('group', 'Group') +
      th('deg', 'Deg', true) +
      th('betw', 'Betw', true);

    const body = shown.map((n) => {
      const m = metrics[n.id] || {};
      const sel = selected === n.id ? ' selected' : '';
      return (
        `<tr class="viz2-node-row${sel}" data-id="${esc(n.id)}">` +
          `<td>${esc(n.id)}</td>` +
          `<td>${esc(n.label || n.id)}</td>` +
          `<td>${esc(n.group || '')}</td>` +
          `<td class="num">${(m.degree ?? 0)}</td>` +
          `<td class="num">${(m.betweenness ?? 0).toFixed(3)}</td>` +
        '</tr>'
      );
    }).join('');

    root.innerHTML =
      `<input type="text" class="viz2-node-search" placeholder="🔎 Type to filter by id / label / group…" value="${esc(ui.query)}">` +
      `<div class="t-label" style="margin:6px 0 2px;">${rows.length} matches (of ${totalActive} total active)</div>` +
      '<div class="viz2-node-table-wrap">' +
        '<table class="viz2-node-table">' +
          `<thead><tr>${headerRow}</tr></thead>` +
          `<tbody>${body}</tbody>` +
        '</table>' +
      '</div>';

    wireEvents(root);
  }

  // Update ONLY the .selected class on existing rows — used by the
  // node-selected event so clicking a node on the SVG highlights the table
  // row without rebuilding the whole panel (and losing input focus).
  function refreshSelectedRow() {
    const root = document.getElementById('viz2-node-browser-body');
    if (!root) return;
    const selected = V.state.selectedNode;
    root.querySelectorAll('tr.viz2-node-row').forEach((tr) => {
      if (tr.dataset.id === String(selected)) tr.classList.add('selected');
      else tr.classList.remove('selected');
    });
  }

  function wireEvents(root) {
    const input = root.querySelector('input.viz2-node-search');
    if (input) {
      input.addEventListener('input', (e) => {
        ui.query = e.target.value || '';
        if (ui.debounceTimer) clearTimeout(ui.debounceTimer);
        ui.debounceTimer = setTimeout(() => {
          ui.debounceTimer = null;
          renderBrowser();
          // Restore focus + caret after re-render.
          const fresh = document.querySelector('#viz2-node-browser-body input.viz2-node-search');
          if (fresh) {
            fresh.focus();
            const len = fresh.value.length;
            try { fresh.setSelectionRange(len, len); } catch (_) {}
          }
        }, DEBOUNCE_MS);
      });
    }

    root.querySelectorAll('th[data-sortkey]').forEach((cell) => {
      cell.addEventListener('click', () => {
        const k = cell.dataset.sortkey;
        if (ui.sortKey === k) {
          ui.sortDir = ui.sortDir === 'asc' ? 'desc' : 'asc';
        } else {
          ui.sortKey = k;
          // Numeric columns default desc, string columns default asc.
          ui.sortDir = (k === 'deg' || k === 'betw') ? 'desc' : 'asc';
        }
        renderBrowser();
      });
    });

    root.querySelectorAll('tr.viz2-node-row').forEach((tr) => {
      tr.addEventListener('click', () => {
        const id = tr.dataset.id;
        if (!id) return;
        V.state.selectedNode = id;
        V.emit('node-selected', { id });
        if (typeof V.updateNodePanel === 'function') V.updateNodePanel();
        if (typeof V.render === 'function') V.render();
        refreshSelectedRow();
      });
    });
  }

  // ── Lifecycle wiring ─────────────────────────────────────────
  V.on('graph-loaded',    () => { ui.query = ''; renderBrowser(); });
  V.on('metrics-updated', () => { if (ui.mounted) renderBrowser(); });
  V.on('removed-changed', () => { if (ui.mounted) renderBrowser(); });
  V.on('view-rebuilt',    () => { if (ui.mounted) renderBrowser(); });
  V.on('node-selected',   () => { refreshSelectedRow(); });
})();
