---
name: dev_solve
description: "Full task-to-MR workflow. Use when: user says 'solve [TICKET-ID]' or 'solve [description]'."
---

# Command: $dev_solve

Full task-to-MR: read requirements, analyze, plan, implement, test, commit, MR.

## Process

### 1. Read Requirements

- If ticket ID provided: gather full ticket context via tuimm_subagent_jira following the jira-context-gathering skill — parent, links, comments, attachments. If the ticket has sub-tasks or linked issues, fetch their full details too (second subagent call). Present a summary of the parent AND all sub-tasks/links before proceeding
- If description/markdown/prompt: read and extract requirements
- If ambiguous: ask for clarification

### 2. Analyze

- Search codebase (grep, glob, read) to understand current state
- Check loaded skills and steering for relevant conventions
- Search the web if the task involves libraries, APIs, or patterns you're not sure about
- Understand project structure (monorepo, packages, layers)

### 3. Propose Plan

Present a clear plan:
- What files will be created/modified
- What the changes will do
- What tests are needed
- Any risks or open questions

**Wait for user confirmation. NEVER proceed without approval.**

### 4. Create Branch

Clone or reuse workspace at `~/.kiro/temp/dev/{TICKET-ID}-{repo_name}/` (see GIT.md § Workspace Conventions):
- If dir exists: `cd {dir} && git fetch --all --prune && git checkout main && git pull` (or master)
- If not: `mkdir -p ~/.kiro/temp/dev && git clone git@ssh.source.tui:{project_path}.git ~/.kiro/temp/dev/{TICKET-ID}-{repo_name}`

Then create the branch:
```
git checkout -b feature/{TICKET-ID}-{short-description}
```

Use hyphens, NEVER underscores in branch names.

### 5. Implement

- Apply changes following project conventions and loaded skills
- Run linting and type checks after changes

### 6. Test

- Run existing tests to verify nothing broke
- Add tests if required by the plan

### 7. Code Review

- Delegate to tuimm_subagent_code_reviewer for pre-commit review
- Address any findings
- If tuimm_subagent_code_reviewer is not available, do a self-review: check for obvious issues, unused imports, type errors

### 8. Commit

- Via tuimm_subagent_gitlab following commit-conventions skill
- Show commit message to user, wait for confirmation

### 9. Push & Create MR

- Remind user: "Push is yours — sync with master first"
- Wait for user to confirm push is done
- Create MR via tuimm_subagent_gitlab with auto-populated description
- Link to Jira ticket if applicable

### 10. Post-MR

- Ask user: "Want me to move {TICKET} to In Review?"
- Set AI usage fields on Jira ticket (see AI_USAGE_TRACKING steering)

### 11. Output

Present results using the dev-solve template. Follow it EXACTLY — LAST STEP, nothing after this.
