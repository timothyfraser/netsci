#!/usr/bin/env bash
set -euo pipefail

# Restore project-pinned packages if renv.lock present
if [ -f "$CLAUDE_PROJECT_DIR/renv.lock" ]; then
  Rscript -e 'if (!requireNamespace("renv", quietly=TRUE)) install.packages("renv"); renv::restore(prompt = FALSE)'
fi

# Make API keys from the .env field available to R sessions
# (these are exported into the shell automatically by Claude Code on the web)
{
#  [ -n "${ANTHROPIC_API_KEY:-}"   ] && echo "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY"
} >> "$HOME/.Renviron" || true

echo "R session ready: $(Rscript -e 'cat(R.version.string)')"
