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
| **Figure background** | Cornell red · White · Light grey · original course neon — swaps all three screenshots |
| **Figure size** | Scales the two figure columns (the left text column absorbs the change) |
| **Text size** | Scales every piece of poster type at once |
| **Descriptive detail** | Minimal (headlines only) · Standard · Detailed (full sentences) |
| **Accent colour** | Defaults to Cornell carnelian `#B31B1B` |
| **Card style** | White cards · warm tinted cards · no cards |
| **Poster background** | Duffield template artwork, or a flat colour — white, Cornell light grey, warm red tint, beige, khaki, navy, Cornell red, or any custom colour. A flat colour keeps the template's branded red band but drops the busy halftone; dark choices flip the type to white automatically. |
| **Backing cards** | Translucent cards behind the figure captions, author block, and (optionally) the title, so text stays readable over the template artwork |
| **Sections** | Show/hide the stats band, QR panel, dataset thumbnails, headshot |
| **Preview zoom** | Screen only — the printed size is always 40 × 30 in |

Defaults open at the settings chosen for this poster: Cornell-red figures, figure and text
size 110%, minimal detail, warm tinted cards, template artwork.

A fit indicator warns if a column overflows the page after a change.

The sidebar never prints. To export: **Ctrl/Cmd + P** → *Save as PDF*, paper size **40 × 30 in**
(or Custom), margins **None**, and tick **Background graphics**.

`preview-cornell-red.pdf` is pre-rendered at the default settings; `preview-white.pdf` is the
same poster with white figure backgrounds.

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
node capture-multi.js                 # all three figures × all four themes
node capture-multi.js red             # just one theme
```

`theme-shared.js` holds the four themes and the palette remap (the course's neon palette →
carnelian / gold / grey / white). In-figure text is enlarged there too, so the screenshots stay
legible at poster scale.

Two details worth knowing if you edit the themes:

- The Cornell-red theme's reds are **sampled from the template artwork itself** — the header
  band is a gradient running `#B02327` at the left to `#E8575A` at the right, so the figures use
  `#C32529` for panels and `#E8575A`/`#F7C948` for accents and stay in family with the band.
- After the CSS theme is injected, a paint pass rewrites anything the stylesheet can't reach:
  green-dominant SVG fills (the course's neon palette), green element backgrounds, and any
  near-black chip or button. The green test is deliberately tuned to catch neon, lime, and mint
  while leaving gold, pale gold, pink, and white alone.

## Files

| Path | What it is |
|---|---|
| `poster-mockup.html` | The poster + control sidebar, self-contained |
| `preview-*.pdf` | Pre-rendered 40×30 exports |
| `build_mockup.py` | Inlines every asset and writes the HTML |
| `capture-multi.js`, `theme-shared.js` | Screenshot pipeline and poster-only theming |
| `shots/` | Source screenshots, `<figure>-<theme>.png` |
| `assets/` | Duffield background artwork, headshot, QR codes |

Dataset thumbnails come from `../data/projects/*/thumb.png`, so build from inside the repo.
QR codes were generated with `segno` (carnelian on white) and verified to decode from the
rendered PDF.

## Gotcha worth remembering

`theme-shared.js` builds the paint pass as a JavaScript **template literal** that is later
`eval`-ed in the page. Backslashes inside it are consumed by the template literal, so any regex
in that string needs them doubled (`\\(`, `\\d`, `\\s`). A single-backslash regex silently
matches nothing — which looks exactly like "the recolour didn't apply" rather than a syntax error.
