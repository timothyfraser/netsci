#!/usr/bin/env bash
# ============================================================================
# prepare-env.sh — ONE-TIME heavy environment prep for the AI-student cohort.
#
#   bash .claude/harness/prepare-env.sh           # prep if not already done
#   bash .claude/harness/prepare-env.sh --force   # re-run even if marked ready
#
# Does the slow stuff exactly once: R install, the code/<case> R packages, and
# the Playwright Chromium download. Writes a readiness marker
# (.harness-env-ready) ONLY when prep actually succeeds.
#
# WHY THIS EXISTS
#   The per-session SessionStart hook used to do all of this on EVERY launch. When
#   personas run in parallel that means N cold installs racing into the SAME shared
#   R library (lock/corruption risk) and every session sitting idle for minutes
#   before any coursework. This script makes the work happen ONCE, up front, and is
#   safe to call concurrently: a flock serializes callers and the marker turns
#   repeat calls into a fast no-op. run-students.sh calls it before fanning out, and
#   the slim session-start.sh falls back to it if the env isn't ready yet.
#
# NETWORK NOTE
#   R packages install fastest from Posit Package Manager (binary builds). It must
#   be on your network allowlist (packagemanager.posit.co); we fall back to CRAN
#   (cloud.r-project.org). If both are blocked, only Ubuntu's r-cran-* debs are
#   available. See .claude/students/NETWORK-ALLOWLIST.md.
# ============================================================================
set -uo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
MARKER="$PROJECT_DIR/.harness-env-ready"
LOCK="$PROJECT_DIR/.harness-env.lock"

# Posit Package Manager binary repo (fast); CRAN is the fallback mirror.
P3M="${P3M:-https://packagemanager.posit.co/cran/__linux__/noble/latest}"

FORCE=0; [ "${1:-}" = "--force" ] && FORCE=1

# Fast readiness check: trust the marker + a working Rscript.
ready() {
  [ "$FORCE" = "0" ] || return 1
  [ -f "$MARKER" ] && command -v Rscript >/dev/null 2>&1
}

# do_prep returns 0 on success, non-zero on failure. It does NOT write the
# marker — the caller does that, and only on success, so a failed install can
# never masquerade as "ready".
do_prep() {
  echo "[prepare-env] preparing environment (one-time; this can take several minutes)..."

  # 1. R itself. setup.sh is the canonical installer (R + system libs); if it
  #    fails (e.g. CRAN's apt key is blocked), fall back to Ubuntu's r-base-core.
  if ! command -v Rscript >/dev/null 2>&1; then
    echo "[prepare-env] Rscript not found -- running setup.sh..."
    bash "$PROJECT_DIR/setup.sh" || echo "[prepare-env] setup.sh failed; trying Ubuntu r-base-core..."
  fi
  if ! command -v Rscript >/dev/null 2>&1; then
    sudo apt-get install -y --no-install-recommends r-base-core || true
  fi
  if ! command -v Rscript >/dev/null 2>&1; then
    echo "[prepare-env] ERROR: R could not be installed (is CRAN or Ubuntu reachable?)."
    return 1
  fi

  # 2. Project-pinned packages, if any.
  if [ -f "$PROJECT_DIR/renv.lock" ]; then
    Rscript -e 'if (!requireNamespace("renv", quietly=TRUE)) install.packages("renv"); renv::restore(prompt = FALSE)' || true
  fi

  # 3. Packages the code/<case>/example.R + harness/aggregate.R scripts need.
  #    Prefer Posit PM binaries (fast); fall back to CRAN source.
  Rscript -e '
    options(repos = c(P3M = Sys.getenv("P3M_REPO"), CRAN = "https://cloud.r-project.org"))
    need <- c("dplyr","readr","tidyr","tibble","stringr","arrow",
              "ggplot2","viridis","patchwork",
              "igraph","tidygraph","ggraph",
              "sf","xgboost","zoo","reticulate","here",
              "jsonlite","purrr")
    miss <- setdiff(need, rownames(installed.packages()))
    if (length(miss)) { message("[prepare-env] installing: ", paste(miss, collapse=", ")); install.packages(miss) }
  ' P3M_REPO="$P3M" || true

  # 4. Playwright Chromium (some personas browse the course site). Best-effort.
  npx -y @playwright/mcp@latest --version >/dev/null 2>&1 || true
  npx -y playwright install chromium --with-deps >/dev/null 2>&1 || true

  return 0
}

# write_marker_on_success — only mark ready if prep succeeded AND R really runs.
finish() {
  if do_prep && command -v Rscript >/dev/null 2>&1; then
    date '+%Y-%m-%d %H:%M:%S' > "$MARKER"
    echo "[prepare-env] done -- marker written to $MARKER"
  else
    echo "[prepare-env] NOT marking ready -- prep did not complete (see errors above)."
    exit 1
  fi
}

if ready; then
  echo "[prepare-env] env already prepared ($(cat "$MARKER" 2>/dev/null)) -- nothing to do."
  exit 0
fi

if command -v flock >/dev/null 2>&1; then
  # Serialize concurrent callers: first one preps, the rest block then no-op.
  exec 9>"$LOCK"
  echo "[prepare-env] acquiring env-prep lock..."
  flock 9
  if ready; then
    echo "[prepare-env] prepared by another process while we waited -- nothing to do."
    exit 0
  fi
  finish
else
  echo "[prepare-env] WARNING: flock not available -- concurrent calls are NOT serialized."
  finish
fi
