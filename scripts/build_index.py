"""Build .notebook/index.md — a structured map of every page and code file.

Each entry is a Markdown subsection with Title, URL, Topic, Use case, and Tags.
NotebookLM chunks by heading and uses the explicit URL to direct students to
the right page or file in answers.

Edit the CURATED metadata below when adding or relabeling pages. Files found
on disk but not in CURATED are emitted with placeholder fields so they show
up in the index (and so the maintainer can fill them in later).

Run locally with:
    pip install beautifulsoup4
    python scripts/build_index.py
"""

from __future__ import annotations

import datetime as dt
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS = REPO_ROOT / "docs"
CODE = REPO_ROOT / "code"
OUT = REPO_ROOT / ".notebook" / "index.md"

SITE_BASE = "https://timothyfraser.github.io/netsci"
REPO_BASE = "https://github.com/timothyfraser/netsci/blob/main"

# ----------------------------------------------------------------------------
# Curated metadata. Keys are POSIX-style paths relative to the repo root.
# ----------------------------------------------------------------------------

WEBSITE: dict[str, dict] = {
    "docs/index.html": {
        "title": "Course Homepage — SYSEN 5470",
        "topic": "Course landing page and overview",
        "use_case": "Start here. One-page overview of what the course is, who it's for, the four professional skills, and how to enroll. Send students here when they're new to the course or want the elevator pitch.",
        "tags": ["overview", "homepage", "landing", "enrollment", "SYSEN 5470", "summer 2026", "Cornell", "three weeks"],
    },
    "docs/syllabus.html": {
        "title": "Syllabus",
        "topic": "Schedule, grading, policies",
        "use_case": "Look up the weekly schedule, due dates, grading breakdown, attendance, AI policy, accommodations, or any official course policy.",
        "tags": ["syllabus", "schedule", "calendar", "grading", "policies", "dates", "weeks", "rubric", "AI policy", "due dates"],
    },
    "docs/materials.html": {
        "title": "Course Materials & Setup",
        "topic": "Software, packages, prerequisites",
        "use_case": "Find out what software to install (R, Python, packages), what to read before week 1, and the recommended hardware setup.",
        "tags": ["materials", "setup", "install", "R", "Python", "packages", "renv", "requirements", "prerequisites", "tools"],
    },
    "docs/four-skills.html": {
        "title": "Four Professional Skills",
        "topic": "Skill framework: Identify, Model, Predict, Decide",
        "use_case": "Explain why the course is organized around four transferable analytical skills, and which case studies build each skill.",
        "tags": ["four skills", "professional skills", "identify", "model", "predict", "decide", "framework", "learning outcomes"],
    },
    "docs/case-studies.html": {
        "title": "Case Studies — Index",
        "topic": "Catalog of all interactive labs",
        "use_case": "Browse the full set of 11 case-study labs with one-line summaries. Use this as the jumping-off point to find a specific lab.",
        "tags": ["case studies", "labs", "index", "catalog", "list", "interactive"],
    },
    "docs/visualizer.html": {
        "title": "Network Visualizer",
        "topic": "Interactive graph visualization tool",
        "use_case": "Open the browser-based visualizer to load any node/edge CSV and see the network. Use it to demo a dataset live or let students explore their own graphs.",
        "tags": ["visualizer", "interactive", "graph viewer", "D3", "CSV", "visualization", "network drawing"],
    },
    "docs/playground.html": {
        "title": "Coding Playground — Hub",
        "topic": "Entry point to the in-browser R and Python sandboxes",
        "use_case": "Pick between the R playground (WebR) and the Python playground (Pyodide). Send students here when they want to try code without installing anything.",
        "tags": ["playground", "coding", "sandbox", "in-browser", "WebR", "Pyodide", "no install"],
    },
    "docs/playground-r.html": {
        "title": "R Playground (WebR, in-browser)",
        "topic": "Run R code in the browser via WebR",
        "use_case": "Open a runnable R sandbox with igraph and tidyverse loaded. No install required. Best for trying small R snippets or working through a case study's example.R online.",
        "tags": ["R playground", "WebR", "R", "tidyverse", "igraph", "in-browser R", "sandbox", "no install"],
    },
    "docs/playground-py.html": {
        "title": "Python Playground (Pyodide, in-browser)",
        "topic": "Run Python code in the browser via Pyodide",
        "use_case": "Open a runnable Python sandbox with networkx and pandas loaded. No install required. Best for trying small Python snippets or working through a case study's example.py online.",
        "tags": ["Python playground", "Pyodide", "Python", "networkx", "pandas", "in-browser Python", "sandbox", "no install"],
    },
    "docs/readings.html": {
        "title": "Readings",
        "topic": "Required and recommended readings list",
        "use_case": "Find the assigned reading for a given week, the recommended-but-optional papers, and direct links to PDFs or DOIs.",
        "tags": ["readings", "papers", "bibliography", "literature", "PDFs", "weekly"],
    },
    "docs/sketchpad.html": {
        "title": "Sketchpad Prompts",
        "topic": "Network sketching exercises",
        "use_case": "Look up the recurring 'sketch a network' prompts students do by hand. Use this to find the prompt for a given day or to give a student an extra one.",
        "tags": ["sketchpad", "sketches", "drawing", "by hand", "warm-up", "prompts", "exercises"],
    },
    "docs/about.html": {
        "title": "About the Course",
        "topic": "Instructor bio, course design philosophy, contact",
        "use_case": "Learn who teaches the course, the design philosophy behind it, and how to contact the instructor.",
        "tags": ["about", "instructor", "bio", "contact", "philosophy", "credits"],
    },
    "docs/flyer.html": {
        "title": "Course Flyer",
        "topic": "Printable promotional flyer",
        "use_case": "Single-page printable flyer for posting around departments or sharing with prospective students.",
        "tags": ["flyer", "promo", "marketing", "print", "poster", "recruitment"],
    },
    "docs/assignments.html": {
        "title": "Assignments",
        "topic": "Graded assignment specs and submission",
        "use_case": "Pull up the spec for a specific assignment — what to turn in, how it's graded, deadlines, and rubrics.",
        "tags": ["assignments", "homework", "deliverables", "rubric", "submission", "deadlines", "graded"],
    },
    "docs/promo.md": {
        "title": "Promo Blurb",
        "topic": "Short promo copy for the course",
        "use_case": "Use this short blurb when announcing the course on Slack, email, or LinkedIn — it's the canonical one-paragraph pitch.",
        "tags": ["promo", "blurb", "marketing", "announcement", "social"],
    },
}

