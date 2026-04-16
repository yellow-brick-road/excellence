# Practice: Plan Mode

## Guild Position

> Design before you implement. Every non-trivial task should produce a technical design document and a task breakdown before writing code. The agent enforces this by entering a structured "plan mode" that outputs artifacts to an ephemeral workspace.

## The Problem

- Developers jump straight to code without thinking through the design
- Design decisions live in Slack threads, heads, or nowhere
- Task breakdowns are vague Jira titles with no technical detail
- When the agent helps plan something (like we did for MCP Gateway), the process is ad-hoc — no consistent structure, no reusable pattern
- Planning artifacts either pollute the repo or get lost

## The Principle

**Structured planning as a first-class workflow.**

When someone says "design X" or "plan Y", the agent doesn't improvise. It follows a defined process that always produces the same types of artifacts, in the same structure, in a predictable location.

> **Relationship to Spec-Driven Dev:** Plan Mode is the explicit, human-triggered version of the planning workflow. Spec-Driven Dev (`SPEC_DRIVEN_DEV.md`) extends this so agents enter plan mode automatically for non-trivial tasks. Plan Mode's `@plan` and `@design` prompts map to Spec-Driven's level 3 (design + plan). The output location (`.plan/`), artifact format, and approval flow are shared.

## The Pattern

Plan Mode is implemented as a two-tier system:

1. **Shared steering** (`STEERING_PLAN_MODE.md`) — loaded by all executing agents. Defines planning levels 0-2: when to plan, how to present, approval flow, output format.
2. **Excellence Planner agent** (`AGENT_EXCELLENCE_PLANNER.md`) — dedicated agent for level 3 deep planning. Consults specialists, produces DESIGN.md + autobuild-compatible task files, and can create Jira tickets from plans.

### How it works

- Levels 0-2: the agent plans itself using the shared steering. Light plans in chat, detailed plans in `.plan/`.
- Level 3: the agent detects cross-domain/architectural scope and delegates to the Planner agent.
- After approval: levels 0-2 execute inline. Level 3 launches via `autobuild .plan/{topic}/tasks/ --bg`.

### Output Structure

```
.plan/                              # git-ignored
└── {topic}/                        # e.g., mcp-gateway, DIS-1234
    ├── PLAN.md                     # Levels 1-2: execution plan
    ├── DESIGN.md                   # Level 3: technical design (Planner)
    └── tasks/                      # Level 3: autobuild-compatible
        ├── 00_setup-infra.md
        ├── 01_core-logic.md
        └── autobuild.json
```

### Design Document Sections

| Section | Purpose |
|---|---|
| **Title** | What's being designed |
| **Context** | Why this is needed, what problem it solves |
| **Constraints** | Non-negotiables (tech stack, timeline, dependencies, team size) |
| **Proposal** | The actual design — architecture, data flow, API contracts, whatever applies |
| **Alternatives Considered** | What else was evaluated and why it was rejected |
| **Risks & Open Questions** | What could go wrong, what's still unclear |
| **Decision** | Go / No-go / Needs more info |

### Task Breakdown Structure

Each task includes:

| Field | Purpose |
|---|---|
| **ID** | Sequential (T-001, T-002...) |
| **Title** | What to build |
| **Depends on** | Which tasks must complete first |
| **Description** | Technical detail — what to implement, where, how |
| **Acceptance criteria** | How to verify it's done |
| **Estimated effort** | S/M/L/XL |

## Prompts

Plan Mode is no longer triggered by standalone prompts. Instead:

- **Automatic**: all executing agents enter plan mode via shared steering (`STEERING_PLAN_MODE.md`)
- **Routing**: Excellence Default detects planning intent and routes to the Planner agent
- **Direct**: users can invoke the Planner agent directly for standalone design work

The `@plan` and `@design` triggers become routing rules in Default's Agent Guard, not standalone prompts.

## Agent Behavior

When plan mode activates:
- Agent switches to structured output mode (no casual chat)
- Asks scope questions upfront if needed
- Creates `.plan/{topic}/` folder
- Writes DESIGN.md following the template
- Writes TASKS.md with ordered, dependency-aware tasks
- Summarizes what was produced at the end

What it does NOT do:
- Implement anything — plan mode is thinking, not doing
- Commit or push — output is ephemeral
- Replace human judgment — the design is a proposal, not a decision

## Connection to Existing Architecture

- **Shared steering** (`STEERING_PLAN_MODE.md`) — loaded by all executing agents, defines levels 0-2
- **Excellence Planner** — dedicated agent for level 3, consults specialists, creates Jira tickets from plans
- **Excellence Dev** — delegates level 3 to Planner, executes levels 0-2 itself
- **Excellence Default** — routes planning intent to Planner via Agent Guard
- **Autobuild** — consumes Planner's task output directly (zero conversion)
- **TUI CLI** could add `tui ai plan` as a convenience command

## What This Formalizes

The manual pattern we've been using:
- MCP Gateway → ARCHITECTURE.md + 8 TASK_*.md
- Testing Philosophy → TESTING_PHILOSOPHY.md
- Confluence Restructuring → CONFLUENCE_RESTRUCTURING.md

All of these followed the same implicit process: understand → research → design → break down. Plan Mode makes it explicit and repeatable.

Spec-Driven Dev (`SPEC_DRIVEN_DEV.md`) takes this further: agents enter this process automatically for any non-trivial task, not just when the user says `@plan`. Plan Mode becomes the "level 3" of a broader spec-driven execution model.

## Open Questions

- [ ] Should `.plan/` be the folder name, or something else? (`.design/`, `.workspace/`, `.scratch/`)
- [ ] Should the agent offer to promote artifacts from `.plan/` to the actual repo when the design is approved?
- [ ] One TASKS.md or individual TASK_NNN.md files per task?
- [ ] Should plan mode support iterating on an existing plan? ("refine the MCP Gateway plan")
- [ ] How does this interact with Jira? Auto-create tickets from tasks, or keep it separate?
- [ ] Should there be a `@plan-review` prompt that reviews an existing plan for completeness?
