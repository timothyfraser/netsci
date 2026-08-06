// Capture each hero figure in the poster themes, one fresh page load per theme.
//   node capture-multi.js [white|grey|red|orig ...]
// All theming lives in theme-shared.js — this file only drives the pages.
const { chromium } = require('playwright-core');
const shared = require('./theme-shared.js');

const BASE = 'https://timothyfraser.com/netsci';
const OUT = __dirname + '/shots';
const THEMES = process.argv.slice(2).length ? process.argv.slice(2) : ['white', 'grey', 'red', 'orig'];

// The plot is the playground's "canvas": it follows the same light/dark choice as the
// network canvas in the other two figures, so every figure has the same A-vs-B contrast.
const { plotCodeFor: plotCode } = require('./plotcode.js');

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
        plotCode(theme));
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
