---
name: netsci-teaching-style
description: |
  Style guide for the parallel R + Python teaching scripts under `code/NN_<case>/`
  in the netsci course repo. Distilled from Tim Fraser's own teaching code in
  stats_bootcamp (minimal, well-commented intro style) and dsai (the
  emoji-flavored console output). Use this when editing any `example.R`,
  `example.py`, `functions.R`, or `functions.py` in this repo.
---

# `netsci` teaching-script style

These scripts are *intro-but-professional*: a brand-new graduate student should
be able to run them cold and learn something, and a senior engineer should
nod and say "yes, that's what I'd write." The two reference repos to study
are:

- **`github.com/timothyfraser/stats_bootcamp`** — minimal, conversational,
  many short comments. The teaching mode is "ask a question, show
  alternatives, comment on what's happening."
- **`github.com/timothyfraser/dsai`** — same shape, plus emoji-flavored
  console output (🚀 ✅ 📝) that liven up `cat()` / `print()` status
  messages.

Below is the synthesized house style.

## 1. File header

Every `example.R` / `example.py` starts with a roxygen / docstring-style
banner. Both languages use the same key names. Use `#'` in R and a single
top-of-file `#` block (one comment per line) in Python.

R:

```r
#' @name example.R
#' @title Case Study 0X — <Name>
#' @author <your-name-here>
#' @description
#' One short sentence saying what this script does.
#'
#' One paragraph (3–5 sentences) saying WHY: what the case study is
#' about, what skill it builds, what the reader will be able to do
#' after running it. Reference the matching interactive lab.
```

Python (mirror as closely as possible):

```python
# example.py
# Case Study 0X — <Name>
# Author: <your-name-here>
#
# One short sentence saying what this script does.
#
# One paragraph (3–5 sentences) saying WHY: what the case study is
# about, what skill it builds, what the reader will be able to do
# after running it. Reference the matching interactive lab.
```

## 2. Section structure

Top-level sections use a long row of `#` after the name. They are
numbered from 0 (Setup) and have a friendly title:

```r
# 0. Setup ###################################################################
# 1. Load and inspect data ###################################################
# 2. Build the network #######################################################
# 3. <whatever the case study is about> ######################################
# 4. Visualize ###############################################################
# 5. Learning Check ##########################################################
```

Subsections use `## N.M Name`:

```r
## 0.1 Packages ##############################################################
## 0.2 Helpers ###############################################################
## 0.3 Data ##################################################################
```

R and Python files use **identical section headers in identical order**, so
a student switching languages mid-script is never lost.

## 3. Opening console banner

The first thing the script does after loading packages: print a short,
emoji-flavored "what you're about to see" banner. R uses `cat()`; Python
uses `print()`. Keep it to 1–3 lines:

R:

```r
cat("\n🚀 Case Study 04 — Centrality & Criticality (R)\n")
cat("   We'll measure who matters in a 500-node distribution network.\n\n")
```

Python:

```python
print("\n🚀 Case Study 04 — Centrality & Criticality (Python)")
print("   We'll measure who matters in a 500-node distribution network.\n")
```

Use 🚀 for "starting / launching." Other approved emojis below.

## 4. Status messages with ✅ and friends

At key milestones — after data load, after a model fits, after a sample
is drawn, after a figure is saved — print one short emoji-flavored line:

```r
cat(sprintf("✅ Loaded %d nodes and %d edges.\n", nrow(nodes), nrow(edges)))
cat(sprintf("📊 Network density: %.3f\n", igraph::edge_density(g)))
cat(sprintf("💾 Saved figure to %s\n", out))
```

```python
print(f"✅ Loaded {len(nodes)} nodes and {len(edges)} edges.")
print(f"📊 Network density: {nx.density(g):.3f}")
print(f"💾 Saved figure to {out}")
```

Approved emoji set (use sparingly — 4–8 per file is plenty):

| Emoji | When to use |
|---|---|
| 🚀 | Top-of-script banner ("starting / launching") |
| ✅ | A step finished successfully ("loaded", "fit", "saved", "passed") |
| 📊 | Reporting a numeric result, a stat, a metric |
| 🔗 | Reporting an edge / graph / network fact |
| 🧪 | A test, a Monte Carlo, or a permutation step |
| 📝 | A textual / interpretive output (top-3 list, ranking) |
| 💾 | Saving a file |
| 🎉 | End-of-script "we're done" line |
| ⚠️ | A caveat the reader should NOT miss |

**Do not put emojis inside code comments.** They go in user-facing
console output only. Comments stay plain ASCII so they read cleanly in
every editor and `git diff`.

