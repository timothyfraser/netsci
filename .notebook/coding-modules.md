# SYSEN 5470 — Coding Modules Bundle

_Auto-generated NotebookLM source · 2026-06-14 01:34 UTC_

Every Markdown, R, and Python file in the course's coding modules, concatenated into one document. Paste this into NotebookLM as a source alongside the website bundle.

**76 files included.**

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

- **Course:** `81765` @ https://canvas.cornell.edu
- **Last pulled from Canvas:** 2026-06-01T16:18:59Z
- **Generated:** 2026-06-01T16:18:59Z

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

| Assignment | Group | Grading | Points | Proposed due |
|---|---|---|---|---|
| [Drawing — Build a Network](https://canvas.cornell.edu/courses/81765/assignments/968346) | Drawings | Completion | 1 | Mon 2026-06-29 13:00 UTC |
| [Learning Checks — Build a Network](https://canvas.cornell.edu/courses/81765/assignments/968347) | Case Studies | Completion | 1 | Mon 2026-06-29 13:00 UTC |
| [Drawing — Network Statistics](https://canvas.cornell.edu/courses/81765/assignments/968348) | Drawings | Completion | 1 | Mon 2026-06-29 13:00 UTC |
| [Learning Checks — Network Statistics](https://canvas.cornell.edu/courses/81765/assignments/968349) | Case Studies | Completion | 1 | Mon 2026-06-29 13:00 UTC |
| [Drawing — Centrality](https://canvas.cornell.edu/courses/81765/assignments/968350) | Drawings | Completion | 1 | Mon 2026-06-29 13:00 UTC |
| [Learning Checks — Centrality](https://canvas.cornell.edu/courses/81765/assignments/968351) | Case Studies | Completion | 1 | Mon 2026-06-29 13:00 UTC |
| [Ed Discussion — Week 1](https://canvas.cornell.edu/courses/81765/assignments/968368) | Participation | Completion | 1 | Mon 2026-06-29 13:00 UTC |
| [Office Hours — Week 1](https://canvas.cornell.edu/courses/81765/assignments/968371) | Participation | Completion | 1 | Wed 2026-06-24 03:59 UTC |
| [Project Case Study — Submission 1](https://canvas.cornell.edu/courses/81765/assignments/968374) | Weekly Homework 1 · Project Case Study | Points | 100 | Mon 2026-06-29 13:00 UTC |
| [Intro Course Survey](https://canvas.cornell.edu/courses/81765/assignments/968417) | Participation | Completion | 1 | Wed 2026-06-24 03:59 UTC |

## Week 2

| Assignment | Group | Grading | Points | Proposed due |
|---|---|---|---|---|
| [Drawing — Supply Chain](https://canvas.cornell.edu/courses/81765/assignments/968352) | Drawings | Completion | 1 | Mon 2026-07-06 13:00 UTC |
| [Learning Checks — Supply Chain](https://canvas.cornell.edu/courses/81765/assignments/968353) | Case Studies | Completion | 1 | Mon 2026-07-06 13:00 UTC |
| [Drawing — Routing](https://canvas.cornell.edu/courses/81765/assignments/968354) | Drawings | Completion | 1 | Mon 2026-07-06 13:00 UTC |
| [Learning Checks — Routing](https://canvas.cornell.edu/courses/81765/assignments/968355) | Case Studies | Completion | 1 | Mon 2026-07-06 13:00 UTC |
| [Drawing — DSM Clustering](https://canvas.cornell.edu/courses/81765/assignments/968356) | Drawings | Completion | 1 | Mon 2026-07-06 13:00 UTC |
| [Learning Checks — DSM Clustering](https://canvas.cornell.edu/courses/81765/assignments/968357) | Case Studies | Completion | 1 | Mon 2026-07-06 13:00 UTC |
| [Drawing — Aggregation](https://canvas.cornell.edu/courses/81765/assignments/968358) | Drawings | Completion | 1 | Mon 2026-07-06 13:00 UTC |
| [Learning Checks — Aggregation](https://canvas.cornell.edu/courses/81765/assignments/968359) | Case Studies | Completion | 1 | Mon 2026-07-06 13:00 UTC |
| [Ed Discussion — Week 2](https://canvas.cornell.edu/courses/81765/assignments/968369) | Participation | Completion | 1 | Mon 2026-07-06 13:00 UTC |
| [Office Hours — Week 2](https://canvas.cornell.edu/courses/81765/assignments/968372) | Participation | Completion | 1 | Mon 2026-07-06 13:00 UTC |
| [Project Case Study — Submission 2](https://canvas.cornell.edu/courses/81765/assignments/968375) | Weekly Homework 2 · Project Case Study | Points | 100 | Mon 2026-07-06 13:00 UTC |
| [Midterm Course Evaluation](https://canvas.cornell.edu/courses/81765/assignments/968418) | Participation | Completion | 1 | Thu 2026-07-02 03:59 UTC |

## Week 3

| Assignment | Group | Grading | Points | Proposed due |
|---|---|---|---|---|
| [Drawing — GNN by Hand](https://canvas.cornell.edu/courses/81765/assignments/968360) | Drawings | Completion | 1 | Sat 2026-07-11 03:59 UTC |
| [Learning Checks — GNN by Hand](https://canvas.cornell.edu/courses/81765/assignments/968361) | Case Studies | Completion | 1 | Sat 2026-07-11 03:59 UTC |
| [Drawing — GNN + XGBoost](https://canvas.cornell.edu/courses/81765/assignments/968362) | Drawings | Completion | 1 | Sat 2026-07-11 03:59 UTC |
| [Learning Checks — GNN + XGBoost](https://canvas.cornell.edu/courses/81765/assignments/968363) | Case Studies | Completion | 1 | Sat 2026-07-11 03:59 UTC |
| [Drawing — Sampling](https://canvas.cornell.edu/courses/81765/assignments/968364) | Drawings | Completion | 1 | Sat 2026-07-11 03:59 UTC |
| [Learning Checks — Sampling](https://canvas.cornell.edu/courses/81765/assignments/968365) | Case Studies | Completion | 1 | Sat 2026-07-11 03:59 UTC |
| [Drawing — Joins](https://canvas.cornell.edu/courses/81765/assignments/968366) | Drawings | Completion | 1 | Sat 2026-07-11 03:59 UTC |
| [Learning Checks — Joins](https://canvas.cornell.edu/courses/81765/assignments/968367) | Case Studies | Completion | 1 | Sat 2026-07-11 03:59 UTC |
| [Ed Discussion — Week 3](https://canvas.cornell.edu/courses/81765/assignments/968370) | Participation | Completion | 1 | Sat 2026-07-11 03:59 UTC |
| [Office Hours — Week 3](https://canvas.cornell.edu/courses/81765/assignments/968373) | Participation | Completion | 1 | Sat 2026-07-11 03:59 UTC |
| [Project Case Study — Submission 3 (final)](https://canvas.cornell.edu/courses/81765/assignments/968376) | Weekly Homework 3 · Project Case Study | Points | 100 | Sat 2026-07-11 03:59 UTC |
| [Final Presentation](https://canvas.cornell.edu/courses/81765/assignments/968377) | Final Presentation | Completion | 1 | Sat 2026-07-11 03:59 UTC |
| [Final Course Evaluation](https://canvas.cornell.edu/courses/81765/assignments/968419) | Participation | Completion | 1 | Sat 2026-07-11 03:59 UTC |

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

## `MERGE-ME.md`

# MERGE-ME — apply the staged student permissions

A setup agent staged `.claude/settings.proposed.json` by merging the repo's existing
`.claude/settings.json` with `.claude/settings.students.json`. **Nothing was applied** —
your live `.claude/settings.json` is untouched.

## What to do

> Review `.claude/settings.proposed.json`; if it looks right, replace `.claude/settings.json`
> with it (or hand-add the listed entries below). These grant the student agents Python,
> file-writes, and Playwright navigate/click/type.

## Entries that would be ADDED to `permissions.allow`

- `Bash(python:*)`
- `Bash(python3:*)`
- `Bash(pip:*)`
- `Bash(pip3:*)`
- `Bash(git fetch:*)`  *(note: base already has `Bash(git fetch *)` with a space; this colon-form variant is added alongside it — harmless)*
- `Bash(git status:*)`
- `Bash(git log:*)`
- `Bash(git diff:*)`
- `Bash(git show:*)`
- `Bash(mkdir:*)`
- `Bash(cp:*)`
- `Bash(mv:*)`
- `Bash(ls:*)`
- `Bash(cat:*)`
- `Bash(head:*)`
- `Bash(tail:*)`
- `Bash(find:*)`
- `Bash(grep:*)`
- `Bash(wc:*)`
- `WebFetch`
- `mcp__playwright__browser_navigate`
- `mcp__playwright__browser_navigate_back`
- `mcp__playwright__browser_click`
- `mcp__playwright__browser_type`
- `mcp__playwright__browser_press_key`
- `mcp__playwright__browser_select_option`
- `mcp__playwright__browser_hover`
- `mcp__playwright__browser_wait_for`
- `mcp__playwright__browser_tabs`

## Entries that would be ADDED to `permissions.deny`

- `Bash(sudo:*)`
- `Bash(rm -rf /:*)`
- `Bash(rm -rf ~:*)`
- `Bash(chmod 777:*)`
- `Bash(git push:*)`
- `Bash(git commit:*)`
- `Read(./.env)`
- `Read(./**/.env)`

## Playwright server-name caveat

The allow-list uses the prefix `mcp__playwright__browser_*`. If `claude mcp list` shows the
Playwright server under a **different name**, these entries won't match and unattended runs
will stall on permission prompts. See the environment verification note in the setup agent's
final report for the detected server name.

---

## `README-ai-students.md`

# SYSEN 5470 — AI Student Walkthrough (Claude Code)

Send hypothetical AI "students" through the live course, have them run the real code,
do the homeworks/project on a network they choose, and report their experience — so you
can find where the course confuses, overloads, or loses people **before** a human cohort does.

This is the Claude Code implementation of the design handoff. It slots into the existing
`timothyfraser/netsci` repo conventions (R SessionStart hook, `code/01_…11_` folders,
tidyverse + base-pipe `CLAUDE.md`, Playwright MCP already configured).

## What's here

```
.claude/
  agents/
    _shared/student-brief.md   ← protocol + journal/report/scores schemas (read by all)
    student-priya.md           ← stellar coder, Python track (the ceiling)
    student-marcus.md          ← strong Python, new to R, shaky inference theory
    student-sofia.md           ← new coder, stats-anxious, R track (retention cliff)
    student-kenji.md           ← stats-strong, tidyverse-naive, demands rigor (R)
    student-aisha.md           ← fluent R, new to Python AND to graphs (Python track)
    student-david.md           ← rusty, time-poor manager (async promise stress test)
    _student-template.md       ← copy to add more personas
  settings.students.json       ← permissions to MERGE into .claude/settings.json
harness/
  run-students.sh              ← headless loop: each persona → its subagent → runs/<id>/
  aggregate.R                  ← builds the cross-persona matrix + summary
orchestrate-students.md        ← prompt to drive the cohort from a main CC session instead
```

Outputs land in `runs/<id>/` (`journal.md`, `report.md`, `scores.json`, `project/`) plus
`runs/_summary.md`, `runs/_matrix_friction.csv`, `runs/_matrix_clarity.csv`.

## Install (one time)

1. Copy `.claude/agents/` and `harness/` into the repo root.
2. **Merge permissions.** Add the `allow` and `deny` entries from
   `.claude/settings.students.json` into your existing `.claude/settings.json`
   `permissions` block. The repo's current allow-list only has *read-only* Playwright
   tools; the students need `browser_navigate`, `browser_click`, `browser_type`, etc.,
   plus Python/file-write — without these, an unattended run stalls on prompts.
   Confirm the Playwright tool names match your installed server with `claude mcp list`.
3. Ensure Python is available (the Python-track personas use it). R is handled by the
   repo's `session-start.sh`.

## Run

**Option A — pilot one persona, supervised (do this first).** Validates that a persona
actually stays in character and runs the code, while you watch:
```
claude
> Use the student-sofia subagent to take SYSEN 5470 in full per its brief,
  run the real code, and write outputs to runs/sofia/.
```

**Option B — headless batch.** All six, sequential, then auto-aggregate:
```
bash harness/run-students.sh
# or a subset:
bash harness/run-students.sh sofia priya
```
Key env vars: `MODEL` (default `sonnet`), `PERMISSION_MODE`
(`acceptEdits` default → `dontAsk` for headless → `bypassPermissions` for fully
unattended, **container only**), `OUTPUT_FORMAT`.

**Option C — orchestrated from a main session.** Paste `orchestrate-students.md` into a
main Claude Code session; it runs preflight, dispatches all six, aggregates, and writes
a synthesis (`runs/_registrar-notes.md`).

Then read `runs/_summary.md`. A friction row red across *many* personas = a course
problem (fix the lab); red for *one* = a fit problem for that learner type.

## Honest caveats

- **Tokens.** Subagent-heavy / parallel runs can cost several times a single-thread
  session. Pilot one persona before launching all six.
- **Headless permission gotchas.** In `-p` mode, 3 consecutive or 20 total safety-blocks
  abort the run — a failed run usually means a missing allow-rule or a too-broad action;
  check `logs/`. `--dangerously-skip-permissions` can still prompt on first use and
  refuses to run as root; `--permission-mode dontAsk` is the cleaner headless choice.
  Run unattended batches in an isolated container.
- **Stats-aversion is performed, not felt.** The model knows the statistics, so Sofia's
  "struggle" is a simulation. Weight the *coding-friction* findings (authentic) above the
  *stats-anxiety* findings, and treat the latter as directional.
- **Sketches are simulated** — you get a judgment about whether sketching *would* help,
  not the real hand-drawing experience.
- **The project report is a simulation artifact, not a submission.** Your AI-use policy
  forbids AI-written report prose; the agent writes report-shaped text only to surface
  the project *experience*. Don't reuse it.
- **Run each persona 2–3× if you can.** Single runs are noisy; stable findings are the
  ones that repeat. AI personas are cheap pre-testing, not a substitute for real students.

---

## `SETUP-AGENT-HANDOFF.md`

# SETUP-AGENT HANDOFF — install the SYSEN 5470 AI-student system

**You are a setup agent (Claude Code) working at the root of the `timothyfraser/netsci`
repository.** Your job is to install the AI-student walkthrough system from this bundle
into the repo, verify the environment, and stage the one human-review step — then stop
and report. A human (Tim) will do the final permission merge and run the cohort in a
fresh session.

This automates the "Install" section of `README-ai-students.md`, stopping short of the
permission merge.

---

## Hard guardrails — do NOT cross these

- ❌ **Do not modify `.claude/settings.json`.** You will *stage* a proposed merge to a
  side file. The human applies it.
- ❌ **Do not run a student cohort** (no `run-students.sh`, no invoking `student-*`
  subagents). Setup only. The first real run happens later, in a fresh session.
- ❌ **Do not `git commit`, `git push`, or alter git history.**
- ❌ **Do not read, print, copy, or echo `.env` or any secret.**
- ✅ Everything you do is additive and reversible. If a step is ambiguous, stop and ask.

---

## Step 0 — Confirm inputs

1. Confirm you are at the repo root: it should contain `.claude/`, `code/`, and `CLAUDE.md`.
   If not, stop and ask for the repo path.
2. Locate the unzipped bundle. Default expected path: `./netsci-ai-students/`. If it's
   elsewhere, ask the human for the path and use it as `$BUNDLE` below.
3. Print what you found (repo root path, bundle path) and proceed only if both exist.

## Step 1 — Place files (additive)

From `$BUNDLE`, copy into the repo:

- `.claude/agents/`  → repo `.claude/agents/`  (new directory; if it already exists, do
  **not** overwrite any file — list collisions and ask).
- `harness/`         → repo `harness/`
- `orchestrate-students.md`, `README-ai-students.md`, `SETUP-AGENT-HANDOFF.md` → repo root
- `.claude/settings.students.json` → repo `.claude/settings.students.json`  (staged, not merged)

Then make the script executable: `chmod +x harness/run-students.sh`.

Confirm by listing `.claude/agents/` (expect `_shared/student-brief.md`, six
`student-*.md`, `_student-template.md`) and `harness/` (expect `run-students.sh`,
`aggregate.R`).

## Step 2 — Stage the settings merge (DO NOT APPLY)

Produce a reviewed-ready proposal without touching `.claude/settings.json`:

```bash
python3 - <<'PY'
import json
base = json.load(open('.claude/settings.json'))
add  = json.load(open('.claude/settings.students.json'))
base.setdefault('permissions', {})
added = {}
for key in ('allow','deny'):
    cur = base['permissions'].get(key, [])
    new = add.get('permissions', {}).get(key, [])
    merged = list(dict.fromkeys([*cur, *new]))     # dedup, preserve order
    added[key] = [x for x in new if x not in cur]
    base['permissions'][key] = merged
json.dump(base, open('.claude/settings.proposed.json','w'), indent=2)
print("ADDED allow:", *added['allow'], sep="\n  ")
print("ADDED deny:",  *added['deny'],  sep="\n  ")
PY
```

This writes `.claude/settings.proposed.json` (existing hooks and all other keys
preserved). Then write a `MERGE-ME.md` at repo root containing:
- The exact list of `allow` and `deny` entries that would be **added** (from the output above).
- This instruction for the human: *"Review `.claude/settings.proposed.json`; if it looks
  right, replace `.claude/settings.json` with it (or hand-add the listed entries). These
  grant the student agents Python, file-writes, and Playwright navigate/click/type."*

## Step 3 — Verify the environment (report, don't force-fix)

Run each check and record ✅ / ⚠️ / ❌:

1. **Playwright MCP** — `claude mcp list`. Confirm a server named exactly **`playwright`**
   is present/connected. The allow-list uses the prefix `mcp__playwright__browser_*`; if
   the server has a different name, the prefix won't match — note the correct name in
   `MERGE-ME.md` so the human can fix the allow entries.
2. **R** — `Rscript --version` (present?). Packages are otherwise handled by
   `.claude/session-start.sh`.
3. **Python** — `python3 --version` and `pip3 --version` (the Python-track personas need them).
4. **Course code** — confirm `code/01_*` … `code/11_*` exist and each contains an
   `example.R` and/or `example.py`.
5. **Course site reachable** — `curl -sI https://timothyfraser.com/netsci | head -1`.

## Step 4 — Close the aggregator's dependency gap

`harness/aggregate.R` needs **`jsonlite`** and **`purrr`**, which are NOT in the repo's
`session-start.sh` baseline. Install them if missing:

```bash
Rscript -e 'p <- c("jsonlite","purrr"); m <- setdiff(p, rownames(installed.packages())); if (length(m)) install.packages(m, repos="https://cloud.r-project.org"); cat("ok\n")'
```

(If the network blocks CRAN in your environment, skip and list `jsonlite`, `purrr` as a
TODO for the human in your final report.)

## Step 5 — Validate the dropped-in files parse

1. **Subagents** — each `.claude/agents/student-*.md` and `_student-template.md` must have
   YAML frontmatter with a `name:`. Confirm the six names are unique:
   `student-priya/marcus/sofia/kenji/aisha/david`.
2. **aggregate.R** — syntax-only check (do **not** execute):
   `Rscript -e 'invisible(parse("harness/aggregate.R")); cat("parse ok\n")'`
3. **run-students.sh** — `bash -n harness/run-students.sh && echo "sh ok"`.

## Step 6 — Create runtime dirs and ignore outputs

```bash
mkdir -p runs logs
# keep generated student outputs/logs out of version control
grep -qxF 'runs/'  .gitignore 2>/dev/null || echo 'runs/'  >> .gitignore
grep -qxF 'logs/'  .gitignore 2>/dev/null || echo 'logs/'  >> .gitignore
grep -qxF '.claude/settings.proposed.json' .gitignore 2>/dev/null || echo '.claude/settings.proposed.json' >> .gitignore
```

## Step 7 — Final report (and then stop)

Print a checklist and the handoff back to the human. Use this shape:

```
SETUP COMPLETE — review before merging.

Placed:        .claude/agents/ (7 files), harness/ (2 files), docs at root  [✅/❌]
Settings:      staged .claude/settings.proposed.json (NOT applied)          [✅/❌]
Playwright MCP: server 'playwright' connected                              [✅/⚠️/❌ + note]
R / Rscript:                                                               [✅/❌]
Python / pip:                                                              [✅/❌]
code/01..11 with example scripts:                                         [✅/❌]
Course site reachable:                                                    [✅/❌]
jsonlite + purrr installed:                                               [✅/⚠️/❌]
Files parse (subagents / aggregate.R / run-students.sh):                  [✅/❌]
runs/ logs/ created, .gitignore updated:                                  [✅/❌]

YOUR TURN, TIM:
1. Review .claude/settings.proposed.json against MERGE-ME.md, then make it your
   .claude/settings.json.
2. (If flagged) install missing R packages / fix the Playwright server-name prefix.
3. In a FRESH session, pilot one persona first:
     claude
     > Use the student-sofia subagent to take SYSEN 5470 in full per its brief and
       write outputs to runs/sofia/.
   Then run the full cohort:  bash harness/run-students.sh
```

Do not proceed past this report. Do not start a cohort run.

---

## `code/01_build-a-network/README.md`

# Case Study 01 — Build a Network

> Interactive lab: [`docs/case-studies/build-a-network.html`](../../docs/case-studies/build-a-network.html)
>
> Skill: **Identify** · Data: synthetic bipartite supplier ↔ component
> network (200 nodes, 577 edges)

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

# Run inside an RStudio session to see the plot interactively; from
# Rscript it goes to the default device.
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


# 1. Single-Node Join ########################################################
#
# Goal: tag each edge with a TRAIT of its START station — was it in a
# majority-Black block group or not?

## 1.1 The basic left_join ###################################################

# The key insight: the ID variable has a different NAME in each table.
#   - in `edges` it's called `start_code`
#   - in `stations` it's called `code`
# In dplyr we say `by = c("start_code" = "code")`.
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

ggplot(stat, aes(x = start_black, y = end_black, fill = percent)) +
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
# `code` -> `start_code` first, which is what most pipelines do).
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
# matrix.
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

ggplot(station_totals, aes(x = trips)) +
  geom_histogram(bins = 40, fill = "#3a8bc6") +
  labs(x     = "trips touching this station (in or out)",
       y     = "# stations",
       title = "Resolution A — station-level trip volume") +
  theme_classic(base_size = 13)

# Resolution B: 12x12 heatmap. Diagonal heavier = neighborhood stickiness.
ggplot(nbhd_pairs,
       aes(x = start_nbhd, y = end_nbhd, fill = trips)) +
  geom_tile(color = "white") +
  scale_fill_viridis(option = "mako") +
  labs(title = "Resolution B — neighborhood x neighborhood",
       x     = "Starting neighborhood",
       y     = "Ending neighborhood") +
  theme_classic(base_size = 12) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

# Resolution C: 4x4 heatmap with the percentages drawn ON the cells.
ggplot(q_pairs,
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


# 4. The point ###############################################################
#
# Resolution A is a hairball. Resolution B (12x12) shows neighborhood
# stickiness — the diagonal is heavier. Resolution C (4x4) makes the
# equity question legible: how much ridership stays in-quintile vs
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
# matrix.
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
# Each one captures a DIFFERENT intuition for "important":
#   - DEGREE: how many neighbors. Local. Hub-detection.
#   - BETWEENNESS: how often this node lies on a shortest path between
#     two other nodes. Global. Bridge-detection.
#   - CLOSENESS: 1 / mean distance to every other node. Reach.
#   - EIGENVECTOR: central if your neighbors are central. Influence.

# All four computed in one tidy table, so we can compare them directly.
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

plot(
  g,
  layout       = igraph::layout_with_fr(g, weights = E(g)$weight, niter = 200),
  vertex.size  = 1 + 8 * (V(g)$btwn / max(V(g)$btwn)),
  vertex.color = V(g)$col,
  vertex.label = NA,
  edge.color   = adjustcolor("grey50", alpha.f = 0.2),
  edge.width   = 0.4,
  main         = "Node size = betweenness. Red = planted bridges."
)


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

for (metric in c("degree", "betweenness", "closeness", "eigenvector")) {
  top5 <- cent |>
    arrange(desc(.data[[metric]])) |>
    head(5) |>
    pull(node_id)
  g_test <- igraph::delete_vertices(g, top5)
  cat(sprintf("   remove top-5 by %-12s -> LCC = %d\n",
              metric, lcc_size(g_test)))
}


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
# Each one captures a DIFFERENT intuition for "important":
#   - DEGREE: how many neighbors. Local. Hub-detection.
#   - BETWEENNESS: how often this node lies on a shortest path
#     between two other nodes. Global. Bridge-detection.
#   - CLOSENESS: 1 / mean distance to every other node. Reach.
#   - EIGENVECTOR: a node is central if its neighbors are central.
#     Recursive. Influence.

# All four computed in one tidy table, so we can compare them directly.
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
# agree on the *order* of nodes (not their magnitudes).

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

results |> mutate(across(-k, ~round(., 3))) |> print()
cat(sprintf("🧪 At k=10: random=%.3f  out_degree=%.3f  betweenness=%.3f\n",
            results$random[results$k == 10],
            results$out_degree[results$k == 10],
            results$betweenness[results$k == 10]))


# 4. Visualize ###############################################################

results_long <- results |>
  pivot_longer(-k, names_to = "strategy", values_to = "coverage")

ggplot(results_long,
       aes(x = k, y = coverage, color = strategy, shape = strategy)) +
  geom_line() +
  geom_point(size = 2.5) +
  scale_y_continuous(limits = c(0, 1.02)) +
  labs(x     = "# of distribution centers removed (k)",
       y     = "supply coverage (fraction of retailers reachable)",
       title = "Targeted vs random DC failures") +
  theme_classic(base_size = 13)


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

## `code/06_dsm-clustering/README.md`

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
Rscript code/06_dsm-clustering/example.R
python  code/06_dsm-clustering/example.py
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

## `code/06_dsm-clustering/data/_generate.py`

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
    python code/06_dsm-clustering/data/_generate.py
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

## `code/06_dsm-clustering/example.R`

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
# Louvain and fast-greedy both want an undirected graph. We make an
# undirected copy whose edges mean "i and j depend on each other,
# in either direction." Standard DSM preprocessing.

g_undirected <- igraph::as.undirected(g, mode = "collapse")
g_undirected

# Louvain (igraph's `cluster_louvain`): greedy modularity optimization,
# moves nodes between communities to maximize modularity score.
louvain <- igraph::cluster_louvain(g_undirected)
cat(sprintf("📊 Louvain found %d modules. Modularity: %.3f\n",
            length(louvain), igraph::modularity(louvain)))

# Fast-greedy: agglomerative — start with each node in its own community,
# repeatedly merge the pair whose merge most increases modularity.
fg <- igraph::cluster_fast_greedy(g_undirected)
cat(sprintf("📊 Fast-greedy found %d modules. Modularity: %.3f\n",
            length(fg), igraph::modularity(fg)))


# 2. Compare to ground truth #################################################
#
# Our synthetic data planted 8 modules. The Adjusted Rand Index (ARI)
# measures how well two clusterings agree, corrected for chance:
# 1.0 = perfect agreement, 0.0 = chance, < 0 = worse than chance.

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
# at the top, like an actual matrix.
par(mfrow = c(1, 2))
image(t(A)[, nrow(A):1], col = c("white", "black"), axes = FALSE,
      main = "DSM — original order")
image(t(A_sorted)[, nrow(A_sorted):1], col = c("white", "black"), axes = FALSE,
      main = "DSM — reordered by Louvain")
par(mfrow = c(1, 1))


# 4. Cascade simulation ######################################################
#
# When component C037 fails, every component that depends on it can
# fail too. We bound to k hops because in a densely-coupled DSM an
# unbounded cascade reaches everything. The interesting question:
# how many fall in the FIRST FEW HOPS?

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

## `code/06_dsm-clustering/example.py`

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
# Louvain and fast-greedy both want an undirected graph. We make an
# undirected copy whose edges represent "i and j depend on each other,
# in either direction." This is the standard DSM preprocessing.

g_undirected = g.as_undirected(mode="collapse")
print(g_undirected.summary())

# Louvain (igraph's `community_multilevel`): greedy modularity
# optimization, moves nodes between communities to maximize modularity.
louvain = g_undirected.community_multilevel()
print(f"📊 Louvain found {len(louvain)} modules. Modularity: {louvain.modularity:.3f}")

# Fast-greedy: agglomerative — start with each node in its own community,
# repeatedly merge the pair whose merge most increases modularity.
fg = g_undirected.community_fastgreedy().as_clustering()
print(f"📊 Fast-greedy found {len(fg)} modules. Modularity: {fg.modularity:.3f}")


# 2. Compare to ground truth #################################################
#
# Our synthetic data planted 8 modules. The Adjusted Rand Index (ARI)
# measures how well two clusterings agree, corrected for chance:
# 1.0 = perfect agreement, 0.0 = chance, < 0 = worse than chance.

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

## `code/06_dsm-clustering/functions.R`

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

## `code/06_dsm-clustering/functions.py`

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

## `code/07_permutation/README.md`

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
Rscript code/07_permutation/example.R
python  code/07_permutation/example.py
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

## `code/07_permutation/data/_generate.py`

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
    python code/07_permutation/data/_generate.py
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

## `code/07_permutation/example.R`

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
#' But — *random with respect to what?* If your network has community
#' structure that you're not controlling for, shuffling labels
#' everywhere gives you a too-easy null. The right comparison is
#' often a BLOCK permutation: shuffle labels within community.
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

null_blocked <- numeric(n_perm)
for (i in seq_len(n_perm)) {
  g_perm <- permute_labels(g, "demo", block_by = "neighborhood")
  null_blocked[i] <- assort_by(g_perm, "demo")
}
p_blocked <- mean(null_blocked >= observed)
cat(sprintf("🧪 Block-permuted null: mean = %+.4f  sd = %.4f  p = %.3f\n",
            mean(null_blocked), sd(null_blocked), p_blocked))


# 4. Visualize ###############################################################

null_df <- bind_rows(
  tibble(null = "Unblocked",      value = null_unblocked),
  tibble(null = "Block-permuted", value = null_blocked)
)

ggplot(null_df, aes(x = value, fill = null)) +
  geom_histogram(alpha = 0.6, position = "identity", bins = 30) +
  geom_vline(xintercept = observed, linetype = "dashed") +
  scale_fill_manual(values = c("Unblocked"      = "#3a8bc6",
                               "Block-permuted" = "#e07b3a")) +
  labs(x     = "Nominal assortativity by `demo`",
       y     = "# of permutations",
       title = "Two null models, two p-values",
       fill  = "Null model") +
  theme_classic(base_size = 13)


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


# 6. Learning Check ##########################################################
#
# QUESTION: What is the *block-permuted* p-value for assortativity by
# `demo`? (Use neighborhood as the block. 500 permutations, seed 42.)
# Report to 3 decimal places.

cat(sprintf("\n📝 Learning Check answer: %.3f\n", p_blocked))

cat("\n🎉 Done. Move on to the case study report when you're ready.\n")
```

---

## `code/07_permutation/example.py`

```python
"""Case Study 07 — Network Permutation Testing (Python track).

The lab walked you through a key idea: when you compute a network
statistic (homophily, assortativity, mean within-group edge weight),
you need a NULL MODEL to know if the value you saw is "real" or just
noise. The null model says "what would we expect if labels were
random?"

But — and this is the crucial part — *random with respect to what?*
If your network has community structure that you're not controlling
for, shuffling labels everywhere can give you a too-easy null. The
right comparison is often a **block permutation**: shuffle labels
within community.

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

null_blocked = np.empty(n_perm)
for i in range(n_perm):
    g_perm = permute_labels(g, "demo", block_by="neighborhood", rng=rng)
    null_blocked[i] = assort_by(g_perm, "demo")

p_blocked = float(np.mean(null_blocked >= observed))
print(f"🧪 Block-permuted null: mean = {null_blocked.mean():+.4f}  "
      f"sd = {null_blocked.std():.4f}  p = {p_blocked:.3f}")


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


# 6. Learning Check ##########################################################
#
# QUESTION: What is the *block-permuted* p-value for assortativity by
# `demo`? (Use neighborhood as the block. 500 permutations.) Report
# to 3 decimal places.

print(f"\n📝 Learning Check answer: {p_blocked:.3f}")

print("\n🎉 Done. Move on to the case study report when you're ready.")
```

---

## `code/07_permutation/functions.R`

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

## `code/07_permutation/functions.py`

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

## `code/08_sampling/README.md`

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
Rscript code/08_sampling/example.R
python  code/08_sampling/example.py
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

## `code/08_sampling/data/_generate.py`

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
    python code/08_sampling/data/_generate.py
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

## `code/08_sampling/example.R`

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

# Use Miami as our point of interest (POI). Project to a meter-based
# CRS so the 200 km buffer is geometrically meaningful, then back.
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

bind_rows(
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


# 4. Which strategy best preserves avg_edgeweight? ###########################
#
# Preservation = max absolute deviation from the population time
# series. Smaller deviation = better preservation. We pick the winner
# by which strategy minimizes that max.

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
print(mad)
winner <- names(which.min(mad))
cat(sprintf("📊 Best preservation: %s\n", winner))


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

## `code/08_sampling/example.py`

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

# Use Miami as our point of interest (POI). Project to a meter-based
# CRS so the 200 km buffer is geometrically meaningful, then back.
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
# We measure preservation as the *maximum absolute deviation* from
# the population time series. Smaller = better preservation.

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
print(f"📊 Best preservation: {winner}")


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

## `code/08_sampling/functions.R`

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

## `code/08_sampling/functions.py`

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

## `code/09_counterfactual/README.md`

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
Rscript code/09_counterfactual/example.R
python  code/09_counterfactual/example.py
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

## `code/09_counterfactual/data/_generate.py`

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
    python code/09_counterfactual/data/_generate.py
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

## `code/09_counterfactual/example.R`

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
cat(sprintf("🧪 Counterfactual APL change (mean):     %+.5f\n", mean(diffs)))
cat(sprintf("🧪 95%% CI on the change:                 [%+.5f, %+.5f]\n",
            ci[[1]], ci[[2]]))
cat(sprintf("📊 Effect significant at 95%%?            %s\n",
            if (ci[[2]] < 0 || ci[[1]] > 0) "True" else "False"))


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

print(p1)
print(p2)


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

## `code/09_counterfactual/example.py`

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
print(f"🧪 Counterfactual APL change (mean):     {diffs.mean():+.5f}")
print(f"🧪 95% CI on the change:                 [{ci_low:+.5f}, {ci_high:+.5f}]")
sig = ci_high < 0 or ci_low > 0
print(f"📊 Effect significant at 95%?            {'True' if sig else 'False'}")


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

## `code/09_counterfactual/functions.R`

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

## `code/09_counterfactual/functions.py`

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

## `code/10_gnn-by-hand/README.md`

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
python  code/10_gnn-by-hand/example.py    # Python track
Rscript code/10_gnn-by-hand/example.R     # R track (calls functions.py via reticulate)
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

## `code/10_gnn-by-hand/data/_generate.py`

```python
"""Generate the tiny + larger toy supply chain networks for case 10.

Two networks are produced:
  - tiny.{nodes,edges}.csv: 6-node hand-toy network mirroring the
    case study lab. Each node has 2 input features.
  - large.{nodes,edges}.csv: 200-node project-scale network with
    planted bottlenecks; same 2 features.

Both are deterministic.

Run:
    python code/10_gnn-by-hand/data/_generate.py
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

## `code/10_gnn-by-hand/example.R`

```r
#' @name example.R
#' @title Case Study 10 — GNN by Hand (R via reticulate)
#' @author <your-name-here>
#' @description
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
# neighbors. These two preprocessing tricks are the heart of a GCN — and
# both come straight from functions.py via the `gcn` handle.

A <- gcn$adjacency(nodes, edges, add_self_loops = TRUE)
cat("A (with self-loops):\n")
print(A)

A_norm <- gcn$normalize(A)
cat("A_norm (symmetric-normalized):\n")
print(round(A_norm, 3))


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

## `code/10_gnn-by-hand/example.py`

```python
"""Case Study 10 — GNN by Hand (Python track).

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
# neighbors. These two preprocessing tricks are the heart of a GCN.

A = adjacency(nodes, edges, add_self_loops=True)
print("A (with self-loops):")
print(A.astype(int))

A_norm = normalize(A)
print("A_norm (symmetric-normalized):")
print(A_norm.round(3))


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

## `code/10_gnn-by-hand/functions.R`

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

## `code/10_gnn-by-hand/functions.py`

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

## `code/11_gnn-xgboost/README.md`

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
python code/11_gnn-xgboost/example.py    # full pipeline
Rscript code/11_gnn-xgboost/example.R    # raw + lag variant
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

## `code/11_gnn-xgboost/data/_generate.py`

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
    python code/11_gnn-xgboost/data/_generate.py
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

## `code/11_gnn-xgboost/example.R`

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

panel <- add_gnn_embeddings(panel, suppliers, edges)
print(head(panel, 10))
cat("✅ Added 1-hop and 2-hop GNN embeddings of lag_rate.\n")


# 3. Merge static features ###################################################
#
# Join the suppliers table (tier, capacity, region, geo_risk) onto the
# panel and one-hot encode region. XGBoost can take factors directly, but
# we keep the encoding explicit so the feature columns are obvious.

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


# 6. Feature importance ######################################################
#
# What does the full model think the most important features are? A high
# gain on `gnn_1hop` or `gnn_2hop` is the visible signature of the GNN
# piece earning its keep.

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

## `code/11_gnn-xgboost/example.py`

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

A = build_adjacency(suppliers, edges)
print(f"📊 Adjacency: {A.shape}, row-sum max = {A.sum(axis=1).max():.2f}")

panel = add_gnn_embeddings(panel, suppliers, A)
print(panel.head(10))
print("✅ Added 1-hop and 2-hop GNN embeddings of lag_rate.")


# 3. Merge static features ###################################################

panel = panel.merge(suppliers, on="supplier_id", how="left")
# one-hot region (XGBoost can handle this directly but we keep it explicit)
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


# 6. Feature importance ######################################################
#
# What does the full model think the most important features are?
# A high gain on `gnn_1hop` or `gnn_2hop` is the visible signature
# of the GNN piece earning its keep.

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

## `code/11_gnn-xgboost/functions.R`

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

## `code/11_gnn-xgboost/functions.py`

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

## `harness/aggregate.R`

```r
#!/usr/bin/env Rscript
# ============================================================================
# aggregate.R — turn per-student scores.json files into a cross-persona view.
#
#   Rscript harness/aggregate.R runs
#
# Reads runs/<id>/scores.json for every persona and writes:
#   runs/_matrix_friction.csv   lab x student friction (1-5)
#   runs/_matrix_clarity.csv    lab x student clarity  (1-5)
#   runs/_summary.md            overall ratings, retention cliffs, tallied fixes
#
# Style: tidyverse, base pipe |>, per the repo CLAUDE.md.
# ============================================================================
suppressPackageStartupMessages({
  library(jsonlite); library(dplyr); library(tidyr)
  library(purrr); library(readr); library(stringr); library(tibble)
})

`%||%` <- function(a, b) if (is.null(a) || length(a) == 0) b else a

args <- commandArgs(trailingOnly = TRUE)
runs_dir <- if (length(args) >= 1) args[[1]] else "runs"

score_files <- list.files(runs_dir, pattern = "^scores\\.json$",
                          recursive = TRUE, full.names = TRUE)
if (length(score_files) == 0) stop("No scores.json found under ", runs_dir)

students <- map(score_files, ~ fromJSON(.x, simplifyVector = FALSE))
ids <- map_chr(students, ~ .x$student %||% "unknown")
message("Found ", length(students), " students: ", paste(ids, collapse = ", "))

# ---- per-lab long table ----------------------------------------------------
labs_long <- map_dfr(students, function(s) {
  if (is.null(s$labs) || length(s$labs) == 0) return(tibble())
  map_dfr(s$labs, function(l) {
    tibble(
      student  = s$student %||% NA_character_,
      lab      = str_c(l$id %||% "??", "_", l$name %||% ""),
      friction = as.numeric(l$friction %||% NA),
      clarity  = as.numeric(l$clarity  %||% NA),
      minutes  = as.numeric(l$minutes  %||% NA),
      ran      = l$ran %||% NA_character_
    )
  })
})
if (nrow(labs_long) == 0)
  stop("No per-lab entries found in any scores.json (check the 'labs' arrays).")

write_matrix <- function(df, value_col, path) {
  m <- df |>
    select(lab, student, all_of(value_col)) |>
    pivot_wider(names_from = student, values_from = all_of(value_col)) |>
    arrange(lab)
  write_csv(m, path)
  m
}
fric_mat <- write_matrix(labs_long, "friction", file.path(runs_dir, "_matrix_friction.csv"))
clar_mat <- write_matrix(labs_long, "clarity",  file.path(runs_dir, "_matrix_clarity.csv"))

# ---- overall per-student table ---------------------------------------------
overall <- map_dfr(students, function(s) {
  tibble(
    student        = s$student %||% NA_character_,
    track          = s$track %||% NA_character_,
    setup_friction = as.numeric(s$setup_friction %||% NA),
    almost_dropped = s$almost_dropped %||% NA_character_,
    recommend      = as.numeric(s$recommend %||% NA),
    job_ready      = as.numeric(s$job_ready %||% NA),
    total_hours    = sum(as.numeric(unlist(s$weekly_hours %||% list())), na.rm = TRUE)
  )
})

# ---- retention cliffs: labs where >=2 students hit friction >=4 ------------
cliffs <- labs_long |>
  filter(!is.na(friction)) |>
  group_by(lab) |>
  summarise(n_high = sum(friction >= 4), who = str_c(student[friction >= 4], collapse = ", "),
            .groups = "drop") |>
  filter(n_high >= 2) |>
  arrange(desc(n_high))

dropped <- overall |>
  filter(!is.na(almost_dropped) & almost_dropped != "null" & almost_dropped != "") |>
  select(student, almost_dropped)

# ---- tally fixes named by >=2 students (loose normalized match) ------------
fixes <- map_dfr(students, function(s) {
  fx <- unlist(s$top_fixes %||% list())
  if (length(fx) == 0) return(tibble(student = character(), fix = character()))
  tibble(student = s$student %||% NA_character_, fix = fx)
})
if (nrow(fixes) == 0) fixes <- tibble(student = character(), fix = character(), key = character())
fixes <- fixes |>
  filter(!is.na(fix), str_trim(fix) != "") |>
  mutate(key = fix |> str_to_lower() |> str_replace_all("[^a-z0-9 ]", "") |> str_squish())

fix_tally <- fixes |>
  group_by(key) |>
  summarise(n = n_distinct(student),
            example = first(fix),
            who = str_c(unique(student), collapse = ", "), .groups = "drop") |>
  filter(n >= 2) |>
  arrange(desc(n))

# ---- write summary.md ------------------------------------------------------
overall_rows <- overall |>
  mutate(across(everything(), as.character)) |>
  pmap_chr(function(student, track, setup_friction, almost_dropped, recommend, job_ready, total_hours)
    str_glue("| {student} | {track} | {setup_friction} | {recommend} | {job_ready} | {total_hours} | {almost_dropped} |"))
overall_tbl <- c(
  "| student | track | setup_friction | recommend | job_ready | total_hrs | almost_dropped |",
  "|---|---|---|---|---|---|---|", overall_rows)

md <- c(
  "# SYSEN 5470 — AI Student Run Summary", "",
  str_glue("_{length(students)} personas: {paste(ids, collapse = ', ')}_"), "",
  "## Overall ratings", "",
  overall_tbl, "",
  "## Retention cliffs (labs where 2+ students hit friction >= 4)", "",
  if (nrow(cliffs) == 0) "_None — no lab tripped up 2+ students._" else
    c("| lab | # high-friction | who |", "|---|---|---|",
      pmap_chr(cliffs, function(lab, n_high, who) str_glue("| {lab} | {n_high} | {who} |"))),
  "",
  "## 'Almost dropped' moments", "",
  if (nrow(dropped) == 0) "_No persona reported almost dropping._" else
    c("| student | lab |", "|---|---|",
      pmap_chr(dropped, function(student, almost_dropped) str_glue("| {student} | {almost_dropped} |"))),
  "",
  "## Highest-ROI fixes (named by 2+ different students)", "",
  if (nrow(fix_tally) == 0) "_No fix was independently named by 2+ students._" else
    c("| # students | fix (example wording) | who |", "|---|---|---|",
      pmap_chr(fix_tally, function(key, n, example, who) str_glue("| {n} | {example} | {who} |"))),
  "",
  "## How to read this", "",
  "- A **friction row red across many personas** (see `_matrix_friction.csv`) = a course problem; fix the lab.",
  "- A row red for **one** persona = a fit problem for that learner type; add an optional on-ramp, don't rebuild.",
  "- Compare **stats-strong** (kenji, priya) vs **stats-averse** (sofia, marcus) on labs 07 & 09 to locate the inference-scaffolding gap.",
  "- Compare **Python track** (priya, marcus, aisha) vs **R track** (sofia, kenji, david) on shared labs to catch track-parity gaps.",
  ""
)
writeLines(unlist(md), file.path(runs_dir, "_summary.md"))

message("Wrote: ",
        file.path(runs_dir, "_summary.md"), ", _matrix_friction.csv, _matrix_clarity.csv")
```

---

## `orchestrate-students.md`

# Orchestration prompt — run the AI student cohort

Paste the block below into a **main Claude Code session at the repo root** when you'd
rather drive the cohort interactively than via the headless `run-students.sh` harness.
The main session acts as **registrar**: it dispatches each persona subagent, then
synthesizes across their reports.

> Sequential dispatch is recommended (cheaper, and easier to keep each persona honest).
> To parallelize, tell the session to run them concurrently — but expect roughly several
> times the token cost, and noisier fidelity.

---

```
You are the registrar for an AI-student evaluation of SYSEN 5470. Six student
personas are defined as subagents in .claude/agents/ (student-priya, student-marcus,
student-sofia, student-kenji, student-aisha, student-david). Each reads the shared
brief at .claude/agents/_shared/student-brief.md and inhabits a fixed skill profile.

Do this:

1. PREFLIGHT. Confirm the environment is ready and report a short checklist:
   - Playwright MCP reachable (the students browse https://timothyfraser.com/netsci).
   - R available (Rscript runs); Python available if any persona uses the Python track
     (priya, marcus, aisha do).
   - .claude/settings.json includes the student allow-list (Bash python/pip, file
     writes, Playwright navigate/click/type). If navigation tools aren't permitted,
     STOP and tell me what to add — otherwise the runs will stall.
   - A runs/ directory exists (create it).
   If anything's missing, list exactly what I need to fix before proceeding.

2. DISPATCH, one persona at a time, in this order: sofia, david, marcus, kenji,
   aisha, priya (struggling students first, so problems surface early). For each:
   "Use the student-<id> subagent to take SYSEN 5470 in full per its brief, run the
   real code, and write journal.md, report.md, scores.json, and project/ into
   runs/<id>/." Wait for it to finish and confirm runs/<id>/report.md exists before
   starting the next. If a persona fails or breaks character, note it and continue.

3. AGGREGATE. After all six finish, run: Rscript harness/aggregate.R runs
   Then read runs/_summary.md and the two matrix CSVs.

4. SYNTHESIZE. Write runs/_registrar-notes.md with:
   - The 3–5 labs that are COURSE problems (red across multiple, different personas),
     each with the specific friction quoted from the relevant report.md.
   - The issues that are FIT problems (one persona only) — and which persona type.
   - The inference-scaffolding verdict: compare labs 07 (permutation) and 09
     (counterfactual MC) across stats-averse (sofia, marcus) vs stats-strong
     (kenji, priya).
   - The track-parity verdict: Python (priya, marcus, aisha) vs R (sofia, kenji,
     david) on shared labs.
   - The retention cliff: where did anyone "almost drop," and is it clustered?
   - A ranked, deduplicated list of the highest-ROI fixes (those named by 2+ students),
     each tagged with which personas asked for it.
   Keep it concrete and quote the students. Do not soften the criticism — blunt is useful.

Begin with the PREFLIGHT checklist and wait for my go-ahead before dispatching.
```

---

**Resilience tip.** A full 3-week walkthrough is a long task for one subagent. The
brief already has each student append to `journal.md` as they go, so progress survives.
If a persona's single run is too long, dispatch it **once per course-week** instead
("...do Week 1 only; resume from your journal"), three calls per persona.

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

