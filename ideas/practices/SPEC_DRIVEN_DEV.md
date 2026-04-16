# Practice: Spec-Driven Development

## Guild Position

> Agents plan before they execute. Every non-trivial task produces a spec that the user reviews and approves before the agent touches code. The spec is the contract between human intent and agent execution.

## The Problem

- Agents jump straight to implementation — if they misunderstand the task, you find out after the code is written
- No visibility into what the agent plans to do until it's done
- When something goes wrong, there's no audit trail of what was intended vs what happened
- "Continue" and "resume" are fragile — the agent reconstructs context from git state, not from a plan
- No checkpoint between "I understood the task" and "I changed your code"

## The Principle

**Spec first, execute second.**

When an agent receives a non-trivial task, it analyzes the scope, proposes a plan, and waits for human approval before writing any code. The plan lives in `.plan/` as a persistent artifact — it's the source of truth for execution, verification, and resumption.

This is not a special mode the user activates. It's how agents work by default.

## The Flow

```
1. ANALYZE     Agent reads ticket/requirement, determines scope
2. DECIDE      Trivial → execute directly. Non-trivial → propose plan
3. PLAN        Agent writes plan to .plan/, presents to user
4. APPROVE     User reviews. Accepts, modifies, or rejects
5. EXECUTE     Agent executes step by step against the plan
6. VERIFY      Agent reviews work against the plan
7. DELIVER     Commit, MR, update Jira — standard workflow
```

The user can override at step 2:
- "This is trivial, just do it" → agent skips to execute
- "I want a full design doc first" → agent escalates plan depth

## Plan Levels (Internal)

The agent uses these levels internally to decide plan depth. The user never sees level numbers — they see the plan at whatever depth the agent chose, and can ask for more or less detail.

| Level | When | What the agent produces |
|-------|------|------------------------|
| 0 — Direct | Trivial: rename, typo, one-liner, config change | Nothing in `.plan/`. Executes immediately |
| 1 — Light | Clear task, few files, well-scoped | Short PLAN.md: bullet list of what it will do |
| 2 — Full | Complex feature, new logic, multiple files | Detailed PLAN.md: files, changes per file, acceptance criteria, risks |
| 3 — Design | Architecture, large refactor, technical decisions | **Delegate to Excellence Planner agent** → DESIGN.md + autobuild-compatible tasks/ |

### How the agent presents it

The agent does NOT say "I propose a Level 2 plan." It explains what it's going to do and why:

```
"I've read DIS-1234. It involves 4 files with new validation logic
 in the composable.

 Before I start, here's my plan — what I'll change, in what order,
 and what to verify. You can review before I touch any code.

 Plan:
 A. Modify useBooking.ts — add date validation logic
 B. Update SearchButton.vue — add disabled prop
 C. Add tests for useBooking (3 cases: valid, past date, empty)
 D. Add translation key 'error.invalidDate'

 Approve, want me to adjust something, or prefer I go straight
 to coding without a plan?"
```

### Level selection heuristics

The agent considers:
- Number of files affected (1-2 → light, 3+ → full)
- New logic vs modification of existing (new → higher level)
- Ambiguity in requirements (unclear → higher level)
- Cross-cutting changes (multiple layers → higher level)
- User's history (if user often overrides → adapt)

These are guidelines, not rules. The agent uses judgment.

## Output Location

Plans live in `.plan/`, git-ignored. Same folder used by `@plan` and `@design` prompts.

```
.plan/
└── {topic}/              # e.g., DIS-1234, search-refactor
    ├── PLAN.md           # Execution plan (levels 1-3)
    └── DESIGN.md         # Technical design (level 3 only)
```

Topic naming:
- Jira ticket: `DIS-1234`
- Ad-hoc task: `kebab-case-description`

## Approval

**Interactive (human-invoked agents):** Always. The agent presents the plan and waits for explicit approval before executing. No exceptions.

**Autonomous (Bot Service, Phase 3):** A specialized reviewer agent evaluates the plan instead of a human. If the reviewer approves, execution proceeds. If rejected, the bot notifies Teams and a human intervenes.

```
Interactive:
  Agent → plan → HUMAN approves → execute

Autonomous:
  Agent → plan → REVIEWER AGENT approves → execute
                → rejects → notify Teams → human intervenes
```

## Verification

After execution, the agent verifies against the plan:
- Each planned step was completed
- Linting, type checking, and tests pass
- Acceptance criteria from the plan are met
- No unplanned changes were introduced

If verification fails, the agent reports what's missing and proposes next steps — it does not silently retry.

## Iteration

Plans can be wrong or incomplete. When that happens:
- The user can edit the plan and ask the agent to re-execute
- The agent can propose amendments to the plan mid-execution
- The agent explains what changed and why before continuing

There is no formal versioning of plans. `.plan/` is ephemeral — it exists for the duration of the task.

## Relationship to Existing Concepts

### vs Jira Tickets

The ticket is input. The plan is the agent's technical interpretation of that input. They are separate artifacts:
- Ticket: what needs to happen (product language)
- Plan: how the agent will do it (technical language)

The agent does not modify the ticket. The plan lives in `.plan/`, not in Jira.

### vs Plan Mode (@plan, @design)

Spec-Driven Dev extends Plan Mode. The shared steering (`STEERING_PLAN_MODE.md`) gives all executing agents planning capability for levels 0-2. For level 3, agents delegate to the Excellence Planner agent, which consults specialists and produces autobuild-compatible output.

- Levels 0-2: agent plans and executes itself
- Level 3: agent delegates to Planner → user approves → `autobuild .plan/{topic}/tasks/ --bg`

### vs Autobuild

Autobuild reads `.md` task files and executes them through kiro-cli. The Excellence Planner produces these task files. The connection:
- Planner produces plan in `.plan/` with individual task files + autobuild.json
- User approves the plan
- `autobuild .plan/{topic}/tasks/ --bg` executes the plan in background
- User checks progress with `autobuild --status`
- Autobuild's review modes (none/final/extended/full) validate execution quality

### vs Testing Philosophy

The plan's acceptance criteria become test targets. "Does every AC have a test?" — the plan makes ACs explicit before implementation starts, giving the agent clear test targets.

## What This Changes

### Excellence Dev — solve workflow

```
Before:
  solve DIS-1234 → read ticket → implement → commit → MR

After:
  solve DIS-1234 → read ticket → propose plan → approve → execute → verify → commit → MR
```

### Excellence Dev — implement workflow

```
Before:
  implement X → parse description → implement → present changes

After:
  implement X → parse description → propose plan → approve → execute → verify → present changes
```

### Excellence Dev — continue workflow

```
Before:
  continue → check git state → reconstruct context → resume

After:
  continue → read plan from .plan/ → check progress → resume from where it stopped
```

The plan is the state. No more reconstructing context from git.

## Open Questions

- [ ] Should the plan include estimated effort per step? (helps user gauge scope)
- [ ] Should the agent track plan completion progress? (step 2/4 done)
- [ ] How does this interact with autobuild's review modes? (plan approval = autobuild's plan review?)
- [ ] Should `.plan/` persist after task completion for audit, or clean up?
- [ ] Should the reviewer agent (Bot Service) have its own steering, or reuse Excellence MR's review logic?
- [ ] Framework-specific plan templates, or always freeform?
