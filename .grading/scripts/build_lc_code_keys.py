"""Run teaching-code Learning Check scripts and capture authoritative numeric answers.

Output: .grading/cache/lc_code_keys.json (gitignored). Regenerate after changing
code/NN_* example.R or example.py.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parent
CONFIG = ROOT / "config" / "assignments.json"
OUT = ROOT / "cache" / "lc_code_keys.json"

ANSWER_RE = re.compile(
    r"Learning Check answer(?:\s*\([^)]+\))?:\s*(.+)",
    re.IGNORECASE,
)
QUESTION_RE = re.compile(
    r"#\s*QUESTION:\s*(.+?)(?:\n#|\nprint|\ncat\s)",
    re.DOTALL,
)

SUBPROCESS_ENV = {
    **os.environ,
    "PYTHONIOENCODING": "utf-8",
    "PYTHONUTF8": "1",
    "R_ENCODING": "UTF-8",
    "LC_ALL": "C.UTF-8",
}


def _parse_question(text: str) -> str:
    m = QUESTION_RE.search(text)
    if not m:
        return ""
    question = re.sub(r"^#\s?", "", m.group(1), flags=re.MULTILINE).strip()
    return re.sub(r"\s+", " ", question)


def _extract_answer(stdout: str) -> tuple[str, str]:
    for line in stdout.splitlines():
        if "Learning Check answer" not in line:
            continue
        m = ANSWER_RE.search(line)
        if m:
            value = m.group(1).strip()
            return value, line.strip()
    return "", ""


def _run_script(code_dir: Path, name: str, *, timeout: int) -> tuple[str, str]:
    if name.endswith(".R"):
        cmd = ["Rscript", name]
    else:
        cmd = [sys.executable, name]
    proc = subprocess.run(
        cmd,
        cwd=code_dir,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        env=SUBPROCESS_ENV,
    )
    combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
    if proc.returncode != 0:
        tail = combined.strip()[-2000:]
        raise RuntimeError(f"exit {proc.returncode}: {tail}")
    return combined, proc.stdout or ""


def _runner_candidates(code_dir: Path) -> list[tuple[str, str]]:
    candidates: list[tuple[str, str]] = []
    if (code_dir / "example.R").is_file() and shutil.which("Rscript"):
        candidates.append(("example.R", "R"))
    if (code_dir / "example.py").is_file():
        candidates.append(("example.py", "Python"))
    return candidates


def _run_assignment(
    code_dir: Path,
    *,
    r_timeout: int = 180,
    py_timeout: int = 600,
) -> tuple[str, str, str, str]:
    last_err: Exception | None = None
    for script_name, runner in _runner_candidates(code_dir):
        timeout = r_timeout if runner == "R" else py_timeout
        try:
            combined, stdout = _run_script(code_dir, script_name, timeout=timeout)
            expected, raw_line = _extract_answer(stdout or combined)
            if expected:
                return script_name, runner, expected, raw_line
            last_err = RuntimeError("no 'Learning Check answer' line in output")
        except Exception as exc:
            last_err = exc
    raise RuntimeError(str(last_err or "no runnable example script"))


def build_keys() -> dict[str, object]:
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    keys: dict[str, object] = {}
    errors: list[str] = []

    for assignment in cfg.get("assignments", []):
        if assignment.get("type") != "learning_checks":
            continue
        akey = assignment["key"]
        rel = assignment.get("code_path", "")
        code_dir = REPO / rel.replace("/", "\\") if rel else Path()
        if not code_dir.is_dir():
            errors.append(f"{akey}: missing code dir {code_dir}")
            continue

        if not _runner_candidates(code_dir):
            errors.append(f"{akey}: no example.R or example.py in {code_dir}")
            continue

        question = ""
        for name in ("example.R", "example.py"):
            script_path = code_dir / name
            if script_path.is_file():
                question = _parse_question(script_path.read_text(encoding="utf-8", errors="replace"))
                break

        try:
            script_name, runner, expected, raw_line = _run_assignment(code_dir)
        except Exception as exc:
            errors.append(f"{akey}: {exc}")
            continue

        keys[akey] = {
            "assignment_key": akey,
            "case_study_key": assignment.get("case_study_key", ""),
            "code_path": rel,
            "source_file": script_name,
            "runner": runner,
            "question": question,
            "expected_value": expected,
            "raw_line": raw_line,
        }
        print(f"OK {akey}: {expected!r} ({runner}/{script_name})")

    if errors:
        for err in errors:
            print(f"FAIL {err}", file=sys.stderr)

    payload: dict[str, object] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "keys": keys,
    }
    if errors:
        payload["errors"] = errors

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {OUT} ({len(keys)} keys, {len(errors)} errors)")
    return payload


def main() -> int:
    payload = build_keys()
    errors = payload.get("errors") or []
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
