# Idea: Excellence Planner Agent

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


## Title

Dedicated planning agent for cross-domain analysis, technical design, and autobuild-compatible task generation.

## Context

Planning and execution are fundamentally different activities. Mixing them in the same agent (e.g., Excellence Dev plans AND codes) leads to agents jumping to implementation before fully understanding the problem. The Planner agent enforces "think first" architecturally — it CAN'T execute, it can only analyze, consult, and produce plans.

### Two-Tier Planning Model

All executing agents (Dev, Default, Quality Guardian, Design System, DevEx) share a `STEERING_PLAN_MODE.md` that gives them lightweight planning capability (levels 0-2). The Planner agent handles deep, cross-domain planning (level 3) that requires consulting multiple specialists.

| Level | Who plans | When |
|-------|-----------|------|
| 0 — Direct | Agent itself | Trivial: rename, typo, config change |
| 1 — Light | Agent itself | Clear task, few files, well-scoped |
| 2 — Full | Agent itself | Complex feature, multiple files, clear domain |
| 3 — Design | **Planner agent** | Architecture, cross-cutting, multi-domain, ambiguous scope |

### When Planner Is Invoked

- **User invokes directly**: "plan the search refactor", "design the MCP Gateway"
- **Default routes to Planner**: Agent Guard detects planning intent
- **Dev delegates**: non-trivial ticket detected (12+ files, new architecture, cross-cutting)
- **Any agent escalates**: detects level 3 scope, delegates to Planner

## Permissions

**Read-only.** The Planner never writes code, never commits, never creates MRs, never modifies Jira.

| Can do | Cannot do |
|--------|-----------|
| Read codebase (fs_read, glob, grep) | Write code (fs_write) |
| Consult other agents (query only) | Execute action commands |
| Write to `.plan/` folder only | Commit, push, create branches |
| Search web for prior art | Modify Jira tickets |
| Read Confluence, Figma, SonarQube data | Create/update Confluence pages |

## Consultation Pattern

The Planner consults Tier 1 specialists for domain-specific input. It asks questions and gathers context, but can also create/edit Jira tickets to materialize plans into actionable work items.

| Specialist | What Planner asks |
|-----------|-------------------|
| Quality Guardian | Quality constraints, coverage requirements, known debt in affected areas |
| Observability | Monitoring needs, existing alerts, error patterns in affected services |
| Design System | Component implications, Figma alignment, design token impact |
| Knowledge | Existing documentation, runbooks, prior decisions on this topic |
| DevEx | Feature flag needs, i18n impact, content model changes |

## Output

All output goes to `.plan/{topic}/`, git-ignored. Autobuild-compatible by default.

```
.plan/{topic}/
  DESIGN.md                    # Technical design document (level 3)
  tasks/
    00_setup-infra.md          # Individual task files, autobuild-compatible
    01_core-logic.md
    02_gate-tests.md           # gate: true
    03_integration.md
  autobuild.json               # Agent map, review mode, health checks
```

### DESIGN.md sections

| Section | Purpose |
|---------|---------|
| Context | Why this is needed, what problem it solves |
| Constraints | Non-negotiables (tech stack, timeline, dependencies) |
| Proposal | Architecture, data flow, API contracts |
| Alternatives Considered | What else was evaluated and why rejected |
| Risks & Open Questions | What could go wrong, what's unclear |
| Specialist Input | Summary of what each consulted agent contributed |

### Task file format

Each task file is a standalone markdown file with optional frontmatter:

```markdown
---
type: component
agent: tui_frontend
verify: "npm run test -- --filter useBooking"
gate: false
deps: ["00"]
estimate: M
---

# Implement booking validation

Add date validation logic to useBooking composable...

## Acceptance Criteria

- [ ] Past dates are rejected with error message
- [ ] Empty dates show validation hint
- [ ] Existing tests still pass
```

### Generated autobuild.json

The Planner also produces the execution config:

```json
{
  "agent": "excellence_dev",
  "review": "final",
  "agent_map": {
    "default": "excellence_dev",
    "rules": [
      { "match": { "type": "test" }, "agent": "excellence_dev" },
      { "match": { "type": "infra" }, "agent": "excellence_dev" }
    ]
  },
  "health": {
    "builtin": true,
    "checks": [
      { "name": "vpn", "cmd": "ping -c1 -W2 source.tui", "required": true }
    ]
  }
}
```

## Subagents

Read-only access to all Tier 2 subagents via MCP Gateway:

- `subagent_jira` — read ticket details, search related issues
- `subagent_gitlab` — read codebase, check existing branches/MRs
- `subagent_sonar` — read quality metrics, known issues in affected areas
- `subagent_confluence` — read existing docs, architecture decisions
- `subagent_figma` — read design context, component specs

## Commands

| Command | Type | Description |
|---------|------|-------------|
| `command_planner_analyze` | command | Analyze a requirement and determine planning level (0-3) |
| `command_planner_design` | command | Produce DESIGN.md with specialist consultation |
| `command_planner_decompose` | command | Break design into autobuild-compatible task files |

## Relationship to Other Agents

| Agent | Relationship |
|-------|-------------|
| Excellence Default | Routes planning intent to Planner via Agent Guard |
| Excellence Dev | Delegates level 3 planning to Planner; executes Planner's output |
| Quality Guardian | Consulted for quality constraints; can delegate batch fix planning |
| Design System | Consulted for component impact; can delegate alignment planning |
| All executing agents | Share `STEERING_PLAN_MODE.md` for levels 0-2; escalate to Planner for level 3 |

## Relationship to Tooling

| Tool | Connection |
|------|-----------|
| Autobuild | Planner's task output is autobuild's input. Zero conversion needed |
| bg | User launches `autobuild .plan/{topic}/tasks/ --bg` after approving the plan |
| logd | Planner logs consultation results and planning decisions |

## What This Changes

### Before
```
User: "solve DIS-5678" (complex ticket)
  → Dev reads ticket → Dev plans → Dev implements → Dev commits
  (planning and execution mixed, planning quality varies)
```

### After
```
User: "solve DIS-5678" (complex ticket)
  → Dev reads ticket → detects level 3 → delegates to Planner
  → Planner consults QG, Design System, Knowledge
  → Planner produces .plan/DIS-5678/ with DESIGN.md + tasks/
  → User approves
  → autobuild .plan/DIS-5678/tasks/ --bg
  → User checks: autobuild --status
```

## Open Questions

- [ ] Should the Planner track plan versions? (v1, v2 after user feedback)
- [ ] Should `.plan/` persist after execution for audit, or clean up?
- [ ] Can the Planner invoke other Tier 1 agents directly, or only through Default?
- [ ] Should there be a `skill_planner_review` that reviews an existing plan?
- [ ] How does the Planner handle iterative refinement? ("adjust the plan, remove task 03")
