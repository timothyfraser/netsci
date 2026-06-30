"""Load authoritative LC answer keys from course website + teaching code."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from env import GRADING_ROOT

REPO_ROOT = GRADING_ROOT.parent
LC_CODE_KEYS_PATH = GRADING_ROOT / "cache" / "lc_code_keys.json"


def _lab_html_path(assignment: dict[str, Any]) -> Path:
    rel = assignment.get("lab_path") or ""
    return REPO_ROOT / rel.replace("/", "\\") if rel else Path()


def _code_dir(assignment: dict[str, Any]) -> Path:
    rel = assignment.get("code_path") or ""
    return REPO_ROOT / rel.replace("/", "\\") if rel else Path()


def parse_lc_cards(html: str) -> list[dict[str, str]]:
    """Extract LC number, question snippet, and correct letter from lab HTML."""
    cards: list[dict[str, str]] = []
    for block in re.split(r'<div class="lc-card">', html)[1:]:
        num_m = re.search(r'<span class="lc-number">(LC\s*\d+)</span>', block)
        q_m = re.search(
            r'<div class="lc-question"[^>]*>(.*?)</div>',
            block,
            re.DOTALL,
        )
        ans_m = re.search(
            r'class="lc-feedback feedback-answer"[^>]*>.*?<strong>Answer:\s*([A-D])',
            block,
            re.DOTALL | re.IGNORECASE,
        )
        if not num_m or not ans_m:
            continue
        question = re.sub(r"<[^>]+>", " ", q_m.group(1) if q_m else "").strip()
        question = re.sub(r"\s+", " ", question)[:400]
        cards.append(
            {
                "id": num_m.group(1).replace(" ", "").lower(),
                "label": num_m.group(1).strip(),
                "question": question,
                "correct_letter": ans_m.group(1).upper(),
            }
        )
    return cards


def parse_code_learning_check(code_dir: Path) -> dict[str, str]:
    """Read the 'I ran the code' question + context from example.py / example.R."""
    for name in ("example.py", "example.R"):
        path = code_dir / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        q_block = re.search(
            r"#\s*QUESTION:\s*(.+?)(?:\n#|\nprint|\ncat\s)",
            text,
            re.DOTALL,
        )
        question = ""
        if q_block:
            question = re.sub(r"^#\s?", "", q_block.group(1), flags=re.MULTILINE).strip()
            question = re.sub(r"\s+", " ", question)
        snippet = text[-2500:] if len(text) > 2500 else text
        return {
            "source_file": name,
            "question": question,
            "code_excerpt": snippet,
        }
    return {"source_file": "", "question": "", "code_excerpt": ""}


def load_lc_code_keys() -> dict[str, Any]:
    """Locally executed code answers (gitignored cache). Instructor branch only."""
    if not LC_CODE_KEYS_PATH.is_file():
        return {}
    try:
        data = json.loads(LC_CODE_KEYS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    keys = data.get("keys")
    return keys if isinstance(keys, dict) else {}


def _merge_local_code_key(
    assignment: dict[str, Any],
    code_ref: dict[str, str],
    local_keys: dict[str, Any],
) -> dict[str, str]:
    akey = assignment.get("key", "")
    local = local_keys.get(akey)
    if not isinstance(local, dict):
        code_ref["answer_source"] = "code_excerpt_only"
        return code_ref
    expected = str(local.get("expected_value", "")).strip()
    if expected:
        code_ref["expected_value"] = expected
        code_ref["answer_source"] = "local_execution"
        if local.get("question"):
            code_ref["question"] = str(local["question"])
        if local.get("source_file"):
            code_ref["source_file"] = str(local["source_file"])
        if local.get("generated_at"):
            code_ref["keys_generated_at"] = str(local["generated_at"])
    else:
        code_ref["answer_source"] = "code_excerpt_only"
    return code_ref


def load_lc_reference(assignment: dict[str, Any]) -> dict[str, Any]:
    lab = _lab_html_path(assignment)
    code = _code_dir(assignment)
    html = lab.read_text(encoding="utf-8", errors="replace") if lab.is_file() else ""
    cards = parse_lc_cards(html)
    code_ref = parse_code_learning_check(code)
    local_keys = load_lc_code_keys()
    code_ref = _merge_local_code_key(assignment, code_ref, local_keys)
    meta: dict[str, Any] = {}
    if LC_CODE_KEYS_PATH.is_file():
        try:
            meta["code_keys_file"] = str(LC_CODE_KEYS_PATH)
            blob = json.loads(LC_CODE_KEYS_PATH.read_text(encoding="utf-8"))
            meta["code_keys_generated_at"] = blob.get("generated_at", "")
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "case_study_key": assignment.get("case_study_key", ""),
        "lab_path": str(lab) if lab.is_file() else "",
        "code_path": str(code) if code.is_dir() else "",
        "learning_checks": cards,
        "code_check": code_ref,
        "website_url": f"https://timothyfraser.com/netsci/{assignment.get('lab_path', '').replace('docs/', '')}",
        "github_code_url": f"https://github.com/timothyfraser/netsci/tree/main/{assignment.get('code_path', '')}",
        **meta,
    }
