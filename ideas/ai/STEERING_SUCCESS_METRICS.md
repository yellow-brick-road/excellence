# Steering: Success Metrics

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


KPIs per Excellence agent. How to measure if the AI architecture is delivering value.

## Measurement Approach

- **Baseline first** — measure current state before agent deployment
- **Compare monthly** — track trends, not snapshots
- **Qualitative + quantitative** — numbers matter, but developer satisfaction matters too
- **Attribution is hard** — improvements may come from multiple factors, not just agents

## Quality Guardian

| Metric | Baseline | Target | Source |
|--------|----------|--------|--------|
| SonarQube issues per sprint | TBD | -30% in 6 months | SonarQube API |
| Tech debt (hours) trend | TBD | Decreasing quarter over quarter | SonarQube API |
| MTTR for tech debt tickets | TBD | -25% | Jira |
| Dependency update lag (days behind latest) | TBD | <14 days for patches, <30 for minors | npm registry |
| Quality gate pass rate | TBD | >95% | SonarQube API |
| Renovate MR triage time | TBD | <1 day for safe updates | GitLab |

## Observability Agent

| Metric | Baseline | Target | Source |
|--------|----------|--------|--------|
| MTTR for production errors | TBD | -40% | Datadog + Jira |
| Time to detect (TTD) | TBD | <15 min for critical | Datadog |
| % errors with auto-investigation | 0% | >80% of CRITICAL/HIGH | Agent logs |
| Recurring error rate | TBD | -50% in 6 months | Datadog |
| Incident report generation time | Manual (hours) | <5 min | Agent logs |

## DevEx Agent

| Metric | Baseline | Target | Source |
|--------|----------|--------|--------|
| Stale feature flags | TBD | 0 flags >90 days at 100% | ConfigCat |
| Translation coverage | TBD | >98% per locale | Weblate |
| Sprint health score | TBD | >80% (no missing estimates, no stale tickets) | Jira |
| MR cycle time (open → merge) | TBD | -20% | GitLab |
| Content model drift (env differences) | TBD | 0 unintended drifts | Contentful |

## Design System Agent

| Metric | Baseline | Target | Source |
|--------|----------|--------|--------|
| DS component adoption rate | TBD | >90% of UI uses DS components | Code scan |
| Design-to-code drift score | TBD | <10% deviation | Figma + code comparison |
| Custom (non-DS) components | TBD | Decreasing trend | Code scan |
| Time from Figma design to code | TBD | -30% | Jira + GitLab |

## Knowledge Agent

| Metric | Baseline | Target | Source |
|--------|----------|--------|--------|
| Documentation coverage (% projects with docs) | TBD | 100% | Confluence |
| Stale pages (>6 months without update) | TBD | <10% | Confluence |
| Onboarding time for new developers | TBD | -25% | Survey |
| Runbook coverage (% services with runbook) | TBD | 100% for critical services | Confluence |

## Excellence Dev

| Metric | Baseline | Target | Source |
|--------|----------|--------|--------|
| Ticket-to-MR time | TBD | -50% for standard tickets | Jira + GitLab |
| First-pass MR approval rate | TBD | >70% | GitLab |
| Pre-commit quality issues caught | 0 | >5 per sprint | Agent logs |

## Excellence MR

| Metric | Baseline | Target | Source |
|--------|----------|--------|--------|
| Review turnaround time | TBD | <4 hours | GitLab |
| Issues caught in review (before prod) | TBD | +30% | GitLab |
| Review consistency across teams | TBD | <15% variance in criteria | Agent logs |

## Excellence Default

| Metric | Baseline | Target | Source |
|--------|----------|--------|--------|
| Successful routing rate | N/A | >95% correct agent on first try | Agent logs |
| Cross-domain report quality | N/A | User satisfaction >4/5 | Survey |

## Org-Wide

| Metric | Baseline | Target | Source |
|--------|----------|--------|--------|
| AI agent adoption rate | 0% | >80% of frontend devs | tui ai status |
| Developer satisfaction with tooling | TBD | +20 NPS points | Survey |
| Time saved per developer per week | 0 | >2 hours | Survey + agent logs |
| Standards compliance across repos | TBD | >90% | tui fe check |