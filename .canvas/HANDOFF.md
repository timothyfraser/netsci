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
