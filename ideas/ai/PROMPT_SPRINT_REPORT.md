# Prompt: @sprint-report

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


> Multi-domain prompt owned by Excellence Default.
> Orchestrates: DevEx Agent + Quality Guardian.

## Agent Guard

Required: excellence_default

## Trigger

`@sprint-report` or "sprint report", "sprint health", "sprint status"

## Purpose

Combined sprint health and quality report. DevEx provides sprint/workflow data, Quality Guardian provides code quality metrics.

## Workflow

1. Delegate to **DevEx Agent**:
   a. Get active sprint data (tickets, status, velocity)
   b. Detect issues (no estimates, missing descriptions, stale tickets)
   c. Find tickets without linked MRs
   d. Calculate MR cycle time and sprint health score

2. Delegate to **Quality Guardian**:
   a. Get quality gate status for sprint-related projects
   b. Get new issues introduced this sprint
   c. Get coverage delta this sprint
   d. Calculate quality trend

3. Merge results into unified report

## Output

- Sprint progress (% complete, tickets by status)
- Velocity vs previous sprints
- Sprint health issues (missing estimates, stale tickets, no MRs)
- MR cycle time average
- Quality gate status
- New issues introduced this sprint
- Coverage trend
- Overall sprint health score

## Phase

Phase 2 (requires both DevEx and Quality Guardian)
