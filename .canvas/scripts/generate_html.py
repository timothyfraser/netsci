#!/usr/bin/env python3
"""
generate_html.py — SYSEN 5470 Canvas content generator.

Reads manifest.json (the single source of truth) and writes:

  pages/home.html                 Canvas front-page body (HTML fragment)
  assignments/<key>.html          one HTML fragment per Canvas assignment (43)
  canvas_plan.json                fully-expanded, machine-readable plan that
                                  push_to_canvas.py consumes
  preview.html                    one self-contained gallery so a human can
                                  eyeball every page + assignment in a browser

WHY FRAGMENTS, NOT FULL PAGES?
  Canvas stores page/assignment bodies as sanitized HTML and renders them
  INSIDE its own <html><head><body>. It strips <head>, <style>, <link>,
  <script>, and most class-based styling. So every value here is an INLINE
  style attribute with a literal color (no CSS variables). The whole body is
  wrapped in one dark "stage" <div> so the neon theme reads on Canvas's white
  content area.

Pure standard library. Run:  python3 scripts/generate_html.py
"""

import json
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
M = json.loads((ROOT / "manifest.json").read_text())

T = M["theme"]
SITE = M["course"]["site_base"].rstrip("/") + "/"


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------
def url(path_or_full: str) -> str:
    """Resolve a manifest path (relative to the site) or pass through a full URL."""
    if path_or_full.startswith("http"):
        return path_or_full
    return SITE + path_or_full.lstrip("/")


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def font(kind: str) -> str:
    return T[f"font_{kind}"]


# ---------------------------------------------------------------------------
# reusable component builders (all inline styles, Canvas-sanitizer-safe)
# ---------------------------------------------------------------------------
def stage(inner: str) -> str:
    """Outer dark panel that recreates the site look on Canvas' white page."""
    return (
        f'<div style="background:{T["black"]};'
        f'background-image:radial-gradient(circle at 18% 0%, rgba(22,101,52,0.35) 0%, rgba(5,10,5,0) 55%);'
        f'border:1px solid {T["border"]};border-radius:16px;'
        f'padding:34px 36px;margin:0;'
        f'font-family:{font("body")};color:{T["mint"]};'
        f'font-size:15px;line-height:1.65;">'
        f"{inner}"
        f"</div>"
    )


def kicker(text: str) -> str:
    return (
        f'<div style="font-family:{font("mono")};font-size:11px;font-weight:700;'
        f'letter-spacing:0.18em;text-transform:uppercase;color:{T["green_bright"]};'
        f'margin:0 0 10px;">{esc(text)}</div>'
    )


def title(text: str) -> str:
    return (
        f'<div style="font-family:{font("display")};font-size:40px;line-height:1.02;'
        f'letter-spacing:0.02em;color:{T["white"]};margin:0 0 12px;">{esc(text)}</div>'
    )


def case_line(label: str, value: str) -> str:
    return (
        f'<div style="font-size:15px;color:{T["mint2"]};margin:0 0 16px;">'
        f'<span style="font-family:{font("mono")};font-size:11px;letter-spacing:0.12em;'
        f'text-transform:uppercase;color:{T["grey"]};margin-right:8px;">{esc(label)}</span>'
        f'<span style="color:{T["white"]};font-weight:600;">{value}</span></div>'
    )


def grading_pill(mode: str, points=None) -> str:
    """mode: 'completion' (green) or 'points' (amber)."""
    if mode == "completion":
        col, txt = T["green_bright"], "Graded · Completion (complete / not complete)"
        bg = "rgba(57,255,20,0.10)"
    else:
        col, txt = T["amber"], f"Graded · {points} Points"
        bg = "rgba(251,191,36,0.10)"
    return (
        f'<span style="display:inline-block;font-family:{font("mono")};font-size:11px;'
        f'font-weight:700;letter-spacing:0.10em;text-transform:uppercase;color:{col};'
        f'background:{bg};border:1px solid {col};border-radius:100px;'
        f'padding:6px 14px;margin:0 0 4px;">{esc(txt)}</span>'
    )


