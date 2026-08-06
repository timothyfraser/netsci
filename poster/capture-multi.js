// Capture each hero figure in the poster themes, one fresh page load per theme.
//   node capture-multi.js [white|grey|red|orig ...]
// All theming lives in theme-shared.js — this file only drives the pages.
const { chromium } = require('playwright-core');
const shared = require('./theme-shared.js');

const BASE = 'https://timothyfraser.com/netsci';
const OUT = __dirname + '/shots';
const THEMES = process.argv.slice(2).length ? process.argv.slice(2) : ['white', 'grey', 'red', 'orig'];

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

  for (const theme of THEMES) {
    // ---------------- case-study lab ----------------
    {
      const page = await ctx.newPage();
      await page.goto(`${BASE}/case-studies/centrality.html`, { waitUntil: 'load', timeout: 60000 });
      await page.waitForTimeout(4000);
      await shared.dress(page, theme);
      await page.waitForTimeout(1800);
      const nodes = page.locator('#network-svg circle');
      const n = await nodes.count();
      if (n > 5) { await nodes.nth(Math.floor(n / 2)).click({ force: true }); await page.waitForTimeout(1800); }
      // scrolling triggers a redraw, so scroll before painting
      await page.locator('section.lab-layout').scrollIntoViewIfNeeded();
      await page.waitForTimeout(1000);
      await shared.paint(page, theme);
      await page.waitForTimeout(400);
      await page.locator('section.lab-layout').screenshot({ path: `${OUT}/lab-${theme}.png` });
      console.log('ok lab', theme);
      await page.close();
    }

    // ---------------- network visualizer ----------------
    {
      const page = await ctx.newPage();
      await page.goto(`${BASE}/visualizer.html`, { waitUntil: 'load', timeout: 60000 });
      await page.waitForTimeout(5000);
      await shared.dress(page, theme);
      await page.selectOption('#sample-select', 'power-grid');
      await page.waitForTimeout(11000);
      // bigger nodes so a 300-node graph reads at poster scale
      await page.evaluate(() => {
        const el = document.querySelector('#node-scale');
        if (!el) return;
        const min = +el.min || 0, max = +el.max || 100;
        el.value = String(min + (max - min) * 0.8);
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
      });
      await page.waitForTimeout(3500);
      try { await page.click('#btn-fit'); await page.waitForTimeout(2500); } catch {}
      await page.evaluate(() => {
        const c = [...document.querySelectorAll('#graph-stage circle')];
        if (!c.length) return;
        c.sort((a, b) => (+b.getAttribute('r') || 0) - (+a.getAttribute('r') || 0));
        c[0].dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
      });
      await page.waitForTimeout(2500);
      const clip = await page.evaluate(() => {
        const st = document.querySelector('.graph-stage-wrap').getBoundingClientRect();
        const ly = document.querySelector('.viz-layout').getBoundingClientRect();
        return { x: st.left + scrollX - 8, y: st.top + scrollY - 8,
                 width: ly.right - st.left + 16, height: st.height + 16 };
      });
      await shared.paint(page, theme);
      await page.waitForTimeout(500);
      await page.screenshot({ path: `${OUT}/viz-${theme}.png`, clip, fullPage: true });
      console.log('ok viz', theme);
      await page.close();
    }

    // ---------------- coding playground ----------------
    {
      const page = await ctx.newPage();
      await page.goto(`${BASE}/playground-py.html`, { waitUntil: 'load', timeout: 90000 });
      await page.waitForFunction(
        () => (document.querySelector('#status-text')?.textContent || '').includes('Ready'), { timeout: 240000 });
      await shared.dress(page, theme);
      await page.selectOption('#sample-select', 'power-grid');
      await page.waitForTimeout(5000);
      await page.evaluate((c) => { document.querySelector('.CodeMirror').CodeMirror.setValue(c); },
        plotCode(theme !== 'orig'));
      await page.click('#btn-run');
      await page.waitForFunction(() => document.querySelector('#plots img, #plots canvas') !== null, { timeout: 240000 });
      await page.click('[data-tab="plots"]');
      await page.waitForTimeout(1500);
      await shared.paint(page, theme);
      await page.waitForTimeout(500);
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
