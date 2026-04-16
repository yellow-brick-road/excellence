# Command: $flag-cleanup

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


> Command name: `devex_flag_cleanup`
> Description: Detect stale feature flags, flags at 100% rollout still in code, orphan flags. Generate cleanup plan with Jira tickets.
> Agent: DevEx

## Trigger

`$flag-cleanup` or "flag cleanup", "stale flags", "feature flags"

## Workflow

1. `subagent_configcat` → list all flags with last toggle date and rollout %
2. Detect stale flags (enabled for X months, never toggled)
3. Detect 100% rollout flags (cleanup candidates)
4. Scan codebase → find flag usage in code (grep for flag keys)
5. Cross-reference: flags in ConfigCat vs flags in code
6. Detect orphan flags (in ConfigCat but not in code, or vice versa)
7. Generate cleanup plan with priority
8. Optionally: `subagent_jira` → create cleanup tickets

## Output

- Total flags count
- Stale flags (with age and last toggle date)
- 100% rollout flags (ready to remove from code)
- Orphan flags (mismatch between ConfigCat and codebase)
- Cleanup plan with effort estimates
- Jira tickets created (if requested)

## Phase

Phase 2 (requires ConfigCat subagent)
