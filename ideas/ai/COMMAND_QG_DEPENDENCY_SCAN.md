# Command: $dependency-scan

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


> Command name: `qg_dependency_scan`
> Description: Proactive dependency analysis — find outdated packages, assess breaking changes against codebase, auto-update safe ones, register blockers.
> Agent: Quality Guardian

## Trigger

`$dependency-scan` or "scan dependencies", "check updates", "dependency scan"

## Coexistence with $dependency-review

- `$dependency-review` — reactive, triages existing Renovate Bot MRs
- `$dependency-scan` — proactive, scans for updates independently of Renovate
- Both coexist. Different triggers, different workflows, same domain

## Workflow

1. Read `package.json` (root + workspaces) → build full dependency list with current versions
2. For each dependency (or batch by scope):
   a. npm registry → get latest available version
   b. Skip if already up to date
   c. Determine update type: patch / minor / major
   d. Scan codebase → find imports and API usage of the package
   e. Cross-reference: do breaking changes affect actual usage in this repo?
   f. Consult dependency graph → which downstream repos consume this package?
   i. If downstream repos exist: assess cross-repo impact
   j. Decision:
      - **SAFE** → create update MR via `subagent_gitlab`
      - **NEEDS_MIGRATION** → create Jira ticket via `subagent_jira` with migration plan
      - **BLOCKED** → register in `DEPENDENCY_DECISIONS.md` with exact reason
3. Update `DEPENDENCY_DECISIONS.md` (create if doesn't exist)
4. Re-check previously blocked entries → has the blocker been resolved in a newer version?
5. Generate summary report

## Decision Criteria

| Update Type | Breaking Changes Affect Us | Action |
|-------------|---------------------------|--------|
| patch | N/A | SAFE → MR |
| minor | No | SAFE → MR |
| minor | Yes | NEEDS_MIGRATION → Jira ticket |
| major | No | SAFE → MR (with note) |
| major | Yes, small scope | NEEDS_MIGRATION → Jira ticket |
| major | Yes, large scope | BLOCKED → decision log |
| security fix | Any | SAFE → MR (priority, flag if breaking) |

## Output

### Summary
- Total dependencies scanned
- Up to date (no action)
- SAFE updates (MRs created)
- NEEDS_MIGRATION (Jira tickets created)
- BLOCKED (registered in decision log)
- Previously blocked now unblocked

### Decision Log Entry Format

See: `SKILL_DEPENDENCY_GOVERNANCE.md`

## Skill

Uses `dependency-governance` skill for decision framework and log format.

## Internal Package Intelligence

When scanning internal packages (`@dx/*`, shared Nuxt module):

1. The agent has access to the library's `$release` changelog — full AST diff, not just commit messages
2. Cross-reference breaking changes with actual consumer usage
3. **Auto-fix capability**: if changes are mechanical (renamed props, changed imports, deprecated API with replacement), apply fixes directly in the update MR
4. MR comment explains each change: what broke, why it's safe, what was auto-fixed
5. See `REPO_STRATEGY.md` → Auto-Propagation section for full flow

### Auto-Fix Scope

Can fix: renamed props/events/slots/exports, changed import paths, deprecated API with equivalent replacement.
Cannot fix: removed features without replacement, changed behavior, architectural changes.

## Phase

Phase 2 (ships with Quality Guardian)
