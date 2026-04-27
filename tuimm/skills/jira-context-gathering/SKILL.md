---
name: jira-context-gathering
description: "Jira ticket full context gathering checklist. Use when: any command reads a Jira ticket as input (create related ticket, edit ticket, solve ticket, investigate linked issue). Contains: required fields to fetch, subagent query pattern, common pitfalls."
---

# Jira Context Gathering

When a command needs to understand a Jira ticket, ALWAYS gather the full context in a single subagent call. A shallow read (summary + status) is never enough.

## Required fields

Ask the subagent for ALL of these explicitly:

| Category | Fields |
|----------|--------|
| Core | summary, description, status, type, priority |
| People | assignee, reporter |
| Classification | labels, components, fix version, sprint |
| Hierarchy | parent (epic or parent issue), subtasks / child issues |
| Links | ALL linked issues with link type (relates-to, blocks, blocked-by, duplicates, clones) |
| Activity | last 10 comments (often contain real requirements, decisions, context not in description) |
| Attachments | list with names, types, dates (mockups, specs, screenshots) |

## Subagent query pattern

Never say "get full details". Be explicit:

> Get ticket {KEY}: summary, description, status, type, priority, labels, components, fix version, sprint, assignee, reporter, parent issue or epic, all child issues/subtasks, all linked issues with link types, last 10 comments, and attachments list.

## Deep context

After getting the parent ticket, if it has sub-tasks or linked issues, make a SECOND subagent call to fetch full details of each one (summary, description, acceptance criteria, status, assignee, attachments, comments). A title + status is never enough — sub-tasks often contain the actual implementation spec, file lists, ACs, and risks that the parent story doesn't have.

Query pattern for the second call:
> Get full details of these N tickets: {KEY-1}, {KEY-2}, ... For each one: summary, description, acceptance criteria, all custom fields (especially Additional Details / customfield_12281), status, assignee, labels, comments, and attachments.

## Why this matters

- Parent/epic links provide project context and scope
- Linked issues reveal dependencies and related work
- Comments often contain the actual requirements (especially when description is empty)
- Attachments may include Figma links, specs, or mockups referenced nowhere else
- Child issues show what's already been broken down

## Pitfalls

- Jira MCP may not return parent in the default response — ask for it explicitly
- An empty description does NOT mean there's no context — check comments and attachments
- If the first query misses hierarchy, do a second query specifically for parent and children
