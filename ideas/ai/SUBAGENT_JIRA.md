# Idea: Jira Subagent

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


## Title

Tool subagent for Jira operations via TUI MCP Gateway.

## Context

API wrapper for Jira. No judgment, no orchestration — receives instructions, executes, reports back. Connected through the centralized MCP Gateway (SSO, RBAC, audited). Used by Quality Guardian, Observability, DevEx, and Knowledge agents.

Based on existing `subagent_jira` which uses Atlassian MCP (`mcp.atlassian.com`) with ADF formatting for descriptions.

## MCP Connection

Via TUI MCP Gateway → Jira Cloud API (Atlassian)

## Capabilities

### Read
- Search tickets by JQL (project, status, assignee, labels, sprint)
- Get ticket details (title, description, acceptance criteria, comments, status)
- Get sprint data (active sprint, velocity, carryover)
- Get board/project configuration
- List transitions available for a ticket

### Write
- Create tickets (with ADF formatting, labels, components, story points)
- Update ticket fields (status, assignee, labels, priority)
- Add comments to tickets
- Transition ticket status
- Link tickets to each other (blocks, relates to, duplicates)
- Bulk operations (batch update labels, move tickets)

### Templates
- Standardized ticket templates per type (feature, bug, spike, tech debt, hotfix)
- Auto-populate fields based on context (repo, team, sprint, epic)
- Enforce minimum quality (description, acceptance criteria, labels)
- Bug template with reproduction steps, environment, expected vs actual
- Spike template with time-box, research questions, deliverables

### Intelligence (light)
- Detect duplicate tickets before creation
- Suggest labels and components based on content
- Validate ticket completeness before submission
- Link related tickets automatically

## Used By

- Quality Guardian → create tech debt tickets, track issue resolution
- Observability Agent → create bug tickets from error investigation
- DevEx Agent → sprint health, workflow automation
- Knowledge Agent → link docs to tickets, extract sprint data
- Excellence Default → ad-hoc ticket operations
