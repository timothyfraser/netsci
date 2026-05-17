/* ──────────────────────────────────────────────────────────────────────
   NotebookLM "Course Companion" floating action button
   Shipped via assets/site.js include on every page.
   Tier 1 · T1.1
   ────────────────────────────────────────────────────────────────────── */
(function () {
  const NOTEBOOK_URL = 'https://notebooklm.google.com/notebook/dce8fe4a-927e-41c6-96fb-ec331fa46423';
  const SEEN_KEY = 'netsci-notebooklm-bubble-seen-v1';

  // Inject only once
  if (document.getElementById('notebooklm-fab')) return;

  // Detect a playground page (lifts the bubble above the persistence bar)
  const isPlayground = document.body && document.body.dataset.page === 'playground';
  const seen = (() => { try { return localStorage.getItem(SEEN_KEY) === '1'; } catch { return false; } })();

  // Styles
  const style = document.createElement('style');
  style.textContent = `
    #notebooklm-fab {
      position: fixed;
      right: 16px;
      bottom: ${isPlayground ? '88px' : '16px'};
      width: 56px;
      height: 56px;
      border-radius: 50%;
      background: var(--green-bright, #39FF14);
      color: var(--black, #050a05);
      border: none;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 8px 28px rgba(0, 0, 0, 0.45),
                  0 0 22px rgba(57, 255, 20, 0.45);
      z-index: 2000;
      transition: transform 0.18s ease, box-shadow 0.18s ease;
      text-decoration: none;
    }
    #notebooklm-fab:hover {
      transform: translateY(-2px) scale(1.04);
      box-shadow: 0 10px 32px rgba(0, 0, 0, 0.55),
                  0 0 30px rgba(57, 255, 20, 0.65);
    }
    #notebooklm-fab:focus-visible {
      outline: 2px solid var(--white, #f0fdf4);
      outline-offset: 3px;
    }
    #notebooklm-fab svg {
      width: 26px;
      height: 26px;
      stroke: currentColor;
      stroke-width: 2;
      fill: none;
      stroke-linecap: round;
      stroke-linejoin: round;
    }
    #notebooklm-fab .nlm-badge {
      position: absolute;
      top: -6px;
      right: -6px;
      background: var(--node-4, #fbbf24);
      color: var(--black, #050a05);
      font-family: var(--font-mono, 'Space Mono', monospace);
      font-size: 9px;
      font-weight: 700;
      letter-spacing: 0.08em;
      padding: 2px 6px;
      border-radius: 999px;
      box-shadow: 0 0 10px rgba(251, 191, 36, 0.6);
      pointer-events: none;
    }
    #notebooklm-tip {
      position: fixed;
      right: 84px;
      bottom: ${isPlayground ? '104px' : '32px'};
      background: rgba(5, 10, 5, 0.92);
      border: 1px solid var(--border, rgba(57, 255, 20, 0.25));
      color: var(--white, #f0fdf4);
      padding: 8px 12px;
      border-radius: 6px;
      font-family: var(--font-mono, 'Space Mono', monospace);
      font-size: 11.5px;
      letter-spacing: 0.04em;
      white-space: nowrap;
      opacity: 0;
      transform: translateX(6px);
      transition: opacity 0.18s ease, transform 0.18s ease;
      pointer-events: none;
      z-index: 2000;
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
    }
    #notebooklm-fab:hover + #notebooklm-tip,
    #notebooklm-fab:focus-visible + #notebooklm-tip {
      opacity: 1;
      transform: translateX(0);
    }
    @media (max-width: 600px) {
      #notebooklm-fab {
        width: 48px;
        height: 48px;
        bottom: ${isPlayground ? '80px' : '14px'};
        right: 14px;
      }
      #notebooklm-fab svg { width: 22px; height: 22px; }
      #notebooklm-tip { display: none; }
    }
    @media (prefers-reduced-motion: reduce) {
      #notebooklm-fab { transition: none; }
      #notebooklm-fab:hover { transform: none; }
    }
  `;
  document.head.appendChild(style);

  // Bubble
  const fab = document.createElement('a');
  fab.id = 'notebooklm-fab';
  fab.href = NOTEBOOK_URL;
  fab.target = '_blank';
  fab.rel = 'noopener noreferrer';
  fab.setAttribute('aria-label', 'Ask the Course Companion (NotebookLM) — opens in new tab');
  fab.innerHTML = `
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
    </svg>
    ${seen ? '' : '<span class="nlm-badge">AI</span>'}
  `;
  fab.addEventListener('click', () => {
    try { localStorage.setItem(SEEN_KEY, '1'); } catch {}
    const badge = fab.querySelector('.nlm-badge');
    if (badge) badge.remove();
  });

  // Tooltip
  const tip = document.createElement('span');
  tip.id = 'notebooklm-tip';
  tip.textContent = 'Ask the Course Companion';

  // Mount once the DOM is ready
  function mount() {
    document.body.appendChild(fab);
    document.body.appendChild(tip);
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mount, { once: true });
  } else {
    mount();
  }
})();
