# Idea: Excellence MR Agent

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


## Title

AI agent for merge request review, feedback, and approval workflow.

## Context

Direct evolution of Javier's `tui_mr` agent. Reviews MR code changes, provides structured feedback with severity levels, checks for common issues, and can approve or request changes. The Excellence version adds team-configurable review criteria, shared review standards, and cross-team consistency.

### What Exists Today (Proof of Concept)

- `mr 242` command triggers full review
- Fetches MR diff and context from GitLab
- Reviews code changes against conventions
- Provides structured feedback (CRITICAL/HIGH/MEDIUM/LOW)
- Can add inline comments on specific lines
- Generates review summary with recommendation
- Can approve, request changes, or add comments
- Can rebase MR on target branch
- Uses human-like review tone (not robotic)

### What Needs to Change for Org-Wide

- Team-configurable review criteria
- Project-aware conventions (not just Vue/BEM)
- Shared review standards from Excellence guidelines
- Team-specific severity thresholds
- Cross-team review consistency

## Subagents

- `subagent_gitlab` — MR data, diffs, discussions, approvals, comments
- `subagent_sonar` — quality gate status, issues in changed files
- `subagent_jira` — ticket context, acceptance criteria validation

## What It Could Do

### MR Review Workflow
- Fetch MR diff and full context
- **If a plan exists in `.plan/`, verify MR implements what the plan specified** (see `SPEC_DRIVEN_DEV.md`)
- Review against team coding standards
- Check for security issues, performance problems, accessibility
- Validate against Jira ticket acceptance criteria
- Generate structured review with severity levels
- Add inline comments on specific code lines
- Provide review summary with APPROVE/REQUEST CHANGES/BLOCK recommendation

### Team-Configurable Review
- Load review criteria per project/team
- Respect team-specific conventions and patterns
- Adjust severity thresholds per team maturity
- Use team's review comment style
- Focus areas configurable (security-heavy, performance-heavy, etc.)

### Review Quality
- Check MR size (warn if too large, suggest splitting)
- Verify MR description completeness
- Check linked Jira ticket exists and matches
- Validate labels and reviewers assigned
- Check branch naming conventions
- Detect breaking changes in shared libraries

### Post-Review Actions
- Approve MR when all checks pass
- Request changes with clear action items
- Rebase MR on target branch
- Add summary comment with findings
- Update Jira ticket status based on review outcome

### Cross-Team Intelligence
- Consistent review standards across teams
- Share common patterns and anti-patterns
- Track review quality metrics (time to review, issues found)
- Identify teams that need review support

## Commands

| Command | Trigger | Description |
|---------|---------|-------------|
| `emr_review` | "review [MR-ID]" | Full MR review with structured feedback and severity levels |
| `emr_approve` | "approve [MR-ID]" | Quick approve with lightweight checks |
| `emr_rebase` | "rebase [MR-ID]" | Rebase MR on target branch, report conflicts |