# Each case study is one row; the script expands it to ~6 entries
# (1 interactive lab + 1 code README + example.R + example.py + functions.R + functions.py).
CASE_STUDIES: list[dict] = [
    {
        "n": 1, "slug": "build-a-network", "name": "Build a Network",
        "skill": "Identify", "topic": "Constructing a graph from node + edge tables",
        "use_case": "Send students here when they ask how to turn raw spreadsheets into a graph object they can compute on. Foundational — do this one first.",
        "tags": ["build a network", "graph construction", "nodes", "edges", "CSV to graph", "igraph", "networkx", "case study 01"],
    },
    {
        "n": 2, "slug": "joins", "name": "Network Joins",
        "skill": "Identify", "topic": "Joining tables to construct multi-attribute networks",
        "use_case": "Use when students need to combine multiple data tables (people, places, transactions) into a single network with rich node/edge attributes.",
        "tags": ["joins", "table joins", "dplyr", "merge", "transit network", "stations", "attributes", "case study 02"],
    },
    {
        "n": 3, "slug": "aggregation", "name": "Network Aggregation",
        "skill": "Identify", "topic": "Aggregating fine-grained networks into coarser ones",
        "use_case": "Use when a network is too granular and you need to roll edges/nodes up to a community, region, or category level.",
        "tags": ["aggregation", "rollup", "grouping", "coarsening", "summarize", "case study 03"],
    },
    {
        "n": 4, "slug": "centrality", "name": "Centrality & Criticality",
        "skill": "Model", "topic": "Finding bottlenecks, hubs, and critical nodes",
        "use_case": "Send students here for any question about who/what is important in a network: degree, betweenness, closeness, eigenvector centrality, and removing nodes to test fragility.",
        "tags": ["centrality", "criticality", "betweenness", "degree", "closeness", "eigenvector", "hubs", "bottleneck", "vulnerability", "case study 04"],
    },
    {
        "n": 5, "slug": "supply-chain", "name": "Supply Chain Networks",
        "skill": "Model", "topic": "Tier-structured supply chain analysis",
        "use_case": "Use when modeling a multi-tier supplier network: who supplies whom, capacity bottlenecks, single-source risk, regional concentration.",
        "tags": ["supply chain", "tiers", "suppliers", "logistics", "capacity", "single-source risk", "case study 05"],
    },
    {
        "n": 6, "slug": "dsm-clustering", "name": "DSM & Clustering",
        "skill": "Model", "topic": "Design Structure Matrix and community detection",
        "use_case": "Use when students need to find clusters/modules in a system — engineering subsystems, organizational teams, or any group structure hidden in a network.",
        "tags": ["DSM", "design structure matrix", "clustering", "community detection", "modularity", "Louvain", "subsystems", "case study 06"],
    },
    {
        "n": 7, "slug": "permutation", "name": "Permutation Tests",
        "skill": "Predict", "topic": "Statistical inference for networks via permutation",
        "use_case": "Send students here when they ask whether an observed network pattern (a correlation, a degree assortativity, a clustering coefficient) is meaningful vs. random.",
        "tags": ["permutation test", "statistical inference", "null model", "randomization", "p-value", "significance", "case study 07"],
    },
    {
        "n": 8, "slug": "sampling", "name": "Network Sampling",
        "skill": "Predict", "topic": "Sampling and approximating large networks",
        "use_case": "Use when the full network is too big to load or query — snowball, random-walk, induced-subgraph sampling, and how to correct estimates for sampling bias.",
        "tags": ["sampling", "snowball", "random walk", "induced subgraph", "big networks", "scaling", "case study 08"],
    },
    {
        "n": 9, "slug": "counterfactual", "name": "Counterfactual Inference",
        "skill": "Decide", "topic": "What-if analysis on networks",
        "use_case": "Use when students need to reason about counterfactuals: 'what would happen if we removed this node / added this edge / rerouted this flow?'",
        "tags": ["counterfactual", "what if", "intervention", "causal", "decision", "policy", "case study 09"],
    },
    {
        "n": 10, "slug": "gnn-by-hand", "name": "Graph Neural Networks by Hand",
        "skill": "Predict", "topic": "Building a GNN from scratch with matrix algebra",
        "use_case": "Use to demystify GNNs — message passing, neighborhood aggregation, and a tiny worked example built without a deep-learning framework.",
        "tags": ["GNN", "graph neural network", "message passing", "neighborhood aggregation", "by hand", "from scratch", "case study 10"],
    },
    {
        "n": 11, "slug": "gnn-xgboost", "name": "GNN + XGBoost for Prediction",
        "skill": "Predict", "topic": "Combining graph features with gradient boosting",
        "use_case": "Use for the capstone-style example of feeding GNN-derived embeddings into XGBoost to predict supplier failure or any node-level outcome.",
        "tags": ["GNN", "XGBoost", "gradient boosting", "node prediction", "embeddings", "machine learning", "supplier failure", "case study 11"],
    },
]

