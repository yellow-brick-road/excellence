---
name: jira_edit-ticket
description: |
  Edit an existing Jira ticket. Use when: user says 'edit ticket [KEY]',
  'update ticket [KEY]', 'editar ticket', or a parent agent needs to modify a Jira issue.
---

# Command: $jira_edit-ticket

Edit fields on an existing Jira ticket.

## Inputs

- **ticket**: Ticket key (e.g. DIS-1234). Required.
- **fields**: What to change — summary, description, acceptance criteria, assignee, labels, status, priority, or any other field.

## Process

1. Gather full ticket context via tuimm_subagent_jira following the tuimm-jira-context-gathering skill — parent, links, comments, attachments. If the ticket has sub-tasks or linked issues, fetch their full details too (second subagent call)
2. Show current values for the fields being changed
3. Ask user to confirm the changes
4. Convert description/comment content to ADF format (consult tuimm-jira-adf skill)
5. Update the ticket via tuimm_subagent_jira
6. Present result using the jira-ticket template for the updated ticket. Follow it EXACTLY — LAST STEP, nothing after this.

## Rules

- All description fields MUST use ADF — never plain text
- For status transitions: call getTransitionsForJiraIssue first to get valid transition IDs
- Show before/after for changed fields — never update silently