def paragraph(htmltext: str) -> str:
    return (
        f'<p style="font-size:15px;line-height:1.65;color:{T["mint"]};'
        f'margin:18px 0;padding-left:14px;border-left:2px solid {T["green_bright"]};">'
        f"{htmltext}</p>"
    )


def button(href: str, label: str, primary=True) -> str:
    if primary:
        style = (
            f'display:inline-block;background:{T["green_bright"]};color:{T["black"]};'
            f'border:1px solid {T["green_bright"]};'
        )
    else:
        style = (
            f'display:inline-block;background:transparent;color:{T["green_bright"]};'
            f'border:1px solid {T["green_bright"]};'
        )
    return (
        f'<a href="{esc(href)}" target="_blank" rel="noopener" '
        f'style="{style}font-family:{font("mono")};font-weight:700;font-size:13px;'
        f'letter-spacing:0.08em;text-transform:uppercase;text-decoration:none;'
        f'padding:13px 22px;border-radius:8px;margin:6px 10px 6px 0;">{esc(label)}</a>'
    )


def footer_note() -> str:
    return (
        f'<p style="font-family:{font("mono")};font-size:11px;letter-spacing:0.04em;'
        f'color:{T["grey_dim"]};margin:22px 0 0;border-top:1px solid {T["border_soft"]};'
        f'padding-top:14px;">↳ This card is a shortcut. <strong style="color:'
        f'{T["mint2"]};">See the course website for the complete, authoritative '
        f'assignment details.</strong></p>'
    )


def card(kick, ttl, lines, pill, body_html, buttons):
    inner = kicker(kick) + title(ttl)
    for lbl, val in lines:
        inner += case_line(lbl, val)
    inner += pill
    inner += paragraph(body_html)
    inner += '<div style="margin:18px 0 0;">' + "".join(buttons) + "</div>"
    inner += footer_note()
    return stage(inner)


# ---------------------------------------------------------------------------
# homepage
# ---------------------------------------------------------------------------
def build_home():
    cs = M["course"]
    inner = kicker(f'{cs["code"]} · {cs["term"]}')
    inner += title("Welcome — Start on the Course Website")
    inner += (
        f'<p style="font-size:16px;line-height:1.7;color:{T["mint"]};margin:0 0 8px;">'
        f'This Canvas space exists to <strong style="color:{T["white"]};">organize your '
        f'submissions and deadlines</strong>. Almost everything you actually <em>do</em> '
        f'— the labs, the readings, the sketches, the playground — lives on the '
        f'<strong style="color:{T["white"]};">course website</strong>, which is built '
        f'for exactly this. Use the shortcuts below to jump straight there.</p>'
    )
    inner += (
        f'<div style="margin:18px 0 26px;">'
        + button(url("index.html"), "Open the Course Website →")
        + button(url("assignments.html"), "Assignments & Rubric", primary=False)
        + "</div>"
    )

    for block in M["home_shortcuts"]:
        inner += (
            f'<div style="font-family:{font("mono")};font-size:12px;font-weight:700;'
            f'letter-spacing:0.16em;text-transform:uppercase;color:{T["green_bright"]};'
            f'margin:26px 0 12px;border-bottom:1px solid {T["border_soft"]};'
            f'padding-bottom:8px;">{esc(block["section"])}</div>'
        )
        for ln in block["links"]:
            href = url(ln["url"]) if "url" in ln else url(ln["path"])
            inner += (
                f'<a href="{esc(href)}" target="_blank" rel="noopener" '
                f'style="display:inline-block;vertical-align:top;width:300px;'
                f'min-height:96px;box-sizing:border-box;'
                f'background:{T["card_bg"]};border:1px solid {T["border"]};'
                f'border-radius:12px;padding:16px 18px;margin:0 12px 12px 0;'
                f'text-decoration:none;">'
                f'<div style="font-family:{font("body")};font-size:17px;font-weight:600;'
                f'color:{T["white"]};margin:0 0 6px;">{ln["icon"]}&nbsp;&nbsp;'
                f'<span style="border-bottom:1px solid {T["green_bright"]};">'
                f'{esc(ln["label"])}</span></div>'
                f'<div style="font-family:{font("body")};font-size:13px;line-height:1.5;'
                f'color:{T["mint2"]};">{esc(ln["desc"])}</div></a>'
            )

    inner += (
        f'<p style="font-family:{font("mono")};font-size:11px;color:{T["grey_dim"]};'
        f'margin:26px 0 0;border-top:1px solid {T["border_soft"]};padding-top:14px;">'
        f'{esc(cs["code"])} · {esc(cs["title"])} · Cornell Engineering · '
        f'{esc(cs["term"])} · tmf77@cornell.edu</p>'
    )
    return stage(inner)


