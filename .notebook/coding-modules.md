# SYSEN 5470 — Coding Modules Bundle

_Auto-generated NotebookLM source · 2026-06-24 20:12 UTC_

Every Markdown, R, and Python file in the course's coding modules, concatenated into one document. Paste this into NotebookLM as a source alongside the website bundle.

**158 files included.**

---

## `.canvas/HANDOFF.md`

# SYSEN 5470 → Canvas — Implementation Handoff

This folder is **course scaffolding only**. It contains ready-to-publish HTML
for a Canvas course (home page + 32 assignments + 5 modules) and two scripts:
one that *generates* the HTML from a manifest, and one that *pushes* it to
Canvas via the REST API. **No API token is stored here.** A future local
session (or you) runs the push script with your token in an environment
variable.

> **TL;DR for the future session**
> 1. `cd .canvas && python3 scripts/generate_html.py` (rebuilds HTML — optional, already built)
> 2. `pip install requests`
> 3. `export CANVAS_BASE_URL=https://canvas.cornell.edu CANVAS_API_TOKEN=… CANVAS_COURSE_ID=…`
> 4. `python3 scripts/push_to_canvas.py --dry-run` → eyeball the plan
> 5. `python3 scripts/push_to_canvas.py` → publish (idempotent; safe to re-run)

---

## 1. What gets created

| Object | Count | Where it comes from |
|---|---|---|
| Course front page ("Home") | 1 | `pages/home.html` |
| Assignment **groups** (weighted) | 6 | `manifest.json → assignment_groups` |
| **Assignments** | 32 | `assignments/*.html` + `canvas_plan.json` |
| **Modules** + items | 5 modules | `manifest.json → modules` |

### Submission units = the 11 case studies (one per lab / code folder)

Each of the 11 lab pages / code folders is its own Canvas submission unit, so it
lines up with its own module and its own point in the course (e.g. Sampling and
Joins are scheduled in different weeks and stay separate). Each case study
produces **one drawing** and **one bundled Learning Check** — the in-lab
case-study Learning Check *and* the "I ran the code" check, submitted together.

### The six weighted assignment groups (sum = 100%)

| Group | Weight | Contains | Rule |
|---|---|---|---|
| **Drawings** | 20% | 11 drawings (1 per case study) | **drops the lowest 2** |
| **Case Studies** | 25% | 11 bundled Learning Checks (1 per case study) | **drops the lowest 2** |
| **Participation** | 10% | 3 weekly Ed Discussions + 3 weekly Office Hours + 1 Final Presentation (7 items) | — |
| **Weekly Homework 1 · Project Case Study** | 15% | Project submission 1 | — |
| **Weekly Homework 2 · Project Case Study** | 15% | Project submission 2 | — |
| **Weekly Homework 3 · Project Case Study** | 15% | Project submission 3 (final) | — |

This matches the weighting you specified:
*drawings 20 · case studies (the bundled learning checks) 25 · participation
(Ed discussion + office hours + final presentation) 10 · weekly homeworks
(= the project) 15 each = 45.* The **drop-lowest-2** rule on Drawings and Case
Studies gives students two freebies in each group for time-crunch weeks (Canvas
group rule `rules[drop_lowest]=2`).

### No due dates (by design)
The cards never mention a due date or week, and **`push_to_canvas.py` does not
set `due_at`**. Assignments are created with no due date so you schedule
everything **in Canvas** and can move things around freely — re-running the
script will not overwrite your hand-set dates. (The Ed Discussion / Office Hours
titles keep a "Week N" label only to tell the three recurring ones apart; that
is an identifier, not a deadline.)

### Grading types
- **Completion** items → Canvas `grading_type = pass_fail` (complete / incomplete).
  Drawings, the bundled Learning Checks, Ed Discussions, Office Hours, Final Presentation.
- **Points** items → Canvas `grading_type = points`, `points_possible = 100`.
  The three project case studies.

Each assignment card shows a colored **pill** stating exactly this
("Graded · Completion" in green, "Graded · 100 Points" in amber).

---

## 2. Decisions & assumptions (change these in `manifest.json` if needed)

Everything below is data-driven from `manifest.json`. Edit the manifest, then
re-run `generate_html.py`, then `push_to_canvas.py`.

1. **Weighting** — exactly as you specified. Within the *Case Studies* and
   *Participation* groups all items are `pass_fail` with `points_possible: 10`
   (Final Presentation `20`) so they weigh roughly equally. The relative split
   inside a weighted group only matters *within* that group.
2. **Due dates** — intentionally **not set**. The cards don't mention them and
   the push script doesn't send `due_at`, so you own all scheduling in Canvas
   and can move things without re-running code. `manifest.json → due_dates` keeps
   the calendar's Monday-9am dates as **reference only** (Week 1 = 2026-06-29,
   Week 2 = 2026-07-06, Week 3 / final = 2026-07-13) if you want to set the same
   dates by hand in Canvas.
3. **Sketch ↔ case-study mapping** is **approximate**. The public
   `docs/sketchpad.html` is described as "a preview library… for case studies
   not yet built," and its prompts do not map perfectly 1:1 to the case studies.
   Each drawing card therefore links to the **Sketchpad page** (the correct
   destination regardless) and names its best-fit sketch in text. If you finalize
   the mapping, edit `sketch_title` / `sketch_anchor` per case study in
   `manifest.json`.
3b. **Cards carry no instructions.** Each card is intentionally a short pointer
   (what the item is + a button to the website), not a restatement of the
   assignment's instructions. The website is the single source of truth, so
   changing an assignment there never requires editing Canvas.
4. **Ed Discussion & Office Hours** are `submission_types: ["none"]` — they
   happen off-Canvas (Ed) or in a meeting, and you mark them complete. The cards
   link to the calendar / office-hours pages. If you wire up a real Ed LTI or a
   Canvas Discussion, switch the type accordingly.
5. **Final Presentation** lives in the *Participation* group (completion-graded)
   alongside Ed Discussions and Office Hours, so the *Case Studies* group is
   exactly the 11 bundled Learning Checks (clean target for "drop the lowest 2")
   and each Weekly Homework group stays cleanly = one project = 15%. Move it to a
   Weekly Homework group or its own group if you want it points-graded. Note the
   *Participation* group has **no** drop rule, so a missed Office Hours / Ed
   Discussion still counts; add `rules[drop_lowest]` there too if you want a
   participation freebie.

---

## 3. Canvas HTML formatting requirements (why the HTML looks the way it does)

Canvas stores page/assignment bodies as **sanitized HTML** and renders them
*inside* its own `<html><head><body>`. You were right:

- **No `<head>`, so no `<style>`, no `<link>`, no `@import`, no `<script>`.**
  All of these are stripped by Canvas's sanitizer. **Every style must be an
  inline `style="…"` attribute.**
- **No CSS variables / classes that resolve to a stylesheet.** `var(--x)` won't
  work — so the generator inlines **literal hex** values (mirrored from
  `docs/assets/design.css`).
- **Canvas pages have a white background** you can't change globally. So each
  body is wrapped in one **dark "stage" `<div>`** with its own
  `background`, recreating the site's neon-on-near-black look on the white page.
- **Layout primitives that survive the sanitizer reliably:** `display:block`,
  `display:inline-block`, `width`, `vertical-align`, `padding`, `margin`,
  `border`, `border-radius`, `background`, `background-image:linear/radial-
  gradient`, `color`, `font-family`, `font-size`, `font-weight`,
  `letter-spacing`, `text-transform`, `line-height`, `text-decoration`. The
  cards use **only these** — no flexbox/grid dependency, no `position:fixed`,
  no `backdrop-filter` (those are unreliable or stripped). The homepage "grid"
  is `inline-block` cards with a fixed `width`, which wrap responsively.
- **Buttons** are `<a>` tags styled as `inline-block` with padding + background
  (there are no real buttons on a Canvas page).
- **Fonts**: Bebas Neue / DM Sans / Space Mono are named first with web-safe
  fallbacks (`Impact`, `Lato`/`Arial`, `Courier New`). Canvas won't load Google
  Fonts, so it falls back gracefully — the *layout and color* carry the brand.
- **Emoji** render fine and are used as lightweight iconography.
- **Links** use `target="_blank" rel="noopener"` so the website opens in a new
  tab and students stay anchored in Canvas.
- **`<iframe>`** is allowed *only* from Canvas's whitelisted domains — we don't
  rely on it.

Preview the exact rendering by opening **`preview.html`** in any browser.

---

## 4. Exact REST API reference (what `push_to_canvas.py` calls)

Base: `https://<canvas-host>/api/v1`. Auth header on every request:
`Authorization: Bearer <CANVAS_API_TOKEN>`. `:course` = `CANVAS_COURSE_ID`.
All bodies are `application/x-www-form-urlencoded`. Order matters — do groups
before assignments (assignments reference `assignment_group_id`).

### 4.1 Turn on weighted groups
```
PUT /courses/:course
    course[apply_assignment_group_weights]=true
```

### 4.2 Assignment groups
```
GET  /courses/:course/assignment_groups            # list (match by name)
POST /courses/:course/assignment_groups            # create
     name=Drawings & group_weight=20 & position=1
     rules[drop_lowest]=2                           # Drawings + Case Studies groups only
PUT  /courses/:course/assignment_groups/:id        # update weight/position/rules
```
The **drop-lowest** freebie is a group *rule*: `rules[drop_lowest]=2`. Other
rule keys exist if you want them: `rules[drop_highest]=N` and
`rules[never_drop][]=<assignment_id>` (e.g. to protect the Final Presentation
from being the dropped one — needs the id, so set it on a second pass).

### 4.3 Front page + set as course home
```
GET  /courses/:course/pages?search_term=Home       # find existing by title
POST /courses/:course/pages                         # create
     wiki_page[title]=Home
     wiki_page[body]=<HTML from pages/home.html>
     wiki_page[published]=true
     wiki_page[front_page]=true
PUT  /courses/:course/pages/:url                     # update (url slug = "home")
PUT  /courses/:course                                # make the wiki page the home
     course[default_view]=wiki
```

### 4.4 Assignments
```
GET  /courses/:course/assignments                   # list (match by name)
POST /courses/:course/assignments                    # create
     assignment[name]=Drawing — Build a Network
     assignment[description]=<HTML from assignments/<key>.html>
     assignment[submission_types][]=online_upload    # repeat key for multiple
     assignment[points_possible]=10
     assignment[grading_type]=pass_fail              # or "points"
     assignment[assignment_group_id]=<group id>
     assignment[published]=true
     # NB: due_at intentionally omitted — set due dates in Canvas, not here
PUT  /courses/:course/assignments/:id                # update
```
- **`grading_type` valid values**: `pass_fail`, `points`, `percent`,
  `letter_grade`, `gpa_scale`, `not_graded`. We use **`pass_fail`** for
  completion and **`points`** for projects.
- **`submission_types` valid values** (array): `online_upload`,
  `online_text_entry`, `online_url`, `on_paper`, `none`, `discussion_topic`,
  `external_tool`, `not_graded`. We use `online_upload` (drawings, projects),
  `online_text_entry` (Learning Checks, projects), `none` (Ed/office/final).

### 4.5 Modules + items
```
GET  /courses/:course/modules                        # list (match by name)
POST /courses/:course/modules                         # create
     module[name]=Week 1 — Think Like a Graph
     module[position]=2 & module[published]=true
PUT  /courses/:course/modules/:id                     # publish / reposition
GET  /courses/:course/modules/:id/items               # existing items (by title)
POST /courses/:course/modules/:id/items               # add item
     module_item[type]=ExternalUrl                    # or SubHeader / Page / Assignment
     module_item[title]=🕸️ Build a Network — Lab
     module_item[external_url]=https://timothyfraser.com/netsci/case-studies/build-a-network.html
     module_item[new_tab]=true & module_item[indent]=1 & module_item[position]=2
```
- `module_item[type]` valid values: `File`, `Page`, `Discussion`, `Assignment`,
  `Quiz`, `SubHeader`, `ExternalUrl`, `ExternalTool`. We use **`ExternalUrl`**
  (links to the website) and **`SubHeader`** (section dividers). Modules are
  intentionally **non-duplicative with the assignments** — they are website
  navigation, with a sub-header pointing students to the Assignments area.

### Idempotency
Every object is matched by **name** first; re-running updates instead of
duplicating. Module *items* are matched by title and only missing ones are
added. So you can iterate: edit manifest → `generate_html.py` →
`push_to_canvas.py` as many times as you like.

---

## 5. Alternative: the Canvas MCP server

If you prefer to drive Canvas through the
[`vishalsachdev/canvas-mcp`](https://github.com/vishalsachdev/canvas-mcp)
server inside an agent instead of the raw API, the same plan maps onto these
tools (see that repo's `tools/README.md`):

| Step | MCP tool | Key args |
|---|---|---|
| Front page | `create_page` then `update_page_settings` | `course_identifier`, `title`, `body`, `front_page=true` |
| Assignments | `create_assignment` / `update_assignment` | `name`, `description`, `submission_types`, `points_possible`, `grading_type`, `assignment_group_id`, `due_at`, `published` |
| Modules | `create_module`, then `add_module_item` | `name`; `item_type` (`ExternalUrl`/`SubHeader`), `external_url`, `title`, `indent` |

Note: that server (as documented) has **no dedicated assignment-group creation
tool**, so create the 5 weighted groups via the raw API call in §4.2 first, then
reference their ids. The HTML bodies in `assignments/*.html` and
`pages/home.html` are exactly what you pass as `description` / `body`.

---

## 6. Verification checklist (after running the push)

- [ ] Course **Home** shows the dark neon welcome page with the three shortcut
      sections (Start Here / Do the Work / Get Help) and working links.
- [ ] **Assignments** index shows 6 groups; group weights read
      20/25/10/15/15/15 and "Total 100%". (Grades → ⋮ → *Assignment Groups
      Weight* is enabled.)
- [ ] A drawing, a bundled Learning Check, and a project each render their card
      with the correct **grading pill** and a working website button. (No card
      mentions a due date or week.)
- [ ] The **Drawings** and **Case Studies** groups show "drop the lowest 2"
      (group → ⋮ → *Assignment Group Rules*).
- [ ] **Modules** shows Getting Started / Week 1 / Week 2 / Week 3 / Wrapping Up,
      each with external links opening the website in a new tab.
- [ ] Assignments have **no due dates** — set them in Canvas as you like.

---

## 7. File map

```
.canvas/
├── HANDOFF.md              ← you are here
├── README.md               ← quick orientation + preview instructions
├── manifest.json           ← SINGLE SOURCE OF TRUTH (edit this)
├── preview.html            ← open in a browser to see every card
├── pages/
│   └── home.html           ← Canvas front-page body
├── assignments/            ← 32 assignment bodies (one HTML fragment each)
│   ├── drawing-<case-study>.html   (11 — one per case study)
│   ├── lc-<case-study>.html        (11 — bundled case-study + code LC per case study)
│   ├── ed-week-{1,2,3}.html        (3)
│   ├── office-week-{1,2,3}.html    (3)
│   ├── project-{1,2,3}.html        (3)
│   └── final-presentation.html     (1)
├── canvas_plan.json        ← generated machine-readable plan (push reads this)
└── scripts/
    ├── generate_html.py    ← manifest → HTML + plan + preview (stdlib only)
    └── push_to_canvas.py   ← plan → Canvas via REST (needs `requests` + env vars)
```

---

## `.canvas/HANDOFF_DUEDATES.md`

# SYSEN 5470 — Due Dates & Points (Canvas contract handoff)

- **Course:** `87652` @ https://canvas.cornell.edu
- **Last pulled from Canvas:** 2026-06-23T18:41:42Z
- **Generated:** 2026-06-23T18:41:42Z

> **Dates below are a PROPOSAL** seeded from the course calendar (each week's Monday 9 AM ET). Edit them — in `canvas_contract.json` or by replying in chat — then they get pushed to Canvas.

**How we keep this in sync**
- *You changed something on Canvas* → run `python scripts/sync_contract.py --pull` (Canvas → this file).
- *You changed this contract* → run `python scripts/sync_contract.py --apply --dry-run` then `--apply` (this file → Canvas).

## Assignment group weights

| Group | Weight | Drop lowest |
|---|---|---|
| Drawings | 20.0% | 2 |
| Case Studies | 25.0% | 2 |
| Participation | 5.0% | — |
| Final Presentation | 5.0% | — |
| Weekly Homework 1 · Project Case Study | 15.0% | — |
| Weekly Homework 2 · Project Case Study | 15.0% | — |
| Weekly Homework 3 · Project Case Study | 15.0% | — |
| **Total** | **100.0%** | |

## Week 1

| Assignment | Group | Grading | Points | Due (default) | Section overrides |
|---|---|---|---|---|---|
| [Drawing — Build a Network](https://canvas.cornell.edu/courses/87652/assignments/968699) | Drawings | Completion | 1 | Thu 2026-07-02 13:00 UTC | SYSEN-5940: Thu 2026-07-02 13:00 UTC |
| [Learning Checks — Build a Network](https://canvas.cornell.edu/courses/87652/assignments/968700) | Case Studies | Completion | 1 | Thu 2026-07-02 13:00 UTC | SYSEN-5940: Thu 2026-07-02 13:00 UTC |
| [Drawing — Network Statistics](https://canvas.cornell.edu/courses/87652/assignments/968701) | Drawings | Completion | 1 | Thu 2026-07-02 13:00 UTC | SYSEN-5940: Thu 2026-07-02 13:00 UTC |
| [Learning Checks — Network Statistics](https://canvas.cornell.edu/courses/87652/assignments/968702) | Case Studies | Completion | 1 | Thu 2026-07-02 13:00 UTC | SYSEN-5940: Thu 2026-07-02 13:00 UTC |
| [Drawing — Centrality](https://canvas.cornell.edu/courses/87652/assignments/968703) | Drawings | Completion | 1 | Thu 2026-07-02 13:00 UTC | SYSEN-5940: Thu 2026-07-02 13:00 UTC |
| [Learning Checks — Centrality](https://canvas.cornell.edu/courses/87652/assignments/968704) | Case Studies | Completion | 1 | Thu 2026-07-02 13:00 UTC | SYSEN-5940: Thu 2026-07-02 13:00 UTC |
| [Ed Discussion — Week 1](https://canvas.cornell.edu/courses/87652/assignments/968721) | Participation | Completion | 1 | Thu 2026-07-02 13:00 UTC | SYSEN-5940: Thu 2026-07-02 13:00 UTC |
| [Office Hours — Week 1](https://canvas.cornell.edu/courses/87652/assignments/968724) | Participation | Completion | 1 | Thu 2026-07-02 13:00 UTC | SYSEN-5940: Thu 2026-07-02 13:00 UTC; LEC001-AD: Thu 2026-06-25 03:59 UTC |
| [Project Case Study — Submission 1](https://canvas.cornell.edu/courses/87652/assignments/968727) | Weekly Homework 1 · Project Case Study | Points | 100 | Thu 2026-07-02 13:00 UTC | SYSEN-5940: Thu 2026-07-02 13:00 UTC |
| [Intro Course Survey](https://canvas.cornell.edu/courses/87652/assignments/968731) | Participation | Completion | 1 | Wed 2026-06-24 03:59 UTC | — |

## Week 2

| Assignment | Group | Grading | Points | Due (default) | Section overrides |
|---|---|---|---|---|---|
| [Drawing — Supply Chain](https://canvas.cornell.edu/courses/87652/assignments/968705) | Drawings | Completion | 1 | Mon 2026-07-06 13:00 UTC | — |
| [Learning Checks — Supply Chain](https://canvas.cornell.edu/courses/87652/assignments/968706) | Case Studies | Completion | 1 | Mon 2026-07-06 13:00 UTC | — |
| [Drawing — Routing](https://canvas.cornell.edu/courses/87652/assignments/968707) | Drawings | Completion | 1 | Mon 2026-07-06 13:00 UTC | — |
| [Learning Checks — Routing](https://canvas.cornell.edu/courses/87652/assignments/968708) | Case Studies | Completion | 1 | Mon 2026-07-06 13:00 UTC | — |
| [Drawing — DSM Clustering](https://canvas.cornell.edu/courses/87652/assignments/968709) | Drawings | Completion | 1 | Mon 2026-07-06 13:00 UTC | — |
| [Learning Checks — DSM Clustering](https://canvas.cornell.edu/courses/87652/assignments/968710) | Case Studies | Completion | 1 | Mon 2026-07-06 13:00 UTC | — |
| [Drawing — Aggregation](https://canvas.cornell.edu/courses/87652/assignments/968711) | Drawings | Completion | 1 | Mon 2026-07-06 13:00 UTC | — |
| [Learning Checks — Aggregation](https://canvas.cornell.edu/courses/87652/assignments/968712) | Case Studies | Completion | 1 | Mon 2026-07-06 13:00 UTC | — |
| [Ed Discussion — Week 2](https://canvas.cornell.edu/courses/87652/assignments/968722) | Participation | Completion | 1 | Mon 2026-07-06 13:00 UTC | — |
| [Office Hours — Week 2](https://canvas.cornell.edu/courses/87652/assignments/968725) | Participation | Completion | 1 | Mon 2026-07-06 13:00 UTC | — |
| [Project Case Study — Submission 2](https://canvas.cornell.edu/courses/87652/assignments/968728) | Weekly Homework 2 · Project Case Study | Points | 100 | Mon 2026-07-06 13:00 UTC | — |
| [Midterm Course Evaluation](https://canvas.cornell.edu/courses/87652/assignments/968732) | Participation | Completion | 1 | Thu 2026-07-02 03:59 UTC | — |

## Week 3

| Assignment | Group | Grading | Points | Due (default) | Section overrides |
|---|---|---|---|---|---|
| [Drawing — GNN by Hand](https://canvas.cornell.edu/courses/87652/assignments/968713) | Drawings | Completion | 1 | Sat 2026-07-11 03:59 UTC | — |
| [Learning Checks — GNN by Hand](https://canvas.cornell.edu/courses/87652/assignments/968714) | Case Studies | Completion | 1 | Sat 2026-07-11 03:59 UTC | — |
| [Drawing — GNN + XGBoost](https://canvas.cornell.edu/courses/87652/assignments/968715) | Drawings | Completion | 1 | Sat 2026-07-11 03:59 UTC | — |
| [Learning Checks — GNN + XGBoost](https://canvas.cornell.edu/courses/87652/assignments/968716) | Case Studies | Completion | 1 | Sat 2026-07-11 03:59 UTC | — |
| [Drawing — Sampling](https://canvas.cornell.edu/courses/87652/assignments/968717) | Drawings | Completion | 1 | Sat 2026-07-11 03:59 UTC | — |
| [Learning Checks — Sampling](https://canvas.cornell.edu/courses/87652/assignments/968718) | Case Studies | Completion | 1 | Sat 2026-07-11 03:59 UTC | — |
| [Drawing — Joins](https://canvas.cornell.edu/courses/87652/assignments/968719) | Drawings | Completion | 1 | Sat 2026-07-11 03:59 UTC | — |
| [Learning Checks — Joins](https://canvas.cornell.edu/courses/87652/assignments/968720) | Case Studies | Completion | 1 | Sat 2026-07-11 03:59 UTC | — |
| [Ed Discussion — Week 3](https://canvas.cornell.edu/courses/87652/assignments/968723) | Participation | Completion | 1 | Sat 2026-07-11 03:59 UTC | — |
| [Office Hours — Week 3](https://canvas.cornell.edu/courses/87652/assignments/968726) | Participation | Completion | 1 | Sat 2026-07-11 03:59 UTC | — |
| [Project Case Study — Submission 3 (final)](https://canvas.cornell.edu/courses/87652/assignments/968729) | Weekly Homework 3 · Project Case Study | Points | 100 | Sat 2026-07-11 03:59 UTC | — |
| [Final Presentation](https://canvas.cornell.edu/courses/87652/assignments/968730) | Final Presentation | Completion | 1 | Sat 2026-07-11 03:59 UTC | — |
| [Final Course Evaluation](https://canvas.cornell.edu/courses/87652/assignments/968733) | Participation | Completion | 1 | Sat 2026-07-11 03:59 UTC | — |

---

## `.canvas/README.md`

# `.canvas/` — Canvas course scaffolding for SYSEN 5470

Starter content for the Cornell **Canvas** site that mirrors the
[course website](https://timothyfraser.com/netsci/). The goal is deliberately
modest: Canvas should **cleanly structure submissions, deadlines, and links** —
and then send students to the (much nicer) website to actually do the work.

## What's here
- A **home page** with shortcut links to the key website pages.
- **32 assignments**, one per submission item across the **11 case studies**
  (each lab keeps its own spot in the course): a drawing and one **bundled
  Learning Check** per case study (the case-study check and the "I ran the code"
  check submitted together), plus a weekly Ed Discussion and Office Hours, three
  project case studies, and a final presentation.
- **5 modules** (Getting Started · Week 1 · Week 2 · Week 3 · Wrapping Up) of
  website links, kept non-duplicative with the assignments.
- Each assignment is a **branded HTML card** (matching the site's neon-green-on-
  near-black theme) with the assignment title, the related case study, a
  completion-vs-points grading tag, and a button to the relevant website page.
- **No due dates** — the cards don't mention them and the push script doesn't
  set them, so you schedule everything in Canvas and can move things freely.

Assignments are sorted into **weighted groups**: Drawings 20% · Case Studies
(the bundled learning checks) 25% · Participation (Ed discussion + office hours
+ final presentation) 10% · Weekly Homework (the project) ×3 = 45%. The Drawings
and Case Studies groups **drop each student's lowest 2 scores** — two freebies
per group for time-crunch weeks.

## Preview it (no Canvas needed)
Open **`preview.html`** in any browser — it renders every page and assignment
exactly as Canvas will display it.

## Publish it (needs your Canvas token)
Nothing here touches Canvas until you run the push script with a token. See
**`HANDOFF.md`** for the full, step-by-step guide. Short version:

```bash
cd .canvas
python3 scripts/generate_html.py          # rebuild HTML from manifest (optional; already built)
pip install requests
export CANVAS_BASE_URL=https://canvas.cornell.edu
export CANVAS_API_TOKEN=…                  # Canvas → Account → Settings → New Access Token
export CANVAS_COURSE_ID=…                  # the number in .../courses/<ID>
python3 scripts/push_to_canvas.py --dry-run   # preview every API call
python3 scripts/push_to_canvas.py             # publish (idempotent — safe to re-run)
```

## Edit the content
`manifest.json` is the single source of truth. Edit it, re-run
`scripts/generate_html.py`, then `scripts/push_to_canvas.py`. Don't hand-edit
files in `assignments/`, `pages/`, or `build/` — they're regenerated.

---

## `code/01_build-a-network/README.md`

# Case Study 01 — Build a Network

> Interactive lab: [`docs/case-studies/build-a-network.html`](../../docs/case-studies/build-a-network.html)
>
> Skill: **Identify** · Data: synthetic bipartite supplier ↔ component
> network (200 nodes, 577 edges)

**New to "bipartite"?** It just means the network has **two kinds of nodes**, and
edges only run *between* the kinds, never within. Here the kinds are suppliers and
components: a supplier links to the components it makes, but suppliers never link
directly to suppliers. The "one-mode projection" (below) collapses that into a
supplier-to-supplier network where two suppliers connect if they share a component.

## What you'll learn

How to take node and edge data sitting in two tables and turn them
into a real graph object you can compute on. Specifically:

- Load a node table and an edge table.
- Build an `igraph` object from them, in either R or Python.
- Check basic properties (number of vertices, edges, degree
  distribution).
- For a bipartite network (two kinds of nodes — suppliers and
  components), do a **one-mode projection** so you can ask
  "which suppliers are exposed to the same components."

This case is the *foundation* for every other case study in the
course. If you understand it, the rest are about *what to do once
you have a graph*.

## Prerequisites

- The case study lab: [Build a Network](../../docs/case-studies/build-a-network.html).
- R packages: `dplyr`, `readr`, `tibble`, `igraph`, `ggplot2`, `here`.
- Python packages: see [`code/requirements.txt`](../requirements.txt).

## Files in this folder

```
01_build-a-network/
├── README.md
├── example.R
├── example.py
├── functions.R
├── functions.py
└── data/
    ├── nodes.csv     # 200 nodes (80 suppliers + 120 components)
    ├── edges.csv     # 577 supplier->component ship-relationships
    └── _generate.py  # how the CSVs are made (deterministic, seeded)
```

## How to run

R:
```bash
Rscript code/01_build-a-network/example.R
```

Python:
```bash
python code/01_build-a-network/example.py
```

> **Run from the repo root.** These scripts resolve their data files with
> `here::here()` (R) and repo-relative paths (Python), so they behave the
> same on every machine — but only if your working directory is the repo
> root. A "file not found" error almost always means you're inside `code/`
> instead of at the top. (That's *why* the course uses `here::here()`: it
> pins paths to the project root instead of wherever you happened to launch.)

### Python note: building a graph from *string* node IDs

`igraph`'s `Graph.DataFrame()` expects **integer** vertex IDs. If your own
project data uses string names (e.g. `"E0004"`), it raises
`TypeError: ... must be 0-based integers`. Map names to integers first, then
keep the names as a vertex attribute:

```python
import igraph as ig

names = nodes["node_id"].tolist()
idx   = {name: i for i, name in enumerate(names)}      # string -> 0-based int
g = ig.Graph(
    n=len(names),
    edges=[(idx[a], idx[b]) for a, b in zip(edges["from_id"], edges["to_id"])],
    directed=False,
)
g.vs["name"] = names   # restore the original string IDs as a vertex attribute
```

(The lab's own `example.py` sidesteps this inside `functions.py`; you'll hit
it the first time you build *your own* network for the project.)

## Learning check (submit this number)

> **In the supplier-supplier one-mode projection, what is the degree of
> supplier `S017`?** (i.e. how many other suppliers share at least one
> component with `S017`?)

The number is printed at the bottom of either `example.R` or
`example.py`.

## Your Project Case Study

If you pick this case study as one of your project case studies, you'll
build a graph from *your own* data (≥ 100 nodes, ≥ 1,000 strongly
preferred), inspect basic structure, and — if your network has two
kinds of nodes — do a one-mode projection.

You'll submit:

1. `project.R` or `project.py` with the full pipeline.
2. A short report (2 pages minimum, your own words, not AI-generated)
   stating the question, the network's operationalization, the
   procedure, and results as numeric quantities of interest in prose
   with supporting tables/figures.

### Suggested project questions

Pick one.

1. **From data to graph.** Take a tabular dataset from your field
   that *isn't* obviously a graph (e.g. coauthorships, shipments,
   support tickets). Define what a node is, what an edge is, what
   the edge weight should be, and justify each choice in prose.
   Build the graph and report basic properties: N, E, density,
   degree distribution.

2. **Bipartite projection in your domain.** Find a real bipartite
   structure in your field (people↔projects, firms↔contracts,
   reviewers↔papers, doctors↔procedures). Build the bipartite
   graph; project it both ways; report what the projection reveals
   that the bipartite graph alone does not.

3. **Two encodings, two stories.** Take the same underlying data and
   build it as a graph in two different ways (e.g. directed vs
   undirected, weighted vs binary, thresholded at two different
   weights). Report which structural conclusions change and which
   are robust.

### What goes in the report

- **Question.** One sentence.
- **Network.** Nodes, edges, weights, where the data came from, basic
  size statistics.
- **Procedure.** What you did, in order, in plain language.
- **Results.** Quantities of interest as numbers in prose, supported
  by at most 2 figures and 1 table.
- **What this tells you, and what it doesn't.** 2-3 sentences.

## Further reading

- The next case study, [`02_joins`](../02_joins), assumes you already
  have edges and nodes in a graph and asks what to *do* with them.
- The sts course `24C_analytics.R` extends this idea into much
  larger committee-affiliation networks with `tidygraph`.

---

## `code/01_build-a-network/data/_generate.py`

```python
"""Generate the synthetic bipartite supplier <-> component network.

We want a deterministic small-but-not-tiny bipartite network so the
Build-a-Network case study has signal: ~80 suppliers, ~120 components,
~600 edges, with planted "shared supplier" patterns so the one-mode
projection (supplier x supplier via shared component) has interesting
structure.

Run once to regenerate the CSVs:

    python code/01_build-a-network/data/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

def main() -> None:
    rng = np.random.default_rng(SEED)

    n_suppliers  = 80
    n_components = 120

    # Suppliers belong to one of 4 regions; that biases which components
    # they ship (some components are regional specialties).
    suppliers = pd.DataFrame({
        "node_id": [f"S{i:03d}" for i in range(n_suppliers)],
        "kind":    "supplier",
        "region":  rng.choice(["NE", "SE", "MW", "W"], size=n_suppliers,
                              p=[0.35, 0.25, 0.25, 0.15]),
        "tier":    rng.choice([1, 2, 3], size=n_suppliers, p=[0.30, 0.45, 0.25]),
        "capacity_units": rng.integers(200, 2000, size=n_suppliers),
    })

    components = pd.DataFrame({
        "node_id": [f"C{i:03d}" for i in range(n_components)],
        "kind":    "component",
        "region":  rng.choice(["NE", "SE", "MW", "W", "ANY"],
                              size=n_components,
                              p=[0.15, 0.15, 0.15, 0.10, 0.45]),
        "tier":    pd.NA,
        "capacity_units": pd.NA,
    })

    nodes = pd.concat([suppliers, components], ignore_index=True)

    # Edges: for each supplier, pick K components to ship, biased toward
    # the supplier's region (or "ANY" region, which any supplier might
    # touch). This gives a planted block structure.
    edges_rows = []
    for _, sup in suppliers.iterrows():
        # how many components this supplier touches
        k = max(1, int(rng.normal(loc=7.5, scale=2.5)))
        # eligible components: same region OR "ANY"
        eligible = components.loc[
            (components["region"] == sup["region"]) |
            (components["region"] == "ANY"),
            "node_id"
        ].to_numpy()
        if len(eligible) < k:
            k = len(eligible)
        picks = rng.choice(eligible, size=k, replace=False)
        for c in picks:
            edges_rows.append({
                "from_id":      sup["node_id"],
                "to_id":        c,
                "volume_units": int(rng.integers(50, 400)),
            })

    edges = pd.DataFrame(edges_rows).sort_values(
        ["from_id", "to_id"]).reset_index(drop=True)

    nodes = nodes.sort_values("node_id").reset_index(drop=True)

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)

    print(f"wrote {HERE / 'nodes.csv'} ({len(nodes)} nodes)")
    print(f"wrote {HERE / 'edges.csv'} ({len(edges)} edges)")


if __name__ == "__main__":
    main()
```

---

## `code/01_build-a-network/example.R`

```r
#' @name example.R
#' @title Case Study 01 — Build a Network
#' @author <your-name-here>
#' @description
#'
#' You've used the interactive lab to drag nodes and draw edges. Now we
#' build a network from *real tables* and let the code do the rest.
#'
#' Our data is a synthetic bipartite supply network:
#'   - 80 suppliers (nodes of kind "supplier")
#'   - 120 components (nodes of kind "component")
#'   - ~577 ship-relationships (a supplier ships a component, weighted by volume)
#'
#' The goal:
#'   1. Get the node table and the edge table into shape.
#'   2. Turn them into a real graph object.
#'   3. Inspect basic structure (sizes, degree distribution).
#'   4. Project the bipartite graph to a one-mode supplier-by-supplier graph
#'      (two suppliers connected if they share a component) — this is
#'      where bipartite networks earn their keep.
#'   5. Find supplier-level structural patterns.


# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `dplyr` and `tibble` for tidy data wrangling. `igraph` is the workhorse
# network library for both R and Python. `here` resolves paths from the
# repo root so the script works no matter where you run it from.
library(dplyr)
library(readr)
library(tibble)
library(igraph)
library(ggplot2)
library(here)

# Heads-up: loading igraph (and others) prints "The following objects are
# masked from ..." messages. Those are NORMAL, not errors -- they just tell
# you which package's version of a same-named function now takes priority.
# Ignore them and keep going.

## 0.2 Load helpers ##########################################################

# `functions.R` lives next to this script and contains tiny wrappers
# around `read_csv()` plus a `build_bipartite()` helper. Open it once
# so you know what's behind each loader.
source(here::here("code", "01_build-a-network", "functions.R"))

# Friendly opening banner so you know the script is doing what it should.
cat("\n🚀 Case Study 01 — Build a Network (R)\n")
cat("   Two CSVs in -> one bipartite igraph object out -> a supplier projection.\n\n")

## 0.3 Load data #############################################################

# Two tables: a node list (one row per entity) and an edge list (one row
# per "this supplier ships that component" relationship).
nodes <- load_nodes()
edges <- load_edges()

# Always glance at the first few rows of any table before trusting it.
nodes |> head()
edges |> head()

# How many of each kind of node? How many edges? The `count()` shortcut
# is the dplyr way to do `group_by() |> summarize(n = n())` in one line.
nodes |> count(kind)
nrow(edges)

cat(sprintf("✅ Loaded %d nodes (%d suppliers + %d components) and %d edges.\n",
            nrow(nodes),
            sum(nodes$kind == "supplier"),
            sum(nodes$kind == "component"),
            nrow(edges)))


# 1. Build the graph #########################################################
#
# A graph is just a set of vertices and a set of edges connecting them.
# Our data is already in that shape; we just need to hand the two
# tables to igraph and ask it to wire them up.

## 1.1 The naive way (suppliers and components mixed) ########################

# `build_bipartite()` (defined in functions.R) does two things:
#   (a) calls `igraph::graph_from_data_frame()` to wire up the edges, and
#   (b) sets the bipartite `type` attribute on every vertex (FALSE for
#       suppliers, TRUE for components), which is what igraph needs to
#       know later that this graph is bipartite.
g <- build_bipartite(nodes, edges)

# Printing an igraph object gives you a one-line summary: vertex count,
# edge count, whether it's directed, and which attributes are attached.
g

## 1.2 Bipartite check #######################################################

# `bipartite_mapping()` returns `$res = TRUE` if igraph agrees with our
# manual labeling. A good sanity check.
is_bip <- igraph::bipartite_mapping(g)$res
cat(sprintf("✅ Bipartite? %s\n", if (is_bip) "True" else "False"))

# Diagnostic: which logical `type` maps to which kind of node? Print the
# cross-tab so you never have to guess (or trace functions.R) when you read
# off proj1 vs proj2 later. FALSE = suppliers, TRUE = components.
print(table(kind = igraph::V(g)$kind, type = igraph::V(g)$type))


# 2. Inspect basic structure #################################################

## 2.1 Degree distribution by kind ###########################################

# Each node's degree is just "how many edges touch it." We bundle the
# three vertex attributes into one tidy tibble for easy summarizing.
degrees <- tibble::tibble(
  node_id = igraph::V(g)$name,
  kind    = igraph::V(g)$kind,
  degree  = igraph::degree(g)
)

# Suppliers tend to touch ~5-10 components; components are touched by
# anywhere from 1 to ~20 suppliers. Compare the two distributions.
deg_summary <- degrees |>
  group_by(kind) |>
  summarize(
    n      = n(),
    mean   = mean(degree),
    median = median(degree),
    min    = min(degree),
    max    = max(degree),
    .groups = "drop"
  )
print(deg_summary)
cat(sprintf("📊 Mean supplier degree: %.1f   Mean component degree: %.1f\n",
            mean(degrees$degree[degrees$kind == "supplier"]),
            mean(degrees$degree[degrees$kind == "component"])))

## 2.2 Top-degree components (the "shared" ones) #############################

# Which components have the most suppliers shipping them? These are
# the structural pivot points in a one-mode projection — when they
# go offline, many suppliers go offline together.
top_shared <- degrees |>
  filter(kind == "component") |>
  arrange(desc(degree)) |>
  head(10)
print(top_shared)


# 3. Bipartite projection ####################################################
#
# The interesting question in a bipartite supply network usually isn't
# "which supplier ships which component" — it's "which suppliers are
# co-exposed because they share a component." If component C037 goes
# offline, every supplier that depends on it is in trouble together.
#
# A bipartite projection answers exactly that. It produces two graphs:
#   - supplier-by-supplier: two suppliers linked if they share >=1 component
#   - component-by-component: two components linked if they share >=1 supplier
# Order matters and trips people up: proj1 is the `type=FALSE` side and
# proj2 the `type=TRUE` side. Here type=FALSE is suppliers. If yours comes
# out swapped, check the `type` vertex attribute rather than the order.

proj <- igraph::bipartite_projection(g)
proj_suppliers  <- proj$proj1   # the "FALSE" side — suppliers
proj_components <- proj$proj2   # the "TRUE"  side — components
proj_suppliers
proj_components

cat(sprintf("🔗 Supplier projection:  %d nodes, %d edges\n",
            igraph::vcount(proj_suppliers),  igraph::ecount(proj_suppliers)))
cat(sprintf("🔗 Component projection: %d nodes, %d edges\n",
            igraph::vcount(proj_components), igraph::ecount(proj_components)))

# Each edge in the suppliers projection has a `weight` attribute equal
# to the NUMBER OF SHARED COMPONENTS between those two suppliers. That
# weight is the closest thing to a "shared-fate" score we get here.

## 3.1 Top supplier-supplier exposures #######################################

# Convert the projection back to a tidy edge-list so we can sort and
# explore it like any other dataframe.
proj_edges <- igraph::as_data_frame(proj_suppliers, what = "edges") |>
  as_tibble() |>
  rename(shared_components = weight) |>
  arrange(desc(shared_components))

# The top of this list is the pair of suppliers most exposed to each
# other — if one is disrupted, the other is most likely to be co-disrupted.
print(proj_edges |> head(10))


# 4. Visualize ###############################################################
#
# A bipartite layout puts suppliers on one side, components on the
# other. It's not always the prettiest layout, but it's the most honest
# rendering of a bipartite graph: you can read off the structure
# without thinking about it.

# Wrap the plotting call so we can draw it once to the screen (RStudio /
# in-browser R session) AND save a copy to a PNG you can open from a file
# browser. Running from `Rscript` otherwise dumps plots into Rplots.pdf,
# which is easy to miss.
draw_bipartite <- function() {
  plot(
    g,
    layout       = igraph::layout_as_bipartite(g),
    vertex.size  = ifelse(igraph::V(g)$kind == "supplier", 4, 2.5),
    vertex.color = ifelse(igraph::V(g)$kind == "supplier", "#1f77b4", "#d62728"),
    vertex.label = NA,
    edge.color   = "#cccccc",
    edge.width   = 0.4,
    main         = "Bipartite supplier <-> component network"
  )
}

# Draw interactively (visible in RStudio / the in-browser R session)...
draw_bipartite()

# ...and also save a copy to file for terminal / Rscript users.
png(here::here("code", "01_build-a-network", "bipartite_network.png"),
    width = 7, height = 5, units = "in", res = 120)
draw_bipartite()
invisible(dev.off())
cat("💾 Saved bipartite_network.png\n")


# 5. Learning Check ##########################################################
#
# QUESTION: In the supplier-supplier projection (where two suppliers are
# linked if they share at least one component), what is the degree of
# supplier "S017"? Put differently: how many *other* suppliers share at
# least one component with S017?

# `V(g)$name == "S017"` returns a logical vector; `which()` gives us
# the integer index igraph needs.
s017   <- which(igraph::V(proj_suppliers)$name == "S017")
answer <- igraph::degree(proj_suppliers, v = s017)

cat(sprintf("\n📝 Learning Check answer: %d\n", answer))

cat("\n🎉 Done. Move on to the case study report when you're ready.\n")
```

---

## `code/01_build-a-network/example.py`

```python
"""Case Study 01 — Build a Network (Python track).

You've used the interactive lab to drag nodes and draw edges. Now we
build a network from *real tables* and let the code do the rest.

Our data is a synthetic bipartite supply network:
  - 80 suppliers (nodes of kind "supplier")
  - 120 components (nodes of kind "component")
  - 577 ship-relationships (a supplier ships a component, weighted by volume)

The goal:

  1. Get the node table and the edge table into shape.
  2. Turn them into a real graph object.
  3. Inspect basic structure (sizes, degree distribution).
  4. Project the bipartite graph to a one-mode supplier-by-supplier graph
     (two suppliers connected if they share a component) — this is
     where bipartite networks earn their keep.
  5. Find supplier-level structural patterns.
"""

# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `pandas` for tidy data wrangling, `igraph` is the workhorse network
# library for both R and Python. `matplotlib` for the static figure
# (we save it to PNG so users without a display can still see it).
import pandas as pd
import numpy as np
import igraph as ig
import matplotlib.pyplot as plt

## 0.2 Load helpers ##########################################################

# `functions.py` sits next to this script. Open it once so you know
# what each loader is doing — they're tiny wrappers around `read_csv`.
from functions import load_nodes, load_edges, build_bipartite

# Friendly opening banner so you know the script is doing what it should.
print("\n🚀 Case Study 01 — Build a Network (Python)")
print("   Two CSVs in -> one bipartite igraph object out -> a supplier projection.\n")

## 0.3 Load data #############################################################

# Two tables: a node list (one row per entity) and an edge list (one row
# per "this supplier ships that component" relationship).
nodes = load_nodes()
edges = load_edges()

# Always glance at the first few rows of any table before trusting it.
print(nodes.head())
print(edges.head())

# How many of each kind of node? How many edges?
print(nodes["kind"].value_counts())
print(f"{len(edges):,} edges")

print(
    f"✅ Loaded {len(nodes)} nodes "
    f"({(nodes['kind']=='supplier').sum()} suppliers + "
    f"{(nodes['kind']=='component').sum()} components) and {len(edges)} edges."
)


# 1. Build the graph #########################################################
#
# A graph is just a set of vertices and a set of edges connecting them.
# Our data is already in that shape; we just need to hand the two
# tables to igraph and ask it to wire them up.

## 1.1 The naive way (suppliers and components mixed) ########################

# `build_bipartite()` (defined in functions.py) does two things:
#   (a) builds the graph from the edge list, and
#   (b) sets the bipartite `type` attribute on every vertex (False for
#       suppliers, True for components), which is what igraph needs to
#       know later that this graph is bipartite.
g = build_bipartite(nodes, edges)

# `summary()` gives a one-line dump: <number of vertices>, <number of
# edges>, directed flag, plus the attribute names.
print(g.summary())

## 1.2 Bipartite check #######################################################

# A quick sanity check that igraph agrees with our manual labeling.
is_bip, _types = g.is_bipartite(return_types=True)
print(f"✅ Bipartite? {is_bip}")


# 2. Inspect basic structure #################################################

## 2.1 Degree distribution by kind ###########################################

# Each node's degree is just "how many edges touch it." We bundle the
# three vertex attributes into one tidy DataFrame for easy summarizing.
degrees = pd.DataFrame({
    "node_id": g.vs["name"],
    "kind":    g.vs["kind"],
    "degree":  g.degree(),
})

# Suppliers tend to touch ~5-10 components; components are touched by
# anywhere from 1 to ~20 suppliers. Compare the two distributions.
print(degrees.groupby("kind")["degree"].describe())
sup_mean = degrees.loc[degrees["kind"] == "supplier",  "degree"].mean()
cmp_mean = degrees.loc[degrees["kind"] == "component", "degree"].mean()
print(f"📊 Mean supplier degree: {sup_mean:.1f}   Mean component degree: {cmp_mean:.1f}")

## 2.2 Top-degree components (the "shared" ones) #############################

# Which components have the most suppliers shipping them? These are
# the structural pivot points in a one-mode projection — when they
# go offline, many suppliers go offline together.
top_shared = (
    degrees.query("kind == 'component'")
    .sort_values("degree", ascending=False)
    .head(10)
)
print(top_shared)


# 3. Bipartite projection ####################################################
#
# The interesting question in a bipartite supply network usually isn't
# "which supplier ships which component" — it's "which suppliers are
# co-exposed because they share a component." If component C037 goes
# offline, every supplier that depends on it is in trouble together.
#
# A bipartite projection answers exactly that. It produces two graphs:
#   - supplier-by-supplier: two suppliers linked if they share >=1 component
#   - component-by-component: two components linked if they share >=1 supplier
# Order matters and trips people up: index 0 is the projection of the
# `type=False` side and index 1 the `type=True` side. Here type=False is
# suppliers, so index 0 = suppliers. If yours comes out swapped, check the
# `type` vertex attribute rather than assuming the order.

proj_suppliers, proj_components = g.bipartite_projection()
print(f"🔗 Supplier projection:  {proj_suppliers.vcount()} nodes, {proj_suppliers.ecount()} edges")
print(f"🔗 Component projection: {proj_components.vcount()} nodes, {proj_components.ecount()} edges")

# Each edge in the suppliers projection has a `weight` attribute equal
# to the NUMBER OF SHARED COMPONENTS between those two suppliers. That
# weight is the closest thing to a "shared-fate" score we get here.

## 3.1 Top supplier-supplier exposures #######################################

# Convert the projection back to a tidy edge-list so we can sort and
# explore it like any other DataFrame.
proj_edges = pd.DataFrame({
    "from": [proj_suppliers.vs[e.source]["name"] for e in proj_suppliers.es],
    "to":   [proj_suppliers.vs[e.target]["name"] for e in proj_suppliers.es],
    "shared_components": proj_suppliers.es["weight"],
})

# The top of this list is the pair of suppliers most exposed to each
# other — if one is disrupted, the other is most likely to be co-disrupted.
print(proj_edges.sort_values("shared_components", ascending=False).head(10))


# 4. Visualize ###############################################################
#
# A bipartite layout puts suppliers on one side, components on the
# other. It's not always the prettiest layout, but it's the most honest
# rendering of a bipartite graph: you can read off the structure
# without thinking about it.

layout = g.layout_bipartite(types=g.vs["type"])
fig, ax = plt.subplots(figsize=(11, 7))
node_color = ["#1f77b4" if k == "supplier" else "#d62728" for k in g.vs["kind"]]
node_size  = [40 if k == "supplier" else 20 for k in g.vs["kind"]]
xs = [pt[0] for pt in layout.coords]
ys = [pt[1] for pt in layout.coords]
for e in g.es:
    x0, y0 = layout.coords[e.source]
    x1, y1 = layout.coords[e.target]
    ax.plot([x0, x1], [y0, y1], color="grey", alpha=0.15, linewidth=0.4)
ax.scatter(xs, ys, c=node_color, s=node_size, edgecolors="white", linewidths=0.3)
ax.set_axis_off()
ax.set_title("Bipartite supplier <-> component network")
fig.tight_layout()
fig.savefig("build_bipartite.png", dpi=120)
plt.close(fig)
print("💾 Saved build_bipartite.png")


# 5. Learning Check ##########################################################
#
# QUESTION: In the supplier-supplier projection (where two suppliers are
# linked if they share at least one component), what is the degree of
# supplier "S017"? Put differently: how many *other* suppliers share at
# least one component with S017?

s017_idx = proj_suppliers.vs.find(name="S017").index
answer = proj_suppliers.degree(s017_idx)

print(f"\n📝 Learning Check answer: {answer}")

print("\n🎉 Done. Move on to the case study report when you're ready.")
```

---

## `code/01_build-a-network/functions.R`

```r
#' @name functions.R
#' @title Helpers for the Build-a-Network case study
#' @description
#'
#' Tiny wrappers around `read_csv()` that resolve paths for us, plus a
#' single helper that takes the node + edge tables and returns an
#' `igraph` object built the "right" way (bipartite, with `kind` tagged
#' on as a vertex attribute).

library(readr)
library(dplyr)
library(igraph)
library(here)

.case_dir <- function() here::here("code", "01_build-a-network", "data")

#' Load the node table.
load_nodes <- function() {
  readr::read_csv(file.path(.case_dir(), "nodes.csv"), show_col_types = FALSE)
}

#' Load the edge table.
load_edges <- function() {
  readr::read_csv(file.path(.case_dir(), "edges.csv"), show_col_types = FALSE)
}

#' Build an igraph bipartite graph from node + edge tables.
#'
#' Sets `type = TRUE` for components and `type = FALSE` for suppliers,
#' which is the convention igraph uses to flag a bipartite graph.
build_bipartite <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- igraph::graph_from_data_frame(
    d = edges |> select(from_id, to_id, volume_units),
    directed = FALSE,
    vertices = nodes |> select(node_id, kind, region, tier, capacity_units)
  )
  igraph::V(g)$type <- igraph::V(g)$kind == "component"
  g
}
```

---

## `code/01_build-a-network/functions.py`

```python
"""Helpers for the Build-a-Network case study.

Tiny wrappers around ``pd.read_csv()`` that resolve paths for us, plus
a single helper that takes the node + edge tables and returns an
``igraph.Graph`` built the "right" way (bipartite, with ``kind`` tagged
on as a vertex attribute).
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig


def _case_dir() -> Path:
    return Path(__file__).resolve().parent / "data"


def load_nodes() -> pd.DataFrame:
    return pd.read_csv(_case_dir() / "nodes.csv")


def load_edges() -> pd.DataFrame:
    return pd.read_csv(_case_dir() / "edges.csv")


def build_bipartite(nodes: pd.DataFrame | None = None,
                    edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build an igraph bipartite graph from node + edge tables.

    Sets ``type = True`` for components and ``type = False`` for
    suppliers, which is the convention igraph uses to flag a
    bipartite graph.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()

    g = ig.Graph.DataFrame(
        edges=edges[["from_id", "to_id", "volume_units"]],
        directed=False,
        vertices=nodes[["node_id", "kind", "region", "tier", "capacity_units"]],
        use_vids=False,
    )
    g.vs["type"] = [k == "component" for k in g.vs["kind"]]
    return g
```

---

## `code/02_joins/README.md`

# Case Study 02 — Network Joins

> Interactive lab: [`docs/case-studies/joins.html`](../../docs/case-studies/joins.html)
>
> Skill: **Identify** · Data: slim Bluebikes-flavored sample (synthetic but
> deterministic — same answer for everyone)

## What you'll learn

When a network's edges live in one table and its node traits live in
another, the JOIN is where the real analysis happens. This case walks
you through:

- a **single-node join** (tagging each edge with a trait of its *start*
  node),
- a **double-node join** (start *and* end, with proper renames so the
  two attributes don't collide),
- aggregating the joined edges to a small 2×2 quantity of interest,
- and a 2×2 heatmap that communicates the result honestly.

If you can do this fluently, you can do 80% of all network analysis on
big tabular data without reaching for anything fancier.

## Prerequisites

- The case study lab: [Network Joins](../../docs/case-studies/joins.html).
- R packages: `dplyr`, `readr`, `ggplot2`, `here`.
- Python packages: see [`code/requirements.txt`](../requirements.txt) —
  you need `pandas`, `pyarrow`, `matplotlib`, `seaborn`.

## Files in this folder

```
02_joins/
├── README.md         # this file
├── example.R         # R track: do the joins with dplyr
├── example.py        # Python track: do the joins with pandas
├── functions.R       # tiny path-resolved data loaders for R
├── functions.py      # tiny path-resolved data loaders for Python
└── data/
    ├── edges.csv     # ~50,000 AM rush 2021 trip rows
    ├── stations.csv  # ~500 stations with a maj_black flag
    └── _generate.py      # how the parquet files are made (deterministic)
```

## How to run

R:
```bash
Rscript code/02_joins/example.R
```

Python:
```bash
python code/02_joins/example.py
```

Both should finish in well under 10 seconds and produce the same
Learning Check answer.

## Learning check (submit this number)

> **How many AM rush rides in 2021 in this slim sample started AND
> ended in a majority-Black block group?**

The number is printed at the bottom of either `example.R` or
`example.py`. Put it into the learning-check form on the website.

## Your Project Case Study

If you pick this case study as one of your project case studies, you'll
apply the join-and-aggregate pattern to **your own network** (≥ 100
nodes, ≥ 1,000 strongly preferred). You'll submit:

1. A `project.R` *or* `project.py` that runs your full analysis,
2. A short report (2 pages minimum, your own words — not AI-generated)
   that states the question, your operationalization of the network,
   the procedure, and the results as numeric quantities of interest in
   prose, with supporting tables/figures.

### Suggested project questions

Pick one. Each is a real question this method can answer.

1. **Attribute homophily on edges.** Take a categorical node attribute
   that matters in your domain (firm tier, region, race, department,
   product line). Do a double-node join, then compute the 2×2 (or
   n×n) "what % of edge weight stays within-group vs crosses
   groups." Report the four/N² percentages with a heatmap.

2. **Aggregate-before-join vs join-before-aggregate.** Demonstrate the
   speed and memory difference between (a) joining all node traits
   onto every edge and *then* aggregating, vs (b) aggregating first
   and joining a small result. Report wall-clock time and peak rows
   in memory for each pipeline.

3. **Silent collision audit.** Take an edge table and join it with two
   different node attributes from the same node table. Show what
   happens when you forget to rename. Then show the renamed version
   side-by-side. Report which one you'd want to debug a year from
   now.

You don't have to write all three. Pick the one that fits your
network best.

### What goes in the report

- **Question.** One sentence stating what you set out to learn.
- **Network.** What are the nodes? What are the edges? Where did
  the data come from? How many nodes, how many edges, how dense?
- **Procedure.** The steps you ran, in plain language. Why those
  steps, in that order.
- **Results.** State the quantities of interest *as numbers, in
  prose*. Support with at most 2 figures and 1 table.
- **What this tells you, and what it doesn't.** Two-three sentences.

## Further reading

- The sts course `21C_databases.R` script extends this idea to a
  multi-million-row SQLite database with `dbplyr`. If your network
  data lives in SQL, that's worth reading.
- The next case study, [`03_aggregation`](../03_aggregation), reuses
  this exact dataset to show how the same joined table can be viewed
  at three resolutions.

---

## `code/02_joins/data/_generate.py`

```python
"""Generate the slim Bluebikes-flavored data files for case 02 (joins).

This produces a small but realistic stand-in for the real Bluebikes SQLite
that lessons 21C/22C of the sts course use. We don't ship the multi-GB
SQLite in this repo; instead, we generate ~500 stations and ~50,000 AM
rush-hour trip rows, deterministically, so the join exercise has signal.

Run once to regenerate the parquet files:

    python code/02_joins/data/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

def main() -> None:
    rng = np.random.default_rng(SEED)

    # ----- stations -----------------------------------------------------------
    # 500 stations spread across 5 "neighborhood clusters" (block groups).
    # We give some clusters higher Black-majority probability and others
    # lower, so the demographic join produces non-trivial cross-class counts.
    n_stations = 500
    cluster_id = rng.integers(0, 5, size=n_stations)
    # cluster 0,1: majority Black; cluster 2,3,4: not
    p_maj_black = np.array([0.85, 0.65, 0.10, 0.05, 0.02])[cluster_id]
    maj_black = np.where(rng.random(n_stations) < p_maj_black, "yes", "no")

    stations = pd.DataFrame({
        "code":      [f"S{idx:04d}" for idx in range(n_stations)],
        "cluster":   cluster_id,
        "maj_black": maj_black,
        # rough Boston-area lat/lon, jittered per cluster
        "x": (-71.10 + (cluster_id - 2) * 0.02
              + rng.normal(0, 0.01, n_stations)),
        "y": (42.34 + (cluster_id - 2) * 0.01
              + rng.normal(0, 0.008, n_stations)),
    })

    # ----- edges --------------------------------------------------------------
    # AM rush, year 2021. We sample 50,000 (start, end, day) triples
    # with assortative bias: trips are more likely within the same cluster.
    n_edges = 50_000

    # day strings YYYY-MM-DD across 2021
    days = pd.date_range("2021-01-01", "2021-12-31", freq="D").strftime("%Y-%m-%d").to_numpy()

    # pick a start station uniformly
    start_idx = rng.integers(0, n_stations, size=n_edges)
    # pick an end station with bias toward the same cluster
    same_cluster = rng.random(n_edges) < 0.70  # 70% within-cluster
    end_idx = np.where(
        same_cluster,
        # within-cluster: sample uniformly among stations in the same cluster
        np.array([rng.choice(np.flatnonzero(cluster_id == cluster_id[s]))
                  for s in start_idx]),
        # across-cluster: pick any
        rng.integers(0, n_stations, size=n_edges),
    )

    edges = pd.DataFrame({
        "start_code": stations["code"].to_numpy()[start_idx],
        "end_code":   stations["code"].to_numpy()[end_idx],
        "day":        rng.choice(days, size=n_edges),
        "rush":       "am",
        "count":      rng.integers(1, 8, size=n_edges),
    })

    # sort for nicer git diffs
    edges = edges.sort_values(["day", "start_code", "end_code"]).reset_index(drop=True)
    stations = stations.sort_values("code").reset_index(drop=True)

    edges.to_csv(HERE / "edges.csv", index=False)
    stations.to_csv(HERE / "stations.csv", index=False)

    print(f"wrote {HERE / 'edges.csv'}  ({len(edges):,} rows)")
    print(f"wrote {HERE / 'stations.csv'} ({len(stations):,} rows)")


if __name__ == "__main__":
    main()
```

---

## `code/02_joins/example.R`

```r
#' @name example.R
#' @title Case Study 02 — Network Joins
#' @author <your-name-here>
#' @description
#'
#' You've worked through the Network Joins lab in the browser. Now
#' let's run the same idea on real(ish) data: a slim, Bluebikes-flavored
#' AM-rush-hour-trips edge list (~50,000 rows) and a stations node table
#' (~500 rows) that's been annotated with a demographic flag from the
#' census block group each station sits in.
#'
#' The whole point of this case study: when you have edges and nodes
#' in two separate tables, the way you JOIN them dictates what you can
#' say about the network. We'll do a single-node join, then a
#' double-node join (start *and* end), then aggregate the result to
#' get a quantity of interest. Pay attention to the *renames* — they
#' are not optional polish, they are the thing that keeps you from
#' silently shooting yourself in the foot.


# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `dplyr` is the workhorse for joins. `readr` reads the CSVs (with
# better defaults than base `read.csv`). The rest are visuals and paths.
library(dplyr)
library(readr)
library(tibble)
library(ggplot2)
library(here)
library(stringr)

## 0.2 Load helpers ##########################################################

# Tiny `load_edges()` / `load_stations()` wrappers that resolve paths
# from the repo root so the script runs from anywhere.
source(here::here("code", "02_joins", "functions.R"))

cat("\n🚀 Case Study 02 — Network Joins (R)\n")
cat("   Edges + stations -> single join, then double join, then a quantity of interest.\n\n")

## 0.3 Load data #############################################################

# Two tables: one for edges (one row per trip aggregate) and one for
# nodes (one row per station, with demographic annotation).
edges    <- load_edges()
stations <- load_stations()

# Get used to running head() before doing anything else. The columns:
#   start_code: where the trip started (station ID)
#   end_code:   where the trip ended (station ID)
#   day:        the day the trip happened (YYYY-MM-DD)
#   rush:       "am" — we've already filtered to AM rush
#   count:      number of trips matching this start/end/day combination
edges |> head()

# Stations table columns:
#   code:      station ID (joins to start_code / end_code in edges)
#   cluster:   neighborhood cluster (block group)
#   maj_black: "yes"/"no" — is the station in a majority-Black block group?
#   x, y:      longitude / latitude
stations |> head()

# How big is each table?
nrow(edges)
nrow(stations)
cat(sprintf("✅ Loaded %d trip rows and %d stations.\n", nrow(edges), nrow(stations)))
# Heads-up on "rows" vs "trips": each row is an AGGREGATE (a start/end/day
# combination), and the `count` column holds how many trips it represents.
# So total trips = sum(count), which is much larger than the row count.
cat(sprintf("ℹ️  %d rows are aggregates; total trips = sum(count) = %d.\n",
            nrow(edges), sum(edges$count, na.rm = TRUE)))


# 1. Single-Node Join ########################################################
#
# Goal: tag each edge with a TRAIT of its START station — was it in a
# majority-Black block group or not?

## 1.1 The basic left_join ###################################################

# The key insight: the ID variable has a different NAME in each table.
#   - in `edges` it's called `start_code`
#   - in `stations` it's called `code`
# In dplyr we say `by = c("start_code" = "code")`. Read the direction like
# this: the name on the LEFT of `=` is the column in the LEFT (first) table,
# the name on the RIGHT is the column in the RIGHT table. It looks like an
# assignment but it isn't -- it's just "match this column to that column."
edges |>
  left_join(by = c("start_code" = "code"), y = stations) |>
  head()

# That joined in EVERY column from stations. Usually too much.
# Better: subset stations to just what you need BEFORE joining. It
# makes the result table easier to read and saves memory on big joins.
edges |>
  left_join(
    by = c("start_code" = "code"),
    y  = stations |> select(code, maj_black)
  ) |>
  head()

## 1.2 Rename on the way in ##################################################

# After the join above, `maj_black` is still ambiguous — is it the
# start station's demographic or the end station's? Rename it to
# `start_black` *as part of* the select() inside the join. This
# habit will save you 20 minutes of "wait, which side was this?"
# confusion later.

edges_with_start <- edges |>
  left_join(
    by = c("start_code" = "code"),
    y  = stations |> select(code, start_black = maj_black)
  )

edges_with_start |> head()

## 1.3 A first quantity of interest ##########################################

# Of all AM rush rides in 2021, how many started in a majority-Black
# block group?
edges_with_start |>
  group_by(start_black) |>
  summarize(trips = sum(count, na.rm = TRUE)) |>
  ungroup()
# Rows where `start_black` is NA mean the START station wasn't in our
# stations table — i.e. it's outside Boston proper. In the real
# Bluebikes data these are Cambridge / Somerville stations.


# 2. Double-Node Join ########################################################
#
# Now we want to know about BOTH ends of the trip. We do a SECOND join
# on `end_code`, and we rename again so the two demographics don't
# clobber each other.

## 2.1 Two joins, two renames ################################################

data <- edges |>
  # join in the START station's trait...
  left_join(
    by = c("start_code" = "code"),
    y  = stations |> select(code, start_black = maj_black)
  ) |>
  # ...then join in the END station's trait.
  left_join(
    by = c("end_code" = "code"),
    y  = stations |> select(code, end_black = maj_black)
  ) |>
  # Drop rows where either side is NA — these are stations not in
  # our stations table (out-of-area).
  filter(!is.na(start_black), !is.na(end_black))

data |> head()
cat(sprintf("✅ After double-join + NA drop: %d rows.\n", nrow(data)))

# How much did the NA drop actually remove? Report it as a share of TRIPS
# (not rows), so you know whether dropping out-of-area stations is a rounding
# error or a meaningful chunk of the data you're about to summarize.
trips_all     <- sum(edges$count, na.rm = TRUE)
trips_kept    <- sum(data$count,  na.rm = TRUE)
pct_dropped   <- 100 * (trips_all - trips_kept) / trips_all
cat(sprintf("ℹ️  NA-drop removed %.1f%% of all trips (out-of-area stations).\n",
            pct_dropped))

## 2.2 An aggregate quantity of interest #####################################

# How many trips happened between EACH of the four demographic
# combinations (yes->yes, yes->no, no->yes, no->no)?
stat <- data |>
  group_by(start_black, end_black) |>
  summarize(trips = sum(count, na.rm = TRUE), .groups = "drop") |>
  mutate(
    total   = sum(trips),
    percent = round(100 * trips / total, 1)
  )

print(stat)
cat(sprintf("📊 Total trips across all four cells: %d\n", sum(stat$trips)))


# 3. A quick visual ##########################################################
#
# A 2x2 heatmap of trips by start-demographic x end-demographic. This
# is the simplest possible "network communication" visualization, and
# it's often the most honest one.

p <- ggplot(stat, aes(x = start_black, y = end_black, fill = percent)) +
  geom_tile(color = "white") +
  geom_text(aes(label = percent), color = "white", size = 6) +
  scale_fill_viridis_c(option = "mako", begin = 0.2, end = 0.8) +
  labs(
    x        = "Starting station\nin majority-Black block group?",
    y        = "Ending station\nin majority-Black block group?",
    fill     = "% of trips",
    subtitle = "AM rush 2021 — slim Bluebikes-flavored sample"
  ) +
  theme_classic(base_size = 13)

# print() shows it in an interactive / in-browser session; ggsave() also
# writes a file so terminal / Rscript users aren't left hunting in Rplots.pdf.
print(p)
ggsave(here::here("code", "02_joins", "demographic_flows.png"),
       p, width = 6, height = 5, dpi = 120)
cat("💾 Saved demographic_flows.png\n")


# 4. Why renames matter (the silent-bug demo) ################################
#
# To drive the point home: try the same double-join WITHOUT renaming
# `maj_black`. What does dplyr do? It auto-suffixes them as `.x` and `.y`,
# which (a) is ugly, and (b) means you can't tell at a glance which side
# is which.

bad <- edges |>
  left_join(stations |> select(code, maj_black),
            by = c("start_code" = "code")) |>
  left_join(stations |> select(code, maj_black),
            by = c("end_code"   = "code"))

bad |> head()
# Notice `maj_black.x` and `maj_black.y`. You can survive this, but
# in any non-trivial pipeline it's a recipe for misreading your own
# code in two weeks. Rename on the way in.


# 5. Learning Check ##########################################################
#
# QUESTION: Of AM rush rides in 2021 in this slim dataset, how many
# trips started in a majority-Black block group AND ended in a
# majority-Black block group?
#
# HINT: you've already computed `stat` above. Find the row where
# start_black == "yes" and end_black == "yes" and read off `trips`.

answer <- stat |>
  filter(start_black == "yes", end_black == "yes") |>
  pull(trips)

cat(sprintf("\n📝 Learning Check answer: %d\n", answer))

# Reminder: this is a synthetic-but-deterministic dataset. Your answer
# should be the SAME as your classmates'. If it isn't, your random
# seed has drifted somewhere.

cat("\n🎉 Done. Move on to the case study report when you're ready.\n")
```

---

## `code/02_joins/example.py`

```python
"""Case Study 02 — Network Joins (Python track).

You've worked through the Network Joins lab in the browser. Now let's
run the same idea on real(ish) data: a slim, Bluebikes-flavored
AM-rush-hour-trips edge list (~50,000 rows) and a stations node table
(~500 rows) that's been annotated with a demographic flag from the
census block group each station sits in.

The whole point of this case study: when you have edges and nodes in
two separate tables, the way you JOIN them dictates what you can say
about the network. We'll do a single-node join, then a double-node
join (start *and* end), then aggregate the result to get a quantity of
interest. Pay attention to the *renames* — they are not optional
polish, they are the thing that keeps you from silently shooting
yourself in the foot.
"""

# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `pandas` is the workhorse for joins. `seaborn` + `matplotlib` for the
# heatmap at the end.
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

## 0.2 Load helpers ##########################################################

# Tiny wrappers around pd.read_csv that resolve paths from the repo root.
from functions import load_edges, load_stations

print("\n🚀 Case Study 02 — Network Joins (Python)")
print("   Edges + stations -> single join, then double join, then a quantity of interest.\n")

## 0.3 Load data #############################################################

# Two tables: one for edges (one row per trip aggregate), one for
# nodes (one row per station, with demographic annotation).
edges    = load_edges()
stations = load_stations()

# Get used to running .head() before doing anything else. The columns:
#   start_code: where the trip started (station ID)
#   end_code:   where the trip ended (station ID)
#   day:        the day the trip happened (YYYY-MM-DD)
#   rush:       "am" — we've already filtered to AM rush
#   count:      number of trips matching this start/end/day combination
print(edges.head())

# Stations table columns:
#   code:      station ID (merges to start_code / end_code in edges)
#   cluster:   neighborhood cluster (block group)
#   maj_black: "yes"/"no" — is the station in a majority-Black block group?
#   x, y:      longitude / latitude
print(stations.head())

# How big is each table?
print(len(edges), "edges")
print(len(stations), "stations")
print(f"✅ Loaded {len(edges)} trip rows and {len(stations)} stations.")


# 1. Single-Node Join ########################################################
#
# Goal: tag each edge with a TRAIT of its START station — was it in a
# majority-Black block group or not?

## 1.1 The basic merge #######################################################

# The key insight: the ID variable has a different NAME in each table.
#   - in `edges` it's called `start_code`
#   - in `stations` it's called `code`
# In pandas we say  left_on="start_code", right_on="code"  (or rename
# `code` -> `start_code` first, which is what most pipelines do). The names
# say it plainly: left_on is the column in the LEFT (first) table, right_on
# is the column in the RIGHT table. (R's dplyr writes the same idea as
# by = c("start_code" = "code") -- left name = left table, right = right.)
print(
    edges
    .merge(stations, left_on="start_code", right_on="code", how="left")
    .head()
)

# That joined in EVERY column from stations. Usually too much.
# Better: subset stations to just what you need BEFORE joining. Easier
# to read AND saves memory on big joins.
print(
    edges
    .merge(stations[["code", "maj_black"]],
           left_on="start_code", right_on="code", how="left")
    .head()
)

## 1.2 Rename on the way in ##################################################

# After the merge above, `maj_black` is still ambiguous — is it the
# start station's demographic or the end station's? Rename it to
# `start_black` *as part of* the merge. This habit will save you 20
# minutes of "wait, which side was this?" confusion later.

edges_with_start = edges.merge(
    stations[["code", "maj_black"]].rename(
        columns={"code": "start_code", "maj_black": "start_black"}),
    on="start_code", how="left")

print(edges_with_start.head())

## 1.3 A first quantity of interest ##########################################

# Of all AM rush rides in 2021, how many started in a majority-Black
# block group?
print(
    edges_with_start
    .groupby("start_black", dropna=False)["count"]
    .sum()
    .reset_index(name="trips")
)
# Rows where `start_black` is NaN mean the START station wasn't in
# our stations table — i.e. it's outside Boston proper. In the real
# Bluebikes data these are Cambridge / Somerville stations.


# 2. Double-Node Join ########################################################
#
# Now we want to know about BOTH ends of the trip. We do a SECOND merge
# on `end_code`, and we rename again so the two demographics don't
# clobber each other.

## 2.1 Two merges, two renames ###############################################

data = (
    edges
    # join in the START station's trait...
    .merge(stations[["code", "maj_black"]].rename(
        columns={"code": "start_code", "maj_black": "start_black"}),
        on="start_code", how="left")
    # ...then join in the END station's trait.
    .merge(stations[["code", "maj_black"]].rename(
        columns={"code": "end_code",   "maj_black": "end_black"}),
        on="end_code", how="left")
    # Drop rows where either side is NaN — these are stations not in
    # our stations table (out-of-area).
    .dropna(subset=["start_black", "end_black"])
    .reset_index(drop=True)
)

print(data.head())
print(f"✅ After double-join + NaN drop: {len(data)} rows.")

## 2.2 An aggregate quantity of interest #####################################

# How many trips happened between EACH of the four demographic
# combinations (yes->yes, yes->no, no->yes, no->no)?
stat = (
    data
    .groupby(["start_black", "end_black"], dropna=False)["count"]
    .sum()
    .reset_index(name="trips")
)
total = stat["trips"].sum()
stat["total"]   = total
stat["percent"] = (100 * stat["trips"] / total).round(1)

print(stat)
print(f"📊 Total trips across all four cells: {int(stat['trips'].sum())}")


# 3. A quick visual ##########################################################
#
# A 2x2 heatmap of trips by start-demographic x end-demographic. This
# is the simplest possible "network communication" visualization, and
# it's often the most honest one.

pivot = stat.pivot(index="end_black", columns="start_black", values="percent")

fig, ax = plt.subplots(figsize=(5.2, 4.5))
sns.heatmap(pivot, annot=True, fmt=".1f", cmap="mako",
            cbar_kws={"label": "% of trips"}, ax=ax)
ax.set_xlabel("Starting station\nin majority-Black block group?")
ax.set_ylabel("Ending station\nin majority-Black block group?")
ax.set_title("AM rush 2021 — slim Bluebikes-flavored sample", loc="left")
fig.tight_layout()
fig.savefig("joins_heatmap.png", dpi=120)
plt.close(fig)
print("💾 Saved joins_heatmap.png")


# 4. Why renames matter (the silent-bug demo) ################################
#
# To drive the point home: try the same double-merge WITHOUT renaming
# `maj_black`. What does pandas do? It auto-suffixes them as `_x` and
# `_y`, which (a) is ugly, and (b) means you can't tell at a glance
# which side is which.

bad = (
    edges
    .merge(stations[["code", "maj_black"]],
           left_on="start_code", right_on="code", how="left")
    .merge(stations[["code", "maj_black"]],
           left_on="end_code", right_on="code", how="left")
)
print(bad.head())
# Notice `maj_black_x` and `maj_black_y`. You can survive this, but
# in any non-trivial pipeline it's a recipe for misreading your own
# code in two weeks. Rename on the way in.


# 5. Learning Check ##########################################################
#
# QUESTION: Of AM rush rides in 2021 in this slim dataset, how many
# trips started in a majority-Black block group AND ended in a
# majority-Black block group?
#
# HINT: you've already computed `stat` above. Find the row where
# start_black == "yes" and end_black == "yes" and read off `trips`.

answer = int(
    stat.loc[(stat["start_black"] == "yes") &
             (stat["end_black"]   == "yes"), "trips"].iloc[0]
)

print(f"\n📝 Learning Check answer: {answer}")

# Reminder: this is a synthetic-but-deterministic dataset. Your answer
# should be the SAME as your classmates'. If it isn't, your random
# seed has drifted somewhere.

print("\n🎉 Done. Move on to the case study report when you're ready.")
```

---

## `code/02_joins/functions.R`

```r
#' @name functions.R
#' @title Helpers for the Network Joins case study
#' @description
#'
#' Small helper functions used by `example.R`:
#'
#' - `load_edges()`   — read the slim rush-hour trips parquet.
#' - `load_stations()` — read the slim stations parquet (with demographic flag).
#' - `make_joined()`  — convenience wrapper that does the standard
#'                       start-side + end-side double join, with renames,
#'                       so we can sanity-check the example.
#'
#' We intentionally keep the functions tiny. The teaching happens in
#' `example.R`; this file is just so you can call `load_edges()` instead
#' of remembering the parquet path.

library(dplyr)
library(readr)
library(here)

# ----- paths -----------------------------------------------------------------

# Resolve paths relative to THIS file's folder, so the script works no matter
# where you run it from.
.case_dir <- function() {
  here::here("code", "02_joins", "data")
}

# ----- data loaders ----------------------------------------------------------

#' Load the slim trips edge list.
#'
#' One row per (start_station, end_station, day, rush) combination, with
#' `count` = number of trips. Already filtered to AM rush + 2021.
load_edges <- function() {
  readr::read_csv(file.path(.case_dir(), "edges.csv"))
}

#' Load the slim stations node table.
#'
#' One row per station, with a `maj_black` flag ("yes"/"no") from the
#' census block group the station sits in.
load_stations <- function() {
  readr::read_csv(file.path(.case_dir(), "stations.csv"))
}

# ----- the reference join ----------------------------------------------------

#' The "standard" double-side join used as a sanity check in the example.
#'
#' Renames demographics to `start_black` and `end_black`, then drops any
#' edge whose start *or* end station is missing from the stations table
#' (these correspond to stations outside Boston proper).
make_joined <- function(edges = load_edges(), stations = load_stations()) {
  edges |>
    left_join(
      by = c("start_code" = "code"),
      y  = stations |> select(code, start_black = maj_black)
    ) |>
    left_join(
      by = c("end_code" = "code"),
      y  = stations |> select(code, end_black = maj_black)
    ) |>
    filter(!is.na(start_black), !is.na(end_black))
}
```

---

## `code/02_joins/functions.py`

```python
"""Helpers for the Network Joins case study.

Small helper functions used by ``example.py``:

- ``load_edges()``    — read the slim rush-hour trips parquet.
- ``load_stations()`` — read the slim stations parquet (with demographic flag).
- ``make_joined()``   — convenience wrapper that does the standard
                        start-side + end-side double merge, with renames.

We keep the functions tiny on purpose. The teaching happens in
``example.py``; this file is so you can call ``load_edges()`` instead of
remembering the parquet path.
"""

from pathlib import Path
import pandas as pd

# ----- paths -----------------------------------------------------------------

# Resolve paths relative to THIS file's folder, so the script works no matter
# where you run it from.
def _case_dir() -> Path:
    return Path(__file__).resolve().parent / "data"


# ----- data loaders ----------------------------------------------------------

def load_edges() -> pd.DataFrame:
    """Load the slim trips edge list.

    One row per (start_station, end_station, day, rush) combination, with
    ``count`` = number of trips. Already filtered to AM rush + 2021.
    """
    return pd.read_csv(_case_dir() / "edges.csv")


def load_stations() -> pd.DataFrame:
    """Load the slim stations node table.

    One row per station, with a ``maj_black`` flag ("yes"/"no") from the
    census block group the station sits in.
    """
    return pd.read_csv(_case_dir() / "stations.csv")


# ----- the reference join ----------------------------------------------------

def make_joined(edges: pd.DataFrame | None = None,
                stations: pd.DataFrame | None = None) -> pd.DataFrame:
    """The "standard" double-side join used as a sanity check.

    Renames demographics to ``start_black`` and ``end_black``, then drops
    any edge whose start *or* end station is missing from the stations
    table (these correspond to stations outside Boston proper).
    """
    if edges is None:
        edges = load_edges()
    if stations is None:
        stations = load_stations()

    out = (
        edges
        .merge(
            stations[["code", "maj_black"]].rename(
                columns={"code": "start_code", "maj_black": "start_black"}),
            on="start_code", how="left")
        .merge(
            stations[["code", "maj_black"]].rename(
                columns={"code": "end_code", "maj_black": "end_black"}),
            on="end_code", how="left")
    )
    return out.dropna(subset=["start_black", "end_black"]).reset_index(drop=True)
```

---

## `code/03_aggregation/README.md`

# Case Study 03 — Aggregation

> Interactive lab: [`docs/case-studies/aggregation.html`](../../docs/case-studies/aggregation.html)
>
> Skill: **Identify** · Data: slim mobility-flow sample with neighborhood
> + income-quintile annotations (500 stations, 40,000 trip rows)

## What you'll learn

Aggregation isn't a chore — it's a way of *finding the question*. The
same network looked at at three different resolutions tells three
different stories. This case walks you through:

- viewing 500-station traffic at the raw station-pair resolution
  (a hairball; the only honest visual is a distribution),
- aggregating to the neighborhood resolution (12×12, a heatmap with
  visible diagonal stickiness),
- aggregating to the income quintile resolution (4×4, where the
  equity question becomes legible).

## Prerequisites

- The case study lab: [Aggregation](../../docs/case-studies/aggregation.html).
- Case study 02 (Joins) — this one assumes you're comfortable with
  double-side joins.
- R packages: `dplyr`, `tidyr`, `readr`, `ggplot2`, `viridis`, `here`.
- Python packages: see [`code/requirements.txt`](../requirements.txt).

## Files in this folder

```
03_aggregation/
├── README.md
├── example.R
├── example.py
├── functions.R
├── functions.py
└── data/
    ├── edges.csv     # 40,000 AM rush 2021 trip rows
    ├── stations.csv  # 500 stations with neighborhood + income_quintile
    └── _generate.py
```

## How to run

```bash
Rscript code/03_aggregation/example.R
python  code/03_aggregation/example.py
```

## Learning check (submit this number)

> **What percentage of all AM rush 2021 trips stay within the *top*
> income quintile (Q4 → Q4)?**

The number is printed at the bottom of either example script.

## Your Project Case Study

If you pick this case study, you'll view your own network at multiple
resolutions and report which one reveals signal. Submission:
`project.R`/`project.py` + a 2-page-minimum report in your own words.

### Suggested project questions

1. **At what resolution does my network become legible?** View your
   network at the raw, mid-resolution, and high-resolution levels.
   Report which resolution best supports the question you actually
   care about, and why.

2. **Diagonal stickiness.** Aggregate your network by a categorical
   node attribute. Compute the fraction of edge weight on the
   diagonal vs off-diagonal. State the number in prose and discuss
   what it means in your domain.

3. **Two competing aggregations.** Aggregate your network by two
   different node attributes (e.g. tier vs region). Report which
   aggregation makes the structural pattern clearer.

### What goes in the report

- **Question.** One sentence.
- **Network.** Nodes, edges, attribute(s) you aggregated by.
- **Procedure.** What you did at each resolution, in order.
- **Results.** Numbers in prose, plus at most 2 figures and 1 table.
- **What this tells you, and what it doesn't.** 2-3 sentences.

## Further reading

- This is the descriptive-statistics complement to case studies on
  centrality (case 04) and community detection (case 06). The sts
  course `22C_datacom.R` makes the same point on the real (multi-GB)
  Bluebikes data.

---

## `code/03_aggregation/data/_generate.py`

```python
"""Generate the slim mobility-flow data for case 03 (aggregation).

Mirrors case 02 in flavor, but adds two extra columns on the stations
table — `neighborhood` (one of 12) and `income_quintile` (1..4 where 4
is wealthiest). This lets the example.* scripts demonstrate the
*aggregation-by-resolution* idea: same network, viewed at 3 zoom
levels.

Run once to regenerate:

    python code/03_aggregation/data/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

def main() -> None:
    rng = np.random.default_rng(SEED)

    n_stations = 500
    n_neighborhoods = 12
    # assign stations to neighborhoods
    nbhd = rng.integers(0, n_neighborhoods, size=n_stations)
    # each neighborhood has a "wealth" score; from that we'll derive a
    # 1..4 quintile (we say "quintile" loosely but use 4 buckets to
    # match the case study's 4-quartile heatmap).
    nbhd_wealth = rng.uniform(size=n_neighborhoods)
    station_wealth = nbhd_wealth[nbhd] + rng.normal(0, 0.05, n_stations)
    quintile = pd.qcut(station_wealth, q=4, labels=[1, 2, 3, 4]).astype(int)

    stations = pd.DataFrame({
        "code": [f"S{i:04d}" for i in range(n_stations)],
        "neighborhood": [f"N{n:02d}" for n in nbhd],
        "income_quintile": quintile,
        "x": (-71.10 + (nbhd - 6) * 0.01 + rng.normal(0, 0.005, n_stations)),
        "y": (42.34 + (nbhd - 6) * 0.005 + rng.normal(0, 0.004, n_stations)),
    })

    # ~40k AM-rush 2021 trip rows. Bias trips to stay within neighborhood.
    n_edges = 40_000
    days = pd.date_range("2021-01-01", "2021-12-31", freq="D").strftime("%Y-%m-%d").to_numpy()

    start_idx = rng.integers(0, n_stations, size=n_edges)
    same_nbhd = rng.random(n_edges) < 0.55
    end_idx = np.where(
        same_nbhd,
        np.array([rng.choice(np.flatnonzero(nbhd == nbhd[s])) for s in start_idx]),
        rng.integers(0, n_stations, size=n_edges),
    )

    edges = pd.DataFrame({
        "start_code": stations["code"].to_numpy()[start_idx],
        "end_code":   stations["code"].to_numpy()[end_idx],
        "day":        rng.choice(days, size=n_edges),
        "rush":       "am",
        "count":      rng.integers(1, 6, size=n_edges),
    }).sort_values(["day", "start_code", "end_code"]).reset_index(drop=True)

    stations = stations.sort_values("code").reset_index(drop=True)

    edges.to_csv(HERE / "edges.csv", index=False)
    stations.to_csv(HERE / "stations.csv", index=False)

    print(f"wrote {HERE / 'edges.csv'} ({len(edges):,} rows)")
    print(f"wrote {HERE / 'stations.csv'} ({len(stations):,} rows)")


if __name__ == "__main__":
    main()
```

---

## `code/03_aggregation/example.R`

```r
#' @name example.R
#' @title Case Study 03 — Aggregation
#' @author <your-name-here>
#' @description
#' The interactive lab showed you the same network at three
#' resolutions: raw stations, neighborhood, income quintile. Each
#' resolution tells a different story. This script does the same in code.
#'
#' Data:
#'   - 500 stations, each tagged with a neighborhood (1 of 12) and an
#'     income quintile (1..4, 4 = wealthiest).
#'   - 40,000 AM rush 2021 trip rows.
#'
#' The point: visualization is partly a tool for *finding the question*.
#' Aggregation reveals signal.


# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `dplyr` and `tidyr` for the grouping pipeline, `ggplot2` + `viridis`
# for the three figures, `here` for path resolution.
library(dplyr)
library(tidyr)
library(ggplot2)
library(viridis)
library(here)

## 0.2 Load helpers ##########################################################

# `make_enriched()` does the double join from Case 02 in one call so we
# can focus on aggregation here.
source(here::here("code", "03_aggregation", "functions.R"))

cat("\n🚀 Case Study 03 — Aggregation (R)\n")
cat("   Same network at three resolutions: station -> neighborhood -> quintile.\n\n")

## 0.3 Load data #############################################################

edges    <- load_edges()
stations <- load_stations()
edges    |> head()
stations |> head()
cat(sprintf("✅ Loaded %d trip rows and %d stations.\n",
            nrow(edges), nrow(stations)))


# 1. Enrich edges with both-side traits ######################################
#
# The helper joins each edge with the start-station's traits AND the
# end-station's traits (renaming to start_nbhd / end_nbhd, etc.). This
# is exactly the "double join, with renames" lesson from case 02.

enriched <- make_enriched(edges, stations)
enriched |> head()
nrow(enriched)
cat(sprintf("✅ Built enriched edge table: %d rows.\n", nrow(enriched)))


# 2. Three resolutions #######################################################

## 2.1 Resolution A — raw station x station ##################################

# Sum trips for each (start, end) station pair. With 500 stations the
# space of possible pairs is 250,000 cells — way too fine to plot as a
# heatmap. The aggregation gives a hairball, useful for nothing but a
# degree histogram.
station_pairs <- enriched |>
  group_by(start_code, end_code) |>
  summarize(trips = sum(count, na.rm = TRUE), .groups = "drop") |>
  arrange(desc(trips))
nrow(station_pairs)
cat(sprintf("📊 Resolution A: %d station pairs.\n", nrow(station_pairs)))
# Context: only ~30k of the ~250,000 possible ordered station pairs ever
# see a trip. That sparsity is real transit demand, not a data error.

## 2.2 Resolution B — neighborhood x neighborhood ############################

# Now sum trips by START neighborhood and END neighborhood. 12 x 12 =
# 144 cells max. Visualizable as a heatmap. This is where structure
# begins to appear (the diagonal is heavier than the off-diagonal).
nbhd_pairs <- enriched |>
  group_by(start_nbhd, end_nbhd) |>
  summarize(trips = sum(count, na.rm = TRUE), .groups = "drop")
nrow(nbhd_pairs)
cat(sprintf("📊 Resolution B: %d neighborhood pairs.\n", nrow(nbhd_pairs)))

## 2.3 Resolution C — income quintile x income quintile ######################

# Finally, aggregate to 4 x 4 income-quintile cells and compute a
# percent column so we can read the equity question directly off the
# matrix. Why the diagonal matters: big diagonal cells mean trips stay
# WITHIN an income level (riders don't cross economic boundaries); heavy
# off-diagonal cells mean the system mixes income groups.
q_pairs <- enriched |>
  group_by(start_quintile, end_quintile) |>
  summarize(trips = sum(count, na.rm = TRUE), .groups = "drop") |>
  mutate(
    total   = sum(trips),
    percent = round(100 * trips / total, 2)
  )

print(q_pairs)
cat(sprintf("📊 Resolution C: 4x4 quintile pairs.\n"))


# 3. Visualize each resolution ###############################################

# Resolution A: degree-like distribution (only honest view at 500 nodes).
# Each station's "trip volume" = sum of trips out + sum of trips in.
station_totals <- bind_rows(
  station_pairs |> group_by(code = start_code) |> summarize(trips = sum(trips)),
  station_pairs |> group_by(code = end_code)   |> summarize(trips = sum(trips))
) |>
  group_by(code) |>
  summarize(trips = sum(trips), .groups = "drop")

# Each plot is assigned to an object, then both print()ed (visible in an
# interactive / in-browser session) AND ggsave()d to a PNG, so terminal /
# Rscript users aren't left wondering where the figures went (Rplots.pdf).
p_a <- ggplot(station_totals, aes(x = trips)) +
  geom_histogram(bins = 40, fill = "#3a8bc6") +
  labs(x     = "trips touching this station (in or out)",
       y     = "# stations",
       title = "Resolution A — station-level trip volume") +
  theme_classic(base_size = 13)
print(p_a)
ggsave(here::here("code", "03_aggregation", "resolution_a_stations.png"),
       p_a, width = 6, height = 4.5, dpi = 120)

# Resolution B: 12x12 heatmap. Diagonal heavier = neighborhood stickiness.
p_b <- ggplot(nbhd_pairs,
       aes(x = start_nbhd, y = end_nbhd, fill = trips)) +
  geom_tile(color = "white") +
  scale_fill_viridis(option = "mako") +
  labs(title = "Resolution B — neighborhood x neighborhood",
       x     = "Starting neighborhood",
       y     = "Ending neighborhood") +
  theme_classic(base_size = 12) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))
print(p_b)
ggsave(here::here("code", "03_aggregation", "resolution_b_neighborhood.png"),
       p_b, width = 6, height = 5, dpi = 120)

# Resolution C: 4x4 heatmap with the percentages drawn ON the cells.
p_c <- ggplot(q_pairs,
       aes(x = factor(start_quintile), y = factor(end_quintile),
           fill = percent)) +
  geom_tile(color = "white") +
  geom_text(aes(label = percent), color = "white", size = 5) +
  scale_fill_viridis(option = "mako", begin = 0.2, end = 0.8) +
  labs(x     = "Starting station's income quintile",
       y     = "Ending station's income quintile",
       fill  = "% of trips",
       title = "Resolution C — trips between income quintiles") +
  theme_classic(base_size = 13)
print(p_c)
ggsave(here::here("code", "03_aggregation", "resolution_c_quintile.png"),
       p_c, width = 6, height = 5, dpi = 120)
cat("💾 Saved resolution_a/b/c PNGs.\n")


# 4. The point ###############################################################
#
# Resolution A is a hairball. Resolution B (12x12) shows neighborhood
# stickiness — the diagonal is heavier. Resolution C (4x4) makes the
# equity question legible: how much ridership stays in-quintile vs
# crosses quintiles.
#
# Visualization is partly a tool for finding the question. The case
# study calls this "aggregation reveals signal."
#
# The through-line: the "right" resolution is the one at which your quantity
# of interest becomes legible. 30,125 station pairs is too fine to read; the
# 4x4 quintile matrix is coarse enough that the equity pattern jumps out.


# 5. Learning Check ##########################################################
#
# QUESTION: What percentage of all AM rush 2021 trips in this dataset
# stay within the *top* income quintile (Q4 -> Q4)?
#
# HINT: pull from `q_pairs` directly — start_quintile == 4 AND
# end_quintile == 4.

answer <- q_pairs |>
  filter(start_quintile == 4, end_quintile == 4) |>
  pull(percent)

cat(sprintf("\n📝 Learning Check answer (%%): %.2f\n", answer))

cat("\n🎉 Done. Move on to the case study report when you're ready.\n")
```

---

## `code/03_aggregation/example.py`

```python
"""Case Study 03 — Aggregation (Python track).

The interactive lab showed you the same network at three resolutions:
raw stations, neighborhood, income quintile. Each resolution tells a
different story. This script does the same thing in code.

The data is a slim mobility-flow dataset:
  - 500 stations, each tagged with a neighborhood (1 of 12)
    and an income quintile (1..4, 4 = wealthiest).
  - 40,000 AM rush 2021 trip rows (start_code, end_code, day, count).

We will:
  1. Enrich the edges with start- and end-side traits.
  2. View the data at three resolutions (raw, neighborhood, quintile).
  3. At each resolution, render the obvious visual.
  4. Land on a single number — what % of trips stay within the
     top income quintile.
"""

# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `pandas` for the grouping pipeline, `seaborn` + `matplotlib` for the
# three figures.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

## 0.2 Load helpers ##########################################################

# `make_enriched()` does the double join from Case 02 in one call so
# we can focus on aggregation here.
from functions import load_edges, load_stations, make_enriched

print("\n🚀 Case Study 03 — Aggregation (Python)")
print("   Same network at three resolutions: station -> neighborhood -> quintile.\n")

## 0.3 Load data #############################################################

edges    = load_edges()
stations = load_stations()
print(edges.head())
print(stations.head())
print(f"✅ Loaded {len(edges)} trip rows and {len(stations)} stations.")


# 1. Enrich edges with both-side traits ######################################
#
# The helper joins each edge with the start-station's traits AND the
# end-station's traits (renaming to start_nbhd / end_nbhd, etc.). This
# is exactly the "double join, with renames" lesson from case 02.

enriched = make_enriched(edges, stations)
print(enriched.head())
print(f"{len(enriched):,} enriched edge rows")
print(f"✅ Built enriched edge table: {len(enriched)} rows.")


# 2. Three resolutions #######################################################

## 2.1 Resolution A — raw station x station ##################################

# Sum trips for each (start, end) station pair. With 500 stations the
# space of possible pairs is 250,000 cells — way too fine to plot as a
# heatmap. The aggregation gives a hairball, useful for nothing but a
# degree histogram.
station_pairs = (
    enriched
    .groupby(["start_code", "end_code"], as_index=False)["count"]
    .sum()
    .rename(columns={"count": "trips"})
    .sort_values("trips", ascending=False)
)
print(f"📊 Resolution A: {len(station_pairs)} station pairs.")
print(station_pairs.head())

## 2.2 Resolution B — neighborhood x neighborhood ############################

# Now sum trips by START neighborhood and END neighborhood. 12 x 12 =
# 144 cells max. Visualizable as a heatmap. This is where structure
# begins to appear (the diagonal is heavier than the off-diagonal).
nbhd_pairs = (
    enriched
    .groupby(["start_nbhd", "end_nbhd"], as_index=False)["count"]
    .sum()
    .rename(columns={"count": "trips"})
)
print(f"📊 Resolution B: {len(nbhd_pairs)} neighborhood pairs.")
print(nbhd_pairs.head())

## 2.3 Resolution C — income quintile x income quintile ######################

# Finally, aggregate to 4 x 4 income-quintile cells and compute a
# percent column so we can read the equity question directly off the
# matrix. Why the diagonal matters: big diagonal cells mean trips stay
# WITHIN an income level (riders don't cross economic boundaries); heavy
# off-diagonal cells mean the system mixes income groups.
q_pairs = (
    enriched
    .groupby(["start_quintile", "end_quintile"], as_index=False)["count"]
    .sum()
    .rename(columns={"count": "trips"})
)
total = q_pairs["trips"].sum()
q_pairs["percent"] = (100 * q_pairs["trips"] / total).round(2)
print("Resolution C — 4x4 income quintile pairs")
print(q_pairs)
print(f"📊 Resolution C: 4x4 quintile pairs.")


# 3. Visualize each resolution ###############################################

# Resolution A: degree distribution (the only honest view at 500 nodes).
# Each station's "trip volume" = sum of trips out + sum of trips in.
station_totals = (
    pd.concat([
        station_pairs.groupby("start_code")["trips"].sum(),
        station_pairs.groupby("end_code")["trips"].sum(),
    ]).groupby(level=0).sum().reset_index(name="trips")
)
fig, ax = plt.subplots(figsize=(6, 4))
ax.hist(station_totals["trips"], bins=40, color="#3a8bc6")
ax.set_xlabel("trips touching this station (in or out)")
ax.set_ylabel("# stations")
ax.set_title("Resolution A — station-level trip volume")
fig.tight_layout()
fig.savefig("agg_A_station.png", dpi=120)
plt.close(fig)

# Resolution B: neighborhood x neighborhood heatmap
pivot_b = nbhd_pairs.pivot(index="end_nbhd", columns="start_nbhd", values="trips")
fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(pivot_b, cmap="mako", ax=ax)
ax.set_title("Resolution B — neighborhood x neighborhood")
fig.tight_layout()
fig.savefig("agg_B_neighborhood.png", dpi=120)
plt.close(fig)

# Resolution C: 4 x 4 quintile heatmap with percentages drawn on the cells.
pivot_c = q_pairs.pivot(index="end_quintile", columns="start_quintile",
                       values="percent")
fig, ax = plt.subplots(figsize=(5.2, 4.5))
sns.heatmap(pivot_c, annot=True, fmt=".1f", cmap="mako",
            cbar_kws={"label": "% of trips"}, ax=ax)
ax.invert_yaxis()  # so quintile 1 is bottom-left
ax.set_xlabel("Starting station's income quintile")
ax.set_ylabel("Ending station's income quintile")
ax.set_title("Resolution C — trips between income quintiles")
fig.tight_layout()
fig.savefig("agg_C_quintile.png", dpi=120)
plt.close(fig)
print("💾 Saved agg_A_station.png, agg_B_neighborhood.png, agg_C_quintile.png")


# 4. The point ###############################################################
#
# Resolution A is a hairball: ~13,500 station pairs, no obvious
# structure to a heatmap. Resolution B (12x12) shows neighborhood
# stickiness — the diagonal is heavier. Resolution C (4x4) makes the
# *equity* question legible: how much ridership stays in-quintile vs
# crosses quintiles.
#
# Visualization is partly a tool for finding the question. The case
# study calls this "aggregation reveals signal."


# 5. Learning Check ##########################################################
#
# QUESTION: What percentage of all AM rush 2021 trips in this dataset
# stay within the *top* income quintile (Q4 -> Q4)?
#
# HINT: pull from `q_pairs` directly — start_quintile == 4 AND
# end_quintile == 4.

answer = float(
    q_pairs.loc[(q_pairs["start_quintile"] == 4) &
                (q_pairs["end_quintile"]   == 4), "percent"].iloc[0]
)

print(f"\n📝 Learning Check answer (%): {answer:.2f}")

print("\n🎉 Done. Move on to the case study report when you're ready.")
```

---

## `code/03_aggregation/functions.R`

```r
#' @name functions.R
#' @title Helpers for the Aggregation case study
#' @description
#' Path-resolved loaders for the slim mobility-flow data.

library(dplyr)
library(here)

.case_dir <- function() here::here("code", "03_aggregation", "data")

load_edges    <- function() readr::read_csv(file.path(.case_dir(), "edges.csv"))
load_stations <- function() readr::read_csv(file.path(.case_dir(), "stations.csv"))

#' Edges with start- and end-side traits already joined in.
make_enriched <- function(edges = load_edges(), stations = load_stations()) {
  edges |>
    left_join(
      by = c("start_code" = "code"),
      y  = stations |> select(code,
                              start_nbhd     = neighborhood,
                              start_quintile = income_quintile)
    ) |>
    left_join(
      by = c("end_code" = "code"),
      y  = stations |> select(code,
                              end_nbhd     = neighborhood,
                              end_quintile = income_quintile)
    )
}
```

---

## `code/03_aggregation/functions.py`

```python
"""Helpers for the Aggregation case study.

Path-resolved loaders for the slim mobility-flow data.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd


def _case_dir() -> Path:
    return Path(__file__).resolve().parent / "data"


def load_edges() -> pd.DataFrame:
    return pd.read_csv(_case_dir() / "edges.csv")


def load_stations() -> pd.DataFrame:
    return pd.read_csv(_case_dir() / "stations.csv")


def make_enriched(edges: pd.DataFrame | None = None,
                  stations: pd.DataFrame | None = None) -> pd.DataFrame:
    """Edges with start- and end-side traits already joined in."""
    if edges is None:
        edges = load_edges()
    if stations is None:
        stations = load_stations()

    s_start = stations[["code", "neighborhood", "income_quintile"]].rename(
        columns={"code": "start_code",
                 "neighborhood": "start_nbhd",
                 "income_quintile": "start_quintile"})
    s_end = stations[["code", "neighborhood", "income_quintile"]].rename(
        columns={"code": "end_code",
                 "neighborhood": "end_nbhd",
                 "income_quintile": "end_quintile"})

    return edges.merge(s_start, on="start_code", how="left") \
                .merge(s_end,   on="end_code",   how="left")
```

---

## `code/04_centrality/README.md`

# Case Study 04 — Centrality & Criticality

> Interactive lab: [`docs/case-studies/centrality.html`](../../docs/case-studies/centrality.html)
>
> Skill: **Measure** · Data: synthetic 500-node transit network with
> planted bridge nodes

## What you'll learn

How to compute and *compare* four different centrality measures —
degree, betweenness, closeness, eigenvector — and recognize that they
are not interchangeable. Specifically:

- High-degree nodes (hubs) are obvious and usually have redundancy.
- High-betweenness, low-degree nodes (bridges) are the actual
  load-bearing structure — and they're invisible if you only look at
  degree.
- A removal simulation confirms: removing the top-5 by betweenness
  fragments the network much more than removing the top-5 by degree.

## Prerequisites

- The case study lab: [Centrality & Criticality](../../docs/case-studies/centrality.html).
- Case study 01 (Build a Network) so you're comfortable with
  `igraph`.
- R packages: `dplyr`, `tibble`, `igraph`, `ggplot2`, `here`.
- Python packages: see [`code/requirements.txt`](../requirements.txt).

## Files in this folder

```
04_centrality/
├── README.md
├── example.R
├── example.py
├── functions.R
├── functions.py
└── data/
    ├── nodes.csv     # 500 nodes (480 regular + 20 planted bridges)
    ├── edges.csv     # ~1,000 weighted edges
    └── _generate.py
```

## How to run

```bash
Rscript code/04_centrality/example.R
python  code/04_centrality/example.py
```

## Learning check (submit this string)

> **List the 5 nodes whose `betweenness_rank - degree_rank` gap is
> largest. What is the `node_id` of the #1 entry?**

Submit the node ID. The script prints it.

## Your Project Case Study

If you pick this case study for your project, you'll find the bridges
hiding in *your* network.

### Suggested project questions

1. **Bridges in plain sight.** Compute degree and betweenness for
   every node. Find the top-10 nodes by `betweenness_rank −
   degree_rank` gap. Report what they are and why they likely have
   that pattern in your domain.

2. **Removal simulation.** Remove the top-5 nodes by each of two
   centrality measures, one at a time. Report the change in the size
   of the largest connected component (or in average path length).
   Which measure picks the more load-bearing nodes?

3. **Which centrality answers my question?** Pick a *specific*
   real-world question about your network (e.g. "which suppliers
   should we audit first?"). Argue from the question to a single
   centrality measure. Then compute it and report the top 5.

### Framing a real question (not just "compute centrality")

The most common trap here is stopping at "I computed betweenness." Push to a
*decision*: "which accounts should fraud analysts audit first?", "which
stations would hurt most if they closed?" Name the decision, then let it pick
the centrality (a centrality is only meaningful paired with the question it
answers). For a worked example of carrying a question through a report in
prose, see [`docs/assignments/sample-report.md`](../../docs/assignments/sample-report.md).

### Report

- **Question.** One sentence.
- **Network.** Nodes, edges, weights, basic sizes.
- **Procedure.** What you computed, in what order.
- **Results.** Quantities of interest as numbers in prose; at most 2
  figures and 1 table.
- **What this tells you, and what it doesn't.** 2-3 sentences. Be
  honest about cases where two centralities pick the same node — that
  doesn't make the metric "right", it just means your network
  doesn't have the bridges-vs-hubs distinction.

## Further reading

- The sts course `26C_analytics.R` runs the same comparison on a
  much larger committee-affiliation network.
- The next case study, [`05_supply-chain`](../05_supply-chain),
  turns centrality into a *resilience* question — what happens to a
  supply chain when critical nodes go offline.

---

## `code/04_centrality/data/_generate.py`

```python
"""Generate the synthetic planted-bridge network for case 04.

We want a graph where degree-centrality and betweenness-centrality
disagree on which nodes matter. The trick: build several dense
clusters, then connect them with a small number of bridge nodes. The
bridge nodes have low degree but high betweenness — exactly the
pattern the case study wants to expose.

Structure:
  - 6 communities of ~80 nodes each (480 transit stops)
  - within-community: Erdos-Renyi p ~ 0.05 (dense-ish)
  - cross-community: a handful of "bridge" nodes, each connected to
    1-3 nodes in TWO communities (so traffic between communities
    must pass through them)
  - 20 extra bridge nodes
  -> ~500 nodes total, ~1500 weighted edges

Edge weight = ridership (Poisson-distributed integer).

Run:
    python code/04_centrality/data/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent
SEED = 42

def main() -> None:
    rng = np.random.default_rng(SEED)

    n_communities = 6
    nodes_per_community = 80
    p_intra = 0.05
    n_bridges = 20

    nodes = []
    edges = []

    # build communities
    for c in range(n_communities):
        start = c * nodes_per_community
        for i in range(nodes_per_community):
            nid = f"N{start + i:04d}"
            nodes.append({"node_id": nid, "community": c, "kind": "regular"})
        # within-community edges
        for i in range(nodes_per_community):
            for j in range(i + 1, nodes_per_community):
                if rng.random() < p_intra:
                    u = f"N{start + i:04d}"
                    v = f"N{start + j:04d}"
                    edges.append({"from": u, "to": v,
                                  "weight": int(rng.poisson(lam=80) + 5)})

    # bridges
    n_total_before = n_communities * nodes_per_community
    for b in range(n_bridges):
        bid = f"B{b:03d}"
        # bridge connects 2 distinct communities
        ca, cb = rng.choice(n_communities, size=2, replace=False)
        nodes.append({"node_id": bid, "community": -1, "kind": "bridge"})
        # bridge links to a few nodes in each community
        for c in [ca, cb]:
            start = c * nodes_per_community
            n_links = int(rng.integers(1, 4))
            picks = rng.choice(nodes_per_community, size=n_links, replace=False)
            for p in picks:
                edges.append({
                    "from": bid,
                    "to":   f"N{start + p:04d}",
                    # bridges carry less ridership in this fake world
                    "weight": int(rng.poisson(lam=30) + 5),
                })

    nodes_df = pd.DataFrame(nodes).sort_values("node_id").reset_index(drop=True)
    edges_df = pd.DataFrame(edges).sort_values(["from", "to"]).reset_index(drop=True)

    # make sure the graph is connected. If not, add a small spanning
    # path between any disconnected components.
    g = ig.Graph.DataFrame(
        edges=edges_df[["from", "to"]],
        directed=False,
        vertices=nodes_df[["node_id"]],
        use_vids=False,
    )
    comps = list(g.connected_components())
    if len(comps) > 1:
        # connect each component to component 0 via the first vertex
        v0 = comps[0][0]
        for comp in comps[1:]:
            v1 = comp[0]
            edges_df.loc[len(edges_df)] = {
                "from":   g.vs[v0]["name"],
                "to":     g.vs[v1]["name"],
                "weight": int(rng.poisson(lam=30) + 5),
            }

    nodes_df.to_csv(HERE / "nodes.csv", index=False)
    edges_df.to_csv(HERE / "edges.csv", index=False)

    print(f"wrote {HERE / 'nodes.csv'}  ({len(nodes_df)} nodes)")
    print(f"wrote {HERE / 'edges.csv'}  ({len(edges_df)} edges)")


if __name__ == "__main__":
    main()
```

---

## `code/04_centrality/example.R`

```r
#' @name example.R
#' @title Case Study 04 — Centrality & Criticality
#' @author <your-name-here>
#' @description
#' The case study lab let you click nodes and watch the network
#' fragment. The point: high-degree nodes ("hubs") are obvious. The
#' nodes that actually matter for keeping the network connected —
#' *bridges* — are often invisible at a glance, because they have low
#' degree but high betweenness.
#'
#' This script makes that idea concrete. We have a synthetic 500-node
#' transit network with planted bridges. We compute four centrality
#' measures, rank-compare them, and find the bridges hiding in plain
#' sight.


# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `igraph` does the centrality math. `dplyr` + `tibble` keep the
# per-node results tidy so we can rank-compare them easily.
library(dplyr)
library(tibble)
library(igraph)
library(ggplot2)
library(here)

## 0.2 Load helpers ##########################################################

# `build_graph()` reads the nodes + edges CSVs and returns an undirected,
# weighted igraph graph. Open functions.R if you want to see the seam.
source(here::here("code", "04_centrality", "functions.R"))

cat("\n🚀 Case Study 04 — Centrality & Criticality (R)\n")
cat("   Four centrality measures, ranked. Find the bridges hiding in plain sight.\n\n")

## 0.3 Load data #############################################################

nodes <- load_nodes()
edges <- load_edges()
g     <- build_graph(nodes, edges)

# Inspecting the graph: ~500 vertices, ~1000 edges, undirected, with a
# weight attribute on every edge.
g
cat(sprintf("✅ Loaded graph: %d vertices, %d edges.\n",
            igraph::vcount(g), igraph::ecount(g)))


# 1. Four centrality measures ################################################
#
# "Most central" is meaningless on its own -- central BY WHICH MEASURE,
# FOR WHICH QUESTION? Reach for:
#   - DEGREE: how many neighbors. Local. "Who is busiest right now?"
#   - BETWEENNESS: how often this node sits on a shortest path between
#     others. Global. "Who is a chokepoint / bridge whose loss splits the
#     network?" This is the one that finds load-bearing nodes.
#   - CLOSENESS: 1 / mean distance to everyone. "Who can reach the whole
#     network fastest?" (good for response / diffusion questions).
#   - EIGENVECTOR: central if your neighbors are central (recursive).
#     "Who sits in the well-connected core?" Prefer it over betweenness
#     when you care about being embedded among important nodes, not about
#     controlling the flow between them.

# All four computed in one tidy table, so we can compare them directly.
# Betweenness is the slow one: it needs all-pairs shortest paths, so on
# 500 nodes expect this to take ~30-60s. It has NOT hung.
#
# +-------------------------------------------------------------------------+
# | /!\ WEIGHT DIRECTION -- THE #1 SILENT BUG IN WEIGHTED CENTRALITY         |
# |                                                                         |
# | igraph reads `weights` as DISTANCE: a higher weight means a LONGER,     |
# | harder-to-traverse edge. Our `weight` here is already a distance-like   |
# | cost, so passing it raw is correct.                                     |
# |                                                                         |
# | If YOUR weight is a STRENGTH (ridership, messages, volume -- higher =   |
# | "closer"), pass 1 / weight instead, the way case 09 builds              |
# | cost = 1 / ridership. Passing strength as-is RUNS WITHOUT ERROR and     |
# | silently computes the wrong thing -- check this before you trust a      |
# | weighted betweenness ranking.                                           |
# +-------------------------------------------------------------------------+
cat("🧪 Computing four centralities on 500 nodes (betweenness ~30-60s)...\n")
cent <- tibble(
  node_id     = igraph::V(g)$name,
  kind        = igraph::V(g)$kind,
  degree      = igraph::degree(g),
  betweenness = igraph::betweenness(g, weights = igraph::E(g)$weight),
  closeness   = igraph::closeness(g,   weights = igraph::E(g)$weight),
  eigenvector = igraph::eigen_centrality(g, weights = igraph::E(g)$weight)$vector
)

cent |> head()


# 2. Rank-compare ############################################################
#
# Different measures rank the SAME node differently. The Spearman
# correlation between two centrality vectors tells you how much the
# two measures agree on the *order* of nodes (not their magnitudes).
# The printed matrix is symmetric, with rows and columns in the SAME
# order (degree, betweenness, closeness, eigenvector) -- read cell
# (i, j) as "how much measures i and j agree on the ranking."

corr_mat <- cent |>
  select(degree, betweenness, closeness, eigenvector) |>
  as.matrix() |>
  cor(method = "spearman") |>
  round(3)
print(corr_mat)
cat(sprintf("📊 Degree vs betweenness Spearman: %.3f\n",
            corr_mat["degree", "betweenness"]))


# 3. Bridges hiding in plain sight ###########################################
#
# We want nodes that are HIGH BETWEENNESS but LOW DEGREE. Rank each
# metric (1 = highest), then compute the GAP: betweenness rank minus
# degree rank. Big positive gap = "matters more for connectivity
# than its degree would suggest."
#
# In our synthetic data we planted some "bridge" nodes — let's see if
# this gap statistic recovers them.
#
# Read the gap as RELATIVE, not absolute: it's a difference of ranks, so
# it only means "this node climbs N places when you rank by betweenness
# instead of degree." A gap of 400 in a 500-node graph is dramatic; the
# same 400 in a 50,000-node graph is mild. Always read it against n.

cent <- cent |>
  mutate(
    deg_rank  = rank(-degree),
    btwn_rank = rank(-betweenness),
    gap       = deg_rank - btwn_rank
  )

bridges <- cent |>
  arrange(desc(gap)) |>
  head(10)
print(bridges)
cat(sprintf("📝 #1 hidden bridge: %s (gap = %.0f)\n",
            bridges$node_id[1], bridges$gap[1]))


# 4. Visualize: size by betweenness ##########################################

# Attach the betweenness value AND a color flag back onto the graph,
# so the plotting call below is just one igraph::plot().
V(g)$btwn <- cent$betweenness
V(g)$col  <- ifelse(V(g)$kind == "bridge", "#d62728", "#1f77b4")

# Wrap the plot so we can both show it interactively AND save a copy to PNG
# (Rscript otherwise sends it to Rplots.pdf). Fix the layout once so the
# screen and file versions are identical.
lay <- igraph::layout_with_fr(g, weights = E(g)$weight, niter = 200)
draw_centrality <- function() {
  plot(
    g,
    layout       = lay,
    vertex.size  = 1 + 8 * (V(g)$btwn / max(V(g)$btwn)),
    vertex.color = V(g)$col,
    vertex.label = NA,
    edge.color   = adjustcolor("grey50", alpha.f = 0.2),
    edge.width   = 0.4,
    main         = "Node size = betweenness. Red = planted bridges."
  )
}

# Show interactively (RStudio / in-browser R session)...
draw_centrality()

# ...and save a copy for terminal / Rscript users.
png(here::here("code", "04_centrality", "centrality_network.png"),
    width = 7, height = 6, units = "in", res = 120)
draw_centrality()
invisible(dev.off())
cat("💾 Saved centrality_network.png\n")


# 5. Simulate: remove the top-5 by each metric ###############################
#
# To confirm betweenness picks the *load-bearing* nodes, remove the
# top-5 by each metric and see what happens to the size of the largest
# connected component. The metric whose top-5 removal fragments the
# network MOST is the one most attuned to network criticality.

lcc_size <- function(g_in) {
  cs <- igraph::components(g_in)$csize
  if (length(cs) == 0) 0L else max(cs)
}

cat(sprintf("\n🧪 Original largest component: %d\n", lcc_size(g)))

lcc_after <- sapply(c("degree", "betweenness", "closeness", "eigenvector"),
                    function(metric) {
  top5 <- cent |>
    arrange(desc(.data[[metric]])) |>
    head(5) |>
    pull(node_id)
  g_test <- igraph::delete_vertices(g, top5)
  size   <- lcc_size(g_test)
  cat(sprintf("   remove top-5 by %-12s -> LCC = %d\n", metric, size))
  size
})

# Land the takeaway so it isn't lost in the four lines above: the SMALLEST
# surviving largest-component is the most damaging attack, i.e. the metric
# most attuned to network criticality.
worst <- names(which.min(lcc_after))
cat(sprintf("📝 Most fragmenting metric: top-5 by %s (LCC = %d). %s\n",
            worst, min(lcc_after),
            if (worst == "betweenness")
              "Betweenness finds the load-bearing bridges degree misses."
            else
              "Compare against betweenness — bridges aren't always the busiest nodes."))


# 6. Learning Check ##########################################################
#
# QUESTION: List the 5 nodes whose betweenness-rank minus degree-rank
# gap is largest. What is the node_id of the #1 entry?

answer <- bridges |> slice(1) |> pull(node_id)

cat(sprintf("\n📝 Learning Check answer: %s\n", answer))

cat("\n🎉 Done. Move on to the case study report when you're ready.\n")
```

---

## `code/04_centrality/example.py`

```python
"""Case Study 04 — Centrality & Criticality (Python track).

The case study lab let you click nodes and watch the network
fragment. The point: high-degree nodes ("hubs") are obvious. The
nodes that actually matter for keeping the network connected —
*bridges* — are often invisible at a glance, because they have *low*
degree but *high* betweenness.

This script makes that idea concrete. We have a synthetic 500-node
transit network with planted bridges. We'll compute four centrality
measures (degree, betweenness, closeness, eigenvector), rank-compare
them, and find the bridges hiding in plain sight.
"""

# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `igraph` does the centrality math. `pandas` for the tidy per-node
# results so we can rank-compare them. `matplotlib` for the figure.
import pandas as pd
import numpy as np
import igraph as ig
import matplotlib.pyplot as plt

## 0.2 Load helpers ##########################################################

# `build_graph()` reads the nodes + edges CSVs and returns an undirected,
# weighted igraph graph. Open functions.py if you want to see the seam.
from functions import load_nodes, load_edges, build_graph

print("\n🚀 Case Study 04 — Centrality & Criticality (Python)")
print("   Four centrality measures, ranked. Find the bridges hiding in plain sight.\n")

## 0.3 Load data #############################################################

nodes = load_nodes()
edges = load_edges()
print(nodes.head())
print(edges.head())

g = build_graph(nodes, edges)
print(g.summary())
print(f"✅ Loaded graph: {g.vcount()} vertices, {g.ecount()} edges.")


# 1. Four centrality measures ################################################
#
# "Most central" is meaningless on its own -- central BY WHICH MEASURE,
# FOR WHICH QUESTION? Reach for:
#   - DEGREE: how many neighbors. Local. "Who is busiest right now?"
#   - BETWEENNESS: how often this node sits on a shortest path between
#     others. Global. "Who is a chokepoint / bridge whose loss splits the
#     network?" This is the one that finds load-bearing nodes.
#   - CLOSENESS: 1 / mean distance to everyone. "Who can reach the whole
#     network fastest?" (good for response / diffusion questions).
#   - EIGENVECTOR: a node is central if its neighbors are central
#     (recursive). "Who sits in the well-connected core?" Prefer it over
#     betweenness when you care about being embedded among important
#     nodes, not about controlling the flow between them.

# All four computed in one tidy table, so we can compare them directly.
# Betweenness is the slow one: it needs all-pairs shortest paths, so on
# 500 nodes expect this to take ~30-60s. It has NOT hung.
#
# +-------------------------------------------------------------------------+
# | /!\ WEIGHT DIRECTION -- THE #1 SILENT BUG IN WEIGHTED CENTRALITY         |
# |                                                                         |
# | igraph reads `weights` as DISTANCE: a higher weight means a LONGER,     |
# | harder-to-traverse edge. Our `weight` here is already a distance-like   |
# | cost, so passing it raw is correct.                                     |
# |                                                                         |
# | If YOUR weight is a STRENGTH (ridership, messages, volume -- higher =   |
# | "closer"), pass 1/weight instead, the way case 09 builds                |
# | cost = 1/ridership. Passing strength as-is RUNS WITHOUT ERROR and       |
# | silently computes the wrong thing -- check this before you trust a      |
# | weighted betweenness ranking.                                           |
# +-------------------------------------------------------------------------+
print("🧪 Computing four centralities on 500 nodes (betweenness ~30-60s)...")
cent = pd.DataFrame({
    "node_id":      g.vs["name"],
    "kind":         g.vs["kind"],
    "degree":       g.degree(),
    "betweenness":  g.betweenness(weights="weight"),
    "closeness":    g.closeness(weights="weight"),
    "eigenvector":  g.eigenvector_centrality(weights="weight"),
})

print(cent.head())


# 2. Rank-compare ############################################################
#
# Different measures rank the SAME node differently. The Spearman
# correlation between two centrality vectors tells you how much they
# agree on the *order* of nodes (not their magnitudes). The printed
# matrix is symmetric, with rows and columns in the SAME order (degree,
# betweenness, closeness, eigenvector) -- read cell (i, j) as "how much
# measures i and j agree on the ranking."

corr = cent[["degree", "betweenness", "closeness", "eigenvector"]].corr(method="spearman")
print(corr.round(3))
print(f"📊 Degree vs betweenness Spearman: {corr.loc['degree', 'betweenness']:.3f}")


# 3. Bridges hiding in plain sight ###########################################
#
# We want nodes that are HIGH BETWEENNESS but LOW DEGREE. To compare
# them on an equal footing, we rank each metric (1 = highest) and
# compute the GAP: betweenness rank minus degree rank. Big positive
# gap = "matters more for connectivity than its degree would suggest."
#
# In our synthetic data we planted some "bridge" nodes — let's see if
# this gap statistic recovers them.

cent["deg_rank"]  = cent["degree"].rank(ascending=False)
cent["btwn_rank"] = cent["betweenness"].rank(ascending=False)
cent["gap"] = cent["deg_rank"] - cent["btwn_rank"]

bridges = cent.sort_values("gap", ascending=False).head(10)
print(bridges)
# Notice how many of the top-gap nodes are tagged kind == "bridge"
# in our synthetic data. That's not a coincidence.
print(f"📝 #1 hidden bridge: {bridges.iloc[0]['node_id']} (gap = {bridges.iloc[0]['gap']:.0f})")


# 4. Visualize: size by betweenness ##########################################

fig, ax = plt.subplots(figsize=(10, 8))
layout = g.layout_fruchterman_reingold(weights="weight", niter=200)
xs = [p[0] for p in layout.coords]
ys = [p[1] for p in layout.coords]
# scale node size with betweenness
btwn = np.array(cent["betweenness"])
sizes = 6 + 90 * (btwn / btwn.max()) if btwn.max() > 0 else np.full_like(btwn, 6)
colors = ["#d62728" if k == "bridge" else "#1f77b4" for k in g.vs["kind"]]
for e in g.es:
    x0, y0 = layout.coords[e.source]
    x1, y1 = layout.coords[e.target]
    ax.plot([x0, x1], [y0, y1], color="grey", alpha=0.10, linewidth=0.3)
ax.scatter(xs, ys, c=colors, s=sizes, edgecolors="white", linewidths=0.3)
ax.set_axis_off()
ax.set_title("Node size = betweenness. Red = planted bridges.")
fig.tight_layout()
fig.savefig("centrality_bridges.png", dpi=120)
plt.close(fig)
print("💾 Saved centrality_bridges.png")


# 5. Simulate: remove the top-5 by each metric ###############################
#
# To confirm betweenness picks the *load-bearing* nodes, remove the
# top-5 nodes by each metric and see what happens to the size of the
# largest connected component. The metric whose top-5 removal
# fragments the network MOST is the one most attuned to network
# criticality.

def lcc_size(g_in):
    return max(len(c) for c in g_in.connected_components())

original_lcc = lcc_size(g)
print(f"\n🧪 Original largest component: {original_lcc}")

for metric in ["degree", "betweenness", "closeness", "eigenvector"]:
    top5 = cent.sort_values(metric, ascending=False).head(5)["node_id"].tolist()
    g_test = g.copy()
    g_test.delete_vertices([v.index for v in g_test.vs if v["name"] in top5])
    print(f"   remove top-5 by {metric:12s} -> LCC = {lcc_size(g_test)}")


# 6. Learning Check ##########################################################
#
# QUESTION: List the 5 nodes whose betweenness-rank minus degree-rank
# gap is largest (the "bridges hiding in plain sight"). What is the
# node_id of the #1 entry?

answer = bridges.iloc[0]["node_id"]

print(f"\n📝 Learning Check answer: {answer}")

print("\n🎉 Done. Move on to the case study report when you're ready.")
```

---

## `code/04_centrality/functions.R`

```r
#' @name functions.R
#' @title Helpers for the Centrality case study

library(readr)
library(dplyr)
library(igraph)
library(here)

.case_dir <- function() here::here("code", "04_centrality", "data")

load_nodes <- function() readr::read_csv(file.path(.case_dir(), "nodes.csv"),
                                         show_col_types = FALSE)
load_edges <- function() readr::read_csv(file.path(.case_dir(), "edges.csv"),
                                         show_col_types = FALSE)

#' Build the centrality graph from node + edge tables.
#'
#' Edges are undirected. `weight` is preserved as an edge attribute.
build_graph <- function(nodes = load_nodes(), edges = load_edges()) {
  igraph::graph_from_data_frame(
    d        = edges,
    directed = FALSE,
    vertices = nodes
  )
}
```

---

## `code/04_centrality/functions.py`

```python
"""Helpers for the Centrality case study."""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig


def _case_dir() -> Path:
    return Path(__file__).resolve().parent / "data"


def load_nodes() -> pd.DataFrame:
    return pd.read_csv(_case_dir() / "nodes.csv")


def load_edges() -> pd.DataFrame:
    return pd.read_csv(_case_dir() / "edges.csv")


def build_graph(nodes: pd.DataFrame | None = None,
                edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the centrality graph from node + edge tables.

    Edges are undirected. ``weight`` is preserved as an edge attribute.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    return ig.Graph.DataFrame(
        edges=edges,
        directed=False,
        vertices=nodes,
        use_vids=False,
    )
```

---

## `code/05_supply-chain/README.md`

# Case Study 05 — Supply Chain Resilience

> Interactive lab: [`docs/case-studies/supply-chain.html`](../../docs/case-studies/supply-chain.html)
>
> Skill: **Measure** · Data: synthetic 3-tier supply chain (150 suppliers,
> 30 DCs, 400 retailers — 580 nodes, ~900 directed weighted edges)

## What you'll learn

Centrality measures aren't just an academic curiosity — they tell you
which nodes to *defend*. This case study takes the supply-chain
resilience question seriously:

- Defines a domain-specific resilience metric (**supply coverage** =
  fraction of retailers still reachable from any supplier).
- Computes per-tier centralities (in/out degree, weighted in/out
  strength, betweenness) on a directed graph.
- Compares **random**, **high-degree**, and **high-betweenness**
  failure strategies on distribution centers.
- Lands on the qualitative result: targeted attacks (by either
  centrality) damage the network meaningfully faster than random
  attacks, and which centrality wins depends on the graph.

## Prerequisites

- Case study 04 (Centrality).
- The interactive lab.
- R packages: `dplyr`, `tibble`, `tidyr`, `igraph`, `ggplot2`, `here`.
- Python packages: see [`code/requirements.txt`](../requirements.txt).

## Files in this folder

```
05_supply-chain/
├── README.md
├── example.R
├── example.py
├── functions.R           # exposes `supply_coverage()` and `remove_and_score()`
├── functions.py
└── data/
    ├── nodes.csv     # 580 nodes (tier ∈ {1,2,3})
    ├── edges.csv     # ~900 directed edges with capacity
    └── _generate.py
```

## How to run

```bash
Rscript code/05_supply-chain/example.R
python  code/05_supply-chain/example.py
```

## Learning check (submit this number)

> **After removing the 5 highest-betweenness distribution centers,
> what is the supply coverage of the network?** (3 decimal places.)

## Your Project Case Study

If you pick this case study, you'll define a resilience metric on
*your* network and run targeted-vs-random failure simulations.

### Suggested project questions

1. **Which centrality picks the load-bearing nodes?** On your
   network, define a resilience metric, then run two targeted-attack
   strategies side-by-side (e.g. top-k by degree vs top-k by
   betweenness). Plot the damage curve and report which strategy
   degrades the metric faster.

2. **Random baseline.** Compare any targeted strategy against random
   removal. Report the *area between the two curves* (a rough proxy
   for how much being targeted matters).

3. **Tier-specific failures.** If your network has tiers/layers, run
   the failure simulation separately within each tier. Report which
   tier is most fragile.

### Report

- **Question.** One sentence.
- **Network and resilience metric.** What's an edge, what's a node,
  what's "coverage" or "throughput" in your domain.
- **Procedure.** What you ran, in order.
- **Results.** Numbers in prose; at most 2 figures (the damage
  curve is a near-mandatory one) and 1 table.
- **What this tells you, and what it doesn't.** 2-3 sentences.

## Further reading

- The sts course `26C_analytics.R` uses the same vocabulary for
  committee networks.
- Case study 06 ([`06_dsm-clustering`](../06_dsm-clustering)) tackles
  the *modularity* side of the same coin: rather than finding
  critical nodes, finding critical *clusters*.

---

## `code/05_supply-chain/data/_generate.py`

```python
"""Generate the synthetic 3-tier supply chain for case 05.

Tiers:
  - 150 suppliers (Tier 1)
  - 30 distribution centers (Tier 2)
  - 400 retailers (Tier 3)
  -> 580 nodes total, ~3000 directed weighted edges

Edge weight = capacity (units per week). Each retailer needs at least
some weekly supply; we keep the network connected by routing each
retailer through at least one DC and each DC through at least one
supplier.

Run:
    python code/05_supply-chain/data/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

def main() -> None:
    rng = np.random.default_rng(SEED)

    n_suppliers = 150
    n_dcs       = 30
    n_retailers = 400

    sup_ids = [f"S{i:03d}" for i in range(n_suppliers)]
    dc_ids  = [f"D{i:03d}" for i in range(n_dcs)]
    ret_ids = [f"R{i:03d}" for i in range(n_retailers)]

    nodes = pd.DataFrame({
        "node_id": sup_ids + dc_ids + ret_ids,
        "tier":    ([1] * n_suppliers) + ([2] * n_dcs) + ([3] * n_retailers),
    })

    edges = []

    # S -> D: every DC gets supplied by 2-5 suppliers
    for d in dc_ids:
        n_links = int(rng.integers(2, 6))
        supplier_picks = rng.choice(sup_ids, size=n_links, replace=False)
        for s in supplier_picks:
            edges.append({"from": s, "to": d,
                          "capacity": int(rng.integers(200, 1500))})

    # D -> R: every retailer gets supplied by 1-3 DCs
    for r in ret_ids:
        n_links = int(rng.integers(1, 4))
        dc_picks = rng.choice(dc_ids, size=n_links, replace=False)
        for d in dc_picks:
            edges.append({"from": d, "to": r,
                          "capacity": int(rng.integers(50, 300))})

    edges_df = pd.DataFrame(edges).sort_values(["from", "to"]).reset_index(drop=True)
    nodes_df = nodes.sort_values("node_id").reset_index(drop=True)

    nodes_df.to_csv(HERE / "nodes.csv", index=False)
    edges_df.to_csv(HERE / "edges.csv", index=False)
    print(f"wrote {HERE / 'nodes.csv'}  ({len(nodes_df)} nodes)")
    print(f"wrote {HERE / 'edges.csv'}  ({len(edges_df)} edges)")


if __name__ == "__main__":
    main()
```

---

## `code/05_supply-chain/example.R`

```r
#' @name example.R
#' @title Case Study 05 — Supply Chain Resilience
#' @author <your-name-here>
#' @description
#' The interactive lab let you click nodes to "fail" them and watched
#' supply coverage collapse. Here we do the same in code, on a
#' synthetic 580-node 3-tier supply chain.
#'
#' The resilience metric: SUPPLY COVERAGE = fraction of retailers
#' (tier 3) still reachable from at least one supplier (tier 1) after
#' the removals. 1.00 = nothing broken. 0.50 = half of all retailers
#' have lost their last incoming path from a supplier.
#'
#' The point of this case: random failures, high-degree failures, and
#' high-betweenness failures cause DIFFERENT amounts of damage.


# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `igraph` for graph + centrality, `dplyr`/`tidyr` to keep the
# per-strategy attack results tidy and easy to plot.
library(dplyr)
library(tibble)
library(tidyr)
library(igraph)
library(ggplot2)
library(here)

## 0.2 Load helpers ##########################################################

# `supply_coverage()` and `remove_and_score()` live in functions.R.
# They compute the % of retailers still reachable from any supplier,
# before and after a list of victims is deleted.
source(here::here("code", "05_supply-chain", "functions.R"))

cat("\n🚀 Case Study 05 — Supply Chain Resilience (R)\n")
cat("   Three attack strategies on a 580-node 3-tier chain. Which one hurts most?\n\n")

## 0.3 Load data #############################################################

nodes <- load_nodes()
edges <- load_edges()
g     <- build_graph(nodes, edges)

# Tier composition: tier 1 = suppliers, tier 2 = DCs, tier 3 = retailers
nodes |> count(tier)
g
cat(sprintf("✅ Loaded chain: %d nodes (%d suppliers, %d DCs, %d retailers).\n",
            igraph::vcount(g),
            sum(nodes$tier == 1), sum(nodes$tier == 2), sum(nodes$tier == 3)))


# 1. Baseline supply coverage ################################################
#
# Before we break anything, what fraction of retailers are reachable
# from at least one supplier? That's our denominator.

base <- supply_coverage(g)
cat(sprintf("📊 Baseline supply coverage: %.3f\n", base))


# 2. Centrality per tier #####################################################
#
# To target the right nodes we need per-node centrality. For a
# directed network we use both weighted degree (capacity) and
# betweenness. We hold these in a tidy table so the attack loop
# below stays one-liner-clean.
#
# WHY DIRECTED HERE (but undirected in case 04)? Goods flow one way through
# a supply chain (supplier -> DC -> retailer), so directed betweenness
# counts only paths that respect that flow. Case 04's transit graph was
# undirected because adjacency there implies mutual access. And we target
# by OUT-degree, not in-degree: a DC that SUPPLIES many retailers
# downstream is the real risk; how many suppliers feed INTO it matters
# less for whether retailers stay covered.

cent <- tibble(
  node_id     = igraph::V(g)$name,
  tier        = igraph::V(g)$tier,
  in_degree   = igraph::degree(g, mode = "in"),
  out_degree  = igraph::degree(g, mode = "out"),
  w_in        = igraph::strength(g, mode = "in",  weights = igraph::E(g)$capacity),
  w_out       = igraph::strength(g, mode = "out", weights = igraph::E(g)$capacity),
  betweenness = igraph::betweenness(g, directed = TRUE)
)

# Most-critical DC by betweenness. These are the candidates an attacker
# would target if they understood the network structure.
top_btwn_dcs <- cent |>
  filter(tier == 2) |>
  arrange(desc(betweenness)) |>
  head(5)
print(top_btwn_dcs)


# 3. Targeted vs random attacks ##############################################
#
# We remove k nodes from tier 2 (DCs) under three strategies:
#   - random
#   - top-k by out-degree (volume hubs)
#   - top-k by betweenness (bridges)
# and track supply coverage as k grows from 0 to 15.

dcs <- cent |> filter(tier == 2)
# Seed once here (not inside run_strategy). Only the "random" strategy
# draws; "out_degree" and "betweenness" are deterministic. Seeding at this
# scope makes the whole script's random attacks reproducible run-to-run.
set.seed(42)  # deterministic random-attack ordering

run_strategy <- function(strategy, ks) {
  vapply(ks, function(k) {
    if (k == 0) return(base)
    if (strategy == "random") {
      victims <- sample(dcs$node_id, size = k)
    } else if (strategy == "out_degree") {
      victims <- dcs |> arrange(desc(out_degree)) |> head(k) |> pull(node_id)
    } else if (strategy == "betweenness") {
      victims <- dcs |> arrange(desc(betweenness)) |> head(k) |> pull(node_id)
    } else {
      stop("unknown strategy")
    }
    remove_and_score(g, victims)
  }, numeric(1))
}

ks      <- 0:15
results <- tibble(
  k           = ks,
  random      = run_strategy("random", ks),
  out_degree  = run_strategy("out_degree", ks),
  betweenness = run_strategy("betweenness", ks)
)

# Reading the table: each column is an attack strategy, each row a number
# of removed DCs (k). LOWER coverage = MORE damage, so the strategy with
# the smallest numbers is the most effective attack (compare across a row).
results |> mutate(across(-k, ~round(., 3))) |> print()
cat(sprintf("🧪 At k=10: random=%.3f  out_degree=%.3f  betweenness=%.3f\n",
            results$random[results$k == 10],
            results$out_degree[results$k == 10],
            results$betweenness[results$k == 10]))


# 4. Visualize ###############################################################

results_long <- results |>
  pivot_longer(-k, names_to = "strategy", values_to = "coverage")

p <- ggplot(results_long,
       aes(x = k, y = coverage, color = strategy, shape = strategy)) +
  geom_line() +
  geom_point(size = 2.5) +
  scale_y_continuous(limits = c(0, 1.02)) +
  labs(x     = "# of distribution centers removed (k)",
       y     = "supply coverage (fraction of retailers reachable)",
       title = "Targeted vs random DC failures") +
  theme_classic(base_size = 13)

# Show interactively AND save a copy (Rscript otherwise hides it in Rplots.pdf).
print(p)
ggsave(here::here("code", "05_supply-chain", "attack_strategies.png"),
       p, width = 6.5, height = 4.5, dpi = 120)
cat("💾 Saved attack_strategies.png\n")


# 5. Learning Check ##########################################################
#
# QUESTION: After removing the 5 highest-betweenness distribution
# centers, what is the supply coverage? Report to 3 decimal places.

top5_btwn <- dcs |>
  arrange(desc(betweenness)) |>
  head(5) |>
  pull(node_id)

answer <- remove_and_score(g, top5_btwn)

cat(sprintf("\n📝 Learning Check answer: %.3f\n", answer))

cat("\n🎉 Done. Move on to the case study report when you're ready.\n")
```

---

## `code/05_supply-chain/example.py`

```python
"""Case Study 05 — Supply Chain Resilience (Python track).

The interactive lab let you click nodes to "fail" them and watched
supply coverage collapse. Here we do the same in code, on a synthetic
580-node 3-tier supply chain.

The resilience metric: SUPPLY COVERAGE = fraction of retailers
(tier 3) still reachable from at least one supplier (tier 1) after
the removals. 1.00 = nothing broken. 0.50 = half of all retailers
have lost their last incoming path from a supplier.

The point of this case: random failures, high-degree failures, and
high-betweenness failures cause DIFFERENT amounts of damage.
"""

# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `igraph` for graph + centrality, `pandas`/`numpy` to keep the
# per-strategy attack results tidy and easy to plot.
import pandas as pd
import numpy as np
import igraph as ig
import matplotlib.pyplot as plt

## 0.2 Load helpers ##########################################################

# `supply_coverage()` and `remove_and_score()` live in functions.py.
# They compute the % of retailers still reachable from any supplier,
# before and after a list of victims is deleted.
from functions import (
    load_nodes, load_edges, build_graph,
    supply_coverage, remove_and_score,
)

print("\n🚀 Case Study 05 — Supply Chain Resilience (Python)")
print("   Three attack strategies on a 580-node 3-tier chain. Which one hurts most?\n")

## 0.3 Load data #############################################################

nodes = load_nodes()
edges = load_edges()
# Tier composition: tier 1 = suppliers, tier 2 = DCs, tier 3 = retailers
print(nodes["tier"].value_counts().sort_index())

g = build_graph(nodes, edges)
print(g.summary())
n1 = int((nodes['tier'] == 1).sum())
n2 = int((nodes['tier'] == 2).sum())
n3 = int((nodes['tier'] == 3).sum())
print(f"✅ Loaded chain: {g.vcount()} nodes ({n1} suppliers, {n2} DCs, {n3} retailers).")


# 1. Baseline supply coverage ################################################
#
# Before we break anything, what fraction of retailers are reachable
# from at least one supplier? That's our denominator.

base = supply_coverage(g)
print(f"📊 Baseline supply coverage: {base:.3f}")


# 2. Centrality per tier #####################################################
#
# To target the right nodes we need per-node centrality. For a
# directed network we use both weighted degree (capacity) and
# betweenness. We hold these in a tidy table so the attack loop
# below stays one-liner-clean.
#
# WHY DIRECTED HERE (but undirected in case 04)? Goods flow one way through
# a supply chain (supplier -> DC -> retailer), so directed betweenness
# counts only paths that respect that flow. Case 04's transit graph was
# undirected because adjacency there implies mutual access. And we target
# by OUT-degree, not in-degree: a DC that SUPPLIES many retailers
# downstream is the real risk; how many suppliers feed INTO it matters
# less for whether retailers stay covered.

cent = pd.DataFrame({
    "node_id":     g.vs["name"],
    "tier":        g.vs["tier"],
    "in_degree":   g.degree(mode="in"),
    "out_degree":  g.degree(mode="out"),
    "w_in":        g.strength(mode="in",  weights="capacity"),
    "w_out":       g.strength(mode="out", weights="capacity"),
    "betweenness": g.betweenness(directed=True),
})

# Most-critical DC by betweenness. These are the candidates an attacker
# would target if they understood the network structure.
print(
    cent.query("tier == 2").sort_values("betweenness", ascending=False).head(5)
)


# 3. Targeted vs random attacks ##############################################
#
# We remove k nodes from tier 2 (DCs) under three strategies:
#   - random
#   - top-k by out-degree (volume hubs)
#   - top-k by betweenness (bridges)
# and track supply coverage as k grows from 0 to 15.

dcs = cent.query("tier == 2").copy()
# One seeded generator, created once and reused across every run_strategy
# call below. Only the "random" strategy draws from it; "out_degree" and
# "betweenness" are deterministic. Because we seed once here (not inside the
# function) the whole script's random attacks are reproducible run-to-run.
rng = np.random.default_rng(42)

def run_strategy(strategy: str, ks: list[int]) -> list[float]:
    out = []
    for k in ks:
        if k == 0:
            out.append(base)
            continue
        if strategy == "random":
            victims = rng.choice(dcs["node_id"].to_numpy(), size=k, replace=False)
        elif strategy == "out_degree":
            victims = dcs.sort_values("out_degree", ascending=False).head(k)["node_id"]
        elif strategy == "betweenness":
            victims = dcs.sort_values("betweenness", ascending=False).head(k)["node_id"]
        else:
            raise ValueError(strategy)
        out.append(remove_and_score(g, victims))
    return out

ks = list(range(0, 16))
results = pd.DataFrame({
    "k":            ks,
    "random":       run_strategy("random", ks),
    "out_degree":   run_strategy("out_degree", ks),
    "betweenness":  run_strategy("betweenness", ks),
})

# Reading the table: each column is an attack strategy, each row a number
# of removed DCs (k). LOWER coverage = MORE damage, so the strategy with
# the smallest numbers is the most effective attack (compare across a row).
print(results.round(3))
row10 = results.loc[results["k"] == 10].iloc[0]
print(f"🧪 At k=10: random={row10['random']:.3f}  out_degree={row10['out_degree']:.3f}"
      f"  betweenness={row10['betweenness']:.3f}")


# 4. Visualize ###############################################################

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.plot(results["k"], results["random"],      marker="o", label="random DCs")
ax.plot(results["k"], results["out_degree"],  marker="s", label="top-k by out-degree")
ax.plot(results["k"], results["betweenness"], marker="^", label="top-k by betweenness")
ax.set_xlabel("# of distribution centers removed (k)")
ax.set_ylabel("supply coverage (fraction of retailers reachable)")
ax.set_title("Targeted vs random DC failures")
ax.set_ylim(0, 1.02)
ax.legend()
fig.tight_layout()
fig.savefig("supply_attack_curve.png", dpi=120)
plt.close(fig)
print("💾 Saved supply_attack_curve.png")


# 5. Learning Check ##########################################################
#
# QUESTION: After removing the 5 highest-betweenness distribution
# centers, what is the supply coverage of this network? Report to 3
# decimal places.

top5_btwn = dcs.sort_values("betweenness", ascending=False).head(5)["node_id"]
answer = remove_and_score(g, top5_btwn)

print(f"\n📝 Learning Check answer: {answer:.3f}")

print("\n🎉 Done. Move on to the case study report when you're ready.")
```

---

## `code/05_supply-chain/functions.R`

```r
#' @name functions.R
#' @title Helpers for the Supply Chain Resilience case study

library(readr)
library(dplyr)
library(igraph)
library(here)

.case_dir <- function() here::here("code", "05_supply-chain", "data")

load_nodes <- function() readr::read_csv(file.path(.case_dir(), "nodes.csv"),
                                         show_col_types = FALSE)
load_edges <- function() readr::read_csv(file.path(.case_dir(), "edges.csv"),
                                         show_col_types = FALSE)

#' Build the directed supply-chain graph.
build_graph <- function(nodes = load_nodes(), edges = load_edges()) {
  igraph::graph_from_data_frame(
    d        = edges,
    directed = TRUE,
    vertices = nodes
  )
}

#' Supply coverage = fraction of retailers (tier-3 nodes) that are
#' still reachable from at least one supplier (tier-1 node) in the
#' graph passed in. This is the resilience metric the case study uses.
supply_coverage <- function(g) {
  v_tier <- igraph::V(g)$tier
  suppliers <- igraph::V(g)[v_tier == 1]
  retailers <- igraph::V(g)[v_tier == 3]
  if (length(retailers) == 0) return(NA_real_)

  # For each retailer, check if any supplier can reach it via directed paths.
  # `subcomponent(mode = "out")` from a supplier gives every vertex it can reach.
  reachable <- rep(FALSE, length(retailers))
  ret_names <- retailers$name
  for (s in suppliers) {
    reachable_from_s <- igraph::subcomponent(g, s, mode = "out")$name
    reachable <- reachable | (ret_names %in% reachable_from_s)
    if (all(reachable)) break
  }
  mean(reachable)
}

#' Simulate removing a set of nodes and report supply coverage.
remove_and_score <- function(g, victims) {
  g2 <- igraph::delete_vertices(g, victims)
  supply_coverage(g2)
}
```

---

## `code/05_supply-chain/functions.py`

```python
"""Helpers for the Supply Chain Resilience case study."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable
import pandas as pd
import igraph as ig


def _case_dir() -> Path:
    return Path(__file__).resolve().parent / "data"


def load_nodes() -> pd.DataFrame:
    return pd.read_csv(_case_dir() / "nodes.csv")


def load_edges() -> pd.DataFrame:
    return pd.read_csv(_case_dir() / "edges.csv")


def build_graph(nodes: pd.DataFrame | None = None,
                edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the directed supply-chain graph."""
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    return ig.Graph.DataFrame(
        edges=edges,
        directed=True,
        vertices=nodes,
        use_vids=False,
    )


def supply_coverage(g: ig.Graph) -> float:
    """Fraction of retailers (tier 3) reachable from any supplier (tier 1)."""
    suppliers = [v.index for v in g.vs if v["tier"] == 1]
    retailers = [v.index for v in g.vs if v["tier"] == 3]
    if not retailers:
        return float("nan")
    retailer_set = set(retailers)
    reachable: set[int] = set()
    for s in suppliers:
        reachable.update(g.subcomponent(s, mode="out"))
        if retailer_set.issubset(reachable):
            break
    return len(reachable & retailer_set) / len(retailer_set)


def remove_and_score(g: ig.Graph, victims: Iterable[str]) -> float:
    """Remove a set of nodes by name and report supply coverage."""
    victims = set(victims)
    g2 = g.copy()
    to_delete = [v.index for v in g2.vs if v["name"] in victims]
    g2.delete_vertices(to_delete)
    return supply_coverage(g2)
```

---

## `code/06_permutation/README.md`

# Case Study 07 — Network Permutation Testing

> Interactive lab: [`docs/case-studies/permutation.html`](../../docs/case-studies/permutation.html)
>
> Skill: **Infer** · Data: 400-node synthetic mobility network with
> planted neighborhood-demo correlation (no direct edge-level
> homophily — the homophily comes from where people live)

## What you'll learn

When you compute a network statistic (homophily, assortativity,
mean within-group edge weight) you need a **null model** to decide
whether the value you saw could have happened by chance. This case
makes the point that the null model is *not* obvious:

- An **unblocked** permutation (shuffle labels across all nodes)
  ignores community structure. It will tell you anything is
  "significant" if neighborhoods are themselves segregated.
- A **block** permutation (shuffle labels only within community)
  controls for that. It's the right null when the question is
  "additional homophily beyond what neighborhood structure
  explains."

The dataset is engineered so the two nulls disagree dramatically:
unblocked p < 0.001, block-permuted p ≈ 0.89.

## Prerequisites

- The interactive lab.
- Case study 02 (Joins) and case study 03 (Aggregation).
- R packages: `dplyr`, `tibble`, `ggplot2`, `igraph`, `here`.
- Python packages: see [`code/requirements.txt`](../requirements.txt).

## Files in this folder

```
07_permutation/
├── README.md
├── example.R
├── example.py
├── functions.R   # `assort_by()`, `permute_labels()`
├── functions.py
└── data/
    ├── nodes.csv  # 400 nodes with neighborhood + demo labels
    ├── edges.csv  # ~18,000 weighted undirected edges
    └── _generate.py
```

## How to run

```bash
Rscript code/06_permutation/example.R
python  code/06_permutation/example.py
```

## Learning check (submit this number)

> **What is the *block-permuted* p-value for nominal assortativity
> by `demo`, using `neighborhood` as the block, with 500
> permutations and seed 42?** (3 decimal places.)

## Your Project Case Study

If you pick this case study, you'll test a homophily claim on *your*
network using two different null models and report when they
disagree.

### Suggested project questions

1. **Two nulls, two stories.** Pick a categorical node attribute in
   your network. Compute observed assortativity. Compute the
   unblocked-permutation null and a block-permutation null on a
   meaningful blocking variable. Report both p-values and discuss.

2. **What's the right block?** Find at least two plausible blocking
   variables. Compute the block-permuted p-value under each.
   Report which choice you prefer and why, given your question.

3. **Beyond assortativity.** Replace nominal assortativity with a
   different network statistic (mean within-group edge weight,
   share of edges that are within-group). Show the same
   blocked/unblocked comparison still applies.

### Choosing your blocking variable

The hard part isn't the code — it's justifying the block. A clean rule:
**your blocking variable is the confounder you most need to rule out.**
Write your claim as "X relates to Y *beyond what Z explains*" — Z is your
block. If a skeptic could say "that's just because of Z," put Z in the
block. For a worked example of carrying a question and its controls
through a report in prose, see
[`docs/assignments/sample-report.md`](../../docs/assignments/sample-report.md).

### Report

- **Question.** One sentence.
- **Network and attribute.** Nodes, edges, the attribute you're
  testing homophily on, plus the blocking variable and why.
- **Procedure.** Number of permutations, seed, statistic.
- **Results.** Both p-values in prose, with one histogram of the
  null distributions and the observed.
- **What this tells you, and what it doesn't.** 2-3 sentences.
  Specifically: when you have only two nulls and they disagree,
  which one is "right" depends on the question you set out to ask.

## Further reading

- The classic intro to network permutation testing is Newman's
  *Networks* (Chapter 7). The block-permutation idea is sometimes
  called a "stratified" permutation.
- The case study's "Bluebikes" framing is a real-world example of
  this trap: AM ridership looks racially segregated even when
  controlling for income, but the right null can disagree.

---

## `code/06_permutation/data/_generate.py`

```python
"""Generate the synthetic data for case 07 (permutation testing).

We want a network where:
  - nodes have a categorical attribute (`demo` in {A, B})
  - edges have a planted homophily: more A-A and B-B than A-B
  - nodes also have a neighborhood, and demographics correlate with
    neighborhood (so a naive "shuffle labels everywhere" null model
    is too permissive — a *block* permutation that shuffles labels
    only within neighborhood is the right null)

400 nodes, 12 neighborhoods, ~25,000 weighted edges.

Run:
    python code/06_permutation/data/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

def main() -> None:
    rng = np.random.default_rng(SEED)

    n_nodes = 400
    n_nbhds = 12

    # neighborhood for each node
    nbhd = rng.integers(0, n_nbhds, size=n_nodes)
    # demographic prob varies by neighborhood (some are mostly A, some mostly B)
    nbhd_p_A = rng.uniform(0.1, 0.9, size=n_nbhds)
    p_A = nbhd_p_A[nbhd]
    demo = np.where(rng.random(n_nodes) < p_A, "A", "B")

    nodes = pd.DataFrame({
        "node_id":      [f"V{i:04d}" for i in range(n_nodes)],
        "neighborhood": [f"N{n:02d}" for n in nbhd],
        "demo":         demo,
    })

    # build edges: NO planted edge-level homophily on `demo`. Instead,
    # we plant strong same-NEIGHBORHOOD bias. Because `demo` correlates
    # with neighborhood, the network will LOOK demo-homophilous when
    # you ignore neighborhood — but if you condition on neighborhood
    # (block permutation), the extra homophily is roughly zero.
    #
    # This is the canonical "wrong null model gives wrong answer"
    # demonstration the case study is built around.
    n_edges = 25_000

    start_idx = rng.integers(0, n_nodes, size=n_edges)
    same_nbhd = rng.random(n_edges) < 0.65  # 65% within-neighborhood
    end_idx = np.empty(n_edges, dtype=np.int64)
    for i in range(n_edges):
        if same_nbhd[i]:
            pool = np.flatnonzero(nbhd == nbhd[start_idx[i]])
        else:
            pool = np.flatnonzero(nbhd != nbhd[start_idx[i]])
        pool = pool[pool != start_idx[i]]
        end_idx[i] = rng.choice(pool)

    edges = pd.DataFrame({
        "from":   nodes["node_id"].to_numpy()[start_idx],
        "to":     nodes["node_id"].to_numpy()[end_idx],
        "weight": rng.integers(1, 8, size=n_edges),
    })
    # aggregate duplicate edges (same start, same end)
    edges = (edges.groupby(["from", "to"], as_index=False)["weight"].sum()
                  .sort_values(["from", "to"]).reset_index(drop=True))

    nodes = nodes.sort_values("node_id").reset_index(drop=True)

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)
    print(f"wrote {HERE / 'nodes.csv'} ({len(nodes)} nodes)")
    print(f"wrote {HERE / 'edges.csv'} ({len(edges)} unique edges)")


if __name__ == "__main__":
    main()
```

---

## `code/06_permutation/example.R`

```r
#' @name example.R
#' @title Case Study 07 — Network Permutation Testing
#' @author <your-name-here>
#' @description
#' The lab walked you through a key idea: when you compute a network
#' statistic (homophily, assortativity, mean within-group edge
#' weight), you need a NULL MODEL to know if the value you saw is
#' "real" or just noise.
#'
#' What is a null model? It asks: what values would our statistic take
#' if the effect we're testing did NOT exist? We build that "no-effect"
#' world by shuffling labels many times and recomputing the statistic
#' each time; that spread is the null distribution. If our observed
#' value sits comfortably inside it, we can't tell it apart from chance
#' ("fail to reject"); if it sits far out in the tail, we can.
#'
#' But — *random with respect to what?* If your network has community
#' structure that you're not controlling for, shuffling labels
#' everywhere gives you a too-easy null. The right comparison is
#' often a BLOCK permutation: shuffle labels within community.
#'
#' If you know regression, a blocking variable is just a covariate you
#' control for. Block permutation holds that confounder fixed (it
#' shuffles labels only WITHIN each block) so you test the within-block
#' signal you actually care about; the unblocked null controls for
#' nothing, which is exactly why it looks "too significant" when
#' neighborhoods are segregated.
#'
#' We'll do both, on a synthetic network engineered to make the two
#' nulls disagree dramatically.


# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `igraph` for assortativity. `dplyr`/`tibble` for tidy results, ggplot
# for the two-null distribution plot.
library(dplyr)
library(tibble)
library(ggplot2)
library(igraph)
library(here)

## 0.2 Load helpers ##########################################################

# `assort_by()` wraps `igraph::assortativity_nominal()`; `permute_labels()`
# shuffles a vertex attribute, optionally within blocks defined by
# another attribute. Both live in functions.R.
source(here::here("code", "07_permutation", "functions.R"))

cat("\n🚀 Case Study 07 — Network Permutation Testing (R)\n")
cat("   Same observed stat, two null models. Watch the p-value change.\n\n")

## 0.3 Load data #############################################################

nodes <- load_nodes()
edges <- load_edges()
g     <- build_graph(nodes, edges)
g
nodes |> head()
cat(sprintf("✅ Loaded graph: %d nodes (demos A vs B in 10 neighborhoods).\n",
            igraph::vcount(g)))


# 1. Observed assortativity ##################################################
#
# Nominal assortativity: positive = same-demo edges over-represented;
# 0 = random; negative = disassortative. This is the number we'll test.

observed <- assort_by(g, "demo")
cat(sprintf("📊 Observed assortativity by `demo`: %.4f\n", observed))


# 2. Null model 1: UNBLOCKED permutation #####################################
#
# Shuffle the `demo` label across ALL nodes, recompute assortativity,
# repeat 500 times. The unblocked null breaks BOTH any demo-edge link
# AND any demo-neighborhood link — it's the "everything is random"
# baseline.

set.seed(42)
n_perm <- 500
null_unblocked <- numeric(n_perm)
for (i in seq_len(n_perm)) {
  g_perm <- permute_labels(g, "demo", block_by = NULL)
  null_unblocked[i] <- assort_by(g_perm, "demo")
}
p_unblocked <- mean(null_unblocked >= observed)
cat(sprintf("🧪 Unblocked null: mean = %+.4f  sd = %.4f  p = %.3f\n",
            mean(null_unblocked), sd(null_unblocked), p_unblocked))


# 3. Null model 2: BLOCK permutation by neighborhood #########################
#
# Shuffle `demo` ONLY within neighborhood. This preserves the
# neighborhood-level composition. A more conservative null, because
# some apparent "homophily" comes from the fact that A's and B's
# already live in different neighborhoods.
#
# Stats analogy: block_by = "neighborhood" == "control for neighborhood".
# We destroy only the within-neighborhood demo signal (what we're testing)
# while holding the neighborhood composition (the confounder) fixed.

null_blocked <- numeric(n_perm)
for (i in seq_len(n_perm)) {
  g_perm <- permute_labels(g, "demo", block_by = "neighborhood")
  null_blocked[i] <- assort_by(g_perm, "demo")
}
p_blocked <- mean(null_blocked >= observed)
cat(sprintf("🧪 Block-permuted null: mean = %+.4f  sd = %.4f  p = %.3f\n",
            mean(null_blocked), sd(null_blocked), p_blocked))

# Which direction is "good"? A LARGE p-value means FAIL TO REJECT — the
# observed value is unremarkable under this null. A SMALL one means REJECT.
cat(sprintf("ℹ️  p = %.3f is %s -> %s.\n", p_blocked,
            if (p_blocked > 0.05) "LARGE" else "SMALL",
            if (p_blocked > 0.05)
              "FAIL TO REJECT: the observed assortativity is ordinary once neighborhood is held fixed"
            else
              "REJECT: homophily remains beyond what neighborhood explains"))


# 4. Visualize ###############################################################

null_df <- bind_rows(
  tibble(null = "Unblocked",      value = null_unblocked),
  tibble(null = "Block-permuted", value = null_blocked)
)

p <- ggplot(null_df, aes(x = value, fill = null)) +
  geom_histogram(alpha = 0.6, position = "identity", bins = 30) +
  geom_vline(xintercept = observed, linetype = "dashed") +
  scale_fill_manual(values = c("Unblocked"      = "#3a8bc6",
                               "Block-permuted" = "#e07b3a")) +
  labs(x     = "Nominal assortativity by `demo`",
       y     = "# of permutations",
       title = "Two null models, two p-values",
       fill  = "Null model") +
  theme_classic(base_size = 13)

# Show interactively AND save a copy (Rscript otherwise hides it in Rplots.pdf).
print(p)
ggsave(here::here("code", "07_permutation", "two_null_distributions.png"),
       p, width = 7, height = 4.5, dpi = 120)
cat("💾 Saved two_null_distributions.png\n")


# 5. The take-home ###########################################################
#
# Compare the two p-values. The UNBLOCKED null is centered well below
# the observed — so unblocked says "very significant homophily". The
# BLOCKED null is centered AT OR ABOVE the observed — so blocked says
# "actually, this network is no more demographically homophilous than
# you'd expect from the fact that A's and B's already live in
# different neighborhoods."
#
# This is the canonical mistake the case study warns against. If you
# fit the wrong null model, you get the wrong answer with great
# confidence.
#
# WHY does the blocked null land so close to the observed value? Within a
# segregated neighborhood almost everyone shares the same demo label, so
# shuffling labels WITHIN a neighborhood barely changes the graph -- each
# permuted network looks almost like the real one, and the null piles up
# right around the observed statistic (so the observed looks ordinary). The
# unblocked null also scrambles geography, destroying the segregation that
# produced most of the assortativity in the first place -- so its null sits
# far below the observed value and the observed looks extreme. Same number,
# two nulls, opposite verdicts.
#
# WHICH NULL DO I REACH FOR ON MY OWN DATA? Decision rule:
#   - Use a BLOCKED null when a known structural variable (here:
#     neighborhood) already explains part of how the labels are
#     distributed, and you want to test the signal that REMAINS after
#     accounting for it. Block on the confounder.
#   - Use the UNBLOCKED null only when no such confounder exists (labels
#     are exchangeable across the whole graph).
# If in doubt, ask: "Would I be fooled by ecological sorting?" If yes
# (your groups cluster in space/teams/departments), block on that
# variable — otherwise you'll mistake sorting for direct homophily.


# 6. Learning Check ##########################################################
#
# QUESTION: What is the *block-permuted* p-value for assortativity by
# `demo`? (Use neighborhood as the block. 500 permutations, seed 42.)
# Report to 3 decimal places.

cat(sprintf("\n📝 Learning Check answer: %.3f\n", p_blocked))

cat("\n🎉 Done. Move on to the case study report when you're ready.\n")
```

---

## `code/06_permutation/example.py`

```python
"""Case Study 07 — Network Permutation Testing (Python track).

The lab walked you through a key idea: when you compute a network
statistic (homophily, assortativity, mean within-group edge weight),
you need a NULL MODEL to know if the value you saw is "real" or just
noise.

What is a null model? It asks: what values would our statistic take if
the effect we're testing did NOT exist? We build that "no-effect" world
by shuffling labels many times and recomputing the statistic each time;
that spread of shuffled values is the null distribution. If our real,
observed value sits comfortably inside that spread, we can't tell it
apart from chance ("fail to reject"); if it sits far out in the tail,
we can.

But — and this is the crucial part — *random with respect to what?*
If your network has community structure that you're not controlling
for, shuffling labels everywhere can give you a too-easy null. The
right comparison is often a **block permutation**: shuffle labels
within community.

If you know regression, a blocking variable is just a covariate you
control for. Block permutation holds that confounder fixed (it shuffles
labels only WITHIN each block) so you test the within-block signal you
actually care about; the unblocked null controls for nothing, which is
exactly why it looks "too significant" when neighborhoods are segregated.

We'll do both, on a synthetic network with planted demographic
homophily AND planted neighborhood-demo correlation.
"""

# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `igraph` for assortativity. `numpy` for the per-permutation array,
# `matplotlib` for the two-null distribution plot.
import pandas as pd
import numpy as np
import igraph as ig
import matplotlib.pyplot as plt

## 0.2 Load helpers ##########################################################

# `assort_by()` wraps `igraph.assortativity_nominal`; `permute_labels()`
# shuffles a vertex attribute, optionally within blocks defined by
# another attribute. Both live in functions.py.
from functions import (
    load_nodes, load_edges, build_graph, assort_by, permute_labels
)

print("\n🚀 Case Study 07 — Network Permutation Testing (Python)")
print("   Same observed stat, two null models. Watch the p-value change.\n")

## 0.3 Load data #############################################################

nodes = load_nodes()
edges = load_edges()
g     = build_graph(nodes, edges)
print(g.summary())
print(nodes.head())
print(f"✅ Loaded graph: {g.vcount()} nodes (demos A vs B in 10 neighborhoods).")


# 1. Observed assortativity ##################################################
#
# Nominal assortativity: positive = same-demo edges over-represented;
# 0 = random; negative = disassortative. This is the number we'll test.

observed = assort_by(g, "demo")
print(f"📊 Observed assortativity by `demo`: {observed:.4f}")


# 2. Null model 1: UNBLOCKED permutation #####################################
#
# Shuffle the `demo` label across ALL nodes, recompute assortativity,
# repeat 500 times. The unblocked null breaks BOTH any demo-edge link
# AND any demo-neighborhood link — it's the "everything is random"
# baseline.

rng = np.random.default_rng(42)
n_perm = 500
null_unblocked = np.empty(n_perm)
for i in range(n_perm):
    g_perm = permute_labels(g, "demo", block_by=None, rng=rng)
    null_unblocked[i] = assort_by(g_perm, "demo")

p_unblocked = float(np.mean(null_unblocked >= observed))
print(f"🧪 Unblocked null: mean = {null_unblocked.mean():+.4f}  "
      f"sd = {null_unblocked.std():.4f}  p = {p_unblocked:.3f}")


# 3. Null model 2: BLOCK permutation by neighborhood #########################
#
# Shuffle `demo` ONLY within neighborhood. This preserves the
# neighborhood-level composition. A more conservative null, because
# some apparent "homophily" comes from the fact that A's and B's
# already live in different neighborhoods.
#
# Stats analogy: `block_by="neighborhood"` == "control for neighborhood".
# We destroy only the within-neighborhood demo signal (what we're testing)
# while holding the neighborhood composition (the confounder) fixed.

null_blocked = np.empty(n_perm)
for i in range(n_perm):
    g_perm = permute_labels(g, "demo", block_by="neighborhood", rng=rng)
    null_blocked[i] = assort_by(g_perm, "demo")

p_blocked = float(np.mean(null_blocked >= observed))
print(f"🧪 Block-permuted null: mean = {null_blocked.mean():+.4f}  "
      f"sd = {null_blocked.std():.4f}  p = {p_blocked:.3f}")

# Which direction is "good"? A LARGE p-value means FAIL TO REJECT — the
# observed value is unremarkable under this null. A SMALL one means REJECT.
if p_blocked > 0.05:
    print(f"ℹ️  p = {p_blocked:.3f} is LARGE -> FAIL TO REJECT: the observed "
          f"assortativity is ordinary once neighborhood is held fixed.")
else:
    print(f"ℹ️  p = {p_blocked:.3f} is SMALL -> REJECT: homophily remains "
          f"beyond what neighborhood explains.")


# 4. Visualize the two null distributions vs the observed ####################

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.hist(null_unblocked, bins=30, alpha=0.55, label="Unblocked null",
        color="#3a8bc6")
ax.hist(null_blocked,   bins=30, alpha=0.55, label="Block-permuted null",
        color="#e07b3a")
ax.axvline(observed, color="black", linestyle="--", label=f"Observed = {observed:.3f}")
ax.set_xlabel("Nominal assortativity by `demo`")
ax.set_ylabel("# of permutations")
ax.set_title("Two null models, two p-values")
ax.legend()
fig.tight_layout()
fig.savefig("permutation_nulls.png", dpi=120)
plt.close(fig)
print("💾 Saved permutation_nulls.png")


# 5. The take-home ###########################################################
#
# Compare the two p-values. The UNBLOCKED null is centered well
# below the observed — so unblocked says "very significant homophily".
# The BLOCKED null is centered MUCH CLOSER to observed — so blocked
# says "okay, much of the apparent homophily was just because A's
# and B's live in different neighborhoods; the *additional* homophily
# beyond that is smaller."
#
# This is the canonical mistake the case study warns against. If you
# fit the wrong null model, you get the wrong answer with great
# confidence.
#
# WHY does the blocked null land so close to the observed value? Within a
# segregated neighborhood almost everyone shares the same demo label, so
# shuffling labels WITHIN a neighborhood barely changes the graph -- each
# permuted network looks almost like the real one, and the null piles up
# right around the observed statistic (so the observed looks ordinary). The
# unblocked null also scrambles geography, destroying the segregation that
# produced most of the assortativity in the first place -- so its null sits
# far below the observed value and the observed looks extreme. Same number,
# two nulls, opposite verdicts.
#
# WHICH NULL DO I REACH FOR ON MY OWN DATA? Decision rule:
#   - Use a BLOCKED null when a known structural variable (here:
#     neighborhood) already explains part of how the labels are
#     distributed, and you want the signal that REMAINS after accounting
#     for it. Block on the confounder.
#   - Use the UNBLOCKED null only when no such confounder exists.
# If in doubt, ask: "Would I be fooled by ecological sorting?" If your
# groups cluster in space/teams/departments, block on that variable.


# 6. Learning Check ##########################################################
#
# QUESTION: What is the *block-permuted* p-value for assortativity by
# `demo`? (Use neighborhood as the block. 500 permutations.) Report
# to 3 decimal places.

print(f"\n📝 Learning Check answer: {p_blocked:.3f}")

print("\n🎉 Done. Move on to the case study report when you're ready.")
```

---

## `code/06_permutation/functions.R`

```r
#' @name functions.R
#' @title Helpers for the Permutation case study

library(readr)
library(dplyr)
library(igraph)
library(here)

.case_dir <- function() here::here("code", "07_permutation", "data")

load_nodes <- function() readr::read_csv(file.path(.case_dir(), "nodes.csv"),
                                         show_col_types = FALSE)
load_edges <- function() readr::read_csv(file.path(.case_dir(), "edges.csv"),
                                         show_col_types = FALSE)

#' Build the graph (undirected, weighted) from node + edge tables.
build_graph <- function(nodes = load_nodes(), edges = load_edges()) {
  igraph::graph_from_data_frame(
    d = edges, directed = FALSE, vertices = nodes
  )
}

#' Nominal assortativity by `attr_name` (e.g. "demo").
#'
#' Uses igraph's built-in `assortativity_nominal()`. Returns a single
#' number; +1 = perfectly assortative, 0 = random, -1 = perfectly
#' disassortative.
assort_by <- function(g, attr_name) {
  igraph::assortativity_nominal(
    g,
    types = as.integer(factor(igraph::vertex_attr(g, attr_name)))
  )
}

#' Permute node labels (the column you name) and return a *new* graph
#' with the permuted labels. `block_by` = NULL means shuffle labels
#' across ALL nodes; otherwise shuffle labels WITHIN each block.
permute_labels <- function(g, attr_name, block_by = NULL) {
  labels <- igraph::vertex_attr(g, attr_name)
  if (is.null(block_by)) {
    new_labels <- sample(labels)
  } else {
    blocks <- igraph::vertex_attr(g, block_by)
    new_labels <- labels
    for (b in unique(blocks)) {
      mask <- blocks == b
      new_labels[mask] <- sample(labels[mask])
    }
  }
  g2 <- g
  g2 <- igraph::set_vertex_attr(g2, attr_name, value = new_labels)
  g2
}
```

---

## `code/06_permutation/functions.py`

```python
"""Helpers for the Permutation case study."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import igraph as ig


def _case_dir() -> Path:
    return Path(__file__).resolve().parent / "data"


def load_nodes() -> pd.DataFrame:
    return pd.read_csv(_case_dir() / "nodes.csv")


def load_edges() -> pd.DataFrame:
    return pd.read_csv(_case_dir() / "edges.csv")


def build_graph(nodes: pd.DataFrame | None = None,
                edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the graph (undirected, weighted) from node + edge tables."""
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    return ig.Graph.DataFrame(
        edges=edges, directed=False, vertices=nodes, use_vids=False
    )


def assort_by(g: ig.Graph, attr_name: str) -> float:
    """Nominal assortativity by ``attr_name`` (e.g. ``demo``).

    Returns a single number; +1 = perfectly assortative, 0 = random,
    -1 = perfectly disassortative.
    """
    types = pd.Categorical(g.vs[attr_name]).codes.tolist()
    return float(g.assortativity_nominal(types=types, directed=False))


def permute_labels(g: ig.Graph, attr_name: str,
                   block_by: str | None = None,
                   rng: np.random.Generator | None = None) -> ig.Graph:
    """Return a copy of ``g`` with node ``attr_name`` shuffled.

    ``block_by=None`` shuffles labels across ALL nodes; otherwise
    shuffles labels WITHIN each block (preserves the block-level
    composition).
    """
    if rng is None:
        rng = np.random.default_rng()
    labels = np.array(g.vs[attr_name])
    if block_by is None:
        new_labels = rng.permutation(labels)
    else:
        blocks = np.array(g.vs[block_by])
        new_labels = labels.copy()
        for b in np.unique(blocks):
            mask = blocks == b
            new_labels[mask] = rng.permutation(labels[mask])
    g2 = g.copy()
    g2.vs[attr_name] = new_labels.tolist()
    return g2
```

---

## `code/07_counterfactual/README.md`

# Case Study 09 — Counterfactual Monte Carlo

> Interactive lab: [`docs/case-studies/counterfactual.html`](../../docs/case-studies/counterfactual.html)
>
> Skill: **Predict** · Data: synthetic 180-station bikeshare-like
> network (Watts-Strogatz topology with Poisson-weighted edges)

## What you'll learn

How to ask "would this intervention *actually* help?" with
statistical honesty. The technique:

1. Re-draw every edge's weight from `Poisson(λ = observed_weight)`,
   R times, to get a *distribution* of plausible networks consistent
   with what you observed.
2. Apply your intervention to each replicate; recompute the metric.
3. Look at the distribution of `metric_intervention − metric_baseline`.
4. The 95% CI of that distribution tells you whether the
   intervention's effect is meaningfully different from zero.

In this case study, the baseline metric is weighted average path
length (APL), and the intervention is adding a high-ridership direct
edge between the two currently-farthest-apart stations.

## Prerequisites

- Case study 04 (Centrality) so you know what APL is and why it
  matters.
- The interactive lab.
- R packages: `dplyr`, `ggplot2`, `igraph`, `here`.
- Python packages: see [`code/requirements.txt`](../requirements.txt).

## Files in this folder

```
09_counterfactual/
├── README.md
├── example.R
├── example.py
├── functions.R    # `weighted_apl()`, `mc_apls()`
├── functions.py
└── data/
    ├── nodes.csv   # 180 stations
    ├── edges.csv   # 720 weighted undirected edges
    └── _generate.py
```

## How to run

```bash
Rscript code/07_counterfactual/example.R
python  code/07_counterfactual/example.py
```

## Learning check (submit this number)

> **For the intervention "add a high-ridership (~120 rides) edge
> between the two currently-farthest-apart stations" with R=500
> Monte Carlo replicates and seed=1, what is the LOW end of the 95%
> CI on the change in weighted APL?** (4 decimal places, signed.)

## Your Project Case Study

If you pick this case study, you'll propose an intervention on
*your* network and report whether the 95% CI on its effect crosses
zero.

### Suggested project questions

1. **Is this intervention real?** Pick an intervention that matters
   in your domain (add an edge, boost a weight, remove a node).
   Compute the 95% CI on its effect on a relevant metric. State in
   prose whether the effect is robust.

2. **Two interventions, one budget.** Propose two competing
   interventions. Compute each one's CI on the same metric. Report
   which is more reliably beneficial.

3. **Sensitivity to R.** Vary the number of Monte Carlo replicates
   (e.g. R = 100, 500, 2000). Report how the CI width shrinks. Find
   the smallest R that gives a CI within 10% of the R=2000 width.

### Decide your "threshold of practical significance" first

Significance is not magnitude. Before you run anything, write down what size
of change would actually make you act ("a >2% drop in weighted APL is worth a
new settlement rail"). Then report your effect *against the baseline* — the
script prints the baseline APL and the change as a % of it — so a tiny absolute
number becomes interpretable. A CI that misses zero but sits below your
threshold is "real but not worth it." For framing this in prose, see
[`docs/assignments/sample-report.md`](../../docs/assignments/sample-report.md).

### Report

- **Question.** One sentence: the intervention and the metric.
- **Network and baseline.** Nodes, edges, baseline metric value.
- **Procedure.** Resampling distribution, R, seed.
- **Results.** Numbers in prose: baseline metric, intervention
  mean, 95% CI. The two-distribution histogram is a strong figure.
- **What this tells you, and what it doesn't.** 2-3 sentences,
  particularly: a CI containing zero is *not* "the intervention
  doesn't work" — it's "you don't have enough evidence either way."

## Further reading

- The bootstrap (Efron 1979) and Monte Carlo simulation are the
  ancestors of this technique; if you want a deeper treatment,
  Davison & Hinkley's *Bootstrap Methods and their Application* is
  the canonical reference.
- The case study's framing (Lakeside Bikeshare) is fictional, but
  the workflow is widely used in transit and infrastructure
  planning to evaluate proposed changes before construction.

---

## `code/07_counterfactual/data/_generate.py`

```python
"""Generate the synthetic bikeshare network for case 09.

We want:
  - ~180 stations
  - undirected, weighted by typical daily riders (Poisson-distributed
    integers between 5 and 200)
  - small-world topology so APL is meaningful

We use a Watts-Strogatz model (ring lattice + rewiring) then assign
Poisson edge weights. APL of the unweighted graph is ~5; weighted APL
(using inverse weight as cost) gives a meaningful counterfactual
target.

Run:
    python code/07_counterfactual/data/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent
SEED = 42

def main() -> None:
    rng = np.random.default_rng(SEED)

    n = 180
    g = ig.Graph.Watts_Strogatz(dim=1, size=n, nei=4, p=0.08)
    edges = g.get_edgelist()

    rows = []
    for u, v in edges:
        rows.append({
            "from":    f"ST{u:03d}",
            "to":      f"ST{v:03d}",
            "ridership": int(rng.poisson(lam=60)) + 5,
        })
    edges_df = pd.DataFrame(rows).sort_values(["from", "to"]).reset_index(drop=True)

    nodes_df = pd.DataFrame({
        "node_id": [f"ST{i:03d}" for i in range(n)],
        "zone":    rng.choice(["downtown", "midtown", "east", "west"],
                              size=n, p=[0.3, 0.3, 0.2, 0.2]),
    })
    nodes_df = nodes_df.sort_values("node_id").reset_index(drop=True)

    nodes_df.to_csv(HERE / "nodes.csv", index=False)
    edges_df.to_csv(HERE / "edges.csv", index=False)
    print(f"wrote {HERE / 'nodes.csv'} ({len(nodes_df)} stations)")
    print(f"wrote {HERE / 'edges.csv'} ({len(edges_df)} weighted edges)")


if __name__ == "__main__":
    main()
```

---

## `code/07_counterfactual/example.R`

```r
#' @name example.R
#' @title Case Study 09 — Counterfactual Monte Carlo
#' @author <your-name-here>
#' @description
#' You propose an intervention in a network (add a station, add an
#' edge, boost an edge's volume) and want to know if it *actually*
#' improves a metric, or if any apparent improvement is within the
#' noise.
#'
#' The answer: bootstrap-style resampling. Re-draw edge weights from a
#' Poisson centered at observed values, R times, and look at the
#' distribution of your metric. Apply the intervention to each
#' replicate and compare distributions. The 95% CI on the difference
#' tells you whether the effect is real.
#'
#' Why Poisson? Edge weights here are COUNTS (rides), and Poisson is the
#' natural noise model for counts: its variance equals its mean, and it
#' never goes negative the way a Normal draw could. Caveat worth knowing:
#' if your counts are overdispersed (variance > mean, common in real
#' data), Poisson understates uncertainty and a negative-binomial draw
#' is better.
#'
#' We use a 180-station synthetic bikeshare network. The metric is
#' weighted average path length (lower is better). The intervention
#' adds a new direct edge between two stations that are currently
#' far apart.


# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `igraph` for distances + APL math. `dplyr` for the tidy result tables.
library(dplyr)
library(ggplot2)
library(igraph)
library(here)

## 0.2 Load helpers ##########################################################

# `weighted_apl()` computes the weighted average path length;
# `mc_apls()` runs R Poisson-resampled APL computations, optionally
# with an extra edge appended. Both live in functions.R.
source(here::here("code", "09_counterfactual", "functions.R"))

cat("\n🚀 Case Study 09 — Counterfactual Monte Carlo (R)\n")
cat("   Add one edge to a bikeshare network. Does APL really improve?\n\n")

## 0.3 Load data #############################################################

nodes <- load_nodes()
edges <- load_edges()
g     <- build_graph(nodes, edges)
g
cat(sprintf("✅ Loaded network: %d stations, %d edges.\n",
            igraph::vcount(g), igraph::ecount(g)))


# 1. Baseline weighted APL ###################################################
#
# APL = average over all (i, j) of the shortest-path *cost* between
# i and j. Cost is 1/ridership, so a high-ridership edge counts as
# "short" — it's a "well-traveled" path between its endpoints.

base_apl <- weighted_apl(g)
cat(sprintf("📊 Baseline weighted APL: %.5f\n", base_apl))

# Quick overdispersion check before trusting Poisson. Poisson assumes
# variance == mean. If the ratio is ~1, Poisson is a fair noise model; if
# it's >> 1 the counts are overdispersed and Poisson understates
# uncertainty (a negative-binomial draw would be better). One line tells
# you whether the model below is appropriate for YOUR data.
vmr <- var(igraph::E(g)$ridership) / mean(igraph::E(g)$ridership)
cat(sprintf("🧪 Edge-weight variance/mean ratio: %.2f  (%s)\n", vmr,
            if (vmr < 1.5) "≈1, Poisson is reasonable"
            else "overdispersed — consider negative binomial"))


# 2. Pick an intervention ####################################################
#
# Find two stations that are far apart in the current network. We'll
# propose adding a high-ridership (~120 rides) edge between them and
# see if that pulls the APL down meaningfully.

dist_mat <- igraph::distances(g, weights = igraph::E(g)$cost)
diag(dist_mat) <- -Inf
ij <- which(dist_mat == max(dist_mat), arr.ind = TRUE)[1, ]
station_a <- igraph::V(g)$name[ij[1]]
station_b <- igraph::V(g)$name[ij[2]]
cat(sprintf("🔗 farthest-apart pair: %s <-> %s (cost = %.4f)\n",
            station_a, station_b, dist_mat[ij[1], ij[2]]))

intervention <- tibble(
  from      = station_a,
  to        = station_b,
  ridership = 120
)


# 3. Monte Carlo: baseline vs counterfactual #################################
#
# For each of R = 500 replicates: Poisson-resample every edge's
# ridership around its observed value, rebuild the graph, and compute
# APL. Do this once WITHOUT the new edge (baseline) and once WITH it
# (counterfactual). The element-wise difference is the per-replicate
# treatment effect.

R <- 500
baseline_apls       <- mc_apls(edges, nodes, R = R, extra = NULL,         seed = 1)
counterfactual_apls <- mc_apls(edges, nodes, R = R, extra = intervention, seed = 1)

diffs <- counterfactual_apls - baseline_apls
ci    <- quantile(diffs, probs = c(0.025, 0.975))

# Significance is not magnitude. A CI that misses zero says the effect is
# real, not that it's big. Always read the change against the baseline APL
# so a tiny absolute number (e.g. -0.001) becomes interpretable as a %.
base_mean <- mean(baseline_apls)
cat(sprintf("📊 Baseline weighted APL:                %.4f\n", base_mean))
cat(sprintf("🧪 Counterfactual APL change (mean):     %+.5f  (%+.2f%% of baseline)\n",
            mean(diffs), 100 * mean(diffs) / base_mean))
cat(sprintf("🧪 95%% CI on the change:                 [%+.5f, %+.5f]\n",
            ci[[1]], ci[[2]]))
is_sig <- ci[[2]] < 0 || ci[[1]] > 0
cat(sprintf("📊 Effect significant at 95%%?            %s\n",
            if (is_sig) "True" else "False"))

# What does the verdict MEAN? A CI that MISSES zero says the effect's
# direction is real (still read the magnitude separately). A CI that
# INCLUDES zero does NOT say "the intervention does nothing" — it says we
# can't distinguish the effect from zero with this many replicates. The
# true effect might be small, or we might just be underpowered. "We can't
# tell" is itself a finding: it means gather more data before committing.
cat(sprintf("ℹ️  Interpretation: %s\n",
            if (is_sig)
              "CI misses zero — the change is directionally real (check size vs baseline)."
            else
              "CI includes zero — can't distinguish from no effect (not proof of 'no effect')."))


# 4. Visualize ###############################################################

mc_df <- bind_rows(
  tibble(apl = baseline_apls,       version = "Baseline"),
  tibble(apl = counterfactual_apls, version = "With intervention")
)

p1 <- ggplot(mc_df, aes(x = apl, fill = version)) +
  geom_histogram(alpha = 0.55, position = "identity", bins = 30) +
  labs(x = "weighted APL", y = "# of replicates",
       fill = NULL,
       title = paste0("Two distributions, R=", R, " replicates")) +
  theme_classic(base_size = 12)

p2 <- ggplot(tibble(d = diffs), aes(x = d)) +
  geom_histogram(fill = "#7b3ae0", alpha = 0.7, bins = 30) +
  geom_vline(xintercept = 0, linetype = "dashed") +
  geom_vline(xintercept = ci[[1]], color = "red", linetype = "dotted") +
  geom_vline(xintercept = ci[[2]], color = "red", linetype = "dotted") +
  labs(x = "APL change (counterfactual - baseline)",
       y = "# of replicates",
       title = "Difference distribution + 95% CI") +
  theme_classic(base_size = 12)

# Show interactively AND save copies (Rscript otherwise hides them in
# Rplots.pdf).
print(p1)
print(p2)
ggsave(here::here("code", "09_counterfactual", "mc_distributions.png"),
       p1, width = 6.5, height = 4.5, dpi = 120)
ggsave(here::here("code", "09_counterfactual", "mc_difference_ci.png"),
       p2, width = 6.5, height = 4.5, dpi = 120)
cat("💾 Saved mc_distributions.png and mc_difference_ci.png\n")


# 5. Learning Check ##########################################################
#
# QUESTION: For the intervention "add a high-ridership (~120 rides)
# edge between the two currently-farthest-apart stations" on this
# 180-station network, what is the 95% CI on the change in weighted
# APL (counterfactual - baseline), with R=500 replicates and seed=1?
# Report the LOW end of the CI rounded to 4 decimal places (signed).

cat(sprintf("\n📝 Learning Check answer (CI low): %.4f\n", ci[[1]]))

cat("\n🎉 Done. Move on to the case study report when you're ready.\n")
```

---

## `code/07_counterfactual/example.py`

```python
"""Case Study 09 — Counterfactual Monte Carlo (Python track).

The lab walked you through this problem: you propose an intervention
in a network (add a station, add an edge, boost an edge's volume)
and want to know if it *actually* improves a metric, or if any
apparent improvement is within the noise.

The answer: bootstrap-style resampling. Re-draw edge weights from a
Poisson centered at observed values, R times, and look at the
distribution of your metric. Apply the intervention to each replicate
and compare distributions. The 95% CI on the difference tells you
whether the effect is real.

Why Poisson? Edge weights here are COUNTS (rides), and Poisson is the
natural noise model for counts: its variance equals its mean, and it
never goes negative the way a Normal draw could. Caveat worth knowing:
if your counts are overdispersed (variance > mean, common in real data),
Poisson understates uncertainty and a negative-binomial draw is better.

We use a 180-station synthetic bikeshare network. The metric is
weighted average path length (lower is better — fewer "hops" between
stations, weighted by ridership). The intervention is adding a new
direct edge between two stations that are currently far apart.
"""

# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `igraph` for distances + APL math. `pandas` for tidy result tables.
# `matplotlib` for the side-by-side distribution + difference plots.
import pandas as pd
import numpy as np
import igraph as ig
import matplotlib.pyplot as plt

## 0.2 Load helpers ##########################################################

# `weighted_apl()` computes the weighted average path length;
# `mc_apls()` runs R Poisson-resampled APL computations, optionally
# with an extra edge appended. Both live in functions.py.
from functions import (
    load_nodes, load_edges, build_graph, weighted_apl, mc_apls,
)

print("\n🚀 Case Study 09 — Counterfactual Monte Carlo (Python)")
print("   Add one edge to a bikeshare network. Does APL really improve?\n")

## 0.3 Load data #############################################################

nodes = load_nodes()
edges = load_edges()
g     = build_graph(nodes, edges)
print(g.summary())
print(f"✅ Loaded network: {g.vcount()} stations, {g.ecount()} edges.")


# 1. Baseline weighted APL ###################################################
#
# APL = average over all (i, j) of the shortest-path *cost* between
# i and j. Cost is 1/ridership, so a high-ridership edge counts as
# "short" — it's a "well-traveled" path between its endpoints.

base_apl = weighted_apl(g)
print(f"📊 Baseline weighted APL: {base_apl:.5f}")

# Quick overdispersion check before trusting Poisson. Poisson assumes
# variance == mean. If the ratio is ~1, Poisson is a fair noise model; if
# it's >> 1 the counts are overdispersed and Poisson understates
# uncertainty (a negative-binomial draw would be better).
vmr = float(np.var(edges["ridership"]) / np.mean(edges["ridership"]))
note = "≈1, Poisson is reasonable" if vmr < 1.5 else "overdispersed — consider negative binomial"
print(f"🧪 Edge-weight variance/mean ratio: {vmr:.2f}  ({note})")


# 2. Pick an intervention ####################################################
#
# Find two stations that are far apart in the current network. We'll
# propose adding a high-ridership (~120 rides) edge between them and
# see if that pulls the APL down meaningfully.

dists = np.array(g.distances(weights="cost"))
np.fill_diagonal(dists, -np.inf)
i, j = np.unravel_index(np.argmax(dists), dists.shape)
station_a = g.vs[i]["name"]
station_b = g.vs[j]["name"]
print(f"🔗 farthest-apart pair: {station_a} <-> {station_b}  (cost = {dists[i, j]:.4f})")

intervention = pd.DataFrame({
    "from":     [station_a],
    "to":       [station_b],
    "ridership":[120],  # the proposed connector has decent ridership
})


# 3. Monte Carlo: baseline vs counterfactual #################################
#
# For each of R = 500 replicates: Poisson-resample every edge's
# ridership around its observed value, rebuild the graph, and compute
# APL. Do this once WITHOUT the new edge (baseline) and once WITH it
# (counterfactual). The element-wise difference is the per-replicate
# treatment effect.

R = 500
baseline_apls       = mc_apls(edges, nodes, R=R, extra=None,         seed=1)
counterfactual_apls = mc_apls(edges, nodes, R=R, extra=intervention, seed=1)

diffs = counterfactual_apls - baseline_apls
ci_low, ci_high = np.quantile(diffs, [0.025, 0.975])

# Significance is not magnitude. A CI that misses zero says the effect is
# real, not that it's big. Always read the change against the baseline APL
# so a tiny absolute number (e.g. -0.001) becomes interpretable as a %.
base_mean = baseline_apls.mean()
print(f"📊 Baseline weighted APL:                {base_mean:.4f}")
print(f"🧪 Counterfactual APL change (mean):     {diffs.mean():+.5f}  "
      f"({100 * diffs.mean() / base_mean:+.2f}% of baseline)")
print(f"🧪 95% CI on the change:                 [{ci_low:+.5f}, {ci_high:+.5f}]")
sig = ci_high < 0 or ci_low > 0
print(f"📊 Effect significant at 95%?            {'True' if sig else 'False'}")

# What does the verdict MEAN? A CI that MISSES zero says the effect's
# direction is real (still read the magnitude separately). A CI that
# INCLUDES zero does NOT say "the intervention does nothing" — it says we
# can't distinguish the effect from zero with this many replicates. "We
# can't tell" is itself a finding: gather more data before committing.
if sig:
    print("ℹ️  Interpretation: CI misses zero — the change is directionally "
          "real (check size vs baseline).")
else:
    print("ℹ️  Interpretation: CI includes zero — can't distinguish from no "
          "effect (NOT proof of 'no effect').")


# 4. Visualize the two distributions and the difference ######################

fig, axes = plt.subplots(1, 2, figsize=(11, 4))

ax = axes[0]
ax.hist(baseline_apls,        bins=30, alpha=0.55, label="Baseline",         color="#3a8bc6")
ax.hist(counterfactual_apls, bins=30, alpha=0.55, label="With intervention", color="#e07b3a")
ax.set_xlabel("weighted APL")
ax.set_ylabel("# of replicates")
ax.legend()
ax.set_title("Two distributions, R=500 replicates")

ax = axes[1]
ax.hist(diffs, bins=30, color="#7b3ae0", alpha=0.7)
ax.axvline(0,        color="black", linestyle="--", linewidth=1)
ax.axvline(ci_low,   color="red",   linestyle=":",  linewidth=1)
ax.axvline(ci_high,  color="red",   linestyle=":",  linewidth=1)
ax.set_xlabel("APL change (counterfactual - baseline)")
ax.set_ylabel("# of replicates")
ax.set_title("Difference distribution + 95% CI")

fig.tight_layout()
fig.savefig("counterfactual_ci.png", dpi=120)
plt.close(fig)
print("💾 Saved counterfactual_ci.png")


# 5. Learning Check ##########################################################
#
# QUESTION: For the intervention "add a high-ridership (~120 rides)
# edge between the two currently-farthest-apart stations" on this
# 180-station network, what is the 95% CI on the change in weighted
# APL (counterfactual - baseline), with R=500 replicates and seed=1?
# Report the LOW end of the CI rounded to 4 decimal places (signed).

print(f"\n📝 Learning Check answer (CI low): {ci_low:.4f}")

print("\n🎉 Done. Move on to the case study report when you're ready.")
```

---

## `code/07_counterfactual/functions.R`

```r
#' @name functions.R
#' @title Helpers for the Counterfactual Monte Carlo case study

library(readr)
library(dplyr)
library(igraph)
library(here)

.case_dir <- function() here::here("code", "09_counterfactual", "data")

load_nodes <- function() readr::read_csv(file.path(.case_dir(), "nodes.csv"),
                                         show_col_types = FALSE)
load_edges <- function() readr::read_csv(file.path(.case_dir(), "edges.csv"),
                                         show_col_types = FALSE)

#' Build the bikeshare graph (undirected) with a `cost` edge attribute.
#'
#' For weighted APL, cost = 1 / ridership so that higher-ridership
#' edges are "shorter."
build_graph <- function(nodes = load_nodes(), edges = load_edges(),
                        with_extra = NULL) {
  if (!is.null(with_extra)) edges <- bind_rows(edges, with_extra)
  edges <- edges |>
    mutate(cost = 1 / pmax(ridership, 1))
  igraph::graph_from_data_frame(
    d = edges, directed = FALSE, vertices = nodes
  )
}

#' Weighted APL using `cost` as edge weight.
weighted_apl <- function(g) {
  igraph::mean_distance(g, weights = igraph::E(g)$cost, directed = FALSE)
}

#' Monte Carlo: draw `R` replicates of the network where each edge's
#' ridership is resampled from Poisson(lambda = observed_ridership),
#' rebuild, and return a vector of weighted APLs.
mc_apls <- function(edges, nodes, R = 500, extra = NULL,
                    seed = 1L) {
  set.seed(seed)
  out <- numeric(R)
  base_ridership <- edges$ridership
  for (i in seq_len(R)) {
    new_ridership <- rpois(length(base_ridership), lambda = base_ridership)
    new_edges <- edges
    new_edges$ridership <- new_ridership
    if (!is.null(extra)) {
      e_extra <- extra
      e_extra$ridership <- rpois(nrow(extra), lambda = extra$ridership)
      new_edges <- bind_rows(new_edges, e_extra)
    }
    g <- build_graph(nodes, new_edges)
    out[i] <- weighted_apl(g)
  }
  out
}
```

---

## `code/07_counterfactual/functions.py`

```python
"""Helpers for the Counterfactual Monte Carlo case study."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import igraph as ig


def _case_dir() -> Path:
    return Path(__file__).resolve().parent / "data"


def load_nodes() -> pd.DataFrame:
    return pd.read_csv(_case_dir() / "nodes.csv")


def load_edges() -> pd.DataFrame:
    return pd.read_csv(_case_dir() / "edges.csv")


def build_graph(nodes: pd.DataFrame, edges: pd.DataFrame,
                with_extra: pd.DataFrame | None = None) -> ig.Graph:
    """Build the bikeshare graph (undirected) with a ``cost`` edge attr.

    For weighted APL, cost = 1 / max(ridership, 1) so that
    higher-ridership edges are "shorter."
    """
    e = edges.copy()
    if with_extra is not None and len(with_extra) > 0:
        e = pd.concat([e, with_extra], ignore_index=True)
    e["cost"] = 1.0 / np.maximum(e["ridership"].to_numpy(), 1)
    return ig.Graph.DataFrame(edges=e, directed=False, vertices=nodes,
                              use_vids=False)


def weighted_apl(g: ig.Graph) -> float:
    """Weighted APL using ``cost`` as edge weight."""
    return float(g.average_path_length(weights="cost", directed=False))


def mc_apls(edges: pd.DataFrame, nodes: pd.DataFrame,
            R: int = 500,
            extra: pd.DataFrame | None = None,
            seed: int = 1) -> np.ndarray:
    """Monte Carlo: ``R`` replicates of the network where each edge's
    ridership is resampled from Poisson(lambda = observed_ridership),
    rebuild, and return a vector of weighted APLs.
    """
    rng = np.random.default_rng(seed)
    out = np.empty(R)
    base_ridership = edges["ridership"].to_numpy()
    for i in range(R):
        new_r = rng.poisson(lam=base_ridership)
        new_edges = edges.copy()
        new_edges["ridership"] = new_r
        extra_resampled = None
        if extra is not None and len(extra) > 0:
            ex = extra.copy()
            ex["ridership"] = rng.poisson(lam=ex["ridership"].to_numpy())
            extra_resampled = ex
        g = build_graph(nodes, new_edges, with_extra=extra_resampled)
        out[i] = weighted_apl(g)
    return out
```

---

## `code/08_gnn-by-hand/README.md`

# Case Study 10 — GNN by Hand

> Interactive lab: [`docs/case-studies/gnn-by-hand.html`](../../docs/case-studies/gnn-by-hand.html)
>
> Skill: **Predict** · Data: 6-node toy supply chain (in lockstep
> with the case study lab) + 200-node project-scale variant with
> planted bottlenecks

## What you'll learn

A Graph Neural Network's "magic" is one specific arithmetic step:
**neighborhood aggregation**. This case strips a GCN down to its
forward pass in numpy and walks through it node by node. You will:

- Build the adjacency matrix with self-loops.
- Symmetric-normalize it (Kipf & Welling 2017).
- Apply a single GCN layer: `H = ReLU(A_norm @ X @ W)`.
- Stack a second layer.
- See that the *bottleneck* node — which has no special features but
  many converging neighbors — ends up with the largest embedding
  values. That's GNN aggregation showing up exactly where you'd hope.

## Track note: R reaches full parity via reticulate

R doesn't have a widely-used, well-maintained Graph Neural Network
library — so instead of re-deriving the math, the R track *borrows* the
Python one. `example.R` drives the same numpy GCN functions in
`functions.py` (`adjacency`, `normalize`, `gcn_layer`) through
`reticulate`, while doing the data loading, plotting, and reporting
natively in R. Because the forward pass runs through the identical numpy
code, the R Learning Check is **byte-identical** to the Python one. Both
tracks are fully runnable; pick whichever you're comfortable in.

## Prerequisites

- The interactive lab.
- Case study 04 (Centrality) so you've seen what "neighborhood"
  means structurally.
- Python packages: see [`code/requirements.txt`](../requirements.txt).
  This case uses only `numpy`, `pandas`, and `matplotlib`.

## Files in this folder

```
10_gnn-by-hand/
├── README.md
├── example.R           # R track: drives functions.py's GCN via reticulate
├── example.py          # Python track
├── functions.R         # R loaders + reticulate bridge to the GCN functions
├── functions.py        # adjacency(), normalize(), gcn_layer()
└── data/
    ├── tiny_nodes.csv  / tiny_edges.csv   # 6-node toy
    ├── large_nodes.csv / large_edges.csv  # 200-node project-scale
    └── _generate.py
```

## How to run

```bash
python  code/08_gnn-by-hand/example.py    # Python track
Rscript code/08_gnn-by-hand/example.R     # R track (calls functions.py via reticulate)
```

The R track needs the `reticulate` package and a Python with `numpy` +
`pandas`. On a current `reticulate` (>= 1.41) the script provisions those
automatically via `py_require()`; otherwise point `reticulate` at a Python
that already has them (e.g. `RETICULATE_PYTHON`).

## Learning check (submit this string)

> **With the layer weights `W1` and `W2` defined in `example.py`
> (symmetric normalization, ReLU, self-loops), what is the final
> embedding (3 numbers) for node 4 on the *tiny* network?**

Submit a comma-separated string of three numbers rounded to 4
decimal places. Example format: `0.1234, -0.5678, 0.9012`.

## Your Project Case Study

If you pick this case study, you'll implement the GNN forward pass
on a slice of *your* network and discuss what the embeddings encode.

### Suggested project questions

1. **Embed your nodes.** Build a 2-feature input matrix from any
   two node attributes in your network. Run a 1-layer GCN with
   sensible random or hand-picked weights. Report the top 5 nodes
   by L2 norm of the embedding, and discuss what they have in
   common structurally.

2. **Aggregation choices.** Implement the GCN with three different
   aggregations: sum, mean, and max-pool over neighbors. Report
   the top-5 nodes by embedding-L2 under each, and discuss why
   different aggregations highlight different nodes.

3. **Depth matters.** Run 1-, 2-, and 3-layer GCNs on the same
   features. Report how the embedding's "receptive field" grows
   with depth. Find a node whose embedding *changes most* between
   1 layer and 3 layers.

### Report

- **Question.** One sentence.
- **Network.** Nodes, edges, input features (and where they came
  from), N, E.
- **Procedure.** Layer dims, weights (fixed or random with seed),
  activation, normalization.
- **Results.** Numbers in prose; a 2-D embedding scatter colored by
  some structural property is a strong figure.
- **What this tells you, and what it doesn't.** 2-3 sentences,
  especially: hand-built GCNs with non-learned weights are useful
  for *intuition*, not for prediction; for prediction you'd train
  the weights against a label.

## Further reading

- Kipf & Welling (2017) "Semi-Supervised Classification with Graph
  Convolutional Networks" — the original GCN paper.
- The next case study, [`11_gnn-xgboost`](../11_gnn-xgboost),
  combines GNN embeddings with classical gradient-boosted trees
  for actual prediction.

---

## `code/08_gnn-by-hand/data/_generate.py`

```python
"""Generate the tiny + larger toy supply chain networks for case 10.

Two networks are produced:
  - tiny.{nodes,edges}.csv: 6-node hand-toy network mirroring the
    case study lab. Each node has 2 input features.
  - large.{nodes,edges}.csv: 200-node project-scale network with
    planted bottlenecks; same 2 features.

Both are deterministic.

Run:
    python code/08_gnn-by-hand/data/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

def main() -> None:
    rng = np.random.default_rng(SEED)

    # --- tiny --------------------------------------------------------------
    # Six nodes in a small DAG. Node 4 is a bottleneck: many things
    # converge on it. Features = (daily_output, defect_rate) in [0, 1].
    tiny_nodes = pd.DataFrame({
        "node_id":      [0, 1, 2, 3, 4, 5],
        "daily_output": [0.80, 0.60, 0.40, 0.55, 0.70, 0.30],
        "defect_rate":  [0.10, 0.20, 0.30, 0.15, 0.05, 0.40],
    })
    tiny_edges = pd.DataFrame([
        {"from": 0, "to": 4}, {"from": 1, "to": 4}, {"from": 2, "to": 4},
        {"from": 3, "to": 4}, {"from": 4, "to": 5},
    ])
    tiny_nodes.to_csv(HERE / "tiny_nodes.csv", index=False)
    tiny_edges.to_csv(HERE / "tiny_edges.csv", index=False)
    print("wrote tiny_nodes.csv / tiny_edges.csv (6 nodes)")

    # --- larger ------------------------------------------------------------
    # 200 nodes; planted bottlenecks every 25 nodes.
    n = 200
    large_nodes = pd.DataFrame({
        "node_id":      np.arange(n),
        "daily_output": rng.beta(2, 2, size=n).round(3),
        "defect_rate":  rng.beta(2, 5, size=n).round(3),
    })
    rows = []
    bottlenecks = [25 * i for i in range(1, 8)]
    for src in range(n):
        # connect to nearest bottleneck downstream
        downstream = [b for b in bottlenecks if b > src]
        if downstream:
            tgt = downstream[0]
            rows.append({"from": src, "to": tgt})
    # connect bottlenecks linearly
    for a, b in zip(bottlenecks, bottlenecks[1:]):
        rows.append({"from": a, "to": b})
    large_edges = pd.DataFrame(rows)
    large_nodes.to_csv(HERE / "large_nodes.csv", index=False)
    large_edges.to_csv(HERE / "large_edges.csv", index=False)
    print(f"wrote large_nodes.csv ({n} nodes) / large_edges.csv ({len(large_edges)} edges)")


if __name__ == "__main__":
    main()
```

---

## `code/08_gnn-by-hand/example.R`

```r
#' @name example.R
#' @title Case Study 10 — GNN by Hand (R via reticulate)
#' @author <your-name-here>
#' @description
#' First, what are we even producing? An EMBEDDING. Where centrality
#' (case 04) gave each node a single number, an embedding gives each node
#' a *vector* — a bundle of several numbers — that captures the node's
#' structural neighborhood. Why not just use betweenness? Because a
#' bundle of numbers carries far more about a node's surroundings than
#' any one score, and it drops straight into a machine-learning model as
#' features (exactly what case 11 does to predict disruptions).
#'
#' The case study lab walked you through a hand-computed forward pass.
#' Here we do it on the same 6-node toy network — but from R. R has no
#' mature Graph Neural Network library, so rather than re-derive the math
#' we borrow the course's canonical numpy implementation (`functions.py`)
#' through `reticulate`. R drives the workflow and does the data loading,
#' plotting, and reporting; Python does the four lines of GCN matrix
#' algebra. Because the numbers run through the exact same code as
#' `example.py`, the Learning Check comes out byte-for-byte identical.
#'
#' Step by step:
#'   1. Build the adjacency matrix (with self-loops).
#'   2. Symmetric-normalize it (D^{-1/2} A D^{-1/2}).
#'   3. Apply a single GCN layer: H = ReLU(A_norm %*% X %*% W).
#'   4. Stack a second layer.
#'   5. Read off the embedding for the bottleneck node (node 4).
#'
#' Then we run the same pipeline on a 200-node project-scale network so
#' you can see GNN embeddings at non-toy scale.


# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `reticulate` is the bridge to the Python GCN functions; `ggplot2` draws
# the embedding scatter; `here` keeps file paths robust.
library(reticulate)
library(ggplot2)
library(here)

## 0.2 Load helpers ##########################################################

# PRE-FLIGHT CHECK (read this if you've never used reticulate). This is the
# one lab that drives Python from R, so the only thing that can go wrong is
# Python not being reachable. We check BEFORE sourcing functions.R (which
# triggers the Python setup) so you get a friendly message instead of a
# cryptic import error halfway through.
#
# If this stops with "Python not found":
#   - reticulate::install_python()         # installs a private Python, or
#   - Sys.setenv(RETICULATE_PYTHON = "/path/to/python-with-numpy")
#   then restart R and re-run. On a current reticulate (>= 1.41) the numpy +
#   pandas requirements are provisioned automatically (see functions.R).
if (!reticulate::py_available(initialize = TRUE)) {
  stop("Python not found for reticulate. Run reticulate::install_python() ",
       "or set RETICULATE_PYTHON to a Python that has numpy + pandas, ",
       "then restart R and re-run this script.")
}
cat("✅ reticulate found Python — bridging to the numpy GCN code.\n")

# functions.R gives us the R-native loaders (load_tiny / load_large) and
# the `gcn` Python module handle (gcn$adjacency / gcn$normalize /
# gcn$gcn_layer). Sourcing it triggers the one-time Python setup.
source(here::here("code", "10_gnn-by-hand", "functions.R"))

cat("\n🚀 Case Study 10 — GNN by Hand (R via reticulate)\n")
cat("   Two-layer GCN, no native R GNN lib. We drive numpy's functions.py from R.\n\n")

## 0.3 Load data #############################################################

tiny  <- load_tiny()
nodes <- tiny$nodes
edges <- tiny$edges
print(nodes)
print(edges)
cat(sprintf("✅ Loaded tiny network: %d nodes, %d edges.\n",
            nrow(nodes), nrow(edges)))


# 1. Adjacency and normalization #############################################
#
# Self-loops let each node "send a message to itself" so its own
# features survive into the next layer. Symmetric normalization
# D^{-1/2} A D^{-1/2} stops high-degree nodes from dominating their
# neighbors -- same intuition as degree-normalizing a count in stats:
# divide out how connected a node is so the average isn't swamped by a
# few hubs. Despite the scary notation it's just a rescaling trick.
# These steps are the heart of a GCN -- both come straight from
# functions.py via the `gcn` handle.

A <- gcn$adjacency(nodes, edges, add_self_loops = TRUE)
cat("A (with self-loops):\n")
print(A)

A_norm <- gcn$normalize(A)
cat("A_norm (symmetric-normalized):\n")
print(round(A_norm, 3))

# Make the normalization VISIBLE (gcn$normalize hides it behind one call).
# The degree matrix D is diagonal, holding each node's degree; symmetric
# normalization is literally D^{-1/2} %*% A %*% D^{-1/2}. Building it by hand
# once demystifies the "scary" formula: it just divides every edge by
# sqrt(deg_i * deg_j), which is what down-weights links to high-degree hubs.
deg           <- rowSums(A)             # the diagonal of D (with self-loops)
D_inv_sqrt    <- diag(1 / sqrt(deg))    # D^{-1/2}
A_norm_byhand <- D_inv_sqrt %*% A %*% D_inv_sqrt
cat(sprintf("   built two ways, max abs difference = %.2e (identical)\n",
            max(abs(A_norm - A_norm_byhand))))


# 2. Feature matrix and weight matrices ######################################
#
# Each node has 2 input features: (daily_output, defect_rate).
# Layer 1 maps 2 -> 3 hidden dims; layer 2 maps 3 -> 3.

X <- as.matrix(nodes[, c("daily_output", "defect_rate")])
cat("X (input features):\n")
print(X)

# Fixed weights for reproducibility — identical to example.py. In a real
# GNN these are learned via gradient descent on an objective; here we
# hard-code them so the whole pipeline is one chain of matrix multiplies.
W1 <- matrix(c( 0.5, -0.2,  0.8,
               -0.7,  0.4,  0.3), nrow = 2, byrow = TRUE)
W2 <- matrix(c( 0.6,  0.1, -0.4,
                0.2,  0.7,  0.3,
               -0.5,  0.4,  0.6), nrow = 3, byrow = TRUE)


# 3. Forward pass ############################################################
#
# H_{l+1} = ReLU(A_norm %*% H_l %*% W_l). The matmul-and-activate happens
# inside gcn$gcn_layer(), the same numpy function example.py calls.
# Why two layers? One layer mixes in each node's IMMEDIATE neighbors
# (1 hop). Stacking a second layer mixes in neighbors-of-neighbors
# (2 hops), so node 4 below can "see" both clusters it sits between.

H1 <- gcn$gcn_layer(A_norm, X,  W1, activation = "relu")
cat("H1 (after layer 1, ReLU):\n")
print(round(H1, 4))

H2 <- gcn$gcn_layer(A_norm, H1, W2, activation = "relu")
cat("H2 (after layer 2, ReLU):\n")
print(round(H2, 4))


# 4. What does node 4 (the bottleneck) end up looking like? ##################
#
# Node 4 sits between two clusters in our 6-node toy. After two GCN
# layers its embedding has absorbed features from both sides. Node 4 is
# 0-indexed in Python, which is row 5 in 1-indexed R.
#
# What do the 3 numbers MEAN? Individually, nothing nameable. Embedding
# dimensions are not "voltage" or "risk" -- in a trained GNN they're
# whatever the optimizer found useful; here they're fixed by W1/W2. What
# matters is RELATIVE: nodes with similar neighborhoods get similar
# vectors, so the embedding is useful as ML input (case 11) even though no
# single dimension has a human label.

emb_node4 <- H2[5, ]
cat("Final embedding for node 4 (the bottleneck):\n")
print(round(emb_node4, 4))
cat(sprintf("🧪 Node 4 embedding norm: %.4f\n",
            sqrt(sum(emb_node4^2))))


# 5. The same pipeline on a 200-node project-scale network ###################

large <- load_large()
A_l   <- gcn$normalize(gcn$adjacency(large$nodes, large$edges, add_self_loops = TRUE))
X_l   <- as.matrix(large$nodes[, c("daily_output", "defect_rate")])

H1_l <- gcn$gcn_layer(A_l,  X_l,  W1, activation = "relu")
H2_l <- gcn$gcn_layer(A_l,  H1_l, W2, activation = "relu")
cat(sprintf("📊 Large network embedding shape: %d x %d\n",
            nrow(H2_l), ncol(H2_l)))

# Plot the first two embedding dimensions, colored by whether the node is
# a planted bottleneck (every 25th node), so we can see whether the
# bottlenecks cluster separately after two GCN layers.
bottlenecks <- 25 * 1:7
plot_df <- data.frame(
  dim0  = H2_l[, 1],
  dim1  = H2_l[, 2],
  group = ifelse(large$nodes$node_id %in% bottlenecks,
                 "planted bottlenecks", "regular nodes")
)

p <- ggplot(plot_df, aes(dim0, dim1, color = group, size = group)) +
  geom_point(alpha = 0.7) +
  scale_color_manual(values = c("planted bottlenecks" = "#d62728",
                                "regular nodes"        = "#999999")) +
  scale_size_manual(values = c("planted bottlenecks" = 3, "regular nodes" = 1.4)) +
  labs(x = "embedding dim 0", y = "embedding dim 1",
       title = "After 2 GCN layers, do bottlenecks separate?",
       color = NULL, size = NULL) +
  theme_minimal()

ggsave(here::here("code", "10_gnn-by-hand", "gnn_embeddings.png"),
       p, width = 7, height = 5, dpi = 120)
cat("💾 Saved gnn_embeddings.png\n")


# 6. Learning Check ##########################################################
#
# QUESTION: With the layer weights W1 and W2 defined above (symmetric
# normalization, ReLU, self-loops), what is the FINAL embedding (3
# numbers) for node 4 on the tiny network?
#
# Round each to 4 decimal places. Submit as a comma-separated string.

emb <- round(emb_node4, 4)
# Collapse IEEE-754 negative zero to positive zero so the printed answer
# matches example.py byte-for-byte.
emb[emb == 0] <- 0
answer <- paste(sprintf("%.4f", emb), collapse = ", ")

cat(sprintf("\n📝 Learning Check answer: %s\n", answer))

cat("\n🎉 Done. Move on to the case study report when you're ready.\n")
```

---

## `code/08_gnn-by-hand/example.py`

```python
"""Case Study 10 — GNN by Hand (Python track).

First, what are we even producing? An EMBEDDING. Where centrality (case
04) gave each node a single number, an embedding gives each node a
*vector* -- a bundle of several numbers -- that captures the node's
structural neighborhood. Why bother instead of just using betweenness?
Because a bundle of numbers carries far more about a node's surroundings
than any one score, and it drops straight into a machine-learning model
as features (that's exactly what case 11 does to predict disruptions).

The case study lab walked you through a hand-computed forward pass.
Here we do it in pure numpy on the same 6-node toy network. No
torch, no torch_geometric. Just the math.

Step by step:
  1. Build the adjacency matrix (with self-loops).
  2. Symmetric-normalize it (D^{-1/2} A D^{-1/2}).
  3. Apply a single GCN layer: H = ReLU(A_norm @ X @ W).
  4. Stack a second layer.
  5. Read off the embedding for the bottleneck node (node 4).

Then we run the same pipeline on a 200-node project-scale network so
you can see GNN embeddings at non-toy scale.
"""

# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# Pure numpy + pandas. No torch — we want you to *see* the matrix math.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

## 0.2 Load helpers ##########################################################

# All the building blocks live in functions.py: tiny + large data
# loaders, adjacency builder, the symmetric normalization, ReLU, and
# the GCN layer itself. Read them once — each is 5-10 lines.
from functions import (
    load_tiny, load_large, adjacency, normalize, relu, gcn_layer,
)

print("\n🚀 Case Study 10 — GNN by Hand (Python)")
print("   Two-layer GCN, no torch. Pure numpy on a 6-node + 200-node network.\n")

## 0.3 Load data #############################################################

nodes, edges = load_tiny()
print(nodes)
print(edges)
print(f"✅ Loaded tiny network: {len(nodes)} nodes, {len(edges)} edges.")


# 1. Adjacency and normalization #############################################
#
# Self-loops let each node "send a message to itself" so its own
# features survive into the next layer. Symmetric normalization
# D^{-1/2} A D^{-1/2} stops high-degree nodes from dominating their
# neighbors -- same intuition as degree-normalizing a count in stats:
# divide out how connected a node is so the average isn't swamped by a
# few hubs. Despite the scary notation it's just a rescaling trick.
# These two preprocessing steps are the heart of a GCN.

A = adjacency(nodes, edges, add_self_loops=True)
print("A (with self-loops):")
print(A.astype(int))

A_norm = normalize(A)
print("A_norm (symmetric-normalized):")
print(A_norm.round(3))

# Make the normalization VISIBLE (normalize() hides it behind one call).
# The degree matrix D is diagonal, holding each node's degree; symmetric
# normalization is literally D^{-1/2} @ A @ D^{-1/2}. Building it by hand
# once demystifies the "scary" formula: it just divides every edge by
# sqrt(deg_i * deg_j), which is what down-weights links to high-degree hubs.
deg            = A.sum(axis=1)             # the diagonal of D (with self-loops)
D_inv_sqrt     = np.diag(1.0 / np.sqrt(deg))  # D^{-1/2}
A_norm_by_hand = D_inv_sqrt @ A @ D_inv_sqrt
print(f"   built two ways, max abs difference = "
      f"{np.abs(A_norm - A_norm_by_hand).max():.2e} (identical)")


# 2. Feature matrix and weight matrices ######################################
#
# Each node has 2 input features: (daily_output, defect_rate).
# Layer 1 maps 2 -> 3 hidden dims; layer 2 maps 3 -> 3.

X = nodes[["daily_output", "defect_rate"]].to_numpy()
print("X (input features):")
print(X)

# Fixed weights for reproducibility. In a real GNN these are learned
# via gradient descent on an objective; here we hard-code them so the
# whole pipeline is one numpy matmul chain.
W1 = np.array([
    [ 0.5, -0.2,  0.8],
    [-0.7,  0.4,  0.3],
])
W2 = np.array([
    [ 0.6,  0.1, -0.4],
    [ 0.2,  0.7,  0.3],
    [-0.5,  0.4,  0.6],
])


# 3. Forward pass ############################################################
#
# H_{l+1} = activation(A_norm @ H_l @ W_l). The activation is ReLU.
# Why two layers? One layer mixes in each node's IMMEDIATE neighbors
# (1 hop). Stacking a second layer mixes in neighbors-of-neighbors
# (2 hops), so node 4 below can "see" both clusters it sits between.

H1 = gcn_layer(A_norm, X,  W1, activation="relu")
print("H1 (after layer 1, ReLU):")
print(H1.round(4))

H2 = gcn_layer(A_norm, H1, W2, activation="relu")
print("H2 (after layer 2, ReLU):")
print(H2.round(4))


# 4. What does node 4 (the bottleneck) end up looking like? ##################
#
# Node 4 sits between two clusters in our 6-node toy. After two GCN
# layers its embedding has absorbed features from both sides.
#
# What do the 3 numbers MEAN? Individually, nothing nameable. Embedding
# dimensions are not "voltage" or "risk" -- in a trained GNN they're
# whatever the optimizer found useful; here they're fixed by W1/W2. What
# matters is RELATIVE: nodes with similar neighborhoods get similar
# vectors, so the embedding is useful as ML input (case 11) even though no
# single dimension has a human label.

print("Final embedding for node 4 (the bottleneck):")
print(H2[4].round(4))
print(f"🧪 Node 4 embedding norm: {np.linalg.norm(H2[4]):.4f}")


# 5. The same pipeline on a 200-node project-scale network ###################

ln, le = load_large()
A_l = normalize(adjacency(ln, le, add_self_loops=True))
X_l = ln[["daily_output", "defect_rate"]].to_numpy()

H1_l = gcn_layer(A_l, X_l, W1, activation="relu")
H2_l = gcn_layer(A_l, H1_l, W2, activation="relu")
print(f"📊 Large network embedding shape: {H2_l.shape}")

# Plot the first two embedding dimensions, colored by node id, so we
# can see whether the bottlenecks (every 25th node) cluster separately.
fig, ax = plt.subplots(figsize=(7, 5))
is_bot = ln["node_id"].isin([25 * i for i in range(1, 8)]).to_numpy()
ax.scatter(H2_l[~is_bot, 0], H2_l[~is_bot, 1], s=12, alpha=0.5,
           c="#999", label="regular nodes")
ax.scatter(H2_l[is_bot, 0], H2_l[is_bot, 1], s=80, c="#d62728",
           edgecolor="white", label="planted bottlenecks")
ax.set_xlabel("embedding dim 0")
ax.set_ylabel("embedding dim 1")
ax.set_title("After 2 GCN layers, do bottlenecks separate?")
ax.legend()
fig.tight_layout()
fig.savefig("gnn_embeddings.png", dpi=120)
plt.close(fig)
print("💾 Saved gnn_embeddings.png")


# 6. Learning Check ##########################################################
#
# QUESTION: With the layer weights W1 and W2 defined above (symmetric
# normalization, ReLU, self-loops), what is the FINAL embedding (3
# numbers) for node 4 on the tiny network?
#
# Round each to 4 decimal places. Submit as a comma-separated string.

emb = H2[4].round(4)
answer = ", ".join(f"{v:.4f}" for v in emb)

print(f"\n📝 Learning Check answer: {answer}")

print("\n🎉 Done. Move on to the case study report when you're ready.")
```

---

## `code/08_gnn-by-hand/functions.R`

```r
#' @name functions.R
#' @title Helpers for the GNN-by-Hand case study (R, reticulate bridge)
#' @author <your-name-here>
#' @description
#' Graph Neural Networks are the one spot in this course where R has no
#' mature native library, so the GCN math itself lives in Python
#' (`functions.py`). This file handles the half R is great at — reading
#' the toy and project-scale networks from CSV — and then reaches across
#' to Python with `reticulate` to borrow the GCN building blocks
#' (`adjacency`, `normalize`, `gcn_layer`). The Python module is loaded
#' once here and exposed as the object `gcn`, so `example.R` can call
#' `gcn$gcn_layer(...)` and friends directly.


# 0. R-native data loaders ###################################################
#
# Reading CSVs is something R does perfectly well, so we keep it on this
# side of the bridge. Each loader returns a named list of two tibbles.

library(here)
library(reticulate)

.case_dir <- function() here::here("code", "10_gnn-by-hand", "data")

#' Load the 6-node toy network as a list of two tibbles.
load_tiny <- function() {
  list(
    nodes = readr::read_csv(file.path(.case_dir(), "tiny_nodes.csv"),
                            show_col_types = FALSE),
    edges = readr::read_csv(file.path(.case_dir(), "tiny_edges.csv"),
                            show_col_types = FALSE)
  )
}

#' Load the 200-node project-scale network as a list of two tibbles.
load_large <- function() {
  list(
    nodes = readr::read_csv(file.path(.case_dir(), "large_nodes.csv"),
                            show_col_types = FALSE),
    edges = readr::read_csv(file.path(.case_dir(), "large_edges.csv"),
                            show_col_types = FALSE)
  )
}


# 1. The GNN half: borrow the numpy GCN functions from functions.py ##########
#
# We only need numpy + pandas on the Python side. On a current reticulate
# (>= 1.41) py_require() records those requirements and provisions them in
# an ephemeral environment the first time Python is touched -- the same
# one-liner used in dsai/07_rag/05_embed.R. (On an older reticulate, point
# it at a Python that already has numpy + pandas via RETICULATE_PYTHON.)
# import_from_path() then hands us the module as the R object `gcn` WITHOUT
# dumping its functions into the global namespace, so our R loaders above
# keep their names.

if (utils::packageVersion("reticulate") >= "1.41") {
  reticulate::py_require(c("numpy", "pandas"))
}

gcn <- reticulate::import_from_path(
  "functions",
  path    = here::here("code", "10_gnn-by-hand"),
  convert = TRUE  # numpy arrays come back as R matrices, automatically
)
```

---

## `code/08_gnn-by-hand/functions.py`

```python
"""Helpers for the GNN-by-Hand case study.

We implement the forward pass of a simple Graph Convolutional
Network (GCN) layer from scratch in numpy. No torch, no
torch_geometric. The point is to see the math.
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd


def _case_dir() -> Path:
    return Path(__file__).resolve().parent / "data"


def load_tiny() -> tuple[pd.DataFrame, pd.DataFrame]:
    n = pd.read_csv(_case_dir() / "tiny_nodes.csv")
    e = pd.read_csv(_case_dir() / "tiny_edges.csv")
    return n, e


def load_large() -> tuple[pd.DataFrame, pd.DataFrame]:
    n = pd.read_csv(_case_dir() / "large_nodes.csv")
    e = pd.read_csv(_case_dir() / "large_edges.csv")
    return n, e


def adjacency(nodes: pd.DataFrame, edges: pd.DataFrame,
              add_self_loops: bool = True) -> np.ndarray:
    """Return an N x N adjacency matrix (undirected) from edges."""
    n = len(nodes)
    idx = {nid: i for i, nid in enumerate(nodes["node_id"].to_numpy())}
    A = np.zeros((n, n))
    for _, r in edges.iterrows():
        i, j = idx[int(r["from"])], idx[int(r["to"])]
        A[i, j] = 1
        A[j, i] = 1
    if add_self_loops:
        np.fill_diagonal(A, 1)
    return A


def normalize(A: np.ndarray) -> np.ndarray:
    """Symmetric normalization: D^{-1/2} A D^{-1/2}.

    This is the GCN normalization (Kipf & Welling 2017).
    """
    d = A.sum(axis=1)
    d_inv_sqrt = 1.0 / np.sqrt(np.where(d == 0, 1, d))
    D_inv_sqrt = np.diag(d_inv_sqrt)
    return D_inv_sqrt @ A @ D_inv_sqrt


def relu(x: np.ndarray) -> np.ndarray:
    return np.maximum(0, x)


def gcn_layer(A_norm: np.ndarray, X: np.ndarray, W: np.ndarray,
              activation: str = "relu") -> np.ndarray:
    """One GCN layer: H = sigma(A_norm @ X @ W).

    Args:
        A_norm: N x N normalized adjacency.
        X: N x F input features.
        W: F x F_out weight matrix.
        activation: "relu" or "none".
    """
    H = A_norm @ X @ W
    if activation == "relu":
        H = relu(H)
    return H
```

---

## `code/09_gnn-xgboost/README.md`

# Case Study 11 — GNN + XGBoost

> Interactive lab: [`docs/case-studies/gnn-xgboost.html`](../../docs/case-studies/gnn-xgboost.html)
>
> Skill: **Predict** · Track: **Python & R both run the full pipeline**
> (R computes the GNN embedding via `reticulate`)
> · Data: synthetic supplier-disruption panel (500 suppliers × 52 weeks,
> ~1,200 directed dependency edges)

## What you'll learn

How to combine three families of features for a node-level
prediction task:

1. **Raw static features** (per-supplier traits — tier, region,
   capacity, geo-risk).
2. **Lag features** (per-supplier history — trailing 4-week
   disruption rate).
3. **GNN-style structural embeddings** (the lag feature *of your
   neighbors* — and your neighbors' neighbors — averaged over the
   directed in-edges).

XGBoost on all three usually beats XGBoost on any subset. The case
study makes that improvement concrete and lets you read the
feature-importance bars to see *why* the GNN helps.

## How R runs the full pipeline

R's `xgboost` package is excellent and R handles the loaders, the lag
feature, the train/test split, and the AUC scoring natively. The one
piece R has no mature library for is the **GNN embedding**, so the R track
borrows the course's numpy implementation through `reticulate` (see
`functions.R`) — the same surgical-bridge pattern as `dsai/07_rag`.

- **Python (`example.py`)**: full pipeline (raw → raw+lag → raw+lag+GNN).
  Final test AUC ≈ 0.66.
- **R (`example.R`)**: same full pipeline. The GNN embedding is computed
  in numpy via `reticulate`; everything else, including XGBoost, is native
  R. Final test AUC ≈ 0.66 as well (R's `xgboost` can differ from Python's
  in the last digits).

The GNN embedding here is a *parameter-free* GCN-style aggregation (mean of
in-neighbors' lag rate over 1 and 2 hops), so there's no torch dependency —
just a couple of matrix multiplies that the shared `functions.py` performs.

## Prerequisites

- Case study 10 (GNN by Hand) so the embedding step makes sense.
- The interactive lab.
- R packages: `dplyr`, `tidyr`, `readr`, `ggplot2`, `xgboost`, `zoo`,
  `here`, `reticulate` (plus a Python with `numpy` + `pandas` for the
  embedding step — auto-provisioned by `py_require()` on reticulate >= 1.41).
- Python packages: see [`code/requirements.txt`](../requirements.txt).
  Uses `scikit-learn` for AUC.

## Files in this folder

```
11_gnn-xgboost/
├── README.md
├── example.R              # XGBoost on raw + lag + GNN (embedding via reticulate)
├── example.py             # XGBoost on raw + lag + GNN embedding
├── functions.R            # R loaders + lag_rate + reticulate bridge to the embedding
├── functions.py           # lag_rate, adjacency, GNN-aggregation helpers
└── data/
    ├── suppliers.csv  # 500 suppliers, static features
    ├── edges.csv      # ~1,200 directed dependency edges
    ├── panel.csv      # 26,000 rows: supplier x week x disrupted
    └── _generate.py
```

## How to run

```bash
python code/09_gnn-xgboost/example.py    # full pipeline
Rscript code/09_gnn-xgboost/example.R    # raw + lag variant
```

## Learning check

> **On the held-out test weeks (40..51), what is the ROC AUC of the
> (raw + lag + GNN 1-hop + GNN 2-hop) XGBoost model?**

Report to 4 decimal places. Both tracks now answer the same question.
The Python and R answers will be very close (≈ 0.66) but may differ in
the last digit or two: the GNN embedding is computed by the same numpy
code, but Python and R train XGBoost with their own implementations and
defaults, which aren't bit-for-bit identical. Submit the value your track
prints.

## Your Project Case Study

If you pick this case study, you'll predict a node-level binary
outcome on *your* network using XGBoost (Python track adds GNN
embeddings).

### Suggested project questions

1. **Does network position help?** Train XGBoost on raw features
   only, then on raw + lag, then on raw + lag + GNN (Python only).
   Report the AUC gain at each step. Discuss whether network
   position adds predictive value in your domain.

2. **Feature importance audit.** Train XGBoost on the full feature
   set. Report the top 5 features by gain. Discuss whether the
   ranking matches your domain intuition.

3. **Class imbalance.** If your target is imbalanced (most cases
   are negatives), report AUC AND precision/recall at a sensible
   threshold. Discuss whether the model is useful at the
   operational decision threshold you care about.

### Report

- **Question.** One sentence, ending with "...so we can [act]."
- **Network and panel.** Nodes, edges, target definition, time
  range, train/test split.
- **Procedure.** Feature sets, model hyperparameters, evaluation
  metric.
- **Results.** AUC (and precision/recall if imbalanced) in prose;
  feature-importance plot as 1 figure; results table.
- **What this tells you, and what it doesn't.** 2-3 sentences.
  Note: an XGBoost AUC of 0.65 is real signal but not a deployable
  prediction — be honest about that.

## Further reading

- Kipf & Welling (2017) for the GCN math the embedding step
  approximates.
- Chen & Guestrin (2016) for the XGBoost algorithm.
- For a more sophisticated GNN-feature pipeline (with trained
  weights instead of parameter-free aggregation), see PyTorch
  Geometric's tutorials.

---

## `code/09_gnn-xgboost/data/_generate.py`

```python
"""Generate the synthetic supplier-disruption panel for case 11.

We build a directed supply network of N suppliers and simulate T
weeks of binary disruption labels per supplier. Each supplier has:

  - static features: tier, region (one-hot), capacity, geographic
    risk score
  - dynamic feature: last-4-weeks disruption rate (a lag feature)
  - network position: who they supply to, who supplies them

Disruption is generated so that BOTH static features AND neighbor
disruptions predict it. This is the signal that lets a GNN
embedding outperform plain features.

Outputs:
  - suppliers.csv (500 rows, static traits)
  - edges.csv    (~1200 directed dependency edges)
  - panel.csv    (500 * 52 = 26000 rows, supplier x week x label)

Run:
    python code/09_gnn-xgboost/data/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

def main() -> None:
    rng = np.random.default_rng(SEED)
    n_suppliers = 500
    n_weeks     = 52

    # --- static features ----------------------------------------------------
    region_levels = np.array(["NE", "SE", "MW", "W"])
    suppliers = pd.DataFrame({
        "supplier_id":    [f"S{i:04d}" for i in range(n_suppliers)],
        "tier":           rng.integers(1, 4, size=n_suppliers),
        "region":         rng.choice(region_levels, size=n_suppliers),
        "capacity":       rng.integers(200, 2000, size=n_suppliers),
        "geo_risk":       rng.beta(2, 5, size=n_suppliers).round(3),
    })

    # --- directed dependency edges (who supplies whom) ----------------------
    rows = []
    for i in range(n_suppliers):
        # each supplier has 1-4 outgoing dependencies
        k = int(rng.integers(1, 5))
        targets = rng.choice(np.delete(np.arange(n_suppliers), i),
                             size=min(k, n_suppliers - 1), replace=False)
        for t in targets:
            rows.append({"from": suppliers["supplier_id"][i],
                         "to":   suppliers["supplier_id"][t]})
    edges = pd.DataFrame(rows).sort_values(["from", "to"]).reset_index(drop=True)

    # --- per-supplier baseline disruption probability ------------------------
    # combines static features (geo_risk + capacity inverse + tier)
    cap_z = (suppliers["capacity"] - suppliers["capacity"].mean()) / suppliers["capacity"].std()
    base_logit = (
        -2.8
        + 1.8 * suppliers["geo_risk"]
        - 0.3 * cap_z
        + 0.3 * (suppliers["tier"] - 1)
        + 0.4 * (suppliers["region"] == "SE").astype(float)
    )

    # --- simulate T weeks of disruption labels ------------------------------
    # at week t, P(disrupt) = sigmoid(base_logit + neighbor_effect)
    # where neighbor_effect = mean of t-1 disruption of in-neighbors
    # (so disruptions cluster temporally and propagate upstream)
    in_neighbors = {s: [] for s in suppliers["supplier_id"]}
    for _, e in edges.iterrows():
        in_neighbors[e["to"]].append(e["from"])

    sup_idx = {s: i for i, s in enumerate(suppliers["supplier_id"])}
    Y = np.zeros((n_suppliers, n_weeks), dtype=np.int8)
    # week 0: pure static baseline
    p0 = 1 / (1 + np.exp(-base_logit.to_numpy()))
    Y[:, 0] = (rng.random(n_suppliers) < p0).astype(np.int8)
    for t in range(1, n_weeks):
        prev = Y[:, t - 1].astype(float)
        neigh_eff = np.zeros(n_suppliers)
        for s, ins in in_neighbors.items():
            if ins:
                neigh_eff[sup_idx[s]] = np.mean([prev[sup_idx[x]] for x in ins])
        logit = base_logit.to_numpy() + 1.5 * neigh_eff
        p = 1 / (1 + np.exp(-logit))
        Y[:, t] = (rng.random(n_suppliers) < p).astype(np.int8)

    # --- build the panel ----------------------------------------------------
    panel_rows = []
    for i, s in enumerate(suppliers["supplier_id"]):
        for t in range(n_weeks):
            panel_rows.append({
                "supplier_id": s,
                "week":        t,
                "disrupted":   int(Y[i, t]),
            })
    panel = pd.DataFrame(panel_rows)

    # --- write --------------------------------------------------------------
    suppliers.sort_values("supplier_id").to_csv(HERE / "suppliers.csv",
                                                    index=False)
    edges.to_csv(HERE / "edges.csv", index=False)
    panel.to_csv(HERE / "panel.csv", index=False)

    print(f"wrote {HERE / 'suppliers.csv'} ({len(suppliers)} suppliers)")
    print(f"wrote {HERE / 'edges.csv'}     ({len(edges):,} edges)")
    print(f"wrote {HERE / 'panel.csv'}     ({len(panel):,} rows = "
          f"{n_suppliers} x {n_weeks})")
    print(f"  overall disruption rate: {panel['disrupted'].mean():.3f}")


if __name__ == "__main__":
    main()
```

---

## `code/09_gnn-xgboost/example.R`

```r
#' @name example.R
#' @title Case Study 11 — GNN + XGBoost (R, full pipeline via reticulate)
#' @author <your-name-here>
#' @description
#' The case study lab showed that combining:
#'   - raw static features
#'   - a lag (history) feature
#'   - a GNN-style structural embedding
#' into XGBoost beats any one of them alone. Here we run that full
#' pipeline in R on a synthetic supplier-disruption panel (500 suppliers
#' x 52 weeks).
#'
#' R does almost all of it natively — the loaders, the lag feature, the
#' XGBoost models, and the AUC scoring. The single piece R has no mature
#' library for is the GNN embedding, so we borrow the course's numpy
#' implementation through `reticulate` (see functions.R). The embedding
#' here is a *parameter-free* GCN-style aggregation (mean of in-neighbors'
#' lag_rate, 1 and 2 hops) — same structural signal as a trained GNN, no
#' torch dependency.
#'
#' Pipeline:
#'   1. Load suppliers, edges, and the (supplier, week, disrupted) panel.
#'   2. Add the 4-week lag_rate feature (R).
#'   3. Add 1-hop and 2-hop GNN embeddings of lag_rate (Python via reticulate).
#'   4. Split into train (weeks 0..39) / test (weeks 40..51).
#'   5. Train three XGBoost models on three feature sets; compare AUC.


# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `xgboost` is the model; `dplyr`/`tidyr` wrangle the panel; `ggplot2`
# draws the importance bars; `reticulate` (loaded in functions.R) bridges
# to the GNN embedding.
library(dplyr)
library(tidyr)
library(ggplot2)
library(xgboost)
library(here)

## 0.2 Load helpers ##########################################################

# functions.R gives us the R-native loaders + add_lag_features(), and the
# add_gnn_embeddings() wrapper that calls the Python embedding code.
source(here::here("code", "11_gnn-xgboost", "functions.R"))

cat("\n🚀 Case Study 11 — GNN + XGBoost (R, full pipeline via reticulate)\n")
cat("   Three feature sets stacked. Watch AUC climb as we add structure.\n\n")

## 0.3 Load data #############################################################

suppliers <- load_suppliers()
edges     <- load_edges()
panel     <- load_panel()
print(head(suppliers))
print(head(panel))
cat(sprintf("✅ Loaded %d suppliers, %d dependency edges, %d panel rows.\n",
            nrow(suppliers), nrow(edges), nrow(panel)))


# 1. Add lag feature #########################################################
#
# `lag_rate` is the rolling 4-week disruption rate for each supplier,
# computed BEFORE the current week to avoid label leakage. It's our best
# non-network feature for predicting next week's disruption.

panel <- add_lag_features(panel, window = 4)
cat("✅ Added 4-week lag_rate feature.\n")


# 2. Add GNN embeddings (Python via reticulate) ##############################
#
# This is the one step with no mature R library, so add_gnn_embeddings()
# (in functions.R) reaches across to numpy: it builds the row-normalized
# in-neighbor adjacency A and computes A %*% lag (1-hop neighbor average)
# and A %*% A %*% lag (2-hop), per week. The result is two new columns.
#
# These embeddings are FIXED aggregations (just a matrix multiply), NOT a
# trained GNN: no learned weights, no backprop. Same distinction as case 10
# -- you computed a forward pass, you didn't train one. The structural
# signal is real; the "learning" is not. A torch GNN would learn what to
# aggregate; here we hard-code "average your neighbors' lag_rate."

panel <- add_gnn_embeddings(panel, suppliers, edges)
print(head(panel, 10))
cat("✅ Added 1-hop and 2-hop GNN embeddings of lag_rate.\n")


# 3. Merge static features ###################################################
#
# Join the suppliers table (tier, capacity, region, geo_risk) onto the
# panel and one-hot encode region. XGBoost can take factors directly, but
# we keep the encoding explicit so the feature columns are obvious.
# We deliberately keep ALL region columns (no dropped reference level). A
# linear model would have collinearity here, but tree models like XGBoost
# don't care, and keeping every level makes the importance plot readable.

dat <- panel |>
  left_join(suppliers, by = "supplier_id") |>
  mutate(
    region_MW = as.integer(region == "MW"),
    region_NE = as.integer(region == "NE"),
    region_SE = as.integer(region == "SE"),
    region_W  = as.integer(region == "W")
  )


# 4. Train/test split ########################################################
#
# Train on weeks 0..39 (the first 40 weeks). Test on weeks 40..51 (the
# last 12). This is the canonical time-series holdout: never train on
# data from a week you'll later evaluate on.

train <- dat |> filter(week < 40)
test  <- dat |> filter(week >= 40)
cat(sprintf("📊 train rows: %d   test rows: %d\n", nrow(train), nrow(test)))
cat(sprintf("📊 train positive rate: %.3f\n", mean(train$disrupted)))


# 5. Three feature sets, three models ########################################
#
# Each feature set is a SUPERSET of the previous one, so any AUC
# improvement from raw -> raw+lag -> raw+lag+GNN tells you what adding
# *that piece* contributed.

raw_cols <- c("tier", "capacity", "geo_risk",
              "region_MW", "region_NE", "region_SE", "region_W")
lag_cols <- c(raw_cols, "lag_rate")
gnn_cols <- c(lag_cols, "gnn_1hop", "gnn_2hop")

# Rank-based AUC (no extra package needed). For each (positive, negative)
# score pair we count how often the positive scored higher — that is the
# ROC AUC by definition (the Mann-Whitney identity), so it matches what
# sklearn's roc_auc_score would report for the same predictions.
auc_rank <- function(scores, labels) {
  pos <- scores[labels == 1]
  neg <- scores[labels == 0]
  if (length(pos) == 0 || length(neg) == 0) return(NA_real_)
  mean(outer(pos, neg, ">")) + 0.5 * mean(outer(pos, neg, "=="))
}

# Fit one XGBoost model on a feature set and return its test AUC + the
# feature-importance table. Same hyperparameters as the Python track. We
# use the low-level xgb.train() + xgb.DMatrix() API because it is stable
# across xgboost versions (the high-level xgboost() signature changed in 3.x).
fit_and_score <- function(features) {
  set.seed(42)  # XGBoost's RNG; keeps runs reproducible
  dtrain <- xgboost::xgb.DMatrix(as.matrix(train[, features]),
                                 label = train$disrupted)
  dtest  <- xgboost::xgb.DMatrix(as.matrix(test[, features]),
                                 label = test$disrupted)
  model  <- xgboost::xgb.train(
    params  = list(max_depth = 4, eta = 0.05,
                   objective = "binary:logistic", eval_metric = "auc"),
    data    = dtrain, nrounds = 200, verbose = 0
  )
  preds <- predict(model, dtest)
  imp   <- xgboost::xgb.importance(model = model, feature_names = features) |>
    arrange(desc(Gain))
  list(model = model, auc = auc_rank(preds, test$disrupted), imp = imp)
}

raw_fit <- fit_and_score(raw_cols)
lag_fit <- fit_and_score(lag_cols)
gnn_fit <- fit_and_score(gnn_cols)

cat(sprintf("🧪 AUC, raw features only:           %.4f\n", raw_fit$auc))
cat(sprintf("🧪 AUC, raw + lag:                   %.4f\n", lag_fit$auc))
cat(sprintf("🧪 AUC, raw + lag + GNN (1+2 hop):   %.4f\n", gnn_fit$auc))

# AUC in plain English: the probability the model scores a truly disrupted
# supplier higher than a healthy one. 0.5 = coin flip, 1.0 = perfect.
# How to read these: the raw-only model is your NON-NETWORK baseline.
# Watch AUC climb as lag (history) and then GNN (structure) features are
# added. For rare-event, noisy disruption prediction ~0.65+ is competitive
# -- don't expect the 0.80+ you'd see on a clean churn model.


# 6. Feature importance ######################################################
#
# What does the full model think the most important features are? A high
# gain on `gnn_1hop` or `gnn_2hop` is the visible signature of the GNN
# piece earning its keep.
#
# Heads-up: a feature can rank LOW here yet still raise AUC. Importance
# counts how often the model splits on a feature; a GNN feature that adds
# weak but INDEPENDENT signal can lift predictions without being split on
# often. Low importance + real AUC lift = exactly that situation.
#
# Connecting back to Week 2 (Case 04): the gnn_1hop / gnn_2hop columns play
# the same role betweenness/centrality did — they summarize a node's
# structural position — except here that signal is LEARNED from the
# neighbors' data (their lag_rate) rather than COMPUTED from pure topology.
# A high gnn_1hop gain means "knowing your neighbors' recent disruption
# rate helps predict your own."

# Reading THIS table: individual-supplier features (capacity, geo_risk)
# usually top it -- a supplier's own characteristics predict its own
# disruption more than its neighbors' do. And gnn_1hop typically outranks
# gnn_2hop, because 2-hop averages in more distant, noisier neighbors and
# dilutes the signal. Structure helps; individual features still dominate.
print(gnn_fit$imp)

p <- ggplot(gnn_fit$imp, aes(x = Gain, y = reorder(Feature, Gain))) +
  geom_col(fill = "#3a8bc6") +
  labs(x = "XGBoost feature importance (gain)", y = NULL,
       title = "Which features matter? (raw + lag + GNN model)") +
  theme_minimal()

ggsave(here::here("code", "11_gnn-xgboost", "xgboost_importance.png"),
       p, width = 7, height = 4.5, dpi = 120)
cat("💾 Saved xgboost_importance.png\n")


# 7. Learning Check ##########################################################
#
# QUESTION: On the held-out test weeks (40..51), what is the ROC AUC of
# the (raw + lag + GNN 1-hop + GNN 2-hop) XGBoost model?
# Report to 4 decimal places.
#
# NOTE: this asks the same question as the Python track. The embedding is
# computed by the same numpy code, but the model is trained by R's own
# xgboost, so the value can differ from Python's in the last digits —
# implementations and their defaults are not bit-for-bit identical.

cat(sprintf("\n📝 Learning Check answer: %.4f\n", gnn_fit$auc))

cat("\n🎉 Done. Move on to the case study report when you're ready.\n")
```

---

## `code/09_gnn-xgboost/example.py`

```python
"""Case Study 11 — GNN + XGBoost (Python track, full pipeline).

The case study lab showed you that combining:
  - raw static features
  - a lag (history) feature
  - a GNN-style structural embedding

into XGBoost beats any one of them alone. Here we do that in code on
a synthetic supplier-disruption panel (500 suppliers x 52 weeks).

The GNN embedding here is a *parameter-free* GCN-style aggregation
(mean of in-neighbors' lag_rate, then mean of 2-hop in-neighbors').
This isn't a *trained* GNN — but it carries the same structural
signal, and it lets us avoid a torch dependency for teaching.

Pipeline:
  1. Load suppliers, edges, and the (supplier, week, disrupted) panel.
  2. Add the 4-week lag_rate feature.
  3. Build the row-normalized in-neighbor adjacency.
  4. Add 1-hop and 2-hop GNN embeddings of lag_rate.
  5. Split into train (weeks 0..39) / test (weeks 40..51).
  6. Train three XGBoost models on three feature sets; compare AUC.
"""

# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `xgboost` for the gradient-boosted trees, `sklearn` just for the AUC
# scorer, `numpy`/`pandas` for the feature engineering.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score
import xgboost as xgb

## 0.2 Load helpers ##########################################################

# All the data + feature-engineering plumbing lives in functions.py.
# `add_gnn_embeddings()` does the matrix-multiply that gives us the
# 1-hop and 2-hop neighbor lag_rate averages.
from functions import (
    load_suppliers, load_edges, load_panel,
    add_lag_features, build_adjacency, add_gnn_embeddings,
)

print("\n🚀 Case Study 11 — GNN + XGBoost (Python, full pipeline)")
print("   Three feature sets stacked. Watch AUC climb as we add structure.\n")

## 0.3 Load data #############################################################

suppliers = load_suppliers()
edges     = load_edges()
panel     = load_panel()
print(suppliers.head())
print(panel.head())
print(f"✅ Loaded {len(suppliers)} suppliers, {len(edges)} dependency edges, "
      f"{len(panel)} panel rows.")


# 1. Add lag feature #########################################################
#
# `lag_rate` is the rolling 4-week disruption rate for each supplier,
# computed BEFORE the current week to avoid label leakage. It's our
# best non-network feature for predicting next week's disruption.

panel = add_lag_features(panel, window=4)
print(panel.head(10))
print(f"✅ Added 4-week lag_rate feature.")


# 2. Build adjacency & add GNN embeddings ####################################
#
# The row-normalized in-neighbor adjacency A turns "compute average of
# my in-neighbors' lag_rate" into a single matrix product: A @ x.
# Applying A twice gives the 2-hop average. This is the simplest
# possible "graph convolution" — no learned weights, no nonlinearity.
#
# So these are FIXED aggregations, NOT a trained GNN: no learned weights,
# no backprop. Same distinction as case 10 -- you computed a forward pass,
# you didn't train one. A torch GNN would LEARN what to aggregate; here we
# hard-code "average your neighbors' lag_rate." The structural signal is
# real; the "learning" is not.

A = build_adjacency(suppliers, edges)
print(f"📊 Adjacency: {A.shape}, row-sum max = {A.sum(axis=1).max():.2f}")

panel = add_gnn_embeddings(panel, suppliers, A)
print(panel.head(10))
print("✅ Added 1-hop and 2-hop GNN embeddings of lag_rate.")


# 3. Merge static features ###################################################

panel = panel.merge(suppliers, on="supplier_id", how="left")
# one-hot region (XGBoost can handle this directly but we keep it explicit).
# We deliberately keep ALL region columns (no drop_first). A linear model
# would have collinearity here, but tree models like XGBoost don't care and
# keeping every level makes the feature-importance plot below readable.
panel = pd.concat([panel, pd.get_dummies(panel["region"], prefix="region")],
                  axis=1)


# 4. Train/test split ########################################################
#
# Train on weeks 0..39 (the first 40 weeks). Test on weeks 40..51
# (the last 12). This is the canonical time-series holdout: never
# train on data from a week you'll later evaluate on.

train = panel[panel["week"] < 40].copy()
test  = panel[panel["week"] >= 40].copy()
print(f"📊 train rows: {len(train):,}   test rows: {len(test):,}")
print(f"📊 train positive rate: {train['disrupted'].mean():.3f}")


# 5. Three feature sets, three models ########################################
#
# Each feature set is a SUPERSET of the previous one. So any AUC
# improvement from raw -> raw+lag -> raw+lag+GNN tells you what
# adding *that piece* contributed.

raw_cols  = ["tier", "capacity", "geo_risk",
             "region_MW", "region_NE", "region_SE", "region_W"]
lag_cols  = raw_cols + ["lag_rate"]
gnn_cols  = lag_cols + ["gnn_1hop", "gnn_2hop"]

def fit_and_auc(features):
    model = xgb.XGBClassifier(
        n_estimators=200, max_depth=4, learning_rate=0.05,
        random_state=42, verbosity=0,
        eval_metric="auc",
    )
    model.fit(train[features], train["disrupted"])
    preds = model.predict_proba(test[features])[:, 1]
    return roc_auc_score(test["disrupted"], preds), model

auc_raw,  _    = fit_and_auc(raw_cols)
auc_lag,  _    = fit_and_auc(lag_cols)
auc_gnn,  m_gnn = fit_and_auc(gnn_cols)

print(f"🧪 AUC, raw features only:           {auc_raw:.4f}")
print(f"🧪 AUC, raw + lag:                   {auc_lag:.4f}")
print(f"🧪 AUC, raw + lag + GNN (1+2 hop):   {auc_gnn:.4f}")

# AUC in plain English: the probability the model scores a truly disrupted
# supplier higher than a healthy one. 0.5 = coin flip, 1.0 = perfect.
# How to read these: the raw-only model is your NON-NETWORK baseline.
# Watch AUC climb as lag (history) and then GNN (structure) features are
# added. For rare-event, noisy disruption prediction ~0.65+ is competitive
# -- don't expect the 0.80+ you'd see on a clean churn model.


# 6. Feature importance ######################################################
#
# What does the full model think the most important features are?
# A high gain on `gnn_1hop` or `gnn_2hop` is the visible signature
# of the GNN piece earning its keep.
#
# Heads-up: a feature can rank LOW here yet still raise AUC. Importance
# counts how often the model splits on a feature; a GNN feature that adds
# weak but INDEPENDENT signal can lift predictions without being split on
# often. Low importance + real AUC lift = exactly that situation.
#
# Connecting back to case 04: gnn_1hop / gnn_2hop play the role betweenness
# did — they summarize a node's structural position — except LEARNED from
# the neighbors' data rather than COMPUTED from pure topology. Reading the
# table: individual-supplier features (capacity, geo_risk) usually top it
# (your own characteristics predict your own disruption more than your
# neighbors' do), and gnn_1hop typically outranks gnn_2hop because 2-hop
# averages in more distant, noisier neighbors. Structure helps; individual
# features still dominate.

imp = pd.DataFrame({
    "feature":    gnn_cols,
    "importance": m_gnn.feature_importances_,
}).sort_values("importance", ascending=False)
print(imp)

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.barh(imp["feature"], imp["importance"], color="#3a8bc6")
ax.invert_yaxis()
ax.set_xlabel("XGBoost feature importance (gain)")
ax.set_title("Which features matter? (raw + lag + GNN model)")
fig.tight_layout()
fig.savefig("xgboost_importance.png", dpi=120)
plt.close(fig)
print("💾 Saved xgboost_importance.png")


# 7. Learning Check ##########################################################
#
# QUESTION: On the held-out test weeks (40..51), what is the ROC AUC
# of the (raw + lag + GNN 1-hop + GNN 2-hop) XGBoost model?
# Report to 4 decimal places.

print(f"\n📝 Learning Check answer: {auc_gnn:.4f}")

print("\n🎉 Done. Move on to the case study report when you're ready.")
```

---

## `code/09_gnn-xgboost/functions.R`

```r
#' @name functions.R
#' @title Helpers for the GNN + XGBoost case study (R, reticulate bridge)
#' @author <your-name-here>
#' @description
#' R handles almost this entire pipeline natively: loading the supplier
#' tables, engineering the lag feature, training XGBoost, and scoring AUC.
#' The ONE piece with no mature R library is the GNN-style structural
#' embedding, so for that step we reach across to the course's canonical
#' numpy implementation (`functions.py`) through `reticulate`. This file
#' exposes the R-native loaders + `add_lag_features()`, plus a thin
#' `add_gnn_embeddings()` wrapper that drives the Python embedding code.


# 0. R-native loaders and lag feature ########################################

library(dplyr)
library(readr)
library(zoo)
library(here)
library(reticulate)

.case_dir <- function() here::here("code", "11_gnn-xgboost", "data")

load_suppliers <- function() readr::read_csv(file.path(.case_dir(), "suppliers.csv"),
                                             show_col_types = FALSE)
load_edges     <- function() readr::read_csv(file.path(.case_dir(), "edges.csv"),
                                             show_col_types = FALSE)
load_panel     <- function() readr::read_csv(file.path(.case_dir(), "panel.csv"),
                                             show_col_types = FALSE)

#' Add a `lag_rate` column: trailing `window`-week disruption rate per
#' supplier, computed from weeks BEFORE the current one (no leakage).
add_lag_features <- function(panel, window = 4) {
  panel <- panel |> arrange(supplier_id, week)
  panel |>
    group_by(supplier_id) |>
    mutate(
      # week 0 has no history; treat absent history as 0 disruption
      prev = dplyr::lag(disrupted, n = 1, default = 0),
      lag_rate = zoo::rollapply(
        prev, width = window, FUN = mean,
        fill = 0, align = "right", partial = TRUE
      )
    ) |>
    select(-prev) |>
    ungroup()
}


# 1. The GNN half: borrow the embedding from functions.py ####################
#
# The structural embedding is the "A %*% x" piece of a GCN layer applied to
# each week's lag_rate (1-hop = neighbor average, 2-hop = neighbors'
# neighbors). There's no maintained R GNN library, so we call the course's
# numpy implementation. We only need numpy + pandas on the Python side;
# py_require() provisions them on a current reticulate (same idiom as
# dsai/07_rag/05_embed.R), and import_from_path() hands us the module as
# `.gnn_py` without polluting the global namespace.

if (utils::packageVersion("reticulate") >= "1.41") {
  reticulate::py_require(c("numpy", "pandas"))
}

.gnn_py <- reticulate::import_from_path(
  "functions",
  path    = here::here("code", "11_gnn-xgboost"),
  convert = TRUE
)

#' Add `gnn_1hop` and `gnn_2hop` columns to the panel.
#'
#' Builds the row-normalized in-neighbor adjacency from the edge list,
#' then averages each supplier's neighbors' (and 2-hop neighbors')
#' lag_rate, per week. Both steps run in numpy via reticulate.
add_gnn_embeddings <- function(panel, suppliers, edges) {
  A <- .gnn_py$build_adjacency(suppliers, edges)
  .gnn_py$add_gnn_embeddings(panel, suppliers, A)
}
```

---

## `code/09_gnn-xgboost/functions.py`

```python
"""Helpers for the GNN + XGBoost case study.

The pipeline:
  - load static features per supplier + dependency edges + disruption panel
  - build a lag feature: 4-week trailing disruption rate per supplier
  - build a structural-GNN embedding: mean of in-neighbors' lag rate
    (1 hop), plus mean of in-neighbors' in-neighbors' lag rate (2 hop).
    This is a parameter-free GCN-style aggregation; no torch needed.
  - train XGBoost on different feature sets and report ROC AUC.
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd


def _case_dir() -> Path:
    return Path(__file__).resolve().parent / "data"


def load_suppliers() -> pd.DataFrame:
    return pd.read_csv(_case_dir() / "suppliers.csv")


def load_edges() -> pd.DataFrame:
    return pd.read_csv(_case_dir() / "edges.csv")


def load_panel() -> pd.DataFrame:
    return pd.read_csv(_case_dir() / "panel.csv")


def add_lag_features(panel: pd.DataFrame, window: int = 4) -> pd.DataFrame:
    """Add a `lag_rate` column: trailing `window`-week disruption rate per supplier.

    Week 0..window-1 use the available history so far.
    """
    panel = panel.sort_values(["supplier_id", "week"]).copy()
    panel["lag_rate"] = (
        panel.groupby("supplier_id")["disrupted"]
        .shift(1)
        .rolling(window, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
    )
    panel["lag_rate"] = panel["lag_rate"].fillna(0.0)
    return panel


def build_adjacency(suppliers: pd.DataFrame, edges: pd.DataFrame) -> np.ndarray:
    """N x N row-normalized in-neighbor matrix (rows sum to 1 or 0)."""
    n = len(suppliers)
    idx = {s: i for i, s in enumerate(suppliers["supplier_id"].to_numpy())}
    A = np.zeros((n, n))
    for _, e in edges.iterrows():
        A[idx[e["to"]], idx[e["from"]]] = 1
    row_sums = A.sum(axis=1, keepdims=True)
    A = np.divide(A, row_sums, out=np.zeros_like(A), where=row_sums > 0)
    return A


def add_gnn_embeddings(panel: pd.DataFrame, suppliers: pd.DataFrame,
                       A: np.ndarray) -> pd.DataFrame:
    """Add 1-hop and 2-hop neighbor-averaged lag-rate features per week.

    These play the role of GNN embedding dimensions; the math is the
    "A_norm @ x" piece of a GCN layer, parameter-free.
    """
    panel = panel.copy()
    idx = {s: i for i, s in enumerate(suppliers["supplier_id"].to_numpy())}
    panel["_idx"] = panel["supplier_id"].map(idx)

    out_1hop = np.empty(len(panel))
    out_2hop = np.empty(len(panel))
    A2 = A @ A
    for week, sub in panel.groupby("week"):
        # vector of lag_rate per supplier index for this week
        lag = np.zeros(len(suppliers))
        lag[sub["_idx"].to_numpy()] = sub["lag_rate"].to_numpy()
        h1 = A @ lag
        h2 = A2 @ lag
        out_1hop[sub.index] = h1[sub["_idx"].to_numpy()]
        out_2hop[sub.index] = h2[sub["_idx"].to_numpy()]
    panel["gnn_1hop"] = out_1hop
    panel["gnn_2hop"] = out_2hop
    return panel.drop(columns=["_idx"])
```

---

## `code/10_dsm-clustering/README.md`

# Case Study 06 — DSM Clustering

> Interactive lab: [`docs/case-studies/dsm-clustering.html`](../../docs/case-studies/dsm-clustering.html)
>
> Skill: **Measure** · Data: synthetic engineered-system DSM with 200
> components and 8 planted modules

## What you'll learn

How to find modular structure in a Design Structure Matrix
automatically. Specifically:

- Build a DSM as a directed graph from a long-format edge list.
- Apply two community-detection algorithms (Louvain and fast-greedy)
  on the undirected collapse.
- Compare the recovered partition against ground truth using the
  adjusted Rand index.
- Reorder the adjacency matrix by module membership and inspect the
  block-diagonal structure visually.
- Run a k-hop cascade simulation from a chosen component.

## Prerequisites

- Case study 01 (Build a Network).
- The interactive lab.
- R packages: `dplyr`, `tibble`, `igraph`, `ggplot2`, `here`.
- Python packages: see [`code/requirements.txt`](../requirements.txt).
  This case uses `scikit-learn`'s `adjusted_rand_score`.

## Files in this folder

```
06_dsm-clustering/
├── README.md
├── example.R
├── example.py
├── functions.R
├── functions.py
└── data/
    ├── nodes.csv    # 200 components, with `true_module` label for verification
    ├── edges.csv    # ~2,900 directed dependency edges
    └── _generate.py
```

## How to run

```bash
Rscript code/10_dsm-clustering/example.R
python  code/10_dsm-clustering/example.py
```

## Learning check (submit this answer)

> **How many modules does Louvain find in this DSM, and what is the
> modularity score (to 3 decimal places)?**  
> Submit BOTH, separated by a comma. Example: `8, 0.612`.

## Your Project Case Study

If you pick this case study, you'll apply Louvain to *your* network
and discuss what the recovered modules mean in your domain.

### Suggested project questions

1. **What are the modules in my network?** Apply Louvain. Report
   the number of modules, the modularity score, and qualitatively
   describe what 2-3 of the modules represent.

2. **Two clustering algorithms, two stories.** Run Louvain AND
   fast-greedy (or Leiden, walktrap — your choice). Report the
   modularity and number of modules for each, and discuss
   meaningful disagreements between them.

3. **Cascade analysis.** If your network has a meaningful dependency
   direction, simulate k-hop cascades from a few interesting seed
   nodes. Report which seeds produce the largest 1-hop and 2-hop
   cascades.

### Report

- **Question.** One sentence.
- **Network.** Nodes, edges, whether your dependencies are directed.
- **Procedure.** Algorithm(s) run, parameters, any preprocessing.
- **Results.** Numbers in prose; the reordered DSM is a powerful
  figure; at most 2 figures and 1 table.
- **What this tells you, and what it doesn't.** 2-3 sentences.

## Further reading

- The sts course `26C_analytics.R` runs Louvain on a much larger
  committee-affiliation network and uses the modules to make
  geographic comparisons.
- Case study 05 ([`05_supply-chain`](../05_supply-chain)) attacks the
  same question from the other side: which *individual* nodes break
  the network.

---

## `code/10_dsm-clustering/data/_generate.py`

```python
"""Generate a synthetic engineered-system DSM for case 06.

A Design Structure Matrix (DSM) is just an adjacency matrix where
component i depends on component j. We plant K dense modules so the
clustering algorithm has something to recover.

  - 200 components
  - 8 modules of 25 components each
  - intra-module edge probability: 0.40
  - inter-module edge probability: 0.03 (the "residual marks")

Outputs:
  - dsm.csv: long-format edge list (from, to)
  - nodes.csv: node_id + true module label (for verification)

Run:
    python code/10_dsm-clustering/data/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

def main() -> None:
    rng = np.random.default_rng(SEED)

    n = 200
    n_modules = 8
    per_module = n // n_modules
    p_intra = 0.40
    p_inter = 0.03

    # assign each component to a module
    module = np.repeat(np.arange(n_modules), per_module)
    rng.shuffle(module)

    nodes = pd.DataFrame({
        "node_id":   [f"C{i:03d}" for i in range(n)],
        "true_module": module,
    })

    # build directed edges (DSM dependencies)
    rows = []
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            p = p_intra if module[i] == module[j] else p_inter
            if rng.random() < p:
                rows.append({
                    "from": f"C{i:03d}",
                    "to":   f"C{j:03d}",
                })
    edges = pd.DataFrame(rows).sort_values(["from", "to"]).reset_index(drop=True)

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)
    print(f"wrote {HERE / 'nodes.csv'} ({len(nodes)} nodes)")
    print(f"wrote {HERE / 'edges.csv'} ({len(edges)} edges)")


if __name__ == "__main__":
    main()
```

---

## `code/10_dsm-clustering/example.R`

```r
#' @name example.R
#' @title Case Study 06 — DSM Clustering
#' @author <your-name-here>
#' @description
#' A Design Structure Matrix (DSM) is just an adjacency matrix where
#' row i to column j means "component i depends on j." Reordering
#' rows and columns so that dense blocks fall on the diagonal reveals
#' the *modular structure* of the system. The case study lab had you
#' drag rows around by hand; here we let an algorithm do it.
#'
#' Steps:
#'   1. Build the DSM graph from a 200-component synthetic system
#'      with 8 planted modules.
#'   2. Run two community-detection algorithms (Louvain and
#'      fast-greedy) on the undirected projection.
#'   3. Reorder the DSM matrix by recovered modules and verify the
#'      block-diagonal structure visually.
#'   4. Simulate a k-hop cascade from a chosen component.


# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `igraph` carries the community-detection algorithms and the matrix
# conversion. `dplyr` + `tibble` for tidy summaries. Base R `image()`
# does the DSM heatmap (no ggplot needed).
library(dplyr)
library(tibble)
library(igraph)
library(ggplot2)
library(here)

## 0.2 Load helpers ##########################################################

# `cascade_bfs()` does a bounded BFS from a starting node along the
# directed dependency edges. It's the cascade simulator we use at the
# end of the script.
source(here::here("code", "06_dsm-clustering", "functions.R"))

cat("\n🚀 Case Study 06 — DSM Clustering (R)\n")
cat("   200 components, 8 planted modules. Can community detection recover them?\n\n")

## 0.3 Load data #############################################################

nodes <- load_nodes()
edges <- load_edges()
g     <- build_graph(nodes, edges)
g
cat(sprintf("✅ Loaded DSM: %d components, %d dependency edges.\n",
            igraph::vcount(g), igraph::ecount(g)))


# 1. Community detection #####################################################
#
# Louvain and fast-greedy both want an undirected graph, so we collapse
# each directed dependency "A depends on B" into a plain "A and B are
# linked." Why it's OK here: community detection asks "which components
# clump together?", and two parts that depend on each other belong in the
# same cluster regardless of which way the arrow points. What we give up:
# the direction itself -- we can no longer tell driver from dependent
# within a cluster. Fine for grouping; keep direction if you cared about
# what cascades when one part fails.

g_undirected <- igraph::as_undirected(g, mode = "collapse")
g_undirected

# A quick word on MODULARITY, the score both algorithms maximize: it
# measures how much more edge weight falls inside communities than you'd
# expect at random. It runs roughly -0.5 to 1; ~0 means "no more clustered
# than random", and > ~0.3 is usually a meaningful community structure.
# We planted 8 modules, so recovering 8 at a healthy modularity is the win.

# Louvain (igraph's `cluster_louvain`): greedy modularity optimization,
# moves nodes between communities to maximize modularity score.
#
# Louvain is STOCHASTIC -- it visits nodes in a randomized order, so an
# unseeded run usually recovers the 8 planted modules (modularity 0.470)
# but occasionally merges two and reports 7 (~0.454). We seed for a
# reproducible Learning Check; expect your own data to wobble by a module
# or two between runs if you don't.
set.seed(5470)
louvain <- igraph::cluster_louvain(g_undirected)
cat(sprintf("📊 Louvain found %d modules. Modularity: %.3f\n",
            length(louvain), igraph::modularity(louvain)))

# Fast-greedy: agglomerative — start with each node in its own community,
# repeatedly merge the pair whose merge most increases modularity. It often
# recovers FEWER modules than Louvain on dense graphs: once it has merged
# greedily it never splits back, so adjacent planted modules get fused into
# one and the recovered count comes in under the truth. That's an algorithm
# property, not randomness — Louvain's node-moving phase avoids it here.
fg <- igraph::cluster_fast_greedy(g_undirected)
cat(sprintf("📊 Fast-greedy found %d modules. Modularity: %.3f\n",
            length(fg), igraph::modularity(fg)))


# 2. Compare to ground truth #################################################
#
# Our synthetic data planted 8 modules. The Adjusted Rand Index (ARI)
# measures how well two clusterings agree, corrected for chance:
# 1.0 = perfect agreement, 0.0 = chance, < 0 = worse than chance.
# Rough field convention for "how good is this recovery?": ARI > 0.8 is a
# strong match, 0.5–0.8 partial, < 0.5 weak. So Louvain's 1.0 is a perfect
# recovery; fast-greedy's lower score reflects the merged modules above.

true_mod <- igraph::V(g)$true_module
ari_louv <- igraph::compare(true_mod, louvain$membership, method = "adjusted.rand")
ari_fg   <- igraph::compare(true_mod, fg$membership,     method = "adjusted.rand")
cat(sprintf("🧪 Louvain    ARI vs truth: %.3f\n", ari_louv))
cat(sprintf("🧪 FastGreedy ARI vs truth: %.3f\n", ari_fg))


# 3. Reorder the DSM by recovered module #####################################
#
# Sort node indices by Louvain module ID. Then build the n x n
# adjacency matrix in that order. Dense blocks should land on the
# diagonal — that's what "modular structure" *looks like*.

ord      <- order(louvain$membership)
A        <- as.matrix(igraph::as_adjacency_matrix(g))
A_sorted <- A[ord, ord]

# Side-by-side base-R image() plots. Reverse the y-axis so row 1 lands
# at the top, like an actual matrix. Wrapped in a function so we can draw
# it both to the screen and to a PNG (Rscript otherwise hides it in
# Rplots.pdf).
draw_dsm <- function() {
  par(mfrow = c(1, 2))
  image(t(A)[, nrow(A):1], col = c("white", "black"), axes = FALSE,
        main = "DSM — original order")
  image(t(A_sorted)[, nrow(A_sorted):1], col = c("white", "black"), axes = FALSE,
        main = "DSM — reordered by Louvain")
  par(mfrow = c(1, 1))
}

# Show interactively...
draw_dsm()

# ...and save a copy for terminal / Rscript users.
png(here::here("code", "06_dsm-clustering", "dsm_reordering.png"),
    width = 9, height = 5, units = "in", res = 120)
draw_dsm()
invisible(dev.off())
cat("💾 Saved dsm_reordering.png\n")


# 4. Cascade simulation ######################################################
#
# When component C037 fails, every component that depends on it can
# fail too. We bound to k hops because in a densely-coupled DSM an
# unbounded cascade reaches everything. The interesting question:
# how many fall in the FIRST FEW HOPS?
#
# Why can a cascade reach far beyond C037's own module even though Louvain
# found clean modules? Because a cascade follows EDGES, not module walls.
# Community detection only says edges are DENSER within modules, not that
# none cross. C037 has a few cross-module dependency edges, and BFS happily
# traverses them -- so a single hub failure jumps boundaries the clustering
# drew.

seed <- "C037"
for (k in c(1, 2, 3)) {
  cat(sprintf("🔗 Cascade from %s in %d hop(s): %d components\n",
              seed, k, length(cascade_bfs(g, seed, n_hops = k))))
}


# 5. Learning Check ##########################################################
#
# QUESTION: How many modules does Louvain find in this DSM, and what
# is the modularity score (to 3 decimal places)? Submit BOTH numbers,
# separated by a comma. Example: "8, 0.612"

n_modules  <- length(louvain)
modularity <- round(igraph::modularity(louvain), 3)

cat(sprintf("\n📝 Learning Check answer: %d, %.3f\n", n_modules, modularity))

cat("\n🎉 Done. Move on to the case study report when you're ready.\n")
```

---

## `code/10_dsm-clustering/example.py`

```python
"""Case Study 06 — DSM Clustering (Python track).

A Design Structure Matrix (DSM) is just an adjacency matrix where row
i to column j means "component i depends on j." Reordering rows and
columns so that dense blocks fall on the diagonal reveals the *modular
structure* of the system. The case study lab had you drag rows around
by hand; here we let an algorithm do it.

Steps:
  1. Build the DSM graph from a 200-component synthetic system with
     8 planted modules.
  2. Run two community-detection algorithms (Louvain and fast-greedy)
     on the undirected projection.
  3. Reorder the DSM matrix by recovered modules and verify the
     block-diagonal structure visually.
  4. Simulate a cascade: which components fail when component C037
     fails (BFS along outgoing dependency edges).
"""

# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `igraph` for community detection + matrix conversion. `numpy` for
# matrix reordering. `matplotlib.imshow` for the DSM heatmap.
import random
import pandas as pd
import numpy as np
import igraph as ig
import matplotlib.pyplot as plt

## 0.2 Load helpers ##########################################################

# `cascade_bfs()` does a bounded BFS from a starting node along the
# directed dependency edges. It's the cascade simulator we use at the
# end of the script.
from functions import load_nodes, load_edges, build_graph, cascade_bfs

print("\n🚀 Case Study 06 — DSM Clustering (Python)")
print("   200 components, 8 planted modules. Can community detection recover them?\n")

## 0.3 Load data #############################################################

nodes = load_nodes()
edges = load_edges()
g     = build_graph(nodes, edges)
print(g.summary())
print(f"✅ Loaded DSM: {g.vcount()} components, {g.ecount()} dependency edges.")


# 1. Community detection #####################################################
#
# Louvain and fast-greedy both want an undirected graph, so we collapse
# each directed dependency "A depends on B" into a plain "A and B are
# linked." Why it's OK here: community detection asks "which components
# clump together?", and two parts that depend on each other belong in the
# same cluster regardless of which way the arrow points. What we give up:
# the direction itself -- we can no longer tell driver from dependent
# within a cluster. That's fine for grouping, but you'd keep direction if
# you cared about, say, what cascades when one part fails.

g_undirected = g.as_undirected(mode="collapse")
print(g_undirected.summary())

# A quick word on MODULARITY, the score both algorithms maximize: it
# measures how much more edge weight falls inside communities than you'd
# expect at random. It runs roughly -0.5 to 1; ~0 means "no more clustered
# than random", and > ~0.3 is usually a meaningful community structure.
# We planted 8 modules, so recovering 8 at a healthy modularity is the win.

# Louvain (igraph's `community_multilevel`): greedy modularity
# optimization, moves nodes between communities to maximize modularity.
#
# Louvain is STOCHASTIC -- it visits nodes in a randomized order, so an
# unseeded run usually recovers the 8 planted modules (modularity 0.470)
# but can occasionally merge two and report 7 (~0.454). We seed for a
# reproducible Learning Check; expect your own data to wobble by a module
# or two between runs if you don't.
random.seed(5470)
louvain = g_undirected.community_multilevel()
print(f"📊 Louvain found {len(louvain)} modules. Modularity: {louvain.modularity:.3f}")

# Fast-greedy: agglomerative — start with each node in its own community,
# repeatedly merge the pair whose merge most increases modularity. It often
# recovers FEWER modules than Louvain on dense graphs: once it has merged
# greedily it never splits back, so adjacent planted modules get fused into
# one and the recovered count comes in under the truth. That's an algorithm
# property, not randomness — Louvain's node-moving phase avoids it here.
fg = g_undirected.community_fastgreedy().as_clustering()
print(f"📊 Fast-greedy found {len(fg)} modules. Modularity: {fg.modularity:.3f}")


# 2. Compare to ground truth #################################################
#
# Our synthetic data planted 8 modules. The Adjusted Rand Index (ARI)
# measures how well two clusterings agree, corrected for chance:
# 1.0 = perfect agreement, 0.0 = chance, < 0 = worse than chance.
# Rough field convention: ARI > 0.8 is a strong match, 0.5–0.8 partial,
# < 0.5 weak. So Louvain's 1.0 is a perfect recovery; fast-greedy's lower
# score reflects the merged modules noted above.
# (igraph ships no ARI, so we borrow sklearn's one function for it.)

from sklearn.metrics import adjusted_rand_score
true_module = np.array(g.vs["true_module"])
louvain_lbl = np.array(louvain.membership)
fg_lbl      = np.array(fg.membership)

print(f"🧪 Louvain    ARI vs truth: {adjusted_rand_score(true_module, louvain_lbl):.3f}")
print(f"🧪 FastGreedy ARI vs truth: {adjusted_rand_score(true_module, fg_lbl):.3f}")


# 3. Reorder the DSM by recovered module #####################################
#
# Sort node indices by Louvain module ID. Then build the n x n
# adjacency matrix in that order. Dense blocks should land on the
# diagonal — that's what "modular structure" *looks like*.

order = np.argsort(louvain_lbl, kind="stable")
A = np.array(g.get_adjacency().data)
A_sorted = A[np.ix_(order, order)]

# Side-by-side imshow plots: original ordering vs reordered.
fig, axes = plt.subplots(1, 2, figsize=(10, 5))
axes[0].imshow(A, cmap="Greys", aspect="equal")
axes[0].set_title("DSM — original order")
axes[1].imshow(A_sorted, cmap="Greys", aspect="equal")
axes[1].set_title("DSM — reordered by Louvain module")
for ax in axes:
    ax.set_xticks([]); ax.set_yticks([])
fig.tight_layout()
fig.savefig("dsm_reorder.png", dpi=120)
plt.close(fig)
print("💾 Saved dsm_reorder.png")


# 4. Cascade simulation ######################################################
#
# When component C037 fails, every component that depends on it can
# fail too. We bound to k hops because in a densely-coupled DSM an
# unbounded cascade reaches everything. The interesting question:
# how many components fall in the FIRST FEW HOPS?
#
# Why can a cascade reach far beyond C037's own module even though Louvain
# found clean modules? Because a cascade follows EDGES, not module walls.
# Community detection only says edges are DENSER within modules, not that
# none cross. C037 has a few cross-module dependency edges, and BFS happily
# traverses them -- so a single hub failure jumps boundaries the clustering
# drew.

seed = "C037"
for k in [1, 2, 3]:
    failed = cascade_bfs(g, seed, n_hops=k)
    print(f"🔗 Cascade from {seed} in {k} hop(s): {len(failed)} components")


# 5. Learning Check ##########################################################
#
# QUESTION: How many modules does Louvain find in this DSM, and what
# is the modularity score (to 3 decimal places)?
# Submit BOTH numbers, separated by a comma.
# Example answer format: "8, 0.612"

n_modules = len(louvain)
modularity = round(louvain.modularity, 3)

print(f"\n📝 Learning Check answer: {n_modules}, {modularity:.3f}")

print("\n🎉 Done. Move on to the case study report when you're ready.")
```

---

## `code/10_dsm-clustering/functions.R`

```r
#' @name functions.R
#' @title Helpers for the DSM Clustering case study

library(readr)
library(dplyr)
library(igraph)
library(here)

.case_dir <- function() here::here("code", "06_dsm-clustering", "data")

load_nodes <- function() readr::read_csv(file.path(.case_dir(), "nodes.csv"),
                                         show_col_types = FALSE)
load_edges <- function() readr::read_csv(file.path(.case_dir(), "edges.csv"),
                                         show_col_types = FALSE)

#' Build the DSM dependency graph (directed).
build_graph <- function(nodes = load_nodes(), edges = load_edges()) {
  igraph::graph_from_data_frame(
    d        = edges,
    directed = TRUE,
    vertices = nodes
  )
}

#' Components that fail within `n_hops` of `seed_node`.
#'
#' Follows outgoing dependency edges. With high inter-module
#' connectivity, an unbounded cascade can reach every component, so
#' we bound to k hops to keep the simulation interpretable.
cascade_bfs <- function(g, seed_node, n_hops = 3) {
  idx <- which(igraph::V(g)$name == seed_node)
  reached <- igraph::ego(g, order = n_hops, nodes = idx, mode = "out")[[1]]
  reached$name
}
```

---

## `code/10_dsm-clustering/functions.py`

```python
"""Helpers for the DSM Clustering case study."""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig


def _case_dir() -> Path:
    return Path(__file__).resolve().parent / "data"


def load_nodes() -> pd.DataFrame:
    return pd.read_csv(_case_dir() / "nodes.csv")


def load_edges() -> pd.DataFrame:
    return pd.read_csv(_case_dir() / "edges.csv")


def build_graph(nodes: pd.DataFrame | None = None,
                edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the DSM dependency graph (directed)."""
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    return ig.Graph.DataFrame(
        edges=edges,
        directed=True,
        vertices=nodes,
        use_vids=False,
    )


def cascade_bfs(g: ig.Graph, seed_node: str, n_hops: int = 3) -> list[str]:
    """Components that fail within ``n_hops`` of ``seed_node``.

    Follows outgoing dependency edges. With high inter-module
    connectivity, an unbounded cascade can reach every component, so
    we bound to k hops to keep the simulation interpretable.
    """
    seed = g.vs.find(name=seed_node).index
    reached = g.neighborhood(seed, order=n_hops, mode="out")
    return [g.vs[i]["name"] for i in reached]
```

---

## `code/11_sampling/README.md`

# Case Study 08 — Sampling Big Networks

> Interactive lab: [`docs/case-studies/sampling.html`](../../docs/case-studies/sampling.html)
>
> Skill: **Identify** · Data: trimmed Hurricane Dorian evacuation
> flow network (316 Florida county subdivisions, ~33,000 weighted
> edges across 8-hour time slices in the Aug 28 - Sep 10 crisis
> window)

## What you'll learn

When a network is too big to fit in memory or in your head, you
sample. But each sampling strategy preserves *different* properties:

- **Ego-centric**: pick N seed nodes, keep edges touching them.
  Preserves node-attribute distributions; can over-sample hubs.
- **Edgewise**: sample edges uniformly. Preserves edge-attribute
  distributions; may miss components.
- **Spatial buffer**: keep nodes within R km of a point of
  interest. Preserves local structure; deeply biased by where you
  drew the circle.

We measure how well each strategy reproduces a *time series* of a
normalized metric — `avg_edgeweight` per node — across the
two-week crisis window.

## Prerequisites

- Case study 02 (Joins).
- The interactive lab.
- R packages: `dplyr`, `tidyr`, `readr`, `ggplot2`, `sf`, `here`.
- Python packages: see [`code/requirements.txt`](../requirements.txt).
  Spatial operations need `geopandas` and `shapely`.

## Files in this folder

```
08_sampling/
├── README.md
├── example.R
├── example.py
├── functions.R                       # `slice_stats()` + loaders
├── functions.py
└── data/
    ├── nodes.csv                  # 316 FL county subdivisions w/ centroid x,y
    ├── edges.csv                  # ~33k 8-hour-slice evacuation flows
    ├── county_subdivisions.geojson    # FL only, simplified polygons
    └── _generate.py                   # trims the raw sts data
```

## How to run

```bash
Rscript code/11_sampling/example.R
python  code/11_sampling/example.py
```

## Learning check (submit this string)

> **Of the three sampling strategies above (`ego_centric`,
> `edgewise`, `spatial_buffer`), which one best preserves the
> population's `avg_edgeweight` time series — measured by the
> smallest max-absolute-deviation across time slices?**

Submit one of: `ego_centric`, `edgewise`, `spatial_buffer`.

## Your Project Case Study

If you pick this case study, you'll sample *your* large network
under at least two strategies and report which network properties
each one preserves vs distorts.

### Suggested project questions

1. **Strategy showdown.** Sample your network ego-centrically and
   edgewise to the same edge count. Compute normalized metrics
   (density, share of nodes linked, edge ratio, mean edge weight)
   on each. Report which metric each strategy preserves best.

2. **Sample-size convergence.** Pick one strategy. Vary the sample
   size from very small to as-large-as-the-population. Report the
   sample size at which density (or another metric you care about)
   stabilizes to within 5% of the population value.

3. **Spatial / temporal targeting.** If your network has a spatial
   or temporal structure, filter by a meaningful region or window
   *before* sampling. Compare the filtered-then-sampled network's
   properties against an unfiltered sample of the same size.

### Report

- **Question.** One sentence.
- **Network.** Nodes, edges, weight semantics, size.
- **Procedure.** Strategy/strategies, sample sizes, RNG seed.
- **Results.** Numbers in prose; at most 2 figures (the over-time
  comparison plot is the strongest); 1 table of preservation
  metrics by strategy.
- **What this tells you, and what it doesn't.** 2-3 sentences,
  including: sampling strategies are not generic — they trade off
  properties, and the right strategy depends on which property
  your question depends on.

## Further reading

- The sts course `29C_databases.R` is the parent workshop. It
  covers the same network at Gulf-states scale and develops more
  sampling strategies (random-walk, snowball).
- For a deeper dive on sampling theory in networks, see Leskovec &
  Faloutsos (2006) "Sampling from large graphs."

---

## `code/11_sampling/data/_generate.py`

```python
"""Generate the slim Hurricane Dorian evacuation dataset for case 08.

We start from the full Gulf-states evacuation network at
https://github.com/timothyfraser/sts (3week branch) and trim:

  - keep only Florida nodes (state FIPS = "12")
  - keep only the columns we use: node, geoid, pop, median_income
  - precompute x/y centroids from the geojson and store on the node
    table, so neither R nor Python needs sf/geopandas just to load
  - keep only edges with evacuation > 0 within Aug 28 - Sep 10, 2019
  - bundle a slimmed florida-only county_subdivisions.geojson

The source .rds files come from:
  https://raw.githubusercontent.com/timothyfraser/sts/3week/data/evacuation/

This script expects them to have been fetched to /tmp/sts_data/:

    mkdir -p /tmp/sts_data && cd /tmp/sts_data
    for f in nodes.rds edges.rds county_subdivisions.geojson states.geojson; do
      curl -sLO "https://raw.githubusercontent.com/timothyfraser/sts/3week/data/evacuation/$f"
    done

Run:
    python code/11_sampling/data/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import pyreadr
import geopandas as gpd

HERE = Path(__file__).resolve().parent
SRC = Path("/tmp/sts_data")

def main() -> None:
    if not SRC.exists():
        raise SystemExit(
            f"expected sts source data at {SRC}; see the docstring at the "
            "top of this script for the curl commands."
        )

    # --- nodes ----------------------------------------------------------------
    n = pyreadr.read_r(str(SRC / "nodes.rds"))[None]
    n = n.assign(state=n["geoid"].str[:2]).loc[lambda d: d["state"] == "12"]
    n = n[["node", "geoid", "pop", "median_income"]].reset_index(drop=True)
    n["node"] = n["node"].astype(int)

    # --- subdivisions polygons (filter to FL, dissolve to centroids) ----------
    cs = gpd.read_file(SRC / "county_subdivisions.geojson")
    cs = cs[cs["geoid"].astype(str).str[:2] == "12"].copy()
    # add x,y centroid to nodes via merge
    centroids = cs.set_geometry(cs.geometry.centroid)
    cs["x"] = centroids.geometry.x.to_numpy()
    cs["y"] = centroids.geometry.y.to_numpy()
    n = n.merge(cs[["geoid", "x", "y"]], on="geoid", how="left")

    # --- edges ----------------------------------------------------------------
    e = pyreadr.read_r(str(SRC / "edges.rds"))[None]
    e = e[["from", "to", "date_time", "evacuation", "km"]].copy()
    e["from"] = e["from"].astype(int)
    e["to"]   = e["to"].astype(int)
    e["date_time"] = pd.to_datetime(e["date_time"])

    # Filter to Florida nodes
    fl_nodes = set(n["node"].astype(int))
    e = e[e["from"].isin(fl_nodes) & e["to"].isin(fl_nodes)]
    # Filter to evacuation > 0 in the crisis window
    start = pd.Timestamp("2019-08-28")
    end   = pd.Timestamp("2019-09-11")
    e = e[(e["evacuation"] > 0) & (e["date_time"] >= start) & (e["date_time"] < end)]
    e = e.reset_index(drop=True)

    # --- write outputs --------------------------------------------------------
    n.to_csv(HERE / "nodes.csv", index=False)
    e.to_csv(HERE / "edges.csv", index=False)

    # Trim subdivisions geojson: drop attribute columns and simplify
    # geometry to keep the file small enough to bundle in a repo.
    cs_slim = cs[["geoid", "geometry"]].copy()
    cs_slim["geometry"] = cs_slim.geometry.simplify(tolerance=0.005,
                                                    preserve_topology=True)
    cs_slim.to_file(HERE / "county_subdivisions.geojson", driver="GeoJSON")

    print(f"wrote {HERE / 'nodes.csv'} ({len(n)} nodes)")
    print(f"wrote {HERE / 'edges.csv'} ({len(e):,} edges)")
    print(f"wrote {HERE / 'county_subdivisions.geojson'} (FL only)")


if __name__ == "__main__":
    main()
```

---

## `code/11_sampling/example.R`

```r
#' @name example.R
#' @title Case Study 08 — Sampling Big Networks
#' @author <your-name-here>
#' @description
#' You can't analyze every node in a million-node network on a laptop.
#' So we sample. But sampling is not neutral — each strategy preserves
#' some properties and distorts others.
#'
#' Data: Hurricane Dorian evacuation flows over Florida county
#' subdivisions, Aug 28 - Sep 10, 2019. Each edge is a (from, to,
#' date_time, evacuation) row where `evacuation` is how many MORE
#' local Facebook users moved between two cities in that 8-hour
#' window than usual. The original sts workshop 29C_databases.R
#' covers this at the Gulf-states scale; we trim to Florida and the
#' crisis weeks.
#'
#' We will:
#'   1. Compute baseline per-time-slice stats on the full network.
#'   2. Apply three sampling strategies (ego, edgewise, spatial buffer).
#'   3. Compare each against the population over time.


# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `dplyr`/`tidyr` for the per-slice aggregations, `sf` for the spatial
# buffer (the only part of this script that needs spatial libraries),
# `ggplot2` for the comparison figure.
library(dplyr)
library(tidyr)
library(ggplot2)
library(sf)
library(here)

## 0.2 Load helpers ##########################################################

# `slice_stats()` computes the per-time-slice network statistics
# (edgeweight, share of nodes touched, etc.) for any edge subset.
# That's the workhorse we'll reuse on every sample.
source(here::here("code", "08_sampling", "functions.R"))

cat("\n🚀 Case Study 08 — Sampling Big Networks (R)\n")
cat("   Three sampling strategies vs population. Which one preserves the truth?\n\n")

## 0.3 Load data #############################################################

nodes <- load_nodes()
edges <- load_edges()
cs    <- load_subdivisions()
cat(sprintf("✅ Loaded %d nodes, %d edges, %d subdivisions.\n",
            nrow(nodes), nrow(edges), nrow(cs)))


# 1. Baseline (population) statistics over time ##############################
#
# We compute four numbers per 8-hour slice: total edgeweight, share of
# nodes touched, edge ratio, average edgeweight per node. The figure
# at the end compares each sample's time series to this baseline.

n_total <- nrow(nodes)
stats   <- slice_stats(edges, n_total)
stats |> head()
cat(sprintf("📊 Baseline: %d time slices computed.\n", nrow(stats)))


# 2. Sampling strategies ######################################################

set.seed(42)  # deterministic samples across runs

## 2.1 Ego-centric: 50 random seed nodes, keep edges touching any of them ####

# An ego sample is biased toward whatever the seeds are. With random
# seeds, the bias averages out, but small samples are still noisy.
ego_nodes <- nodes |> slice_sample(n = 50) |> pull(node)
ego_edges <- edges |> filter(from %in% ego_nodes | to %in% ego_nodes)
ego_stats <- slice_stats(ego_edges, n_total)
cat(sprintf("✅ Ego sample: %d seeds, %d edges retained.\n",
            length(ego_nodes), nrow(ego_edges)))

## 2.2 Edgewise: 10,000 random edges #########################################

# Uniform random sampling of edges. Preserves the marginal edge-weight
# distribution well but tends to leave nodes with low degree under-sampled.
edge_sample <- edges |> slice_sample(n = 10000)
edge_stats  <- slice_stats(edge_sample, n_total)
cat(sprintf("✅ Edge sample: %d edges.\n", nrow(edge_sample)))

## 2.3 Spatial buffer: nodes within 200 km of Miami ##########################

# Drop the handful of nodes whose centroid couldn't be computed (a
# subdivision present in the node table but missing from the trimmed
# geojson). sf is strict about NAs in coordinates.
nodes_geo <- nodes |> filter(!is.na(x), !is.na(y))

# Use Miami as our point of interest (POI). Why the projection dance?
# EPSG:4326 is lat/lon in DEGREES, so a "200 km" buffer in degrees is
# meaningless (a degree is a different distance at the equator vs Maine).
# EPSG:3857 is in METERS, so we project there to draw the 200 km circle,
# then project back to 4326 to match the node coordinates. Non-GIS
# readers: switch to a meter ruler, measure, switch back.
miami <- nodes_geo |> filter(geoid == "1208692158") |> slice(1)
poi <- sf::st_as_sf(
  data.frame(x = miami$x, y = miami$y),
  coords = c("x", "y"), crs = 4326
)
buf <- poi |>
  sf::st_transform(3857) |>
  sf::st_buffer(dist = 200 * 1000) |>
  sf::st_transform(4326)

node_pts     <- sf::st_as_sf(nodes_geo, coords = c("x", "y"), crs = 4326)
nodes_in_buf <- sf::st_join(node_pts, buf, join = sf::st_within, left = FALSE)
ids_in       <- nodes_in_buf$node

# Keep only edges where BOTH endpoints are inside the buffer.
buf_edges <- edges |> filter(from %in% ids_in & to %in% ids_in)
buf_stats <- slice_stats(buf_edges, n_total)
cat(sprintf("✅ Buffer sample: %d nodes within 200 km of Miami, %d edges.\n",
            length(ids_in), nrow(buf_edges)))


# 3. Compare ##################################################################

p <- bind_rows(
  stats     |> mutate(strategy = "Population"),
  ego_stats |> mutate(strategy = "Ego-centric"),
  edge_stats|> mutate(strategy = "Edgewise"),
  buf_stats |> mutate(strategy = "Spatial buffer")
) |>
  ggplot(aes(x = date_time, y = avg_edgeweight, color = strategy)) +
  geom_line() +
  labs(y     = "avg edgeweight per node",
       title = "Sample vs population — avg edgeweight per node",
       x     = NULL) +
  theme_classic(base_size = 12) +
  theme(axis.text.x = element_text(angle = 30, hjust = 1))

# This is the figure that makes the whole case: all three sample lines
# against the population line. Show it AND save it (Rscript otherwise hides
# it in Rplots.pdf, so the most important plot in the lab goes unseen).
print(p)
ggsave(here::here("code", "08_sampling", "sample_vs_population.png"),
       p, width = 7, height = 4.5, dpi = 120)
cat("💾 Saved sample_vs_population.png\n")


# 4. Which strategy best preserves avg_edgeweight? ###########################
#
# What makes one sample "better"? It tracks the true population most
# closely. We score that as the max absolute deviation: over the whole
# time series, the largest gap between the sample's average edge weight
# and the population's. Smaller = better, and we pick the strategy that
# minimizes it. (Worst-case gap is a simple, strict choice; you could
# instead use mean-squared error or correlation for average-case fit.)

max_abs_dev <- function(sample_stats) {
  merged <- inner_join(
    stats        |> select(date_time, pop  = avg_edgeweight),
    sample_stats |> select(date_time, samp = avg_edgeweight),
    by = "date_time"
  )
  max(abs(merged$pop - merged$samp))
}

mad <- c(
  ego_centric    = max_abs_dev(ego_stats),
  edgewise       = max_abs_dev(edge_stats),
  spatial_buffer = max_abs_dev(buf_stats)
)
cat("Max |population - sample| in avg_edgeweight, by strategy (smaller = better):\n")
print(round(mad, 3))
winner <- names(which.min(mad))
cat(sprintf("📊 Best preservation (smallest max-absolute-deviation): %s\n", winner))

# WHY does the spatial buffer usually win for this network? Evacuation flow
# is spatially structured -- neighboring subdivisions surge together -- so a
# geographic buffer captures a coherent, internally-intact subnetwork whose
# per-node averages track the population. Ego and edgewise sampling slice
# the graph arbitrarily, fragmenting that local structure.


# 5. Learning Check ##########################################################
#
# QUESTION: Of the three sampling strategies above (ego-centric,
# edgewise, spatial buffer around Miami), which one best preserves
# the population's `avg_edgeweight` time series — measured by the
# smallest max-absolute-deviation? Submit the strategy name.

cat(sprintf("\n📝 Learning Check answer: %s\n", winner))

cat("\n🎉 Done. Move on to the case study report when you're ready.\n")
```

---

## `code/11_sampling/example.py`

```python
"""Case Study 08 — Sampling Big Networks (Python track).

You can't analyze every node in a million-node network on a laptop.
So we sample. But sampling is not neutral — each strategy preserves
some properties and distorts others. This case study shows you which.

Data: Hurricane Dorian evacuation flows over Florida county
subdivisions, Aug 28 - Sep 10, 2019. Each edge is a (from, to,
date_time, evacuation) tuple where `evacuation` is how many MORE
local Facebook users moved between two cities in that 8-hour window
than usual. The original sts workshop 29C_databases.R covers the
same network at a Gulf scale; we trim to Florida and to the crisis
weeks.

We will:
  1. Compute baseline per-time-slice network statistics on the full
     filtered network.
  2. Take three sampling strategies (ego-centric, edgewise, spatial
     buffer around Miami).
  3. Compare each sample's stats against the population over time.
"""

# 0. Setup ###################################################################

## 0.1 Packages ##############################################################

# `pandas`/`numpy` for the per-slice aggregations, `geopandas`/`shapely`
# for the spatial buffer (the only part of this script that needs
# spatial libraries), `matplotlib` for the comparison figure.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point

## 0.2 Load helpers ##########################################################

# `slice_stats()` computes the per-time-slice network statistics
# (edgeweight, share of nodes touched, etc.) for any edge subset.
# That's the workhorse we'll reuse on every sample.
from functions import (
    load_nodes, load_edges, load_subdivisions, slice_stats,
)

print("\n🚀 Case Study 08 — Sampling Big Networks (Python)")
print("   Three sampling strategies vs population. Which one preserves the truth?\n")

## 0.3 Load data #############################################################

nodes = load_nodes()
edges = load_edges()
print(f"nodes: {len(nodes):,}  edges: {len(edges):,}")
print(edges.head())
print(f"✅ Loaded {len(nodes)} nodes, {len(edges)} edges.")


# 1. Baseline (population) statistics over time ##############################
#
# We compute four numbers per 8-hour slice: total edgeweight, share of
# nodes touched, edge ratio, average edgeweight per node. The figure
# at the end compares each sample's time series to this baseline.

n_total = len(nodes)
stats = slice_stats(edges, n_total)
print(stats.head())
print(f"📊 Baseline: {len(stats)} time slices computed.")


# 2. Sampling strategies #####################################################

rng = np.random.default_rng(42)  # deterministic samples across runs

## 2.1 Ego-centric: sample N nodes, keep edges that touch any sampled node ###

# An ego sample is biased toward whatever the seeds are. With random
# seeds, the bias averages out, but small samples are still noisy.
ego_nodes = nodes.sample(n=50, random_state=42)["node"].to_numpy()
ego_edges = edges[edges["from"].isin(ego_nodes) | edges["to"].isin(ego_nodes)]
print(f"ego sample: {len(ego_nodes)} seed nodes, {len(ego_edges):,} edges")
ego_stats = slice_stats(ego_edges, n_total)
print(f"✅ Ego sample: {len(ego_nodes)} seeds, {len(ego_edges)} edges retained.")

## 2.2 Edgewise: sample edges uniformly ######################################

# Uniform random sampling of edges. Preserves the marginal edge-weight
# distribution well but tends to leave nodes with low degree under-sampled.
edge_sample = edges.sample(n=10_000, random_state=42)
edge_stats  = slice_stats(edge_sample, n_total)
print(f"edge sample: {len(edge_sample):,} edges")
print(f"✅ Edge sample: {len(edge_sample)} edges.")

## 2.3 Spatial buffer: keep edges where BOTH endpoints are within 200 km of Miami

# Use Miami as our point of interest (POI). Why the projection dance?
# EPSG:4326 is lat/lon in DEGREES, so a "200 km" buffer in degrees is
# meaningless (a degree is a different distance at the equator vs Maine).
# EPSG:3857 is in METERS, so we project there to draw the 200 km circle,
# then project back to 4326 to match the node coordinates. Non-GIS
# readers: switch to a meter ruler, measure, switch back.
miami_geoid = "1208692158"
miami_row = nodes[nodes["geoid"] == miami_geoid].iloc[0]
poi = gpd.GeoSeries([Point(miami_row["x"], miami_row["y"])], crs="EPSG:4326")
poi_m   = poi.to_crs("EPSG:3857")
buf_m   = poi_m.buffer(200_000)              # 200 km
buf_ll  = gpd.GeoSeries(buf_m, crs="EPSG:3857").to_crs("EPSG:4326")

node_pts = gpd.GeoDataFrame(
    nodes,
    geometry=[Point(xy) for xy in zip(nodes["x"], nodes["y"])],
    crs="EPSG:4326",
)
nodes_in_buf = node_pts[node_pts.within(buf_ll.iloc[0])]
print(f"buffer sample: {len(nodes_in_buf)} nodes within 200 km of Miami")

# Keep only edges where BOTH endpoints are inside the buffer.
ids_in = set(nodes_in_buf["node"].to_numpy())
buf_edges = edges[edges["from"].isin(ids_in) & edges["to"].isin(ids_in)]
buf_stats = slice_stats(buf_edges, n_total)
print(f"✅ Buffer sample: {len(nodes_in_buf)} nodes within 200 km of Miami, "
      f"{len(buf_edges)} edges.")


# 3. Compare samples vs population ###########################################

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharex=True)

ax = axes[0]
ax.plot(stats["date_time"],     stats["avg_edgeweight"],     label="Population",     color="black")
ax.plot(ego_stats["date_time"], ego_stats["avg_edgeweight"], label="Ego-centric",     color="#3a8bc6")
ax.plot(edge_stats["date_time"],edge_stats["avg_edgeweight"],label="Edgewise",        color="#e07b3a")
ax.plot(buf_stats["date_time"], buf_stats["avg_edgeweight"], label="Spatial buffer", color="#7b3ae0")
ax.set_ylabel("avg_edgeweight (per node)")
ax.legend(fontsize=8)
ax.set_title("avg edgeweight per node")

ax = axes[1]
ax.plot(stats["date_time"],     stats["pc_nodes_linked"],     label="Population",     color="black")
ax.plot(ego_stats["date_time"], ego_stats["pc_nodes_linked"], label="Ego-centric",     color="#3a8bc6")
ax.plot(edge_stats["date_time"],edge_stats["pc_nodes_linked"],label="Edgewise",        color="#e07b3a")
ax.plot(buf_stats["date_time"], buf_stats["pc_nodes_linked"], label="Spatial buffer", color="#7b3ae0")
ax.set_ylabel("pc_nodes_linked")
ax.set_title("share of nodes touched by any edge")

for ax in axes:
    ax.tick_params(axis="x", rotation=30)
fig.tight_layout()
fig.savefig("sampling_compare.png", dpi=120)
plt.close(fig)
print("💾 Saved sampling_compare.png")


# 4. Which strategy best preserves average edgeweight? #######################
#
# What makes one sample "better"? It tracks the true population most
# closely. We score that as the *maximum absolute deviation*: over the
# whole time series, the largest gap between the sample's average edge
# weight and the population's. Smaller = better. (Worst-case gap is a
# simple, strict choice; you could instead use mean-squared error or
# correlation if you cared about average rather than worst-case fit.)

def max_abs_dev(sample_stats):
    merged = stats[["date_time", "avg_edgeweight"]].merge(
        sample_stats[["date_time", "avg_edgeweight"]],
        on="date_time", suffixes=("_pop", "_samp"))
    return float((merged["avg_edgeweight_pop"]
                  - merged["avg_edgeweight_samp"]).abs().max())

mad = {
    "ego_centric":     max_abs_dev(ego_stats),
    "edgewise":        max_abs_dev(edge_stats),
    "spatial_buffer":  max_abs_dev(buf_stats),
}
print("Max |population - sample| in avg_edgeweight by strategy:")
for k, v in mad.items():
    print(f"  {k:16s}: {v:.3f}")

winner = min(mad, key=mad.get)
print(f"📊 Best preservation (smallest max-absolute-deviation): {winner}")

# WHY does the spatial buffer usually win for this network? Evacuation flow
# is spatially structured -- neighboring subdivisions surge together -- so a
# geographic buffer captures a coherent, internally-intact subnetwork whose
# per-node averages track the population. Ego and edgewise sampling slice
# the graph arbitrarily, fragmenting that local structure.


# 5. Learning Check ##########################################################
#
# QUESTION: Of the three sampling strategies above (ego-centric,
# edgewise, spatial buffer around Miami), which one best preserves
# the population's `avg_edgeweight` time series — measured by the
# smallest max-absolute-deviation? Submit the strategy name.

print(f"\n📝 Learning Check answer: {winner}")

print("\n🎉 Done. Move on to the case study report when you're ready.")
```

---

## `code/11_sampling/functions.R`

```r
#' @name functions.R
#' @title Helpers for the Sampling case study

library(dplyr)
library(sf)
library(here)

.case_dir <- function() here::here("code", "08_sampling", "data")

load_nodes <- function() {
  readr::read_csv(
    file.path(.case_dir(), "nodes.csv"),
    # geoid is a numeric-looking string; keep it as character so
    # comparisons like `geoid == "1208692158"` work.
    col_types = readr::cols(geoid = readr::col_character(),
                            .default = readr::col_guess())
  )
}
load_edges <- function() {
  readr::read_csv(
    file.path(.case_dir(), "edges.csv"),
    show_col_types = FALSE
  )
}
load_subdivisions <- function() {
  sf::st_read(file.path(.case_dir(), "county_subdivisions.geojson"),
              quiet = TRUE)
}

#' Compute normalized network statistics per time slice.
#'
#' Mirrors the workshop helper from 29C_databases.R: edge weight,
#' edge count, node count, # linked nodes, density, % linked, edges
#' per node, average edgeweight per node.
slice_stats <- function(edges, n_total_nodes) {
  edges |>
    group_by(date_time) |>
    summarize(
      edgeweight     = sum(evacuation, na.rm = TRUE),
      n_edges        = dplyr::n(),
      n_nodes        = n_total_nodes,
      n_nodes_linked = length(unique(c(from, to))),
      .groups        = "drop"
    ) |>
    mutate(
      density          = 2 * n_edges / (n_nodes * (n_nodes - 1)),
      pc_nodes_linked  = n_nodes_linked / n_nodes,
      edge_ratio       = n_edges / n_nodes,
      avg_edgeweight   = edgeweight / n_nodes
    )
}
```

---

## `code/11_sampling/functions.py`

```python
"""Helpers for the Sampling case study."""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import geopandas as gpd


def _case_dir() -> Path:
    return Path(__file__).resolve().parent / "data"


def load_nodes() -> pd.DataFrame:
    # geoid is a numeric-looking string ("1208692158"); force string read
    # so equality comparisons against literal "1208692158" succeed.
    return pd.read_csv(_case_dir() / "nodes.csv", dtype={"geoid": "string"})


def load_edges() -> pd.DataFrame:
    # date_time is ISO-8601 in CSV; parse to Timestamps so groupby
    # gives an ordered time series.
    return pd.read_csv(_case_dir() / "edges.csv", parse_dates=["date_time"])


def load_subdivisions() -> gpd.GeoDataFrame:
    return gpd.read_file(_case_dir() / "county_subdivisions.geojson")


def slice_stats(edges: pd.DataFrame, n_total_nodes: int) -> pd.DataFrame:
    """Per-time-slice network statistics, mirrors the sts 29C workshop.

    Columns: edgeweight, n_edges, n_nodes, n_nodes_linked, density,
    pc_nodes_linked, edge_ratio, avg_edgeweight.
    """
    out = (
        edges
        .groupby("date_time", as_index=False)
        .agg(
            edgeweight=("evacuation", "sum"),
            n_edges=("evacuation", "size"),
            from_set=("from", lambda s: set(s)),
            to_set=("to",   lambda s: set(s)),
        )
    )
    out["n_nodes"] = n_total_nodes
    out["n_nodes_linked"] = out.apply(
        lambda r: len(r["from_set"] | r["to_set"]), axis=1)
    out = out.drop(columns=["from_set", "to_set"])
    out["density"] = 2 * out["n_edges"] / (out["n_nodes"] * (out["n_nodes"] - 1))
    out["pc_nodes_linked"] = out["n_nodes_linked"] / out["n_nodes"]
    out["edge_ratio"]      = out["n_edges"]       / out["n_nodes"]
    out["avg_edgeweight"]  = out["edgeweight"]    / out["n_nodes"]
    return out
```

---

## `code/README.md`

# `code/` — Teaching scripts for the eleven case studies

This folder is where the *interactive case studies* on the website become
*real, runnable code*.

Every case study on the [Case Studies page](../docs/case-studies.html) lives
in two places:

1. **An interactive HTML lab** under `docs/case-studies/<name>.html`. You
   click, drag, and toggle through the analysis to build intuition.
2. **A code folder here** under `code/NN_<name>/` containing parallel **R**
   and **Python** scripts that run the *same analysis as plain code*.

The pattern across every case folder is identical, so you can move between
case studies (and between R and Python) without losing your footing.

```
code/NN_<name>/
├── README.md       # the case in 2 minutes — what, why, what you'll submit
├── example.R       # the analysis, in R, with tidyverse + igraph + ggraph
├── example.py      # the analysis, in Python, with pandas + igraph + matplotlib
├── functions.R     # helpers: data loaders, synthetic-network generators, sims
├── functions.py    # the Python counterparts
└── data/           # slim, bundled data files (CSV / Parquet / GeoJSON, < few MB)
```

Both `example.R` and `example.py` use **identical section headers in identical
order**, so if you started a case in one language and want to switch, the
section you were on is in the same place in the other file.

## Which track should I pick?

Pick the one that matches your background and stay on it. **The two tracks are
equal, first-class citizens — not an "original" and a "bolted-on port."** The R
and Python scripts are written line-for-line parallel and compute the *same
Learning Check answers* (see the parity note at the bottom), so neither track is
at any disadvantage for grading. R appears first in some prose only because the
course began in R; the Python track is fully supported. New to both? R +
tidyverse is gentle for non-programmers; Python is the easier landing if you
already write Python or SQL.

## How to install

### R

R packages (run once at the top of the repo):

```r
install.packages(c(
  # core wrangling
  "dplyr", "readr", "tidyr", "purrr", "stringr", "tibble", "here",
  # networks
  "igraph", "tidygraph", "ggraph",
  # viz
  "ggplot2", "viridis", "patchwork", "scales",
  # spatial (case 08 only)
  "sf",
  # case 11 only
  "xgboost", "zoo"
))
```

If your repo uses `renv`, prefer `renv::install(...)` instead of
`install.packages(...)`.

We use the **base pipe `|>`** (not magrittr `%>%`) throughout. We use
`here::here()` to resolve paths. Run any script with:

```bash
Rscript code/NN_<name>/example.R
```

### Python

Python deps (run once):

```bash
pip install -r code/requirements.txt
```

Run any script with:

```bash
python code/NN_<name>/example.py
```

## The case studies

Each row pairs an interactive lab with its code folder. The lab is for
exploring; the code folder is for *doing the same thing on your own data*.

| #  | Case study               | Skill    | Lab                                                         | Code folder                                  |
|----|--------------------------|----------|-------------------------------------------------------------|----------------------------------------------|
| 01 | Build a Network          | Identify | [lab](../docs/case-studies/build-a-network.html)            | [`01_build-a-network`](01_build-a-network/)  |
| 02 | Network Joins            | Identify | [lab](../docs/case-studies/joins.html)                      | [`02_joins`](02_joins/)                      |
| 03 | Aggregation              | Identify | [lab](../docs/case-studies/aggregation.html)                | [`03_aggregation`](03_aggregation/)          |
| 04 | Centrality & Criticality | Measure  | [lab](../docs/case-studies/centrality.html)                 | [`04_centrality`](04_centrality/)            |
| 05 | Supply Chain Resilience  | Measure  | [lab](../docs/case-studies/supply-chain.html)               | [`05_supply-chain`](05_supply-chain/)        |
| 06 | DSM Clustering           | Measure  | [lab](../docs/case-studies/dsm-clustering.html)             | [`06_dsm-clustering`](06_dsm-clustering/)    |
| 07 | Network Permutation      | Infer    | [lab](../docs/case-studies/permutation.html)                | [`07_permutation`](07_permutation/)          |
| 08 | Sampling Big Networks    | Identify | [lab](../docs/case-studies/sampling.html)                   | [`08_sampling`](08_sampling/)                |
| 09 | Counterfactual MC        | Predict  | [lab](../docs/case-studies/counterfactual.html)             | [`09_counterfactual`](09_counterfactual/)    |
| 10 | GNN by Hand              | Predict  | [lab](../docs/case-studies/gnn-by-hand.html)                | [`10_gnn-by-hand`](10_gnn-by-hand/)          |
| 11 | GNN + XGBoost            | Predict  | [lab](../docs/case-studies/gnn-xgboost.html)                | [`11_gnn-xgboost`](11_gnn-xgboost/)          |

## What you submit (the short version)

Every week of the course, by Monday at 9 a.m. you submit:

1. The **sketchpad** assignments for that week.
2. The **case study learning checks** for the *previous* week's case studies.
3. The **code learning checks** for the *previous* week's `example.R` /
   `example.py` (one per case study completed).
4. The **project code + report** for whichever case study you are using as
   *your* project case study that week.

See the [Assignments page](../docs/assignments.html) for full details.

## A note on R and Python parity

We try to keep the two scripts as close as possible:

- Same section headers, in the same order.
- Same intermediate variables (so a student following along in either
  language can sanity-check against the other).
- Same Learning Check numeric answer.

The two GNN cases are the one place R has no mature native library, so the
R scripts borrow the course's numpy code through `reticulate` — doing
everything else (loading, wrangling, XGBoost, plotting) natively in R. The
pattern follows `dsai/07_rag/05_embed.R`: reticulate is a surgical bridge
for the one Python-only capability, not a wholesale rewrite.

- **GNN-by-hand (case 10)**: `example.R` drives the same numpy GCN
  functions (`functions.py`: `adjacency`, `normalize`, `gcn_layer`) via
  `reticulate`, so the forward pass — and the Learning Check — are
  **byte-identical** to `example.py`.
- **GNN + XGBoost (case 11)**: R now runs the full pipeline. Only the GNN
  embedding (the one step with no R library) is computed in numpy via
  `reticulate`; the lag feature, the train/test split, **XGBoost**, and the
  AUC scoring are all native R. The R Learning Check asks the same question
  as Python (full-model AUC); because R trains with its own `xgboost`, the
  value can differ from Python's in the last digits.

Everything else is parallel.

---

## `data/projects/README.md`

# Project datasets

Larger, project-grade synthetic networks for SYSEN 5470 **project case studies**.
Each is bigger and richer than the lab datasets (100–500+ nodes), uniformly
documented, and ready to load in R, Python, or the in-browser playgrounds.

Each dataset folder contains:

| File | What it is |
|---|---|
| `nodes.csv` | The node list (one row per node; a `kind` column when the graph is bipartite/multimodal). |
| `edges.csv` | The edge list (`from`/`to` + weight columns; a `day`/`hour`/`period` column when temporal). |
| `*.csv` (extra) | Optional lookup tables (e.g. `zones.csv`). |
| `README.md` | At-a-glance facts + a **codebook** table for every file. |
| `load.R` / `load.py` | Lightweight loaders that build an `igraph` (R) / `networkx`-or-`igraph` (Python) object. |
| `_generate.py` | The deterministic generator (run it to reproduce the CSVs). |

## Available datasets

| Dataset | Nodes | Edges | Directed | Weighted | Bipartite | Temporal | One-line |
|---|---:|---:|:--:|:--:|:--:|:--:|---|
| [`amazon-last-mile`](amazon-last-mile/) | 313 | 2,142 | ✓ | ✓ | — | ✓ | A week of package flow: hubs → stations → delivery zones. |
| [`uber-manhattan`](uber-manhattan/) | 370 | 3,000 | — | ✓ | ✓ | ✓ | A day of driver↔rider ride-matching across downtown Manhattan. |
| [`semiconductor-supply`](semiconductor-supply/) | 368 | 739 | ✓ | ✓ | — | — | Multi-tier global chip supply chain, raw materials → products. |
| [`aerospace-components`](aerospace-components/) | 300 | 777 | ✓ | ✓ | — | — | An aircraft's bill-of-materials + supplier network. |
| [`mutualaid-quake`](mutualaid-quake/) | 250 | 2,935 | ✓ | ✓ | — | ✓ | Neighborhood mutual aid before / during / after an earthquake. |
| [`financial-contagion`](financial-contagion/) | 220 | 1,701 | ✓ | ✓ | — | ✓ | Interbank exposure network across a financial crisis. |
| [`airline-delays`](airline-delays/) | 200 | 2,244 | ✓ | ✓ | — | ✓ | Domestic route network with delay propagation over a day. |
| [`power-grid`](power-grid/) | 300 | 422 | — | ✓ | — | — | A regional electrical transmission grid. |
| [`campus-contact`](campus-contact/) | 300 | 3,699 | — | ✓ | — | ✓ | Campus face-to-face contact network during an outbreak. |
| [`opensource-deps`](opensource-deps/) | 400 | 2,251 | ✓ | ✓ | — | — | An open-source package dependency graph. |
| [`trade-commodity`](trade-commodity/) | 140 | 1,210 | ✓ | ✓ | — | ✓ | International commodity trade across a supply shock. |
| [`reorg-comms`](reorg-comms/) | 250 | 7,926 | ✓ | ✓ | — | ✓ | Corporate communication before / during / after a reorg + layoff. |
| [`satellite-constellation`](satellite-constellation/) | 298 | 733 | — | ✓ | — | — | Multi-operator LEO satellite comms: orbits, inter-satellite links, ground stations. |
| [`drone-components`](drone-components/) | 183 | 617 | ✓ | ✓ | — | — | A drone's functional component + software dependency graph (what needs what to fly). |
| [`transit-multimodal`](transit-multimodal/) | 152 | 384 | — | ✓ | — | — | A city's bus + metro network with neighborhood nodes (hub-spoke + ring). |
| [`satellite-supply-chain`](satellite-supply-chain/) | 276 | 562 | ✓ | ✓ | — | — | Multi-tier satellite manufacturing supply chain, materials → subsystems → programs. |
| [`aircraft-supply-chain`](aircraft-supply-chain/) | 300 | 624 | ✓ | ✓ | — | — | Multi-tier commercial-aircraft supply chain, materials → systems → programs. |
| [`ups-ground-network`](ups-ground-network/) | 149 | 347 | ✓ | ✓ | — | — | UPS-style truck line-haul: plant→plant lanes (packages, trucks, distance, transit time). |
| [`ups-package-flow`](ups-package-flow/) | 149 | 5,200 | ✓ | ✓ | — | — | Package-level companion: one edge per parcel (service, weight, distance, on-time). |
| [`nyc-realestate-capital`](nyc-realestate-capital/) | 270 | 5,044 | ✓ | ✓ | ✓ | ✓ | NYC CRE capital flows: typed investors + banks → properties, quarterly invested vs pledged. |
| [`nyc-realestate-portfolio`](nyc-realestate-portfolio/) | 190 | 1,155 | — | ✓ | — | — | NYC properties linked by shared equity financing (companion projection of the capital network). |

All 21 are larger than the lab datasets, mostly weighted, and several are temporal
(`period`/`day`/`hour`/`week` columns), bipartite, or multimodal (`kind`/`mode`
columns). `satellite-constellation` and `transit-multimodal` are multi-layer (link
type / transit mode); `transit-multimodal` is purpose-built for counterfactual
"add-one-edge" connectivity analysis.

## Previews

Node colors encode a categorical attribute (kind / operator / subsystem /
district / region); layouts use real coordinates where the data has them,
otherwise a force-directed layout. Click a thumbnail for its dataset.

|   |   |   |
|---|---|---|
| <a href="amazon-last-mile/"><img src="amazon-last-mile/thumb.png" width="260" alt="amazon-last-mile"><br>amazon-last-mile</a> | <a href="uber-manhattan/"><img src="uber-manhattan/thumb.png" width="260" alt="uber-manhattan"><br>uber-manhattan</a> | <a href="semiconductor-supply/"><img src="semiconductor-supply/thumb.png" width="260" alt="semiconductor-supply"><br>semiconductor-supply</a> |
| <a href="aerospace-components/"><img src="aerospace-components/thumb.png" width="260" alt="aerospace-components"><br>aerospace-components</a> | <a href="mutualaid-quake/"><img src="mutualaid-quake/thumb.png" width="260" alt="mutualaid-quake"><br>mutualaid-quake</a> | <a href="financial-contagion/"><img src="financial-contagion/thumb.png" width="260" alt="financial-contagion"><br>financial-contagion</a> |
| <a href="airline-delays/"><img src="airline-delays/thumb.png" width="260" alt="airline-delays"><br>airline-delays</a> | <a href="power-grid/"><img src="power-grid/thumb.png" width="260" alt="power-grid"><br>power-grid</a> | <a href="campus-contact/"><img src="campus-contact/thumb.png" width="260" alt="campus-contact"><br>campus-contact</a> |
| <a href="opensource-deps/"><img src="opensource-deps/thumb.png" width="260" alt="opensource-deps"><br>opensource-deps</a> | <a href="trade-commodity/"><img src="trade-commodity/thumb.png" width="260" alt="trade-commodity"><br>trade-commodity</a> | <a href="reorg-comms/"><img src="reorg-comms/thumb.png" width="260" alt="reorg-comms"><br>reorg-comms</a> |
| <a href="satellite-constellation/"><img src="satellite-constellation/thumb.png" width="260" alt="satellite-constellation"><br>satellite-constellation</a> | <a href="drone-components/"><img src="drone-components/thumb.png" width="260" alt="drone-components"><br>drone-components</a> | <a href="transit-multimodal/"><img src="transit-multimodal/thumb.png" width="260" alt="transit-multimodal"><br>transit-multimodal</a> |
| <a href="satellite-supply-chain/"><img src="satellite-supply-chain/thumb.png" width="260" alt="satellite-supply-chain"><br>satellite-supply-chain</a> | <a href="aircraft-supply-chain/"><img src="aircraft-supply-chain/thumb.png" width="260" alt="aircraft-supply-chain"><br>aircraft-supply-chain</a> | <a href="ups-ground-network/"><img src="ups-ground-network/thumb.png" width="260" alt="ups-ground-network"><br>ups-ground-network</a> |
| <a href="ups-package-flow/"><img src="ups-package-flow/thumb.png" width="260" alt="ups-package-flow"><br>ups-package-flow</a> | <a href="nyc-realestate-capital/"><img src="nyc-realestate-capital/thumb.png" width="260" alt="nyc-realestate-capital"><br>nyc-realestate-capital</a> | <a href="nyc-realestate-portfolio/"><img src="nyc-realestate-portfolio/thumb.png" width="260" alt="nyc-realestate-portfolio"><br>nyc-realestate-portfolio</a> |

## How to use them

**In R**

```bash
Rscript data/projects/amazon-last-mile/load.R
```

```r
source("data/projects/amazon-last-mile/load.R")
g <- load_amazon()      # a directed, weighted igraph object
```

**In Python**

```bash
python data/projects/amazon-last-mile/load.py
```

```python
import sys; sys.path.insert(0, "data/projects/amazon-last-mile")
from load import load_amazon
g = load_amazon()       # a directed, weighted python-igraph object
```

**In the browser playground** — open the
[R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground and pick
the dataset from the **▾ Load sample** menu (under *Project datasets*).

## A note on the data

Every dataset is **synthetic but not random**. Each has planted, realistic
structure — usually *several* overlapping patterns — that reward genuine analysis.
The patterns are intentionally undocumented: finding and explaining them is the
project. "Bigger places have more activity" is where you start, not where you stop.

## Reproducing / contributing

Each `_generate.py` is deterministic (fixed seed). After regenerating any dataset,
mirror the CSVs into the playground's served folder:

```bash
python data/projects/<name>/_generate.py
python data/projects/_sync_to_playground.py
```

The authoring standard (folder layout, README + codebook format, loader
templates, and the "planted story" design rules) lives in the
`netsci-dataset-builder` skill under `.claude/skills/`.

---

## `data/projects/_make_thumbnails.py`

```python
"""Render a distinct ICON thumbnail (thumb.png) for each project dataset.

Each dataset gets a recognizable emoji icon (a satellite for the satellite
network, a drone for the drone network, ...) centered on the course's dark-green
tile with the dataset name beneath it. Far more legible at thumbnail size than a
node-link hairball. Deterministic and self-contained (Pillow + NotoColorEmoji).

Run after adding a dataset (add it to ICONS below):
    python data/projects/_make_thumbnails.py
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PROJECTS = Path(__file__).resolve().parent

# course palette
BG = (10, 31, 18, 255)        # #0a1f12 card bg
BORDER = (57, 255, 20, 255)   # #39FF14 neon green
LABEL = (209, 250, 229, 255)  # #d1fae5 mint

SIZE = 320
EMOJI_PX = 168
EMOJI_FONT = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
LABEL_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# one recognizable, distinct emoji per dataset
ICONS = {
    "amazon-last-mile":        "🚚",
    "uber-manhattan":          "🚕",
    "semiconductor-supply":    "🖥️",
    "aerospace-components":     "✈️",
    "mutualaid-quake":         "🤝",
    "financial-contagion":     "📉",
    "airline-delays":          "🛫",
    "power-grid":              "⚡",
    "campus-contact":          "🦠",
    "opensource-deps":         "🧩",
    "trade-commodity":         "🌐",
    "reorg-comms":             "💬",
    "satellite-constellation": "🛰️",
    "drone-components":        "🚁",
    "transit-multimodal":      "🚇",
    "satellite-supply-chain":  "📡",
    "aircraft-supply-chain":   "🛩️",
    "ups-ground-network":      "🚛",
    "ups-package-flow":        "📦",
    "nyc-realestate-capital":  "🏙️",
    "nyc-realestate-portfolio": "🏢",
}


def _emoji_font() -> ImageFont.FreeTypeFont:
    # NotoColorEmoji is a bitmap-strike font: only specific sizes load.
    for s in (109, 136, 128):
        try:
            return ImageFont.truetype(EMOJI_FONT, s)
        except OSError:
            continue
    raise OSError("could not load NotoColorEmoji at any known strike size")


def _render_emoji(ch: str, font: ImageFont.FreeTypeFont) -> Image.Image:
    """Render one emoji glyph to a tight RGBA image, scaled to EMOJI_PX."""
    tmp = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    d.text((80, 80), ch, font=font, anchor="mm", embedded_color=True)
    bbox = tmp.getbbox() or (0, 0, 160, 160)
    glyph = tmp.crop(bbox)
    w, h = glyph.size
    scale = EMOJI_PX / max(w, h)
    return glyph.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)


def _make(name: str, ch: str, font: ImageFont.FreeTypeFont, label_font) -> None:
    tile = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    d.rounded_rectangle([4, 4, SIZE - 5, SIZE - 5], radius=28, fill=BG,
                        outline=BORDER, width=3)
    glyph = _render_emoji(ch, font)
    gx = (SIZE - glyph.width) // 2
    tile.alpha_composite(glyph, (gx, 56))
    d.text((SIZE // 2, 268), name, font=label_font, anchor="mm", fill=LABEL)
    tile.convert("RGB").save(PROJECTS / name / "thumb.png")
    print(f"  {name}/thumb.png  {ch}")


def main() -> None:
    font = _emoji_font()
    label_font = ImageFont.truetype(LABEL_FONT, 19)
    for name, ch in ICONS.items():
        if (PROJECTS / name).is_dir():
            _make(name, ch, font, label_font)


if __name__ == "__main__":
    main()
```

---

## `data/projects/_sync_to_playground.py`

```python
"""Mirror project-dataset CSVs into the playground's served data folder.

The canonical datasets live in `data/projects/<name>/` (browsable on GitHub).
GitHub Pages only serves `docs/`, so the in-browser playgrounds fetch their
samples from `docs/playground-data/`. This script copies each dataset's CSVs
there with a flat, prefixed name (`<name>-<file>.csv`) matching the existing
`karate-nodes.csv` convention, so `SAMPLE_CONFIGS` in playground-r.html /
playground-py.html can fetch them.

Run after (re)generating any dataset:
    python data/projects/_sync_to_playground.py
"""
from __future__ import annotations

import shutil
from pathlib import Path

PROJECTS = Path(__file__).resolve().parent
DEST = PROJECTS.parent.parent / "docs" / "playground-data"


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    n = 0
    for ds in sorted(p for p in PROJECTS.iterdir() if p.is_dir()):
        for csv in sorted(ds.glob("*.csv")):
            target = DEST / f"{ds.name}-{csv.name}"
            shutil.copyfile(csv, target)
            print(f"  {csv.relative_to(PROJECTS)} -> playground-data/{target.name}")
            n += 1
        thumb = ds / "thumb.png"
        if thumb.exists():
            shutil.copyfile(thumb, DEST / f"{ds.name}-thumb.png")
            n += 1
    print(f"synced {n} file(s) into {DEST}")


if __name__ == "__main__":
    main()
```

---

## `data/projects/aerospace-components/README.md`

# aerospace-components

*The bill-of-materials and supplier network behind one commercial aircraft
program — detail parts and firms roll up through sub-assemblies into major
systems.*

![Preview of the aerospace-components network](thumb.png)

## At a glance

| | |
|---|---|
| **Direction** | Directed (supply / build flow: detail parts & suppliers → final assembly) |
| **Weights** | Weighted (`qty_per_aircraft` — units installed per airframe) |
| **Modality** | Multimodal — 2 node kinds (`part` across BOM tiers 1–4, `supplier`) |
| **Temporal** | No — a single program snapshot |
| **Nodes** | 300 (258 part + 42 supplier) |
| **Edges** | 777 (399 `is_part_of` roll-ups + 378 `supplies`) |
| **Files** | `nodes.csv`, `edges.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

"Program X" is a stylized commercial-aircraft bill of materials. There are two
kinds of node:

- **`part`** — components and assemblies, with a `tier` giving BOM depth:
  tier 1 = major system assemblies, tier 2 = sub-assemblies, tier 3 = components,
  tier 4 = detail parts (fasteners, seals, fittings, bushings);
- **`supplier`** — firms that make or provide parts.

Edges are directed and point *up the build* toward the final airframe:

- `supplies` — a firm supplies a part (`supplier → part`);
- `is_part_of` — a deeper part rolls up into the assembly above it
  (`child part → parent part`).

Each edge carries `qty_per_aircraft` (the install quantity, an edge weight).
Parts carry a `system` (engine, avionics, fuselage, landing_gear, hydraulics,
interior), a `safety_critical` flag, a `single_source` flag, a `defect_rate`, and
a `cert_level`. Suppliers carry a `supplier_region` and a `defect_rate`.

This is a dependency-and-risk network. It rewards students who trace
dependencies *through* the BOM rather than counting connections. Some questions
to chew on:

- Which node, if it failed, would ground the most safety-critical assemblies?
  Would degree point you to it, or do you need to trace the build paths and run a
  knock-out / criticality analysis? Are the biggest suppliers the riskiest ones?
- Some safety-critical parts look dual-sourced. Are they *actually* redundant, or
  does the apparent redundancy collapse a hop or two upstream?
- Are defect rates spread evenly, or do they cluster — and if they cluster, by
  what (tier, system, region, a particular broker)? Does the pattern survive
  controlling for tier?
- Where does the heaviest certification burden sit, and is that the same place as
  the program's structural weak point?

> **Note.** The interesting findings here are deliberately *not* documented. "Deep
> parts have more parents" is the starting point, not a finding. Push past it —
> degree and a single sourcing column will both mislead you.

## `nodes.csv`

One row per node. Supplier rows leave the part-only columns (`tier`, `system`,
`cert_level`) blank; part rows leave `supplier_region` blank.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique key. `A1##`/`A2###` assembly parts, `C3###`/`C4###` components & detail parts, `S###` suppliers. Referenced by edges. | character | `A117`, `A2014`, `C4004`, `S031` |
| `kind` | Node kind | Whether the node is a part or a supplier firm. | character | `part`, `supplier` |
| `tier` | BOM tier | Build depth for parts: 1 = major assembly … 4 = detail part. Blank for suppliers. | integer | `1`, `3`, `4` |
| `system` | Aircraft system | Which system the part belongs to (blank for suppliers). | character | `engine`, `hydraulics`, `avionics` |
| `safety_critical` | Safety-critical flag | 1 if failure of this part is flight-safety relevant. | integer | `0`, `1` |
| `single_source` | Single-source flag | 1 if the part has only one qualified supplier. | integer | `0`, `1` |
| `supplier_region` | Supplier region | Home region of the supplier firm (blank for parts). | character | `USA`, `Europe`, `Japan`, `Mexico`, `China`, `India` |
| `defect_rate` | Defect rate | Observed fraction of units rejected / nonconforming. | double | `0.0029`, `0.0271`, `0.0807` |
| `cert_level` | Certification level | Highest certification the part is built to (blank for suppliers). | character | `standard`, `DO-178C`, `AS9100`, `NADCAP` |
| `label` | Display name | Human-readable label. (`name` is avoided — python-igraph reserves it for the ID.) | character | `Hydraulics Major Assy 17`, `Supplier 031 (Europe)` |

## `edges.csv`

One row per supply or roll-up relationship. Directed toward the final assembly.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | Source node ID | The supplier, or the deeper (child) part. | character | `S032`, `C4004` |
| `to_id` | Target node ID | The supplied part, or the parent assembly it rolls into. | character | `A2037`, `C3083` |
| `qty_per_aircraft` | Quantity per aircraft | Units of `from_id` installed per airframe (the edge weight). | integer | `10`, `22`, `120` |
| `relation` | Relation type | `supplies` (firm → part) or `is_part_of` (child part → parent). | character | `supplies`, `is_part_of` |

## Load it

```bash
Rscript data/projects/aerospace-components/load.R     # R    (igraph)
python  data/projects/aerospace-components/load.py     # Python (python-igraph)
```

Both build a directed, weighted `igraph` graph and print a one-screen summary. In
the [R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**aerospace-components** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/aerospace-components>

---

## `data/projects/aerospace-components/_generate.py`

```python
"""Generate the `aerospace-components` project network (deterministic).

A bill-of-materials + supplier network for one commercial aircraft program.
Two node kinds:
  - part      components and assemblies, with a tier 1..4 BOM depth
              (1 = final-assembly-level, 4 = small detail parts/fasteners/seals)
  - supplier  firms that make / provide parts

Edges are directed `supplies` / `is-part-of` relations pointing UP the build
toward the final assembly:
  - supplier -> part   (a firm supplies a part)
  - part(child, deeper tier) -> part(parent, shallower tier)  (sub-assembly
    rolls up into its parent assembly)
The edge weight is `qty_per_aircraft` (units installed per airframe).

Node attributes: kind, tier, system, safety_critical, single_source,
supplier_region, defect_rate, cert_level, label.

Design parameters (the only record of the planted structure):
  - NAIL_SUPPLIER: a tiny tier-3/4 fastener/seal supplier sits on the build path
    of MULTIPLE safety-critical assemblies. Low degree, high betweenness, and
    single_source -- the "for want of a nail" hidden critical path.
  - FAKE_DUAL: a safety-critical part has TWO apparent direct suppliers, but
    BOTH draw their key sub-part from the SAME upstream sub-supplier, so the
    redundancy is an illusion (visible only 2 hops up).
  - COUNTERFEIT_BROKER: parts sourced through one broker/region carry an
    elevated defect_rate and fan out across several systems.
  - CERT_ON_PATH: high cert_level concentrates on the critical (nail) path.

Run:
    python data/projects/aerospace-components/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

SYSTEMS = ["engine", "avionics", "fuselage", "landing_gear", "hydraulics", "interior"]
REGIONS = ["USA", "Europe", "Japan", "Mexico", "China", "India"]
CERTS = ["standard", "DO-178C", "AS9100", "NADCAP"]

# BOM shape: counts of parts per tier (tier1 shallow .. tier4 deep)
N_T1 = 18     # major assemblies (one+ per system)
N_T2 = 60     # sub-assemblies
N_T3 = 110    # components
N_T4 = 70     # detail parts (fasteners, seals, fittings)
N_SUPPLIERS = 42

# --- planted parameters -----------------------------------------------------
COUNTERFEIT_REGION = "China"     # broker region with elevated defect rate
COUNTERFEIT_BROKER_EXTRA = 0.045  # added mean defect_rate for broker parts
BASE_DEFECT = 0.012
CERT_PATH_BONUS = 2              # cert-level steps added on the critical path
N_SAFETY_VIA_NAIL = 7           # how many safety-critical assemblies the nail feeds


def main() -> None:
    rng = np.random.default_rng(SEED)

    rows = []   # node rows

    # ----- tier-1 major assemblies (one per system, then extras) -----------
    t1 = []
    for i in range(N_T1):
        sysn = SYSTEMS[i % len(SYSTEMS)]
        pid = f"A1{i+1:02d}"
        t1.append(pid)
        rows.append({"node_id": pid, "kind": "part", "tier": 1, "system": sysn,
                     "safety_critical": int(sysn in ("engine", "landing_gear", "hydraulics")),
                     "single_source": 0, "supplier_region": pd.NA,
                     "defect_rate": pd.NA, "cert_level": pd.NA,
                     "label": f"{sysn.title()} Major Assy {i+1:02d}"})

    # ----- tier-2 sub-assemblies -------------------------------------------
    t2 = []
    for i in range(N_T2):
        sysn = SYSTEMS[rng.integers(0, len(SYSTEMS))]
        pid = f"A2{i+1:03d}"
        t2.append(pid)
        rows.append({"node_id": pid, "kind": "part", "tier": 2, "system": sysn,
                     "safety_critical": int(rng.random() < 0.35 and
                                            sysn in ("engine", "landing_gear", "hydraulics", "avionics")),
                     "single_source": 0, "supplier_region": pd.NA,
                     "defect_rate": pd.NA, "cert_level": pd.NA,
                     "label": f"{sysn.title()} Sub-Assy {i+1:03d}"})

    # ----- tier-3 components ------------------------------------------------
    t3 = []
    for i in range(N_T3):
        sysn = SYSTEMS[rng.integers(0, len(SYSTEMS))]
        pid = f"C3{i+1:03d}"
        t3.append(pid)
        rows.append({"node_id": pid, "kind": "part", "tier": 3, "system": sysn,
                     "safety_critical": int(rng.random() < 0.25),
                     "single_source": 0, "supplier_region": pd.NA,
                     "defect_rate": pd.NA, "cert_level": pd.NA,
                     "label": f"{sysn.title()} Component {i+1:03d}"})

    # ----- tier-4 detail parts (fasteners, seals, fittings) ----------------
    t4 = []
    detail_kinds = ["fastener", "seal", "fitting", "bushing", "o_ring", "bolt", "rivet"]
    for i in range(N_T4):
        sysn = SYSTEMS[rng.integers(0, len(SYSTEMS))]
        pid = f"C4{i+1:03d}"
        t4.append(pid)
        dk = detail_kinds[i % len(detail_kinds)]
        rows.append({"node_id": pid, "kind": "part", "tier": 4, "system": sysn,
                     "safety_critical": int(rng.random() < 0.15),
                     "single_source": int(rng.random() < 0.45),
                     "supplier_region": pd.NA, "defect_rate": pd.NA,
                     "cert_level": pd.NA, "label": f"{dk.title()} {i+1:03d}"})

    # ----- suppliers --------------------------------------------------------
    sup = []
    for i in range(N_SUPPLIERS):
        reg = rng.choice(REGIONS, p=np.array([0.34, 0.26, 0.12, 0.12, 0.10, 0.06]))
        sid = f"S{i+1:03d}"
        sup.append(sid)
        rows.append({"node_id": sid, "kind": "supplier", "tier": pd.NA,
                     "system": pd.NA, "safety_critical": 0,
                     "single_source": 0, "supplier_region": reg,
                     "defect_rate": pd.NA, "cert_level": pd.NA,
                     "label": f"Supplier {i+1:03d} ({reg})"})

    nodes = pd.DataFrame(rows)
    region_of = dict(zip(nodes.node_id, nodes.supplier_region))
    sysd = dict(zip(nodes.node_id, nodes.system))
    sc = dict(zip(nodes.node_id, nodes.safety_critical))

    eds = []

    def add_edge(frm, to, qty, rel):
        eds.append({"from_id": frm, "to_id": to,
                    "qty_per_aircraft": int(max(qty, 1)), "relation": rel})

    # ---- BOM roll-up: deeper tier -> shallower tier -----------------------
    # each tier-2 rolls into 1 tier-1 (prefer same system)
    for p in t2:
        parents = [a for a in t1 if sysd[a] == sysd[p]] or t1
        add_edge(p, rng.choice(parents), rng.integers(1, 6), "is_part_of")
    # each tier-3 rolls into 1-2 tier-2
    for p in t3:
        cand = [a for a in t2 if sysd[a] == sysd[p]] or t2
        for par in rng.choice(cand, size=int(rng.integers(1, 3)), replace=False):
            add_edge(p, par, rng.integers(1, 12), "is_part_of")
    # each tier-4 rolls into 1-3 tier-3
    for p in t4:
        cand = [a for a in t3 if sysd[a] == sysd[p]] or t3
        for par in rng.choice(cand, size=int(rng.integers(1, 4)), replace=False):
            add_edge(p, par, rng.integers(2, 40), "is_part_of")

    # reserve the four planted suppliers so the default wiring never touches
    # them (keeps the nail tiny and the fake-dual pair clean).
    nail_supplier = sup[0]
    sup_a, sup_b, shared_subsupplier = sup[1], sup[2], sup[3]
    reserved = {nail_supplier, sup_a, sup_b, shared_subsupplier}
    open_sup = [s for s in sup if s not in reserved]
    # the nail supplier is deliberately NOT in the broker region (keep stories
    # separable); give it an ordinary region.
    nodes.loc[nodes.node_id == nail_supplier, "supplier_region"] = "USA"
    region_of[nail_supplier] = "USA"

    # ---- suppliers -> parts (who makes what) ------------------------------
    # default: each non-trivial part has 1-2 suppliers (dual-source common)
    part_ids = t1 + t2 + t3 + t4
    supplied_by = {}
    for p in part_ids:
        n_sup = 1 if rng.random() < 0.5 else 2
        chosen = list(rng.choice(open_sup, size=n_sup, replace=False))
        supplied_by[p] = chosen
        for s in chosen:
            add_edge(s, p, rng.integers(1, 20), "supplies")

    # =========================================================================
    # PLANTED (a): the "nail" -- a tiny tier-4 supplier on many critical paths
    # =========================================================================
    # pick a small tier-4 seal/fastener part and make ONE supplier its sole
    # source; that part rolls up into several safety-critical assemblies.
    nail_part = t4[3]                         # a single detail part
    nodes.loc[nodes.node_id == nail_part, "single_source"] = 1
    # the nail supplier ONLY makes the nail part (low degree). Clear any prior
    # suppliers of the nail part, then set the sole source.
    eds = [e for e in eds if not (e["relation"] == "supplies" and e["to_id"] == nail_part)]
    add_edge(nail_supplier, nail_part, 120, "supplies")
    supplied_by[nail_part] = [nail_supplier]
    # route the nail part up into N safety-critical tier-3 components that each
    # belong to a DIFFERENT safety-critical assembly chain
    # ensure targets are (or become) safety_critical and roll into sc tier-2/1
    targets = list(rng.choice(t3, size=N_SAFETY_VIA_NAIL, replace=False))
    for c in targets:
        nodes.loc[nodes.node_id == c, "safety_critical"] = 1
        add_edge(nail_part, c, rng.integers(8, 30), "is_part_of")
        # make sure c rolls into a safety-critical tier-2 -> tier-1 path
        par2 = rng.choice(t2)
        nodes.loc[nodes.node_id == par2, "safety_critical"] = 1
        add_edge(c, par2, rng.integers(1, 6), "is_part_of")
        par1 = rng.choice(t1)
        nodes.loc[nodes.node_id == par1, "safety_critical"] = 1
        add_edge(par2, par1, rng.integers(1, 4), "is_part_of")

    # =========================================================================
    # PLANTED (b): fake dual-sourcing -- a safety-critical part with two
    # apparent suppliers that BOTH depend on the same upstream sub-supplier.
    # =========================================================================
    dual_part = t2[5]
    nodes.loc[nodes.node_id == dual_part, "safety_critical"] = 1
    # clear any existing suppliers of dual_part, set exactly two (sup_a, sup_b
    # were reserved above)
    eds = [e for e in eds if not (e["relation"] == "supplies" and e["to_id"] == dual_part)]
    add_edge(sup_a, dual_part, 4, "supplies")
    add_edge(sup_b, dual_part, 4, "supplies")
    supplied_by[dual_part] = [sup_a, sup_b]
    # both sup_a and sup_b draw a key sub-component from the SAME tier-3 part,
    # which is itself single-sourced from one hidden sub-supplier.
    shared_subpart = t3[7]
    nodes.loc[nodes.node_id == shared_subpart, "single_source"] = 1
    eds = [e for e in eds if not (e["relation"] == "supplies" and e["to_id"] == shared_subpart)]
    add_edge(shared_subsupplier, shared_subpart, 16, "supplies")
    # the shared sub-part feeds parts that sup_a and sup_b make. Represent the
    # supplier dependence as: shared_subpart -> two intermediate parts, each of
    # which is_part_of the dual_part, and each made by sup_a / sup_b.
    int_a, int_b = t3[8], t3[9]
    # sup_a is the sole supplier of int_a, sup_b of int_b: drop any prior
    # suppliers of these two intermediates first, then set the sole sources.
    eds = [e for e in eds if not (e["relation"] == "supplies"
                                  and e["to_id"] in (int_a, int_b))]
    nodes.loc[nodes.node_id.isin([int_a, int_b]), "single_source"] = 1
    add_edge(shared_subpart, int_a, 6, "is_part_of")
    add_edge(shared_subpart, int_b, 6, "is_part_of")
    add_edge(int_a, dual_part, 2, "is_part_of")
    add_edge(int_b, dual_part, 2, "is_part_of")
    add_edge(sup_a, int_a, 3, "supplies")
    add_edge(sup_b, int_b, 3, "supplies")

    # =========================================================================
    # PLANTED (c): counterfeit-risk cluster -- one broker region's parts have
    # elevated defect rates and fan out across several systems.
    # =========================================================================
    broker_suppliers = [s for s in sup if region_of[s] == COUNTERFEIT_REGION]
    if not broker_suppliers:
        broker_suppliers = [sup[-1]]
        nodes.loc[nodes.node_id == sup[-1], "supplier_region"] = COUNTERFEIT_REGION
        region_of[sup[-1]] = COUNTERFEIT_REGION

    # ---- assign defect_rate & cert_level to PARTS -------------------------
    # a part's defect_rate reflects (mainly) its supplier region + part tier +
    # noise. Parts sourced from the broker region carry the planted bump.
    edge_df = pd.DataFrame(eds)
    sup_edges = edge_df[edge_df.relation == "supplies"]
    part_to_sups = sup_edges.groupby("to_id")["from_id"].apply(list).to_dict()

    for p in part_ids:
        srcs = part_to_sups.get(p, [])
        regs = [region_of[s] for s in srcs if pd.notna(region_of.get(s))]
        broker = any(r == COUNTERFEIT_REGION for r in regs)
        tier = int(nodes.loc[nodes.node_id == p, "tier"].iloc[0])
        base = BASE_DEFECT + 0.004 * (tier - 1)
        if broker:
            base += COUNTERFEIT_BROKER_EXTRA
        dr = float(np.clip(base + rng.normal(0, 0.010), 0.001, 0.20))
        nodes.loc[nodes.node_id == p, "defect_rate"] = round(dr, 4)
        # cert level: higher for safety-critical & shallow tiers, plus noise
        base_cert = 0
        if sc.get(p, 0) or nodes.loc[nodes.node_id == p, "safety_critical"].iloc[0]:
            base_cert += 1
        if tier <= 2:
            base_cert += 1
        base_cert += int(rng.random() < 0.3)
        nodes.loc[nodes.node_id == p, "cert_level"] = CERTS[min(base_cert, len(CERTS) - 1)]

    # suppliers carry the mean defect_rate of what they ship (noisy proxy)
    for s in sup:
        myparts = sup_edges[sup_edges.from_id == s]["to_id"].tolist()
        if myparts:
            mdr = nodes.loc[nodes.node_id.isin(myparts), "defect_rate"].astype(float).mean()
            nodes.loc[nodes.node_id == s, "defect_rate"] = round(float(mdr), 4)

    # =========================================================================
    # PLANTED (d): certification bottleneck -- bump cert on the nail path.
    # =========================================================================
    crit_path = {nail_part} | set(targets)
    for c in crit_path:
        cur = nodes.loc[nodes.node_id == c, "cert_level"].iloc[0]
        i0 = CERTS.index(cur) if cur in CERTS else 0
        nodes.loc[nodes.node_id == c, "cert_level"] = CERTS[min(i0 + CERT_PATH_BONUS, len(CERTS) - 1)]

    edges = pd.DataFrame(eds)

    # final column order
    nodes = nodes[["node_id", "kind", "tier", "system", "safety_critical",
                   "single_source", "supplier_region", "defect_rate",
                   "cert_level", "label"]]
    edges = edges[["from_id", "to_id", "qty_per_aircraft", "relation"]]

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)

    kc = nodes.kind.value_counts()
    print(f"aerospace-components: {len(nodes)} nodes "
          f"({kc.get('part',0)} part + {kc.get('supplier',0)} supplier), "
          f"{len(edges)} edges.")


if __name__ == "__main__":
    main()
```

---

## `data/projects/aerospace-components/load.R`

```r
#' @name load.R
#' @title Load the `aerospace-components` project network (R)
#' @description
#'
#' Reads the two CSVs in this folder and builds a directed, weighted igraph
#' object: the bill-of-materials + supplier network for a commercial aircraft
#' program (detail parts & suppliers roll up toward the final assembly). Run it
#' straight (`Rscript load.R`) for a quick summary, or `source()` it and call
#' `load_aero()` in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "aerospace-components")

#' Load the node table (one row per part / supplier).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per supply / roll-up relationship).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Build the directed, weighted graph.
#'
#' Edges are weighted by `qty_per_aircraft` and point up the build toward the
#' final assembly. The `relation` edge attribute is `supplies` (firm -> part) or
#' `is_part_of` (child part -> parent). Trace what depends on a node with
#' `subcomponent(g, v, mode = "out")`, or knock a supplier out to see how many
#' safety-critical assemblies lose their supply.
load_aero <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = TRUE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$qty_per_aircraft
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n✈️  aerospace-components (R)\n")
  cat("   Parts & suppliers roll up toward final assembly; weighted by qty/aircraft.\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_aero(nodes, edges)

  cat(sprintf("✅ Loaded %d nodes (%d parts + %d suppliers) and %d edges.\n",
              nrow(nodes), sum(nodes$kind == "part"),
              sum(nodes$kind == "supplier"), nrow(edges)))
  cat(sprintf("🔗 Directed: %s | safety-critical parts: %d | single-source parts: %d\n",
              is_directed(g), sum(nodes$safety_critical == 1, na.rm = TRUE),
              sum(nodes$single_source == 1, na.rm = TRUE)))
  cat(sprintf("🧩 Relations: %d supplies + %d is_part_of\n",
              sum(edges$relation == "supplies"), sum(edges$relation == "is_part_of")))
  cat("🎉 Graph ready. `g` is a directed, weighted igraph (weight = qty_per_aircraft).\n")
}
```

---

## `data/projects/aerospace-components/load.py`

```python
"""Load the `aerospace-components` project network (Python).

Reads the two CSVs in this folder and builds a directed, weighted python-igraph
object: the bill-of-materials + supplier network for a commercial aircraft
program (detail parts & suppliers roll up toward the final assembly). Run it
straight (``python load.py``) for a quick summary, or import ``load_aero()`` into
your own script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per part / supplier."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per supply / roll-up relationship."""
    return pd.read_csv(HERE / "edges.csv")


def load_aero(nodes: pd.DataFrame | None = None,
              edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the directed, weighted graph (edge weight = ``qty_per_aircraft``).

    Edges point up the build toward the final assembly. The ``relation`` edge
    attribute is ``supplies`` (firm -> part) or ``is_part_of`` (child part ->
    parent). Trace what depends on a node with ``g.subcomponent(v, mode="out")``,
    or delete a supplier to see how many safety-critical assemblies lose supply.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=True, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["qty_per_aircraft"]
    return g


if __name__ == "__main__":
    print("\n✈️  aerospace-components (Python)")
    print("   Parts & suppliers roll up toward final assembly; "
          "weighted by qty/aircraft.\n")

    nodes = load_nodes()
    edges = load_edges()
    g = load_aero(nodes, edges)

    kinds = nodes["kind"].value_counts()
    print(f"✅ Loaded {len(nodes)} nodes "
          f"({kinds.get('part',0)} parts + {kinds.get('supplier',0)} suppliers) "
          f"and {len(edges)} edges.")
    print(f"🔗 Directed: {g.is_directed()} | "
          f"safety-critical parts: {int(nodes['safety_critical'].fillna(0).sum())} | "
          f"single-source parts: {int(nodes['single_source'].fillna(0).sum())}")
    rel = edges["relation"].value_counts()
    print(f"🧩 Relations: {rel.get('supplies',0)} supplies + "
          f"{rel.get('is_part_of',0)} is_part_of")
    print("🎉 Graph ready. Object `g` is a directed, weighted igraph "
          "(weight = qty_per_aircraft).")
```

---

## `data/projects/aircraft-supply-chain/README.md`

# aircraft-supply-chain

*A multi-tier commercial-aircraft supply chain — raw materials flow up through
components and major systems into integrators and finished aircraft programs.*

![Preview of the aircraft-supply-chain network](thumb.png)

## At a glance

| | |
|---|---|
| **Direction** | Directed (supply flow: upstream tier → downstream tier) |
| **Weights** | Weighted (`units_per_year`; paired `value_musd` and `lead_time_days`) |
| **Modality** | Multimodal — 5 node kinds across 5 tiers (`material`, `component`, `system`, `integrator`, `program`) |
| **Temporal** | No — a single annual snapshot |
| **Nodes** | 300 (64 material + 86 component + 58 system + 44 integrator + 48 program) |
| **Edges** | 624 supply relationships |
| **Files** | `nodes.csv`, `edges.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

A stylized model of the commercial-aircraft (airplane) supply chain. Supply flows
from the most upstream tier to the most downstream:

- **tier 4 `material`** — raw materials: titanium, aluminium, CFRP composite,
  nickel superalloy, forgings, fasteners, avionics ICs;
- **tier 3 `component`** — parts / line-replaceable units: turbine blades, FADEC,
  actuators, avionics LRUs, fuel pumps, wiring harnesses, brackets;
- **tier 2 `system`** — major systems / structures: engine, avionics suite,
  flight controls, wing box, fuselage section, landing gear;
- **tier 1 `integrator`** — Tier-1 suppliers / major-section integrators & OEM
  final assembly;
- **tier 0 `program`** — end aircraft programs / fleets (narrowbody, widebody,
  regional jet, freighter, military transport).

Each directed edge is a supply relationship weighted by `units_per_year`
(shipsets / units per year), with a dollar `value_musd` and a `lead_time_days`.
Nodes carry a `region`, a `tier`, a `capacity`, a nominal `lead_time_days`, and a
`subtype`.

This is a flow-and-criticality network. It rewards students who look past which
nodes have the most connections. Some questions to chew on:

- If you could harden one node against disruption, which would it be — and would
  degree, betweenness, or a knockout/criticality analysis give you the same
  answer? Are the busiest suppliers the most important ones?
- Is the chain's resilience the same everywhere, or are some aircraft programs one
  bad day away from having no viable supply path at all?
- Does geography matter? If a region were hit by an export ban or a strike, how
  much downstream output would be cut, and through which tier?
- Recovery is not free: when the system is shocked, which nodes are also the
  slowest to come back?

> **Note.** The interesting findings here are deliberately *not* documented. "Big
> suppliers ship more volume" is the starting point, not a finding. Push past it —
> raw degree will mislead you.

## `nodes.csv`

One row per node (supplier, system, integrator, or program). Every node has every
column populated.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique key. `M###` material, `C###` component, `S###` system, `I###` integrator, `P###` program. Referenced by edges. | character | `M005`, `C027`, `S001`, `I023`, `P009` |
| `kind` | Node kind | Tier role of the node. | character | `material`, `component`, `system`, `integrator`, `program` |
| `tier` | Supply tier | Depth in the chain: 4 = most upstream (material) … 0 = end program. | integer | `4`, `3`, `0` |
| `region` | Region | Where the node operates. | character | `USA`, `Europe`, `Canada`, `Japan`, `Brazil`, `China` |
| `subtype` | Subtype | Kind-specific detail: material class, component type, system type, integrator/program segment. | character | `nickel_superalloy`, `turbine_blade`, `engine`, `narrowbody` |
| `capacity` | Capacity | Nominal annual throughput capacity (relative units). | integer | `2383`, `446`, `163` |
| `lead_time_days` | Lead time | Nominal replenishment / production lead time in days. | integer | `172`, `137`, `104` |
| `label` | Display name | Human-readable label. (`name` is avoided — python-igraph reserves it for the ID.) | character | `Titanium Co 001`, `Engine System 001` |

## `edges.csv`

One row per supply relationship. Directed from the upstream node (`from_id`) to
the downstream node (`to_id`).

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | Upstream node ID | Supplying node (higher tier). | character | `M005`, `C002`, `S014` |
| `to_id` | Downstream node ID | Receiving node (lower tier). | character | `C002`, `S001`, `P009` |
| `units_per_year` | Annual units | Shipsets / units shipped on this relationship per year (the edge weight). | integer | `238`, `82`, `63` |
| `value_musd` | Annual value | Dollar value of the flow, millions USD. | double | `40.611`, `29.573`, `23.543` |
| `lead_time_days` | Edge lead time | Lead time for deliveries on this relationship, days. | integer | `175`, `166`, `78` |

## Load it

```bash
Rscript data/projects/aircraft-supply-chain/load.R     # R    (igraph)
python  data/projects/aircraft-supply-chain/load.py     # Python (python-igraph)
```

Both build a directed, weighted `igraph` graph and print a one-screen summary. In
the [R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**aircraft-supply-chain** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/aircraft-supply-chain>

---

## `data/projects/aircraft-supply-chain/_generate.py`

```python
"""Generate the `aircraft-supply-chain` project network (deterministic).

A multi-tier commercial-aircraft (airplane) manufacturing supply chain spanning
five tiers of nodes:
  - tier 4  material    raw materials (titanium, aluminium, CFRP composite,
                        nickel superalloy, forgings, fasteners, avionics ICs)
  - tier 3  component   parts / line-replaceable units (turbine blades, FADEC,
                        actuators, avionics LRUs, fuel pumps, wiring harnesses)
  - tier 2  system      major systems / structures (engine, avionics suite,
                        flight controls, wing box, fuselage section, landing gear)
  - tier 1  integrator  Tier-1 suppliers / major-section integrators & OEM
                        final assembly
  - tier 0  program     end aircraft programs / fleets (narrowbody, widebody,
                        regional jet, freighter, military transport)

Edges are directed supply flows from upstream (higher tier) to downstream
(lower tier). One row per supply relationship. The edge weight is
`units_per_year` (shipsets / units per year) with a paired `value_musd` and
`lead_time_days`.

Node attributes: kind, tier, region, subtype, capacity, lead_time_days, label.
Regions: USA, Europe, Canada, Japan, Brazil, China.

Design parameters (the only record of the planted structure):
  - HUB_COMPONENT: one USA engine-control unit (FADEC) feeds nearly all
    flight-critical systems (engines, avionics, flight controls). High
    BETWEENNESS but only modest degree -- a genuine single point of failure that
    raw connection-counts miss. Removing it severs most advanced program output.
  - CHOKE_MATERIAL: one nickel-superalloy supplier (tier 4) feeds nearly every
    flight-critical component (turbine blades etc.); a second hidden critical
    node, betweenness >> degree-rank.
  - ADV_REGION: flight-critical systems concentrate in ONE region (USA); a
    regional shock severs many downstream paths.
  - LEADTIME_ON_PATH: the longest lead times cluster ON the critical path (hub
    FADEC, choke superalloy, US flight-critical systems) so the bottleneck is
    also the slowest to recover.
  - COMMODITY decoys: aluminium & fasteners feed almost every standard component
    (highest DEGREE upstream nodes) but are fully substitutable, so they out-rank
    the real choke on degree and hide it.

Run:
    python data/projects/aircraft-supply-chain/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

REGIONS = ["USA", "Europe", "Canada", "Japan", "Brazil", "China"]

# tier population sizes (total ~ 300 nodes)
N_MATERIAL = 64      # tier 4
N_COMPONENT = 86     # tier 3
N_SYSTEM = 58        # tier 2
N_INTEGRATOR = 44    # tier 1
N_PROGRAM = 48       # tier 0

# --- planted parameters -----------------------------------------------------
HUB_SHARE = 0.80          # share of flight-critical system feed via the hub
CHOKE_SHARE = 0.86        # share of flight-critical components the choke feeds
ADV_REGION = "USA"        # where flight-critical systems concentrate
ADV_CONC = 0.80           # share of advanced integrator feed from that region
LEADTIME_PATH_BONUS = 90  # extra lead-time days loaded onto the critical path
NOISE_REGION_FLIP = 0.10  # fraction of nodes whose region is "wrong" (noise)

COMP_ADV = ["turbine_blade", "fadec", "actuator", "avionics_lru", "fuel_pump"]
COMP_STD = ["wiring_harness", "bracket", "skin_panel", "ducting", "bearing"]
SYS_ADV = ["engine", "avionics_suite", "flight_controls"]
SYS_STD = ["wing_box", "fuselage_section", "landing_gear"]


def main() -> None:
    rng = np.random.default_rng(SEED)

    # region sampling weights: airframe world is USA/Europe heavy
    rweights = np.array([0.32, 0.26, 0.10, 0.10, 0.08, 0.14])
    rweights = rweights / rweights.sum()

    def pick_regions(n):
        return rng.choice(REGIONS, size=n, p=rweights)

    rows = []  # node rows

    # ----- tier 4: materials ----------------------------------------------
    mat_kinds = ["titanium", "aluminium", "cfrp_composite", "fastener",
                 "nickel_superalloy", "avionics_ic", "steel_forging", "sealant"]
    mat_region = pick_regions(N_MATERIAL)
    for i in range(N_MATERIAL):
        sub = mat_kinds[i % len(mat_kinds)]
        rows.append({
            "node_id": f"M{i+1:03d}", "kind": "material", "tier": 4,
            "region": mat_region[i], "subtype": sub,
            "capacity": int(rng.integers(200, 4000)),
            "lead_time_days": int(np.clip(rng.normal(90, 24), 21, 200)),
            "label": f"{sub.replace('_',' ').title()} Co {i+1:03d}",
        })

    # ----- tier 3: components ---------------------------------------------
    c_region = pick_regions(N_COMPONENT)
    c_adv = rng.random(N_COMPONENT) < 0.42   # flight-critical parts
    for i in range(N_COMPONENT):
        sub = COMP_ADV[i % len(COMP_ADV)] if c_adv[i] else COMP_STD[i % len(COMP_STD)]
        rows.append({
            "node_id": f"C{i+1:03d}", "kind": "component", "tier": 3,
            "region": c_region[i], "subtype": sub,
            "capacity": int(rng.integers(20, 240) * (2 if c_adv[i] else 1)),
            "lead_time_days": int(np.clip(rng.normal(130, 28), 45, 260)),
            "label": f"{sub.replace('_',' ').title()} Unit {i+1:03d}",
        })

    # ----- tier 2: systems ------------------------------------------------
    s_region = pick_regions(N_SYSTEM)
    s_adv = rng.random(N_SYSTEM) < 0.45      # flight-critical systems
    # advanced systems concentrate in ADV_REGION (~70% relocated there).
    for i in range(N_SYSTEM):
        if s_adv[i] and rng.random() < 0.70:
            s_region[i] = ADV_REGION
    for i in range(N_SYSTEM):
        sub = SYS_ADV[i % len(SYS_ADV)] if s_adv[i] else SYS_STD[i % len(SYS_STD)]
        rows.append({
            "node_id": f"S{i+1:03d}", "kind": "system", "tier": 2,
            "region": s_region[i], "subtype": sub,
            "capacity": int(rng.integers(30, 320)),
            "lead_time_days": int(np.clip(rng.normal(70, 18), 20, 150)),
            "label": f"{sub.replace('_',' ').title()} System {i+1:03d}",
        })

    # ----- tier 1: integrators --------------------------------------------
    i_region = pick_regions(N_INTEGRATOR)
    i_segment = rng.choice(["narrowbody", "widebody", "regional",
                            "business_jet", "cargo"], size=N_INTEGRATOR)
    i_advanced = np.isin(i_segment, ["narrowbody", "widebody", "business_jet"]) \
        & (rng.random(N_INTEGRATOR) < 0.85)
    for i in range(N_INTEGRATOR):
        rows.append({
            "node_id": f"I{i+1:03d}", "kind": "integrator", "tier": 1,
            "region": i_region[i], "subtype": i_segment[i],
            "capacity": int(rng.integers(20, 220)),
            "lead_time_days": int(np.clip(rng.normal(50, 14), 14, 120)),
            "label": f"Integrator {i+1:03d} ({i_segment[i]})",
        })

    # ----- tier 0: programs -----------------------------------------------
    pr_region = pick_regions(N_PROGRAM)
    pr_segment = rng.choice(["narrowbody", "widebody", "regional_jet",
                             "freighter", "military_transport"], size=N_PROGRAM)
    for i in range(N_PROGRAM):
        rows.append({
            "node_id": f"P{i+1:03d}", "kind": "program", "tier": 0,
            "region": pr_region[i], "subtype": pr_segment[i],
            "capacity": int(rng.integers(20, 700)),
            "lead_time_days": int(np.clip(rng.normal(35, 12), 7, 80)),
            "label": f"Program {i+1:03d} ({pr_segment[i]})",
        })

    nodes = pd.DataFrame(rows)

    def ids(kind):
        return nodes.loc[nodes.kind == kind, "node_id"].tolist()
    mat_ids = ids("material")
    comp_ids = ids("component")
    sys_ids = ids("system")
    int_ids = ids("integrator")
    prog_ids = ids("program")
    region_of = dict(zip(nodes.node_id, nodes.region))
    sub_of = dict(zip(nodes.node_id, nodes.subtype))

    adv_comp = [c for c, a in zip(comp_ids, c_adv) if a]
    std_comp = [c for c in comp_ids if c not in set(adv_comp)]
    adv_sys = [s for s, a in zip(sys_ids, s_adv) if a]
    std_sys = [s for s in sys_ids if s not in set(adv_sys)]
    adv_sys_region = [s for s in adv_sys if region_of[s] == ADV_REGION] or adv_sys[:1]

    # ---- planted critical nodes ------------------------------------------
    # HUB_COMPONENT: a USA engine-control unit (FADEC).
    us_fadec = [c for c in adv_comp
                if region_of[c] == "USA" and sub_of[c] == "fadec"]
    HUB_COMPONENT = us_fadec[0] if us_fadec else adv_comp[0]
    # CHOKE_MATERIAL: a nickel-superalloy supplier.
    superalloy_ids = nodes.loc[(nodes.kind == "material") &
                               (nodes.subtype == "nickel_superalloy"), "node_id"].tolist()
    CHOKE_MATERIAL = superalloy_ids[0]

    advanced_integrators = [i for i, a in zip(int_ids, i_advanced) if a]
    adv_int_set = set(advanced_integrators)
    std_integrators = [i for i in int_ids if i not in adv_int_set]

    prog_seg = dict(zip(prog_ids, pr_segment))
    adv_prog = [p for p in prog_ids if prog_seg[p] in
                ("narrowbody", "widebody", "military_transport", "freighter")]
    std_prog = [p for p in prog_ids if p not in set(adv_prog)]

    eds = []  # edge rows

    def add_edge(frm, to, vol, ltd):
        eds.append({
            "from_id": frm, "to_id": to,
            "units_per_year": int(max(vol, 1)),
            "value_musd": round(float(max(vol, 1)) * rng.uniform(0.08, 0.55), 3),
            "lead_time_days": int(ltd),
        })

    def lt_of(n):
        return int(nodes.loc[nodes.node_id == n, "lead_time_days"].iloc[0])

    choke_lt = lt_of(CHOKE_MATERIAL)
    hub_lt = lt_of(HUB_COMPONENT)

    # DECOY commodity materials feeding nearly every standard component: highest
    # DEGREE upstream, but fully substitutable, so removing one cuts almost
    # nothing. They out-rank the real choke on degree and hide it.
    commodity_pool = [m for m in mat_ids
                      if sub_of[m] == "aluminium" and m != CHOKE_MATERIAL]
    COMMODITY = commodity_pool[0]
    commodity2_pool = [m for m in mat_ids if sub_of[m] == "fastener"]
    COMMODITY2 = commodity2_pool[0]

    # ===== FLIGHT-CRITICAL CORRIDOR (the fragile spine) ===================
    # choke superalloy -> flight-critical components (its ONLY upstream input).
    add_edge(CHOKE_MATERIAL, HUB_COMPONENT, int(rng.integers(120, 240)), choke_lt)
    for c in adv_comp:
        if c != HUB_COMPONENT:
            add_edge(CHOKE_MATERIAL, c, int(rng.integers(40, 140)), choke_lt)

    # hub component -> ALL flight-critical systems: sole upstream feeder, hence a
    # genuine cut vertex on every advanced path while touching only a handful of
    # nodes (modest degree). Volume biased toward the US systems.
    for s in adv_sys:
        vol = int(rng.integers(160, 320)) if region_of.get(s) == ADV_REGION \
            else int(rng.integers(30, 100))
        add_edge(HUB_COMPONENT, s, vol, hub_lt)

    # other flight-critical components sell into the STANDARD integrator market
    # (a secondary outlet) -- they do NOT feed advanced systems, giving the
    # advanced corridor no alternative path.
    for c in adv_comp:
        if c != HUB_COMPONENT:
            for it in rng.choice(std_integrators, size=int(rng.integers(1, 3)), replace=False):
                add_edge(c, it, int(rng.integers(15, 80)), lt_of(c))

    # advanced systems -> advanced integrators (concentrated on US houses).
    us_sys = [s for s in adv_sys if region_of.get(s) == ADV_REGION] or adv_sys
    for it in advanced_integrators:
        if rng.random() < ADV_CONC:
            add_edge(rng.choice(us_sys), it, int(rng.integers(70, 260)), lt_of(us_sys[0]))
        else:
            s = rng.choice(adv_sys)
            add_edge(s, it, int(rng.integers(70, 260)), lt_of(s))
    # advanced integrators -> advanced programs
    for p in adv_prog:
        for it in rng.choice(advanced_integrators, size=int(rng.integers(1, 3)), replace=False):
            add_edge(it, p, int(rng.integers(40, 300)), lt_of(it))

    # ===== COMMODITY CORRIDOR (resilient, multi-sourced) ==================
    for c in std_comp:
        add_edge(COMMODITY, c, int(rng.integers(30, 150)), lt_of(COMMODITY))
        if rng.random() < 0.85:
            add_edge(COMMODITY2, c, int(rng.integers(25, 120)), lt_of(COMMODITY2))
        if rng.random() < 0.25:
            add_edge(CHOKE_MATERIAL, c, int(rng.integers(25, 110)), choke_lt)
        excl = (COMMODITY, COMMODITY2, CHOKE_MATERIAL)
        for m in rng.choice([x for x in mat_ids if x not in excl],
                            size=int(rng.integers(2, 5)), replace=False):
            add_edge(m, c, int(rng.integers(5, 80)), lt_of(m))
    # some materials also feed standard systems directly
    for s in std_sys:
        for m in rng.choice([x for x in mat_ids if x != CHOKE_MATERIAL],
                            size=int(rng.integers(1, 3)), replace=False):
            add_edge(m, s, int(rng.integers(5, 60)), lt_of(m))
    # standard components -> standard systems (multi-sourced)
    for s in std_sys:
        for c in rng.choice(std_comp, size=int(rng.integers(2, 4)), replace=False):
            add_edge(c, s, int(rng.integers(18, 120)), lt_of(c))
    # standard systems -> standard integrators
    for it in std_integrators:
        for s in rng.choice(std_sys, size=int(rng.integers(2, 4)), replace=False):
            add_edge(s, it, int(rng.integers(25, 120)), lt_of(s))
    # standard integrators -> standard programs
    for p in std_prog:
        for it in rng.choice(std_integrators, size=int(rng.integers(2, 4)), replace=False):
            add_edge(it, p, int(rng.integers(40, 280)), lt_of(it))

    edges = pd.DataFrame(eds)

    # ---- LEADTIME_ON_PATH: load extra lead time onto the critical path ----
    crit = {HUB_COMPONENT, CHOKE_MATERIAL} | set(adv_sys)
    nodes.loc[nodes.node_id.isin(crit), "lead_time_days"] = (
        nodes.loc[nodes.node_id.isin(crit), "lead_time_days"] + LEADTIME_PATH_BONUS
    ).clip(upper=340)
    edges.loc[edges.from_id.isin(crit), "lead_time_days"] = (
        edges.loc[edges.from_id.isin(crit), "lead_time_days"] + LEADTIME_PATH_BONUS
    ).clip(upper=360)

    # ---- region noise: flip a few regions so region != destiny ------------
    flip = rng.random(len(nodes)) < NOISE_REGION_FLIP
    nodes.loc[flip, "region"] = rng.choice(REGIONS, size=int(flip.sum()))

    nodes = nodes[["node_id", "kind", "tier", "region", "subtype",
                   "capacity", "lead_time_days", "label"]]

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)

    kc = nodes.kind.value_counts()
    print(f"aircraft-supply-chain: {len(nodes)} nodes "
          f"({kc.get('material',0)} material + {kc.get('component',0)} component + "
          f"{kc.get('system',0)} system + {kc.get('integrator',0)} integrator + "
          f"{kc.get('program',0)} program), {len(edges)} edges.")


if __name__ == "__main__":
    main()
```

---

## `data/projects/aircraft-supply-chain/load.R`

```r
#' @name load.R
#' @title Load the `aircraft-supply-chain` project network (R)
#' @description
#'
#' Reads the two CSVs in this folder and builds a directed, weighted igraph
#' object: a multi-tier commercial-aircraft supply chain (materials ->
#' components -> systems -> integrators -> programs). Run it straight
#' (`Rscript load.R`) for a quick summary, or `source()` it and call
#' `load_aircraft()` in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "aircraft-supply-chain")

#' Load the node table (one row per supplier / system / program).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per supply relationship).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Build the directed, weighted graph.
#'
#' Edges are weighted by `units_per_year` and flow from the upstream node to the
#' downstream node. Use `subcomponent(g, v, mode = "out")` to trace everything
#' downstream of a node, or knock a node out (`delete_vertices`) to test how much
#' end-program output it carries.
load_aircraft <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = TRUE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$units_per_year
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n✈️  aircraft-supply-chain (R)\n")
  cat("   Materials -> components -> systems -> integrators -> programs;",
      "weighted by units per year.\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_aircraft(nodes, edges)

  cat(sprintf("✅ Loaded %d nodes (%d material, %d component, %d system, %d integrator, %d program) and %d edges.\n",
              nrow(nodes), sum(nodes$kind == "material"),
              sum(nodes$kind == "component"), sum(nodes$kind == "system"),
              sum(nodes$kind == "integrator"), sum(nodes$kind == "program"),
              nrow(edges)))
  cat(sprintf("🔗 Directed: %s | total units/year: %s | total value: $%s M\n",
              is_directed(g),
              format(sum(edges$units_per_year), big.mark = ","),
              format(round(sum(edges$value_musd)), big.mark = ",")))
  cat("🎉 Graph ready. `g` is a directed, weighted igraph (weight = units_per_year).\n")
}
```

---

## `data/projects/aircraft-supply-chain/load.py`

```python
"""Load the `aircraft-supply-chain` project network (Python).

Reads the two CSVs in this folder and builds a directed, weighted python-igraph
object: a multi-tier commercial-aircraft supply chain (materials -> components ->
systems -> integrators -> programs). Run it straight (``python load.py``) for a
quick summary, or import ``load_aircraft()`` into your own script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per supplier / system / program."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per supply relationship."""
    return pd.read_csv(HERE / "edges.csv")


def load_aircraft(nodes: pd.DataFrame | None = None,
                  edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the directed, weighted graph (edge weight = ``units_per_year``).

    Edges flow from the upstream node to the downstream node. Use
    ``g.subcomponent(v, mode="out")`` to trace everything downstream of a node,
    or delete a vertex to test how much end-program output it carries.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=True, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["units_per_year"]
    return g


if __name__ == "__main__":
    print("\n✈️  aircraft-supply-chain (Python)")
    print("   Materials -> components -> systems -> integrators -> programs; "
          "weighted by units per year.\n")

    nodes = load_nodes()
    edges = load_edges()
    g = load_aircraft(nodes, edges)

    kinds = nodes["kind"].value_counts()
    print(f"✅ Loaded {len(nodes)} nodes "
          f"({kinds.get('material',0)} material, {kinds.get('component',0)} component, "
          f"{kinds.get('system',0)} system, {kinds.get('integrator',0)} integrator, "
          f"{kinds.get('program',0)} program) and {len(edges)} edges.")
    print(f"🔗 Directed: {g.is_directed()} | total units/year: "
          f"{edges['units_per_year'].sum():,} | total value: "
          f"${round(edges['value_musd'].sum()):,} M")
    print("🎉 Graph ready. Object `g` is a directed, weighted igraph "
          "(weight = units_per_year).")
```

---

## `data/projects/airline-delays/README.md`

# airline-delays

*One operating day of a domestic carrier's route network, sliced into four time
blocks: directed flights between airports, each carrying a flight count and an
average departure delay.*

![Preview of the airline-delays network](thumb.png)

## At a glance

| | |
|---|---|
| **Direction** | Directed (flights fly origin → destination) |
| **Weights** | Weighted (`number_of_flights` per edge; `delay_min` quality field) |
| **Modality** | Unimodal — one node kind (`airport`) |
| **Temporal** | Yes — one row per (origin, destination, **block**: morning/midday/afternoon/evening) |
| **Nodes** | 200 airports (6 hubs) |
| **Edges** | 2,244 (561 directed routes × 4 blocks) |
| **Files** | `nodes.csv`, `edges.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

"Meridian Air" flies a domestic schedule across five regions. Each **airport** is
a node; each directed **flight route** is an edge, recorded in four time blocks
across one day (morning → midday → afternoon → evening). An edge's weight is the
number of flights on that leg in that block, and each edge also carries the
average departure `delay_min` for that leg and block. Airports carry a hub flag,
region, runway count, a weather-exposure score, and rough map coordinates.

This is a flow-and-resilience network with a temporal dimension. It rewards
students who track how disruption moves through a system. Some questions to chew
on:

- The day is not uniform. Does delay stay put, or does a bad block at one airport
  show up somewhere else in the *next* block?
- Are all the big hubs equally fragile, or does one shrug off trouble that
  flattens another?
- If you had to protect one airport to keep regions reachable, which would it be —
  and would flight volume, degree, or betweenness point you to the same node?
- When delays correlate between two airports, is it because they are close
  together on the map, or because they are wired together by routes?
- Which airports are big because they are *busy* versus big because they are
  *structurally important*?

> **Note.** The interesting findings here are deliberately *not* documented.
> "Busy hubs handle more flights" is the starting point, not a finding. Push past
> it.

## `nodes.csv`

One row per airport.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique 3-letter airport code (fictional). Referenced by edges. | character | `ABK`, `AGC`, `AAY` |
| `kind` | Node kind | Always `airport` (single-mode network). | character | `airport` |
| `label` | Display name | Human-readable label. (`name` is avoided — python-igraph reserves it for the ID.) | character | `ABK International`, `AFO Regional` |
| `region` | Region | Geographic region the airport sits in. | character | `Northeast`, `Midwest`, `West` |
| `hub` | Hub flag | 1 if the airport is a hub, else 0. | integer | `0`, `1` |
| `runways` | Runways | Number of runways (capacity proxy). | integer | `2`, `5` |
| `weather_exposure` | Weather exposure | Propensity to weather disruption, 0–1. | double | `0.31`, `0.74` |
| `x` | X coordinate | Horizontal position on a 0–100 map grid. | double | `54.12`, `13.88` |
| `y` | Y coordinate | Vertical position on a 0–100 map grid. | double | `60.40`, `49.07` |

## `edges.csv`

One row per (origin, destination, block). Directed.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | Origin airport ID | Departing airport. | character | `ABK`, `AGC` |
| `to_id` | Destination airport ID | Arriving airport. | character | `AAB`, `AEZ` |
| `block` | Time block | Part of the operating day: `morning`, `midday`, `afternoon`, `evening`. | character | `midday`, `evening` |
| `number_of_flights` | Number of flights | Flights on that leg in that block (the edge weight). | integer | `3`, `11` |
| `seats` | Seats | Total scheduled seats on that leg in that block. | integer | `412`, `1830` |
| `delay_min` | Average departure delay | Mean departure delay on that leg in that block, minutes. | double | `8.4`, `61.2` |

## Load it

```bash
Rscript data/projects/airline-delays/load.R     # R    (igraph)
python  data/projects/airline-delays/load.py     # Python (python-igraph)
```

Both build a directed, weighted `igraph` graph and print a one-screen summary. In
the [R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**airline-delays** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/airline-delays>

---

## `data/projects/airline-delays/_generate.py`

```python
"""Generate the `airline-delays` project network (deterministic).

A domestic airline route network for a fictional carrier "Meridian Air" across
one operating day, sliced into four time blocks:
  - ~200 airport nodes (kind = "airport")
Edges are directed scheduled flights origin -> destination, one row per
(origin, destination, block), weighted by `number_of_flights`, each carrying an
average departure `delay_min` for that leg in that block.

Design parameters (the only record of the planted structure):
  - WX_HUB: one major hub suffers a weather event in the MIDDAY block; its
    outbound delay_min spikes that block and PROPAGATES downstream -- airports
    directly fed by it show elevated delay in the NEXT (afternoon) block
    (a measurable temporal lag), then it partially clears by evening.
  - RESILIENT_HUB: a second major hub absorbs/reroutes and shows little
    propagation, so hubs are not equally fragile.
  - CONNECTOR: a mid-size airport with few flights but high betweenness; it is
    the only bridge between two regional clusters, so removing it disconnects
    regional pairs more than removing a high-flight point-to-point airport.
  - DELAY_ALONG_EDGES: delay travels along routes, not by raw geography -- the
    propagation coupling is via the directed edges, with noise added so distance
    does not predict delay correlation.

Run:
    python data/projects/airline-delays/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

N_AIRPORTS = 200
BLOCKS = ["morning", "midday", "afternoon", "evening"]
REGIONS = ["Northeast", "Southeast", "Midwest", "West", "Mountain"]

# --- planted parameters -----------------------------------------------------
N_HUBS = 6                 # designated hubs (high degree)
WX_HUB_IDX = 0             # the fragile hub hit by weather at midday
RESILIENT_HUB_IDX = 1      # the hub that absorbs the shock
WX_DELAY_SPIKE = 58.0      # extra outbound delay (min) at WX hub during midday
PROPAGATE_FRAC = 0.62      # share of WX-hub outbound delay inherited next block
RESILIENT_ABSORB = 0.88    # resilient hub damps its own propagated delay
BASE_DELAY = 7.0           # baseline avg delay (min) on a normal leg
BLOCK_LOAD = {"morning": 0.9, "midday": 1.0, "afternoon": 1.15, "evening": 1.05}


def main() -> None:
    rng = np.random.default_rng(SEED)

    # ----- airport positions & regions -------------------------------------
    # Five regional clusters laid out across a 0-100 map, each a Gaussian blob.
    centers = {
        "Northeast": (82, 78),
        "Southeast": (74, 22),
        "Midwest":   (54, 60),
        "West":      (14, 50),
        "Mountain":  (34, 40),
    }
    region_of = rng.choice(REGIONS, size=N_AIRPORTS,
                           p=[0.22, 0.20, 0.22, 0.20, 0.16])
    xs = np.empty(N_AIRPORTS)
    ys = np.empty(N_AIRPORTS)
    for i in range(N_AIRPORTS):
        cx, cy = centers[region_of[i]]
        xs[i] = np.clip(cx + rng.normal(0, 9), 0, 100)
        ys[i] = np.clip(cy + rng.normal(0, 9), 0, 100)

    # ----- pick hubs & the connector ---------------------------------------
    # Hubs: one per region plus an extra, chosen as the most central within
    # their own region blob so they read as natural hubs.
    hub_idx = []
    for r in REGIONS:
        members = np.where(region_of == r)[0]
        cx, cy = centers[r]
        d = np.hypot(xs[members] - cx, ys[members] - cy)
        hub_idx.append(int(members[np.argmin(d)]))
    # one extra hub in the busiest region (Midwest)
    mid_members = np.where(region_of == "Midwest")[0]
    extra = int(mid_members[np.argsort(np.hypot(
        xs[mid_members] - centers["Midwest"][0],
        ys[mid_members] - centers["Midwest"][1]))[1]])
    hub_idx.append(extra)
    hub_idx = list(dict.fromkeys(hub_idx))[:N_HUBS]
    hub_set = set(hub_idx)

    wx_hub = hub_idx[WX_HUB_IDX]
    resilient_hub = hub_idx[RESILIENT_HUB_IDX]

    # The connector: a non-hub airport that we will MAKE the sole bridge between
    # two regions (West <-> Mountain). Pick a modest airport near the gap.
    west_members = np.where(region_of == "West")[0]
    # closest West airport to the Mountain center, but not a hub
    cand = [m for m in west_members if m not in hub_set]
    cand = sorted(cand, key=lambda m: np.hypot(
        xs[m] - centers["Mountain"][0], ys[m] - centers["Mountain"][1]))
    connector = int(cand[0])

    is_hub = np.zeros(N_AIRPORTS, dtype=int)
    for h in hub_idx:
        is_hub[h] = 1

    runways = np.where(is_hub == 1,
                       rng.integers(4, 7, N_AIRPORTS),
                       rng.integers(1, 4, N_AIRPORTS))
    # weather exposure: spatial gradient (more in the West/Mountain) + noise
    wx_grad = 0.30 + 0.004 * (100 - xs) + 0.002 * ys
    weather_exposure = np.clip(wx_grad + rng.normal(0, 0.08, N_AIRPORTS), 0.02, 0.98)

    codes = _airport_codes(N_AIRPORTS)
    nodes = pd.DataFrame({
        "node_id": codes,
        "kind": "airport",
        "label": [f"{codes[i]} Regional" if not is_hub[i] else f"{codes[i]} International"
                  for i in range(N_AIRPORTS)],
        "region": region_of,
        "hub": is_hub,
        "runways": runways,
        "weather_exposure": weather_exposure.round(3),
        "x": xs.round(2),
        "y": ys.round(2),
    })

    # ----- build the directed route topology -------------------------------
    # Routes: (a) hub-and-spoke within region, (b) hub-to-hub trunk routes,
    # (c) some point-to-point, (d) the connector as the ONLY West<->Mountain link.
    route_pairs: set[tuple[int, int]] = set()

    def add(a, b):
        if a != b:
            route_pairs.add((a, b))

    # (a) each non-hub connects to the 1-2 nearest hubs in its own region
    for i in range(N_AIRPORTS):
        if is_hub[i]:
            continue
        same = [h for h in hub_idx if region_of[h] == region_of[i]]
        if not same:
            same = hub_idx
        same = sorted(same, key=lambda h: np.hypot(xs[h] - xs[i], ys[h] - ys[i]))
        for h in same[:2]:
            add(i, h)
            add(h, i)

    # (b) hub-to-hub trunk routes among the "core" hubs (every region EXCEPT
    # West). The West hub is deliberately NOT trunked to the core -- the whole
    # West region reaches the rest of the network ONLY through the connector.
    west_hub = [h for h in hub_idx if region_of[h] == "West"][0]
    mtn_hub = [h for h in hub_idx if region_of[h] == "Mountain"][0]
    core_hubs = [h for h in hub_idx if h != west_hub]
    for a in core_hubs:
        for b in core_hubs:
            add(a, b)

    # (c) point-to-point: a high-volume non-hub "big P2P airport" with many
    # direct spokes. Its spokes ALSO attach to the regional hub, so removing the
    # big airport does NOT fragment the network -- it just removes volume.
    nonhub = [i for i in range(N_AIRPORTS)
              if not is_hub[i] and i != connector and region_of[i] != "West"]
    big_p2p = int(max(nonhub, key=lambda i: runways[i] * 1.0 + rng.random()))
    bp_hub = [h for h in hub_idx if region_of[h] == region_of[big_p2p]][0]
    same_region = [i for i in range(N_AIRPORTS)
                   if region_of[i] == region_of[big_p2p] and i != big_p2p
                   and not is_hub[i]]
    for j in rng.choice(same_region, size=min(14, len(same_region)), replace=False):
        add(big_p2p, int(j))
        add(int(j), big_p2p)
        add(bp_hub, int(j))          # also reachable via the hub (redundant)
        add(int(j), bp_hub)

    # scattered intra-region P2P (never crosses into/out of West)
    for i in range(N_AIRPORTS):
        if region_of[i] == "West":
            continue
        if rng.random() < 0.25:
            same = [j for j in range(N_AIRPORTS)
                    if region_of[j] == region_of[i] and j != i
                    and region_of[j] != "West"]
            if same:
                j = int(rng.choice(same))
                add(i, j)

    # (d) the connector: the SOLE gateway in/out of the West region. West hub
    # <-> connector <-> Mountain hub (the Mountain hub is part of the core mesh).
    # The connector itself sits in the West region with modest degree.
    add(west_hub, connector)
    add(connector, west_hub)
    add(mtn_hub, connector)
    add(connector, mtn_hub)
    # a couple of West spokes also feed the connector so it has some local degree
    west_spokes = [i for i in np.where(region_of == "West")[0]
                   if not is_hub[i] and i != connector]
    for j in rng.choice(west_spokes, size=min(3, len(west_spokes)), replace=False):
        add(connector, int(j))
        add(int(j), connector)

    # ----- assign per-block delays -----------------------------------------
    # First pass: baseline delays per (edge, block) with weather noise.
    # Then a SECOND pass propagates the WX hub's midday outbound spike to its
    # downstream airports' delays in the AFTERNOON block.
    edges_list = sorted(route_pairs)

    # outbound delay contributed to each origin airport, per block (we average
    # over its outgoing legs to get an airport-level "delay state").
    # Build base edge delays first.
    base_delay = {}  # (a,b,block) -> delay
    for (a, b) in edges_list:
        for blk in BLOCKS:
            d = (BASE_DELAY * BLOCK_LOAD[blk]
                 + 9.0 * weather_exposure[a]            # exposed origins delay more
                 + rng.normal(0, 4.0))
            base_delay[(a, b, blk)] = max(0.0, d)

    # WX hub weather event at MIDDAY: spike all its outbound legs.
    for (a, b) in edges_list:
        if a == wx_hub:
            base_delay[(a, b, "midday")] += WX_DELAY_SPIKE + rng.normal(0, 5)

    # airport-level midday outbound delay state (mean of outgoing legs)
    def airport_block_delay(node, blk):
        outs = [base_delay[(a, b, blk)] for (a, b) in edges_list if a == node]
        return float(np.mean(outs)) if outs else 0.0

    wx_midday_state = airport_block_delay(wx_hub, "midday")

    # downstream set of the WX hub (direct successors)
    downstream = sorted({b for (a, b) in edges_list if a == wx_hub})

    # PROPAGATION: each downstream airport inherits a fraction of the WX hub's
    # midday delay into the AFTERNOON block, scaled by edge flow share. The
    # resilient hub damps it heavily.
    for node in downstream:
        absorb = RESILIENT_ABSORB if node == resilient_hub else 0.0
        inherited = PROPAGATE_FRAC * (1 - absorb) * wx_midday_state
        # apply to that airport's OWN outbound legs in the afternoon
        for (a, b) in edges_list:
            if a == node:
                base_delay[(a, b, "afternoon")] += inherited + rng.normal(0, 3)
        # WX hub itself partially clears by afternoon (storm passing)
    # WX hub clears: afternoon outbound returns toward normal, evening normal.
    for (a, b) in edges_list:
        if a == wx_hub:
            # afternoon still somewhat elevated, evening near-normal
            base_delay[(a, b, "afternoon")] = (
                base_delay[(a, b, "afternoon")] * 0.35
                + BASE_DELAY * BLOCK_LOAD["afternoon"])

    # ----- flight volumes ---------------------------------------------------
    rows = []
    for (a, b) in edges_list:
        # base flights scale with whether endpoints are hubs and runways
        base_flights = 1 + (3 if is_hub[a] else 0) + (3 if is_hub[b] else 0)
        base_flights += runways[a] // 2
        if a == big_p2p or b == big_p2p:
            base_flights += 6           # the big point-to-point airport is busy
        if a == connector or b == connector:
            base_flights = max(1, base_flights - 2)   # connector is LOW volume
        for blk in BLOCKS:
            nf = max(1, int(round(base_flights * BLOCK_LOAD[blk]
                                  + rng.normal(0, 1.0))))
            dly = round(base_delay[(a, b, blk)] + rng.normal(0, 1.5), 1)
            dly = max(0.0, dly)
            seats = int(nf * rng.integers(70, 200))
            rows.append({
                "from_id": codes[a],
                "to_id": codes[b],
                "block": blk,
                "number_of_flights": nf,
                "seats": seats,
                "delay_min": dly,
            })

    edges = pd.DataFrame(rows)
    # order blocks chronologically for readability
    blk_order = {b: i for i, b in enumerate(BLOCKS)}
    edges["_o"] = edges["block"].map(blk_order)
    edges = edges.sort_values(["from_id", "to_id", "_o"]).drop(columns="_o").reset_index(drop=True)

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)
    print(f"airline-delays: {len(nodes)} nodes "
          f"({int(nodes.hub.sum())} hubs), {len(edges)} edges "
          f"({len(edges_list)} directed routes x {len(BLOCKS)} blocks).")


def _airport_codes(n: int) -> list[str]:
    """Deterministic unique 3-letter airport codes AAA, AAB, ... (not real)."""
    codes = []
    i = 0
    while len(codes) < n:
        a = i // (26 * 26)
        b = (i // 26) % 26
        c = i % 26
        codes.append(chr(65 + a) + chr(65 + b) + chr(65 + c))
        i += 1
    return codes


if __name__ == "__main__":
    main()
```

---

## `data/projects/airline-delays/load.R`

```r
#' @name load.R
#' @title Load the `airline-delays` project network (R)
#' @description
#'
#' Reads the two CSVs in this folder and builds a directed, weighted igraph
#' object: one day of scheduled flights between airports, sliced into four time
#' blocks. Run it straight (`Rscript load.R`) for a quick summary, or `source()`
#' it and call `load_airline()` to get the graph in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "airline-delays")

#' Load the node table (one row per airport).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per origin x destination x block).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Build the directed, weighted graph.
#'
#' Edges are weighted by `number_of_flights`. Because the data is temporal (a
#' `block` column), an edge between the same pair appears up to 4 times; igraph
#' keeps them as parallel edges, so filter to one `block` first if you want a
#' simple graph.
load_airline <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = TRUE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$number_of_flights
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n✈️  airline-delays (R)\n")
  cat("   Directed flights between airports, weighted by flights, in 4 time blocks.\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_airline(nodes, edges)

  cat(sprintf("✅ Loaded %d airports (%d hubs) and %d edges (%d routes x 4 blocks).\n",
              nrow(nodes), sum(nodes$hub == 1), nrow(edges),
              nrow(unique(edges[, c("from_id", "to_id")]))))
  cat(sprintf("\U0001F517 Directed: %s | total flights: %s\n",
              is_directed(g), format(sum(edges$number_of_flights), big.mark = ",")))
  cat("\U0001F389 Graph ready. Object `g` is a directed, weighted igraph.\n")
}
```

---

## `data/projects/airline-delays/load.py`

```python
"""Load the `airline-delays` project network (Python).

Reads the two CSVs in this folder and builds a directed, weighted python-igraph
object: one day of scheduled flights between airports, sliced into four time
blocks. Run it straight (``python load.py``) for a quick summary, or import
``load_airline()`` into your own script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per airport."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per origin x destination x block."""
    return pd.read_csv(HERE / "edges.csv")


def load_airline(nodes: pd.DataFrame | None = None,
                 edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the directed, weighted graph (edge weight = ``number_of_flights``).

    The data is temporal (a ``block`` column), so an edge between the same pair of
    airports appears up to 4 times as parallel edges. Filter to one ``block``
    first if you want a simple graph.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=True, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["number_of_flights"]
    return g


if __name__ == "__main__":
    print("\n✈️  airline-delays (Python)")
    print("   Directed flights between airports, weighted by flights, in 4 time blocks.\n")

    nodes = load_nodes()
    edges = load_edges()
    g = load_airline(nodes, edges)

    n_routes = edges[["from_id", "to_id"]].drop_duplicates().shape[0]
    print(f"✅ Loaded {len(nodes)} airports ({int(nodes['hub'].sum())} hubs) "
          f"and {len(edges)} edges ({n_routes} routes x 4 blocks).")
    print(f"🔗 Directed: {g.is_directed()} | total flights: "
          f"{edges['number_of_flights'].sum():,}")
    print("🎉 Graph ready. Object `g` is a directed, weighted igraph.")
```

---

## `data/projects/amazon-last-mile/README.md`

# amazon-last-mile

*One week of package flow through a fictional metro's last-mile delivery network:
fulfillment hubs → delivery stations → neighborhood zones.*

![Preview of the amazon-last-mile network](thumb.png)

## At a glance

| | |
|---|---|
| **Direction** | Directed (package flow: hub → station → zone) |
| **Weights** | Weighted (`packages` per edge; `on_time_rate` quality field) |
| **Modality** | Multimodal — 3 node kinds (`hub`, `station`, `zone`) |
| **Temporal** | Yes — one row per (origin, destination, **day** 1–7) |
| **Nodes** | 313 (4 hubs + 24 stations + 285 zones) |
| **Edges** | 2,142 (147 line-haul + 1,995 last-mile) |
| **Files** | `nodes.csv`, `edges.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

"Cascadia Logistics" runs a metro delivery operation. Bulk freight moves overnight
from **fulfillment hubs** to local **delivery stations** (the *line-haul* leg), then
vans fan out from each station to the **neighborhood zones** it serves (the
*last-mile* leg). Every delivery edge carries a package count and an on-time
delivery rate, recorded daily across one week. Zones carry demographic attributes
(median income, population, Prime-membership rate); stations and hubs carry
throughput capacity.

This is a flow-and-criticality network with a temporal dimension. It rewards
students who look past raw volume. Some questions to chew on:

- Who actually bears delivery risk? Is on-time performance explained by distance,
  or by *something about the neighborhoods themselves*?
- Is any single station carrying more than its share of the network — and what
  happens to it under stress?
- The week is not uniform. Does the network behave the same on every day, or does
  a demand surge expose a weak point?
- Does the *structure* of who-serves-whom stay fixed across the week, or does it
  change partway through?
- If you had to harden this system against a one-day outage, which node would you
  protect first — and would degree, betweenness, or load tell you the same answer?

> **Note.** The interesting findings here are deliberately *not* documented. "Busier
> zones get more packages" is the starting point, not a finding. Push past it.

## `nodes.csv`

One row per node. Hub/station rows leave the zone-only demographic columns blank;
zone rows leave `capacity_pkgs` blank.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique key. `H##` hub, `S##` station, `Z###` zone. Referenced by edges. | character | `H03`, `S14`, `Z001` |
| `kind` | Node kind | Tier of the network this node sits in. | character | `hub`, `station`, `zone` |
| `label` | Display name | Human-readable label. (`name` is avoided — python-igraph reserves it for the ID.) | character | `Cascadia FC C`, `DS-14`, `Zone 001` |
| `x` | X coordinate | Horizontal position on a 0–100 metro grid. | double | `21.59`, `69.18` |
| `y` | Y coordinate | Vertical position on a 0–100 metro grid. | double | `83.29`, `40.85` |
| `region` | Region | Metro quadrant the node falls in. | character | `North`, `South`, `East`, `West` |
| `median_income` | Median household income | Zone median income in USD (blank for hubs/stations). | integer | `79554`, `41220` |
| `population` | Population | Residents served by the zone (blank for hubs/stations). | integer | `7665`, `2310` |
| `prime_rate` | Prime membership rate | Fraction of the zone that are Prime members (blank for hubs/stations). | double | `0.39`, `0.71` |
| `capacity_pkgs` | Daily package capacity | Nominal throughput capacity (blank for zones). | integer | `50264`, `2740` |

## `edges.csv`

One row per (origin, destination, day). Directed. `line_haul` rows have no
`on_time_rate` (it is a quality measure of last-mile delivery only).

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | Origin node ID | Sending node (`H##` for line-haul, `S##` for last-mile). | character | `H03`, `S08` |
| `to_id` | Destination node ID | Receiving node (`S##` for line-haul, `Z###` for last-mile). | character | `S01`, `Z002` |
| `day` | Day of week | 1 = Monday … 7 = Sunday. | integer | `1`, `6` |
| `packages` | Packages | Number of packages moved on that edge that day (the edge weight). | integer | `3827`, `131` |
| `on_time_rate` | On-time delivery rate | Share of last-mile packages delivered on time (blank for line-haul). | double | `0.865`, `0.724` |
| `distance_km` | Distance | Road distance between the two nodes, kilometers. | double | `15.79`, `9.29` |
| `service` | Service type | `line_haul`, or last-mile `standard` / `same_day`. | character | `line_haul`, `standard`, `same_day` |

## Load it

```bash
Rscript data/projects/amazon-last-mile/load.R     # R    (igraph)
python  data/projects/amazon-last-mile/load.py     # Python (python-igraph)
```

Both build a directed, weighted `igraph` graph and print a one-screen summary. In
the [R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**amazon-last-mile** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/amazon-last-mile>

---

## `data/projects/amazon-last-mile/_generate.py`

```python
"""Generate the `amazon-last-mile` project network (deterministic).

A one-week last-mile delivery network for a fictional metro area "Cascadia":
  - 4 fulfillment hubs        (kind = "hub")
  - 24 delivery stations      (kind = "station")
  - ~285 delivery zones       (kind = "zone")  -> ~313 nodes total

Edges are directed package flows, one row per (origin, destination, day):
  - line-haul   hub  -> station   (trucks moving bulk freight overnight)
  - last-mile   station -> zone   (vans delivering to neighborhoods)
weighted by `packages`, with a delivery-quality field `on_time_rate`.

Design parameters (the only record of the planted structure):
  - INCOME_PENALTY: on-time rate falls with zone income, *independent of
    distance*; same-day eligibility tracks income too.
  - OVERLOAD_STATION: one station is assigned far more zones than its
    capacity; its on-time rate is depressed and degrades hardest on the
    demand-spike day.
  - SPIKE_DAY (day 6): a ~2x volume surge ("Prime Day").
  - REASSIGN: a cluster of zones is moved from the overloaded station to a
    neighbor starting on day 4 (a structural rewiring mid-week).

Run:
    python data/projects/amazon-last-mile/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

N_HUBS = 4
N_STATIONS = 24
N_ZONES = 285
DAYS = list(range(1, 8))            # 1=Mon ... 7=Sun
SPIKE_DAY = 6
REGIONS = ["North", "South", "East", "West"]

# --- planted parameters -----------------------------------------------------
INCOME_PENALTY = 0.16     # max on-time reduction for the lowest-income zones
OVERLOAD_IDX = 7          # which station (0-based) is silently over capacity
OVERLOAD_PENALTY = 0.10   # on-time reduction at the overloaded station
SPIKE_PENALTY = 0.07      # extra on-time reduction on the spike day
REASSIGN_FROM = 7         # zones leave this station ...
REASSIGN_TO = 8           # ... and join this one, starting day 4
REASSIGN_DAY = 4


def main() -> None:
    rng = np.random.default_rng(SEED)

    # ----- hubs ------------------------------------------------------------
    hub_xy = rng.uniform(15, 85, size=(N_HUBS, 2))
    hubs = pd.DataFrame({
        "node_id": [f"H{i:02d}" for i in range(1, N_HUBS + 1)],
        "kind": "hub",
        "label": [f"Cascadia FC {chr(65+i)}" for i in range(N_HUBS)],
        "x": hub_xy[:, 0].round(2),
        "y": hub_xy[:, 1].round(2),
        "region": [REGIONS[i % 4] for i in range(N_HUBS)],
        "median_income": pd.NA,
        "population": pd.NA,
        "prime_rate": pd.NA,
        "capacity_pkgs": rng.integers(40000, 60000, N_HUBS),
    })

    # ----- stations --------------------------------------------------------
    st_xy = rng.uniform(5, 95, size=(N_STATIONS, 2))
    stations = pd.DataFrame({
        "node_id": [f"S{i:02d}" for i in range(1, N_STATIONS + 1)],
        "kind": "station",
        "label": [f"DS-{i:02d}" for i in range(1, N_STATIONS + 1)],
        "x": st_xy[:, 0].round(2),
        "y": st_xy[:, 1].round(2),
        "region": [REGIONS[int(y // 25.0001)] for y in st_xy[:, 1]],
        "median_income": pd.NA,
        "population": pd.NA,
        "prime_rate": pd.NA,
        # nominal daily capacity; the overloaded station gets the same cap but
        # far more demand than the rest.
        "capacity_pkgs": rng.integers(2200, 3200, N_STATIONS),
    })

    # ----- zones -----------------------------------------------------------
    z_xy = rng.uniform(0, 100, size=(N_ZONES, 2))
    # Income has a spatial gradient (richer to the west/north) PLUS noise, so
    # income is not perfectly readable from location.
    grad = 38000 + 520 * (100 - z_xy[:, 0]) + 300 * z_xy[:, 1]
    income = np.clip(grad + rng.normal(0, 9000, N_ZONES), 22000, 165000)
    income_norm = (income - income.min()) / (income.max() - income.min())
    population = rng.integers(900, 9000, N_ZONES)
    # Prime membership rises with income but is noisy.
    prime_rate = np.clip(0.25 + 0.45 * income_norm + rng.normal(0, 0.07, N_ZONES), 0.05, 0.95)

    zones = pd.DataFrame({
        "node_id": [f"Z{i:03d}" for i in range(1, N_ZONES + 1)],
        "kind": "zone",
        "label": [f"Zone {i:03d}" for i in range(1, N_ZONES + 1)],
        "x": z_xy[:, 0].round(2),
        "y": z_xy[:, 1].round(2),
        "region": [REGIONS[int(y // 25.0001)] for y in z_xy[:, 1]],
        "median_income": income.round(0).astype(int),
        "population": population,
        "prime_rate": prime_rate.round(3),
        "capacity_pkgs": pd.NA,
    })

    nodes = pd.concat([hubs, stations, zones], ignore_index=True)

    # ----- assign each zone to a station -----------------------------------
    # Nearest station, but the overloaded station "wins" any zone within a
    # generous radius -> it ends up with far more zones than its peers.
    st_pos = st_xy
    assign = np.empty(N_ZONES, dtype=int)
    for zi in range(N_ZONES):
        d = np.hypot(st_pos[:, 0] - z_xy[zi, 0], st_pos[:, 1] - z_xy[zi, 1])
        nearest = int(np.argmin(d))
        if d[OVERLOAD_IDX] < d[nearest] + 22:   # greedy land-grab
            nearest = OVERLOAD_IDX
        assign[zi] = nearest

    # zones to reassign to a neighbor partway through the week
    overload_zones = np.where(assign == REASSIGN_FROM)[0]
    reassigned = set(overload_zones[: max(1, len(overload_zones) // 3)].tolist())

    # ----- hub feeding each station ----------------------------------------
    hub_of_station = np.empty(N_STATIONS, dtype=int)
    for si in range(N_STATIONS):
        d = np.hypot(hub_xy[:, 0] - st_pos[si, 0], hub_xy[:, 1] - st_pos[si, 1])
        hub_of_station[si] = int(np.argmin(d))

    # ----- build edges -----------------------------------------------------
    DOW_FACTOR = {1: 1.05, 2: 1.00, 3: 1.00, 4: 1.02, 5: 1.10, 6: 2.0, 7: 0.7}
    last_mile_rows = []
    for day in DAYS:
        for zi in range(N_ZONES):
            # which station serves this zone today?
            st = assign[zi]
            if zi in reassigned and day >= REASSIGN_DAY:
                st = REASSIGN_TO

            dist = float(np.hypot(st_pos[st, 0] - z_xy[zi, 0], st_pos[st, 1] - z_xy[zi, 1]))
            base_demand = population[zi] * (0.012 + 0.05 * prime_rate[zi])
            lam = base_demand * DOW_FACTOR[day]
            pkgs = int(rng.poisson(max(lam, 1)))
            if pkgs == 0:
                continue

            # on-time rate: distance hurts a little; LOW INCOME hurts a lot
            # (independent of distance); overloaded station + spike day hurt.
            ot = 0.985 - 0.0011 * dist - INCOME_PENALTY * (1 - income_norm[zi])
            if st == OVERLOAD_IDX:
                ot -= OVERLOAD_PENALTY
            if day == SPIKE_DAY:
                ot -= SPIKE_PENALTY
                if st == OVERLOAD_IDX:
                    ot -= 0.05      # the overloaded station buckles hardest
            ot = float(np.clip(ot + rng.normal(0, 0.015), 0.40, 0.999))

            # same-day service offered mainly where income & prime are high
            same_day = (income_norm[zi] > 0.55 and prime_rate[zi] > 0.55)
            service = "same_day" if same_day else "standard"

            last_mile_rows.append({
                "from_id": f"S{st+1:02d}",
                "to_id": zones.at[zi, "node_id"],
                "day": day,
                "packages": pkgs,
                "on_time_rate": round(ot, 3),
                "distance_km": round(dist * 0.9, 2),
                "service": service,
            })

    last_mile = pd.DataFrame(last_mile_rows)

    # line-haul: hub -> station, weight = packages that station pushed that day
    haul_rows = []
    pushed = (last_mile.assign(st=last_mile["from_id"])
              .groupby(["st", "day"])["packages"].sum().reset_index())
    for _, r in pushed.iterrows():
        si = int(r["st"][1:]) - 1
        hub = hub_of_station[si]
        haul_rows.append({
            "from_id": f"H{hub+1:02d}",
            "to_id": r["st"],
            "day": int(r["day"]),
            "packages": int(r["packages"]),
            "on_time_rate": pd.NA,
            "distance_km": round(float(np.hypot(
                hub_xy[hub, 0] - st_pos[si, 0], hub_xy[hub, 1] - st_pos[si, 1])) * 0.9, 2),
            "service": "line_haul",
        })
    haul = pd.DataFrame(haul_rows)

    edges = pd.concat([haul, last_mile], ignore_index=True)

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)
    print(f"amazon-last-mile: {len(nodes)} nodes "
          f"({(nodes.kind=='hub').sum()} hubs + {(nodes.kind=='station').sum()} stations + "
          f"{(nodes.kind=='zone').sum()} zones), {len(edges)} edges "
          f"({len(haul)} line-haul + {len(last_mile)} last-mile).")


if __name__ == "__main__":
    main()
```

---

## `data/projects/amazon-last-mile/load.R`

```r
#' @name load.R
#' @title Load the `amazon-last-mile` project network (R)
#' @description
#'
#' Reads the two CSVs in this folder and builds a directed, weighted igraph
#' object: package flow through hubs -> stations -> zones over one week. Run it
#' straight (`Rscript load.R`) for a quick summary, or `source()` it and call
#' `load_amazon()` to get the graph in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "amazon-last-mile")

#' Load the node table (one row per hub / station / zone).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per origin x destination x day).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Build the directed, weighted graph.
#'
#' Edges are weighted by `packages`. Because the data is temporal (a `day`
#' column), an edge between the same pair appears up to 7 times; igraph keeps
#' them as parallel edges, so filter to one `day` first if you want a simple
#' graph.
load_amazon <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = TRUE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$packages
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n📦 amazon-last-mile (R)\n")
  cat("   Hubs -> stations -> zones; weighted by packages, daily for one week.\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_amazon(nodes, edges)

  cat(sprintf("✅ Loaded %d nodes (%d hubs, %d stations, %d zones) and %d edges.\n",
              nrow(nodes), sum(nodes$kind == "hub"),
              sum(nodes$kind == "station"), sum(nodes$kind == "zone"), nrow(edges)))
  cat(sprintf("🔗 Directed: %s | total packages moved: %s\n",
              is_directed(g), format(sum(edges$packages), big.mark = ",")))
  cat("🎉 Graph ready. Object `g` is a directed, weighted igraph.\n")
}
```

---

## `data/projects/amazon-last-mile/load.py`

```python
"""Load the `amazon-last-mile` project network (Python).

Reads the two CSVs in this folder and builds a directed, weighted python-igraph
object: package flow through hubs -> stations -> zones over one week. Run it
straight (``python load.py``) for a quick summary, or import ``load_amazon()``
into your own script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per hub / station / zone."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per origin x destination x day."""
    return pd.read_csv(HERE / "edges.csv")


def load_amazon(nodes: pd.DataFrame | None = None,
                edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the directed, weighted graph (edge weight = ``packages``).

    The data is temporal (a ``day`` column), so an edge between the same pair of
    nodes appears up to 7 times as parallel edges. Filter to one ``day`` first if
    you want a simple graph.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=True, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["packages"]
    return g


if __name__ == "__main__":
    print("\n📦 amazon-last-mile (Python)")
    print("   Hubs -> stations -> zones; weighted by packages, daily for one week.\n")

    nodes = load_nodes()
    edges = load_edges()
    g = load_amazon(nodes, edges)

    kinds = nodes["kind"].value_counts()
    print(f"✅ Loaded {len(nodes)} nodes "
          f"({kinds.get('hub',0)} hubs, {kinds.get('station',0)} stations, "
          f"{kinds.get('zone',0)} zones) and {len(edges)} edges.")
    print(f"🔗 Directed: {g.is_directed()} | total packages moved: "
          f"{edges['packages'].sum():,}")
    print("🎉 Graph ready. Object `g` is a directed, weighted igraph.")
```

---

## `data/projects/campus-contact/README.md`

# campus-contact

*Four weeks of face-to-face proximity on a university campus, recorded as a
respiratory illness moves through the population.*

![Preview of the campus-contact network](thumb.png)

## At a glance

| | |
|---|---|
| **Direction** | Undirected (a contact links two people who were co-located) |
| **Weights** | Weighted (`contact_minutes` per pair per week) |
| **Modality** | One node kind (`person`) with a `kind` role (student / faculty / staff) |
| **Temporal** | Yes — one row per (person, person, **week** 1–4); `status.csv` is per (person, week) |
| **Nodes** | 300 (252 students + 26 faculty + 22 staff) |
| **Edges** | 3,699 contact-weeks |
| **Files** | `nodes.csv`, `edges.csv`, `status.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

A campus **contact-tracing** network. Wearable proximity sensors logged who spent
time near whom, aggregated into weekly co-location contacts. Each edge carries the
total minutes a pair spent in proximity that week (`contact_minutes`), and edges
are tagged by `week` (1–4). Over the same four weeks a respiratory illness spread
through campus; the companion `status.csv` records, for every person and week,
whether they were infected by then. People carry a role (`kind`), a `unit` (their
dorm or academic department), and — for students — a class `year`.

This is the natural home for **community detection**, **centrality / criticality**,
**network-aware inference**, and **diffusion** questions. Some things worth digging
into:

- The contact graph is far from uniform. Does it break into communities, and do
  those communities line up with anything in `nodes.csv`?
- If you had to name the one person whose removal would most have slowed the spread
  between groups, who is it — and would degree alone have told you?
- Roles are not interchangeable. Do students, faculty, and staff sit in the same
  structural position, or do some of them do something the others don't?
- The four weeks are not the same. Does the contact structure change partway
  through, and does anything about the outbreak change at the same time?
- Who tends to get infected first? Is being infected early random, or is it
  predictable from where you sit in the network?

> **Note.** The interesting findings here are deliberately *not* documented. "People
> in the same dorm see each other a lot" is the starting point, not a finding. Push
> past it.

## `nodes.csv`

One row per person. The `year` column is blank for faculty and staff.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique key. `P###`. Referenced by edges and by `status.csv`. | character | `P001`, `P218`, `P300` |
| `kind` | Role | Which population the person belongs to. | character | `student`, `faculty`, `staff` |
| `unit` | Unit | Dorm (students) or department (faculty/staff) the person belongs to. | character | `West Hall`, `Engineering`, `Annex` |
| `year` | Class year | Student class year 1–4 (blank for faculty/staff). | integer | `1`, `4` |
| `label` | Display name | Human-readable label. (`name` is avoided — python-igraph reserves it for the ID.) | character | `Student 042`, `Faculty 03` |

## `edges.csv`

One row per (person, person, week). Undirected co-location contact.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | First person ID | One endpoint of the contact (joins to `nodes.csv`). | character | `P059` |
| `to_id` | Second person ID | The other endpoint (joins to `nodes.csv`). | character | `P088` |
| `week` | Study week | Week of the study, 1–4. | integer | `1`, `3` |
| `contact_minutes` | Contact minutes | Total minutes the pair spent in proximity that week (the edge weight). | integer | `44`, `19`, `207` |

## `status.csv`

Infection status, one row per (person, week). Not a node list — join it onto
`nodes.csv` on `node_id` (and filter or pivot on `week`).

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Person this status row describes (joins to `nodes.csv`). | character | `P001` |
| `week` | Study week | Week the status was observed, 1–4. | integer | `1`, `4` |
| `infected` | Infected flag | 1 if the person had been infected by this week (cumulative), else 0. | integer | `0`, `1` |

## Load it

```bash
Rscript data/projects/campus-contact/load.R     # R    (igraph)
python  data/projects/campus-contact/load.py     # Python (python-igraph)
```

Both build an undirected, weighted `igraph` graph (edge weight = `contact_minutes`)
and print a one-screen summary. Because the data is temporal, a pair can appear up
to four times (one per week) as parallel edges — filter to one `week` for a simple
graph. In the [R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**campus-contact** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/campus-contact>

---

## `data/projects/campus-contact/_generate.py`

```python
"""Generate the `campus-contact` project network (deterministic).

A face-to-face proximity / co-location contact network on a university campus,
recorded over four weeks as a respiratory illness spreads:
  - ~300 people (kind = student / faculty / staff)
  - undirected co-location contacts, one row per (person, person, week)
weighted by `contact_minutes` (time the two spent in proximity that week).
A companion `status.csv` records each person's infection state per week.

Design parameters (the only record of the planted structure):
  - N_UNITS: people belong to ~8 units (dorms for students, departments for
    faculty/staff); contacts cluster strongly WITHIN unit -> high modularity.
  - BRIDGE: faculty are the main inter-unit links between student clusters; ONE
    individual (the "connector") is a cross-unit bridge with extreme betweenness
    relative to their degree, touching the most units.
  - SEED_UNIT: the outbreak seeds inside the connector's unit; it jumps to other
    units mainly THROUGH the connector (their removal would have contained it).
  - INTERVENTION (week 3): the highest-degree contacts are cut sharply (a
    structural change); top contacts' degree drops, and infection growth flattens
    afterward.
  - HUB_EARLY: high-degree hubs get infected earlier than average (degree predicts
    early infection -> negative degree~infection-week correlation).

Run:
    python data/projects/campus-contact/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

N_PEOPLE = 300
WEEKS = [1, 2, 3, 4]

# --- planted parameters -----------------------------------------------------
# units: 6 student residences + 2 academic departments. Faculty/staff sit in the
# two departments; students sit in the dorms. Faculty bridge dorms <-> depts.
DORMS = ["West Hall", "East Hall", "North Hall", "South Hall", "Gradflat", "Annex"]
DEPTS = ["Engineering", "Sciences"]
UNITS = DORMS + DEPTS

WITHIN_BASE = 0.16        # baseline P(contact) within the same unit (high)
BETWEEN_BASE = 0.006      # baseline P(contact) across units (low) -> modularity
FACULTY_CROSS = 0.030     # faculty get extra cross-unit contact probability
CONNECTOR_CROSS = 0.55    # the connector blankets MANY units (bridge)

INTERVENTION_WEEK = 3     # high-degree contacts cut starting this week
TOP_CUT_FRAC = 0.10       # fraction of highest-degree people whose ties get cut
CUT_KEEP_PROB = 0.22      # of a cut person's ties, keep only this share at/after wk3

SEED_INFECTIONS = 12      # initial cases in the connector's seed unit (week 1)


def main() -> None:
    rng = np.random.default_rng(SEED)

    # ----- people ----------------------------------------------------------
    # roles: mostly students, some faculty/staff. Faculty/staff live in depts.
    roles = []
    units = []
    years = []
    # assign first the dept people (faculty + staff), then dorm students
    n_faculty = 26
    n_staff = 22
    n_students = N_PEOPLE - n_faculty - n_staff   # 252
    for _ in range(n_faculty):
        roles.append("faculty")
        units.append(rng.choice(DEPTS))
        years.append(0)                      # 0 = not a student year
    for _ in range(n_staff):
        roles.append("staff")
        units.append(rng.choice(DEPTS))
        years.append(0)
    for _ in range(n_students):
        roles.append("student")
        units.append(rng.choice(DORMS))
        years.append(int(rng.integers(1, 5)))   # class year 1..4

    roles = np.array(roles)
    units = np.array(units)
    years = np.array(years)

    node_id = np.array([f"P{i:03d}" for i in range(1, N_PEOPLE + 1)])
    labels = []
    fac_n = stf_n = stu_n = 0
    for r in roles:
        if r == "faculty":
            fac_n += 1; labels.append(f"Faculty {fac_n:02d}")
        elif r == "staff":
            stf_n += 1; labels.append(f"Staff {stf_n:02d}")
        else:
            stu_n += 1; labels.append(f"Student {stu_n:03d}")
    labels = np.array(labels)

    unit_of = dict(zip(node_id, units))
    role_of = dict(zip(node_id, roles))

    # ----- choose the connector (cross-unit bridge) ------------------------
    # a faculty member who will touch many units.
    faculty_ids = node_id[roles == "faculty"]
    connector = str(rng.choice(faculty_ids))
    seed_unit = unit_of[connector]

    # ----- build per-week contacts -----------------------------------------
    # We construct a base contact propensity per person (sociability) so that
    # hubs exist; then draw weekly edges from a unit-block model plus bridges.
    sociability = rng.lognormal(mean=0.0, sigma=0.5, size=N_PEOPLE)
    sociability = sociability / sociability.mean()
    soc_of = dict(zip(node_id, sociability))

    # identify the eventual top-degree people for the intervention. We estimate
    # expected degree from sociability + role and cut the top fraction.
    # faculty / connector are naturally high; intervention targets the busiest.
    expected_deg = sociability.copy()
    expected_deg[roles == "faculty"] *= 1.5
    expected_deg[node_id == connector] *= 3.0
    # rank by expected degree but EXCLUDE the connector from the cut: the
    # connector's bridging ties persist, so its criticality (and the "removal
    # would have contained it" counterfactual) stays intact through the study.
    order = [int(i) for i in np.argsort(-expected_deg) if node_id[i] != connector]
    n_cut = max(1, int(TOP_CUT_FRAC * N_PEOPLE))
    cut_ids = set(node_id[order[:n_cut]].tolist())

    idx_of = {nid: i for i, nid in enumerate(node_id)}

    edge_rows = []
    for week in WEEKS:
        intervened = week >= INTERVENTION_WEEK
        # draw a fresh set of contacts for the week
        seen = {}
        # within-unit contacts (block model)
        for u in UNITS:
            members = node_id[units == u]
            m = len(members)
            for a in range(m):
                for b in range(a + 1, m):
                    ia, ib = members[a], members[b]
                    p = WITHIN_BASE * np.sqrt(soc_of[ia] * soc_of[ib])
                    if rng.random() < p:
                        _add(seen, ia, ib, rng)
        # the connector is a guaranteed bridge: each week it makes ties into
        # EVERY other unit (a few members each), giving it max units-touched and
        # extreme betweenness relative to its degree. These bridge ties are the
        # only short paths between many unit pairs.
        for u in UNITS:
            if u == unit_of[connector]:
                continue
            cand = node_id[(units == u)]
            k = min(len(cand), int(rng.integers(2, 5)))
            for ib in rng.choice(cand, size=k, replace=False):
                _add(seen, connector, str(ib), rng)

        # cross-unit contacts: rare in general, more for faculty, lots for connector
        all_ids = node_id
        for ia in all_ids:
            # connector reaches across many units
            if ia == connector:
                cross_p = CONNECTOR_CROSS
            elif role_of[ia] == "faculty":
                cross_p = FACULTY_CROSS
            elif role_of[ia] == "staff":
                cross_p = BETWEEN_BASE * 2
            else:
                cross_p = BETWEEN_BASE
            # number of cross attempts scales with sociability
            n_try = rng.poisson(cross_p * 60 * soc_of[ia])
            for _ in range(n_try):
                ib = str(rng.choice(all_ids))
                if ib == ia or unit_of[ib] == unit_of[ia]:
                    continue
                _add(seen, ia, ib, rng)

        # apply intervention (week 3+): (1) cut most ties touching the top-degree
        # people -> their degree collapses; (2) a campus-wide reduction in contact
        # intensity (everyone meets a bit less) -> dampens the contact_minutes that
        # drive transmission, so the outbreak's growth flattens.
        for (ia, ib), mins in list(seen.items()):
            if intervened and (ia in cut_ids or ib in cut_ids):
                if rng.random() > CUT_KEEP_PROB:
                    del seen[(ia, ib)]
        if intervened:
            # the campus restrictions escalate: week 3 is partial, week 4 tighter.
            damp = 0.30 if week == 3 else 0.16
            for key in list(seen.keys()):
                seen[key] = int(max(3, seen[key] * damp))

        for (ia, ib), mins in seen.items():
            edge_rows.append({
                "from_id": ia, "to_id": ib, "week": week,
                "contact_minutes": mins,
            })

    edges = pd.DataFrame(edge_rows)

    # ----- infection dynamics over weeks -----------------------------------
    # SIR-ish on the realized weekly contact graph, seeded in the connector unit.
    infected_week = {nid: 0 for nid in node_id}     # 0 = never infected (within study)
    state = {nid: "S" for nid in node_id}

    # seed: cases in the seed unit, weighted toward more-social members (the
    # outbreak takes hold among the busiest people first -> hubs infected early).
    seed_pool = np.array([n for n in node_id[units == seed_unit] if n != connector])
    w = np.array([soc_of[n] ** 2 for n in seed_pool]); w = w / w.sum()
    seeds = rng.choice(seed_pool, size=min(SEED_INFECTIONS, len(seed_pool)),
                       replace=False, p=w)
    # a few stray introductions campus-wide, weighted to the most-social people,
    # so connectivity (not just being in the seed unit) governs early infection.
    others = np.array([n for n in node_id if n not in set(seeds) and n != connector])
    wo = np.array([soc_of[n] ** 3 for n in others]); wo = wo / wo.sum()
    sparks = rng.choice(others, size=4, replace=False, p=wo)
    for s in list(seeds) + list(sparks):
        state[s] = "I"
        infected_week[s] = 1

    # transmission probability per contact-minute; hubs more exposed naturally
    BETA = 0.0027
    for week in WEEKS:
        wk_edges = edges[edges["week"] == week]
        # build adjacency for this week
        contacts = {}
        for r in wk_edges.itertuples():
            contacts.setdefault(r.from_id, []).append((r.to_id, r.contact_minutes))
            contacts.setdefault(r.to_id, []).append((r.from_id, r.contact_minutes))
        newly = []
        for person, nbrs in contacts.items():
            if state[person] != "S":
                continue
            # force of infection from infected neighbors this week
            foi = 0.0
            for (nb, mins) in nbrs:
                if state[nb] == "I":
                    foi += BETA * mins
            # hubs (high sociability) get strongly extra exposure -> infected
            # earlier than peripheral people (friendship-paradox flavored).
            foi *= (0.10 + 4.0 * soc_of[person])
            if rng.random() < 1 - np.exp(-foi):
                newly.append(person)
        for p in newly:
            state[p] = "I"
            infected_week[p] = week

    # status long table: node_id, week, infected (cumulative 0/1)
    status_rows = []
    for nid in node_id:
        iw = infected_week[nid]
        for week in WEEKS:
            status_rows.append({
                "node_id": nid, "week": week,
                "infected": int(iw != 0 and week >= iw),
            })
    status = pd.DataFrame(status_rows)

    # ----- nodes table -----------------------------------------------------
    nodes = pd.DataFrame({
        "node_id": node_id,
        "kind": roles,
        "unit": units,
        "year": [y if y > 0 else pd.NA for y in years],
        "label": labels,
    })

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)
    status.to_csv(HERE / "status.csv", index=False)
    n_ever = sum(1 for v in infected_week.values() if v != 0)
    print(f"campus-contact: {len(nodes)} nodes "
          f"({(roles=='student').sum()} student + {(roles=='faculty').sum()} faculty + "
          f"{(roles=='staff').sum()} staff), {len(edges)} edge-weeks, "
          f"{len(UNITS)} units, {n_ever} ever-infected.")


def _add(seen, ia, ib, rng):
    """Add an undirected contact with contact-minutes; merge duplicates."""
    key = (ia, ib) if ia < ib else (ib, ia)
    mins = int(np.clip(rng.gamma(shape=2.0, scale=22.0), 3, 600))
    if key in seen:
        seen[key] += mins
    else:
        seen[key] = mins


if __name__ == "__main__":
    main()
```

---

## `data/projects/campus-contact/load.R`

```r
#' @name load.R
#' @title Load the `campus-contact` project network (R)
#' @description
#'
#' Reads the CSVs in this folder and builds an undirected, weighted igraph
#' object: weekly face-to-face co-location contacts on a campus over four weeks.
#' Run it straight (`Rscript load.R`) for a quick summary, or `source()` it and
#' call `load_campus()` to get the graph in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "campus-contact")

#' Load the node table (one row per person).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per person x person x week).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Load the infection-status table (one row per person x week).
load_status <- function() {
  read.csv(file.path(.dir(), "status.csv"), stringsAsFactors = FALSE)
}

#' Build the undirected, weighted contact graph.
#'
#' Edges are weighted by `contact_minutes`. Because the data is temporal (a
#' `week` column), a pair can appear up to 4 times as parallel edges; filter to
#' one `week` first if you want a simple graph.
load_campus <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = FALSE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$contact_minutes
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n\U0001F9A0 campus-contact (R)\n")
  cat("   Weekly face-to-face contacts on campus; weighted by contact minutes.\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  status <- load_status()
  g <- load_campus(nodes, edges)

  cat(sprintf("✅ Loaded %d people (%d students, %d faculty, %d staff) and %d contact-weeks.\n",
              nrow(nodes), sum(nodes$kind == "student"),
              sum(nodes$kind == "faculty"), sum(nodes$kind == "staff"), nrow(edges)))
  cat(sprintf("\U0001F517 Directed: %s | total contact minutes: %s\n",
              is_directed(g), format(sum(edges$contact_minutes), big.mark = ",")))
  inf <- tapply(status$infected, status$week, sum)
  cat(sprintf("\U0001F4C8 Cumulative infected by week: %s\n",
              paste(sprintf("wk%d=%d", as.integer(names(inf)), inf), collapse = "  ")))
  cat("\U0001F389 Graph ready. Object `g` is an undirected, weighted igraph.\n")
}
```

---

## `data/projects/campus-contact/load.py`

```python
"""Load the `campus-contact` project network (Python).

Reads the CSVs in this folder and builds an undirected, weighted python-igraph
object: weekly face-to-face co-location contacts on a campus over four weeks.
Run it straight (``python load.py``) for a quick summary, or import
``load_campus()`` into your own script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per person."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per person x person x week."""
    return pd.read_csv(HERE / "edges.csv")


def load_status() -> pd.DataFrame:
    """Infection-status table: one row per person x week."""
    return pd.read_csv(HERE / "status.csv")


def load_campus(nodes: pd.DataFrame | None = None,
                edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the undirected, weighted contact graph (edge weight = ``contact_minutes``).

    The data is temporal (a ``week`` column), so a pair can appear up to 4 times
    as parallel edges. Filter to one ``week`` first if you want a simple graph.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=False, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["contact_minutes"]
    return g


if __name__ == "__main__":
    print("\n\U0001F9A0 campus-contact (Python)")
    print("   Weekly face-to-face contacts on campus; weighted by contact minutes.\n")

    nodes = load_nodes()
    edges = load_edges()
    status = load_status()
    g = load_campus(nodes, edges)

    kinds = nodes["kind"].value_counts()
    print(f"✅ Loaded {len(nodes)} people "
          f"({kinds.get('student',0)} students, {kinds.get('faculty',0)} faculty, "
          f"{kinds.get('staff',0)} staff) and {len(edges)} contact-weeks.")
    print(f"\U0001F517 Directed: {g.is_directed()} | total contact minutes: "
          f"{edges['contact_minutes'].sum():,}")
    inf = status.groupby("week")["infected"].sum()
    print("\U0001F4C8 Cumulative infected by week: "
          + "  ".join(f"wk{w}={c}" for w, c in inf.items()))
    print("\U0001F389 Graph ready. Object `g` is an undirected, weighted igraph.")
```

---

## `data/projects/drone-components/README.md`

# drone-components

*A functional dependency map of a small UAV (drone): which hardware components and
software modules require which others to work.*

![Preview of the drone-components network](thumb.png)

## At a glance

| | |
|---|---|
| **Direction** | Directed (`from` requires → `to`) |
| **Weights** | Weighted (`coupling_strength` 1–5 = how tightly `from` is coupled to `to`) |
| **Modality** | Two node kinds (`hardware`, `software`), grouped into `subsystem` |
| **Temporal** | No — a single design snapshot |
| **Nodes** | 183 components (131 hardware, 52 software) |
| **Edges** | 617 "requires to function" relationships |
| **Files** | `nodes.csv`, `edges.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

Every node is a **component** of a drone — either a physical part (`hardware`:
motors, ESCs, battery, autopilot, IMUs, GPS, radios, camera, frame …) or a
`software` module (firmware, flight stack, sensor drivers, the EKF estimator, the
attitude controller, failsafe, telemetry stack …). A directed edge `A → B` means
*A depends on / requires B to function*: if B fails or is removed, A is impaired.
This is a **functional dependency graph** — a Design Structure Matrix view of
"what needs what" — not a supply chain. The edge weight, `coupling_strength`
(1–5), is how tightly A is bound to B. Each component carries its `kind`,
`subsystem`, `component_type`, `vendor`, a 1–5 `criticality` rating, a `redundant`
flag, and (for hardware) `mass_g` and `power_draw_w`.

This is a directed-graph **criticality, reachability, modularity, and
failure-propagation** playground. Some things worth investigating:

- The autopilot is the obvious hub by raw degree. But is the *most* critical node
  the one with the highest degree? Try ranking nodes by how many others can reach
  them *transitively*, or by betweenness, and see whether a different, quieter
  component rises to the top.
- Counterfactual disruption: remove one node and ask how much of the system gets
  stranded (can no longer reach what it needs). Does the biggest blast radius come
  from a high-degree node, or from one that degree analysis underrates?
- Is this graph acyclic? Look for strongly-connected components — feedback loops
  where two modules each depend on the other.
- Some components are flagged `redundant`. Check whether a redundant pair truly
  buys you independence, or whether both ultimately funnel into the same single
  downstream consumer.
- Does the system partition cleanly into `subsystem` modules (high modularity)?
  Which few cross-subsystem edges are the integration seams?
- Combine reach with `vendor` and `criticality`: is there a module the whole stack
  leans on that comes from a single vendor? What happens to a subsystem if you
  remove one vendor's parts entirely?

> **Note.** The interesting findings here are deliberately *not* documented.
> "The autopilot connects to everything" is the starting point, not a finding.
> Look at what raw degree alone hides.

## `nodes.csv`

One row per component.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique key referenced by edges. Spine parts get mnemonic ids; generic parts are `hw###` / `sw###`. | character | `mot1`, `fc`, `ekf`, `hw042`, `sw017` |
| `kind` | Component kind | Whether the node is a physical part or a software module. | character | `hardware`, `software` |
| `subsystem` | Subsystem | Functional group the component belongs to. | character | `propulsion`, `power`, `flight_control`, `navigation`, `software` |
| `component_type` | Component type | Finer-grained type within the subsystem. | character | `motor`, `esc`, `autopilot`, `estimator`, `sensor_driver` |
| `vendor` | Vendor | Supplier of the part / author of the module (~6 vendors). | character | `Aerex`, `Voltspan`, `NaviCore`, `PixHawk` |
| `criticality` | Criticality rating | Designer-assigned importance, 1 (minor) to 5 (flight-critical). | integer | `1`, `3`, `5` |
| `redundant` | Redundant flag | 1 if the part is nominally backed up by a sibling, else 0. | integer | `0`, `1` |
| `mass_g` | Mass (grams) | Component mass; blank for software. | double | `14.3`, `42.0`, `320.0` |
| `power_draw_w` | Power draw (watts) | Typical electrical draw; blank for software. | double | `0.3`, `1.82`, `4.46` |
| `label` | Display name | Human-readable label. (`name` is avoided — python-igraph reserves it for the ID.) | character | `Motor FL`, `Autopilot FC`, `EKF Estimator` |

## `edges.csv`

One row per dependency. Directed: `from_id` requires `to_id` to function.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | Dependent component ID | The component that has the dependency (joins to `nodes.csv`). | character | `esc1`, `ekf`, `mot2` |
| `to_id` | Required component ID | The component being depended on (joins to `nodes.csv`). | character | `pdb`, `imu_a`, `bec5v` |
| `dep_type` | Dependency type | Nature of the coupling. | character | `power`, `data`, `control`, `mechanical`, `software` |
| `coupling_strength` | Coupling strength | How tightly `from_id` is bound to `to_id`, 1 (loose) to 5 (tight). The edge weight. | integer | `1`, `3`, `5` |

## Load it

```bash
Rscript data/projects/drone-components/load.R     # R    (igraph)
python  data/projects/drone-components/load.py     # Python (python-igraph)
```

Both build a directed, weighted `igraph` graph (edge weight =
`coupling_strength`) and print a one-screen summary. In the
[R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**drone-components** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/drone-components>

---

## `data/projects/drone-components/_generate.py`

```python
"""Generate the `drone-components` project network (deterministic).

A FUNCTIONAL dependency graph for a small UAV (drone): hardware components and
software modules, and which one *requires* which to function. This is a
dependency-type graph (a Design Structure Matrix / "what needs what to work"),
NOT a supply chain. A directed edge ``A -> B`` means *A depends on / requires B
to function* (if B fails, A is impaired). Edges are weighted by
``coupling_strength`` (1-5). Nodes are multimodal: ``kind`` in {hardware,
software}, grouped into a ``subsystem``.

Design parameters (the ONLY record of the planted structure; parameter-level):
  - HIDDEN_SPOF = the power-distribution board ("pdb"). It has only MODERATE
    direct degree, but an outsized share of nodes transitively depend on it
    (high transitive in-reach + betweenness), so degree alone misses it.
    Knocking it out strands a large fraction of the system.
  - FUSION_NODE = the single sensor-fusion / EKF estimator. Two "redundant"
    sensor pairs (dual IMUs, and GPS+RTK) BOTH feed this one node -> the
    redundancy is fake (common single downstream dependent).
  - CYCLE: the flight controller <-> ESC telemetry and estimator <-> controller
    form real cyclic dependencies, so the graph is NOT a clean DAG (SCC size>1).
  - MODULARITY: components cluster by subsystem (dense within, sparse across),
    with a few cross-subsystem couplings = integration risk seams.
  - LEGACY_MODULE = a critical legacy software module ("sensor driver core")
    with high downstream reach and a single vendor = bus-factor risk.
  - VENDOR_LOCKIN: one vendor's parts depend tightly on each other through a
    proprietary protocol; removing that vendor fragments its subsystem.

Run:
    python data/projects/drone-components/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

VENDORS = ["Aerex", "Voltspan", "NaviCore", "PixHawk", "SkyLink", "GimbalWorks"]

# --- planted parameters -----------------------------------------------------
N_FILLER_HW = 90        # extra generic hardware components (noise)
N_FILLER_SW = 40        # extra generic software modules (noise)
CROSS_LINK_P = 0.06     # base prob of a cross-subsystem coupling (integration seam)
WITHIN_LINK_P = 0.34    # prob of a within-subsystem coupling (modularity)
SPOF_FANIN = 34         # how many nodes the power board ultimately feeds (reach)
LEGACY_REACH = 30       # downstream consumers of the legacy driver core
VENDOR_LOCK_VENDOR = "NaviCore"   # the lock-in vendor (navigation/comms parts)


def main() -> None:
    rng = np.random.default_rng(SEED)

    # ----- the named "spine" components (the realistic UAV skeleton) --------
    # Each tuple: (node_id, kind, subsystem, component_type, label)
    spine = [
        # propulsion (4 motors + 4 ESCs + 4 props + mounts)
        ("mot1", "hardware", "propulsion", "motor", "Motor FL"),
        ("mot2", "hardware", "propulsion", "motor", "Motor FR"),
        ("mot3", "hardware", "propulsion", "motor", "Motor RL"),
        ("mot4", "hardware", "propulsion", "motor", "Motor RR"),
        ("esc1", "hardware", "propulsion", "esc", "ESC FL"),
        ("esc2", "hardware", "propulsion", "esc", "ESC FR"),
        ("esc3", "hardware", "propulsion", "esc", "ESC RL"),
        ("esc4", "hardware", "propulsion", "esc", "ESC RR"),
        ("prop1", "hardware", "propulsion", "propeller", "Prop FL"),
        ("prop2", "hardware", "propulsion", "propeller", "Prop FR"),
        ("prop3", "hardware", "propulsion", "propeller", "Prop RL"),
        ("prop4", "hardware", "propulsion", "propeller", "Prop RR"),
        ("mount1", "hardware", "propulsion", "motor_mount", "Mount FL"),
        ("mount2", "hardware", "propulsion", "motor_mount", "Mount FR"),
        ("mount3", "hardware", "propulsion", "motor_mount", "Mount RL"),
        ("mount4", "hardware", "propulsion", "motor_mount", "Mount RR"),
        # power
        ("battery", "hardware", "power", "battery", "LiPo Battery"),
        ("pdb", "hardware", "power", "power_distribution", "Power Dist Board"),
        ("bec5v", "hardware", "power", "regulator", "BEC 5V Rail"),
        ("bec12v", "hardware", "power", "regulator", "BEC 12V Rail"),
        ("harness", "hardware", "power", "wiring_harness", "Wiring Harness"),
        # flight_control
        ("fc", "hardware", "flight_control", "autopilot", "Autopilot FC"),
        ("imu_a", "hardware", "flight_control", "imu", "IMU A"),
        ("imu_b", "hardware", "flight_control", "imu", "IMU B"),
        ("accel", "hardware", "flight_control", "accelerometer", "Accelerometer"),
        ("gyro", "hardware", "flight_control", "gyroscope", "Gyroscope"),
        ("baro", "hardware", "flight_control", "barometer", "Barometer"),
        ("mag", "hardware", "flight_control", "magnetometer", "Compass"),
        # navigation
        ("gps", "hardware", "navigation", "gps", "GPS Receiver"),
        ("rtk", "hardware", "navigation", "rtk", "RTK Module"),
        ("optflow", "hardware", "navigation", "optical_flow", "Optical Flow"),
        # comms
        ("rx", "hardware", "comms", "rc_receiver", "RC Receiver"),
        ("telem", "hardware", "comms", "telemetry_radio", "Telemetry Radio"),
        ("ant_rc", "hardware", "comms", "antenna", "RC Antenna"),
        ("ant_telem", "hardware", "comms", "antenna", "Telem Antenna"),
        ("datalink", "hardware", "comms", "datalink", "Datalink Unit"),
        # payload
        ("camera", "hardware", "payload", "camera", "Camera"),
        ("gimbal", "hardware", "payload", "gimbal", "Gimbal"),
        ("lidar", "hardware", "payload", "lidar", "Lidar"),
        # airframe
        ("frame", "hardware", "airframe", "frame", "Airframe"),
        ("gear", "hardware", "airframe", "landing_gear", "Landing Gear"),
        # software
        ("firmware", "software", "software", "firmware", "Bootloader/Firmware"),
        ("flightstack", "software", "software", "flight_stack", "Flight Stack Scheduler"),
        ("drv_core", "software", "software", "sensor_driver", "Sensor Driver Core"),
        ("drv_imu", "software", "software", "sensor_driver", "IMU Driver"),
        ("drv_gps", "software", "software", "sensor_driver", "GPS Driver"),
        ("drv_baro", "software", "software", "sensor_driver", "Baro Driver"),
        ("ekf", "software", "software", "estimator", "EKF Estimator"),
        ("controller", "software", "software", "controller", "Attitude Controller"),
        ("mixer", "software", "software", "motor_mixer", "Motor Mixer"),
        ("failsafe", "software", "software", "failsafe", "Failsafe/Geofence"),
        ("telemstack", "software", "software", "telemetry_stack", "Telemetry Stack"),
        ("paramstore", "software", "software", "parameter_store", "Parameter Store"),
    ]

    spine_ids = [s[0] for s in spine]
    spine_set = set(spine_ids)

    # ----- generic filler nodes (noise) ------------------------------------
    hw_subsystems = ["propulsion", "power", "flight_control", "navigation",
                     "comms", "payload", "airframe"]
    hw_types = {
        "propulsion": ["motor", "esc", "propeller", "motor_mount", "fastener"],
        "power": ["regulator", "wiring_harness", "connector", "fuse", "capacitor"],
        "flight_control": ["sensor", "io_expander", "buzzer", "led", "switch"],
        "navigation": ["gps", "antenna", "ground_marker", "beacon"],
        "comms": ["antenna", "filter", "amplifier", "connector"],
        "payload": ["camera", "mount", "cable", "lens"],
        "airframe": ["arm", "standoff", "cover", "damper", "bracket"],
    }

    filler = []
    # sort the subsystem pool first so rng.choice ordering is deterministic
    for i in range(1, N_FILLER_HW + 1):
        sub = str(rng.choice(sorted(hw_subsystems)))
        ctype = str(rng.choice(sorted(hw_types[sub])))
        nid = f"hw{i:03d}"
        filler.append((nid, "hardware", sub, ctype, f"{ctype.title()} {i:03d}"))

    sw_types = ["sensor_driver", "service", "library", "logger", "watchdog",
                "calibration", "interface"]
    for i in range(1, N_FILLER_SW + 1):
        ctype = str(rng.choice(sorted(sw_types)))
        nid = f"sw{i:03d}"
        filler.append((nid, "software", "software", ctype, f"{ctype.title()} {i:03d}"))

    all_nodes = spine + filler
    node_id = np.array([n[0] for n in all_nodes])
    kind = np.array([n[1] for n in all_nodes])
    subsystem = np.array([n[2] for n in all_nodes])
    component_type = np.array([n[3] for n in all_nodes])
    label = np.array([n[4] for n in all_nodes])
    n = len(node_id)
    idx = {nid: i for i, nid in enumerate(node_id)}

    # ----- node attributes -------------------------------------------------
    vendor = rng.choice(VENDORS, size=n)
    criticality = rng.integers(1, 6, size=n)
    redundant = (rng.random(n) < 0.12).astype(int)

    mass_g = np.where(kind == "hardware",
                      np.clip(rng.gamma(2.0, 18.0, size=n), 1, 600).round(1),
                      np.nan)
    power_draw_w = np.where(kind == "hardware",
                            np.clip(rng.gamma(1.6, 1.4, size=n), 0.0, 60.0).round(2),
                            np.nan)

    # force realistic attributes for the named spine + planted nodes
    def setattrs(nid, **kw):
        i = idx[nid]
        for k, v in kw.items():
            if k == "vendor":
                vendor[i] = v
            elif k == "criticality":
                criticality[i] = v
            elif k == "redundant":
                redundant[i] = v
            elif k == "mass_g":
                mass_g[i] = v
            elif k == "power_draw_w":
                power_draw_w[i] = v

    # power board: moderate criticality LABEL on attributes (don't reveal SPOF)
    setattrs("pdb", vendor="Voltspan", criticality=3, redundant=0,
             mass_g=42.0, power_draw_w=1.2)
    setattrs("battery", vendor="Voltspan", criticality=5, redundant=0,
             mass_g=320.0, power_draw_w=0.0)
    setattrs("fc", vendor="PixHawk", criticality=5, redundant=0,
             mass_g=38.0, power_draw_w=2.5)
    setattrs("ekf", vendor="PixHawk", criticality=4, redundant=0)
    setattrs("controller", vendor="PixHawk", criticality=5, redundant=0)
    # dual IMUs marked redundant (the redundancy illusion)
    setattrs("imu_a", vendor="PixHawk", criticality=4, redundant=1,
             mass_g=4.0, power_draw_w=0.3)
    setattrs("imu_b", vendor="Aerex", criticality=4, redundant=1,
             mass_g=4.0, power_draw_w=0.3)
    # GPS + RTK also "redundant" position sources
    setattrs("gps", vendor="NaviCore", criticality=3, redundant=1)
    setattrs("rtk", vendor="NaviCore", criticality=3, redundant=1)
    # legacy driver core: single vendor, moderate criticality flag
    setattrs("drv_core", vendor="Aerex", criticality=3, redundant=0)
    # vendor lock-in cluster
    setattrs("datalink", vendor=VENDOR_LOCK_VENDOR)
    setattrs("telem", vendor=VENDOR_LOCK_VENDOR)
    setattrs("ant_telem", vendor=VENDOR_LOCK_VENDOR)
    setattrs("optflow", vendor=VENDOR_LOCK_VENDOR)

    # ----- build dependency edges ------------------------------------------
    edges = {}   # (src, dst) -> coupling_strength

    def add_edge(src, dst, w=None):
        if src == dst:
            return
        key = (src, dst)
        if w is None:
            w = int(np.clip(rng.integers(1, 6), 1, 5))
        # keep the strongest coupling if duplicated
        edges[key] = max(edges.get(key, 0), w)

    # ---- (1) realistic spine dependencies (domain-true) -------------------
    spine_edges = [
        # propulsion: motor needs ESC + mount + prop; ESC needs power + mixer
        ("mot1", "esc1", 5), ("mot2", "esc2", 5), ("mot3", "esc3", 5), ("mot4", "esc4", 5),
        ("mot1", "mount1", 4), ("mot2", "mount2", 4), ("mot3", "mount3", 4), ("mot4", "mount4", 4),
        ("mot1", "prop1", 3), ("mot2", "prop2", 3), ("mot3", "prop3", 3), ("mot4", "prop4", 3),
        ("esc1", "pdb", 5), ("esc2", "pdb", 5), ("esc3", "pdb", 5), ("esc4", "pdb", 5),
        ("esc1", "mixer", 4), ("esc2", "mixer", 4), ("esc3", "mixer", 4), ("esc4", "mixer", 4),
        # power chain
        ("pdb", "battery", 5),
        ("bec5v", "pdb", 5), ("bec12v", "pdb", 5),
        ("harness", "pdb", 3),
        ("pdb", "harness", 4),
        # flight control hardware powered via the 5V rail (-> pdb transitively)
        ("fc", "bec5v", 5),
        ("imu_a", "bec5v", 4), ("imu_b", "bec5v", 4),
        ("accel", "bec5v", 3), ("gyro", "bec5v", 3),
        ("baro", "bec5v", 3), ("mag", "bec5v", 3),
        ("fc", "firmware", 5),
        ("fc", "flightstack", 5),
        # sensors feed the FC / drivers
        ("imu_a", "drv_imu", 3), ("imu_b", "drv_imu", 3),
        ("accel", "imu_a", 2), ("gyro", "imu_a", 2),
        ("baro", "drv_baro", 3),
        ("mag", "drv_core", 2),
        # navigation hardware
        ("gps", "bec5v", 3), ("rtk", "bec5v", 3), ("optflow", "bec5v", 3),
        ("rtk", "gps", 4),
        ("gps", "drv_gps", 3), ("rtk", "drv_gps", 3),
        # comms
        ("rx", "bec5v", 3), ("telem", "bec5v", 3),
        ("rx", "ant_rc", 4), ("telem", "ant_telem", 4),
        ("datalink", "telem", 4),
        ("fc", "rx", 4),
        # payload
        ("camera", "bec12v", 4), ("gimbal", "bec12v", 4), ("lidar", "bec12v", 4),
        ("gimbal", "camera", 3),
        ("camera", "frame", 2), ("gimbal", "frame", 2),
        # airframe
        ("frame", "gear", 1),
        ("mount1", "frame", 3), ("mount2", "frame", 3),
        ("mount3", "frame", 3), ("mount4", "frame", 3),
        # ---- software stack ----
        ("flightstack", "firmware", 5),
        ("drv_imu", "drv_core", 5),
        ("drv_gps", "drv_core", 5),
        ("drv_baro", "drv_core", 5),
        ("drv_core", "firmware", 4),
        ("ekf", "drv_imu", 5),
        ("ekf", "drv_gps", 4),
        ("ekf", "drv_baro", 3),
        ("controller", "ekf", 5),
        ("mixer", "controller", 5),
        ("failsafe", "ekf", 4),
        ("failsafe", "rx", 3),
        ("failsafe", "controller", 3),
        ("telemstack", "telem", 4),
        ("telemstack", "ekf", 3),
        ("flightstack", "paramstore", 3),
        ("controller", "paramstore", 2),
        ("ekf", "paramstore", 2),
        ("mixer", "paramstore", 2),
        # FC software depends on FC hardware abstraction
        ("flightstack", "drv_core", 3),
    ]
    for s, d, w in spine_edges:
        add_edge(s, d, w)

    # ---- (2) REDUNDANCY ILLUSION: dual IMUs + GPS/RTK both feed single EKF -
    add_edge("ekf", "imu_a", 5)
    add_edge("ekf", "imu_b", 5)       # both IMUs -> same single EKF
    add_edge("ekf", "gps", 4)
    add_edge("ekf", "rtk", 4)         # both position sources -> same single EKF
    add_edge("ekf", "optflow", 3)

    # ---- (3) FEEDBACK LOOPS / CYCLES (graph is not a DAG) -----------------
    # controller <-> ekf (estimator uses control input feedforward)
    add_edge("ekf", "controller", 3)         # closes controller<->ekf loop
    # fc <-> esc telemetry: ESCs report back rpm/temp to the FC
    add_edge("fc", "esc1", 2)
    add_edge("esc1", "fc", 2)                 # closes fc<->esc1 loop
    # mixer -> esc -> ... and fc consumes mixer output via flightstack
    add_edge("flightstack", "mixer", 3)
    add_edge("mixer", "flightstack", 2)       # small scheduler<->mixer loop

    # ---- (4) HIDDEN SPOF: route a large share of nodes to power via pdb ----
    # Many hardware components draw power; we wire them to a rail (bec5v/bec12v/
    # harness) -> all rails depend on pdb -> pdb gets huge TRANSITIVE in-reach
    # while its DIRECT in-degree stays moderate (only the rails + escs touch it).
    rails = ["bec5v", "bec12v", "harness"]
    hw_idx = [i for i in range(n) if kind[i] == "hardware"
              and node_id[i] not in {"pdb", "battery"}]
    # choose ~SPOF_FANIN hardware nodes to draw from a rail (sorted for determinism)
    hw_pool = sorted(node_id[i] for i in hw_idx)
    chosen = rng.choice(hw_pool, size=min(SPOF_FANIN, len(hw_pool)), replace=False)
    for nid in chosen:
        rail = str(rng.choice(rails))
        add_edge(str(nid), rail, w=int(rng.integers(2, 5)))

    # ---- (5) LEGACY MODULE: drv_core gets high downstream reach -----------
    sw_pool = sorted(node_id[i] for i in range(n)
                     if kind[i] == "software" and node_id[i] != "drv_core")
    legacy_consumers = rng.choice(sw_pool, size=min(LEGACY_REACH, len(sw_pool)),
                                  replace=False)
    for nid in legacy_consumers:
        add_edge(str(nid), "drv_core", w=int(rng.integers(2, 6)))

    # ---- (6) VENDOR LOCK-IN: NaviCore parts depend on each other tightly --
    lock_nodes = [node_id[i] for i in range(n) if vendor[i] == VENDOR_LOCK_VENDOR
                  and subsystem[i] in {"navigation", "comms"}]
    lock_nodes = sorted(lock_nodes)
    # a proprietary datalink protocol: chain + mutual coupling within the vendor
    for a in range(len(lock_nodes)):
        for b in range(len(lock_nodes)):
            if a == b:
                continue
            if rng.random() < 0.45:
                add_edge(lock_nodes[a], lock_nodes[b], w=int(rng.integers(3, 6)))

    # Power-sink nodes: power flows strictly DOWN into them, so they must never
    # be the SOURCE of a noise edge (this keeps pdb the sole gateway to battery
    # = a genuine articulation point for power).
    POWER_SINKS = {"battery", "pdb", "bec5v", "bec12v", "harness"}

    # ---- (7) MODULARITY: dense within-subsystem, sparse cross-subsystem ----
    by_sub = {}
    for i in range(n):
        by_sub.setdefault(subsystem[i], []).append(node_id[i])
    for sub, members in by_sub.items():
        members = sorted(members)
        for a in members:
            for b in members:
                if a == b:
                    continue
                if rng.random() < WITHIN_LINK_P * 0.18:
                    if a in POWER_SINKS:
                        continue
                    add_edge(a, b, w=int(rng.integers(1, 4)))
    # sparse cross-subsystem integration seams
    all_sorted = sorted(node_id.tolist())
    for a in all_sorted:
        if rng.random() < CROSS_LINK_P:
            if a in POWER_SINKS:
                continue
            # pick a target in a DIFFERENT subsystem
            sa = subsystem[idx[a]]
            others = [x for x in all_sorted
                      if subsystem[idx[x]] != sa and x != a]
            if others:
                b = str(rng.choice(others))
                add_edge(a, b, w=int(rng.integers(1, 4)))

    # ---- (8) connect filler software to spine so they aren't isolated ------
    spine_sw = ["firmware", "flightstack", "drv_core", "ekf", "controller",
                "paramstore"]
    for i in range(n):
        if kind[i] == "software" and node_id[i].startswith("sw"):
            if rng.random() < 0.85:
                add_edge(node_id[i], str(rng.choice(sorted(spine_sw))),
                         w=int(rng.integers(1, 4)))
    # connect filler hardware to its subsystem spine anchor or a rail
    anchors = {"propulsion": "frame", "power": "bec5v", "flight_control": "fc",
               "navigation": "gps", "comms": "telem", "payload": "frame",
               "airframe": "frame"}
    for i in range(n):
        if kind[i] == "hardware" and node_id[i].startswith("hw"):
            if rng.random() < 0.80:
                anchor = anchors.get(subsystem[i], "frame")
                add_edge(node_id[i], anchor, w=int(rng.integers(1, 4)))

    # ----- emit ------------------------------------------------------------
    edge_rows = [{"from_id": s, "to_id": d, "dep_type": _dep_type(s, d, kind, idx,
                                                                  subsystem),
                  "coupling_strength": w}
                 for (s, d), w in edges.items()]
    edges_df = pd.DataFrame(edge_rows)
    # stable ordering
    edges_df = edges_df.sort_values(["from_id", "to_id"]).reset_index(drop=True)

    nodes = pd.DataFrame({
        "node_id": node_id,
        "kind": kind,
        "subsystem": subsystem,
        "component_type": component_type,
        "vendor": vendor,
        "criticality": criticality,
        "redundant": redundant,
        "mass_g": mass_g,
        "power_draw_w": power_draw_w,
        "label": label,
    })

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges_df.to_csv(HERE / "edges.csv", index=False)

    kinds = dict(pd.Series(kind).value_counts())
    print(f"drone-components: {len(nodes)} nodes "
          f"({kinds.get('hardware', 0)} hardware, {kinds.get('software', 0)} software), "
          f"{len(edges_df)} dependency edges.")


def _dep_type(src, dst, kind, idx, subsystem):
    """Infer a plausible dependency type for an edge (power/data/control/
    mechanical/software). Deterministic from the endpoints' kind/subsystem."""
    ks, kd = kind[idx[src]], kind[idx[dst]]
    ss, sd = subsystem[idx[src]], subsystem[idx[dst]]
    if dst in {"pdb", "battery", "bec5v", "bec12v", "harness"}:
        return "power"
    if ks == "software" and kd == "software":
        return "software"
    if kd == "software" or ks == "software":
        return "data"
    if sd == "propulsion" and dst.startswith(("esc", "mixer", "mot")):
        return "control"
    if dst in {"frame", "gear"} or dst.startswith("mount"):
        return "mechanical"
    if ss == "propulsion" or sd == "propulsion":
        return "control"
    return "data"


if __name__ == "__main__":
    main()
```

---

## `data/projects/drone-components/load.R`

```r
#' @name load.R
#' @title Load the `drone-components` project network (R)
#' @description
#'
#' Reads the two CSVs in this folder and builds a directed, weighted igraph
#' object: a UAV functional dependency graph (`A -> B` means *A depends on /
#' requires B to function*). Run it straight (`Rscript load.R`) for a quick
#' summary, or `source()` it and call `load_drone()` in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "drone-components")

#' Load the node table (one row per component).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per dependency).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Build the directed, weighted dependency graph.
#'
#' Edges are weighted by `coupling_strength`. Direction is `from_id -> to_id`,
#' i.e. `from_id` depends on / requires `to_id` to function. The graph is
#' intentionally NOT a clean DAG.
load_drone <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = TRUE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$coupling_strength
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n\U0001F681 drone-components (R)\n")
  cat("   UAV functional dependency graph; A -> B means A requires B to function.\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_drone(nodes, edges)

  nh <- sum(nodes$kind == "hardware")
  ns <- sum(nodes$kind == "software")
  cat(sprintf("✅ Loaded %d components (%d hardware, %d software) and %d dependency edges.\n",
              nrow(nodes), nh, ns, nrow(edges)))
  cat(sprintf("\U0001F517 Directed: %s | is DAG: %s | total coupling: %s\n",
              is_directed(g), is_dag(g),
              format(sum(edges$coupling_strength), big.mark = ",")))
  ind <- igraph::degree(g, mode = "in")
  outd <- igraph::degree(g, mode = "out")
  cat(sprintf("\U0001F4CA Max in-degree: %d (%s) | max out-degree: %d (%s)\n",
              max(ind), names(which.max(ind)), max(outd), names(which.max(outd))))
  cat("\U0001F389 Graph ready. Object `g` is a directed, weighted igraph.\n")
}
```

---

## `data/projects/drone-components/load.py`

```python
"""Load the `drone-components` project network (Python).

Reads the two CSVs in this folder and builds a directed, weighted python-igraph
object: a UAV functional dependency graph (``A -> B`` means *A depends on / requires
B to function*). Run it straight (``python load.py``) for a quick summary, or
import ``load_drone()`` into your own script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per component (hardware or software module)."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per dependency (from_id requires to_id)."""
    return pd.read_csv(HERE / "edges.csv")


def load_drone(nodes: pd.DataFrame | None = None,
               edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the directed, weighted dependency graph (weight = ``coupling_strength``).

    Direction is ``from_id -> to_id``: ``from_id`` depends on / requires
    ``to_id`` to function. The graph is intentionally NOT a clean DAG.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=True, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["coupling_strength"]
    return g


if __name__ == "__main__":
    print("\n\U0001F681 drone-components (Python)")
    print("   UAV functional dependency graph; A -> B means A requires B to function.\n")

    nodes = load_nodes()
    edges = load_edges()
    g = load_drone(nodes, edges)

    kinds = nodes["kind"].value_counts()
    print(f"✅ Loaded {len(nodes)} components "
          f"({kinds.get('hardware', 0)} hardware, {kinds.get('software', 0)} software) "
          f"and {len(edges)} dependency edges.")
    print(f"\U0001F517 Directed: {g.is_directed()} | is DAG: {g.is_dag()} | "
          f"total coupling: {edges['coupling_strength'].sum():,}")
    indeg = g.indegree()
    outdeg = g.outdegree()
    names = g.vs["name"]
    i_max = max(range(len(indeg)), key=lambda i: indeg[i])
    o_max = max(range(len(outdeg)), key=lambda i: outdeg[i])
    print(f"\U0001F4CA Max in-degree: {indeg[i_max]} ({names[i_max]}) | "
          f"max out-degree: {outdeg[o_max]} ({names[o_max]})")
    print("\U0001F389 Graph ready. Object `g` is a directed, weighted igraph.")
```

---

## `data/projects/financial-contagion/README.md`

# financial-contagion

*A directed interbank exposure network across three periods of a financial
crisis: who lent to whom, before the storm, during the crash, and in the calmer
aftermath.*

![Preview of the financial-contagion network](thumb.png)

## At a glance

| | |
|---|---|
| **Direction** | Directed (exposure runs creditor → debtor) |
| **Weights** | Weighted (`exposure` = dollars at risk on each link) |
| **Modality** | Single-mode — one node kind (firms), typed by `type` |
| **Temporal** | Yes — one row per (creditor, debtor, **period**: before / during / after) |
| **Nodes** | 220 firms (111 banks, 71 hedge funds, 34 insurers, 4 CCPs) |
| **Edges** | 1,701 (before 838 · during 609 · after 254) |
| **Files** | `nodes.csv`, `edges.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

Banks, hedge funds, insurers, and central counterparties (**CCPs**) lend to and
borrow from one another, forming a web of **financial exposures**. Each directed
edge points from a **creditor** to a **debtor** and carries the dollar size of
the exposure — the amount the lender stands to lose if the borrower can't pay.
The network is recorded across three periods: a calm, densely interlinked
**before**; the **during** of a crisis as positions unwind; and the sparser
**after** of a tentative recovery. Each firm carries its size (`assets`), its
`leverage`, its `type`, and its home `region`.

This is a network for **systemic risk, criticality, and cascade** questions.
Some things worth investigating:

- If one firm fails, who is exposed — and does the damage stop there, or ripple
  outward? Can you measure how far a shock travels?
- Degree tells you who has the most counterparties. But who actually sits *between*
  everyone else — whose failure would sever the most connections? Are those the
  same firms?
- Exposures look fine one firm at a time. Do they look fine in aggregate? Are
  lots of firms quietly crowded into the same handful of borrowers?
- Did everyone get caught off guard, or did some firms pull back *before* the
  crash? How would you tell who saw it coming?
- How does the network reshape itself afterward? Is recovery a return to the old
  structure, or a flight toward something safer?

> **Note.** The interesting findings here are deliberately *not* documented. "Big
> firms have more exposures" is the starting point, not a finding. Look for the
> structure that size and volume don't explain.

## `nodes.csv`

One row per firm.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique firm key. Referenced by edges. | character | `F001`, `F063` |
| `type` | Firm type | Kind of financial institution. | character | `bank`, `hedge_fund`, `insurer`, `ccp` |
| `assets` | Total assets | Balance-sheet size in $ billions (firm "size"). | double | `6.71`, `39.82` |
| `leverage` | Leverage ratio | Assets-to-equity ratio; higher = more fragile. | double | `10.07`, `38.0` |
| `region` | Region | Home region of the firm. | character | `NorthAm`, `Europe`, `Asia`, `LatAm` |
| `label` | Display name | Human-readable label. (`name` is avoided — python-igraph reserves it for the ID.) | character | `Bank 002`, `CCP 029` |

## `edges.csv`

One row per (creditor, debtor, period). Directed: exposure runs from `from_id`
(the creditor / lender) to `to_id` (the debtor / borrower).

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | Creditor node ID | The lending firm (bears the loss if the debtor fails; joins to `nodes.csv`). | character | `F001`, `F108` |
| `to_id` | Debtor node ID | The borrowing firm (joins to `nodes.csv`). | character | `F062`, `F079` |
| `period` | Period | Phase of the crisis the exposure was recorded in. | character | `before`, `during`, `after` |
| `exposure` | Exposure | Dollars at risk on this link (the edge weight; arbitrary units). | double | `4.34`, `2.30` |

## Load it

```bash
Rscript data/projects/financial-contagion/load.R     # R    (igraph)
python  data/projects/financial-contagion/load.py     # Python (python-igraph)
```

Both build a directed, weighted `igraph` graph and print a one-screen summary. In
the [R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**financial-contagion** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/financial-contagion>

---

## `data/projects/financial-contagion/_generate.py`

```python
"""Generate the `financial-contagion` project network (deterministic).

A directed interbank / financial-exposure network across three periods of a
crisis:
  - period = "before"   (calm; dense interlinked exposures)
  - period = "during"   (the crash; one firm fails and a cascade unwinds)
  - period = "after"    (recovery; sparser, flight-to-quality star structure)

Nodes are financial firms; an edge is a directed exposure (a loan / credit line)
from a creditor to a debtor, weighted by exposure dollars, one row per
(creditor, debtor, period).

Node attributes: type (bank / hedge_fund / insurer / ccp), assets (size),
leverage, region, label.

Design parameters (the only record of the planted structure):
  - FAIL_NODE: one over-leveraged, mid-size firm fails DURING. Its creditor
    edges vanish, and several of THOSE creditors then drop edges too (a
    measurable cascade radius around it).
  - CCP_HUB: a central counterparty has modest degree but the highest
    betweenness (a hidden systemic hub intermediating most flows).
  - HERD: a large cluster of firms all lend to the same handful of debtors
    (correlated / overlapping common exposure).
  - FRONT_RUNNERS: a few firms sharply cut outgoing exposure before->during
    (they saw it coming) while everyone else stays exposed until the crash.
  - FLIGHT: surviving firms rewire toward low-leverage bank/ccp nodes AFTER;
    the network is sparser and more star-like.

Run:
    python data/projects/financial-contagion/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

N_FIRMS = 220
PERIODS = ["before", "during", "after"]
REGIONS = ["NorthAm", "Europe", "Asia", "LatAm"]
TYPES = ["bank", "hedge_fund", "insurer", "ccp"]

# --- planted parameters -----------------------------------------------------
N_CCP = 4                       # central counterparties (systemic intermediaries)
N_HERD = 55                     # firms in the common-exposure herd
N_HERD_TARGETS = 5              # the handful of debtors the herd all lends to
N_FRONT_RUNNERS = 8             # firms that cut exposure pre-crash
FRONT_RUNNER_CUT = 0.20         # they keep only ~20% of out-exposure during
FAIL_LEVERAGE = 38.0            # leverage of the firm that fails (top-decile)
CASCADE_DROP = 0.55            # share of failed-firm creditors who then cut too
DENSIFY = {"before": 1.0, "during": 0.72, "after": 0.40}  # tie-rate by period


def _gini(x: np.ndarray) -> float:
    x = np.sort(np.asarray(x, dtype=float))
    n = len(x)
    if n == 0 or x.sum() == 0:
        return 0.0
    idx = np.arange(1, n + 1)
    return float((2 * (idx * x).sum() - (n + 1) * x.sum()) / (n * x.sum()))


def main() -> None:
    rng = np.random.default_rng(SEED)

    # ----- firms -----------------------------------------------------------
    ftype = rng.choice(["bank", "hedge_fund", "insurer"],
                       size=N_FIRMS, p=[0.5, 0.32, 0.18])
    # designate the central counterparties
    ccp_idx = rng.choice(N_FIRMS, N_CCP, replace=False)
    ftype = ftype.astype(object)
    for c in ccp_idx:
        ftype[c] = "ccp"

    # assets (size, $B), log-normalish; banks & ccp larger on average
    base_assets = rng.lognormal(mean=2.4, sigma=0.9, size=N_FIRMS)
    for i in range(N_FIRMS):
        if ftype[i] == "bank":
            base_assets[i] *= 1.8
        elif ftype[i] == "ccp":
            base_assets[i] *= 2.4
        elif ftype[i] == "hedge_fund":
            base_assets[i] *= 0.7
    assets = np.clip(base_assets, 0.5, None)

    # leverage: hedge funds high, banks moderate, insurers/ccp low; noisy.
    lev = np.empty(N_FIRMS)
    for i in range(N_FIRMS):
        if ftype[i] == "hedge_fund":
            lev[i] = np.clip(rng.normal(14, 6), 3, 45)
        elif ftype[i] == "bank":
            lev[i] = np.clip(rng.normal(9, 3), 2, 22)
        elif ftype[i] == "insurer":
            lev[i] = np.clip(rng.normal(6, 2), 1.5, 14)
        else:  # ccp
            lev[i] = np.clip(rng.normal(3, 1), 1.2, 6)

    region = rng.choice(REGIONS, N_FIRMS)

    firms = pd.DataFrame({
        "node_id": [f"F{i:03d}" for i in range(1, N_FIRMS + 1)],
        "type": ftype,
        "assets": assets.round(2),
        "leverage": lev.round(2),
        "region": region,
        "label": [f"{('CCP' if t == 'ccp' else str(t).replace('_', ' ').title())} {i:03d}"
                  for i, t in zip(range(1, N_FIRMS + 1), ftype)],
    })
    node_ids = list(firms.node_id)
    idx_of = {n: i for i, n in enumerate(node_ids)}
    ccp_ids = [node_ids[c] for c in ccp_idx]

    # ----- choose the failing firm: mid-size, top-decile leverage ----------
    mid_mask = (assets > np.quantile(assets, 0.35)) & (assets < np.quantile(assets, 0.65))
    cand = np.where(mid_mask & (ftype == "hedge_fund"))[0]
    if len(cand) == 0:
        cand = np.where(mid_mask)[0]
    fail_i = int(cand[np.argmax(lev[cand])])
    # force its leverage to the planted top-decile value
    lev[fail_i] = FAIL_LEVERAGE
    firms.loc[fail_i, "leverage"] = FAIL_LEVERAGE
    fail_id = node_ids[fail_i]

    # ----- structural sets -------------------------------------------------
    # herd: a cluster of firms all lending to the same few debtors
    herd_ids = list(rng.choice([n for n in node_ids if n != fail_id],
                               N_HERD, replace=False))
    herd_targets = list(rng.choice([n for n in node_ids
                                    if n not in herd_ids and n != fail_id],
                                   N_HERD_TARGETS, replace=False))
    # front-runners: firms that cut outgoing exposure pre-crash
    front_runners = set(rng.choice([n for n in node_ids if n != fail_id],
                                   N_FRONT_RUNNERS, replace=False))
    # low-leverage "quality" nodes (flight destinations after the crash)
    quality_ids = [n for n in node_ids
                   if firms.at[idx_of[n], "type"] in ("bank", "ccp")
                   and firms.at[idx_of[n], "leverage"] <= 7]

    # ----- systemic hub design --------------------------------------------
    # One CCP is the SYSTEMIC bridge: firms split into two camps, and almost the
    # only path between them runs through this CCP. That gives it the highest
    # betweenness while its degree stays modest (a hidden systemic hub).
    systemic_ccp = ccp_ids[0]
    sys_i = idx_of[systemic_ccp]
    camp = rng.integers(0, 2, N_FIRMS)        # camp 0 / camp 1
    camp[sys_i] = -1                          # the hub belongs to neither camp
    camp_of = {n: int(camp[idx_of[n]]) for n in node_ids}
    # a modest set of "gateway" firms in each camp connect to the systemic CCP
    camp0 = [n for n in node_ids if camp_of[n] == 0]
    camp1 = [n for n in node_ids if camp_of[n] == 1]
    gateways0 = list(rng.choice(camp0, min(9, len(camp0)), replace=False))
    gateways1 = list(rng.choice(camp1, min(9, len(camp1)), replace=False))
    gateways = set(gateways0 + gateways1)

    # base "connectivity" per node ~ assets (bigger firms have more links)
    connect = assets / assets.mean()

    def exposure_amt(creditor, debtor):
        a = assets[idx_of[creditor]]
        return float(rng.gamma(2.0, 1.0) * (1.0 + 0.15 * a))

    rows = []

    def add_edge(seen, creditor, debtor, period, scale=1.0):
        if creditor == debtor:
            return
        # the failed firm has no exposures (in OR out) once it fails
        if period in ("during", "after") and debtor == fail_id:
            return
        amt = exposure_amt(creditor, debtor) * scale
        key = debtor
        if key in seen:
            seen[key] += amt
        else:
            seen[key] = amt

    # who lent TO the failed firm "before" (its creditors) -> needed for cascade
    fail_creditors_before = []

    for period in PERIODS:
        rate = DENSIFY[period]
        for creditor in node_ids:
            # the failed firm has NO outgoing/incoming edges during & after
            if period in ("during", "after") and creditor == fail_id:
                continue

            base_deg = max(0.4, 2.6 * connect[idx_of[creditor]] * rate)

            # front-runners slash their out-exposure during the crash
            if period == "during" and creditor in front_runners:
                base_deg *= FRONT_RUNNER_CUT

            n_ties = rng.poisson(base_deg)
            seen = {}

            # ---- systemic CCP as the bridge between the two camps -----------
            # gateways route exposure THROUGH the systemic CCP; the CCP re-lends
            # into the OTHER camp. Few links, but it sits on most cross-camp
            # paths -> highest betweenness, modest degree.
            if period in ("before", "during"):
                if creditor in gateways:
                    add_edge(seen, creditor, systemic_ccp, period)
                if creditor == systemic_ccp:
                    # lend a modest amount into both camps' gateways
                    for t in (gateways0 + gateways1):
                        if rng.random() < 0.55:
                            add_edge(seen, creditor, t, period)

            # other (non-systemic) CCPs are ordinary clearing nodes
            if creditor in ccp_ids and creditor != systemic_ccp:
                targets = rng.choice([n for n in node_ids if n != creditor],
                                     size=min(6, n_ties + 3), replace=False)
                for t in targets:
                    add_edge(seen, creditor, t, period)

            # ---- herd: herd members lend to the shared targets --------------
            if creditor in herd_ids and period in ("before", "during"):
                for t in herd_targets:
                    if rng.random() < 0.75:
                        add_edge(seen, creditor, t, period, scale=1.3)

            # ---- ordinary exposures (mostly within one's own camp) ----------
            my_camp = camp_of[creditor]
            same_camp = camp0 if my_camp == 0 else (camp1 if my_camp == 1
                                                    else node_ids)
            for _ in range(int(n_ties)):
                if period == "after":
                    # FLIGHT TO QUALITY: route toward low-leverage bank/ccp
                    if quality_ids and rng.random() < 0.7:
                        debtor = str(rng.choice(quality_ids))
                    else:
                        debtor = str(rng.choice(node_ids))
                else:
                    # before/during: lend mostly within camp (keeps the systemic
                    # CCP as the scarce cross-camp bridge), weighted by size
                    pool = same_camp if rng.random() < 0.9 else node_ids
                    w = np.array([connect[idx_of[n]] for n in pool], dtype=float)
                    debtor = str(rng.choice(pool, p=w / w.sum()))
                add_edge(seen, creditor, debtor, period)

            # before: some firms lend to the failing firm (its creditors)
            if period == "before" and creditor != fail_id and rng.random() < 0.18:
                add_edge(seen, creditor, fail_id, period, scale=1.4)
                fail_creditors_before.append(creditor)

            for debtor, amt in seen.items():
                rows.append({
                    "from_id": creditor,       # creditor (lender)
                    "to_id": debtor,           # debtor (borrower)
                    "period": period,
                    "exposure": round(amt, 2),
                })

    # ---- cascade: a share of the failed firm's creditors DROP edges during -
    # We model this by removing a fraction of those creditors' DURING out-edges.
    edges = pd.DataFrame(rows)
    fail_creditors_before = list(dict.fromkeys(fail_creditors_before))
    cascade_hit = set(rng.choice(
        fail_creditors_before,
        max(1, int(len(fail_creditors_before) * CASCADE_DROP)),
        replace=False)) if fail_creditors_before else set()

    keep = np.ones(len(edges), dtype=bool)
    for i, r in edges.iterrows():
        if r["period"] == "during" and r["from_id"] in cascade_hit:
            # each cascade-hit creditor drops ~60% of its during edges
            if rng.random() < 0.6:
                keep[i] = False
    edges = edges[keep].reset_index(drop=True)

    firms.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)
    by_p = edges.period.value_counts().to_dict()
    print(f"financial-contagion: {len(firms)} nodes "
          f"({(firms.type=='bank').sum()} banks, {(firms.type=='hedge_fund').sum()} hedge funds, "
          f"{(firms.type=='insurer').sum()} insurers, {(firms.type=='ccp').sum()} ccps), "
          f"{len(edges)} edges "
          f"(before={by_p.get('before',0)}, during={by_p.get('during',0)}, "
          f"after={by_p.get('after',0)}); exposure Gini(before)="
          f"{_gini(edges[edges.period=='before'].groupby('to_id').exposure.sum().values):.2f}.")


if __name__ == "__main__":
    main()
```

---

## `data/projects/financial-contagion/load.R`

```r
#' @name load.R
#' @title Load the `financial-contagion` project network (R)
#' @description
#'
#' Reads the two CSVs in this folder and builds a directed, weighted igraph
#' object: directed financial exposures (creditor -> debtor) among ~220 firms
#' across three periods of a crisis (before / during / after). Run it straight
#' (`Rscript load.R`) for a quick summary, or `source()` it and call
#' `load_contagion()` to get the graph in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "financial-contagion")

#' Load the node table (one row per firm).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per creditor x debtor x period).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Build the directed, weighted graph.
#'
#' Edges are weighted by `exposure` (dollars at risk). Because the data is
#' temporal (a `period` column: before/during/after), an exposure between the
#' same pair can appear up to 3 times; igraph keeps them as parallel edges, so
#' filter to one `period` first if you want a single-period graph.
load_contagion <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = TRUE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$exposure
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n\U0001F3E6 financial-contagion (R)\n")
  cat("   Directed creditor -> debtor exposures; before / during / after a crisis.\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_contagion(nodes, edges)

  cat(sprintf("✅ Loaded %d nodes (%d banks, %d hedge funds, %d insurers, %d ccps) and %d edges.\n",
              nrow(nodes), sum(nodes$type == "bank"), sum(nodes$type == "hedge_fund"),
              sum(nodes$type == "insurer"), sum(nodes$type == "ccp"), nrow(edges)))
  for (p in c("before", "during", "after")) {
    cat(sprintf("   period %-7s: %d exposures\n", p, sum(edges$period == p)))
  }
  cat(sprintf("\U0001F517 Directed: %s | total exposure: %s\n",
              is_directed(g), format(round(sum(edges$exposure)), big.mark = ",")))
  cat("\U0001F389 Graph ready. Object `g` is a directed, weighted igraph.\n")
}
```

---

## `data/projects/financial-contagion/load.py`

```python
"""Load the `financial-contagion` project network (Python).

Reads the two CSVs in this folder and builds a directed, weighted python-igraph
object: directed financial exposures (creditor -> debtor) among ~220 firms across
three periods of a crisis (before / during / after). Run it straight
(``python load.py``) for a quick summary, or import ``load_contagion()`` into
your own script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per firm."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per creditor x debtor x period."""
    return pd.read_csv(HERE / "edges.csv")


def load_contagion(nodes: pd.DataFrame | None = None,
                   edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the directed, weighted graph (edge weight = ``exposure``).

    The data is temporal (a ``period`` column: before/during/after), so an
    exposure between the same pair can appear up to 3 times as parallel edges.
    Filter to one ``period`` first if you want a single-period graph.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=True, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["exposure"]
    return g


if __name__ == "__main__":
    print("\n\U0001F3E6 financial-contagion (Python)")
    print("   Directed creditor -> debtor exposures; before / during / after a crisis.\n")

    nodes = load_nodes()
    edges = load_edges()
    g = load_contagion(nodes, edges)

    t = nodes["type"].value_counts()
    print(f"✅ Loaded {len(nodes)} nodes "
          f"({t.get('bank',0)} banks, {t.get('hedge_fund',0)} hedge funds, "
          f"{t.get('insurer',0)} insurers, {t.get('ccp',0)} ccps) "
          f"and {len(edges)} edges.")
    for p in ("before", "during", "after"):
        print(f"   period {p:<7}: {(edges['period']==p).sum()} exposures")
    print(f"\U0001F517 Directed: {g.is_directed()} | total exposure: "
          f"{round(edges['exposure'].sum()):,}")
    print("\U0001F389 Graph ready. Object `g` is a directed, weighted igraph.")
```

---

## `data/projects/mutualaid-quake/README.md`

# mutualaid-quake

*Who helped whom in fictional "Eastvale" before, during, and after an
earthquake: a directed neighborhood mutual-aid network of residents and local
organizations.*

![Preview of the mutualaid-quake network](thumb.png)

## At a glance

| | |
|---|---|
| **Direction** | Directed (aid flows from giver → receiver) |
| **Weights** | Weighted (`amount` of aid per edge; `acts` = number of helping acts) |
| **Modality** | Multimodal — 2 node kinds (`resident`, `org`) |
| **Temporal** | Yes — one row per (giver, receiver, **period**: before / during / after) |
| **Nodes** | 250 (222 residents + 28 orgs) |
| **Edges** | 2,935 (before 325 · during 1,899 · after 711) |
| **Files** | `nodes.csv`, `edges.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

When the ground shook in **Eastvale**, neighbors started helping neighbors. This
network records directed acts of **mutual aid** — food, shelter, information, and
money passed from a giver to a receiver — across three periods: the ordinary days
**before** the quake, the acute shock **during** it, and the **after** recovery.
Nodes are individual **residents** (with block, income, tenure, age, and whether
they were civically active before the quake) and local **organizations** —
churches, schools, nonprofits, community centers. Eight sub-neighborhood blocks
(`B1`–`B8`) carve up the town. Each edge carries how much aid moved and how many
separate helping acts it represents.

This is a network for studying **social capital, brokerage, and recovery**. Some
questions worth chewing on:

- Who becomes a hub when disaster strikes? Are the people and places that carry
  the load *during* the shock the same ones who were central *before*?
- Does the *structure* of a sub-neighborhood predict how it fares afterward? Why
  do some blocks bounce back while one seems to stay starved?
- Money isn't everything. Is the wealthiest block also the best connected — or
  could resources and connectedness pull apart?
- Who sits on the most paths during the crisis? Are the key brokers obvious from
  their pre-quake standing, or do new leaders emerge?
- Does the surge of helping fade completely afterward, or does some of it stick —
  and does it stick evenly everywhere?

> **Note.** The interesting findings here are deliberately *not* documented.
> "Everyone helps more during a disaster" is the starting point, not a finding.
> Push past the obvious densification.

## `nodes.csv`

One row per node. Org rows leave the resident-only demographic columns blank.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique key. `P###` resident, `O###` organization. Referenced by edges. | character | `P001`, `O014` |
| `kind` | Node kind | Whether this node is a person or an organization. | character | `resident`, `org` |
| `block` | Sub-neighborhood block | Which of the eight Eastvale blocks the node sits in. | character | `B1`, `B6`, `B8` |
| `income` | Household income | Resident annual household income, USD (blank for orgs). | integer | `62711`, `143919` |
| `tenure` | Housing tenure | Whether the resident owns or rents (blank for orgs). | character | `homeowner`, `renter` |
| `age` | Age | Resident age in years (blank for orgs). | integer | `26`, `71` |
| `prior_civic` | Prior civic engagement | 1 if active in community orgs before the quake, else 0 (orgs are always 1). | integer | `0`, `1` |
| `label` | Display name | Human-readable label. (`name` is avoided — python-igraph reserves it for the ID.) | character | `Resident 001`, `Nonprofit 01` |

## `edges.csv`

One row per (giver, receiver, period). Directed: aid flows from `from_id` to
`to_id`.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | Giver node ID | Node providing the aid (joins to `nodes.csv`). | character | `P002`, `O014` |
| `to_id` | Receiver node ID | Node receiving the aid (joins to `nodes.csv`). | character | `P211`, `O014` |
| `period` | Period | Phase of the disaster the aid occurred in. | character | `before`, `during`, `after` |
| `amount` | Aid amount | Total aid given on this edge in the period (the edge weight; arbitrary units). | double | `20.9`, `120.8` |
| `acts` | Helping acts | Number of distinct helping acts that make up this edge. | integer | `1`, `2` |
| `aid_type` | Aid type | Dominant kind of aid exchanged. | character | `food`, `shelter`, `info`, `money` |
| `cross_block` | Cross-block flag | 1 if giver and receiver are in different blocks, else 0. | integer | `0`, `1` |

## Load it

```bash
Rscript data/projects/mutualaid-quake/load.R     # R    (igraph)
python  data/projects/mutualaid-quake/load.py     # Python (python-igraph)
```

Both build a directed, weighted `igraph` graph and print a one-screen summary. In
the [R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**mutualaid-quake** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/mutualaid-quake>

---

## `data/projects/mutualaid-quake/_generate.py`

```python
"""Generate the `mutualaid-quake` project network (deterministic).

A neighborhood mutual-aid network in fictional "Eastvale" spanning three periods
of an earthquake disaster:
  - period = "before"   (ordinary times, sparse helping)
  - period = "during"   (the shock; helping surges)
  - period = "after"    (recovery; partly persistent)

Nodes are people and organizations across eight sub-neighborhood blocks (B1..B8):
  - ~residents (kind = "resident")
  - ~orgs      (kind = "org") churches, schools, nonprofits, community centers
  -> ~250 nodes total.

Edges are directed acts of aid GIVEN from giver to receiver (food / shelter /
info / money), weighted by amount/frequency, one row per (giver, receiver,
period).

Design parameters (the only record of the planted structure):
  - CIVIC_ACTIVATION: orgs and prior-civic residents are ordinary "before" but
    their out/in strength jumps far more than others "during" (latent social
    capital activates) and decays only partly "after".
  - BRIDGE_RECOVERY: blocks with more cross-block bridging ties receive more aid
    "after" (bridging predicts recovery); STARVED_BLOCK has almost no bridges and
    stays starved.
  - ENCLAVE_BLOCK: one high-income block is internally cohesive but barely linked
    to the rest (external-tie share low despite high income).
  - BROKERS: a few residents with low "before" centrality have the highest
    betweenness "during" (emergent informal leaders / brokers).
  - DENSIFY/PERSIST: edge counts rise "during" then partly persist "after"
    (new ties formed = social capital), non-uniformly across blocks.

Run:
    python data/projects/mutualaid-quake/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

N_RESIDENTS = 222
N_ORGS = 28                       # -> 250 nodes
BLOCKS = [f"B{i}" for i in range(1, 9)]
PERIODS = ["before", "during", "after"]
AID_TYPES = ["food", "shelter", "info", "money"]

# --- planted parameters -----------------------------------------------------
PRIOR_CIVIC_RATE = 0.20          # share of residents civically active pre-quake
CIVIC_ACTIVATION = 3.4           # multiplier on "during" giving for orgs/civic
CIVIC_PERSIST = 1.6              # residual "after" multiplier for them
ENCLAVE_BLOCK = "B6"             # affluent, internally cohesive, externally sparse
ENCLAVE_EXTERNAL_DAMP = 0.12     # enclave cross-block ties scaled way down
STARVED_BLOCK = "B8"             # isolated; almost no bridges; recovers poorly
N_BROKERS = 9                    # emergent informal leaders during the shock
DENSIFY = {"before": 1.0, "during": 3.2, "after": 1.7}  # base tie-rate by period

# per-block "bridging propensity": how readily a block forms cross-block ties.
# High-bridge blocks recover better "after"; enclave & starved are low.
BRIDGE_PROPENSITY = {
    "B1": 1.30, "B2": 1.15, "B3": 1.45, "B4": 1.00,
    "B5": 0.85, "B6": 0.25, "B7": 1.20, "B8": 0.18,
}
# block base income centers (USD), gives a spatial-ish gradient + noise
BLOCK_INCOME = {
    "B1": 62000, "B2": 54000, "B3": 71000, "B4": 48000,
    "B5": 58000, "B6": 138000, "B7": 66000, "B8": 41000,
}


def _gini(x: np.ndarray) -> float:
    x = np.sort(np.asarray(x, dtype=float))
    n = len(x)
    if n == 0 or x.sum() == 0:
        return 0.0
    idx = np.arange(1, n + 1)
    return float((2 * (idx * x).sum() - (n + 1) * x.sum()) / (n * x.sum()))


def main() -> None:
    rng = np.random.default_rng(SEED)

    # ----- residents -------------------------------------------------------
    # assign residents to blocks (enclave & starved a bit smaller)
    block_w = np.array([1.0, 1.0, 1.0, 1.1, 1.0, 0.75, 1.0, 0.7])
    block_w /= block_w.sum()
    res_block = rng.choice(BLOCKS, N_RESIDENTS, p=block_w)

    income = np.array([
        np.clip(BLOCK_INCOME[b] + rng.normal(0, 11000), 18000, 240000)
        for b in res_block
    ])
    tenure = np.where(
        rng.random(N_RESIDENTS) < (0.35 + 0.0000035 * (income - 40000)),
        "homeowner", "renter")
    age = np.clip(rng.normal(44, 16, N_RESIDENTS), 18, 92).round(0).astype(int)
    # prior civic engagement: more likely for homeowners & longer-lived; noisy.
    civic_p = np.clip(
        PRIOR_CIVIC_RATE
        + 0.10 * (tenure == "homeowner")
        + 0.004 * (age - 44)
        + rng.normal(0, 0.05, N_RESIDENTS),
        0.02, 0.85)
    prior_civic = (rng.random(N_RESIDENTS) < civic_p).astype(int)

    residents = pd.DataFrame({
        "node_id": [f"P{i:03d}" for i in range(1, N_RESIDENTS + 1)],
        "kind": "resident",
        "block": res_block,
        "income": income.round(0).astype(int),
        "tenure": tenure,
        "age": age,
        "prior_civic": prior_civic,
        "label": [f"Resident {i:03d}" for i in range(1, N_RESIDENTS + 1)],
    })

    # ----- orgs ------------------------------------------------------------
    org_kinds = ["church", "school", "nonprofit", "community_center"]
    org_block = rng.choice(BLOCKS, N_ORGS)
    org_type = rng.choice(org_kinds, N_ORGS)
    orgs = pd.DataFrame({
        "node_id": [f"O{i:03d}" for i in range(1, N_ORGS + 1)],
        "kind": "org",
        "block": org_block,
        "income": pd.NA,
        "tenure": pd.NA,
        "age": pd.NA,
        "prior_civic": 1,            # orgs are civic by definition
        "label": [f"{t.replace('_', ' ').title()} {i:02d}"
                  for i, t in zip(range(1, N_ORGS + 1), org_type)],
    })

    nodes = pd.concat([residents, orgs], ignore_index=True)
    node_ids = list(nodes.node_id)
    block_of = dict(zip(nodes.node_id, nodes.block))
    is_org = dict(zip(nodes.node_id, nodes.kind == "org"))
    civic_of = dict(zip(nodes.node_id, nodes.prior_civic.fillna(0).astype(int)))

    # "latent capacity" = how central a node becomes during the shock.
    # orgs and prior-civic residents have high latent capacity (the planted hubs).
    by_block = {b: [n for n in node_ids if block_of[n] == b] for b in BLOCKS}

    # emergent brokers: pick low-civic ordinary residents (not orgs, not civic)
    ordinary = [n for n in node_ids
                if not is_org[n] and civic_of[n] == 0]
    broker_set = set(rng.choice(ordinary, N_BROKERS, replace=False))

    latent = {}
    for n in node_ids:
        base = rng.gamma(2.0, 0.5)
        if is_org[n]:
            base *= CIVIC_ACTIVATION
        elif civic_of[n] == 1:
            base *= (CIVIC_ACTIVATION * 0.7)
        latent[n] = base

    # per-node small "popularity" used to weight who receives aid generally
    popularity = {n: rng.gamma(2.0, 1.0) for n in node_ids}

    # ----- build edges -----------------------------------------------------
    # We sample directed giver->receiver ties per period. The number of ties a
    # node initiates scales with its period-specific "giving capacity".
    rows = []

    def giving_capacity(n, period):
        # baseline ordinary capacity (small, gamma) + activation during shock
        base = 0.6 + 0.5 * rng.gamma(1.5, 1.0)
        cap = base
        if period == "during":
            if is_org[n] or civic_of[n] == 1:
                cap *= CIVIC_ACTIVATION
            else:
                cap *= 1.5            # general densification for everyone
        elif period == "after":
            if is_org[n] or civic_of[n] == 1:
                cap *= CIVIC_PERSIST
            else:
                cap *= 1.05
        return cap

    def pick_receiver(giver, period):
        gb = block_of[giver]
        # decide same-block vs cross-block (a "bridge")
        bridge_pref = BRIDGE_PROPENSITY[gb]
        # enclave gives almost no external ties
        if gb == ENCLAVE_BLOCK:
            bridge_pref *= ENCLAVE_EXTERNAL_DAMP
        p_bridge = np.clip(0.35 * bridge_pref, 0.02, 0.85)
        cross = rng.random() < p_bridge
        if cross:
            others = [b for b in BLOCKS if b != gb]
            # starved block is rarely chosen as a bridge target (few bridges in)
            w = np.array([0.2 if b == STARVED_BLOCK else 1.0 for b in others])
            tb = rng.choice(others, p=w / w.sum())
            pool = by_block[tb]
        else:
            pool = [x for x in by_block[gb] if x != giver]
        if not pool:
            return None
        # receivers weighted by popularity; brokers attract more flow DURING
        wts = np.array([popularity[x] for x in pool], dtype=float)
        if period == "during":
            for k, x in enumerate(pool):
                if x in broker_set:
                    wts[k] *= 4.0      # brokers sit on many during-shock paths
        wts /= wts.sum()
        return str(rng.choice(pool, p=wts))

    for period in PERIODS:
        rate = DENSIFY[period]
        for giver in node_ids:
            cap = giving_capacity(giver, period) * rate
            n_ties = rng.poisson(max(cap, 0.05))
            # brokers initiate extra bridging ties during the shock
            if period == "during" and giver in broker_set:
                n_ties += rng.poisson(4.0)
            seen = {}
            for _ in range(int(n_ties)):
                recv = pick_receiver(giver, period)
                if recv is None or recv == giver:
                    continue
                key = recv
                # amount of aid (weight): orgs/civic give larger amounts during
                amt = rng.gamma(2.0, 18.0)
                if period == "during" and (is_org[giver] or civic_of[giver] == 1):
                    amt *= 1.5
                aid = rng.choice(AID_TYPES, p=[0.4, 0.2, 0.25, 0.15])
                if key in seen:
                    seen[key]["amount"] += amt
                    seen[key]["acts"] += 1
                else:
                    seen[key] = {"amount": amt, "acts": 1, "aid_type": aid}
            for recv, d in seen.items():
                rows.append({
                    "from_id": giver,
                    "to_id": recv,
                    "period": period,
                    "amount": round(float(d["amount"]), 1),
                    "acts": int(d["acts"]),
                    "aid_type": d["aid_type"],
                    "cross_block": int(block_of[giver] != block_of[recv]),
                })

    edges = pd.DataFrame(rows)

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)
    by_p = edges.period.value_counts().to_dict()
    print(f"mutualaid-quake: {len(nodes)} nodes "
          f"({(nodes.kind=='resident').sum()} residents + {(nodes.kind=='org').sum()} orgs), "
          f"{len(edges)} edges "
          f"(before={by_p.get('before',0)}, during={by_p.get('during',0)}, "
          f"after={by_p.get('after',0)}); aid Gini(during)="
          f"{_gini(edges[edges.period=='during'].groupby('to_id').amount.sum().values):.2f}.")


if __name__ == "__main__":
    main()
```

---

## `data/projects/mutualaid-quake/load.R`

```r
#' @name load.R
#' @title Load the `mutualaid-quake` project network (R)
#' @description
#'
#' Reads the two CSVs in this folder and builds a directed, weighted igraph
#' object: acts of mutual aid given between residents and organizations in
#' fictional "Eastvale" across three periods of an earthquake. Run it straight
#' (`Rscript load.R`) for a quick summary, or `source()` it and call
#' `load_mutualaid()` to get the graph in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "mutualaid-quake")

#' Load the node table (one row per resident / org).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per giver x receiver x period).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Build the directed, weighted graph.
#'
#' Edges are weighted by `amount` (aid given). Because the data is temporal (a
#' `period` column with before/during/after), an edge between the same pair can
#' appear up to 3 times; igraph keeps them as parallel edges, so filter to one
#' `period` first if you want a single-period graph.
load_mutualaid <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = TRUE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$amount
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n\U0001F91D mutualaid-quake (R)\n")
  cat("   Directed aid between residents & orgs; before / during / after a quake.\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_mutualaid(nodes, edges)

  cat(sprintf("✅ Loaded %d nodes (%d residents, %d orgs) and %d edges.\n",
              nrow(nodes), sum(nodes$kind == "resident"),
              sum(nodes$kind == "org"), nrow(edges)))
  for (p in c("before", "during", "after")) {
    cat(sprintf("   period %-7s: %d ties\n", p, sum(edges$period == p)))
  }
  cat(sprintf("\U0001F517 Directed: %s | total aid given: %s\n",
              is_directed(g), format(round(sum(edges$amount)), big.mark = ",")))
  cat("\U0001F389 Graph ready. Object `g` is a directed, weighted igraph.\n")
}
```

---

## `data/projects/mutualaid-quake/load.py`

```python
"""Load the `mutualaid-quake` project network (Python).

Reads the two CSVs in this folder and builds a directed, weighted python-igraph
object: acts of mutual aid given between residents and organizations in fictional
"Eastvale" across three periods of an earthquake. Run it straight
(``python load.py``) for a quick summary, or import ``load_mutualaid()`` into
your own script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per resident / org."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per giver x receiver x period."""
    return pd.read_csv(HERE / "edges.csv")


def load_mutualaid(nodes: pd.DataFrame | None = None,
                   edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the directed, weighted graph (edge weight = ``amount``).

    The data is temporal (a ``period`` column: before/during/after), so an edge
    between the same pair can appear up to 3 times as parallel edges. Filter to
    one ``period`` first if you want a single-period graph.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=True, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["amount"]
    return g


if __name__ == "__main__":
    print("\n\U0001F91D mutualaid-quake (Python)")
    print("   Directed aid between residents & orgs; before / during / after a quake.\n")

    nodes = load_nodes()
    edges = load_edges()
    g = load_mutualaid(nodes, edges)

    kinds = nodes["kind"].value_counts()
    print(f"✅ Loaded {len(nodes)} nodes "
          f"({kinds.get('resident',0)} residents, {kinds.get('org',0)} orgs) "
          f"and {len(edges)} edges.")
    for p in ("before", "during", "after"):
        print(f"   period {p:<7}: {(edges['period']==p).sum()} ties")
    print(f"\U0001F517 Directed: {g.is_directed()} | total aid given: "
          f"{round(edges['amount'].sum()):,}")
    print("\U0001F389 Graph ready. Object `g` is a directed, weighted igraph.")
```

---

## `data/projects/nyc-realestate-capital/README.md`

# nyc-realestate-capital

*Who is funding New York City's commercial real estate — and how much of the promised money actually shows up — tracked quarter by quarter for three years.*

## At a glance

| | |
|---|---|
| **Direction** | Directed (capital provider → property) |
| **Weights** | Yes — `invested_usd` (capital deployed); also `pledged_usd` |
| **Modality** | Multi-mode: `property` · `investor` · `bank` (bipartite providers → properties) |
| **Temporal** | Yes — 12 quarterly slices, `2024Q1` … `2026Q4` (long format) |
| **Nodes** | 270 (190 properties · 64 investors · 16 banks) |
| **Edges** | 5,044 provider–property–quarter funding rows |
| **Files** | `nodes.csv`, `edges.csv` |

## What this network is

A capital-flow network for commercial real estate (CRE) in New York City. Two
kinds of **capital providers** fund individual **properties**: `investor` nodes
supply equity (typed by who they are — local, POC-led, corporate, multinational,
institutional, family office, REIT, sovereign, nonprofit) and `bank` nodes supply
debt (commercial, investment, community-development/CDFI, GSE, private credit). An
edge is a funding relationship in a given quarter; it records capital **already
deployed** (`invested_usd`) versus capital **pledged but not yet deployed**
(`pledged_usd`). The same provider→property pair recurs across quarters, so the
network grows and shifts over the three years.

It pairs with **`nyc-realestate-portfolio`**, which shares the property `node_id`s
exactly: that companion projects this bipartite network down to property↔property
shared-financing ties.

Example project questions:
- For each property, what **share of investment** comes from local vs.
  multinational capital? From equity vs. debt? (`invested_usd` by provider type.)
- Is a property's **deployment ratio** — `invested / (invested + pledged)` —
  related to its neighborhood, *after* controlling for appraised value?
- Which providers are **systemically central** (fund many properties, or bridge
  otherwise-separate portfolios)? What happens to the network at `2025Q2`?
- Predict which properties end the period **under-funded** (deployed far below
  appraised value) from their funding mix and neighborhood.

The genuinely interesting findings here are deliberately undocumented. "Prime
buildings attract more capital" is the *starting point*, not a finding — look for
what is true once you hold size, value, and location constant.

## `nodes.csv`

One row per node. `kind` selects which columns apply; provider-only or
property-only columns are blank where they don't apply.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique key edges reference (`P###` property, `I###` investor, `B##` bank) | string | `P001`, `I001`, `B01` |
| `kind` | Node kind | Which mode this node is | string | `property`, `investor`, `bank` |
| `label` | Label | Human-readable display name | string | `Astoria Mixed Use 1`, `Reit Capital 1` |
| `borough` | Borough | Property borough (property rows) | string | `Manhattan`, `Brooklyn`, `Bronx` |
| `neighborhood` | Neighborhood | Property neighborhood (property rows) | string | `Midtown`, `Bushwick`, `South Bronx` |
| `property_type` | Property type | Asset class (property rows) | string | `office`, `multifamily`, `retail`, `hotel` |
| `building_class` | Building class | CRE quality grade (property rows) | string | `A`, `B`, `C` |
| `year_built` | Year built | Construction year (property rows) | integer | `1968`, `2025` |
| `sqft` | Square footage | Gross floor area, ft² (property rows) | integer | `48821`, `512000` |
| `stories` | Stories | Number of floors (property rows) | integer | `7`, `42` |
| `appraised_value` | Appraised value | Total appraised value, USD (property rows) | integer | `30370000`, `423590000` |
| `occupancy_rate` | Occupancy rate | Share of space leased, 0–1 (property rows) | float | `0.838`, `0.41` |
| `investor_type` | Investor type | Equity-investor category (investor rows) | string | `local`, `poc_led`, `multinational`, `reit` |
| `capital_scale` | Capital scale | Rough size of the investor (investor rows) | string | `small`, `mid`, `large` |
| `lender_type` | Lender type | Debt-provider category (bank rows) | string | `commercial`, `investment`, `community_dev`, `gse`, `private_credit` |
| `hq_location` | Headquarters | Provider HQ city (provider rows) | string | `New York`, `London`, `Abu Dhabi` |
| `founded_year` | Founded year | Year the provider was founded (provider rows) | integer | `1981`, `1920` |
| `x` | X coordinate | Schematic east–west map position (property rows) | float | `6.401` |
| `y` | Y coordinate | Schematic north–south map position (property rows) | float | `9.739` |

## `edges.csv`

One row per (provider, property, quarter) once the relationship is active.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | Provider ID | Capital provider (`I###` investor or `B##` bank) | string | `I006`, `B01` |
| `to_id` | Property ID | Property receiving capital (`P###`) | string | `P001` |
| `quarter` | Quarter | Calendar quarter of this slice | string | `2024Q1`, `2025Q2`, `2026Q4` |
| `instrument` | Instrument | Type of capital | string | `equity`, `debt`, `mezzanine` |
| `invested_usd` | Invested (USD) | Capital actually deployed to date, USD | integer | `2679000`, `4379000` |
| `pledged_usd` | Pledged (USD) | Committed capital not yet deployed, USD | integer | `7862000`, `5029000` |

## Load it

```bash
Rscript data/projects/nyc-realestate-capital/load.R
python  data/projects/nyc-realestate-capital/load.py
```

In the **R or Python playground** (or the **Visualizer**), pick
`nyc-realestate-capital` from the **▾ Load sample** menu. The graph is directed
(provider → property), weighted by `invested_usd`, and bipartite in structure
(`type` = TRUE for properties). Filter the `quarter` column for one temporal
slice, or aggregate by it.

## Get this data

<https://github.com/timothyfraser/netsci/tree/main/data/projects/nyc-realestate-capital>

---

## `data/projects/nyc-realestate-capital/_generate.py`

```python
"""Generate the `nyc-realestate-capital` project network (deterministic).

A temporal, multi-mode commercial-real-estate capital network for a single metro
(New York City), tracked quarter-by-quarter across three years (2024Q1–2026Q4).

Three node kinds:
  - property : individual CRE assets across the five boroughs (~190)
  - investor : equity capital providers, typed (local, poc_led, corporate,
               multinational, institutional, family_office, reit, sovereign,
               nonprofit) (~64)
  - bank     : debt / portfolio-company lenders (commercial, investment,
               community_dev/CDFI, gse, private_credit) (~16)

Edges are funding relationships provider -> property, in long temporal format
(one row per provider-property-quarter once the relationship is active). Each row
carries capital ALREADY deployed (`invested_usd`) vs capital pledged-but-not-yet
deployed (`pledged_usd`), plus the `instrument` (equity/debt/mezzanine).

This generator is the single source of truth: it writes this folder's CSVs AND
derives the companion `nyc-realestate-portfolio` projection (properties linked by
shared equity financing), so the two datasets share property `node_id`s exactly.

Design parameters (the only record of the planted structure):
  - TYPE_SORTING: equity *type* sorts by neighborhood prestige — multinational /
    sovereign / institutional capital concentrates in prime Manhattan; local /
    POC-led / community (CDFI) capital concentrates in lower-prestige outer
    neighborhoods. (Capital-source segregation, ~orthogonal to deal size.)
  - PLEDGE_GAP: in low-prestige neighborhoods, large *external* capital pledges
    but is slow to deploy (pledged lingers, invested lags) — a disinvestment gap
    in the invested/(invested+pledged) ratio that survives controlling for value;
    local/CDFI capital deploys normally.
  - OVERLEVERAGE: one REIT cross-collateralizes a cluster of ~24 gentrifying
    Brooklyn properties -> a dense over-shared community in the portfolio
    projection (concentration / single-point-of-failure).
  - SHOCK_Q: a mid-period rate shock (2025Q2) freezes new debt deployment and
    withdraws pledged capital, hitting the over-leveraged cluster + outer-borough
    assets hardest.

Run:
    python data/projects/nyc-realestate-capital/_generate.py
"""
from __future__ import annotations

from pathlib import Path
from itertools import combinations
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
PORTFOLIO_DIR = HERE.parent / "nyc-realestate-portfolio"
SEED = 42

N_PROPERTIES = 190
N_INVESTORS = 64
N_BANKS = 16
QUARTERS = [f"{y}Q{q}" for y in (2024, 2025, 2026) for q in (1, 2, 3, 4)]  # 12

# --- planted parameters -----------------------------------------------------
TYPE_SORTING = 1.0       # strength of capital-type sorting by neighborhood prime
PLEDGE_GAP = 0.78        # how much external-capital deployment slows in low-prime areas
OVERLEVERAGE_N = 24      # properties cross-collateralized by the one big REIT
SHOCK_Q = 5              # index into QUARTERS (2025Q2): rate shock
SHOCK_DEBT_SLOW = 0.45   # post-shock multiplier on new debt deployment
SHOCK_PLEDGE_WITHDRAW = 0.30  # fraction of remaining pledge withdrawn for exposed deals

# neighborhood: (name, borough, prime 0..1, x, y)  — prime = prestige/value tier
NEIGH = [
    ("Midtown",          "Manhattan",     0.97, 5.0, 9.2),
    ("FiDi",             "Manhattan",     0.93, 4.7, 7.4),
    ("Hudson Yards",     "Manhattan",     0.95, 4.3, 9.0),
    ("SoHo",             "Manhattan",     0.96, 4.8, 8.2),
    ("Upper East Side",  "Manhattan",     0.90, 5.4, 10.1),
    ("Harlem",           "Manhattan",     0.46, 5.2, 11.4),
    ("Washington Hts",   "Manhattan",     0.40, 5.0, 12.3),
    ("Williamsburg",     "Brooklyn",      0.74, 6.4, 8.0),
    ("DUMBO",            "Brooklyn",      0.82, 6.0, 7.7),
    ("Downtown Bklyn",   "Brooklyn",      0.70, 6.2, 7.2),
    ("Bushwick",         "Brooklyn",      0.52, 7.1, 8.1),
    ("Bed-Stuy",         "Brooklyn",      0.50, 6.8, 7.6),
    ("Brownsville",      "Brooklyn",      0.24, 7.6, 6.6),
    ("Sunset Park",      "Brooklyn",      0.44, 6.1, 6.2),
    ("Long Island City", "Queens",        0.72, 6.6, 9.1),
    ("Astoria",          "Queens",        0.60, 6.6, 9.9),
    ("Flushing",         "Queens",        0.55, 8.4, 9.6),
    ("Jamaica",          "Queens",        0.34, 8.6, 7.6),
    ("South Bronx",      "Bronx",         0.22, 5.7, 12.9),
    ("Fordham",          "Bronx",         0.30, 5.6, 13.6),
    ("St. George",       "Staten Island", 0.42, 4.0, 5.0),
]
PROP_TYPES = ["office", "multifamily", "retail", "industrial", "mixed_use", "hotel"]
INV_TYPES = ["local", "poc_led", "corporate", "multinational", "institutional",
             "family_office", "reit", "sovereign", "nonprofit"]
# which equity types are "big external" capital (slow to deploy in low-prime areas)
EXTERNAL = {"multinational", "institutional", "sovereign", "corporate"}
# which are place-based / mission capital (deploy regardless of prime)
LOCAL_CAP = {"local", "poc_led", "nonprofit"}
BANK_TYPES = ["commercial", "investment", "community_dev", "gse", "private_credit"]


def main() -> None:
    rng = np.random.default_rng(SEED)
    neigh = pd.DataFrame(NEIGH, columns=["neighborhood", "borough", "prime", "x", "y"])
    prime = dict(zip(neigh.neighborhood, neigh.prime))

    # ----- properties ------------------------------------------------------
    # more properties in prime + mid neighborhoods, but every neighborhood gets some
    nw = (0.5 + neigh.prime.values)
    nw = nw / nw.sum()
    p_neigh = rng.choice(neigh.neighborhood.values, N_PROPERTIES, p=nw)
    prows = []
    for i, nb in enumerate(p_neigh, start=1):
        pr = prime[nb]
        ptype = rng.choice(PROP_TYPES, p=[0.26, 0.30, 0.16, 0.12, 0.12, 0.04])
        sqft = int(np.clip(rng.lognormal(11.0 + 0.8 * pr, 0.5), 8000, 1_800_000))
        year = int(np.clip(rng.normal(1968 + 30 * pr, 26), 1900, 2025))
        bclass = rng.choice(["A", "B", "C"],
                            p=[max(0.05, pr - 0.05), 0.45, max(0.05, 0.85 - pr)]
                              / np.sum([max(0.05, pr - 0.05), 0.45, max(0.05, 0.85 - pr)]))
        # appraised value: prime + size + type premium + noise (psf * sqft)
        type_prem = {"office": 1.15, "multifamily": 1.0, "retail": 0.95,
                     "industrial": 0.7, "mixed_use": 1.05, "hotel": 1.2}[ptype]
        psf = (180 + 720 * pr) * type_prem * np.exp(rng.normal(0, 0.18))
        value = int(round(sqft * psf, -4))
        occ = float(np.clip(rng.normal(0.78 + 0.16 * pr, 0.1), 0.25, 0.99))
        nbr = neigh.loc[neigh.neighborhood == nb].iloc[0]
        prows.append({
            "node_id": f"P{i:03d}", "kind": "property",
            "label": f"{nb} {ptype.replace('_', ' ').title()} {i}",
            "borough": nbr.borough, "neighborhood": nb, "property_type": ptype,
            "building_class": bclass, "year_built": year, "sqft": sqft,
            "stories": int(np.clip(round(sqft / 18000 + rng.normal(0, 3)), 1, 95)),
            "appraised_value": value, "occupancy_rate": round(occ, 3),
            "x": round(float(nbr.x + rng.normal(0, 0.18)), 3),
            "y": round(float(nbr.y + rng.normal(0, 0.18)), 3),
        })
    props = pd.DataFrame(prows)

    # ----- investors (equity) ----------------------------------------------
    itype = rng.choice(INV_TYPES, N_INVESTORS,
                       p=[0.16, 0.12, 0.12, 0.10, 0.12, 0.10, 0.08, 0.05, 0.15])
    # ensure exactly one dominant REIT (the over-leverager): make investor I001 a reit
    itype[0] = "reit"
    inv_scale = []
    irows = []
    for i, t in enumerate(itype, start=1):
        scale = {"local": "small", "poc_led": "small", "nonprofit": "small",
                 "family_office": "mid", "corporate": "mid", "reit": "large",
                 "institutional": "large", "multinational": "large",
                 "sovereign": "large"}[t]
        if i == 1:
            scale = "large"
        inv_scale.append(scale)
        hq = rng.choice(["New York", "New York", "Boston", "London", "Toronto",
                         "Singapore", "Abu Dhabi", "Los Angeles", "Chicago"])
        if t in LOCAL_CAP:
            hq = "New York"
        irows.append({
            "node_id": f"I{i:03d}", "kind": "investor",
            "label": f"{t.replace('_', ' ').title()} Capital {i}",
            "investor_type": t, "capital_scale": scale, "hq_location": hq,
            "founded_year": int(np.clip(rng.normal(1995, 18), 1950, 2022)),
        })
    investors = pd.DataFrame(irows)
    inv_type = dict(zip(investors.node_id, investors.investor_type))
    reit_id = "I001"

    # ----- banks / portfolio-company lenders (debt) ------------------------
    btype = rng.choice(BANK_TYPES, N_BANKS, p=[0.34, 0.18, 0.18, 0.12, 0.18])
    brows = []
    for i, t in enumerate(btype, start=1):
        hq = rng.choice(["New York", "New York", "Charlotte", "London", "San Francisco"])
        if t in ("community_dev", "gse"):
            hq = "New York"
        brows.append({
            "node_id": f"B{i:02d}", "kind": "bank",
            "label": f"{t.replace('_', ' ').title()} Lender {i}",
            "lender_type": t, "hq_location": hq,
            "founded_year": int(np.clip(rng.normal(1975, 30), 1850, 2018)),
        })
    banks = pd.DataFrame(brows)
    bank_type = dict(zip(banks.node_id, banks.lender_type))

    # ----- assign providers to each property (homophily by neighborhood prime)
    inv_ids = list(investors.node_id)
    bank_ids = list(banks.node_id)

    def equity_weight(iid, pr):
        t = inv_type[iid]
        if t in EXTERNAL:                       # big external -> chase prime
            return 0.12 + TYPE_SORTING * pr
        if t in LOCAL_CAP:                      # place-based -> chase non-prime
            return 0.12 + TYPE_SORTING * (1 - pr)
        return 0.5                              # reit / family_office: neutral-ish

    def debt_weight(bid, pr):
        t = bank_type[bid]
        if t == "community_dev":
            return 0.15 + (1 - pr)              # CDFIs lend outer-borough
        if t in ("investment", "private_credit"):
            return 0.15 + pr                    # IBs / private credit chase prime
        return 0.5                              # commercial / gse: broad

    # planted over-leveraged cluster: 24 gentrifying Brooklyn props all share the REIT
    cluster_pool = props[props.neighborhood.isin(["Bushwick", "Bed-Stuy", "Williamsburg"])]
    cluster_ids = list(cluster_pool.sample(n=min(OVERLEVERAGE_N, len(cluster_pool)),
                                           random_state=7).node_id)

    rels = []   # (provider_id, property_id, instrument, commitment)
    for r in props.itertuples():
        pr = prime[r.neighborhood]
        val = r.appraised_value
        # equity syndicate (1-3 investors)
        n_eq = int(rng.choice([1, 2, 3], p=[0.45, 0.4, 0.15]))
        ew = np.array([equity_weight(i, pr) for i in inv_ids]); ew = ew / ew.sum()
        eq_pick = list(rng.choice(inv_ids, size=n_eq, replace=False, p=ew))
        if r.node_id in cluster_ids and reit_id not in eq_pick:
            eq_pick[0] = reit_id                # force the REIT into the cluster
        equity_total = val * float(np.clip(rng.normal(0.32, 0.07), 0.12, 0.5))
        shares = rng.dirichlet(np.ones(len(eq_pick)))
        for iid, s in zip(eq_pick, shares):
            instr = "mezzanine" if (inv_type[iid] == "private_credit") else "equity"
            rels.append((iid, r.node_id, instr, float(equity_total * s)))
        # debt stack (1-2 banks)
        n_db = int(rng.choice([1, 2], p=[0.6, 0.4]))
        bw = np.array([debt_weight(b, pr) for b in bank_ids]); bw = bw / bw.sum()
        db_pick = list(rng.choice(bank_ids, size=n_db, replace=False, p=bw))
        debt_total = val * float(np.clip(rng.normal(0.55, 0.08), 0.2, 0.75))
        dshares = rng.dirichlet(np.ones(len(db_pick)))
        for bid, s in zip(db_pick, dshares):
            d_instr = "mezzanine" if bank_type[bid] == "private_credit" else "debt"
            rels.append((bid, r.node_id, d_instr, float(debt_total * s)))

    # ----- simulate quarterly deployment (invested vs pledged) -------------
    # Capital ramps toward a *ceiling* fraction of its commitment; the rest is
    # pledged that never deploys. The ceiling falls in low-prestige neighborhoods
    # (a persistent disinvestment gap that survives controlling for deal value),
    # softened for place-based / mission capital that actually shows up. A mid-
    # period shock freezes deployment and withdraws pledges on exposed deals.
    prop_prime = dict(zip(props.node_id, [prime[n] for n in props.neighborhood]))

    def deploy_ceiling(prov, pr):
        base = 0.55 + 0.40 * pr                      # neighborhood disinvestment gradient
        if prov.startswith("I"):
            t = inv_type[prov]
            if t in LOCAL_CAP:
                base += 0.18 * PLEDGE_GAP            # mission capital deploys
            elif t in EXTERNAL:
                base -= 0.12 * PLEDGE_GAP            # external capital pledges, lingers
        else:
            bt = bank_type[prov]
            if bt in ("commercial", "gse"):
                base += 0.10
            elif bt == "community_dev":
                base += 0.15
        return float(np.clip(base, 0.40, 0.99))

    erows = []
    for prov, pid, instr, commit in rels:
        pr = prop_prime[pid]
        ceiling = deploy_ceiling(prov, pr)
        rate = {"debt": 0.70, "equity": 0.45, "mezzanine": 0.52}[instr]
        start_q = int(rng.integers(0, 8))
        exposed = (pid in cluster_ids) or (pr < 0.4)
        for qi in range(start_q, len(QUARTERS)):
            t = qi - start_q
            # exposed deals freeze their deployment progress at the shock
            t_eff = t
            if exposed and qi >= SHOCK_Q:
                t_eff = max(0, (SHOCK_Q - 1) - start_q)
            # debt deployment slows for everyone after the rate shock
            r_eff = rate * (SHOCK_DEBT_SLOW if (instr in ("debt", "mezzanine") and qi >= SHOCK_Q) else 1.0)
            ramp = 1 - np.exp(-r_eff * (t_eff + 1))
            invested = ceiling * commit * ramp * float(np.clip(1 + rng.normal(0, 0.02), 0.9, 1.1))
            pledged = max(0.0, commit - invested)
            if exposed and qi >= SHOCK_Q:            # pledges pulled at the shock
                pledged *= (1 - SHOCK_PLEDGE_WITHDRAW)
            erows.append({
                "from_id": prov, "to_id": pid, "quarter": QUARTERS[qi],
                "instrument": instr,
                "invested_usd": int(round(invested, -3)),
                "pledged_usd": int(round(pledged, -3)),
            })
    edges = pd.DataFrame(erows)

    # ----- assemble + write capital ----------------------------------------
    nodes = pd.concat([props, investors, banks], ignore_index=True)
    # stable column order (union; blanks where N/A)
    col_order = ["node_id", "kind", "label", "borough", "neighborhood",
                 "property_type", "building_class", "year_built", "sqft", "stories",
                 "appraised_value", "occupancy_rate", "investor_type", "capital_scale",
                 "lender_type", "hq_location", "founded_year", "x", "y"]
    for c in col_order:
        if c not in nodes.columns:
            nodes[c] = pd.NA
    nodes = nodes[col_order]
    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)

    # ----- derive portfolio projection (shared EQUITY financing only) ------
    # banks (ubiquitous debt) are excluded so the projection stays sparse and the
    # over-leveraged equity clusters stand out.
    eq_rel = [(prov, pid) for (prov, pid, instr, _c) in rels
              if prov.startswith("I")]
    by_inv: dict[str, list[str]] = {}
    invested_pp: dict[tuple, float] = {}
    tot_inv = edges.groupby(["from_id", "to_id"])["invested_usd"].max()
    for prov, pid in eq_rel:
        by_inv.setdefault(prov, []).append(pid)
        invested_pp[(prov, pid)] = float(tot_inv.get((prov, pid), 0.0))
    pair_shared: dict[tuple, int] = {}
    pair_co: dict[tuple, float] = {}
    for prov, plist in by_inv.items():
        plist = sorted(set(plist))
        for a, b in combinations(plist, 2):
            key = (a, b)
            pair_shared[key] = pair_shared.get(key, 0) + 1
            pair_co[key] = pair_co.get(key, 0.0) + min(invested_pp[(prov, a)],
                                                       invested_pp[(prov, b)])
    prows2 = [{
        "from_id": a, "to_id": b,
        "n_shared_investors": pair_shared[(a, b)],
        "co_investment_usd": int(round(pair_co[(a, b)], -3)),
    } for (a, b) in pair_shared]
    pedges = pd.DataFrame(prows2).sort_values(["from_id", "to_id"]).reset_index(drop=True)
    # portfolio nodes = properties only (same ids/traits, drop the 'kind' column)
    pnodes = props.drop(columns=["kind"]).reset_index(drop=True)

    PORTFOLIO_DIR.mkdir(parents=True, exist_ok=True)
    pnodes.to_csv(PORTFOLIO_DIR / "nodes.csv", index=False)
    pedges.to_csv(PORTFOLIO_DIR / "edges.csv", index=False)

    print(f"nyc-realestate-capital: {len(nodes)} nodes "
          f"({len(props)} properties + {len(investors)} investors + {len(banks)} banks), "
          f"{len(edges)} funding rows over {len(QUARTERS)} quarters.")
    print(f"nyc-realestate-portfolio: {len(pnodes)} properties, {len(pedges)} "
          f"shared-financing edges (over-leveraged cluster = {len(cluster_ids)} props).")


if __name__ == "__main__":
    main()
```

---

## `data/projects/nyc-realestate-capital/load.R`

```r
#' @name load.R
#' @title Load the `nyc-realestate-capital` project network (R)
#' @description
#'
#' Reads the CSVs in this folder and builds a directed, weighted, temporal funding
#' network: capital providers (investors + banks) -> NYC properties. Edges are
#' provider-property-quarter rows carrying capital already deployed (`invested_usd`)
#' vs pledged-but-not-yet-deployed (`pledged_usd`). Run it straight
#' (`Rscript load.R`) for a summary, or `source()` it and call `load_capital()`.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "nyc-realestate-capital")

#' Load the node table (properties + investors + banks; see the `kind` column).
load_nodes <- function() read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)

#' Load the edge table (one row per provider-property-quarter).
load_edges <- function() read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)

#' Build the directed, weighted funding graph (edge weight = `invested_usd`).
#'
#' The graph is bipartite in structure (providers connect only to properties);
#' `V(g)$type` is TRUE for properties, FALSE for capital providers. Edges are kept
#' in long temporal form: filter `E(g)$quarter` (e.g. "2025Q2") for one slice, or
#' `subgraph.edges()` it. Collapse repeat quarters with
#' `simplify(g, edge.attr.comb = list(invested_usd = "sum", weight = "sum"))`.
load_capital <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = TRUE, vertices = nodes)
  igraph::V(g)$type <- igraph::V(g)$kind == "property"
  igraph::E(g)$weight <- igraph::E(g)$invested_usd
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n🏙️  nyc-realestate-capital (R)\n")
  cat("   Investors + banks -> NYC properties; quarterly invested vs pledged.\n\n")

  nodes <- load_nodes(); edges <- load_edges(); g <- load_capital(nodes, edges)

  cat(sprintf("✅ Loaded %d nodes (%d properties + %d investors + %d banks) and %d funding rows.\n",
              nrow(nodes), sum(nodes$kind == "property"),
              sum(nodes$kind == "investor"), sum(nodes$kind == "bank"), nrow(edges)))
  cat(sprintf("🔗 Quarters: %s | total invested: $%sB | total pledged (open): $%sB\n",
              length(unique(edges$quarter)),
              format(round(sum(edges$invested_usd) / 1e9, 1), nsmall = 1),
              format(round(sum(edges$pledged_usd) / 1e9, 1), nsmall = 1)))
  cat("🎉 Graph ready. Directed providers -> properties; weight = invested_usd; filter E(g)$quarter.\n")
}
```

---

## `data/projects/nyc-realestate-capital/load.py`

```python
"""Load the `nyc-realestate-capital` project network (Python).

Reads the CSVs in this folder and builds a directed, weighted, temporal funding
network with python-igraph: capital providers (investors + banks) -> NYC
properties. Edges are provider-property-quarter rows carrying capital already
deployed (``invested_usd``) vs pledged-but-not-deployed (``pledged_usd``). Run it
straight (``python load.py``) for a summary, or import ``load_capital()``.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: properties + investors + banks (see the ``kind`` column)."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per provider-property-quarter."""
    return pd.read_csv(HERE / "edges.csv")


def load_capital(nodes: pd.DataFrame | None = None,
                 edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the directed, weighted funding graph (edge weight = ``invested_usd``).

    The graph is bipartite in structure (providers connect only to properties);
    ``vs['type']`` is True for properties, False for capital providers. Edges stay
    in long temporal form: filter ``es['quarter']`` (e.g. "2025Q2") for one slice.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=True, vertices=nodes, use_vids=False)
    g.vs["type"] = [k == "property" for k in g.vs["kind"]]
    g.es["weight"] = g.es["invested_usd"]
    return g


if __name__ == "__main__":
    print("\n🏙️  nyc-realestate-capital (Python)")
    print("   Investors + banks -> NYC properties; quarterly invested vs pledged.\n")

    nodes = load_nodes(); edges = load_edges(); g = load_capital(nodes, edges)
    k = nodes["kind"].value_counts()
    print(f"✅ Loaded {len(nodes)} nodes ({k.get('property',0)} properties + "
          f"{k.get('investor',0)} investors + {k.get('bank',0)} banks) and "
          f"{len(edges)} funding rows.")
    print(f"🔗 Quarters: {edges['quarter'].nunique()} | total invested: "
          f"${edges['invested_usd'].sum()/1e9:,.1f}B | total pledged (open): "
          f"${edges['pledged_usd'].sum()/1e9:,.1f}B")
    print("🎉 Graph ready. Directed providers -> properties; weight = invested_usd; filter es['quarter'].")
```

---

## `data/projects/nyc-realestate-portfolio/README.md`

# nyc-realestate-portfolio

*A New York City commercial-real-estate portfolio as a network: properties linked when they share an equity backer — so you can see where financing is diversified and where it is dangerously concentrated.*

## At a glance

| | |
|---|---|
| **Direction** | Undirected |
| **Weights** | Yes — `co_investment_usd` (shared capital across the tie) |
| **Modality** | Unimodal (properties only) |
| **Temporal** | No (a single cumulative snapshot) |
| **Nodes** | 190 properties |
| **Edges** | 1,155 shared-financing ties |
| **Files** | `nodes.csv`, `edges.csv` |

## What this network is

Each node is a commercial property in NYC. Two properties are connected when they
share **at least one common equity investor** — i.e. they sit inside the same
ownership/financing portfolio and are, in effect, cross-collateralized. Edge
weight (`co_investment_usd`) is how much shared capital ties them together. Debt
lenders (banks) are intentionally **excluded** from the projection: they are
near-ubiquitous and would turn the graph into a hairball, hiding the structure
that matters.

The modeling premise is a real one in portfolio finance: **fewer shared-financing
ties is usually healthier** — a property whose backers are independent of everyone
else's fails alone. Dense, tightly shared clusters mean correlated risk: one
backer in trouble can drag a whole neighborhood of buildings down with it.
Sometimes shared financing reflects healthy diversification; sometimes it reflects
dangerous concentration. Telling those apart is the work.

This dataset is **derived from** `nyc-realestate-capital` and shares its property
`node_id`s exactly, so you can join the two: bring each property's appraised value,
investor mix, and quarterly invested/pledged totals onto these nodes.

Example project questions:
- Which properties are the **most central** in the portfolio (highest degree /
  betweenness)? Are they the most valuable ones, or something else?
- Run **community detection** — do the financing clusters line up with
  neighborhood, borough, or property type? Which cluster is most concentrated?
- If one backer's portfolio failed, **how many properties** and how much value
  would be exposed (knock out a hub, recompute connectivity)?
- Is shared financing **assortative** by building class or borough?

The interesting findings are deliberately undocumented. "Big buildings have more
ties" is the starting point, not a finding.

## `nodes.csv`

One row per property (identical ids and traits to the property rows in
`nyc-realestate-capital`).

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique property key edges reference | string | `P001`, `P059` |
| `label` | Label | Human-readable display name | string | `Astoria Mixed Use 1` |
| `borough` | Borough | NYC borough | string | `Manhattan`, `Brooklyn`, `Queens` |
| `neighborhood` | Neighborhood | NYC neighborhood | string | `Midtown`, `Bushwick`, `South Bronx` |
| `property_type` | Property type | Asset class | string | `office`, `multifamily`, `retail`, `hotel` |
| `building_class` | Building class | CRE quality grade | string | `A`, `B`, `C` |
| `year_built` | Year built | Construction year | integer | `1968`, `2025` |
| `sqft` | Square footage | Gross floor area, ft² | integer | `48821`, `512000` |
| `stories` | Stories | Number of floors | integer | `7`, `42` |
| `appraised_value` | Appraised value | Total appraised value, USD | integer | `30370000`, `423590000` |
| `occupancy_rate` | Occupancy rate | Share of space leased, 0–1 | float | `0.838`, `0.41` |
| `x` | X coordinate | Schematic east–west map position | float | `6.401` |
| `y` | Y coordinate | Schematic north–south map position | float | `9.739` |

## `edges.csv`

One row per shared-financing tie (undirected; `from_id` < `to_id`).

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | Property A | One endpoint property id | string | `P001` |
| `to_id` | Property B | Other endpoint property id | string | `P009` |
| `n_shared_investors` | Shared investors | How many equity investors the two properties share | integer | `1`, `4` |
| `co_investment_usd` | Co-investment (USD) | Shared capital tying the two together, USD | integer | `7279000` |

## Load it

```bash
Rscript data/projects/nyc-realestate-portfolio/load.R
python  data/projects/nyc-realestate-portfolio/load.py
```

In the **R or Python playground** (or the **Visualizer**), pick
`nyc-realestate-portfolio` from the **▾ Load sample** menu. The graph is
undirected and weighted by `co_investment_usd`; color nodes by `borough` or
`property_type`.

## Get this data

<https://github.com/timothyfraser/netsci/tree/main/data/projects/nyc-realestate-portfolio>

---

## `data/projects/nyc-realestate-portfolio/_generate.py`

```python
"""Generate the `nyc-realestate-portfolio` project network (deterministic).

This dataset is DERIVED from its companion `nyc-realestate-capital`: nodes are the
same NYC properties (identical `node_id`s and traits), and an undirected edge
links two properties that share at least one common *equity* investor — i.e. they
sit in the same financing portfolio (cross-collateralization / co-ownership).
Debt lenders are intentionally excluded so the projection stays sparse and the
over-shared clusters stand out (best practice is as few shared-financing ties as
possible; dense clusters signal concentrated, correlated risk).

Because both datasets must share property ids exactly, the canonical generator
lives in `../nyc-realestate-capital/_generate.py`; it writes BOTH folders. Running
this file just delegates to it.

Run:
    python data/projects/nyc-realestate-portfolio/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import runpy

CAPITAL_GEN = Path(__file__).resolve().parent.parent / "nyc-realestate-capital" / "_generate.py"

if __name__ == "__main__":
    runpy.run_path(str(CAPITAL_GEN), run_name="__main__")
```

---

## `data/projects/nyc-realestate-portfolio/load.R`

```r
#' @name load.R
#' @title Load the `nyc-realestate-portfolio` project network (R)
#' @description
#'
#' Reads the CSVs in this folder and builds an undirected, weighted property
#' portfolio network: nodes are NYC properties, an edge links two properties that
#' share at least one common equity investor (co-ownership / cross-collateral).
#' Edge weight is `co_investment_usd`. Run it straight (`Rscript load.R`) for a
#' summary, or `source()` it and call `load_portfolio()`. Shares property
#' `node_id`s with the companion `nyc-realestate-capital` dataset.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "nyc-realestate-portfolio")

#' Load the node table (one row per property).
load_nodes <- function() read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)

#' Load the edge table (one row per shared-financing tie).
load_edges <- function() read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)

#' Build the undirected, weighted portfolio graph (weight = `co_investment_usd`).
load_portfolio <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = FALSE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$co_investment_usd
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n🏢 nyc-realestate-portfolio (R)\n")
  cat("   Properties linked by shared equity financing; weight = co_investment_usd.\n\n")

  nodes <- load_nodes(); edges <- load_edges(); g <- load_portfolio(nodes, edges)

  cat(sprintf("✅ Loaded %d properties and %d shared-financing edges.\n",
              nrow(nodes), nrow(edges)))
  cat(sprintf("🔗 Components: %d | mean degree: %.1f | densest cluster hints at concentration risk.\n",
              igraph::components(g)$no, mean(igraph::degree(g))))
  cat("🎉 Graph ready. Undirected; weight = co_investment_usd; group by borough / property_type.\n")
}
```

---

## `data/projects/nyc-realestate-portfolio/load.py`

```python
"""Load the `nyc-realestate-portfolio` project network (Python).

Reads the CSVs in this folder and builds an undirected, weighted property
portfolio network with python-igraph: nodes are NYC properties, an edge links two
properties that share at least one common equity investor (co-ownership /
cross-collateral). Edge weight is ``co_investment_usd``. Run it straight
(``python load.py``) for a summary, or import ``load_portfolio()``. Shares
property ``node_id``s with the companion ``nyc-realestate-capital`` dataset.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per property."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per shared-financing tie."""
    return pd.read_csv(HERE / "edges.csv")


def load_portfolio(nodes: pd.DataFrame | None = None,
                   edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the undirected, weighted portfolio graph (weight = ``co_investment_usd``)."""
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=False, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["co_investment_usd"]
    return g


if __name__ == "__main__":
    print("\n🏢 nyc-realestate-portfolio (Python)")
    print("   Properties linked by shared equity financing; weight = co_investment_usd.\n")

    nodes = load_nodes(); edges = load_edges(); g = load_portfolio(nodes, edges)
    comps = g.connected_components()
    deg = g.degree()
    print(f"✅ Loaded {len(nodes)} properties and {len(edges)} shared-financing edges.")
    print(f"🔗 Components: {len(comps)} | mean degree: {sum(deg)/len(deg):.1f} | "
          f"densest cluster hints at concentration risk.")
    print("🎉 Graph ready. Undirected; weight = co_investment_usd; group by borough / property_type.")
```

---

## `data/projects/opensource-deps/README.md`

# opensource-deps

*A snapshot of an open-source software ecosystem's dependency graph: which
packages depend on which, and how heavily.*

![Preview of the opensource-deps network](thumb.png)

## At a glance

| | |
|---|---|
| **Direction** | Directed (`from` depends on → `to`) |
| **Weights** | Weighted (`import_count` = how heavily the dependency is used) |
| **Modality** | One node kind (`package`) |
| **Temporal** | No — a single snapshot |
| **Nodes** | 400 packages |
| **Edges** | 2,251 "depends on" relationships |
| **Files** | `nodes.csv`, `edges.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

Every node is a software **package**; a directed edge `A → B` means *package A
depends on package B* (A imports and calls into B). The edge weight,
`import_count`, is how many call sites in A reach into B — a proxy for how heavily
A leans on that dependency. Each package carries its `ecosystem_area` (web, data,
build, test, crypto), its number of `maintainers`, its `weekly_downloads`, and how
many `months_since_update` it has gone without a release.

This is a directed-graph **criticality, reachability, and reverse-dependency**
playground. Some things worth investigating:

- Direct in-degree (how many packages name you as a dependency) is the obvious
  importance measure. But is it the *right* one? What happens if you count how many
  packages can reach you *transitively* — and does that change who looks critical?
- If one package were compromised or yanked, how much of the ecosystem would feel
  it? Is the biggest blast radius attached to a big, well-known library — or
  something small?
- Risk is not just about reach. Combine reach with `maintainers` and
  `months_since_update`: is there a package the whole ecosystem leans on that
  almost nobody is maintaining?
- Out-degree tells a different story than in-degree. Is any package unusually
  fragile because it depends on a huge number of others?
- Look for packages that look almost identical and sit at the same depth, each
  with a large but *different* set of dependents. What would happen if a project
  needed both?

> **Note.** The interesting findings here are deliberately *not* documented.
> "Popular libraries are depended on a lot" is the starting point, not a finding.
> Look at what direct degree alone hides.

## `nodes.csv`

One row per package.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique key. `pkg###`. Referenced by edges. | character | `pkg001`, `pkg007`, `pkg400` |
| `ecosystem_area` | Ecosystem area | Functional area the package serves. | character | `web`, `data`, `crypto` |
| `maintainers` | Maintainer count | Number of active maintainers on the package. | integer | `1`, `4`, `10` |
| `weekly_downloads` | Weekly downloads | Registry downloads in a typical week. | integer | `8532`, `154618` |
| `months_since_update` | Months since update | Months since the last release. | double | `0.1`, `12.4`, `57.0` |
| `label` | Display name | Human-readable label. (`name` is avoided — python-igraph reserves it for the ID.) | character | `web-lib-001`, `tiny-pad` |

## `edges.csv`

One row per dependency. Directed: `from_id` depends on `to_id`.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | Dependent package ID | The package that has the dependency (joins to `nodes.csv`). | character | `pkg042` |
| `to_id` | Dependency package ID | The package being depended on (joins to `nodes.csv`). | character | `pkg007` |
| `import_count` | Import count | Number of call sites through which `from_id` uses `to_id` (the edge weight). | integer | `1`, `7`, `30` |

## Load it

```bash
Rscript data/projects/opensource-deps/load.R     # R    (igraph)
python  data/projects/opensource-deps/load.py     # Python (python-igraph)
```

Both build a directed, weighted `igraph` graph (edge weight = `import_count`) and
print a one-screen summary. In the
[R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**opensource-deps** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/opensource-deps>

---

## `data/projects/opensource-deps/_generate.py`

```python
"""Generate the `opensource-deps` project network (deterministic).

A package dependency graph for a fictional open-source ecosystem:
  - ~400 packages (kind = "package")
  - directed "depends on" edges (package -> the dependency it imports)
weighted by `import_count` (how many call sites use that dependency = how
heavily it is used).

Design parameters (the only record of the planted structure):
  - LEFTPAD: one tiny utility package has LOW direct in-degree relative to the
    big libraries, but a HUGE transitive in-degree (almost the whole ecosystem
    can reach it) -> the hidden critical supply-chain node.
  - ABANDONED: a package with very high downstream reach has months_since_update
    in the top decile AND maintainers == 1 (bus-factor risk on a critical node).
  - GOD_PKG: one package depends on an unusually large number of others (huge
    out-degree) -> fragile, breaks if any dependency breaks.
  - DIAMOND: a popular lower-level library exists as TWO version nodes (v1 / v2);
    many packages depend on one or the other -> a version-conflict hotspot.

Run:
    python data/projects/opensource-deps/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

N_PACKAGES = 400
AREAS = ["web", "data", "build", "test", "crypto"]

# --- planted parameters -----------------------------------------------------
N_FOUNDATION = 8       # a few low-level libraries everyone leans on
GOD_OUT_DEGREE = 55    # the "god package" depends on this many others (outlier)
DIAMOND_DEPENDENTS = 70  # how many packages point at each version of the diamond lib
LEFTPAD_DIRECT = 6     # the left-pad node's small DIRECT in-degree (looks minor)


def main() -> None:
    rng = np.random.default_rng(SEED)

    # ----- packages --------------------------------------------------------
    area = rng.choice(AREAS, size=N_PACKAGES, p=[0.34, 0.26, 0.16, 0.16, 0.08])
    node_id = np.array([f"pkg{i:03d}" for i in range(1, N_PACKAGES + 1)])

    # a "level" 0..3: lower levels are more foundational (depended on more).
    # foundation libs are level 0; leaves (apps) are level 3.
    level = rng.choice([0, 1, 2, 3], size=N_PACKAGES, p=[0.06, 0.24, 0.40, 0.30])

    # popularity (weekly downloads) is heavy-tailed and higher for low levels.
    base_pop = rng.lognormal(mean=9.0, sigma=1.6, size=N_PACKAGES)
    pop_mult = np.array([4.0, 2.2, 1.2, 0.7])[level]
    weekly_downloads = (base_pop * pop_mult).astype(int)

    maintainers = np.clip(rng.poisson(2.4, N_PACKAGES) + 1, 1, 18)
    months_since_update = np.clip(rng.gamma(2.0, 4.0, N_PACKAGES), 0, 60).round(1)

    labels = np.array([f"{a}-lib-{i:03d}" for i, a in zip(range(1, N_PACKAGES + 1), area)])

    # ----- pick the special nodes ------------------------------------------
    foundation = node_id[level == 0]
    # left-pad: a tiny utility, force it to look like a low-level helper but we
    # will route nearly everything through it transitively while keeping its
    # DIRECT in-degree small.
    leftpad = "pkg007"
    god_pkg = "pkg400"            # the god package (will get huge out-degree)
    # diamond: two version nodes of one popular library
    diamond_v1 = "pkg010"
    diamond_v2 = "pkg011"
    abandoned = "pkg015"         # high-reach + stale + single maintainer

    idx = {nid: i for i, nid in enumerate(node_id)}

    # force attributes for the planted nodes
    level[idx[leftpad]] = 0
    area[idx[leftpad]] = "build"
    maintainers[idx[leftpad]] = 2
    months_since_update[idx[leftpad]] = 7.0
    weekly_downloads[idx[leftpad]] = int(weekly_downloads.mean() * 0.6)  # modest!
    labels[idx[leftpad]] = "tiny-pad"

    level[idx[diamond_v1]] = 0
    level[idx[diamond_v2]] = 0
    area[idx[diamond_v1]] = "data"
    area[idx[diamond_v2]] = "data"
    labels[idx[diamond_v1]] = "coreutil-v1"
    labels[idx[diamond_v2]] = "coreutil-v2"
    weekly_downloads[idx[diamond_v1]] = int(weekly_downloads.mean() * 3.5)
    weekly_downloads[idx[diamond_v2]] = int(weekly_downloads.mean() * 3.0)

    level[idx[god_pkg]] = 3
    area[idx[god_pkg]] = "web"
    labels[idx[god_pkg]] = "kitchen-sink"

    # abandoned-but-critical: stale + single maintainer + (high reach engineered below)
    level[idx[abandoned]] = 0
    maintainers[idx[abandoned]] = 1
    months_since_update[idx[abandoned]] = 57.0
    area[idx[abandoned]] = "crypto"
    weekly_downloads[idx[abandoned]] = int(weekly_downloads.mean() * 2.0)
    labels[idx[abandoned]] = "oldcrypto"

    # ----- build dependency edges ------------------------------------------
    # General rule: a package depends mostly on packages at a LOWER level
    # (more foundational), a few at the same level, weighted by popularity.
    edges = {}   # (src,dst) -> import_count

    def add_edge(src, dst, w=None):
        if src == dst:
            return
        key = (src, dst)
        if w is None:
            w = int(np.clip(rng.gamma(2.0, 3.0), 1, 60))
        edges[key] = edges.get(key, 0) + w

    pop_norm = weekly_downloads / weekly_downloads.max()

    for i in range(N_PACKAGES):
        src = node_id[i]
        if src in (leftpad, god_pkg):
            continue   # handled specially
        lv = level[i]
        # number of direct dependencies grows with level (apps depend on more)
        n_deps = {0: rng.integers(0, 3), 1: rng.integers(1, 5),
                  2: rng.integers(2, 8), 3: rng.integers(3, 11)}[lv]
        # candidate targets: lower or equal level
        cand_mask = (level <= lv) & (node_id != src)
        cand = node_id[cand_mask]
        if len(cand) == 0:
            continue
        cand_pop = pop_norm[cand_mask] + 0.02
        w = cand_pop / cand_pop.sum()
        chosen = rng.choice(cand, size=min(n_deps, len(cand)), replace=False, p=w)
        for dst in chosen:
            add_edge(src, str(dst))

    # ----- LEFT-PAD: keep direct in-degree small, transitive in-degree huge --
    # Strategy: make the FOUNDATION libraries (which everything reaches) all
    # depend on left-pad. So anyone who depends on a foundation lib transitively
    # reaches left-pad, but left-pad's own direct dependents are just the few
    # foundation libs + a handful -> small direct in-degree.
    foundation_deps = [f for f in foundation if f not in (leftpad,)]
    # pick a small set of direct dependents = the foundation libs (a handful)
    direct_dependents = list(rng.choice(foundation_deps,
                                        size=min(LEFTPAD_DIRECT, len(foundation_deps)),
                                        replace=False))
    for d in direct_dependents:
        add_edge(str(d), leftpad, w=int(rng.integers(2, 8)))
    # ensure the diamond version libs (which sit at the top of reachability) also
    # depend on left-pad, so left-pad inherits all of THEIR ancestors too. This
    # pushes left-pad's TRANSITIVE in-degree above every other node while its
    # DIRECT in-degree stays small.
    for d in (diamond_v1, diamond_v2):
        add_edge(d, leftpad, w=int(rng.integers(2, 8)))
    # to make transitive reach huge, ensure MOST mid/high-level packages depend
    # (directly) on at least one of these foundation libs -> they all reach
    # left-pad through it.
    midhigh = node_id[level >= 1]
    for src in midhigh:
        if src in (leftpad, god_pkg):
            continue
        # 80% of mid/high packages get wired to a foundation lib (the conduit)
        if rng.random() < 0.80:
            dst = str(rng.choice(direct_dependents))
            add_edge(str(src), dst)

    # ----- GOD PACKAGE: depends on a huge number of others -----------------
    god_targets = rng.choice([n for n in node_id if n != god_pkg],
                             size=GOD_OUT_DEGREE, replace=False)
    for dst in god_targets:
        add_edge(god_pkg, str(dst))

    # ----- DIAMOND: two versions, each with many distinct dependents --------
    pool = [n for n in node_id if n not in (diamond_v1, diamond_v2, leftpad, god_pkg)]
    rng.shuffle(pool)
    v1_dependents = pool[:DIAMOND_DEPENDENTS]
    v2_dependents = pool[DIAMOND_DEPENDENTS:2 * DIAMOND_DEPENDENTS]
    for s in v1_dependents:
        add_edge(str(s), diamond_v1, w=int(rng.integers(1, 20)))
    for s in v2_dependents:
        add_edge(str(s), diamond_v2, w=int(rng.integers(1, 20)))

    # ----- ABANDONED-but-critical: give it high downstream reach -----------
    # make many mid-level libs depend on it so a large fraction reaches it.
    abandoned_direct = rng.choice([n for n in node_id[level >= 1]
                                   if n not in (abandoned, god_pkg)],
                                  size=45, replace=False)
    for s in abandoned_direct:
        add_edge(str(s), abandoned, w=int(rng.integers(1, 12)))

    # ----- guarantee LEFT-PAD tops transitive in-degree --------------------
    # Build the directed graph, find the few nodes with reach above left-pad, and
    # make THEM depend on left-pad: left-pad then inherits all their ancestors and
    # ends up with the single largest transitive in-degree, while its direct
    # in-degree stays an order of magnitude below the big libraries.
    import igraph as _ig
    _erows = [(s, d) for (s, d) in edges.keys()]
    _g = _ig.Graph(directed=True)
    _g.add_vertices(list(node_id))
    _g.add_edges([(s, d) for (s, d) in _erows])
    def _trans_in(graph, name):
        return len(graph.subcomponent(name, mode="in")) - 1
    lp_reach = _trans_in(_g, leftpad)
    # nodes whose reach >= left-pad's (excluding itself); make them depend on it
    above = []
    for nm in node_id:
        if nm == leftpad:
            continue
        if _trans_in(_g, nm) >= lp_reach:
            above.append(nm)
    for nm in above:
        add_edge(str(nm), leftpad, w=int(rng.integers(1, 5)))

    # ----- emit ------------------------------------------------------------
    edge_rows = [{"from_id": s, "to_id": d, "import_count": w}
                 for (s, d), w in edges.items()]
    edges_df = pd.DataFrame(edge_rows)

    nodes = pd.DataFrame({
        "node_id": node_id,
        "ecosystem_area": area,
        "maintainers": maintainers,
        "weekly_downloads": weekly_downloads,
        "months_since_update": months_since_update,
        "label": labels,
    })

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges_df.to_csv(HERE / "edges.csv", index=False)
    print(f"opensource-deps: {len(nodes)} packages, {len(edges_df)} dependency edges "
          f"(areas: {dict(pd.Series(area).value_counts())}).")


if __name__ == "__main__":
    main()
```

---

## `data/projects/opensource-deps/load.R`

```r
#' @name load.R
#' @title Load the `opensource-deps` project network (R)
#' @description
#'
#' Reads the two CSVs in this folder and builds a directed, weighted igraph
#' object: a software-package dependency graph (`A -> B` means A depends on B).
#' Run it straight (`Rscript load.R`) for a quick summary, or `source()` it and
#' call `load_deps()` to get the graph in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "opensource-deps")

#' Load the node table (one row per package).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per dependency).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Build the directed, weighted dependency graph.
#'
#' Edges are weighted by `import_count`. Direction is `from_id -> to_id`,
#' i.e. `from_id` depends on `to_id`.
load_deps <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = TRUE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$import_count
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n\U0001F4E6 opensource-deps (R)\n")
  cat("   Package dependency graph; A -> B means A depends on B, weighted by imports.\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_deps(nodes, edges)

  cat(sprintf("✅ Loaded %d packages and %d dependency edges.\n",
              nrow(nodes), nrow(edges)))
  cat(sprintf("\U0001F517 Directed: %s | total import call-sites: %s\n",
              is_directed(g), format(sum(edges$import_count), big.mark = ",")))
  ind <- igraph::degree(g, mode = "in")
  outd <- igraph::degree(g, mode = "out")
  cat(sprintf("\U0001F4CA Max direct in-degree: %d (%s) | max out-degree: %d (%s)\n",
              max(ind), names(which.max(ind)), max(outd), names(which.max(outd))))
  cat("\U0001F389 Graph ready. Object `g` is a directed, weighted igraph.\n")
}
```

---

## `data/projects/opensource-deps/load.py`

```python
"""Load the `opensource-deps` project network (Python).

Reads the two CSVs in this folder and builds a directed, weighted python-igraph
object: a software-package dependency graph (``A -> B`` means A depends on B).
Run it straight (``python load.py``) for a quick summary, or import
``load_deps()`` into your own script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per package."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per dependency (from_id depends on to_id)."""
    return pd.read_csv(HERE / "edges.csv")


def load_deps(nodes: pd.DataFrame | None = None,
              edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the directed, weighted dependency graph (edge weight = ``import_count``).

    Direction is ``from_id -> to_id``: ``from_id`` depends on ``to_id``.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=True, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["import_count"]
    return g


if __name__ == "__main__":
    print("\n\U0001F4E6 opensource-deps (Python)")
    print("   Package dependency graph; A -> B means A depends on B, weighted by imports.\n")

    nodes = load_nodes()
    edges = load_edges()
    g = load_deps(nodes, edges)

    print(f"✅ Loaded {len(nodes)} packages and {len(edges)} dependency edges.")
    print(f"\U0001F517 Directed: {g.is_directed()} | total import call-sites: "
          f"{edges['import_count'].sum():,}")
    indeg = g.indegree()
    outdeg = g.outdegree()
    names = g.vs["name"]
    i_max = max(range(len(indeg)), key=lambda i: indeg[i])
    o_max = max(range(len(outdeg)), key=lambda i: outdeg[i])
    print(f"\U0001F4CA Max direct in-degree: {indeg[i_max]} ({names[i_max]}) | "
          f"max out-degree: {outdeg[o_max]} ({names[o_max]})")
    print("\U0001F389 Graph ready. Object `g` is a directed, weighted igraph.")
```

---

## `data/projects/power-grid/README.md`

# power-grid

*A regional electrical transmission grid: buses (generators, substations, loads)
wired together by undirected transmission lines, each rated by capacity.*

![Preview of the power-grid network](thumb.png)

## At a glance

| | |
|---|---|
| **Direction** | Undirected (a transmission line carries power either way) |
| **Weights** | Weighted (`capacity_mw` per line; `length_km` attribute) |
| **Modality** | Single mode (`bus`), with a `kind` tag — `generator` / `substation` / `load` |
| **Temporal** | No — a single static snapshot of the grid |
| **Nodes** | 300 buses (57 generators + 101 substations + 142 loads) |
| **Edges** | 422 transmission lines |
| **Files** | `nodes.csv`, `edges.csv`, `regions.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

This is the transmission grid of a fictional utility split into three control
areas. Each **bus** is a node — a generating plant, a switching substation, or a
load center that draws power. Each undirected **transmission line** is an edge,
rated by its MW carrying `capacity_mw` and tagged with a `length_km`. Buses carry
a `capacity_mw` field (generation nameplate for generators, peak draw for loads),
a `voltage_kv` level, a region, and map coordinates. A companion `regions.csv`
names the three control areas.

This is a criticality-and-resilience network. It rewards students who ask what
happens when a piece fails. Some questions to chew on:

- If exactly one line went out, which one would hurt the most — and does line
  capacity, line length, or its position in the network tell you which?
- Where is the power *made* versus where is it *used*? Does the geography line up,
  and if not, what carries the difference?
- Is the whole grid built the same way, or are some areas looped-and-redundant
  while others hang off a single feed?
- Which bus is more important than it looks — central to the flow of power without
  being one of the biggest or most-connected nodes?
- If you had a maintenance budget for exactly one upgrade, where would betweenness,
  degree, and capacity each tell you to spend it — and would they agree?

> **Note.** The interesting findings here are deliberately *not* documented. "Big
> substations have more lines" is the starting point, not a finding. Push past it.

## `nodes.csv`

One row per bus.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique bus key. Referenced by edges. | character | `BUS0001`, `BUS0252` |
| `kind` | Bus kind | Role of the bus on the grid. | character | `generator`, `substation`, `load` |
| `region` | Control area | Which of the three control areas the bus sits in (join to `regions.csv`). | character | `A`, `B`, `C` |
| `label` | Display name | Human-readable label. (`name` is avoided — python-igraph reserves it for the ID.) | character | `Load 0001`, `Generator 0252` |
| `x` | X coordinate | Horizontal position on a 0–100 map grid. | double | `16.56`, `90.12` |
| `y` | Y coordinate | Vertical position on a 0–100 map grid. | double | `63.25`, `70.40` |
| `capacity_mw` | Capacity (MW) | Generation nameplate for generators, peak load draw for loads; ~0 for pass-through substations. | integer | `64`, `235`, `812` |
| `voltage_kv` | Voltage level | Nominal operating voltage of the bus, kilovolts. | integer | `69`, `230`, `500` |

## `edges.csv`

One row per transmission line. Undirected (`from_id`/`to_id` ordering is arbitrary).

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | Endpoint bus ID | One end of the line. | character | `BUS0092`, `BUS0023` |
| `to_id` | Endpoint bus ID | Other end of the line. | character | `BUS0098`, `BUS0092` |
| `capacity_mw` | Line capacity (MW) | Thermal carrying capacity of the line (the edge weight). | integer | `202`, `1500`, `1800` |
| `length_km` | Line length | Physical length of the line, kilometers. | double | `14.04`, `3.53` |

## `regions.csv`

Lookup table for the three control areas. Not a node list — join it onto
`nodes.csv` on `region`.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `region` | Region code | Control-area code, matches `nodes.region`. | character | `A`, `B`, `C` |
| `name` | Region name | Human-readable control-area name. | character | `Metro East Control Area`, `High Plains Control Area` |
| `center_x` | Center X | Approximate map-grid X of the area's center. | integer | `28`, `90` |
| `center_y` | Center Y | Approximate map-grid Y of the area's center. | integer | `55`, `70` |

## Load it

```bash
Rscript data/projects/power-grid/load.R     # R    (igraph)
python  data/projects/power-grid/load.py     # Python (python-igraph)
```

Both build an undirected, weighted `igraph` graph and print a one-screen summary.
In the [R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**power-grid** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/power-grid>

---

## `data/projects/power-grid/_generate.py`

```python
"""Generate the `power-grid` project network (deterministic).

A regional electrical transmission grid (static -- no time dimension):
  - ~300 bus nodes (kind = "generator" | "substation" | "load")
Edges are undirected transmission lines, weighted by line `capacity_mw`, each
with a `length_km`. A companion `regions.csv` lists the three control areas.

Design parameters (the only record of the planted structure):
  - INTERTIE: ONE high-capacity interconnect line ties region C (a remote
    generation area) to the rest of the grid. It carries very high edge
    betweenness; removing it severs C from the load centers.
  - GEN_LOAD_MISMATCH: generators are concentrated in region C (a remote
    renewable cluster) while load concentrates in regions A and B, so power must
    traverse a few long high-capacity corridors -- the critical path.
  - RADIAL_TAILS: region B has radial (tree-like, single-feed) tails that lose
    power if one upstream line fails; region A's core is meshed (looped,
    redundant) and does not.
  - BRIDGE_SUB: a hidden bridge substation with high betweenness but modest
    degree sits between two otherwise weakly connected clusters inside region A.

Run:
    python data/projects/power-grid/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

# region sizes (sum ~ 300)
N_A = 130      # meshed urban load region
N_B = 110      # mixed region with radial tails
N_C = 60       # remote generation region
REGIONS = ["A", "B", "C"]

# --- planted parameters -----------------------------------------------------
VOLT_LEVELS = [69, 138, 230, 345, 500]
INTERTIE_CAP = 1800           # MW on the single C<->grid intertie
CORRIDOR_CAP = 1500           # MW on the long generation corridors
MESH_EXTRA_EDGES = 110        # extra loops added to region A's core (meshing)
RADIAL_FRACTION = 0.55        # fraction of region B that is radial tails


def main() -> None:
    rng = np.random.default_rng(SEED)

    # region centers on a 0-100 map; C is remote (far right)
    centers = {"A": (28, 55), "B": (52, 30), "C": (90, 70)}

    rows = []
    nid = 1

    def make_node(region, kind, cx, cy, spread, cap_lo, cap_hi):
        nonlocal nid
        x = float(np.clip(cx + rng.normal(0, spread), 0, 100))
        y = float(np.clip(cy + rng.normal(0, spread), 0, 100))
        node_id = f"BUS{nid:04d}"
        nid += 1
        cap = int(rng.integers(cap_lo, cap_hi)) if cap_hi > cap_lo else 0
        rows.append({
            "node_id": node_id, "kind": kind, "region": region,
            "label": f"{kind.capitalize()} {node_id[3:]}",
            "x": round(x, 2), "y": round(y, 2),
            "capacity_mw": cap,
            "voltage_kv": int(rng.choice(VOLT_LEVELS,
                              p=[0.30, 0.30, 0.20, 0.13, 0.07])),
        })
        return node_id

    # ----- region A: meshed urban load + a few generators ------------------
    a_ids = []
    for _ in range(N_A):
        roll = rng.random()
        if roll < 0.08:
            kind, cap = "generator", (150, 600)
        elif roll < 0.45:
            kind, cap = "substation", (0, 1)
        else:
            kind, cap = "load", (40, 320)        # capacity_mw = peak load draw
        a_ids.append(make_node("A", kind, *centers["A"], 11, *cap))

    # ----- region B: mixed, with radial tails ------------------------------
    b_ids = []
    for _ in range(N_B):
        roll = rng.random()
        if roll < 0.06:
            kind, cap = "generator", (120, 450)
        elif roll < 0.40:
            kind, cap = "substation", (0, 1)
        else:
            kind, cap = "load", (30, 260)
        b_ids.append(make_node("B", kind, *centers["B"], 12, *cap))

    # ----- region C: remote GENERATION cluster (renewables) ----------------
    c_ids = []
    for _ in range(N_C):
        roll = rng.random()
        if roll < 0.62:
            kind, cap = "generator", (200, 900)   # lots of generation
        elif roll < 0.85:
            kind, cap = "substation", (0, 1)
        else:
            kind, cap = "load", (10, 80)          # very little load out here
        c_ids.append(make_node("C", kind, *centers["C"], 9, *cap))

    nodes = pd.DataFrame(rows)
    pos = {r.node_id: (r.x, r.y) for r in nodes.itertuples()}

    def dist(a, b):
        (ax, ay), (bx, by) = pos[a], pos[b]
        return float(np.hypot(ax - bx, ay - by))

    edges_set: dict[tuple[str, str], dict] = {}

    def add_line(a, b, cap, kind="line"):
        if a == b:
            return
        key = (a, b) if a < b else (b, a)
        if key in edges_set:
            return
        d = dist(a, b)
        edges_set[key] = {
            "from_id": key[0], "to_id": key[1],
            "capacity_mw": int(cap),
            "length_km": round(d * 1.4 + rng.uniform(0, 2), 2),
        }

    def nearest_within(node, pool, k):
        ds = sorted((dist(node, p), p) for p in pool if p != node)
        return [p for _, p in ds[:k]]

    # ----- region A core: build a connected MESH (redundant loops) ---------
    # First a spanning backbone (nearest-neighbor chain), then many extra loops.
    a_sorted = sorted(a_ids, key=lambda n: pos[n][0] + pos[n][1])
    for i in range(1, len(a_sorted)):
        # connect each to a nearby earlier node (keeps it connected + local)
        prev = nearest_within(a_sorted[i], a_sorted[:i], 1)[0]
        add_line(a_sorted[i], prev, rng.integers(200, 700))
    # extra meshing edges among nearby A nodes -> loops, triangles, redundancy
    added = 0
    attempts = 0
    while added < MESH_EXTRA_EDGES and attempts < MESH_EXTRA_EDGES * 8:
        attempts += 1
        u = rng.choice(a_ids)
        cand = nearest_within(u, a_ids, 6)
        v = rng.choice(cand)
        key = (u, v) if u < v else (v, u)
        if key not in edges_set:
            add_line(u, v, rng.integers(250, 800))
            added += 1

    # ----- region B: a meshed sub-core PLUS radial (tree) tails ------------
    n_radial = int(N_B * RADIAL_FRACTION)
    b_core = b_ids[:N_B - n_radial]
    b_tails = b_ids[N_B - n_radial:]
    # core: small mesh
    b_core_sorted = sorted(b_core, key=lambda n: pos[n][0] + pos[n][1])
    for i in range(1, len(b_core_sorted)):
        prev = nearest_within(b_core_sorted[i], b_core_sorted[:i], 1)[0]
        add_line(b_core_sorted[i], prev, rng.integers(180, 600))
    for _ in range(18):
        u = rng.choice(b_core)
        v = rng.choice(nearest_within(u, b_core, 5))
        add_line(u, v, rng.integers(200, 550))
    # tails: each radial node hangs off exactly ONE upstream node (a tree) ->
    # single feed, no redundancy. Attach to nearest already-connected B node.
    connected_b = list(b_core)
    for t in b_tails:
        parent = nearest_within(t, connected_b, 1)[0]
        add_line(t, parent, rng.integers(60, 200))   # thinner radial feeders
        connected_b.append(t)

    # ----- region C: internal collector network (radial-ish to a C hub) ----
    # choose a C substation as the collector hub
    c_subs = [n for n in c_ids
              if nodes.loc[nodes.node_id == n, "kind"].iloc[0] == "substation"]
    c_hub = c_subs[0] if c_subs else c_ids[0]
    c_sorted = sorted(c_ids, key=lambda n: dist(n, c_hub))
    connected_c = [c_hub]
    for n in c_sorted:
        if n == c_hub:
            continue
        parent = nearest_within(n, connected_c, 1)[0]
        add_line(n, parent, rng.integers(150, 500))
        connected_c.append(n)
    # a little meshing inside C so it isn't a pure tree
    for _ in range(10):
        u = rng.choice(c_ids)
        v = rng.choice(nearest_within(u, c_ids, 4))
        add_line(u, v, rng.integers(150, 450))

    # ----- A <-> B coupling: a few normal-capacity ties (redundant) --------
    # pick the closest A/B node pairs and connect a handful (so A-B is robust)
    ab_pairs = sorted(
        ((dist(a, b), a, b) for a in a_ids for b in b_ids),
        key=lambda t: t[0])[:6]
    for _, a, b in ab_pairs:
        add_line(a, b, rng.integers(400, 900))

    # ----- THE GENERATION CORRIDORS + SINGLE INTERTIE to region C ----------
    # Region C connects to the rest of the grid through ONE intertie line into a
    # region-B gateway substation, plus long high-capacity corridors carry C's
    # generation toward the A/B load centers. The intertie is the sole electrical
    # path from C to everything else.
    # gateway on the grid side: the region-B node closest to the C hub
    gateway = min(b_ids, key=lambda n: dist(n, c_hub))
    # the single intertie line (very high capacity, long)
    add_line(c_hub, gateway, INTERTIE_CAP)
    # long corridors: from gateway deep into A's core (high-capacity backbone)
    a_core_targets = sorted(a_ids, key=lambda n: dist(n, gateway))[:3]
    corridor_prev = gateway
    for tgt in a_core_targets:
        add_line(corridor_prev, tgt, CORRIDOR_CAP)
        corridor_prev = tgt

    # ----- BRIDGE SUBSTATION inside region A -------------------------------
    # Split region A loosely into two halves by x; route nearly all cross-half
    # A traffic through ONE substation with modest degree (a hidden bridge).
    a_x = {n: pos[n][0] for n in a_ids}
    median_x = np.median(list(a_x.values()))
    left = [n for n in a_ids if a_x[n] < median_x]
    right = [n for n in a_ids if a_x[n] >= median_x]
    # remove any existing left-right A edges to force the bottleneck
    to_drop = []
    for key in list(edges_set.keys()):
        u, v = key
        if u in a_x and v in a_x:
            lu = u in left
            lv = v in left
            if lu != lv:
                to_drop.append(key)
    # keep the bridge edges only: pick a bridge substation near the divide
    a_subs = [n for n in a_ids
              if nodes.loc[nodes.node_id == n, "kind"].iloc[0] == "substation"]
    bridge = min(a_subs, key=lambda n: abs(a_x[n] - median_x))
    for key in to_drop:
        del edges_set[key]
    # connect the bridge to ONE node on each side (deliberately modest degree)
    bl = nearest_within(bridge, left, 1)
    br = nearest_within(bridge, right, 1)
    for n in bl + br:
        add_line(bridge, n, rng.integers(300, 700))

    # repair: dropping the cross-divide A edges can orphan a few nodes. Reconnect
    # any now-isolated A node to its nearest SAME-SIDE neighbor (never across the
    # divide), so the bridge stays the sole left<->right path but no bus is dead.
    incident = set()
    for (u, v) in edges_set:
        incident.add(u)
        incident.add(v)
    for n in a_ids:
        if n in incident:
            continue
        side = left if n in left else right
        side_pool = [m for m in side if m != n and m != bridge]
        parent = nearest_within(n, side_pool, 1)[0]
        add_line(n, parent, rng.integers(200, 600))

    edges = pd.DataFrame(list(edges_set.values()))

    # ----- regions lookup table --------------------------------------------
    regions = pd.DataFrame({
        "region": REGIONS,
        "name": ["Metro East Control Area", "Central Valley Control Area",
                 "High Plains Control Area"],
        "center_x": [centers[r][0] for r in REGIONS],
        "center_y": [centers[r][1] for r in REGIONS],
    })

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)
    regions.to_csv(HERE / "regions.csv", index=False)
    kc = nodes.kind.value_counts()
    print(f"power-grid: {len(nodes)} buses "
          f"({kc.get('generator',0)} generators + {kc.get('substation',0)} substations + "
          f"{kc.get('load',0)} loads), {len(edges)} lines, {len(regions)} regions.")


if __name__ == "__main__":
    main()
```

---

## `data/projects/power-grid/load.R`

```r
#' @name load.R
#' @title Load the `power-grid` project network (R)
#' @description
#'
#' Reads the CSVs in this folder and builds an undirected, weighted igraph
#' object: a regional electrical transmission grid of buses and lines. Run it
#' straight (`Rscript load.R`) for a quick summary, or `source()` it and call
#' `load_grid()` to get the graph in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "power-grid")

#' Load the node table (one row per bus).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per transmission line).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Load the control-area lookup table (join onto nodes by `region`).
load_regions <- function() {
  read.csv(file.path(.dir(), "regions.csv"), stringsAsFactors = FALSE)
}

#' Build the undirected, weighted grid graph.
#'
#' Edges are weighted by line `capacity_mw`. The graph is a single static
#' snapshot (no time dimension).
load_grid <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = FALSE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$capacity_mw
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n\U0001F50C power-grid (R)\n")
  cat("   Undirected transmission grid; lines weighted by capacity (MW).\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_grid(nodes, edges)

  cat(sprintf("✅ Loaded %d buses (%d generators, %d substations, %d loads) and %d lines.\n",
              nrow(nodes), sum(nodes$kind == "generator"),
              sum(nodes$kind == "substation"), sum(nodes$kind == "load"), nrow(edges)))
  cat(sprintf("\U0001F517 Directed: %s | total line capacity: %s MW\n",
              is_directed(g), format(sum(edges$capacity_mw), big.mark = ",")))
  cat("\U0001F389 Graph ready. Object `g` is an undirected, weighted igraph.\n")
}
```

---

## `data/projects/power-grid/load.py`

```python
"""Load the `power-grid` project network (Python).

Reads the CSVs in this folder and builds an undirected, weighted python-igraph
object: a regional electrical transmission grid of buses and lines. Run it
straight (``python load.py``) for a quick summary, or import ``load_grid()`` into
your own script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per bus."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per transmission line."""
    return pd.read_csv(HERE / "edges.csv")


def load_regions() -> pd.DataFrame:
    """Control-area lookup table (join onto nodes by ``region``)."""
    return pd.read_csv(HERE / "regions.csv")


def load_grid(nodes: pd.DataFrame | None = None,
              edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the undirected, weighted grid graph (edge weight = ``capacity_mw``).

    The graph is a single static snapshot (no time dimension).
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=False, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["capacity_mw"]
    return g


if __name__ == "__main__":
    print("\n🔌 power-grid (Python)")
    print("   Undirected transmission grid; lines weighted by capacity (MW).\n")

    nodes = load_nodes()
    edges = load_edges()
    g = load_grid(nodes, edges)

    kinds = nodes["kind"].value_counts()
    print(f"✅ Loaded {len(nodes)} buses "
          f"({kinds.get('generator',0)} generators, {kinds.get('substation',0)} substations, "
          f"{kinds.get('load',0)} loads) and {len(edges)} lines.")
    print(f"🔗 Directed: {g.is_directed()} | total line capacity: "
          f"{edges['capacity_mw'].sum():,} MW")
    print("🎉 Graph ready. Object `g` is an undirected, weighted igraph.")
```

---

## `data/projects/reorg-comms/README.md`

# reorg-comms

*Internal employee communication (email + chat volume) at a ~250-person company,
observed before, during, and after a reorganization and layoff.*

![Preview of the reorg-comms network](thumb.png)

## At a glance

| | |
|---|---|
| **Direction** | Directed (message flow: sender → receiver) |
| **Weights** | Weighted (`message_count` per edge) |
| **Modality** | Unimodal — one node kind (`employee`) |
| **Temporal** | Yes — one row per (sender, receiver, **period**): `before` / `during` / `after` |
| **Nodes** | 250 (employees across 8 departments) |
| **Edges** | 7,926 (≈2,562 before + ≈3,511 during + ≈1,853 after) |
| **Files** | `nodes.csv`, `edges.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

A directed, weighted communication network for a fictional company. Each
**employee** belongs to a department and sits somewhere on the formal org chart
(`level` and `manager_id`); a directed **message edge** carries a
`message_count` from a sender to a receiver. The company is observed across three
**periods** — a stable org (`before`), the middle of a reorganization and layoff
(`during`), and the settled, smaller org (`after`). The node table records each
employee's department, level, tenure, location, formal manager, and whether they
were laid off.

This is a communication, influence, and resilience network with an organizational
shock you can study as a natural experiment. Some questions to chew on:

- Does the org chart predict who actually holds communication power? Are the most
  *connected* people the same as the most *senior* people?
- Is there anyone whose departure would quietly sever communication between two
  parts of the company — and does their job title hint at that importance?
- Some people left in the layoff. Were they interchangeable, or did the company
  lose connective tissue it did not realize it had?
- Compare the three periods. Did the company talk more or less under stress? Did
  the *shape* of who-talks-to-whom change after the teams were redrawn?
- If you wanted to keep two departments talking after a reorg, who would you make
  sure to keep?

> **Note.** The interesting findings here are deliberately *not* documented.
> "Senior people send more messages" is the starting point, not a finding. Push
> past it — and remember that the formal hierarchy and the real one need not match.

## `nodes.csv`

One row per employee.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique employee key (`E###`). Referenced by edges and by `manager_id`. | character | `E001`, `E004`, `E250` |
| `kind` | Node kind | Node type (all employees in this network). | character | `employee` |
| `label` | Display name | Human-readable label. (`name` is avoided — python-igraph reserves it for the ID.) | character | `Emp 001`, `Emp 004` |
| `dept` | Department | Organizational unit the employee belongs to. | character | `Engineering`, `Sales`, `Finance` |
| `level` | Job level | Seniority tier on the formal hierarchy. | character | `ic`, `manager`, `director`, `vp` |
| `tenure_months` | Tenure | Months the employee has been at the company. | integer | `9`, `45`, `173` |
| `location` | Work location | Where the employee is based. | character | `HQ`, `Remote`, `EU Office`, `APAC Office` |
| `manager_id` | Manager node ID | `node_id` of the employee's formal manager (blank for department heads). | character | `E002`, `E227`, *(blank)* |
| `laid_off` | Laid off | 1 if the employee was let go in the layoff, else 0. | integer | `0`, `1` |

## `edges.csv`

One row per (sender, receiver, period). Directed; a pair can appear up to three
times (once per period).

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `sender_id` | Sender node ID | Employee who sent the messages. | character | `E001`, `E004` |
| `receiver_id` | Receiver node ID | Employee who received the messages. | character | `E004`, `E017` |
| `period` | Period | Org era: `before`, `during`, or `after` the reorganization. | character | `before`, `during`, `after` |
| `message_count` | Message count | Number of messages sent on that edge in that period (the edge weight). | integer | `1`, `2`, `41` |

## Load it

```bash
Rscript data/projects/reorg-comms/load.R     # R    (igraph)
python  data/projects/reorg-comms/load.py     # Python (python-igraph)
```

Both build a directed, weighted `igraph` graph and print a one-screen summary. In
the [R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**reorg-comms** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/reorg-comms>

---

## `data/projects/reorg-comms/_generate.py`

```python
"""Generate the `reorg-comms` project network (deterministic).

Internal corporate communication (email + chat volume) among ~250 employees of a
fictional company, observed across three periods around a reorganization + layoff:
  - period = "before"  : stable org
  - period = "during"  : reorg announced, layoffs happening (anxiety spike)
  - period = "after"   : new teams settled, headcount reduced

Nodes are employees (kind = "employee"); edges are directed messages
sender -> receiver for a given period, weighted by message_count.

Design parameters (the only record of the planted structure):
  - INFORMAL_BROKER: a long-tenured low-`level` IC who is one of the top brokers
    by betweenness — informal influence the formal org chart (manager_id tree)
    does not show.
  - BOTTLENECK_MGR: one manager who sits on the only communication path between
    two large departments (very high betweenness); most cross-dept info routes
    through them.
  - LOAD_BEARING_LEAVERS: several laid-off employees were high-betweenness
    connectors; removing the laid_off set fragments cross-dept comms far more
    than removing a random equal-size set.
  - SILOING: cross-department edges fall and within-(new-)team edges rise from
    before -> after (modularity by dept rises after the reorg).
  - VOLUME_SPIKE: total message volume peaks DURING (uncertainty / anxiety).

Run:
    python data/projects/reorg-comms/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

PERIODS = ["before", "during", "after"]

N_EMP = 250
DEPTS = ["Engineering", "Product", "Sales", "Marketing",
         "Finance", "Operations", "Support", "HR"]
LOCATIONS = ["HQ", "Remote", "EU Office", "APAC Office"]

# --- planted parameters -----------------------------------------------------
LAYOFF_RATE = 0.18          # fraction of employees laid off
VOLUME_DURING = 1.55        # message-volume multiplier DURING (anxiety spike)
VOLUME_AFTER = 0.82         # message-volume multiplier AFTER (smaller org, calmer)
CROSS_DEPT_BEFORE = 0.32    # share of comms that cross departments BEFORE
CROSS_DEPT_AFTER = 0.14     # share that cross departments AFTER (siloing)
N_LOAD_BEARING = 7          # laid-off employees who were key connectors


def main() -> None:
    rng = np.random.default_rng(SEED)

    # ----- departments & levels -------------------------------------------
    # department sizes (Engineering & Sales are the two big ones the bottleneck
    # manager will sit between).
    dept_sizes = np.array([60, 28, 55, 22, 18, 25, 27, 15])
    dept_sizes = dept_sizes * N_EMP // dept_sizes.sum()
    # fix rounding so they sum to N_EMP
    dept_sizes[0] += N_EMP - dept_sizes.sum()
    dept_of = []
    for d, n in zip(DEPTS, dept_sizes):
        dept_of += [d] * int(n)
    dept_of = np.array(dept_of)
    rng.shuffle(dept_of)

    emp_ids = [f"E{i:03d}" for i in range(1, N_EMP + 1)]

    # levels: mostly ICs, some managers, fewer directors, few VPs
    level = rng.choice(["ic", "manager", "director", "vp"],
                       size=N_EMP, p=[0.70, 0.18, 0.09, 0.03])
    tenure = rng.integers(2, 180, N_EMP)
    location = rng.choice(LOCATIONS, size=N_EMP, p=[0.45, 0.30, 0.15, 0.10])

    # ----- build a formal org chart (manager_id tree) per department -------
    # each dept gets a head (director or vp), managers report to head, ICs report
    # to managers. manager_id is the FORMAL reporting line.
    manager_id = [""] * N_EMP
    idx_by_dept = {d: [i for i in range(N_EMP) if dept_of[i] == d] for d in DEPTS}
    for d in DEPTS:
        members = idx_by_dept[d]
        # head = highest level member (prefer vp, then director, then manager)
        order = {"vp": 0, "director": 1, "manager": 2, "ic": 3}
        members_sorted = sorted(members, key=lambda i: order[level[i]])
        head = members_sorted[0]
        # ensure head is at least director
        if level[head] not in ("director", "vp"):
            level[head] = "director"
        mgrs = [i for i in members if level[i] == "manager" and i != head]
        if not mgrs:
            # promote a couple ICs to manager so there is a middle layer
            cand = [i for i in members if level[i] == "ic" and i != head][:2]
            for c in cand:
                level[c] = "manager"
            mgrs = cand
        for m in mgrs:
            manager_id[m] = emp_ids[head]
        ics = [i for i in members if i not in mgrs and i != head]
        for i in ics:
            manager_id[i] = emp_ids[int(rng.choice(mgrs))] if mgrs else emp_ids[head]
        # head reports to nobody (blank) -> top of the dept

    # ----- planted special people -----------------------------------------
    eng = idx_by_dept["Engineering"]
    sales = idx_by_dept["Sales"]

    # INFORMAL_BROKER: a long-tenured IC in Engineering (low level, high influence)
    eng_ics = [i for i in eng if level[i] == "ic"]
    informal_broker = max(eng_ics, key=lambda i: tenure[i])
    tenure[informal_broker] = max(tenure[informal_broker], 160)  # very senior IC

    # BOTTLENECK_MGR: a manager who alone bridges Engineering <-> Sales.
    eng_mgrs = [i for i in eng if level[i] == "manager"]
    bottleneck_mgr = eng_mgrs[0]

    nodes = pd.DataFrame({
        "node_id": emp_ids,
        "kind": "employee",
        "label": [f"Emp {i:03d}" for i in range(1, N_EMP + 1)],
        "dept": dept_of,
        "level": level,
        "tenure_months": tenure,
        "location": location,
        "manager_id": manager_id,
    })

    # ----- layoffs ---------------------------------------------------------
    n_layoff = int(round(N_EMP * LAYOFF_RATE))
    # LOAD_BEARING_LEAVERS: pick some cross-dept connectors to be laid off, plus
    # the rest at random. (Connectors = people we will wire as cross-dept bridges.)
    # We designate bridge people first, then ensure several are laid off.
    # Cross-dept bridge pool: a handful per department.
    bridge_pool = []
    for d in DEPTS:
        members = [i for i in idx_by_dept[d]
                   if i not in (informal_broker, bottleneck_mgr)]
        bridge_pool += list(rng.choice(members, size=3, replace=False))
    load_bearing = list(rng.choice(bridge_pool, size=N_LOAD_BEARING, replace=False))
    # rest of layoffs random, excluding protected key people we want to keep
    protected = {informal_broker, bottleneck_mgr}
    pool = [i for i in range(N_EMP)
            if i not in load_bearing and i not in protected]
    extra = list(rng.choice(pool, size=n_layoff - len(load_bearing), replace=False))
    laid_off_idx = set(load_bearing) | set(extra)
    nodes["laid_off"] = [1 if i in laid_off_idx else 0 for i in range(N_EMP)]

    # ----- communication generation ---------------------------------------
    # Each employee has an "activity" level; messages flow mostly within dept,
    # a tunable share cross-dept, plus planted bridges.
    activity = rng.lognormal(mean=2.4, sigma=0.5, size=N_EMP)
    # managers/directors a bit more active
    lvl_boost = {"ic": 1.0, "manager": 1.4, "director": 1.6, "vp": 1.8}
    activity = activity * np.array([lvl_boost[level[i]] for i in range(N_EMP)])

    # --- designate cross-department bridges ------------------------------
    # Cross-dept messages must pass THROUGH a bridge employee, so bridges sit on
    # the only cross-dept paths -> high betweenness, and removing them fragments
    # cross-dept communication. Each ordered department pair gets one or more
    # assigned bridge "owners". This is what makes the planted connectors real.
    pair_bridge = {}   # frozenset({deptA, deptB}) -> list of employee idx
    for a in range(len(DEPTS)):
        for b in range(a + 1, len(DEPTS)):
            da, db = DEPTS[a], DEPTS[b]
            key = frozenset({da, db})
            if key == frozenset({"Engineering", "Sales"}):
                pair_bridge[key] = [bottleneck_mgr]   # SOLE bridge -> bottleneck
            else:
                # one owner from each side, drawn from the bridge pool
                opts_a = [i for i in bridge_pool if dept_of[i] == da] or \
                         [i for i in idx_by_dept[da] if level[i] != "ic"][:1] or \
                         [idx_by_dept[da][0]]
                opts_b = [i for i in bridge_pool if dept_of[i] == db] or \
                         [i for i in idx_by_dept[db] if level[i] != "ic"][:1] or \
                         [idx_by_dept[db][0]]
                pair_bridge[key] = [opts_a[0], opts_b[0]]

    # informal broker: make it a bridge owner for MANY dept pairs (across the
    # whole company), giving a low-level IC outsized betweenness.
    for key in list(pair_bridge):
        if "Engineering" in key and frozenset({"Engineering"}) != key:
            if key != frozenset({"Engineering", "Sales"}):
                pair_bridge[key] = list(set(pair_bridge[key]) | {informal_broker})

    edge_rows = []

    def add_through_bridge(pair_counts, s, r, active_set):
        """Route a cross-dept message s->r through an assigned bridge."""
        key = frozenset({dept_of[s], dept_of[r]})
        owners = [b for b in pair_bridge.get(key, []) if b in active_set]
        if not owners:
            return  # no live bridge -> message cannot cross (fragmentation!)
        br = int(rng.choice(owners))
        if br == s or br == r:
            _bump(pair_counts, s, r)
            return
        # model the two-hop path s -> bridge -> r as two directed edges
        _bump(pair_counts, s, br)
        _bump(pair_counts, br, r)

    def gen_period(period):
        if period == "before":
            vol = 1.0; cross = CROSS_DEPT_BEFORE; active = set(range(N_EMP))
        elif period == "during":
            vol = VOLUME_DURING; cross = (CROSS_DEPT_BEFORE + CROSS_DEPT_AFTER) / 2
            active = set(range(N_EMP))  # leavers still present during
        else:  # after
            vol = VOLUME_AFTER; cross = CROSS_DEPT_AFTER
            active = set(i for i in range(N_EMP) if i not in laid_off_idx)

        active = list(active)
        active_set = set(active)
        n_msgs = int(2600 * vol)

        w = np.array([activity[i] for i in active])
        w = w / w.sum()

        pair_counts = {}
        for _ in range(n_msgs):
            s = int(rng.choice(active, p=w))
            if rng.random() < cross:
                # cross-department message -> must go through a bridge
                r = _other_dept_receiver(rng, s, dept_of, active, active_set)
                if dept_of[r] == dept_of[s]:
                    continue
                add_through_bridge(pair_counts, s, r, active_set)
            else:
                # within-department message
                same = [i for i in idx_by_dept[dept_of[s]]
                        if i in active_set and i != s]
                if not same:
                    continue
                r = int(rng.choice(same))
                if r != s:
                    _bump(pair_counts, s, r)

        for (s, r), c in pair_counts.items():
            c2 = max(1, int(round(c * rng.uniform(0.85, 1.15))))
            edge_rows.append({
                "sender_id": emp_ids[s], "receiver_id": emp_ids[r],
                "period": period, "message_count": c2,
            })

    for p in PERIODS:
        gen_period(p)

    edges = pd.DataFrame(edge_rows)
    # collapse any dup (sender, receiver, period)
    edges = (edges.groupby(["sender_id", "receiver_id", "period"], as_index=False)
             .agg(message_count=("message_count", "sum")))

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)

    import os
    if os.environ.get("REORG_DEBUG"):
        print("DEBUG informal_broker:", emp_ids[informal_broker],
              "dept", dept_of[informal_broker], "level", level[informal_broker],
              "tenure", tenure[informal_broker])
        print("DEBUG bottleneck_mgr:", emp_ids[bottleneck_mgr],
              "dept", dept_of[bottleneck_mgr], "level", level[bottleneck_mgr])
        print("DEBUG load_bearing leavers:", [emp_ids[i] for i in load_bearing])
        print("DEBUG n laid_off:", len(laid_off_idx))

    print(f"reorg-comms: {len(nodes)} nodes (employees), {len(edges)} edges "
          f"across {edges['period'].nunique()} periods "
          f"(before={int((edges.period=='before').sum())}, "
          f"during={int((edges.period=='during').sum())}, "
          f"after={int((edges.period=='after').sum())}); "
          f"{int(nodes.laid_off.sum())} laid off.")


def _bump(d, s, r):
    d[(s, r)] = d.get((s, r), 0) + 1


def _other_dept_receiver(rng, s, dept_of, active, active_set):
    for _ in range(8):
        r = int(rng.choice(active))
        if dept_of[r] != dept_of[s]:
            return r
    return int(rng.choice(active))


if __name__ == "__main__":
    main()
```

---

## `data/projects/reorg-comms/load.R`

```r
#' @name load.R
#' @title Load the `reorg-comms` project network (R)
#' @description
#'
#' Reads the two CSVs in this folder and builds a directed, weighted igraph
#' object: internal message volume between employees, recorded across three
#' periods (`before` / `during` / `after` a reorganization + layoff). Run it
#' straight (`Rscript load.R`) for a quick summary, or `source()` it and call
#' `load_reorg()` to get the graph in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "reorg-comms")

#' Load the node table (one row per employee).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE,
           colClasses = c(manager_id = "character"))
}

#' Load the edge table (one row per sender x receiver x period).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Build the directed, weighted graph.
#'
#' Edges are weighted by `message_count`. Because the data is temporal (a
#' `period` column), a sender->receiver pair can appear up to three times (once
#' per period) as parallel edges. Filter to one `period` first if you want a
#' simple graph, e.g. `edges <- subset(load_edges(), period == "before")`.
#'
#' Note: `manager_id` on the node table is the FORMAL org-chart reporting line
#' (blank for department heads), separate from who actually messages whom.
load_reorg <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = TRUE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$message_count
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n\U0001F4AC reorg-comms (R)\n")
  cat("   Employee-to-employee message volume; weighted by message_count,\n")
  cat("   across before / during / after a reorganization + layoff.\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_reorg(nodes, edges)

  cat(sprintf("✅ Loaded %d employees (%d laid off) and %d edges across %d periods.\n",
              nrow(nodes), sum(nodes$laid_off == 1), nrow(edges),
              length(unique(edges$period))))
  cat(sprintf("\U0001F517 Directed: %s | total messages: %s\n",
              is_directed(g), format(sum(edges$message_count), big.mark = ",")))
  per <- tapply(edges$message_count, edges$period, sum)
  cat("\U0001F4E8 Messages by period: ",
      paste(sprintf("%s=%s", names(per), format(per, big.mark = ",")),
            collapse = " | "), "\n")
  cat("\U0001F389 Graph ready. Object `g` is a directed, weighted igraph.\n")
}
```

---

## `data/projects/reorg-comms/load.py`

```python
"""Load the `reorg-comms` project network (Python).

Reads the two CSVs in this folder and builds a directed, weighted python-igraph
object: internal message volume between employees, recorded across three periods
(``before`` / ``during`` / ``after`` a reorganization + layoff). Run it straight
(``python load.py``) for a quick summary, or import ``load_reorg()`` into your own
script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per employee.

    ``manager_id`` is read as a string (it is a node id, blank for department
    heads).
    """
    return pd.read_csv(HERE / "nodes.csv", dtype={"manager_id": "string"})


def load_edges() -> pd.DataFrame:
    """Edge table: one row per sender x receiver x period."""
    return pd.read_csv(HERE / "edges.csv")


def load_reorg(nodes: pd.DataFrame | None = None,
               edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the directed, weighted graph (edge weight = ``message_count``).

    The data is temporal (a ``period`` column), so a sender->receiver pair can
    appear up to three times (once per period) as parallel edges. Filter to one
    ``period`` first if you want a simple graph, e.g.
    ``edges[edges.period == "before"]``.

    Note: ``manager_id`` on the node table is the FORMAL org-chart reporting line
    (blank for department heads), separate from who actually messages whom.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    # igraph dislikes pandas <NA> in vertex attributes; blank out missing managers.
    nodes = nodes.copy()
    nodes["manager_id"] = nodes["manager_id"].fillna("").astype(str)
    g = ig.Graph.DataFrame(edges, directed=True, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["message_count"]
    return g


if __name__ == "__main__":
    print("\n\U0001F4AC reorg-comms (Python)")
    print("   Employee-to-employee message volume; weighted by message_count,")
    print("   across before / during / after a reorganization + layoff.\n")

    nodes = load_nodes()
    edges = load_edges()
    g = load_reorg(nodes, edges)

    print(f"✅ Loaded {len(nodes)} employees ({int((nodes.laid_off==1).sum())} laid off) "
          f"and {len(edges)} edges across {edges['period'].nunique()} periods.")
    print(f"\U0001F517 Directed: {g.is_directed()} | total messages: "
          f"{edges['message_count'].sum():,}")
    per = edges.groupby('period')['message_count'].sum()
    print("\U0001F4E8 Messages by period: " +
          " | ".join(f"{k}={v:,}" for k, v in per.items()))
    print("\U0001F389 Graph ready. Object `g` is a directed, weighted igraph.")
```

---

## `data/projects/satellite-constellation/README.md`

# satellite-constellation

*A single-instant snapshot of three operators' low-Earth-orbit (LEO) satellite
broadband networks: satellites linked to each other and down to ground gateways,
each link rated by capacity and latency.*

![Preview of the satellite-constellation network](thumb.png)

## At a glance

| | |
|---|---|
| **Direction** | Undirected (a radio/laser link carries traffic either way) |
| **Weights** | Weighted (`capacity_gbps` per link; `latency_ms` attribute) |
| **Modality** | Multimodal — 2 node kinds (`satellite`, `ground_station`) across 3 operators |
| **Temporal** | No — one frozen snapshot of all orbits at instant *t0* |
| **Nodes** | 298 (274 satellites + 24 ground stations) |
| **Edges** | 733 (210 intra-plane ISL + 199 inter-plane ISL + 2 cross-seam + 322 feeder) |
| **Files** | `nodes.csv`, `edges.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

Three fictional broadband operators — **Helios**, **Polaris**, and **Nimbus** —
each fly their own constellation of LEO **satellites**, arranged in orbital
*planes* with several satellites (*slots*) per plane. Some satellites talk
directly to their neighbors in space over **inter-satellite links** (ISLs);
traffic ultimately reaches the internet through **ground stations** (gateways) on
the surface via **feeder** links. A handful of gateways are neutral and shared by
all three operators; the rest belong to one operator. Each link carries a
throughput `capacity_gbps` (the edge weight) and a one-way `latency_ms`.
Satellites carry their orbital geometry (plane, slot, altitude, inclination,
RAAN, sub-satellite lat/lon), radio band, ISL capability, launch year, and
operational status; ground stations carry their region and capacity. This is a
frozen snapshot — every satellite is "parked" at the position its orbit puts it
in at instant *t0*.

This is a criticality, resilience, and equity network. It rewards students who
ask how the *architecture* of each operator changes what happens under stress.
Some questions to chew on:

- The three operators are built differently. If every ground station went dark at
  once, which operators keep talking to themselves in orbit, and which simply fall
  apart — and *why* does the answer differ by operator?
- A few links sit on a structural fault line in the orbital mesh. Can you find the
  links that carry far more routed traffic than their capacity or count suggests?
- Latency to a gateway is not the same everywhere. Is it explained by *where* a
  satellite is, even after you account for how many satellites are around?
- Which ground stations are single points of failure for their operator, and would
  degree, strength, and betweenness point you at the same ones?
- Run community detection. What do the communities correspond to, and which nodes
  end up acting as the bridges between them?
- Not every satellite is in the same shape. Is there a pattern to which ones are
  degraded, and does it line up with anything about the fleet's history?

> **Note.** The interesting findings here are deliberately *not* documented.
> "Bigger constellations have more links" is the starting point, not a finding.
> Push past it.

## `nodes.csv`

One row per node. Satellite rows leave `region` blank; ground-station rows leave
the orbital columns (`plane`, `slot`, `altitude_km`, `inclination_deg`,
`raan_deg`, `band`, `isl_capable`, `launch_year`, `status`) blank.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique key. `SAT####` satellite, `GS###` ground station. Referenced by edges. | character | `SAT0001`, `GS004` |
| `kind` | Node kind | Whether the node is in orbit or on the ground. | character | `satellite`, `ground_station` |
| `operator` | Operator | Owning operator; `neutral` for shared gateways. | character | `Helios`, `Polaris`, `Nimbus`, `neutral` |
| `plane` | Orbital plane | Index of the orbital plane the satellite is in (blank for ground stations). | integer | `0`, `5`, `11` |
| `slot` | Slot in plane | Position of the satellite within its plane (blank for ground stations). | integer | `0`, `6`, `10` |
| `altitude_km` | Altitude | Orbital altitude above the surface, kilometers (blank for ground stations). | double | `546.9`, `780.2`, `1200.4` |
| `inclination_deg` | Inclination | Orbital-plane inclination to the equator, degrees (blank for ground stations). | double | `53.02`, `86.41`, `88.0` |
| `raan_deg` | RAAN | Right ascension of the ascending node — the plane's orientation, degrees (blank for ground stations). | double | `0.0`, `90.0`, `157.5` |
| `region` | Region | Surface region of a ground station (blank for satellites). | character | `North America`, `Europe`, `East Asia` |
| `lat` | Latitude | Sub-satellite latitude (satellite) or site latitude (ground station), degrees. | double | `43.79`, `-29.97`, `50.12` |
| `lon` | Longitude | Sub-satellite longitude (satellite) or site longitude (ground station), degrees. | double | `19.19`, `-94.3`, `125.6` |
| `x` | X coordinate | Map X (= longitude), for plotting. | double | `19.19`, `-94.3` |
| `y` | Y coordinate | Map Y (= latitude), for plotting. | double | `43.79`, `50.12` |
| `band` | Radio/optical band | Primary link band of the satellite (blank for ground stations). | character | `optical`, `Ka`, `Ku` |
| `isl_capable` | ISL capable | 1 if the satellite has inter-satellite links, else 0 (blank for ground stations). | integer | `0`, `1` |
| `launch_year` | Launch year | Year the satellite was launched (blank for ground stations). | integer | `2019`, `2022`, `2025` |
| `status` | Status | Operational state of the satellite (blank for ground stations). | character | `active`, `degraded`, `spare` |
| `capacity_gbps` | Capacity (Gbps) | Per-node throughput capacity (satellite payload, or gateway backhaul). | double | `5.74`, `14.89`, `42.10` |
| `label` | Display name | Human-readable label. (`name` is avoided — python-igraph reserves it for the ID.) | character | `Helios 00-00`, `Europe GW 08` |

## `edges.csv`

One row per link. Undirected (`from_id`/`to_id` ordering is arbitrary).

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | Endpoint node ID | One end of the link. | character | `SAT0001`, `SAT0150` |
| `to_id` | Endpoint node ID | Other end of the link. | character | `SAT0002`, `GS004` |
| `link_type` | Link type | Kind of link: `intra_isl` (fore/aft neighbor in the same plane), `inter_isl` (to an adjacent plane), `crossseam` (spanning the orbital seam), `feeder` (satellite ↔ ground station). | character | `intra_isl`, `inter_isl`, `crossseam`, `feeder` |
| `capacity_gbps` | Link capacity (Gbps) | Throughput capacity of the link (the edge weight). | double | `8.04`, `15.36`, `28.10` |
| `latency_ms` | Latency | One-way link latency, milliseconds. | double | `17.0`, `33.7`, `41.2` |
| `band` | Band | Radio/optical band the link uses. | character | `optical`, `Ka`, `Ku` |

## Load it

```bash
Rscript data/projects/satellite-constellation/load.R     # R    (igraph)
python  data/projects/satellite-constellation/load.py     # Python (python-igraph)
```

Both build an undirected, weighted `igraph` graph and print a one-screen summary.
In the [R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**satellite-constellation** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/satellite-constellation>

---

## `data/projects/satellite-constellation/_generate.py`

```python
"""Generate the `satellite-constellation` project network (deterministic).

A single-instant snapshot of a multi-operator low-Earth-orbit (LEO) satellite
communications network. Three fictional operators fly distinct constellation
architectures, plus a set of ground stations (gateways) on the surface:

  - satellites    (kind = "satellite")  ~274 across three operators
  - ground_station(kind = "ground_station")  ~24 gateways

Operators (each a real-world architecture in disguise):
  - "Helios"  : Walker-Delta, i~53 deg, ~550 km, dense LASER inter-satellite
                links (a connected mesh); needs few gateways.   12 x 12 = 144
  - "Polaris" : Walker-Star near-polar i~88 deg, ~1200 km, BENT-PIPE: NO
                inter-satellite links at all -- every satellite depends on
                reaching a ground gateway.                       8 x  8 =  64
  - "Nimbus"  : Walker-Star polar i~86.4 deg, ~780 km, Ka-band crosslinks
                including a few cross-seam links.                 6 x 11 =  66

Edges (undirected), `link_type`:
  - intra_isl  : sat <-> fore/aft neighbor in the SAME plane (a ring)
  - inter_isl  : sat <-> nearest sat in an adjacent plane
  - crossseam  : the rare ISL spanning the Walker-Star ascending/descending seam
  - feeder     : sat <-> ground_station (the only way bent-pipe sats reach the net)
weighted by `capacity_gbps`, with `latency_ms` and `band`.

Design parameters (the only record of the planted structure):
  - BENTPIPE_OPERATOR = "Polaris": has zero ISLs, so removing all ground
    stations shatters it into isolated satellites while Helios's ISL mesh
    barely changes its largest component (architecture-divide resilience).
  - SEAM_LINK_FRACTION: in Walker-Star operators only a few planes bridge the
    ascending/descending seam; those crossseam links carry outsized betweenness.
  - GATEWAY_REGIONS: gateways cluster in NA/EU/E-Asia; sats over oceans / the
    global south / poles must hop far to a gateway -> FEEDER_LAT_PENALTY raises
    feeder latency with |lat| and ocean-ness, independent of satellite count.
  - GATEWAY_HUB_FRACTION: a few gateways absorb most feeders -> high strength /
    betweenness, single points of failure.
  - Operator + plane structure is recoverable by community detection; the few
    NEUTRAL shared gateways are the bridges between operator clusters.
  - AGING: early launch_year -> higher P(degraded) and lower capacity, and the
    earliest-launched satellites sit in the lowest-numbered planes.

Run:
    python data/projects/satellite-constellation/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

EARTH_R_KM = 6371.0

# --- constellation geometry -------------------------------------------------
# operator -> (n_planes, sats_per_plane, inclination_deg, altitude_km, has_isl)
OPERATORS = {
    "Helios":  dict(planes=12, per_plane=12, inc=53.0,  alt=550.0,  isl=True,
                    walker="delta", band="optical"),
    "Polaris": dict(planes=8,  per_plane=8,  inc=88.0,  alt=1200.0, isl=False,
                    walker="star",  band="Ku"),
    "Nimbus":  dict(planes=6,  per_plane=11, inc=86.4,  alt=780.0,  isl=True,
                    walker="star",  band="Ka"),
}

# --- planted parameters -----------------------------------------------------
BENTPIPE_OPERATOR = "Polaris"   # the operator with NO inter-satellite links
SEAM_LINK_FRACTION = 0.18       # frac of seam-adjacent planes that bridge seam
GATEWAY_HUB_FRACTION = 0.25     # frac of gateways that soak up most feeders
FEEDER_LAT_PENALTY = 26.0       # extra feeder latency (ms) at the poles/oceans
AGING_DEGRADE = 0.55            # max P(degraded) for the oldest satellites
N_NEUTRAL_GATEWAYS = 4          # shared gateways that bridge operator clusters

# gateway clusters: (name, lat, lon, n, radius_deg). Dense in NA/EU/E-Asia.
GATEWAY_REGIONS = [
    ("North America", 40.0,  -95.0, 6, 9.0),
    ("Europe",        50.0,   10.0, 6, 7.0),
    ("East Asia",     35.0,  125.0, 5, 8.0),
    ("South America", -20.0, -55.0, 2, 9.0),
    ("Oceania",       -30.0, 145.0, 2, 8.0),
    ("Africa",         5.0,   25.0, 1, 9.0),
    ("Mid-Ocean",     10.0,  -40.0, 2, 6.0),   # sparse, near nothing
]

# launch-year window
YEAR_MIN, YEAR_MAX = 2019, 2025


def subsatellite_latlon(inc_deg, raan_deg, anomaly_deg):
    """Sub-satellite latitude/longitude for a circular orbit at one instant.

    Standard spherical relations: given inclination i, RAAN, and argument of
    latitude u (here the true anomaly from the ascending node), the geocentric
    latitude and longitude of the sub-satellite point are
        lat = asin(sin i * sin u)
        lon = raan + atan2(cos i * sin u, cos u)
    (Earth rotation / GMST is folded into RAAN for this snapshot.)
    """
    i = np.radians(inc_deg)
    u = np.radians(anomaly_deg)
    raan = np.radians(raan_deg)
    lat = np.arcsin(np.sin(i) * np.sin(u))
    lon = raan + np.arctan2(np.cos(i) * np.sin(u), np.cos(u))
    lat_d = np.degrees(lat)
    lon_d = (np.degrees(lon) + 180.0) % 360.0 - 180.0
    return lat_d, lon_d


def haversine_km(lat1, lon1, lat2, lon2):
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dl = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * EARTH_R_KM * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def ocean_ness(lat, lon):
    """Crude 0..1 'how oceanic / underserved' score for a sub-satellite point.

    High over open ocean and the polar/southern reaches, low over the
    well-served NA/EU/E-Asia land masses. Not physical -- just a coverage proxy.
    """
    land_centers = [(40, -95), (50, 10), (35, 125), (-10, -55), (0, 20)]
    best = min(haversine_km(lat, lon, la, lo) for la, lo in land_centers)
    land_score = np.clip(best / 5000.0, 0, 1)         # far from land -> oceanic
    polar = np.clip((abs(lat) - 35) / 55.0, 0, 1)     # high |lat| underserved
    return float(np.clip(0.55 * land_score + 0.45 * polar, 0, 1))


def main() -> None:
    rng = np.random.default_rng(SEED)

    # ===== 1. satellites ===================================================
    sat_rows = []
    # per-operator record of (node_id, plane, slot, lat, lon) for edge building
    sat_index: dict[str, list[dict]] = {op: [] for op in OPERATORS}

    sid = 1
    for op in sorted(OPERATORS):                      # deterministic op order
        cfg = OPERATORS[op]
        nP, nS = cfg["planes"], cfg["per_plane"]
        # Walker-Star spreads RAAN over 180 deg; Walker-Delta over 360 deg.
        raan_span = 180.0 if cfg["walker"] == "star" else 360.0
        for p in range(nP):
            raan = (raan_span * p / nP) % 360.0
            # phasing offset between planes (Walker phase factor), small jitter
            phase = (360.0 / (nP * nS)) * p
            for s in range(nS):
                anomaly = (360.0 * s / nS + phase) % 360.0
                inc = cfg["inc"] + float(rng.normal(0, 0.05))
                alt = cfg["alt"] + float(rng.normal(0, 3.0))
                lat, lon = subsatellite_latlon(inc, raan, anomaly)

                # AGING: earliest planes launched first; year rises with plane.
                yr_frac = p / max(nP - 1, 1)
                launch_year = int(round(YEAR_MIN + yr_frac * (YEAR_MAX - YEAR_MIN)
                                        + rng.normal(0, 0.4)))
                launch_year = int(np.clip(launch_year, YEAR_MIN, YEAR_MAX))
                age_frac = (YEAR_MAX - launch_year) / (YEAR_MAX - YEAR_MIN)
                p_deg = AGING_DEGRADE * age_frac
                roll = rng.random()
                if roll < 0.04:
                    status = "spare"
                elif roll < 0.04 + p_deg:
                    status = "degraded"
                else:
                    status = "active"

                # capacity: optical/Ka fast; bent-pipe Ku slower; degraded lower
                base_cap = {"optical": 20.0, "Ka": 12.0, "Ku": 8.0}[cfg["band"]]
                cap = base_cap * (1.0 - 0.45 * age_frac) * (1 + rng.normal(0, 0.06))
                if status == "degraded":
                    cap *= 0.55
                cap = float(np.clip(cap, 1.0, 30.0))

                node_id = f"SAT{sid:04d}"
                rec = dict(
                    node_id=node_id, kind="satellite", operator=op,
                    plane=p, slot=s,
                    altitude_km=round(alt, 1), inclination_deg=round(inc, 2),
                    raan_deg=round(raan, 2),
                    lat=round(lat, 4), lon=round(lon, 4),
                    x=round(lon, 4), y=round(lat, 4),
                    band=cfg["band"], isl_capable=int(cfg["isl"]),
                    launch_year=launch_year, status=status,
                    capacity_gbps=round(cap, 2),
                    label=f"{op} {p:02d}-{s:02d}",
                )
                sat_rows.append(rec)
                sat_index[op].append(rec)
                sid += 1

    # ===== 2. ground stations =============================================
    gs_rows = []
    gs_all = []
    gid = 1
    # build a flat, ordered list of gateway positions first
    gw_positions = []
    for region, clat, clon, n, radius in GATEWAY_REGIONS:
        for _ in range(n):
            la = float(np.clip(clat + rng.normal(0, radius), -85, 85))
            lo = (clon + rng.normal(0, radius) + 180) % 360 - 180
            gw_positions.append((region, la, lo))

    n_gw = len(gw_positions)
    # decide which gateways are NEUTRAL (shared) vs operator-specific.
    # neutral ones are chosen by index (sorted) for determinism.
    neutral_idx = set(sorted(range(n_gw))[:N_NEUTRAL_GATEWAYS])
    ops_cycle = sorted(OPERATORS)
    for k, (region, la, lo) in enumerate(gw_positions):
        if k in neutral_idx:
            operator = "neutral"
        else:
            operator = ops_cycle[k % len(ops_cycle)]
        capacity = float(np.clip(40 + rng.normal(0, 12), 8, 90))
        rec = dict(
            node_id=f"GS{gid:03d}", kind="ground_station", operator=operator,
            region=region, lat=round(la, 4), lon=round(lo, 4),
            x=round(lo, 4), y=round(la, 4),
            capacity_gbps=round(capacity, 2),
            label=f"{region} GW {gid:02d}",
        )
        gs_rows.append(rec)
        gs_all.append(rec)
        gid += 1

    # ===== 3. edges ========================================================
    edges = []
    seen = set()

    def add_edge(a, b, link_type, cap, lat_ms, band):
        if a == b:
            return
        key = (a, b) if a < b else (b, a)
        if key in seen:
            return
        seen.add(key)
        edges.append(dict(
            from_id=key[0], to_id=key[1], link_type=link_type,
            capacity_gbps=round(float(cap), 2), latency_ms=round(float(lat_ms), 2),
            band=band,
        ))

    # ---- inter/intra ISL for operators that have ISL ----------------------
    for op in sorted(OPERATORS):
        cfg = OPERATORS[op]
        if not cfg["isl"]:
            continue
        nP, nS = cfg["planes"], cfg["per_plane"]
        recs = sat_index[op]
        # index by (plane, slot)
        by_ps = {(r["plane"], r["slot"]): r for r in recs}

        # intra-plane ring: fore/aft neighbors in the same plane
        for p in range(nP):
            for s in range(nS):
                a = by_ps[(p, s)]
                b = by_ps[(p, (s + 1) % nS)]
                d = haversine_km(a["lat"], a["lon"], b["lat"], b["lon"])
                lat_ms = d / 200.0 + rng.uniform(0.1, 0.6)   # light-speed-ish
                cap = min(a["capacity_gbps"], b["capacity_gbps"]) * 1.4
                add_edge(a["node_id"], b["node_id"], "intra_isl",
                         cap, lat_ms, cfg["band"])

        # inter-plane: each sat links to nearest sat in the next plane.
        # Walker-Star has a SEAM between plane (nP-1) and plane 0 (ascending vs
        # descending side); only a few planes bridge it (crossseam links).
        seam_pairs = {(nP - 1, 0)}
        for p in range(nP):
            q = (p + 1) % nP
            is_seam = (p, q) in seam_pairs or (q, p) in seam_pairs
            if cfg["walker"] == "star" and is_seam:
                # only a small fraction of slots bridge the seam
                n_bridge = max(1, int(round(nS * SEAM_LINK_FRACTION)))
                bridge_slots = sorted(range(nS))[:n_bridge]
            else:
                bridge_slots = list(range(nS))
            for s in bridge_slots:
                a = by_ps[(p, s)]
                # nearest slot in plane q
                cands = [by_ps[(q, s2)] for s2 in range(nS)]
                dists = [haversine_km(a["lat"], a["lon"], c["lat"], c["lon"])
                         for c in cands]
                b = cands[int(np.argmin(dists))]
                d = min(dists)
                if d > 4000:           # too far to close a link
                    continue
                lat_ms = d / 200.0 + rng.uniform(0.2, 0.8)
                if cfg["walker"] == "star" and is_seam:
                    lt = "crossseam"
                    # seam crossings are bandwidth-starved (sats cross at high
                    # relative velocity): low capacity -> a weighted bottleneck.
                    cap = min(a["capacity_gbps"], b["capacity_gbps"]) * 0.35
                else:
                    lt = "inter_isl"
                    cap = min(a["capacity_gbps"], b["capacity_gbps"]) * 1.1
                add_edge(a["node_id"], b["node_id"], lt, cap, lat_ms, cfg["band"])

    # ---- feeder links: satellites <-> ground stations ---------------------
    # A satellite can reach a gateway it is "over" (within an elevation mask).
    # Hub gateways soak up most feeders. Bent-pipe sats depend ENTIRELY on these.
    # Visibility footprint half-angle grows with altitude (rough proxy).
    gw_by_op: dict[str, list[dict]] = {op: [] for op in OPERATORS}
    neutral_gws = [g for g in gs_all if g["operator"] == "neutral"]
    for g in gs_all:
        if g["operator"] in gw_by_op:
            gw_by_op[g["operator"]].append(g)

    # choose hub gateways (deterministic: first fraction by node_id order)
    sorted_gw_ids = sorted(g["node_id"] for g in gs_all)
    n_hub = max(1, int(round(len(sorted_gw_ids) * GATEWAY_HUB_FRACTION)))
    hub_ids = set(sorted_gw_ids[:n_hub])

    for op in sorted(OPERATORS):
        cfg = OPERATORS[op]
        # gateways this operator can use: its own + neutral
        usable = sorted(gw_by_op[op] + neutral_gws, key=lambda g: g["node_id"])
        # footprint radius (km) on the ground; higher altitude sees farther
        footprint = 2500.0 + cfg["alt"] * 1.4
        for sat in sat_index[op]:
            # distances to all usable gateways
            ds = [(haversine_km(sat["lat"], sat["lon"], g["lat"], g["lon"]), g)
                  for g in usable]
            ds.sort(key=lambda t: (t[0], t[1]["node_id"]))
            # link to gateways within footprint; bias toward hub gateways
            linked = 0
            target = 2 if cfg["isl"] else 3   # bent-pipe craves more feeders
            for d, g in ds:
                if d > footprint and linked >= 1:
                    break
                if d > footprint * 1.6:
                    break
                # hubs win: non-hub gateways links are probabilistically dropped
                if g["node_id"] not in hub_ids and rng.random() < 0.5 and linked >= 1:
                    continue
                # feeder latency: distance + penalty for oceanic/polar coverage
                oc = ocean_ness(sat["lat"], sat["lon"])
                lat_ms = (d / 200.0) + FEEDER_LAT_PENALTY * oc + rng.uniform(0.2, 1.0)
                cap = min(sat["capacity_gbps"], g["capacity_gbps"]) * 0.8
                add_edge(sat["node_id"], g["node_id"], "feeder",
                         cap, lat_ms, sat["band"])
                linked += 1
                if linked >= target:
                    break
            # guarantee bent-pipe sats are not totally isolated: if none in
            # range, attach to the single nearest usable gateway (long hop).
            if linked == 0 and ds:
                d, g = ds[0]
                oc = ocean_ness(sat["lat"], sat["lon"])
                lat_ms = (d / 200.0) + FEEDER_LAT_PENALTY * oc + rng.uniform(0.2, 1.0)
                cap = min(sat["capacity_gbps"], g["capacity_gbps"]) * 0.8
                add_edge(sat["node_id"], g["node_id"], "feeder",
                         cap, lat_ms, sat["band"])

    # ===== 4. assemble & write ============================================
    sat_df = pd.DataFrame(sat_rows)
    gs_df = pd.DataFrame(gs_rows)

    # unified column order; satellite-only cols blank for ground stations
    cols = ["node_id", "kind", "operator", "plane", "slot", "altitude_km",
            "inclination_deg", "raan_deg", "region", "lat", "lon", "x", "y",
            "band", "isl_capable", "launch_year", "status", "capacity_gbps",
            "label"]
    for c in cols:
        if c not in sat_df.columns:
            sat_df[c] = pd.NA
        if c not in gs_df.columns:
            gs_df[c] = pd.NA
    nodes = pd.concat([sat_df[cols], gs_df[cols]], ignore_index=True)

    edges_df = pd.DataFrame(edges, columns=[
        "from_id", "to_id", "link_type", "capacity_gbps", "latency_ms", "band"])

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges_df.to_csv(HERE / "edges.csv", index=False)

    nsat = (nodes.kind == "satellite").sum()
    ngs = (nodes.kind == "ground_station").sum()
    lc = edges_df.link_type.value_counts()
    print(f"satellite-constellation: {len(nodes)} nodes "
          f"({nsat} satellites + {ngs} ground_stations), {len(edges_df)} edges "
          f"(intra_isl={lc.get('intra_isl',0)}, inter_isl={lc.get('inter_isl',0)}, "
          f"crossseam={lc.get('crossseam',0)}, feeder={lc.get('feeder',0)}).")


if __name__ == "__main__":
    main()
```

---

## `data/projects/satellite-constellation/load.R`

```r
#' @name load.R
#' @title Load the `satellite-constellation` project network (R)
#' @description
#'
#' Reads the two CSVs in this folder and builds an undirected, weighted igraph
#' object: a one-instant snapshot of three operators' LEO satellite broadband
#' networks (satellites + ground stations, joined by ISL and feeder links). Run
#' it straight (`Rscript load.R`) for a quick summary, or `source()` it and call
#' `load_constellation()` to get the graph in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "satellite-constellation")

#' Load the node table (one row per satellite / ground station).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per link).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Build the undirected, weighted constellation graph.
#'
#' Edges are weighted by link `capacity_gbps`. The graph is a single frozen
#' snapshot of all orbits at one instant (no time dimension).
load_constellation <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = FALSE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$capacity_gbps
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n\U0001F6F0\UFE0F  satellite-constellation (R)\n")
  cat("   Undirected LEO network; links weighted by capacity (Gbps).\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_constellation(nodes, edges)

  cat(sprintf("✅ Loaded %d nodes (%d satellites, %d ground stations) and %d links.\n",
              nrow(nodes), sum(nodes$kind == "satellite"),
              sum(nodes$kind == "ground_station"), nrow(edges)))
  cat(sprintf("\U0001F517 Directed: %s | total link capacity: %s Gbps\n",
              is_directed(g),
              format(round(sum(edges$capacity_gbps)), big.mark = ",")))
  cat("\U0001F389 Graph ready. Object `g` is an undirected, weighted igraph.\n")
}
```

---

## `data/projects/satellite-constellation/load.py`

```python
"""Load the `satellite-constellation` project network (Python).

Reads the two CSVs in this folder and builds an undirected, weighted
python-igraph object: a one-instant snapshot of three operators' LEO satellite
broadband networks (satellites + ground stations, joined by ISL and feeder
links). Run it straight (``python load.py``) for a quick summary, or import
``load_constellation()`` into your own script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per satellite / ground station."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per link."""
    return pd.read_csv(HERE / "edges.csv")


def load_constellation(nodes: pd.DataFrame | None = None,
                       edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the undirected, weighted constellation graph.

    Edges are weighted by link ``capacity_gbps``. The graph is a single frozen
    snapshot of all orbits at one instant (no time dimension).
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=False, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["capacity_gbps"]
    return g


if __name__ == "__main__":
    print("\n🛰️  satellite-constellation (Python)")
    print("   Undirected LEO network; links weighted by capacity (Gbps).\n")

    nodes = load_nodes()
    edges = load_edges()
    g = load_constellation(nodes, edges)

    kinds = nodes["kind"].value_counts()
    print(f"✅ Loaded {len(nodes)} nodes "
          f"({kinds.get('satellite',0)} satellites, "
          f"{kinds.get('ground_station',0)} ground stations) and {len(edges)} links.")
    print(f"🔗 Directed: {g.is_directed()} | total link capacity: "
          f"{round(edges['capacity_gbps'].sum()):,} Gbps")
    print("🎉 Graph ready. Object `g` is an undirected, weighted igraph.")
```

---

## `data/projects/satellite-supply-chain/README.md`

# satellite-supply-chain

*A multi-tier satellite manufacturing supply chain — space-grade materials flow up
through components and subsystems into integrators and finished space programs.*

![Preview of the satellite-supply-chain network](thumb.png)

## At a glance

| | |
|---|---|
| **Direction** | Directed (supply flow: upstream tier → downstream tier) |
| **Weights** | Weighted (`units_per_year`; paired `value_musd` and `lead_time_days`) |
| **Modality** | Multimodal — 5 node kinds across 5 tiers (`material`, `component`, `subsystem`, `integrator`, `program`) |
| **Temporal** | No — a single annual snapshot |
| **Nodes** | 276 (60 material + 72 component + 54 subsystem + 42 integrator + 48 program) |
| **Edges** | 562 supply relationships |
| **Files** | `nodes.csv`, `edges.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

A stylized model of the global spacecraft (satellite) supply chain. Supply flows
from the most upstream tier to the most downstream:

- **tier 4 `material`** — space-grade raw materials: radiation-hardened wafers,
  solar cells, propellant, composite prepreg, battery cells, optics blanks;
- **tier 3 `component`** — units / "black boxes": star trackers, reaction wheels,
  rad-hard on-board computers, TWT amplifiers, harnesses, structure panels;
- **tier 2 `subsystem`** — spacecraft subsystems: ADCS (attitude), comms payload,
  command & data handling, structure, thermal, power;
- **tier 1 `integrator`** — satellite-bus integrators / prime contractors;
- **tier 0 `program`** — end programs / operators (broadband constellations,
  government comsats, navigation, earth observation, deep-space probes).

Each directed edge is a supply relationship weighted by `units_per_year`, with a
dollar `value_musd` and a `lead_time_days`. Nodes carry a `region`, a `tier`, a
`capacity`, a nominal `lead_time_days`, and a `subtype`.

This is a flow-and-criticality network. It rewards students who look past which
nodes have the most connections. Some questions to chew on:

- If you could harden one node against disruption, which would it be — and would
  degree, betweenness, or a knockout/criticality analysis give you the same
  answer? Are the busiest suppliers the most important ones?
- Is the chain's resilience the same everywhere, or are some end programs one bad
  day away from having no viable supply path at all?
- Does geography matter? If a region were embargoed or hit by an export ban, how
  much downstream output would be cut, and through which tier?
- Recovery is not free: when the system is shocked, which nodes are also the
  slowest to come back?

> **Note.** The interesting findings here are deliberately *not* documented. "Big
> suppliers ship more volume" is the starting point, not a finding. Push past it —
> raw degree will mislead you.

## `nodes.csv`

One row per node (supplier, subsystem, integrator, or program). Every node has
every column populated.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique key. `M###` material, `C###` component, `S###` subsystem, `I###` integrator, `P###` program. Referenced by edges. | character | `M001`, `C031`, `S019`, `I012`, `P033` |
| `kind` | Node kind | Tier role of the node. | character | `material`, `component`, `subsystem`, `integrator`, `program` |
| `tier` | Supply tier | Depth in the chain: 4 = most upstream (material) … 0 = end program. | integer | `4`, `3`, `0` |
| `region` | Region | Where the node operates. | character | `USA`, `Europe`, `Japan`, `India`, `China`, `Other` |
| `subtype` | Subtype | Kind-specific detail: material class, component type, subsystem type, integrator/program segment. | character | `radhard_wafer`, `star_tracker`, `adcs`, `broadband_constellation` |
| `capacity` | Capacity | Nominal annual throughput capacity (relative units). | integer | `1870`, `1320`, `33` |
| `lead_time_days` | Lead time | Nominal replenishment / production lead time in days. | integer | `181`, `113`, `47` |
| `label` | Display name | Human-readable label. (`name` is avoided — python-igraph reserves it for the ID.) | character | `Radhard Wafer Co 001`, `ADCS Subsystem 019` |

## `edges.csv`

One row per supply relationship. Directed from the upstream node (`from_id`) to
the downstream node (`to_id`).

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | Upstream node ID | Supplying node (higher tier). | character | `M001`, `C003`, `S027` |
| `to_id` | Downstream node ID | Receiving node (lower tier). | character | `C003`, `S019`, `P033` |
| `units_per_year` | Annual units | Units shipped on this relationship per year (the edge weight). | integer | `164`, `29`, `16` |
| `value_musd` | Annual value | Dollar value of the flow, millions USD. | double | `50.396`, `3.096`, `2.585` |
| `lead_time_days` | Edge lead time | Lead time for deliveries on this relationship, days. | integer | `181`, `120`, `95` |

## Load it

```bash
Rscript data/projects/satellite-supply-chain/load.R     # R    (igraph)
python  data/projects/satellite-supply-chain/load.py     # Python (python-igraph)
```

Both build a directed, weighted `igraph` graph and print a one-screen summary. In
the [R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**satellite-supply-chain** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/satellite-supply-chain>

---

## `data/projects/satellite-supply-chain/_generate.py`

```python
"""Generate the `satellite-supply-chain` project network (deterministic).

A multi-tier spacecraft (satellite) manufacturing supply chain spanning five
tiers of nodes:
  - tier 4  material    space-grade raw materials (rad-hard wafers, solar cells,
                        propellant, composite prepreg, battery cells, optics)
  - tier 3  component   units / black boxes (star trackers, reaction wheels,
                        rad-hard on-board computers, TWT amplifiers, harnesses)
  - tier 2  subsystem   spacecraft subsystems (ADCS, comms payload, command &
                        data handling, structure, thermal, power)
  - tier 1  integrator  satellite-bus integrators / prime contractors
  - tier 0  program     end space programs / operators (broadband constellations,
                        government comsats, navigation, earth observation, probes)

Edges are directed supply flows from upstream (higher tier) to downstream
(lower tier). One row per supply relationship. The edge weight is
`units_per_year` with a paired `value_musd` and `lead_time_days`.

Node attributes: kind, tier, region, subtype, capacity, lead_time_days, label.
Regions: USA, Europe, Japan, India, China, Other.

Design parameters (the only record of the planted structure):
  - HUB_COMPONENT: one USA radiation-hardened on-board computer feeds nearly all
    flight-critical subsystems. High BETWEENNESS but only modest in/out-degree
    (a few fat edges, not many). Removing it severs most advanced program output.
  - CHOKE_MATERIAL: one rad-hard wafer supplier (tier 4) feeds nearly every
    flight-critical component (a second hidden critical node, betweenness >>
    degree-rank).
  - ADV_REGION: flight-critical subsystems are concentrated in ONE region (USA,
    an ITAR-style concentration); a regional shock severs many downstream paths.
  - LEADTIME_ON_PATH: the longest lead times cluster ON the critical path (hub
    computer, choke wafer, US flight-critical subsystems) so the bottleneck is
    also the slowest to recover.
  - COMMODITY decoys: composite prepreg & solar cells feed almost every standard
    component (highest DEGREE upstream nodes) but are fully substitutable, so they
    out-rank the real choke on degree and hide it.

Run:
    python data/projects/satellite-supply-chain/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

REGIONS = ["USA", "Europe", "Japan", "India", "China", "Other"]

# tier population sizes (total ~ 276 nodes)
N_MATERIAL = 60      # tier 4
N_COMPONENT = 72     # tier 3
N_SUBSYSTEM = 54     # tier 2
N_INTEGRATOR = 42    # tier 1
N_PROGRAM = 48       # tier 0

# --- planted parameters -----------------------------------------------------
HUB_SHARE = 0.80          # share of flight-critical subsystem feed via the hub
CHOKE_SHARE = 0.86        # share of flight-critical components the choke feeds
ADV_REGION = "USA"        # where flight-critical subsystems concentrate
ADV_CONC = 0.80           # share of advanced integrator feed from that region
LEADTIME_PATH_BONUS = 80  # extra lead-time days loaded onto the critical path
NOISE_REGION_FLIP = 0.10  # fraction of nodes whose region is "wrong" (noise)

COMP_ADV = ["star_tracker", "reaction_wheel", "radhard_obc", "twt_amplifier", "imu"]
COMP_STD = ["harness", "thermal_blanket", "structure_panel", "solar_array", "deployable_boom"]
SUBSYS_ADV = ["adcs", "comms_payload", "command_data_handling"]
SUBSYS_STD = ["structure", "thermal_control", "power_eps"]


def main() -> None:
    rng = np.random.default_rng(SEED)

    # region sampling weights: space hardware is USA/Europe heavy
    rweights = np.array([0.34, 0.22, 0.12, 0.10, 0.14, 0.08])
    rweights = rweights / rweights.sum()

    def pick_regions(n):
        return rng.choice(REGIONS, size=n, p=rweights)

    rows = []  # node rows

    # ----- tier 4: materials ----------------------------------------------
    mat_kinds = ["radhard_wafer", "solar_cell", "propellant", "composite_prepreg",
                 "battery_cell", "optics_blank", "tungsten_target", "space_capacitor"]
    mat_region = pick_regions(N_MATERIAL)
    for i in range(N_MATERIAL):
        sub = mat_kinds[i % len(mat_kinds)]
        rows.append({
            "node_id": f"M{i+1:03d}", "kind": "material", "tier": 4,
            "region": mat_region[i], "subtype": sub,
            "capacity": int(rng.integers(200, 4000)),
            "lead_time_days": int(np.clip(rng.normal(80, 22), 21, 180)),
            "label": f"{sub.replace('_',' ').title()} Co {i+1:03d}",
        })

    # ----- tier 3: components ---------------------------------------------
    c_region = pick_regions(N_COMPONENT)
    c_adv = rng.random(N_COMPONENT) < 0.42   # flight-critical electronics
    for i in range(N_COMPONENT):
        sub = COMP_ADV[i % len(COMP_ADV)] if c_adv[i] else COMP_STD[i % len(COMP_STD)]
        rows.append({
            "node_id": f"C{i+1:03d}", "kind": "component", "tier": 3,
            "region": c_region[i], "subtype": sub,
            "capacity": int(rng.integers(20, 220) * (2 if c_adv[i] else 1)),
            "lead_time_days": int(np.clip(rng.normal(120, 26), 45, 240)),
            "label": f"{sub.replace('_',' ').title()} Unit {i+1:03d}",
        })

    # ----- tier 2: subsystems ---------------------------------------------
    s_region = pick_regions(N_SUBSYSTEM)
    s_adv = rng.random(N_SUBSYSTEM) < 0.45   # electronics-heavy subsystems
    # advanced subsystems concentrate in ADV_REGION (~70% relocated there).
    for i in range(N_SUBSYSTEM):
        if s_adv[i] and rng.random() < 0.70:
            s_region[i] = ADV_REGION
    for i in range(N_SUBSYSTEM):
        sub = SUBSYS_ADV[i % len(SUBSYS_ADV)] if s_adv[i] else SUBSYS_STD[i % len(SUBSYS_STD)]
        rows.append({
            "node_id": f"S{i+1:03d}", "kind": "subsystem", "tier": 2,
            "region": s_region[i], "subtype": sub,
            "capacity": int(rng.integers(30, 300)),
            "lead_time_days": int(np.clip(rng.normal(60, 16), 20, 130)),
            "label": f"{sub.replace('_',' ').upper()} Subsystem {i+1:03d}",
        })

    # ----- tier 1: integrators --------------------------------------------
    i_region = pick_regions(N_INTEGRATOR)
    i_segment = rng.choice(["geo_comsat", "leo_broadband", "science",
                            "navigation", "earth_obs"], size=N_INTEGRATOR)
    i_advanced = np.isin(i_segment, ["geo_comsat", "leo_broadband", "navigation"]) \
        & (rng.random(N_INTEGRATOR) < 0.85)
    for i in range(N_INTEGRATOR):
        rows.append({
            "node_id": f"I{i+1:03d}", "kind": "integrator", "tier": 1,
            "region": i_region[i], "subtype": i_segment[i],
            "capacity": int(rng.integers(20, 200)),
            "lead_time_days": int(np.clip(rng.normal(45, 14), 14, 110)),
            "label": f"Integrator {i+1:03d} ({i_segment[i]})",
        })

    # ----- tier 0: programs -----------------------------------------------
    pr_region = pick_regions(N_PROGRAM)
    pr_segment = rng.choice(["broadband_constellation", "gov_comsat", "earth_observation",
                             "navigation_sat", "deep_space_probe"], size=N_PROGRAM)
    for i in range(N_PROGRAM):
        rows.append({
            "node_id": f"P{i+1:03d}", "kind": "program", "tier": 0,
            "region": pr_region[i], "subtype": pr_segment[i],
            "capacity": int(rng.integers(20, 600)),
            "lead_time_days": int(np.clip(rng.normal(30, 10), 7, 70)),
            "label": f"Program {i+1:03d} ({pr_segment[i]})",
        })

    nodes = pd.DataFrame(rows)

    def ids(kind):
        return nodes.loc[nodes.kind == kind, "node_id"].tolist()
    mat_ids = ids("material")
    comp_ids = ids("component")
    sub_ids = ids("subsystem")
    int_ids = ids("integrator")
    prog_ids = ids("program")
    region_of = dict(zip(nodes.node_id, nodes.region))
    sub_of = dict(zip(nodes.node_id, nodes.subtype))

    adv_comp = [c for c, a in zip(comp_ids, c_adv) if a]
    std_comp = [c for c in comp_ids if c not in set(adv_comp)]
    adv_sub = [s for s, a in zip(sub_ids, s_adv) if a]
    std_sub = [s for s in sub_ids if s not in set(adv_sub)]
    adv_sub_region = [s for s in adv_sub if region_of[s] == ADV_REGION] or adv_sub[:1]

    # ---- planted critical nodes ------------------------------------------
    # HUB_COMPONENT: a USA rad-hard on-board computer.
    us_obc = [c for c in adv_comp
              if region_of[c] == "USA" and sub_of[c] == "radhard_obc"]
    HUB_COMPONENT = us_obc[0] if us_obc else adv_comp[0]
    # CHOKE_MATERIAL: a rad-hard wafer supplier.
    wafer_ids = nodes.loc[(nodes.kind == "material") &
                          (nodes.subtype == "radhard_wafer"), "node_id"].tolist()
    CHOKE_MATERIAL = wafer_ids[0]

    advanced_integrators = [i for i, a in zip(int_ids, i_advanced) if a]
    adv_int_set = set(advanced_integrators)
    std_integrators = [i for i in int_ids if i not in adv_int_set]

    prog_seg = dict(zip(prog_ids, pr_segment))
    adv_prog = [p for p in prog_ids if prog_seg[p] in
                ("broadband_constellation", "gov_comsat", "navigation_sat", "deep_space_probe")]
    std_prog = [p for p in prog_ids if p not in set(adv_prog)]

    eds = []  # edge rows

    def add_edge(frm, to, vol, ltd):
        eds.append({
            "from_id": frm, "to_id": to,
            "units_per_year": int(max(vol, 1)),
            "value_musd": round(float(max(vol, 1)) * rng.uniform(0.05, 0.40), 3),
            "lead_time_days": int(ltd),
        })

    def lt_of(n):
        return int(nodes.loc[nodes.node_id == n, "lead_time_days"].iloc[0])

    choke_lt = lt_of(CHOKE_MATERIAL)
    hub_lt = lt_of(HUB_COMPONENT)

    # DECOY commodity materials feeding nearly every standard component: highest
    # DEGREE upstream, but fully substitutable, so removing one cuts almost
    # nothing. They out-rank the real choke on degree and hide it.
    commodity_pool = [m for m in mat_ids
                      if sub_of[m] == "composite_prepreg" and m != CHOKE_MATERIAL]
    COMMODITY = commodity_pool[0]
    commodity2_pool = [m for m in mat_ids if sub_of[m] == "solar_cell"]
    COMMODITY2 = commodity2_pool[0]

    # ===== FLIGHT-CRITICAL CORRIDOR (the fragile spine) ===================
    # choke wafer -> flight-critical components (its ONLY upstream input here).
    add_edge(CHOKE_MATERIAL, HUB_COMPONENT, int(rng.integers(120, 240)), choke_lt)
    for c in adv_comp:
        if c != HUB_COMPONENT:
            add_edge(CHOKE_MATERIAL, c, int(rng.integers(40, 140)), choke_lt)

    # hub component -> ALL flight-critical subsystems: it is the sole upstream
    # feeder, hence a genuine cut vertex on every advanced path while touching
    # only a handful of nodes (modest degree). Volume biased to the US houses.
    for s in adv_sub:
        vol = int(rng.integers(160, 320)) if region_of.get(s) == ADV_REGION \
            else int(rng.integers(30, 100))
        add_edge(HUB_COMPONENT, s, vol, hub_lt)

    # other flight-critical components sell into the STANDARD integrator market
    # (a secondary outlet) -- they do NOT feed advanced subsystems, giving the
    # advanced corridor no alternative path.
    for c in adv_comp:
        if c != HUB_COMPONENT:
            for it in rng.choice(std_integrators, size=int(rng.integers(1, 3)), replace=False):
                add_edge(c, it, int(rng.integers(15, 80)), lt_of(c))

    # advanced subsystems -> advanced integrators (concentrated on US houses).
    us_sub = [s for s in adv_sub if region_of.get(s) == ADV_REGION] or adv_sub
    for it in advanced_integrators:
        if rng.random() < ADV_CONC:
            add_edge(rng.choice(us_sub), it, int(rng.integers(70, 260)), lt_of(us_sub[0]))
        else:
            s = rng.choice(adv_sub)
            add_edge(s, it, int(rng.integers(70, 260)), lt_of(s))
    # advanced integrators -> advanced programs
    for p in adv_prog:
        for it in rng.choice(advanced_integrators, size=int(rng.integers(1, 3)), replace=False):
            add_edge(it, p, int(rng.integers(40, 300)), lt_of(it))

    # ===== COMMODITY CORRIDOR (resilient, multi-sourced) ==================
    for c in std_comp:
        add_edge(COMMODITY, c, int(rng.integers(30, 140)), lt_of(COMMODITY))
        if rng.random() < 0.85:
            add_edge(COMMODITY2, c, int(rng.integers(25, 110)), lt_of(COMMODITY2))
        if rng.random() < 0.25:
            add_edge(CHOKE_MATERIAL, c, int(rng.integers(25, 110)), choke_lt)
        excl = (COMMODITY, COMMODITY2, CHOKE_MATERIAL)
        for m in rng.choice([x for x in mat_ids if x not in excl],
                            size=int(rng.integers(2, 5)), replace=False):
            add_edge(m, c, int(rng.integers(5, 70)), lt_of(m))
    # some materials also feed standard subsystems directly
    for s in std_sub:
        for m in rng.choice([x for x in mat_ids if x != CHOKE_MATERIAL],
                            size=int(rng.integers(1, 3)), replace=False):
            add_edge(m, s, int(rng.integers(5, 55)), lt_of(m))
    # standard components -> standard subsystems (multi-sourced)
    for s in std_sub:
        for c in rng.choice(std_comp, size=int(rng.integers(2, 4)), replace=False):
            add_edge(c, s, int(rng.integers(18, 110)), lt_of(c))
    # standard subsystems -> standard integrators
    for it in std_integrators:
        for s in rng.choice(std_sub, size=int(rng.integers(2, 4)), replace=False):
            add_edge(s, it, int(rng.integers(25, 110)), lt_of(s))
    # standard integrators -> standard programs
    for p in std_prog:
        for it in rng.choice(std_integrators, size=int(rng.integers(2, 4)), replace=False):
            add_edge(it, p, int(rng.integers(40, 260)), lt_of(it))

    edges = pd.DataFrame(eds)

    # ---- LEADTIME_ON_PATH: load extra lead time onto the critical path ----
    crit = {HUB_COMPONENT, CHOKE_MATERIAL} | set(adv_sub)
    nodes.loc[nodes.node_id.isin(crit), "lead_time_days"] = (
        nodes.loc[nodes.node_id.isin(crit), "lead_time_days"] + LEADTIME_PATH_BONUS
    ).clip(upper=320)
    edges.loc[edges.from_id.isin(crit), "lead_time_days"] = (
        edges.loc[edges.from_id.isin(crit), "lead_time_days"] + LEADTIME_PATH_BONUS
    ).clip(upper=340)

    # ---- region noise: flip a few regions so region != destiny ------------
    flip = rng.random(len(nodes)) < NOISE_REGION_FLIP
    nodes.loc[flip, "region"] = rng.choice(REGIONS, size=int(flip.sum()))

    nodes = nodes[["node_id", "kind", "tier", "region", "subtype",
                   "capacity", "lead_time_days", "label"]]

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)

    kc = nodes.kind.value_counts()
    print(f"satellite-supply-chain: {len(nodes)} nodes "
          f"({kc.get('material',0)} material + {kc.get('component',0)} component + "
          f"{kc.get('subsystem',0)} subsystem + {kc.get('integrator',0)} integrator + "
          f"{kc.get('program',0)} program), {len(edges)} edges.")


if __name__ == "__main__":
    main()
```

---

## `data/projects/satellite-supply-chain/load.R`

```r
#' @name load.R
#' @title Load the `satellite-supply-chain` project network (R)
#' @description
#'
#' Reads the two CSVs in this folder and builds a directed, weighted igraph
#' object: a multi-tier satellite manufacturing supply chain (materials ->
#' components -> subsystems -> integrators -> programs). Run it straight
#' (`Rscript load.R`) for a quick summary, or `source()` it and call
#' `load_satellite()` in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "satellite-supply-chain")

#' Load the node table (one row per supplier / subsystem / program).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per supply relationship).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Build the directed, weighted graph.
#'
#' Edges are weighted by `units_per_year` and flow from the upstream node to the
#' downstream node. Use `subcomponent(g, v, mode = "out")` to trace everything
#' downstream of a node, or knock a node out (`delete_vertices`) to test how much
#' end-program output it carries.
load_satellite <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = TRUE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$units_per_year
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n🛰️  satellite-supply-chain (R)\n")
  cat("   Materials -> components -> subsystems -> integrators -> programs;",
      "weighted by units per year.\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_satellite(nodes, edges)

  cat(sprintf("✅ Loaded %d nodes (%d material, %d component, %d subsystem, %d integrator, %d program) and %d edges.\n",
              nrow(nodes), sum(nodes$kind == "material"),
              sum(nodes$kind == "component"), sum(nodes$kind == "subsystem"),
              sum(nodes$kind == "integrator"), sum(nodes$kind == "program"),
              nrow(edges)))
  cat(sprintf("🔗 Directed: %s | total units/year: %s | total value: $%s M\n",
              is_directed(g),
              format(sum(edges$units_per_year), big.mark = ","),
              format(round(sum(edges$value_musd)), big.mark = ",")))
  cat("🎉 Graph ready. `g` is a directed, weighted igraph (weight = units_per_year).\n")
}
```

---

## `data/projects/satellite-supply-chain/load.py`

```python
"""Load the `satellite-supply-chain` project network (Python).

Reads the two CSVs in this folder and builds a directed, weighted python-igraph
object: a multi-tier satellite manufacturing supply chain (materials ->
components -> subsystems -> integrators -> programs). Run it straight
(``python load.py``) for a quick summary, or import ``load_satellite()`` into
your own script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per supplier / subsystem / program."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per supply relationship."""
    return pd.read_csv(HERE / "edges.csv")


def load_satellite(nodes: pd.DataFrame | None = None,
                   edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the directed, weighted graph (edge weight = ``units_per_year``).

    Edges flow from the upstream node to the downstream node. Use
    ``g.subcomponent(v, mode="out")`` to trace everything downstream of a node,
    or delete a vertex to test how much end-program output it carries.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=True, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["units_per_year"]
    return g


if __name__ == "__main__":
    print("\n🛰️  satellite-supply-chain (Python)")
    print("   Materials -> components -> subsystems -> integrators -> programs; "
          "weighted by units per year.\n")

    nodes = load_nodes()
    edges = load_edges()
    g = load_satellite(nodes, edges)

    kinds = nodes["kind"].value_counts()
    print(f"✅ Loaded {len(nodes)} nodes "
          f"({kinds.get('material',0)} material, {kinds.get('component',0)} component, "
          f"{kinds.get('subsystem',0)} subsystem, {kinds.get('integrator',0)} integrator, "
          f"{kinds.get('program',0)} program) and {len(edges)} edges.")
    print(f"🔗 Directed: {g.is_directed()} | total units/year: "
          f"{edges['units_per_year'].sum():,} | total value: "
          f"${round(edges['value_musd'].sum()):,} M")
    print("🎉 Graph ready. Object `g` is a directed, weighted igraph "
          "(weight = units_per_year).")
```

---

## `data/projects/semiconductor-supply/README.md`

# semiconductor-supply

*A multi-tier global semiconductor supply chain — raw materials and gases flow up
through fabs, packaging houses, and chip designers into finished electronic
products.*

![Preview of the semiconductor-supply network](thumb.png)

## At a glance

| | |
|---|---|
| **Direction** | Directed (supply flow: upstream tier → downstream tier) |
| **Weights** | Weighted (`annual_volume`; paired `value_musd` and `lead_time_days`) |
| **Modality** | Multimodal — 5 node kinds across 5 tiers (`material`, `foundry`, `packaging`, `designer`, `product`) |
| **Temporal** | No — a single annual snapshot |
| **Nodes** | 368 (70 material + 46 foundry + 60 packaging + 96 designer + 96 product) |
| **Edges** | 739 supply relationships |
| **Files** | `nodes.csv`, `edges.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

"GlobalFab" is a stylized model of the world semiconductor supply chain. Supply
flows from the most upstream tier to the most downstream:

- **tier 4 `material`** — raw materials, specialty gases, silicon wafers,
  photoresist, sputter targets, bonding wire;
- **tier 3 `foundry`** — wafer fabrication plants ("fabs"), at process nodes from
  mature (28 nm) to leading-edge (3 nm);
- **tier 2 `packaging`** — assembly / test houses (OSATs), standard or advanced
  (2.5D/3D) packaging;
- **tier 1 `designer`** — chip designers and IDMs that place silicon orders;
- **tier 0 `product`** — end OEM products (phones, GPUs, servers, vehicles).

Each directed edge is a supply relationship weighted by `annual_volume` (units or
wafer-starts), with a dollar `value_musd` and a `lead_time_days`. Nodes carry a
`region`, a `tier`, a `capacity`, a nominal `lead_time_days`, and a `subtype`.

This is a flow-and-criticality network. It rewards students who look past which
nodes have the most connections. Some questions to chew on:

- If you could harden one node against disruption, which would it be — and would
  degree, betweenness, or a knockout/criticality analysis give you the same
  answer? Are the busiest suppliers the most important ones?
- Is the chain's resilience the same everywhere, or are some end products one bad
  day away from having no viable supply path at all?
- Does geography matter? If a region were embargoed or hit by a quake, how much
  downstream output would be cut, and through which tier?
- Recovery is not free: when the system is shocked, which nodes are also the
  slowest to come back?

> **Note.** The interesting findings here are deliberately *not* documented. "Big
> suppliers ship more volume" is the starting point, not a finding. Push past it —
> raw degree will mislead you.

## `nodes.csv`

One row per node (supplier or product). Every node has every column populated.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique key. `M###` material, `F###` foundry, `P###` packaging, `D###` designer, `E###` product. Referenced by edges. | character | `M001`, `F016`, `P007`, `D053`, `E030` |
| `kind` | Node kind | Tier role of the node. | character | `material`, `foundry`, `packaging`, `designer`, `product` |
| `tier` | Supply tier | Depth in the chain: 4 = most upstream (material) … 0 = end product. | integer | `4`, `3`, `0` |
| `region` | Region | Where the node operates. | character | `Taiwan`, `South Korea`, `USA`, `Japan`, `China`, `Europe` |
| `subtype` | Subtype | Kind-specific detail: material class, fab process node, packaging grade, designer/product segment. | character | `specialty_gas`, `5nm`, `advanced`, `gpu`, `router` |
| `capacity` | Capacity | Nominal annual throughput capacity (relative units). | integer | `3967`, `310`, `196` |
| `lead_time_days` | Lead time | Nominal replenishment / production lead time in days. | integer | `126`, `35`, `18` |
| `label` | Display name | Human-readable label. (`name` is avoided — python-igraph reserves it for the ID.) | character | `Specialty Gas Co 001`, `OSAT 007 (standard)` |

## `edges.csv`

One row per supply relationship. Directed from the upstream node (`from_id`) to
the downstream node (`to_id`).

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | Upstream node ID | Supplying node (higher tier). | character | `M001`, `D038`, `P039` |
| `to_id` | Downstream node ID | Receiving node (lower tier). | character | `F016`, `E049`, `D053` |
| `annual_volume` | Annual volume | Units / wafer-starts shipped on this relationship per year (the edge weight). | integer | `153`, `227`, `30` |
| `value_musd` | Annual value | Dollar value of the flow, millions USD. | double | `5.504`, `16.824` |
| `lead_time_days` | Edge lead time | Lead time for deliveries on this relationship, days. | integer | `126`, `49`, `29` |

## Load it

```bash
Rscript data/projects/semiconductor-supply/load.R     # R    (igraph)
python  data/projects/semiconductor-supply/load.py     # Python (python-igraph)
```

Both build a directed, weighted `igraph` graph and print a one-screen summary. In
the [R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**semiconductor-supply** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/semiconductor-supply>

---

## `data/projects/semiconductor-supply/_generate.py`

```python
"""Generate the `semiconductor-supply` project network (deterministic).

A multi-tier global semiconductor supply chain spanning five tiers of nodes:
  - tier 4  material   raw materials, specialty gases, wafers, photoresist
  - tier 3  foundry    wafer fabrication plants ("fabs")
  - tier 2  packaging  assembly / test / advanced packaging houses (OSATs)
  - tier 1  designer   chip designers and IDMs (place orders for silicon)
  - tier 0  product    end OEM products (phones, GPUs, cars, servers)

Edges are directed supply flows from upstream (higher tier number) to
downstream (lower tier number). One row per supply relationship. The edge
weight is `annual_volume` (millions of units / wafer-starts) with a paired
`value_musd` ($ value) and `lead_time_days`.

Node attributes: kind, tier, region, capacity, lead_time_days, label.
Regions: Taiwan, South Korea, USA, Japan, China, Europe.

Design parameters (the only record of the planted structure):
  - HUB_FOUNDRY: one advanced Taiwan foundry takes a dominant share of all
    *advanced-node* demand. Many tier-1 designers route advanced parts through
    it, so it has high BETWEENNESS but only modest in-degree (a few fat edges,
    not many edges). Removing it severs most advanced product output.
  - ADV_PACK_REGION: advanced `packaging` is concentrated in ONE region
    (Taiwan); a regional shock severs many advanced downstream paths.
  - CHOKE_MATERIAL: one tier-4 specialty-gas supplier feeds nearly every
    foundry (a second hidden critical node, again betweenness >> degree-rank).
  - LEADTIME_ON_PATH: the longest lead times cluster ON the critical path
    (hub foundry, choke material, advanced packaging) so the bottleneck is
    also the slowest to recover.

Run:
    python data/projects/semiconductor-supply/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

REGIONS = ["Taiwan", "South Korea", "USA", "Japan", "China", "Europe"]

# tier population sizes (total ~ 360 nodes)
N_MATERIAL = 70     # tier 4
N_FOUNDRY = 46      # tier 3
N_PACKAGING = 60    # tier 2
N_DESIGNER = 96     # tier 1
N_PRODUCT = 96      # tier 0

# --- planted parameters -----------------------------------------------------
HUB_SHARE = 0.78          # share of advanced-node demand the hub foundry takes
CHOKE_SHARE = 0.88        # share of foundries the choke material feeds
ADV_PACK_REGION = "Taiwan"
ADV_PACK_CONC = 0.80      # share of advanced packaging routed to that region
LEADTIME_PATH_BONUS = 70  # extra lead-time days loaded onto the critical path
NOISE_REGION_FLIP = 0.10  # fraction of nodes whose region is "wrong" (noise)


def main() -> None:
    rng = np.random.default_rng(SEED)

    # region sampling weights: chip world is Asia-heavy
    rweights = np.array([0.26, 0.16, 0.18, 0.14, 0.16, 0.10])
    rweights = rweights / rweights.sum()

    def pick_regions(n):
        return rng.choice(REGIONS, size=n, p=rweights)

    rows = []  # node rows

    # ----- tier 4: materials ----------------------------------------------
    mat_kinds = ["specialty_gas", "silicon_wafer", "photoresist", "rare_earth",
                 "sputter_target", "cmp_slurry", "lead_frame", "bonding_wire"]
    mat_region = pick_regions(N_MATERIAL)
    for i in range(N_MATERIAL):
        sub = mat_kinds[i % len(mat_kinds)]
        rows.append({
            "node_id": f"M{i+1:03d}", "kind": "material", "tier": 4,
            "region": mat_region[i], "subtype": sub,
            "capacity": int(rng.integers(200, 4000)),
            "lead_time_days": int(np.clip(rng.normal(60, 18), 14, 140)),
            "label": f"{sub.replace('_',' ').title()} Co {i+1:03d}",
        })

    # ----- tier 3: foundries ----------------------------------------------
    f_region = pick_regions(N_FOUNDRY)
    # node tier (process node, nm); a minority are "advanced" (<= 7nm)
    f_node_nm = rng.choice([28, 14, 10, 7, 5, 3], size=N_FOUNDRY,
                           p=[0.30, 0.18, 0.14, 0.16, 0.14, 0.08])
    for i in range(N_FOUNDRY):
        adv = f_node_nm[i] <= 7
        rows.append({
            "node_id": f"F{i+1:03d}", "kind": "foundry", "tier": 3,
            "region": f_region[i], "subtype": f"{int(f_node_nm[i])}nm",
            "capacity": int(rng.integers(20, 220) * (3 if adv else 1)),
            "lead_time_days": int(np.clip(rng.normal(95, 22), 40, 200)),
            "label": f"Fab {i+1:03d} ({int(f_node_nm[i])}nm)",
        })

    # ----- tier 2: packaging ----------------------------------------------
    p_region = pick_regions(N_PACKAGING)
    p_adv = rng.random(N_PACKAGING) < 0.40  # advanced packaging (2.5D/3D/CoWoS)
    # advanced packaging is geographically concentrated: ~70% of the advanced
    # houses sit in ADV_PACK_REGION (a planted single-region dependence).
    for i in range(N_PACKAGING):
        if p_adv[i] and rng.random() < 0.70:
            p_region[i] = ADV_PACK_REGION
    for i in range(N_PACKAGING):
        sub = "advanced" if p_adv[i] else "standard"
        rows.append({
            "node_id": f"P{i+1:03d}", "kind": "packaging", "tier": 2,
            "region": p_region[i], "subtype": sub,
            "capacity": int(rng.integers(30, 300)),
            "lead_time_days": int(np.clip(rng.normal(40, 12), 12, 90)),
            "label": f"OSAT {i+1:03d} ({sub})",
        })

    # ----- tier 1: designers ----------------------------------------------
    d_region = pick_regions(N_DESIGNER)
    d_segment = rng.choice(["mobile", "gpu", "cpu", "auto", "iot", "network"],
                           size=N_DESIGNER)
    # designers that need advanced nodes (high-performance silicon)
    d_advanced = np.isin(d_segment, ["gpu", "cpu", "mobile"]) & (rng.random(N_DESIGNER) < 0.85)
    for i in range(N_DESIGNER):
        rows.append({
            "node_id": f"D{i+1:03d}", "kind": "designer", "tier": 1,
            "region": d_region[i], "subtype": d_segment[i],
            "capacity": int(rng.integers(50, 600)),
            "lead_time_days": int(np.clip(rng.normal(30, 10), 7, 70)),
            "label": f"Designer {i+1:03d} ({d_segment[i]})",
        })

    # ----- tier 0: products -----------------------------------------------
    pr_region = pick_regions(N_PRODUCT)
    pr_segment = rng.choice(["phone", "gpu_card", "server", "vehicle", "iot_device",
                             "router"], size=N_PRODUCT)
    for i in range(N_PRODUCT):
        rows.append({
            "node_id": f"E{i+1:03d}", "kind": "product", "tier": 0,
            "region": pr_region[i], "subtype": pr_segment[i],
            "capacity": int(rng.integers(100, 2000)),
            "lead_time_days": int(np.clip(rng.normal(20, 8), 5, 50)),
            "label": f"Product {i+1:03d} ({pr_segment[i]})",
        })

    nodes = pd.DataFrame(rows)

    # convenient id pools / lookups
    def ids(kind):
        return nodes.loc[nodes.kind == kind, "node_id"].tolist()
    mat_ids = ids("material")
    fou_ids = ids("foundry")
    pack_ids = ids("packaging")
    des_ids = ids("designer")
    prod_ids = ids("product")
    region_of = dict(zip(nodes.node_id, nodes.region))
    sub_of = dict(zip(nodes.node_id, nodes.subtype))

    adv_fou = [f for f in fou_ids if int(sub_of[f].replace("nm", "")) <= 7]
    std_fou = [f for f in fou_ids if f not in adv_fou]
    adv_pack = [p for p in pack_ids if sub_of[p] == "advanced"]
    std_pack = [p for p in pack_ids if p not in adv_pack]
    adv_pack_region = [p for p in adv_pack if region_of[p] == ADV_PACK_REGION]
    if not adv_pack_region:  # safety
        adv_pack_region = adv_pack[:1]

    # ---- pick the planted critical nodes ---------------------------------
    # HUB_FOUNDRY: a Taiwan advanced foundry
    tw_adv = [f for f in adv_fou if region_of[f] == "Taiwan"]
    HUB_FOUNDRY = tw_adv[0] if tw_adv else adv_fou[0]
    # CHOKE_MATERIAL: a specialty-gas material supplier (feeds foundries)
    gas_ids = nodes.loc[(nodes.kind == "material") &
                        (nodes.subtype == "specialty_gas"), "node_id"].tolist()
    CHOKE_MATERIAL = gas_ids[0]

    advanced_designers = [d for d, a in zip(des_ids, d_advanced) if a]
    adv_designers_set = set(advanced_designers)
    std_designers = [d for d in des_ids if d not in adv_designers_set]

    # advanced products (high-performance) vs mature products
    prod_seg = dict(zip(prod_ids, pr_segment))
    adv_prod = [e for e in prod_ids if prod_seg[e] in ("gpu_card", "server", "phone")]
    std_prod = [e for e in prod_ids if e not in set(adv_prod)]

    eds = []  # edge rows

    def add_edge(frm, to, vol, ltd):
        eds.append({
            "from_id": frm, "to_id": to,
            "annual_volume": int(max(vol, 1)),
            "value_musd": round(float(max(vol, 1)) * rng.uniform(0.02, 0.18), 3),
            "lead_time_days": int(ltd),
        })

    def lt_of(n):
        return int(nodes.loc[nodes.node_id == n, "lead_time_days"].iloc[0])

    choke_lt = lt_of(CHOKE_MATERIAL)
    hub_lt = lt_of(HUB_FOUNDRY)

    # DECOY commodity materials that feed almost every mature foundry. They are
    # the highest-DEGREE upstream nodes, but fully substitutable (mature
    # foundries have many suppliers), so removing one cuts almost nothing.
    # Their job is to out-rank the real choke on degree, hiding the choke.
    commodity_pool = [m for m in mat_ids
                      if sub_of[m] == "silicon_wafer" and m != CHOKE_MATERIAL]
    COMMODITY = commodity_pool[0]
    COMMODITY2 = commodity_pool[1]

    # Strict tier order: material(4) -> foundry(3) -> packaging(2)
    #                    -> designer(1) -> product(0).
    #
    # Two weakly separable corridors:
    #   * a MATURE corridor that is richly multi-sourced (resilient), and
    #   * an ADVANCED corridor that funnels through the choke material, the hub
    #     foundry, and Taiwan advanced packaging (fragile single points).
    # The advanced corridor never borrows resilience from the mature side, so
    # the hub & choke are genuine cut vertices for advanced product output --
    # findable by criticality/betweenness but NOT by raw degree.

    # ===== ADVANCED CORRIDOR (the fragile spine) ==========================
    # choke material -> the advanced foundries (its ONLY upstream input).
    add_edge(CHOKE_MATERIAL, HUB_FOUNDRY, int(rng.integers(150, 260)), choke_lt)
    for f in adv_fou:
        if f != HUB_FOUNDRY:
            add_edge(CHOKE_MATERIAL, f, int(rng.integers(60, 160)), choke_lt)

    # hub foundry -> advanced packaging corridor (the Taiwan-led set).
    # The hub is the SOLE upstream feeder of every advanced packaging house,
    # so it lies on every path to the advanced products beyond them -- a genuine
    # cut vertex -- while touching only a handful of nodes (modest degree).
    corridor_pack = list(adv_pack)              # ALL advanced packaging
    # bias volume toward the Taiwan houses so the geographic concentration is
    # real but not a giveaway (noise on the non-Taiwan houses).
    for p in corridor_pack:
        vol = int(rng.integers(180, 360)) if region_of.get(p) == ADV_PACK_REGION \
            else int(rng.integers(40, 110))
        add_edge(HUB_FOUNDRY, p, vol, hub_lt)

    # the other advanced fabs exist but sell into the MATURE designer market
    # (a secondary outlet) -- they do NOT feed advanced packaging, so they give
    # the advanced corridor no alternative path.
    for f in adv_fou:
        if f != HUB_FOUNDRY:
            for d in rng.choice(std_designers, size=int(rng.integers(1, 3)), replace=False):
                add_edge(f, d, int(rng.integers(20, 90)), lt_of(f))

    # advanced packaging -> advanced designers. Each designer draws mostly from
    # the Taiwan corridor houses (concentration) plus occasionally another.
    tw_pack = [p for p in corridor_pack if region_of.get(p) == ADV_PACK_REGION] or corridor_pack
    for d in advanced_designers:
        if rng.random() < ADV_PACK_CONC:
            add_edge(rng.choice(tw_pack), d, int(rng.integers(80, 300)), lt_of(tw_pack[0]))
        else:
            p = rng.choice(corridor_pack)
            add_edge(p, d, int(rng.integers(80, 300)), lt_of(p))
    # advanced designers -> advanced products
    for e in adv_prod:
        for d in rng.choice(advanced_designers, size=int(rng.integers(1, 3)), replace=False):
            add_edge(d, e, int(rng.integers(60, 400)), lt_of(d))

    # ===== MATURE CORRIDOR (resilient, multi-sourced) =====================
    # materials -> mature foundries. The COMMODITY feeds nearly all of them
    # (highest degree, but substitutable); a moderate share also draw the
    # choke gas; everyone has 2-4 ordinary suppliers.
    for f in std_fou:
        add_edge(COMMODITY, f, int(rng.integers(40, 160)), lt_of(COMMODITY))
        # a SECOND commodity wafer line feeds most mature foundries too, so the
        # commodity suppliers (not the choke gas) dominate raw degree.
        if rng.random() < 0.85:
            add_edge(COMMODITY2, f, int(rng.integers(30, 120)), lt_of(COMMODITY2))
        if rng.random() < 0.25:
            add_edge(CHOKE_MATERIAL, f, int(rng.integers(30, 120)), choke_lt)
        excl = (COMMODITY, COMMODITY2, CHOKE_MATERIAL)
        for m in rng.choice([x for x in mat_ids if x not in excl],
                            size=int(rng.integers(2, 5)), replace=False):
            add_edge(m, f, int(rng.integers(5, 80)), lt_of(m))
    # some materials also feed standard packaging directly
    for p in std_pack:
        for m in rng.choice([x for x in mat_ids if x != CHOKE_MATERIAL],
                            size=int(rng.integers(1, 3)), replace=False):
            add_edge(m, p, int(rng.integers(5, 60)), lt_of(m))
    # mature foundries -> standard packaging (multi-sourced)
    for p in std_pack:
        for f in rng.choice(std_fou, size=int(rng.integers(2, 4)), replace=False):
            add_edge(f, p, int(rng.integers(20, 120)), lt_of(f))
    # standard packaging -> mature designers
    for d in std_designers:
        for p in rng.choice(std_pack, size=int(rng.integers(2, 4)), replace=False):
            add_edge(p, d, int(rng.integers(30, 120)), lt_of(p))
    # mature designers -> mature products
    for e in std_prod:
        for d in rng.choice(std_designers, size=int(rng.integers(2, 4)), replace=False):
            add_edge(d, e, int(rng.integers(50, 300)), lt_of(d))

    corridor_pack = list(dict.fromkeys(corridor_pack))
    edges = pd.DataFrame(eds)

    # ---- LEADTIME_ON_PATH: load extra lead time onto the critical path ----
    crit = {HUB_FOUNDRY, CHOKE_MATERIAL}
    crit |= set(corridor_pack)
    nodes.loc[nodes.node_id.isin(crit), "lead_time_days"] = (
        nodes.loc[nodes.node_id.isin(crit), "lead_time_days"] + LEADTIME_PATH_BONUS
    ).clip(upper=300)
    # reflect onto edges that originate from those critical nodes
    edges.loc[edges.from_id.isin(crit), "lead_time_days"] = (
        edges.loc[edges.from_id.isin(crit), "lead_time_days"] + LEADTIME_PATH_BONUS
    ).clip(upper=320)

    # ---- region noise: flip a few regions so region != destiny ------------
    flip = rng.random(len(nodes)) < NOISE_REGION_FLIP
    nodes.loc[flip, "region"] = rng.choice(REGIONS, size=int(flip.sum()))

    nodes = nodes[["node_id", "kind", "tier", "region", "subtype",
                   "capacity", "lead_time_days", "label"]]

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)

    kc = nodes.kind.value_counts()
    print(f"semiconductor-supply: {len(nodes)} nodes "
          f"({kc.get('material',0)} material + {kc.get('foundry',0)} foundry + "
          f"{kc.get('packaging',0)} packaging + {kc.get('designer',0)} designer + "
          f"{kc.get('product',0)} product), {len(edges)} edges.")


if __name__ == "__main__":
    main()
```

---

## `data/projects/semiconductor-supply/load.R`

```r
#' @name load.R
#' @title Load the `semiconductor-supply` project network (R)
#' @description
#'
#' Reads the two CSVs in this folder and builds a directed, weighted igraph
#' object: a multi-tier semiconductor supply chain (materials -> foundries ->
#' packaging -> designers -> products). Run it straight (`Rscript load.R`) for a
#' quick summary, or `source()` it and call `load_semi()` in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "semiconductor-supply")

#' Load the node table (one row per supplier / product).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per supply relationship).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Build the directed, weighted graph.
#'
#' Edges are weighted by `annual_volume` and flow from the upstream node to the
#' downstream node. Use `subcomponent(g, v, mode = "out")` to trace everything
#' downstream of a node, or knock a node out (`delete_vertices`) to test how
#' much end-product output it carries.
load_semi <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = TRUE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$annual_volume
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n🔌 semiconductor-supply (R)\n")
  cat("   Materials -> foundries -> packaging -> designers -> products;",
      "weighted by annual volume.\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_semi(nodes, edges)

  cat(sprintf("✅ Loaded %d nodes (%d material, %d foundry, %d packaging, %d designer, %d product) and %d edges.\n",
              nrow(nodes), sum(nodes$kind == "material"),
              sum(nodes$kind == "foundry"), sum(nodes$kind == "packaging"),
              sum(nodes$kind == "designer"), sum(nodes$kind == "product"),
              nrow(edges)))
  cat(sprintf("🔗 Directed: %s | total annual volume: %s | total value: $%s M\n",
              is_directed(g),
              format(sum(edges$annual_volume), big.mark = ","),
              format(round(sum(edges$value_musd)), big.mark = ",")))
  cat("🎉 Graph ready. `g` is a directed, weighted igraph (weight = annual_volume).\n")
}
```

---

## `data/projects/semiconductor-supply/load.py`

```python
"""Load the `semiconductor-supply` project network (Python).

Reads the two CSVs in this folder and builds a directed, weighted python-igraph
object: a multi-tier semiconductor supply chain (materials -> foundries ->
packaging -> designers -> products). Run it straight (``python load.py``) for a
quick summary, or import ``load_semi()`` into your own script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per supplier / product."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per supply relationship."""
    return pd.read_csv(HERE / "edges.csv")


def load_semi(nodes: pd.DataFrame | None = None,
              edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the directed, weighted graph (edge weight = ``annual_volume``).

    Edges flow from the upstream node to the downstream node. Use
    ``g.subcomponent(v, mode="out")`` to trace everything downstream of a node,
    or delete a vertex to test how much end-product output it carries.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=True, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["annual_volume"]
    return g


if __name__ == "__main__":
    print("\n🔌 semiconductor-supply (Python)")
    print("   Materials -> foundries -> packaging -> designers -> products; "
          "weighted by annual volume.\n")

    nodes = load_nodes()
    edges = load_edges()
    g = load_semi(nodes, edges)

    kinds = nodes["kind"].value_counts()
    print(f"✅ Loaded {len(nodes)} nodes "
          f"({kinds.get('material',0)} material, {kinds.get('foundry',0)} foundry, "
          f"{kinds.get('packaging',0)} packaging, {kinds.get('designer',0)} designer, "
          f"{kinds.get('product',0)} product) and {len(edges)} edges.")
    print(f"🔗 Directed: {g.is_directed()} | total annual volume: "
          f"{edges['annual_volume'].sum():,} | total value: "
          f"${round(edges['value_musd'].sum()):,} M")
    print("🎉 Graph ready. Object `g` is a directed, weighted igraph "
          "(weight = annual_volume).")
```

---

## `data/projects/trade-commodity/README.md`

# trade-commodity

*World trade in a single strategic commodity ("refined metal", in tonnes) among
~140 countries, observed before, during, and after a major supply disruption.*

![Preview of the trade-commodity network](thumb.png)

## At a glance

| | |
|---|---|
| **Direction** | Directed (export flow: exporter → importer) |
| **Weights** | Weighted (`tonnes` per edge; `price_usd_per_t` companion field) |
| **Modality** | Unimodal — one node kind (`country`) |
| **Temporal** | Yes — one row per (exporter, importer, **period**): `before` / `during` / `after` |
| **Nodes** | 140 (countries across 6 regional blocs) |
| **Edges** | 1,210 (≈422 before + ≈378 during + ≈410 after) |
| **Files** | `nodes.csv`, `edges.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

A directed, weighted trade network for one strategic commodity. Each **country**
both produces and consumes the commodity; a directed **export flow** carries
`tonnes` from an exporting country to an importing country, with a per-tonne
trade price attached. The world is observed across three **periods** — a normal
market (`before`), a market disrupted by a supply shock (`during`), and a
partially recovered market (`after`). Countries carry attributes for region/bloc,
GDP per capita, and domestic production and consumption capacity.

This is a flow, criticality, and community network with a built-in shock you can
study as a natural experiment. Some questions to chew on:

- Which importers are most exposed if a single supplier disappears? Is exposure
  about *how much* a country trades, or *how concentrated* its sources are?
- Does the trade map break into regional communities, and who are the few
  countries that bridge between blocs?
- If you ranked countries by how much trade *passes through* them, would that
  match a ranking by raw trade volume — or would different countries top each?
- The three periods are not the same world. What changed between them, who was
  hurt, and did anyone fail to recover?
- Whose removal would cut some group of countries off from supply entirely?

> **Note.** The interesting findings here are deliberately *not* documented.
> "Bigger economies trade more" is the starting point, not a finding. Push past it.

## `nodes.csv`

One row per country.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique country key (`C###`). Referenced by edges. | character | `C001`, `C047`, `C140` |
| `kind` | Node kind | Node type (all countries in this network). | character | `country` |
| `label` | Display name | Human-readable label (region prefix + index). (`name` is avoided — python-igraph reserves it for the ID.) | character | `NOR-001`, `SOU-031`, `EUR-061` |
| `region` | Region / bloc | Continental trade bloc the country belongs to. | character | `North America`, `Africa`, `Asia-Pacific` |
| `gdp_per_capita` | GDP per capita | National income per person, USD. | integer | `54442`, `43966`, `14354` |
| `production` | Production | Domestic output capacity of the commodity, tonnes. | double | `7016`, `33045`, `15239` |
| `consumption` | Consumption | Domestic demand for the commodity, tonnes. | double | `52860`, `11350`, `31147` |

## `edges.csv`

One row per (exporter, importer, period). Directed; a pair can appear up to three
times (once per period).

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `exporter_id` | Exporter node ID | Country sending the commodity. | character | `C004`, `C047` |
| `importer_id` | Importer node ID | Country receiving the commodity. | character | `C001`, `C007` |
| `period` | Period | Market era: `before`, `during`, or `after` the supply disruption. | character | `before`, `during`, `after` |
| `tonnes` | Tonnes traded | Quantity moved on that edge in that period (the edge weight). | integer | `78`, `1340`, `40285` |
| `price_usd_per_t` | Price per tonne | Trade price for that flow, USD per tonne. | integer | `889`, `974`, `1183` |

## Load it

```bash
Rscript data/projects/trade-commodity/load.R     # R    (igraph)
python  data/projects/trade-commodity/load.py     # Python (python-igraph)
```

Both build a directed, weighted `igraph` graph and print a one-screen summary. In
the [R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**trade-commodity** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/trade-commodity>

---

## `data/projects/trade-commodity/_generate.py`

```python
"""Generate the `trade-commodity` project network (deterministic).

International trade in a single strategic commodity ("refined metal", measured in
tonnes) among ~140 countries, observed across three periods around a supply
shock:
  - period = "before"  : normal market
  - period = "during"  : a dominant exporter goes offline
  - period = "after"   : partial, costlier rewiring

Nodes are countries (kind = "country"); edges are directed export flows
exporter -> importer for a given period, weighted by tonnes traded.

Design parameters (the only record of the planted structure):
  - DOMINANT_EXPORTERS: a few large exporters supply most of the world. One of
    them (the SHOCKED exporter) collapses to ~0 out-strength DURING and recovers
    only partially AFTER.
  - DEPENDENT_IMPORTERS: a handful of importers draw the large majority of their
    supply from ONE or TWO dominant exporters (very high top-2 supply share).
    When their dominant source goes offline they scramble: in-strength collapses
    DURING and partially rewires to costlier sources AFTER (some never recover).
  - REEXPORTER: one mid-size country imports heavily and re-exports most of it
    (import ~= export, high throughput, high betweenness) — a transshipment hub
    that brokers flow and masks origin.
  - BLOCS: trade clusters strongly within region/bloc (high modularity) with a
    few inter-bloc broker countries.
  - BROKERS: a few structurally critical countries sit on the only supply path
    into otherwise peripheral importer groups (high betweenness vs degree).

Run:
    python data/projects/trade-commodity/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

PERIODS = ["before", "during", "after"]

# blocs (region label, count, base gdp-per-capita tier 0..1)
BLOCS = [
    ("North America", 18, 0.82),
    ("South America", 20, 0.45),
    ("Europe", 30, 0.78),
    ("Africa", 28, 0.30),
    ("Middle East", 16, 0.55),
    ("Asia-Pacific", 28, 0.50),
]

# --- planted parameters -----------------------------------------------------
N_DOMINANT = 6          # big exporters that supply most of the market
SHOCK_OFFSET = 0        # index (within dominant list) of the exporter that fails
SHOCK_RECOVERY = 0.35   # AFTER out-strength as fraction of BEFORE for shocked exporter
N_DEPENDENT = 9         # importers concentrated on one/two dominant sources
DEP_SHARE = 0.86        # share of a dependent importer's supply from its top source(s)
DEP_RECOVERY = 0.55     # AFTER in-strength as fraction of BEFORE for dependents
N_PERIPHERAL_GROUPS = 4 # importer groups reachable only via a broker
COST_PREMIUM = 1.0      # AFTER price premium added when rewiring to new sources


def main() -> None:
    rng = np.random.default_rng(SEED)

    # ----- countries -------------------------------------------------------
    rows = []
    cid = 1
    bloc_of = {}
    for region, n, tier in BLOCS:
        for _ in range(n):
            gdp = int(np.clip(2500 + tier * 60000 + rng.normal(0, 9000), 800, 110000))
            # latent production / consumption capacity (tonnes), noisy
            prod = float(np.clip(rng.lognormal(mean=10.0, sigma=1.1), 2e3, 5e6))
            cons = float(np.clip(rng.lognormal(mean=10.2, sigma=0.9), 5e3, 4e6))
            node_id = f"C{cid:03d}"
            bloc_of[node_id] = region
            rows.append({
                "node_id": node_id,
                "kind": "country",
                "label": f"{region[:3].upper()}-{cid:03d}",
                "region": region,
                "gdp_per_capita": gdp,
                "production": round(prod, 0),
                "consumption": round(cons, 0),
            })
            cid += 1
    nodes = pd.DataFrame(rows)
    ids = list(nodes.node_id)
    n_countries = len(ids)
    region_arr = nodes["region"].to_numpy()
    prod_arr = nodes["production"].to_numpy().astype(float).copy()
    cons_arr = nodes["consumption"].to_numpy().astype(float).copy()

    idx_of = {nid: i for i, nid in enumerate(ids)}

    # ----- choose dominant exporters --------------------------------------
    # the highest-production countries become dominant exporters; give them a
    # large production bump so the market really concentrates on them.
    dominant = list(np.argsort(-prod_arr)[:N_DOMINANT])
    for d in dominant:
        prod_arr[d] *= 4.0
    nodes.loc[:, "production"] = prod_arr.round(0)
    shocked = dominant[SHOCK_OFFSET]

    # ----- choose dependent importers -------------------------------------
    # high-consumption, low-production countries that lean on dominant sources.
    deficit = cons_arr - prod_arr
    cand = [i for i in np.argsort(-deficit) if i not in dominant]
    dependent = cand[:N_DEPENDENT]
    # each dependent importer is pinned to 1-2 dominant sources, and the SHOCKED
    # exporter is the primary source for several of them.
    dep_sources = {}
    for k, di in enumerate(dependent):
        if k < 5:
            primary = shocked
        else:
            primary = dominant[(k % (N_DOMINANT - 1)) + 1]
        secondary = dominant[(dominant.index(primary) + 2) % N_DOMINANT]
        dep_sources[di] = (primary, secondary)

    # ----- re-exporter (transshipment hub) --------------------------------
    # a mid-size country (mid production, mid consumption) that brokers flow.
    mid = [i for i in range(n_countries)
           if i not in dominant and i not in dependent]
    # pick a mid-size country with genuine demand capacity so it can sustain a
    # high import + re-export throughput.
    mid_sorted = sorted(mid, key=lambda i: -(prod_arr[i] + cons_arr[i]))
    reexporter = mid_sorted[8]   # not a top producer, but well-connected & sizeable

    # ----- peripheral importer groups reachable only via a broker ---------
    # pick a few brokers; behind each, a cluster of small importers that buy ONLY
    # from the broker (so the broker sits on their only supply path).
    broker_pool = [i for i in mid if i != reexporter]
    rng.shuffle(broker_pool)
    brokers = broker_pool[:N_PERIPHERAL_GROUPS]
    periph = {}
    used = set(brokers) | {reexporter} | set(dominant) | set(dependent)
    remaining = [i for i in range(n_countries) if i not in used]
    rng.shuffle(remaining)
    cur = 0
    for b in brokers:
        grp = remaining[cur:cur + 4]
        cur += 4
        periph[b] = grp
        used.update(grp)

    # supplier of each broker = a NON-shocked dominant exporter (so the broker's
    # downstream group keeps a stable single supply path: dom -> broker -> periph)
    nonshock_dom = [d for d in dominant if d != shocked]
    broker_src = {b: nonshock_dom[j % len(nonshock_dom)]
                  for j, b in enumerate(brokers)}
    periph_members = {g for grp in periph.values() for g in grp}

    # ----- helper: base trade volume for a pair ---------------------------
    def base_volume(src, dst):
        # gravity-ish: bigger exporter * bigger importer, same-bloc bonus
        s = prod_arr[src] ** 0.5
        d = cons_arr[dst] ** 0.5
        bloc_bonus = 1.6 if region_arr[src] == region_arr[dst] else 1.0
        return s * d * 1e-3 * bloc_bonus

    edge_rows = []

    by_region = {}
    for r in {region_arr[i] for i in range(n_countries)}:
        by_region[r] = [i for i in range(n_countries) if region_arr[i] == r]

    # producers within each bloc, ranked by production (bloc background trade
    # routes mostly through these regional suppliers -> tight communities).
    # Exclude brokers and the re-exporter so their degree stays low and their
    # betweenness (structural role) stands out against degree.
    _excl = set(brokers) | {reexporter}
    bloc_suppliers = {r: [i for i in sorted(members, key=lambda i: -prod_arr[i])
                          if i not in _excl][:8]
                      for r, members in by_region.items()}

    # ----- build BEFORE flows ---------------------------------------------
    # 1) within-bloc background trade: every country buys from several same-bloc
    #    suppliers (dense, high-volume -> creates modular community structure).
    def background_flows(period, scale=1.0):
        out = []
        for dst in range(n_countries):
            if dst in periph_members:
                continue  # peripheral importers buy ONLY via their broker
            r = region_arr[dst]
            same = [i for i in bloc_suppliers[r] if i != dst]
            if not same:
                continue
            k = rng.integers(3, min(7, len(same) + 1))
            picks = rng.choice(same, size=min(k, len(same)), replace=False)
            for s in picks:
                vol = base_volume(s, dst) * rng.uniform(0.45, 1.1) * scale
                out.append((s, dst, vol))
        return out

    # 2) dominant exporters sell broadly across blocs (big inter-bloc ties)
    def dominant_flows(period, shocked_factor):
        out = []
        for d in dominant:
            factor = shocked_factor if d == shocked else 1.0
            buyers = rng.choice(n_countries, size=20, replace=False)
            for b in buyers:
                if b == d or b in periph_members:
                    continue
                vol = base_volume(d, b) * rng.uniform(0.20, 0.45) * factor
                out.append((d, b, vol))
        return out

    # 3) dependent importers: concentrate supply on 1-2 dominant sources, but
    #    keep a small surviving non-dominant tail that persists through the shock
    #    (so in-strength collapses DURING then partially recovers AFTER).
    def dependent_flows(period, shocked_factor):
        out = []
        for di in dependent:
            primary, secondary = dep_sources[di]
            need = cons_arr[di] * 0.9
            p_factor = shocked_factor if primary == shocked else 1.0
            s_factor = shocked_factor if secondary == shocked else 1.0
            out.append((primary, di, need * DEP_SHARE * 0.78 * p_factor))
            out.append((secondary, di, need * DEP_SHARE * 0.22 * s_factor))
            # surviving tail of non-dominant suppliers (unaffected by the shock);
            # AFTER, this tail grows as the importer rewires to costlier sources.
            r = region_arr[di]
            tail = [i for i in bloc_suppliers[r]
                    if i not in (primary, secondary, di)][:3]
            rewire = 1.0 + (2.2 if period == "after" else 0.0)
            for o in tail:
                out.append((o, di, need * (1 - DEP_SHARE) * 0.5 * rewire))
        return out

    # 4) re-exporter: imports a lot from dominants, re-exports most to many
    #    (import ~= export, very high throughput & betweenness).
    def reexport_flows(period, shocked_factor):
        out = []
        re = reexporter
        srcs = dominant[1:4]   # avoid the shocked one as sole source
        total_in = 0.0
        # large absolute imports so the hub has real throughput regardless of its
        # own small domestic consumption.
        per_src = 40000
        for s in srcs:
            f = shocked_factor if s == shocked else 1.0
            vol = per_src * rng.uniform(0.85, 1.15) * f
            out.append((s, re, vol))
            total_in += vol
        # re-export ~90% of imports to many buyers across blocs (import ~= export)
        buyers = rng.choice(n_countries, size=22, replace=False)
        buyers = [b for b in buyers if b != re and b not in periph_members]
        per = (total_in * 0.9) / max(len(buyers), 1)
        for b in buyers:
            out.append((re, b, per * rng.uniform(0.7, 1.3)))
        return out

    # 5) broker -> peripheral groups (broker is the SOLE supplier of its group,
    #    so it sits on the only supply path -> high betweenness vs degree).
    def broker_flows(period, shocked_factor):
        out = []
        for b in brokers:
            src = broker_src[b]
            f = shocked_factor if src == shocked else 1.0
            vol_in = base_volume(src, b) * 1.8 * f + 4000 * f
            out.append((src, b, vol_in))
            grp = periph[b]
            per = (vol_in * 0.85) / max(len(grp), 1)
            for g in grp:
                out.append((b, g, per * rng.uniform(0.8, 1.2)))
        return out

    def assemble(period, shocked_factor, premium):
        flows = []
        flows += [(s, d, v, "bloc") for (s, d, v) in background_flows(period)]
        flows += [(s, d, v, "major") for (s, d, v) in dominant_flows(period, shocked_factor)]
        flows += [(s, d, v, "dependency") for (s, d, v) in dependent_flows(period, shocked_factor)]
        flows += [(s, d, v, "reexport") for (s, d, v) in reexport_flows(period, shocked_factor)]
        flows += [(s, d, v, "broker") for (s, d, v) in broker_flows(period, shocked_factor)]
        for (s, d, v, kind) in flows:
            if s == d:
                continue
            noise = rng.lognormal(mean=0.0, sigma=0.25)
            tonnes = max(v * noise, 0.0)
            row = {
                "exporter_id": ids[s], "importer_id": ids[d], "period": period,
                "tonnes": int(round(tonnes)), "flow_type": kind,
            }
            # price: base + distance/scarcity; AFTER rewired flows cost more
            base_price = 900 + (0 if region_arr[s] == region_arr[d] else 220)
            base_price += premium * 180 if kind in ("dependency", "broker") else 0
            base_price *= rng.uniform(0.92, 1.10)
            row["price_usd_per_t"] = int(round(base_price))
            if row["tonnes"] >= 50:
                edge_rows.append(row)

    # BEFORE: normal
    assemble("before", shocked_factor=1.0, premium=0.0)
    # DURING: shocked exporter collapses to ~0; dependents scramble; brokers/reexport
    # drained; market does NOT fully replace the lost supply.
    assemble("during", shocked_factor=0.04, premium=0.4)
    # AFTER: shocked exporter partially recovers; dependents partially rewire to
    # costlier sources (premium up); some never recover (handled by recovery<1).
    assemble("after", shocked_factor=SHOCK_RECOVERY, premium=COST_PREMIUM)

    edges = pd.DataFrame(edge_rows)
    # collapse duplicate (exporter, importer, period) rows by summing tonnes and
    # taking a tonnes-weighted mean price. `flow_type` is an INTERNAL design tag
    # only — it is deliberately NOT written out (it would reveal the planted
    # structure). Different flow mechanisms between the same pair merge here.
    edges["_pt"] = edges["price_usd_per_t"] * edges["tonnes"]
    edges = (edges.groupby(["exporter_id", "importer_id", "period"],
                           as_index=False)
             .agg(tonnes=("tonnes", "sum"), _pt=("_pt", "sum")))
    edges["price_usd_per_t"] = (edges["_pt"] / edges["tonnes"]).round(0).astype(int)
    edges = edges[["exporter_id", "importer_id", "period", "tonnes",
                   "price_usd_per_t"]]

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)

    # Optional debug dump of planted identities (only when explicitly requested,
    # so the normal run prints just the one-line summary and never leaks the
    # story into stdout that students would see).
    import os
    if os.environ.get("TRADE_DEBUG"):
        print("DEBUG shocked_exporter:", ids[shocked])
        print("DEBUG dominant:", [ids[d] for d in dominant])
        print("DEBUG dependents:", [ids[d] for d in dependent])
        print("DEBUG reexporter:", ids[reexporter])
        print("DEBUG brokers:", [ids[b] for b in brokers])
        print("DEBUG periph:", {ids[b]: [ids[g] for g in grp]
                                 for b, grp in periph.items()})

    print(f"trade-commodity: {len(nodes)} nodes (countries), {len(edges)} edges "
          f"across {edges['period'].nunique()} periods "
          f"(before={int((edges.period=='before').sum())}, "
          f"during={int((edges.period=='during').sum())}, "
          f"after={int((edges.period=='after').sum())}).")


if __name__ == "__main__":
    main()
```

---

## `data/projects/trade-commodity/load.R`

```r
#' @name load.R
#' @title Load the `trade-commodity` project network (R)
#' @description
#'
#' Reads the two CSVs in this folder and builds a directed, weighted igraph
#' object: export flows of a single strategic commodity between countries,
#' recorded across three periods (`before` / `during` / `after` a supply shock).
#' Run it straight (`Rscript load.R`) for a quick summary, or `source()` it and
#' call `load_trade()` to get the graph in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "trade-commodity")

#' Load the node table (one row per country).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per exporter x importer x period).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Build the directed, weighted graph.
#'
#' Edges are weighted by `tonnes`. Because the data is temporal (a `period`
#' column), an exporter->importer pair can appear up to three times (once per
#' period) as parallel edges. Filter to one `period` first if you want a simple
#' graph, e.g. `edges <- subset(load_edges(), period == "before")`.
load_trade <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = TRUE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$tonnes
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n\U0001F310 trade-commodity (R)\n")
  cat("   Country-to-country commodity export flows; weighted by tonnes,\n")
  cat("   across before / during / after a supply shock.\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_trade(nodes, edges)

  cat(sprintf("✅ Loaded %d countries and %d edges across %d periods.\n",
              nrow(nodes), nrow(edges), length(unique(edges$period))))
  cat(sprintf("\U0001F517 Directed: %s | total tonnes traded: %s\n",
              is_directed(g), format(sum(edges$tonnes), big.mark = ",")))
  per <- tapply(edges$tonnes, edges$period, sum)
  cat("\U0001F4E6 Tonnes by period: ",
      paste(sprintf("%s=%s", names(per), format(per, big.mark = ",")),
            collapse = " | "), "\n")
  cat("\U0001F389 Graph ready. Object `g` is a directed, weighted igraph.\n")
}
```

---

## `data/projects/trade-commodity/load.py`

```python
"""Load the `trade-commodity` project network (Python).

Reads the two CSVs in this folder and builds a directed, weighted python-igraph
object: export flows of a single strategic commodity between countries, recorded
across three periods (``before`` / ``during`` / ``after`` a supply shock). Run it
straight (``python load.py``) for a quick summary, or import ``load_trade()``
into your own script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per country."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per exporter x importer x period."""
    return pd.read_csv(HERE / "edges.csv")


def load_trade(nodes: pd.DataFrame | None = None,
               edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the directed, weighted graph (edge weight = ``tonnes``).

    The data is temporal (a ``period`` column), so an exporter->importer pair can
    appear up to three times (once per period) as parallel edges. Filter to one
    ``period`` first if you want a simple graph, e.g.
    ``edges[edges.period == "before"]``.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=True, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["tonnes"]
    return g


if __name__ == "__main__":
    print("\n\U0001F310 trade-commodity (Python)")
    print("   Country-to-country commodity export flows; weighted by tonnes,")
    print("   across before / during / after a supply shock.\n")

    nodes = load_nodes()
    edges = load_edges()
    g = load_trade(nodes, edges)

    print(f"✅ Loaded {len(nodes)} countries and {len(edges)} edges across "
          f"{edges['period'].nunique()} periods.")
    print(f"\U0001F517 Directed: {g.is_directed()} | total tonnes traded: "
          f"{edges['tonnes'].sum():,}")
    per = edges.groupby('period')['tonnes'].sum()
    print("\U0001F4E6 Tonnes by period: " +
          " | ".join(f"{k}={v:,}" for k, v in per.items()))
    print("\U0001F389 Graph ready. Object `g` is a directed, weighted igraph.")
```

---

## `data/projects/transit-multimodal/README.md`

# transit-multimodal

*A hypothetical city's public-transit network: neighborhoods linked by metro and
bus, with travel times, service frequency, and capacity on every link.*

![Preview of the transit-multimodal network](thumb.png)

## At a glance

| | |
|---|---|
| **Direction** | Undirected (a transit link runs both ways) |
| **Weights** | Weighted (`capacity` riders/hr; also `travel_time_min`, `frequency_per_hr`) |
| **Modality** | Multimodal / multiplex — two edge `mode`s (`metro`, `bus`); a pair may carry BOTH (parallel edges). `lines.csv` is a route lookup |
| **Temporal** | No — a single service snapshot (typical weekday) |
| **Nodes** | 152 neighborhoods |
| **Edges** | 384 links (81 metro + 303 bus) |
| **Files** | `nodes.csv`, `edges.csv`, `lines.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

Nodes are **neighborhoods** laid out on a 2D city map with a central business
district (CBD) at the middle and concentric rings of neighborhoods outward.
Edges are **transit links** between neighborhoods in two modes: a fast,
high-frequency, high-capacity **metro** that runs on a set of radial lines plus
ring lines, and a slower, lower-capacity **bus** mesh that covers many more
neighborhoods and feeds outer areas to the rail. Because the same pair of
neighborhoods can be connected by both a metro and a bus link, the graph is a
**multiplex** with parallel edges (use the `mode` attribute to tell them apart).
Each link records its travel time, how many vehicles run per hour, and its
hourly seat capacity (the primary edge weight). Each neighborhood records its
district, map position, population, median income, jobs, and whether it has a
metro station.

This is a natural home for **criticality**, **accessibility/equity**, and
**counterfactual ("what if we add a link?")** questions. Some things worth
investigating:

- Which neighborhoods are interchange **hubs**, and how fragile is the network if
  one of them goes down? Do the ring lines change the answer?
- Is access to jobs evenly distributed? Compute a job-access travel time or a
  gravity-accessibility score per neighborhood. Is what you see explained by
  population and distance from the center — or by *something about the
  neighborhoods*?
- Some neighborhoods are far better served than others at the same distance from
  downtown. What separates them?
- **Counterfactual:** if you could add a single new transit link anywhere, which
  one would most improve travel times for an underserved part of the city — and
  how does that compare to adding a random link?
- Project or partition the network: do districts behave as communities? Where are
  the structural gaps between them?

> **Note.** The interesting findings are deliberately undocumented. "Busy central
> neighborhoods have more service" is the starting point, not an answer. Look for
> the structure — and the gaps — underneath.

## `nodes.csv`

One row per neighborhood.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique key (`N###`). Referenced by edges. | character | `N003`, `N025`, `N127` |
| `label` | Label | Human-readable display name (district + number). | character | `CBD 003`, `East 025` |
| `district` | District | Which wedge of the city the neighborhood sits in. | character | `CBD`, `East`, `NorthWest` |
| `x` | X coordinate | Map x position (CBD is near the origin). | double | `0.051`, `-0.395` |
| `y` | Y coordinate | Map y position. | double | `-0.008`, `0.159` |
| `population` | Population | Residents in the neighborhood. | integer | `4539`, `22073` |
| `median_income` | Median household income | Neighborhood median income, USD. | integer | `129919`, `24000` |
| `jobs` | Jobs | Number of jobs located in the neighborhood. | integer | `66400`, `80` |
| `has_metro` | Has metro station | 1 if a metro line stops here, else 0. | integer | `1`, `0` |

## `edges.csv`

One row per transit link. Undirected link between `from_id` and `to_id`. The same
pair may appear twice with different `mode` (parallel edges = the multiplex).

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | From node ID | One endpoint neighborhood (joins to `nodes.csv`). | character | `N003`, `N025` |
| `to_id` | To node ID | Other endpoint neighborhood (joins to `nodes.csv`). | character | `N007`, `N047` |
| `mode` | Mode | Transit mode of the link. | character | `metro`, `bus` |
| `line` | Line / route | Line or route id this link belongs to (joins to `lines.csv`). | character | `M1`, `Ring`, `B045`, `F570` |
| `travel_time_min` | In-vehicle travel time | Minutes to ride this link (metro is faster than bus). | double | `2.0`, `3.5`, `17.8` |
| `frequency_per_hr` | Service frequency | Vehicles per hour on this link (higher = shorter wait). | double | `12.0`, `1.5`, `23.0` |
| `capacity` | Capacity | Seats offered per hour — the primary edge weight. | integer | `2544`, `120` |

## `lines.csv`

Lookup table for transit lines and bus routes (one row per line). Not a node
list — join it onto the `line` column in `edges.csv`.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `line_id` | Line ID | Unique line/route key. | character | `M1`, `Ring`, `OuterArc`, `B045` |
| `mode` | Mode | Mode the line operates. | character | `metro`, `bus` |
| `kind` | Line kind | Structural role of the line. | character | `radial`, `inner_ring`, `outer_ring_partial`, `local`, `feeder` |
| `label` | Label | Human-readable line name. | character | `Metro Line M1`, `Bus Route F570` |
| `n_stations` | Station count | Number of stops/stations on the line. | integer | `7`, `2` |

## Load it

```bash
Rscript data/projects/transit-multimodal/load.R     # R    (igraph, multimodal)
python  data/projects/transit-multimodal/load.py     # Python (python-igraph, multimodal)
```

Both build an undirected, weighted, multimodal `igraph` graph (edge weight =
`capacity`; `mode` distinguishes metro vs bus parallel edges) and print a
one-screen summary. In the
[R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**transit-multimodal** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/transit-multimodal>

---

## `data/projects/transit-multimodal/_generate.py`

```python
"""Generate the `transit-multimodal` project network (deterministic).

A multimodal urban public-transit network for one hypothetical city.
  - ~160 NEIGHBORHOODS (nodes), placed on a 2D city layout with a CBD center
    and concentric outer rings.
Edges are transit links between neighborhoods, in TWO modes (a multiplex):
  - metro: fast, high-frequency, high-capacity, but only serves neighborhoods
    on the rail lines (radial spokes + an inner ring + a partial outer ring).
  - bus: a denser, slower, lower-capacity mesh that covers many more
    neighborhoods, plus feeder routes that bring outer areas to the nearest
    metro station.
The same neighborhood pair can carry BOTH a bus and a metro edge -> parallel
edges (the multiplex). A companion `lines.csv` lists each transit line/route.

Design parameters (the only record of the planted structure):
  - INCOME_PENALTY: job-access travel-time rises as neighborhood income FALLS,
    holding population and distance-to-CBD fixed. We force this by giving
    low-income peripheral areas metro=0 and only sparse, infrequent bus service,
    while planting a few WEALTHY low-population near-metro areas that are
    over-served. So income predicts access AFTER controlling for pop & distance.
  - DESERT_NODES: a planted set of HIGH-population, LOW-income, peripheral
    neighborhoods deliberately left off the metro with thin bus service ->
    bottom-decile closeness/accessibility despite high population (transit
    deserts that are NOT explained by demand).
  - MISSING_LINK: two large adjacent districts (EAST and SOUTH wedges) are NOT
    directly connected; every trip between them detours through the CBD. Adding
    ONE crosstown edge collapses shortest paths for that whole region (the
    counterfactual centerpiece). The single best edge to add is the EAST<->SOUTH
    crosstown link.
  - CBD_HUB: all radial metro lines meet at the CBD interchange -> very high
    betweenness (#1). Removing it sharply raises mean path length, BUT the metro
    ring lines provide partial redundancy so the network does not shatter.
  - MODE_GAP: at matched distance-to-CBD, metro-served neighborhoods get far
    shorter job-access times than bus-only ones.
  - JOBS: jobs concentrate in the CBD plus ONE secondary edge-city center
    (north-west). Peripheral bus-only areas have long job-access despite high
    population.

Run:
    python data/projects/transit-multimodal/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

# --- planted parameters -----------------------------------------------------
N_TARGET = 160              # target neighborhood count (final is close to this)
N_RADIAL = 6               # number of radial metro lines (spokes)
RING_RADIUS = 1.9          # radius of the inner metro ring line
OUTER_RING_RADIUS = 4.2    # radius of the partial outer metro ring
CITY_RADIUS = 6.0          # outer edge of the city
INCOME_PENALTY = 0.85      # how strongly low income thins out transit service
N_DESERTS = 9              # planted high-pop low-income transit deserts
N_OVERSERVED = 7           # planted low-pop wealthy over-served near-metro areas

# metro is fast & frequent; bus is slow & infrequent (per km factors)
METRO_TIME_PER_UNIT = 2.2   # min per layout-unit on metro
BUS_TIME_PER_UNIT = 5.6     # min per layout-unit on bus (much slower)
METRO_FREQ = (10, 24)       # trains/hr range
BUS_FREQ = (1.5, 12)        # buses/hr range (wide: low-income areas near 1.5)
METRO_CAP = (1200, 3000)    # riders/hr
BUS_CAP = (180, 700)        # riders/hr

# the two big districts that are NOT directly connected (the missing link)
WEDGE_EAST = "East"
WEDGE_SOUTH = "South"

DISTRICTS = ["CBD", "North", "NorthEast", "East", "SouthEast",
             "South", "SouthWest", "West", "NorthWest"]


def main() -> None:
    rng = np.random.default_rng(SEED)

    # ------------------------------------------------------------------ NODES
    # Place neighborhoods in concentric rings around a CBD at (0,0).
    # Ring 0 = CBD core; rings grow outward. Angle determines the district wedge.
    nodes_rows = []
    nid = 1

    def wedge_of(angle_deg: float) -> str:
        # 0 deg = East, increasing counter-clockwise.
        a = angle_deg % 360
        # 8 wedges of 45 deg, centered so "East"=0
        sectors = {
            0: "East", 45: "NorthEast", 90: "North", 135: "NorthWest",
            180: "West", 225: "SouthWest", 270: "South", 315: "SouthEast",
        }
        nearest = min(sectors, key=lambda s: min(abs(a - s), 360 - abs(a - s)))
        return sectors[nearest]

    # CBD core: a handful of central neighborhoods (the interchange district)
    n_cbd = 6
    for _ in range(n_cbd):
        r = rng.uniform(0.0, 0.55)
        th = rng.uniform(0, 2 * np.pi)
        x = r * np.cos(th)
        y = r * np.sin(th)
        nodes_rows.append({"px": x, "py": y, "district": "CBD"})

    # rings of neighborhoods outward
    ring_specs = [
        (1.0, 18),   # inner residential
        (1.9, 22),   # at inner ring radius
        (2.8, 26),
        (3.6, 28),
        (4.4, 28),
        (5.2, 24),
    ]
    for radius, count in ring_specs:
        for k in range(count):
            base_ang = (360.0 / count) * k
            ang = base_ang + rng.uniform(-8, 8)
            rr = radius + rng.uniform(-0.28, 0.28)
            th = np.deg2rad(ang)
            x = rr * np.cos(th)
            y = rr * np.sin(th)
            district = wedge_of(ang) if rr > 0.8 else "CBD"
            nodes_rows.append({"px": x, "py": y, "district": district})

    nodes = pd.DataFrame(nodes_rows)
    nodes = nodes.iloc[:N_TARGET].reset_index(drop=True)
    n = len(nodes)
    nodes["node_id"] = [f"N{i:03d}" for i in range(1, n + 1)]

    nodes["x"] = nodes["px"].round(3)
    nodes["y"] = nodes["py"].round(3)
    nodes["dist_cbd"] = np.hypot(nodes["px"], nodes["py"])

    # --- income: spatial gradient (rich near center & in the NW) + noise -----
    # wealth decreases outward overall, but NW wedge is affluent and parts of
    # the periphery vary; add noise so location does not perfectly reveal income.
    ang = np.rad2deg(np.arctan2(nodes["py"], nodes["px"])) % 360
    nw_bonus = np.exp(-((((ang - 135) + 180) % 360 - 180) ** 2) / (2 * 35 ** 2))
    base_income = (
        95000
        - 9000 * nodes["dist_cbd"]
        + 28000 * nw_bonus
        + rng.normal(0, 11000, n)
    )
    nodes["median_income"] = np.clip(base_income, 24000, 210000).round().astype(int)

    # --- population: outer rings hold more people; noise -------------------
    base_pop = (
        4500
        + 1300 * nodes["dist_cbd"]
        + rng.normal(0, 1500, n)
    )
    nodes["population"] = np.clip(base_pop, 800, 30000).round().astype(int)

    # --- jobs: concentrate in CBD + one secondary edge-city center (NW) -----
    # secondary center location
    sec_ang = np.deg2rad(135)
    sec_r = 3.4
    sec_x, sec_y = sec_r * np.cos(sec_ang), sec_r * np.sin(sec_ang)
    d_sec = np.hypot(nodes["px"] - sec_x, nodes["py"] - sec_y)
    jobs = (
        2200 * np.exp(-(nodes["dist_cbd"] ** 2) / (2 * 1.1 ** 2)) * 30   # CBD peak
        + 1400 * np.exp(-(d_sec ** 2) / (2 * 0.9 ** 2)) * 30            # edge city
        + 300
        + rng.normal(0, 600, n)
    )
    nodes["jobs"] = np.clip(jobs, 80, None).round().astype(int)

    pos = {r.node_id: (r.px, r.py) for r in nodes.itertuples()}
    ids = list(nodes.node_id)

    def dist(a: str, b: str) -> float:
        (ax, ay), (bx, by) = pos[a], pos[b]
        return float(np.hypot(ax - bx, ay - by))

    # ---------------------------------------------------- METRO LINE LAYOUT
    # Radial spokes: pick, for each of N_RADIAL angles, a chain of neighborhoods
    # marching outward (nearest to the ideal point at each radius step).
    metro_nodes: set[str] = set()
    metro_edges: list[dict] = []
    lines_rows: list[dict] = []

    # the CBD interchange node: the neighborhood closest to (0,0)
    cbd_hub = min(ids, key=lambda nd: nodes.loc[nodes.node_id == nd, "dist_cbd"].iloc[0])

    def nearest_free(target_xy, pool, used):
        cand = sorted(
            ((np.hypot(pos[p][0] - target_xy[0], pos[p][1] - target_xy[1]), p)
             for p in pool if p not in used),
            key=lambda t: (round(t[0], 6), t[1]),
        )
        return cand[0][1] if cand else None

    radial_angles = [(360.0 / N_RADIAL) * k for k in range(N_RADIAL)]
    radial_steps = [0.0, 1.0, 1.9, 2.8, 3.6, 4.4, 5.2]

    line_idx = 1
    for ang_deg in radial_angles:
        line_id = f"M{line_idx}"
        line_idx += 1
        th = np.deg2rad(ang_deg)
        chain = [cbd_hub]
        used_for_line = {cbd_hub}
        for step in radial_steps[1:]:
            tx, ty = step * np.cos(th), step * np.sin(th)
            # restrict to nodes roughly in this wedge & near this radius
            pool = [p for p in ids
                    if abs(nodes.loc[nodes.node_id == p, "dist_cbd"].iloc[0] - step) < 0.6]
            nd = nearest_free((tx, ty), pool, used_for_line)
            if nd is not None and nd != chain[-1]:
                chain.append(nd)
                used_for_line.add(nd)
        # build consecutive metro edges along the chain
        for a, b in zip(chain[:-1], chain[1:]):
            metro_nodes.update([a, b])
            metro_edges.append({"a": a, "b": b, "line": line_id})
        lines_rows.append({
            "line_id": line_id, "mode": "metro", "kind": "radial",
            "label": f"Metro Line {line_id}", "n_stations": len(chain),
        })

    # inner ring metro line: order the neighborhoods nearest RING_RADIUS by angle
    def ring_chain(radius: str, tol: float):
        ring_pool = [p for p in ids
                     if abs(nodes.loc[nodes.node_id == p, "dist_cbd"].iloc[0] - radius) < tol]
        ring_pool = sorted(
            ring_pool,
            key=lambda p: np.rad2deg(np.arctan2(pos[p][1], pos[p][0])) % 360,
        )
        return ring_pool

    inner_ring = ring_chain(RING_RADIUS, 0.5)
    for a, b in zip(inner_ring, inner_ring[1:] + inner_ring[:1]):  # close the loop
        metro_nodes.update([a, b])
        metro_edges.append({"a": a, "b": b, "line": "Ring"})
    lines_rows.append({
        "line_id": "Ring", "mode": "metro", "kind": "inner_ring",
        "label": "Inner Ring Line", "n_stations": len(inner_ring),
    })

    # PARTIAL outer ring metro line: an arc covering the WEST/NORTH side only,
    # deliberately leaving a GAP on the EAST<->SOUTH side (relevant to the
    # missing link, and giving partial-but-not-full ring redundancy).
    outer_ring_all = ring_chain(OUTER_RING_RADIUS, 0.7)
    # keep only nodes whose angle is in [60, 240] deg (covers N, NW, W, SW),
    # leaving East (0/315) and South (270) unconnected by the outer ring.
    def angle_of(p):
        return np.rad2deg(np.arctan2(pos[p][1], pos[p][0])) % 360
    outer_arc = [p for p in outer_ring_all if 60 <= angle_of(p) <= 240]
    outer_arc = sorted(outer_arc, key=angle_of)
    for a, b in zip(outer_arc[:-1], outer_arc[1:]):  # an OPEN arc (not closed)
        metro_nodes.update([a, b])
        metro_edges.append({"a": a, "b": b, "line": "OuterArc"})
    lines_rows.append({
        "line_id": "OuterArc", "mode": "metro", "kind": "outer_ring_partial",
        "label": "Outer Ring (partial)", "n_stations": len(outer_arc),
    })

    nodes["has_metro"] = nodes["node_id"].isin(metro_nodes).astype(int)

    # ----------------------------------------------- TRANSIT DESERTS / EQUITY
    # Plant high-pop, low-income, peripheral deserts: force metro=0 and mark them
    # for thin bus service. Choose peripheral (dist_cbd large) low-income nodes
    # that are currently bus-territory, biasing toward high population.
    periph = nodes[(nodes.dist_cbd > 3.0) & (nodes.has_metro == 0)].copy()
    # score: want HIGH pop and LOW income -> rank
    periph["desert_score"] = (
        (periph.population - periph.population.mean()) / periph.population.std()
        - (periph.median_income - periph.median_income.mean()) / periph.median_income.std()
    )
    desert_ids = list(
        periph.sort_values(["desert_score", "node_id"], ascending=[False, True])
        .head(N_DESERTS).node_id
    )
    nodes["is_desert_param"] = nodes["node_id"].isin(desert_ids).astype(int)
    # push deserts to be genuinely high-pop & low-income (strengthen the signal)
    for did in desert_ids:
        i = nodes.index[nodes.node_id == did][0]
        nodes.at[i, "population"] = int(min(30000, nodes.at[i, "population"] + 8000))
        nodes.at[i, "median_income"] = int(max(24000, nodes.at[i, "median_income"] - 14000))

    # Over-served wealthy low-pop near-metro nodes (for the equity contrast)
    near_metro = nodes[(nodes.has_metro == 1) & (nodes.dist_cbd > 1.2)].copy()
    near_metro["over_score"] = (
        (near_metro.median_income - near_metro.median_income.mean()) / near_metro.median_income.std()
        - (near_metro.population - near_metro.population.mean()) / near_metro.population.std()
    )
    overserved_ids = list(
        near_metro.sort_values(["over_score", "node_id"], ascending=[False, True])
        .head(N_OVERSERVED).node_id
    )
    nodes["is_overserved_param"] = nodes["node_id"].isin(overserved_ids).astype(int)
    for oid in overserved_ids:
        i = nodes.index[nodes.node_id == oid][0]
        nodes.at[i, "median_income"] = int(min(210000, nodes.at[i, "median_income"] + 18000))
        nodes.at[i, "population"] = int(max(800, nodes.at[i, "population"] - 2500))

    # ------------------------------------------------------------------- BUS
    # Dense mesh: connect spatially-adjacent neighborhoods (k nearest), with
    # service level scaled by income (low-income -> fewer buses) and deserts thin.
    bus_edges: list[dict] = []
    bus_keys: set[tuple[str, str]] = set()
    income_arr = nodes.set_index("node_id")["median_income"]
    inc_min, inc_max = income_arr.min(), income_arr.max()

    def inc_norm(p):
        return float((income_arr[p] - inc_min) / (inc_max - inc_min))

    desert_set = set(desert_ids)

    def k_nearest(node, k, pool=None):
        pool = pool or ids
        cand = sorted(
            ((dist(node, p), p) for p in pool if p != node),
            key=lambda t: (round(t[0], 6), t[1]),
        )
        return [p for _, p in cand[:k]]

    bus_route_idx = 1

    def add_bus(a, b, route_id):
        if a == b:
            return
        key = (a, b) if a < b else (b, a)
        if key in bus_keys:
            return
        bus_keys.add(key)
        d = dist(a, b)
        # service level: richer endpoints get more frequent service; deserts thin
        avg_inc = (inc_norm(a) + inc_norm(b)) / 2
        desert_factor = 0.40 if (a in desert_set or b in desert_set) else 1.0
        freq = BUS_FREQ[0] + (BUS_FREQ[1] - BUS_FREQ[0]) * (
            INCOME_PENALTY * avg_inc + (1 - INCOME_PENALTY) * rng.random()
        )
        freq = float(np.clip(freq * desert_factor, 1.5, BUS_FREQ[1]))
        cap = int(np.clip(
            rng.integers(*BUS_CAP) * (0.6 + 0.8 * avg_inc) * desert_factor,
            120, BUS_CAP[1]))
        # low-income routes are also slightly slower (older, more circuitous)
        slow = 1.0 + 0.30 * (1 - avg_inc) + (0.20 if desert_factor < 1 else 0.0)
        ttime = d * BUS_TIME_PER_UNIT * slow * rng.uniform(0.95, 1.20) + 1.5
        bus_edges.append({
            "a": key[0], "b": key[1], "line": route_id,
            "travel_time_min": round(ttime, 1),
            "frequency_per_hr": round(freq, 1),
            "capacity": cap,
        })

    # local mesh: each neighborhood to its nearest neighbors. Lower-income areas
    # get FEWER bus links (k smaller) -> thinner coverage, independent of pop.
    for p in ids:
        kbase = 4
        # income reduces connectivity: poorest get k=2, richest k=5
        k = int(round(2 + 3 * inc_norm(p)))
        if p in desert_set:
            k = 2
        k = max(2, min(5, k))
        for q in k_nearest(p, max(kbase, k))[:k]:
            add_bus(p, q, f"B{bus_route_idx:03d}")
            bus_route_idx += 1

    # FEEDER routes: every non-metro neighborhood gets a bus to its nearest metro
    # station (brings outer areas to the rail) -- but deserts get a LONG feeder
    # (their nearest metro is far) which we keep, modeling poor access.
    metro_list = sorted(metro_nodes)
    for p in ids:
        if p in metro_nodes:
            continue
        nearest_metro = min(metro_list, key=lambda m: (round(dist(p, m), 6), m))
        add_bus(p, nearest_metro, f"F{bus_route_idx:03d}")
        bus_route_idx += 1

    # ---- ensure the MISSING LINK: isolate the East wedge into a spoke-only ---
    # peninsula. We cut ALL bus links from East-wedge nodes to their two
    # neighbouring wedges (NorthEast and SouthEast), and keep the inner-ring and
    # outer-arc gaps on the East/South side. The result: every trip from East to
    # the South side of the city must detour inward down the East radial metro
    # spoke, through the CBD interchange, and back out -- a long way round.
    # Adding ONE crosstown edge (East <-> SouthEast/South) collapses that detour.
    dist_map = nodes.set_index("node_id")["dist_cbd"]
    district_map = nodes.set_index("node_id")["district"]
    ISOLATE = WEDGE_EAST
    NEIGHBORS = {"NorthEast", "SouthEast"}

    def crosses_cut(p, q):
        dp, dq = district_map[p], district_map[q]
        return (dp == ISOLATE and dq in NEIGHBORS) or (dq == ISOLATE and dp in NEIGHBORS)

    bus_edges = [e for e in bus_edges if not crosses_cut(e["a"], e["b"])]
    bus_keys = {(e["a"], e["b"]) for e in bus_edges}
    # the inner-ring metro must also not bridge East to its neighbours
    metro_edges = [e for e in metro_edges if not crosses_cut(e["a"], e["b"])]

    # repair: cutting cross-wedge links can orphan an East node. Reconnect any
    # now-isolated East node to its nearest East-wedge OR CBD neighbour (never
    # across the cut), so East stays a connected spoke-only peninsula.
    incident = set()
    for e in bus_edges:
        incident.update([e["a"], e["b"]])
    incident.update(metro_nodes)
    east_ids = [p for p in ids if district_map[p] == ISOLATE]
    inward_pool = [p for p in ids if district_map[p] in (ISOLATE, "CBD")]
    for p in east_ids:
        if p in incident:
            continue
        pool = [q for q in inward_pool if q != p]
        parent = min(pool, key=lambda q: (round(dist(p, q), 6), q))
        add_bus(p, parent, f"R{bus_route_idx:03d}")
        bus_route_idx += 1
        incident.add(p)
    bus_keys = {(e["a"], e["b"]) for e in bus_edges}

    # ----------------------------------------- BUILD METRO EDGE ATTRIBUTES
    metro_rows = []
    for e in metro_edges:
        a, b = e["a"], e["b"]
        d = dist(a, b)
        freq = float(rng.integers(*METRO_FREQ))
        cap = int(rng.integers(*METRO_CAP))
        ttime = d * METRO_TIME_PER_UNIT * rng.uniform(0.9, 1.1) + 0.8
        metro_rows.append({
            "from_id": a, "to_id": b, "mode": "metro", "line": e["line"],
            "travel_time_min": round(ttime, 1),
            "frequency_per_hr": round(freq, 1),
            "capacity": cap,
        })

    bus_rows = []
    for e in bus_edges:
        bus_rows.append({
            "from_id": e["a"], "to_id": e["b"], "mode": "bus", "line": e["line"],
            "travel_time_min": e["travel_time_min"],
            "frequency_per_hr": e["frequency_per_hr"],
            "capacity": e["capacity"],
        })

    edges = pd.DataFrame(metro_rows + bus_rows)

    # bus route lines lookup (collapse the many tiny route ids into the table)
    bus_line_ids = sorted({e["line"] for e in bus_edges})
    for lid in bus_line_ids:
        cnt = sum(1 for e in bus_edges if e["line"] == lid)
        lines_rows.append({
            "line_id": lid, "mode": "bus",
            "kind": "feeder" if lid.startswith("F") else "local",
            "label": f"Bus Route {lid}", "n_stations": cnt + 1,
        })
    lines = pd.DataFrame(lines_rows)

    # ------------------------------------------------------------- FINALIZE
    nodes["label"] = nodes["district"] + " " + nodes["node_id"].str[1:]
    out_nodes = nodes[[
        "node_id", "label", "district", "x", "y",
        "population", "median_income", "jobs", "has_metro",
    ]].copy()

    out_nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)
    lines.to_csv(HERE / "lines.csv", index=False)

    n_metro = int((edges["mode"] == "metro").sum())
    n_bus = int((edges["mode"] == "bus").sum())
    print(f"transit-multimodal: {len(out_nodes)} neighborhoods, "
          f"{len(edges)} edges ({n_metro} metro + {n_bus} bus), "
          f"{len(lines)} lines, {out_nodes.has_metro.sum()} metro-served nodes.")


if __name__ == "__main__":
    main()
```

---

## `data/projects/transit-multimodal/load.R`

```r
#' @name load.R
#' @title Load the `transit-multimodal` project network (R)
#' @description
#'
#' Reads the CSVs in this folder and builds an undirected, weighted, multimodal
#' igraph object: neighborhoods are nodes; edges are transit links in two modes
#' (`metro` and `bus`). The same neighborhood pair can carry both a metro and a
#' bus link, so the graph is a multiplex with parallel edges. The edge weight is
#' `capacity` (riders/hr). Run it straight (`Rscript load.R`) for a quick
#' summary, or `source()` it and call `load_transit()` in your own script.
#' `load_lines()` returns the line/route lookup table.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "transit-multimodal")

#' Load the node table (one row per neighborhood).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per transit link: metro or bus).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Load the line/route lookup table (join onto edges by `line`).
load_lines <- function() {
  read.csv(file.path(.dir(), "lines.csv"), stringsAsFactors = FALSE)
}

#' Build the undirected, weighted, multimodal transit graph.
#'
#' Edges are weighted by `capacity` (riders/hr). The `mode` edge attribute is
#' either `"metro"` or `"bus"`; the same neighborhood pair may appear as both
#' (parallel edges). Filter edges to analyze a single mode, or collapse with
#' `simplify(g, edge.attr.comb = list(weight = "sum"))`.
load_transit <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = FALSE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$capacity
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n\U0001F687 transit-multimodal (R)\n")
  cat("   Undirected multimodal transit; neighborhoods linked by metro & bus.\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_transit(nodes, edges)

  cat(sprintf("✅ Loaded %d neighborhoods and %d edges (%d metro + %d bus).\n",
              nrow(nodes), nrow(edges),
              sum(edges$mode == "metro"), sum(edges$mode == "bus")))
  cat(sprintf("\U0001F517 Directed: %s | metro-served neighborhoods: %d | total seat capacity: %s riders/hr\n",
              is_directed(g), sum(nodes$has_metro),
              format(sum(edges$capacity), big.mark = ",")))
  cat("\U0001F389 Graph ready. Object `g` is an undirected, weighted, multimodal igraph.\n")
}
```

---

## `data/projects/transit-multimodal/load.py`

```python
"""Load the `transit-multimodal` project network (Python).

Reads the CSVs in this folder and builds an undirected, weighted, multimodal
python-igraph object: neighborhoods are nodes; edges are transit links in two
modes (``metro`` and ``bus``). Because the same neighborhood pair can carry both
a metro and a bus link, the graph is a multiplex with parallel edges. The edge
weight is ``capacity`` (riders/hr). Run it straight (``python load.py``) for a
quick summary, or import ``load_transit()`` / ``load_lines()`` into your script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per neighborhood."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per transit link (metro or bus)."""
    return pd.read_csv(HERE / "edges.csv")


def load_lines() -> pd.DataFrame:
    """Line/route lookup table (join onto edges by ``line``)."""
    return pd.read_csv(HERE / "lines.csv")


def load_transit(nodes: pd.DataFrame | None = None,
                 edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the undirected, weighted, multimodal graph (weight = ``capacity``).

    The same neighborhood pair may appear twice (a metro edge AND a bus edge) ->
    parallel edges. The ``mode`` edge attribute distinguishes them. To analyze a
    single mode, filter edges first; to collapse to one link per pair, use
    ``g.simplify(combine_edges={'weight': 'sum'})``.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=False, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["capacity"]
    return g


if __name__ == "__main__":
    print("\n🚇 transit-multimodal (Python)")
    print("   Undirected multimodal transit; neighborhoods linked by metro & bus.\n")

    nodes = load_nodes()
    edges = load_edges()
    g = load_transit(nodes, edges)

    modes = edges["mode"].value_counts()
    print(f"✅ Loaded {len(nodes)} neighborhoods and {len(edges)} edges "
          f"({modes.get('metro', 0)} metro + {modes.get('bus', 0)} bus).")
    print(f"🔗 Directed: {g.is_directed()} | metro-served neighborhoods: "
          f"{int(nodes['has_metro'].sum())} | total seat capacity: "
          f"{edges['capacity'].sum():,} riders/hr")
    print("🎉 Graph ready. Object `g` is an undirected, weighted, multimodal igraph.")
```

---

## `data/projects/uber-manhattan/README.md`

# uber-manhattan

*One day of ride-matching in downtown Manhattan: which drivers got matched to
which riders, where they were picked up and dropped off, and what each ride cost.*

![Preview of the uber-manhattan network](thumb.png)

## At a glance

| | |
|---|---|
| **Direction** | Undirected matches (a ride links a driver and a rider) |
| **Weights** | Weighted (`fare`, `tip`, `wait_min`, `surge_mult`; also count of repeat rides) |
| **Modality** | Bipartite — two node kinds (`driver`, `rider`); `zones.csv` is a lookup table |
| **Temporal** | Yes — each ride has an `hour` (0–23) |
| **Nodes** | 370 (120 drivers + 250 riders) |
| **Edges** | 3,000 rides (driver–rider pairs may repeat → parallel edges) |
| **Files** | `nodes.csv`, `edges.csv`, `zones.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

A bipartite **matching** network: one side is drivers, the other is riders, and an
edge is a completed ride. Because a rider can ride with the same driver more than
once, repeated pairs appear as parallel edges. Every ride records where it started
and ended (zones on a downtown-Manhattan grid), the hour of day, how long the rider
waited, the trip distance, the fare, the surge multiplier in effect, and the tip.
The `zones.csv` lookup gives each zone a neighborhood, grid position, median income,
and a nightlife flag.

This is the natural home for **bipartite projection**, **matching/assignment**, and
**inequality** questions. Some things worth investigating:

- Project the bipartite graph onto drivers (two drivers linked if they shared a
  rider) or onto zones. What communities fall out, and what do they mean?
- Is service evenly distributed across the city? Look at wait times and match rates
  by pickup zone — is what you see explained by demand, or by *something about the
  zones*?
- Earnings are never perfectly equal, but how unequal are they here, and is the
  inequality random or structured? Who captures the most valuable trips?
- Surge pricing moves in space and time. Where and when does it spike, and does it
  change rider behavior (e.g., tipping)?
- Are there rider–driver pairs that ride together far more than chance would
  predict? What kind of trips are those?

> **Note.** The findings are deliberately undocumented. "Busy zones have more rides"
> is the starting point, not an answer. Look for the structure underneath.

## `nodes.csv`

One row per driver or rider. Driver-only columns are blank for riders and vice
versa.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique key. `D###` driver, `R###` rider. Referenced by edges. | character | `D015`, `R012` |
| `kind` | Node kind | Which side of the bipartite graph. | character | `driver`, `rider` |
| `home_zone` | Home zone | Zone ID the actor is based in (joins to `zones.csv`). | character | `Z22`, `Z04` |
| `vehicle_type` | Vehicle type | Driver's vehicle class (blank for riders). | character | `uberx`, `xl`, `black` |
| `tenure_months` | Tenure (months) | How long the driver has been active (blank for riders). | integer | `75`, `13` |
| `rating` | Star rating | Average rating, 1–5 (present for both sides). | double | `5.0`, `4.9` |
| `income_bracket` | Income bracket | Rider's income band (blank for drivers). | character | `low`, `mid`, `high` |

## `edges.csv`

One row per ride. Undirected match between `driver_id` and `rider_id`.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `driver_id` | Driver ID | The driver on this ride (joins to `nodes.csv`). | character | `D015` |
| `rider_id` | Rider ID | The rider on this ride (joins to `nodes.csv`). | character | `R012` |
| `hour` | Hour of day | Local start hour, 0–23. | integer | `8`, `18`, `22` |
| `pickup_zone` | Pickup zone | Zone the ride began in (joins to `zones.csv`; `ZJFK` = airport). | character | `Z23`, `ZJFK` |
| `dropoff_zone` | Dropoff zone | Zone the ride ended in. | character | `Z04`, `ZJFK` |
| `wait_min` | Wait (minutes) | Minutes the rider waited for pickup. | double | `4.7`, `8.9` |
| `distance_km` | Distance | Trip distance, kilometers. | double | `6.92`, `21.4` |
| `fare` | Fare | Trip fare in USD (the primary edge weight). | double | `16.03`, `48.20` |
| `surge_mult` | Surge multiplier | Dynamic-pricing multiplier in effect (1.0 = no surge). | double | `1.0`, `1.9` |
| `tip` | Tip | Tip in USD. | double | `4.61`, `0.0` |

## `zones.csv`

Lookup table for the downtown-Manhattan zone grid (one row per zone). Not a node
list — join it onto the `home_zone` / `pickup_zone` / `dropoff_zone` fields.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `zone_id` | Zone ID | Unique zone key. `ZJFK` is the airport pseudo-zone. | character | `Z01`, `ZJFK` |
| `name` | Zone name | Short label. | character | `FiDi`, `SoHo` |
| `neighborhood` | Neighborhood | Full neighborhood name. | character | `Financial District`, `SoHo` |
| `avenue` | Avenue index | West→east grid column. | integer | `3`, `1` |
| `street` | Street index | South→north grid row. | integer | `1`, `8` |
| `x` | X coordinate | Map x (≈ avenue, jittered). | double | `2.88`, `0.77` |
| `y` | Y coordinate | Map y (≈ street, jittered). | double | `1.09`, `0.84` |
| `median_income` | Median household income | Zone median income, USD (blank for the airport). | integer | `156437`, `41220` |
| `nightlife` | Nightlife flag | 1 if a nightlife district, else 0. | integer | `0`, `1` |

## Load it

```bash
Rscript data/projects/uber-manhattan/load.R     # R    (igraph, bipartite)
python  data/projects/uber-manhattan/load.py     # Python (python-igraph, bipartite)
```

Both build a bipartite, weighted `igraph` graph (vertex `type`: rider = TRUE) and
print a one-screen summary. In the
[R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**uber-manhattan** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/uber-manhattan>

---

## `data/projects/uber-manhattan/_generate.py`

```python
"""Generate the `uber-manhattan` project network (deterministic).

A bipartite ride-matching network for one day in downtown Manhattan:
  - ~120 drivers   (kind = "driver")
  - ~250 riders    (kind = "rider")   -> ~370 nodes total
Edges are individual rides (driver served rider), so the same driver-rider pair
can appear several times (parallel edges = repeat customers). Each ride carries
pickup/dropoff zone, hour, wait time, distance, fare, surge multiplier, and tip.
A companion `zones.csv` is the lookup table for the Manhattan zone grid.

Design parameters (the only record of the planted structure):
  - DESERT_PENALTY: pickups in low-income zones wait longer and are served less
    (a spatial service gap that is NOT explained by demand).
  - PRO_DRIVERS: a small clique of high-tenure drivers monopolize airport runs
    and the high-fare long trips -> extreme earnings concentration.
  - SURGE: evening surge concentrates in nightlife zones; tips fall as surge
    rises (riders tip less when they feel gouged).
  - LOYAL_PAIRS: a set of commuter rider-driver pairs ride together repeatedly
    in the morning peak (a planted bipartite community).

Run:
    python data/projects/uber-manhattan/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

N_DRIVERS = 120
N_RIDERS = 250
N_RIDES = 3000

# --- planted parameters -----------------------------------------------------
N_PRO = 10            # pro drivers who corner the airport / long-haul market
N_LOYAL_PAIRS = 28    # commuter rider-driver pairs that repeat
DESERT_PENALTY = 6.5  # extra wait-minutes in the lowest-income pickup zones
NIGHTLIFE = {"Lower East Side", "East Village", "West Village",
             "Meatpacking", "Nolita"}

# downtown-Manhattan zone grid: (name, neighborhood, avenue col, street row,
# income tier 0..1). Income is a *tier*; dollars get jittered below.
ZONE_DEFS = [
    ("FiDi",          "Financial District", 3, 1, 0.85),
    ("Battery Park",  "Battery Park City",  1, 1, 0.90),
    ("Tribeca",       "Tribeca",            2, 2, 0.97),
    ("Civic Center",  "Civic Center",       4, 2, 0.55),
    ("Chinatown",     "Chinatown",          5, 3, 0.28),
    ("Two Bridges",   "Two Bridges",        6, 2, 0.22),
    ("Lower East Side", "Lower East Side",  6, 4, 0.30),
    ("SoHo",          "SoHo",               3, 4, 0.92),
    ("Little Italy",  "Little Italy",       4, 4, 0.60),
    ("Nolita",        "Nolita",             5, 4, 0.78),
    ("Hudson Square", "Hudson Square",      2, 5, 0.80),
    ("Greenwich Vlg", "Greenwich Village",  3, 6, 0.88),
    ("West Village",  "West Village",       2, 6, 0.95),
    ("East Village",  "East Village",       6, 6, 0.45),
    ("NoHo",          "NoHo",               4, 6, 0.82),
    ("Bowery",        "Bowery",             5, 5, 0.50),
    ("Meatpacking",   "Meatpacking",        1, 7, 0.93),
    ("Chelsea",       "Chelsea",            2, 8, 0.84),
    ("Flatiron",      "Flatiron",           4, 8, 0.86),
    ("Union Square",  "Union Square",       4, 7, 0.80),
    ("Gramercy",      "Gramercy",           5, 8, 0.83),
    ("Kips Bay",      "Kips Bay",           6, 8, 0.62),
    ("Murray Hill",   "Murray Hill",        6, 9, 0.74),
    ("Stuy Town",     "Stuyvesant Town",    7, 7, 0.58),
]


def main() -> None:
    rng = np.random.default_rng(SEED)

    # ----- zones -----------------------------------------------------------
    zrows = []
    for i, (name, nbhd, ave, st, tier) in enumerate(ZONE_DEFS, start=1):
        income = int(np.clip(35000 + tier * 140000 + rng.normal(0, 8000), 22000, 220000))
        zrows.append({
            "zone_id": f"Z{i:02d}", "name": name, "neighborhood": nbhd,
            "avenue": ave, "street": st,
            "x": round(ave * 1.0 + rng.normal(0, 0.12), 2),
            "y": round(st * 1.0 + rng.normal(0, 0.12), 2),
            "median_income": income,
            "nightlife": int(nbhd in NIGHTLIFE),
        })
    # airport pseudo-zone, far to the southeast
    zrows.append({"zone_id": "ZJFK", "name": "JFK Airport", "neighborhood": "JFK Airport",
                  "avenue": 12, "street": -6, "x": 14.0, "y": -6.0,
                  "median_income": pd.NA, "nightlife": 0})
    zones = pd.DataFrame(zrows)
    zpos = {r.zone_id: (r.x, r.y) for r in zones.itertuples()}
    z_ids = [z for z in zones.zone_id if z != "ZJFK"]
    z_income = {r.zone_id: r.median_income for r in zones.itertuples()}
    inc_vals = np.array([z_income[z] for z in z_ids], dtype=float)
    inc_norm = {z: (z_income[z] - inc_vals.min()) / (inc_vals.max() - inc_vals.min())
                for z in z_ids}
    nightlife_z = set(zones.loc[zones.nightlife == 1, "zone_id"])

    # ----- drivers ---------------------------------------------------------
    veh = rng.choice(["uberx", "xl", "black"], size=N_DRIVERS, p=[0.72, 0.18, 0.10])
    tenure = rng.integers(1, 84, N_DRIVERS)
    # pros = the 10 longest-tenured; bump them to premium vehicles.
    pro_idx = np.argsort(-tenure)[:N_PRO]
    for p in pro_idx:
        veh[p] = "black" if rng.random() < 0.6 else "xl"
    drivers = pd.DataFrame({
        "node_id": [f"D{i:03d}" for i in range(1, N_DRIVERS + 1)],
        "kind": "driver",
        "home_zone": rng.choice(z_ids, N_DRIVERS),
        "vehicle_type": veh,
        "tenure_months": tenure,
        "rating": np.round(np.clip(rng.normal(4.85, 0.12, N_DRIVERS), 4.2, 5.0), 2),
        "income_bracket": pd.NA,
    })
    pro_ids = set(drivers.node_id.iloc[pro_idx])

    # ----- riders ----------------------------------------------------------
    # riders live disproportionately in residential (mid/low income) zones
    res_w = np.array([1.4 - 0.5 * inc_norm[z] for z in z_ids]); res_w /= res_w.sum()
    rider_home = rng.choice(z_ids, N_RIDERS, p=res_w)
    rbrack = []
    for z in rider_home:
        pr = inc_norm[z]
        w = np.array([max(0.05, 0.6 - 0.5 * pr), 0.4, max(0.05, 0.05 + 0.5 * pr)])
        rbrack.append(rng.choice(["low", "mid", "high"], p=w / w.sum()))
    riders = pd.DataFrame({
        "node_id": [f"R{i:03d}" for i in range(1, N_RIDERS + 1)],
        "kind": "rider",
        "home_zone": rider_home,
        "vehicle_type": pd.NA,
        "tenure_months": pd.NA,
        "rating": np.round(np.clip(rng.normal(4.9, 0.1, N_RIDERS), 4.3, 5.0), 2),
        "income_bracket": rbrack,
    })
    rider_ids = list(riders.node_id)
    rider_home_map = dict(zip(riders.node_id, riders.home_zone))
    rider_brack_map = dict(zip(riders.node_id, riders.income_bracket))

    nodes = pd.concat([drivers, riders], ignore_index=True)

    # planted loyal commuter pairs
    loyal = list(zip(rng.choice(rider_ids, N_LOYAL_PAIRS, replace=False),
                     rng.choice(list(drivers.node_id), N_LOYAL_PAIRS, replace=False)))

    def dist(a, b):
        (ax, ay), (bx, by) = zpos[a], zpos[b]
        return float(np.hypot(ax - bx, ay - by))

    # ----- rides -----------------------------------------------------------
    rows = []
    # each commuter pair rides together repeatedly across the (implied) week:
    # 3 morning commutes out + 3 evening commutes home.
    loyal_cycles = 3
    n_loyal_rides = N_LOYAL_PAIRS * 2 * loyal_cycles
    for rid, did in loyal:
        work = rng.choice(z_ids)               # the rider's steady workplace zone
        for _ in range(loyal_cycles):
            for hour in (8, 18):               # morning out, evening back
                pu = rider_home_map[rid] if hour == 8 else work
                do = work if hour == 8 else rider_home_map[rid]
                rows.append(_ride(rng, did, rid, hour, pu, do, dist, inc_norm,
                                  nightlife_z, pro_ids, rider_brack_map, DESERT_PENALTY))

    for _ in range(N_RIDES - n_loyal_rides):
        rid = rng.choice(rider_ids)
        roll = rng.random()
        if roll < 0.08:                        # airport run
            pu = rng.choice(z_ids); do = "ZJFK"
            hour = int(rng.choice([5, 6, 7, 15, 16, 17]))
            did = rng.choice(sorted(pro_ids)) if rng.random() < 0.8 else rng.choice(list(drivers.node_id))
        elif roll < 0.34:                      # nightlife
            pu = rng.choice(z_ids)
            do = rng.choice(sorted(nightlife_z))
            hour = int(rng.choice([19, 20, 21, 22, 23, 0, 1, 2]))
            did = rng.choice(list(drivers.node_id))
        else:                                  # ordinary daytime
            pu = rider_home_map[rid] if rng.random() < 0.5 else rng.choice(z_ids)
            do = rng.choice(z_ids)
            hour = int(rng.integers(7, 20))
            # pros skip low-income pickups; regulars take them (and wait longer)
            if inc_norm[pu] < 0.4 and rng.random() < 0.85:
                pool = [d for d in drivers.node_id if d not in pro_ids]
                did = rng.choice(pool)
            else:
                did = rng.choice(list(drivers.node_id))
        rows.append(_ride(rng, did, rid, hour, pu, do, dist, inc_norm,
                          nightlife_z, pro_ids, rider_brack_map, DESERT_PENALTY))

    edges = pd.DataFrame(rows)

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)
    zones.to_csv(HERE / "zones.csv", index=False)
    print(f"uber-manhattan: {len(nodes)} nodes ({N_DRIVERS} drivers + {N_RIDERS} riders), "
          f"{len(edges)} rides, {len(zones)} zones.")


def _ride(rng, did, rid, hour, pu, do, dist, inc_norm, nightlife_z, pro_ids,
          rider_brack_map, desert_penalty):
    d_km = dist(pu, do) * 0.9 + 0.4
    evening = hour >= 19 or hour <= 2
    surge = 1.0
    if pu in nightlife_z and evening:
        surge = round(float(np.clip(rng.normal(1.9, 0.4), 1.1, 3.2)), 2)
    elif evening:
        surge = round(float(np.clip(rng.normal(1.25, 0.2), 1.0, 2.0)), 2)
    elif do == "ZJFK":
        surge = round(float(np.clip(rng.normal(1.15, 0.15), 1.0, 1.8)), 2)

    desert = desert_penalty * (1 - inc_norm.get(pu, 0.6)) if pu != "ZJFK" else 0.0
    wait = float(np.clip(rng.normal(3.5, 1.0) + desert + (2.0 if evening else 0), 0.5, 28))

    base = 2.6 + 1.85 * d_km * surge + (9.0 if do == "ZJFK" else 0.0)
    fare = round(float(base + rng.normal(0, 1.2)), 2)
    rb = rider_brack_map.get(rid, "mid")
    rb_norm = {"low": 0.0, "mid": 0.5, "high": 1.0}[rb]
    tip = round(float(max(0.0, fare * (0.16 + 0.10 * rb_norm - 0.09 * (surge - 1))
                          + rng.normal(0, 0.6))), 2)
    return {
        "driver_id": did, "rider_id": rid, "hour": hour,
        "pickup_zone": pu, "dropoff_zone": do,
        "wait_min": round(wait, 1), "distance_km": round(d_km, 2),
        "fare": fare, "surge_mult": surge, "tip": tip,
    }


if __name__ == "__main__":
    main()
```

---

## `data/projects/uber-manhattan/load.R`

```r
#' @name load.R
#' @title Load the `uber-manhattan` project network (R)
#' @description
#'
#' Reads the CSVs in this folder and builds a bipartite, weighted igraph object:
#' drivers on one side, riders on the other, edges are rides (weighted by fare).
#' Run it straight (`Rscript load.R`) for a quick summary, or `source()` it and
#' call `load_uber()` in your own script. `load_zones()` returns the zone lookup.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "uber-manhattan")

#' Load the node table (drivers + riders).
load_nodes <- function() read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)

#' Load the edge table (one row per ride).
load_edges <- function() read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)

#' Load the zone lookup table (join onto pickup/dropoff/home zones).
load_zones <- function() read.csv(file.path(.dir(), "zones.csv"), stringsAsFactors = FALSE)

#' Build the bipartite, weighted graph.
#'
#' Edges are weighted by `fare`. The vertex attribute `type` is the igraph
#' bipartite flag: TRUE for riders, FALSE for drivers. Repeat rider-driver pairs
#' stay as parallel edges; collapse with `simplify(g, edge.attr.comb = "sum")`
#' if you want a single weighted edge per pair.
load_uber <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = FALSE, vertices = nodes)
  igraph::V(g)$type <- igraph::V(g)$kind == "rider"
  igraph::E(g)$weight <- igraph::E(g)$fare
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n🚕 uber-manhattan (R)\n")
  cat("   Bipartite drivers <-> riders; edges are rides weighted by fare.\n\n")

  nodes <- load_nodes(); edges <- load_edges(); g <- load_uber(nodes, edges)

  cat(sprintf("✅ Loaded %d nodes (%d drivers + %d riders) and %d rides.\n",
              nrow(nodes), sum(nodes$kind == "driver"),
              sum(nodes$kind == "rider"), nrow(edges)))
  cat(sprintf("🔗 Bipartite: %s | total fares: $%s | total tips: $%s\n",
              igraph::is_bipartite(g),
              format(round(sum(edges$fare)), big.mark = ","),
              format(round(sum(edges$tip)), big.mark = ",")))
  cat("🎉 Graph ready. `g` is bipartite (V(g)$type: rider = TRUE), weighted by fare.\n")
}
```

---

## `data/projects/uber-manhattan/load.py`

```python
"""Load the `uber-manhattan` project network (Python).

Reads the CSVs in this folder and builds a bipartite, weighted python-igraph
object: drivers on one side, riders on the other, edges are rides (weighted by
fare). Run it straight (``python load.py``) for a quick summary, or import
``load_uber()`` / ``load_zones()`` into your own script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: drivers + riders."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per ride."""
    return pd.read_csv(HERE / "edges.csv")


def load_zones() -> pd.DataFrame:
    """Zone lookup table (join onto pickup/dropoff/home zones)."""
    return pd.read_csv(HERE / "zones.csv")


def load_uber(nodes: pd.DataFrame | None = None,
              edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the bipartite, weighted graph (edge weight = ``fare``).

    The vertex attribute ``type`` is the bipartite flag: True for riders, False
    for drivers. Repeat rider-driver pairs stay as parallel edges; collapse with
    ``g.simplify(combine_edges={'weight': 'sum'})`` for one edge per pair.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=False, vertices=nodes, use_vids=False)
    g.vs["type"] = [k == "rider" for k in g.vs["kind"]]
    g.es["weight"] = g.es["fare"]
    return g


if __name__ == "__main__":
    print("\n🚕 uber-manhattan (Python)")
    print("   Bipartite drivers <-> riders; edges are rides weighted by fare.\n")

    nodes = load_nodes(); edges = load_edges(); g = load_uber(nodes, edges)
    kinds = nodes["kind"].value_counts()
    print(f"✅ Loaded {len(nodes)} nodes ({kinds.get('driver',0)} drivers + "
          f"{kinds.get('rider',0)} riders) and {len(edges)} rides.")
    print(f"🔗 Bipartite: {g.is_bipartite()} | total fares: "
          f"${edges['fare'].sum():,.0f} | total tips: ${edges['tip'].sum():,.0f}")
    print("🎉 Graph ready. `g` is bipartite (vs['type']: rider = True), weighted by fare.")
```

---

## `data/projects/ups-ground-network/README.md`

# ups-ground-network

*A UPS-style ground line-haul network — large trucks move parcels between package
plants, from local centers up through regional hubs to national sort gateways.*

![Preview of the ups-ground-network network](thumb.png)

## At a glance

| | |
|---|---|
| **Direction** | Directed (a lane is one origin plant → one destination plant) |
| **Weights** | Weighted (`packages`; each lane also carries `trucks`, `distance_km`, `transit_hours`) |
| **Modality** | Multimodal — 3 plant kinds (`gateway`, `hub`, `center`) across the continental US |
| **Temporal** | No — a single daily snapshot (aggregated per lane) |
| **Nodes** | 149 plants (5 gateway + 36 hub + 108 center) |
| **Edges** | 347 directed lanes (one row per source-plant → destination-plant) |
| **Files** | `nodes.csv`, `edges.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

A stylized model of a parcel carrier's ground (truck) distribution network across
the continental US. Three kinds of plant:

- **`gateway`** — national sort hubs (the long-haul backbone, e.g. Louisville,
  Chicago, Dallas, Atlanta, Ontario CA);
- **`hub`** — regional metro hubs;
- **`center`** — local package centers (the origin / destination plants).

Each **edge is a lane aggregated at the source-plant → destination-plant level**:
one row per ordered pair (e.g. *Ithaca → Syracuse* moves 2,000-odd packages on a
couple of trucks). The lane weight is `packages`; the lane also records how many
`trucks` it takes, the `distance_km` between the two plants, and the
`transit_hours` in transit. Plants carry their coordinates (`x` = longitude,
`y` = latitude), a `region`, and a `daily_packages` throughput.

This is a flow-and-**resilience** network. Some questions to chew on:

- If one plant went dark for a day, which one would hurt the network most — and
  would degree, betweenness, or a knockout/criticality analysis agree? Is the
  busiest plant the most critical one?
- Are some regions one bad day away from being cut off from the rest of the
  country entirely? Which single closure would isolate the most plants?
- When a lane fails, how much longer (km and hours) is the next-best route? Where
  is rerouting cheap, and where is it ruinous?
- Trucks are finite. Which lanes are already running near full and have no slack
  to absorb a surge or a reroute?
- Does geography decide everything, or do some lanes carry far more than distance
  alone would predict?

> **Note.** The interesting findings here are deliberately *not* documented. "Big
> hubs move more packages" is the starting point, not a finding. Push past it —
> raw degree and raw volume will both mislead you.

## `nodes.csv`

One row per plant. Every node has every column populated.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique key. `G##` gateway, `H###` hub, `C###` center. Referenced by edges. | character | `G01`, `H001`, `C040` |
| `kind` | Plant kind | Role in the network. | character | `gateway`, `hub`, `center` |
| `region` | Region | US region the plant sits in. | character | `Northeast`, `Mid-Atlantic`, `Southeast`, `Midwest`, `South`, `Mountain`, `West` |
| `x` | Longitude | Plant longitude (decimal degrees). | double | `-85.76`, `-71.06` |
| `y` | Latitude | Plant latitude (decimal degrees). | double | `38.25`, `42.36` |
| `daily_packages` | Daily throughput | Nominal parcels handled per day at this plant. | integer | `130710`, `71515`, `29913` |
| `label` | Display name | Self-describing plant name: `<city> Gateway` / `<city> Hub` / `<town> Center`. (`name` is avoided — python-igraph reserves it for the ID.) | character | `Louisville KY Gateway`, `Syracuse NY Hub`, `Ithaca NY Center` |

## `edges.csv`

One row per **lane**, directed from the origin plant (`from_id`) to the
destination plant (`to_id`), aggregated over a day.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | Origin plant ID | Sending plant. | character | `C001`, `H001`, `G01` |
| `to_id` | Destination plant ID | Receiving plant. | character | `H001`, `C001`, `G04` |
| `packages` | Packages per day | Parcels moved on this lane per day (the edge weight). | integer | `5299`, `26493`, `4545` |
| `trucks` | Trucks per day | Large trucks dispatched on this lane per day. | integer | `8`, `25`, `7` |
| `distance_km` | Distance | Lane distance between the two plants, kilometres. | double | `56.7`, `3120.1`, `17.6` |
| `transit_hours` | Transit time | Door-to-door time in transit on the lane, hours. | double | `4.6`, `45.68`, `2.71` |

A useful derived quantity is **packages ÷ trucks** (parcels per truck): lanes near
the trailer's capacity have little slack to absorb a disruption.

## Load it

```bash
Rscript data/projects/ups-ground-network/load.R     # R    (igraph)
python  data/projects/ups-ground-network/load.py     # Python (python-igraph)
```

Both build a directed, weighted `igraph` graph and print a one-screen summary. In
the [R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**ups-ground-network** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/ups-ground-network>

---

## `data/projects/ups-ground-network/_generate.py`

```python
"""Generate the `ups-ground-network` project network (deterministic).

A stylized UPS-style ground line-haul network: large trucks move parcels between
package plants (facilities) across the continental US. Three kinds of node:
  - gateway  national sort hubs (e.g., Louisville, Chicago, Dallas, Atlanta,
             Ontario CA) -- the long-haul backbone;
  - hub      regional metro hubs;
  - center   local package centers (origin/destination plants).

Edges are DIRECTED lanes aggregated at the **source-plant -> destination-plant**
level: one row per ordered (from_id, to_id) pair (e.g., Ithaca -> Syracuse sends
N packages on T trucks). Lane attributes are the things you track about trucks:
`packages` (the weight), `trucks`, `distance_km`, and `transit_hours`.

Node attributes: kind, region, x (lon), y (lat), daily_packages, label.

Design parameters (the only record of the planted structure):
  - GATEWAYS form a fully-meshed long-haul backbone; almost all cross-region
    flow passes through them, so they have very high BETWEENNESS and are the real
    single points of failure for resilience.
  - DOMINANT_GATEWAY (Louisville): a national hub that most regional hubs also
    feed directly, so it concentrates the most cross-region paths.
  - SINGLE_HOMED_REGION (Southeast): its hubs connect to the backbone ONLY through
    ATLANTA. Removing Atlanta disconnects the whole region -- a genuine cut vertex
    a degree ranking will under-rate.
  - DECOY_HUB (Los Angeles): a busy regional metro hub that is NOT on the
    cross-region backbone, so removing it barely dents national connectivity --
    a reminder that a locally busy plant is not automatically a critical one.
  - TIGHT_BACKBONE: backbone & single-homed lanes run near truck capacity
    (high packages-per-truck, little slack); regional lanes carry slack. So the
    fragile lanes are the ones with the least spare capacity to absorb a surge.
  - Distance is real (haversine of coordinates); transit time = drive time at a
    lane-type speed + per-stop dwell + congestion noise.

Run:
    python data/projects/ups-ground-network/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import math
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42

TRUCK_CAP = 1200          # max parcels a single line-haul trailer carries
DOMINANT_GATEWAY = "Louisville KY"
SINGLE_HOMED_REGION = "Southeast"
SINGLE_HOME_GATEWAY = "Atlanta GA"
DECOY_CITY = "Los Angeles CA"
MULTIHOME_SHARE = 0.60    # share of (non-single-homed) hubs that also feed Louisville
CENTERS_PER_HUB = 3

# (city, region, lat, lon)
GATEWAYS = [
    ("Louisville KY", "Midwest", 38.25, -85.76),
    ("Chicago IL", "Midwest", 41.88, -87.63),
    ("Dallas TX", "South", 32.78, -96.80),
    ("Atlanta GA", "Southeast", 33.75, -84.39),
    ("Ontario CA", "West", 34.06, -117.65),
]

HUBS = [
    # Northeast
    ("Boston MA", "Northeast", 42.36, -71.06),
    ("Syracuse NY", "Northeast", 43.05, -76.15),
    ("Albany NY", "Northeast", 42.65, -73.76),
    ("Buffalo NY", "Northeast", 42.89, -78.88),
    ("Hartford CT", "Northeast", 41.76, -72.69),
    # Mid-Atlantic
    ("New York NY", "Mid-Atlantic", 40.71, -74.01),
    ("Philadelphia PA", "Mid-Atlantic", 39.95, -75.17),
    ("Pittsburgh PA", "Mid-Atlantic", 40.44, -79.99),
    ("Baltimore MD", "Mid-Atlantic", 39.29, -76.61),
    ("Richmond VA", "Mid-Atlantic", 37.54, -77.44),
    # Southeast
    ("Charlotte NC", "Southeast", 35.23, -80.84),
    ("Nashville TN", "Southeast", 36.16, -86.78),
    ("Orlando FL", "Southeast", 28.54, -81.38),
    ("Miami FL", "Southeast", 25.76, -80.19),
    ("Memphis TN", "Southeast", 35.15, -90.05),
    # Midwest
    ("Indianapolis IN", "Midwest", 39.77, -86.16),
    ("Columbus OH", "Midwest", 39.96, -82.99),
    ("Detroit MI", "Midwest", 42.33, -83.05),
    ("Minneapolis MN", "Midwest", 44.98, -93.27),
    ("St Louis MO", "Midwest", 38.63, -90.20),
    ("Kansas City MO", "Midwest", 39.10, -94.58),
    # South
    ("Houston TX", "South", 29.76, -95.37),
    ("San Antonio TX", "South", 29.42, -98.49),
    ("Austin TX", "South", 30.27, -97.74),
    ("New Orleans LA", "South", 29.95, -90.07),
    ("Oklahoma City OK", "South", 35.47, -97.52),
    # Mountain
    ("Denver CO", "Mountain", 39.74, -104.99),
    ("Salt Lake City UT", "Mountain", 40.76, -111.89),
    ("Phoenix AZ", "Mountain", 33.45, -112.07),
    ("Albuquerque NM", "Mountain", 35.08, -106.65),
    # West
    ("Los Angeles CA", "West", 34.05, -118.24),
    ("San Francisco CA", "West", 37.77, -122.42),
    ("Seattle WA", "West", 47.61, -122.33),
    ("Portland OR", "West", 45.52, -122.68),
    ("Las Vegas NV", "West", 36.17, -115.14),
    ("Sacramento CA", "West", 38.58, -121.49),
]

# Three real satellite towns per regional hub, so every package center has a
# recognizable place name (e.g. Ithaca / Utica / Binghamton feed Syracuse).
CENTER_TOWNS = {
    # Northeast
    "Boston MA": ["Cambridge MA", "Worcester MA", "Providence RI"],
    "Syracuse NY": ["Ithaca NY", "Utica NY", "Binghamton NY"],
    "Albany NY": ["Schenectady NY", "Troy NY", "Saratoga Springs NY"],
    "Buffalo NY": ["Niagara Falls NY", "Rochester NY", "Jamestown NY"],
    "Hartford CT": ["New Haven CT", "Springfield MA", "Waterbury CT"],
    # Mid-Atlantic
    "New York NY": ["Newark NJ", "Yonkers NY", "Jersey City NJ"],
    "Philadelphia PA": ["Camden NJ", "Wilmington DE", "Allentown PA"],
    "Pittsburgh PA": ["Greensburg PA", "Washington PA", "Altoona PA"],
    "Baltimore MD": ["Annapolis MD", "Towson MD", "Frederick MD"],
    "Richmond VA": ["Petersburg VA", "Charlottesville VA", "Fredericksburg VA"],
    # Southeast
    "Charlotte NC": ["Gastonia NC", "Concord NC", "Rock Hill SC"],
    "Nashville TN": ["Murfreesboro TN", "Franklin TN", "Clarksville TN"],
    "Orlando FL": ["Kissimmee FL", "Sanford FL", "Lakeland FL"],
    "Miami FL": ["Fort Lauderdale FL", "Hialeah FL", "West Palm Beach FL"],
    "Memphis TN": ["Southaven MS", "Jackson TN", "West Memphis AR"],
    # Midwest
    "Indianapolis IN": ["Carmel IN", "Bloomington IN", "Lafayette IN"],
    "Columbus OH": ["Dublin OH", "Newark OH", "Lancaster OH"],
    "Detroit MI": ["Ann Arbor MI", "Warren MI", "Dearborn MI"],
    "Minneapolis MN": ["St Paul MN", "Bloomington MN", "Rochester MN"],
    "St Louis MO": ["St Charles MO", "Florissant MO", "Belleville IL"],
    "Kansas City MO": ["Overland Park KS", "Independence MO", "Olathe KS"],
    # South
    "Houston TX": ["Pasadena TX", "Sugar Land TX", "Galveston TX"],
    "San Antonio TX": ["New Braunfels TX", "Schertz TX", "Seguin TX"],
    "Austin TX": ["Round Rock TX", "San Marcos TX", "Georgetown TX"],
    "New Orleans LA": ["Metairie LA", "Baton Rouge LA", "Slidell LA"],
    "Oklahoma City OK": ["Norman OK", "Edmond OK", "Moore OK"],
    # Mountain
    "Denver CO": ["Boulder CO", "Aurora CO", "Fort Collins CO"],
    "Salt Lake City UT": ["Provo UT", "Ogden UT", "Orem UT"],
    "Phoenix AZ": ["Mesa AZ", "Tempe AZ", "Scottsdale AZ"],
    "Albuquerque NM": ["Santa Fe NM", "Rio Rancho NM", "Los Lunas NM"],
    # West
    "Los Angeles CA": ["Long Beach CA", "Anaheim CA", "Pasadena CA"],
    "San Francisco CA": ["Oakland CA", "San Jose CA", "Berkeley CA"],
    "Seattle WA": ["Tacoma WA", "Bellevue WA", "Everett WA"],
    "Portland OR": ["Beaverton OR", "Gresham OR", "Salem OR"],
    "Las Vegas NV": ["Henderson NV", "North Las Vegas NV", "Pahrump NV"],
    "Sacramento CA": ["Roseville CA", "Elk Grove CA", "Davis CA"],
}


def haversine_km(a_lat, a_lon, b_lat, b_lon):
    R = 6371.0
    p1, p2 = math.radians(a_lat), math.radians(b_lat)
    dphi = math.radians(b_lat - a_lat)
    dlmb = math.radians(b_lon - a_lon)
    h = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def main() -> None:
    rng = np.random.default_rng(SEED)

    rows = []
    coord = {}    # node_id -> (lat, lon)
    region_of = {}
    kind_of = {}

    # ----- gateways -------------------------------------------------------
    gateway_ids = []
    for i, (city, region, lat, lon) in enumerate(GATEWAYS):
        nid = f"G{i+1:02d}"
        gateway_ids.append(nid)
        coord[nid] = (lat, lon); region_of[nid] = region; kind_of[nid] = "gateway"
        rows.append({"node_id": nid, "kind": "gateway", "region": region,
                     "x": round(lon, 3), "y": round(lat, 3),
                     "daily_packages": int(rng.integers(120000, 240000)),
                     "label": f"{city} Gateway"})
    gw_by_city = {GATEWAYS[i][0]: gateway_ids[i] for i in range(len(GATEWAYS))}

    # ----- hubs -----------------------------------------------------------
    hub_ids = []
    hub_city = {}
    for i, (city, region, lat, lon) in enumerate(HUBS):
        nid = f"H{i+1:03d}"
        hub_ids.append(nid)
        hub_city[nid] = city
        coord[nid] = (lat, lon); region_of[nid] = region; kind_of[nid] = "hub"
        rows.append({"node_id": nid, "kind": "hub", "region": region,
                     "x": round(lon, 3), "y": round(lat, 3),
                     "daily_packages": int(rng.integers(20000, 80000)),
                     "label": f"{city} Hub"})

    # ----- centers (origin/destination plants) ----------------------------
    center_ids = []
    centers_of_hub = {h: [] for h in hub_ids}
    cidx = 0
    for h in hub_ids:
        city = hub_city[h]
        hlat, hlon = coord[h]
        towns = CENTER_TOWNS[city]
        for k in range(CENTERS_PER_HUB):
            cidx += 1
            nid = f"C{cidx:03d}"
            center_ids.append(nid)
            centers_of_hub[h].append(nid)
            lbl = f"{towns[k]} Center"
            # nudge coords toward a plausible nearby spot
            clat = hlat + rng.normal(0, 0.45)
            clon = hlon + rng.normal(0, 0.45)
            coord[nid] = (clat, clon); region_of[nid] = region_of[h]; kind_of[nid] = "center"
            rows.append({"node_id": nid, "kind": "center", "region": region_of[h],
                         "x": round(clon, 3), "y": round(clat, 3),
                         "daily_packages": int(rng.integers(1500, 9000)),
                         "label": lbl})

    nodes = pd.DataFrame(rows)
    size = dict(zip(nodes.node_id, nodes.daily_packages))

    # nearest gateway for each hub (by great-circle distance)
    def nearest_gateway(h):
        hlat, hlon = coord[h]
        return min(gateway_ids,
                   key=lambda g: haversine_km(hlat, hlon, *coord[g]))

    eds = []

    def add_lane(frm, to, packages, critical=False):
        d = haversine_km(*coord[frm], *coord[to])
        # speed by lane type: long backbone faster cruising; short regional slower
        base_speed = 88.0 if d > 600 else (78.0 if d > 200 else 64.0)
        speed = base_speed * rng.uniform(0.92, 1.06)
        dwell = rng.uniform(1.5, 4.0)                 # sort/handling hours
        congest = rng.uniform(0.0, 0.25) * (d / 100)  # mild distance-scaled noise
        transit = d / speed + dwell + congest
        packages = int(max(packages, 1))
        # capacity: tight on critical lanes (little slack), looser on regional
        per_truck = rng.uniform(1050, 1180) if critical else rng.uniform(560, 950)
        trucks = int(max(1, math.ceil(packages / per_truck)))
        eds.append({
            "from_id": frm, "to_id": to,
            "packages": packages,
            "trucks": trucks,
            "distance_km": round(d, 1),
            "transit_hours": round(transit, 2),
        })

    # ===== feeder + delivery: center <-> regional hub =====================
    for h in hub_ids:
        for c in centers_of_hub[h]:
            # origin plant -> hub (induction)
            add_lane(c, h, int(size[c] * rng.uniform(0.55, 0.9)))
            # hub -> destination plant (delivery)
            add_lane(h, c, int(size[c] * rng.uniform(0.55, 0.9)))

    # ===== line-haul: hub <-> gateway =====================================
    for h in hub_ids:
        region = region_of[h]
        if region == SINGLE_HOMED_REGION:
            gws = [gw_by_city[SINGLE_HOME_GATEWAY]]      # single-homed: Atlanta only
        else:
            gws = [nearest_gateway(h)]
            louis = gw_by_city[DOMINANT_GATEWAY]
            if louis not in gws and rng.random() < MULTIHOME_SHARE:
                gws.append(louis)                         # most also feed Louisville
        for g in gws:
            crit = (region == SINGLE_HOMED_REGION) or (g == gw_by_city[DOMINANT_GATEWAY])
            vol = int(size[h] * rng.uniform(0.35, 0.7))
            add_lane(h, g, vol, critical=crit)            # outbound to backbone
            add_lane(g, h, int(vol * rng.uniform(0.8, 1.15)), critical=crit)  # inbound

    # ===== trunk: gateway <-> gateway (full mesh) =========================
    for a in gateway_ids:
        for b in gateway_ids:
            if a == b:
                continue
            vol = int(min(size[a], size[b]) * rng.uniform(0.20, 0.45))
            add_lane(a, b, vol, critical=True)

    # ===== a few direct intra-region hub <-> hub lanes ====================
    by_region = {}
    for h in hub_ids:
        by_region.setdefault(region_of[h], []).append(h)
    for region, hs in by_region.items():
        if len(hs) < 2:
            continue
        n_direct = min(len(hs), int(rng.integers(2, 5)))
        for _ in range(n_direct):
            a, b = rng.choice(hs, size=2, replace=False)
            vol = int(min(size[a], size[b]) * rng.uniform(0.12, 0.3))
            add_lane(a, b, vol)

    edges = pd.DataFrame(eds)
    nodes = nodes[["node_id", "kind", "region", "x", "y", "daily_packages", "label"]]

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)

    kc = nodes.kind.value_counts()
    print(f"ups-ground-network: {len(nodes)} nodes "
          f"({kc.get('gateway',0)} gateway + {kc.get('hub',0)} hub + "
          f"{kc.get('center',0)} center), {len(edges)} lanes. "
          f"{edges.packages.sum():,} packages/day on {edges.trucks.sum():,} trucks.")


if __name__ == "__main__":
    main()
```

---

## `data/projects/ups-ground-network/load.R`

```r
#' @name load.R
#' @title Load the `ups-ground-network` project network (R)
#' @description
#'
#' Reads the two CSVs in this folder and builds a directed, weighted igraph
#' object: a UPS-style ground line-haul network of large trucks moving parcels
#' between package plants (centers -> regional hubs -> national gateways). Run it
#' straight (`Rscript load.R`) for a quick summary, or `source()` it and call
#' `load_ups()` in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "ups-ground-network")

#' Load the node table (one row per plant: gateway / hub / center).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per source-plant -> destination-plant lane).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Build the directed, weighted graph.
#'
#' Lanes are weighted by `packages` and flow from the origin plant to the
#' destination plant. Each lane also carries `trucks`, `distance_km`, and
#' `transit_hours`. Knock a node out (`delete_vertices`) to test how much flow it
#' carries, or use `distances()` to see how reroutes lengthen transit time.
load_ups <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = TRUE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$packages
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n🚛 ups-ground-network (R)\n")
  cat("   Centers -> regional hubs -> national gateways;",
      "lanes weighted by packages, with trucks / distance / transit time.\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_ups(nodes, edges)

  cat(sprintf("✅ Loaded %d nodes (%d gateway, %d hub, %d center) and %d lanes.\n",
              nrow(nodes), sum(nodes$kind == "gateway"),
              sum(nodes$kind == "hub"), sum(nodes$kind == "center"),
              nrow(edges)))
  cat(sprintf("🔗 Directed: %s | total packages/day: %s on %s trucks | mean lane: %.0f km, %.1f h\n",
              is_directed(g),
              format(sum(edges$packages), big.mark = ","),
              format(sum(edges$trucks), big.mark = ","),
              mean(edges$distance_km), mean(edges$transit_hours)))
  cat("🎉 Graph ready. `g` is a directed, weighted igraph (weight = packages).\n")
}
```

---

## `data/projects/ups-ground-network/load.py`

```python
"""Load the `ups-ground-network` project network (Python).

Reads the two CSVs in this folder and builds a directed, weighted python-igraph
object: a UPS-style ground line-haul network of large trucks moving parcels
between package plants (centers -> regional hubs -> national gateways). Run it
straight (``python load.py``) for a quick summary, or import ``load_ups()`` into
your own script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per plant (gateway / hub / center)."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per source-plant -> destination-plant lane."""
    return pd.read_csv(HERE / "edges.csv")


def load_ups(nodes: pd.DataFrame | None = None,
             edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the directed, weighted graph (edge weight = ``packages``).

    Lanes flow from the origin plant to the destination plant and also carry
    ``trucks``, ``distance_km``, and ``transit_hours``. Delete a vertex to test
    how much flow it carries, or use ``g.distances()`` to see how reroutes
    lengthen transit time after a disruption.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=True, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["packages"]
    return g


if __name__ == "__main__":
    print("\n🚛 ups-ground-network (Python)")
    print("   Centers -> regional hubs -> national gateways; "
          "lanes weighted by packages, with trucks / distance / transit time.\n")

    nodes = load_nodes()
    edges = load_edges()
    g = load_ups(nodes, edges)

    kinds = nodes["kind"].value_counts()
    print(f"✅ Loaded {len(nodes)} nodes "
          f"({kinds.get('gateway',0)} gateway, {kinds.get('hub',0)} hub, "
          f"{kinds.get('center',0)} center) and {len(edges)} lanes.")
    print(f"🔗 Directed: {g.is_directed()} | total packages/day: "
          f"{edges['packages'].sum():,} on {edges['trucks'].sum():,} trucks | "
          f"mean lane: {edges['distance_km'].mean():.0f} km, "
          f"{edges['transit_hours'].mean():.1f} h")
    print("🎉 Graph ready. Object `g` is a directed, weighted igraph "
          "(weight = packages).")
```

---

## `data/projects/ups-package-flow/README.md`

# ups-package-flow

*The package-level companion to `ups-ground-network` — one row per individual
parcel, origin plant → destination plant, with its service, weight, distance, and
whether it arrived on time.*

![Preview of the ups-package-flow network](thumb.png)

## At a glance

| | |
|---|---|
| **Direction** | Directed (a parcel goes from its origin plant to its destination plant) |
| **Weights** | Weighted (`weight_kg`; each parcel also carries distance, transit, promise, on-time) |
| **Unit of analysis** | **The individual package** — one edge per parcel (a directed multigraph) |
| **Modality** | Multimodal plants (`gateway`, `hub`, `center`) across the continental US |
| **Temporal** | No — a single day of shipments |
| **Nodes** | 149 plants (5 gateway + 36 hub + 108 center) |
| **Edges** | 5,200 packages |
| **Files** | `nodes.csv`, `edges.csv`, `load.R`, `load.py`, `_generate.py` |

## What this network is

This is the **disaggregated** view of the same parcel system as
[`ups-ground-network`](../ups-ground-network/). There, each row is a truck *lane*
(the unit of analysis is the truck). **Here, each row is a single package** — its
origin plant, its destination plant, and what happened to it. Group the package
rows by `(from_id, to_id)` and you get back a lane-level view; that round trip is
half the point.

Each parcel records its `service_level` (ground / two-day / overnight), its
`weight_kg`, the `distance_km` between origin and destination, the actual
`transit_hours`, the `promised_hours` for its service, whether it was `on_time`,
and whether it was `damaged`. Plants carry coordinates (`x` = longitude,
`y` = latitude), a `region`, and a daily throughput.

This is a service-performance and inference network. Some questions to chew on:

- Which plants are the worst to *ship to*? Rank destinations by on-time rate — and
  check whether that ranking just reflects how far away they are, or something
  else.
- Is there a service gap that survives controlling for distance and service level?
  Who eats it?
- Do cross-region parcels arrive late more often than within-region ones the same
  distance apart? Is the penalty the same for every service tier?
- Aggregate to lanes (sum packages, average transit) — does the busy-lane picture
  match the package-level one, or does aggregation hide who is being failed?
- Build a model to predict `on_time` from package + network features. What carries
  the signal — distance, service, destination, region crossing?

> **Note.** The interesting findings here are deliberately *not* documented.
> "Farther parcels take longer" is the starting point, not a finding. Push past it
> — control for the obvious things and see what's left.

## `nodes.csv`

One row per plant. Every node has every column populated.

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `node_id` | Node ID | Unique key. `G##` gateway, `H###` hub, `C###` center. Referenced by edges. | character | `G01`, `H001`, `C054` |
| `kind` | Plant kind | Role in the network. | character | `gateway`, `hub`, `center` |
| `region` | Region | US region the plant sits in. | character | `Northeast`, `Mid-Atlantic`, `Southeast`, `Midwest`, `South`, `Mountain`, `West` |
| `x` | Longitude | Plant longitude (decimal degrees). | double | `-85.76`, `-71.06` |
| `y` | Latitude | Plant latitude (decimal degrees). | double | `38.25`, `42.36` |
| `daily_packages` | Daily throughput | Nominal parcels handled per day at this plant. | integer | `130710`, `71515`, `4820` |
| `label` | Display name | Self-describing plant name: `<city> Gateway` / `<city> Hub` / `<town> Center`. (`name` is avoided — python-igraph reserves it for the ID.) | character | `Louisville KY Gateway`, `Boston MA Hub`, `Cambridge MA Center` |

## `edges.csv`

One row per **package**, directed from the origin plant (`from_id`) to the
destination plant (`to_id`).

| Variable | Full name | Description | Class | Example values |
|---|---|---|---|---|
| `from_id` | Origin plant ID | Where the parcel was inducted. | character | `C054`, `C052`, `C092` |
| `to_id` | Destination plant ID | Where the parcel is delivered. | character | `C010`, `C047`, `C058` |
| `package_id` | Package ID | Unique parcel identifier. | character | `PKG000001`, `PKG005200` |
| `service_level` | Service level | Service tier purchased. | character | `ground`, `two_day`, `overnight` |
| `weight_kg` | Weight | Parcel weight, kilograms. | double | `1.21`, `3.18`, `12.4` |
| `distance_km` | Distance | Great-circle distance origin → destination, kilometres. | double | `361.4`, `2441.2` |
| `transit_hours` | Transit time | Actual time in transit, hours. | double | `30.23`, `32.08` |
| `promised_hours` | Promised time | Service commitment for this parcel, hours. | double | `30.6`, `48.0` |
| `on_time` | On time | 1 if `transit_hours <= promised_hours`, else 0. | integer | `1`, `0` |
| `damaged` | Damaged | 1 if the parcel was damaged in transit, else 0. | integer | `0`, `1` |

## Load it

```bash
Rscript data/projects/ups-package-flow/load.R     # R    (igraph)
python  data/projects/ups-package-flow/load.py     # Python (python-igraph)
```

Both build a directed, weighted `igraph` **multigraph** (one edge per package) and
print a one-screen summary. In the
[R](https://timothyfraser.com/netsci/playground-r.html) or
[Python](https://timothyfraser.com/netsci/playground-py.html) playground, pick
**ups-package-flow** from the *Load sample* menu.

## Get this data

Browse or download from the course repo:
<https://github.com/timothyfraser/netsci/tree/main/data/projects/ups-package-flow>

---

## `data/projects/ups-package-flow/_generate.py`

```python
"""Generate the `ups-package-flow` project network (deterministic).

The PACKAGE-LEVEL companion to `ups-ground-network`: where that dataset
aggregates flow to one row per truck lane, here the **unit of analysis is the
individual package** -- one row per parcel. Each parcel is a directed edge from
its origin plant to its destination plant, so the edge list is a directed
multigraph over the same plant universe (gateways / hubs / centers). Aggregating
the package rows by (from_id, to_id) reproduces a lane-level view.

Per-package attributes: service_level, weight_kg, distance_km, transit_hours,
promised_hours, on_time, damaged.

Node attributes: kind, region, x (lon), y (lat), daily_packages, label.

Design parameters (the only record of the planted structure):
  - SERVICE mix drives the promise: `overnight` < `two_day` < `ground` lead time;
    on_time = (transit_hours <= promised_hours).
  - CROSS_REGION_PENALTY: parcels whose origin and destination are in different
    regions take extra hours (more hand-offs across the backbone) *independent of
    distance*, so their on-time rate is worse even after controlling for distance.
  - RURAL_DEST_PENALTY: parcels delivered to low-throughput (rural) destination
    plants run slower *controlling for distance* -- a planted service-equity gap.
  - WEIGHT effects: heavier parcels are a little slower and a little more likely
    to be `damaged`.
  - Distance is real (haversine of plant coordinates).

Run:
    python data/projects/ups-package-flow/_generate.py
"""
from __future__ import annotations

from pathlib import Path
import math
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEED = 42
N_PACKAGES = 5200
CENTERS_PER_HUB = 3

# planted effect sizes (hours unless noted)
CROSS_REGION_PENALTY = (5.0, 16.0)   # uniform extra hours for inter-region parcels
RURAL_DEST_MAX = 13.0                 # max extra hours for the smallest dest plant
HEAVY_PENALTY_PER_KG = 0.25          # extra hours per kg over 5 kg
DAMAGE_BASE = 0.012

# (city, region, lat, lon)
GATEWAYS = [
    ("Louisville KY", "Midwest", 38.25, -85.76),
    ("Chicago IL", "Midwest", 41.88, -87.63),
    ("Dallas TX", "South", 32.78, -96.80),
    ("Atlanta GA", "Southeast", 33.75, -84.39),
    ("Ontario CA", "West", 34.06, -117.65),
]
HUBS = [
    ("Boston MA", "Northeast", 42.36, -71.06), ("Syracuse NY", "Northeast", 43.05, -76.15),
    ("Albany NY", "Northeast", 42.65, -73.76), ("Buffalo NY", "Northeast", 42.89, -78.88),
    ("Hartford CT", "Northeast", 41.76, -72.69),
    ("New York NY", "Mid-Atlantic", 40.71, -74.01), ("Philadelphia PA", "Mid-Atlantic", 39.95, -75.17),
    ("Pittsburgh PA", "Mid-Atlantic", 40.44, -79.99), ("Baltimore MD", "Mid-Atlantic", 39.29, -76.61),
    ("Richmond VA", "Mid-Atlantic", 37.54, -77.44),
    ("Charlotte NC", "Southeast", 35.23, -80.84), ("Nashville TN", "Southeast", 36.16, -86.78),
    ("Orlando FL", "Southeast", 28.54, -81.38), ("Miami FL", "Southeast", 25.76, -80.19),
    ("Memphis TN", "Southeast", 35.15, -90.05),
    ("Indianapolis IN", "Midwest", 39.77, -86.16), ("Columbus OH", "Midwest", 39.96, -82.99),
    ("Detroit MI", "Midwest", 42.33, -83.05), ("Minneapolis MN", "Midwest", 44.98, -93.27),
    ("St Louis MO", "Midwest", 38.63, -90.20), ("Kansas City MO", "Midwest", 39.10, -94.58),
    ("Houston TX", "South", 29.76, -95.37), ("San Antonio TX", "South", 29.42, -98.49),
    ("Austin TX", "South", 30.27, -97.74), ("New Orleans LA", "South", 29.95, -90.07),
    ("Oklahoma City OK", "South", 35.47, -97.52),
    ("Denver CO", "Mountain", 39.74, -104.99), ("Salt Lake City UT", "Mountain", 40.76, -111.89),
    ("Phoenix AZ", "Mountain", 33.45, -112.07), ("Albuquerque NM", "Mountain", 35.08, -106.65),
    ("Los Angeles CA", "West", 34.05, -118.24), ("San Francisco CA", "West", 37.77, -122.42),
    ("Seattle WA", "West", 47.61, -122.33), ("Portland OR", "West", 45.52, -122.68),
    ("Las Vegas NV", "West", 36.17, -115.14), ("Sacramento CA", "West", 38.58, -121.49),
]
CENTER_TOWNS = {
    "Boston MA": ["Cambridge MA", "Worcester MA", "Providence RI"],
    "Syracuse NY": ["Ithaca NY", "Utica NY", "Binghamton NY"],
    "Albany NY": ["Schenectady NY", "Troy NY", "Saratoga Springs NY"],
    "Buffalo NY": ["Niagara Falls NY", "Rochester NY", "Jamestown NY"],
    "Hartford CT": ["New Haven CT", "Springfield MA", "Waterbury CT"],
    "New York NY": ["Newark NJ", "Yonkers NY", "Jersey City NJ"],
    "Philadelphia PA": ["Camden NJ", "Wilmington DE", "Allentown PA"],
    "Pittsburgh PA": ["Greensburg PA", "Washington PA", "Altoona PA"],
    "Baltimore MD": ["Annapolis MD", "Towson MD", "Frederick MD"],
    "Richmond VA": ["Petersburg VA", "Charlottesville VA", "Fredericksburg VA"],
    "Charlotte NC": ["Gastonia NC", "Concord NC", "Rock Hill SC"],
    "Nashville TN": ["Murfreesboro TN", "Franklin TN", "Clarksville TN"],
    "Orlando FL": ["Kissimmee FL", "Sanford FL", "Lakeland FL"],
    "Miami FL": ["Fort Lauderdale FL", "Hialeah FL", "West Palm Beach FL"],
    "Memphis TN": ["Southaven MS", "Jackson TN", "West Memphis AR"],
    "Indianapolis IN": ["Carmel IN", "Bloomington IN", "Lafayette IN"],
    "Columbus OH": ["Dublin OH", "Newark OH", "Lancaster OH"],
    "Detroit MI": ["Ann Arbor MI", "Warren MI", "Dearborn MI"],
    "Minneapolis MN": ["St Paul MN", "Bloomington MN", "Rochester MN"],
    "St Louis MO": ["St Charles MO", "Florissant MO", "Belleville IL"],
    "Kansas City MO": ["Overland Park KS", "Independence MO", "Olathe KS"],
    "Houston TX": ["Pasadena TX", "Sugar Land TX", "Galveston TX"],
    "San Antonio TX": ["New Braunfels TX", "Schertz TX", "Seguin TX"],
    "Austin TX": ["Round Rock TX", "San Marcos TX", "Georgetown TX"],
    "New Orleans LA": ["Metairie LA", "Baton Rouge LA", "Slidell LA"],
    "Oklahoma City OK": ["Norman OK", "Edmond OK", "Moore OK"],
    "Denver CO": ["Boulder CO", "Aurora CO", "Fort Collins CO"],
    "Salt Lake City UT": ["Provo UT", "Ogden UT", "Orem UT"],
    "Phoenix AZ": ["Mesa AZ", "Tempe AZ", "Scottsdale AZ"],
    "Albuquerque NM": ["Santa Fe NM", "Rio Rancho NM", "Los Lunas NM"],
    "Los Angeles CA": ["Long Beach CA", "Anaheim CA", "Pasadena CA"],
    "San Francisco CA": ["Oakland CA", "San Jose CA", "Berkeley CA"],
    "Seattle WA": ["Tacoma WA", "Bellevue WA", "Everett WA"],
    "Portland OR": ["Beaverton OR", "Gresham OR", "Salem OR"],
    "Las Vegas NV": ["Henderson NV", "North Las Vegas NV", "Pahrump NV"],
    "Sacramento CA": ["Roseville CA", "Elk Grove CA", "Davis CA"],
}
SERVICES = ["ground", "two_day", "overnight"]
SERVICE_P = [0.62, 0.26, 0.12]


def haversine_km(a_lat, a_lon, b_lat, b_lon):
    R = 6371.0
    p1, p2 = math.radians(a_lat), math.radians(b_lat)
    dphi = math.radians(b_lat - a_lat)
    dlmb = math.radians(b_lon - a_lon)
    h = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def main() -> None:
    rng = np.random.default_rng(SEED)

    rows = []
    coord = {}
    for i, (city, region, lat, lon) in enumerate(GATEWAYS):
        nid = f"G{i+1:02d}"; coord[nid] = (lat, lon)
        rows.append({"node_id": nid, "kind": "gateway", "region": region,
                     "x": round(lon, 3), "y": round(lat, 3),
                     "daily_packages": int(rng.integers(120000, 240000)),
                     "label": f"{city} Gateway"})
    hub_ids, hub_city = [], {}
    for i, (city, region, lat, lon) in enumerate(HUBS):
        nid = f"H{i+1:03d}"; hub_ids.append(nid); hub_city[nid] = city; coord[nid] = (lat, lon)
        rows.append({"node_id": nid, "kind": "hub", "region": region,
                     "x": round(lon, 3), "y": round(lat, 3),
                     "daily_packages": int(rng.integers(20000, 80000)),
                     "label": f"{city} Hub"})
    center_ids = []
    cidx = 0
    for h in hub_ids:
        city = hub_city[h]; hlat, hlon = coord[h]
        for k in range(CENTERS_PER_HUB):
            cidx += 1; nid = f"C{cidx:03d}"; center_ids.append(nid)
            clat = hlat + rng.normal(0, 0.45); clon = hlon + rng.normal(0, 0.45)
            coord[nid] = (clat, clon)
            rows.append({"node_id": nid, "kind": "center",
                         "region": next(r for c, r, *_ in HUBS if c == city),
                         "x": round(clon, 3), "y": round(clat, 3),
                         "daily_packages": int(rng.integers(1500, 9000)),
                         "label": f"{CENTER_TOWNS[city][k]} Center"})

    nodes = pd.DataFrame(rows)
    region_of = dict(zip(nodes.node_id, nodes.region))
    size_of = dict(zip(nodes.node_id, nodes.daily_packages))

    # parcels originate and terminate at local centers
    centers = np.array(center_ids)
    csize = np.array([size_of[c] for c in centers], dtype=float)
    p_origin = csize / csize.sum()
    # destination size normaliser for the rural-dest penalty (0 = smallest)
    smin, smax = csize.min(), csize.max()
    size_norm = {c: (size_of[c] - smin) / (smax - smin) for c in center_ids}
    clat = {c: coord[c][0] for c in center_ids}
    clon = {c: coord[c][1] for c in center_ids}

    origins = rng.choice(centers, size=N_PACKAGES, p=p_origin)
    services = rng.choice(SERVICES, size=N_PACKAGES, p=SERVICE_P)

    eds = []
    for i in range(N_PACKAGES):
        o = origins[i]
        # destination: distance-decayed, size-weighted, not the origin
        olat, olon = coord[o]
        d_to = np.array([haversine_km(olat, olon, clat[c], clon[c]) for c in centers])
        w = csize / (1.0 + (d_to / 800.0) ** 2)
        w[centers == o] = 0.0
        w = w / w.sum()
        dest = centers[rng.choice(len(centers), p=w)]
        dist = haversine_km(olat, olon, clat[dest], clon[dest])

        svc = services[i]
        wkg = float(np.clip(rng.lognormal(0.6, 0.8), 0.1, 40.0))

        if svc == "ground":
            transit = dist / 80.0 + rng.uniform(8, 20)
            promised = 24.0 + dist / 55.0
            pscale = 1.0                  # ground rides the full hand-off chain
        elif svc == "two_day":
            transit = dist / 280.0 + rng.uniform(14, 26)
            promised = 48.0
            pscale = 0.6
        else:  # overnight (air) — bypasses most ground hand-off delay
            transit = dist / 650.0 + rng.uniform(9, 16)
            promised = 30.0
            pscale = 0.3

        # planted penalties (independent of distance), scaled by service mode
        pen = 0.0
        if region_of[o] != region_of[dest]:
            pen += rng.uniform(*CROSS_REGION_PENALTY)                 # cross-region hand-offs
        pen += RURAL_DEST_MAX * (1.0 - size_norm[dest])              # rural dest gap
        if wkg > 5.0:
            pen += (wkg - 5.0) * HEAVY_PENALTY_PER_KG
        transit += pen * pscale + rng.normal(0, 3.0)                  # + noise
        transit = max(1.0, round(transit, 2))
        promised = round(promised, 1)

        on_time = int(transit <= promised)
        p_damage = DAMAGE_BASE + max(0.0, (wkg - 10.0)) * 0.004 + \
            (0.01 if region_of[o] != region_of[dest] else 0.0)
        damaged = int(rng.random() < p_damage)

        eds.append({
            "from_id": o, "to_id": dest, "package_id": f"PKG{i+1:06d}",
            "service_level": svc, "weight_kg": round(wkg, 2),
            "distance_km": round(dist, 1), "transit_hours": round(transit, 2),
            "promised_hours": round(promised, 1), "on_time": on_time,
            "damaged": damaged,
        })

    edges = pd.DataFrame(eds)
    nodes = nodes[["node_id", "kind", "region", "x", "y", "daily_packages", "label"]]

    nodes.to_csv(HERE / "nodes.csv", index=False)
    edges.to_csv(HERE / "edges.csv", index=False)

    kc = nodes.kind.value_counts()
    print(f"ups-package-flow: {len(nodes)} plants "
          f"({kc.get('gateway',0)} gateway + {kc.get('hub',0)} hub + "
          f"{kc.get('center',0)} center), {len(edges)} packages. "
          f"on-time {edges.on_time.mean():.1%}, damaged {edges.damaged.mean():.1%}.")


if __name__ == "__main__":
    main()
```

---

## `data/projects/ups-package-flow/load.R`

```r
#' @name load.R
#' @title Load the `ups-package-flow` project network (R)
#' @description
#'
#' Reads the two CSVs in this folder and builds a directed, weighted igraph
#' multigraph where the **unit of analysis is the individual package**: one edge
#' per parcel, from its origin plant to its destination plant. Run it straight
#' (`Rscript load.R`) for a quick summary, or `source()` it and call
#' `load_packages()` in your own script.

# 0. Setup ###################################################################
library(igraph)
library(here)

.dir <- function() here::here("data", "projects", "ups-package-flow")

#' Load the node table (one row per plant: gateway / hub / center).
load_nodes <- function() {
  read.csv(file.path(.dir(), "nodes.csv"), stringsAsFactors = FALSE)
}

#' Load the edge table (one row per package).
load_edges <- function() {
  read.csv(file.path(.dir(), "edges.csv"), stringsAsFactors = FALSE)
}

#' Build the directed, weighted multigraph (one edge per package).
#'
#' Edge weight is `weight_kg`. Each package edge also carries `service_level`,
#' `distance_km`, `transit_hours`, `promised_hours`, `on_time`, and `damaged`.
#' Aggregate the edges by (from, to) to recover a lane-level view, or summarise
#' `on_time` by destination plant to compare service across facilities.
load_packages <- function(nodes = load_nodes(), edges = load_edges()) {
  g <- graph_from_data_frame(d = edges, directed = TRUE, vertices = nodes)
  igraph::E(g)$weight <- igraph::E(g)$weight_kg
  g
}

# 1. Demo ####################################################################
if (sys.nframe() == 0) {
  cat("\n📦 ups-package-flow (R)\n")
  cat("   One edge per package: origin plant -> destination plant;",
      "weight = weight_kg.\n\n")

  nodes <- load_nodes()
  edges <- load_edges()
  g <- load_packages(nodes, edges)

  cat(sprintf("✅ Loaded %d plants (%d gateway, %d hub, %d center) and %d packages.\n",
              nrow(nodes), sum(nodes$kind == "gateway"),
              sum(nodes$kind == "hub"), sum(nodes$kind == "center"),
              nrow(edges)))
  cat(sprintf("🔗 Directed: %s | on-time: %.1f%% | damaged: %.1f%% | mean transit: %.1f h\n",
              is_directed(g),
              100 * mean(edges$on_time), 100 * mean(edges$damaged),
              mean(edges$transit_hours)))
  cat("🎉 Graph ready. `g` is a directed, weighted multigraph (weight = weight_kg).\n")
}
```

---

## `data/projects/ups-package-flow/load.py`

```python
"""Load the `ups-package-flow` project network (Python).

Reads the two CSVs in this folder and builds a directed, weighted python-igraph
multigraph where the **unit of analysis is the individual package**: one edge per
parcel, from its origin plant to its destination plant. Run it straight
(``python load.py``) for a quick summary, or import ``load_packages()`` into your
own script.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import igraph as ig

HERE = Path(__file__).resolve().parent


def load_nodes() -> pd.DataFrame:
    """Node table: one row per plant (gateway / hub / center)."""
    return pd.read_csv(HERE / "nodes.csv")


def load_edges() -> pd.DataFrame:
    """Edge table: one row per package."""
    return pd.read_csv(HERE / "edges.csv")


def load_packages(nodes: pd.DataFrame | None = None,
                  edges: pd.DataFrame | None = None) -> ig.Graph:
    """Build the directed, weighted multigraph (one edge per package).

    Edge weight is ``weight_kg``. Each package edge also carries
    ``service_level``, ``distance_km``, ``transit_hours``, ``promised_hours``,
    ``on_time``, and ``damaged``. Aggregate the edges by (from, to) to recover a
    lane-level view, or summarise ``on_time`` by destination plant to compare
    service across facilities.
    """
    if nodes is None:
        nodes = load_nodes()
    if edges is None:
        edges = load_edges()
    g = ig.Graph.DataFrame(edges, directed=True, vertices=nodes, use_vids=False)
    g.es["weight"] = g.es["weight_kg"]
    return g


if __name__ == "__main__":
    print("\n📦 ups-package-flow (Python)")
    print("   One edge per package: origin plant -> destination plant; "
          "weight = weight_kg.\n")

    nodes = load_nodes()
    edges = load_edges()
    g = load_packages(nodes, edges)

    kinds = nodes["kind"].value_counts()
    print(f"✅ Loaded {len(nodes)} plants "
          f"({kinds.get('gateway',0)} gateway, {kinds.get('hub',0)} hub, "
          f"{kinds.get('center',0)} center) and {len(edges)} packages.")
    print(f"🔗 Directed: {g.is_directed()} | on-time: "
          f"{100 * edges['on_time'].mean():.1f}% | damaged: "
          f"{100 * edges['damaged'].mean():.1f}% | mean transit: "
          f"{edges['transit_hours'].mean():.1f} h")
    print("🎉 Graph ready. Object `g` is a directed, weighted multigraph "
          "(weight = weight_kg).")
```

---

## `quickstart/README.md`

# SYSEN 5470 — Quickstart

Welcome. You've landed in the SYSEN 5470 course repo. If you're new to Git or
GitHub, you're in the right place — this folder walks you through the minimum
setup to follow along with the course.

> 💡 **The pretty version of this guide lives on the course website:**
> [tmfraser.com/netsci/help/github-setup.html](https://tmfraser.com/netsci/help/github-setup.html)
> Same content, prettier formatting, screenshots, OS tabs.

---

## Six steps

1. [Install Git](#1-install-git)
2. [Make a GitHub account](#2-make-a-github-account)
3. [Clone the course repo](#3-clone-the-course-repo)
4. [Make your project repo](#4-make-your-project-repo)
5. [Basic add / commit / push](#5-basic-add--commit--push)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. Install Git

Git is the command-line tool. GitHub is the hosting service. You need Git
locally before GitHub becomes useful.

- **macOS:** open Terminal, run `git --version`. If it prompts you to install
  Xcode command-line tools, accept. Otherwise you already have it.
- **Windows:** install [Git for Windows](https://git-scm.com/download/win).
  Includes Git Bash — keep it checked.
- **Linux:** `sudo apt install git` (Debian/Ubuntu) or your distro's
  equivalent.

Verify:

```sh
git --version
# → git version 2.43.0  (any 2.x is fine)
```

Tell Git who you are, once per machine:

```sh
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
```

---

## 2. Make a GitHub account

If you already have one, skip. If not:

- Sign up at <https://github.com/signup>. The free tier is plenty.
- Generate a **Personal Access Token** (PAT) for command-line use:
  Settings → Developer settings → Personal access tokens → Tokens (classic)
  → Generate new token. Scope: `repo` is enough. Save it — GitHub only shows
  it once.
- When Git asks for a password, paste the PAT.

SSH keys also work — see GitHub's
[SSH guide](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
if you'd rather. The course doesn't care which you pick.

---

## 3. Clone the course repo

```sh
# navigate to your code folder, then:
git clone https://github.com/timothyfraser/netsci.git
cd netsci
ls
```

You should see folders like `docs/`, `code/`, and this top-level `README.md`.

To pull the latest updates each week:

```sh
cd netsci
git pull
```

> You won't push to this repo — it's read-only for students. The course pushes
> *to* you; you push your own work to a separate repo (step 4).

---

## 4. Make your project repo

Your project case studies live in your own private GitHub repo.

1. On GitHub, click **New repository**. Name it `netsci-project` (or whatever).
   Set it to **Private**.
2. On your laptop:

```sh
mkdir netsci-project
cd netsci-project
git init
mkdir code data report

echo "# My SYSEN 5470 Project" > README.md
echo "3 project case studies. Each lives under code/." >> README.md

git add .
git commit -m "Initial commit"

# replace USERNAME with your GitHub handle
git remote add origin https://github.com/USERNAME/netsci-project.git
git branch -M main
git push -u origin main
```

Add Tim (`timothyfraser`) as a collaborator on your repo so he can read it
without it being public.

### Suggested layout

```
netsci-project/
├── README.md           # short overview + which 3 case studies you picked
├── code/
│   ├── 01-centrality/  # your first project case study
│   │   ├── project.R   # OR project.py
│   │   └── report.pdf
│   ├── 02-clustering/
│   └── 03-routing/
├── data/               # raw inputs (CSVs, edgelists)
└── notes/              # scratch, sketches, anything
```

---

## 5. Basic add / commit / push

After every meaningful chunk of work:

```sh
# 1. see what's changed
git status

# 2. stage the changes you want to commit
git add code/01-centrality/project.R
# or stage everything modified:
git add .

# 3. record the change with a short message
git commit -m "Centrality: first pass, top-10 nodes by betweenness"

# 4. push to GitHub
git push
```

That's the whole loop. **Commit often, in small chunks, with short messages.**

### Pull before push

```sh
git pull   # pull down anything new
git push   # then send yours up
```

### What NOT to commit

- Large datasets (over ~50 MB)
- Credentials (`.env` files, API keys)
- Anything inside `node_modules/`, `.Rproj.user/`, `__pycache__/`

Add a `.gitignore` with common patterns —
[github/gitignore](https://github.com/github/gitignore) has templates.

---

## 6. Troubleshooting

### `fatal: not a git repository`

`cd` into the folder that has the `.git` directory, or run `git init` if you
intended to start one here.

### Stuck in vim during a commit

Press `Esc`, type `:wq`, press `Enter`. Use `git commit -m "your message"`
next time to skip the editor entirely.

### `Updates were rejected because the tip of your branch is behind`

```sh
git pull --rebase
git push
```

### `Permission denied (publickey)`

You're using SSH but your key isn't registered with GitHub. Either set up the
SSH key (link above) or switch the remote to HTTPS:

```sh
git remote set-url origin https://github.com/USERNAME/netsci-project.git
```

### Accidentally committed a big file / a secret

If you haven't pushed:

```sh
git reset HEAD~          # undo the last commit, keep changes
# then add the file to .gitignore and recommit
```

If you already pushed a secret: **rotate it.** Git history doesn't forgive —
the secret is in the repo even if you delete the file in a new commit.

---

For everything else, see the course website's
[FAQ](https://tmfraser.com/netsci/help/faq.html) or the
[full GitHub Setup page](https://tmfraser.com/netsci/help/github-setup.html).

---

