#!/usr/bin/env bash
# SessionStart hook — kept deliberately SLIM so it doesn't do heavy installs on
# every launch (which, under parallel persona runs, raced the shared R library and
# left sessions idle for minutes). The heavy, one-time work lives in
# .claude/harness/prepare-env.sh, which is flock-guarded and idempotent.
set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
MARKER="$PROJECT_DIR/.harness-env-ready"

if [ -f "$MARKER" ] && command -v Rscript >/dev/null 2>&1; then
  # Fast path: environment was already prepared (e.g. by prepare-env.sh before a
  # cohort, or by an earlier session). Near-instant.
  echo "env ready (prepared $(cat "$MARKER" 2>/dev/null)); R: $(Rscript -e 'cat(R.version.string)' 2>/dev/null)"
else
  # Not prepared yet — delegate to the flock-guarded one-time prep. If several
  # sessions hit this at once, flock serializes them so only the first installs.
  echo "env not prepared — running prepare-env.sh (one-time)…"
  bash "$PROJECT_DIR/.claude/harness/prepare-env.sh" || true
fi

# Make API keys from the .env file available to R sessions (cheap; every session).
{
  :  # add 'echo "ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}"' style lines here to expose secrets to R
} >> "$HOME/.Renviron" || true
