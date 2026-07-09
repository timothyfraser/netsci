# Building an Interactive, AI‑Supported Coding Course — A Platform Playbook

*A handoff for a fresh agent (and instructor) who has a starter codebase for a
coding‑heavy course and wants to turn it into a polished, interactive,
AI‑supported website with Canvas integration — the way this course did.*

---

## 0. How to read this

You are starting from **an existing course**: some lecture notes or a book‑style
website (Bookdown/Quarto/GitBook/Jekyll/plain HTML), a set of coding exercises,
maybe some datasets. It works, but it is static prose. You want to add the layer
that made *this* course feel alive:

1. A **dedicated, polished class website** (not a generic LMS page).
2. **In‑browser code playgrounds** — students run real R and Python in the
   browser with zero install, via WebAssembly.
3. A **domain‑specific interactive tool** (here: a network Visualizer) that lets
   students *manipulate* the subject matter and **export runnable code** of what
   they just did.
4. **Synced project datasets** with uniform READMEs/codebooks and a
   single‑source‑of‑truth pipeline that feeds the site, the playgrounds, and the
   AI tools.
5. **Interactive learning checks** whose answers are captured and made available
   to the grading bot.
6. An **AI study companion** (a NotebookLM "classbot") grounded in the course
   content that tutors Socratically and refuses to hand out answers.
7. **AI‑assisted grading** — a rubric‑driven bot that drafts structured feedback
   for routine and larger assignments and publishes it to Canvas.
8. **Canvas integration** — push course structure, sync due dates, pull
   submissions, push grades — over the Canvas REST API.

This document is **not a carbon copy of any one course**. It is the reusable
*architecture* and the *decisions that mattered*, written so any instructor can
adapt them to a new subject on top of a provided starter codebase. Each section
says: **what it is**, **why it worked**, **how it's built (stack + mechanism,
with real code)**, **what's generic vs. course‑specific**, and **how to adapt +
extend it**.

Where a mechanism has a reference implementation, the file path is given so you
can read the original. The critical code is inlined so this document stands on
its own.

> **The one‑sentence thesis.** A static site on free hosting + WebAssembly
> runtimes in the browser + a single source of truth with generators + a thin
> Canvas API layer gives you a fully interactive, AI‑supported course with **no
> backend server to run, near‑zero hosting cost, and content that keeps working
> for years.**

---

## 1. The architecture at a glance

```
                       ┌─────────────────────────────────────────────┐
   SINGLE SOURCE       │  data/projects/<name>/                       │
   OF TRUTH            │    _generate.py  (deterministic, seed=42)    │
                       │    nodes.csv  edges.csv  README.md           │
                       │    load.R  load.py  thumb.png                │
                       └───────────────┬─────────────────────────────┘
                                       │  generators / sync scripts
        ┌──────────────────────────────┼───────────────────────────────┐
        ▼                              ▼                                ▼
  docs/playground-data/        docs/*.html (the site)          .notebook/*.md
  (flat, prefixed CSVs)        + generated menus               (AI study bundle)
        │                              │                                │
        ▼                              ▼                                ▼
  ┌───────────────┐          ┌───────────────────┐            ┌────────────────┐
  │  PLAYGROUNDS  │          │   THE WEBSITE      │            │  STUDY BOT     │
  │ WebR (R)      │◄────────►│ static HTML on     │            │  (NotebookLM)  │
  │ Pyodide (Py)  │ handoff  │ GitHub Pages       │            │  Socratic,     │
  │ CodeMirror    │          │ vanilla JS + CDN   │            │  answer‑refusing│
  └───────────────┘          │ design tokens/CSS  │            └────────────────┘
        ▲                    └─────────┬─────────┘
        │ "Open in playground"          │  same content files, re‑consumed
        │ (localStorage handoff)        ▼
  ┌───────────────┐          ┌───────────────────┐            ┌────────────────┐
  │ VISUALIZER    │          │  LEARNING CHECKS   │───────────►│  GRADING BOT   │
  │ D3 + module   │─exports─►│  MC (in‑page JS)   │  answer     │ .grading Flask │
  │ registry +    │  code    │  + code LC (parity)│  keys       │ rubric→LLM→    │
  │ event bus     │          │  + self‑grade      │             │ Canvas comment │
  └───────────────┘          └───────────────────┘            └───────┬────────┘
                                                                       │ Canvas REST
                                            ┌──────────────────────────▼────────┐
                                            │  CANVAS  (.canvas push structure,  │
                                            │  sync due dates; .grading pull     │
                                            │  submissions, push grades)         │
                                            └────────────────────────────────────┘
```

### The load‑bearing design principles

These are the choices that made everything else cheap and durable. Steal these
first; the specific features are downstream of them.

| Principle | What it means | Why it mattered |
|---|---|---|
| **Static + WASM = no backend** | The site is static files; code execution happens in the student's browser via WebAssembly runtimes streamed from public CDNs. | No server to run, secure, near‑zero cost, and it keeps working even if you stop maintaining it. |
| **Single source of truth + generators** | Datasets, menus, AI bundles, indexes are all *generated* from canonical files. You never hand‑edit a derived artifact. | Change one file, regenerate, everything downstream is consistent. |
| **Convention over framework** | Plain HTML + vanilla JS + CDN libraries. No bundler, no build step for the interactive parts. | Portable into *any* host site (Bookdown, Quarto, Jekyll, plain HTML); trivial to reason about; nothing rots. (Cost: some duplication — see §13.) |
| **Instructor/student branch firewall** | A gold `instructor` branch holds everything; a generated `main` branch is a pruned student subset. | Instructor tooling, answer keys, and grading never leak to students, enforced by CI, not vigilance. |
| **Dual‑consumption of content** | The same content files feed *both* the study bot (which must refuse answers) *and* the grader (which needs answers). | One authoring surface, two audiences — but you must keep the answer‑key corpus separate from the tutor corpus (§6, §13). |
| **Determinism everywhere** | Every generator seeds `numpy.default_rng(42)`; re‑running byte‑reproduces outputs. | Reproducible datasets, testable planted effects, no surprise diffs. |
| **Progressive enhancement** | The UI is useful before the heavy runtime finishes loading (code appears in the editor before WebR boots). | 30 MB WASM downloads don't block the student from reading/seeing. |

### The full tech stack

