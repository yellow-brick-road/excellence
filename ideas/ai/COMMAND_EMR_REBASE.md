# Command: $rebase

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


> Command name: `emr_rebase`
> Description: Rebase MR on target branch. Handles conflicts report if any.
> Agent: Excellence MR

## Trigger

`rebase [MR-ID]` or "rebase", "rebase this MR"

## Workflow

1. `subagent_gitlab` → get MR details (source branch, target branch)
2. `subagent_gitlab` → trigger rebase via API
3. If conflicts: report conflicting files and suggest resolution
4. If clean: confirm rebase completed

## Output

- Rebase completed confirmation
- Or: conflict report with affected files

## Phase

Phase 2 (ships with Excellence MR)
