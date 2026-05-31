# `.canvas/` — Canvas course scaffolding for SYSEN 5470

Starter content for the Cornell **Canvas** site that mirrors the
[course website](https://timothyfraser.com/netsci/). The goal is deliberately
modest: Canvas should **cleanly structure submissions, deadlines, and links** —
and then send students to the (much nicer) website to actually do the work.

## What's here
- A **home page** with shortcut links to the key website pages.
- **43 assignments** — one per real submission item on the site: a drawing and a
  code "I ran the code" Learning Check and a case-study Learning Check for each
  of the 11 case studies, plus a weekly Ed Discussion and Office Hours, three
  project case studies, and a final presentation.
- **5 modules** (Getting Started · Week 1 · Week 2 · Week 3 · Wrapping Up) of
  website links, kept non-duplicative with the assignments.
- Each assignment is a **branded HTML card** (matching the site's neon-green-on-
  near-black theme) with the assignment title, the related case study, a
  completion-vs-points grading tag, and a button to the relevant website page.

Assignments are sorted into **weighted groups**: Drawings 20% · Case Study
Completion 20% · Weekly Homework (the project) ×3 = 60%.

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
