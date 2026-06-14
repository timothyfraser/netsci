# MERGE-ME — apply the staged student permissions

A setup agent staged `.claude/settings.proposed.json` by merging the repo's existing
`.claude/settings.json` with `.claude/settings.students.json`. **Nothing was applied** —
your live `.claude/settings.json` is untouched.

## What to do

> Review `.claude/settings.proposed.json`; if it looks right, replace `.claude/settings.json`
> with it (or hand-add the listed entries below). These grant the student agents Python,
> file-writes, and Playwright navigate/click/type.

## Entries that would be ADDED to `permissions.allow`

- `Bash(python:*)`
- `Bash(python3:*)`
- `Bash(pip:*)`
- `Bash(pip3:*)`
- `Bash(git fetch:*)`  *(note: base already has `Bash(git fetch *)` with a space; this colon-form variant is added alongside it — harmless)*
- `Bash(git status:*)`
- `Bash(git log:*)`
- `Bash(git diff:*)`
- `Bash(git show:*)`
- `Bash(mkdir:*)`
- `Bash(cp:*)`
- `Bash(mv:*)`
- `Bash(ls:*)`
- `Bash(cat:*)`
- `Bash(head:*)`
- `Bash(tail:*)`
- `Bash(find:*)`
- `Bash(grep:*)`
- `Bash(wc:*)`
- `WebFetch`
- `mcp__playwright__browser_navigate`
- `mcp__playwright__browser_navigate_back`
- `mcp__playwright__browser_click`
- `mcp__playwright__browser_type`
- `mcp__playwright__browser_press_key`
- `mcp__playwright__browser_select_option`
- `mcp__playwright__browser_hover`
- `mcp__playwright__browser_wait_for`
- `mcp__playwright__browser_tabs`

## Entries that would be ADDED to `permissions.deny`

- `Bash(sudo:*)`
- `Bash(rm -rf /:*)`
- `Bash(rm -rf ~:*)`
- `Bash(chmod 777:*)`
- `Bash(git push:*)`
- `Bash(git commit:*)`
- `Read(./.env)`
- `Read(./**/.env)`

## Playwright server-name caveat

The allow-list uses the prefix `mcp__playwright__browser_*`. If `claude mcp list` shows the
Playwright server under a **different name**, these entries won't match and unattended runs
will stall on permission prompts. See the environment verification note in the setup agent's
final report for the detected server name.
