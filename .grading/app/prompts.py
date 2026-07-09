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

INSTRUCTOR_CRITIQUE_PRIORITIES = """
Prioritize feedback the instructor actually uses when conferencing with students.
**At least 3 of top_issues MUST address content quality below** (question, results prose,
figures/tables, readability). Rank #1 and #2 should usually be about results prose or
question quality — the main gaps in a data-science report.

1. **Numbers in prose (especially Results) — HIGHEST PRIORITY** — Do results paragraphs
   state numeric findings in sentences (counts, density, centralities, modularity, path lengths,
   etc.)? Flag when numbers appear ONLY in tables/figures with no values repeated in text.
   Say explicitly what is missing (e.g. "no centrality values in Results paragraphs").

2. **Testable scientific question** — Falsifiable with this network and analysis?
   Flag opinion prompts ("Is X important?", "Should we…") with no measurable claim.

3. **Dataset-specific vs generic** — Tied to this client/network, or a slogan any graph could use?

4. **Figures explained** — Referenced by number ("Figure 1…") WITH takeaway for the client?

5. **Tables explained** — Cited in text and interpreted, not orphaned.

6. **Readable analysis vs buzzwords** — Concrete chain (metric → value → meaning for client)?

Quote or paraphrase short evidence from the report; name section/paragraph locations.
"""

HYGIENE_AND_GITHUB_POLICY = """
**GitHub / code — de-prioritize in narrative feedback:**
- Students often submit code as Canvas **attachments**; extracted submission text may omit repo URLs
  and scripts even when work is fine. Do NOT treat missing GitHub in text as a major flaw.
- `github_link`: mark **missing** only if no URL/github.com string appears in submission text;
  use **not_assessable** if the report otherwise looks complete (instructor will check attachments).
  Proposed deduction 0–2 max when only absent from pasted text — never 5.
- `project_script`: almost always **not_assessable** from report/PDF text alone. Do not discuss
  at length in classbot_summary or top_issues.
- **Never** put GitHub, repo URL, or "run project.R" as top_issues rank #1–#2 unless the report
  has zero content problems. At most one brief hygiene note at the bottom of top_issues (rank 4–5).
- classbot_summary must NOT lead with GitHub; lead with results-in-prose and question quality.
"""

# Rubric ids treated as hygiene in Canvas comment display (shown last, never drive top_issues).
HYGIENE_REQUIREMENT_IDS = frozenset({"github_link", "project_script", "min_pages", "min_nodes"})

REPORT_CHECKLIST_LABELS: dict[str, str] = {
    "research_question": "Research question scoped, specific, and testable",
    "dataset_assumptions": "Dataset and assumptions well described",
    "methods_client_language": "Methods in client-ready language (not code jargon)",
    "results_statistics_in_text": "Results with statistics cited in prose",
    "discussion_limitations": "Discussion and limitations at the close",
}

REPORT_CHECKLIST_PROMPT = """
**Structured report checklist (required)** — include exactly these five items in `report_checklist`,
each with `rating` (strong | partial | weak), `evidence` (one sentence), `location`:

1. `research_question` — Scoped to this client/dataset? Specific entities/measures? Falsifiable/testable
   (not opinion: "Is X important?")?
2. `dataset_assumptions` — Nodes, edges, weights, source, and key assumptions stated clearly?
3. `methods_client_language` — Methods explained for a client reader? Flag code-style prose
   (function names, snake_case, package names, "I ran cluster_fast_greedy()") as weak.
4. `results_statistics_in_text` — Results section cites many specific numbers in sentences, not only
   in tables/figures? Count whether prose is thin on statistics.
5. `discussion_limitations` — Closing discusses what findings mean for the client AND limitations
   ("what this tells me / what it doesn't")?

Include `client_ai_likelihood` in JSON for the instructor dashboard (not repeated in student-facing prose elsewhere).
- `rating`: low | medium | high — how likely a **client** would suspect the report prose is AI-generated
  from writing patterns alone (not an accusation; a style signal).
- `rationale`: 1-2 sentences.
- `patterns`: up to 6 short bullets (e.g. "uniform paragraph length", "stock transitions",
  "no typos or informal voice", "generic filler", "list-heavy buzzwords", "over-polished tone").
Use low when voice sounds authentically student/client-specific with concrete details.
"""

