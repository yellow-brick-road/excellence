# Excellence: AI-Powered Engineering at Scale

> A practical framework for accelerating software delivery through AI agents, shared tooling, and automated workflows.

> ⚠️ **Vision document.** Written for the Excellence demo (Apr 10, 2026). Describes the target state, not current implementation. Some features (TUI CLI, routines, MCP Gateway) are planned, not built. For current state, see ROADMAP.md and the actual `tuimm/` implementation.

## The Problem

Engineering teams face the same friction everywhere. Configs drift between repos. Onboarding takes days. Code reviews are inconsistent. Documentation goes stale. Dependency updates pile up. Production errors get investigated manually. Every team solves these problems independently, and the solutions don't travel.

What if we could encode the best engineering practices into AI agents that work alongside developers — and distribute them with a single command?

That's what Excellence does.

---

## 1. TUI CLI — One Command to Rule Them All

The TUI CLI (`@tui/cli`) is a domain-oriented internal CLI. It's the distribution mechanism for everything Excellence produces: agents, configs, templates, tools. Think of it as the executable arm of the guild.

### Why a CLI?

Without it, adopting any standard means copy-pasting files, reading wikis, and hoping everyone does it the same way. With it, one command sets up a developer's entire environment.

### Three Domains

The CLI is organized by what you want to do, not by what tool you're using.

**`tui ai` — AI Tooling**

Install and manage the AI agent ecosystem.

```bash
tui ai install agents                  # Deploy all Excellence agents
tui ai install agents quality-guardian  # Deploy a specific agent
tui ai install commands                # Deploy all agent commands
tui ai install commands --agent QG     # Only Quality Guardian commands
tui ai install skills                  # Deploy knowledge skills
tui ai install tools                   # Deploy Python utilities (autobuild, etc.)
tui ai status                          # What's installed, what's outdated
tui ai update                          # Update everything to latest
```

Every artifact is versioned in a git-based registry. The CLI tracks what's installed locally and handles updates.

**`tui fe` — Frontend Project Lifecycle**

Create, maintain, and govern frontend projects.

```bash
tui fe create my-project --template b2c   # Scaffold a fully compliant project
tui fe add component SearchBar            # Generate Vue component (BEM, tests, types)
tui fe sync configs                       # Pull latest shared ESLint, Stylelint, etc.
tui fe check                              # Compliance score (0-100%)
tui fe check --fix                        # Auto-fix what's possible
tui fe deps                               # Dependency health check
```

`tui fe create` sets up everything from day one: Nuxt 4, TypeScript, ESLint, Stylelint, Vitest, Husky, commitlint, Docker, CI/CD pipeline, Renovate Bot, SonarQube. A new repo is 100% compliant from commit zero.

**`tui cli` — Self-Management**

```bash
tui cli setup     # Install all prerequisites (Node, Python, Docker, kiro-cli, etc.)
tui cli doctor    # Health check — is everything working?
tui cli update    # Update the CLI itself
```

`setup` is idempotent. First run is a full bootstrap. Subsequent runs check and fix.

### You Don't Need to Memorize Anything

Just type `tui` and the CLI guides you:

```
$ tui

┌  TUI CLI
│
◆  What domain?
│  ● AI Tooling
│  ○ Frontend
│  ○ Backend
│  ○ Cloud
│  ○ CLI Management
└
```

Pick "AI Tooling" and it asks what you want to do. Pick "Install" and it asks what to install. Every level narrows down the options until you reach the action. No need to remember commands — the CLI walks you through it. And if you already know what you want, `tui ai install agents` works directly.

### Not Just Frontend

The CLI architecture is domain-extensible. Today it's `tui ai` and `tui fe`. Tomorrow it could be `tui be` for backend services, `tui cloud` for infrastructure, `tui data` for data pipelines. Same pattern, different domains. Any guild can plug in.

### Interactive Mode

Every command also works interactively. Run `tui ai` with no arguments and you get a guided flow:

```
$ tui ai

┌  TUI CLI — AI Tooling
│
◆  What would you like to do?
│  ● Install agents
│  ○ Update agents
│  ○ Install commands
│  ○ Install skills
│  ○ Show status
└
```

