# TUIMM — AI Agent System for TUI Musement Frontend

TUIMM is a two-tier AI agent architecture for the Frontend Engineering Guild. It connects Kiro CLI to the tools we use daily — Jira, GitLab, SonarQube, Datadog, Figma, Contentful, ConfigCat, Confluence — through specialized agents that know our conventions.

## Installation

```
tuimm/
├── agents/    → copy to ~/.kiro/agents/
└── tuimm/     → copy to ~/.kiro/tuimm/
```

```bash
cp agents/*.json ~/.kiro/agents/
cp -r tuimm/ ~/.kiro/tuimm/
```

Then configure credentials. See [SETUP.md](tuimm/SETUP.md).

## Prerequisites

- Kiro CLI installed and working
- Node.js 18+ with npx
- Python 3.10+ (for tools: logd, autobuild, bg)
- Git with SSH access to source.tui (`git@ssh.source.tui:`)
- VPN for SonarQube
- Linux, WSL, or macOS

## How it works

```
┌─────────────────────────────────────────────────────────────┐
│  User                                                       │
│  kiro-cli --agent tuimm_dev                                 │
└──────────────┬──────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────┐
│  Tier 1 — Specialist Agents (9)                             │
│                                                             │
│  tuimm_default ─── concierge, routes to the right agent     │
│  tuimm_dev ─────── ticket → branch → code → MR             │
│  tuimm_mr ──────── review, comments, approve, rebase        │
│  tuimm_quality_guardian ── SonarQube, debt, deps, releases  │
│  tuimm_observability ──── Datadog scans, error investigation│
│  tuimm_devex ───── flags, i18n, content models, sprint      │
│  tuimm_design_system ──── Figma ↔ code alignment            │
│  tuimm_knowledge ── Confluence, docs, runbooks, onboarding  │
│  tuimm_planner ──── analysis, design docs, task breakdown   │
│                                                             │
│  Each agent loads: steering + skills + its own commands      │
│  Each agent delegates to Tier 2 subagents via MCP            │
└──────────────┬──────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────┐
│  Tier 2 — Tool Subagents (10)                               │
│                                                             │
│  tuimm_subagent_jira ──────── Atlassian Cloud (OAuth)       │
│  tuimm_subagent_confluence ── Atlassian Cloud (OAuth)       │
│  tuimm_subagent_gitlab ────── source.tui API                │
│  tuimm_subagent_sonar ─────── SonarQube (VPN)              │
│  tuimm_subagent_datadog ───── Datadog EU                    │
│  tuimm_subagent_figma ─────── Figma API                     │
│  tuimm_subagent_contentful ── Contentful CMA                │
│  tuimm_subagent_configcat ─── ConfigCat Management API      │
│  tuimm_subagent_code_reviewer  read-only cross-system review│
│  tuimm_subagent_nuxt ──────── nuxt.com/mcp (public)        │
│                                                             │
│  Subagents are API wrappers — they execute, they don't      │
│  decide. Tier 1 agents provide judgment and orchestration.   │
└─────────────────────────────────────────────────────────────┘
```

Tier 1 agents are invoked directly by users (`kiro-cli --agent tuimm_dev`). They read requirements, plan, and delegate API calls to Tier 2 subagents. Subagents connect to external services via MCP (Model Context Protocol) — each one wraps a single API.

Weblate is the exception: no MCP server available, so it's handled via 4 commands + 1 skill that clone the repo, parse XLIFF files, and create MRs through the GitLab subagent.

## Package contents

### agents/ (19 JSON files → ~/.kiro/agents/)

Agent configuration files. Each defines: name, prompt (behavioral instructions), tools, MCP servers, and resources to load.

The `"name"` field determines how you invoke it: `kiro-cli --agent tuimm_dev`.

Resources use relative paths (`../tuimm/steering/*.md`) that resolve correctly when agents live at `~/.kiro/agents/` and the package at `~/.kiro/tuimm/`.

