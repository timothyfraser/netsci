#!/usr/bin/env python3
"""
generate_html.py — SYSEN 5470 Canvas content generator.

Reads manifest.json (the single source of truth) and writes:

  pages/home.html                 Canvas front-page body (HTML fragment)
  assignments/<key>.html          one HTML fragment per Canvas assignment
  canvas_plan.json                fully-expanded, machine-readable plan that
                                  push_to_canvas.py consumes
  preview.html                    one self-contained gallery so a human can
                                  eyeball every page + assignment in a browser

SUBMISSION UNITS = the 11 case studies (manifest.json -> case_studies), one per
lab page / code folder, so each lines up with its own module and its own point
in the course. Each case study produces one drawing and one bundled Learning
Check (the in-lab case-study check AND the "I ran the code" check, submitted
together).

NO DUE DATES. The cards never mention a due date or week, and the push script
does NOT set due_at — so you schedule everything in Canvas and can move things
around freely without re-running any code.

WHY FRAGMENTS, NOT FULL PAGES?
  Canvas stores page/assignment bodies as sanitized HTML and renders them
  INSIDE its own <html><head><body>. It strips <head>, <style>, <link>,
  <script>, and class-based styling. So every value here is an INLINE style
  attribute with a literal color (no CSS variables). The whole body is wrapped
  in one dark "stage" <div> so the neon theme reads on Canvas's white area.

Pure standard library. Run:  python3 scripts/generate_html.py
"""

import json
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
M = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))

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


