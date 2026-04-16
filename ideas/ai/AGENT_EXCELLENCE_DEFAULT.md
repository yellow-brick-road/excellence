# Idea: Excellence Default Agent

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


## Title

General-purpose Excellence agent — ad-hoc queries, routing, and cross-domain tasks.

## Context

Mirrors the `tui_default` pattern. The agent you talk to when you don't know which specialist to use, or when the task spans multiple domains. Can invoke all 7 specialist agents. Also handles general Excellence work: planning, brainstorming, documentation, standards drafting.

## Role

- Entry point for ad-hoc Excellence queries
- Routes to specialist agents when the task is clear
- Handles cross-domain tasks that don't fit one specialist
- General planning, brainstorming, and documentation work
- Standards drafting and review

## Can Invoke

- Quality Guardian
- Observability Agent
- DevEx Agent
- Design System Agent
- Knowledge Agent
- Excellence Dev
- Excellence MR
- All 9 Tier 2 tool subagents (Jira, GitLab, SonarQube, Datadog, Figma, Confluence, Contentful, ConfigCat, Weblate)

## What It Could Do

### Routing & Delegation
- Detect intent and route to the right specialist ("check prod errors" → Observability)
- Handle multi-domain tasks by orchestrating multiple specialists
- Aggregate results from multiple agents into unified reports

### Standards & Governance
- Draft coding standards, conventions, and guidelines
- Review and iterate on proposed standards
- Compare standards across teams (detect divergence)
- Generate RFC documents for new standards

### Planning & Strategy
- Help plan Excellence initiatives
- Draft proposals for new tools, processes, or standards
- Prepare presentations and reports for leadership
- Track Excellence OKRs and KPIs

### Team Support
- Answer questions about Excellence scope and processes
- Onboard new team members to Excellence workflows
- Generate training materials
- Facilitate knowledge sharing between teams

### Agent Guard: Master Key

Excellence Default bypasses all Agent Guards — it can execute any prompt in the system. When running a single-domain prompt, it SHOULD delegate to the specialist to preserve domain context.

### Multi-Domain Prompts (owned by Default)

Prompts that coordinate two or more specialists belong exclusively to Default. No other agent can run them. These are the only workflows that use Agent Guard.

- @sprint-report → Default orchestrates DevEx Agent + Quality Guardian
- @incident-report → Default orchestrates Observability Agent + Knowledge Agent

### Other Prompts
- General ad-hoc queries (no specific prompt)
- Ad-hoc queries and general assistance
- Any future cross-domain prompts

Note: Default has no commands of its own. Single-domain actions are commands owned by their respective specialist agents.