Built with `@clack/prompts` for a polished terminal experience. Direct mode for scripting and CI, interactive mode for humans.

---

## 2. Excellence Agents — AI That Knows Your Stack

The core of the system. Nine specialized AI agents that understand your codebase, your tools, and your workflows. They don't replace developers — they handle the repetitive, time-consuming work so developers can focus on what matters.

### How It Works

Each agent is a specialist invoked directly by the developer. You don't go through a central router — you talk to the expert you need. If you're not sure which one, the Default agent tells you.

Two tiers. Tier 1 agents talk to developers. Tier 2 subagents talk to tools.

```
Developer
    │
    ├── kiro-cli --agent excellence_dev        (direct invocation)
    ├── kiro-cli --agent excellence_mr         (direct invocation)
    ├── /agent swap excellence_quality_guardian (switch within session)
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  TIER 1 — Specialist Agents                         │
│                                                     │
│  Default · Quality Guardian · Observability · DevEx │
│  Design System · Knowledge · Dev · MR · Planner     │
└──────────────────────┬──────────────────────────────┘
                       │ agents call tool APIs via MCP
                       ▼
┌─────────────────────────────────────────────────────┐
│  TIER 2 — Tool Subagents (API wrappers)             │
│                                                     │
│  Jira · GitLab · SonarQube · Datadog · Figma        │
│  Confluence · Contentful · ConfigCat · Nuxt          │
└─────────────────────────────────────────────────────┘
```

Don't know which agent to use? Start with the Default:

```
$ kiro-cli --agent excellence_default

You: "I need to check if our dependencies are up to date"

Excellence Default:
  That's a job for the Quality Guardian. You want $qg_dependency-scan.

  - Switch here: /agent swap excellence_quality_guardian
  - Or open a new session: kiro-cli --agent excellence_quality_guardian

  Once there, just say: "$qg_dependency-scan"
```

Here's what it looks like in practice:

```
$ kiro-cli --agent excellence_dev

You: "I need to work on DIS-1234"

Excellence Dev:
  Reading the ticket first.

  Invoking subagent: excellence_subagent_jira
    with query: Get issue DIS-1234 with full description, acceptance criteria,
    and linked issues
  ✓ excellence_subagent_jira (3 tool uses · 2.1s)

  Got it: "Add date picker to search filters. AC: supports range selection,
  validates min/max dates, syncs with URL params."

  Invoking subagent: excellence_subagent_gitlab
    with query: Clone repository dx/b2c-tuimusement-frontend
  ✓ excellence_subagent_gitlab (2 tool uses · 3.8s)

  Invoking subagent: excellence_subagent_gitlab
    with query: Create and checkout branch feature/DIS-1234-date-picker-filters
  ✓ excellence_subagent_gitlab (1 tool uses · 0.9s)

  Reading project files to understand the codebase...
  ✓ Read 12 files: SearchFilters.vue, useFilters.ts, BaseFilter.vue, ...

  Searching knowledge base for relevant conventions...
  ✓ Found: vue-component-guidelines, BEM naming, composable patterns

  Here's my plan:
    1. Create useDatePicker composable with range support
       { detailed code explanation }
    2. Add DatePickerFilter component following existing filter pattern
       { detailed code explanation }
    3. Wire URL param sync in SearchFilters.vue
       { detailed code explanation }
    4. Add unit tests
       { detailed code explanation }

  Approve? [y/n]

You: "y"

  Implementing step 1...
  ✓ Created composables/useDatePicker.ts
  Implementing step 2...
  ✓ Created components/DatePickerFilter.vue
  Implementing step 3...
  ✓ Modified SearchFilters.vue
  Running tests... all green.

  Changes ready to commit. Want me to commit? [y/n]

You: "y"

  Invoking subagent: excellence_subagent_gitlab
    with query: Stage and commit all changes with message
    "feat(DIS-1234): add date picker to search filters"
  ✓ excellence_subagent_gitlab (2 tool uses · 1.1s)

  Committed. Push is on you:
  git push origin feature/DIS-1234-date-picker-filters

You: "done, pushed"

  Want me to create the MR? [y/n]

You: "y"

  Invoking subagent: excellence_subagent_gitlab
    with query: Read merge request template from repository
  ✓ excellence_subagent_gitlab (1 tool uses · 0.8s)

  Invoking subagent: excellence_subagent_gitlab
    with query: Create merge request for branch
    feature/DIS-1234-date-picker-filters using template, link DIS-1234
  ✓ excellence_subagent_gitlab (3 tool uses · 2.4s)

  Invoking subagent: excellence_subagent_jira
    with query: Transition DIS-1234 to "In Review" and add comment with MR link
  ✓ excellence_subagent_jira (2 tool uses · 1.4s)

  Done. MR !847 created: https://source.tui/dx/.../merge_requests/847
  Jira ticket moved to In Review.
```