## 5. Comment density

This is the place most of my old scripts under-deliver. Tim's style is
**lots of short comments**, not few long ones. Aim for:

- A 1–3 line comment **before every non-trivial code chunk** explaining
  what the chunk does AND why we're doing it.
- A short comment on tricky lines (a renamed argument, an `na.rm = TRUE`,
  a specific seed).
- A "what would happen if..." aside where it builds intuition. Example:
  `# Without na.rm = TRUE, R returns NA the moment any row is missing.`

Conversational tone — second person ("we", "you", "let's"). Avoid
academic passive voice. Avoid restating the function name in English.
Bad: `# Call left_join().` Good: `# Tag every edge with the START
station's demographic flag.`

## 6. Learning checks

Each script ends with a clearly-labeled `# 5. Learning Check ###` (or
whichever section number lands last) that computes the answer and
prints it. Use the canonical emoji 📝:

R:

```r
# 5. Learning Check ##########################################################
#
# QUESTION: Of AM rush rides in 2021 in this slim dataset, how many trips
# started in a majority-Black block group AND ended in a majority-Black
# block group?

answer <- stat |>
  filter(start_black == "yes", end_black == "yes") |>
  pull(trips)

cat(sprintf("\n📝 Learning Check answer: %d\n", answer))
```

The printed line MUST match `example.py` byte-for-byte (same emoji,
same field, same number) so the grader can compare both languages with
a string equality check.

## 7. Closing line

Every script ends with one cheerful 🎉 line so the reader knows it
finished cleanly:

```r
cat("\n🎉 Done. Move on to the case study report when you're ready.\n")
```

```python
print("\n🎉 Done. Move on to the case study report when you're ready.")
```

## 8. R-specific conventions

- Base pipe `|>` only (no `%>%`), per CLAUDE.md.
- Always namespace external functions on first use (`igraph::degree(g)`,
  `dplyr::filter(d, ...)`) so the reader sees where things come from.
  After the first reference inside a section you can drop the prefix.
- Use `here::here()` for any file path, never `setwd()` and never a
  relative path that assumes the user's cwd.
- Console output is via `cat()` with `\n`. Avoid `print()` (it adds
  `[1]` and quotes strings).
- `sprintf()` is preferred over `paste0()` when formatting numbers,
  because the format string is easier to read.

## 9. Python-specific conventions

- f-strings, never `%`-formatting or `.format()`.
- Use `pandas` + `igraph` (the `python-igraph` package). Bring in
  `networkx` only when the case study explicitly needs an algorithm
  python-igraph doesn't ship.
- Resolve data paths via `pathlib.Path(__file__).resolve().parent`, never
  via the cwd.
- Top-of-file `from __future__ import annotations` for any module that
  defines functions with type hints, so the same code works on older
  Pythons.

## 10. Data conventions

- All bundled data files in `code/NN_<case>/data/` are CSV (plus
  optional GeoJSON for spatial). No parquet — keeps the R / Python
  dependency footprint identical.
- Each `data/_generate.py` is deterministic from `seed=42`.
- Keep total bundled-data size for a case under ~5 MB. Trim aggressively
  if you have to.

## 11. Parity rule

The two scripts in a case study MUST:

1. Print the same opening banner (modulo "R" / "Python" suffix).
2. Use the same section header text and order.
3. Compute and print the same Learning Check answer to the same number
   of decimal places.
4. End with the same closing 🎉 line.

The README documents any intentional divergence (case 10 is
Python-primary; case 11 uses different LC questions per track).

## 12. Testing rule

Before claiming a script is "done":

```bash
Rscript code/NN_<case>/example.R    # exits 0, prints all sections + LC
python  code/NN_<case>/example.py   # exits 0, prints all sections + LC
```

Both LCs must match (case 1–10) or be the documented per-track variants
(case 11). The CI sweep at the bottom of this skill runs both languages
for every case and diffs the LC lines — keep it green.

### One-shot CI sweep

```bash
# from repo root
for d in code/[0-9][0-9]_*/; do
  name=$(basename "${d%/}")
  rlc=$(Rscript "$d/example.R" 2>&1 | grep -i "Learning Check answer" | tail -1)
  plc=$(python  "$d/example.py" 2>&1 | grep -i "Learning Check answer" | tail -1)
  printf "%-22s\n  R : %s\n  Py: %s\n" "$name" "$rlc" "$plc"
done
```

For cases 1–10 the two lines should be identical character-for-character
modulo trailing whitespace. For case 11 they are intentionally different
(R reports top-3 features by gain; Python reports AUC).
