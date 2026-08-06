// Print-resolution capture of the case-study lab.
// Chromium silently fails to raster past ~16384 px in a dimension, so the scale factor
// is chosen to keep both dimensions under that; the result is verified, not assumed.
const { chromium } = require('playwright-core');
const shared = require('./theme-shared.js');
const fs = require('fs');

const BASE = 'https://timothyfraser.com/netsci';
const OUT = __dirname + '/shots';
const THEME = process.argv[2] || 'stagelight';
const DSF = +(process.argv[3] || 12);

(async () => {
  const browser = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium',
    proxy: { server: process.env.HTTPS_PROXY },
    args: ['--ssl-version-max=tls1.2'],
  });
  const ctx = await browser.newContext({
    viewport: { width: 1280, height: 900 }, deviceScaleFactor: DSF, ignoreHTTPSErrors: true,
  });
  const page = await ctx.newPage();
  await page.goto(`${BASE}/case-studies/centrality.html`, { waitUntil: 'load', timeout: 90000 });
  await page.waitForTimeout(4500);
  await shared.dress(page, THEME);
  await page.waitForTimeout(2000);

  const nodes = page.locator('#network-svg circle');
  const n = await nodes.count();
  if (n > 5) { await nodes.nth(Math.floor(n / 2)).click({ force: true }); await page.waitForTimeout(2000); }
  const selected = await page.evaluate(() => {
    const el = document.querySelector('#lab-selected, .lab-selected, section.lab-layout');
    return (el ? el.textContent : '').includes('RIVERSIDE') ||
           (document.body.textContent || '').includes('SHORTEST PATHS THROUGH THIS NODE');
  });
  console.log('node selected:', selected);

  await page.locator('section.lab-layout').scrollIntoViewIfNeeded();
  await page.waitForTimeout(1200);
  await shared.paint(page, THEME);
  await page.waitForTimeout(600);

  const buf = await page.locator('section.lab-layout').screenshot({ timeout: 420000 });
  const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20);
  fs.writeFileSync(`${OUT}/lab-${THEME}-hi.png`, buf);
  console.log(`lab ${w}x${h}  ${(buf.length / 1e6).toFixed(1)} MB  (limit 16384 -> ${w < 16384 && h < 16384 ? 'OK' : 'OVER'})`);
  await browser.close();
})();
