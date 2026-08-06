// Cornell Duffield 40x30 teaching poster — "Production-Quality Interactive Course Labs, Built with AI"
// Builds MTEI-teaching-poster.pptx on the official Duffield template background.
const pptxgen = require('pptxgenjs');
const path = require('path');

const A = (p) => path.join(__dirname, 'assets', p);
const SHOT = (p) => path.join(__dirname, 'shots', p);

// ---- palette (Cornell red on white; course green lives only inside screenshots) ----
const RED = 'B31B1B'; // Cornell carnelian
const DARK = '222222';
const GRAY = '555555';
const LIGHT_LINE = 'DDDDDD';
const WHITE = 'FFFFFF';

const pres = new pptxgen();
pres.defineLayout({ name: 'POSTER', width: 40, height: 30 });
pres.layout = 'POSTER';

const slide = pres.addSlide();

// Template background (red Cornell Duffield Engineering band + halftone texture)
slide.addImage({ path: A('background.png'), x: 0, y: 0, w: 40, h: 30 });

// ---------- helpers ----------
function panel(x, y, w, h) {
  slide.addShape('roundRect', {
    x, y, w, h,
    rectRadius: 0.12,
    fill: { color: WHITE },
    line: { color: LIGHT_LINE, width: 1.25 },
    shadow: { type: 'outer', angle: 90, blur: 10, color: '888888', offset: 3, opacity: 0.3 },
  });
}

function framedImage(imgPath, x, y, w, h) {
  const B = 0.045; // frame thickness
  slide.addShape('roundRect', {
    x: x - B, y: y - B, w: w + 2 * B, h: h + 2 * B,
    rectRadius: 0.06,
    fill: { color: '1A241A' },
    line: { color: '333333', width: 1 },
    shadow: { type: 'outer', angle: 90, blur: 12, color: '777777', offset: 4, opacity: 0.35 },
  });
  slide.addImage({ path: imgPath, x, y, w, h });
}

function sectionHeader(text, x, y, w, opts = {}) {
  slide.addText(text, {
    x, y, w, h: 0.62,
    fontFace: 'Arial', fontSize: 30, bold: true, color: RED,
    charSpacing: 2, margin: 0, align: opts.align || 'left',
  });
}

// ---------- title zone ----------
slide.addText('Production-Quality Interactive Course Labs, Built with AI', {
  x: 0.9, y: 1.95, w: 27.2, h: 3.0,
  fontFace: 'Arial', fontSize: 96, bold: true, color: RED,
  margin: 0, align: 'left', valign: 'top', lineSpacingMultiple: 1.0,
});
slide.addText(
  'How AI coding agents let one instructor ship a fully interactive, zero-install course platform — ' +
  'SYSEN 5470: Network Science & Applications for Systems Engineering',
  {
    x: 0.9, y: 5.0, w: 27.2, h: 0.85,
    fontFace: 'Arial', fontSize: 26, color: GRAY, italic: true,
    margin: 0, align: 'left', valign: 'top',
  }
);

// author block (top right, below band)
slide.addImage({ path: A('instructor.jpg'), x: 29.3, y: 2.15, w: 2.1, h: 2.1, rounding: true });
slide.addText(
  [
    { text: 'Tim Fraser, Ph.D.', options: { fontSize: 34, bold: true, color: DARK, breakLine: true } },
    { text: 'Systems Engineering · Cornell University', options: { fontSize: 23, color: GRAY, breakLine: true } },
    { text: 'tmf77@cornell.edu · timothyfraser.com/netsci', options: { fontSize: 23, color: GRAY } },
  ],
  { x: 31.7, y: 2.35, w: 7.6, h: 1.9, fontFace: 'Arial', margin: 0, align: 'left', valign: 'middle', lineSpacingMultiple: 1.12 }
);

