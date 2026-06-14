#!/usr/bin/env bash
# ============================================================================
# prepare-env.sh — ONE-TIME heavy environment prep for the AI-student cohort.
#
#   bash .claude/harness/prepare-env.sh           # prep if not already done
#   bash .claude/harness/prepare-env.sh --force   # re-run even if marked ready
#
# Does the slow stuff exactly once: R install (setup.sh), renv restore, the
# code/<case> R packages, and the Playwright Chromium download. Writes a marker
# (.harness-env-ready) when done.
#
# WHY THIS EXISTS
#   The per-session SessionStart hook used to do all of this on EVERY launch. When
#   personas run in parallel that means N cold installs racing into the SAME shared
#   R library (lock/corruption risk) and every session sitting idle for minutes
#   before any coursework. This script makes the work happen ONCE, up front, and is
#   safe to call concurrently: a flock serializes callers and the marker turns
#   repeat calls into a fast no-op. run-students.sh calls it before fanning out, and
#   the slim session-start.sh falls back to it if the env isn't ready yet.
# ============================================================================
set -uo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
MARKER="$PROJECT_DIR/.harness-env-ready"
LOCK="$PROJECT_DIR/.harness-env.lock"

FORCE=0; [ "${1:-}" = "--force" ] && FORCE=1

# Fast readiness check: trust the marker + a working Rscript.
ready() {
  [ "$FORCE" = "0" ] || return 1
  [ -f "$MARKER" ] && command -v Rscript >/dev/null 2>&1
}

do_prep() {
  echo "[prepare-env] preparing environment (one-time; this can take several minutes)…"

  # 1. R itself (setup.sh is idempotent: R + system libs + CRAN baseline)
  if ! command -v Rscript >/dev/null 2>&1; then
    echo "[prepare-env] Rscript not found — running setup.sh…"
    bash "$PROJECT_DIR/setup.sh"
  fi

  # 2. Project-pinned packages, if any
  if [ -f "$PROJECT_DIR/renv.lock" ]; then
    Rscript -e 'if (!requireNamespace("renv", quietly=TRUE)) install.packages("renv"); renv::restore(prompt = FALSE)' || true
  fi

  # 3. Packages the code/<case>/example.R + harness/aggregate.R scripts need
  Rscript -e '
    need <- c("dplyr","readr","tidyr","tibble","stringr","arrow",
              "ggplot2","viridis","patchwork",
              "igraph","tidygraph","ggraph",
              "sf","xgboost","zoo","reticulate","here",
              "jsonlite","purrr")
    miss <- setdiff(need, rownames(installed.packages()))
    if (length(miss)) { message("[prepare-env] installing: ", paste(miss, collapse=", ")); install.packages(miss) }
  ' || true

  # 4. Playwright Chromium (some personas browse the course site). Best-effort.
  npx -y @playwright/mcp@latest --version >/dev/null 2>&1 || true
  npx -y playwright install chromium --with-deps >/dev/null 2>&1 || true

  date '+%Y-%m-%d %H:%M:%S' > "$MARKER"
  echo "[prepare-env] done — marker written to $MARKER"
}

if ready; then
  echo "[prepare-env] env already prepared ($(cat "$MARKER" 2>/dev/null)) — nothing to do."
  exit 0
fi

if command -v flock >/dev/null 2>&1; then
  # Serialize concurrent callers: first one preps, the rest block then no-op.
  exec 9>"$LOCK"
  echo "[prepare-env] acquiring env-prep lock…"
  flock 9
  if ready; then
    echo "[prepare-env] prepared by another process while we waited — nothing to do."
    exit 0
  fi
  do_prep
else
  echo "[prepare-env] WARNING: flock not available — concurrent calls are NOT serialized."
  do_prep
fi
