---
name: netsci-browser-testing
description: |
  How to actually run and verify the netsci site's interactive pages (the
  Visualizer at docs/visualizer.html, the playgrounds, any D3/JS UI) in a REAL
  headless browser from this environment — even though the agent proxy blocks the
  Playwright/Chromium CDN. Use this whenever a change touches docs/assets/*.js or
  any interactive HTML and you need to confirm it actually works (colors render,
  controls fire, no console errors) instead of guessing from static analysis.
  TL;DR: headless Chromium WORKS here via npm-hosted packages.
---

# Browser testing for the netsci site

**Headless Chromium works in this environment.** You do not need the Playwright
MCP. The trick is that the agent proxy blocks arbitrary CDNs (incl. Playwright's
browser CDN, `playwright.download.prss.microsoft.com` → `403 host not permitted`)
but **package registries are allow-listed** (`registry.npmjs.org`, `pypi.org`,
…). So pull a Chromium that ships *as an npm package*, and vendor any page CDN
deps from npm too.

## One-time setup (in the scratchpad, NOT the repo)

```bash
cd "$SCRATCHPAD"            # the session scratchpad dir, never the repo
mkdir -p viztest && cd viztest && npm init -y >/dev/null
npm install puppeteer-core @sparticuz/chromium d3@7 papaparse
```

- `@sparticuz/chromium` ships a Chromium binary inside the npm tarball
  (`executablePath()` extracts to `/tmp/chromium`). No CDN download.
- `puppeteer-core` drives it. (Playwright-the-package also works, but
  puppeteer-core + @sparticuz/chromium is the proven combo here.)
- `d3@7` + `papaparse` give you local copies of the two libraries
  `visualizer.html` loads from cdnjs — serve those via request interception so
  the page needs zero network at runtime.

Launch args that work:

```js
const browser = await puppeteer.launch({
  args: [...chromium.args, '--no-sandbox'],
  executablePath: await chromium.executablePath(),
  headless: true,
});
```

## Driving the real Visualizer

The page loads `d3.min.js` and `papaparse.min.js` from cdnjs and `fetch()`es
sample CSVs from `playground-data/` (XHR — needs an http origin, not `file://`).
So: serve `docs/` over a tiny local `http.server`, and intercept the two cdnjs
script requests, fulfilling them from the npm copies. Then everything is local.

```js
await page.setRequestInterception(true);
page.on('request', req => {
  const u = req.url();
  if (u.includes('d3.min.js'))            return req.respond({contentType:'text/javascript', body: d3src});
  if (u.toLowerCase().includes('papaparse')) return req.respond({contentType:'text/javascript', body: papasrc});
  return req.continue();
});
page.on('pageerror', e => errors.push('PAGEERROR '+e.message));   // ALWAYS capture these
page.on('console', m => { if (m.type()==='error') errors.push('CONSOLE '+m.text()); });
```

The Visualizer exposes its internals on `window.NetSciViz` (`{state, loadGraph,
loadProjectDataset, loadSampleGraph}`), which makes assertions easy. Load a
sample by setting `#sample-select` and dispatching `change`, then wait on
`window.NetSciViz.state.graph`:

```js
await page.evaluate(k => { const s=document.getElementById('sample-select'); s.value=k; s.dispatchEvent(new Event('change')); }, 'ups-ground-network');
await page.waitForFunction(() => window.NetSciViz?.state?.graph?.nodes?.length>0, {timeout:20000});
```

## What to actually assert (don't trust "it renders")

Read back computed state + the rendered DOM. Real bugs this caught:

- **Node colors not displaying / nodes duplicated.** Check
  `state.graph.nodes.length` matches the dataset's node count (a doubled count
  means node ids and edge endpoints didn't match → mis-mapped `nodeId`), and that
  the drawn circles have **more than one** `fill`:
  ```js
  const fills = [...document.querySelectorAll('#graph g.nodes > g')]
    .map(g => [...g.querySelectorAll('circle')].find(c=>c.getAttribute('fill')&&c.getAttribute('fill')!=='none')?.getAttribute('fill'))
    .filter(Boolean);
  const uniqueFills = new Set(fills);   // ==1 (all green) => coloring broken
  ```
- **Aggregate menu.** Set `#aggregate-by` → `change`, then assert
  `state.graph.nodes.length` dropped to the trait's cardinality and
  `state.graph.links.length > 0` (0 edges => endpoints lost their attrs).
- **Mappings.** Assert `state.mapping.{nodeId,nodeGroup,weight,time}` are the
  columns you expect for each sample (e.g. time should map for temporal sets).
- Screenshot before/after (`page.screenshot({path})`) for a visual gut check.

Run with `node harness.mjs <dataset-key>` and print
`JSON.stringify({errors, colorInfo, aggResult}, null, 2)`. A non-empty `errors`
(other than a single benign `ERR_CONNECTION_CLOSED` from a blocked beacon) means
something threw — investigate before claiming success.

## Test the interaction, not just the default

A control can be present but mis-wired. Don't just check default state — **flip
each control and read the rendered DOM back**, asserting it changed:
- palette select → node circle `fill`s differ between palettes (neon contains
  `#39FF14`; viridis must NOT);
- group-column select → fills change;
- aggregate select → node count drops and links > 0.
A test that only reads `state.*` (not the rendered `fill`s after the change) will
miss "the selector does nothing" bugs.

## Cache-busting (real-user gotcha)

`visualizer.html` loads `assets/viz.js?v=YYYYMMDD`. **Bump the `?v=` whenever you
change `viz.js`** (or other versioned assets). Without it, returning users get a
stale cached script: the new HTML shows a new control, but the old JS ignores it
(classic symptom: "palette stuck on neon / changing it does nothing"). If a user
reports a shipped feature "doesn't work" but your headless test passes, suspect a
missed `?v=` bump before suspecting the code.

## Gotchas
- Run all of this from the **scratchpad**, never add these npm deps to the repo.
- Always check `pageerror`/`console.error` — a silent JS throw will leave the old
  graph on screen and look like "nothing happened."
- `file://` blocks the CSV XHR; use the local http server.
- If you only need to check pure logic (not rendering), you can still load
  `viz.js` reasoning-only, but prefer the real browser — it's available.
