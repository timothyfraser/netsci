#!/usr/bin/env node
// build-standalone.mjs — fuse the whole docs/ site into ONE self-contained HTML file.
//
// The output (docs/netsci-standalone.html) is a single file a student can keep on
// their own computer forever. It inlines everything WE host (page HTML, CSS, the
// viz JS modules, dataset CSVs, thumbnails) and keeps the third-party WASM/JS
// runtimes (WebR, Pyodide, CodeMirror, d3, papaparse, driver.js, Google Fonts) as
// absolute https:// URLs — so the file survives our own website going dark while
// still connecting to those independent CDNs.
//
// Architecture: a chrome-less shell hosts one <iframe>. Each original page becomes
// an isolated srcdoc document (so the two playgrounds' globals and the duplicate
// d3/CodeMirror loads can't collide). A tiny prelude injected into every page
// (1) shims fetch() to serve playground-data/*.csv from an in-file manifest, and
// (2) intercepts intra-site link clicks and routes them to the shell for in-file
// navigation. Nothing is fetched from our origin at runtime.
//
// Run:  node scripts/build-standalone.mjs
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DOCS = path.join(ROOT, 'docs');
const OUT  = path.join(DOCS, 'netsci-standalone.html');

// Pages we DON'T fold in: instructor-only, redirect stubs, legacy, and the output itself.
const EXCLUDE = new Set([
  'netsci-standalone.html',
  'visualizer2.html',   // redirect stub (its meta-refresh/JS points at visualizer.html)
  // NOTE: visualizer1.html IS included — the current Visualizer's "V1" pill links
  // to it, so leaving it out would be a dead link in the offline copy.
]);
const EXCLUDE_DIRS = new Set(['instructor']);

const MIME = {
  '.csv': 'text/csv', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
  '.gif': 'image/gif', '.svg': 'image/svg+xml', '.webp': 'image/webp', '.json': 'application/json',
  '.geojson': 'application/geo+json', '.txt': 'text/plain',
};
const mimeOf = (p) => MIME[path.extname(p).toLowerCase()] || 'application/octet-stream';

// ── discover pages ──────────────────────────────────────────────────────────
function walkHtml(dir, base = '') {
  const out = [];
  for (const name of fs.readdirSync(dir).sort()) {
    const full = path.join(dir, name);
    const rel = base ? base + '/' + name : name;
    const st = fs.statSync(full);
    if (st.isDirectory()) {
      if (EXCLUDE_DIRS.has(name)) continue;
      out.push(...walkHtml(full, rel));
    } else if (name.endsWith('.html') && !EXCLUDE.has(rel)) {
      out.push(rel);
    }
  }
  return out;
}
const pages = walkHtml(DOCS);

// ── helpers ─────────────────────────────────────────────────────────────────
const readText = (rel) => fs.readFileSync(path.join(DOCS, rel), 'utf8');
const b64File  = (rel) => fs.readFileSync(path.join(DOCS, rel)).toString('base64');
const b64Str   = (s)   => Buffer.from(s, 'utf8').toString('base64');
const exists   = (rel) => fs.existsSync(path.join(DOCS, rel));

