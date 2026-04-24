---
name: mr_approve
description: "Approve a merge request. Use when: user says 'approve [MR-ID]'."
---

# Command: $mr_approve

Approve a merge request via GitLab API.

## Process

1. Resolve MR project from context or ask user
2. Approve MR via tuimm_subagent_gitlab
3. Present result using the mr-approve template. Follow it EXACTLY — LAST STEP, nothing after this.
