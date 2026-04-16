# Idea: Excellence AI Architecture v2

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


## Title

Two-tier agent architecture with centralized MCP gateway for Excellence AI tooling.

## Context

Based on the proven pattern from Javier's personal Kiro setup (`tui_default`, `tui_dev`, `tui_mr`, `tui_datadog`), where user-facing agents are invoked directly for their domain and a general-purpose agent can also delegate to specialists. No routing bottleneck — go straight to the expert when you know what you need.

The key innovation for Excellence: a centralized **TUI MCP Gateway** replaces per-developer API credentials with SSO-authenticated, RBAC-controlled, audited access to all tools. All subagents connect to tools through the gateway.

**Core execution principle: Spec-Driven Development.** Agents plan before they execute. Every non-trivial task produces a plan that the user reviews and approves before the agent writes code. The plan lives in `.plan/` as the contract between human intent and agent execution. See `SPEC_DRIVEN_DEV.md` for the full practice.

## Architecture Diagram

```
╔══════════════════════════════════════════════════════════════════════════════════╗
║                           EXCELLENCE — FULL PICTURE                            ║
╚══════════════════════════════════════════════════════════════════════════════════╝


  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  DISTRIBUTION                                                              │
  │                                                                            │
  │  TUI CLI (@tui/cli)                                                        │
  │  ├── tui ai install agents/prompts/commands/skills/templates/steering       │
  │  ├── tui ai config gateway                                                 │
  │  ├── tui fe create/sync/check/add                                          │
  │  └── tui cli doctor/update                                                 │
  │                                                                            │
  │  Registry (git repo) → agents, prompts, commands, skills, templates, configs│
  └──────────────────────────────────┬──────────────────────────────────────────┘
                                     │ installs on each developer machine
                                     ▼
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  DEVELOPER MACHINE                                                         │
  │                                                                            │
  │  ┌───────────────────────────────────────────────────────────────────────┐  │
  │  │  STEERING (shared context, loaded by all agents)                     │  │
  │  │  Agent Rules · Conventions · Subagents · Prompts · Error Handling    │  │
  │  │  Success Metrics · Implementation Priority                           │  │
  │  └───────────────────────────────────────────────────────────────────────┘  │
  │                                                                            │
  │  ┌───────────────────────────────────────────────────────────────────────┐  │
  │  │  TIER 1 — User-Facing Agents (invoke directly)                      │  │
  │  │                                                                      │  │
  │  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │  │
  │  │  │  Excellence  │ │   Quality   │ │Observability│ │    DevEx    │   │  │
  │  │  │  Default     │ │  Guardian   │ │             │ │             │   │  │
  │  │  │  router +    │ │ quality,    │ │ errors,     │ │ flags,      │   │  │
  │  │  │  master key  │ │ debt, deps  │ │ monitoring  │ │ i18n, sprint│   │  │
  │  │  └──────┬───────┘ └─────────────┘ └─────────────┘ └─────────────┘   │  │
  │  │         │                                                            │  │
  │  │         │         ┌─────────────┐ ┌─────────────┐                   │  │
  │  │         ├────────▶│   Design    │ │  Knowledge  │                   │  │
  │  │         │         │   System    │ │             │                   │  │
  │  │         │         │ figma↔code  │ │ docs, wiki  │                   │  │
  │  │         │         └─────────────┘ └─────────────┘                   │  │
  │  │         │                                                            │  │
  │  │         │         ┌─────────────┐ ┌─────────────┐                   │  │
  │  │         ├────────▶│  Excellence │ │  Excellence │                   │  │
  │  │         │         │  Dev        │ │  MR         │                   │  │
  │  │         │         │ ticket→MR   │ │ review+     │                   │  │
  │  │         │         │             │ │ approve     │                   │  │
  │  │         │         └─────────────┘ └─────────────┘                   │  │
  │  │         │                                                            │  │
  │  │         │         ┌─────────────┐                                   │  │
  │  │         ├────────▶│  Excellence │                                   │  │
  │  │         │         │  Planner    │                                   │  │
  │  │         │         │ design+plan │                                   │  │
  │  │         │         │ read-only   │                                   │  │
  │  │         │         └─────────────┘                                   │  │
  │  │         │                                                            │  │
  │  │         └────────▶ can invoke any specialist                        │  │
  │  └───────────────────────────────────────────────────────────────────────┘  │
  │                          │                                                  │
  │                          │ agents call subagents                            │
  │                          ▼                                                  │
  │  ┌───────────────────────────────────────────────────────────────────────┐  │
  │  │  TIER 2 — Tool Subagents (API wrappers)                             │  │
  │  │                                                                      │  │
  │  │  Jira · GitLab · SonarQube · Datadog · Figma                        │  │
  │  │  Confluence · Contentful · ConfigCat · Weblate                       │  │
  │  └──────────────────────────────┬────────────────────────────────────────┘  │
  │                                 │                                           │
  └─────────────────────────────────┼───────────────────────────────────────────┘
                                    │ all tool calls via single endpoint
                                    ▼
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  MCP GATEWAY (AWS, centralized)                                            │
  │  https://mcp.tui.internal/v1/sse                                           │
  │                                                                            │
  │  SSO/OAuth · RBAC · Audit logging · Rate limiting · Kill switch            │
  │  Credentials in vault (zero keys on laptops)                               │
  │                                                                            │
  │  ┌─────┐ ┌──────┐ ┌─────┐ ┌──────┐ ┌─────┐ ┌─────┐ ┌────┐ ┌────┐ ┌────┐ │
  │  │Jira │ │GitLab│ │Sonar│ │Datadog│ │Figma│ │Confl│ │Ctfl│ │ CC │ │ WL │ │
  │  │ API │ │ API  │ │ API │ │  API  │ │ API │ │ API │ │API │ │API │ │API │ │
  │  └─────┘ └──────┘ └─────┘ └──────┘ └─────┘ └─────┘ └────┘ └────┘ └────┘ │
  │                                                                            │
  │  ┌────────┐ ┌──────┐ ┌─────┐ ┌──────────┐                                 │
  │  │SearXNG │ │Tavily│ │Brave│ │DuckDuckGo│                                 │
  │  │(self)  │ │ API  │ │ API │ │          │                                 │
  │  └────────┘ └──────┘ └─────┘ └──────────┘                                 │
  └─────────────────────────────────────────────────────────────────────────────┘


  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  AUTONOMOUS LAYER — Phase 3 (AWS)                                          │
  │                                                                            │
  │  Excellence Bot Service (Nitro, ECS Fargate)                               │
  │                                                                            │
  │  Webhooks in:                        LLM API:                              │
  │  ┌──────────────┐                    ┌──────────────────────┐              │
  │  │ GitLab       │──Renovate MR ────▶│ Quality Guardian     │              │
  │  │ (merge_req)  │                    │ $dependency-review   │              │
  │  ├──────────────┤                    ├──────────────────────┤              │
  │  │ Datadog      │──alert ──────────▶│ Observability        │              │
  │  │ (monitor)    │                    │ $investigate         │              │
  │  ├──────────────┤                    ├──────────────────────┤              │
  │  │ SonarQube    │──quality gate ───▶│ Quality Guardian     │              │
  │  │ (webhook)    │                    │ $quality-check       │              │
  │  └──────────────┘                    └──────────────────────┘              │
  │                                                                            │
  │  Scheduled (cron):                   ┌──────────────────────┐              │
  │  daily   $morning-scan          ────▶│ Observability        │              │
  │  weekly  $dependency-scan       ────▶│ Quality Guardian     │              │
  │  weekly  $tech-debt-report      ────▶│ Quality Guardian     │              │
  │  weekly  $doc-health            ────▶│ Knowledge            │              │
  │  monthly $i18n-coverage         ────▶│ DevEx                │              │
  │                                      └──────────────────────┘              │
  │                                                                            │
  │  Notifications → Teams (only BLOCK / NEEDS ATTENTION)                      │
  └─────────────────────────────────────────────────────────────────────────────┘


  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  PROMPTS, COMMANDS & TEMPLATES                                             │
  │                                                                            │
  │  Prompts (2, multi-domain, owned by Default):                              │
  │    @incident-report (Observability + Knowledge)                            │
  │    @sprint-report (DevEx + Quality Guardian)                               │
  │                                                                            │
  │  Commands (21, loaded per agent):                                          │
  │  Observability    $morning-scan · $investigate                             │
  │  Quality          $quality-check · $tech-debt-report · $dependency-review  │
  │                   $dependency-scan · $release                               │
  │  DevEx            $flag-cleanup · $i18n-coverage · $content-audit          │
  │  Design System    $design-audit · $component-check                         │
  │  Knowledge        $doc-health · $runbook · $onboarding                     │
  │  Excellence Dev   solve · implement · continue                             │
  │  Excellence MR    review · approve · rebase                                │
  │                                                                            │
  │  Templates (output formats):                                               │
  │    mr-review-summary · mr-description · jira-ticket                        │
  │    code-review-report · incident-report · runbook · sprint-report          │
  └─────────────────────────────────────────────────────────────────────────────┘


  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  ENGINEERING PRACTICES (guild positions, 11 docs)                           │
  │                                                                            │
  │  Testing Philosophy — behavior > coverage, selective TDD, Option C skills   │
  │  Confluence Restructuring — audit → AI-friendly structure → tooling         │
  │  Plan Mode — shared steering + Planner agent for deep design              │
  │  Pipeline Optimization — right checks, right stage, right cost             │
  │  Repo Strategy — consolidation + shared Nuxt module, corporate-first       │
  │  Ticket Standardization — structured tickets for AI agents, Agile-compat   │
  │  Onboarding DX — zero to running in 15 min, README templates              │
  │  Accessibility — a11y-by-default shared library, WCAG 2.1 AA              │
  │  Qodo PR Agent — org-wide config, best_practices.md, rules, rollout       │
  │  Release Strategy — agent-driven releases, 3 levels, replaces sem-release  │
  │  Auto Documentation — AI-generated docs from code, JSDoc, README sync      │
  └─────────────────────────────────────────────────────────────────────────────┘


  ═══════════════════════════════════════════════════════════════════════════════
  ROLLOUT
  ═══════════════════════════════════════════════════════════════════════════════

  Phase 1 (Foundation)     Steering + TUI CLI v1 + MCP Gateway (4 APIs)
                           Excellence Default + Observability
  Phase 2 (Specialists)    Quality Guardian + DevEx + Design System + Knowledge
                           Excellence Dev + Excellence MR + Excellence Planner
                           Remaining subagents + commands
  Phase 3 (Autonomous)     Excellence Bot Service + Teams notifications
                           Webhook-triggered agent sessions via LLM API
```

