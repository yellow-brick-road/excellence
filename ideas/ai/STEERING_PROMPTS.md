# Steering: Prompts, Commands & Templates

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


Reference for all agent workflows and output formats. Loaded as steering by every Tier 1 agent.

## Model

Excellence uses seven types of agent artifacts:

- **Prompts** — generic, multi-domain orchestrations owned by Excellence Default. Live in `~/.kiro/prompts/`, installable via TUI CLI. Agent Guard enforced. Broad workflows that coordinate multiple specialists.
- **Commands** — specific, targeted actions owned by a single agent. Live in `~/.kiro/commands/`, referenced by file path in the agent's system prompt. Loaded on-demand via `fs_read` when triggered (not preloaded as resources). User triggers with `$name` prefix. Domain enforcement is structural (only the owning agent lists the command in its prompt).
- **Templates** — output format templates. Live in `~/.kiro/templates/`. Define HOW something should look (MR description, Jira ticket, code review report, runbook). Not executable — consumed by agents and commands to produce structured output.
- **Skills** — knowledge reference material. Live in `~/.kiro/skills/`. Declared in agent JSON as resources. Informational, not executable.
- **Steering** — shared behavioral rules. Live in `~/.kiro/steering/`. Auto-loaded by all agents at startup.
- **Scripts** — shell automation. Live in `~/.kiro/scripts/`. Invoked by agents via `execute_bash`. For git operations, API calls, data pipelines. Not agent-specific.
- **Tools** — standalone Python tools with own tests, skills, and CLI. Live in `~/.kiro/tools/{name}/`. Each has a manifest in `REGISTRY.md`. Can be invoked by agents or used independently.

### Key distinction

| | Prompts | Commands | Templates | Skills | Steering | Scripts | Tools |
|---|---------|----------|-----------|--------|----------|---------|-------|
| Scope | Multi-domain | Single-domain | Format only | Knowledge | Behavior | Automation | Standalone |
| Owner | Default | Specific agent | Shared | Shared | Shared | Shared | Shared |
| Location | `prompts/` | `commands/` | `templates/` | `skills/` | `steering/` | `scripts/` | `tools/` |
| Loading | Preloaded | On-demand | On-demand | Declared | Auto-loaded | On-demand | On-demand |
| Trigger | @name | $name | N/A | N/A | N/A | `execute_bash` | `execute_bash` |
| Example | @incident-report | $morning-scan | mr-review.md | mcp_atlassian | AGENT_RULES.md | gitlab-list-mrs.sh | autobuild |

## Prompts (2)

Multi-domain workflows that coordinate two or more specialist agents. Owned exclusively by Excellence Default.

| Prompt | Orchestrates | Trigger | Phase |
|--------|-------------|---------|-------|
| @incident-report | Observability + Knowledge | "incident report", "post-mortem" | 2 |
| @sprint-report | DevEx + Quality Guardian | "sprint report", "sprint health" | 2 |

Detailed specs: `PROMPT_INCIDENT_REPORT.md`, `PROMPT_SPRINT_REPORT.md`

## Commands by Agent (21)

Direct invocation: `$command-name`. Fuzzy triggers also listed — agent asks for confirmation if input is similar but not exact.

### Observability (2)

| Command | Trigger | Description |
|---------|---------|-------------|
| `obs_morning_scan` | "morning scan", "check prod" | Structured production error scan, time-aware |
| `obs_dd-investigate` | "investigate [error]", "root cause" | Deep root cause analysis |

### Quality Guardian (5)

| Command | Trigger | Description |
|---------|---------|-------------|
| `qg_quality_check` | "quality check", "quality scan" | Full quality scan across projects |
| `qg_tech_debt_report` | "tech debt", "debt report" | Debt quantification and prioritization |
| `qg_dependency_review` | "dependency review", "renovate" | Reactive Renovate MR triage |
| `qg_dependency_scan` | "scan dependencies", "check updates" | Proactive dependency analysis |
| `qg_release` | "$release", "$release [package]" | Version bump, changelog, publish workflow |

### DevEx (3)

| Command | Trigger | Description |
|---------|---------|-------------|
| `devex_flag_cleanup` | "flag cleanup", "stale flags" | Stale flag detection and cleanup plan |
| `devex_i18n_coverage` | "i18n coverage", "translations" | Translation coverage report |
| `devex_content_audit` | "content audit", "contentful check" | Content model health check |

### Design System (2)

| Command | Trigger | Description |
|---------|---------|-------------|
| `ds_design_audit` | "design audit", "DS compliance" | Full design system compliance check |
| `ds_component_check` | "component check [name]" | Compare Figma spec vs code |

### Knowledge (3)

| Command | Trigger | Description |
|---------|---------|-------------|
| `kn_doc_health` | "doc health", "docs audit" | Documentation health audit |
| `kn_runbook` | "runbook [topic]" | Generate runbook from existing knowledge |
| `kn_onboarding` | "onboarding [team]" | Generate onboarding guide |

### Excellence Dev (3)

| Command | Trigger | Description |
|---------|---------|-------------|
| `edev_solve` | "solve [TICKET-ID]" | Full ticket-to-MR workflow |
| `edev_implement` | "implement [description]" | Ad-hoc implementation without ticket |
| `edev_continue` | "continue", "resume" | Resume interrupted workflow |

### Excellence MR (3)

| Command | Trigger | Description |
|---------|---------|-------------|
| `emr_review` | "review [MR-ID]" | Full MR review with structured feedback |
| `emr_approve` | "approve [MR-ID]" | Quick approve with summary |
| `emr_rebase` | "rebase [MR-ID]" | Rebase MR on target branch |

## Templates

Output format templates consumed by agents and commands. Not executable — they define the structure of generated output.

| Template | Used by | Description |
|----------|---------|-------------|
| `mr-review-summary` | Excellence MR | MR review summary format (verdict, issues, recommendation) |
| `mr-description` | Excellence Dev | MR description format (what, why, how, testing) |
| `jira-ticket` | Excellence Dev, DevEx | Jira ticket format (background, AC, technical notes) |
| `code-review-report` | Excellence MR, Quality Guardian | Pre-commit review report (severity, issues, verdict) |
| `incident-report` | Observability, Knowledge | Post-mortem format (timeline, impact, root cause, actions) |
| `runbook` | Knowledge | Runbook format (trigger, steps, rollback, contacts) |
| `sprint-report` | DevEx, Quality Guardian | Sprint health report format (velocity, quality, blockers) |

Templates are installed via `tui ai install templates` and live in `~/.kiro/templates/`.

## Detailed Specs

- Commands: `COMMAND_*.md`
- Prompts: `PROMPT_*.md`
- Dependency governance (knowledge skill): `SKILL_DEPENDENCY_GOVERNANCE.md`
