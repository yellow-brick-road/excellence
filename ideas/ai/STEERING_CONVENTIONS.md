# Steering: Conventions

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


Tech stack, coding conventions, prompt structure, and skill references. Loaded as steering by every Tier 1 agent.

## Tech Stack

> **Note:** Versions below reflect the current TUI tech stack (March 2026) from `TUI_TECH_STACK.md`. Update at launch (June 2026) to match actual production versions.

### Vue / Nuxt

- Nuxt 4.3, Vue 3.5, Composition API with `<script setup>`
- Pinia 3.0 for state management
- Skills: `vue`, `vue-best-practices`, `nuxt`, `pinia`

### TypeScript

- TypeScript 5.9, strict mode enabled
- Prefer `interface` over `type` for objects
- Use `unknown` over `any`
- Explicit return types on public functions
- Skill: `typescript-advanced-types`

### Testing

- Vitest with `@nuxt/test-utils`, Happy DOM
- Coverage: v8 provider, thresholds 80% (libraries) / 40-80% (frontend)
- Skills: `vitest`, `tui_vitest_plan`

### CSS / SCSS

- BEM methodology, `hc-` prefix for design system
- Scoped styles, no inline styles
- Stylelint with `stylelint-config-standard-scss`
- Skill: `tui_vue-component-guidelines`

### Git & Commits

- Conventional commits: `feat:`, `fix:`, `refactor:`, `chore:`, `docs:`, `test:`
- Branch naming: `feature/DIS-{ticket}_{description}`, `bugfix/...`, `hotfix/...`
- Skill: `tui_commit-conventions_guide`

### Build & Infra

- Node.js 22.14 (frontend) / 24.13 (libraries)
- npm workspaces, Lerna 9.x (publishing)
- Husky 9.x, lint-staged 16.x, Commitlint
- Docker, GitLab CI/CD

### CMS & Services

- Contentful (CMS)
- ConfigCat (feature flags, A/B testing)
- Datadog (APM, RUM, logs)
- Weblate (i18n)

## Spec-Driven Development

Agents plan before they execute. See `SPEC_DRIVEN_DEV.md` for the full practice.

### Conventions

- Plans live in `.plan/{topic}/` (git-ignored)
- Topic naming: Jira ticket ID (`DIS-1234`) or `kebab-case-description`
- Plan file: `PLAN.md`. Design file (level 3 only): `DESIGN.md`
- Agent proposes plan depth based on scope — user can override
- Human approval required before execution (interactive). Reviewer agent approval for Bot Service (autonomous)

## Naming Conventions

### Files & Folders
- `kebab-case` for files and folders
- Vue components: `PascalCase.vue`
- Composables: `use{Name}.ts`
- Stores: `{name}.store.ts`
- Tests: `{name}.spec.ts` (colocated) or `__tests__/{name}.spec.ts`

### Code
- Variables/functions: `camelCase`
- Constants: `SCREAMING_SNAKE_CASE`
- Types/Interfaces: `PascalCase`
- CSS classes: BEM (`block__element--modifier`)

## Agent Guard

Agent Guard applies only to **prompts** (multi-domain orchestrations). Commands don't need guards — domain enforcement is structural (only the owning agent loads the command).

### Rules

1. **Excellence Default is a master key** — it bypasses all Agent Guards and can execute any prompt
2. **Multi-domain prompts belong to Default** — if a prompt requires coordination between two or more specialists, its guard is `required: excellence_default`
3. **Guard failure = hard stop** — if the current agent does not match the guard (and is not Default), the prompt MUST NOT execute. Respond with: `This prompt requires {agent_name}.`

### Agent Guard Table

| Prompt | Required Agent | Orchestrates |
|--------|---------------|-------------|
| @incident-report | excellence_default | Observability + Knowledge |
| @sprint-report | excellence_default | DevEx + Quality Guardian |

## Commands

Single-agent targeted actions. Each command lives in `~/.kiro/commands/` as a `.md` file with detailed instructions.

### How It Works

1. The agent's **system prompt** lists its available commands: name, trigger, one-line description, and file path
2. Commands are **NOT loaded as resources** — they're read on-demand via `fs_read` when triggered (zero context waste)
3. The user triggers a command with `$name` prefix
4. The agent reads the command file and follows its instructions

### Execution Rules

- `$exact-name` → read the command file and execute immediately
- Similar input (e.g. "scan", "morning") → ask: "¿Quieres ejecutar $morning-scan?"
- `$commands` → list all available commands with descriptions (generic prompt, works on any agent)

### Agent System Prompt Example

```
## Commands

Available commands (read the file ONLY when triggered):

| Command | Trigger | Path |
|---------|---------|------|
| morning-scan | $morning-scan, $scan | ~/.kiro/commands/obs_morning_scan.md |
| investigate | $dd-investigate | ~/.kiro/commands/obs_dd-investigate.md |

Execution rules:
- $exact-name → read the command file and execute immediately
- Similar input → ask: "¿Quieres ejecutar $command-name?"
- $commands → list all available commands with descriptions
```

### Command File Structure

```markdown
# Command: $name

> Command name: `agent_prefix_command_name`
> Description: One-line description.
> Agent: Agent Name

## Trigger
## Workflow
## Output
## Phase
```

## Templates

Output format templates that define HOW generated content should look. Not executable — consumed by agents and commands to produce structured output.

Templates live in `~/.kiro/templates/` and are referenced by agents/commands that need them.

### Template Structure

```markdown
# Template: name

> Used by: Agent Name, Command Name

## Format
## Sections
## Example
```

## Scripts

Shell scripts for automation tasks. Live in `~/.kiro/scripts/`.

### Conventions

- Naming: `kebab-case.sh` (e.g. `gitlab-list-all-mrs.sh`)
- Must be executable (`chmod +x`)
- Agents invoke via `execute_bash`
- Not agent-specific — any agent with bash access can use them
- Subdirectories for grouped scripts (e.g. `scripts/weblate/`)

### Script File Structure

```bash
#!/usr/bin/env bash
# Description: One-line description
# Usage: ./script-name.sh [args]
# Used by: Agent Name, Command Name
```

## Tools

Standalone Python tools with their own tests, skills, and CLI interfaces. Live in `~/.kiro/tools/{name}/`.

### Conventions

- Naming: `kebab-case` directory (e.g. `tools/guidelines-generator/`)
- Each tool has a manifest entry in `REGISTRY.md` (version, deps, files, tests)
- Companion skill in `~/.kiro/skills/excellence_{name}/` documents usage
- Tests in `__tests__/` subdirectory, run with pytest
- Dependencies: stdlib only (no pip deps) where possible
- Binary symlinks in `~/.local/bin/` for CLI access

### Tool Directory Structure

```
tools/{name}/
├── {name}.py           # Main entry point
├── __tests__/
│   └── test_{name}.py  # Tests
└── (supporting modules)
```

## Knowledge Skills

Reference material (not executable workflows). No Agent Guard, no triggers. Declare intended consumers.

### Format

```markdown
## Intended Agents

Primary: <agent_name>
Also useful for: <agent_name>, <agent_name>
```

### Rules

1. **Informational, not enforced** — any agent can load any skill
2. **Primary = designed for** — the agent that benefits most
3. **Also useful for = secondary consumers** — agents that may reference occasionally