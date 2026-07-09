"""Load authoritative LC answer keys from course website + teaching code."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from env import GRADING_ROOT

REPO_ROOT = GRADING_ROOT.parent
LC_CODE_KEYS_PATH = GRADING_ROOT / "cache" / "lc_code_keys.json"
LC_ANSWER_KEYS_PATH = GRADING_ROOT / "cache" / "lc_answer_keys.json"


def _lab_html_path(assignment: dict[str, Any]) -> Path:
    rel = assignment.get("lab_path") or ""
    return REPO_ROOT / rel.replace("/", "\\") if rel else Path()


def _code_dir(assignment: dict[str, Any]) -> Path:
    rel = assignment.get("code_path") or ""
    return REPO_ROOT / rel.replace("/", "\\") if rel else Path()


def _strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _lc_id_from_label(label: str) -> str:
    num = re.search(r"\d+", label)
    return f"lc{int(num.group()):02d}" if num else label.replace(" ", "").lower()


LC_CARD_SPLIT = re.compile(r'<div class="lc-card"[^>]*>', re.IGNORECASE)


def _find_lc_label(block: str) -> str | None:
    match = re.search(r'class="lc-number">(LC\s*\d+)', block, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r'class="lc-badge">(LC\s*\d+)', block, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def _find_lc_question(block: str) -> str:
    for pattern in (
        r'<div class="lc-question"[^>]*>(.*?)</div>',
        r'<h3 class="lc-question">(.*?)</h3>',
        r'<p class="lc-question">(.*?)</p>',
        r'<p class="lc-prompt">(.*?)</p>',
    ):
        match = re.search(pattern, block, re.DOTALL | re.IGNORECASE)
        if match:
            return _strip_html(match.group(1))[:400]
    return ""


def _letter_from_select_option(block: str) -> str:
    match = re.search(
        r"selectOption\s*\(\s*\d+\s*,\s*['\"]([A-D])['\"]\s*,\s*true\s*\)",
        block,
        re.IGNORECASE,
    )
    return match.group(1).upper() if match else ""


def _letter_from_feedback(text: str) -> str:
    for pattern in (
        r"(?:Answer|Correct):\s*([A-D])\b",
        r"\b([A-D])\s+is\s+correct\b",
        r"^([A-D])\s*[—\-]",
    ):
        match = re.search(pattern, _strip_html(text), re.IGNORECASE)
        if match:
            return match.group(1).upper()
    for pattern in (
        r"<strong>\s*(?:Answer|Correct):\s*([A-D])\b",
        r"<strong>\s*([A-D])\s+is\s+correct\b",
        r"<strong>\s*([A-D])\s*[—\-]",
    ):
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).upper()
    return ""


def _find_answer_letter(block: str) -> str:
    letter = _letter_from_select_option(block)
    if letter:
        return letter
    for match in re.finditer(
        r'class="[^"]*(?:feedback-answer|answer-box|lc-answer)[^"]*"[^>]*>(.*?)</div>',
        block,
        re.DOTALL | re.IGNORECASE,
    ):
        letter = _letter_from_feedback(match.group(1))
        if letter:
            return letter
    return _letter_from_feedback(block)


def _parse_lc_correct_map(html: str) -> dict[int, str]:
    out: dict[int, str] = {}
    match = re.search(r"const\s+lcCorrect\s*=\s*\{([^}]+)\}", html)
    if not match:
        return out
    for num_s, letter, num in re.findall(
        r'(\d+):\s*(?:"([A-D])"|(\d+))',
        match.group(1),
        re.IGNORECASE,
    ):
        out[int(num_s)] = letter.upper() if letter else num
    return out


def _parse_correct_answers_map(html: str) -> dict[int, str]:
    out: dict[int, str] = {}
    match = re.search(r"const\s+CORRECT_ANSWERS\s*=\s*\{([^}]+)\}", html)
    if not match:
        return out
    for num_s, letter in re.findall(r"(\d+):\s*\"([A-D])\"", match.group(1), re.IGNORECASE):
        out[int(num_s)] = letter.upper()
    return out


def _parse_lc_content_questions(html: str) -> dict[int, str]:
    """Joins lab: LC 03 question lives only in LC_CONTENT JS."""
    out: dict[int, str] = {}
    for num_s, body in re.findall(
        r"(\d+):\s*\{\s*question:\s*\{\s*r:\s*`([\s\S]*?)`",
        html,
    ):
        out[int(num_s)] = _strip_html(body.replace("\\n", " "))[:500]
    return out


def _answer_rationale(block: str) -> str:
    for match in re.finditer(
        r'class="[^"]*(?:feedback-answer|answer-box|lc-answer)[^"]*"[^>]*>(.*?)</div>',
        block,
        re.DOTALL | re.IGNORECASE,
    ):
        text = _strip_html(match.group(1))
        if text:
            return text[:500]
    return ""


def _card(
    *,
    label: str,
    question: str,
    answer_kind: str,
    correct_letter: str = "",
    correct_value: str = "",
    answer_rationale: str = "",
) -> dict[str, str]:
    return {
        "id": _lc_id_from_label(label),
        "label": label,
        "question": question,
        "answer_kind": answer_kind,
        "correct_letter": correct_letter,
        "correct_value": correct_value,
        "answer_rationale": answer_rationale,
    }


def parse_joins_lc_cards(html: str) -> list[dict[str, str]]:
    """Joins lab stores numeric LC answers in lcCorrect and MC in LC_CONTENT."""
    lc_correct = _parse_lc_correct_map(html)
    js_questions = _parse_lc_content_questions(html)
    cards: list[dict[str, str]] = []
    for block in LC_CARD_SPLIT.split(html)[1:]:
        label = _find_lc_label(block)
        if not label:
            continue
        lc_num = int(re.search(r"\d+", label).group())
        question = _find_lc_question(block) or js_questions.get(lc_num, "")
        rationale = _answer_rationale(block)
        correct = lc_correct.get(lc_num, "")
        if lc_num <= 2:
            cards.append(
                _card(
                    label=label,
                    question=question,
                    answer_kind="numeric",
                    correct_value=str(correct),
                    answer_rationale=rationale,
                )
            )
        else:
            letter = str(correct).upper() if correct else _find_answer_letter(block)
            cards.append(
                _card(
                    label=label,
                    question=question,
                    answer_kind="letter",
                    correct_letter=letter,
                    answer_rationale=rationale,
                )
            )
    return cards


def parse_dsm_lc_cards(html: str) -> list[dict[str, str]]:
    correct_map = _parse_correct_answers_map(html)
    cards: list[dict[str, str]] = []
    for block in LC_CARD_SPLIT.split(html)[1:]:
        label = _find_lc_label(block)
        if not label:
            continue
        lc_num = int(re.search(r"\d+", label).group())
        letter = correct_map.get(lc_num) or _find_answer_letter(block)
        if not letter:
            continue
        cards.append(
            _card(
                label=label,
                question=_find_lc_question(block),
                answer_kind="letter",
                correct_letter=letter,
                answer_rationale=_answer_rationale(block),
            )
        )
    return cards


def parse_lc_cards(html: str) -> list[dict[str, str]]:
    """Extract LC number, question snippet, and correct answer from lab HTML."""
    if "const LC_CONTENT" in html and "const lcCorrect" in html:
        return parse_joins_lc_cards(html)
    if "const CORRECT_ANSWERS" in html:
        return parse_dsm_lc_cards(html)

    cards: list[dict[str, str]] = []
    for block in LC_CARD_SPLIT.split(html)[1:]:
        label = _find_lc_label(block)
        if not label:
            continue
        letter = _find_answer_letter(block)
        if not letter:
            continue
        cards.append(
            _card(
                label=label,
                question=_find_lc_question(block),
                answer_kind="letter",
                correct_letter=letter,
                answer_rationale=_answer_rationale(block),
            )
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


def load_lc_answer_keys() -> dict[str, Any]:
    """Full LC answer keys (gitignored). Built by scripts/build_lc_answer_keys.py."""
    if not LC_ANSWER_KEYS_PATH.is_file():
        return {}
    try:
        data = json.loads(LC_ANSWER_KEYS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    assignments = data.get("assignments")
    return assignments if isinstance(assignments, dict) else {}


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


def build_lc_reference(assignment: dict[str, Any]) -> dict[str, Any]:
    """Parse case-study HTML + code folder into authoritative LC reference."""
    lab = _lab_html_path(assignment)
    code = _code_dir(assignment)
    html = lab.read_text(encoding="utf-8", errors="replace") if lab.is_file() else ""
    cards = parse_lc_cards(html)
    code_ref = parse_code_learning_check(code)
    code_ref = _merge_local_code_key(assignment, code_ref, load_lc_code_keys())
    return {
        "assignment_key": assignment.get("key", ""),
        "case_study_key": assignment.get("case_study_key", ""),
        "lab_path": str(lab) if lab.is_file() else "",
        "code_path": str(code) if code.is_dir() else "",
        "learning_checks": cards,
        "code_check": code_ref,
        "website_url": f"https://timothyfraser.com/netsci/{assignment.get('lab_path', '').replace('docs/', '')}",
        "github_code_url": f"https://github.com/timothyfraser/netsci/tree/main/{assignment.get('code_path', '')}",
    }


def validate_lc_reference(ref: dict[str, Any]) -> list[str]:
    """Return validation errors for a built reference."""
    errors: list[str] = []
    akey = ref.get("assignment_key", "?")
    cards = ref.get("learning_checks") or []
    if not cards:
        errors.append(f"{akey}: no learning_checks parsed")
        return errors
    for card in cards:
        cid = card.get("id", "?")
        if not (card.get("question") or "").strip():
            errors.append(f"{akey}/{cid}: missing question")
        kind = card.get("answer_kind", "letter")
        if kind == "numeric" and not str(card.get("correct_value", "")).strip():
            errors.append(f"{akey}/{cid}: missing correct_value")
        if kind == "letter" and not str(card.get("correct_letter", "")).strip():
            errors.append(f"{akey}/{cid}: missing correct_letter")
    return errors


def load_lc_reference(assignment: dict[str, Any]) -> dict[str, Any]:
    """Load LC reference: prefer gitignored lc_answer_keys.json, else live parse."""
    akey = assignment.get("key", "")
    cached = load_lc_answer_keys().get(akey)
    if cached:
        ref = dict(cached)
    else:
        ref = build_lc_reference(assignment)

    # Always refresh code_check from lc_code_keys (may be regenerated without full rebuild).
    code = _code_dir(assignment)
    code_ref = parse_code_learning_check(code)
    code_ref = _merge_local_code_key(assignment, code_ref, load_lc_code_keys())
    ref["code_check"] = code_ref

    meta: dict[str, Any] = {"answer_key_source": "cache" if cached else "live_parse"}
    if LC_ANSWER_KEYS_PATH.is_file():
        try:
            blob = json.loads(LC_ANSWER_KEYS_PATH.read_text(encoding="utf-8"))
            meta["answer_keys_generated_at"] = blob.get("generated_at", "")
            meta["answer_keys_file"] = str(LC_ANSWER_KEYS_PATH)
        except (json.JSONDecodeError, OSError):
            pass
    if LC_CODE_KEYS_PATH.is_file():
        try:
            meta["code_keys_file"] = str(LC_CODE_KEYS_PATH)
            blob = json.loads(LC_CODE_KEYS_PATH.read_text(encoding="utf-8"))
            meta["code_keys_generated_at"] = blob.get("generated_at", "")
        except (json.JSONDecodeError, OSError):
            pass
    ref.update(meta)
    return ref
