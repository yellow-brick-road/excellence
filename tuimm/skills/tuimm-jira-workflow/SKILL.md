---
name: tuimm-jira-workflow
description: Shared Jira commands for ticket creation, editing, commenting, and AI usage tracking. Available from all Tier 1 agents.
---

# Jira Workflow

Shared commands available from all TUIMM Tier 1 agents for Jira operations.

## Available Commands

- `$jira_create-ticket` — "create ticket", "new ticket" — Create a Jira ticket with structured template. Read the command from [commands/create-ticket.md](commands/create-ticket.md)
- `$jira_edit-ticket` — "edit ticket [KEY]" — Edit an existing Jira ticket. Read the command from [commands/edit-ticket.md](commands/edit-ticket.md)
- `$jira_comment-ticket` — "comment on [KEY]" — Add a comment to a Jira ticket. Read the command from [commands/comment-ticket.md](commands/comment-ticket.md)
- `$jira_set-ai-usage` — "set ai usage [KEY]" — Set AI usage tracking fields on a ticket. Read the command from [commands/set-ai-usage.md](commands/set-ai-usage.md)

## Templates

- [assets/templates/jira-ticket.md](assets/templates/jira-ticket.md) — Jira ticket structure
- [assets/templates/jira-comment.md](assets/templates/jira-comment.md) — Jira comment format
