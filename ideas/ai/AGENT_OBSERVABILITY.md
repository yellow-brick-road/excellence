# Idea: Observability Agent

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


## Title

AI-powered production monitoring, error investigation, and incident management agent.

## Context

Direct evolution of Javier's `tui_datadog` agent — the most mature agent in the current setup. It already does structured morning scans, error pattern comparison, severity classification, root cause investigation, and can apply fixes through subagents. The Excellence version scales this to all teams, adds project awareness via MCP context, and integrates cross-service correlation.

### What Exists Today (Proof of Concept)

- Morning scan with time-aware windows (Monday = weekend, other days = 24h)
- Error grouping by normalized pattern
- Daily comparison (NEW, RECURRING, SPIKE, RESOLVED)
- Severity classification (CRITICAL/HIGH/MEDIUM/LOW)
- Root cause investigation following systematic-debugging methodology
- Fix workflow: file_modifier → code_reviewer → commit → gitlab MR → jira ticket
- Daily log persistence for trend tracking
- Hardcoded to `b2c-tuimusement-frontend` and `b2c-tuimusement-node`

### What Needs to Change for Org-Wide

- Project-aware configuration (which services, repos, teams)
- Multi-project scanning in one run
- Cross-service error correlation
- Team-specific baselines and thresholds
- Shared error knowledge base

## Subagents

- `subagent_datadog` — logs, APM, metrics, RUM
- `subagent_gitlab` — correlate errors with deploys and MRs
- `subagent_jira` — create bug tickets with full context
- `subagent_sonar` — correlate code quality with production errors
- `subagent_confluence` — incident reports, runbook creation and updates
- `subagent_configcat` — correlate errors with feature flag changes

## What It Could Do

### Project-Aware Configuration
- MCP provides project context: services, repos, team, environment URLs
- Each team configures their services once
- Support multiple projects simultaneously
- Project-specific error baselines (what's "normal" per service)
- Custom severity thresholds per project
- Environment-aware queries (prod, staging, dev)

### Enhanced Scan Mode
- Morning scan across ALL configured projects
- Cross-project error correlation ("same error in 3 services at once")
- Org-wide error dashboard (total errors, top offenders, trends)
- Team-specific scan reports
- Configurable scan schedules per team
- Weekend/holiday-aware scanning
- Automatic baseline adjustment (learns what's normal)

### Error Investigation
- Cross-service trace correlation (frontend → API → database)
- APM integration (traces, spans, latency — not just logs)
- RUM data correlation (real user impact)
- Error impact estimation (users affected, pages, countries)
- Historical pattern matching ("this looks like the error from 2 weeks ago")
- Automated root cause suggestions from error patterns database
- Dependency failure detection ("upstream service X is down")

### Deployment Correlation
- Correlate error spikes with deployments
- Canary deployment monitoring
- Rollback recommendations based on error rate changes
- Pre/post deployment error comparison
- Feature flag correlation (error appeared when flag X was enabled)

### Performance Monitoring
- Page load time tracking per route
- Core Web Vitals (LCP, FID, CLS)
- Performance regression detection per deployment
- API response time trends
- Performance budgets per page/route
- Compare performance across deployments

### Alerting & Notifications
- Pattern-based smart alerting (not just threshold)
- Alert fatigue reduction (group related, suppress known)
- Escalation workflows
- Incident auto-creation from error spikes
- Post-incident timeline generation

### Knowledge Base
- Auto-document resolved errors (what, root cause, fix)
- Searchable error knowledge base
- "Have we seen this before?" instant lookup
- Error pattern taxonomy (network, auth, data, rendering, third-party)
- Runbook generation from investigation history

### Cross-Team Intelligence
- Error pattern sharing ("Team A fixed this, here's how")
- Common error catalog with known fixes
- Cross-team error trends
- Shared runbooks for common error types

### Metrics & Reporting
- Error rate trends per service/team
- MTTR per team
- Error recurrence rate
- Service reliability scores
- SLA compliance tracking
- DORA metrics (change failure rate, MTTR)

## Commands

| Command | Trigger | Description |
|---------|---------|-------------|
| `obs_morning_scan` | "morning scan", "scan", "check prod" | Structured production error scan, time-aware (Monday = weekend) |
| `obs_dd-investigate` | "investigate [error]", "root cause" | Deep root cause analysis, cross-service trace, fix suggestion |

Note: `@incident-report` is a multi-domain prompt owned by Excellence Default (orchestrates Observability + Knowledge).
