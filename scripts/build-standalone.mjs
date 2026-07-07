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
  'visualizer2.html',   // redirect stub
  'visualizer1.html',   // legacy visualizer
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
  // Route intra-site link clicks up to the shell for in-file navigation.
  document.addEventListener('click', function(e){
    var a = e.target && e.target.closest && e.target.closest('a[href]');
    if(!a) return;
    if(a.target === '_blank') return;
    var href = a.getAttribute('href') || '';
    if(!href || /^(https?:|mailto:|tel:|javascript:|data:|#)/i.test(href)) return;
    e.preventDefault();
    try { window.parent.postMessage({ __netsciNav: href }, '*'); } catch(_){}
  }, true);
})();
</script>`;

function transformPage(rel) {
  let html = readText(rel);
  const pageDir = path.posix.dirname(rel) === '.' ? '' : path.posix.dirname(rel);

  // 1) Inline local stylesheets:  <link rel="stylesheet" href="(../)*assets/x.css"[ media]>
  html = html.replace(/<link\b[^>]*\bhref="((?:\.\.\/)*assets\/[^"]+\.css)(?:\?[^"]*)?"[^>]*>/gi, (m, href) => {
    if (/print\.css/.test(href) && /media="print"/i.test(m)) return m; // leave print stylesheet inert
    const p = resolveAsset(href, pageDir);
    if (!exists(p)) return m;
    return `<style data-inlined="${p}">\n${readText(p)}\n</style>`;
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