The developer talks to one agent. Behind the scenes, that agent orchestrates Jira, GitLab, SonarQube — whatever it needs. No context switching between dashboards.

### The Nine Agents

| Agent | What It Does | Example |
|-------|-------------|---------|
| **Excellence Default** | Entry point and concierge. Knows what every agent can do, guides you to the right one. Handles shared commands (Jira, Weblate) directly | "I need to review an MR" → "That's `excellence_mr`. Switch: `/agent swap excellence_mr`" |
| **Quality Guardian** | Code quality, tech debt, dependencies, releases | "Check quality for this MR" → SonarQube analysis + coverage + new issues |
| **Observability** | Production errors, monitoring, incident investigation | "Scan production errors" → Datadog log analysis + error patterns |
| **DevEx** | Feature flags, translations, content models, sprint workflow | "Find stale feature flags" → ConfigCat audit + codebase cross-reference |
| **Design System** | Figma-to-code alignment, component governance | "Audit design system adoption" → Figma tokens vs codebase scan |
| **Knowledge** | Documentation health, runbooks, onboarding guides | "Check doc health" → Confluence inventory + stale/orphan detection |
| **Excellence Dev** | Ticket-to-MR workflow. Reads ticket, plans, implements, creates MR | "Solve DIS-1234" → reads Jira → plans → codes → MR |
| **Excellence MR** | MR review, feedback, approval | "Review MR 242" → structured review with severity levels |
| **Excellence Planner** | Cross-domain analysis, technical design, task decomposition, Jira ticket creation from plans | "Design the new search architecture" → DESIGN.md + task breakdown + Jira tickets |

### Commands — Repeatable Workflows

Each agent has commands: structured, step-by-step workflows for specific tasks. 37 commands across 11 domains.

A few examples:

**`$qg_quality-check`** — Quality Guardian scans SonarQube for a project, pulls new issues, checks coverage trends, compares against quality gates, and produces a report with actionable items.

**`$obs_dd-scan`** — Observability agent queries Datadog for recent errors in production, groups them by pattern, identifies new vs recurring issues, and flags anything that needs attention.

**`$devex_flag-cleanup`** — DevEx agent lists all feature flags in ConfigCat, identifies stale ones (100% rollout, old, or orphaned), cross-references with the codebase to find usage, and produces a cleanup plan.

**`$kn_runbook`** — Knowledge agent searches existing documentation, pulls incident history from Observability, gathers code context, and synthesizes a runbook that gets published to Confluence.

**`$planner_design`** — Planner agent consults relevant specialists, analyzes the codebase, and produces a technical design document with architecture decisions, trade-offs, and a task breakdown compatible with the autobuild engine.

Commands are markdown files with YAML frontmatter. They load on-demand — the agent reads the command, follows the steps, and uses its subagents to execute each one.

### Steering — Shared Behavior

All agents share 11 steering files that define how they behave: conventions, git rules, communication style, error handling, tool usage rules. This ensures consistency — every agent follows the same standards regardless of domain.

```
steering/
├── 1_AGENT_RULES.md          # Hub — references all others
├── OPERATING_MODE.md          # Mandatory workflow: understand → plan → execute → verify
├── GIT.md                     # Branch naming, commit conventions
├── COMMUNICATION.md           # How agents communicate with developers
├── TOOL_RULES.md              # Which tools to use and how
├── CONVENTIONS.md             # Coding standards, naming, file structure
├── SUBAGENTS.md               # Tier 2 reference and mapping
├── ARTIFACTS.md               # Commands, skills, templates registry
├── ERROR_HANDLING.md          # What to do when things fail
├── AI_USAGE_TRACKING.md       # Jira AI usage fields
└── TECH_STACK.md              # Framework versions, dependencies
```