| Layer | Technology | Notes / version |
|---|---|---|
| Hosting | **GitHub Pages** (served from a branch's `/docs`) | Free, static, custom domain at the account level. No server headers possible — this constrains the WASM story (§3). |
| Site | **Plain HTML + vanilla JS + CSS custom properties** | No framework. Shared theme in `docs/assets/design.css`; components in `site.css`. |
| R runtime | **WebR** (`https://webr.r-wasm.org/latest/webr.mjs`) | R compiled to WebAssembly. Runs entirely client‑side. |
| Python runtime | **Pyodide** (`https://cdn.jsdelivr.net/pyodide/v0.26.2/full/`) | CPython + scientific stack compiled to WebAssembly. |
| Code editor | **CodeMirror 5.65.16** (cdnjs) | R and Python modes, themes, bracket matching. |
| Visualization | **D3 v7.8.5**, **PapaParse 5.4.1**, **Driver.js 1.3.1** (cdnjs) | Force‑directed SVG graph, CSV parsing, guided tour. |
| Datasets | **Python** (numpy + pandas) generators; **CSV** everywhere | Deterministic, `seed=42`. |
| Study bot | **Google NotebookLM** + Python bundle builders | Free; grounded in auto‑generated markdown bundles. |
| Grading bot | **Local Flask app** + LLM via an **API gateway** (LiteLLM/OpenAI SDK) | Rubric‑injected prompts → structured JSON → Canvas comment. |
| LMS | **Canvas REST API v1** via Python + a personal access token | Not LTI, not QTI. Idempotent name‑matched pushes. |
| CI | **GitHub Actions** | Publishes the student subset, AI bundles, a sample‑report PDF, and a single‑file offline export. |

---

## 2. The website (the foundation)

### What it is

The entire site is `docs/` — a set of **hand‑authored, fully standalone HTML
pages** served by GitHub Pages. There is **no framework**: no Jekyll config, no
Bookdown, no bundler. Each page is a complete `.html` document.

### Why it worked

- **Zero build friction for interactivity.** Because pages are plain HTML that
  pull libraries from CDNs, you can drop a `<script>` that boots a WebAssembly
  runtime into any page without a toolchain. This is *the* reason the
  interactive features were cheap to add.
- **Portable.** The interactive components (playground, visualizer) are
  self‑contained vanilla‑JS + CDN artifacts. They embed in *any* host — so if
  your starter codebase is a Bookdown/Quarto book, you don't have to migrate it;
  you drop the interactive pieces in as standalone pages or iframes.
- **Durable.** Nothing depends on a package registry resolving at build time.

### How it's built

**Design tokens live in one file.** `docs/assets/design.css` defines the theme
as CSS custom properties (colors, fonts). Every page and even the Canvas
generator references these values, so the brand is consistent and changes in one
place:

```css
:root {
  --green-bright: #39FF14;
  --black: #050a05;
  /* …fonts imported from Google Fonts… */
}
```

**Shared behavior, not shared markup.** `docs/assets/site.js` does *not* inject
the nav; it only *enhances* markup already on the page — it highlights the active
nav link by reading `document.body.dataset.page` and matching `a[data-page]`, and
wires dropdown menus. A couple of scripts *do* inject shared elements on every
page: `network-bg.js` (animated background) and `notebooklm-bubble.js` (the study‑bot
FAB). A per‑page "On this page" sidebar (`case-toc.js`) self‑builds by scanning
for a whitelist of section IDs and only renders if ≥2 are present — so a page
opts in purely by using those IDs.

> **Fragility to fix in a new build (§13).** The nav bar is **copy‑pasted into
> every page** — there is no server‑side include. Changing a nav link means
> editing ~40 files. In a fresh build, add a tiny include step: either a 20‑line
> `build_nav.py` that splices nav markup between `<!-- NAV -->` markers, or a
> client‑side `fetch('/_nav.html')` injected by `site.js`, or use your book
> generator's native layout if you keep one for prose.

### The instructor/student branch firewall

This is one of the highest‑leverage ideas. Two branches:

- **`instructor`** — the gold source of truth. Everything: the site, scripts,
  answer keys, grading tooling, Canvas scripts. **All work happens here** (feature
  branch → PR into `instructor`). **GitHub Pages serves the live site from
  `instructor`/`docs`.**
- **`main`** — a *generated* student subset. A CI job, on every push to
  `instructor`, checks out `main`, **prunes everything**, then restores *only*
  whitelisted paths:

```yaml
# .github/workflows/publish-student-subset.yml
env:
  WHITELIST: "data code quickstart setup.sh .Rprofile README.md LICENSE .gitignore"
```
```bash
git rm -r -q . || true
for p in ${WHITELIST}; do
  if git cat-file -e "origin/instructor:${p}" 2>/dev/null; then
    git checkout "origin/instructor" -- "${p}"
  fi
done
```

The prune‑then‑restore approach mirrors adds/edits/**deletes** and *guarantees*
no instructor‑only file can ever linger on `main`. Students clone/browse `main`;
the website they use is served from `instructor`. Answer keys, grading prompts,
and Canvas tokens live in dot‑prefixed dirs (`.canvas/`, `.grading/`,
`.notebook/`) that are simply never on the whitelist.

Instructor *pages* that must be on the public site (`docs/instructor/…`) are
hidden by convention, not access control: not linked anywhere, `robots.txt`
`Disallow: /instructor/`, and `<meta name="robots" content="noindex, nofollow">`.
**Know the limit:** this is security‑by‑obscurity — anyone who guesses the URL
can read them. Never put real answer keys or secrets in `docs/`; keep them in the
non‑whitelisted dot‑dirs.

### CI workflows (all trigger on push to `instructor`)

| Workflow | Builds | Publishes |
|---|---|---|
| `publish-student-subset.yml` | prune+restore whitelist | regenerated `main` branch |
| `publish-standalone.yml` | `node scripts/build-standalone.mjs` | a single‑file offline site as a **GitHub Release** asset (§10) |
| `notebook-bundles.yml` | 5 Python builders | refreshed `.notebook/*.md`, auto‑committed back |
| `sample-report-pdf.yml` | pandoc + xelatex | the exemplar assignment PDF, auto‑committed |

### Adapt it

- Keep your prose in whatever generator you already have (Bookdown/Quarto) **if
  you like it** — you only need plain HTML pages for the *interactive* surfaces,
  and those can live alongside a book. The playground and visualizer don't care
  what generated the surrounding page.
- Adopt the branch firewall on day one; it's much harder to retrofit once
  answer keys have leaked into history.
- Put the theme in CSS custom properties in one file from the start.

---

## 3. In‑browser code playgrounds (WebAssembly) — the crown jewel

This is the feature instructors most want to understand: *how did we run real R
and Python in the browser with no server?* Here is the whole story.

### What it is

Two standalone pages — `docs/playground-r.html` (WebR) and
`docs/playground-py.html` (Pyodide) — each a **fully self‑contained** artifact
(all logic inline in the HTML; only cosmetic scripts are shared). A student opens
the page, waits ~10–30 s the first time while a ~30 MB WebAssembly runtime
streams from a CDN (cached thereafter), and then runs real R/Python: editor,
Run button, console output, plots, a data browser — entirely client‑side.

There is also a static `playground.html` chooser that explains *why two pages*:
each language ships its own ~30 MB bundle, so loading both at once would double
the wait — they're kept separate.

### Why it worked

- **Zero install for students.** No R, no Python, no packages, no PATH problems —
  the #1 friction killer in a coding course, gone.
- **No backend.** Nothing to run, secure, or pay for. The runtime lives in the
  browser tab; the CDN serves immutable WASM.
- **It survives you.** Because the runtimes are public CDNs (WebR, Pyodide,
  jsDelivr), the playground keeps working even if you stop maintaining the site.

### How the R playground works (WebR)

**Bootstrap** — an ES‑module import straight from the WebR CDN:

```html
<script type="module">
import { WebR } from 'https://webr.r-wasm.org/latest/webr.mjs';
const webR = new WebR();          // NB: no options — see the channel gotcha below
await webR.init();
```

**Package install** — eager, before Run is enabled, so every advertised
`library()` is guaranteed to work. WebR installs **precompiled WASM binary
packages** from two repos (tried in array order):

```js
const REPOS = ['https://igraph.r-universe.dev', 'https://repo.r-wasm.org'];
const PACKAGES = ['igraph','dplyr','tidyr','ggplot2','readr','purrr',
                  'tidygraph','ggraph','DBI','RSQLite'];
for (let i = 0; i < PACKAGES.length; i++) {
  setStatus(`Installing packages (${i+1}/${PACKAGES.length}): ${PACKAGES[i]}…`);
  try { await webR.installPackages([PACKAGES[i]], { repos: REPOS }); }
  catch (e) { console.warn('install failed:', PACKAGES[i], e); }   // one bad repo won't strand the session
}
```

> **Critical constraint:** only packages **built for WebAssembly** can be
> installed — i.e. those present in `repo.r-wasm.org` (the WebR CRAN‑for‑WASM
> mirror) or an r‑universe WASM build (like `igraph.r-universe.dev`). A CRAN
> package with compiled C/Fortran that nobody has built for WASM **will not
> install.** Before promising a package to students, verify it's available.
> This is the single biggest gotcha when adapting to a new subject: **check your
> required packages against the WASM repos first.**

**Output + plots** — WebR's `Shelter` + `captureR` captures console output *and*
the R graphics device (base `plot()` *and* `ggplot2`/`ggraph`) as image bitmaps:

```js
const shelter = await new webR.Shelter();
try {
  const cap = await shelter.captureR(code, {
    captureGraphics: { width: 600, height: 400 },
    withAutoprint: true,     // bare expressions print like a REPL
  });
  appendConsole(cap.output);                 // [{type:'stdout'|'stderr'|'message', data}]
  for (const img of (cap.images || [])) addPlotFromImageBitmap(img);
} finally {
  shelter.purge();           // free WASM memory every run — prevents leaks
}
```

### How the Python playground works (Pyodide)

**Bootstrap** — pinned version, main‑thread runtime:

```html
<script type="module">
import { loadPyodide } from 'https://cdn.jsdelivr.net/pyodide/v0.26.2/full/pyodide.mjs';
const pyodide = await loadPyodide({ indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.26.2/full/' });
```

**Package install** — `pyodide.loadPackage()` (not micropip) pulls Pyodide's own
curated WASM wheels from the pinned `indexURL`:

```js
const PACKAGES = ['matplotlib','numpy','pandas','igraph','networkx','scipy','scikit-learn'];
for (let i = 0; i < PACKAGES.length; i++) {
  try { await pyodide.loadPackage([PACKAGES[i]]); } catch (e) { console.warn(e); }
}
// micropip is offered to students only as an escape hatch for extra pure-Python wheels.
```

**Plot capture** — matplotlib runs headless (`AGG`) and `plt.show` is
monkey‑patched to stash each figure as a base64 PNG that JS then renders:

```python
import matplotlib; matplotlib.use('AGG')
import matplotlib.pyplot as plt, io, base64
_plots = []
def _capture_show(*a, **k):
    fig = plt.gcf()
    if fig.get_axes():
        buf = io.BytesIO(); fig.savefig(buf, format='png', dpi=110, bbox_inches='tight')
        _plots.append(base64.b64encode(buf.getvalue()).decode())
    plt.close('all')
plt.show = _capture_show      # students call plt.show() to send a figure to the Plots tab
```

Console capture is direct: `pyodide.setStdout/​setStderr({batched: …})` then
`await pyodide.runPythonAsync(code)`.

### The gotcha that will bite you: cross‑origin isolation (COOP/COEP)

**This is the single most important thing to know for a GitHub Pages course.**

- **WebR's *fast* channel uses `SharedArrayBuffer`, which requires the page to be
  *cross‑origin isolated*** (`Cross-Origin-Opener-Policy: same-origin` +
  `Cross-Origin-Embedder-Policy: require-corp`). **GitHub Pages cannot set
  response headers**, so a Pages site is *not* cross‑origin isolated and
  `SharedArrayBuffer` is unavailable.
- **The workaround here is runtime choice, not headers.** Calling `new WebR()`
  with **no channel option** lets WebR auto‑select its **non‑SharedArrayBuffer
  fallback channel** (PostMessage/service‑worker). The repo sets **no COOP/COEP
  anywhere** — production runs on the fallback channel by design. Slightly slower
  interrupt handling; otherwise fully functional.
- **Pyodide sidesteps the issue entirely** — it doesn't need `SharedArrayBuffer`
  or isolation. This is why the Python playground "just works" on a static host
  with zero configuration. **If you add only one runtime first, start with
  Pyodide.**
- If you *do* want WebR's fast path on Pages, the usual trick is
  `coi-serviceworker.js` (a service worker that re‑serves the page with synthetic
  COOP/COEP headers). This course deliberately avoided that complexity.

> **Version‑pinning lesson.** Pyodide is pinned (`v0.26.2`); WebR is pulled from
> `latest`. Pulling `latest` means an upstream WebR release can silently change
> behavior with no change in your repo. **Pin both** to fixed releases for a
> durable course.

### Data access: staging CSVs into the virtual filesystem

The playgrounds don't read URLs from inside R/Python. The JS layer stages files
into the WASM **virtual filesystem** first, then student code reads them as
ordinary local files:

```js
// pick a dataset → fetch its CSVs relative to the page → write into the WASM FS
for (const fname of cfg.files) {
  const buf = new Uint8Array(await (await fetch(`playground-data/${fname}`)).arrayBuffer());
  await webR.FS.writeFile('/home/web_user/' + fname, buf);   // (Pyodide: pyodide.FS.writeFile(fname, buf))
  await idbPutFile(fname, buf);                                // cache to IndexedDB so it survives refresh
}
editor.setValue(sampleSnippet(key) + '\n# (previous code below)\n# ' + editor.getValue());
```

The generated starter snippet then just does `read.csv("power-grid-nodes.csv")`
/ `pd.read_csv(...)` against the staged file. A `SAMPLE_CONFIGS` object maps each
dataset key → `{files, title, directed, weight}`, and `sampleSnippet(key)` emits
language‑appropriate starter code (igraph in R, networkx in Python). Uploaded
files go through the same `writeFile` + IndexedDB path.

### Persistence model (both playgrounds)

- **Editor code** → `localStorage` (debounced 500 ms auto‑save).
- **Editor theme** → `localStorage` (shared key across pages).
- **Uploaded + sample CSVs** → **IndexedDB**, restored into the WASM FS on boot
  (uploads survive refresh but never leave the device).
- A **Clear‑cache** button (in a *non‑module* script so it runs even if the WASM
  module hangs) wipes CacheStorage/service workers/`playground-*` localStorage and
  hard‑reloads with a cache‑buster.

### Scaling to "many, many runnable chunks" — the honest path

The instructor's real goal is often *many* runnable code chunks sprinkled through
tutorial pages, not two monolithic playground pages. Here's the candid
assessment and the refactor path.

**What exists today** is a **standalone full‑page app**, plus one deep‑link
primitive: any same‑origin page can preload code by writing a handoff payload to
`localStorage['netsci-playground-handoff']` and `window.open('playground-r.html')`
(this is exactly how the Visualizer's "Open in playground" works — §4). That is a
*new‑tab handoff*, not an in‑page chunk.

**To get many runnable chunks per page**, it's a **refactor, not a rewrite** —
the hard problems (channel fallback, package install, plot capture, FS staging)
are already solved and directly portable. The moves:

1. **One shared runtime per page, not per chunk.** The expensive object is the
   ~30 MB runtime. Boot it **once per page** as a singleton and let N chunk
   widgets share the single `webR`/`pyodide` instance. Booting per chunk is fatal.
2. **Extract the inline logic into a reusable module.** Today `runCode`,
   `loadSample`/`sampleSnippet`, the IndexedDB wrapper, and the handoff reader are
   self‑contained functions duplicated inline across two 1500‑line HTML files.
   Hoist them into `playground-core-r.js` / `playground-core-py.js` exporting a
   `mountChunk(el, {lang, starterCode, datasetKey})` that renders a mini
   editor+output into any element.
3. **Lazy boot on first Run.** For a page with 10 chunks, boot the shared runtime
   the first time *any* chunk's Run is pressed (click or IntersectionObserver),
   then reuse.
4. **Namespace per‑chunk state.** localStorage keys, IndexedDB DB names, and
   element IDs are singletons today; per‑chunk widgets need per‑instance keys/IDs.
5. **Avoid iframe‑per‑chunk** — it reintroduces one‑runtime‑per‑frame. Prefer
   in‑page shared‑singleton widgets.

> If your course is a statistics/coding course, this is likely the highest‑value
> extension: a Markdown/HTML authoring convention (e.g. a `<div class="run-chunk"
> data-lang="r">…code…</div>`) that `mountChunk` upgrades into a live runnable
> block, sharing one runtime per page. Everything you need is already proven in
> the two playground files.

### Adapt it

- **Swap the package lists** for your subject and **verify WASM availability**
  (the #1 adaptation risk for R). Pyodide's scientific stack (numpy, pandas,
  scipy, statsmodels via micropip, scikit‑learn, matplotlib) covers most of a
  statistics course out of the box.
- Keep the **eager‑install‑then‑enable‑Run** pattern; it makes "Ready ✓" a real
  guarantee.
- Keep the **stage‑to‑FS** data model; it's simpler and more robust than trying
  to read URLs from inside the interpreter.

---

## 4. The domain interactive tool (the Visualizer) — a reusable pattern

The Visualizer is subject‑specific (it's a network‑science tool), but its
**architecture is a reusable template for any interactive "explore + export"
tool** — an interactive distribution explorer, a regression/DOE sandbox, a
control‑chart simulator, whatever your subject needs.

### What it is

`docs/visualizer.html` + a core module (`viz2-core.js`) + ~13 feature modules
(`viz2-metrics.js`, `viz2-removal.js`, `viz2-permutation.js`,
`viz2-montecarlo.js`, `viz2-codeexport.js`, …). Students load a dataset, see a
force‑directed graph, and run real analyses (centrality, disruption,
permutation tests, Monte‑Carlo counterfactuals, sampling, community detection)
with live results — then **export runnable R/Python code that reproduces exactly
what they just did.**

### The reusable architecture: registry + event bus + feature modules

No bundler, no ES modules, no framework. **Plain, ordered `<script defer>` tags.**
The core publishes a single global registry; every feature module consumes it:

```js
// core publishes the registry
window.NetSciViz2 = { state, on, emit, utils, loadGraph, render, /* … */ };

