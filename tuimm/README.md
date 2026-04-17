# TUIMM — Your AI Engineering Team

What if you could type "solve DIS-1234" and an AI agent reads the Jira ticket, understands the codebase, writes the code, runs the tests, creates the MR, and updates the ticket — all in one conversation?

That's what TUIMM does.

TUIMM is a set of AI agents built for TUI Musement's frontend teams. They plug into Kiro CLI and connect to the tools you already use: Jira, GitLab, SonarQube, Datadog, Figma, Contentful, ConfigCat, Confluence. Nine specialist agents, each one focused on a specific part of the workflow. You talk to the expert you need, and it handles the rest.

No dashboards to check. No context switching. No copy-pasting between tools.

---

## What can it do?

Here are some real examples:

```
You: "solve DIS-1234"
→ Agent reads the ticket, plans the implementation, writes code, creates the MR, moves the ticket to In Review.

You: "review MR 242"
→ Agent fetches the diff, checks SonarQube, reviews against the team's checklist, posts comments on GitLab.

You: "scan production errors"
→ Agent queries Datadog, groups errors by pattern, flags new issues, compares with known patterns.

You: "find stale feature flags"
→ Agent audits ConfigCat, cross-references with the codebase, produces a cleanup plan.

You: "design the new search architecture"
→ Agent analyzes the codebase, produces a technical design doc, breaks it into Jira tickets.
```

Every agent knows our conventions — branch naming, commit format, BEM, Vue patterns, testing standards. It's not a generic AI assistant. It's one that knows how we work.

---

## The agents

Two tiers. You talk to Tier 1. Tier 1 talks to Tier 2 behind the scenes.

```
                            ┌─────────────────┐
                            │    Developer     │
                            │  kiro-cli        │
                            └────────┬────────┘
                                     │
                 ┌───────────────────┼───────────────────┐
                 │                   │                    │
          ┌──────▼──────┐    ┌──────▼──────┐     ┌──────▼──────┐
          │     Dev      │    │     MR      │     │  Planner    │
          │  solve ticket│    │  review MR  │     │  design doc │
          └──────┬──────┘    └──────┬──────┘     └──────┬──────┘
                 │                  │                    │
    ┌────────────┼──────────────────┼────────────────────┘
    │            │                  │
    │   ┌────────┼──────────┬──────┼──────────┬──────────────┐
    │   │        │          │      │          │              │
    ▼   ▼        ▼          ▼      ▼          ▼              ▼
  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
  │  Jira  │ │ GitLab │ │ Sonar  │ │Datadog │ │ Figma  │ │  ...   │
  │  MCP   │ │  MCP   │ │  MCP   │ │  MCP   │ │  MCP   │ │        │
  └────┬───┘ └────┬───┘ └────┬───┘ └────┬───┘ └────┬───┘ └────────┘
       │          │          │          │          │
       ▼          ▼          ▼          ▼          ▼
    Jira API   source.tui  SonarQube  Datadog EU  Figma API


  ┌──────────────────────────────────────────────────────────────┐
  │  Also in Tier 1:                                             │
  │                                                              │
  │  Default ─────── concierge, routes you to the right agent    │
  │  Quality Guardian ── SonarQube, tech debt, deps, releases    │
  │  Observability ───── Datadog scans, error investigation      │
  │  DevEx ──────────── feature flags, i18n, content models      │
  │  Design System ──── Figma ↔ code alignment                   │
  │  Knowledge ──────── Confluence, docs, runbooks               │
  └──────────────────────────────────────────────────────────────┘
```

**Tier 1 — The specialists** (you invoke these directly)

| Agent | What it does |
|-------|-------------|
| **Default** | Don't know where to start? Ask here. It knows what every agent can do and points you to the right one |
| **Dev** | Ticket-to-MR in one conversation. Reads Jira, plans, codes, tests, commits, creates MR |
| **MR** | Reviews merge requests. Structured feedback with severity levels. Can approve, comment, rebase |
| **Quality Guardian** | SonarQube analysis, tech debt tracking, dependency audits, release management |
| **Observability** | Datadog log analysis, production error investigation, incident patterns |
| **DevEx** | Feature flags, translations (Weblate), content models, sprint workflow |
| **Design System** | Figma-to-code alignment, component governance, design token audits |
| **Knowledge** | Confluence health checks, runbook generation, onboarding guides |
| **Planner** | Technical design documents, task decomposition, cross-domain analysis |

