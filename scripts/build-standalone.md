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
the duplicate d3/CodeMirror loads stay separate. Deep links work via `#page.html`
in the URL hash.

A small prelude injected into each page makes everything connect offline:

- **Data**: shims `fetch()` *and* `XMLHttpRequest.open` (PapaParse's
  `{download:true}` uses XHR) to serve `playground-data/*` from the in-file
  manifest.
- **Links**: routes intra-site `<a href>` clicks up to the shell for in-file
  navigation — but leaves real downloads (`a[download]`, `blob:`/`data:` hrefs),
  `target="_blank"`, and external links alone so Export-PNG / Download-code / CSV
  export still work.
- **Programmatic nav**: overrides `window.open` so the code-export "Open in
  playground" handoff navigates in-file instead of 404-ing to the file's folder.
  The handoff payload is mirrored through the shell (not just `localStorage`,
  which is flaky on `file://`) so it survives the page swap.
- **Clear-cache buttons**: their `location.replace(url)` self-reload is rewritten
  at build time to re-render the current page (a single file has no HTTP cache).
- **YouTube**: `<iframe>` embeds refuse to play from a `file://` (null-origin)
  page, so each is swapped for a click-to-open facade (thumbnail → opens the
  video on youtube.com in a new tab).
- **WebR (R playground)**: `new WebR()` is rewritten to force the PostMessage
  channel. WebR's default channel needs cross-origin isolation or a service
  worker; neither exists on `file://`, so `webR.init()` would hang. (Pyodide is
  unaffected — it runs on the main thread.)

A dead-link scan (in the repo's build check) confirms every page-to-page link
resolves within the bundle.

## Requirements & caveats

- **Needs internet on first use of each interactive tool.** The playgrounds and
  visualizer stream their WASM runtimes/libraries from the CDNs above. The file is
  independent of *our* server, not of the public internet.
- Runs from a plain `file://` double-click — verified end-to-end (Pyodide +
  networkx boot, visualizer renders) in headless Chromium. The R playground uses
  the same mechanism; confirm once on a real machine.
- A single HTML file is inherently readable/copyable; the header carries a
  copyright + personal-use notice, which is a deterrent, not technical DRM.

## YouTube thumbnails

The build fetches each case-study video's thumbnail from `i.ytimg.com` and inlines
it as a data URI (cached under `scripts/.cache/yt-thumbs/`, gitignored). If the
build machine can't reach YouTube, the facade falls back to the remote thumbnail
URL — so **run the build somewhere with open internet** (e.g. the GitHub Action
below) to get a fully self-contained file.

## Distribution — GitHub Release, not the repo

The built file is ~9–10 MB and is regenerated on every content change, so it is
**not committed** (it's in `.gitignore`). It ships as a **GitHub Release asset**
via `.github/workflows/publish-standalone.yml`:

- Actions tab → **Publish standalone app** → *Run workflow* → updates the
  `standalone-latest` release, or
- push a tag `standalone-v<n>` → creates a versioned release.

The Action runs on a GitHub runner (open internet), so it inlines the YouTube
thumbnails that a restricted local build can't. Download link:
`https://github.com/timothyfraser/netsci/releases/latest/download/netsci-standalone.html`