# Top-level repo files.
REPO_FILES: dict[str, dict] = {
    "code/README.md": {
        "title": "Code Modules — Overview",
        "topic": "Index of the 11 case-study code folders",
        "use_case": "Browse the structure of the code/ directory: how each case study is organized into example/, functions/, data/, and how to run them locally.",
        "tags": ["code", "overview", "modules", "README", "directory structure", "how to run"],
    },
    "code/requirements.txt": {
        "title": "Python Requirements",
        "topic": "Python package list for the case-study code",
        "use_case": "Pin the Python packages needed to run example.py and functions.py for every case study locally.",
        "tags": ["requirements", "pip", "Python packages", "install", "dependencies"],
    },
    "README.md": {
        "title": "Repository README",
        "topic": "GitHub repo top-level description",
        "use_case": "Short pointer to the course and where the materials live. Mostly a landing page for visitors arriving at the GitHub repo.",
        "tags": ["repository", "GitHub", "README", "top-level"],
    },
    ".notebook/website.md": {
        "title": "NotebookLM Source — Full Website",
        "topic": "Concatenated visible text of every page in docs/",
        "use_case": "The single Markdown bundle to paste into NotebookLM as a source for ALL website content. Re-paste when you push site updates.",
        "tags": ["NotebookLM", "source", "bundle", "website", "markdown", "concatenated"],
    },
    ".notebook/coding-modules.md": {
        "title": "NotebookLM Source — Coding Modules",
        "topic": "Concatenated .md / .R / .py from the code/ directory",
        "use_case": "The single Markdown bundle to paste into NotebookLM as a source for ALL coding modules. Re-paste when you push code updates.",
        "tags": ["NotebookLM", "source", "bundle", "coding modules", "R", "Python", "case studies"],
    },
    ".notebook/index.md": {
        "title": "NotebookLM Source — Index of Everything",
        "topic": "This file: structured map of every page and file with URLs",
        "use_case": "The metadata source for NotebookLM. Paste this as a source so NotebookLM can answer 'where do I find X?' with a direct link.",
        "tags": ["NotebookLM", "source", "index", "map", "metadata", "URLs", "directory"],
    },
}


