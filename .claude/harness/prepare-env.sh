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

  # 1. R itself + the system libraries the spatial/graph/ML packages link
  #    against. setup.sh is the canonical installer (R + system libs via the
  #    CRAN apt repo); run it when R is missing. EITHER WAY, ensure the system
  #    -dev libraries AND the recommended R packages are present afterwards.
  #    WHY THIS MATTERS: a bare `r-base-core` ships WITHOUT the recommended
  #    packages (Matrix, MASS, ...) and without GDAL/GEOS/PROJ/udunits/BLAS, so
  #    the SOURCE builds of sf/igraph/xgboost/reticulate fail. This apt step is
  #    idempotent (a fast no-op once everything is installed), so it is safe to
  #    run even when Rscript already exists (which is exactly when it used to be
  #    skipped, leaving a half-built environment marked "ready").
  if ! command -v Rscript >/dev/null 2>&1; then
    echo "[prepare-env] Rscript not found -- running setup.sh..."
    bash "$PROJECT_DIR/setup.sh" || echo "[prepare-env] setup.sh failed; falling back to apt below..."
  fi
  sudo apt-get update -qq || true
  sudo apt-get install -y --no-install-recommends \
    r-base-core r-recommended \
    gfortran libblas-dev liblapack-dev \
    libudunits2-dev libgdal-dev libgeos-dev libproj-dev \
    libxml2-dev libcurl4-openssl-dev libssl-dev libglpk-dev \
    libfontconfig1-dev libharfbuzz-dev libfribidi-dev \
    libfreetype6-dev libpng-dev libtiff5-dev libjpeg-dev || true
  if ! command -v Rscript >/dev/null 2>&1; then
    echo "[prepare-env] ERROR: R could not be installed (is CRAN or Ubuntu reachable?)."
    return 1
  fi

  # 2. Project-pinned packages, if any.
  if [ -f "$PROJECT_DIR/renv.lock" ]; then
    Rscript -e 'if (!requireNamespace("renv", quietly=TRUE)) install.packages("renv"); renv::restore(prompt = FALSE)' || true
  fi

  # 3. Packages the code/<case>/example.{R,py} + harness/aggregate.R scripts
  #    need. Set HTTPUserAgent so Posit PM serves prebuilt BINARIES (fast, no
  #    compilation); fall back to CRAN source (which works now that the system
  #    -dev libraries from step 1 are present). `arrow` is best-effort: the
  #    coursework reads CSV/geojson, not parquet, so it is not required.
  Rscript -e '
    options(
      HTTPUserAgent = sprintf("R/%s R (%s)", getRversion(),
        paste(getRversion(), R.version$platform, R.version$arch, R.version$os)),
      repos = c(P3M = Sys.getenv("P3M_REPO"), CRAN = "https://cloud.r-project.org"),
      Ncpus = max(1L, parallel::detectCores() - 1L)
    )
    need <- c("dplyr","readr","tidyr","tibble","stringr","arrow",
              "ggplot2","viridis","patchwork",
              "igraph","tidygraph","ggraph",
              "sf","xgboost","zoo","reticulate","here",
              "jsonlite","purrr")
    miss <- setdiff(need, rownames(installed.packages()))
    if (length(miss)) { message("[prepare-env] installing: ", paste(miss, collapse=", ")); install.packages(miss) }
  ' P3M_REPO="$P3M" || true

  # 3b. reticulate (cases 10-11) drives Python from R, so it needs a Python with
  #     numpy + pandas to point at. Best-effort; PEP-668 distros need the flag.
  python3 -m pip install --break-system-packages -q numpy pandas >/dev/null 2>&1 \
    || pip install -q numpy pandas >/dev/null 2>&1 || true

  # 4. Playwright Chromium (some personas browse the course site). Best-effort.
  npx -y @playwright/mcp@latest --version >/dev/null 2>&1 || true
  npx -y playwright install chromium --with-deps >/dev/null 2>&1 || true

  # 5. Verify the packages the coursework actually runs really LOAD. If any are
  #    missing, return non-zero so finish() does NOT write a false "ready"
  #    marker. (The old hook marked ready unconditionally, so a run where every
  #    compile failed still looked prepared -- exactly the trap we hit.)
  Rscript -e '
    crit <- c("dplyr","tidyr","readr","tibble","ggplot2","viridis",
              "igraph","sf","xgboost","reticulate","here")
    ok <- vapply(crit, requireNamespace, logical(1), quietly = TRUE)
    if (any(!ok)) {
      cat("[prepare-env] MISSING:", paste(crit[!ok], collapse = ", "), "\n")
      quit(status = 1)
    }
    cat("[prepare-env] all critical R packages load.\n")
  ' || return 1

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
