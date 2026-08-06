// Capture each hero figure in four poster-only themes, with a fresh page load per theme
// so nothing the page re-renders can survive between themes.
//   white | grey | red | orig
const { chromium } = require('playwright-core');

const BASE = 'https://timothyfraser.com/netsci';
const OUT = __dirname + '/shots';
const THEMES = process.argv.slice(2).length ? process.argv.slice(2) : ['white', 'grey', 'red', 'orig'];

const BIG_TEXT = `
  :root {
    --fs-xs:15px !important; --fs-sm:17px !important; --fs-base:20px !important;
    --fs-md:22px !important; --fs-lg:26px !important; --fs-xl:33px !important; --fs-2xl:46px !important;
  }
  #network-svg text { font-size:16px !important; font-weight:700 !important; }
  #graph-stage text { font-size:19px !important; font-weight:700 !important; }
  .CodeMirror { font-size:17px !important; line-height:1.45 !important; }
  [id*="notebook" i],[class*="notebook" i],[id*="fab" i],[class*="fab" i],
  [class*="bubble" i],[id*="bubble" i] { display:none !important; }
`;

const LIGHT = (bg, panel) => `
  :root {
    --black:${bg} !important; --black-2:${panel} !important;
    --white:#1A1A1A !important; --grey:#585858 !important; --grey-dim:#8A8A8A !important;
    --green-mint:#3C3C3C !important; --green-mint-2:#6B6B6B !important;
    --green-bright:#B31B1B !important; --green-mid:#8C1515 !important;
    --green-dark:#E4A11B !important; --green-deeper:#F3E7E7 !important; --green-laser:#E4A11B !important;
    --card-bg: rgba(179,27,27,0.045) !important; --card-bg-2: rgba(0,0,0,0.02) !important;
    --border: rgba(179,27,27,0.30) !important; --border-strong: rgba(179,27,27,0.62) !important;
    --border-soft: rgba(179,27,27,0.13) !important;
    --accent:#B31B1B !important; --accent-soft:#8C1515 !important; --link:#B31B1B !important;
    --success:#8C1515 !important; --warning:#B8860B !important; --danger:#B31B1B !important;
    --node-1:#9A9A9A !important; --node-2:#B31B1B !important; --node-3:#E4A11B !important;
    --node-4:#B31B1B !important; --node-5:#7C1010 !important; --node-6:#5A5A5A !important;
    --node-7:#6E0F0F !important; --node-8:#BDBDBD !important;
    --edge: rgba(90,90,90,0.55) !important; --edge-dim: rgba(90,90,90,0.28) !important;
    --edge-strong: rgba(179,27,27,0.90) !important;
  }
  body, #main { background:${bg} !important; }
  #network-svg, #graph-stage, .graph-stage-wrap { background:${bg} !important; }
  .lab-card, .pg-card, .viz-card, .card { background:${panel} !important; }
  .CodeMirror, .CodeMirror-gutters { background:${panel} !important; color:#1A1A1A !important; }
  .CodeMirror-linenumber { color:#9A9A9A !important; }
  .cm-comment { color:#7A7A7A !important; } .cm-string { color:#8C1515 !important; }
  .cm-keyword, .cm-builtin { color:#B31B1B !important; font-weight:700; }
  .cm-number, .cm-atom { color:#8A6A00 !important; }
  .cm-variable, .cm-property, .cm-operator, .cm-def { color:#1A1A1A !important; }
  .CodeMirror-cursor { border-left-color:#1A1A1A !important; }
`;

