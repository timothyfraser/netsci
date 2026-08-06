# Cornell Engineering teaching poster (40″ × 30″)

**“Production-Quality Interactive Course Labs, Built with AI”** — a teaching poster about how
SYSEN 5470's interactive labs, playgrounds, datasets, and visualizer were built with AI coding
agents. Laid out on the official Cornell Duffield Engineering 40×30 poster artwork.

## Start here

Open **`poster-mockup.html`** in a browser. It is one self-contained file (every image is
inlined, nothing loads from the network) and it opens with a **control sidebar** for choosing
how the poster looks:

### The three colour roles

The poster reads as three independent background layers, and the sidebar controls each one:

1. **Figure background** — the background *inside* the screenshots. A figure has two zones that
   should **contrast**, or it reads flat: **A**, the canvas the network is drawn on, and **B**,
   the panel chrome around it. The two headline options set them against each other —
   **white canvas · red panels** and **red canvas · white panels** — and the playground's plot
   follows the same choice so all three figures agree. Single-tone variants (all white, all light
   grey, all light red, all Cornell red, all dark red, original neon) are also available.
   All are separately captured, since the colour is baked into the images.
2. **Card background** — the poster's cards, and the backing cards behind the captions, author
   block, and title. Any colour; the type inside flips to light automatically on a dark card.
3. **True background** — what sits behind and between the cards: the Duffield template artwork,
   or a flat colour (a flat colour keeps the branded red band and drops only the busy halftone).

**Colour combos** in the sidebar set all three at once:

| | Figure (canvas · panels) | Cards | True background |
|---|---|---|---|
| Default | white · red | white | template artwork |
| A | white · red | light red | white |
| B | white · red | white | light grey |
| C | red · white | white | template artwork |
| D | red · white | light red | dark red |

### Everything else

| Control | What it does |
|---|---|
| **Figure size** | Scales the two figure columns; the text column never drops below 7.9 in |
| **Text size** | Scales every piece of poster type at once |
| **Descriptive detail** | Minimal (headlines only) · Standard · Detailed (full sentences) |
| **Accent colour** | Defaults to Cornell carnelian `#B31B1B` |
| **Backing cards** | Behind captions, author block, and the title — keeps text readable over the artwork |
| **Sections** | Show/hide the stats band, QR panel, dataset thumbnails, headshot, author QR |
| **Preview zoom** | Screen only — the printed size is always 40 × 30 in |

Defaults open at the chosen settings: Cornell-red figures, white cards, template artwork,
figure and text size 110%, minimal detail, backing cards on.

A fit indicator warns if a column overflows the page after a change.

The sidebar never prints. To export: **Ctrl/Cmd + P** → *Save as PDF*, paper size **40 × 30 in**
(or Custom), margins **None**, and tick **Background graphics**.

**`poster-print-40x30.pdf` is the print deliverable** — the default look at 110% text, 40 × 30 in,
with the figures embedded at print resolution. `preview-default.pdf` and `preview-red-canvas.pdf`
are lighter screen previews.

### Print resolution

| Element | Effective resolution at printed size |
|---|---|
| All poster text | vector — resolution-independent |
| Playground figure | 1039 ppi |
| Visualizer figure | 990 ppi |
| Case-study lab figure | 693 ppi |
| QR codes | 960–1190 ppi |
| Dataset thumbnails | 948 ppi |
| Headshot | 279 ppi — limited by the 460 px source |
| Duffield template artwork | 72 ppi — limited by Cornell's 2880 px template |

Rebuild it with:

```bash
node hires-lab.js stagelight 12      # the lab, kept under Chromium's raster limit
node hires-viz-pg.js stagelight 14   # visualizer + playground
python3 build_mockup.py --print      # writes poster-print.html with the hi-res figures
chromium --headless --no-pdf-header-footer \
  --print-to-pdf=poster-print-40x30.pdf "file://$PWD/poster-print.html"
```

**Chromium silently fails to rasterise past ~16384 px in a dimension** — it returns an image of
the requested size with most of the content missing. That is why the lab is captured at scale 12
(11472 × 11688) rather than 18: at 18 both dimensions cleared the limit and the canvas came back
blank. Always check the captured content, not just its dimensions. To render any other combination
headlessly, pass URL parameters — `?combo=a` … `?combo=d`, or `?theme=…&card=…&bg=…&ts=…&fs=…&detail=…`:

```bash
chromium --headless --no-pdf-header-footer \
  --print-to-pdf=combo-b.pdf "file://$PWD/poster-mockup.html?combo=b"
```

### QR codes

Three, all verified to decode from the rendered 40×30 PDF (including at a third of print scale):

| Where | Links to |
|---|---|
| Beside the author block | `https://timothyfraser.com` |
| Bottom right, "Course site" | `https://timothyfraser.com/netsci/` |
| Bottom right, "Network Visualizer" | `https://timothyfraser.com/netsci/visualizer.html` |

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

`theme-shared.js` holds the eight themes and the palette remap (the course's neon palette →
carnelian / gold / grey / white). In-figure text is enlarged there too, so the screenshots stay
legible at poster scale.

Two details worth knowing if you edit the themes:

- The Cornell-red theme's reds are **sampled from the template artwork itself** — the header
  band is a gradient running `#B02327` at the left to `#E8575A` at the right, so the figures use
  `#C32529` for panels and `#E8575A`/`#F7C948` for accents and stay in family with the band.
- The paint pass is **zone-aware**: it asks whether each element sits inside the canvas
  (`#network-svg, #graph-stage`) or in the chrome around it, and applies that zone's palette,
  panel colour, and text contrast. That is what makes the mixed themes possible — canvas labels
  go dark on a light canvas and white on a red one, independent of the chrome.
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
QR codes were generated with `segno` (carnelian on white).

## Gotcha worth remembering

`theme-shared.js` builds the paint pass as a JavaScript **template literal** that is later
`eval`-ed in the page. Backslashes inside it are consumed by the template literal, so any regex
in that string needs them doubled (`\\(`, `\\d`, `\\s`). A single-backslash regex silently
matches nothing — which looks exactly like "the recolour didn't apply" rather than a syntax error.
