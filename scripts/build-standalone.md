# Standalone single-file export

`build-standalone.mjs` fuses the entire `docs/` site into **one** self-contained
HTML file, `docs/netsci-standalone.html`, that a student can keep on their own
computer forever.

```bash
node scripts/build-standalone.mjs
```

## What it does

- Walks every page under `docs/` (skipping `instructor/`, the `visualizer2.html`
  redirect stub, and `visualizer1.html`) and folds each one into the single file.
- **Inlines everything we host**: page HTML, `assets/*.css`, `assets/*.js` (the
  `viz2-*` visualizer modules, `site.js`, etc.), dataset thumbnails, and every
  `playground-data/*.csv` (served at runtime from an in-file manifest).
- **Keeps third-party runtimes as absolute `https://` URLs** so the file survives
  our own site going offline: WebR (`webr.r-wasm.org`), Pyodide (`jsdelivr`),
  CodeMirror + d3 + papaparse + driver.js (`cdnjs`), and the Google Font.
- Strips links into the instructor area and drops the `banner*.png` social-preview
  images (they're `og:image` only, never shown).

## How it works

The output is a chrome-less shell hosting one `<iframe>`. Each page is stored
base64-encoded and rendered into the iframe via `srcdoc`, so every page gets its
own isolated `window` — the R and Python playgrounds can't collide on globals, and
the duplicate d3/CodeMirror loads stay separate. A small prelude injected into each
page (a) shims `fetch()` to serve `playground-data/*` from the manifest and (b)
routes intra-site link clicks up to the shell for in-file navigation. Deep links
work via `#page.html` in the URL hash.

## Requirements & caveats

- **Needs internet on first use of each interactive tool.** The playgrounds and
  visualizer stream their WASM runtimes/libraries from the CDNs above. The file is
  independent of *our* server, not of the public internet.
- Runs from a plain `file://` double-click — verified end-to-end (Pyodide +
  networkx boot, visualizer renders) in headless Chromium. The R playground uses
  the same mechanism; confirm once on a real machine.
- A single HTML file is inherently readable/copyable; the header carries a
  copyright + personal-use notice, which is a deterrent, not technical DRM.

## Distribution

The built file is ~9 MB. Options: commit it so it's downloadable from the site at
`/netsci-standalone.html`, or attach it to a GitHub Release / your LMS and keep it
out of git history. Re-run the build after any site change to refresh it.
