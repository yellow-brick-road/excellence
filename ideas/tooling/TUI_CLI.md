# Idea: TUI CLI

## Title

Domain-oriented internal CLI with interactive flows for frontend project lifecycle and AI tooling.

## Context

Excellence defines standards, conventions, shared configs, AI agents, and prompts. But without a delivery mechanism, adoption depends on copy-pasting, tribal knowledge, and manual setup. Every new repo starts from scratch. Every config update requires manual propagation to N repos.

The TUI CLI (`@tui/cli`) is the executable arm of Excellence — it creates repos that are 100% compliant from commit zero, keeps them aligned over time, and distributes AI tooling as first-class artifacts.

## UX Philosophy

Commands are organized by **domain**, not by utility. Developers think "I want to do something with AI" → `tui ai`, not "what was the subcommand for installing a prompt?"

Every domain command works in two modes:
- **Interactive** — run `tui ai` with no args → guided flow with selectable options
- **Direct** — run `tui ai install agents` → executes immediately, scriptable for CI

Interactive flows use `@clack/prompts` for a polished terminal UX (spinners, selects, confirmations, grouped options).

## The Problem

```
Today:

1. New repo → clone something, delete half of it, manually configure
   - ESLint? Copy from another repo. Which one? Depends who you ask
   - Stylelint? Maybe. If someone remembers
   - Husky + commitlint? Sometimes
   - Vitest? Different setup per repo
   - BEM? "We use BEM" (but 3 different interpretations)

2. Config update → update one repo, forget the other 12
   - New ESLint rule? Good luck propagating
   - Node version bump? Each repo on its own schedule
   - Shared package update? Manual, error-prone

3. AI tooling → manual installation, no versioning, no updates
   - Agents? Copy JSON files manually
   - Prompts? Copy markdown files manually
   - Skills? Clone repos, symlink, hope for the best
   - MCP servers? Each dev configures independently
```

## The Solution

```
$ tui ai

┌  TUI CLI — AI Tooling
│
◆  What would you like to do?
│  ● Install agents
│  ○ Update agents
│  ○ Install prompts
│  ○ Install skills
│  ○ Configure MCP Gateway
│  ○ Show status
└

$ tui fe

┌  TUI CLI — Frontend
│
◆  What would you like to do?
│  ● Create project
│  ○ Add component
│  ○ Add composable
│  ○ Add store
│  ○ Sync configs
│  ○ Check compliance
│  ○ Check dependencies
└
```

## Domains

### `tui ai` — AI Tooling

Everything related to the Excellence AI architecture.

**Interactive flow:**
```
tui ai
├── Install agents       → Select which agents (all, or pick from list)
├── Update agents        → Check for updates, apply
├── Install prompts      → Select which prompts (all, or pick from list)
├── Install skills       → Select which commands (all, or by agent: OBS, QG, DEV, DS, KN, EDEV, EMR)
├── Install tools        → Python tools: logd, bg, autobuild (resolves deps)
├── Configure MCP Gateway → SSO auth setup for mcp.tui.internal
├── Show status          → What's installed, what's outdated, versions
└── Suggest              → "I want to do X" → recommends agent/prompt
```

**Direct mode:**
```bash
tui ai install agents                  # Install all agents
tui ai install agents quality-guardian  # Install specific agent
tui ai install prompts                 # Install all prompts (2)
tui ai install commands                # Install all commands (21)
tui ai install commands --agent QG     # Install only Quality Guardian commands
tui ai install skills                  # Install all knowledge skills
tui ai install templates               # Install all output templates
tui ai install tools                   # Install all Python tools (logd + bg + autobuild)
tui ai install tools logd              # Install only logd
tui ai install tools bg                # Install bg + logd (dependency)
tui ai install tools autobuild         # Install autobuild + bg + logd (dependencies)
tui ai install tools --check           # Show what's missing without installing
tui ai update                          # Update everything
tui ai status                          # Show installed versions
tui ai config gateway                  # Configure MCP Gateway
```

