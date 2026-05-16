// Highlight active nav link based on body.dataset.page; mark dropdown parents
(function () {
  var page = (document.body && document.body.dataset && document.body.dataset.page) || '';
  if (page) {
    var links = document.querySelectorAll('.nav-links a[data-page]');
    links.forEach(function (a) {
      if (a.dataset.page === page) a.classList.add('active');
      else a.classList.remove('active');
    });
    document.querySelectorAll('.nav-dropdown').forEach(function (dd) {
      if (dd.querySelector('a.active')) dd.classList.add('has-active');
    });
  }
})();

// Dropdown menus: click-toggle, click-outside to close, Escape to close,
// arrow-key nav within an open menu, focus returns to the trigger on close.
(function () {
  var dropdowns = document.querySelectorAll('.nav-dropdown');
  if (!dropdowns.length) return;

  function items(dd) {
    return dd.querySelectorAll('.nav-menu a[role="menuitem"]');
  }

  function closeAll(except, restoreFocus) {
    dropdowns.forEach(function (dd) {
      if (dd !== except) {
        if (dd.classList.contains('open') && restoreFocus) {
          var b = dd.querySelector('.nav-trigger');
          if (b) b.focus();
        }
        dd.classList.remove('open');
        var btn = dd.querySelector('.nav-trigger');
        if (btn) btn.setAttribute('aria-expanded', 'false');
      }
    });
  }

  dropdowns.forEach(function (dd) {
    var btn = dd.querySelector('.nav-trigger');
    if (!btn) return;
    btn.setAttribute('aria-expanded', 'false');

    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var willOpen = !dd.classList.contains('open');
      closeAll(dd, false);
      dd.classList.toggle('open', willOpen);
      btn.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
      if (willOpen) {
        var first = items(dd)[0];
        if (first) setTimeout(function () { first.focus(); }, 0);
      }
    });

    // ArrowDown on the trigger opens the menu and focuses the first item.
    btn.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown' || e.key === 'Enter' || e.key === ' ') {
        if (!dd.classList.contains('open')) {
          e.preventDefault();
          closeAll(dd, false);
          dd.classList.add('open');
          btn.setAttribute('aria-expanded', 'true');
          var first = items(dd)[0];
          if (first) first.focus();
        }
      }
    });

    // Arrow-key cycling within the open menu, plus Escape to close & return focus.
    dd.addEventListener('keydown', function (e) {
      if (!dd.classList.contains('open')) return;
      var list = Array.prototype.slice.call(items(dd));
      var idx = list.indexOf(document.activeElement);
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        var next = list[(idx + 1) % list.length] || list[0];
        if (next) next.focus();
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        var prev = list[(idx - 1 + list.length) % list.length] || list[list.length - 1];
        if (prev) prev.focus();
      } else if (e.key === 'Home') {
        e.preventDefault();
        if (list[0]) list[0].focus();
      } else if (e.key === 'End') {
        e.preventDefault();
        if (list[list.length - 1]) list[list.length - 1].focus();
      } else if (e.key === 'Escape') {
        e.preventDefault();
        closeAll(null, true);
      } else if (e.key === 'Tab') {
        // Let Tab flow naturally but close the menu so focus exits cleanly.
        closeAll(null, false);
      }
    });
  });

  document.addEventListener('click', function (e) {
    var inside = e.target.closest && e.target.closest('.nav-dropdown');
    if (!inside) closeAll(null, false);
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeAll(null, true);
  });
})();

