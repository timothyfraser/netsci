# Network allowlist — cloud / web Claude Code sessions

The AI-student cohort runs in a cloud Claude Code session that needs **outbound
network**, but you don't have to grant Full internet. Use the environment's
**Custom** network mode with the default Trusted bundle **left ON**, then paste the
domains below into the **Allowed domains** field.

## How to enter it (phone or desktop)

1. Open the `netsci` environment settings → **Network access**.
2. Choose **Custom**, and keep **"include defaults"** (the Trusted bundle) **ON**.
3. Paste the block below into **Allowed domains**.

**Format rules (important):** one domain per line, host-only (no `https://`, no ports),
`*.` for wildcard subdomains. **No comment lines** — the field rejects `#` lines, so the
block below is intentionally comment-free.

## Paste this (defaults ON — only the gaps the defaults miss)

```
packagemanager.posit.co
cloud.r-project.org
cran.r-project.org
cdn.playwright.dev
playwright.azureedge.net
timothyfraser.com
*.timothyfraser.com
fonts.googleapis.com
fonts.gstatic.com
cdn.jsdelivr.net
cdnjs.cloudflare.com
download.pytorch.org
data.pyg.org
```

With defaults ON, npm (`registry.npmjs.org`), PyPI (`pypi.org`,
`files.pythonhosted.org`), GitHub, and Ubuntu apt (`*.ubuntu.com`) are already granted —
so the list above is everything else the run needs.

## What each line is for

| Domain(s) | Why |
|---|---|
| `packagemanager.posit.co` | Posit Package Manager — **prebuilt binary** R packages. `prepare-env.sh` prefers it because it's far faster than compiling from CRAN source. Not in the default Trusted list. |
| `cloud.r-project.org`, `cran.r-project.org` | R itself + the `install.packages()` fallback when Posit is unavailable. CRAN is **not** in the default Trusted list — this (or Posit) is the #1 thing that silently breaks R in cloud sessions. `cloud.r-project.org` is a CDN that serves the apt repo, the signing key, and source package downloads. (If both Posit and CRAN are blocked, only Ubuntu's `r-cran-*` debs via `*.ubuntu.com` are available — enough for most cases but not `xgboost`.) |
| `cdn.playwright.dev`, `playwright.azureedge.net` | Chromium binary download for the Playwright MCP server (npm itself is in the defaults). |
| `timothyfraser.com`, `*.timothyfraser.com` | The live course site the personas browse. **Optional** — the site is mirrored in the repo under `docs/`, so you can drop these and the labs still work offline. |
| `fonts.googleapis.com`, `fonts.gstatic.com`, `cdn.jsdelivr.net`, `cdnjs.cloudflare.com` | Fonts/CDN assets the rendered course site pulls. Optional, paired with the course-site lines. |
| `download.pytorch.org`, `data.pyg.org` | torch / torch-geometric wheels for the Python GNN labs (10, 11). Drop if no persona runs the Python GNN track. |

## Optional add-ons (only if needed)

```
api.anthropic.com
apache.jfrog.io
```

- `api.anthropic.com` — only if a persona exercises the `ellmer`/LLM-call labs live.
- `apache.jfrog.io` — only if the `arrow` R package fails building from source and tries to
  fetch a prebuilt C++ library. Usually unnecessary.

## If you turn the defaults OFF instead

Then also add the pieces the Trusted bundle was covering:

```
registry.npmjs.org
pypi.org
files.pythonhosted.org
archive.ubuntu.com
security.ubuntu.com
*.ubuntu.com
ppa.launchpad.net
github.com
api.github.com
codeload.github.com
raw.githubusercontent.com
objects.githubusercontent.com
```