**What it manages:**
- Agent definitions (JSON configs) → `.kiro/agents/`
- Prompts (markdown) → `.kiro/prompts/`
- Skills (markdown + config) → `.kiro/skills/`
- Tools (Python) → `~/.kiro/{tool}/` — standalone scripts with dependency resolution
- MCP Gateway connection → agent MCP server configs
- Steering files → `.kiro/steering/`
- Version tracking per artifact

**Tools — Python utilities with dependency graph:**

| Tool | Deps | Install path | Description |
|------|------|-------------|-------------|
| `logd` | — | `~/.kiro/tools/logd/` | UDP log daemon + client library |
| `bg` | logd | `~/.kiro/tools/bg/` | Background execution helpers (--bg/--status/--tail/--stop) |
| `autobuild` | logd, bg | `~/.kiro/tools/autobuild/` | Task engine + kiro-cli wrapper |

Install resolves dependencies recursively. `tui ai install tools bg` checks if logd is present, installs it if missing, then installs bg. Each tool declares deps in its `manifest.json`.

Requires Python 3.10+ (verified by `tui cli setup` / `tui cli doctor`).

---

### `tui fe` — Frontend Project Lifecycle

Everything for creating, maintaining, and governing frontend projects.

**Interactive flow:**
```
tui fe
├── Create project       → Template selection (b2c, library, component)
│   └── Asks: name, template, GitLab group, SonarQube setup
├── Add component        → Scaffolds Vue component (BEM, test file, types)
│   └── Asks: name, directory, with test?, with story?
├── Add composable       → Scaffolds composable with test
│   └── Asks: name, directory
├── Add store            → Scaffolds Pinia store with test
│   └── Asks: name, directory
├── Add page             → Scaffolds page + route
│   └── Asks: name, path, layout, middleware?
├── Add plugin           → Scaffolds Nuxt plugin
│   └── Asks: name, client/server/universal
├── Add layer            → Scaffolds Nuxt layer structure
│   └── Asks: name, directory
├── Add middleware        → Scaffolds route middleware
│   └── Asks: name, global?
├── Sync configs         → Pull latest shared configs
│   └── Asks: which configs? (all, or pick: eslint, stylelint, vitest, ci, husky)
├── Check compliance     → Full scan, score 0-100%, actionable items
│   └── Shows: configs, coverage, CI, required files, BEM, Node version
├── Fix issues           → Auto-fix what's possible
│   └── Shows: what will change, asks confirmation
├── Check dependencies   → Outdated, vulnerable, misaligned
│   └── Shows: update suggestions with breaking change warnings
├── Audit security       → npm audit + license compliance
├── SonarQube status     → Quality gate, coverage, issues summary
├── Setup IDE            → VS Code extensions, settings, snippets for frontend
│   └── Asks: full setup or pick (extensions, settings, snippets)
└── Sync IDE settings    → Pull latest recommended VS Code config
```

**Direct mode:**
```bash
tui fe create my-project --template b2c
tui fe add component SearchBar --dir components/search
tui fe add composable useBooking
tui fe add store booking
tui fe add page checkout --layout default
tui fe add plugin analytics --mode client
tui fe sync configs
tui fe sync configs --only eslint,stylelint
tui fe check                           # Full compliance check
tui fe check --fix                     # Auto-fix
tui fe check --report                  # Generate report
tui fe deps                            # Dependency check
tui fe deps --align                    # Align shared deps across workspaces
tui fe audit                           # Security audit
tui fe sonar                           # SonarQube status
tui fe ide setup                       # Full VS Code setup for frontend
tui fe ide extensions                  # Install recommended extensions
tui fe ide settings                    # Apply workspace settings
tui fe ide snippets                    # Install code snippets
```

**Templates:**
- `b2c` — Full Nuxt 4 B2C frontend (layers, Pinia, i18n, Contentful, ConfigCat, Datadog)
- `library` — Shared Nuxt library (`@dx/*` package)
- `component` — Standalone Vue component package