const THEME_CSS = {
  white: LIGHT('#FFFFFF', '#F6F2F2'),
  grey: LIGHT('#EBEBEB', '#E2E2E2'),
  red: `
    :root {
      --black:#7C1010 !important; --black-2:#6B0E0E !important;
      --white:#FFFFFF !important; --grey:#F0DCDC !important; --grey-dim:#D9B8B8 !important;
      --green-mint:#FBEDED !important; --green-mint-2:#F0D9A8 !important;
      --green-bright:#F7C948 !important; --green-mid:#F0B323 !important;
      --green-dark:#4E0A0A !important; --green-deeper:#5C0C0C !important; --green-laser:#FFFFFF !important;
      --card-bg: rgba(255,255,255,0.10) !important; --card-bg-2: rgba(255,255,255,0.06) !important;
      --border: rgba(255,255,255,0.38) !important; --border-strong: rgba(247,201,72,0.85) !important;
      --border-soft: rgba(255,255,255,0.18) !important;
      --accent:#F7C948 !important; --accent-soft:#FFFFFF !important; --link:#F7C948 !important;
      --success:#F0B323 !important; --warning:#F7C948 !important; --danger:#FFD9D9 !important;
      --node-1:#FFE9A8 !important; --node-2:#F7C948 !important; --node-3:#FFFFFF !important;
      --node-4:#F7C948 !important; --node-5:#FFC9C9 !important; --node-6:#E0C0C0 !important;
      --node-7:#4E0A0A !important; --node-8:#D9D9D9 !important;
      --edge: rgba(255,255,255,0.50) !important; --edge-dim: rgba(255,255,255,0.26) !important;
      --edge-strong: rgba(247,201,72,0.95) !important;
    }
    body, #main { background:#7C1010 !important; }
    #network-svg, #graph-stage, .graph-stage-wrap { background:#6B0E0E !important; }
    .lab-card, .pg-card, .viz-card, .card { background:rgba(255,255,255,0.07) !important; }
    .CodeMirror, .CodeMirror-gutters { background:#5C0C0C !important; color:#FFFFFF !important; }
    .CodeMirror-linenumber { color:#D9B8B8 !important; }
    .cm-comment { color:#E8C0C0 !important; } .cm-string { color:#F7C948 !important; }
    .cm-keyword, .cm-builtin { color:#FFD98A !important; font-weight:700; }
    .cm-number, .cm-atom { color:#FFE9A8 !important; }
    .cm-variable, .cm-property, .cm-operator, .cm-def { color:#FFFFFF !important; }
  `,
  orig: '',
};

const MAP_LIGHT = { '#39ff14': '#9A9A9A', '#86efac': '#C9A227', '#5eead4': '#E4A11B', '#fbbf24': '#B31B1B',
                    '#f472b6': '#7C1010', '#818cf8': '#5A5A5A', '#f97316': '#6E0F0F', '#e2e8f0': '#BDBDBD',
                    '#22c55e': '#8C1515', '#166534': '#6E0F0F', '#d1fae5': '#3C3C3C', '#a3b8a3': '#585858' };
const MAP_RED   = { '#39ff14': '#FFE9A8', '#86efac': '#F0D9A8', '#5eead4': '#FFFFFF', '#fbbf24': '#F7C948',
                    '#f472b6': '#FFC9C9', '#818cf8': '#E0C0C0', '#f97316': '#4E0A0A', '#e2e8f0': '#D9D9D9',
                    '#22c55e': '#F0B323', '#166534': '#4E0A0A', '#d1fae5': '#FBEDED', '#a3b8a3': '#F0DCDC' };

// Idempotent: maps the course palette onto the poster palette wherever it appears.
const PAINT = `(args) => {
  const { map, light } = args;
  const edge = light ? '90,90,90' : '255,255,255';
  document.querySelectorAll('svg *').forEach((el) => {
    ['fill', 'stroke'].forEach((attr) => {
      const v = el.getAttribute(attr);
      if (!v) return;
      const k = v.trim().toLowerCase();
      if (map[k]) { el.setAttribute(attr, map[k]); return; }
      const g = /^rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)(?:,\\s*([\\d.]+))?\\)$/.exec(k);
      if (g) {
        const [r, gr, b] = [+g[1], +g[2], +g[3]];
        const a = g[4] === undefined ? 1 : +g[4];
        if (gr > r && gr > b && gr > 40) el.setAttribute(attr, 'rgba(' + edge + ',' + a + ')');
      }
      if (light && el.tagName.toLowerCase() === 'text') {
        const m = /^#([0-9a-f]{6})$/i.exec(el.getAttribute(attr) || '');
        if (m) {
          const n = parseInt(m[1], 16);
          const L = (0.2126*((n>>16)&255) + 0.7152*((n>>8)&255) + 0.0722*(n&255)) / 255;
          if (L > 0.7) el.setAttribute(attr, '#1A1A1A');
        }
      }
    });
  });
}`;

const plotCode = (cornell) => `# Power grid — which buses actually carry the load?
import pandas as pd, networkx as nx
import matplotlib.pyplot as plt

nodes = pd.read_csv("power-grid-nodes.csv")
edges = pd.read_csv("power-grid-edges.csv")
G = nx.from_pandas_edgelist(edges, source="from_id", target="to_id")
print("Nodes:", G.number_of_nodes(), " Edges:", G.number_of_edges())

bet = nx.betweenness_centrality(G)
print("Most critical:", sorted(bet, key=bet.get, reverse=True)[:5])
${cornell
  ? 'from matplotlib.colors import LinearSegmentedColormap\nCMAP = LinearSegmentedColormap.from_list("c", ["#C4C4C4", "#E4A11B", "#B31B1B", "#6E0F0F"])'
  : 'CMAP = "plasma"'}
plt.rcParams.update({"font.size": 15, "axes.titlesize": 19})
pos = nx.spring_layout(G, seed=42)
plt.figure(figsize=(6.4, 4.8))
nx.draw_networkx_edges(G, pos, edge_color="#c9c9c9", width=0.8)
nx.draw_networkx_nodes(G, pos, node_color=[bet[n] for n in G.nodes], cmap=CMAP,
                       node_size=[1400 * bet[n] + 16 for n in G.nodes], linewidths=0)
plt.title("Power grid — size & color = betweenness")
plt.axis("off"); plt.tight_layout(); plt.show()
`;