// ---------- stats band ----------
const stats = [
  ['11', 'interactive labs, live on the course site'],
  ['21', 'planted-story project datasets'],
  ['2', 'languages taught in lockstep (R + Python)'],
  ['17', 'packages preloaded in the browser'],
  ['$0', 'servers, accounts, or hosting'],
];
{
  const y = 5.95, h = 1.8, gap = 0.5;
  const w = (38.5 - 4 * gap) / 5;
  stats.forEach(([num, label], i) => {
    const x = 0.75 + i * (w + gap);
    panel(x, y, w, h);
    slide.addText(num, {
      x: x + 0.25, y, w: 2.35, h,
      fontFace: 'Arial', fontSize: 64, bold: true, color: RED,
      margin: 0, align: 'center', valign: 'middle',
    });
    slide.addText(label, {
      x: x + 2.7, y: y + 0.18, w: w - 2.95, h: h - 0.36,
      fontFace: 'Arial', fontSize: 21, color: GRAY, bold: true,
      margin: 0, align: 'left', valign: 'middle', lineSpacingMultiple: 1.05,
    });
  });
}

// ---------- left column: problem + AI workflow ----------
const LX = 0.75, LW = 9.0;

panel(LX, 8.15, LW, 5.0);
sectionHeader('THE PROBLEM', LX + 0.35, 8.45, LW - 0.7);
slide.addText(
  [
    { text: 'Students learn networks by clicking, breaking, and rebuilding them — not by reading PDFs. ', options: { bold: true, color: DARK } },
    { text: 'But one production-quality interactive lab takes weeks of web engineering: simulation code, instant-feedback questions, mobile support. A full course needs dozens — plus datasets, codebooks, and teaching code in two languages. That is months of engineering no teaching schedule allows.', options: { color: DARK } },
  ],
  { x: LX + 0.35, y: 9.2, w: LW - 0.7, h: 4.3, fontFace: 'Arial', fontSize: 22.5, margin: 0, align: 'left', valign: 'top', lineSpacingMultiple: 1.12 }
);

panel(LX, 13.55, LW, 12.8);
sectionHeader('THE AI WORKFLOW', LX + 0.35, 13.85, LW - 0.7);
slide.addText('The instructor directs and reviews; AI agents do the engineering.', {
  x: LX + 0.35, y: 14.48, w: LW - 0.7, h: 0.62,
  fontFace: 'Arial', fontSize: 21, italic: true, color: GRAY, margin: 0,
});
const steps = [
  ['Encode conventions once', 'Reusable agent "skills" capture teaching style, dataset standards, and the course glossary.'],
  ['AI drafts each artifact', 'A lab page, a dataset generator, or a matched R + Python teaching script.'],
  ['Verify automatically', 'Headless-browser tests; answer keys recomputed from the rendered page; R and Python outputs cross-checked to match.'],
  ['Instructor reviews', 'A pedagogy, tone, and accuracy pass on every artifact before it ships.'],
  ['Ship free & static', 'GitHub Pages hosting; CI rebuilds the student repo and AI study companion automatically.'],
];
{
  let y = 15.3;
  const stepH = 1.95;
  steps.forEach(([lead, body], i) => {
    slide.addShape('ellipse', {
      x: LX + 0.38, y: y + 0.06, w: 0.62, h: 0.62,
      fill: { color: RED }, line: { color: RED, width: 1 },
    });
    slide.addText(String(i + 1), {
      x: LX + 0.38, y: y + 0.06, w: 0.62, h: 0.62,
      fontFace: 'Arial', fontSize: 26, bold: true, color: WHITE,
      margin: 0, align: 'center', valign: 'middle',
    });
    slide.addText(
      [
        { text: lead + ' — ', options: { bold: true, color: DARK } },
        { text: body, options: { color: '333333' } },
      ],
      { x: LX + 1.22, y, w: LW - 1.6, h: stepH - 0.1, fontFace: 'Arial', fontSize: 21, margin: 0, align: 'left', valign: 'top', lineSpacingMultiple: 1.1 }
    );
    y += stepH;
  });
  slide.addText('Built with agentic AI coding tools (Claude Code). Every artifact is verified; none is hand-coded.', {
    x: LX + 0.35, y: y + 0.05, w: LW - 0.7, h: 0.6,
    fontFace: 'Arial', fontSize: 18.5, italic: true, color: GRAY, margin: 0, valign: 'top',
  });
}

