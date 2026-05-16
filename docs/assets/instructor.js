// Shared helpers for /instructor/* pages.
// - copyToClipboard: writes plain text to clipboard with a fallback.
// - wireCopyButtons: scans for [data-copy-target] and wires click → copy.
// - renderTemplate: replaces {{week}}, {{date}}, {{slug}}, {{student}} in a template.
(function () {
  function copyToClipboard(text) {
    return new Promise(function (resolve) {
      var done = function (ok) { resolve(!!ok); };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () { done(true); }, function () { fallback(text); done(true); });
      } else {
        fallback(text); done(true);
      }
    });
  }
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

  function gatherFields(scope) {
    // Collect any inputs/selects in scope keyed by data-field
    var fields = {};
    var inputs = scope.querySelectorAll('[data-field]');
    inputs.forEach(function (el) {
      fields[el.dataset.field] = (el.value || '').trim() || el.dataset.placeholder || ('{{' + el.dataset.field + '}}');
    });
    // Inject today's date in YYYY-MM-DD if not provided
    if (!fields.date) {
      var d = new Date();
      var pad = function (n) { return n < 10 ? '0' + n : '' + n; };
      fields.date = d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
    }
    return fields;
  }

  function applyFields(template, fields) {
    return template.replace(/\{\{(\w+)\}\}/g, function (_, key) {
      return key in fields ? fields[key] : '{{' + key + '}}';
    });
  }

  function wireCopyButtons() {
    var buttons = document.querySelectorAll('[data-copy-target]');
    buttons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var targetId = btn.dataset.copyTarget;
        var target = document.getElementById(targetId);
        if (!target) return;
        var scope = btn.closest('[data-template-scope]') || document;
        var fields = gatherFields(scope);
        var raw = target.textContent;
        var rendered = applyFields(raw, fields);
        copyToClipboard(rendered).then(function () {
          var orig = btn.textContent;
          btn.textContent = '✓ Copied';
          setTimeout(function () { btn.textContent = orig; }, 1800);
        });
      });
    });
  }

  // Expose for grading-scratchpad which builds its export string dynamically.
  window.instructor = {
    copy: copyToClipboard,
    applyFields: applyFields
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', wireCopyButtons);
  } else {
    wireCopyButtons();
  }
})();