## Comparison with Javier's Current Setup

| Current (personal) | Excellence (org-wide) |
|---|---|
| `tui_default` (general) | `excellence_default` (general) |
| `tui_datadog` (errors) | `observability_agent` (prod monitoring) |
| `tui_dev` (ticket solver) | `excellence_dev` (ticket-to-MR workflow) |
| `tui_mr` (MR review) | `excellence_mr` (MR review + approval) |
| — | `quality_guardian` (code quality) |
| — | `devex_agent` (dev workflow) |
| — | `design_system` (design governance) |
| — | `knowledge_agent` (documentation) |
| — | `excellence_planner` (cross-domain planning) |

> 4 of 8 Excellence agents are direct evolutions of the personal setup (`tui_default`, `tui_datadog`, `tui_dev`, `tui_mr`). The other 4 cover new domains.

## Design Principles

- **No routing bottleneck** — go directly to the specialist when you know what you need
- **Default as fallback** — Excellence Default can delegate to any specialist for ad-hoc queries
- **Subagents are shared infra** — any Tier 1 agent can use tool subagents for its domain
- **Agents add judgment** — Tier 1 agents combine tools with intelligence and domain knowledge
- **Subagents isolate complexity** — tool-specific knowledge (ADF formatting, JQL, query syntax) stays in the subagent, not in Tier 1 prompts
- **Commands for repeatable workflows** — single-agent actions loaded on-demand via `fs_read`, domain enforcement is structural
- **Prompts for cross-domain orchestration** — multi-agent workflows owned by Default, Agent Guard enforced
- **Centralized security** — MCP Gateway handles auth, RBAC, and audit for all tools
- **Zero credentials on laptops** — SSO through the gateway, no API keys in agent configs

