// ============================================================
// SYSEN 5470 — Network Visualizer v2 · Tutorial walkthrough
// Wired to: #viz2-tutorial-btn
// Driver.js (https://driverjs.com — MIT, ~5KB) drives a step-by-step
// overlay tour of the cards. Loads a sample dataset first so every card
// has content to highlight.
// ============================================================
(function () {
  'use strict';

  // localStorage key for the card open/closed state (shared with visualizer2.html).
  const CARDS_KEY = 'viz2-cards-state-v1';
  // Sample dataset to autoload if nothing is loaded yet — picked for color/variety.
  const SAMPLE_KEY = 'ups-ground-network';

  // Tour steps. Each step targets a real DOM element and shows a popover.
  // `side` follows the column layout: left-column → right, right-column → left,
  // center cards → top, opening/closing popovers omit `element`.
  const STEPS = [
    { // 0 — welcome
      popover: {
        title: '🎓 Welcome to Visualizer v2',
        description: "This tour shows you what's new. Press → to advance, ✕ to quit.",
      },
    },
    { // 1 — sample picker (left column)
      element: '#sample-select',
      popover: {
        title: '📥 Load a dataset',
        description: 'Drop in any of 21 project datasets here, or upload your own CSV.',
        side: 'right',
      },
    },
    { // 2 — the graph itself (center)
      element: '#graph-stage',
      popover: {
        title: '🌐 Your network',
        description: 'This is your network. Click any node to inspect it. Drag to pan, scroll to zoom.',
        side: 'top',
      },
    },
    { // 3 — selected node card (right column)
      element: 'details[data-card="selected"]',
      popover: {
        title: '🏷 Selected Node',
        description: 'Click a node, then this card shows degree, betweenness, and shortest paths through it.',
        side: 'left',
      },
    },
    { // 4 — disruption (center, left of the row)
      element: '#viz2-disruption-card',
      popover: {
        title: '🧨 Disruption Stats',
        description: 'Remove a node from the Selected card. This card reports avg path length, diameter, and components — Original vs Live vs Δ.',
        side: 'top',
      },
    },
    { // 5 — group coverage (center, right of the row)
      element: '#viz2-coverage-panel',
      popover: {
        title: '🛡 Group Coverage',
        description: 'Pick a reference group; coverage tells you what fraction of every other group is reachable from it.',
        side: 'top',
      },
    },
    { // 6 — counterfactuals (center)
      element: '#viz2-montecarlo-card',
      popover: {
        title: '🎲 Counterfactuals',
        description: 'Run Counterfactuals: Poisson-resamples edge weights and reports a 95% CI on a metric you pick.',
        side: 'top',
      },
    },
    { // 7 — permutation test (center)
      element: '#viz2-permutation-card',
      popover: {
        title: '🔀 Permutation Test',
        description: 'Permutation Test: shuffles a node attribute and reports a one-sided p-value vs the observed value.',
        side: 'top',
      },
    },
    { // 8 — group composition (right column)
      element: '#viz2-group-composition-card',
      popover: {
        title: '📐 Group Composition',
        description: 'Group Composition: change the grouping variable for the WHOLE network and see the per-group bar chart + Similarity Index.',
        side: 'left',
      },
    },
    { // 9 — browse nodes (right column)
      element: '#viz2-node-browser-panel',
      popover: {
        title: '🔎 Browse Nodes',
        description: 'When the graph is too dense to click into, browse nodes here — search, sort, click a row to select.',
        side: 'left',
      },
    },
    { // 10 — scenario tools (stage toolbar, top of graph)
      element: '#btn-add-node',
      popover: {
        title: '✏ Scenarios',
        description: 'Add what-if scenario nodes (＋N) and edges (＋E) directly on the graph. Save bundles in your browser.',
        side: 'bottom',
      },
    },
    { // 11 — done
      popover: {
        title: '🎓 Tour complete',
        description: "That's it. Press 🎓 again any time to re-run this tour.",
      },
    },
  ];

  // ── style injection ─────────────────────────────────────────
  // Driver.js ships a light-blue/white stock sheet; override it to match the
  // netsci dark/neon-green palette (design tokens in assets/design.css).
  // Injected once, on first tour run, so we don't add CSS until needed.
  function injectTutorialCss() {
    if (document.getElementById('viz2-tutorial-css')) return;
    const css = `
      /* Driver.js overlay — darker than default for contrast on dark theme. */
      .driver-overlay {
        fill: #050a05 !important;
      }

      /* Popover card */
      .driver-popover {
        background: rgba(5, 10, 5, 0.96) !important;
        color: #d1fae5 !important;
        border: 1px solid rgba(57, 255, 20, 0.55) !important;
        border-radius: 8px !important;
        box-shadow: 0 0 24px rgba(57, 255, 20, 0.18),
                    0 8px 32px rgba(0, 0, 0, 0.6) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        font-family: 'DM Sans', system-ui, sans-serif !important;
        padding: 18px 20px 16px !important;
        max-width: 340px !important;
      }

      /* Title — big display font with neon-green underline accent */
      .driver-popover-title {
        font-family: 'Bebas Neue', 'Impact', sans-serif !important;
        color: #f0fdf4 !important;
        font-size: 20px !important;
        font-weight: 400 !important;
        letter-spacing: 0.06em !important;
        line-height: 1.15 !important;
        margin: 0 0 10px !important;
        padding-bottom: 8px !important;
        border-bottom: 1px solid rgba(57, 255, 20, 0.35) !important;
      }

      /* Body description */
      .driver-popover-description {
        font-family: 'DM Sans', system-ui, sans-serif !important;
        color: #a7f3d0 !important;
        font-size: 13.5px !important;
        line-height: 1.5 !important;
        margin: 0 !important;
      }

      /* Footer wraps progress + buttons */
      .driver-popover-footer {
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
        margin-top: 14px !important;
        padding-top: 12px !important;
        border-top: 1px solid rgba(57, 255, 20, 0.12) !important;
      }

      /* Step counter */
      .driver-popover-progress-text {
        font-family: 'Space Mono', 'JetBrains Mono', ui-monospace, monospace !important;
        color: #a3b8a3 !important;
        font-size: 10.5px !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
      }

      /* Generic button base — matches .viz-btn from visualizer2.html */
      .driver-popover-navigation-btns button,
      .driver-popover-next-btn,
      .driver-popover-prev-btn,
      .driver-popover-done-btn {
        font-family: 'Space Mono', 'JetBrains Mono', ui-monospace, monospace !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
        padding: 8px 14px !important;
        border-radius: 6px !important;
        cursor: pointer !important;
        transition: all 0.15s !important;
        text-shadow: none !important;
      }

      /* Next / Done — primary CTA (green-bright fill, black text) */
      .driver-popover-next-btn,
      .driver-popover-done-btn {
        background: #39FF14 !important;
        color: #050a05 !important;
        border: 1px solid #39FF14 !important;
      }
      .driver-popover-next-btn:hover,
      .driver-popover-done-btn:hover {
        background: #86efac !important;
        border-color: #86efac !important;
      }

      /* Back — ghost (transparent + green border) */
      .driver-popover-prev-btn {
        background: transparent !important;
        color: #39FF14 !important;
        border: 1px solid #39FF14 !important;
      }
      .driver-popover-prev-btn:hover {
        background: rgba(57, 255, 20, 0.1) !important;
      }

      /* Close (✕) — top-right, neutral */
      .driver-popover-close-btn {
        color: #a3b8a3 !important;
        font-size: 20px !important;
        font-weight: 400 !important;
        opacity: 0.7 !important;
        transition: all 0.15s !important;
        background: transparent !important;
        border: none !important;
        padding: 4px 8px !important;
        top: 8px !important;
        right: 8px !important;
      }
      .driver-popover-close-btn:hover {
        color: #39FF14 !important;
        opacity: 1 !important;
      }

      /* Arrows — recolor to match the popover border. Driver.js v1.3.1 uses
         per-side classes; cover all four. The arrow is a CSS triangle built
         from border colors, so override the relevant border side. */
      .driver-popover-arrow-side-left.driver-popover-arrow {
        border-left-color: rgba(57, 255, 20, 0.55) !important;
      }
      .driver-popover-arrow-side-right.driver-popover-arrow {
        border-right-color: rgba(57, 255, 20, 0.55) !important;
      }
      .driver-popover-arrow-side-top.driver-popover-arrow {
        border-top-color: rgba(57, 255, 20, 0.55) !important;
      }
      .driver-popover-arrow-side-bottom.driver-popover-arrow {
        border-bottom-color: rgba(57, 255, 20, 0.55) !important;
      }
    `;
    const style = document.createElement('style');
    style.id = 'viz2-tutorial-css';
    style.textContent = css;
    document.head.appendChild(style);
  }

  // ── helpers ─────────────────────────────────────────────────

  // Read/write the shared card-state map without throwing in Safari private mode.
  function loadCardState() {
    try { return JSON.parse(localStorage.getItem(CARDS_KEY)) || {}; }
    catch (_) { return {}; }
  }
  function saveCardState(s) {
    try { localStorage.setItem(CARDS_KEY, JSON.stringify(s)); } catch (_) {}
  }

  // Snapshot every <details data-card> open/closed state, then force them open
  // so the tour's popovers point at populated content.
  function expandAllCards() {
    const prev = {};
    document.querySelectorAll('details[data-card]').forEach((d) => {
      prev[d.dataset.card] = d.open;
      d.open = true;
    });
    return prev;
  }

  // Restore the snapshot and persist it to the shared key.
  function restoreCards(prev) {
    if (!prev) return;
    const s = loadCardState();
    document.querySelectorAll('details[data-card]').forEach((d) => {
      const k = d.dataset.card;
      if (Object.prototype.hasOwnProperty.call(prev, k)) {
        d.open = !!prev[k];
        s[k] = !!prev[k];
      }
    });
    saveCardState(s);
  }

  // Autoload a sample dataset if state.graph is empty. Resolves after the
  // 'graph-loaded' event fires (or immediately if a graph is already loaded).
  function ensureGraphLoaded() {
    return new Promise((resolve) => {
      const NV = window.NetSciViz2;
      if (!NV) { resolve(); return; }
      if (NV.state && NV.state.graph) { resolve(); return; }
      if (typeof NV.on === 'function') NV.on('graph-loaded', () => resolve());
      if (typeof NV.loadProjectDataset === 'function') {
        try { NV.loadProjectDataset(SAMPLE_KEY); } catch (_) { resolve(); }
      } else {
        resolve();
      }
      // Safety net: if the event never fires (offline / proxy-blocked fetch),
      // bail after 5s and run the tour anyway.
      setTimeout(resolve, 5000);
    });
  }

  // ── main ────────────────────────────────────────────────────

  async function runTour() {
    // Driver.js IIFE build exposes window.driver.js.driver.
    if (!window.driver || !window.driver.js || !window.driver.js.driver) {
      alert('Tutorial library unavailable');
      return;
    }

    injectTutorialCss();
    await ensureGraphLoaded();
    const prevCards = expandAllCards();

    let restored = false;
    const finish = () => {
      if (restored) return;
      restored = true;
      restoreCards(prevCards);
    };

    const tour = window.driver.js.driver({
      showProgress: true,
      animate: true,
      allowClose: true,
      overlayOpacity: 0.55,
      progressText: '{{current}} of {{total}}',
      nextBtnText: 'Next →',
      prevBtnText: '← Back',
      doneBtnText: 'Done',
      steps: STEPS,
      onDestroyed: () => { finish(); try { tour.destroy && tour.destroy(); } catch (_) {} },
      onCloseClick: () => { try { tour.destroy(); } catch (_) {} finish(); },
    });

    tour.drive();
  }

  // Wire the button on DOMContentLoaded — don't block page init on tour setup.
  function wire() {
    const btn = document.getElementById('viz2-tutorial-btn');
    if (!btn) return;
    btn.addEventListener('click', () => {
      runTour().catch((err) => {
        // Don't let a tour error swallow itself silently.
        console.error('[viz2-tutorial] tour failed:', err);
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', wire);
  } else {
    wire();
  }
})();
