# Command: $approve

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


> Command name: `emr_approve`
> Description: Quick approve MR with summary. Runs lightweight checks and approves if no blockers found.
> Agent: Excellence MR

## Trigger

`approve [MR-ID]` or "approve", "lgtm"

## Workflow

1. `subagent_gitlab` → fetch MR diff
2. Quick scan for CRITICAL issues only (security, breaking changes)
3. `subagent_sonar` → verify quality gate passes
4. `subagent_gitlab` → check pipeline status
5. If no blockers: `subagent_gitlab` → approve MR with summary comment
6. If blockers found: report issues, do NOT approve

## Output

- Approval posted on MR with summary
- Or: blocker report explaining why approval was withheld

## Phase

Phase 2 (ships with Excellence MR)
