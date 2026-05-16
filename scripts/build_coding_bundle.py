"""Bundle every .md, .R, and .py file in the repo into one Markdown file.

Output: .notebook/coding-modules.md

Skips the website source (docs/) — that's covered by build_notebooklm_source.py —
and skips this script directory, generated bundles, and project meta files.
The result is a single document students can paste into NotebookLM as a source
for the coding teaching modules.

Run locally with:
    python scripts/build_coding_bundle.py
"""

from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT = REPO_ROOT / ".notebook" / "coding-modules.md"

EXCLUDE_DIRS = {
    ".git",
    ".github",
    ".claude",
    ".notebook",
    "scripts",
    "build",
    "node_modules",
    "renv",
    "__pycache__",
    ".Rproj.user",
    "docs",  # website content lives in the other bundle
}

EXCLUDE_FILES = {
    "README.md",
    "LICENSE",
    "LICENSE.md",
    "CLAUDE.md",
}

EXTENSIONS = {
    ".md": None,
    ".R": "r",
    ".r": "r",
    ".py": "python",
}


def is_excluded(path: Path) -> bool:
    parts = set(path.relative_to(REPO_ROOT).parts)
    if parts & EXCLUDE_DIRS:
        return True
    if path.name in EXCLUDE_FILES and path.parent == REPO_ROOT:
        return True
    return False


def gather_files() -> list[Path]:
    found: list[Path] = []
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in EXTENSIONS:
            continue
        if is_excluded(path):
            continue
        found.append(path)
    found.sort(key=lambda p: p.relative_to(REPO_ROOT).as_posix())
    return found


def render(path: Path) -> str:
    rel = path.relative_to(REPO_ROOT).as_posix()
    lang = EXTENSIONS[path.suffix]
    body = path.read_text(encoding="utf-8", errors="replace").rstrip()
    header = f"## `{rel}`\n\n"
    if lang is None:
        return f"{header}{body}\n\n---\n\n"
    return f"{header}```{lang}\n{body}\n```\n\n---\n\n"


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    files = gather_files()
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    parts: list[str] = [
        "# SYSEN 5470 — Coding Modules Bundle\n\n",
        f"_Auto-generated NotebookLM source · {timestamp}_\n\n",
        "Every Markdown, R, and Python file in the course's coding modules, "
        "concatenated into one document. Paste this into NotebookLM as a "
        "source alongside the website bundle.\n\n",
    ]

    if not files:
        parts.append(
            "_No coding-module files (.md / .R / .py) were found outside "
            "`docs/` and `scripts/` when this bundle was generated._\n"
        )
    else:
        parts.append(f"**{len(files)} files included.**\n\n---\n\n")
        for path in files:
            parts.append(render(path))

    OUT.write_text("".join(parts), encoding="utf-8")
    size_kb = OUT.stat().st_size / 1024
    print(f"Wrote {OUT.relative_to(REPO_ROOT)} ({size_kb:.1f} KB, {len(files)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