// ---------- centerpiece: the labs, live ----------
const CX = 10.15, CW = 19.7;

sectionHeader('THE LABS, LIVE — EVERY ONE A MANIPULABLE ARTIFACT, NOT A PDF', CX + 1.1, 8.1, CW - 1.2, {});

// hero: interactive transit lab
const heroW = 16.2, heroH = heroW / 1.6; // 10.125
const heroX = CX + (CW - heroW) / 2, heroY = 8.85;
framedImage(SHOT('lab-interactive.png'), heroX, heroY, heroW, heroH);
slide.addText(
  [
    { text: 'Case-study lab “Why does betweenness matter?” — ', options: { bold: true, color: DARK } },
    { text: 'remove a transit station and watch path lengths, components, and criticality shift live. Learning checks are recomputed from the rendered network, so answers can never drift.', options: { color: '333333' } },
  ],
  { x: CX, y: heroY + heroH + 0.15, w: CW, h: 0.78, fontFace: 'Arial', fontSize: 20.5, margin: 0, valign: 'top', lineSpacingMultiple: 1.08 }
);

// two supporting shots
{
  const w = 8.8, h = w / 1.6, gap = 0.5; // 5.5
  const x0 = CX + (CW - 2 * w - gap) / 2;
  const y = 19.95;
  framedImage(SHOT('playground-plot.png'), x0, y, w, h);
  framedImage(SHOT('visualizer-loaded.png'), x0 + w + gap, y, w, h);
  slide.addText(
    [
      { text: 'In-browser R & Python playgrounds ', options: { bold: true, color: DARK } },
      { text: '(WebAssembly): real code, real plots, on the student’s own device — no install, no login.', options: { color: '333333' } },
    ],
    { x: x0, y: y + h + 0.15, w, h: 0.85, fontFace: 'Arial', fontSize: 19.5, margin: 0, valign: 'top', lineSpacingMultiple: 1.06 }
  );
  slide.addText(
    [
      { text: 'Network Visualizer: ', options: { bold: true, color: DARK } },
      { text: 'point-and-click failure cascades and counterfactuals — then export the runnable script that reproduces every click.', options: { color: '333333' } },
    ],
    { x: x0 + w + gap, y: y + h + 0.15, w, h: 0.85, fontFace: 'Arial', fontSize: 19.5, margin: 0, valign: 'top', lineSpacingMultiple: 1.06 }
  );
}

// ---------- right column: students + phone + QR ----------
const RX = 30.35, RW = 8.9;

panel(RX, 8.15, RW, 5.5);
sectionHeader('WHAT STUDENTS GET', RX + 0.35, 8.45, RW - 0.7);
const bullets = [
  'Real R & Python in the browser — zero install, no accounts, works on any device.',
  'Labs that push back: remove a node, watch the metrics shift, get instant feedback.',
  'Explore visually, then export a complete runnable script and keep going in code.',
  'A Socratic AI study companion that asks questions back instead of giving answers.',
];
slide.addText(
  bullets.map((t, i) => ({
    text: t,
    options: { bullet: { code: '2022', indent: 14 }, color: '333333', breakLine: true, paraSpaceAfter: i === bullets.length - 1 ? 0 : 10 },
  })),
  { x: RX + 0.35, y: 9.25, w: RW - 0.7, h: 4.95, fontFace: 'Arial', fontSize: 21.5, margin: 0, align: 'left', valign: 'top', lineSpacingMultiple: 1.08 }
);