## Agent → Subagent Mapping

| Agent | Subagents | Purpose |
|---|---|---|
| Excellence Default | all 7 agents + all subagents | General routing, ad-hoc |
| Quality Guardian | sonar, gitlab, jira, datadog | Code quality, tech debt, coverage, quality-error correlation |
| Observability Agent | datadog, gitlab, jira, sonar, confluence, configcat | Error investigation, monitoring, incidents, runbooks, flag correlation |
| DevEx Agent | gitlab, jira, configcat, weblate, contentful, confluence | Dev workflow, flags, i18n, content, sprint reports |
| Design System Agent | figma, gitlab, sonar, weblate | Design-to-code, component governance, design-to-i18n |
| Knowledge Agent | confluence, jira, gitlab, contentful | Documentation, runbooks, onboarding, CMS docs |
| Excellence Dev | jira, gitlab, sonar | Ticket-to-MR workflow, implementation |
| Excellence MR | gitlab, sonar, jira | MR review, feedback, approval |
| Excellence Planner | jira, gitlab, sonar, confluence, figma | Cross-domain analysis, technical design, task decomposition, Jira ticket creation |

## Domain Boundaries

Areas where multiple agents touch the same domain. Ownership is explicit to avoid confusion.

| Domain | Owner | Contributors |
|---|---|---|
| MR quality checks | Quality Guardian | Excellence MR (review feedback), DevEx (workflow/process) |
| MR review & approval | Excellence MR | Quality Guardian (automated quality gates) |
| Ticket implementation | Excellence Dev | DevEx (workflow context), Quality Guardian (pre-commit quality) |
| Error knowledge base | Observability Agent | Knowledge Agent (org-wide docs) |
| Onboarding guides | Knowledge Agent | DevEx (team-specific data) |
| Release notes | Knowledge Agent | DevEx (sprint data extraction) |
| Runbooks | Knowledge Agent | Observability Agent (creates from incidents) |
| Sprint retrospectives | DevEx (data extraction) | Knowledge Agent (Confluence page creation) |
| Translation keys | DevEx | Design System (extracts text from Figma) |

