# Idea: DevEx Agent

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


## Title

AI agent for developer experience, workflow automation, and cross-tool lifecycle management.

## Context

The "Swiss army knife" agent. Covers the daily developer workflow across multiple tools: feature flags, translations, content models, sprint management, and GitLab operations. It's the agent that reduces friction in the day-to-day — the things that aren't about quality or monitoring, but about getting stuff done faster.

## Subagents

- `subagent_gitlab` — MRs, branches, pipelines
- `subagent_jira` — tickets, sprints, workflow
- `subagent_configcat` — feature flags, A/B tests
- `subagent_weblate` — translations, i18n
- `subagent_contentful` — CMS content models, entries
- `subagent_confluence` — sprint retrospectives, release notes

## What It Could Do

### Feature Flag Lifecycle
- List, search, and query flags from terminal
- Create flags with standardized naming conventions
- Toggle flags per environment with safety checks
- Detect stale flags (enabled for months, never toggled)
- Find flags 100% rolled out but still in code (cleanup candidates)
- Scan codebase for flag usage and map to ConfigCat
- Generate cleanup tickets in Jira for stale flags
- Flag retirement workflow (remove from code → remove from ConfigCat)
- A/B test monitoring (duration, sample size, significance)
- Audit log of flag changes
- Cross-team flag visibility dashboard

### Translation Management
- Add/remove/rename translation keys across all locales
- Detect untranslated keys per locale
- Find inconsistent translations (same source, different translations)
- Detect placeholder mismatches ({0}, {1})
- Translation coverage per module and locale
- Detect hardcoded strings in Vue templates that should be i18n keys
- Scan codebase for `$t('key')` calls and verify keys exist
- Key naming convention enforcement
- Cross-module terminology consistency
- Generate translation tickets when new keys are added

### Content Model Management
- Query and visualize Contentful content models
- Generate TypeScript interfaces from content types
- Detect content model inconsistencies across environments
- Track content model changes over time
- Detect breaking changes before production
- Find unused content types
- Content freshness audit
- Migration script generation

### Sprint & Workflow
- Sprint health dashboard (tickets without estimates, missing descriptions, stale)
- Find tickets without linked MRs
- Auto-transition tickets based on MR status
- Sprint retrospective data extraction (velocity, carryover, completion)
- Generate weekly/sprint reports per team
- Cross-team dependency detection

### GitLab Workflow
- MR quality checks (description, labels, linked ticket, reviewers)
- Smart reviewer assignment based on file ownership
- MR size warnings (suggest splitting)
- Pipeline failure categorization (test, lint, build, deploy)
- Flaky test detection and reporting
- Branch hygiene (stale branches, naming conventions)
- Cross-repo dependency impact analysis

### Developer Onboarding (supports Knowledge Agent)
- Provide team-specific data for onboarding guides (owned by Knowledge Agent)
- Map new developer to relevant repos and tools
- Explain project structure and conventions
- Suggest first tasks based on skill level

### Metrics & Reporting
- Developer satisfaction surveys (tooling friction points)
- Time spent on non-coding tasks (flag management, translations, content)
- Sprint velocity and predictability
- MR cycle time (open → merge)
- Pipeline success rate trends
- Deployment frequency

## Commands

| Command | Trigger | Description |
|---------|---------|-------------|
| `devex_flag_cleanup` | "flag cleanup", "stale flags" | Stale flag detection, orphan flags, cleanup plan with Jira tickets |
| `devex_i18n_coverage` | "i18n coverage", "translations" | Translation coverage report across modules and locales |
| `devex_content_audit` | "content audit", "contentful check" | Content model health, environment drift, TypeScript interfaces |

Note: `@sprint-report` is a multi-domain prompt owned by Excellence Default (orchestrates DevEx + Quality Guardian).

### TUI CLI Integration

The DevEx Agent can invoke TUI CLI logic programmatically, acting as the intelligent layer on top of the CLI engine:
- "Check if this repo is compliant" → `tui fe check`
- "Update ESLint config" → `tui fe sync configs --only eslint`
- "What's outdated?" → `tui fe deps`
- "Set up my IDE" → `tui fe ide setup`
- "Install AI agents" → `tui ai install agents`

See: `ideas/tooling/TUI_CLI.md`
