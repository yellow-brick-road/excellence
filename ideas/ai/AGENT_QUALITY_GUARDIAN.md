# Idea: Quality Guardian Agent

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


## Title

AI agent for code quality governance, technical debt management, and quality standards enforcement.

## Context

Combines SonarQube intelligence with GitLab and Jira to create a proactive quality management system. Not just "check the dashboard" — it investigates, correlates, prioritizes, and acts. Inspired by the existing `tui_datadog` pattern but focused on code quality instead of production errors.

## Subagents

- `subagent_sonar` — quality gates, issues, metrics, coverage
- `subagent_gitlab` — MRs, pipelines, code changes
- `subagent_jira` — tech debt tickets, bug tracking
- `subagent_datadog` — correlate code quality issues with production error patterns (enriches $quality-check and $tech-debt-report with production impact data, not used in a dedicated command)

## What It Could Do

### Quality Gate Monitoring
- Monitor quality gate status across all projects
- Alert teams when quality gate fails before CI tells them
- Track quality gate trends over time per team
- Compare quality gate configs across projects (detect inconsistencies)
- Recommend threshold adjustments based on team maturity

### Issue Management
- Prioritize issues by impact (security > bugs > code smells)
- Group related issues across files (same root cause, different locations)
- Auto-create Jira tickets for critical/blocker issues
- Track issue resolution rate per team
- Identify recurring patterns ("this team keeps introducing the same bug type")
- Suggest fixes with code examples for common issues

### Technical Debt
- Quantify tech debt per project (hours/days)
- Debt trend analysis — growing or shrinking?
- Debt hotspots — which files/modules accumulate most debt
- ROI analysis — "fixing these 5 issues reduces debt by 40%"
- Tech debt budget recommendations per sprint
- Cross-team debt comparison

### Security
- Security vulnerability scanning and prioritization
- OWASP Top 10 compliance checking
- Dependency vulnerability tracking
- Security hotspot review workflow
- Time-to-fix tracking for security issues
- Security audit report generation

### Code Coverage
- Coverage trends per project
- Identify untested critical paths (high complexity, low coverage)
- Coverage gap analysis — what's missing and what matters most
- Cross-team coverage comparison
- Recommend coverage targets based on code criticality
- Track coverage changes per MR

### MR Quality
- Automated first-pass review on MRs (patterns, common mistakes)
- Highlight breaking changes in shared libraries
- Flag security-sensitive changes
- MR size warnings (too large → suggest splitting)
- Detect changes that affect other repos (dependency graph awareness)

### Cross-Team Intelligence
- Org-wide code quality dashboard
- Team benchmarking (quality trends, not shaming)
- Extract best practices from highest-quality projects
- Identify teams that need support (declining quality trends)
- Share patterns from teams that improved

### Standards & Rules
- Unified SonarQube rule set across projects
- Custom rules for TUI patterns (BEM, Vue conventions)
- Rule exception management and justification tracking
- Detect projects using outdated rule profiles

### Metrics & Reporting
- Weekly/monthly quality reports per team
- DORA metrics correlation (quality vs deployment frequency)
- Reliability and maintainability rating trends
- Duplicated code percentage and trends
- Cognitive complexity hotspots

### Dependency Health
- Triage Renovate Bot MRs automatically
- Analyze changelogs and breaking changes per dependency update
- Cross-reference breaking changes with actual codebase usage
- Assess impact: which files/modules are affected
- CVE and security advisory tracking for dependencies
- Approve safe updates, flag risky ones with detailed reasoning
- Phase 3: fully automated — Renovate MR triggers review via webhook

## Commands

| Command | Trigger | Description |
|---------|---------|-------------|
| `qg_quality_check` | "quality check", "quality scan" | Full quality scan across projects, cross-project comparison |
| `qg_tech_debt_report` | "tech debt", "debt report" | Debt quantification, hotspots, ROI analysis |
| `qg_dependency_review` | "dependency review", "renovate" | Reactive Renovate MR triage with changelog analysis |
| `qg_dependency_scan` | "scan dependencies", "check updates" | Proactive dependency analysis, auto-update or block |
| `qg_release` | "$release", "$release [package]" | Analyze changes, propose version bump, generate changelog, publish |
