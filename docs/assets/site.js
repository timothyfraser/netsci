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
