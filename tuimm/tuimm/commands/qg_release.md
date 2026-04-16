---
name: qg_release
description: "Analyze changes and publish release. Use when: user says '$release' or '$release [package-name]'."
---

# Command: $qg_release

Analyze changes since last release, propose version bump, generate changelog, publish on approval.

## Process

### 1. Determine Scope

- If package name provided: scope to that package (monorepo)
- If no package name in monorepo: analyze all packages, propose releases for those with changes
- If single-package repo: scope to root

### 2. Find Last Release

Delegate to tuimm_subagent_gitlab:
- Find last release tag for the package
- Get all MRs merged since that tag

### 3. Analyze Code Diff

Compare last tag → HEAD:
- New/removed/changed exports
- Modified type signatures and interfaces
- Added/removed component props
- Dependency changes in `package.json`
- Read actual code, not just commit messages

### 4. Fetch Ticket Context

Delegate to tuimm_subagent_jira:
- For each MR with a linked ticket: fetch title and description
- Use for changelog context

### 5. Classify Changes

| Classification | Triggers |
|---------------|----------|
| **Major** | Removed exports, changed public interfaces, breaking prop changes |
| **Minor** | New exports, new features, new component props |
| **Patch** | Bug fixes, internal refactors, dependency bumps |

Highest classification wins.

### 6. Generate Changelog

Group by category:

```markdown
## [X.Y.Z] — {DATE}

### ⚠️ Breaking Changes
- Removed `exportName` — use `newExportName` instead (!{MR_ID}, {TICKET-ID})

### ✨ Features
- Added `ComponentName` prop `propName` (!{MR_ID}, {TICKET-ID})

### 🐛 Fixes
- Fixed race condition in `functionName` (!{MR_ID}, {TICKET-ID})

### 🏗️ Internal
- Refactored `moduleName` for clarity (!{MR_ID})
```

### 7. Present Proposal

Present results using the qg-release template. Follow it EXACTLY.

**Wait for user confirmation. NEVER publish without approval.**

User can adjust: version number, changelog content, classification.

### 8. Publish (on approval)

1. Bump version in `package.json`
2. Update `CHANGELOG.md`
3. Commit: `chore(release): {package}@{version}`
4. Remind user to push
5. After push confirmed: create git tag via tuimm_subagent_gitlab
6. Run `npm publish` (shell)
7. Delegate to tuimm_subagent_jira: comment on related tickets with release info

### 9. Monorepo Cross-Impact

If package A was released and package B depends on A:
- Flag B for potential version bump
- "Package {B} depends on {A}@{old}. Want me to update it?"
