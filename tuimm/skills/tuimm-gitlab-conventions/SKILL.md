---
name: tuimm-gitlab-conventions
description: |
  GitLab conventions for TUI Musement.
  Use when: creating MRs, resolving threads, querying GitLab API, or syncing branches.
  Contains: MR templates, title format, thread resolution rules, query limits, git sync patterns, API notes.
---

# GitLab Conventions

## MR Templates

Before creating any MR, check for templates:

```
.gitlab/merge_request_templates/Default.md
```

If a template exists, fill it. Never create an MR without checking first.

## MR Title Format

```
type(TICKET-ID): brief description
```

Types: `feat`, `fix`, `refactor`, `chore`, `docs`, `test`, `style`, `perf`

## Thread Resolution

- ONLY resolve threads from BOT comments (Qodo, automated reviewers)
- NEVER resolve threads from HUMAN reviewers — only the reviewer or author resolves those

## Query Limits

Always apply these filters to avoid overloading the API:

| Parameter | Rule |
|-----------|------|
| `state` | Always filter — default to `opened` |
| `per_page` | Always ≤ 10 |
| `scope` | Use specific scopes when possible |

## Git Sync

Before any MR or branch operation, always run:

```bash
git fetch --all --prune
```

## GitLab API

- Base URL: `https://source.tui/api/v4`
- SSH clone: `git@ssh.source.tui:` (NOT `source.tui`)
- Browse: `https://source.tui/{group}/{project}`
