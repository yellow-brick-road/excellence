# Idea: Knowledge Agent

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


## Title

AI agent for documentation health, knowledge management, and organizational learning via Confluence.

## Context

Documentation is one of the biggest pain points in any org — outdated, scattered, or nonexistent. This agent makes documentation a first-class citizen without adding manual overhead. It creates, maintains, audits, and connects documentation across the organization.

## Subagents

- `subagent_confluence` — pages, spaces, search, creation
- `subagent_jira` — link tickets to docs, extract sprint data
- `subagent_gitlab` — sync code docs, extract MR data for release notes
- `subagent_contentful` — sync CMS documentation, content model references

## What It Could Do

### Documentation Creation
- Generate technical docs from code (README, API docs, architecture decisions)
- Create ADRs (Architecture Decision Records) from conversations or MR discussions
- Auto-generate onboarding guides per team/project
- Create runbooks from incident post-mortems
- Template library for common doc types (RFC, ADR, runbook, how-to, retrospective)
- Generate release notes from merged MRs
- Create incident pages from Datadog alerts (via Observability Agent)

### Knowledge Search & Discovery
- Natural language search across all Confluence spaces
- Surface relevant docs when creating Jira tickets
- "Does this already exist?" check before creating new pages
- Cross-reference documentation with actual code (detect drift)
- Personalized reading lists for new joiners

### Documentation Health
- Detect stale pages (not updated in X months, referenced code changed)
- Identify orphan pages (no links pointing to them)
- Find duplicate or contradictory documentation
- Documentation coverage report per team/project
- Flag pages with broken links or outdated screenshots
- Freshness scoring

### Standards & Governance
- Enforce documentation templates per page type
- Ensure new projects have minimum docs (README, architecture, deployment)
- Review documentation quality (completeness, clarity, structure)
- Maintain documentation style guide
- Suggest improvements to existing pages

### Automation
- Auto-create sprint retrospective pages from Jira data
- Update architecture diagrams when dependencies change
- Notify owners when their documentation becomes stale
- Sync README and docs/ folder with Confluence
- Generate personalized onboarding paths

### Metrics
- Documentation coverage per team (% of projects with docs)
- Freshness score (average age of last update)
- Most/least viewed pages
- Search success rate
- Time to first documentation for new projects
- Stale page percentage

## Commands

| Command | Trigger | Description |
|---------|---------|-------------|
| `kn_doc_health` | "doc health", "docs audit" | Documentation health audit, freshness scores, stale/orphan detection |
| `kn_runbook` | "runbook [topic]" | Generate runbook from incidents, code, and docs |
| `kn_onboarding` | "onboarding [team]" | Personalized onboarding guide for new team members |
