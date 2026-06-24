# R Environment

- Run R scripts with: `Rscript path/to/script.R`
- Install packages with: `Rscript -e 'install.packages("pkg")'`
- Code style: tidyverse (dplyr, ggplot2, purrr, tidyr, readr)
- Use `|>` (base pipe), not `%>%`, unless a package requires magrittr
- Prefer `here::here()` for paths
- If `renv.lock` exists, use `renv::install()` not `install.packages()`
- Use `renv` for project dependencies when present
- Secrets are in `.env`; access via `Sys.getenv("KEY")`

## Common commands
- Lint: `Rscript -e 'lintr::lint_dir()'`
- Test: `Rscript -e 'testthat::test_dir("tests/testthat")'`

## Skills available (read these before related work)

Skills live in `.claude/skills/<name>/SKILL.md`. Invoke/read the relevant one
*before* starting, not after.

- **netsci-browser-testing** — how to run the interactive pages (Visualizer,
  playgrounds, any D3/JS UI) in a **real headless Chromium** here. Headless
  Chromium **works** (via `puppeteer-core` + `@sparticuz/chromium` from npm —
  the Playwright/Chromium CDN is proxy-blocked, but npm registries are
  allow-listed). Use it to actually verify front-end changes (colors render,
  controls fire, no console errors) instead of guessing. Don't re-discover this.
- **netsci-dataset-builder** — standard for authoring project datasets under
  `data/projects/<name>/` (folder layout, deterministic generator, README
  codebook, loaders, playground/visualizer wiring, the "planted story" rules).
- **netsci-glossary** — authoritative network-science vocabulary for the course;
  load before defining methods, mapping concepts to code, or writing checks.
- **netsci-teaching-style** — style for the parallel R/Python teaching scripts
  under `code/NN_<case>/`.

## Front-end / Visualizer notes
- The Visualizer (`docs/visualizer.html` + `docs/assets/viz.js`) exposes
  `window.NetSciViz` (`state`, `loadGraph`, `loadProjectDataset`) for testing.
- It loads `d3` + `papaparse` from cdnjs and `fetch`es sample CSVs from
  `playground-data/` — see **netsci-browser-testing** for how to run it offline.
- After editing `viz.js`, verify in headless Chromium (above), not just
  `node --check`.
