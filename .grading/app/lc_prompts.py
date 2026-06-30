"""Prompts and HTML comments for learning-check (completion) grading."""

from __future__ import annotations

import html
import json
from typing import Any

from prompts import DISCLOSURE_HTML, GLOSSARY_DISCIPLINE


def build_lc_system_prompt() -> str:
    return f"""You are Classbot, grading SYSEN 5470 Learning Check submissions (completion, 1 point).
Students paste in Canvas text entry: LC1/LC2/LC3 letter choices plus the numeric answer printed by running the lab code.

Return ONLY valid JSON:
{{
  "checks": [
    {{
      "id": "lc01",
      "label": "LC 01",
      "student_answer": "B",
      "correct_answer": "B",
      "verdict": "correct" | "incorrect" | "missing" | "unclear",
      "feedback": "short emoji-friendly note for instructor"
    }}
  ],
  "code_answer": {{
    "student_value": "what they submitted",
    "expected_summary": "what the code should print (from reference)",
    "verdict": "correct" | "incorrect" | "missing" | "unclear",
    "feedback": "short note"
  }},
  "format_ok": true,
  "proposed_grade": "1" or "0",
  "classbot_summary": "2-3 sentences for instructor (use student_first_name from metadata — never last name alone)",
  "confidence": "low" | "medium" | "high"
}}

Grading policy (completion):
- Default proposed_grade "1" if they attempted all parts and most answers are correct or close.
- Use "0" only when multiple LC letters are wrong, code answer is clearly wrong/missing, or submission is empty/gibberish.
- For a single wrong LC letter, still grade "1" but explain the mistake briefly in feedback.
- Use emojis in feedback fields (👍 ✅ ⚠️ ❌ 💡 📎).
- Be generous on formatting (LC1 vs LC 01 vs lc1: B).
- In classbot_summary, use the student's first name only (never last name alone or shouting).
- For code_answer: when reference.code_check.expected_value is present (answer_source local_execution),
  treat it as the authoritative expected answer; compare student_value against it (allow minor formatting).

{GLOSSARY_DISCIPLINE}
"""


def build_lc_user_prompt(
    submission_text: str,
    reference: dict[str, Any],
    metadata: dict[str, Any],
) -> str:
    return f"""Assignment metadata:
{json.dumps(metadata, indent=2)}

Authoritative answer key (from course website + code folder):
{json.dumps(reference, indent=2)}

Student Canvas text submission:
---
{submission_text[:8000]}
---
"""


def _verdict_emoji(verdict: str) -> str:
    return {
        "correct": "✅",
        "incorrect": "❌",
        "missing": "📭",
        "unclear": "❓",
    }.get(verdict, "•")


def build_lc_comment_html(review: dict[str, Any]) -> str:
    parts: list[str] = [
        "<p><strong>📝 Learning Check review</strong></p>",
    ]
    summary = (review.get("classbot_summary") or "").strip()
    if summary:
        parts.append(f"<p>{html.escape(summary)}</p>")

    checks = review.get("checks") or []
    if checks:
        parts.append("<p><strong>🔍 Multiple choice</strong></p><ul>")
        for chk in checks:
            emoji = _verdict_emoji(chk.get("verdict", ""))
            label = html.escape(chk.get("label", chk.get("id", "LC")))
            student = html.escape(str(chk.get("student_answer", "—")))
            correct = html.escape(str(chk.get("correct_answer", "—")))
            fb = html.escape(chk.get("feedback", ""))
            parts.append(
                f"<li>{emoji} <strong>{label}</strong>: submitted <em>{student}</em> "
                f"(key <em>{correct}</em>) — {fb}</li>"
            )
        parts.append("</ul>")

    code = review.get("code_answer") or {}
    if code:
        emoji = _verdict_emoji(code.get("verdict", ""))
        parts.append("<p><strong>⌨️ I ran the code</strong></p>")
        parts.append(
            f"<p>{emoji} Student: <em>{html.escape(str(code.get('student_value', '—')))}</em> — "
            f"{html.escape(code.get('feedback', ''))}</p>"
        )

    conf = review.get("confidence", "medium")
    parts.append(f"<p><small>🤖 Classbot confidence: {html.escape(conf)}</small></p>")
    return "\n".join(parts)


def compose_lc_canvas_comment(instructor_comment: str, classbot_comment: str) -> str:
    from prompts import _text_to_html

    parts: list[str] = []
    instructor = (instructor_comment or "").strip()
    classbot = (classbot_comment or "").strip()

    if instructor:
        parts.append("<p><strong>✏️ Instructor comments</strong></p>")
        parts.append(_text_to_html(instructor))

    parts.append("<hr>")
    parts.append("<p><strong>📚 Learning Check feedback</strong></p>")
    if classbot.lstrip().startswith("<"):
        parts.append(classbot)
    else:
        parts.append(_text_to_html(classbot))
    parts.append(f"<p>{DISCLOSURE_HTML}</p>")
    return "\n".join(parts)
