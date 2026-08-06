// Re-capture the lab (paint AFTER scroll-into-view, which triggers a redraw) and the
// visualizer (bigger nodes so a 300-node graph is legible at poster size).
const { chromium } = require('playwright-core');
const shared = require('./theme-shared.js');

const BASE = 'https://timothyfraser.com/netsci';
const OUT = __dirname + '/shots';
const THEMES = process.argv.slice(2).length ? process.argv.slice(2) : ['white', 'grey', 'red', 'orig'];

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
    // ---------------- lab ----------------
    {
      const page = await ctx.newPage();
      await page.goto(`${BASE}/case-studies/centrality.html`, { waitUntil: 'load', timeout: 60000 });
      await page.waitForTimeout(4000);
      await shared.dress(page, theme);
      await page.waitForTimeout(1800);
      const nodes = page.locator('#network-svg circle');
      const n = await nodes.count();
      if (n > 5) { await nodes.nth(Math.floor(n / 2)).click({ force: true }); await page.waitForTimeout(1800); }
      // scroll first — scrolling triggers a redraw that would undo the recolour
      await page.locator('section.lab-layout').scrollIntoViewIfNeeded();
      await page.waitForTimeout(1200);
      await shared.paint(page, theme);
      await page.waitForTimeout(400);
      await page.locator('section.lab-layout').screenshot({ path: `${OUT}/lab-${theme}.png` });
      console.log('ok lab', theme);
      await page.close();
    }

    // ---------------- visualizer ----------------
    {
      const page = await ctx.newPage();
      await page.goto(`${BASE}/visualizer.html`, { waitUntil: 'load', timeout: 60000 });
      await page.waitForTimeout(5000);
      await shared.dress(page, theme);
      await page.selectOption('#sample-select', 'power-grid');
      await page.waitForTimeout(11000);

      // bump node size so the graph reads at poster scale
      const scaled = await page.evaluate(() => {
        const el = document.querySelector('#node-scale');
        if (!el) return 'no slider';
        const min = +el.min || 0, max = +el.max || 100;
        el.value = String(min + (max - min) * 0.8);
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
        return `node-scale ${el.value} of ${min}..${max}`;
      });
      console.log('  ', scaled);
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
      // the stats strip keeps a hard-coded dark panel; make it match the theme
      await page.evaluate((light) => {
        const n = document.querySelector('#stat-nodes');
        if (!n) return;
        let p = n.parentElement;
        for (let i = 0; i < 4 && p; i++) {
          p.style.background = light ? 'transparent' : 'rgba(255,255,255,0.06)';
          p = p.parentElement;
        }
      }, theme !== 'red' && theme !== 'orig');
      await page.waitForTimeout(400);
      await page.screenshot({ path: `${OUT}/viz-${theme}.png`, clip, fullPage: true });
      console.log('ok viz', theme);
      await page.close();
    }
  }
  await browser.close();
})();