// On case-study pages, inject an "Open the code" callout linking to
// the matching folder under /code/<NN_slug>/README.md on GitHub.
// We figure out the slug from the URL path so we don't have to edit
// every case-study HTML file by hand.
(function () {
  var path = window.location.pathname || '';
  var match = path.match(/case-studies\/([a-z0-9-]+)\.html$/i);
  if (!match) return;
  var slug = match[1];

  // case-study slug -> /code/NN_<slug>/ folder
  var folder = {
    'build-a-network':  '01_build-a-network',
    'joins':            '02_joins',
    'aggregation':      '03_aggregation',
    'centrality':       '04_centrality',
    'supply-chain':     '05_supply-chain',
    'dsm-clustering':   '06_dsm-clustering',
    'permutation':      '07_permutation',
    'sampling':         '08_sampling',
    'counterfactual':   '09_counterfactual',
    'gnn-by-hand':      '10_gnn-by-hand',
    'gnn-xgboost':      '11_gnn-xgboost'
  }[slug];
  if (!folder) return;

  // Build the GitHub link. Adjust the org/repo here once if it ever moves.
  var repoBase = 'https://github.com/timothyfraser/netsci/tree/main/code/';
  var href = repoBase + folder + '#readme';

  // Render the callout
  var section = document.createElement('aside');
  section.className = 'case-code-link';
  section.style.cssText = [
    'margin: 36px auto 28px',
    'max-width: 760px',
    'padding: 20px 24px',
    'border: 1px solid rgba(255,255,255,0.18)',
    'border-radius: 12px',
    'background: rgba(255,255,255,0.04)',
    'font-family: inherit'
  ].join(';');
  section.innerHTML = (
    '<h3 style="margin:0 0 6px;font-size:1.05rem;letter-spacing:0.02em;">' +
      'Run this in code' +
    '</h3>' +
    '<p style="margin:0 0 14px;opacity:0.78;font-size:0.95rem;line-height:1.5;">' +
      "Now that you've worked through this case study interactively, run " +
      'the same analysis as plain R or Python on a slim dataset, then ' +
      'apply it to your own network.' +
    '</p>' +
    '<a href="' + href + '" ' +
       'class="btn primary" ' +
       'style="display:inline-block;padding:10px 16px;border-radius:8px;' +
       'background:#3a8bc6;color:#fff;text-decoration:none;font-weight:600;">' +
      'Open the code folder on GitHub →' +
    '</a>'
  );

  // Insert before the closing </main> if there is one, else append to body
  var main = document.querySelector('main') || document.querySelector('.page');
  if (main) {
    main.appendChild(section);
  } else {
    document.body.appendChild(section);
  }
})();