### tuimm/steering/ (11 markdown files)

Shared behavioral rules loaded by ALL agents at startup via `file://` glob. Non-negotiable — agents must follow these.

| File | What it governs |
|------|-----------------|
| 1_AGENT_RULES.md | Hub — references all other steering files. Read first. |
| OPERATING_MODE.md | How agents process every request: context → understand → plan → execute → verify |
| GIT.md | Branch naming, workspace conventions, commit rules, clone paths |
| COMMUNICATION.md | Tone, language, reporting style |
| SUBAGENTS.md | Which subagents exist, who delegates to whom, runtime limitations |
| TOOL_RULES.md | When to use glob vs shell, subagent delegation rules |
| ERROR_HANDLING.md | Never auto-retry, always inform, partial results OK |
| CONVENTIONS.md | File naming, code style, BEM, TypeScript, Vue, testing |
| TECH_STACK.md | Current versions: Nuxt 4.3, Vue 3.5, Node 22/24, tooling |
| AI_USAGE_TRACKING.md | Jira AI usage fields — what to set after agent work |
| ARTIFACTS.md | Registry of all commands, skills, templates, tools with ownership |

### tuimm/commands/ (35 markdown files)

Executable instructions. Each command defines inputs, a step-by-step process, and which template to use for output. Agents load their own commands as skills via `skill://` globs.

Commands are prefixed by domain: `dev_`, `mr_`, `obs_`, `qg_`, `devex_`, `ds_`, `kn_`, `planner_`, `jira_`, `weblate_`, plus `get-commands` (meta).

Users trigger them with `$command-name` or natural language ("solve DIS-1234", "review 242", "scan").

### tuimm/skills/ (14 directories, each with SKILL.md)

Knowledge documents that agents consult before acting. Not executable — they're reference material.

| Skill | Used by | What it contains |
|-------|---------|------------------|
| commit-conventions | GitLab subagent, Code Reviewer | Commit format, types, scope rules |
| gitlab-conventions | GitLab subagent, Code Reviewer | MR templates, thread rules, API limits |
| jira-adf | Jira subagent, Confluence subagent | Atlassian Document Format for descriptions/comments |
| jira-context-gathering | Jira commands, Dev commands | Full ticket context checklist — what to fetch |
| weblate-conventions | Weblate commands | Repo URL, module discovery, XLIFF format |
| code-review-checklist | Code Reviewer | Pre-commit checklist ordered by severity |
| file-modifier | Dev, MR, any write agent | Lint/format order after file changes |
| workspace-mcp | Dev, MR, Default | nuxt-mcp-dev workspace config pattern |
| mcp-tools-reference | Code Reviewer, any agent | Read vs write tool classification per MCP server |
| known-error-patterns | Observability | Recurring production errors with Datadog queries |
| security-preflight | Quality Guardian, MR | How to extract preflight-sast findings from pipelines |
| autobuild-reference | Planner | Task engine CLI, task file format, config |
| bg-reference | Tools that run in background | Background execution library API |
| logd-reference | Observability, autobuild | Log daemon and client library API |

### tuimm/templates/ (35 markdown files)

Output format definitions. Commands reference them as "present results using the X template." They ensure consistent, structured output across agents.

One template per command output, plus `template-blueprint.md` as a reference for creating new ones.

### tuimm/tools/ (10 files across subdirectories)

Shell scripts and Python utilities invoked by commands at runtime.