(async () => {
  const browser = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium',
    proxy: { server: process.env.HTTPS_PROXY },
    args: ['--ssl-version-max=tls1.2'],
  });
  const ctx = await browser.newContext({
    viewport: { width: 1280, height: 900 }, deviceScaleFactor: 3, ignoreHTTPSErrors: true,
  });

  const dress = async (page, theme) => {
    await page.addStyleTag({ content: BIG_TEXT });
    if (THEME_CSS[theme]) await page.addStyleTag({ content: THEME_CSS[theme] });
    await page.waitForTimeout(600);
  };
  const paint = async (page, theme) => {
    if (theme === 'orig') return;
    await page.evaluate(new Function('return ' + PAINT)(),
      { map: theme === 'red' ? MAP_RED : MAP_LIGHT, light: theme !== 'red' });
    await page.waitForTimeout(300);
  };

  for (const theme of THEMES) {
    // ---- lab ----
    {
      const page = await ctx.newPage();
      await page.goto(`${BASE}/case-studies/centrality.html`, { waitUntil: 'load', timeout: 60000 });
      await page.waitForTimeout(4000);
      await dress(page, theme);
      await page.waitForTimeout(1800);
      const nodes = page.locator('#network-svg circle');
      const n = await nodes.count();
      if (n > 5) { await nodes.nth(Math.floor(n / 2)).click({ force: true }); await page.waitForTimeout(1800); }
      await paint(page, theme);
      await page.locator('section.lab-layout').screenshot({ path: `${OUT}/lab-${theme}.png` });
      console.log('ok lab', theme);
      await page.close();
    }
    // ---- visualizer ----
    {
      const page = await ctx.newPage();
      await page.goto(`${BASE}/visualizer.html`, { waitUntil: 'load', timeout: 60000 });
      await page.waitForTimeout(5000);
      await dress(page, theme);
      await page.selectOption('#sample-select', 'power-grid');
      await page.waitForTimeout(11000);
      try { await page.click('#btn-fit'); await page.waitForTimeout(2500); } catch {}
      await page.evaluate(() => {
        const c = [...document.querySelectorAll('#graph-stage circle')];
        if (!c.length) return;
        c.sort((a, b) => (+b.getAttribute('r') || 0) - (+a.getAttribute('r') || 0));
        c[0].dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
      });
      await page.waitForTimeout(2500);
      await paint(page, theme);
      const clip = await page.evaluate(() => {
        const st = document.querySelector('.graph-stage-wrap').getBoundingClientRect();
        const ly = document.querySelector('.viz-layout').getBoundingClientRect();
        return { x: st.left + scrollX - 8, y: st.top + scrollY - 8, width: ly.right - st.left + 16, height: st.height + 16 };
      });
      await page.screenshot({ path: `${OUT}/viz-${theme}.png`, clip, fullPage: true });
      console.log('ok viz', theme);
      await page.close();
    }
    // ---- playground ----
    {
      const page = await ctx.newPage();
      await page.goto(`${BASE}/playground-py.html`, { waitUntil: 'load', timeout: 90000 });
      await page.waitForFunction(
        () => (document.querySelector('#status-text')?.textContent || '').includes('Ready'), { timeout: 240000 });
      await dress(page, theme);
      await page.selectOption('#sample-select', 'power-grid');
      await page.waitForTimeout(5000);
      await page.evaluate((c) => { document.querySelector('.CodeMirror').CodeMirror.setValue(c); },
        plotCode(theme !== 'orig'));
      await page.click('#btn-run');
      await page.waitForFunction(() => document.querySelector('#plots img, #plots canvas') !== null, { timeout: 240000 });
      await page.click('[data-tab="plots"]');
      await page.waitForTimeout(1500);
      await paint(page, theme);
      const clip = await page.evaluate(() => {
        const g = document.querySelector('.pg-grid').getBoundingClientRect();
        const pl = document.querySelector('#plots img, #plots canvas');
        const top = g.top + scrollY;
        return { x: g.left + scrollX - 6, y: top - 6, width: g.width + 12,
                 height: pl.getBoundingClientRect().bottom + scrollY + 50 - top + 12 };
      });
      await page.screenshot({ path: `${OUT}/pg-${theme}.png`, clip, fullPage: true });
      console.log('ok pg', theme);
      await page.close();
    }
  }
  await browser.close();
})();
