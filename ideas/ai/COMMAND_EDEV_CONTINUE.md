# Command: $continue

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


> Command name: `edev_continue`
> Description: Resume an interrupted workflow. Picks up where the last solve or implement left off.
> Agent: Excellence Dev

## Trigger

`continue` or "resume", "keep going", "where were we"

## Workflow

1. **Read plan from `.plan/`** — the plan is the source of truth for state
2. Check current git state (branch, uncommitted changes, last commit)
3. Determine what was in progress (solve ticket or ad-hoc implement)
4. Assess progress against plan: which steps are done, which are pending
5. If solve: cross-reference with Jira ticket for any updates
6. Resume execution from the next pending plan step
7. Follow same quality gates as solve/implement

## Output

- Resumed workflow with context summary
- Remaining work completed
- Same quality gates applied (lint, test, review)

## Phase

Phase 2 (ships with Excellence Dev)