# ----------------------------------------------------------------------------
# Builders
# ----------------------------------------------------------------------------


def site_url(rel_path: str) -> str:
    # docs/ is the published root.
    if rel_path.startswith("docs/"):
        return f"{SITE_BASE}/{rel_path[len('docs/'):]}"
    return f"{REPO_BASE}/{rel_path}"


def repo_url(rel_path: str) -> str:
    return f"{REPO_BASE}/{rel_path}"


def entry(title: str, url: str, topic: str, use_case: str, tags: list[str]) -> str:
    tags_str = ", ".join(tags) if tags else "_(none)_"
    return (
        f"## {title}\n\n"
        f"- **URL:** {url}\n"
        f"- **Topic:** {topic}\n"
        f"- **Use case:** {use_case}\n"
        f"- **Tags:** {tags_str}\n\n"
    )


def expand_case_study(cs: dict) -> list[tuple[str, dict]]:
    """One case study expands to the lab page + 5 code files."""
    nn = f"{cs['n']:02d}"
    slug = cs["slug"]
    folder = f"code/{nn}_{slug}"
    lab_path = f"docs/case-studies/{slug}.html"
    base_tags = cs["tags"] + [f"skill: {cs['skill']}"]

    out: list[tuple[str, dict]] = []
    out.append((lab_path, {
        "title": f"Lab {nn} — {cs['name']} (interactive)",
        "topic": cs["topic"],
        "use_case": f"Interactive in-browser lab for case study {cs['n']}. {cs['use_case']}",
        "tags": base_tags + ["interactive lab", "browser"],
    }))
    out.append((f"{folder}/README.md", {
        "title": f"Code {nn} — {cs['name']} (README)",
        "topic": cs["topic"],
        "use_case": f"Conceptual writeup for case study {cs['n']}: what the dataset is, what the script does, and what students should take away.",
        "tags": base_tags + ["README", "writeup", "concepts"],
    }))
    out.append((f"{folder}/example.R", {
        "title": f"Code {nn} — {cs['name']} (R example)",
        "topic": cs["topic"] + " — R implementation",
        "use_case": "Runnable R script that works through case study " + str(cs["n"]) + " end-to-end with igraph and tidyverse. Pair with the R Playground or run locally.",
        "tags": base_tags + ["R", "igraph", "tidyverse", "example.R", "runnable"],
    }))
    out.append((f"{folder}/example.py", {
        "title": f"Code {nn} — {cs['name']} (Python example)",
        "topic": cs["topic"] + " — Python implementation",
        "use_case": "Runnable Python script that mirrors example.R using networkx + pandas. Pair with the Python Playground or run locally.",
        "tags": base_tags + ["Python", "networkx", "pandas", "example.py", "runnable"],
    }))
    out.append((f"{folder}/functions.R", {
        "title": f"Code {nn} — {cs['name']} (R helper functions)",
        "topic": cs["topic"] + " — R utilities",
        "use_case": "Reusable R helper functions referenced by example.R — students can crib these for assignments.",
        "tags": base_tags + ["R", "functions", "helpers", "utilities"],
    }))
    out.append((f"{folder}/functions.py", {
        "title": f"Code {nn} — {cs['name']} (Python helper functions)",
        "topic": cs["topic"] + " — Python utilities",
        "use_case": "Reusable Python helper functions referenced by example.py — students can crib these for assignments.",
        "tags": base_tags + ["Python", "functions", "helpers", "utilities"],
    }))
    return out