def meta_line(label: str, value: str) -> str:
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
        style = (f'display:inline-block;background:{T["green_bright"]};color:{T["black"]};'
                 f'border:1px solid {T["green_bright"]};')
    else:
        style = (f'display:inline-block;background:transparent;color:{T["green_bright"]};'
                 f'border:1px solid {T["green_bright"]};')
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
        inner += meta_line(lbl, val)
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
# assignment expansion (11 case studies + weekly items + projects + final)
# ---------------------------------------------------------------------------
def build_assignments():
    out = []

    # ---- per CASE STUDY: one drawing + one bundled learning check ----
    for c in M["case_studies"]:
        cs_label = f'{c["icon"]} {esc(c["name"])}'
        lab = url(c["lab"])
        code = url(c["code"] + "#readme")
        sketch = url(c["sketch_anchor"])

        # Drawing (group: drawings)
        body = (
            f'The hand-drawn sketchpad activity for this case study — '
            f'<strong style="color:{T["white"]};">{esc(c["sketch_title"])}</strong>. '
            f'The full prompt and what to submit live on the course website. '
            f'<strong style="color:{T["white"]};">To submit:</strong> paste a photo of '
            f'your drawing directly into the text box (Online · Text Entry) so it is easy '
            f'to review right here in Canvas.'
        )
        out.append({
            "key": f'drawing-{c["key"]}',
            "name": f'Drawing — {c["short"]}',
            "group": "drawings",
            "grading": "completion", "points": 1,
            "submission_types": ["online_text_entry"],
            "html": card("Drawing Submission", f'Drawing · {c["short"]}',
                         [("Case study", cs_label), ("Skill", c["skill"])],
                         grading_pill("completion"), body,
                         [button(sketch, "Open the Sketchpad →"),
                          button(lab, "View the Lab", primary=False)]),
        })

        # Bundled Learning Check = case-study LC + code "I ran the code" LC
        # (group: casestudies)
        body = (
            f'Your combined Learning Check for this case study — the in-lab '
            f'case-study check <em>and</em> the “I ran the code” check, '
            f'<strong style="color:{T["white"]};">submitted together</strong>. The full '
            f'instructions live on the course website. '
            f'<strong style="color:{T["white"]};">To submit (Online · Text Entry):</strong> '
            f'include your code either (A) by pasting it at the end of the text box, or '
            f'(B) by pasting a link to the exact file in your GitHub repo. '
            f'<strong style="color:{T["amber"]};">Option B is the harder path</strong> — if I '
            f'(GitHub <span style="font-family:{font("mono")};color:{T["white"]};">timothyfraser</span>) '
            f'cannot open that repo at the deadline, the assignment is a 0, so make your repo '
            f'public or grant me access before you submit.'
        )
        out.append({
            "key": f'lc-{c["key"]}',
            "name": f'Learning Checks — {c["short"]}',
            "group": "casestudies",
            "grading": "completion", "points": 1,
            "submission_types": ["online_text_entry"],
            "html": card("Learning Checks · Case Study + “I Ran the Code”",
                         f'Learning Checks · {c["short"]}',
                         [("Case study", cs_label), ("Skill", c["skill"])],
                         grading_pill("completion"), body,
                         [button(lab, "Open the Lab →"),
                          button(code, "Open the Code Folder", primary=False)]),
        })

    # ---- Ed Discussion, one per week (group: participation) ----
    for w in M["extras"]["ed_discussion_weeks"]:
        body = (
            f'Your weekly post on <strong style="color:{T["white"]};">Ed Discussion</strong> '
            f'(linked in the Canvas left-hand navigation). The prompt and details live on '
            f'the course website. <strong style="color:{T["white"]};">To submit (Online · '
            f'Text Entry):</strong> paste a screenshot of your Ed Discussion post into the '
            f'text box.'
        )
        out.append({
            "key": f"ed-week-{w}",
            "name": f"Ed Discussion — Week {w}",
            "group": "participation",
            "grading": "completion", "points": 1,
            "submission_types": ["online_text_entry"],
            "html": card("Ed Discussion", f"Ed Discussion · Week {w}",
                         [], grading_pill("completion"), body,
                         [button(url("calendar.html"), "See the Course Calendar →")]),
        })

    # ---- Office Hours, one per week (group: participation) ----
    for w in M["extras"]["office_hours_weeks"]:
        body = (
            f'Your office-hours check-in for the week — <strong style="color:'
            f'{T["white"]};">three are required across the course</strong>. Book a slot on '
            f'the course website. <strong style="color:{T["white"]};">To submit (Online · '
            f'Text Entry):</strong> paste a screenshot of your calendar invite to our '
            f'office-hours meeting into the text box.'
        )
        out.append({
            "key": f"office-week-{w}",
            "name": f"Office Hours — Week {w}",
            "group": "participation",
            "grading": "completion", "points": 1,
            "submission_types": ["online_text_entry"],
            "html": card("Office Hours", f"Office Hours · Week {w}",
                         [], grading_pill("completion"), body,
                         [button(url("help/office-hours.html"), "Book Office Hours →")]),
        })

    # ---- Projects, one per weekly-homework group ----
    for p in M["extras"]["projects"]:
        body = (
            f'Your weekly homework <em>is</em> the project — the analysis code plus your '
            f'written report, on a network you chose. The full spec, the four-skill '
            f'rubric, the hard requirements, and a sample report all live on the '
            f'Assignments page of the course website.'
        )
        out.append({
            "key": f"project-{p['n']}",
            "name": p["title"],
            "group": p["group"],
            "grading": "points", "points": 100,
            "submission_types": ["online_upload", "online_text_entry"],
            "html": card("Weekly Homework · Project Case Study", p["title"],
                         [("Case study", "Your choice — one of the methods")],
                         grading_pill("points", 100), body,
                         [button(url("assignments.html"), "Open the Project Spec & Rubric →"),
                          button(url("case-studies.html"), "Browse the Case Studies", primary=False)]),
        })

    # ---- Final Presentation (group: participation) ----
    fp = M["extras"]["final_presentation"]
    body = (
        f'A short presentation on your <strong style="color:{T["white"]};">strongest of '
        f'the three project case studies</strong>. Format and details are confirmed on '
        f'the course website.'
    )
    out.append({
        "key": "final-presentation",
        "name": "Final Presentation",
        "group": fp["group"],
        "grading": "completion", "points": 1,
        "submission_types": ["none"],
        "html": card("Final Presentation", "Final Presentation",
                     [], grading_pill("completion"), body,
                     [button(url("assignments.html"), "See Presentation Details →")]),
    })

    # ---- Course surveys (group: participation) ----
    for s in M.get("surveys", []):
        form_url = s.get("url")
        if s["key"] == "final-eval":
            body = (
                f'<strong style="color:{T["white"]};">Take the Final Course Evaluation.</strong> '
                f'🕒 Estimated time: 5–10 minutes. All participants receive course credit for '
                f'completing the final course survey — it helps your instructor tailor this course '
                f'to suit future students. <strong style="color:{T["white"]};">Your answers are '
                f'fully anonymized.</strong> To complete it, search your inbox for the email from '
                f'Cornell about final course evaluations. <strong style="color:{T["white"]};">To '
                f'submit (Online · URL):</strong> paste the confirmation link to affirm you '
                f'completed the evaluation so I can give you credit.'
            )
        else:
            body = (
                f'A short course survey — <strong style="color:{T["white"]};">all participants '
                f'receive course credit</strong> for completing it. 🕒 A few minutes, answers '
                f'anonymized. <strong style="color:{T["white"]};">To submit (Online · URL):</strong> '
                f'paste the link to your completed Google Form (or its confirmation) into the box.'
            )
        if form_url:
            buttons = [button(form_url, "Open the Survey →")]
        else:
            buttons = [button("#", "Survey Link — Coming Soon")]
            body += (f' <span style="color:{T["grey_dim"]};">(The form link will be posted '
                     f'here shortly.)</span>')
        out.append({
            "key": s["key"],
            "name": s["name"],
            "group": s["group"],
            "grading": "completion", "points": 1,
            "submission_types": ["online_url"],
            "html": card(s["name"], f'{s["icon"]} {s["name"]}', [],
                         grading_pill("completion"), body, buttons),
        })

    return out


