// Final playground shot: run a network plot and frame editor + output.
const { chromium } = require('playwright-core');

const BASE = 'https://timothyfraser.com/netsci';
const OUT = __dirname + '/shots';

const CODE = `# Zachary's karate club — who bridges the club?
import pandas as pd, networkx as nx
import matplotlib.pyplot as plt

nodes = pd.read_csv("karate-nodes.csv")
edges = pd.read_csv("karate-edges.csv")
G = nx.from_pandas_edgelist(edges, source="source", target="target")
print("Nodes:", G.number_of_nodes(), " Edges:", G.number_of_edges())

bet = nx.betweenness_centrality(G)
top = max(bet, key=bet.get)
print("Top betweenness:", top, round(bet[top], 3))

pos = nx.spring_layout(G, seed=42)
plt.figure(figsize=(6.4, 4.8))
nx.draw_networkx(
    G, pos,
    node_color=[bet[n] for n in G.nodes],
    cmap="viridis",
    node_size=[2500 * bet[n] + 120 for n in G.nodes],
    font_size=7, font_color="white", edge_color="#aaaaaa",
)
plt.title("Karate club — sized & colored by betweenness")
plt.axis("off")
plt.tight_layout()
plt.show()
`;

(async () => {
  const browser = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium',
    proxy: { server: process.env.HTTPS_PROXY || process.env.https_proxy },
    args: ['--ssl-version-max=tls1.2'],
  });
  const ctx = await browser.newContext({
    viewport: { width: 1600, height: 1000 },
    deviceScaleFactor: 2,
    ignoreHTTPSErrors: true,
  });
  const page = await ctx.newPage();
  await page.goto(`${BASE}/playground-py.html`, { waitUntil: 'load', timeout: 90000 });
  await page.waitForFunction(
    () => (document.querySelector('#status-text')?.textContent || '').includes('Ready'),
    { timeout: 180000 }
  );
  console.log('ready');
  await page.selectOption('#sample-select', 'karate');
  await page.waitForTimeout(3000); // stages karate CSVs into the WASM FS
  await page.evaluate((code) => {
    const cm = document.querySelector('.CodeMirror').CodeMirror;
    cm.setValue(code);
  }, CODE);
  await page.click('#btn-run');
  try {
    await page.waitForFunction(
      () => document.querySelector('#plots img, #plots canvas') !== null,
      { timeout: 120000 }
    );
    console.log('plot rendered');
  } catch {
    console.log('no plot appeared');
    await page.click('[data-tab="console"]');
    await page.waitForTimeout(500);
    console.log('CONSOLE:', (await page.textContent('#console')).slice(0, 800));
  }
  await page.click('[data-tab="plots"]');
  await page.waitForTimeout(1000);
  // Frame: put the status pill at the top of the viewport so editor+output fill the shot
  await page.evaluate(() => {
    const el = document.querySelector('#status');
    const y = el.getBoundingClientRect().top + window.scrollY - 30;
    window.scrollTo(0, y);
  });
  await page.waitForTimeout(800);
  await page.screenshot({ path: `${OUT}/playground-plot.png` });
  console.log('ok playground-plot');
  await browser.close();
})();
