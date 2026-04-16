---
name: qg_dependency-scan
description: "Proactive dependency analysis. Use when: user says 'scan dependencies', 'check updates', or 'dependency scan'."
---

# Command: $qg_dependency-scan

Proactive scan — find outdated packages, assess breaking changes, create update MRs or Jira tickets.

## Coexistence with $qg_dependency-review

- `$qg_dependency-review` — reactive, triages existing Renovate Bot MRs
- `$qg_dependency-scan` — proactive, scans for updates independently of Renovate

## Process

### 1. Build Dependency List

Read `package.json` (root + workspaces if monorepo):
- All dependencies and devDependencies with current versions
- Group by scope (@dx/*, @nuxt/*, etc.)

### 2. Check Registry

For each dependency (or batch by scope):
- Query npm registry for latest available version
- Skip if already up to date
- Determine update type: patch / minor / major

### 3. Assess Each Outdated Package

#### a. Scan Codebase Usage
- Search for imports and API usage (grep, glob, read)
- Identify affected files/modules

#### b. Check Breaking Changes
- For major updates: review changelog/release notes
- Cross-reference breaking changes with actual usage

#### c. Cross-Repo Impact
- For internal packages (@dx/*): check dependency graph — which downstream repos consume this?
- Flag cross-repo breaking changes

#### d. Decision

| Update Type | Breaking Changes Affect Us | Action |
|-------------|---------------------------|--------|
| patch | N/A | SAFE → propose MR |
| minor, no breaking | No | SAFE → propose MR |
| minor, breaking | Yes | NEEDS MIGRATION → propose Jira ticket |
| major, no breaking | No | SAFE → propose MR (with note) |
| major, small scope | Yes | NEEDS MIGRATION → propose Jira ticket |
| major, large scope | Yes | BLOCKED → log reason |
| security fix | Any | SAFE → propose MR (priority) |

### 4. Internal Package Intelligence

For `@dx/*` packages:
- Check if the library has a changelog with AST diff
- If changes are mechanical (renamed props, changed imports, deprecated API with replacement): note as auto-fixable
- Flag non-mechanical changes for manual migration

### 5. Output

Present results using the qg-dependency-scan template. Follow it EXACTLY.

### 6. Ask User

- "Want me to create update MRs for the SAFE packages?"
- "Want me to create Jira tickets for the NEEDS MIGRATION packages?"

NEVER create MRs or tickets without explicit user confirmation.
