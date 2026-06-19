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
    print(f"synced {n} CSV file(s) into {DEST}")


if __name__ == "__main__":
    main()