def auto_title(path: Path) -> str:
    """Fallback title extractor for files not in any curated table."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return path.name
    if path.suffix == ".html":
        soup = BeautifulSoup(text, "html.parser")
        if soup.title and soup.title.get_text(strip=True):
            return soup.title.get_text(strip=True)
    m = re.search(r"^# (.+)$", text, flags=re.MULTILINE)
    if m:
        return m.group(1).strip()
    return path.name


def find_uncurated(curated_paths: set[str]) -> list[str]:
    """Find files on disk that should probably be indexed but aren't curated."""
    found: list[str] = []
    for path in sorted(DOCS.rglob("*.html")):
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel not in curated_paths:
            found.append(rel)
    for path in sorted(CODE.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix not in {".R", ".py", ".md"}:
            continue
        if "data" in path.relative_to(CODE).parts:
            continue  # data/_generate.py covered elsewhere if curated
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel not in curated_paths:
            found.append(rel)
    return found


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)

    # Expand case studies into per-file entries.
    case_study_entries: list[tuple[str, dict]] = []
    for cs in CASE_STUDIES:
        case_study_entries.extend(expand_case_study(cs))

    curated_paths: set[str] = (
        set(WEBSITE) | set(REPO_FILES) | {p for p, _ in case_study_entries}
    )

    parts: list[str] = []
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    parts.append(
        f"# SYSEN 5470 — Resource Index\n\n"
        f"_Auto-generated NotebookLM source · {timestamp}_\n\n"
        "Structured index of every public page and code file in the course. "
        "Paste this into NotebookLM as a source so it can answer 'where do I "
        "find X?' with a direct link. Each entry has a title, URL, topic, "
        "use case, and tags to help with retrieval.\n\n---\n\n"
    )

    # 1. Website pages (in nav order).
    parts.append("# Website Pages\n\n")
    nav_order = [
        "docs/index.html", "docs/syllabus.html", "docs/materials.html",
        "docs/four-skills.html", "docs/case-studies.html",
        "docs/visualizer.html", "docs/playground.html",
        "docs/playground-r.html", "docs/playground-py.html",
        "docs/readings.html", "docs/sketchpad.html", "docs/about.html",
        "docs/flyer.html", "docs/assignments.html", "docs/promo.md",
    ]
    for rel in nav_order:
        meta = WEBSITE.get(rel)
        if meta is None:
            continue
        parts.append(entry(meta["title"], site_url(rel), meta["topic"],
                           meta["use_case"], meta["tags"]))

    # 2. Case studies (lab + 5 code files per study, in order).
    parts.append("---\n\n# Case Studies — Interactive Labs and Code\n\n")
    for rel, meta in case_study_entries:
        if rel.startswith("docs/"):
            url = site_url(rel)
        else:
            url = repo_url(rel)
        parts.append(entry(meta["title"], url, meta["topic"],
                           meta["use_case"], meta["tags"]))

    # 3. Top-level repo files and notebook sources.
    parts.append("---\n\n# Repository & NotebookLM Sources\n\n")
    for rel, meta in REPO_FILES.items():
        parts.append(entry(meta["title"], repo_url(rel), meta["topic"],
                           meta["use_case"], meta["tags"]))

    # 4. Auto-detected uncurated files (so the index stays complete).
    uncurated = find_uncurated(curated_paths)
    if uncurated:
        parts.append(
            "---\n\n# Uncurated (auto-detected, needs metadata)\n\n"
            "_These files exist on disk but don't yet have curated metadata. "
            "Add them to `scripts/build_index.py` to give them topic/use-case/tags._\n\n"
        )
        for rel in uncurated:
            path = REPO_ROOT / rel
            title = auto_title(path)
            url = site_url(rel) if rel.startswith("docs/") else repo_url(rel)
            parts.append(entry(
                title, url,
                topic="_(uncurated — fill me in)_",
                use_case="_(uncurated — fill me in)_",
                tags=[],
            ))
        print(
            f"NOTE: {len(uncurated)} file(s) auto-detected without curated metadata.",
            file=sys.stderr,
        )
        for rel in uncurated:
            print(f"  - {rel}", file=sys.stderr)

    OUT.write_text("".join(parts), encoding="utf-8")
    n_entries = sum(1 for p in parts if p.startswith("## "))
    size_kb = OUT.stat().st_size / 1024
    print(f"Wrote {OUT.relative_to(REPO_ROOT)} ({size_kb:.1f} KB, {n_entries} entries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
