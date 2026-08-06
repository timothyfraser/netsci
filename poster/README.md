# Cornell Engineering teaching poster (40″ × 30″)

**“Production-Quality Interactive Course Labs, Built with AI”** — a teaching poster
about how SYSEN 5470's interactive labs, playgrounds, datasets, and visualizer were
built with AI coding agents. Built on the official Cornell Duffield Engineering
40×30 PowerPoint poster template.

## Files

| File | What it is |
|---|---|
| `MTEI-teaching-poster.pptx` | The poster, editable in PowerPoint (40″ × 30″ slide) |
| `MTEI-teaching-poster.pdf` | Print-ready PDF export |
| `build-poster.js` | Generates the `.pptx` from assets + screenshots (pptxgenjs) |
| `assets/` | Template background, headshot, QR codes (course site + visualizer) |
| `shots/` | Screenshots of the live course site used on the poster |
| `tools/` | Playwright scripts that captured `shots/` from timothyfraser.com/netsci |

## Rebuild

```bash
cd poster
npm install pptxgenjs
node build-poster.js          # writes MTEI-teaching-poster.pptx
```

Dataset thumbnails are read from `../data/projects/*/thumb.png`, so build from
within the repo. To re-capture screenshots (needs Chromium + `playwright-core`):

```bash
node tools/capture-shots.js            # lab, visualizer, phone keyboard
node tools/capture-playground-plot.js  # Python playground running a plot
```

QR codes were generated with `segno` (Python):
`segno.make(url, error='q').save(..., scale=24, border=2, dark='#B31B1B', light='white')`.
