// ============================================================
// SYSEN 5470 — Network Visualizer · Code Export & Playground Handoff
// A right-column card that generates a self-contained R or Python script
// reproducing the CURRENT visualizer state:
//   • loaded dataset (project sample only — uploaded CSVs are noted but not
//     re-emitted; the playground exposes read.csv / read_csv against files
//     the user pastes into it)
//   • removed nodes (delete_vertices)
//   • scenario nodes + edges (add_vertices + add_edges)
//   • [optional] centrality distribution
//   • [optional] permutation-test block if the Permutation card has an
//     attribute + stat set
//   • [optional] counterfactual MC block if the Counterfactuals card has a
//     metric set
// Each "optional" section has an include-checkbox in the card so students
// can uncheck the heavier analyses when they only want a quick script.
//
// Handoff: writes { lang, code, datasetKey, ts, source } to
// localStorage['netsci-playground-handoff'] then opens the R or Python
// playground in a new tab. The playgrounds pick the payload up on
// bootstrap-ready, fetch the dataset's CSVs into their WASM FS, and drop
// the code into the CodeMirror editor.
//
// Mounted at: #viz2-codeexport-body (declared in visualizer2.html).
// ============================================================
(function () {
  'use strict';
  if (!window.NetSciViz2) return;
  const NV = window.NetSciViz2;
  const HANDOFF_KEY = 'netsci-playground-handoff';
  const HR = '────────────────────────────────────────────────────────────';

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
  function dfLiteralPy(rows, cols) {
    const parts = cols.map((c) => pyStr(c) + ': ' + pyListLit(rows.map((r) => r[c])));
    return 'pd.DataFrame({\n    ' + parts.join(',\n    ') + '\n})';
  }

  // UI state persists across renders. The include* flags gate the
  // optional analysis sections; ui.lang picks between R / Python emitters.
  const ui = {
    lang: 'r',
    includeScenarios: true,  // Section 2 — node removals + scenario nodes/edges
    includeDist: true,       // Section 3 — centrality distribution
    includePerm: true,       // Section 4 — permutation test
    includeMc: true,         // Section 5 — counterfactual Monte Carlo
  };

  // ── Snapshot the visualizer's live state ────────────────────
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
      datasetKey: s.currentDatasetKey || null,
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
      // The "include" flags come from the checkboxes in the export card.
      // Default true; a student can uncheck to keep the emitted script
      // short + fast when they don't need that analysis. Unchecking
      // scenarios also skips the Section 2 "apply visualizer edits" block,
      // which is how a user asks for a "just the raw graph" reproducer.
      include: {
        scenarios: !!ui.includeScenarios,
        dist:      !!ui.includeDist,
        perm:      !!ui.includePerm,
        mc:        !!ui.includeMc,
      },
    };
  }

  // Reorder columns so the endpoint columns come first — igraph's
  // graph_from_data_frame / Graph.DataFrame both use the first two columns
  // as source/target.
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
    const dirWord = snap.directed ? 'directed' : 'undirected';
    const weight = snap.weightCol || (cfg && cfg.weight) || null;
    const label = snap.datasetKey || 'inline sample / uploaded data';
    const L = [];

    // ── 0. Header banner (roxygen-style, matches code/NN_<case>/example.R) ──
    L.push("#' @name reproducer.R");
    L.push("#' @title Network Visualizer Reproducer — " + label);
    L.push("#' @author (you — regenerate anytime from visualizer2.html)");
    L.push("#' @description");
    L.push("#' This script reproduces exactly what was on your screen in the");
    L.push("#' Network Visualizer at the moment you pressed \"Open in playground\":");
    L.push("#' the same dataset (or the same inline data if you were on the ▶ Sample");
    L.push("#' or an uploaded CSV), the same node removals, the same scenario items,");
    L.push("#' and whichever of the three analyses you left checked in the export card");
    L.push("#' (centrality distribution, permutation test, counterfactual MC).");
    L.push('');
    L.push('');

    // ── 0. Setup ─────────────────────────────────────────────────
    L.push('# 0. Setup ###################################################################');
    L.push('');
    L.push('## 0.1 Packages ##############################################################');
    L.push('');
    L.push('# igraph does all the graph math. The playground has dplyr / ggplot2 / readr');
    L.push('# available too if you want to extend the analysis beyond this script.');
    L.push('library(igraph)');
    L.push('');
    L.push('## 0.2 Helpers ###############################################################');
    L.push('');
    L.push('# pretty_section() prints a bordered header before each analysis block. It\'s');
    L.push('# purely cosmetic — it just makes the playground console output easier to');
    L.push('# skim by giving each section a visible divider.');
    L.push('pretty_section <- function(name) {');
    L.push('  cat("\\n", "' + HR + '", "\\n", sep = "")');
    L.push('  cat("  ", name, "\\n", sep = "")');
    L.push('  cat("' + HR + '", "\\n", sep = "")');
    L.push('}');
    L.push('');
    L.push('cat("\\n🚀 Network Visualizer reproducer — ' + label + ' (R)\\n")');
    L.push('cat("   Reproducing the on-screen state at handoff.\\n")');
    L.push('');
    L.push('');

    // ── 0.3 Data — CSV OR inline ─────────────────────────────────
    L.push('## 0.3 Data ##################################################################');
    L.push('');
    L.push('pretty_section("Loading data")');
    L.push('');
    if (cfg) {
      L.push('# The visualizer\'s handoff hook wrote these CSVs into WebR\'s virtual FS');
      L.push('# under /home/web_user/ before you ever pressed Run, so read.csv() finds');
      L.push('# them by bare filename. If you download this script and run it locally,');
      L.push('# grab the same two files from');
      L.push('#   docs/playground-data/' + cfg.files[0]);
      L.push('#   docs/playground-data/' + cfg.files[1]);
      L.push('# and drop them next to the script.');
      L.push('nodes <- read.csv(' + rStr(cfg.files[0]) + ', stringsAsFactors = FALSE)');
      L.push('edges <- read.csv(' + rStr(cfg.files[1]) + ', stringsAsFactors = FALSE)');
    } else {
      L.push('# You were on the built-in ▶ Sample (or on an uploaded CSV), so there\'s no');
      L.push('# named project dataset to read.csv() from. Instead the visualizer inlined');
      L.push('# the same rows as data.frame() calls right here — that keeps the script');
      L.push('# self-contained and lets you run it anywhere without file dependencies.');
      const nCols = reorderNodeCols(snap.nodeCols, snap.nodeIdCol);
      const eCols = reorderEdgeCols(snap.edgeCols, snap.fromCol, snap.toCol);
      L.push('nodes <- ' + dfLiteralR(snap.nodeCsv, nCols));
      L.push('');
      L.push('edges <- ' + dfLiteralR(snap.edgeCsv, eCols));
    }
    L.push('');
    L.push('cat(sprintf("✅ Loaded %d nodes and %d edges.\\n", nrow(nodes), nrow(edges)))');
    L.push('');
    L.push('');

    // ── 1. Build the graph ───────────────────────────────────────
    L.push('# 1. Build the graph #########################################################');
    L.push('');
    L.push('pretty_section("Building the graph")');
    L.push('');
    L.push('# graph_from_data_frame() treats the FIRST TWO columns of the edges table as');
    L.push('# endpoints (from -> to). Vertex metadata (kind, region, …) is joined onto');
    L.push('# each node by matching the first column of the nodelist to those endpoints.');
    L.push('# directed = ' + dirFlag + '  matches how the visualizer built this graph.');
    L.push('g <- graph_from_data_frame(edges, vertices = nodes, directed = ' + dirFlag + ')');
    L.push('');
    if (weight) {
      L.push('# The visualizer used "' + weight + '" as the edge weight. igraph looks for');
      L.push('# a slot literally named E(g)$weight, so we copy it into that slot now.');
      L.push('# Downstream functions (strength, betweenness, mean_distance) pick it up');
      L.push('# automatically once it lives there.');
      L.push('E(g)$weight <- E(g)$' + weight);
      L.push('');
    }
    L.push('cat(sprintf("🔗 Graph: %d vertices, %d edges (' + dirWord + ').\\n",');
    L.push('            vcount(g), ecount(g)))');
    L.push('');
    L.push('');

    // ── 2. Apply the visualizer's edits (only if there were any) ─
    const hasRemoval  = snap.removed.length > 0;
    const hasScenario = snap.scenarioNodes.length > 0 || snap.scenarioLinks.length > 0;
    if (snap.include.scenarios && (hasRemoval || hasScenario)) {
      L.push('# 2. Apply the visualizer\'s edits ############################################');
      L.push('');
      L.push('pretty_section("Applying visualizer edits")');
      L.push('');
      let sub = 0;

      if (hasRemoval) {
        sub++;
        L.push('## 2.' + sub + ' Node removals #########################################################');
        L.push('');
        L.push('# You clicked "Remove" on ' + snap.removed.length + ' node(s) in the Selected Node card.');
        L.push('# delete_vertices() drops both the node itself AND all edges incident to it,');
        L.push('# so downstream metrics see the same subgraph the visualizer was showing.');
        L.push('# We guard with %in% V(g)$name so the script survives if a node happens to');
        L.push('# already be missing (e.g. filtered out earlier).');
        L.push('removed_ids <- c(' + snap.removed.map(rStr).join(', ') + ')');
        L.push('g <- delete_vertices(g, removed_ids[removed_ids %in% V(g)$name])');
        L.push('');
        L.push('cat(sprintf("🧨 After %d removals: %d vertices, %d edges.\\n",');
        L.push('            length(removed_ids), vcount(g), ecount(g)))');
        L.push('');
      }

      if (hasScenario) {
        sub++;
        L.push('## 2.' + sub + ' Scenario items ########################################################');
        L.push('');
        L.push('# The +N and +E buttons on the visualizer stage added these while you');
        L.push('# hypothesized (e.g. "what if we opened a new hub here?"). add_vertices()');
        L.push('# and add_edges() apply the same items to this graph so the downstream');
        L.push('# stats include them too.');
        if (snap.scenarioNodes.length) {
          L.push('scenario_nodes <- c(' + snap.scenarioNodes.map((n) => rStr(n.id)).join(', ') + ')');
          L.push('g <- add_vertices(g, length(scenario_nodes), name = scenario_nodes)');
          L.push('cat(sprintf("➕ Added %d scenario node(s).\\n", length(scenario_nodes)))');
          L.push('');
        }
        if (snap.scenarioLinks.length) {
          const pairs = snap.scenarioLinks.map((l) => rStr(l.source) + ', ' + rStr(l.target)).join(', ');
          L.push('scenario_edges <- c(' + pairs + ')');
          if (weight) {
            L.push('g <- add_edges(g, scenario_edges,');
            L.push('               attr = list(weight = c(' + snap.scenarioLinks.map((l) => l.weight).join(', ') + ')))');
          } else {
            L.push('g <- add_edges(g, scenario_edges)');
          }
          L.push('cat(sprintf("➕ Added %d scenario edge(s).\\n", length(scenario_edges) / 2))');
          L.push('');
        }
      }
      L.push('');
    }

    // ── 3. Centrality distribution (optional) ────────────────────
    if (snap.include.dist) {
      const metric = snap.dist.metric;
      L.push('# 3. Centrality distribution #################################################');
      L.push('');
      L.push('pretty_section("Centrality distribution")');
      L.push('');
      L.push('# This is the "📊 Centrality Distributions" sub-card at the bottom of the');
      L.push('# Network Stats panel — same metric you had picked when you handed off.');
      L.push('');
      if (metric === 'weighted_degree') {
        L.push('# strength(g, weights = E(g)$weight) is degree BUT summed over the weight');
        L.push('# column instead of just counted. Same neighbor list, different accounting.');
        L.push('vals <- strength(g' + (weight ? ', weights = E(g)$weight' : '') + ')');
        L.push('metric_name <- "Weighted degree"');
      } else if (metric === 'betweenness') {
        L.push('# betweenness(v) = fraction of shortest paths between OTHER node pairs that');
        L.push('# pass through v, normalized to [0, 1]. When we weight edges, we invert');
        L.push('# the weight ( 1/w ) so "heavy" edges are treated as SHORT — same convention');
        L.push('# the visualizer uses so the two numbers line up.');
        L.push('vals <- betweenness(g, normalized = TRUE' + (weight ? ', weights = 1 / E(g)$weight' : '') + ')');
        L.push('metric_name <- "Betweenness (normalized)"');
      } else if (metric === 'closeness') {
        L.push('# closeness(v) = 1 / mean shortest-path distance from v to everyone else.');
        L.push('# High closeness = "on the way to a lot of the network."');
        L.push('vals <- closeness(g, normalized = TRUE)');
        L.push('metric_name <- "Closeness (normalized)"');
      } else {
        L.push('# degree(v) = raw count of edges incident to v. Same number that shows up');
        L.push('# in the visualizer\'s Top Degree ranking.');
        L.push('vals <- degree(g)');
        L.push('metric_name <- "Degree"');
      }
      L.push('');
      L.push('# Attach node names so we can rank them by centrality below.');
      L.push('names(vals) <- V(g)$name');
      L.push('');
      L.push('# Print the distribution\'s summary stats — matches the "min · median · mean · max"');
      L.push('# line the visualizer shows below the histogram.');
      L.push('cat(sprintf("📊 %s: min %.4f · median %.4f · mean %.4f · max %.4f\\n",');
      L.push('            metric_name, min(vals), median(vals), mean(vals), max(vals)))');
      L.push('');
      L.push('# Rank the top 3 nodes by this centrality — the same "who matters most"');
      L.push('# reading the visualizer\'s Top-N ranking gives you.');
      L.push('top3 <- head(sort(vals, decreasing = TRUE), 3)');
      L.push('cat("📝 Top 3 by ", metric_name, ":\\n", sep = "")');
      L.push('# For each of the 3 top nodes k in 1..3: print its rank, name, and score.');
      L.push('for (k in seq_along(top3)) {');
      L.push('  cat(sprintf("     %d. %-24s %.4f\\n", k, names(top3)[k], top3[k]))');
      L.push('}');
      L.push('');
      L.push('# The playground renders this hist() into its Plots tab (and to Rplots.pdf if');
      L.push('# you download the script and run it locally).');
      L.push('hist(vals, breaks = 24, col = "#39FF14", border = "#0a0f0a",');
      L.push('     main = paste0(metric_name, " distribution"), xlab = metric_name)');
      if (snap.selectedNode) {
        L.push('');
        L.push('# You had this node selected on the graph, so we overlay its observed value');
        L.push('# as a pink dashed vertical line — same treatment the visualizer uses.');
        L.push('sel_name <- ' + rStr(snap.selectedNode));
        L.push('if (sel_name %in% V(g)$name) {');
        L.push('  abline(v = vals[sel_name], col = "#f472b6", lwd = 2, lty = 2)');
        L.push('}');
      }
      L.push('');
      L.push('');
    }

    // ── 4. Permutation test (optional) ───────────────────────────
    if (snap.include.perm && snap.perm && snap.perm.attr && snap.groupCol !== null) {
      const attr = snap.perm.attr;
      const stat = snap.perm.stat;
      const reps = snap.perm.reps;
      const nodeBlocks = snap.perm.blockList.filter((b) => b.kind === 'node').map((b) => b.col);
      L.push('# 4. Permutation test ########################################################');
      L.push('');
      L.push('pretty_section("Permutation test")');
      L.push('');
      L.push('# This mirrors what the Permutation card was set up to run: shuffle a node');
      L.push('# attribute R times, recompute the test statistic each time, and compare the');
      L.push('# observed value against that null distribution. If the observed sits far');
      L.push('# in the tail, the effect is unlikely to be chance. Full walk-through lives');
      L.push('# in code/06_permutation/example.R — the two helpers below are lifted from');
      L.push('# code/06_permutation/functions.R verbatim.');
      L.push('');
      L.push('## 4.1 Helpers ###############################################################');
      L.push('');
      L.push('# assort_by() wraps igraph\'s nominal assortativity, casting to integer codes');
      L.push('# so the levels of the attribute are numbered consistently across the null.');
      L.push('assort_by <- function(g, a) {');
      L.push('  igraph::assortativity_nominal(');
      L.push('    g,');
      L.push('    types = as.integer(factor(vertex_attr(g, a)))');
      L.push('  )');
      L.push('}');
      L.push('');
      L.push('# permute_labels() returns a NEW graph whose vertex attribute `a` has been');
      L.push('# shuffled. When block_by is NULL we shuffle across all nodes; otherwise we');
      L.push('# shuffle only WITHIN each block, which preserves within-block composition');
      L.push('# and gives a stricter, more conservative null.');
      L.push('permute_labels <- function(g, a, block_by = NULL) {');
      L.push('  labs <- vertex_attr(g, a)');
      L.push('  if (is.null(block_by)) {');
      L.push('    new_labs <- sample(labs)');
      L.push('  } else {');
      L.push('    blocks <- vertex_attr(g, block_by)');
      L.push('    new_labs <- labs');
      L.push('    # For each unique block value b: pull the nodes with that block, and');
      L.push('    # reshuffle labels only within that subset. Preserves the block totals.');
      L.push('    for (b in unique(blocks)) {');
      L.push('      m <- blocks == b            # boolean mask of "this block"');
      L.push('      new_labs[m] <- sample(labs[m])   # in-block shuffle');
      L.push('    }');
      L.push('  }');
      L.push('  set_vertex_attr(g, a, value = new_labs)');
      L.push('}');
      L.push('');
      L.push('## 4.2 Observed statistic ####################################################');
      L.push('');
      L.push('# One call, one number — the value we compare the null distribution against.');
      if (stat === 'apl') {
        L.push('stat_fn <- function(g) mean_distance(g, directed = ' + dirFlag + ')');
      } else if (stat === 'diam') {
        L.push('stat_fn <- function(g) diameter(g, directed = ' + dirFlag + ')');
      } else {
        L.push('# NOTE: The visualizer\'s "Similarity Index" uses the course-specific formula');
        L.push('# from docs/case-studies/permutation.html. It shares intent with nominal');
        L.push('# assortativity but scales differently. We use assort_by() here so the');
        L.push('# reproducer stays a two-file script; if you want the exact SI, port it');
        L.push('# from viz2-core.js:similarityIndex().');
        L.push('stat_fn <- function(g) assort_by(g, ' + rStr(attr) + ')');
      }
      L.push('');
      L.push('observed <- stat_fn(g)');
      L.push('cat(sprintf("📊 Observed stat: %.4f\\n", observed))');
      L.push('');
      L.push('## 4.3 Build the null distribution ###########################################');
      L.push('');
      L.push('# Deterministic seed so a re-run of the SAME script produces the SAME numbers.');
      L.push('# Bump R to 500 or 1000 for a tighter p-value once you\'re happy with the setup.');
      L.push('set.seed(42)');
      L.push('R <- ' + reps);
      L.push('null_dist <- numeric(R)');
      L.push('');
      L.push('# For each replicate i in 1..R:');
      L.push('#   1. Shuffle the attribute across nodes (permute_labels)');
      L.push('#   2. Compute the test statistic on the shuffled graph (stat_fn)');
      L.push('#   3. Store it as the i-th entry of null_dist');
      L.push('# After R iterations, null_dist is a vector of R plausible-under-shuffling values.');
      L.push('for (i in seq_len(R)) {');
      if (nodeBlocks.length) {
        L.push('  g_perm <- permute_labels(g, ' + rStr(attr) + ', block_by = ' + rStr(nodeBlocks[0]) + ')  # step 1');
      } else {
        L.push('  g_perm <- permute_labels(g, ' + rStr(attr) + ')  # step 1: one fresh shuffled graph');
      }
      L.push('  null_dist[i] <- stat_fn(g_perm)                  # steps 2 + 3: compute + store');
      L.push('}');
      L.push('');
      L.push('## 4.4 Report + plot #########################################################');
      L.push('');
      L.push('# One-sided p-value: what fraction of the null is AT LEAST as extreme as the');
      L.push('# observed value. We flip to the smaller tail so we don\'t accidentally report');
      L.push('# ~1 when the effect is on the OTHER side of the null.');
      L.push('p_right <- mean(null_dist >= observed)');
      L.push('p_val   <- min(p_right, 1 - p_right)');
      L.push('cat(sprintf("🧪 Null: mean %.4f · sd %.4f · p (one-sided) = %.3f\\n",');
      L.push('            mean(null_dist), sd(null_dist), p_val))');
      L.push('');
      L.push('# Histogram of the null with the observed value overlaid.');
      L.push('hist(null_dist, breaks = 24, col = "#818cf8", border = "#0a0f0a",');
      L.push('     main = "Permutation null distribution", xlab = "test statistic")');
      L.push('abline(v = observed, col = "#f472b6", lwd = 2, lty = 2)');
      L.push('');
      L.push('');
    }

    // ── 5. Counterfactual Monte Carlo (optional) ─────────────────
    if (snap.include.mc && snap.mc && weight) {
      const reps = snap.mc.reps;
      L.push('# 5. Counterfactual Monte Carlo ##############################################');
      L.push('');
      L.push('pretty_section("Counterfactual Monte Carlo")');
      L.push('');
      L.push('# This mirrors what the Counterfactuals card would run: each replicate');
      L.push('# Poisson-resamples the edge weights around their observed values, rebuilds');
      L.push('# the weighted average path length, and repeats. The point isn\'t a single');
      L.push('# number — it\'s a *distribution* of APLs, from which we can read off a 95%');
      L.push('# CI and decide whether a proposed intervention actually shifts the metric');
      L.push('# beyond the noise. Full walk-through in code/07_counterfactual/example.R.');
      L.push('');
      L.push('## 5.1 Metric ################################################################');
      L.push('');
      L.push('# weighted_apl() uses cost = 1 / weight, so heavier-weighted edges count as');
      L.push('# SHORTER for path-length purposes. Matches code/07_counterfactual/functions.R');
      L.push('# and the visualizer\'s "apl_weighted" metric.');
      L.push('weighted_apl <- function(g) {');
      L.push('  mean_distance(');
      L.push('    g,');
      L.push('    weights  = 1 / pmax(E(g)$weight, 1),');
      L.push('    directed = ' + dirFlag);
      L.push('  )');
      L.push('}');
      L.push('');
      L.push('## 5.2 Run the simulation ####################################################');
      L.push('');
      L.push('# Different seed than the permutation test so the two blocks don\'t share draws.');
      L.push('set.seed(1)');
      L.push('R <- ' + reps);
      L.push('apls <- numeric(R)');
      L.push('');
      L.push('# Save the observed weight vector once — we\'ll use it as the per-edge Poisson');
      L.push('# rate every iteration. pmax(., 1) guards against zero-weight edges (Poisson');
      L.push('# with lambda = 0 is degenerate — always draws 0).');
      L.push('base_w <- E(g)$weight');
      L.push('');
      L.push('# For each replicate i in 1..R:');
      L.push('#   1. Copy the graph (assignment in R copies-on-write, so `gg <- g` is safe).');
      L.push('#   2. Draw fresh Poisson weights around the observed edge weights.');
      L.push('#   3. Compute weighted APL on the jittered graph and store it as apls[i].');
      L.push('for (i in seq_len(R)) {');
      L.push('  gg <- g                                                      # step 1');
      L.push('  E(gg)$weight <- rpois(length(base_w), lambda = pmax(base_w, 1))  # step 2');
      L.push('  apls[i] <- weighted_apl(gg)                                  # step 3');
      L.push('}');
      L.push('');
      L.push('## 5.3 Report + plot #########################################################');
      L.push('');
      L.push('# quantile(., c(0.025, 0.975)) reads off a percentile-based 95% CI.');
      L.push('ci <- quantile(apls, c(0.025, 0.975))');
      L.push('cat(sprintf("🧪 MC APL: mean %.4f · sd %.4f · 95%% CI [%.4f, %.4f]\\n",');
      L.push('            mean(apls), sd(apls), ci[1], ci[2]))');
      L.push('');
      L.push('hist(apls, breaks = 24, col = "#39FF14", border = "#0a0f0a",');
      L.push('     main = "MC weighted APL", xlab = "APL (1 / weight cost)")');
      L.push('');
      L.push('');
    }

    L.push('cat("\\n' + HR + '\\n")');
    L.push('cat("🎉 Done. Re-run for slightly different draws, or press Open in playground again after editing the visualizer.\\n")');
    L.push('cat("' + HR + '\\n")');
    L.push('');
    return L.join('\n');
  }

  // ── Python script emitter ───────────────────────────────────
  function generatePy(snap) {
    const cfg = SAMPLE_CONFIGS_LITE[snap.datasetKey];
    const dirFlag = snap.directed ? 'True' : 'False';
    const dirWord = snap.directed ? 'directed' : 'undirected';
    const weight = snap.weightCol || (cfg && cfg.weight) || null;
    const label = snap.datasetKey || 'inline sample / uploaded data';
    const L = [];

    // ── 0. Header banner ──────────────────────────────────────────
    L.push('# reproducer.py');
    L.push('# Network Visualizer Reproducer — ' + label);
    L.push('# Author: (you — regenerate anytime from visualizer2.html)');
    L.push('#');
    L.push('# This script reproduces exactly what was on your screen in the');
    L.push('# Network Visualizer at the moment you pressed "Open in playground":');
    L.push('# the same dataset (or the same inline data if you were on the');
    L.push('# ▶ Sample or an uploaded CSV), the same node removals, the same');
    L.push('# scenario items, and whichever of the three analyses you left');
    L.push('# checked in the export card (centrality, permutation, MC).');
    L.push('');
    L.push('');

    // ── 0. Setup ─────────────────────────────────────────────────
    L.push('# 0. Setup ###################################################################');
    L.push('');
    L.push('## 0.1 Packages ##############################################################');
    L.push('');
    L.push('# igraph does all the graph math. numpy + pandas are the tabular scaffolding');
    L.push('# and matplotlib renders the histograms into the playground\'s Plots tab.');
    L.push('import numpy as np');
    L.push('import pandas as pd');
    L.push('import matplotlib.pyplot as plt');
    L.push('import igraph as ig');
    L.push('');
    L.push('## 0.2 Helpers ###############################################################');
    L.push('');
    L.push('# pretty_section() prints a bordered header before each analysis block. It\'s');
    L.push('# purely cosmetic — it just makes the playground console output easier to');
    L.push('# skim by giving each section a visible divider.');
    L.push('def pretty_section(name):');
    L.push('    print("\\n" + "' + HR + '")');
    L.push('    print("  " + name)');
    L.push('    print("' + HR + '")');
    L.push('');
    L.push('print("\\n🚀 Network Visualizer reproducer — ' + label + ' (Python)")');
    L.push('print("   Reproducing the on-screen state at handoff.")');
    L.push('');
    L.push('');

    // ── 0.3 Data ─────────────────────────────────────────────────
    L.push('## 0.3 Data ##################################################################');
    L.push('');
    L.push('pretty_section("Loading data")');
    L.push('');
    if (cfg) {
      L.push('# The visualizer\'s handoff hook wrote these CSVs into Pyodide\'s virtual FS');
      L.push('# at the working directory root before you ever pressed Run, so pd.read_csv()');
      L.push('# finds them by bare filename. If you download this script and run it locally,');
      L.push('# grab the two files from');
      L.push('#   docs/playground-data/' + cfg.files[0]);
      L.push('#   docs/playground-data/' + cfg.files[1]);
      L.push('# and drop them next to the script.');
      L.push('nodes = pd.read_csv(' + pyStr(cfg.files[0]) + ')');
      L.push('edges = pd.read_csv(' + pyStr(cfg.files[1]) + ')');
    } else {
      L.push('# You were on the built-in ▶ Sample (or on an uploaded CSV), so there\'s no');
      L.push('# named project dataset to pd.read_csv() from. Instead the visualizer inlined');
      L.push('# the same rows as pd.DataFrame() calls right here — that keeps the script');
      L.push('# self-contained and lets you run it anywhere without file dependencies.');
      const nCols = reorderNodeCols(snap.nodeCols, snap.nodeIdCol);
      const eCols = reorderEdgeCols(snap.edgeCols, snap.fromCol, snap.toCol);
      L.push('nodes = ' + dfLiteralPy(snap.nodeCsv, nCols));
      L.push('');
      L.push('edges = ' + dfLiteralPy(snap.edgeCsv, eCols));
    }
    L.push('');
    L.push('print(f"✅ Loaded {len(nodes)} nodes and {len(edges)} edges.")');
    L.push('');
    L.push('');

    // ── 1. Build the graph ───────────────────────────────────────
    L.push('# 1. Build the graph #########################################################');
    L.push('');
    L.push('pretty_section("Building the graph")');
    L.push('');
    L.push('# ig.Graph.DataFrame() treats the FIRST TWO columns of the edges frame as');
    L.push('# endpoints (from -> to). Vertex metadata is joined onto each node by matching');
    L.push('# the first column of the nodelist to those endpoints. use_vids=False means');
    L.push('# "match by NAME string, not by 0-based index" — critical when your ids are');
    L.push('# strings like "H001" instead of integers.');
    L.push('# directed=' + dirFlag + '  matches how the visualizer built this graph.');
    L.push('g = ig.Graph.DataFrame(');
    L.push('    edges=edges,');
    L.push('    directed=' + dirFlag + ',');
    L.push('    vertices=nodes,');
    L.push('    use_vids=False,');
    L.push(')');
    L.push('');
    if (weight) {
      L.push('# The visualizer used "' + weight + '" as the edge weight. igraph looks for');
      L.push('# a slot literally named g.es["weight"], so we copy it into that slot now.');
      L.push('# Downstream functions (strength, betweenness, average_path_length) will pick');
      L.push('# it up automatically once it lives there.');
      L.push('g.es["weight"] = edges[' + pyStr(weight) + '].tolist()');
      L.push('');
    }
    L.push('print(f"🔗 Graph: {g.vcount()} vertices, {g.ecount()} edges (' + dirWord + ').")');
    L.push('');
    L.push('');

    // ── 2. Apply the visualizer's edits ──────────────────────────
    const hasRemoval  = snap.removed.length > 0;
    const hasScenario = snap.scenarioNodes.length > 0 || snap.scenarioLinks.length > 0;
    if (snap.include.scenarios && (hasRemoval || hasScenario)) {
      L.push('# 2. Apply the visualizer\'s edits ############################################');
      L.push('');
      L.push('pretty_section("Applying visualizer edits")');
      L.push('');
      let sub = 0;

      if (hasRemoval) {
        sub++;
        L.push('## 2.' + sub + ' Node removals #########################################################');
        L.push('');
        L.push('# You clicked "Remove" on ' + snap.removed.length + ' node(s) in the Selected Node card.');
        L.push('# delete_vertices() drops both the node itself AND all edges incident to it,');
        L.push('# so downstream metrics see the same subgraph the visualizer was showing.');
        L.push('# The list-comprehension guard survives a stale id (already-missing node).');
        L.push('removed = [' + snap.removed.map(pyStr).join(', ') + ']');
        L.push('names = set(g.vs["name"])');
        L.push('g.delete_vertices([v for v in removed if v in names])');
        L.push('');
        L.push('print(f"🧨 After {len(removed)} removals: {g.vcount()} vertices, {g.ecount()} edges.")');
        L.push('');
      }

      if (hasScenario) {
        sub++;
        L.push('## 2.' + sub + ' Scenario items ########################################################');
        L.push('');
        L.push('# The +N and +E buttons on the visualizer stage added these while you were');
        L.push('# hypothesizing (e.g. "what if we opened a new hub here?"). add_vertices()');
        L.push('# and add_edges() apply the same items to this graph so downstream stats');
        L.push('# include them too.');
        if (snap.scenarioNodes.length) {
          L.push('scenario_nodes = [' + snap.scenarioNodes.map((n) => pyStr(n.id)).join(', ') + ']');
          L.push('g.add_vertices(scenario_nodes)');
          L.push('print(f"➕ Added {len(scenario_nodes)} scenario node(s).")');
          L.push('');
        }
        if (snap.scenarioLinks.length) {
          const pairs = snap.scenarioLinks.map((l) => '(' + pyStr(l.source) + ', ' + pyStr(l.target) + ')').join(', ');
          L.push('scenario_edges = [' + pairs + ']');
          L.push('added = g.add_edges(scenario_edges)');
          if (weight) {
            const ws = snap.scenarioLinks.map((l) => l.weight).join(', ');
            L.push('# For each newly-added edge e and its intended weight w: attach w.');
            L.push('for e, w in zip(added, [' + ws + ']):');
            L.push('    e["weight"] = w');
          }
          L.push('print(f"➕ Added {len(scenario_edges)} scenario edge(s).")');
          L.push('');
        }
      }
      L.push('');
    }

    // ── 3. Centrality distribution (optional) ────────────────────
    if (snap.include.dist) {
      const metric = snap.dist.metric;
      L.push('# 3. Centrality distribution #################################################');
      L.push('');
      L.push('pretty_section("Centrality distribution")');
      L.push('');
      L.push('# This is the "📊 Centrality Distributions" sub-card at the bottom of the');
      L.push('# Network Stats panel — same metric you had picked when you handed off.');
      L.push('');
      if (metric === 'weighted_degree') {
        L.push('# g.strength(weights="weight") is degree summed over the weight column');
        L.push('# instead of counted. Same neighbor list, different accounting.');
        L.push('vals = np.array(g.strength(weights=' + (weight ? '"weight"' : 'None') + '), dtype=float)');
        L.push('metric_name = "Weighted degree"');
      } else if (metric === 'betweenness') {
        L.push('# g.betweenness(v) = fraction of shortest paths between OTHER node pairs that');
        L.push('# pass through v. When we weight edges, we invert the weight (1/w) so "heavy"');
        L.push('# edges are treated as SHORT — same convention the visualizer uses.');
        L.push('vals = np.array(g.betweenness(' + (weight ? 'weights=[1.0 / max(w, 1e-9) for w in g.es["weight"]]' : '') + '), dtype=float)');
        L.push('');
        L.push('# Brandes normalization for undirected graphs: divide by (N-1)(N-2)/2 so the');
        L.push('# result lives in [0, 1] and is comparable across networks of different N.');
        L.push('N = g.vcount()');
        L.push('vals = vals / max(1, (N - 1) * (N - 2) / 2)');
        L.push('metric_name = "Betweenness (normalized)"');
      } else if (metric === 'closeness') {
        L.push('# closeness(v) = 1 / mean shortest-path distance from v to everyone else.');
        L.push('# High closeness = "on the way to a lot of the network."');
        L.push('vals = np.array(g.closeness(normalized=True), dtype=float)');
        L.push('metric_name = "Closeness (normalized)"');
      } else {
        L.push('# g.degree() = raw count of edges incident to v. Same number that shows up');
        L.push('# in the visualizer\'s Top Degree ranking.');
        L.push('vals = np.array(g.degree(), dtype=float)');
        L.push('metric_name = "Degree"');
      }
      L.push('');
      L.push('# Print the distribution\'s summary stats — matches the "min · median · mean · max"');
      L.push('# line the visualizer shows below the histogram.');
      L.push('print(f"📊 {metric_name}: min {vals.min():.4f} · median {np.median(vals):.4f} · mean {vals.mean():.4f} · max {vals.max():.4f}")');
      L.push('');
      L.push('# Rank the top 3 nodes by this centrality — the same "who matters most"');
      L.push('# reading the visualizer\'s Top-N ranking gives you.');
      L.push('names = g.vs["name"]');
      L.push('order = np.argsort(-vals)   # indices, sorted DESCENDING by vals');
      L.push('print(f"📝 Top 3 by {metric_name}:")');
      L.push('# For each of the 3 top nodes k in 1..3: print rank, name, and score.');
      L.push('for k, idx in enumerate(order[:3], start=1):');
      L.push('    print(f"     {k}. {names[idx]:<24} {vals[idx]:.4f}")');
      L.push('');
      L.push('# plt.show() sends the figure to the playground\'s Plots tab. If you run this');
      L.push('# script locally, the same call opens a matplotlib window (or falls back to');
      L.push('# Agg + savefig when MPLBACKEND=Agg is set).');
      L.push('plt.figure(figsize=(6, 3.2))');
      L.push('plt.hist(vals, bins=24, color="#39FF14", edgecolor="#0a0f0a")');
      L.push('plt.title(f"{metric_name} distribution")');
      L.push('plt.xlabel(metric_name)');
      if (snap.selectedNode) {
        L.push('');
        L.push('# You had this node selected on the graph, so we overlay its observed value');
        L.push('# as a pink dashed vertical line — same treatment the visualizer uses.');
        L.push('sel = ' + pyStr(snap.selectedNode));
        L.push('if sel in names:');
        L.push('    plt.axvline(vals[names.index(sel)], color="#f472b6", ls="--", lw=2, label="selected")');
        L.push('    plt.legend()');
      }
      L.push('plt.tight_layout()');
      L.push('plt.show()');
      L.push('');
      L.push('');
    }

    // ── 4. Permutation test (optional) ───────────────────────────
    if (snap.include.perm && snap.perm && snap.perm.attr && snap.groupCol !== null) {
      const attr = snap.perm.attr;
      const stat = snap.perm.stat;
      const reps = snap.perm.reps;
      const nodeBlocks = snap.perm.blockList.filter((b) => b.kind === 'node').map((b) => b.col);
      L.push('# 4. Permutation test ########################################################');
      L.push('');
      L.push('pretty_section("Permutation test")');
      L.push('');
      L.push('# This mirrors what the Permutation card was set up to run: shuffle a node');
      L.push('# attribute R times, recompute the test statistic each time, and compare');
      L.push('# the observed value against that null distribution. If the observed sits');
      L.push('# far in the tail, the effect is unlikely to be chance. Full walk-through');
      L.push('# in code/06_permutation/example.py — the two helpers below are lifted from');
      L.push('# code/06_permutation/functions.py verbatim.');
      L.push('');
      L.push('## 4.1 Helpers ###############################################################');
      L.push('');
      L.push('# assort_by() wraps igraph\'s nominal assortativity, casting categories to');
      L.push('# integer codes so levels are numbered consistently across the null draws.');
      L.push('def assort_by(g, a):');
      L.push('    types = pd.Categorical(g.vs[a]).codes.tolist()');
      L.push('    return float(g.assortativity_nominal(types=types, directed=' + dirFlag + '))');
      L.push('');
      L.push('# permute_labels() returns a NEW graph whose vertex attribute a has been');
      L.push('# shuffled. block_by=None shuffles across all nodes; naming a block_by column');
      L.push('# shuffles only WITHIN each block, which preserves within-block composition');
      L.push('# and gives a stricter null.');
      L.push('def permute_labels(g, a, block_by=None, rng=None):');
      L.push('    rng = rng or np.random.default_rng()');
      L.push('    labs = np.array(g.vs[a])');
      L.push('    if block_by is None:');
      L.push('        new_labs = rng.permutation(labs)');
      L.push('    else:');
      L.push('        blocks = np.array(g.vs[block_by])');
      L.push('        new_labs = labs.copy()');
      L.push('        # For each unique block value b: pull the nodes with that block,');
      L.push('        # and reshuffle labels only within that subset.');
      L.push('        for b in np.unique(blocks):');
      L.push('            m = blocks == b                       # boolean mask of "this block"');
      L.push('            new_labs[m] = rng.permutation(labs[m])   # in-block shuffle');
      L.push('    g2 = g.copy()');
      L.push('    g2.vs[a] = new_labs.tolist()');
      L.push('    return g2');
      L.push('');
      L.push('## 4.2 Observed statistic ####################################################');
      L.push('');
      L.push('# One call, one number — the value we compare the null distribution against.');
      if (stat === 'apl') {
        L.push('def stat_fn(g):');
        L.push('    return g.average_path_length(directed=' + dirFlag + ')');
      } else if (stat === 'diam') {
        L.push('def stat_fn(g):');
        L.push('    return g.diameter(directed=' + dirFlag + ')');
      } else {
        L.push('# NOTE: The visualizer\'s "Similarity Index" is a course-specific formula.');
        L.push('# It shares intent with nominal assortativity but scales differently. We');
        L.push('# use assort_by() here so the reproducer stays a two-file script; port');
        L.push('# viz2-core.js:similarityIndex() if you want the exact SI.');
        L.push('def stat_fn(g):');
        L.push('    return assort_by(g, ' + pyStr(attr) + ')');
      }
      L.push('');
      L.push('observed = stat_fn(g)');
      L.push('print(f"📊 Observed stat: {observed:.4f}")');
      L.push('');
      L.push('## 4.3 Build the null distribution ###########################################');
      L.push('');
      L.push('# Deterministic seed so a re-run of the SAME script produces the SAME numbers.');
      L.push('# Bump R to 500 or 1000 for a tighter p-value once you\'re happy with the setup.');
      L.push('rng = np.random.default_rng(42)');
      L.push('R = ' + reps);
      L.push('null_dist = np.empty(R)');
      L.push('');
      L.push('# For each replicate i in 0..R-1:');
      L.push('#   1. Shuffle the attribute across nodes (permute_labels)');
      L.push('#   2. Compute the test statistic on the shuffled graph (stat_fn)');
      L.push('#   3. Store it as the i-th entry of null_dist');
      L.push('# After R iterations, null_dist is a length-R vector of plausible-under-shuffling values.');
      L.push('for i in range(R):');
      if (nodeBlocks.length) {
        L.push('    gp = permute_labels(g, ' + pyStr(attr) + ', block_by=' + pyStr(nodeBlocks[0]) + ', rng=rng)  # step 1');
      } else {
        L.push('    gp = permute_labels(g, ' + pyStr(attr) + ', rng=rng)  # step 1: one fresh shuffled graph');
      }
      L.push('    null_dist[i] = stat_fn(gp)                       # steps 2 + 3: compute + store');
      L.push('');
      L.push('## 4.4 Report + plot #########################################################');
      L.push('');
      L.push('# One-sided p-value: what fraction of the null is AT LEAST as extreme as the');
      L.push('# observed value. We flip to the smaller tail so we don\'t report ~1 when');
      L.push('# the effect is on the OTHER side of the null.');
      L.push('p_right = float((null_dist >= observed).mean())');
      L.push('p_val = min(p_right, 1 - p_right)');
      L.push('print(f"🧪 Null: mean {null_dist.mean():.4f} · sd {null_dist.std():.4f} · p (one-sided) = {p_val:.3f}")');
      L.push('');
      L.push('plt.figure(figsize=(6, 3.2))');
      L.push('plt.hist(null_dist, bins=24, color="#818cf8", edgecolor="#0a0f0a")');
      L.push('plt.axvline(observed, color="#f472b6", ls="--", lw=2)');
      L.push('plt.title("Permutation null distribution")');
      L.push('plt.xlabel("test statistic")');
      L.push('plt.tight_layout()');
      L.push('plt.show()');
      L.push('');
      L.push('');
    }

    // ── 5. Counterfactual Monte Carlo (optional) ─────────────────
    if (snap.include.mc && snap.mc && weight) {
      const reps = snap.mc.reps;
      L.push('# 5. Counterfactual Monte Carlo ##############################################');
      L.push('');
      L.push('pretty_section("Counterfactual Monte Carlo")');
      L.push('');
      L.push('# This mirrors what the Counterfactuals card would run: each replicate');
      L.push('# Poisson-resamples the edge weights around their observed values, rebuilds');
      L.push('# the weighted average path length, and repeats. The point isn\'t a single');
      L.push('# number — it\'s a *distribution* of APLs, from which we read off a 95% CI');
      L.push('# and decide whether a proposed intervention actually shifts the metric');
      L.push('# beyond the noise. Full walk-through in code/07_counterfactual/example.py.');
      L.push('');
      L.push('## 5.1 Metric ################################################################');
      L.push('');
      L.push('# weighted_apl() uses cost = 1 / weight, so heavier-weighted edges count as');
      L.push('# SHORTER for path-length purposes. Matches code/07_counterfactual/functions.py');
      L.push('# and the visualizer\'s "apl_weighted" metric.');
      L.push('def weighted_apl(g):');
      L.push('    costs = [1.0 / max(w, 1) for w in g.es["weight"]]');
      L.push('    return float(g.average_path_length(weights=costs, directed=' + dirFlag + '))');
      L.push('');
      L.push('## 5.2 Run the simulation ####################################################');
      L.push('');
      L.push('# Different seed than the permutation test so the two blocks don\'t share draws.');
      L.push('rng = np.random.default_rng(1)');
      L.push('R = ' + reps);
      L.push('apls = np.empty(R)');
      L.push('');
      L.push('# Save the observed weight vector once — we\'ll use it as the per-edge Poisson');
      L.push('# rate every iteration. np.maximum(., 1) guards against zero-weight edges');
      L.push('# (Poisson with lambda = 0 is degenerate — always draws 0).');
      L.push('base_w = np.maximum(np.array(g.es["weight"], dtype=float), 1.0)');
      L.push('');
      L.push('# For each replicate i in 0..R-1:');
      L.push('#   1. Copy the graph so we don\'t mutate g.');
      L.push('#   2. Draw fresh Poisson weights (rng.poisson takes a per-item lambda array).');
      L.push('#   3. Recompute weighted APL and store as apls[i].');
      L.push('for i in range(R):');
      L.push('    gg = g.copy()                                       # step 1');
      L.push('    gg.es["weight"] = rng.poisson(lam=base_w).tolist()  # step 2');
      L.push('    apls[i] = weighted_apl(gg)                          # step 3');
      L.push('');
      L.push('## 5.3 Report + plot #########################################################');
      L.push('');
      L.push('# np.quantile(., [0.025, 0.975]) reads off a percentile-based 95% CI.');
      L.push('lo, hi = np.quantile(apls, [0.025, 0.975])');
      L.push('print(f"🧪 MC APL: mean {apls.mean():.4f} · sd {apls.std():.4f} · 95% CI [{lo:.4f}, {hi:.4f}]")');
      L.push('');
      L.push('plt.figure(figsize=(6, 3.2))');
      L.push('plt.hist(apls, bins=24, color="#39FF14", edgecolor="#0a0f0a")');
      L.push('plt.title("MC weighted APL")');
      L.push('plt.xlabel("APL (1 / weight cost)")');
      L.push('plt.tight_layout()');
      L.push('plt.show()');
      L.push('');
      L.push('');
    }

    L.push('print("\\n' + HR + '")');
    L.push('print("🎉 Done. Re-run for slightly different draws, or press Open in playground again after editing the visualizer.")');
    L.push('print("' + HR + '")');
    L.push('');
    return L.join('\n');
  }

  // Minimal mirror of the playground SAMPLE_CONFIGS — only the fields the
  // export module needs (file list + weight column).
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

    // A checkbox that's on but has no card configuration renders a hint
    // so the student knows why the section didn't appear.
    const scenariosCfgd = !!(snap.removed.length || snap.scenarioNodes.length || snap.scenarioLinks.length);
    const permCfgd = !!(snap.perm && snap.perm.attr);
    const mcCfgd   = !!(snap.mc && snap.weightCol);
    const dimmedNote = (checked, cfgd) => (!checked || cfgd) ? '' :
      ' <span style="color:var(--grey);font-size:10.5px;">(none set)</span>';

    host.innerHTML = `
      <div class="color-by-row" style="margin-bottom:6px;">
        <label for="viz2-codeexport-lang">Language</label>
        <select id="viz2-codeexport-lang" class="viz-select">
          <option value="r"${ui.lang === 'r' ? ' selected' : ''}>R (WebR playground)</option>
          <option value="py"${ui.lang === 'py' ? ' selected' : ''}>Python (Pyodide playground)</option>
        </select>
      </div>
      <fieldset class="viz2-export-includes" style="border:1px solid var(--border-soft); border-radius:6px; padding:4px 10px 6px; margin:2px 0 8px;">
        <legend style="padding:0 6px; font-size:10.5px; color:var(--green-bright); letter-spacing:0.1em; text-transform:uppercase;">Include analyses</legend>
        <label class="viz2-export-opt" style="display:inline-flex;align-items:center;gap:5px;margin-right:14px;font-size:12px;color:var(--green-mint);">
          <input type="checkbox" id="viz2-codeexport-inc-scenarios" ${ui.includeScenarios ? 'checked' : ''} style="accent-color:var(--green-bright);">
          <span>🧨 Apply scenarios${dimmedNote(ui.includeScenarios, scenariosCfgd)}</span>
        </label>
        <label class="viz2-export-opt" style="display:inline-flex;align-items:center;gap:5px;margin-right:14px;font-size:12px;color:var(--green-mint);">
          <input type="checkbox" id="viz2-codeexport-inc-dist" ${ui.includeDist ? 'checked' : ''} style="accent-color:var(--green-bright);">
          <span>📊 Centrality distribution</span>
        </label>
        <label class="viz2-export-opt" style="display:inline-flex;align-items:center;gap:5px;margin-right:14px;font-size:12px;color:var(--green-mint);">
          <input type="checkbox" id="viz2-codeexport-inc-perm" ${ui.includePerm ? 'checked' : ''} style="accent-color:var(--green-bright);">
          <span>🧪 Permutation test${dimmedNote(ui.includePerm, permCfgd)}</span>
        </label>
        <label class="viz2-export-opt" style="display:inline-flex;align-items:center;gap:5px;margin-right:14px;font-size:12px;color:var(--green-mint);">
          <input type="checkbox" id="viz2-codeexport-inc-mc" ${ui.includeMc ? 'checked' : ''} style="accent-color:var(--green-bright);">
          <span>🧪 Counterfactual MC${dimmedNote(ui.includeMc, mcCfgd)}</span>
        </label>
      </fieldset>
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

    // Wire the three include-checkboxes. Each toggles a ui.* flag and
    // re-renders so the code preview reflects the new selection.
    const bind = (id, key) => {
      const el = $(id);
      if (!el) return;
      el.addEventListener('change', (e) => { ui[key] = !!e.target.checked; render(); });
    };
    bind('viz2-codeexport-inc-scenarios', 'includeScenarios');
    bind('viz2-codeexport-inc-dist',      'includeDist');
    bind('viz2-codeexport-inc-perm',      'includePerm');
    bind('viz2-codeexport-inc-mc',        'includeMc');
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
