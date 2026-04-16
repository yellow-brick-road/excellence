---
name: planner_decompose
description: "Break design into autobuild-compatible task files. Use when: user says 'decompose', 'break into tasks', or after $planner_design is approved."
---

# Command: $planner_decompose

Break an approved DESIGN.md into autobuild-compatible task files in `.plan/{topic}/tasks/`.

## Inputs

- **topic**: required. Must match an existing `.plan/{topic}/DESIGN.md`.

## Process

### 1. Read Design

Read `.plan/{topic}/DESIGN.md` — extract:
- Proposal (what to build)
- Constraints (what limits apply)
- Dependencies (what must exist first)

### 2. Identify Tasks

Break the proposal into discrete, independently executable tasks:
- Each task should be completable in one agent session
- Tasks should have clear acceptance criteria
- Identify dependencies between tasks (what must finish before what)
- Identify gate tasks (must pass before continuing)

### 3. Generate Task Files

Create `.plan/{topic}/tasks/NN_short-name.md` for each task:

```markdown
---
type: {component|composable|page|test|config|infra|refactor}
agent: tuimm_dev
verify: "{command to verify task is done}"
gate: {true|false}
deps: ["{NN}"]
estimate: {S|M|L|XL}
---

# {Task title}

{Clear description of what to do.}

## Context
{Why this task exists, reference to DESIGN.md section.}

## Acceptance Criteria
- [ ] {criterion}
- [ ] {criterion}

## Files
- {file to create/modify}: {what to do}

## Notes
- {any gotchas or references}
```

### 4. Generate autobuild.json

Create `.plan/{topic}/autobuild.json`:

```json
{
  "agent": "tuimm_dev",
  "review": "final",
  "agent_map": {
    "default": "tuimm_dev",
    "rules": []
  },
  "health": {
    "builtin": true,
    "checks": []
  }
}
```

### 5. Output Summary

Present results using the planner-decompose template. Follow it EXACTLY.

### 6. Present to User

Show task list and dependency graph for review.

**Wait for user approval before finalizing.**

User can:
- Approve → files are ready for autobuild
- Adjust → add/remove/reorder tasks
- Re-plan → go back to $planner_design
