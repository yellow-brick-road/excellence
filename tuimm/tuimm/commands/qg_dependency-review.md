---
name: qg_dependency-review
description: "Triage Renovate Bot MRs. Use when: user says 'dependency review', 'renovate', or 'check dependencies'."
---

# Command: $qg_dependency-review

Reactive triage of Renovate Bot MRs — analyze changelogs, assess codebase impact, approve or flag.

## Services

Ask the user which project to review. If not specified, ask before proceeding.

## Process

### 1. List Renovate MRs

Delegate to tuimm_subagent_gitlab:
- List open MRs authored by Renovate Bot (or similar dependency bots)
- Get title, source branch, pipeline status for each

### 2. Analyze Each MR

For each Renovate MR:

#### a. Parse Update
- Delegate to tuimm_subagent_gitlab: get diff (package.json/lock changes)
- Extract: package name, old version → new version, update type (patch/minor/major)

#### b. Scan Codebase Usage
- Search codebase for imports and API usage of the package (grep, glob, read)
- Identify which files/modules depend on it

#### c. Assess Impact
- For major/minor: check changelog for breaking changes
- Cross-reference breaking changes with actual usage in the codebase
- If breaking changes don't affect any used APIs → safe

#### d. Check Pipeline
- Delegate to tuimm_subagent_gitlab: pipeline status (tests passing?)

#### e. Check Quality
- Delegate to tuimm_subagent_sonar: any new issues introduced?

#### f. Decision

| Update Type | Tests Pass | Breaking Changes Affect Us | Decision |
|-------------|------------|---------------------------|----------|
| patch | ✅ | N/A | APPROVE |
| minor | ✅ | No | APPROVE |
| minor | ✅ | Yes | NEEDS ATTENTION |
| minor | ❌ | — | BLOCK |
| major | ✅ | No | APPROVE (with note) |
| major | ✅ | Yes | NEEDS ATTENTION |
| major | ❌ | — | BLOCK |
| security fix | ✅ | — | APPROVE (priority) |
| any | ❌ | — | BLOCK |

### 3. Output

Present results using the qg-dependency-review template. Follow it EXACTLY.

### 4. Ask User

For each APPROVE: "Want me to approve and merge?"
For NEEDS ATTENTION: "Want me to add a comment with the analysis?"

NEVER approve or merge without explicit user confirmation.
