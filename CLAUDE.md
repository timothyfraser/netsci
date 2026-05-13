# R Environment

- Run R scripts with: `Rscript path/to/script.R`
- Install packages with: `Rscript -e 'install.packages("pkg")'`
- Code style: tidyverse (dplyr, ggplot2, purrr, tidyr, readr)
- Use `|>` (base pipe), not `%>%`, unless a package requires magrittr
- Prefer `here::here()` for paths
- Use `renv` for project dependencies when present

## Common commands
- Lint: `Rscript -e 'lintr::lint_dir()'`
- Test: `Rscript -e 'testthat::test_dir("tests/testthat")'`
