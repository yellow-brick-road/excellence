---
name: dev_implement
description: "Ad-hoc implementation without Jira ticket. Use when: user says 'implement [description]' or describes a change to make."
---

# Command: $dev_implement

Implement a change described by the user — no Jira ticket required.

## Process

Same as $dev_solve but:
- Skip step 1 (Jira fetch) — requirements come from user description
- Skip step 10 (Jira transition, AI usage tracking) — no ticket to update
- Branch naming: `chore/{short-description}` or `feature/{short-description}`

Present results using the dev-solve template. Follow it EXACTLY — LAST STEP, nothing after this.