# ---------------------------------------------------------------------------
# modules — OVERVIEW / ACTIVITIES / REMINDERS, assembled from the manifest.
# Every assignment appears in the module it relates to (content week). Items
# of type "Assignment" carry a "ref" = the assignment key; push_to_canvas.py
# resolves the ref to the Canvas assignment id at push time.
# ---------------------------------------------------------------------------
def build_modules():
    MOD = M["modules"]
    readings = MOD["readings_path"]
    videos = M["extras"].get("week_videos", {})
    surveys_by_module = {}
    for s in M.get("surveys", []):
        surveys_by_module.setdefault(s["module"], []).append(s)

    def sub(t):
        return {"type": "SubHeader", "title": t}

    def ext(t, path=None, url_=None, indent=1):
        d = {"type": "ExternalUrl", "title": t, "indent": indent}
        if url_:
            d["url"] = url_
        else:
            d["path"] = path
        return d

    def asg(ref, indent=1):
        return {"type": "Assignment", "ref": ref, "indent": indent}

    modules = []

    # ---- Getting Started ----
    gs = MOD["getting_started"]
    items = [sub("OVERVIEW")]
    for ln in gs["overview"]:
        items.append(ext(ln["title"], ln.get("path"), ln.get("url")))
    items.append(sub("ACTIVITIES"))
    for s in surveys_by_module.get("getting-started", []):
        items.append(asg(s["key"]))
    # surface the first office hours + first ed discussion here too
    items.append(asg("office-week-1"))
    items.append(asg("ed-week-1"))
    modules.append({"name": gs["name"], "items": items})

    # ---- Week 1 / 2 / 3 ----
    for w in (1, 2, 3):
        cs_week = [c for c in M["case_studies"] if c["week"] == w]
        items = [sub("OVERVIEW")]
        vid = videos.get(str(w))
        if vid:
            items.append(ext(f"🎬 Week {w} Overview Video", url_=vid))
        else:
            items.append(ext(f"🎬 Week {w} Overview Video (coming soon)", path="index.html"))
        items.append(ext(f"📚 Readings for Week {w}", path=readings))
        items.append(sub("ACTIVITIES"))
        # Office Hours + Ed Discussion always come first
        items.append(asg(f"office-week-{w}"))
        items.append(asg(f"ed-week-{w}"))
        # then each case-study Lab, with its Drawing + Learning Check nested under it
        for c in cs_week:
            items.append(ext(f'{c["icon"]} {c["short"]} — Lab', path=c["lab"], indent=1))
            items.append(asg(f'drawing-{c["key"]}', indent=2))
            items.append(asg(f'lc-{c["key"]}', indent=2))
        for s in surveys_by_module.get(f"week{w}", []):
            items.append(asg(s["key"]))
        items.append(sub("REMINDERS"))
        items.append(ext("📤 Submit on Canvas — How to Submit", path="help/submit.html"))
        for p in M["extras"]["projects"]:
            if p["n"] == w and w in (1, 2):   # project-3 (final) lives in Wrapping Up
                items.append(asg(f"project-{p['n']}"))
        modules.append({"name": MOD["week_titles"][str(w)], "items": items})

    # ---- Wrapping Up ----
    wu = MOD["wrapping_up"]
    items = [sub("OVERVIEW")]
    for ln in wu["overview"]:
        items.append(ext(ln["title"], ln.get("path"), ln.get("url")))
    items.append(sub("ACTIVITIES"))
    for s in surveys_by_module.get("wrapping-up", []):
        items.append(asg(s["key"]))
    items.append(sub("REMINDERS"))
    items.append(asg("final-presentation"))
    items.append(asg("project-3"))
    modules.append({"name": wu["name"], "items": items})

    return modules


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
        'falls back to its own sans. Nothing here has been pushed to Canvas. Due dates are set '
        'in Canvas, not here.</p></div>',
    ]

    parts.append(section_label("Course Homepage (front page)"))
    parts.append(frame("Home", home_html))

    surveys = ("intro-survey", "midterm-eval", "final-eval")
    buckets = [
        ("Drawings  ·  group weight 20%  ·  drops the lowest 2  ·  1 pt · Text Entry",
         lambda a: a["group"] == "drawings"),
        ("Case Studies — Learning Checks (case study + “I ran the code”)  ·  25%  ·  drops the lowest 2  ·  1 pt · Text Entry",
         lambda a: a["key"].startswith("lc-")),
        ("Participation · Ed Discussions  ·  Participation 5%  ·  1 pt", lambda a: a["key"].startswith("ed-week")),
        ("Participation · Office Hours  ·  Participation 5%  ·  1 pt", lambda a: a["key"].startswith("office-week")),
        ("Participation · Course Surveys  ·  Participation 5%  ·  1 pt · Online URL", lambda a: a["key"] in surveys),
        ("Final Presentation  ·  own group 5%", lambda a: a["key"] == "final-presentation"),
        ("Weekly Homework · Projects  ·  15% each  ·  100 pts", lambda a: a["key"].startswith("project")),
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
    # clear stale fragments so renamed/removed assignments don't linger
    for f in asg_dir.glob("*.html"):
        f.unlink()

    home_html = build_home()
    (pages_dir / "home.html").write_text(home_html, encoding="utf-8")

    assignments = build_assignments()
    for a in assignments:
        (asg_dir / f'{a["key"]}.html').write_text(a["html"], encoding="utf-8")

    plan = {
        "course": M["course"],
        "apply_assignment_group_weights": M["course"]["apply_assignment_group_weights"],
        "assignment_groups": M["assignment_groups"],
        "front_page": {"title": "Home", "slug": "home", "html_file": "pages/home.html"},
        "assignments": [
            {k: a[k] for k in ("key", "name", "group", "grading", "points",
                               "submission_types")}
            | {"html_file": f'assignments/{a["key"]}.html'}
            for a in assignments
        ],
        "modules": build_modules(),
        "site_base": SITE,
    }
    (ROOT / "canvas_plan.json").write_text(
        json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")

    (ROOT / "preview.html").write_text(build_preview(home_html, assignments),
                                       encoding="utf-8")

    print(f"✅ Wrote 1 front page  -> pages/home.html")
    print(f"✅ Wrote {len(assignments)} assignment fragments -> assignments/")
    print(f"✅ Wrote canvas_plan.json ({len(assignments)} assignments, "
          f'{len(M["assignment_groups"])} groups, {len(M["modules"])} modules)')
    print(f"✅ Wrote preview.html  (open this in a browser)")


if __name__ == "__main__":
    main()
