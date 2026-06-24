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
