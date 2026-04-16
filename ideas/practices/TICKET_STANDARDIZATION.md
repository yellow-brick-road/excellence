# Ticket Standardization for AI Agents

> Status: Idea (early)
> Author: Javier Fernández
> Created: 2026-03-04

## The Pain

AI agents (Excellence Dev, Quality Guardian, etc.) need structured, predictable ticket content to work effectively. Current Jira tickets vary wildly in format, detail level, and field usage across teams. An agent trying to solve a ticket often finds:

- Vague descriptions ("fix the thing")
- Missing acceptance criteria
- No technical context (which repo, which component, which environment)
- Inconsistent use of labels, components, and custom fields
- Critical info buried in comments instead of the description

When a human reads a bad ticket, they ask questions. When an agent reads a bad ticket, it guesses — or fails.

## The Tension

This collides with Agile orthodoxy:

- Agile says tickets should be "just enough" — lightweight, conversational
- Scrum says the conversation IS the requirement, not the ticket
- Teams resist templates as bureaucracy
- Product owners don't want to fill forms

Excellence can't mandate ticket formats. That's not the operating model. But we can:

1. **Provide templates that help, not hinder** — a good template saves time, it doesn't add it
2. **Make it opt-in with clear benefits** — "use this format and the agent can solve it autonomously"
3. **Let agents handle the gap** — if a ticket is incomplete, the agent asks for what's missing before starting

## Proposed Approach

### Connection to Spec-Driven Dev

The ticket is input. The agent's plan (`SPEC_DRIVEN_DEV.md`) is the technical interpretation. Structured tickets produce better plans — this is the incentive for adoption.

### Minimum Viable Ticket (for AI)

Fields that make a ticket agent-ready:

| Field | Why |
|-------|-----|
| Title with prefix (`[FE]`, `[BE]`) | Agent knows its domain |
| Repo/project reference | Agent knows where to work |
| Current behavior | Agent understands the problem |
| Expected behavior | Agent knows the goal |
| Acceptance criteria (checkboxes) | Agent can verify completion |
| Affected component/page | Agent can scope the change |

### Strategy

- **Don't enforce** — provide Jira templates that teams can adopt
- **Incentivize** — tickets using the template get faster agent resolution
- **Backfill** — Excellence Dev agent asks clarifying questions when fields are missing, then updates the ticket before starting work
- **Measure** — track agent success rate by ticket quality. Show the data: structured tickets = faster resolution

## Connection to Excellence

- The `tui_jira-task_template` skill already defines a format — this scales it as a guild recommendation
- Excellence Dev agent (`COMMAND_EDEV_SOLVE`) is the primary consumer
- Quality Guardian's dependency tickets (`COMMAND_QG_DEPENDENCY_SCAN`) auto-create structured tickets — leading by example

## Open Questions

- [ ] How much resistance will this get from product owners and scrum masters?
- [ ] Can we create Jira issue templates (not just text templates) that pre-fill fields?
- [ ] Should the agent refuse to work on tickets below a quality threshold, or always try?
- [ ] How do we handle legacy tickets that will never be reformatted?
