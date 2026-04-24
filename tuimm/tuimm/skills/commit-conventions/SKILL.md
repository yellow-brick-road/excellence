---
name: commit-conventions
description: |
  Conventional commit format and process. Use when:
  - Creating git commits
  - Writing commit messages
  - Deciding commit type (feat/fix/refactor/chore/docs/test/style/perf)
  Contains: type definitions, scope rules, commit process, verification
---

# Commit Conventions

## Format

```
{type}({scope}): {description}
```

## Types

| Type | Use for |
|------|---------|
| feat | New feature |
| fix | Bug fix |
| refactor | Code refactoring (no functional changes) |
| docs | Documentation changes |
| test | Adding or updating tests |
| chore | Maintenance tasks (deps, config) |
| style | Code style changes (formatting) |
| perf | Performance improvements |

## Scope

- Use ticket key if available: `feat(DIS-1234): add loading spinner`
- Use `NO-TICKET` if no ticket: `fix(NO-TICKET): correct typo`
- Can also use component/area: `feat(auth): add login validation`

## Description Rules

- Brief (max 50 chars ideally)
- Lowercase, no period at end
- Imperative mood ("add" not "added")
- Describe WHAT, not HOW

## Process

1. Check what's staged: `git diff --staged --stat`
2. If nothing staged: report and stop
3. Determine type from the changes
4. Determine scope (ticket ID or NO-TICKET)
5. Write description — brief, human-like, imperative mood
6. Show commit message to caller — wait for confirmation
7. Execute: `git commit -m "{message}"`
8. Verify: `git log -1 --oneline` — if output shows your message, report SUCCESS with hash. If not, report FAILURE

## Rules

- NEVER add `[skip ci]`
- NEVER use `git commit --amend`

## Good Examples

```
feat(DIS-1234): add loading spinner to checkout
fix(DIS-5678): handle null response from API
refactor(NO-TICKET): simplify error handling logic
chore(DIS-9012): update dependencies
```
