---
name: kn_onboarding
description: "Generate personalized onboarding guide. Use when: user says 'onboarding [team]', 'new joiner guide', or 'onboarding guide'."
---

# Command: $kn_onboarding

Generate a personalized onboarding guide for a new team member — repos, tools, docs, first tasks.

## Inputs

- **team**: required. Team name or project area.
- **role**: optional. Frontend, backend, QA, etc. Defaults to frontend.

## Process

### 1. Existing Onboarding Docs

Delegate to tuimm_subagent_confluence:
- Search for existing onboarding docs for the team
- Collect any setup guides, conventions, or team-specific docs

### 2. Team Repos

Delegate to tuimm_subagent_gitlab:
- List team's repos with descriptions
- Identify main repo(s) vs supporting repos
- Check each repo for README quality

### 3. Team Context

Delegate to tuimm_subagent_jira:
- Get team's active project and board
- Current sprint overview (to suggest first tasks)
- Team members (for contacts)

### 4. Content Models (if applicable)

Delegate to tuimm_subagent_contentful:
- List content models the team works with
- Key content types and their purpose

### 5. Compile Guide

```markdown
# Onboarding Guide — {team}

## Team Overview
What the team does, key contacts, communication channels.

## Repositories
| Repo | Purpose | Tech Stack | README |
|------|---------|-----------|--------|

## Development Setup
Step-by-step to get the main repo running locally.
Prerequisites, env vars, commands.

## Tools & Access
| Tool | Purpose | How to Get Access |
|------|---------|------------------|

## Key Documentation
Must-read docs with links (architecture, conventions, deployment).

## Conventions
Team-specific conventions (from loaded skills and steering).

## Suggested First Tasks
Easy tickets from current sprint to get started.

## Useful Commands
Common commands for daily work.
```

### 6. Present Draft

Show the guide to the user for review.

**Wait for user confirmation before creating the Confluence page.**

### 7. Create Page

On approval, delegate to tuimm_subagent_confluence:
- Create page in the team's space
- Apply onboarding template/labels
- Link to related docs

### 8. Output

Present results using the kn-onboarding template. Follow it EXACTLY — LAST STEP, nothing after this.
