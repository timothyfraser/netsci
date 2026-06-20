"""Concatenate the three NotebookLM bundles into ONE uploadable Markdown blob.

NotebookLM (and most LLM source limits) handle a single ~125k-word Markdown file
fine — well under NotebookLM's 500,000-words-per-source ceiling — so instead of
uploading website.md + coding-modules.md + index.md separately, you can upload
just `.notebook/netsci-notebooklm.md`.

Reads the three section files (build them first) and writes the combined file with
a title, provenance note, and a table of contents. Run after the other builders:

    python scripts/build_notebooklm_source.py
    python scripts/build_coding_bundle.py
    python scripts/build_index.py
    python scripts/build_combined_bundle.py
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

NB = Path(__file__).resolve().parent.parent / ".notebook"
OUT = NB / "netsci-notebooklm.md"

# (filename, section title, one-line description) in reading order
SECTIONS = [
    ("index.md", "Resource Index",
     "A map of every course resource — labs, code folders, datasets, help pages."),
    ("website.md", "Course Website",
     "The full visible text of the course site: syllabus, labs, assignments, help."),
    ("coding-modules.md", "Coding Modules",
     "Every Markdown / R / Python file in the repo — case-study code, project "
     "datasets (READMEs + loaders + generators), and skills."),
]


def main() -> None:
    parts = [
        "# SYSEN 5470 — Combined NotebookLM Source",
        "",
        "> Network Science and Applications for Systems Engineering · Cornell Engineering",
        ">",
        f"> Single-file bundle generated {date.today().isoformat()} from the course repo "
        "(`timothyfraser/netsci`). Upload **this one file** to NotebookLM instead of the "
        "three section files separately — it contains all of them.",
        "",
        "## Contents",
    ]
    available = [(f, t, d) for f, t, d in SECTIONS if (NB / f).exists()]
    for i, (_, title, desc) in enumerate(available, 1):
        anchor = title.lower().replace(" ", "-")
        parts.append(f"{i}. [{title}](#{anchor}) — {desc}")
    parts.append("")

    for fname, title, desc in available:
        body = (NB / fname).read_text().rstrip()
        parts.append("")
        parts.append("---")
        parts.append("")
        parts.append(f"# {title}")
        parts.append("")
        parts.append(f"*{desc}*")
        parts.append("")
        parts.append(body)

    OUT.write_text("\n".join(parts) + "\n")
    words = len(OUT.read_text().split())
    print(f"Wrote {OUT.relative_to(NB.parent)} "
          f"({OUT.stat().st_size/1024:.1f} KB, ~{words:,} words, "
          f"{len(available)} sections)")


if __name__ == "__main__":
    main()
