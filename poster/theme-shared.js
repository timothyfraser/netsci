// Shared poster-only theming used by the capture scripts.
const BIG_TEXT = `
  :root {
    --fs-xs:15px !important; --fs-sm:17px !important; --fs-base:20px !important;
    --fs-md:22px !important; --fs-lg:26px !important; --fs-xl:33px !important; --fs-2xl:46px !important;
  }
  #network-svg *, #graph-stage *, .lab-card *, .viz-card *, .pg-card * {
    filter:none !important; text-shadow:none !important;
  }
  #network-svg text { font-size:16px !important; font-weight:700 !important; }
  #graph-stage text { font-size:19px !important; font-weight:700 !important; }
  .CodeMirror { font-size:17px !important; line-height:1.45 !important; }
  [id*="notebook" i],[class*="notebook" i],[id*="fab" i],[class*="fab" i],
  [class*="bubble" i],[id*="bubble" i] { display:none !important; }
`;

const LIGHT = (bg, panel) => `
  :root {
    --black:${bg} !important; --black-2:${panel} !important;
    --white:#1A1A1A !important; --grey:#585858 !important; --grey-dim:#8A8A8A !important;
    --green-mint:#3C3C3C !important; --green-mint-2:#6B6B6B !important;
    --green-bright:#B31B1B !important; --green-mid:#8C1515 !important;
    --green-dark:#E4A11B !important; --green-deeper:#F3E7E7 !important; --green-laser:#E4A11B !important;
    --card-bg: rgba(179,27,27,0.045) !important; --card-bg-2: rgba(0,0,0,0.02) !important;
    --border: rgba(179,27,27,0.30) !important; --border-strong: rgba(179,27,27,0.62) !important;
    --border-soft: rgba(179,27,27,0.13) !important;
    --accent:#B31B1B !important; --accent-soft:#8C1515 !important; --link:#B31B1B !important;
    --success:#8C1515 !important; --warning:#B8860B !important; --danger:#B31B1B !important;
    --node-1:#9A9A9A !important; --node-2:#B31B1B !important; --node-3:#E4A11B !important;
    --node-4:#B31B1B !important; --node-5:#7C1010 !important; --node-6:#5A5A5A !important;
    --node-7:#6E0F0F !important; --node-8:#BDBDBD !important;
    --edge: rgba(90,90,90,0.55) !important; --edge-dim: rgba(90,90,90,0.28) !important;
    --edge-strong: rgba(179,27,27,0.90) !important;
  }
  body, #main { background:${bg} !important; }
  #network-svg, #graph-stage, .graph-stage-wrap { background:${bg} !important; }
  .lab-card, .pg-card, .viz-card, .card { background:${panel} !important; }
  .CodeMirror, .CodeMirror-gutters { background:${panel} !important; color:#1A1A1A !important; }
  .CodeMirror-linenumber { color:#9A9A9A !important; }
  .cm-comment { color:#7A7A7A !important; } .cm-string { color:#8C1515 !important; }
  .cm-keyword, .cm-builtin { color:#B31B1B !important; font-weight:700; }
  .cm-number, .cm-atom { color:#8A6A00 !important; }
  .cm-variable, .cm-property, .cm-operator, .cm-def { color:#1A1A1A !important; }
  .CodeMirror-cursor { border-left-color:#1A1A1A !important; }
`;

