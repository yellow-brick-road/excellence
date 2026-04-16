---
name: planner_analyze
description: "Analyze a requirement and determine planning level. Use when: user says 'analyze [requirement]' or an agent escalates a complex task."
---

# Command: $planner_analyze

Analyze a requirement — scan codebase, assess complexity, determine planning level, recommend handler.

## Inputs

- **requirement**: Jira ticket ID, description, or topic. If ticket ID, fetch via tuimm_subagent_jira.

## Process

### 1. Understand the Requirement

- If ticket ID: delegate to tuimm_subagent_jira — gather full context following the jira-context-gathering skill (parent, links, comments, attachments, not just title and ACs). If the ticket has sub-tasks or linked issues, fetch their full details too (second subagent call)
- If description: parse and extract scope, goals, constraints
- Ask clarifying questions if ambiguous

### 2. Scan Codebase

- Search for affected files and modules (grep, glob, read)
- Estimate scope: how many files, how many modules, cross-cutting?
- Check for existing patterns that apply
- Identify dependencies and downstream impact

### 3. Consult Quality Context

Delegate to tuimm_subagent_sonar (read-only):
- Known issues in affected areas
- Coverage of affected files
- Tech debt in affected modules

### 4. Determine Planning Level

| Level | Criteria | Handler |
|-------|----------|---------|
| 0 — Direct | Trivial: rename, typo, config change. 1-2 files | tuimm_dev (no plan needed) |
| 1 — Light | Clear task, few files, well-scoped. 3-5 files | tuimm_dev (inline plan) |
| 2 — Full | Complex feature, multiple files, clear domain. 6-12 files | tuimm_dev (plan + confirm) |
| 3 — Design | Architecture, cross-cutting, multi-domain, ambiguous. 12+ files or new patterns | tuimm_planner (full design) |

### 5. Output

Present results using the planner-analyze template. Follow it EXACTLY — LAST STEP, nothing after this.

### 6. Next Step

- Level 0-2: "Recommend delegating to tuimm_dev. Proceed?"
- Level 3: "This needs a full design. Want me to run $planner_design?"