**What `create` sets up:**
- Nuxt 4 with TypeScript
- ESLint + Stylelint (Excellence standard config)
- Vitest with `@nuxt/test-utils` and coverage thresholds
- Husky + commitlint + lint-staged
- Docker + `.gitlab-ci.yml`
- Renovate Bot config
- README from template
- `.editorconfig`, `.nvmrc`
- SonarQube project (optional)
- GitLab repo creation (optional)

**What scaffolded files include:**
- Component: `<script setup lang="ts">`, BEM SCSS block, test file, prop types interface
- Composable: typed return, test file
- Store: Pinia setup store with typed state, test file
- Page: `definePageMeta`, layout, SEO meta

**Compliance checks:**
- ESLint config matches Excellence standard
- Stylelint config matches Excellence standard
- Vitest configured with correct thresholds
- Husky hooks installed and configured
- Commitlint configured
- Node.js version matches target (`.nvmrc`)
- CI/CD pipeline uses latest templates
- Required files exist (README, .editorconfig, Docker, .nvmrc)
- BEM naming in SCSS
- Coverage thresholds meet minimum
- Renovate Bot configured
- SonarQube project linked
- No hardcoded secrets

**Output:** compliance score with color-coded results and fix suggestions.

---

### `tui cli` — CLI Self-Management

Meta commands for the CLI itself.

**Interactive flow:**
```
tui cli
├── Setup                → Install/configure all prerequisites
├── Update               → Update CLI to latest version
├── Version              → Show current version
├── Doctor               → Self-check (Node, npm, git, auth, connectivity)
└── Config               → CLI configuration (registry URL, defaults)
```

**Direct mode:**
```bash
tui cli setup                          # Install all prerequisites
tui cli setup --check                  # Dry-run: show what's missing
tui cli update                         # Update CLI
tui cli version                        # Show version
tui cli doctor                         # Health check
tui cli config                         # Show/edit config
```

**Setup installs/configures:**
- nvm + Node.js (target version from `.nvmrc`)
- Python 3.10+ (via pyenv or system)
- Docker + Docker Compose
- kiro-cli (latest)
- logd daemon (`~/.kiro/tools/logd/`) — start + enable on boot
- Git config (user, email, default branch)
- GitLab SSH key check
- npm registry auth (internal `@tui/*`)

`setup` is idempotent — skips what's already installed, updates what's outdated. On first run it's a full bootstrap; on subsequent runs it's a health check + fix.

**Doctor checks:**
- Node.js version (matches required)
- Python 3.10+ available
- npm/pnpm available
- Docker running
- logd daemon running
- Git configured (user, email)
- GitLab authentication
- MCP Gateway connectivity
- Registry reachable
- Disk space

## Architecture

```
@tui/cli (npm package)
│
├── domains/
│   ├── ai/           → Agent, prompt, skill management
│   ├── fe/           → Project scaffolding, code generation, quality, deps, IDE
│   └── cli/          → Self-management
│
├── flows/            → Interactive flow definitions (@clack/prompts)
│
├── generators/       → Code generators (component, composable, store, page)
│
├── templates/        → Project templates (or fetched from registry)
│
├── configs/          → Shared config definitions (ESLint, Stylelint, etc.)
│
├── registry/         → Registry client (fetch artifacts, check versions)
│
└── core/
    ├── diff          → Config diffing and merging
    ├── git           → Git operations
    ├── gitlab        → GitLab API integration
    └── sonar         → SonarQube project setup
```

### Tech Stack
- Node.js + TypeScript
- citty (CLI framework — lightweight, from UnJS ecosystem, Nuxt-aligned)
- `@clack/prompts` (interactive terminal UX)
- Published as `@tui/cli` on internal npm registry
- Invoked via `npx @tui/cli` or global install

### Registry

Git-based registry (`tui-cli-registry` repo) with versioned artifacts:

```
tui-cli-registry/
├── templates/
│   ├── b2c/
│   ├── library/
│   └── component/
├── configs/
│   ├── eslint/
│   ├── stylelint/
│   └── ...
├── agents/
│   ├── excellence-default.json
│   ├── quality-guardian.json
│   └── ...
├── prompts/
│   ├── OBS_morning-scan.md
│   ├── QG_quality-check.md
│   └── ...
├── skills/
│   ├── tui_vue-component-guidelines/
│   ├── tui_commit-conventions/
│   └── ...
├── tools/
│   ├── logd/
│   │   ├── manifest.json    # { version, deps: [], files, install_path }
│   │   ├── logd.py
│   │   └── loglib.py
│   ├── bg/
│   │   ├── manifest.json    # { version, deps: ["logd"], files, install_path }
│   │   └── bg.py
│   └── autobuild/
│       ├── manifest.json    # { version, deps: ["logd", "bg"], files, install_path }
│       ├── engine.py
│       └── kiro.py
├── ide/
│   ├── vscode-extensions.json
│   ├── vscode-settings.json
│   └── snippets/
└── manifest.json     # Version index for all artifacts
```

## Connection to Excellence AI Architecture

| AI Architecture Component | CLI Domain | Command |
|---|---|---|
| Tier 1 agents (9) | `tui ai` | `tui ai install agents` |
| Tier 2 subagent configs | `tui ai` | `tui ai install agents` |
| MCP Gateway connection | `tui ai` | `tui ai config gateway` |
| Reusable prompts (2) | `tui ai` | `tui ai install prompts` |
| Commands (21) | `tui ai` | `tui ai install commands` |
| Output templates | `tui ai` | `tui ai install templates` |
| Knowledge skills | `tui ai` | `tui ai install skills` |
| Python tools (logd, bg, autobuild) | `tui ai` | `tui ai install tools` |
| Shared configs | `tui fe` | `tui fe sync configs` |
| Project templates | `tui fe` | `tui fe create` |
| Compliance verification | `tui fe` | `tui fe check` |
| IDE standardization | `tui fe` | `tui fe ide setup` |

## Connection to DevEx Agent

The DevEx Agent can invoke CLI logic programmatically:
- "Check compliance" → `tui fe check`
- "Update ESLint" → `tui fe sync configs --only eslint`
- "What's outdated?" → `tui fe deps`
- "Set up my IDE" → `tui fe ide setup`
- "Install AI agents" → `tui ai install agents`

The CLI provides the engine, the agent provides the intelligence.

## Implementation Phases

### Phase 1: Foundation
- `tui fe create` with b2c and library templates
- `tui fe sync configs` for ESLint and Stylelint
- `tui fe check` with basic compliance rules
- `tui cli doctor` and `tui cli update`
- Git-based registry with initial templates and configs
- Interactive flows with `@clack/prompts`
- Published as `@tui/cli` on internal npm registry

### Phase 2: AI + Code Generation
- `tui ai` — full agent/prompt/command/skill/template management
- `tui fe add` — component, composable, store, page generators
- `tui fe sync configs` expanded to all targets
- `tui fe deps` for dependency governance
- MCP Gateway configuration

### Phase 3: Full Experience
- `tui fe ide` — VS Code setup, snippets, settings
- `tui fe` — full compliance scoring and reporting
- Integration with DevEx Agent
- Org-wide compliance dashboard
- Custom template management

## Open Questions

- [ ] Should `tui fe` also cover non-Nuxt projects? Or add `tui node` later for backend services?
- [ ] Registry: git-based vs npm packages vs custom API?
- [ ] How to handle config conflicts during sync? (merge strategy, overwrite, skip)
- [ ] Should `tui fe create` also set up GitLab project + CI/CD, or just local scaffolding?
- [ ] How to version templates independently from the CLI?
- [ ] Global install (`npm i -g @tui/cli`) vs `npx @tui/cli` vs both?
- [ ] How to handle teams with legitimate deviations from standards? (allowlist, overrides)
- [ ] Should code generators (add component, etc.) be opinionated or configurable?