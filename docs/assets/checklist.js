// Interactive self-grade checklist on assignments.html.
// Renders a list of yes/no items and a "Copy paste-able status block" button
// that writes a markdown summary to the clipboard. Session-only — no persistence.
(function () {
  var mount = document.getElementById('self-grade-checklist');
  if (!mount) return;

  var items = [
    'Sketches photographed and uploaded for every prompt this week',
    'Case-study LC answer recorded for every lab last week',
    'Code LC answer recorded — example.R or example.py ran end-to-end',
    'Project script (project.R or project.py) runs end-to-end on submitted data',
    'Project network has at least 100 nodes',
    'Project report fills at least 2 pages',
    'Report includes the question in one sentence',
    'Report includes how the network was operationalized (node, edge, weight, source)',
    'Report states results as numbers in prose, not just figures',
    'Report has a "what this tells me, and what it doesn\'t" close',
    'GitHub repo URL ready to paste; project folder is pushed',
    'No AI-written prose in the report — wording is mine'
  ];

  var listHtml = '<ul class="sg-list">';
  items.forEach(function (text, i) {
    listHtml += '<li>'
      + '<label>'
      + '<input type="checkbox" data-sg-idx="' + i + '">'
      + '<span class="sg-text">' + text + '</span>'
      + '</label>'
      + '</li>';
  });
  listHtml += '</ul>';

  mount.innerHTML = listHtml
    + '<div class="sg-actions">'
    + '  <button type="button" class="sg-copy">⧉ Copy paste-able status block</button>'
    + '  <span class="sg-feedback" aria-live="polite"></span>'
    + '</div>';

  var btn = mount.querySelector('.sg-copy');
  var fb  = mount.querySelector('.sg-feedback');

  btn.addEventListener('click', function () {
    var boxes = mount.querySelectorAll('input[type="checkbox"]');
    var today = new Date();
    var pad = function (n) { return n < 10 ? '0' + n : '' + n; };
    var date = today.getFullYear() + '-' + pad(today.getMonth() + 1) + '-' + pad(today.getDate());
    var lines = ['SYSEN 5470 — Self-check ' + date];
    boxes.forEach(function (box) {
      var mark = box.checked ? '[x]' : '[ ]';
      var text = box.parentNode.querySelector('.sg-text').textContent;
      lines.push(mark + ' ' + text);
    });
    var block = lines.join('\n');

    var done = function () {
      fb.textContent = 'Copied — paste into the project box on Canvas.';
      setTimeout(function () { fb.textContent = ''; }, 4000);
    };

    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(block).then(done, function () {
        fallback(block); done();
      });
    } else {
      fallback(block); done();
    }
  });

  function fallback(text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.top = '-1000px';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); } catch (_) {}
    document.body.removeChild(ta);
  }
})();
