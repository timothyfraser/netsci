// ============================================================
// SYSEN 5470 — Network Visualizer v2 · Feature D1: Scenario Editor
// Mounts: #viz2-scenarios-panel
// Wires: #btn-add-node (stage click → new node), #btn-add-edge (two node
// clicks → new edge). localStorage save/load named scenarios. Marks
// scenario nodes/edges with amber dashed styling (handled in viz2-core).
//
// IMPORTANT: scenario edits push directly into state.baseGraph + state.graph
// (the same array refs viz2-core renders from) and call computeMetrics +
// render. They never call loadGraph() or layout() — both would clobber
// existing node positions, which would defeat the "what-if on this layout"
// purpose of the editor.
// ============================================================
(function () {
  'use strict';
  if (!window.NetSciViz2) return;

  const V = window.NetSciViz2;
  const state = V.state;
  const LS_KEY = 'viz2-scenarios-v1';

  // ── localStorage helpers (Safari private mode can throw) ────
  function readSaved() {
    try {
      const raw = localStorage.getItem(LS_KEY);
      if (!raw) return [];
      const parsed = JSON.parse(raw);
      return Array.isArray(parsed) ? parsed : [];
    } catch (e) { return []; }
  }
  function writeSaved(list) {
    try { localStorage.setItem(LS_KEY, JSON.stringify(list)); return true; }
    catch (e) { return false; }
  }

  // ── DOM helpers ─────────────────────────────────────────────
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');

  function setActive(btn, on) {
    if (!btn) return;
    btn.classList.toggle('active', !!on);
  }

  // ── Graph mutation helpers ──────────────────────────────────
  // Push a scenario node into the live base + view graphs so the next
  // render() picks it up. Pinned via fx/fy so the force sim leaves it alone.
  function pushScenarioNode(sn) {
    const n = Object.assign(
      { deg: 0, weighted: 0, isScenario: true },
      sn
    );
    if (n.x !== undefined && n.fx === undefined) n.fx = n.x;
    if (n.y !== undefined && n.fy === undefined) n.fy = n.y;
    if (state.baseGraph && state.baseGraph !== state.graph) {
      if (!state.baseGraph.nodes.some((x) => x.id === n.id)) {
        state.baseGraph.nodes.push(n);
      }
    }
    if (state.graph && !state.graph.nodes.some((x) => x.id === n.id)) {
      state.graph.nodes.push(n);
    }
  }

  function pushScenarioLink(sl) {
    const w = isFinite(sl.weight) && sl.weight > 0 ? sl.weight : 1;
    const link = {
      source: sl.source, target: sl.target,
      weight: w, time: null, timeRaw: null,
      isScenario: true
    };
    if (state.baseGraph && state.baseGraph !== state.graph) {
      state.baseGraph.links.push({ ...link });
    }
    if (state.graph) state.graph.links.push(link);
  }

  // Remove every scenario node/edge from baseGraph + graph (mutating in place).
  function purgeScenarioFromGraph() {
    const drop = (g) => {
      if (!g) return;
      g.nodes = g.nodes.filter((n) => !n.isScenario);
      g.links = g.links.filter((l) => !l.isScenario);
    };
    drop(state.baseGraph);
    if (state.graph !== state.baseGraph) drop(state.graph);
  }

  function rebuildAfterScenarioChange() {
    V.computeMetrics();
    V.render();
  }

  // ── Mode toggles ────────────────────────────────────────────
  function deactivateAll() {
    state.stageClickMode = null;
    state.addEdgePending = null;
    setActive($('btn-add-node'), false);
    setActive($('btn-add-edge'), false);
  }

  function toggleAddNodeMode() {
    if (state.stageClickMode === 'add-node') {
      deactivateAll();
      V.setStatus('Add-node cancelled.', '');
      return;
    }
    deactivateAll();
    state.stageClickMode = 'add-node';
    setActive($('btn-add-node'), true);
    V.setStatus('Click an empty area of the stage to drop a scenario node.', '');
  }

  function toggleAddEdgeMode() {
    if (state.stageClickMode === 'add-edge') {
      deactivateAll();
      V.setStatus('Add-edge cancelled.', '');
      return;
    }
    deactivateAll();
    state.stageClickMode = 'add-edge';
    state.addEdgePending = null;
    setActive($('btn-add-edge'), true);
    V.setStatus('Pick the FIRST endpoint…', '');
  }

  // ── Add-node handler ────────────────────────────────────────
  V.on('stage-clicked', ({ sx, sy }) => {
    if (state.stageClickMode !== 'add-node') return;
    if (!state.graph) {
      V.setStatus('Load a network before adding scenario nodes.', 'err');
      deactivateAll();
      return;
    }
    const id = 'scenario_n_' + (state.scenarioNodes.length + 1);
    const group = state.scenarioDefaultGroup || '(scenario)';
    const sn = {
      id, label: id, group,
      isScenario: true,
      x: sx, y: sy, fx: sx, fy: sy
    };
    state.scenarioNodes.push(sn);
    pushScenarioNode(sn);
    V.emit('scenario-changed', { kind: 'node-added', id });
    rebuildAfterScenarioChange();
    renderPanel();
    V.setStatus('Added scenario node ' + id + '.', 'ok');
    deactivateAll();
  });

  // ── Add-edge handler ────────────────────────────────────────
  V.on('node-selected', ({ id }) => {
    if (state.stageClickMode !== 'add-edge') return;
    if (state.addEdgePending === null) {
      state.addEdgePending = id;
      V.setStatus('Pick the OTHER endpoint…', '');
      return;
    }
    if (id === state.addEdgePending) {
      V.setStatus('Pick a different node (no self-loops).', 'err');
      return;
    }
    const src = state.addEdgePending;
    const tgt = id;
    // Prompt for weight (default 1)
    let weight = 1;
    try {
      const ans = window.prompt('Edge weight from "' + src + '" to "' + tgt + '"?', '1');
      if (ans === null) {
        // user hit cancel — abort cleanly
        deactivateAll();
        V.setStatus('Add-edge cancelled.', '');
        return;
      }
      const n = Number(ans);
      if (isFinite(n) && n > 0) weight = n;
    } catch (e) { /* keep default */ }

    const sl = { source: src, target: tgt, weight, isScenario: true };
    state.scenarioLinks.push(sl);
    pushScenarioLink(sl);
    V.emit('scenario-changed', { kind: 'edge-added', source: src, target: tgt });
    rebuildAfterScenarioChange();
    renderPanel();
    V.setStatus('Added scenario edge ' + src + ' → ' + tgt + ' (w=' + weight + ').', 'ok');
    deactivateAll();
  });

  // ── Scenarios panel UI ──────────────────────────────────────
  function renderPanel() {
    const panel = $('viz2-scenarios-panel');
    if (!panel) return;
    // Remove any old body div (preserve the <h3> header).
    const old = panel.querySelector('.viz2-scen-body');
    if (old) old.remove();
    const placeholder = panel.querySelector('.node-empty');
    if (placeholder) placeholder.remove();

    const body = document.createElement('div');
    body.className = 'viz2-scen-body';

    const nN = state.scenarioNodes.length;
    const nE = state.scenarioLinks.length;
    const saved = readSaved();

    const summary = document.createElement('div');
    summary.style.cssText = 'font-family:var(--font-mono);font-size:11.5px;color:var(--green-mint);line-height:1.6;margin-bottom:10px;';
    summary.innerHTML =
      '<div>Unsaved scenario: ' +
        '<span style="color:#fbbf24;">n + ' + nN + '</span> scenario nodes, ' +
        '<span style="color:#fbbf24;">e + ' + nE + '</span> scenario edges.' +
      '</div>' +
      '<div style="color:var(--grey-dim);font-size:10.5px;margin-top:4px;">' +
        'Use <strong style="color:#fbbf24;">＋N</strong> / <strong style="color:#fbbf24;">＋E</strong> on the stage toolbar.' +
      '</div>';
    body.appendChild(summary);

    // Action buttons row
    const btnRow = document.createElement('div');
    btnRow.className = 'btn-row';
    btnRow.style.marginTop = '4px';

    const btnSave = document.createElement('button');
    btnSave.className = 'viz-btn viz-btn-ghost';
    btnSave.type = 'button';
    btnSave.innerHTML = '💾 SAVE';
    btnSave.addEventListener('click', onSaveScenario);
    if (nN === 0 && nE === 0) {
      btnSave.disabled = true;
      btnSave.style.opacity = '0.45';
      btnSave.style.cursor = 'not-allowed';
    }
    btnRow.appendChild(btnSave);

    const btnClear = document.createElement('button');
    btnClear.className = 'viz-btn viz-btn-danger';
    btnClear.type = 'button';
    btnClear.innerHTML = '🗑 CLEAR';
    btnClear.addEventListener('click', onClearScenario);
    if (nN === 0 && nE === 0) {
      btnClear.disabled = true;
      btnClear.style.opacity = '0.45';
      btnClear.style.cursor = 'not-allowed';
    }
    btnRow.appendChild(btnClear);

    body.appendChild(btnRow);

    // Load dropdown
    const loadRow = document.createElement('div');
    loadRow.style.cssText = 'margin-top:10px;display:flex;gap:6px;align-items:center;';
    if (saved.length) {
      const sel = document.createElement('select');
      sel.className = 'viz-select';
      sel.style.flex = '1';
      sel.innerHTML = '<option value="">📂 LOAD…</option>' +
        saved.map((s, i) =>
          '<option value="' + i + '">' + esc(s.name) +
          ' (n+' + (s.nodes ? s.nodes.length : 0) +
          ', e+' + (s.links ? s.links.length : 0) + ')</option>'
        ).join('');
      sel.addEventListener('change', (e) => {
        const idx = e.target.value;
        if (idx === '') return;
        onLoadScenario(Number(idx));
      });
      loadRow.appendChild(sel);

      const btnDel = document.createElement('button');
      btnDel.className = 'viz-btn viz-btn-neutral';
      btnDel.type = 'button';
      btnDel.title = 'Delete a saved scenario';
      btnDel.innerHTML = '🗑';
      btnDel.style.padding = '7px 10px';
      btnDel.addEventListener('click', onDeleteScenario);
      loadRow.appendChild(btnDel);
    } else {
      loadRow.innerHTML = '<div style="font-family:var(--font-mono);font-size:10.5px;color:var(--grey-dim);">No saved scenarios yet.</div>';
    }
    body.appendChild(loadRow);

    panel.appendChild(body);
  }

  function onSaveScenario() {
    if (!state.scenarioNodes.length && !state.scenarioLinks.length) {
      V.setStatus('Nothing to save — add some scenario nodes or edges first.', 'err');
      return;
    }
    let name;
    try {
      name = window.prompt('Name this scenario:', 'Scenario ' + new Date().toISOString().slice(0, 10));
    } catch (e) { name = null; }
    if (!name) return;
    name = String(name).trim();
    if (!name) return;

    // Deep-clone scenario items so future edits don't mutate the saved copy.
    const nodes = state.scenarioNodes.map((n) => JSON.parse(JSON.stringify(n)));
    const links = state.scenarioLinks.map((l) => ({
      source: typeof l.source === 'object' ? l.source.id : l.source,
      target: typeof l.target === 'object' ? l.target.id : l.target,
      weight: l.weight,
      isScenario: true
    }));

    const list = readSaved();
    list.push({ name, savedAt: Date.now(), nodes, links });
    if (writeSaved(list)) {
      V.setStatus('Saved scenario "' + name + '".', 'ok');
    } else {
      V.setStatus('Could not save (localStorage unavailable).', 'err');
    }
    renderPanel();
  }

  function onLoadScenario(idx) {
    const list = readSaved();
    const s = list[idx];
    if (!s) return;

    // Replace current scenario set with the saved one.
    purgeScenarioFromGraph();
    state.scenarioNodes = (s.nodes || []).map((n) => JSON.parse(JSON.stringify(n)));
    state.scenarioLinks = (s.links || []).map((l) => ({
      source: l.source, target: l.target,
      weight: l.weight, isScenario: true
    }));

    // Push them into the live graph(s).
    state.scenarioNodes.forEach(pushScenarioNode);
    state.scenarioLinks.forEach(pushScenarioLink);

    V.emit('scenario-changed', { kind: 'loaded', name: s.name });
    rebuildAfterScenarioChange();
    renderPanel();
    V.setStatus('Loaded scenario "' + s.name + '" (n+' +
      state.scenarioNodes.length + ', e+' + state.scenarioLinks.length + ').', 'ok');
  }

  function onDeleteScenario() {
    const list = readSaved();
    if (!list.length) return;
    const names = list.map((s, i) => (i + 1) + ') ' + s.name).join('\n');
    let pick;
    try {
      pick = window.prompt('Delete which saved scenario? Enter its number:\n' + names, '');
    } catch (e) { pick = null; }
    if (!pick) return;
    const n = Number(pick);
    if (!isFinite(n) || n < 1 || n > list.length) return;
    const removed = list.splice(n - 1, 1)[0];
    writeSaved(list);
    V.setStatus('Deleted saved scenario "' + removed.name + '".', 'ok');
    renderPanel();
  }

  function onClearScenario() {
    if (!state.scenarioNodes.length && !state.scenarioLinks.length) return;
    let ok = true;
    try { ok = window.confirm('Clear all unsaved scenario nodes & edges from the graph?'); }
    catch (e) { /* default true */ }
    if (!ok) return;
    purgeScenarioFromGraph();
    state.scenarioNodes = [];
    state.scenarioLinks = [];
    state.addEdgePending = null;
    V.emit('scenario-changed', { kind: 'cleared' });
    rebuildAfterScenarioChange();
    renderPanel();
    V.setStatus('Cleared all scenario items.', '');
  }

  // ── Lifecycle ───────────────────────────────────────────────
  // New dataset → reset scenario state. (Don't persist across switches —
  // scenarios were authored against the OLD node-id namespace.)
  V.on('graph-loaded', () => {
    state.scenarioNodes = [];
    state.scenarioLinks = [];
    state.stageClickMode = null;
    state.addEdgePending = null;
    setActive($('btn-add-node'), false);
    setActive($('btn-add-edge'), false);
    renderPanel();
  });

  // ── Wire toolbar buttons + initial panel render ─────────────
  function init() {
    const bN = $('btn-add-node');
    const bE = $('btn-add-edge');
    if (bN) bN.addEventListener('click', (e) => { e.preventDefault(); toggleAddNodeMode(); });
    if (bE) bE.addEventListener('click', (e) => { e.preventDefault(); toggleAddEdgeMode(); });
    renderPanel();
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