| Tool | Used by | What it does |
|------|---------|--------------|
| gitlab-list-mrs.sh | $mr_list | Queries GitLab for MRs across repos (reviewer, assignee, author, bots) |
| tracked-repos.txt | gitlab-list-mrs.sh | List of GitLab project paths to track for bot MRs |
| workspace-cleanup-check.py | Session start (background) | Scans ~/.kiro/temp/ for stale workspaces, checks GitLab for merged MRs |
| autobuild/engine.py | $planner_decompose | Task engine — executes markdown task files through kiro-cli agents |
| autobuild/kiro.py | engine.py | ACP client wrapper for kiro-cli |
| bg/bg.py | Any script needing background mode | Adds --bg/--status/--stop/--tail to Python scripts |
| logd/logd.py | Observability, autobuild | UDP log daemon with SQLite storage |
| logd/loglib.py | Any Python tool | Fire-and-forget log client |
| logd/extensions/obs_scan.py | $obs_dd-scan | Load/save scan results for cross-scan comparison |
| guidelines-generator/guidelines-generator.py | Standalone utility | Extracts coding conventions from committed files via AI |

### tuimm/prompts/ (empty)

Reserved for multi-domain workflow prompts. Not yet populated.

## How the pieces connect

A concrete example — user runs `$dev_solve DIS-1234`:

1. **Agent** (`tuimm_dev.json`) receives the command
2. **Steering** (`GIT.md`, `CONVENTIONS.md`) tells it how to name branches and write code
3. **Command** (`dev_solve.md`) defines the step-by-step process
4. **Skill** (`jira-context-gathering`) tells it what to fetch from the ticket
5. **Subagent** (`tuimm_subagent_jira`) calls the Jira API to get ticket details
6. **Subagent** (`tuimm_subagent_gitlab`) creates the branch and later the MR
7. **Skill** (`commit-conventions`) formats the commit message
8. **Subagent** (`tuimm_subagent_code_reviewer`) reviews code before commit
9. **Template** (`dev-solve.md`) formats the final output
10. **Steering** (`AI_USAGE_TRACKING.md`) reminds it to set AI usage fields on the ticket

## Shared commands

Jira and Weblate commands are available from multiple agents — you don't need to swap to a specific one.

| Commands | Available from |
|----------|---------------|
| $jira_create-ticket, $jira_edit-ticket, $jira_comment-ticket | All Tier 1 agents except Default |
| $weblate_add-key, $weblate_validate, $weblate_coverage, $weblate_translate-missing | Dev, MR, DevEx, Design System |

The Default agent doesn't execute commands — it tells you which agent to use and how to get there.

## Quick reference

| I want to... | Agent | Command |
|--------------|-------|---------|
| Solve a Jira ticket | tuimm_dev | $dev_solve DIS-1234 |
| Review an MR | tuimm_mr | $mr_review 242 |
| Check my open MRs | tuimm_mr | $mr_list |
| Scan production errors | tuimm_observability | $obs_dd-scan |
| Check code quality | tuimm_quality_guardian | $qg_quality-check |
| Find stale feature flags | tuimm_devex | $devex_flag-cleanup |
| Compare Figma vs code | tuimm_design_system | $ds_component-check |
| Audit Confluence docs | tuimm_knowledge | $kn_doc-health |
| Plan a large feature | tuimm_planner | $planner_design |
| Create a Jira ticket | any agent (except default) | $jira_create-ticket |
| Add a translation key | tuimm_dev | $weblate_add-key |
| See all commands | any agent | $get-commands |

## Customization

- **tracked-repos.txt** — edit to match your team's repos (used by $mr_list for bot MR tracking)
- **known-error-patterns** — add your service's recurring errors (used by $obs_dd-scan)
- **nuxt-mcp-dev** — optional per-project setup for deep Nuxt context (see SETUP.md)

## Credentials

Each developer provides their own API tokens. No shared credentials, no centralized gateway. See [SETUP.md](tuimm/SETUP.md) for the full list with URLs.

| Service | Auth method |
|---------|-------------|
| GitLab | Personal access token (env var) |
| Datadog | API + App key (env vars) |
| SonarQube | API token (env var, VPN required) |
| Jira / Confluence | OAuth via browser (automatic) |
| Figma | Personal access token (env var) |
| Contentful | CMA token (env var) |
| ConfigCat | API user + password (env vars) |
| Nuxt docs | Public endpoint (no setup) |
