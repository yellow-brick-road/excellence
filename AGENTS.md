# AGENTS.md — TUIMM Package Installation Guide

This file is for AI assistants helping developers install the TUIMM agent package. If you are a human, read README.md instead.

## What this package is

TUIMM is a set of 19 AI agent configurations for Kiro CLI, designed for TUI Musement's frontend engineering teams. It connects to Jira, GitLab, SonarQube, Datadog, Figma, Contentful, ConfigCat, and Confluence via MCP (Model Context Protocol).

## Package structure

```
tuimm/                              ← inside the excellence repo
├── AGENTS.md                       ← you are reading this
├── README.md                       ← human-readable overview
├── SETUP.md                        ← credentials and env var guide
├── agents/                         ← 19 agent JSON configs
│   ├── default.json                ← entry point / concierge
│   ├── dev.json                    ← ticket-to-MR workflow
│   ├── mr.json                     ← MR review and approval
│   └── subagent_*.json             ← 10 Tier 2 tool subagents
│
├── steering/                       ← 11 *.md behavioral rules
│   ├── 1_AGENT_RULES.md            ← hub file, references all others
│   ├── GIT.md
│   ├── scripts/                    ← session utilities
│   │   └── workspace-cleanup-check.py
│   └── ...
│
├── skills/                         ← 27 skill directories
│   ├── dev-workflow/                ← workflow skill (commands + templates)
│   │   ├── SKILL.md
│   │   ├── commands/
│   │   └── assets/templates/
│   ├── autobuild-reference/         ← knowledge skill with scripts
│   │   ├── SKILL.md
│   │   └── scripts/
│   ├── commit-conventions/          ← knowledge skill (reference only)
│   │   └── SKILL.md
│   └── ...
│
├── tuimm/                          ← knowledgeBase index (just README.md)
│   └── README.md
│
└── prompts/                        ← empty (reserved)
```