// Resolve an asset reference that may be prefixed with any number of "../" and
// live relative to a page's directory, to a docs-relative path.
function resolveAsset(ref, pageDir) {
  const clean = ref.replace(/[?#].*$/, '');           // strip ?v=… / #frag
  const abs = path.posix.normalize(path.posix.join(pageDir || '.', clean));
  return abs.replace(/^\.\//, '');
}

// ── YouTube thumbnails: fetch + inline (best-effort, cached) ─────────────────
// Populated before the pages are assembled. If a thumbnail can't be fetched
// (offline build / blocked host), the facade falls back to the remote URL.
const ytThumb = {};
const YT_CACHE = path.join(ROOT, 'scripts', '.cache', 'yt-thumbs');
async function loadYtThumb(id) {
  const f = path.join(YT_CACHE, id + '.jpg');
  try { const b = fs.readFileSync(f); if (b.length > 1000) return 'data:image/jpeg;base64,' + b.toString('base64'); } catch {}
  for (const q of ['hqdefault', 'mqdefault']) {
    try {
      const r = await fetch(`https://i.ytimg.com/vi/${id}/${q}.jpg`);
      if (r.ok) {
        const b = Buffer.from(await r.arrayBuffer());
        if (b.length > 1000) { fs.mkdirSync(YT_CACHE, { recursive: true }); fs.writeFileSync(f, b); return 'data:image/jpeg;base64,' + b.toString('base64'); }
      }
    } catch {}
  }
  return null;
}

// ── per-page transform ───────────────────────────────────────────────────────
const RUNTIME_PRELUDE = `<script>
(function(){
  // Serve inlined data files (playground-data/*.csv) from the shell's manifest,
  // pass everything https:// straight through to the real network.
  try {
    var MAN = (window.parent && window.parent.__NETSCI_ASSETS__) || {};
    var b2u = function(b){ var s=atob(b), u=new Uint8Array(s.length); for(var i=0;i<s.length;i++) u[i]=s.charCodeAt(i); return u; };
    var orig = window.fetch ? window.fetch.bind(window) : null;
    window.fetch = function(input, init){
      var url = (typeof input === 'string') ? input : (input && input.url) || '';
      var m = String(url).match(/playground-data\\/([^\\/?#]+)/);
      if (m && MAN[m[1]]) {
        var a = MAN[m[1]];
        return Promise.resolve(new Response(new Blob([b2u(a.b)], {type:a.t}), {status:200, headers:{'Content-Type':a.t}}));
      }
      if (orig) return orig(input, init);
      return Promise.reject(new Error('offline: '+url));
    };
    // PapaParse's {download:true} and any other XHR bypass fetch. Rewrite a
    // playground-data/* request to a data: URL from the manifest BEFORE the real
    // open(), so the native XHR loads it straight from the in-file bundle.
    if (window.XMLHttpRequest) {
      var op = XMLHttpRequest.prototype.open;
      XMLHttpRequest.prototype.open = function(method, url){
        try {
          var mm = String(url).match(/playground-data\\/([^\\/?#]+)/);
          if (mm && MAN[mm[1]]) {
            var a2 = MAN[mm[1]];
            arguments[1] = 'data:' + a2.t + ';base64,' + a2.b;
          }
        } catch(_){}
        return op.apply(this, arguments);
      };
    }
  } catch(e){}

  var isExternal = function(u){ return /^(https?:|mailto:|tel:|javascript:|data:|blob:|about:|#)/i.test(u); };
  var navTo = function(u){ try { window.parent.postMessage({ __netsciNav: u }, '*'); } catch(_){} };

  // Route intra-site link clicks up to the shell for in-file navigation.
  // Leave real downloads (a[download], blob:/data: hrefs) and external/new-tab
  // links alone so Export-PNG / Download-code / CSV export still work.
  document.addEventListener('click', function(e){
    var a = e.target && e.target.closest && e.target.closest('a[href]');
    if(!a) return;
    if(a.target === '_blank' || a.hasAttribute('download')) return;
    var href = a.getAttribute('href') || '';
    if(!href || isExternal(href)) return;
    e.preventDefault();
    navTo(href);
  }, true);

  // Programmatic navigation to another page (e.g. the code-export "Open in
  // playground" handoff uses window.open) resolves relative URLs against the
  // downloaded file's folder and 404s. Route same-site .html targets in-file.
  // The handoff payload is already in localStorage (shared across pages, same
  // origin), so the destination page picks it up on load.
  try {
    var origOpen = window.open ? window.open.bind(window) : null;
    window.open = function(url, name, feat){
      var u = String(url == null ? '' : url);
      if (u && !isExternal(u)) { navTo(u); return null; }
      return origOpen ? origOpen(url, name, feat) : null;
    };
  } catch(_){}

  // The visualizer -> playground handoff passes code via localStorage, which is
  // flaky (or absent) on file:// across browsers. Mirror just that one key
  // through the shell so it survives the page swap no matter what — and never
  // let it throw, so the handoff always proceeds to navigate.
  try {
    var HK = 'netsci-playground-handoff', P = window.parent, SP = Storage.prototype;
    var _set = SP.setItem, _get = SP.getItem, _del = SP.removeItem;
    SP.setItem = function(k, v){
      if (k === HK) { try { P.__NETSCI_HANDOFF__ = v; } catch(_){}
        try { return _set.apply(this, arguments); } catch(_){ return; } }
      return _set.apply(this, arguments);
    };
    SP.getItem = function(k){
      var r = null; try { r = _get.apply(this, arguments); } catch(_){}
      if (k === HK && r == null) { try { return P.__NETSCI_HANDOFF__ != null ? P.__NETSCI_HANDOFF__ : null; } catch(_){} }
      return r;
    };
    SP.removeItem = function(k){
      if (k === HK) { try { P.__NETSCI_HANDOFF__ = null; } catch(_){} }
      try { return _del.apply(this, arguments); } catch(_){ return; }
    };
  } catch(_){}

  // A single file has no separate HTTP cache to bust, so the clear-cache
  // buttons' self-reload (rewritten at build time to call this) just re-renders
  // the current page after storage was cleared.
  window.__netsciReload = function(){ try { window.parent.postMessage({ __netsciReload: true }, '*'); } catch(_){} };
})();
</script>`;

function transformPage(rel) {
  let html = readText(rel);
  const pageDir = path.posix.dirname(rel) === '.' ? '' : path.posix.dirname(rel);

  // 1) Inline local stylesheets:  <link rel="stylesheet" href="(../)*assets/x.css"[ media]>
  //    Preserve a media="print" link as <style media="print"> so the file stays
  //    fully self-contained (no request to our origin for print.css).
  html = html.replace(/<link\b[^>]*\bhref="((?:\.\.\/)*assets\/[^"]+\.css)(?:\?[^"]*)?"[^>]*>/gi, (m, href) => {
    const p = resolveAsset(href, pageDir);
    if (!exists(p)) return m;
    const mediaAttr = /media="print"/i.test(m) ? ' media="print"' : '';
    return `<style data-inlined="${p}"${mediaAttr}>\n${readText(p)}\n</style>`;
  });

  // 2) Inline local scripts:  <script src="(../)*assets/x.js"[ defer]></script>
  html = html.replace(/<script\b([^>]*)\bsrc="((?:\.\.\/)*assets\/[^"]+\.js)(?:\?[^"]*)?"([^>]*)><\/script>/gi, (m, pre, src, post) => {
    const p = resolveAsset(src, pageDir);
    if (!exists(p)) return m;
    return `<script data-inlined="${p}">\n${readText(p)}\n</script>`;
  });

  // 3) Inline local images referenced by src="(../)*(images|playground-data)/x.(png|jpg…)"
  html = html.replace(/\bsrc="((?:\.\.\/)*(?:images|playground-data)\/[^"]+\.(?:png|jpe?g|gif|webp|svg))(?:\?[^"]*)?"/gi, (m, ref) => {
    const p = resolveAsset(ref, pageDir);
    if (!exists(p)) return m;
    return `src="data:${mimeOf(p)};base64,${b64File(p)}"`;
  });

  // 4) Drop any link into the instructor area — it isn't in this copy, and the
  //    offline file shouldn't advertise back-of-house tooling.
  html = html.replace(/<a\b[^>]*\bhref="(?:\.\.\/)*instructor\/[^"]*"[^>]*>.*?<\/a>/gis, '');

  // 4b) The clear-cache buttons self-reload via location.replace(url) with a
  //     cache-bust query — meaningless (and blanks the iframe) in a single file.
  //     Route it through the shell to re-render the current page instead.
  html = html.replace(/location\.replace\(url\.toString\(\)\)/g, 'window.__netsciReload()');

  // 4c) YouTube <iframe> embeds refuse to play from a file:// (null-origin) page,
  //     so they break in a downloaded copy. Swap each for a click-to-open facade:
  //     the video thumbnail linking to youtube.com (opens in a new tab). Fills the
  //     same 16:9 .ratio box (absolute inset:0, matching the original iframe CSS).
  html = html.replace(
    /<iframe\b[^>]*\bsrc="https:\/\/www\.youtube(?:-nocookie)?\.com\/embed\/([A-Za-z0-9_-]+)[^"]*"[^>]*><\/iframe>/gis,
    (m, id) =>
      `<a href="https://www.youtube.com/watch?v=${id}" target="_blank" rel="noopener"` +
      ` title="Watch on YouTube (opens youtube.com)"` +
      ` style="position:absolute;inset:0;width:100%;height:100%;display:flex;align-items:center;justify-content:center;` +
      `text-decoration:none;background:#000 center/cover no-repeat url('${ytThumb[id] || `https://i.ytimg.com/vi/${id}/hqdefault.jpg`}');">` +
      `<span aria-hidden="true" style="width:72px;height:50px;border-radius:14px;background:rgba(200,0,0,0.88);` +
      `display:flex;align-items:center;justify-content:center;color:#fff;font:700 26px/1 sans-serif;">&#9654;</span>` +
      `<span style="position:absolute;bottom:8px;right:10px;color:#fff;font:600 12px/1 sans-serif;` +
      `background:rgba(0,0,0,0.6);padding:4px 7px;border-radius:5px;">▶ Watch on YouTube</span></a>`
  );

  // 4d) WebR's default channel needs cross-origin isolation or a service worker,
  //     and neither is available from a file:// page — so webR.init() hangs. Force
  //     the PostMessage channel (no special headers / no service worker required).
  html = html.replace(
    /import\s*\{\s*WebR\s*\}\s*from\s*(['"])(https:\/\/webr\.r-wasm\.org\/[^'"]+)\1/,
    'import { WebR, ChannelType } from $1$2$1'
  );
  html = html.replace(/\bnew WebR\(\)/g, 'new WebR({ channelType: ChannelType.PostMessage })');

  // 5) Inject the runtime prelude as the first thing inside <head>.
  html = html.replace(/<head([^>]*)>/i, (m) => `${m}\n${RUNTIME_PRELUDE}`);

  return html;
}

// ── build the CSV/data manifest (fetched at runtime by the playgrounds) ──────
const manifest = {};
const dataDir = path.join(DOCS, 'playground-data');
for (const name of fs.readdirSync(dataDir)) {
  if (!name.endsWith('.csv')) continue;           // thumbnails are inlined per-page as data URIs
  manifest[name] = { t: mimeOf(name), b: b64File('playground-data/' + name) };
}

// ── assemble PAGES map (each transformed page, base64'd to dodge all escaping) ─
// Prefetch every unique YouTube thumbnail before assembling the pages.
const ytIds = new Set();
for (const rel of pages) { const s = readText(rel); let mm; const re = /youtube(?:-nocookie)?\.com\/embed\/([A-Za-z0-9_-]+)/g; while ((mm = re.exec(s))) ytIds.add(mm[1]); }
for (const id of ytIds) ytThumb[id] = await loadYtThumb(id);
const nThumb = Object.values(ytThumb).filter(Boolean).length;
console.log(`  youtube thumbnails inlined: ${nThumb}/${ytIds.size}` + (nThumb < ytIds.size ? ' (rest fall back to remote i.ytimg.com — build machine had no reach)' : ''));

const PAGES = {};
for (const rel of pages) PAGES[rel] = b64Str(transformPage(rel));

const START = pages.includes('index.html') ? 'index.html' : pages[0];

// ── shell ─────────────────────────────────────────────────────────────────────
const YEAR = 2026;
const shell = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>SYSEN 5470 · Network Science — Offline Copy</title>
<style>
  html,body{margin:0;padding:0;height:100%;background:#050a05;}
  #frame{position:fixed;inset:0;width:100%;height:100%;border:0;display:block;}
  #boot{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;
    color:#7CFF6B;font-family:ui-monospace,Menlo,Consolas,monospace;font-size:14px;background:#050a05;z-index:2;}
</style>
</head>
<body>
<div id="boot">Loading offline copy…</div>
<iframe id="frame" title="SYSEN 5470"></iframe>
<script>
/* ============================================================================
   SYSEN 5470 — Network Science for Systems Engineering
   Offline single-file copy. © ${YEAR} Timothy Fraser. All rights reserved.
   Provided for personal educational use. Not for redistribution, resale, or
   modification. The interactive playgrounds and visualizer connect to
   third-party runtimes (WebR, Pyodide) and libraries over the public internet.
   ============================================================================ */
(function(){
  "use strict";
  var PAGES = __PAGES__;
  window.__NETSCI_ASSETS__ = __ASSETS__;
  var START = ${JSON.stringify(START)};
  var frame = document.getElementById('frame');
  var boot  = document.getElementById('boot');

  function b64ToStr(b){
    var s = atob(b), u = new Uint8Array(s.length);
    for (var i=0;i<s.length;i++) u[i]=s.charCodeAt(i);
    return new TextDecoder('utf-8').decode(u);
  }
  // Resolve an href (possibly ../ relative) from the current page to a PAGES key.
  function resolveKey(fromKey, href){
    href = href.replace(/[#?].*$/, '');
    var baseDir = fromKey.indexOf('/') >= 0 ? fromKey.replace(/\\/[^/]*$/, '') : '';
    var parts = (baseDir ? baseDir.split('/') : []);
    href.split('/').forEach(function(seg){
      if (seg === '' || seg === '.') return;
      if (seg === '..') parts.pop(); else parts.push(seg);
    });
    return parts.join('/');
  }
  var current = START;
  function show(key, hash){
    if (!PAGES[key]) { return false; }
    current = key;
    frame.setAttribute('srcdoc', b64ToStr(PAGES[key]));
    if (boot) { boot.style.display='none'; }
    // reflect location for back/forward + bookmarking within the file
    var newHash = '#' + key + (hash ? hash : '');
    if (location.hash !== newHash) { try { history.pushState({key:key}, '', newHash); } catch(_){ location.hash = key; } }
    return true;
  }
  window.addEventListener('message', function(e){
    var d = e.data;
    if (d && d.__netsciNav) {
      var key = resolveKey(current, d.__netsciNav);
      var frag = (d.__netsciNav.match(/#.*$/) || [''])[0];
      if (!show(key, frag)) { console.warn('[offline] not in this copy:', d.__netsciNav); }
    } else if (d && d.__netsciReload) {
      // re-render the current page from scratch (clear-cache buttons)
      frame.setAttribute('srcdoc', b64ToStr(PAGES[current]));
    }
  });
  function fromHash(){
    var h = location.hash.replace(/^#/, '');
    var key = h.split('#')[0] || START;
    if (PAGES[key] && key !== current) { current = key; frame.setAttribute('srcdoc', b64ToStr(PAGES[key])); if(boot) boot.style.display='none'; }
  }
  window.addEventListener('popstate', fromHash);
  window.addEventListener('hashchange', fromHash);
  // initial page from hash (bookmark) or default
  var initKey = (location.hash.replace(/^#/, '').split('#')[0]) || START;
  if (!PAGES[initKey]) initKey = START;
  show(initKey);
})();
</script>
</body>
</html>`;

// Inject the big literals without template-literal escaping headaches.
const finalHtml = shell
  .replace('__PAGES__', () => JSON.stringify(PAGES))
  .replace('__ASSETS__', () => JSON.stringify(manifest));

fs.writeFileSync(OUT, finalHtml);
const mb = (fs.statSync(OUT).size / (1024 * 1024)).toFixed(1);
console.log(`Wrote ${path.relative(ROOT, OUT)}  (${mb} MB)`);
console.log(`  pages: ${pages.length}   data files: ${Object.keys(manifest).length}   start: ${START}`);
