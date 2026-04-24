---
name: jira_create-ticket
description: |
  Create a Jira ticket with structured template. Use when: user says 'create ticket',
  'new ticket', 'crear ticket', or a parent agent needs to create a Jira issue.
---

# Command: $jira_create-ticket

Create a Jira ticket following the jira-ticket template and ADF format.

## Inputs

- **project**: Project key (e.g. DIS, CDT). Required — never assume a default.
- **type**: Issue type (Story, Task, Bug, Debt, Risk). Default: Task.
- **summary**: Ticket title. Required.
- **description**: What needs to happen and why.
- **acceptance_criteria**: List of verifiable criteria (optional).
- **assignee**: Assignee email or display name (optional).
- **labels**: Labels to apply (optional).
- **sprint**: Sprint name or ID (optional).

## Process

1. If any required input is missing, ask the user
2. If a reference ticket is provided (URL, key, or "related to X"), gather its full context following the tuimm-jira-context-gathering skill — parent, links, comments, attachments. If the ticket has sub-tasks or linked issues, fetch their full details too (second subagent call). Present a summary to the user before proceeding
3. Structure the ticket following the jira-ticket template:
   - Description section
   - Background section (if context provided)
   - Acceptance Criteria section (if provided)
   - Definition of Done section (standard checklist)
4. Convert all content to ADF format (consult tuimm-jira-adf skill)
5. Create the ticket via tuimm_subagent_jira
6. Present result using the jira-ticket template for the created ticket. Follow it EXACTLY — LAST STEP, nothing after this.

## Rules

- All description and comment fields MUST use ADF — never plain text
- Project key is always required — never assume
- Standard issue types only: Story, Task, Bug, Debt, Risk