### Skills — Reusable Knowledge

Skills are knowledge documents that agents load when they need specific expertise. Commit conventions, code review checklists, Weblate translation workflows, file modification patterns, MCP tool references. Eight skills today, growing as we codify more practices.

### Routines — Automated Workflows

Agents can run routines: multi-step workflows that combine several commands and agents. Some examples of what's possible:

- **Morning scan** — Observability checks production errors, Quality Guardian checks quality gates, DevEx summarizes pending work. One command, three agents, full picture.
- **MR lifecycle** — Dev agent implements a ticket, creates the MR, MR agent reviews it, Quality Guardian checks quality. The developer approves and merges.
- **Weekly health check** — Knowledge agent audits documentation, Quality Guardian scans dependencies, DevEx checks feature flag hygiene. Reports land in Confluence.

### Simplified Example: Solving a Ticket

```
Developer: "solve DIS-1234"

Excellence Dev agent:
  1. Reads the Jira ticket (via Jira subagent)
  2. Analyzes the codebase to understand context
  3. Proposes a plan → developer approves
  4. Implements the changes
  5. Runs tests
  6. Creates a feature branch, commits, pushes
  7. Creates a merge request (via GitLab subagent)
  8. Updates the Jira ticket status

Developer reviews the MR, adjusts if needed, merges.
```

### Simplified Example: Reviewing an MR

```
Developer: "review MR 242"

Excellence MR agent:
  1. Fetches MR details and diff (via GitLab subagent)
  2. Checks SonarQube for new issues (via SonarQube subagent)
  3. Reviews code changes against the checklist:
     - CRITICAL: broken imports, removed functions, changed signatures
     - HIGH: race conditions, null access, error handling
     - MEDIUM: dead code, performance, accessibility
     - LOW: style, naming
  4. Posts structured comments on the MR
  5. Provides overall recommendation: approve / request changes / needs discussion
```

---

## 3. Tools — Automation Beyond Chat

Not everything needs a conversation. Some tasks are better as automated pipelines that run in the background.

### Autobuild — Task Engine

Autobuild executes multi-step pipelines defined as markdown task files. It's the engine behind complex workflows that would be tedious to run manually.

How it works: you define tasks as markdown files in a `.plan/` folder. Each task has a description, acceptance criteria, and dependencies. Autobuild picks them up, executes them in order (respecting dependencies), and reports results.

```
.plan/search-refactor/
├── DESIGN.md                    # Technical design (produced by Planner agent)
└── tasks/
    ├── 001_extract-types.md     # Task 1: extract shared types
    ├── 002_create-composable.md # Task 2: create useSearch composable
    ├── 003_migrate-component.md # Task 3: migrate SearchBar component
    └── 004_add-tests.md         # Task 4: add unit tests
```

Autobuild processes tasks in waves, handles retries on failure, and produces structured logs. It integrates with the agent system — the Planner agent produces the design and task breakdown, autobuild executes it.

### Guidelines Generator

Extracts coding guidelines from real code. Instead of writing style guides from scratch, it analyzes your actual codebase and produces documented conventions based on what the code already does.

It processes every file in the project, extracts patterns (naming, structure, error handling, testing approaches), and produces a guidelines document. The output becomes a skill that agents can reference when writing or reviewing code.

Result from our first run: 174 guidelines extracted from 237 candidates (73% retention rate after quality filtering).

### What Else?

The tooling layer is extensible. Today we have autobuild and the guidelines generator. Tomorrow it could be:

- **Test generator** — analyzes code and generates meaningful test cases
- **Migration assistant** — automates framework upgrades (Vue 2→3, Nuxt 2→4)
- **Compliance reporter** — scheduled reports on code quality across all repos

Each tool follows the same pattern: a Python script that can run standalone or be invoked by an agent. Background execution support (via the `bg` library) means long-running tasks don't block the developer.

---

## 4. The Future — From Assistant to Autonomous

Everything described so far is human-initiated. A developer asks an agent, the agent responds. But many of these workflows don't need a human to start them.

### The Excellence Bot Service

A lightweight server that receives external events and invokes the right agent automatically. The bot has no intelligence — it's a dispatcher. All reasoning lives in the agents.

