"""Fail if tracked grading paths contain student data (run before commit)."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parent

FORBIDDEN_PATH_PARTS = (
    "/data/",
    "/cache/",
    "/.venv/",
    "/.env",
    "grades.csv",
)


def _forbidden_path(norm: str) -> bool:
    if any(part in norm for part in FORBIDDEN_PATH_PARTS):
        # .env.example is a template, not secrets
        if norm.endswith(".env.example"):
            return False
        if norm.endswith("/.env") or norm.endswith(".grading/.env"):
            return True
        if "/data/" in norm or "/cache/" in norm or "/.venv/" in norm or "grades.csv" in norm:
            return True
        return "/.env" in norm and not norm.endswith(".example")
    return False

# Real submission text / grades in source — field names and mock fixtures are OK.
FORBIDDEN_CONTENT_PATTERNS = (
    re.compile(r"Assenheimer|Kanoa Chun|5895303|5619875"),
    re.compile(r"proposed_score.*\d{2,3}.*final_grade", re.I),
)


def staged_grading_files() -> list[str]:
    out = subprocess.check_output(
        ["git", "diff", "--cached", "--name-only", "--", ".grading", ".gitignore"],
        cwd=REPO,
        text=True,
    )
    return [line.strip() for line in out.splitlines() if line.strip()]


def main() -> int:
    files = staged_grading_files()
    if not files:
        # Not staged yet — scan intended commit paths on disk
        candidates = [
            p for p in ROOT.rglob("*")
            if p.is_file()
            and not _forbidden_path(str(p.relative_to(REPO)).replace("\\", "/"))
            and p.suffix not in (".pyc",)
            and ".venv" not in str(p)
        ]
        rel_paths = [str(p.relative_to(REPO)).replace("\\", "/") for p in candidates]
    else:
        rel_paths = files

    errors: list[str] = []
    for rel in rel_paths:
        norm = rel.replace("\\", "/")
        if _forbidden_path(norm):
            errors.append(f"forbidden path staged: {rel}")
            continue
        path = REPO / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if path.name == "verify_commit_safe.py":
            continue
        for pat in FORBIDDEN_CONTENT_PATTERNS:
            if pat.search(text):
                errors.append(f"suspicious content in {rel}: {pat.pattern}")
                break

    if errors:
        for e in errors:
            print("FAIL:", e, file=sys.stderr)
        return 1

    print(f"OK: {len(rel_paths)} paths checked — no student data/cache/grades detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
