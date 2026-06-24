/* case-toc.js — per-case-study "On this page" sidebar table of contents.
 * Renders a fixed upper-left sidebar that links to whichever of the known
 * sections exist on the page, with a close (×) button and a ☰ re-opener.
 * Pages opt in by (a) giving sections the ids below and (b) loading this file.
 */
(function () {
  const SECTIONS = [
    { id: 'video-overview',      label: 'Video Overview',        icon: '🎬' },
    { id: 'readings',            label: 'Readings',              icon: '📚' },
    { id: 'sketchpad',           label: 'Sketchpad',             icon: '✏️' },
    { id: 'interactive-tutorial',label: 'Interactive Tutorial',  icon: '🧭' },
    { id: 'learning-checks',     label: 'Learning Checks',       icon: '📝' },
    { id: 'code-it',             label: 'Code It',               icon: '⌨️' },
    { id: 'project-seeds',       label: 'Project Seed Questions',icon: '📄' },
  ];

  function build() {
    const present = SECTIONS.filter(s => document.getElementById(s.id));
    if (present.length < 2) return;  // nothing worth a menu

    const nav = document.createElement('nav');
    nav.className = 'case-toc';
    nav.setAttribute('aria-label', 'Sections of this case study');
    nav.innerHTML =
      '<div class="case-toc-head">' +
        '<span class="case-toc-title">On this page</span>' +
        '<button class="case-toc-toggle" aria-label="Hide section menu" title="Hide">×</button>' +
      '</div>' +
      '<ul class="case-toc-list">' +
        present.map(s =>
          `<li><a href="#${s.id}" data-id="${s.id}"><span class="case-toc-ico">${s.icon}</span><span>${s.label}</span></a></li>`
        ).join('') +
      '</ul>';

    const opener = document.createElement('button');
    opener.className = 'case-toc-open';
    opener.setAttribute('aria-label', 'Show section menu');
    opener.title = 'Sections';
    opener.textContent = '☰';

    document.body.appendChild(nav);
    document.body.appendChild(opener);

    function setCollapsed(c) {
      nav.classList.toggle('collapsed', c);
      opener.style.display = c ? 'flex' : 'none';
      // when open on wide screens, CSS shifts the page content right (no overlap)
      document.documentElement.classList.toggle('toc-open', !c);
      try { localStorage.setItem('caseTocCollapsed', c ? '1' : '0'); } catch (e) {}
    }
    const saved = (function () { try { return localStorage.getItem('caseTocCollapsed'); } catch (e) { return null; } })();
    const startCollapsed = saved === '1' || (saved === null && window.innerWidth < 1000);
    setCollapsed(startCollapsed);

    nav.querySelector('.case-toc-toggle').addEventListener('click', () => setCollapsed(true));
    opener.addEventListener('click', () => setCollapsed(false));

    const links = [...nav.querySelectorAll('a')];
    links.forEach(a => a.addEventListener('click', (e) => {
      const el = document.getElementById(a.dataset.id);
      if (!el) return;
      e.preventDefault();
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      history.replaceState(null, '', a.getAttribute('href'));
      if (window.innerWidth < 1000) setCollapsed(true);
    }));

    // highlight the section currently in view
    const obs = new IntersectionObserver((entries) => {
      entries.forEach(en => {
        if (en.isIntersecting) {
          links.forEach(a => a.classList.toggle('active', a.dataset.id === en.target.id));
        }
      });
    }, { rootMargin: '-25% 0px -65% 0px' });
    present.forEach(s => { const el = document.getElementById(s.id); if (el) obs.observe(el); });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', build);
  else build();
})();
