# Cornell Engineering teaching poster (40″ × 30″)

**“Production-Quality Interactive Course Labs, Built with AI”** — a teaching poster about how
SYSEN 5470's interactive labs, playgrounds, datasets, and visualizer were built with AI coding
agents. Laid out on the official Cornell Duffield Engineering 40×30 poster artwork.

## Start here

Open **`poster-mockup.html`** in a browser. It is one self-contained file (every image is
inlined, nothing loads from the network) and it opens with a **control sidebar** for choosing
how the poster looks:

| Control | What it does |
|---|---|
| **Figure background** | White · Light grey · Cornell red · Original course neon — swaps all three screenshots |
| **Figure size** | Scales the two figure columns (the left text column absorbs the change) |
| **Text size** | Scales every piece of poster type at once |
| **Descriptive detail** | Minimal (headlines only) · Standard · Detailed (full sentences) |
| **Accent colour** | Defaults to Cornell carnelian `#B31B1B` |
| **Card style** | White cards · warm tinted cards · no cards |
| **Poster background** | Duffield template artwork, or plain white with a red band |
| **Sections** | Show/hide the stats band, QR panel, dataset thumbnails, headshot |
| **Preview zoom** | Screen only — the printed size is always 40 × 30 in |

A fit indicator warns if a column overflows the page after a change.

The sidebar never prints. To export: **Ctrl/Cmd + P** → *Save as PDF*, paper size **40 × 30 in**
(or Custom), margins **None**, and tick **Background graphics**.

`preview-white.pdf` and `preview-orig.pdf` are pre-rendered at the two headline settings.

## Rebuilding

```bash
cd poster
python3 build_mockup.py        # re-embeds shots/ + assets/ into poster-mockup.html
```

Screenshots are captured from the live course site with Playwright + the pre-installed
Chromium. Each figure is captured once per theme; the poster-only restyle is injected as CSS
(the site's theme is CSS-variable driven, so backgrounds, accents, and font sizes can be
overridden without touching the site).

```bash
node capture-multi.js          # all three figures × all four themes
node capture-lab.js            # the case-study lab only
node capture-fix.js            # lab + visualizer only
```

`theme-shared.js` holds the four themes and the palette remap (the course's neon palette →
carnelian / gold / grey / white). In-figure text is enlarged there too, so the screenshots stay
legible at poster scale.

## Files

| Path | What it is |
|---|---|
| `poster-mockup.html` | The poster + control sidebar, self-contained |
| `preview-*.pdf` | Pre-rendered 40×30 exports |
| `build_mockup.py` | Inlines every asset and writes the HTML |
| `capture-*.js`, `theme-shared.js` | Screenshot pipeline and poster-only theming |
| `shots/` | Source screenshots, `<figure>-<theme>.png` |
| `assets/` | Duffield background artwork, headshot, QR codes |

Dataset thumbnails come from `../data/projects/*/thumb.png`, so build from inside the repo.
QR codes were generated with `segno` (carnelian on white) and verified to decode from the
rendered PDF.
