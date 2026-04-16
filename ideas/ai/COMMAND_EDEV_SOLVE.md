# Command: $solve

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


> Command name: `edev_solve`
> Description: Full ticket-to-MR workflow. Read Jira ticket, create branch, implement, test, commit, create MR.
> Agent: Excellence Dev

## Trigger

`solve [TICKET-ID]` or "solve DIS-1234"

## Workflow

1. `subagent_jira` → read ticket (title, description, acceptance criteria)
2. Analyze scope: files affected, complexity, new logic vs modification
3. **Propose execution plan** — depth based on scope (see `SPEC_DRIVEN_DEV.md`). Write to `.plan/{ticket-id}/PLAN.md`
4. **Wait for user approval** — user can approve, modify, escalate, or skip plan
5. `subagent_gitlab` → create feature branch following steering conventions
6. Execute plan step by step following steering tech stack and conventions
7. Run linting (ESLint, Stylelint) and type checking (TypeScript)
8. Run unit tests (Vitest)
9. `subagent_sonar` → pre-commit quality check
10. **Verify against plan** — all steps completed, acceptance criteria met
11. Self-review against coding standards
12. Commit with conventional commit format from steering
13. `subagent_gitlab` → create MR with description linked to ticket
14. `subagent_jira` → transition ticket status

## Output

- Feature branch created
- Changes implemented and tested
- MR created with:
  - Description linked to Jira ticket
  - Acceptance criteria checklist
  - Summary of changes
- Ticket status updated

## Phase

Phase 2 (ships with Excellence Dev)
