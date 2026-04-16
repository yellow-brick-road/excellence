# Idea: Excellence Dev Agent

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


## Title

AI agent for Jira ticket implementation — from ticket to merge request in one command.

## Context

Direct evolution of Javier's `tui_dev` agent — the most productive agent in the personal setup. Takes a Jira ticket, reads requirements, creates a branch, implements changes, runs tests, commits, and creates an MR. The Excellence version adds team-configurable conventions, project awareness, and shared coding standards.

### What Exists Today (Proof of Concept)

- `solve DIS-1234` command triggers full workflow
- Reads Jira ticket (title, description, acceptance criteria)
- Creates feature branch following naming conventions
- Implements changes following Vue/Nuxt conventions
- Runs ESLint, Stylelint, TypeScript checks
- Runs unit tests (Vitest)
- Commits with conventional commit format
- Creates MR with description linked to ticket
- Hardcoded to TUI B2C frontend conventions

### What Needs to Change for Org-Wide

- Team-configurable coding conventions (not just Vue/BEM)
- Project-aware context (which repo, which framework, which standards)
- Shared coding standards loaded from Excellence guidelines
- Team-specific templates for MR descriptions
- Support for different tech stacks across teams

## Subagents

- `subagent_jira` — read ticket details, update status, add comments
- `subagent_gitlab` — branches, MRs, pipelines, code context
- `subagent_sonar` — pre-commit quality check, rule awareness

## What It Could Do

### Ticket-to-MR Workflow
- Read Jira ticket and extract requirements
- **Analyze scope and propose execution plan** (see `SPEC_DRIVEN_DEV.md`)
- **Wait for user approval before writing code**
- Create feature branch with correct naming convention
- Execute plan step by step following team conventions
- Run linting, type checking, and tests
- **Verify work against the plan** — all steps completed, ACs met
- Pre-commit code review (self-review against standards)
- Commit with conventional commit format
- Create MR with auto-populated description
- Link MR to Jira ticket, transition ticket status

### Team-Configurable Conventions
- Load coding standards per project/team (from Excellence guidelines or team config)
- Respect team-specific ESLint/Stylelint configs
- Follow team's component patterns and file structure
- Use team's commit message format
- Apply team's MR description template

### Quality Gates
- Run SonarQube rules locally before committing
- Check coverage thresholds before creating MR
- Validate against team's quality standards
- Flag potential issues before human review

### Context Awareness
- Understand project structure (monorepo, packages, layers)
- Know which files to modify based on ticket scope
- Respect CODEOWNERS and file ownership
- Detect cross-repo impact for shared libraries

## Commands

| Command | Trigger | Description |
|---------|---------|-------------|
| `edev_solve` | "solve [TICKET-ID]" | Full ticket-to-MR: read ticket, branch, implement, test, commit, MR |
| `edev_implement` | "implement [description]" | Ad-hoc implementation without Jira ticket |
| `edev_continue` | "continue", "resume" | Resume interrupted solve or implement workflow |