## Distribution: TUI CLI

The AI architecture needs a delivery mechanism. The **TUI CLI** (`@tui/cli`) is a domain-oriented internal CLI that distributes agents, prompts, skills, and MCP Gateway config to all developers.

3 domains: `tui ai` (AI tooling), `tui fe` (frontend project lifecycle), `tui cli` (self-management).

Key commands:
- `tui ai install agents` — deploys all Excellence agents
- `tui ai install prompts` — deploys all reusable prompts
- `tui ai config gateway` — configures MCP Gateway connection (SSO)
- `tui fe create` — scaffolds compliant projects from templates
- `tui fe sync configs` — syncs shared configs (ESLint, Stylelint, etc.)

Without the CLI, onboarding a developer to the AI architecture is manual. With it, one command.

See: `ideas/tooling/TUI_CLI.md`

## Shared Steering

Excellence agents share a set of **steering files** — conventions, rules, and references loaded by every Tier 1 agent. Equivalent to Javier's personal `~/.kiro/steering/` files, scaled to org-wide use.

### Steering Files

| File | Purpose |
|------|---------|
| `STEERING_AGENT_RULES.md` | Shared rules: error handling, delegation, git, tool usage, Agent Guard enforcement |
| `STEERING_CONVENTIONS.md` | Tech stack, naming, coding conventions, Agent Guard (2 multi-domain prompts), commands, templates, skill refs |
| `STEERING_SUBAGENTS.md` | Tier 2 subagent reference with MCP skill links |
| `STEERING_PROMPTS.md` | Prompt & command reference: 2 multi-domain prompts + 21 commands by agent |
| `STEERING_ERROR_HANDLING.md` | Failure patterns, partial results, retry policy, MCP Gateway errors |
| `STEERING_SUCCESS_METRICS.md` | KPIs per agent with baselines, targets, and data sources |
| `STEERING_IMPLEMENTATION_PRIORITY.md` | Value/effort matrix, dependency graph, rollout timeline |
| `STEERING_PLAN_MODE.md` | Shared planning behavior: levels 0-3, approval flow, output format, escalation to Planner |

### Agent Guard & Commands

Two types of executable workflows:

- **Commands** (21) — single-agent actions loaded on-demand via `fs_read`. Domain enforcement is structural: only the owning agent lists the command in its system prompt. No runtime guard needed.
- **Prompts** (2) — multi-domain orchestrations owned by Excellence Default. Agent Guard enforced: `Required: excellence_default`. Only @incident-report and @sprint-report.

Full conventions: `STEERING_CONVENTIONS.md`

## Autonomous Layer (Phase 3)

The autonomous layer enables agents to act without human invocation. External events trigger agent sessions programmatically via direct LLM API calls.

See: `ideas/ai/AUTONOMOUS_BOT_SERVICE.md` for full design.

### Summary

The **Excellence Bot Service** is a lightweight Nitro server deployed on AWS (ECS Fargate) that receives external events (webhooks, alerts, schedules) and invokes the correct Excellence agent. The bot has no intelligence — it's a dispatcher. All reasoning lives in the agents.

**Production approach:** The bot calls the LLM API directly (Vercel AI SDK + Anthropic/OpenAI) with the agent's system prompt and MCP Gateway tools. No dependency on kiro-cli in server.