# ---------------------------------------------------------------------------
# assignment expansion
# ---------------------------------------------------------------------------
def build_assignments():
    out = []  # list of dicts: {key, name, group, grading, points, submission_types, due, html}

    due = M["due_dates"]
    week_due = {1: due["week1"], 2: due["week2"], 3: due["week3"]}

    for c in M["case_studies"]:
        wk = c["week"]
        cs_label = f'{c["icon"]} {esc(c["name"])}'
        lab = url(c["lab"])
        code = url(c["code"] + "#readme")
        sketch = url(c["sketch_anchor"])

        # ---- Drawing (group: drawings) ----
        body = (
            f'Complete the sketchpad activity that pairs with this case study — '
            f'<strong style="color:{T["white"]};">{esc(c["sketch_title"])}</strong>. '
            f'Draw it by hand (no keyboard), photograph the finished sketch, and upload '
            f'the photo here. We grade whether the sketch shows you understood the '
            f'structure before you wrote any code — not artistic quality.'
        )
        out.append({
            "key": f'drawing-{c["key"]}',
            "name": f'Drawing — {c["short"]}',
            "group": "drawings",
            "grading": "completion", "points": 10,
            "submission_types": ["online_upload"],
            "due": week_due[wk],
            "html": card("Drawing Submission", f'Drawing · {c["short"]}',
                         [("Case study", cs_label), ("Week", f"Week {wk}")],
                         grading_pill("completion"), body,
                         [button(sketch, "Open the Sketchpad →"),
                          button(lab, "View the Lab", primary=False)]),
        })

        # ---- Code Learning Check — "I ran the code" (group: completion) ----
        body = (
            f'Run <code style="color:{T["green_laser"]};">example.R</code> or '
            f'<code style="color:{T["green_laser"]};">example.py</code> in this case '
            f'study’s code folder on GitHub. Each script prints a single numeric '
            f'(or string) answer at the very bottom — <strong style="color:{T["white"]};">'
            f'paste that answer here</strong>. Pick either track (R or Python); you do '
            f'not need to do both.'
        )
        out.append({
            "key": f'code-lc-{c["key"]}',
            "name": f'Code Learning Check (I Ran the Code) — {c["short"]}',
            "group": "completion",
            "grading": "completion", "points": 10,
            "submission_types": ["online_text_entry"],
            "due": week_due[wk],
            "html": card("Code Learning Check · I Ran the Code",
                         f'Code Check · {c["short"]}',
                         [("Case study", cs_label), ("Week", f"Week {wk}")],
                         grading_pill("completion"), body,
                         [button(code, "Open the Code Folder →"),
                          button(lab, "View the Lab", primary=False)]),
        })

        # ---- Case Study Learning Check (group: completion) ----
        body = (
            f'Work through the interactive lab for this case study on the course '
            f'website, then submit your in-lab <strong style="color:{T["white"]};">'
            f'Learning Check</strong> answer here. One Learning Check per case study.'
        )
        out.append({
            "key": f'cs-lc-{c["key"]}',
            "name": f'Case Study Learning Check — {c["short"]}',
            "group": "completion",
            "grading": "completion", "points": 10,
            "submission_types": ["online_text_entry"],
            "due": week_due[wk],
            "html": card("Case Study Learning Check",
                         f'Learning Check · {c["short"]}',
                         [("Case study", cs_label), ("Week", f"Week {wk}")],
                         grading_pill("completion"), body,
                         [button(lab, "Open the Lab →")]),
        })

    # ---- Ed Discussion, one per week (group: completion) ----
    for w in M["extras"]["ed_discussion_weeks"]:
        body = (
            f'Post your weekly reflection and discussion contribution on '
            f'<strong style="color:{T["white"]};">Ed Discussion</strong> (linked in the '
            f'Canvas left-hand navigation). One substantive post per week — react to a '
            f'classmate where you can. Week 3 also includes a short course-level '
            f'retrospective.'
        )
        out.append({
            "key": f"ed-week-{w}",
            "name": f"Ed Discussion — Week {w}",
            "group": "completion",
            "grading": "completion", "points": 10,
            "submission_types": ["none"],
            "due": week_due[w],
            "html": card("Ed Discussion", f"Ed Discussion · Week {w}",
                         [("Cadence", f"Week {w} · due Monday 9:00 AM")],
                         grading_pill("completion"), body,
                         [button(url("calendar.html"), "See the Week on the Calendar →")]),
        })

    # ---- Office Hours, one per week (group: completion) ----
    for w in M["extras"]["office_hours_weeks"]:
        body = (
            f'Attend one virtual office-hour session this week — '
            f'<strong style="color:{T["white"]};">three are required across the '
            f'course</strong>. They are informal: bring a question, a stuck spot, or a '
            f'project idea. Book a slot on the course website; we mark this complete '
            f'after we meet.'
        )
        out.append({
            "key": f"office-week-{w}",
            "name": f"Office Hours — Week {w}",
            "group": "completion",
            "grading": "completion", "points": 10,
            "submission_types": ["none"],
            "due": week_due[w],
            "html": card("Office Hours", f"Office Hours · Week {w}",
                         [("Cadence", f"Week {w} · one of three required")],
                         grading_pill("completion"), body,
                         [button(url("help/office-hours.html"), "Book Office Hours →")]),
        })

    # ---- Projects, one per weekly-homework group ----
    for p in M["extras"]["projects"]:
        body = (
            f'Your weekly homework <em>is</em> the project. Pick one of the eleven '
            f'case-study methods, apply it to a network <strong style="color:'
            f'{T["white"]};">you</strong> chose (≥ 100 nodes; 1,000+ strongly '
            f'preferred), and write a 2-page-minimum report in your own words. Submit '
            f'(a) your <code style="color:{T["green_laser"]};">project.R</code> / '
            f'<code style="color:{T["green_laser"]};">project.py</code> and (b) the '
            f'report (PDF preferred). The full spec, the four-skill rubric, the hard '
            f'requirements, and a sample report all live on the Assignments page.'
        )
        out.append({
            "key": f"project-{p['n']}",
            "name": p["title"],
            "group": p["group"],
            "grading": "points", "points": 100,
            "submission_types": ["online_upload", "online_text_entry"],
            "due": week_due[{"week1": 1, "week2": 2, "week3": 3}[p["due"]]],
            "html": card("Weekly Homework · Project Case Study", p["title"],
                         [("Case study", "Your choice — one of the eleven methods")],
                         grading_pill("points", 100), body,
                         [button(url("assignments.html"), "Open the Project Spec & Rubric →"),
                          button(url("case-studies.html"), "Browse the Case Studies", primary=False)]),
        })

    # ---- Final Presentation (group: completion) ----
    fp = M["extras"]["final_presentation"]
    body = (
        f'Give a short presentation on your <strong style="color:{T["white"]};">'
        f'strongest of the three project case studies</strong>. We use these to share '
        f'what worked across the cohort. Format and length are confirmed on the course '
        f'site once enrollment closes.'
    )
    out.append({
        "key": "final-presentation",
        "name": "Final Presentation",
        "group": fp["group"],
        "grading": "completion", "points": 20,
        "submission_types": ["none"],
        "due": M["due_dates"][fp["due"]],
        "html": card("Final Presentation", "Final Presentation",
                     [("When", "End of term · Week 3")],
                     grading_pill("completion"), body,
                     [button(url("assignments.html"), "See Presentation Details →")]),
    })

    return out


