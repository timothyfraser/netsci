#!/usr/bin/env bash
set -euxo pipefail

# --- R base + build tools ---
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
  software-properties-common dirmngr gnupg ca-certificates curl

# CRAN repo for current R (Ubuntu)
curl -fsSL https://cloud.r-project.org/bin/linux/ubuntu/marutter_pubkey.asc \
  | sudo tee /etc/apt/trusted.gpg.d/cran_ubuntu_key.asc
echo "deb https://cloud.r-project.org/bin/linux/ubuntu $(lsb_release -cs)-cran40/" \
  | sudo tee /etc/apt/sources.list.d/cran.list

sudo apt-get update
sudo apt-get install -y --no-install-recommends \
  r-base r-base-dev \
  libcurl4-openssl-dev libssl-dev libxml2-dev \
  libfontconfig1-dev libharfbuzz-dev libfribidi-dev \
  libfreetype6-dev libpng-dev libtiff5-dev libjpeg-dev \
  libgit2-dev libsodium-dev \
  libudunits2-dev libgdal-dev libgeos-dev libproj-dev \
  default-libmysqlclient-dev libpq-dev libsqlite3-dev \
  pandoc

# --- User R library + CRAN mirror + parallel installs ---
mkdir -p "$HOME/R/library"
cat > "$HOME/.Renviron" <<'EOF'
R_LIBS_USER=~/R/library
EOF

cat > "$HOME/.Rprofile" <<'EOF'
options(
  repos = c(CRAN = "https://cloud.r-project.org"),
  Ncpus = max(1L, parallel::detectCores() - 1L),
  install.packages.compile.from.source = "never"
)
EOF

# --- Baseline CRAN packages ---
Rscript -e '
pkgs <- c(
  "tidyverse","here","janitor","glue","fs",
  "network","igraph","tidygraph",
  "readxl","writexl","arrow",
  "DBI","RPostgres","RMariaDB","RSQLite",
  "tidymodels","broom","bonsai","lightgbm","xgboost",
  "sf",
  "httr2","jsonlite","plumber",
  "shiny","shinychat","bslib","DT",
  "devtools","usethis","renv","testthat","lintr","styler",
  "rmarkdown","knitr","ellmer","ollamar"
)
have <- rownames(installed.packages())
need <- setdiff(pkgs, have)
if (length(need)) install.packages(need)
'

echo "R setup complete: $(R --version | head -1)"