const THEME_CSS = {
  white: LIGHT('#FFFFFF', '#F6F2F2'),
  grey: LIGHT('#EBEBEB', '#E2E2E2'),
  red: `
    :root {
      --black:#C32529 !important; --black-2:#B02327 !important;
      --white:#FFFFFF !important; --grey:#FFE2E2 !important; --grey-dim:#F3C3C3 !important;
      --green-mint:#FFF1F1 !important; --green-mint-2:#FFE9A8 !important;
      --green-bright:#F7C948 !important; --green-mid:#FFD98A !important;
      --green-dark:#8C1515 !important; --green-deeper:#A81E22 !important; --green-laser:#FFFFFF !important;
      --card-bg: rgba(255,255,255,0.16) !important; --card-bg-2: rgba(255,255,255,0.10) !important;
      --border: rgba(255,255,255,0.48) !important; --border-strong: rgba(247,201,72,0.90) !important;
      --border-soft: rgba(255,255,255,0.22) !important;
      --accent:#F7C948 !important; --accent-soft:#FFFFFF !important; --link:#F7C948 !important;
      --success:#FFD98A !important; --warning:#F7C948 !important; --danger:#FFE0E0 !important;
      --node-1:#F7C948 !important; --node-2:#FFFFFF !important; --node-3:#FFD6D6 !important;
      --node-4:#FF9E9E !important; --node-5:#E8575A !important; --node-6:#E8E8E8 !important;
      --node-7:#8C1515 !important; --node-8:#FFD24A !important;
      --edge: rgba(255,255,255,0.62) !important; --edge-dim: rgba(255,255,255,0.34) !important;
      --edge-strong: rgba(247,201,72,0.95) !important;
    }
    body, #main { background:#C32529 !important; }
    #network-svg, #graph-stage, .graph-stage-wrap { background:#B72A2E !important; }
    .lab-card, .pg-card, .viz-card, .card { background:rgba(255,255,255,0.13) !important; }
    .CodeMirror, .CodeMirror-gutters { background:#A81E22 !important; color:#FFFFFF !important; }
    .CodeMirror-linenumber { color:#F3C3C3 !important; }
    .cm-comment { color:#FFD9D9 !important; } .cm-string { color:#F7C948 !important; }
    .cm-keyword, .cm-builtin { color:#FFE9A8 !important; font-weight:700; }
    .cm-number, .cm-atom { color:#FFD24A !important; }
    .cm-variable, .cm-property, .cm-operator, .cm-def { color:#FFFFFF !important; }
  `,
  redlight: LIGHT('#F9E9E9', '#F2DBDB'),
  reddark: `
    :root {
      --black:#7A1216 !important; --black-2:#6A1013 !important;
      --white:#FFFFFF !important; --grey:#F0D8D8 !important; --grey-dim:#D9B0B0 !important;
      --green-mint:#FBEDED !important; --green-mint-2:#FFE9A8 !important;
      --green-bright:#F7C948 !important; --green-mid:#FFD98A !important;
      --green-dark:#4E0A0A !important; --green-deeper:#5C0C0C !important; --green-laser:#FFFFFF !important;
      --card-bg: rgba(255,255,255,0.14) !important; --card-bg-2: rgba(255,255,255,0.08) !important;
      --border: rgba(255,255,255,0.45) !important; --border-strong: rgba(247,201,72,0.90) !important;
      --border-soft: rgba(255,255,255,0.20) !important;
      --accent:#F7C948 !important; --accent-soft:#FFFFFF !important; --link:#F7C948 !important;
      --success:#FFD98A !important; --warning:#F7C948 !important; --danger:#FFE0E0 !important;
      --node-1:#F7C948 !important; --node-2:#FFFFFF !important; --node-3:#FFD6D6 !important;
      --node-4:#FF9E9E !important; --node-5:#E8575A !important; --node-6:#E8E8E8 !important;
      --node-7:#8C1515 !important; --node-8:#FFD24A !important;
      --edge: rgba(255,255,255,0.60) !important; --edge-dim: rgba(255,255,255,0.32) !important;
      --edge-strong: rgba(247,201,72,0.95) !important;
    }
    body, #main { background:#7A1216 !important; }
    #network-svg, #graph-stage, .graph-stage-wrap { background:#6E1114 !important; }
    .lab-card, .pg-card, .viz-card, .card { background:rgba(255,255,255,0.11) !important; }
    .CodeMirror, .CodeMirror-gutters { background:#5C0C0C !important; color:#FFFFFF !important; }
    .CodeMirror-linenumber { color:#D9B0B0 !important; }
    .cm-comment { color:#FFD9D9 !important; } .cm-string { color:#F7C948 !important; }
    .cm-keyword, .cm-builtin { color:#FFE9A8 !important; font-weight:700; }
    .cm-number, .cm-atom { color:#FFD24A !important; }
    .cm-variable, .cm-property, .cm-operator, .cm-def { color:#FFFFFF !important; }
  `,
  orig: '',
};

const MAP_LIGHT = { '#39ff14': '#9A9A9A', '#86efac': '#C9A227', '#5eead4': '#E4A11B', '#fbbf24': '#B31B1B',
                    '#f472b6': '#7C1010', '#818cf8': '#5A5A5A', '#f97316': '#6E0F0F', '#e2e8f0': '#BDBDBD',
                    '#22c55e': '#8C1515', '#166534': '#6E0F0F', '#d1fae5': '#3C3C3C', '#a3b8a3': '#585858' };
const MAP_RED   = { '#39ff14': '#F7C948', '#86efac': '#FFD6D6', '#5eead4': '#FFFFFF', '#fbbf24': '#FFD24A',
                    '#f472b6': '#FF9E9E', '#818cf8': '#E8E8E8', '#f97316': '#E8575A', '#e2e8f0': '#FFF1F1',
                    '#22c55e': '#FFD98A', '#166534': '#E8575A', '#d1fae5': '#FFF1F1', '#a3b8a3': '#FFE2E2' };

