# Command: $review

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


> Command name: `emr_review`
> Description: Full MR review — fetch diff, review against conventions, structured feedback with severity, inline comments, recommendation.
> Agent: Excellence MR

## Trigger

`review [MR-ID]` or "review mr 242", "review this MR"

## Workflow

1. `subagent_gitlab` → fetch MR diff and context
2. `subagent_jira` → get linked ticket for acceptance criteria
3. Review against steering conventions (tech stack, naming, patterns)
4. Check for security issues, performance problems, accessibility
5. Validate against Jira acceptance criteria
6. `subagent_sonar` → check quality gate for changed files
7. Classify findings by severity (CRITICAL/HIGH/MEDIUM/LOW)
8. `subagent_gitlab` → add inline comments on specific code lines
9. Generate review summary with APPROVE/REQUEST CHANGES/BLOCK recommendation
10. `subagent_gitlab` → post review summary

## Output

- Inline comments on specific lines
- Review summary with:
  - Findings by severity
  - Recommendation (APPROVE/REQUEST CHANGES/BLOCK)
  - Quality gate status
  - Acceptance criteria validation

## Phase

Phase 2 (ships with Excellence MR)
