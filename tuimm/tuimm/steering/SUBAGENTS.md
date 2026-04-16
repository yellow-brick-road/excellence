# Subagents

Tool subagents available to TUIMM agents. Each connects to an external API via MCP.

## Setup

Each developer configures their own MCP connections with personal tokens. No centralized gateway — direct MCP connections per developer machine.

Required tokens:
- **Jira**: OAuth via browser (mcp-remote → mcp.atlassian.com). No env var needed
- **Confluence**: Same OAuth as Jira (shared session)
- **GitLab**: Personal access token (source.tui)
- **SonarQube**: API token (SonarQube instance)
- **Datadog**: API + App key (tui-musement.datadoghq.eu)
- **Figma**: Personal access token (figma.com)
- **Contentful**: CMA token (contentful.com)
- **ConfigCat**: API user + password (configcat.com)

See `SETUP.md` for detailed instructions and URLs.

## Subagents

| Subagent | API | Description |
|----------|-----|-------------|
| tuimm_subagent_jira | Atlassian Cloud (mcp.atlassian.com) | Tickets, JQL search, sprint data, transitions, comments |
| tuimm_subagent_confluence | Atlassian Cloud (mcp.atlassian.com) | Pages, CQL search, spaces, comments, content management |
| tuimm_subagent_figma | Figma API (figma-developer-mcp) | Design context, components, tokens, layout extraction |
| tuimm_subagent_contentful | Contentful CMA (@contentful/mcp-server) | Content types, entries, assets, locales, publishing |
| tuimm_subagent_configcat | ConfigCat Management API (@configcat/mcp-server) | Feature flags, targeting, segments, environments, audit |
| tuimm_subagent_gitlab | source.tui | MRs, branches, pipelines, diffs, discussions, approvals, git operations, commits |
| tuimm_subagent_sonar | SonarQube API | Quality gates, issues, coverage, metrics |
| tuimm_subagent_datadog | tui-musement.datadoghq.eu | Logs, APM traces, RUM, error investigation |
| tuimm_subagent_code_reviewer | Direct MCPs (read-only): Atlassian, GitLab, SonarQube, Datadog, Figma | Pre-commit code review with cross-system context |
| tuimm_subagent_nuxt | nuxt.com/mcp (mcp-remote) | Nuxt framework documentation, APIs, composables, guides |

## Agent → Subagent Mapping

| Agent | Subagents |
|-------|-----------|
| TUIMM Default | none (concierge — redirects users to the correct agent, direct MCP for ad-hoc queries) |
| TUIMM Dev | Jira, GitLab, SonarQube, Figma, Code Reviewer, Nuxt |
| TUIMM MR | GitLab, SonarQube, Jira, Figma, Code Reviewer, Nuxt |
| Quality Guardian | SonarQube, GitLab, Jira, Datadog |
| Observability | Datadog, GitLab, Jira, SonarQube, ConfigCat, Confluence |
| Knowledge | Confluence, Jira |
| DevEx | Jira, Confluence, Contentful, ConfigCat, GitLab, Nuxt |
| Design System | Figma, GitLab, Jira, Nuxt |
| TUIMM Planner | Jira, GitLab, SonarQube, Figma, Confluence |

## Rules

- Subagents are **API wrappers** — they execute, they don't decide
- Tier 1 agents provide judgment and orchestration
- When a subagent fails, report the error — don't improvise alternatives
- Subagent-specific knowledge (ADF formatting, JQL syntax) stays in the subagent

## Subagent Runtime Limitations

When a Tier 1 agent is spawned as a subagent (e.g., from tuimm_default), it runs with a reduced tool set. See `TOOL_RULES.md § Subagent Runtime Limitations` for the full list.

Key constraint: **subagents cannot spawn other subagents**. This means Tier 1 agents running as subagents from the default CANNOT delegate to Tier 2 subagents. They can only use tools available in the subagent runtime: `read`, `write`, `shell`, `code`, and their own MCP tools.

Design implication: if an agent needs to work both as a main agent AND as a subagent, it needs direct MCP access (`includeMcpJson: true`) rather than relying on Tier 2 delegation.
