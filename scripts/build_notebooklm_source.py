"""Concatenate visible text from docs/ into one Markdown file for NotebookLM.

Output: .notebook/website.md

The file is committed to the repo by the GitHub Actions workflow so the latest
version is always one click away on GitHub (open the file, click "Raw", paste
into NotebookLM).

Run locally with:
    pip install beautifulsoup4 markdownify
    python scripts/build_notebooklm_source.py
"""

from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from markdownify import markdownify

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS = REPO_ROOT / "docs"
OUT = REPO_ROOT / ".notebook" / "website.md"

COURSE_TITLE = "SYSEN 5470 — Network Science for Systems Engineering"

# Order matches the site's nav, then case studies alphabetical, then extras.
ROOT_ORDER = [
    "index.html",
    "syllabus.html",
    "materials.html",
    "four-skills.html",
    "case-studies.html",
    # case-studies/*.html inserted here at runtime
    "visualizer.html",
    "playground.html",
    "playground-r.html",
    "playground-py.html",
    "readings.html",
    "sketchpad.html",
    "about.html",
    "flyer.html",
]

EXTRAS = [
    "promo.md",
    "images/README.md",
    "playground-data/README.md",
]

# Tags whose content we never want in the extracted text.
DROP_TAGS = ("script", "style", "noscript", "canvas", "svg", "nav")
# Class names that flag decorative or navigational containers.
DROP_CLASSES = {"nav", "nav-inner", "nav-links", "nav-cta", "bg-canvas"}


def extract_html(path: Path) -> tuple[str, str]:
    """Return (title, markdown_body) for an HTML file."""
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")

    title_tag = soup.find("title")
    h1_tag = soup.find("h1")
    title = (
        title_tag.get_text(strip=True)
        if title_tag and title_tag.get_text(strip=True)
        else (h1_tag.get_text(strip=True) if h1_tag else path.stem)
    )

    # Strip noise.
    for tag in soup(list(DROP_TAGS)):
        tag.decompose()
    for el in soup.find_all(class_=True):
        classes = set(el.get("class", []))
        if classes & DROP_CLASSES:
            el.decompose()
    if soup.head:
        soup.head.decompose()

    body = soup.body or soup
    markdown = markdownify(
        str(body),
        heading_style="ATX",
        strip=["a"],  # drop link URLs but keep the visible link text
    )
    # Collapse 3+ blank lines into 2.
    lines = [line.rstrip() for line in markdown.splitlines()]
    cleaned: list[str] = []
    blank = 0
    for line in lines:
        if not line.strip():
            blank += 1
            if blank <= 2:
                cleaned.append("")
        else:
            blank = 0
            cleaned.append(line)
    return title, "\n".join(cleaned).strip()


def section(title: str, source_rel: str, body: str) -> str:
    return f"# {title}\n\n_Source: {source_rel}_\n\n{body}\n\n---\n\n"


def gather_files() -> list[Path]:
    """Build the ordered list of files to include."""
    ordered: list[Path] = []
    seen: set[Path] = set()

    def add(path: Path) -> None:
        if path.exists() and path not in seen:
            ordered.append(path)
            seen.add(path)

    for name in ROOT_ORDER:
        add(DOCS / name)
        if name == "case-studies.html":
            for case in sorted((DOCS / "case-studies").glob("*.html")):
                add(case)

    # Anything else in docs/ we haven't covered (so future pages auto-include).
    for extra in sorted(DOCS.glob("*.html")):
        add(extra)

    for rel in EXTRAS:
        add(DOCS / rel)

    return ordered


def main() -> int:
    if not DOCS.is_dir():
        print(f"docs/ not found at {DOCS}", file=sys.stderr)
        return 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    files = gather_files()
    if not files:
        print("No docs/ files matched", file=sys.stderr)
        return 1

    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    parts: list[str] = [
        f"# {COURSE_TITLE}\n\n",
        f"_Auto-generated NotebookLM source · {timestamp}_\n\n",
        "This document is the concatenated visible text of the course website. "
        "It refreshes automatically whenever the site changes. "
        "Paste this file into NotebookLM as a source.\n\n---\n\n",
    ]

    for path in files:
        rel = path.relative_to(REPO_ROOT).as_posix()
        if path.suffix == ".html":
            title, body = extract_html(path)
        else:
            body = path.read_text(encoding="utf-8").strip()
            title = path.stem.replace("-", " ").replace("_", " ").title()
        parts.append(section(title, rel, body))

    OUT.write_text("".join(parts), encoding="utf-8")
    size_kb = OUT.stat().st_size / 1024
    print(f"Wrote {OUT.relative_to(REPO_ROOT)} ({size_kb:.1f} KB, {len(files)} sections)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
