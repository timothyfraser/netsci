# SYSEN 5470 → Canvas — Implementation Handoff

This folder is **course scaffolding only**. It contains ready-to-publish HTML
for a Canvas course (home page + 26 assignments + 5 modules) and two scripts:
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
| Assignment **groups** (weighted) | 5 | `manifest.json → assignment_groups` |
| **Assignments** | 26 | `assignments/*.html` + `canvas_plan.json` |
| **Modules** + items | 5 modules | `manifest.json → modules` |

### Submission units = 8 case-study TOPICS (not 11 labs)

The site has **11 lab pages / code folders**, but they roll up into **8
case-study topics** (the "What You'll Learn" list on the website home page).
Two topics bundle two labs each, and Centrality & Criticality absorbs Supply
Chain. **Canvas submission units are the 8 topics**, so students see 8 tidy
units instead of 11:

| Topic | Lab(s) it bundles | Due |
|---|---|---|
| 🕸️ Network Fundamentals | build-a-network | Wk 1 |
| 📐 Network Statistics | permutation | Wk 1 |
| 📊 Centrality & Criticality | centrality **+** supply-chain | Wk 2 |
| 🚦 Routing & Optimization | counterfactual | Wk 2 |
| 🧩 Clustering & Communities | dsm-clustering | Wk 2 |
| 🗺️ Visualization | aggregation | Wk 2 |
| 🤖 AI & Machine Learning | gnn-by-hand **+** gnn-xgboost | Wk 3 |
| 🗄️ Big Network Data | joins **+** sampling | Wk 3 |

Each topic produces **one drawing** and **one bundled Learning Check** (the
case-study Learning Check *and* the "I ran the code" check submitted together).
A two-lab topic's card lists both labs with deep links and asks for both.

### The five weighted assignment groups (sum = 100%)

| Group | Weight | Contains | Rule |
|---|---|---|---|
| **Drawings** | 20% | 8 drawings (1 per topic) | **drops the lowest 1** |
| **Case Study Completion** | 20% | 8 bundled Learning Checks + 3 weekly Ed Discussions + 3 weekly Office Hours + 1 Final Presentation (15 items) | **drops the lowest 1** |
| **Weekly Homework 1 · Project Case Study** | 20% | Project submission 1 | — |
| **Weekly Homework 2 · Project Case Study** | 20% | Project submission 2 | — |
| **Weekly Homework 3 · Project Case Study** | 20% | Project submission 3 (final) | — |

This matches the weighting you specified:
*drawings 20 · case-study completion (bundled LCs + Ed discussion + office
hours) 20 · weekly homeworks (= the project) 20 each.* The **drop-lowest-1**
rule on Drawings and Case Study Completion gives students one freebie in each
group for time-crunch weeks (Canvas group rule `rules[drop_lowest]=1`).

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

1. **Weighting** — exactly as you specified. Within the *Case Study Completion*
   group all items are `pass_fail` with `points_possible: 10` (Final Presentation
   `20`) so they weigh roughly equally. The relative split inside a weighted
   group only matters *within* that group.
2. **Due dates** — taken from `docs/calendar.html`: every weekly submission is
   due **Monday 9:00 AM America/New_York**. In summer that is EDT (UTC−4), so
   `due_at` is stored as `13:00:00Z`. Week 1 = 2026-06-29, Week 2 = 2026-07-06,
   Week 3 / final = 2026-07-13. Per-case-study items inherit their case study's
   week. Projects: submission 1 due Week 2, submissions 2 & 3 due the final
   deadline (the calendar's actual cadence — first project in Week 2, the
   remaining two by the final). Adjust in `manifest.json → due_dates` / `extras.projects`.
3. **Sketch ↔ case-study mapping** is **approximate**. The public
   `docs/sketchpad.html` has 11 prompts described as "a preview library… for
   case studies not yet built," and it does not map 1:1 to the 11 case studies
   (e.g. two aggregation-flavored sketches, one shared supply-chain/GNN
   neighborhood sketch). Each drawing card therefore links to the **Sketchpad
   page** (the correct destination regardless) and names its best-fit sketch in
   text. If you finalize the mapping, edit `sketch_title` / `sketch_anchor` per
   case study in `manifest.json`.
4. **Ed Discussion & Office Hours** are `submission_types: ["none"]` — they
   happen off-Canvas (Ed) or in a meeting, and you mark them complete. The cards
   link to the calendar / office-hours pages. If you wire up a real Ed LTI or a
   Canvas Discussion, switch the type accordingly.
5. **Final Presentation** is folded into *Case Study Completion* (completion-
   graded) so each Weekly Homework group stays cleanly = one project = 20%. Move
   it to a Weekly Homework group or its own group if you want it points-graded.

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
     rules[drop_lowest]=1                           # Drawings + Case Study groups only
PUT  /courses/:course/assignment_groups/:id        # update weight/position/rules
```
The **drop-lowest** freebie is a group *rule*: `rules[drop_lowest]=1`. Other
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
     assignment[due_at]=2026-06-29T13:00:00Z
     assignment[published]=true
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
- [ ] **Assignments** index shows 5 groups; group weights read 20/20/20/20/20
      and "Total 100%". (Grades → ⋮ → *Assignment Groups Weight* is enabled.)
- [ ] A drawing, a bundled Learning Check, and a project each render their card
      with the correct **grading pill** and a working website button. (A two-lab
      topic's Learning Check lists both labs with Lab + Code links.)
- [ ] The **Drawings** and **Case Study Completion** groups show "drop the lowest"
      (group → ⋮ → *Assignment Group Rules*).
- [ ] **Modules** shows Getting Started / Week 1 / Week 2 / Week 3 / Wrapping Up,
      each with external links opening the website in a new tab.
- [ ] Due dates show the three Mondays at 9:00 AM Eastern.

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
├── assignments/            ← 26 assignment bodies (one HTML fragment each)
│   ├── drawing-<topic>.html        (8 — one per topic)
│   ├── lc-<topic>.html             (8 — bundled case-study + code LC per topic)
│   ├── ed-week-{1,2,3}.html        (3)
│   ├── office-week-{1,2,3}.html    (3)
│   ├── project-{1,2,3}.html        (3)
│   └── final-presentation.html     (1)
├── build/
│   └── canvas_plan.json    ← generated machine-readable plan (push reads this)
└── scripts/
    ├── generate_html.py    ← manifest → HTML + plan + preview (stdlib only)
    └── push_to_canvas.py   ← plan → Canvas via REST (needs `requests` + env vars)
```
