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
