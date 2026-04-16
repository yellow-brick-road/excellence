# Command: $morning-scan

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


> Command name: `obs_morning_scan`
> Description: Structured morning scan of production errors. Monday covers weekend, other days cover 24h. Groups by pattern, classifies severity, correlates with deploys.
> Agent: Observability

## Trigger

`$morning-scan` or "scan", "morning scan", "check prod"

## Workflow

1. Determine time window (Monday = weekend, other days = 24h)
2. `subagent_datadog` → search error logs across all configured services
3. Normalize error messages (strip dynamic values)
4. Group by error pattern
5. Compare with previous scan (NEW, RECURRING, SPIKE, RESOLVED)
6. Classify severity (CRITICAL/HIGH/MEDIUM/LOW)
7. For CRITICAL/HIGH: correlate with recent deploys via `subagent_gitlab`
8. For CRITICAL/HIGH: check if related to flag changes via `subagent_configcat` *(optional — Phase 2, skip if ConfigCat unavailable)*
9. Generate scan report with actionable items

## Output

Structured report per project:
- Error count vs previous period
- New errors (not seen before)
- Spikes (existing errors with increased frequency)
- Resolved errors (previously seen, now gone)
- Top errors by frequency and severity
- Deployment correlation (if error appeared after a deploy)

## Phase

Phase 1 (ships with Observability Agent)