// Idempotent: maps the course palette onto the poster palette wherever it appears.
const PAINT = `(args) => {
  const { map, light, panel, accent, edgeRGB, murkMax } = args;
  const parse = (c) => {
    const m = /rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)(?:,\\s*([\\d.]+))?\\)/.exec(c || '');
    if (m) return { r: +m[1], g: +m[2], b: +m[3], a: m[4] === undefined ? 1 : +m[4] };
    const h = /^#([0-9a-f]{6})$/i.exec((c || '').trim());
    if (h) { const n = parseInt(h[1], 16); return { r: (n>>16)&255, g: (n>>8)&255, b: n&255, a: 1 }; }
    return null;
  };
  const isGreen = (o) => o && o.a > 0.02 && (
    (o.g > o.r + 8 && o.g > o.b + 8) ||                       // the course's dark panel green
    (o.g > o.b + 25 && o.g > o.r - 10 && o.g > 60));          // neon, lime, mint
  const lum = (o) => (0.2126 * o.r + 0.7152 * o.g + 0.0722 * o.b) / 255;

  document.querySelectorAll('svg *').forEach((el) => {
    ['fill', 'stroke'].forEach((attr) => {
      const v = el.getAttribute(attr);
      if (!v) return;
      const k = v.trim().toLowerCase();
      if (map[k]) { el.setAttribute(attr, map[k]); return; }
      const o = parse(k);
      if (isGreen(o)) el.setAttribute(attr, o.a < 1 ? 'rgba(' + edgeRGB + ',' + o.a + ')' : accent);
      if (light && el.tagName.toLowerCase() === 'text') {
        const c = parse(el.getAttribute(attr) || '');
        if (c && (0.2126*c.r + 0.7152*c.g + 0.0722*c.b) / 255 > 0.7) el.setAttribute(attr, '#1A1A1A');
      }
    });
  });

  // The site styles many chips with !important, so tag the offenders and win with a
  // stylesheet appended last rather than with inline styles.
  document.querySelectorAll('body *').forEach((el) => {
    const cs = getComputedStyle(el);
    const bg = parse(cs.backgroundColor);
    const r = el.getBoundingClientRect();
    const small = r.width > 0 && r.width < 240 && r.height < 150;  // a chip, button or badge
    const murky = bg && bg.a > 0.4 && lum(bg) < murkMax;
    if (isGreen(bg) || (small && murky)) el.setAttribute('data-pfix-bg', '1');
    if (isGreen(parse(cs.borderTopColor))) el.setAttribute('data-pfix-bd', '1');
    if (isGreen(parse(cs.color))) el.setAttribute('data-pfix-fg', '1');
  });
  const st = document.createElement('style');
  st.textContent =
    '[data-pfix-bg]{background-color:' + panel + ' !important;background-image:none !important}' +
    '[data-pfix-bd]{border-color:' + accent + ' !important}' +
    '[data-pfix-fg]{color:' + accent + ' !important}';
  document.head.appendChild(st);
}`;


// CSS wins over SVG presentation attributes, and survives any redraw loop the page runs.
function paletteCss(map) {
  return Object.entries(map).map(([from, to]) =>
    `[fill="${from}" i]{fill:${to} !important}[stroke="${from}" i]{stroke:${to} !important}`
  ).join('\n');
}

async function dress(page, theme) {
  await page.addStyleTag({ content: BIG_TEXT });
  if (THEME_CSS[theme]) await page.addStyleTag({ content: THEME_CSS[theme] });
  const pa = PAINT_ARGS[theme];
  if (pa) await page.addStyleTag({ content: paletteCss(pa.light ? MAP_LIGHT : MAP_RED) });
  await page.waitForTimeout(600);
}
const PAINT_ARGS = {
  white:    { panel: 'rgba(179,27,27,0.07)', accent: '#B31B1B', edgeRGB: '90,90,90',    murkMax: 0.45, light: true },
  grey:     { panel: 'rgba(179,27,27,0.08)', accent: '#B31B1B', edgeRGB: '90,90,90',    murkMax: 0.45, light: true },
  redlight: { panel: 'rgba(179,27,27,0.10)', accent: '#B31B1B', edgeRGB: '120,80,80',   murkMax: 0.45, light: true },
  red:      { panel: 'rgba(255,255,255,0.18)', accent: '#F7C948', edgeRGB: '255,255,255', murkMax: 0.20, light: false },
  reddark:  { panel: 'rgba(255,255,255,0.16)', accent: '#F7C948', edgeRGB: '255,255,255', murkMax: 0.20, light: false },
};

async function paint(page, theme) {
  const args = PAINT_ARGS[theme];
  if (!args) return;                       // 'orig' keeps the course's own palette
  await page.evaluate(new Function('return ' + PAINT)(),
    Object.assign({ map: args.light ? MAP_LIGHT : MAP_RED }, args));
  await page.waitForTimeout(300);
}
module.exports = { BIG_TEXT, THEME_CSS, MAP_LIGHT, MAP_RED, PAINT, PAINT_ARGS, paletteCss, dress, paint };