```
EVENT                              AGENT                    ACTION
─────────────────────────────────────────────────────────────────────
Renovate creates MR          →  Quality Guardian    →  Automated dependency review
Datadog fires alert          →  Observability       →  Automated investigation
SonarQube gate fails         →  Quality Guardian    →  Automated quality analysis
Weekly schedule              →  Knowledge           →  Documentation health audit
Weekly schedule              →  Quality Guardian    →  Dependency scan across repos
Daily schedule               →  Observability       →  Production error summary
```

The bot only notifies humans when something needs attention. A dependency update that passes all checks? Merged automatically. A production error that matches a known pattern? Documented and tracked. A quality gate failure on a critical path? That gets flagged to the team.

### Proactive Notifications

Instead of developers checking dashboards, the system comes to them:

- **Pending work summaries** — weekly email: "You have 3 MRs waiting for review, 2 Jira tickets in progress, 1 stale feature flag"
- **Quality trends** — "Tech debt increased 12% this sprint. Top 3 hotspots: ..."
- **Dependency alerts** — "Critical security update available for package X. MR created automatically"
- **Documentation gaps** — "Service Y has no runbook. Last incident took 45 minutes to resolve"

### The MCP Gateway

Today, each developer configures their own API tokens for Jira, GitLab, SonarQube, etc. It works for a pilot, but it doesn't scale.

The MCP Gateway is a centralized endpoint that handles authentication (SSO), authorization (RBAC), and audit logging for all tool access. Developers authenticate once, agents connect through the gateway, and every action is logged.

```
Developer machine                    MCP Gateway                    APIs
┌──────────────┐                ┌──────────────────┐          ┌──────────┐
│ Agent        │── SSO auth ──▶│ mcp.tui.internal │── API ──▶│ Jira     │
│              │                │                  │          │ GitLab   │
│              │                │ • Authentication │          │ SonarQube│
│              │                │ • Authorization  │          │ Datadog  │
│              │                │ • Audit logging  │          │ Figma    │
│              │                │ • Rate limiting  │          │ ...      │
└──────────────┘                └──────────────────┘          └──────────┘
```

Zero API keys on developer laptops. One endpoint. Full audit trail.

### The Vision

```
Phase 1 (NOW)     Agents on developer machines, direct API connections
                  TUI CLI for distribution
                  Human-initiated workflows

Phase 2 (NEXT)    MCP Gateway for centralized, secure access
                  Full agent coverage (all 9 specialists)
                  Routines and multi-agent workflows

Phase 3 (FUTURE)  Bot Service for autonomous workflows
                  Webhook-triggered agent sessions
                  Proactive notifications
                  Scheduled health checks and reports
```

The progression is natural. Phase 1 proves the value with real developers. Phase 2 makes it secure and scalable. Phase 3 removes the human from the loop for predictable tasks.

---

## What This Means for Teams

For a developer joining a team today:

```
# Day 1
tui cli setup                    # Prerequisites installed
tui ai install agents            # AI agents ready
tui fe create my-first-project   # Compliant project from scratch

# Day 2
"solve DIS-1234"                 # Agent reads ticket, implements, creates MR
"review MR 242"                  # Agent reviews code, posts comments
"scan production errors"         # Agent checks Datadog, reports issues

# Ongoing
"check quality"                  # Quality report in seconds
"find stale feature flags"       # Cleanup plan generated
"create runbook for service X"   # Documentation synthesized from code + incidents
```

No tribal knowledge. No copy-pasting configs. No manual dashboard checking. The standards are encoded in the agents, distributed by the CLI, and enforced automatically.

---

## Summary

| Layer | What | Status |
|-------|------|--------|
| **TUI CLI** | Distribution mechanism — install agents, configs, templates with one command | POC planned |
| **Excellence Agents** | 9 specialist agents + 10 tool subagents + 37 commands + 25 skills | ✅ Built |
| **Tools** | Autobuild, guidelines generator, background execution | ✅ Built |
| **Bot Service** | Autonomous workflows, webhooks, scheduled tasks, notifications | Phase 3 design |

The agents are built. The steering is defined. The commands are written. What comes next is proving it works with real teams and scaling it across the organization.
