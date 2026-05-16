# SYSEN 5470 — Quickstart

Welcome. You've landed in the SYSEN 5470 course repo. If you're new to Git or
GitHub, you're in the right place — this folder walks you through the minimum
setup to follow along with the course.

> 💡 **The pretty version of this guide lives on the course website:**
> [tmfraser.com/netsci/help/github-setup.html](https://tmfraser.com/netsci/help/github-setup.html)
> Same content, prettier formatting, screenshots, OS tabs.

---

## Six steps

1. [Install Git](#1-install-git)
2. [Make a GitHub account](#2-make-a-github-account)
3. [Clone the course repo](#3-clone-the-course-repo)
4. [Make your project repo](#4-make-your-project-repo)
5. [Basic add / commit / push](#5-basic-add--commit--push)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. Install Git

Git is the command-line tool. GitHub is the hosting service. You need Git
locally before GitHub becomes useful.

- **macOS:** open Terminal, run `git --version`. If it prompts you to install
  Xcode command-line tools, accept. Otherwise you already have it.
- **Windows:** install [Git for Windows](https://git-scm.com/download/win).
  Includes Git Bash — keep it checked.
- **Linux:** `sudo apt install git` (Debian/Ubuntu) or your distro's
  equivalent.

Verify:

```sh
git --version
# → git version 2.43.0  (any 2.x is fine)
```

Tell Git who you are, once per machine:

```sh
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
```

---

## 2. Make a GitHub account

If you already have one, skip. If not:

- Sign up at <https://github.com/signup>. The free tier is plenty.
- Generate a **Personal Access Token** (PAT) for command-line use:
  Settings → Developer settings → Personal access tokens → Tokens (classic)
  → Generate new token. Scope: `repo` is enough. Save it — GitHub only shows
  it once.
- When Git asks for a password, paste the PAT.

SSH keys also work — see GitHub's
[SSH guide](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
if you'd rather. The course doesn't care which you pick.

---

## 3. Clone the course repo

```sh
# navigate to your code folder, then:
git clone https://github.com/timothyfraser/netsci.git
cd netsci
ls
```

You should see folders like `docs/`, `code/`, and this top-level `README.md`.

To pull the latest updates each week:

```sh
cd netsci
git pull
```

> You won't push to this repo — it's read-only for students. The course pushes
> *to* you; you push your own work to a separate repo (step 4).

---

## 4. Make your project repo

Your project case studies live in your own private GitHub repo.

1. On GitHub, click **New repository**. Name it `netsci-project` (or whatever).
   Set it to **Private**.
2. On your laptop:

```sh
mkdir netsci-project
cd netsci-project
git init
mkdir code data report

echo "# My SYSEN 5470 Project" > README.md
echo "3 project case studies. Each lives under code/." >> README.md

git add .
git commit -m "Initial commit"

# replace USERNAME with your GitHub handle
git remote add origin https://github.com/USERNAME/netsci-project.git
git branch -M main
git push -u origin main
```

Add Tim (`timothyfraser`) as a collaborator on your repo so he can read it
without it being public.

### Suggested layout

```
netsci-project/
├── README.md           # short overview + which 3 case studies you picked
├── code/
│   ├── 01-centrality/  # your first project case study
│   │   ├── project.R   # OR project.py
│   │   └── report.pdf
│   ├── 02-clustering/
│   └── 03-routing/
├── data/               # raw inputs (CSVs, edgelists)
└── notes/              # scratch, sketches, anything
```

---

## 5. Basic add / commit / push

After every meaningful chunk of work:

```sh
# 1. see what's changed
git status

# 2. stage the changes you want to commit
git add code/01-centrality/project.R
# or stage everything modified:
git add .

# 3. record the change with a short message
git commit -m "Centrality: first pass, top-10 nodes by betweenness"

# 4. push to GitHub
git push
```

That's the whole loop. **Commit often, in small chunks, with short messages.**

### Pull before push

```sh
git pull   # pull down anything new
git push   # then send yours up
```

### What NOT to commit

- Large datasets (over ~50 MB)
- Credentials (`.env` files, API keys)
- Anything inside `node_modules/`, `.Rproj.user/`, `__pycache__/`

Add a `.gitignore` with common patterns —
[github/gitignore](https://github.com/github/gitignore) has templates.

---

## 6. Troubleshooting

### `fatal: not a git repository`

`cd` into the folder that has the `.git` directory, or run `git init` if you
intended to start one here.

### Stuck in vim during a commit

Press `Esc`, type `:wq`, press `Enter`. Use `git commit -m "your message"`
next time to skip the editor entirely.

### `Updates were rejected because the tip of your branch is behind`

```sh
git pull --rebase
git push
```

### `Permission denied (publickey)`

You're using SSH but your key isn't registered with GitHub. Either set up the
SSH key (link above) or switch the remote to HTTPS:

```sh
git remote set-url origin https://github.com/USERNAME/netsci-project.git
```

### Accidentally committed a big file / a secret

If you haven't pushed:

```sh
git reset HEAD~          # undo the last commit, keep changes
# then add the file to .gitignore and recommit
```

If you already pushed a secret: **rotate it.** Git history doesn't forgive —
the secret is in the repo even if you delete the file in a new commit.

---

For everything else, see the course website's
[FAQ](https://tmfraser.com/netsci/help/faq.html) or the
[full GitHub Setup page](https://tmfraser.com/netsci/help/github-setup.html).
