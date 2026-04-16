# Steering: Subagents

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


Tier 2 tool subagents available to all Excellence agents via MCP Gateway. Loaded as steering by every Tier 1 agent.

## Connection

All subagents connect through the TUI MCP Gateway (`mcp.tui.internal`). SSO-authenticated, RBAC-controlled, audited. Zero credentials on developer machines.

See: `MCP_GATEWAY.md`

## Subagent Reference

| Subagent | API | MCP Skill | Description |
|----------|-----|-----------|-------------|
| Jira | Atlassian Cloud | `mcp_atlassian` | Tickets, JQL search, ADF formatting, sprint data, transitions |
| GitLab | source.tui | `mcp_gitlab` | MRs, branches, pipelines, diffs, discussions, approvals |
| SonarQube | SonarQube API | `mcp_sonarqube` | Quality gates, issues, coverage, metrics, rules |
| Datadog | datadoghq.eu | `mcp_datadog` | Logs, APM traces, RUM, metrics, service maps |
| Figma | Figma API | `mcp_figma` | Design context, components, tokens, layout extraction |
| Confluence | Atlassian Cloud | `mcp_atlassian` | Pages, spaces, search (CQL), templates, labels |
| Contentful | Contentful API | — | Content models, entries, assets, environments, locales |
| ConfigCat | ConfigCat API | — | Feature flags, targeting rules, A/B tests, audit log |
| Weblate | Weblate API | — | Translation keys, locales, coverage, modules |

## Usage Rules

- Subagents are **API wrappers** — they execute, they don't decide
- Tier 1 agents provide judgment and orchestration
- Any Tier 1 agent can use any subagent within its domain
- Subagent-specific knowledge (ADF formatting, JQL syntax, CQL queries) stays in the subagent

## Agent → Subagent Mapping

| Agent | Subagents |
|-------|-----------|
| Excellence Default | all (master key) |
| Quality Guardian | SonarQube, GitLab, Jira, Datadog |
| Observability | Datadog, GitLab, Jira, SonarQube, Confluence, ConfigCat |
| DevEx | GitLab, Jira, ConfigCat, Weblate, Contentful, Confluence |
| Design System | Figma, GitLab, SonarQube, Weblate |
| Knowledge | Confluence, Jira, GitLab, Contentful |
| Excellence Dev | Jira, GitLab, SonarQube |
| Excellence MR | GitLab, SonarQube, Jira |

## Detailed Specs

For full capabilities per subagent, see individual docs:
- `SUBAGENT_JIRA.md`, `SUBAGENT_GITLAB.md`, `SUBAGENT_SONARQUBE.md`
- `SUBAGENT_DATADOG.md`, `SUBAGENT_FIGMA.md`, `SUBAGENT_CONFLUENCE.md`
- `SUBAGENT_CONTENTFUL.md`, `SUBAGENT_CONFIGCAT.md`, `SUBAGENT_WEBLATE.md`