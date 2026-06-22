# SYSEN 5470 — Network Science and Applications for Systems Engineering

Course repository for **SYSEN 5470** at Cornell, taught by [Tim Fraser][tf].
A graduate course on analyzing networked engineered systems — supply chains,
transit, power grids, disaster response — in R and Python.

## 🚀 Quick links

| | |
|---|---|
| 🌐 **Course website** (start here) | [timothyfraser.com/netsci][site] |
| 🎓 **Canvas** (assignments, grades, announcements) | [canvas.cornell.edu][canvas] |
| 💻 **Coding playground** (run code in your browser) | [playground][play] · [R][play-r] · [Python][play-py] |

## 📚 For students

On the **[course website][site]**: syllabus, calendar, assignments, case studies,
the four skills (Identify · Measure · Infer · Predict), readings, and the sketchpad.

In **this repository**:

| | |
|---|---|
| [`data/projects/`](data/projects) | Project datasets (100–500+ node networks), each with a README codebook and ready-to-run R + Python loaders |
| [`code/`](code) | Case-study teaching code, in parallel R and Python |
| [`quickstart/`](quickstart) | Get your environment set up |

## 💻 Coding playgrounds

Both [playgrounds][play] run **entirely in your browser** — no install — and come
preloaded with the project datasets:

- **[R][play-r]** — igraph, tidygraph, ggraph (via WebR)
- **[Python][play-py]** — pandas, networkx, matplotlib (via Pyodide)

On a phone, a tap-to-code block keyboard lets you write code without fighting the
on-screen keyboard.

## 🤖 Study Companion

A NotebookLM-based tutor configured to **help you think, not do your work** — with
chat commands like `/study`, `/glossary`, `/quizme`, and `/interpret`. Your
instructor shares the link on Canvas.

---

*Instructor note: this `main` branch is the student-facing view, generated
automatically from the `instructor` branch, which holds the full course source
(website, build tooling, and study-companion materials).*

[tf]: https://timothyfraser.com
[site]: https://timothyfraser.com/netsci
[canvas]: https://canvas.cornell.edu/courses/87652
[play]: https://timothyfraser.com/netsci/playground.html
[play-r]: https://timothyfraser.com/netsci/playground-r.html
[play-py]: https://timothyfraser.com/netsci/playground-py.html
