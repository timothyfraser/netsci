# SYSEN 5470 Study Companion

A NotebookLM-based AI tutor for **SYSEN 5470: Network Science and Applications for Systems Engineering** (Cornell, Tim Fraser).

This folder contains everything needed to set up and maintain the class Study Companion. It is free, requires no infrastructure, and is designed to **support learning, not replace it**.

---

## What this is

The Study Companion is a [NotebookLM](https://notebooklm.google.com) notebook configured to act as a Socratic tutor for SYSEN 5470 students. It:

- Knows the course materials (syllabus, labs, readings) because they're loaded as sources
- Refuses to give direct answers to homework, learning checks, or lab questions
- Asks students questions back, helping them work through concepts on their own
- Generates flashcards, concept checks, and reflection prompts on demand
- Is grounded in course sources, so it cites specific labs/readings rather than inventing

## Why NotebookLM

- **Free** for students and instructor (no API costs, no subscriptions required)
- **Grounded retrieval** — answers come from uploaded course materials, not the open internet
- **Persistent persona** (up to 10,000 characters) configured once at the notebook level
- **No infrastructure** to maintain
- Students can't see the system persona, but the tool is designed to nudge, not enforce — the goal is to support good learning habits, not police bad ones

---

## Files in this folder

| File | What it is |
|------|-----------|
| `README.md` | This file |
| `study_companion_persona.md` | The system persona text to paste into NotebookLM's Configure Chat |
| `study_companion_prompts.md` | The prompt library to publish to students on Canvas |

---

## Initial setup (one-time)

1. **Create a new notebook** at [notebooklm.google.com](https://notebooklm.google.com). Name it `SYSEN 5470 Study Companion`.

2. **Upload course sources.** Recommended starter set:
   - Syllabus (PDF)
   - All rendered lab HTMLs as they're created
   - Any required readings (PDF or EPUB)
   - Lecture slide decks (PDF) and/or lecture transcripts
   - Module overviews or reading guides

   *Free tier limit: 50 sources per notebook. Plenty for a 3-week course.*

3. **Set the persona.** Click the gear icon in the chat panel → **Configure Chat** → **Custom** mode. Paste the entire contents of `study_companion_persona.md`. Save.

4. **Share the notebook** with the class. Use the share button to generate a read-only link, then post it on Canvas. Students access without needing to sign in beyond a Google account.

5. **Publish the prompt library.** Copy `study_companion_prompts.md` onto a Canvas page titled "Study Companion — Prompt Library." Link it from the course homepage.

6. **Run the Week 1 orientation activity** (described at the bottom of the prompt library) during the first synchronous session.

---

## Maintenance

### When you add a new lab
1. Render the lab to HTML.
2. Upload the HTML to the notebook as a new source.
3. (Optional) Re-test the Companion with a sample question from the new lab to confirm it retrieves correctly.

### When the course ends
- Archive a copy of the notebook for next year.
- Review your own logs (if any) and student feedback to decide which prompts to keep, cut, or add.

### Quota notes
Free tier gives each student:
- 50 daily chat queries per user
- 50 sources per notebook (instructor-side)
- 3 Audio Overviews per day

A typical 2–4 hour lab session uses 10–30 queries, well inside the limit.

---

## Design principles behind the tool

These are the principles the persona and prompt library encode. Worth knowing if you adapt or extend them:

1. **Nudge, don't enforce.** Students who want to cheat will cheat; the goal is to make the *right* path the easy path.
2. **Socratic by default.** The Companion's first move is almost always a question back.
3. **Concepts before code.** The Companion explains what an error category means, but won't fix the code. It explains what a function does, but won't write the assignment.
4. **Grounded in course materials.** Citations point to specific labs and readings. If something isn't in the sources, the Companion says so.
5. **Engineer's lens.** Every concept connects back to a real engineered system — supply chains, transit, power grids, crisis response.
6. **The sketchpad stays sacred.** Several prompts explicitly prepare students to draw rather than type.

---

## Known limitations

- **No usage logs.** You can't see what students are asking. If you want that signal, run a midterm survey or have students share Companion transcripts as part of a reflection assignment.
- **Persona leakage.** A determined student can extract the persona text. This is by design accepted — the philosophy is nudge over enforce.
- **Source freshness.** The notebook doesn't auto-sync from GitHub. You must manually upload new sources as labs are finalized.
- **Model behavior drift.** NotebookLM's underlying model updates periodically. Re-test the Companion at the start of each semester with 3–5 standard queries to confirm it still behaves Socratically.

---

## Iteration log

Use this section to record changes you make to the persona or prompt library between course offerings.

| Date | Change | Reason |
|------|--------|--------|
| _initial_ | Created v1 persona + 4-group prompt library | Pre-launch setup |
