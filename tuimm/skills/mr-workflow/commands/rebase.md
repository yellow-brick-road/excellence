---
name: mr_rebase
description: "Rebase a merge request on target branch. Use when: user says 'rebase [MR-ID]'."
---

# Command: $mr_rebase

Rebase MR on target branch via GitLab API.

## Process

1. Resolve MR project from context or ask user
2. Rebase via tuimm-subagent_gitlab using GitLab API endpoint
3. Present result using the mr-rebase template. Follow it EXACTLY — LAST STEP, nothing after this.

## Rules

- ALWAYS use GitLab API rebase, NEVER local git rebase + force push