DISCLOSURE_HTML = (
    "<em>Processed using Cornell's AI Gateway; No student data retained.</em>"
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
Include top_issues: 2-5 highest-value **content** problems for the instructor with rank, title, description, location, search_hint (EXACTLY three words).
top_issues titles should be plain English (e.g. "Results lack numeric prose", "Question is opinion-based", "Figure 2 never explained").
Do NOT use top_issues for GitHub/repo/script unless all content issues are already met.
Include classbot_summary: 2-4 sentences for the instructor only — **lead with results-in-prose and question quality**, never GitHub or page count.
In classbot_summary, refer to the student as "the student" or "they" — do not use or invent a personal name.
Include confidence: "low", "medium", or "high".

{REPORT_CHECKLIST_PROMPT}

{INSTRUCTOR_CRITIQUE_PRIORITIES}

{HYGIENE_AND_GITHUB_POLICY}

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


def _checklist_rating_emoji(rating: str) -> str:
    return {"strong": "✅", "partial": "⚠️", "weak": "❌"}.get(rating, "❓")


def _ai_likelihood_label(rating: str) -> str:
    return {
        "low": "Low — reads human / client-specific",
        "medium": "Medium — some AI-like polish",
        "high": "High — client may suspect AI prose",
    }.get(rating, rating)


def render_report_checklist_html(
    review: dict[str, Any], *, include_ai_likelihood: bool = False
) -> str:
    items = review.get("report_checklist") or []
    ai = review.get("client_ai_likelihood") or {}
    if not items and not ai:
        return ""

    parts: list[str] = ["<p><strong>📊 Report checklist</strong></p>", "<ul>"]
    order = list(REPORT_CHECKLIST_LABELS.keys())
    by_id = {str(i.get("id")): i for i in items if i.get("id")}
    for cid in order:
        item = by_id.get(cid)
        if not item:
            continue
        label = REPORT_CHECKLIST_LABELS.get(cid, cid)
        rating = item.get("rating", "?")
        emoji = _checklist_rating_emoji(str(rating))
        evidence = html.escape(str(item.get("evidence", "") or ""))
        loc = html.escape(str(item.get("location", "") or ""))
        loc_bit = f" <small>📍 {loc}</small>" if loc else ""
        parts.append(
            f"<li>{emoji} <strong>{html.escape(label)}</strong> "
            f"({html.escape(str(rating))}) — {evidence}{loc_bit}</li>"
        )
    parts.append("</ul>")

    if include_ai_likelihood and ai:
        ai_rating = str(ai.get("rating", "medium"))
        ai_emoji = {"low": "🙂", "medium": "🤔", "high": "🤖"}.get(ai_rating, "🤔")
        rationale = html.escape(str(ai.get("rationale", "") or ""))
        parts.append(
            f"<p><strong>{ai_emoji} Client AI-likelihood</strong> "
            f"({html.escape(_ai_likelihood_label(ai_rating))})<br>{rationale}</p>"
        )
        patterns = ai.get("patterns") or []
        if patterns:
            parts.append("<ul>")
            for p in patterns[:6]:
                parts.append(f"<li><small>{html.escape(str(p))}</small></li>")
            parts.append("</ul>")

    return "\n".join(parts)


def _is_hygiene_top_issue(issue: dict[str, Any]) -> bool:
    hay = " ".join(
        str(issue.get(k, "") or "") for k in ("title", "description", "search_hint")
    ).lower()
    return any(
        token in hay
        for token in (
            "github",
            "repo url",
            "repository",
            "project script",
            "project.r",
            "project.py",
            "project folder",
        )
    )


def _order_top_issues(issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    content = [i for i in issues if not _is_hygiene_top_issue(i)]
    hygiene = [i for i in issues if _is_hygiene_top_issue(i)]
    ordered = content + hygiene[:1]
    out: list[dict[str, Any]] = []
    for rank, issue in enumerate(ordered, start=1):
        item = dict(issue)
        item["rank"] = rank
        out.append(item)
    return out


def build_classbot_comment_html(review: dict[str, Any]) -> str:
    parts: list[str] = []
    parts.append("<p><strong>🤖 Classbot first-pass review</strong></p>")

    summary = (review.get("classbot_summary") or "").strip()
    if summary:
        parts.append(f"<p><strong>📋 Instructor notes</strong><br>{html.escape(summary)}</p>")

    checklist_html = render_report_checklist_html(review)
    if checklist_html:
        parts.append(checklist_html)

    issues = _order_top_issues(list(review.get("top_issues") or []))
    if issues:
        parts.append("<p><strong>🔍 What to review with the student</strong></p><ul>")
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
    content_gaps = [r for r in gaps if r.get("id") not in HYGIENE_REQUIREMENT_IDS]
    hygiene_gaps = [r for r in gaps if r.get("id") in HYGIENE_REQUIREMENT_IDS]
    if content_gaps:
        parts.append("<p><strong>📝 Checklist gaps</strong></p><ul>")
        for r in content_gaps:
            emoji = _status_emoji(r.get("status", ""))
            label = html.escape(r.get("id", ""))
            evidence = html.escape(r.get("evidence", ""))
            ded = r.get("proposed_deduction", 0)
            parts.append(
                f"<li>{emoji} <strong>{label}</strong>: {evidence}"
                f" <em>(−{ded} pts)</em></li>"
            )
        parts.append("</ul>")
    if hygiene_gaps:
        parts.append("<p><strong>📝 Hygiene (optional — check attachments)</strong></p><ul>")
        for r in hygiene_gaps:
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

    if classbot:
        if classbot.lstrip().startswith("<"):
            parts.append(classbot)
        else:
            parts.append(_text_to_html(classbot))
    else:
        parts.append("<p><em>🤖 No Classbot block for this submission.</em></p>")

    parts.append(f"<p>{DISCLOSURE_HTML}</p>")
    return "\n".join(parts)


def compose_canvas_comment_plain_preview(instructor_comment: str, classbot_comment: str) -> str:
    """Plain-text fallback for modal preview."""
    plain = re.sub(r"<[^>]+>", "", compose_canvas_comment(instructor_comment, classbot_comment))
    plain = html.unescape(plain)
    return re.sub(r"\n{3,}", "\n\n", plain).strip()
