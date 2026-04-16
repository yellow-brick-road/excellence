# Command: $dependency-review

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


> Command name: `qg_dependency_review`
> Description: Triage Renovate Bot MRs — analyze changelogs, assess codebase impact, approve or flag with detailed reasoning.
> Agent: Quality Guardian

## Trigger

`$dependency-review` or "dependency review", "renovate", "check dependencies", "npm updates"

## Workflow

1. `subagent_gitlab` → list open MRs by Renovate Bot
2. For each MR:
   a. `subagent_gitlab` → get diff (package.json/lock changes)
   b. Parse: extract package name, old version → new version, update type (major/minor/patch)
   c. Scan codebase → find imports and API usage of the package
   d. Cross-reference: do breaking changes affect actual usage?
   e. `subagent_gitlab` → check pipeline status (tests passing?)
   h. `subagent_sonar` → any new issues introduced?
   i. Decision: APPROVE / NEEDS ATTENTION / BLOCK
   j. `subagent_gitlab` → add comment with analysis, optionally approve

## Decision Criteria

| Update Type | Tests Pass | Breaking Changes Affect Us | Decision |
|---|---|---|---|
| patch | ✅ | N/A | APPROVE |
| minor | ✅ | No | APPROVE |
| minor | ✅ | Yes | NEEDS ATTENTION |
| minor | ❌ | — | BLOCK |
| major | ✅ | No | APPROVE (with note) |
| major | ✅ | Yes | NEEDS ATTENTION |
| major | ❌ | — | BLOCK |
| any | ❌ | — | BLOCK |
| security fix | ✅ | — | APPROVE (priority) |

## Output Per MR

- Package: name, old → new version, update type
- Changelog summary (key changes, breaking changes)
- Codebase impact (files using the package, affected APIs)
- Pipeline status
- Decision with reasoning
- GitLab comment posted on the MR

## Output Summary

- Total Renovate MRs reviewed
- Approved (safe to merge)
- Needs attention (manual review required)
- Blocked (failing tests or breaking changes)

## Phase 3 Potential

Renovate creates MR → GitLab webhook → bot → Quality Guardian runs $dependency-review automatically. Zero human intervention for safe updates.

## Phase

Phase 2 (ships with Quality Guardian)