// every feature module is an IIFE that bails until core exists, then subscribes
(function () {
  'use strict';
  if (!window.NetSciViz2) return;
  const NV = window.NetSciViz2;
  NV.on('graph-loaded', rebuildMyCard);     // ~10-line pub/sub event bus
  NV.on('metrics-updated', refreshMyStats);
})();
```

Three pieces make this scale to a dozen features without a framework:

1. **One shared `state` object**, mutated in place, referenced by every module.
2. **A ~10‑line event bus** (`on`/`emit` over a `_listeners` map) — core emits
   lifecycle events (`graph-loaded`, `metrics-updated`, `node-selected`,
   `removed-changed`, `scenario-changed`, …); feature modules subscribe and
   re‑render themselves. This decouples features from core with **no
   monkey‑patching**.
3. **Shared math in `NV.utils`** (BFS, Dijkstra, components, quantiles, the
   course's statistics) so every card computes results the *same* way the R/Python
   labs do — the browser numbers match the teaching‑code numbers.

Rendering is **D3 v7 into SVG** (force simulation with degree/edge‑count‑adaptive
constants to avoid the "hairball," plus a freeze‑on‑convergence so before/after
comparisons keep identical node positions). But the *rendering choice is
incidental* — the transferable part is the **registry + event bus + shared‑state +
shared‑utils** pattern, which works for any interactive tool.

### The killer feature: code export + playground handoff

The Visualizer emits a **complete, teaching‑style R or Python script** that
reproduces the current UI state, and hands it to the playground:

- `snapshot()` reads the live state + card settings into a plain object (dataset,
  column mapping, removed nodes/edges, scenario edits, layout, analysis settings).
- `generateR(snap)` / `generatePy(snap)` build the script line by line **in the
  course's teaching style** — a roxygen/docstring banner, idiomatic
  igraph/tidyverse or igraph/pandas, inline pedagogical comments, emoji `cat()`/
  `print()` flourishes.
- **Handoff** to the playground is a shared‑origin localStorage message + a
  new‑tab open:

```js
localStorage.setItem('netsci-playground-handoff', JSON.stringify({
  lang: ui.lang, code, datasetKey: snap.datasetKey, ts: Date.now(), source: 'visualizer',
}));
window.open(ui.lang === 'r' ? 'playground-r.html' : 'playground-py.html', '_blank');
```

The playground reads it in **two stages**: (1) an at‑load IIFE prefills the editor
*immediately* (language‑gated, 5‑minute TTL, consumed once) so code appears even
before the runtime boots; (2) after the runtime is ready, it fetches that
dataset's CSVs into the virtual FS so the pasted `read.csv()` calls resolve. It
does **not** auto‑run — code is visible instantly, execution waits for a genuinely
ready runtime.

> **Why this matters pedagogically.** It closes the loop between *manipulating* a
> concept visually and *writing the code* for it: the student sees the analysis,
> then gets the exact reproducible script and runs it live. This "explore →
> export runnable code → run it" loop is the most transferable idea in the whole
> platform. Any interactive tool you build should emit the code for what it did.

### Adapt it

- Reuse the **registry + event bus + shared‑state** skeleton verbatim for your
  subject's interactive tool; replace the D3 graph with your visualization and the
  feature modules with your analyses.
- Keep the **code‑export + handoff** feature — it's the highest‑value, most
  distinctive part.
- **Refactor friction to fix (§13):** the dataset registry is duplicated in ~4
  places (the visualizer dropdown, `DATASET_MAPPINGS`, the code‑export
  `SAMPLE_CONFIGS_LITE`, and each playground's `SAMPLE_CONFIGS`). In a fresh
  build, define **one JSON dataset manifest** and have the visualizer, code
  exporter, and both playgrounds read it.

---

## 5. Synced project datasets with codebooks (single source of truth)

### What it is

A library of purpose‑built, deterministically‑generated datasets, each a
self‑contained folder with a generator, the data, a uniform README/codebook, and
loaders — all flowing from one canonical location into the site, playgrounds, and
AI tools.

```
data/projects/<name>/
├── _generate.py     # deterministic (numpy default_rng(42)); writes the CSVs
├── nodes.csv        # entities  (first column is the key; never call it `name`)
├── edges.csv        # relations (endpoints first, then a numeric weight column)
├── <lookup>.csv     # optional supplementary table
├── README.md        # At-a-glance block + a codebook table per file
├── load.R           # tiny igraph loader, course teaching style
├── load.py          # tiny loader, course teaching style
└── thumb.png        # generated emoji tile for menus
```

### Why it worked — the "planted story" principle (the pedagogical heart)

A dataset is only worth analyzing if it has **non‑random, domain‑true structure
that tells a story — ideally several overlapping stories — that students must
discover.** The rules that made these datasets teach:

- **"Bigger nodes get more traffic" is NOT a story.** Degree ∝ size is the
  trivial baseline. Plant signal that **survives controlling for the obvious
  confounder**: e.g. delivery on‑time rate that drops with neighborhood income
  *independent of distance*.
- **Layer 2–4 independent stories** so different students find different things
  (an equity gradient, a hidden over‑capacity node, a temporal shock that exposes
  a weak point, a mid‑period structural rewiring).
- **Make it falsifiable and checkable.** After generating, write a quick script
  that confirms each planted effect is present and distinguishable from noise.
- **Add realistic noise** so signals aren't trivially perfect.
- **Never tell students the story** — not in the README, not in obvious column
  names. The `_generate.py` parameters are the **only** record of the design.

Real example — the equity penalty is applied *after* subtracting a distance term,
so it survives controlling for distance:

```python
INCOME_PENALTY = 0.16     # the planted effect (the only record of it lives here)
# on-time rate: distance hurts a little; LOW INCOME hurts a lot (independent of distance)
ot = 0.985 - 0.0011 * dist - INCOME_PENALTY * (1 - income_norm[zi])
ot = float(np.clip(ot + rng.normal(0, 0.015), 0.40, 0.999))   # noise keeps it non-trivial
```

This principle is **fully subject‑transferable**: a statistics course wants
tabular datasets with a planted confound, an interaction, a Simpson's paradox, or
a process shift — same discipline (deterministic generator, planted effect that
survives the naive analysis, checkable, undocumented).

### The codebook format (uniform across every dataset)

Every README has a fixed shape so datasets "feel the same":

1. Title + one‑line tagline.
2. An **At‑a‑glance** two‑column table (direction, weights, modality, temporal
   yes/no, #nodes, #edges, file list).
3. A "what this is" paragraph + example project questions + the required note
   that the interesting findings are deliberately undocumented.
4. **One codebook table per file**, columns exactly:
   `Variable | Full name | Description | Class | Example values` (with 2–3 real
   example values pulled from the data).
5. "Load it" (the `load.R`/`load.py` commands) and "Get this data" (GitHub link).

### The sync pipeline (canonical → everywhere)

`data/projects/` is **canonical**; everything else is generated:

- **`_sync_to_playground.py`** copies each dataset's CSVs to
  `docs/playground-data/<name>-<file>.csv` (flat, prefixed) — because GitHub Pages
  only serves `docs/`, and the playgrounds/visualizer fetch from there.
- **`_make_thumbnails.py`** renders a deterministic emoji tile per dataset.
- **`build_dataset_menus.py`** reads node/edge counts *live from the CSVs* and
  idempotently rewrites the playground load‑panels and the assignments gallery
  between `<!-- PROJECT-DATASETS -->` markers.
- The AI‑bundle builders (§7) pull the READMEs/loaders/generators into the study
  bot.

The same CSVs feed **four consumers**: both playgrounds (via `SAMPLE_CONFIGS` +
`sampleSnippet`), the visualizer (via `DATASET_MAPPINGS` + `loadProjectDataset`),
the assignments page ("Get the project datasets" + generated gallery), and the
NotebookLM bundle. **You never hand‑edit `docs/playground-data/`** — you
regenerate and re‑sync.

> **Fragility (§13):** the marker‑based `re.sub` splice silently no‑ops if the
> anchor string drifts, and `build_dataset_menus.py` is a manual step (no CI runs
> it). And the dataset list is duplicated in several registries. In a fresh
> build, drive all menus + registries from **one JSON manifest** and run the
> generator in CI.

### Adapt it

- Keep the folder standard, the deterministic generator, the codebook table
  format, and the sync scripts almost verbatim (edit the destination path, the
  `ICONS` emoji map, the dataset list, and the repo URL).
- **Codify the standard as a skill/README** so future datasets are authored
  consistently (the reference course keeps a `netsci-dataset-builder` SKILL that
  encodes layout, codebook format, loader templates, and the planted‑story rules).
- The **hard, non‑transferable work is designing good planted stories** for your
  subject; the plumbing is copy‑paste.

---

## 6. Learning checks + exercises (and getting answers back to the bot)

### What it is

Three distinct "learning check" surfaces, loosely connected:

1. **In‑page multiple‑choice checks** inside each tutorial (`docs/case-studies/
   *.html`): a `<div class="lc-card">` with options wired to `onclick=
   "selectOption(n,'A')"`, instant color feedback, Hint/Reveal buttons, and a
   hidden answer div. State is **session‑only** (no persistence). The correct
   answer is either a hardcoded JS map (`const CORRECT_ANSWERS = {1:'B',…}`) or —
   better — **recomputed from the live rendered artifact** so it can't drift out
   of sync with the content.
2. **Teaching‑script learning checks** — every `code/NN_<case>/example.R` and
   `example.py` ends with a section that computes an answer and prints a fixed
   sentinel line, **byte‑identical across R and Python**:

   ```r
   cat(sprintf("\n📝 Learning Check answer: %s\n", answer))     # R
   ```
   ```python
   print(f"\n📝 Learning Check answer: {answer}")                # Python
   ```

   The **parity rule** (R and Python must print the same value on a
   `Learning Check answer: …` line) is a machine contract — the grader regexes it.
3. **A self‑grade checklist** (`checklist.js`) that renders a yes/no list and a
   "copy paste‑able status block" button — self‑assessment, session‑only.

### How answers get "back to the class bot" (the grader)

This is exactly the instructor's ask — *make LC answers available to the bot at
the end.* Two builders produce machine‑readable keys into a **gitignored cache**
(never committed, instructor‑branch‑only):

- **`build_lc_answer_keys.py`** *scrapes* the correct MC answers out of the
  case‑study HTML (parsing the `lc-card` blocks and the JS answer maps) →
  `cache/lc_answer_keys.json`.
- **`build_lc_code_keys.py`** *actually executes* each `example.R`/`example.py`,
  captures the `Learning Check answer:` line, and records the expected value →
  `cache/lc_code_keys.json`.

Those JSON keys are then injected into the LC grading prompt (§8). So the
"aggregation back to the bot" is real, but **semi‑manual** (you re‑run the two
builders after editing labs) and **instructor‑only**.

> **The dual‑consumption trap (important design lesson).** The *same* case‑study
> HTML feeds both the grader (which needs answers) and the study bot's content
> bundle (§7, which must refuse answers). Because the reveal text literally
> contains `Answer: B`, **the MC answers leak into the study‑bot bundle** — the
> bot's refusal rests on its persona, not on redaction. **In a fresh build,
> author answers in a separate machine‑readable key file** (one per check),
> strip reveal text from the study bundle, and let both bots read from the
> appropriate source. Keep the tutor corpus and the answer‑key corpus physically
> separate.

### Adapt + extend it

- Keep the **printed‑sentinel parity contract** — it makes code‑based LCs
  gradable by a dumb regex and keeps R/Python honest. **Add a CI test** that runs
  both languages and diffs the LC line (the reference course relies on convention
  here; a test is a cheap upgrade).
- **Persist in‑page LC state** to localStorage if you want progress to survive a
  refresh (currently it doesn't).
- **Prefer computed‑from‑artifact answers** over hardcoded maps where feasible,
  so checks can't drift from the content.

---

## 7. The AI study companion — "classbot" #1 (NotebookLM)

> Note: *two* different things get called "classbot." This one is the
> **student‑facing Socratic tutor**. §8 is the **instructor‑facing grader**. They
> have opposite goals — the tutor *refuses* answers; the grader *needs* them.

### What it is

A **Google NotebookLM notebook** configured as a Socratic tutor, grounded in
auto‑generated bundles of the course content. Its persona (pasted into "Configure
Chat") **refuses to give direct answers to homework/learning checks/labs and asks
the student questions back**, and it exposes slash commands (`/glossary`,
`/quizme`, `/interpret`, `/methodpick`, `/flashcards`, `/study`, …). It is **free
and needs zero infrastructure.**

### How it's built

Five Python builders concatenate course content into `.notebook/*.md`:

| Builder | Output | Pulls in |
|---|---|---|
| `build_notebooklm_source.py` | `website.md` | visible text of every `docs/*.html` (strips scripts/nav/head, then `markdownify`) |
| `build_coding_bundle.py` | `coding-modules.md` | every `.md/.R/.py` under the repo (excluding docs/scripts/dotdirs) — the teaching scripts, dataset READMEs, loaders, generators |
| `build_index.py` | `index.md` | a curated resource map (title/URL/topic/tags) |
| `build_skills_bundle.py` | `skills.md` | the invokable authoring skills |
| `build_combined_bundle.py` | `netsci-notebooklm.md` | concatenates the four into **one big markdown file** the instructor uploads |

CI (`notebook-bundles.yml`) rebuilds these on every push to `instructor` and
auto‑commits them back (the recurring `chore(notebook): refresh NotebookLM
bundles` commits). NotebookLM doesn't auto‑pull, so the instructor periodically
re‑uploads the one big file.

On the site, `notebooklm-bubble.js` injects a floating "Course Companion" FAB on
every page linking to the notebook (a hardcoded URL), with a first‑time "AI"
badge tracked in localStorage.

### Why it worked

- **Free, instant, grounded.** NotebookLM does the RAG for you; you just curate
  the corpus. No vector DB, no API keys, no hosting.
- **Answer‑refusing by persona** keeps it a tutor, not a cheat sheet.

### Adapt + extend it

- Point the builders at *your* `docs/` and code; write a persona for your subject;
  embed the bubble with your notebook URL.
- **Fix the leak (§6):** strip reveal‑answer text from `website.md` so the tutor
  corpus doesn't contain the keys.
- **Extension:** if you want auto‑refresh and hard answer‑gating (NotebookLM
  can't guarantee refusal), build a small RAG chatbot over the same bundle with a
  system prompt that refuses, and serve it from the site — but that reintroduces
  infrastructure and cost the NotebookLM approach avoids.

---

## 8. AI‑assisted grading — "classbot" #2 (the `.grading` app)

### What it is

A **local Flask/HTTP app** (instructor‑branch‑only, in `.grading/`) that drafts
structured feedback and publishes it to Canvas. Two flows, dispatched by
assignment type: **`project_case_study`** (larger reports, 100 pts) and
**`learning_checks`** (routine, completion‑graded).

### How it works

**A machine‑readable rubric** drives everything (`config/rubric.json`):

```json
{
  "starting_score": 100,
  "target_fine_report_score": 85,
  "requirements": [
    { "id": "min_nodes",     "label": "…", "max_deduction": 8,  "category": "hygiene" },
    { "id": "results_prose", "label": "…", "max_deduction": 10, "category": "content" },
    { "id": "ai_prose",      "label": "…", "max_deduction": 12, "category": "policy"  }
  ]
}
```

Those requirement `id`s **mirror the student self‑grade checklist** (§6) — same
requirements, two audiences.

**The prompt template injects the rubric** and demands **valid‑JSON‑only** output
with a per‑requirement verdict:

```
For each requirement return {id, status (met/partial/missing/not_assessable),
  evidence, location, proposed_deduction, search_hint}
Plus: report_checklist, top_issues, classbot_summary, confidence, client_ai_likelihood.
Anchor: ~85/100 for a fine-but-not-great report.
```

**Learning‑check grading** passes the executed answer keys (§6) into the prompt,
then applies a **deterministic numeric guardrail** on top of the LLM verdict:
`code_values_match()` overrides an LLM "incorrect" to "correct" when the student's
numeric answer is within tolerance (`rtol 0.06 / atol 0.02`) — accounting for
Monte‑Carlo seed variation. So it's **LLM + a deterministic override**, not blind
trust in the model.

**Model + privacy:** the LLM is reached through an **institutional AI gateway**
(LiteLLM behind an OpenAI‑SDK wrapper; default a small fast model, larger models
available for PDFs). Submission text/metadata is **anonymized** before sending; a
`MOCK_LLM=1` mode runs offline against fixtures for development.

**The workflow:** sync submissions from Canvas → run the bot (structured JSON
review) → instructor toggles the proposed deductions in a local web UI → publish
grade + a delineated Instructor/Classbot comment to Canvas. Student work stays in
gitignored caches; `.grading/` never reaches `main`.

There's also a **manual fallback**: `docs/instructor/grading-scratchpad.html`, a
session‑only rubric‑tier picker that exports a paste‑able feedback block for
Canvas SpeedGrader (no AI) — useful when you don't want to run the bot.

### Why it worked

- **Structured, not free‑form.** A JSON rubric → JSON verdict → composed comment
  keeps the bot consistent and the human in control (toggle deductions, edit
  before publish).
- **Deterministic guardrails** where correctness is objective (numeric LC
  answers) — the LLM proposes, arithmetic disposes.
- **Human‑in‑the‑loop by design.** The bot drafts; the instructor approves and
  publishes.

### Adapt + extend it

- Author your **`rubric.json`** for your assignments; the prompt template, Canvas
  client, anonymization, and mock mode are generic.
- Reuse the **LLM + deterministic‑override** pattern for any objectively‑checkable
  item.
- Point the gateway at whatever LLM API you have (any OpenAI‑compatible endpoint).
- **Extension:** add assignment types (the reference course stubs a `poster`
  type); add a calibration set of pre‑graded exemplars to tune the deduction
  anchors.

---

## 9. Canvas integration

### What it is

**Not LTI, not QTI/IMSCC.** It's a set of **Python scripts hitting the Canvas
REST API v1 with a personal access token.** Two subsystems, both instructor‑only:

- **`.canvas/`** — pushes course *structure and content*. A `manifest.json` is
  the single source of truth (course info, theme hex values mirrored from
  `design.css`, assignment groups + weights, assignments, modules). One script
  renders branded HTML cards; another (`push_to_canvas.py`) creates them in
  Canvas **idempotently by matching objects by name** — assignment groups, a wiki
  front page, all assignments, and modules. Plus `sync_contract.py`, a
  bidirectional due‑date/points/weights sync (a human‑editable
  `canvas_contract.json` is the durable intent; `--pull` reads Canvas→contract,
  `--apply` pushes contract→Canvas).
- **`.grading/`** — pulls *submissions* and pushes *grades + comments* (§8), via
  the same token model.

Auth is env‑based:

```
CANVAS_BASE_URL   https://canvas.<institution>.edu
CANVAS_API_TOKEN  a personal access token (Account → Settings → New Access Token)
CANVAS_COURSE_ID  the numeric id from .../courses/<ID>
```

### Design decisions worth copying

- **Idempotent, name‑matched creation** so you can re‑run the push safely.
- **Due dates are deliberately NOT set by the structure push** — you schedule
  them in Canvas (or via the contract) so re‑running the push never clobbers
  dates.
- **A `--dry-run` and `--only <key>`** to pilot one assignment before pushing all.
- Link‑header **pagination** and **rate‑limit backoff** on the API client.

### Why it worked

- **No LMS lock‑in, no plugin approval.** A personal token + REST calls need no
  institutional LTI setup. You control exactly what's pushed and when.
- **The manifest is the source of truth**, so the Canvas course, the website, and
  the theme all agree.

### Adapt + extend it

- Set your `manifest.json` (course, groups, assignments, modules), base URL,
  token, and course id; run `push_to_canvas.py --dry-run`, then for real.
- **Fragilities to respect (§13):** name‑matching means **renaming an assignment
  in Canvas creates a duplicate** on the next push — treat names as stable keys,
  or match on a stored Canvas id. The course id and any section overrides are
  hardcoded. It's all manual scripts (no CI) — which is *appropriate*, since
  pushing to a live gradebook should be deliberate.

---

## 10. Bonus: the perpetuity export (single‑file offline site)

For students to keep the whole course forever, a build script
(`scripts/build-standalone.mjs`) **fuses the entire `docs/` site into one
self‑contained HTML file**: each page is base64‑encoded into a `PAGES` map and
rendered into a chrome‑less shell via `srcdoc` iframes (so each page keeps its own
isolated `window` and the two playgrounds' globals can't collide). Local CSS/JS/
images are inlined; the third‑party WASM runtimes stay as absolute CDN URLs so the
file survives the course site going offline but still streams WebR/Pyodide on
demand. A runtime prelude shims `fetch`/`XHR` to serve bundled CSVs, rewrites
in‑file navigation, swaps YouTube embeds for click‑to‑open facades (embeds refuse
to play from `file://`), and forces WebR's PostMessage channel (its default
channel hangs on `file://`). It's published as a **GitHub Release asset** (not
committed — it's ~10 MB and regenerated on every content change) by CI.

This is optional and advanced, but it's the logical endpoint of "static + WASM":
the course becomes a single file a student downloads and keeps.

---

## 11. Cross‑cutting design principles (the transferable wisdom)

Independent of subject, these are the decisions to carry forward:

1. **Static + WASM = no backend.** Push all computation to the browser. It's the
   cheapest, most durable, most secure architecture for a coding course.
2. **Single source of truth + generators.** Never hand‑maintain a derived
   artifact. But make the generators run in **CI**, and prefer a **structured
   manifest** over marker‑based text splicing (which silently no‑ops on drift).
3. **Convention over framework — with one include step.** Vanilla JS + CDN keeps
   everything portable and rot‑free; the *only* thing you must not hand‑duplicate
   is the nav/shell (add a tiny include or build step).
4. **Branch firewall for instructor/student.** Adopt it day one. Keep secrets and
   answer keys in non‑whitelisted dot‑dirs, never in `docs/`.
5. **Separate the tutor corpus from the answer‑key corpus.** The same content
   feeding a Socratic tutor and a grader is fine — but strip answers from the
   tutor bundle; don't rely on persona alone.
6. **Determinism everywhere.** Seed generators; reproducible datasets are
   testable datasets, and planted effects can be verified.
7. **Pin every CDN runtime** to a fixed version. `latest` will surprise you.
8. **Progressive enhancement.** Make the UI useful before the 30 MB runtime
   finishes (prefill editors, show content, boot lazily).
9. **Human‑in‑the‑loop AI.** Bots *draft*; instructors *approve*. Add
   deterministic guardrails wherever correctness is objective.
10. **Emit the code.** Any interactive tool should export a runnable script of
    what the student just did, and hand it to the playground.

---

## 12. A concrete build order (the playbook)

Given a starter codebase, build in this order — each phase is independently
useful and verifiable in a real headless browser before you move on.

| Phase | Do | Verify |
|---|---|---|
| **0. Host + firewall** | Put the site on GitHub Pages from a branch's `/docs`. Set up `instructor` (gold) + generated `main` (whitelist) branches. Theme tokens in one CSS file. | Pages serves; a push to `instructor` regenerates `main` with only whitelisted paths. |
| **1. Shell** | One page template with nav via an *include* (not copy‑paste). Design tokens wired. | Nav highlights the active page; theme consistent. |
| **2. First playground (Pyodide)** | Add `playground-py.html`: Pyodide boot, eager package install, CodeMirror, run + stdout + `plt.show` capture, editor persistence. Start with Python — it needs no COOP/COEP. | A real chunk runs and plots in the browser on the live Pages URL. |
| **3. Dataset SSOT** | `data/projects/<name>/` standard: one deterministic generator with a **planted story**, codebook README, loaders, thumbnail. Write the sync + menu scripts. | `_generate.py` byte‑reproduces; a check script confirms the planted effect; sync lands CSVs in `docs/playground-data/`. |
| **4. Wire data → playground** | `SAMPLE_CONFIGS` + `sampleSnippet` + stage‑to‑FS loading. | Pick a dataset → CSVs load → starter snippet runs. |
| **5. Second playground (WebR)** | Add `playground-r.html`. Mind the **channel gotcha** (leave `new WebR()` option‑less) and **verify your R packages exist as WASM builds**. Pin the WebR version. | R runs and plots on the live Pages URL (fallback channel). |
| **6. The interactive tool** | Build your subject's explore tool on the **registry + event bus + shared‑state + shared‑utils** skeleton. Add **code export + playground handoff**. | Manipulate → export teaching‑style code → "Open in playground" prefills the editor and the data loads. |
| **7. Learning checks** | In‑page MC checks (prefer computed answers) + teaching‑script LCs with the **printed‑sentinel parity contract**. Answer‑key builders + a **CI parity test**. | Both languages print the same LC line; key builders emit JSON. |
| **8. Study companion** | Bundle builders → one markdown file → NotebookLM notebook with an answer‑refusing persona. On‑site FAB. **Strip answers from the tutor bundle.** | The bot answers Socratically and refuses direct answers. |
| **9. Canvas + grading** | `.canvas/` manifest push (dry‑run first) + due‑date contract sync. `.grading/` rubric → LLM → Canvas comment, with deterministic guardrails and a mock mode. | A dry‑run push shows the right diff; a mock grading run produces a structured comment. |
| **10. Perpetuity + CI** | Single‑file standalone export as a Release; CI for subset, bundles, and export. | The Release file opens offline and the playgrounds still boot. |

---

## 13. Known fragilities — what to do differently in a fresh build

The reference implementation works well but carries debt from organic growth.
**Fix these from the start:**

1. **Nav duplicated across ~40 HTML files.** Add an include/build step for the
   nav/shell on day one.
2. **Dataset registry duplicated in ~4 places** (visualizer dropdown,
   `DATASET_MAPPINGS`, code‑export `SAMPLE_CONFIGS_LITE`, playground
   `SAMPLE_CONFIGS`). Define **one JSON dataset manifest** consumed by all.
3. **Marker‑based HTML splicing** (`<!-- PROJECT-DATASETS -->` + `re.sub`)
   **silently no‑ops** if the anchor drifts. Prefer generating whole pages/
   fragments from data, and **run generators in CI**, not by hand.
4. **WebR pinned to `latest`.** Pin it to a fixed release.
5. **Playground logic duplicated inline** in two 1500‑line HTML files. Extract a
   shared `playground-core-*.js` (also unlocks the many‑runnable‑chunks refactor,
   §3).
6. **Answer text leaks into the study‑bot bundle.** Author answers in separate
   key files; strip reveal text from the tutor corpus.
7. **No automated R/Python LC parity test.** Add one in CI.
8. **Instructor `docs/instructor/` pages are publicly reachable** (obscurity
   only). Never place real keys/secrets there; keep them in non‑whitelisted
   dot‑dirs.
9. **Canvas name‑matching creates duplicates on rename.** Store and match on
   Canvas object ids.
10. **Several manual re‑run steps** (dataset menus, LC key builders, NotebookLM
    re‑upload). Automate what you safely can in CI; keep genuinely deliberate
    actions (live gradebook pushes) manual on purpose.

---

## 14. Reusable engine vs. course‑specific content

| Subsystem | Reusable engine (carry over ~as‑is) | Course‑specific (re‑author) | Effort to adapt |
|---|---|---|---|
| Website shell | branch model, CI, design‑token CSS, `site.js` behavior | pages, nav items, branding | Low |
| Playgrounds | boot + install + editor + capture + FS‑staging + persistence + handoff patterns | package lists (verify WASM availability), starter snippets | **Low–Med** (R package availability is the risk) |
| Interactive tool | registry + event bus + shared‑state + shared‑utils + code‑export/handoff | the visualization + the analysis modules | Med–High |
| Datasets | folder standard, deterministic generator pattern, codebook format, sync scripts | every generator (planted stories), the inventory | **High** (designing good planted stories is the real work) |
| Learning checks | MC card mechanics, printed‑sentinel parity contract, key builders | the questions + answers | Low–Med |
| Study bot | bundle builders, CI refresh, on‑site FAB | the corpus, the persona, the notebook | Low |
| Grading bot | prompt template, Canvas client, anonymization, mock mode, deterministic override | `rubric.json`, assignment types | Med |
| Canvas | REST client, idempotent push, contract sync | `manifest.json`, course id, token | Low–Med |

---

## Appendix: reference file map

If you have access to the reference implementation, these are the files to read:

- **Site + branches:** `.github/workflows/publish-student-subset.yml` (WHITELIST +
  prune/restore), `docs/assets/{design.css,site.js,case-toc.js,notebooklm-bubble.js}`.
- **Playgrounds:** `docs/playground-r.html` (WebR boot ~L1100, install ~L1116,
  `captureR` ~L1181), `docs/playground-py.html` (Pyodide boot ~L1058, `loadPackage`
  ~L1066, `plt.show` monkey‑patch ~L1075), `docs/playground.html` (chooser).
- **Visualizer:** `docs/visualizer.html` + `docs/assets/viz2-core.js` (the
  `NetSciViz2` registry + event bus + `utils`), `docs/assets/viz2-codeexport.js`
  (code export + `openInPlayground` handoff ~L1965).
- **Datasets:** `.claude/skills/netsci-dataset-builder/SKILL.md` (the codified
  standard), `data/projects/amazon-last-mile/` (exemplar), `data/projects/
  _sync_to_playground.py`, `scripts/build_dataset_menus.py`.
- **Learning checks + bots:** `docs/case-studies/centrality.html` (LC cards +
  computed answers), `code/NN_*/example.{R,py}` (LC parity),
  `scripts/build_{notebooklm_source,coding_bundle,combined_bundle,skills_bundle}.py`,
  `.notebook/README.md`, `.grading/config/rubric.json`, `.grading/app/prompts.py`,
  `.grading/scripts/build_lc_{answer,code}_keys.py`.
- **Canvas:** `.canvas/manifest.json`, `.canvas/scripts/{push_to_canvas,
  sync_contract}.py`, `.grading/app/canvas_client.py`.
- **Perpetuity export:** `scripts/build-standalone.mjs`,
  `.github/workflows/publish-standalone.yml`.

---

*This playbook describes a platform, not a syllabus. The subject is
interchangeable; the architecture — static site, browser‑side WebAssembly, a
single source of truth with generators, an interactive tool that exports runnable
code, an answer‑refusing study bot, a rubric‑driven grader, and a thin Canvas API
layer — is what made the course feel like software instead of a PDF.*