Skills follow the [agentskills.io](https://agentskills.io) standard. There are two types:
- **Workflow skills** (12): contain commands + templates for a domain (e.g. `dev-workflow`)
- **Knowledge skills** (14): reference material only (e.g. `commit-conventions`)

## Installation steps

### Step 1 — Copy files

Contents go to `~/.kiro/` global directories. The installer (`aitm`) adds a `tuimm-` prefix to agents and skills, and places steering files in a `tuimm/` subfolder, preventing collisions with other packages.

```bash
mkdir -p ~/.kiro/agents ~/.kiro/steering/tuimm ~/.kiro/skills ~/.kiro/tuimm

cp agents/*.json ~/.kiro/agents/
cp steering/*.md ~/.kiro/steering/tuimm/
cp -r steering/scripts ~/.kiro/steering/
cp -r skills/*/ ~/.kiro/skills/
cp tuimm/README.md ~/.kiro/tuimm/
```

### Step 2 — Verify file placement

```bash
ls ~/.kiro/agents/tuimm-*.json | wc -l         # expect: 19
ls ~/.kiro/steering/tuimm/*.md | wc -l         # expect: 11
ls -d ~/.kiro/skills/tuimm-*/ | wc -l          # expect: 27
```

After copying, the structure must be:

```
~/.kiro/
├── agents/
│   ├── tuimm-default.json
│   ├── tuimm-dev.json
│   └── ... (19 total tuimm-*.json files)
│
├── steering/
│   └── tuimm/
│       ├── 1_AGENT_RULES.md
│       └── ... (11 total *.md files)
│
├── skills/
│   ├── tuimm-dev-workflow/
│   ├── tuimm-mr-workflow/
│   ├── tuimm-commit-conventions/
│   └── ... (27 total tuimm-* directories)
│
└── tuimm/
    └── README.md    ← knowledgeBase index target
```

### Step 3 — Why the paths matter

Agent JSONs use `${INSTALL_DIRECTORY}` paths in their `resources` field:

```
file://${INSTALL_DIRECTORY}/.kiro/steering/tuimm/*.md
skill://${INSTALL_DIRECTORY}/.kiro/skills/tuimm-*/SKILL.md
```

The `tuimm/` folder for steering and `tuimm-` prefix for skills scopes the glob to only TUIMM files, preventing collision with personal or other package files in the same directories.

### Step 4 — Configure credentials

The user needs to set environment variables for the MCP servers. Read `SETUP.md` for the full list.

Summary of required env vars:

| Variable | Service | Where to get it |
|----------|---------|-----------------|
| GITLAB_PERSONAL_ACCESS_TOKEN | GitLab | https://source.tui/-/user_settings/personal_access_tokens |
| DD_API_KEY | Datadog | https://tui-musement.datadoghq.eu/organization-settings/api-keys |
| DD_APP_KEY | Datadog | same URL |
| SONARQUBE_TOKEN | SonarQube | https://sonarqube.devops.tui/account/security |
| FIGMA_API_KEY | Figma | https://www.figma.com/settings |
| CONTENTFUL_MANAGEMENT_ACCESS_TOKEN | Contentful | https://app.contentful.com/account/profile/cma_tokens |
| CONFIGCAT_API_USER | ConfigCat | https://app.configcat.com/my-account/public-api-credentials |
| CONFIGCAT_API_PASS | ConfigCat | same URL |

Services that DON'T need env vars:
- Jira / Confluence — OAuth via browser, automatic on first use
- Nuxt docs — public endpoint, no auth

The env vars must be exported in the shell BEFORE starting kiro-cli. Add them to `~/.bashrc` (Linux/WSL) or `~/.zshrc` (macOS).

### Step 5 — Verify installation

```bash
kiro-cli --agent tuimm-default
```

Once inside, type `$get-commands`. If it lists 40 commands across 9 agents, the installation is correct.

## How the pieces relate

```
Agent JSON (tuimm-dev.json)
  │
  ├── loads steering/tuimm/*.md at startup (behavioral rules)
  ├── loads skills/tuimm-*/SKILL.md on demand (progressive disclosure)
  │     Each skill may contain:
  │       commands/   → executable workflows
  │       assets/templates/ → output formats
  │       references/ → additional docs
  ├── indexes ~/.kiro/tuimm/ as knowledgeBase (semantic search)
  │
  ├── spawns subagents via the subagent tool:
  │     tuimm-subagent_jira → Atlassian MCP → Jira API
  │     tuimm-subagent_gitlab → GitLab MCP → source.tui API
  │     tuimm-subagent_sonar → SonarQube MCP → sonarqube.devops.tui
  │     tuimm-subagent_code_reviewer → 5 MCPs (read-only)
  │     ...
  │
  └── runs scripts bundled inside skills via shell:
        autobuild (engine.py), bg (bg.py), logd, guidelines-generator, etc.
```

Commands reference templates: "present results using the mr-review-summary template."
Commands reference skills: "consult the tuimm-jira-adf skill before writing descriptions."
Commands reference subagents: "delegate to tuimm-subagent_gitlab."
Steering references other steering: "read and follow GIT.md."

## Existing agents warning

If the user already has files in `~/.kiro/agents/` with `tuimm-` prefix, the copy will overwrite them. Check first:

```bash
ls ~/.kiro/agents/tuimm-*.json 2>/dev/null
```

If files exist, ask the user whether to overwrite or back up first.

## Uninstallation

```bash
rm ~/.kiro/agents/tuimm-*.json
rm -rf ~/.kiro/steering/tuimm/
rm -rf ~/.kiro/skills/tuimm-*/
rm -rf ~/.kiro/tuimm/
```

This removes all TUIMM agents and content. It does not remove env vars from the shell config — those are harmless to leave.

## Do NOT modify

- Do not rename agent JSON files — the filename must match the `"name"` field
- Do not rename steering files — agents load them via `tuimm/*.md` glob
- Do not rename skill directories — must match the `name:` field in SKILL.md
- Do not edit steering files unless the user explicitly asks — they are shared across all agents
