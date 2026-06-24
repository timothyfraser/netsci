"""Render a distinct ICON thumbnail (thumb.png) for each project dataset.

Each dataset gets a recognizable emoji icon (a satellite for the satellite
network, a drone for the drone network, ...) centered on the course's dark-green
tile with the dataset name beneath it. Far more legible at thumbnail size than a
node-link hairball. Deterministic and self-contained (Pillow + NotoColorEmoji).

Run after adding a dataset (add it to ICONS below):
    python data/projects/_make_thumbnails.py
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PROJECTS = Path(__file__).resolve().parent

# course palette
BG = (10, 31, 18, 255)        # #0a1f12 card bg
BORDER = (57, 255, 20, 255)   # #39FF14 neon green
LABEL = (209, 250, 229, 255)  # #d1fae5 mint

SIZE = 320
EMOJI_PX = 168
EMOJI_FONT = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
LABEL_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# one recognizable, distinct emoji per dataset
ICONS = {
    "amazon-last-mile":        "🚚",
    "uber-manhattan":          "🚕",
    "semiconductor-supply":    "🖥️",
    "aerospace-components":     "✈️",
    "mutualaid-quake":         "🤝",
    "financial-contagion":     "📉",
    "airline-delays":          "🛫",
    "power-grid":              "⚡",
    "campus-contact":          "🦠",
    "opensource-deps":         "🧩",
    "trade-commodity":         "🌐",
    "reorg-comms":             "💬",
    "satellite-constellation": "🛰️",
    "drone-components":        "🚁",
    "transit-multimodal":      "🚇",
    "satellite-supply-chain":  "📡",
    "aircraft-supply-chain":   "🛩️",
    "ups-ground-network":      "🚛",
    "ups-package-flow":        "📦",
    "nyc-realestate-capital":  "🏙️",
    "nyc-realestate-portfolio": "🏢",
}


def _emoji_font() -> ImageFont.FreeTypeFont:
    # NotoColorEmoji is a bitmap-strike font: only specific sizes load.
    for s in (109, 136, 128):
        try:
            return ImageFont.truetype(EMOJI_FONT, s)
        except OSError:
            continue
    raise OSError("could not load NotoColorEmoji at any known strike size")


def _render_emoji(ch: str, font: ImageFont.FreeTypeFont) -> Image.Image:
    """Render one emoji glyph to a tight RGBA image, scaled to EMOJI_PX."""
    tmp = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    d.text((80, 80), ch, font=font, anchor="mm", embedded_color=True)
    bbox = tmp.getbbox() or (0, 0, 160, 160)
    glyph = tmp.crop(bbox)
    w, h = glyph.size
    scale = EMOJI_PX / max(w, h)
    return glyph.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)


def _make(name: str, ch: str, font: ImageFont.FreeTypeFont, label_font) -> None:
    tile = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    d.rounded_rectangle([4, 4, SIZE - 5, SIZE - 5], radius=28, fill=BG,
                        outline=BORDER, width=3)
    glyph = _render_emoji(ch, font)
    gx = (SIZE - glyph.width) // 2
    tile.alpha_composite(glyph, (gx, 56))
    d.text((SIZE // 2, 268), name, font=label_font, anchor="mm", fill=LABEL)
    tile.convert("RGB").save(PROJECTS / name / "thumb.png")
    print(f"  {name}/thumb.png  {ch}")


def main() -> None:
    font = _emoji_font()
    label_font = ImageFont.truetype(LABEL_FONT, 19)
    for name, ch in ICONS.items():
        if (PROJECTS / name).is_dir():
            _make(name, ch, font, label_font)


if __name__ == "__main__":
    main()
