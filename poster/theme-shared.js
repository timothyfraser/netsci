// Shared poster-only theming used by the capture scripts.
const BIG_TEXT = `
  :root {
    --fs-xs:15px !important; --fs-sm:17px !important; --fs-base:20px !important;
    --fs-md:22px !important; --fs-lg:26px !important; --fs-xl:33px !important; --fs-2xl:46px !important;
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
      --black:#7C1010 !important; --black-2:#6B0E0E !important;
      --white:#FFFFFF !important; --grey:#F0DCDC !important; --grey-dim:#D9B8B8 !important;
      --green-mint:#FBEDED !important; --green-mint-2:#F0D9A8 !important;
      --green-bright:#F7C948 !important; --green-mid:#F0B323 !important;
      --green-dark:#4E0A0A !important; --green-deeper:#5C0C0C !important; --green-laser:#FFFFFF !important;
      --card-bg: rgba(255,255,255,0.10) !important; --card-bg-2: rgba(255,255,255,0.06) !important;
      --border: rgba(255,255,255,0.38) !important; --border-strong: rgba(247,201,72,0.85) !important;
      --border-soft: rgba(255,255,255,0.18) !important;
      --accent:#F7C948 !important; --accent-soft:#FFFFFF !important; --link:#F7C948 !important;
      --success:#F0B323 !important; --warning:#F7C948 !important; --danger:#FFD9D9 !important;
      --node-1:#FFE9A8 !important; --node-2:#F7C948 !important; --node-3:#FFFFFF !important;
      --node-4:#F7C948 !important; --node-5:#FFC9C9 !important; --node-6:#E0C0C0 !important;
      --node-7:#4E0A0A !important; --node-8:#D9D9D9 !important;
      --edge: rgba(255,255,255,0.50) !important; --edge-dim: rgba(255,255,255,0.26) !important;
      --edge-strong: rgba(247,201,72,0.95) !important;
    }
    body, #main { background:#7C1010 !important; }
    #network-svg, #graph-stage, .graph-stage-wrap { background:#6B0E0E !important; }
    .lab-card, .pg-card, .viz-card, .card { background:rgba(255,255,255,0.07) !important; }
    .CodeMirror, .CodeMirror-gutters { background:#5C0C0C !important; color:#FFFFFF !important; }
    .CodeMirror-linenumber { color:#D9B8B8 !important; }
    .cm-comment { color:#E8C0C0 !important; } .cm-string { color:#F7C948 !important; }
    .cm-keyword, .cm-builtin { color:#FFD98A !important; font-weight:700; }
    .cm-number, .cm-atom { color:#FFE9A8 !important; }
    .cm-variable, .cm-property, .cm-operator, .cm-def { color:#FFFFFF !important; }
  `,
  orig: '',
};

const MAP_LIGHT = { '#39ff14': '#9A9A9A', '#86efac': '#C9A227', '#5eead4': '#E4A11B', '#fbbf24': '#B31B1B',
                    '#f472b6': '#7C1010', '#818cf8': '#5A5A5A', '#f97316': '#6E0F0F', '#e2e8f0': '#BDBDBD',
                    '#22c55e': '#8C1515', '#166534': '#6E0F0F', '#d1fae5': '#3C3C3C', '#a3b8a3': '#585858' };
const MAP_RED   = { '#39ff14': '#FFE9A8', '#86efac': '#F0D9A8', '#5eead4': '#FFFFFF', '#fbbf24': '#F7C948',
                    '#f472b6': '#FFC9C9', '#818cf8': '#E0C0C0', '#f97316': '#4E0A0A', '#e2e8f0': '#D9D9D9',
                    '#22c55e': '#F0B323', '#166534': '#4E0A0A', '#d1fae5': '#FBEDED', '#a3b8a3': '#F0DCDC' };

// Idempotent: maps the course palette onto the poster palette wherever it appears.
const PAINT = `(args) => {
  const { map, light } = args;
  const edge = light ? '90,90,90' : '255,255,255';
  document.querySelectorAll('svg *').forEach((el) => {
    ['fill', 'stroke'].forEach((attr) => {
      const v = el.getAttribute(attr);
      if (!v) return;
      const k = v.trim().toLowerCase();
      if (map[k]) { el.setAttribute(attr, map[k]); return; }
      const g = /^rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)(?:,\\s*([\\d.]+))?\\)$/.exec(k);
      if (g) {
        const [r, gr, b] = [+g[1], +g[2], +g[3]];
        const a = g[4] === undefined ? 1 : +g[4];
        if (gr > r && gr > b && gr > 40) el.setAttribute(attr, 'rgba(' + edge + ',' + a + ')');
      }
      if (light && el.tagName.toLowerCase() === 'text') {
        const m = /^#([0-9a-f]{6})$/i.exec(el.getAttribute(attr) || '');
        if (m) {
          const n = parseInt(m[1], 16);
          const L = (0.2126*((n>>16)&255) + 0.7152*((n>>8)&255) + 0.0722*(n&255)) / 255;
          if (L > 0.7) el.setAttribute(attr, '#1A1A1A');
        }
      }
    });
  });
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
  if (theme !== 'orig') {
    await page.addStyleTag({ content: paletteCss(theme === 'red' ? MAP_RED : MAP_LIGHT) });
  }
  await page.waitForTimeout(600);
}
async function paint(page, theme) {
  if (theme === 'orig') return;
  await page.evaluate(new Function('return ' + PAINT)(),
    { map: theme === 'red' ? MAP_RED : MAP_LIGHT, light: theme !== 'red' });
  await page.waitForTimeout(300);
}
module.exports = { BIG_TEXT, THEME_CSS, MAP_LIGHT, MAP_RED, PAINT, paletteCss, dress, paint };