# ---------------------------------------------------------------------------
# preview gallery
# ---------------------------------------------------------------------------
def build_preview(home_html, assignments):
    canvas_page = (
        'background:#ffffff;max-width:1100px;margin:0 auto 40px;'
        'padding:28px 40px 40px;border:1px solid #d4d7da;border-radius:6px;'
        'box-shadow:0 1px 4px rgba(0,0,0,0.08);'
    )

    def section_label(t):
        return (f'<h2 style="font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,'
                f'sans-serif;font-size:13px;letter-spacing:0.14em;text-transform:uppercase;'
                f'color:#2d3b45;max-width:1100px;margin:38px auto 14px;padding:0 8px;">'
                f'{html.escape(t)}</h2>')

    def frame(name, body):
        return (f'<div style="{canvas_page}">'
                f'<div style="font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,'
                f'sans-serif;font-size:22px;font-weight:600;color:#2d3b45;'
                f'border-bottom:1px solid #e8eaec;padding-bottom:14px;margin-bottom:22px;">'
                f'{html.escape(name)}</div>{body}</div>')

    parts = [
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '<title>SYSEN 5470 · Canvas Content Preview</title></head>',
        '<body style="margin:0;padding:30px 0;background:#f5f5f5;">',
        '<div style="font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;'
        'max-width:1100px;margin:0 auto 10px;padding:0 8px;">'
        '<div style="font-size:28px;font-weight:700;color:#2d3b45;">SYSEN 5470 — Canvas Content Preview</div>'
        '<p style="color:#556;max-width:760px;line-height:1.6;">Each white card below is rendered '
        'the way Canvas will show it (white content area, dark neon panel inside). This is a '
        'faithful local preview — fonts like Bebas Neue may differ slightly from Canvas, which '
        'falls back to its own sans. Nothing here has been pushed to Canvas.</p></div>',
    ]

    parts.append(section_label("Course Homepage (front page)"))
    parts.append(frame("Home", home_html))

    buckets = [
        ("Drawings  ·  group weight 20%", lambda a: a["group"] == "drawings"),
        ("Case Study Learning Checks  ·  Case Study Completion 20%", lambda a: a["key"].startswith("cs-lc")),
        ("Code Learning Checks (I Ran the Code)  ·  Case Study Completion 20%", lambda a: a["key"].startswith("code-lc")),
        ("Ed Discussions  ·  Case Study Completion 20%", lambda a: a["key"].startswith("ed-week")),
        ("Office Hours  ·  Case Study Completion 20%", lambda a: a["key"].startswith("office-week")),
        ("Final Presentation  ·  Case Study Completion 20%", lambda a: a["key"] == "final-presentation"),
        ("Weekly Homework · Projects  ·  20% each", lambda a: a["key"].startswith("project")),
    ]
    for label, pred in buckets:
        parts.append(section_label(label))
        for a in assignments:
            if pred(a):
                parts.append(frame(a["name"], a["html"]))

    parts.append("</body></html>")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    pages_dir = ROOT / "pages"
    asg_dir = ROOT / "assignments"
    for d in (pages_dir, asg_dir):
        d.mkdir(exist_ok=True)

    home_html = build_home()
    (pages_dir / "home.html").write_text(home_html)

    assignments = build_assignments()
    for a in assignments:
        (asg_dir / f'{a["key"]}.html').write_text(a["html"])

    # machine-readable plan for push_to_canvas.py (HTML referenced by file path)
    plan = {
        "course": M["course"],
        "apply_assignment_group_weights": M["course"]["apply_assignment_group_weights"],
        "assignment_groups": M["assignment_groups"],
        "front_page": {"title": "Home", "slug": "home", "html_file": "pages/home.html"},
        "assignments": [
            {k: a[k] for k in ("key", "name", "group", "grading", "points",
                               "submission_types", "due")}
            | {"html_file": f'assignments/{a["key"]}.html'}
            for a in assignments
        ],
        "modules": M["modules"],
        "site_base": SITE,
    }
    (ROOT / "canvas_plan.json").write_text(json.dumps(plan, indent=2, ensure_ascii=False))

    (ROOT / "preview.html").write_text(build_preview(home_html, assignments))

    print(f"✅ Wrote 1 front page  -> pages/home.html")
    print(f"✅ Wrote {len(assignments)} assignment fragments -> assignments/")
    print(f"✅ Wrote canvas_plan.json ({len(assignments)} assignments, "
          f'{len(M["assignment_groups"])} groups, {len(M["modules"])} modules)')
    print(f"✅ Wrote preview.html  (open this in a browser)")


if __name__ == "__main__":
    main()
