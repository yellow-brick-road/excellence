# Skill: dependency-governance

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


## Intended Agents

Primary: quality_guardian
Also useful for: excellence_default, excellence_dev

## Purpose

Decision framework for dependency updates: when to update, when to block, and how to document decisions.

## Decision Log

Every repo using `$dependency-scan` maintains a `DEPENDENCY_DECISIONS.md` at the repo root.

### Format

```markdown
# Dependency Decisions

> Auto-maintained by Quality Guardian via $dependency-scan.
> Manual edits allowed — the agent preserves them.

## Blocked Updates

| Package | Current | Available | Reason | Date | Revisit |
|---------|---------|-----------|--------|------|---------|
| example-pkg | 2.1.0 | 3.0.0 | `useExample()` returns `Promise<T>` instead of `T` — used synchronously in 12 files | 2026-02-25 | 2026-04-01 |

## Pending Migration

| Package | Current | Target | Ticket | Effort | Notes |
|---------|---------|--------|--------|--------|-------|
| example-lib | 1.x | 2.x | DIS-4567 | 2 days | Migration guide: [link] |

## Resolved

| Package | Was Blocked At | Updated To | Resolution | Date |
|---------|---------------|------------|------------|------|
| other-pkg | 4.0.0 | 4.1.0 | Breaking change reverted in 4.1.0 | 2026-03-10 |
```

### Rules

1. **Reason must be exact** — not "breaking changes", but "method `X` removed, used in `FileA.vue`, `FileB.vue`"
2. **Revisit date is mandatory** — blocked entries must be re-evaluated periodically
3. **Resolved entries are kept** — they serve as historical record
4. **Cross-repo impact noted** — if blocking affects downstream repos, list them

## Decision Framework

### SAFE (auto-update)

- Patch updates (bug fixes, no API changes)
- Minor updates where breaking changes don't affect our usage
- Major updates where breaking changes don't affect our usage
- Security fixes (always prioritize, flag if breaking)

### NEEDS_MIGRATION (Jira ticket)

- Breaking changes affect our code but migration is feasible
- Effort estimate included in ticket
- Link to migration guide if available
- Ticket blocks the update — update happens after migration

### BLOCKED (decision log)

- Breaking changes affect our code and migration is non-trivial
- No migration path available yet
- Upstream issue pending resolution
- Incompatible with other dependencies (version conflict)

## Cross-Repo Awareness

When scanning a shared package (`@dx/*`, `b2c-nuxt-libraries`):

1. Identify all downstream repos that consume it
2. Assess if the update breaks downstream consumers
3. If yes: the update is BLOCKED or NEEDS_MIGRATION at the shared package level
4. Note affected downstream repos in the decision log

## Re-evaluation

On every `$dependency-scan` run:

1. Check all BLOCKED entries
2. For each: is a newer version available that resolves the blocker?
3. If yes: move from Blocked to Resolved, attempt update
4. If revisit date passed: flag for manual review