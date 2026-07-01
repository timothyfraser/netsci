// ============================================================
// SYSEN 5470 — Network Visualizer · Code Export & Playground Handoff
// A right-column card that generates a self-contained R or Python script
// reproducing the CURRENT visualizer state:
//   • loaded dataset (project sample only — uploaded CSVs are noted but not
//     re-emitted; the playground exposes read.csv / read_csv against files
//     the user pastes into it)
//   • removed nodes (delete_vertices)
//   • scenario nodes + edges (add_vertices + add_edges)
//   • centrality distribution for the metric picked in the Distributions card
//   • permutation-test block if the Permutation card has an attribute + stat set
//   • counterfactual MC block if the Counterfactuals card has a metric set
//
// Handoff: writes { lang, code, datasetKey, ts, source } to
// localStorage['netsci-playground-handoff'] then opens the R or Python
// playground in a new tab. The playgrounds pick the payload up on
// bootstrap-ready, fetch the dataset's CSVs into their WASM FS, and drop
// the code into the CodeMirror editor.
//
// Mounted at: #viz2-codeexport-body (declared in visualizer.html).
// ============================================================
(function () {
  'use strict';
  if (!window.NetSciViz2) return;
  const NV = window.NetSciViz2;
  const HANDOFF_KEY = 'netsci-playground-handoff';

  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  // Escape a JS string for safe use as an R string literal (double-quote wrapped).
  const rStr = (s) => '"' + String(s ?? '').replace(/\\/g, '\\\\').replace(/"/g, '\\"') + '"';
  // Same for a Python single-quote-wrapped string.
  const pyStr = (s) => "'" + String(s ?? '').replace(/\\/g, '\\\\').replace(/'/g, "\\'") + "'";

  // Emit an R vector literal from a JS array of values. Detects the "shape"
  // of the column (numeric / logical / character) so the resulting data.frame
  // matches what read.csv would have produced. NA'd out on null/undefined/''
  // so the loader doesn't blow up on missing values.
  function rVectorLit(values) {
    const isMissing = (v) => v === null || v === undefined || v === '';
    const allNumeric = values.every((v) => isMissing(v) || (typeof v === 'number' && Number.isFinite(v)));
    const allLogical = values.every((v) => isMissing(v) || typeof v === 'boolean');
    if (allNumeric) return 'c(' + values.map((v) => isMissing(v) ? 'NA' : String(v)).join(', ') + ')';
    if (allLogical) return 'c(' + values.map((v) => isMissing(v) ? 'NA' : (v ? 'TRUE' : 'FALSE')).join(', ') + ')';
    return 'c(' + values.map((v) => isMissing(v) ? 'NA_character_' : rStr(v)).join(', ') + ')';
  }
  // Emit `data.frame(col1 = c(...), col2 = c(...), stringsAsFactors = FALSE)`
  // for a table-of-rows + ordered column names. One line per column so it's
  // still readable in the emitted script when there are only a few dozen rows.
  function dfLiteralR(rows, cols) {
    const parts = cols.map((c) => c + ' = ' + rVectorLit(rows.map((r) => r[c])));
    return 'data.frame(\n  ' + parts.join(',\n  ') + ',\n  stringsAsFactors = FALSE\n)';
  }
  function pyListLit(values) {
    const isMissing = (v) => v === null || v === undefined || v === '';
    const allNumeric = values.every((v) => isMissing(v) || (typeof v === 'number' && Number.isFinite(v)));
    if (allNumeric) return '[' + values.map((v) => isMissing(v) ? 'None' : String(v)).join(', ') + ']';
    return '[' + values.map((v) => isMissing(v) ? 'None' : pyStr(v)).join(', ') + ']';
  }
  // `pd.DataFrame({'col1': [...], 'col2': [...]})`
  function dfLiteralPy(rows, cols) {
    const parts = cols.map((c) => pyStr(c) + ': ' + pyListLit(rows.map((r) => r[c])));
    return 'pd.DataFrame({\n    ' + parts.join(',\n    ') + '\n})';
  }

  const ui = { lang: 'r' };  // 'r' | 'py'

  // ── Snapshot the visualizer's live state ────────────────────
  // Everything the code-export needs, gathered into ONE plain object so the
  // R / Python emitters are pure serializers.
  function snapshot() {
    const s = NV.state;
    if (!s.graph) return null;
    const removed = Array.from(s.removedNodes || []);
    const scenarioNodes = (s.scenarioNodes || []).map((n) => ({
      id: n.id, label: n.label || n.id, group: n.group || ''
    }));
    const scenarioLinks = (s.scenarioLinks || []).map((l) => {
      const src = typeof l.source === 'object' ? l.source.id : l.source;
      const tgt = typeof l.target === 'object' ? l.target.id : l.target;
      return { source: src, target: tgt, weight: Number(l.weight) || 1 };
    });

    // Live-read the analysis-card dropdowns so the export mirrors exactly
    // what the user has on-screen (no monkey-patching required).
    const distMetric = ($('viz2-dist-metric') || {}).value || 'degree';
    const distGroupBy = ($('viz2-dist-groupby') || {}).value || '';
    const mcMetric = ($('viz2-mc-metric') || {}).value || '';
    const mcReps = parseInt(($('viz2-mc-reps') || {}).value || '0', 10) || 0;
    const permAttr = ($('viz2-perm-attr') || {}).value || '';
    const permStat = ($('viz2-perm-stat') || {}).value || '';
    const permReps = parseInt(($('viz2-perm-reps') || {}).value || '0', 10) || 0;
    const permBlocks = Array.from(document.querySelectorAll('.viz2-perm-block-chk:checked'))
      .map((el) => el.value);

    return {
      datasetKey: s.currentDatasetKey || null,   // null when the user uploaded custom CSVs OR used the ▶ Sample button
      directed: !!s.directed,
      weightCol: s.mapping.weight || null,
      groupCol: s.mapping.nodeGroup || null,
      nodeIdCol: s.mapping.nodeId || null,
      nodeLabelCol: s.mapping.nodeLabel || null,
      fromCol: s.mapping.from || null,
      toCol: s.mapping.to || null,
      nodeCount: s.graph.nodes.length,
      edgeCount: s.graph.links.length,
      selectedNode: s.selectedNode || null,
      removed: removed,
      scenarioNodes: scenarioNodes,
      scenarioLinks: scenarioLinks,
      // Raw CSV rows — the emitter inlines these as data.frame(...) when no
      // project dataset key is set so the code is self-contained (doesn't
      // depend on the playground having any files hydrated).
      nodeCsv: s.nodeCsv || [],
      edgeCsv: s.edgeCsv || [],
      nodeCols: s.nodeCols || [],
      edgeCols: s.edgeCols || [],
      dist: { metric: distMetric, groupBy: distGroupBy },
      mc: mcMetric ? { metric: mcMetric, reps: mcReps || 100 } : null,
      perm: permAttr ? {
        attr: permAttr, stat: permStat || 'similarity',
        reps: permReps || 100,
        blockList: permBlocks.map((tok) => {
          const kind = tok.startsWith('edge:') ? 'edge' : 'node';
          const col = tok.slice(5);
          return { kind, col };
        })
      } : null,
    };
  }

  // Reorder columns so the endpoint columns come first — igraph's
  // graph_from_data_frame / Graph.DataFrame both use the first two columns
  // as source/target. Works for any inlined data (from a sample graph, an
  // uploaded CSV, or a project dataset).
  function reorderEdgeCols(cols, fromCol, toCol) {
    if (!fromCol || !toCol) return cols;
    return [fromCol, toCol].concat(cols.filter((c) => c !== fromCol && c !== toCol));
  }
  function reorderNodeCols(cols, idCol) {
    if (!idCol) return cols;
    return [idCol].concat(cols.filter((c) => c !== idCol));
  }

  // ── R script emitter ────────────────────────────────────────
  function generateR(snap) {
    const cfg = SAMPLE_CONFIGS_LITE[snap.datasetKey];
    const dirFlag = snap.directed ? 'TRUE' : 'FALSE';
    const weight = snap.weightCol || (cfg && cfg.weight) || null;

    const lines = [];
    lines.push('# ─────────────────────────────────────────────────────');
    lines.push('# SYSEN 5470 — Reproducer emitted by the Network Visualizer');
    lines.push('# Source dataset: ' + (snap.datasetKey || '(inline sample / uploaded data)'));
    lines.push('# ' + snap.nodeCount + ' nodes · ' + snap.edgeCount + ' edges · ' + (snap.directed ? 'directed' : 'undirected'));
    lines.push('# ─────────────────────────────────────────────────────');
    lines.push('');
    lines.push('library(igraph)');
    lines.push('');

    if (cfg) {
      // Known project sample — the playground's handoff hook hydrated these CSVs into WebR's FS.
      lines.push('# Files loaded into the R playground\'s virtual FS by the handoff:');
      lines.push('#   ' + cfg.files.join('  '));
      lines.push('nodes <- read.csv(' + rStr(cfg.files[0]) + ', stringsAsFactors = FALSE)');
      lines.push('edges <- read.csv(' + rStr(cfg.files[1]) + ', stringsAsFactors = FALSE)');
    } else {
      // Sample graph or uploaded CSVs — inline the data so the script is
      // self-contained and runs anywhere without file dependencies.
      lines.push('# The visualizer was on the built-in sample or uploaded CSVs (no project');
      lines.push('# dataset), so the data is inlined below. Just run and you get the same graph.');
      const nCols = reorderNodeCols(snap.nodeCols, snap.nodeIdCol);
      const eCols = reorderEdgeCols(snap.edgeCols, snap.fromCol, snap.toCol);
      lines.push('nodes <- ' + dfLiteralR(snap.nodeCsv, nCols));
      lines.push('edges <- ' + dfLiteralR(snap.edgeCsv, eCols));
    }
    lines.push('');
    lines.push('g <- graph_from_data_frame(edges, vertices = nodes, directed = ' + dirFlag + ')');
    if (weight) lines.push('E(g)$weight <- E(g)$' + weight + '  # weight column used in the visualizer');
    lines.push('cat(sprintf("Loaded: %d vertices, %d edges\\n", vcount(g), ecount(g)))');

    // Removed nodes
    if (snap.removed.length) {
      lines.push('');
      lines.push('# ── Node removals from the visualizer ─────────────────');
      lines.push('removed_ids <- c(' + snap.removed.map(rStr).join(', ') + ')');
      lines.push('g <- delete_vertices(g, removed_ids[removed_ids %in% V(g)$name])');
      lines.push('cat(sprintf("After removals: %d vertices, %d edges\\n", vcount(g), ecount(g)))');
    }

    // Scenario nodes + edges
    if (snap.scenarioNodes.length || snap.scenarioLinks.length) {
      lines.push('');
      lines.push('# ── Scenario items added in the visualizer ────────────');
      if (snap.scenarioNodes.length) {
        lines.push('scenario_nodes <- c(' + snap.scenarioNodes.map((n) => rStr(n.id)).join(', ') + ')');
        lines.push('g <- add_vertices(g, length(scenario_nodes), name = scenario_nodes)');
      }
      if (snap.scenarioLinks.length) {
        const pairs = snap.scenarioLinks.map((l) => rStr(l.source) + ', ' + rStr(l.target)).join(', ');
        lines.push('scenario_edges <- c(' + pairs + ')');
        lines.push('g <- add_edges(g, scenario_edges' +
          (weight ? ', attr = list(weight = c(' + snap.scenarioLinks.map((l) => l.weight).join(', ') + '))' : '') + ')');
      }
    }

    // Distribution
    lines.push('');
    lines.push('# ── Centrality distribution (matching the visualizer\'s Distributions card) ──');
    const metric = snap.dist.metric;
    if (metric === 'weighted_degree') {
      lines.push('vals <- strength(g' + (weight ? ', weights = E(g)$weight' : '') + ')');
      lines.push('metric_name <- "Weighted degree"');
    } else if (metric === 'betweenness') {
      lines.push('vals <- betweenness(g, normalized = TRUE' + (weight ? ', weights = 1 / E(g)$weight' : '') + ')');
      lines.push('metric_name <- "Betweenness (normalized)"');
    } else if (metric === 'closeness') {
      lines.push('vals <- closeness(g, normalized = TRUE)');
      lines.push('metric_name <- "Closeness (normalized)"');
    } else {
      lines.push('vals <- degree(g)');
      lines.push('metric_name <- "Degree"');
    }
    lines.push('cat(sprintf("%s summary — min %.4f · median %.4f · mean %.4f · max %.4f\\n",');
    lines.push('            metric_name, min(vals), median(vals), mean(vals), max(vals)))');
    lines.push('hist(vals, breaks = 24, col = "#39FF14", border = "#0a0f0a",');
    lines.push('     main = paste0(metric_name, " distribution"), xlab = metric_name)');
    if (snap.selectedNode) {
      lines.push('# The visualizer had this node selected — overlay its observed value:');
      lines.push('sel_name <- ' + rStr(snap.selectedNode));
      lines.push('if (sel_name %in% V(g)$name) abline(v = vals[sel_name], col = "#f472b6", lwd = 2, lty = 2)');
    }

    // Permutation block
    if (snap.perm && snap.perm.attr && snap.groupCol !== null) {
      const attr = snap.perm.attr;
      const stat = snap.perm.stat;
      const reps = snap.perm.reps;
      const nodeBlocks = snap.perm.blockList.filter((b) => b.kind === 'node').map((b) => b.col);
      lines.push('');
      lines.push('# ── Permutation test (matches viz2-permutation.js — mirrors code/06_permutation) ──');
      lines.push('assort_by <- function(g, a) {');
      lines.push('  igraph::assortativity_nominal(g, types = as.integer(factor(vertex_attr(g, a))))');
      lines.push('}');
      lines.push('permute_labels <- function(g, a, block_by = NULL) {');
      lines.push('  labs <- vertex_attr(g, a)');
      lines.push('  if (is.null(block_by)) { new_labs <- sample(labs) }');
      lines.push('  else { blocks <- vertex_attr(g, block_by); new_labs <- labs;');
      lines.push('         for (b in unique(blocks)) { m <- blocks == b; new_labs[m] <- sample(labs[m]) } }');
      lines.push('  set_vertex_attr(g, a, value = new_labs)');
      lines.push('}');
      // Test statistic emission — similarity + newman + apl + diameter.
      if (stat === 'apl') lines.push('stat_fn <- function(g) mean_distance(g, directed = ' + dirFlag + ')');
      else if (stat === 'diam') lines.push('stat_fn <- function(g) diameter(g, directed = ' + dirFlag + ')');
      else if (stat === 'assort') lines.push('stat_fn <- function(g) assort_by(g, ' + rStr(attr) + ')');
      else lines.push('stat_fn <- function(g) assort_by(g, ' + rStr(attr) + ')  # (course "Similarity Index" ≈ nominal assortativity in this reproducer)');
      lines.push('observed <- stat_fn(g)');
      lines.push('cat(sprintf("Observed stat: %.4f\\n", observed))');
      lines.push('set.seed(42); R <- ' + reps + '; null_dist <- numeric(R)');
      lines.push('for (i in seq_len(R)) {');
      if (nodeBlocks.length) {
        lines.push('  g_perm <- permute_labels(g, ' + rStr(attr) + ', block_by = ' + rStr(nodeBlocks[0]) + ')');
      } else {
        lines.push('  g_perm <- permute_labels(g, ' + rStr(attr) + ')');
      }
      lines.push('  null_dist[i] <- stat_fn(g_perm)');
      lines.push('}');
      lines.push('p_right <- mean(null_dist >= observed); p_val <- min(p_right, 1 - p_right)');
      lines.push('cat(sprintf("Null: mean %.4f · sd %.4f · p (one-sided) = %.3f\\n",');
      lines.push('            mean(null_dist), sd(null_dist), p_val))');
      lines.push('hist(null_dist, breaks = 24, col = "#818cf8", border = "#0a0f0a",');
      lines.push('     main = "Permutation null distribution", xlab = "test statistic")');
      lines.push('abline(v = observed, col = "#f472b6", lwd = 2, lty = 2)');
    }

    // Monte Carlo block
    if (snap.mc && weight) {
      const reps = snap.mc.reps;
      lines.push('');
      lines.push('# ── Counterfactual Monte Carlo (mirrors code/07_counterfactual/example.R) ──');
      lines.push('# Poisson-resample edge weights R times; distribution of weighted APL.');
      lines.push('weighted_apl <- function(g) {');
      lines.push('  mean_distance(g, weights = 1 / pmax(E(g)$weight, 1), directed = ' + dirFlag + ')');
      lines.push('}');
      lines.push('set.seed(1); R <- ' + reps + '; apls <- numeric(R)');
      lines.push('base_w <- E(g)$weight');
      lines.push('for (i in seq_len(R)) {');
      lines.push('  gg <- g; E(gg)$weight <- rpois(length(base_w), lambda = pmax(base_w, 1))');
      lines.push('  apls[i] <- weighted_apl(gg)');
      lines.push('}');
      lines.push('cat(sprintf("MC APL — mean %.4f · sd %.4f · 95%% CI [%.4f, %.4f]\\n",');
      lines.push('            mean(apls), sd(apls), quantile(apls, 0.025), quantile(apls, 0.975)))');
      lines.push('hist(apls, breaks = 24, col = "#39FF14", border = "#0a0f0a",');
      lines.push('     main = "MC weighted APL", xlab = "APL (1/weight cost)")');
    }
    lines.push('');
    return lines.join('\n');
  }

  // ── Python script emitter ───────────────────────────────────
  function generatePy(snap) {
    const cfg = SAMPLE_CONFIGS_LITE[snap.datasetKey];
    const dirFlag = snap.directed ? 'True' : 'False';
    const weight = snap.weightCol || (cfg && cfg.weight) || null;

    const lines = [];
    lines.push('# ─────────────────────────────────────────────────────');
    lines.push('# SYSEN 5470 — Reproducer emitted by the Network Visualizer');
    lines.push('# Source dataset: ' + (snap.datasetKey || '(inline sample / uploaded data)'));
    lines.push('# ' + snap.nodeCount + ' nodes · ' + snap.edgeCount + ' edges · ' + (snap.directed ? 'directed' : 'undirected'));
    lines.push('# ─────────────────────────────────────────────────────');
    lines.push('');
    lines.push('import numpy as np');
    lines.push('import pandas as pd');
    lines.push('import matplotlib.pyplot as plt');
    lines.push('import igraph as ig');
    lines.push('');

    if (cfg) {
      lines.push('# Files hydrated into the Pyodide FS by the playground handoff.');
      lines.push('nodes = pd.read_csv(' + pyStr(cfg.files[0]) + ')');
      lines.push('edges = pd.read_csv(' + pyStr(cfg.files[1]) + ')');
    } else {
      lines.push('# The visualizer was on the built-in sample or uploaded CSVs (no project');
      lines.push('# dataset), so the data is inlined below. Just run and you get the same graph.');
      const nCols = reorderNodeCols(snap.nodeCols, snap.nodeIdCol);
      const eCols = reorderEdgeCols(snap.edgeCols, snap.fromCol, snap.toCol);
      lines.push('nodes = ' + dfLiteralPy(snap.nodeCsv, nCols));
      lines.push('edges = ' + dfLiteralPy(snap.edgeCsv, eCols));
    }
    lines.push('g = ig.Graph.DataFrame(edges=edges, directed=' + dirFlag + ', vertices=nodes, use_vids=False)');
    if (weight) lines.push('g.es["weight"] = edges[' + pyStr(weight) + '].tolist()');
    lines.push('print(f"Loaded: {g.vcount()} vertices, {g.ecount()} edges")');

    if (snap.removed.length) {
      lines.push('');
      lines.push('# ── Node removals from the visualizer ─────────────────');
      lines.push('removed = [' + snap.removed.map(pyStr).join(', ') + ']');
      lines.push('names = set(g.vs["name"])');
      lines.push('g.delete_vertices([v for v in removed if v in names])');
      lines.push('print(f"After removals: {g.vcount()} vertices, {g.ecount()} edges")');
    }

    if (snap.scenarioNodes.length || snap.scenarioLinks.length) {
      lines.push('');
      lines.push('# ── Scenario items added in the visualizer ────────────');
      if (snap.scenarioNodes.length) {
        lines.push('scenario_nodes = [' + snap.scenarioNodes.map((n) => pyStr(n.id)).join(', ') + ']');
        lines.push('g.add_vertices(scenario_nodes)');
      }
      if (snap.scenarioLinks.length) {
        const pairs = snap.scenarioLinks.map((l) => '(' + pyStr(l.source) + ', ' + pyStr(l.target) + ')').join(', ');
        lines.push('scenario_edges = [' + pairs + ']');
        lines.push('added = g.add_edges(scenario_edges)');
        if (weight) {
          const ws = snap.scenarioLinks.map((l) => l.weight).join(', ');
          lines.push('for e, w in zip(added, [' + ws + ']): e["weight"] = w');
        }
      }
    }

    // Distribution
    lines.push('');
    lines.push('# ── Centrality distribution (matches the visualizer\'s Distributions card) ──');
    const metric = snap.dist.metric;
    if (metric === 'weighted_degree') {
      lines.push('vals = np.array(g.strength(weights=' + (weight ? '"weight"' : 'None') + '), dtype=float)');
      lines.push('metric_name = "Weighted degree"');
    } else if (metric === 'betweenness') {
      lines.push('vals = np.array(g.betweenness(' + (weight ? 'weights=[1.0 / max(w, 1e-9) for w in g.es["weight"]]' : '') + '), dtype=float)');
      lines.push('# Brandes normalization for undirected graphs: divide by (N-1)(N-2)/2');
      lines.push('N = g.vcount(); vals = vals / max(1, (N - 1) * (N - 2) / 2)');
      lines.push('metric_name = "Betweenness (normalized)"');
    } else if (metric === 'closeness') {
      lines.push('vals = np.array(g.closeness(normalized=True), dtype=float)');
      lines.push('metric_name = "Closeness (normalized)"');
    } else {
      lines.push('vals = np.array(g.degree(), dtype=float)');
      lines.push('metric_name = "Degree"');
    }
    lines.push('print(f"{metric_name} summary — min {vals.min():.4f} · median {np.median(vals):.4f} · mean {vals.mean():.4f} · max {vals.max():.4f}")');
    lines.push('plt.figure(figsize=(6, 3.2))');
    lines.push('plt.hist(vals, bins=24, color="#39FF14", edgecolor="#0a0f0a")');
    lines.push('plt.title(f"{metric_name} distribution"); plt.xlabel(metric_name)');
    if (snap.selectedNode) {
      lines.push('sel = ' + pyStr(snap.selectedNode));
      lines.push('names = g.vs["name"]');
      lines.push('if sel in names: plt.axvline(vals[names.index(sel)], color="#f472b6", ls="--", lw=2, label="selected")');
      lines.push('plt.legend()');
    }
    lines.push('plt.tight_layout(); plt.show()');

    // Permutation block
    if (snap.perm && snap.perm.attr && snap.groupCol !== null) {
      const attr = snap.perm.attr;
      const stat = snap.perm.stat;
      const reps = snap.perm.reps;
      const nodeBlocks = snap.perm.blockList.filter((b) => b.kind === 'node').map((b) => b.col);
      lines.push('');
      lines.push('# ── Permutation test (mirrors code/06_permutation) ────');
      lines.push('def assort_by(g, a):');
      lines.push('    types = pd.Categorical(g.vs[a]).codes.tolist()');
      lines.push('    return float(g.assortativity_nominal(types=types, directed=' + dirFlag + '))');
      lines.push('def permute_labels(g, a, block_by=None, rng=None):');
      lines.push('    rng = rng or np.random.default_rng()');
      lines.push('    labs = np.array(g.vs[a])');
      lines.push('    if block_by is None:');
      lines.push('        new = rng.permutation(labs)');
      lines.push('    else:');
      lines.push('        blocks = np.array(g.vs[block_by]); new = labs.copy()');
      lines.push('        for b in np.unique(blocks):');
      lines.push('            m = blocks == b; new[m] = rng.permutation(labs[m])');
      lines.push('    g2 = g.copy(); g2.vs[a] = new.tolist(); return g2');
      if (stat === 'apl') lines.push('def stat_fn(g): return g.average_path_length(directed=' + dirFlag + ')');
      else if (stat === 'diam') lines.push('def stat_fn(g): return g.diameter(directed=' + dirFlag + ')');
      else lines.push('def stat_fn(g): return assort_by(g, ' + pyStr(attr) + ')');
      lines.push('observed = stat_fn(g); print(f"Observed stat: {observed:.4f}")');
      lines.push('rng = np.random.default_rng(42); R = ' + reps);
      lines.push('null_dist = np.empty(R)');
      lines.push('for i in range(R):');
      if (nodeBlocks.length) {
        lines.push('    gp = permute_labels(g, ' + pyStr(attr) + ', block_by=' + pyStr(nodeBlocks[0]) + ', rng=rng)');
      } else {
        lines.push('    gp = permute_labels(g, ' + pyStr(attr) + ', rng=rng)');
      }
      lines.push('    null_dist[i] = stat_fn(gp)');
      lines.push('p_right = float((null_dist >= observed).mean()); p_val = min(p_right, 1 - p_right)');
      lines.push('print(f"Null: mean {null_dist.mean():.4f} · sd {null_dist.std():.4f} · p (one-sided) = {p_val:.3f}")');
      lines.push('plt.figure(figsize=(6, 3.2))');
      lines.push('plt.hist(null_dist, bins=24, color="#818cf8", edgecolor="#0a0f0a")');
      lines.push('plt.axvline(observed, color="#f472b6", ls="--", lw=2)');
      lines.push('plt.title("Permutation null distribution"); plt.xlabel("test statistic")');
      lines.push('plt.tight_layout(); plt.show()');
    }

    // Monte Carlo block
    if (snap.mc && weight) {
      const reps = snap.mc.reps;
      lines.push('');
      lines.push('# ── Counterfactual Monte Carlo (mirrors code/07_counterfactual) ──');
      lines.push('def weighted_apl(g):');
      lines.push('    costs = [1.0 / max(w, 1) for w in g.es["weight"]]');
      lines.push('    return float(g.average_path_length(weights=costs, directed=' + dirFlag + '))');
      lines.push('rng = np.random.default_rng(1); R = ' + reps + '; apls = np.empty(R)');
      lines.push('base_w = np.maximum(np.array(g.es["weight"], dtype=float), 1.0)');
      lines.push('for i in range(R):');
      lines.push('    gg = g.copy(); gg.es["weight"] = rng.poisson(lam=base_w).tolist()');
      lines.push('    apls[i] = weighted_apl(gg)');
      lines.push('lo, hi = np.quantile(apls, [0.025, 0.975])');
      lines.push('print(f"MC APL — mean {apls.mean():.4f} · sd {apls.std():.4f} · 95% CI [{lo:.4f}, {hi:.4f}]")');
      lines.push('plt.figure(figsize=(6, 3.2))');
      lines.push('plt.hist(apls, bins=24, color="#39FF14", edgecolor="#0a0f0a")');
      lines.push('plt.title("MC weighted APL"); plt.xlabel("APL (1/weight cost)")');
      lines.push('plt.tight_layout(); plt.show()');
    }
    lines.push('');
    return lines.join('\n');
  }

  // Minimal mirror of the playground SAMPLE_CONFIGS — only the fields the
  // export module needs (file list + weight column). Kept here so the export
  // doesn't need to reach into the playground JS. Two-file loaders only —
  // datasets with a third lookup CSV drop it silently (the export never
  // touches lookup tables anyway).
  const SAMPLE_CONFIGS_LITE = {
    'karate':                { files: ['karate-nodes.csv',                'karate-edges.csv'],                weight: null },
    'lakeside':              { files: ['lakeside-nodes.csv',              'lakeside-edges.csv'],              weight: null },
    'riverdale':             { files: ['riverdale-nodes.csv',             'riverdale-edges.csv'],             weight: null },
    'supply-chain':          { files: ['supply-chain-nodes.csv',          'supply-chain-edges.csv'],          weight: 'volume_units' },
    'amazon-last-mile':      { files: ['amazon-last-mile-nodes.csv',      'amazon-last-mile-edges.csv'],      weight: 'packages' },
    'uber-manhattan':        { files: ['uber-manhattan-nodes.csv',        'uber-manhattan-edges.csv'],        weight: 'fare' },
    'semiconductor-supply':  { files: ['semiconductor-supply-nodes.csv',  'semiconductor-supply-edges.csv'],  weight: 'annual_volume' },
    'aerospace-components':  { files: ['aerospace-components-nodes.csv',  'aerospace-components-edges.csv'],  weight: 'qty_per_aircraft' },
    'mutualaid-quake':       { files: ['mutualaid-quake-nodes.csv',       'mutualaid-quake-edges.csv'],       weight: 'amount' },
    'financial-contagion':   { files: ['financial-contagion-nodes.csv',   'financial-contagion-edges.csv'],   weight: 'exposure' },
    'airline-delays':        { files: ['airline-delays-nodes.csv',        'airline-delays-edges.csv'],        weight: 'number_of_flights' },
    'power-grid':            { files: ['power-grid-nodes.csv',            'power-grid-edges.csv'],            weight: 'capacity_mw' },
    'campus-contact':        { files: ['campus-contact-nodes.csv',        'campus-contact-edges.csv'],        weight: 'contact_minutes' },
    'opensource-deps':       { files: ['opensource-deps-nodes.csv',       'opensource-deps-edges.csv'],       weight: 'import_count' },
    'trade-commodity':       { files: ['trade-commodity-nodes.csv',       'trade-commodity-edges.csv'],       weight: 'tonnes' },
    'reorg-comms':           { files: ['reorg-comms-nodes.csv',           'reorg-comms-edges.csv'],           weight: 'message_count' },
    'satellite-constellation': { files: ['satellite-constellation-nodes.csv', 'satellite-constellation-edges.csv'], weight: 'capacity_gbps' },
    'drone-components':      { files: ['drone-components-nodes.csv',      'drone-components-edges.csv'],      weight: 'coupling_strength' },
    'transit-multimodal':    { files: ['transit-multimodal-nodes.csv',    'transit-multimodal-edges.csv'],    weight: 'capacity' },
    'satellite-supply-chain':{ files: ['satellite-supply-chain-nodes.csv','satellite-supply-chain-edges.csv'],weight: 'units_per_year' },
    'aircraft-supply-chain': { files: ['aircraft-supply-chain-nodes.csv', 'aircraft-supply-chain-edges.csv'], weight: 'units_per_year' },
    'ups-ground-network':    { files: ['ups-ground-network-nodes.csv',    'ups-ground-network-edges.csv'],    weight: 'packages' },
    'ups-package-flow':      { files: ['ups-package-flow-nodes.csv',      'ups-package-flow-edges.csv'],      weight: 'weight_kg' },
    'nyc-realestate-capital':  { files: ['nyc-realestate-capital-nodes.csv',  'nyc-realestate-capital-edges.csv'],  weight: 'invested_usd' },
    'nyc-realestate-portfolio':{ files: ['nyc-realestate-portfolio-nodes.csv','nyc-realestate-portfolio-edges.csv'],weight: 'co_investment_usd' },
  };

  // ── Buttons ─────────────────────────────────────────────────
  function copyCode() {
    const pre = $('viz2-codeexport-code'); if (!pre) return;
    const t = pre.textContent || '';
    navigator.clipboard.writeText(t).then(() => flashStatus('Copied to clipboard'), () => flashStatus('Copy failed', true));
  }
  function downloadCode() {
    const pre = $('viz2-codeexport-code'); if (!pre) return;
    const t = pre.textContent || '';
    const ext = ui.lang === 'r' ? 'R' : 'py';
    const blob = new Blob([t], { type: 'text/plain;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'netsci-visualizer-reproducer.' + ext;
    document.body.appendChild(a); a.click(); a.remove();
  }
  function openInPlayground() {
    const pre = $('viz2-codeexport-code'); if (!pre) return;
    const snap = snapshot(); if (!snap) return;
    const payload = {
      lang: ui.lang,
      code: pre.textContent || '',
      datasetKey: snap.datasetKey,
      ts: Date.now(),
      source: 'visualizer',
    };
    try { localStorage.setItem(HANDOFF_KEY, JSON.stringify(payload)); }
    catch (e) { flashStatus('Could not save handoff (localStorage full?)', true); return; }
    const url = ui.lang === 'r' ? 'playground-r.html' : 'playground-py.html';
    window.open(url, '_blank');
    flashStatus('Opened in new tab — the playground picks it up when it finishes loading.');
  }
  function flashStatus(msg, isErr) {
    const el = $('viz2-codeexport-status'); if (!el) return;
    el.textContent = msg;
    el.style.color = isErr ? '#f472b6' : 'var(--green-mint)';
    clearTimeout(flashStatus._t);
    flashStatus._t = setTimeout(() => { el.textContent = ''; }, 3500);
  }

  // ── Render (only when the visualizer has a live graph) ──────
  function render() {
    const host = $('viz2-codeexport-body'); if (!host) return;
    const snap = snapshot();
    if (!snap) {
      host.innerHTML = '<div class="node-empty">Load a network to generate code.</div>';
      return;
    }
    const code = ui.lang === 'r' ? generateR(snap) : generatePy(snap);
    const bits = [];
    if (snap.removed.length)         bits.push(snap.removed.length + ' removed');
    if (snap.scenarioNodes.length)   bits.push(snap.scenarioNodes.length + ' scenario node(s)');
    if (snap.scenarioLinks.length)   bits.push(snap.scenarioLinks.length + ' scenario edge(s)');
    if (snap.perm)                   bits.push('permutation set');
    if (snap.mc)                     bits.push('MC set');
    const bitsHtml = bits.length ? ' · <span style="color:var(--grey);">' + esc(bits.join(' · ')) + '</span>' : '';
    const unloaded = !snap.datasetKey
      ? '<div class="formula-note" style="color:#fbbf24;">You uploaded custom CSVs — the export will read them by filename but the playground doesn\'t know about them. Upload the same files into the playground first, or download the .R/.py file and open it locally.</div>'
      : '';

    host.innerHTML = `
      <div class="color-by-row" style="margin-bottom:6px;">
        <label for="viz2-codeexport-lang">Language</label>
        <select id="viz2-codeexport-lang" class="viz-select">
          <option value="r"${ui.lang === 'r' ? ' selected' : ''}>R (WebR playground)</option>
          <option value="py"${ui.lang === 'py' ? ' selected' : ''}>Python (Pyodide playground)</option>
        </select>
      </div>
      <div class="formula-note" style="margin:-2px 0 6px;">
        Reproduces the current state${bitsHtml}. Regenerates automatically as you change things.
      </div>
      ${unloaded}
      <pre id="viz2-codeexport-code" style="max-height:220px;overflow:auto;padding:8px;background:rgba(5,20,10,0.6);border:1px solid var(--border-soft);border-radius:6px;font:11px/1.4 'Space Mono',monospace;color:#d1fae5;white-space:pre;">${esc(code)}</pre>
      <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:6px;align-items:center;">
        <button id="viz2-codeexport-open" class="viz-btn viz-btn-primary" style="flex:1;min-width:130px;">▶ Open in playground</button>
        <button id="viz2-codeexport-copy" class="viz-btn" title="Copy to clipboard">📋 Copy</button>
        <button id="viz2-codeexport-dl"   class="viz-btn" title="Download the script">⬇ .${ui.lang === 'r' ? 'R' : 'py'}</button>
      </div>
      <div id="viz2-codeexport-status" class="formula-note" style="margin-top:4px;min-height:14px;"></div>`;

    const langSel = $('viz2-codeexport-lang');
    if (langSel) langSel.addEventListener('change', (e) => { ui.lang = e.target.value; render(); });
    const openBtn = $('viz2-codeexport-open'); if (openBtn) openBtn.addEventListener('click', openInPlayground);
    const copyBtn = $('viz2-codeexport-copy'); if (copyBtn) copyBtn.addEventListener('click', copyCode);
    const dlBtn   = $('viz2-codeexport-dl');   if (dlBtn)   dlBtn.addEventListener('click', downloadCode);
  }

  // Re-render on every event that could change the snapshot.
  NV.on('init',            render);
  NV.on('graph-loaded',    render);
  NV.on('view-rebuilt',    render);
  NV.on('removed-changed', render);
  NV.on('scenario-changed',render);
  NV.on('node-selected',   render);
  NV.on('metrics-updated', render);

  // Also refresh when analysis-card selects change — those live in DOM and
  // don't emit events. Delegate on the whole document (cheap; only on change).
  document.addEventListener('change', (e) => {
    const t = e.target; if (!t || !t.id) return;
    if (/^viz2-(mc|perm|dist)-/.test(t.id) || t.classList.contains('viz2-perm-block-chk')) {
      render();
    }
  });

  if (document.readyState !== 'loading') render();
  else document.addEventListener('DOMContentLoaded', render);
})();
