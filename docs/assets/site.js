// Highlight active nav link based on body.dataset.page
(function () {
  var page = (document.body && document.body.dataset && document.body.dataset.page) || '';
  if (!page) return;
  var links = document.querySelectorAll('.nav-links a[data-page]');
  links.forEach(function (a) {
    if (a.dataset.page === page) a.classList.add('active');
    else a.classList.remove('active');
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
