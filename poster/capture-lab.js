const { chromium } = require('playwright-core');
const shared = require('./theme-shared.js');
const BASE = 'https://timothyfraser.com/netsci';
const OUT = __dirname + '/shots';
(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium',
    proxy: { server: process.env.HTTPS_PROXY }, args: ['--ssl-version-max=tls1.2'] });
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 },
    deviceScaleFactor: 3, ignoreHTTPSErrors: true });
  for (const theme of ['white', 'grey', 'red', 'orig']) {
    const page = await ctx.newPage();
    await page.goto(`${BASE}/case-studies/centrality.html`, { waitUntil: 'load', timeout: 60000 });
    await page.waitForTimeout(4000);
    await shared.dress(page, theme);
    await page.waitForTimeout(1800);
    const nodes = page.locator('#network-svg circle');
    const n = await nodes.count();
    if (n > 5) { await nodes.nth(Math.floor(n / 2)).click({ force: true }); await page.waitForTimeout(1800); }
    await page.locator('section.lab-layout').scrollIntoViewIfNeeded();
    await page.waitForTimeout(1000);
    await shared.paint(page, theme);
    await page.waitForTimeout(400);
    await page.locator('section.lab-layout').screenshot({ path: `${OUT}/lab-${theme}.png` });
    console.log('ok lab', theme);
    await page.close();
  }
  await browser.close();
})();