**Tech stack:** Nitro + Vercel AI SDK + MCP Gateway client, deployed on ECS Fargate.

**Event sources and routing:**

| Source | Event | Agent | Command |
|---|---|---|---|
| GitLab | Renovate MR created | Quality Guardian | $dependency-review |
| Datadog | Monitor alert | Observability | $investigate |
| SonarQube | Quality gate failure | Quality Guardian | $quality-check |
| Cron (weekly) | Scheduled | Knowledge Agent | $doc-health |
| Cron (weekly) | Scheduled | Quality Guardian | $dependency-scan |
| Cron (daily) | Scheduled | Observability | $morning-scan |

**Notifications:** Teams (only when human attention is needed — BLOCK, NEEDS ATTENTION, critical findings).

## Engineering Practices

Guild positions on engineering debates. Framework-agnostic where possible. These inform agent behavior and shared skills.

| Practice | Summary | Doc |
|---|---|---|
| Testing Philosophy | Behavior over coverage, selective TDD by file type, Option C shared testing skills across Dev/QG/MR agents, explicit "what not to test" list | `ideas/practices/TESTING_PHILOSOPHY.md` |
| Confluence Restructuring | 3-phase overhaul: audit → AI-friendly structure → tooling. Page templates per type, label taxonomy, lifecycle management, migrate-on-touch strategy | `ideas/practices/CONFLUENCE_RESTRUCTURING.md` |
| Plan Mode | Structured `@plan`/`@design` prompts that output technical design + task breakdown to ephemeral `.plan/` folder | `ideas/practices/PLAN_MODE.md` |
| Pipeline Optimization | Environment-aware CI/CD: right checks at the right stage. Dev deploys fast, heavy checks move to staging/production | `ideas/practices/PIPELINE_OPTIMIZATION.md` |
| Repo Strategy | Repo consolidation + shared Nuxt module for components, configs, integrations. Corporate-first, migrate on touch | `ideas/practices/REPO_STRATEGY.md` |
| Ticket Standardization | Structured Jira tickets for AI agent consumption. Opt-in templates, agent backfill, Agile-compatible | `ideas/practices/TICKET_STANDARDIZATION.md` |
| Onboarding DX | Zero to running app in 15 minutes. Standardized README, `.env.example` contract, `tui fe init` | `ideas/practices/ONBOARDING_DX.md` |
| Accessibility | A11y-by-default shared library (WCAG 2.1 AA). Wrapper components, directives, composables for incremental adoption | `ideas/practices/ACCESSIBILITY.md` |
| Qodo PR Agent | Org-wide Qodo optimization: config (.pr_agent.toml), hierarchical best_practices.md, repo overrides, future Rules System | `ideas/practices/QODO_PR_AGENT.md` |
| Release Strategy | Agent-driven releases replacing semantic-release. 3 progressive levels: manual $release → semi-autonomous → full autonomous | `ideas/practices/RELEASE_STRATEGY.md` |
| Auto Documentation | AI-generated docs from real code. Global and per-team documentation that agents consume as skills/steering. Living docs | `ideas/practices/AUTO_DOCUMENTATION.md` |

## Implementation Phases

### Phase 1: Foundation
- Steering files (7 operational files, loaded by all agents)
- TUI CLI v1 (`tui ai` domain — install agents, prompts, skills, steering)
- MCP Gateway core (SSO + proxy to Jira, GitLab, SonarQube, Datadog)
- Jira, GitLab, SonarQube, Datadog subagents connected to gateway
- Excellence Default agent (router + master key)
- Observability Agent (port from tui_datadog)

### Phase 2: Specialists
- Quality Guardian, DevEx, Design System, Knowledge agents
- Excellence Dev (port from tui_dev), Excellence MR (port from tui_mr)
- Add Figma, Confluence, Contentful, ConfigCat, Weblate to gateway
- Create remaining subagents for new tools
- Create remaining commands per agent (19 Phase 2 skills) and 2 multi-domain prompts

### Phase 3: Autonomous
- Excellence Bot Service (Nitro + Vercel AI SDK, ECS Fargate)
- Direct LLM API calls with agent system prompts + MCP Gateway tools
- GitLab, Datadog, SonarQube webhook listeners
- Scheduled tasks (weekly dependency scan, doc health, daily morning scan)
- Teams notifications for events requiring human attention
- See: `ideas/ai/AUTONOMOUS_BOT_SERVICE.md`