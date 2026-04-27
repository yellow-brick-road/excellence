---
name: jira_comment-ticket
description: |
  Add a comment to a Jira ticket. Use when: user says 'comment on [KEY]',
  'add comment to [KEY]', 'comentar en ticket', or a parent agent needs to post a Jira comment.
---

# Command: $jira_comment-ticket

Add a comment to an existing Jira ticket.

## Inputs

- **ticket**: Ticket key (e.g. DIS-1234). Required.
- **comment**: Comment text. Required.

## Process

1. Convert comment content to ADF format (consult tuimm-jira-adf skill)
2. Post comment via tuimm_subagent_jira
3. Present result using the jira-comment template. Follow it EXACTLY — LAST STEP, nothing after this.

## Rules

- Comments MUST use ADF — never plain text
- Show the formatted comment to the user before posting
