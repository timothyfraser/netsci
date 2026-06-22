"""Bundle the student-facing, chat-invokable skills into one Markdown file.

Output: .notebook/skills.md

The course's NotebookLM Study Companion exposes a set of slash commands
(`/glossary`, `/quizme`, `/interpret`, ...). Each command's behavior is defined
by a `SKILL.md` under `.notebook/<command>/`. This builder concatenates only the
**invokable** skills — the ones that work inline in a chat — into a single source
so they ride along in the combined NotebookLM bundle.

Deliberately EXCLUDED: skills whose output is not a chat interaction and so don't
make sense to "invoke" in the Companion — `cheatsheet/` (a printable doc) and
`videos/` (Audio/Video Overview prompts). They still live in the repo.

Run after editing any `.notebook/<skill>/SKILL.md`, before the combined bundle:

    python scripts/build_skills_bundle.py
    python scripts/build_combined_bundle.py
"""
from __future__ import annotations

from pathlib import Path

NB = Path(__file__).resolve().parent.parent / ".notebook"
OUT = NB / "skills.md"

# Ordered list of invokable skills: (folder, command, one-line description).
# The persona must be first — it's what makes the commands work.
SKILLS = [
    ("study_companion_persona", "/study",
     "General study mode + the persona to paste into Configure Chat. Tell it what "
     "you're working on and it coaches you (and lists the other commands)."),
    ("study_companion_prompts", "/prompts",
     "The command quick-reference and the full copy-paste prompt library."),
    ("glossary", "/glossary",
     "Define or contrast course vocabulary and flag the common mistakes."),
    ("flashcards", "/flashcards",
     "Generate a copy-pasteable flashcard set on a topic."),
    ("quizme", "/quizme",
     "Adaptive one-at-a-time quiz with scoring and a review list."),
    ("interpret", "/interpret",
     "Stress-test your own interpretation of a result."),
    ("method-picker", "/methodpick",
     "Choose an approach by interrogating the question you're answering."),
    ("sketchpad", "/sketch",
     "By-hand sketchpad questions to do before opening R."),
]


def main() -> None:
    parts = [
        "# SYSEN 5470 — Student Skills & Commands",
        "",
        "> The Study Companion understands a set of **slash commands**. Type one at the",
        "> start of a message (e.g. `/glossary`, `/quizme`) to switch study modes. Every",
        "> command is built to help you *think*, not to do your work. The persona below",
        "> defines them; paste it into NotebookLM's Configure Chat once to turn them on.",
        "",
        "## Available commands",
        "",
        "| Command | Skill | What it does |",
        "|---|---|---|",
    ]
    available = [(f, c, d) for f, c, d in SKILLS if (NB / f / "SKILL.md").exists()]
    for folder, cmd, desc in available:
        parts.append(f"| `{cmd}` | {folder} | {desc} |")
    parts.append("")

    for folder, cmd, _ in available:
        body = (NB / folder / "SKILL.md").read_text().rstrip()
        parts.append("")
        parts.append("---")
        parts.append("")
        parts.append(f"<!-- skill: {folder} · command: {cmd} -->")
        parts.append("")
        parts.append(body)

    OUT.write_text("\n".join(parts) + "\n")
    words = len(OUT.read_text().split())
    print(f"Wrote {OUT.relative_to(NB.parent)} "
          f"({OUT.stat().st_size/1024:.1f} KB, ~{words:,} words, "
          f"{len(available)} skills)")


if __name__ == "__main__":
    main()
