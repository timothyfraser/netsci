// Interaction-driven captures: interactive lab, loaded visualizer, running Python playground, phone keyboard.
const { chromium } = require('playwright-core');

const BASE = 'https://timothyfraser.com/netsci';
const OUT = __dirname + '/shots';

(async () => {
  const browser = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium',
    proxy: { server: process.env.HTTPS_PROXY || process.env.https_proxy },
    args: ['--ssl-version-max=tls1.2'],
  });

  const desktop = await browser.newContext({
    viewport: { width: 1600, height: 1000 },
    deviceScaleFactor: 2,
    ignoreHTTPSErrors: true,
  });

  // 1. Centrality lab — the interactive network itself
  {
    const page = await desktop.newPage();
    await page.goto(`${BASE}/case-studies/centrality.html`, { waitUntil: 'load', timeout: 60000 });
    await page.waitForTimeout(5000);
    await page.locator('#network-svg').scrollIntoViewIfNeeded();
    await page.waitForTimeout(2500);
    // click a node to populate the inspector, if nodes are clickable circles
    try {
      const nodes = page.locator('#network-svg circle');
      const n = await nodes.count();
      if (n > 5) { await nodes.nth(Math.floor(n / 2)).click({ force: true }); await page.waitForTimeout(1500); }
    } catch (e) { console.log('node click skipped:', e.message.split('\n')[0]); }
    await page.screenshot({ path: `${OUT}/lab-interactive.png` });
    console.log('ok lab-interactive');
    await page.locator('#learning-checks').scrollIntoViewIfNeeded();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: `${OUT}/lab-learning-checks.png` });
    console.log('ok lab-learning-checks');
    await page.close();
  }

  // 2. Visualizer with a dataset loaded
  {
    const page = await desktop.newPage();
    await page.goto(`${BASE}/visualizer.html`, { waitUntil: 'load', timeout: 60000 });
    await page.waitForTimeout(6000);
    const values = await page.$$eval('#sample-select option', (os) => os.map((o) => o.value).filter(Boolean));
    console.log('viz samples:', values.slice(0, 8).join(','));
    const pick = values.find((v) => /power/.test(v)) || values.find((v) => /transit|metro|supply/.test(v)) || values[0];
    if (pick) {
      await page.selectOption('#sample-select', pick);
      console.log('viz loaded sample:', pick);
      await page.waitForTimeout(9000);
    }
    await page.locator('#graph-stage').scrollIntoViewIfNeeded();
    await page.waitForTimeout(2000);
    try { await page.click('#btn-fit'); await page.waitForTimeout(2000); } catch {}
    await page.screenshot({ path: `${OUT}/visualizer-loaded.png` });
    console.log('ok visualizer-loaded');
    await page.close();
  }

  // 3. Python playground — wait for Ready, load sample, run, show plot
  {
    const page = await desktop.newPage();
    await page.goto(`${BASE}/playground-py.html`, { waitUntil: 'load', timeout: 90000 });
    try {
      await page.waitForFunction(
        () => (document.querySelector('#status-text')?.textContent || '').includes('Ready'),
        { timeout: 180000 }
      );
      console.log('pyodide ready');
    } catch { console.log('pyodide never ready — capturing as-is'); }
    const values = await page.$$eval('#sample-select option', (os) => os.map((o) => o.value).filter(Boolean));
    console.log('pg samples:', values.slice(0, 8).join(','));
    const pick = values.find((v) => /karate|power|supply/.test(v)) || values[0];
    if (pick) { await page.selectOption('#sample-select', pick); await page.waitForTimeout(2000); console.log('pg sample:', pick); }
    try { await page.click('#btn-run'); await page.waitForTimeout(15000); } catch (e) { console.log('run failed', e.message.split('\n')[0]); }
    try { await page.click('[data-tab="plots"]'); await page.waitForTimeout(1500); } catch {}
    await page.locator('#btn-run').scrollIntoViewIfNeeded();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: `${OUT}/playground-running.png` });
    console.log('ok playground-running');
    await page.close();
  }

  // 4. Phone — block keyboard on the Python playground
  const phone = await browser.newContext({
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 3,
    isMobile: true,
    hasTouch: true,
    ignoreHTTPSErrors: true,
    userAgent:
      'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
  });
  {
    const page = await phone.newPage();
    await page.goto(`${BASE}/playground-py.html`, { waitUntil: 'load', timeout: 90000 });
    try {
      await page.waitForFunction(
        () => (document.querySelector('#status-text')?.textContent || '').includes('Ready'),
        { timeout: 180000 }
      );
    } catch {}
    const values = await page.$$eval('#sample-select option', (os) => os.map((o) => o.value).filter(Boolean));
    const pick = values.find((v) => /karate|power|supply/.test(v)) || values[0];
    if (pick) { await page.selectOption('#sample-select', pick); await page.waitForTimeout(2000); }
    // make sure block keyboard is open and in view
    try {
      const kbd = page.locator('#kbd');
      if (!(await kbd.isVisible())) { await page.click('#kbd-toggle'); await page.waitForTimeout(1000); }
      await page.locator('#btn-run').scrollIntoViewIfNeeded();
      await page.waitForTimeout(1000);
    } catch (e) { console.log('kbd handling:', e.message.split('\n')[0]); }
    await page.screenshot({ path: `${OUT}/phone-keyboard.png` });
    console.log('ok phone-keyboard');
    await page.close();
  }

  await browser.close();
})();
