
# Git

Git rules for all TUIMM agents.

## Confirmation Required

These operations require explicit user confirmation before executing:
- `git commit` (any form)
- `git pull`, `git merge`, `git rebase`
- `git stash`, `git stash pop`, `git stash drop`
- Staging or unstaging files (`git add`, `git reset`)
- Any operation that modifies the working tree or history

**Exception:** Branch creation and checkout during structured command workflows (`$dev_solve`, `$mr_review`) are pre-authorized by the user invoking the command.

## Read-Only (no confirmation needed)

`git status`, `git diff`, `git log`, `git branch`, `git fetch`

## Branch Naming

Use `-` (hyphens) in branch names, NEVER `_` (underscores). Underscores cause problems with semantic-release and other tooling.

### Before creating a branch

Follow this flow every time:

**Step 1 — Check for cached config.** Look for `docs/BRANCH_RULES.md` in the repo. If it exists, read it and confirm with the user: "Branch rules found — last updated {date}. Still current?" If confirmed, use those rules. If not, re-investigate (Step 2).

**Step 2 — Investigate the repo (only if no cached config or user says it's outdated):**

1. **CI template** — read `.gitlab-ci.yml`. Check `include:` to find the shared template. Look at `workflow:rules` to determine which branch prefixes trigger pipelines (e.g., `feature/*`, `bugfix/*`, `hotfix/*`). Note whether `chore/*` or other prefixes are supported
2. **Semantic-release config** — read `release.config.*`, `.releaserc.*`, or `package.json` release section. Check which branch patterns trigger releases, whether prereleases are configured, and what branch naming they expect

3. **Summarize findings** to the user: "This repo uses {template}, pipelines trigger on {prefixes}, semantic-release is configured for {branches}. Branch prefix should be {recommendation}."

**Step 3 — Suggest caching.** After investigating, suggest: "Want me to save this as `docs/BRANCH_RULES.md` so we don't have to check next time?" If yes, create the doc with: CI template name, valid branch prefixes, semantic-release config summary, date.

### Standard prefixes (fallback if investigation not possible)

- Feature: `feature/{TICKET-ID}-{short-description}`
- Bugfix: `bugfix/{TICKET-ID}-{short-description}`
- Hotfix: `hotfix/{TICKET-ID}-{short-description}`

## Workspace Conventions

All repo clones go under `~/.kiro/temp/`. Never clone into CWD or random /tmp paths.

```
~/.kiro/temp/
├── mr/                          ← MR work (persistent until user cleans up)
│   ├── mr-{iid}-{repo_name}/
│   └── ...
├── dev/                         ← Dev work (persistent until user cleans up)
│   ├── {TICKET}-{repo_name}/
│   └── ...
├── weblate/                     ← Disposable (cleaned after command)
│   └── weblate-{timestamp}/
└── search/                      ← Disposable shallow clones (cleaned after use)
```

### Clone rules

- **mr/ and dev/** are persistent — user pushes from there. Do NOT delete after command
- **weblate/ and search/** are ephemeral — always clean up after use
- Clone URL: `git@ssh.source.tui:{project_path}.git`
- Naming includes identifier + repo for isolation: `mr-100-b2c-tuimusement-frontend`, `DIS-1234-b2c-nuxt-libraries`
- `mr_review` and `mr_comments` share the same clone for the same MR
- If workspace already exists: `git fetch --all --prune && git checkout {branch} && git pull`

### Cleanup

At session start, a background check scans mr/ and dev/ for stale workspaces (merged MRs, closed branches). The agent presents findings and asks before deleting anything.

## Rules

- NEVER commit `session.md` — local-only ephemeral file
- NEVER add `[skip ci]` in commits
- NEVER use `git commit --amend` — make extra commits instead
- NEVER force push
- NEVER use `git checkout origin/master -- .` or `git checkout origin/main -- .` — this replaces the working tree with master's content and causes divergence. Use `git merge` instead
- Prefer `git merge` over `git rebase`

All NEVER rules apply unless the user explicitly says otherwise.

## Pre-Push Sync

Before the user pushes (especially on long-lived feature branches):

```bash
git fetch --all --prune
git merge origin/master          # NOT rebase, NOT checkout
# resolve conflicts if any
rm -rf node_modules package-lock.json && npm install
# run tests locally
# commit lockfile changes if any
```

If merge conflicts appear, help the user resolve them. NEVER use `git checkout origin/master -- .` as a shortcut — it destroys the branch's changes.

## After Commit

Remind the user: "Push is yours — run `git fetch --all --prune && git merge origin/master` before pushing if your branch is behind."

## AI Usage Tracking

After committing work on a Jira ticket, set AI usage fields. Use `$jira_set-ai-usage` or let `$dev_solve` handle it automatically. See `AI_USAGE_TRACKING.md`.