**Tier 2 — The tool connectors** (agents call these, you don't)

Jira · Confluence · GitLab · SonarQube · Datadog · Figma · Contentful · ConfigCat · Nuxt docs · Code Reviewer

Each one wraps a single API via MCP (Model Context Protocol). They execute — they don't decide. The intelligence lives in Tier 1.

---

## Quick start

### 1. Copy the files

```bash
# Agent configs go to ~/.kiro/agents/
cp agents/*.json ~/.kiro/agents/

# Package contents go to ~/.kiro/tuimm/
cp -r tuimm/* ~/.kiro/tuimm/
```

That's it for the files. The agents reference `~/.kiro/tuimm/` for everything — steering rules, commands, skills, templates, tools.

### 2. Set up your credentials

Each developer uses their own API tokens. No shared accounts, no centralized server.

Open **[SETUP.md](tuimm/SETUP.md)** — it has the full list with URLs where to get each token. The short version:

| Service | What you need |
|---------|--------------|
| GitLab | Personal access token |
| Datadog | API key + App key |
| SonarQube | API token (VPN required) |
| Figma | Personal access token |
| Contentful | CMA token |
| ConfigCat | API user + password |
| Jira / Confluence | Nothing — OAuth via browser, automatic |
| Nuxt docs | Nothing — public endpoint |

Add the env vars to your `~/.bashrc` or `~/.zshrc`. They need to be exported before starting Kiro CLI.

### 3. Verify

```bash
kiro-cli --agent tuimm_default
```

Type `$get-commands`. If you see 36 commands across 9 agents, you're good.

---

## How to use it

Start with the agent that matches what you need:

| I want to... | Agent | Command |
|--------------|-------|---------|
| Solve a Jira ticket | `tuimm_dev` | `$dev_solve DIS-1234` |
| Continue previous work | `tuimm_dev` | `$dev_continue` |
| Review an MR | `tuimm_mr` | `$mr_review 242` |
| Check my open MRs | `tuimm_mr` | `$mr_list` |
| Scan production errors | `tuimm_observability` | `$obs_dd-scan` |
| Investigate a specific error | `tuimm_observability` | `$obs_dd-investigate` |
| Check code quality | `tuimm_quality_guardian` | `$qg_quality-check` |
| Audit dependencies | `tuimm_quality_guardian` | `$qg_dependency-scan` |
| Find stale feature flags | `tuimm_devex` | `$devex_flag-cleanup` |
| Check translation coverage | `tuimm_devex` | `$weblate_coverage` |
| Compare Figma vs code | `tuimm_design_system` | `$ds_component-check` |
| Audit Confluence docs | `tuimm_knowledge` | `$kn_doc-health` |
| Generate a runbook | `tuimm_knowledge` | `$kn_runbook` |
| Design a feature | `tuimm_planner` | `$planner_design` |
| Create a Jira ticket | any agent | `$jira_create-ticket` |
| See all commands | any agent | `$get-commands` |

You can also just talk naturally. "I need to review an MR" works as well as `$mr_review 242`.

---

## What's inside the package

```
tuimm/
├── agents/          19 agent configs (→ ~/.kiro/agents/)
└── tuimm/           package contents (→ ~/.kiro/tuimm/)
    ├── SETUP.md     credentials guide — start here after copying files
    ├── steering/    11 shared behavioral rules (loaded by all agents)
    ├── commands/    36 executable workflows (loaded per agent)
    ├── skills/      14 knowledge documents (consulted on demand)
    ├── templates/   37 output format definitions
    └── tools/       scripts and utilities (autobuild, guidelines-generator, etc.)
```

**Steering** defines how agents behave: git conventions, communication style, error handling, coding standards. All agents share the same rules — consistency is built in.

**Commands** are step-by-step workflows. When you type `$dev_solve`, the agent reads the command file, follows the steps, delegates to subagents, and formats the output using a template. 36 commands across 11 domains.

**Skills** are reference knowledge. Commit conventions, code review checklists, Weblate workflows, Jira document format. Agents load them when they need specific expertise.

**Tools** are standalone scripts: a task engine (autobuild), a coding guidelines extractor (guidelines-generator), background execution support, structured logging, and GitLab utilities.

---

## Prerequisites

- [Kiro CLI](https://kiro.dev) installed and working
- Node.js 18+ with npx
- Python 3.10+ (for tools)
- Git with SSH access to `ssh.source.tui`
- VPN for SonarQube
- Linux, WSL, or macOS

---

## Customization

A few things you might want to adapt to your team:

- **`tools/tracked-repos.txt`** — which repos to track for bot MR monitoring (`$mr_list`)
- **`skills/known-error-patterns/`** — add your service's recurring production errors (`$obs_dd-scan`)
- **`SETUP.md`** — has optional per-project Nuxt MCP setup for deeper codebase context

---

## Uninstall

```bash
rm ~/.kiro/agents/tuimm_*.json
rm -rf ~/.kiro/tuimm/
```

Env vars in your shell config are harmless to leave.

---

## More info

- **[SETUP.md](tuimm/SETUP.md)** — full credentials guide with URLs
- **[AGENTS.md](AGENTS.md)** — technical reference for AI assistants installing the package
- **[ideas/](../ideas/)** — architecture proposals and engineering practice specs
- **[docs/](../docs/)** — reference documentation about Excellence
