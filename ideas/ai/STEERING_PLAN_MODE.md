# Steering: Plan Mode

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


Shared planning behavior for all executing agents. Loaded by every Tier 1 agent that performs actions (not analysis-only agents like Excellence MR).

## Core Rule

> Plan before you execute. Every non-trivial task produces a plan that the user reviews before the agent writes code.

## Planning Levels

| Level | Scope | Agent plans itself? | Output |
|-------|-------|--------------------:|--------|
| 0 — Direct | Trivial (rename, typo, config) | Yes, no plan needed | Execute immediately |
| 1 — Light | Clear, few files | Yes | Bullet list in chat: "I'll do A, B, C. Approve?" |
| 2 — Full | Complex, multiple files, single domain | Yes | `.plan/{topic}/PLAN.md` with files, changes, ACs |
| 3 — Design | Architecture, cross-cutting, multi-domain | **No — delegate to Planner agent** | `.plan/{topic}/DESIGN.md` + `tasks/*.md` |

## Level Selection Heuristics

Consider:
- Files affected: 1-2 → light, 3-5 → full, 6+ → consider design
- New logic vs modification: new architecture → higher level
- Ambiguity: unclear requirements → higher level
- Cross-cutting: multiple layers/domains → design level
- User history: if user often overrides level, adapt

These are guidelines, not rules. Use judgment.

## How to Present a Plan

Do NOT say "I propose a Level 2 plan." Explain what you'll do:

```
I've read DIS-1234. It involves 4 files with new validation logic.

Before I start, here's my plan:
A. Modify useBooking.ts — add date validation
B. Update SearchButton.vue — add disabled state
C. Add 3 test cases for useBooking
D. Add translation key 'error.invalidDate'

Approve? Want changes? Or skip the plan and I'll just code it?
```

## Approval

- **Always wait for approval** before executing levels 1-3
- User can say "just do it" → skip to execute (override to level 0)
- User can say "I want more detail" → escalate level
- User can modify the plan → agent adjusts and re-presents

## Output Location

```
.plan/                              # git-ignored
└── {topic}/                        # DIS-1234, search-refactor, etc.
    ├── PLAN.md                     # Levels 1-2: execution plan
    ├── DESIGN.md                   # Level 3: technical design (Planner produces this)
    └── tasks/                      # Level 3: autobuild-compatible task files
        ├── 00_setup.md
        ├── 01_core.md
        └── autobuild.json
```

Level 1: plan in chat only (no files).
Level 2: PLAN.md in `.plan/`.
Level 3: delegate to Excellence Planner agent → DESIGN.md + tasks/.

## Escalation to Planner

When an agent detects level 3 scope, it delegates to the Excellence Planner agent:

```
"This looks like it needs architectural decisions and touches multiple domains.
 I'm going to hand this to the Planner for a proper design + task breakdown.
 You'll review the plan before anything gets built."
```

The Planner consults specialists (Quality Guardian, Design System, Knowledge, etc.) and produces autobuild-compatible output.

## After Approval

- Levels 0-2: agent executes the plan itself
- Level 3: user launches `autobuild .plan/{topic}/tasks/ --bg` and checks periodically with `--status`

## TODO Convention

When executing a plan, if you cannot fully complete a step:
- Leave a `TODO(autobuild): <reason>` comment in the code
- Never skip or silently omit functionality
- Report incomplete steps in the verification phase

## Resume

If execution is interrupted:
- Read plan from `.plan/` — the plan is the state
- Check which steps are complete (git diff, file existence)
- Resume from the next incomplete step
- No need to reconstruct context from git — the plan has it