// On case-study pages, also inject a "Project Question Seeds" card so the
// three suggested project questions from the matching code/NN_<slug>/README.md
// are visible without leaving the lab.
(function () {
  var path = window.location.pathname || '';
  var match = path.match(/case-studies\/([a-z0-9-]+)\.html$/i);
  if (!match) return;
  var slug = match[1];

  var folder = {
    'build-a-network':  '01_build-a-network',
    'joins':            '02_joins',
    'aggregation':      '03_aggregation',
    'centrality':       '04_centrality',
    'supply-chain':     '05_supply-chain',
    'dsm-clustering':   '06_dsm-clustering',
    'permutation':      '07_permutation',
    'sampling':         '08_sampling',
    'counterfactual':   '09_counterfactual',
    'gnn-by-hand':      '10_gnn-by-hand',
    'gnn-xgboost':      '11_gnn-xgboost'
  }[slug];
  if (!folder) return;

  var seeds = {
    'build-a-network': [
      ['From data to graph', 'Take a tabular dataset that isn\'t obviously a graph. Define node, edge, edge weight; justify each.'],
      ['Bipartite projection in your domain', 'Find a real bipartite structure (people↔projects, firms↔contracts). Project both ways; report what the projection reveals.'],
      ['Two encodings, two stories', 'Same underlying data, two graph builds (directed/undirected, weighted/binary). Which conclusions are robust?']
    ],
    'joins': [
      ['Attribute homophily on edges', 'Double-node-join a categorical attribute. Report within-group vs cross-group edge weight as a heatmap.'],
      ['Aggregate-before-join vs join-before-aggregate', 'Run both orderings. Report wall-clock time and peak memory.'],
      ['Silent collision audit', 'Join two attributes from the same node table. Show the failure mode without renames, then the fix.']
    ],
    'aggregation': [
      ['At what resolution does my network become legible?', 'Try raw, mid-, and high-resolution views. Report which one fits the question and why.'],
      ['Diagonal stickiness', 'Aggregate by a categorical attribute. Report the fraction of weight on the diagonal.'],
      ['Two competing aggregations', 'Aggregate by two attributes (e.g. tier vs region). Report which makes the pattern clearer.']
    ],
    'centrality': [
      ['Bridges in plain sight', 'Compute degree and betweenness. Find the top-10 by (betweenness_rank − degree_rank) gap.'],
      ['Removal simulation', 'Remove top-5 by each of two centralities. Report change in LCC or shortest path.'],
      ['Which centrality answers my question?', 'Pick a real-world question, argue from question to metric, then compute and report top 5.']
    ],
    'supply-chain': [
      ['Which centrality picks the load-bearing nodes?', 'Run two targeted-attack strategies (e.g. degree vs betweenness). Plot the damage curve.'],
      ['Random baseline', 'Compare any targeted strategy against random removal. Report the area between the two curves.'],
      ['Tier-specific failures', 'If your network has tiers, simulate failure inside each. Report which tier is most fragile.']
    ],
    'dsm-clustering': [
      ['What are the modules in my network?', 'Apply Louvain. Report number of modules, modularity, and what 2–3 modules represent.'],
      ['Two clustering algorithms, two stories', 'Run Louvain plus fast-greedy (or Leiden, walktrap). Compare and discuss disagreements.'],
      ['Cascade analysis', 'Simulate k-hop cascades from seed nodes. Report which seeds produce the largest 1- and 2-hop cascades.']
    ],
    'permutation': [
      ['Two nulls, two stories', 'Pick a categorical attribute. Compare unblocked and block-permutation nulls; report both p-values.'],
      ['What\'s the right block?', 'Try two plausible blocking variables. Report which you prefer and why.'],
      ['Beyond assortativity', 'Replace assortativity with another network statistic. Show blocked/unblocked still applies.']
    ],
    'sampling': [
      ['Strategy showdown', 'Sample ego-centrically and edgewise to the same edge count. Report which metric each strategy preserves.'],
      ['Sample-size convergence', 'Vary sample size on one strategy. Find where density stabilizes within 5% of the population.'],
      ['Spatial / temporal targeting', 'Filter by region or window before sampling. Compare against an unfiltered same-size sample.']
    ],
    'counterfactual': [
      ['Is this intervention real?', 'Pick a domain-meaningful intervention. Compute the 95% CI on its effect on a metric.'],
      ['Two interventions, one budget', 'Propose two competing interventions. Compute each CI; report which is more reliably beneficial.'],
      ['Sensitivity to R', 'Vary R (e.g. 100, 500, 2000). Find the smallest R that gives a CI within 10% of R = 2000.']
    ],
    'gnn-by-hand': [
      ['Embed your nodes', 'Build a 2-feature input. Run a 1-layer GCN. Report top 5 by embedding L2 and what they share.'],
      ['Aggregation choices', 'Try sum, mean, and max-pool. Report top-5 under each; discuss why aggregations differ.'],
      ['Depth matters', 'Compare 1-, 2-, 3-layer GCNs. Find a node whose embedding changes most between 1 and 3 layers.']
    ],
    'gnn-xgboost': [
      ['Does network position help?', 'Train XGBoost on raw, then raw+lag, then raw+lag+GNN. Report AUC gain at each step.'],
      ['Feature importance audit', 'Train on the full set. Report top 5 by gain. Does the ranking match domain intuition?'],
      ['Class imbalance', 'If imbalanced, report AUC plus precision/recall at a sensible threshold. Is it useful operationally?']
    ]
  }[slug];
  if (!seeds || !seeds.length) return;

  var readmeHref = 'https://github.com/timothyfraser/netsci/tree/main/code/' + folder + '#your-project-case-study';

  var card = document.createElement('aside');
  card.className = 'project-seeds';
  card.style.cssText = [
    'margin: 28px auto 0',
    'max-width: 760px',
    'padding: 22px 26px',
    'border: 1px solid rgba(57,255,20,0.3)',
    'border-left: 3px solid #39ff14',
    'border-radius: 12px',
    'background: rgba(57,255,20,0.04)',
    'backdrop-filter: blur(8px)',
    'font-family: inherit'
  ].join(';');

  var seedsHtml = '';
  seeds.forEach(function (s, i) {
    seedsHtml += '<li style="margin-bottom:10px;">'
      + '<strong style="color:#fff;">' + (i + 1) + '. ' + s[0] + '.</strong> '
      + '<span style="opacity:0.85;">' + s[1] + '</span>'
      + '</li>';
  });

  card.innerHTML = (
    '<div style="font-family:var(--font-mono);font-size:10.5px;letter-spacing:0.14em;' +
      'text-transform:uppercase;color:#39ff14;margin-bottom:6px;">Project case study</div>' +
    '<h3 style="margin:0 0 6px;font-family:var(--font-display);font-size:22px;' +
      'color:#fff;letter-spacing:0.03em;">Project Question Seeds</h3>' +
    '<p style="margin:0 0 12px;font-family:var(--font-body);font-size:14px;' +
      'color:var(--green-mint);line-height:1.55;">' +
      'Pick one of these — or use them as starting points for your own — when ' +
      'this is the case study you\'re doing for the week\'s project.' +
    '</p>' +
    '<ol style="list-style:none;padding:0;margin:0 0 14px;font-family:var(--font-body);' +
      'font-size:14px;color:var(--green-mint);line-height:1.55;">' + seedsHtml + '</ol>' +
    '<a href="' + readmeHref + '" target="_blank" rel="noopener" ' +
       'style="font-family:var(--font-mono);font-size:11px;color:#39ff14;' +
       'letter-spacing:0.1em;text-transform:uppercase;text-decoration:none;">' +
      'Read the full Project Case Study brief →' +
    '</a>'
  );

  var main = document.querySelector('main') || document.querySelector('.page');
  if (main) main.appendChild(card);
  else document.body.appendChild(card);
})();
