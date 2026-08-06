// Print-resolution capture of the visualizer and playground.
// Everything outside the figure's own container is hidden first, so the full-page raster
// stays bounded at a high deviceScaleFactor while the figure's own layout is untouched.
const { chromium } = require('playwright-core');
const shared = require('./theme-shared.js');
const { plotCodeFor } = require('./plotcode.js');
const fs = require('fs');

const BASE = 'https://timothyfraser.com/netsci';
const OUT = __dirname + '/shots';
const THEME = process.argv[2] || 'stagelight';
const DSF = +(process.argv[3] || 14);
const size = (b) => `${b.readUInt32BE(16)}x${b.readUInt32BE(20)}`;

const isolate = `(sel) => {
  const keep = document.querySelector(sel);
  for (let el = keep; el && el !== document.body; el = el.parentElement) {
    for (const sib of [...el.parentElement.children]) {
      if (sib !== el) sib.style.display = 'none';
    }
  }
  window.scrollTo(0, 0);
}`;

(async () => {
  const browser = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium',
    proxy: { server: process.env.HTTPS_PROXY },
    args: ['--ssl-version-max=tls1.2'],
  });
  const ctx = await browser.newContext({
    viewport: { width: 1280, height: 900 }, deviceScaleFactor: DSF, ignoreHTTPSErrors: true,
  });

  // ---------------- visualizer ----------------
  {
    const page = await ctx.newPage();
    await page.goto(`${BASE}/visualizer.html`, { waitUntil: 'load', timeout: 90000 });
    await page.waitForTimeout(5000);
    await shared.dress(page, THEME);
    await page.selectOption('#sample-select', 'power-grid');
    await page.waitForTimeout(12000);
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
    await shared.paint(page, THEME);
    await page.waitForTimeout(600);
    await page.evaluate(new Function('return ' + isolate)(), '.viz-layout');
    await page.waitForTimeout(1500);
    const clip = await page.evaluate(() => {
      const st = document.querySelector('.graph-stage-wrap').getBoundingClientRect();
      const ly = document.querySelector('.viz-layout').getBoundingClientRect();
      return { x: st.left + scrollX - 8, y: st.top + scrollY - 8,
               width: ly.right - st.left + 16, height: st.height + 16 };
    });
    console.log('viz clip css px:', JSON.stringify(clip));
    const buf = await page.screenshot({ clip, fullPage: true, timeout: 420000 });
    fs.writeFileSync(`${OUT}/viz-${THEME}-hi.png`, buf);
    console.log('viz ', size(buf), (buf.length / 1e6).toFixed(1) + ' MB');
    await page.close();
  }

  // ---------------- playground ----------------
  {
    const page = await ctx.newPage();
    await page.goto(`${BASE}/playground-py.html`, { waitUntil: 'load', timeout: 120000 });
    await page.waitForFunction(
      () => (document.querySelector('#status-text')?.textContent || '').includes('Ready'), { timeout: 300000 });
    await shared.dress(page, THEME);
    await page.selectOption('#sample-select', 'power-grid');
    await page.waitForTimeout(5000);
    await page.evaluate((c) => { document.querySelector('.CodeMirror').CodeMirror.setValue(c); }, plotCodeFor(THEME));
    await page.click('#btn-run');
    await page.waitForFunction(() => document.querySelector('#plots img, #plots canvas') !== null, { timeout: 300000 });
    await page.click('[data-tab="plots"]');
    await page.waitForTimeout(1800);
    await shared.paint(page, THEME);
    await page.waitForTimeout(600);
    const clip = await page.evaluate(() => {
      const g = document.querySelector('.pg-grid').getBoundingClientRect();
      const pl = document.querySelector('#plots img, #plots canvas');
      const top = g.top + scrollY;
      return { x: g.left + scrollX - 6, y: top - 6, width: g.width + 12,
               height: pl.getBoundingClientRect().bottom + scrollY + 50 - top + 12 };
    });
    // measure first, then trim the page so the raster stays bounded
    const before = await page.evaluate(() => document.querySelector('.pg-grid').getBoundingClientRect().top + scrollY);
    await page.evaluate(new Function('return ' + isolate)(), '.pg-grid');
    await page.waitForTimeout(1500);
    const after = await page.evaluate(() => document.querySelector('.pg-grid').getBoundingClientRect().top + scrollY);
    clip.y -= (before - after);          // the grid moved up by whatever was hidden above it
    console.log('pg clip css px:', JSON.stringify(clip));
    const buf = await page.screenshot({ clip, fullPage: true, timeout: 420000 });
    fs.writeFileSync(`${OUT}/pg-${THEME}-hi.png`, buf);
    console.log('pg  ', size(buf), (buf.length / 1e6).toFixed(1) + ' MB');
    await page.close();
  }

  await browser.close();
})();