// phone screenshot + annotation
{
  const pw = 3.45, ph = pw * (2532 / 1170); // 7.47
  const py = 14.1;
  framedImage(SHOT('phone-keyboard.png'), RX + 0.15, py, pw, ph);
  slide.addText(
    [
      { text: 'Code on a phone.\n', options: { bold: true, color: DARK, fontSize: 24 } },
      { text: 'A tap-to-code block keyboard — D-pad cursor, undo/redo, and context-aware code chips — lets students write real code from the bus, the gym, or the back row.', options: { color: '333333', fontSize: 20.5 } },
    ],
    { x: RX + pw + 0.6, y: py + 0.3, w: RW - pw - 0.75, h: ph - 0.5, fontFace: 'Arial', margin: 0, valign: 'top', lineSpacingMultiple: 1.1 }
  );
}

// QR panel
{
  const y = 22.3, h = 4.05;
  panel(RX, y, RW, h);
  sectionHeader('TRY IT RIGHT NOW', RX + 0.35, y + 0.22, RW - 0.7);
  const qs = 2.5;
  slide.addImage({ path: A('qr-site.png'), x: RX + (RW / 2 - qs) / 2, y: y + 1.05, w: qs, h: qs });
  slide.addImage({ path: A('qr-visualizer.png'), x: RX + RW / 2 + (RW / 2 - qs) / 2, y: y + 1.05, w: qs, h: qs });
  slide.addText('Course site', {
    x: RX + 0.1, y: y + h - 0.48, w: RW / 2 - 0.2, h: 0.4,
    fontFace: 'Arial', fontSize: 19, bold: true, color: GRAY, align: 'center', margin: 0,
  });
  slide.addText('Network Visualizer', {
    x: RX + RW / 2 + 0.1, y: y + h - 0.48, w: RW / 2 - 0.2, h: 0.4,
    fontFace: 'Arial', fontSize: 19, bold: true, color: GRAY, align: 'center', margin: 0,
  });
}

// ---------- bottom gallery: all 21 datasets ----------
slide.addText(
  [
    { text: '21 synthetic project datasets, generated by AI under a strict codebook standard — ', options: { bold: true, color: DARK } },
    { text: 'each hides a “planted story” that survives naive analysis, and ships with R + Python loaders.', options: { color: '333333' } },
  ],
  { x: 0.75, y: 26.85, w: 38.5, h: 0.55, fontFace: 'Arial', fontSize: 22, margin: 0, align: 'center', valign: 'middle' }
);
const THUMBS = [
  'amazon-last-mile', 'uber-manhattan', 'semiconductor-supply', 'aerospace-components', 'mutualaid-quake',
  'financial-contagion', 'airline-delays', 'power-grid', 'campus-contact', 'opensource-deps', 'trade-commodity',
  'reorg-comms', 'satellite-constellation', 'drone-components', 'transit-multimodal', 'satellite-supply-chain',
  'aircraft-supply-chain', 'ups-ground-network', 'ups-package-flow', 'nyc-realestate-capital', 'nyc-realestate-portfolio',
];
{
  const n = THUMBS.length, size = 1.62, gap = (38.5 - n * size) / (n - 1);
  THUMBS.forEach((name, i) => {
    slide.addImage({
      path: path.join(__dirname, "..", "data", "projects", name, "thumb.png"),
      x: 0.75 + i * (size + gap), y: 27.55, w: size, h: size,
    });
  });
}

// footer credit
slide.addText('This poster was built with the same AI workflow it describes.', {
  x: 0.75, y: 29.32, w: 38.5, h: 0.4,
  fontFace: 'Arial', fontSize: 16, italic: true, color: '777777', margin: 0, align: 'center',
});

pres.writeFile({ fileName: path.join(__dirname, 'MTEI-teaching-poster.pptx') }).then((f) => console.log('wrote', f));
