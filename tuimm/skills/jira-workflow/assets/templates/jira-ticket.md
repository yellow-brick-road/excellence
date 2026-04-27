---
name: jira-ticket
description: "Jira ticket structure template. Use when: creating or editing tickets via $jira_create-ticket or $jira_edit-ticket. Contains: section order, content expectations, ADF heading mapping."
---

## Description

What this ticket is about. Clear, concise, one paragraph. What needs to happen and why it matters.

## Background

Context the implementer needs. Prior art, related tickets, links, technical constraints. Skip if the description is self-explanatory.

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2

Use "Given/When/Then" for complex behavior, plain bullets for simple checks. Each criterion independently verifiable.

## Definition of Done

- [ ] Code reviewed and approved
- [ ] Tests passing (unit + existing integration)
- [ ] No new SonarQube critical/blocker issues
- [ ] Pipeline green on feature branch
- [ ] Tested on feature branch URL

RULES: This is the COMPLETE output. Do NOT add extra sections, commentary, or formatting beyond what is defined above.
