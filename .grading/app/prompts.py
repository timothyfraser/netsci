"""Classbot system prompt and comment composer."""

from __future__ import annotations

import html
import json
import re
from typing import Any

from rubric import load_rubric

GLOSSARY_DISCIPLINE = """
Use SYSEN 5470 network-science vocabulary precisely:
- Name the question each metric answers (never say "most central" without the measure).
- Do not treat community detection output as ground truth.
- Prefer configuration-model nulls over Erdős–Rényi when discussing significance.
- Distinguish node embeddings from predictions.
- Sampling strategy must match the inference claim.
"""

DISCLOSURE_HTML = (
    "<em>Processed through Cornell's AI API Gateway (CIT AI Program), approved for "
    "moderate-risk/FERPA educational data. Chat Completions API: prompts and "
    "completions are not stored by the gateway or model providers.</em>"
)


def build_system_prompt() -> str:
    rubric = load_rubric()
    target = rubric.get("target_fine_report_score", 85)
    req_lines = "\n".join(
        f"- {r['id']}: {r['label']} (max deduction {r['max_deduction']})"
        for r in rubric["requirements"]
    )
    return f"""You are Classbot, a grading assistant for SYSEN 5470 project case study reports.
Review the student submission against each requirement. Return ONLY valid JSON matching the schema.

Requirements to assess (self-grade checklist — use these ids exactly):
{req_lines}

Scoring anchor: a fine-but-not-great report that meets most requirements with minor gaps
should land around {target}/100 total (~{100 - target} points in accepted deductions).
Reserve scores below 75 for multiple missing core elements. Scores above 92 need clear excellence.

Status values: "met", "partial", "missing", "not_assessable"
Use "not_assessable" for project_script when the report/Canvas text does not let you verify code runs.
For each requirement include: id, status, evidence, location, proposed_deduction (0 if met), search_hint (EXACTLY three words).
Include top_issues: 2-5 highest-value problems with rank, title, description, location, search_hint (EXACTLY three words).
Include classbot_summary: 2-4 sentences for the instructor.
Include confidence: "low", "medium", or "high".

{GLOSSARY_DISCIPLINE}

Be specific about WHERE in the report each issue appears. Proposed deductions must not exceed each requirement's max.
"""


def build_user_prompt(
    report_text: str,
    metadata: dict[str, Any],
) -> str:
    meta = json.dumps(metadata, indent=2)
    return f"""Submission metadata:
{meta}

Report text (may include Canvas submission body + extracted PDF):
---
{report_text[:120000]}
---
"""


def _text_to_html(text: str) -> str:
    text = text.strip()
    if not text:
        return ""
    escaped = html.escape(text)
    return "<p>" + escaped.replace("\n\n", "</p><p>").replace("\n", "<br>") + "</p>"


def _status_emoji(status: str) -> str:
    return {
        "met": "✅",
        "partial": "⚠️",
        "missing": "❌",
        "not_assessable": "➖",
    }.get(status, "❓")


def build_classbot_comment_html(review: dict[str, Any]) -> str:
    parts: list[str] = []
    parts.append("<p><strong>🤖 Classbot first-pass review</strong></p>")

    summary = (review.get("classbot_summary") or "").strip()
    if summary:
        parts.append(f"<p><strong>📋 Summary</strong><br>{html.escape(summary)}</p>")

    issues = review.get("top_issues") or []
    if issues:
        parts.append("<p><strong>🔍 Top issues</strong></p><ul>")
        for issue in sorted(issues, key=lambda x: x.get("rank", 99)):
            rank = issue.get("rank", "?")
            title = html.escape(issue.get("title", "Issue"))
            desc = html.escape(issue.get("description", issue.get("desc", "")))
            loc = html.escape(issue.get("location", ""))
            hint = html.escape(issue.get("search_hint", ""))
            parts.append(
                f"<li><strong>#{rank} {title}</strong> — {desc}"
                f"<br><small>📍 {loc} · 🔎 {hint}</small></li>"
            )
        parts.append("</ul>")

    reqs = review.get("requirements") or []
    gaps = [r for r in reqs if r.get("status") in ("partial", "missing")]
    if gaps:
        parts.append("<p><strong>📝 Checklist gaps</strong></p><ul>")
        for r in gaps:
            emoji = _status_emoji(r.get("status", ""))
            label = html.escape(r.get("id", ""))
            evidence = html.escape(r.get("evidence", ""))
            ded = r.get("proposed_deduction", 0)
            parts.append(
                f"<li>{emoji} <strong>{label}</strong>: {evidence}"
                f" <em>(−{ded} pts)</em></li>"
            )
        parts.append("</ul>")

    met = [r for r in reqs if r.get("status") == "met"]
    if met:
        met_ids = ", ".join(html.escape(r.get("id", "")) for r in met)
        parts.append(f"<p><strong>✅ Met</strong> {met_ids}</p>")

    na = [r for r in reqs if r.get("status") == "not_assessable"]
    if na:
        na_ids = ", ".join(html.escape(r.get("id", "")) for r in na)
        parts.append(f"<p><strong>➖ Not assessable from report</strong> {na_ids}</p>")

    confidence = review.get("confidence", "medium")
    conf_emoji = {"high": "💪", "medium": "👍", "low": "🤔"}.get(confidence, "👍")
    parts.append(
        f"<p><small>{conf_emoji} Classbot confidence: {html.escape(confidence)}</small></p>"
    )
    return "\n".join(parts)


def build_classbot_comment_from_review(review: dict[str, Any]) -> str:
    """Return HTML comment block for Canvas."""
    return build_classbot_comment_html(review)


def compose_canvas_comment(instructor_comment: str, classbot_comment: str) -> str:
    parts: list[str] = []
    instructor = (instructor_comment or "").strip()
    classbot = (classbot_comment or "").strip()

    if instructor:
        parts.append("<p><strong>✏️ Instructor comments</strong></p>")
        parts.append(_text_to_html(instructor))

    parts.append("<hr>")
    parts.append("<p><strong>🎓 SYSEN 5470 project feedback</strong></p>")
    parts.append(f"<p>{DISCLOSURE_HTML}</p>")

    if classbot:
        if classbot.lstrip().startswith("<"):
            parts.append(classbot)
        else:
            parts.append(_text_to_html(classbot))
    else:
        parts.append("<p><em>🤖 No Classbot block for this submission.</em></p>")

    return "\n".join(parts)


def compose_canvas_comment_plain_preview(instructor_comment: str, classbot_comment: str) -> str:
    """Plain-text fallback for modal preview."""
    plain = re.sub(r"<[^>]+>", "", compose_canvas_comment(instructor_comment, classbot_comment))
    plain = html.unescape(plain)
    return re.sub(r"\n{3,}", "\n\n", plain).strip()
