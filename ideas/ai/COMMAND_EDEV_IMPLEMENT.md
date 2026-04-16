# Command: $implement

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


> Command name: `edev_implement`
> Description: Ad-hoc implementation without a Jira ticket. Describe what you need, agent implements following conventions.
> Agent: Excellence Dev

## Trigger

`implement [description]` or "implement this", "code this"

## Workflow

1. Parse user description into requirements
2. Analyze scope: files affected, complexity
3. **Propose execution plan** if non-trivial (see `SPEC_DRIVEN_DEV.md`). Write to `.plan/{topic}/PLAN.md`
4. **Wait for user approval** — user can approve, modify, or skip plan
5. Execute plan step by step following steering conventions
6. Run linting and type checking
7. Run unit tests
8. **Verify against plan** — all steps completed
9. Self-review against coding standards
10. Present changes for user review

## Output

- Changes implemented following conventions
- Linting and tests passing
- Summary of what was changed and why

## Phase

Phase 2 (ships with Excellence Dev)
