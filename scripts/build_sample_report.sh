#!/usr/bin/env bash
#
# build_sample_report.sh — regenerate the project sample report PDF.
#
# Converts docs/assignments/sample-report.md -> docs/assignments/sample-report.pdf
# (the exemplar the Assignments page links to). Page geometry and font size come
# from the YAML front matter in the .md, so this script just picks an engine.
#
# Needs pandoc + a LaTeX engine (xelatex recommended). If pandoc isn't on PATH
# but Docker is, it falls back to the official pandoc/latex image — no local
# TeX install required.
#
# The two embedded figures are generated separately (and committed) by
# scripts/build_sample_report_figures.py; this script just embeds the existing
# PNGs via --resource-path.
#
# Usage:  scripts/build_sample_report.sh
#
set -euo pipefail

# repo root = parent of this script's directory
cd "$(dirname "$0")/.."

SRC="docs/assignments/sample-report.md"
OUT="docs/assignments/sample-report.pdf"
ARGS=(--pdf-engine=xelatex --resource-path=docs/assignments -o "$OUT" "$SRC")

if command -v pandoc >/dev/null 2>&1; then
  echo "→ Building $OUT with local pandoc + xelatex…"
  pandoc "${ARGS[@]}"
elif command -v docker >/dev/null 2>&1; then
  echo "→ pandoc not found; building $OUT via the pandoc/latex Docker image…"
  docker run --rm -v "$PWD":/data -w /data pandoc/latex:latest "${ARGS[@]}"
else
  echo "✗ Need either pandoc (+xelatex) or Docker installed." >&2
  echo "  macOS:  brew install pandoc && brew install --cask mactex-no-gui" >&2
  echo "  Ubuntu: sudo apt-get install pandoc texlive-xetex" >&2
  echo "  Docker: install Docker Desktop, then re-run this script." >&2
  exit 1
fi

echo "✓ Wrote $OUT"
