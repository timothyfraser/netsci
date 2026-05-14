#!/usr/bin/env bash
set -euo pipefail

# 1. Bootstrap R if it isn't installed yet.
# The repo's setup.sh handles the full install (R + system libs + CRAN
# packages). It's safe to re-run because each step is idempotent.
if ! command -v Rscript >/dev/null 2>&1; then
  echo "Rscript not found - running setup.sh to install R..."
  bash "$CLAUDE_PROJECT_DIR/setup.sh"
fi

# 2. Restore project-pinned packages if renv.lock present
if [ -f "$CLAUDE_PROJECT_DIR/renv.lock" ]; then
  Rscript -e 'if (!requireNamespace("renv", quietly=TRUE)) install.packages("renv"); renv::restore(prompt = FALSE)'
fi

# 3. Make sure the code/<case>/example.R scripts can run by
# installing any package they need that may not be in the baseline
# (this is cheap when the packages are already there).
Rscript -e '
need <- c("dplyr","readr","tidyr","tibble","stringr","arrow",
          "ggplot2","viridis","patchwork",
          "igraph","tidygraph","ggraph",
          "sf","xgboost","zoo","reticulate","here")
have <- rownames(installed.packages())
miss <- setdiff(need, have)
if (length(miss)) {
  message("installing missing R packages: ", paste(miss, collapse = ", "))
  install.packages(miss)
}
' || true

# 4. Make API keys from the .env file available to R sessions
{
#  [ -n "${ANTHROPIC_API_KEY:-}"   ] && echo "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY"
} >> "$HOME/.Renviron" || true

echo "R session ready: $(Rscript -e 'cat(R.version.string)')"
