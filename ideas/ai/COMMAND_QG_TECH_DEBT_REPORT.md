# Command: $tech-debt-report

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


> Command name: `qg_tech_debt_report`
> Description: Quantify and prioritize technical debt across projects. Identify hotspots, calculate ROI of fixing top issues, generate cleanup plan.
> Agent: Quality Guardian

## Trigger

`$tech-debt-report` or "tech debt", "debt report", "technical debt"

## Workflow

1. `subagent_sonar` → get tech debt metrics per project (hours/days)
2. `subagent_sonar` → identify debt hotspots (files/modules with most debt)
3. `subagent_sonar` → get debt trend (growing or shrinking per sprint)
4. `subagent_sonar` → categorize debt (security, reliability, maintainability)
5. Calculate ROI: "fixing these N issues reduces debt by X%"
6. `subagent_jira` → check existing tech debt tickets
7. Recommend sprint budget for debt reduction

## Output

- Total debt per project (hours/days)
- Debt trend (last 4 sprints)
- Top 10 debt hotspots with fix effort
- ROI analysis (effort vs debt reduction)
- Existing Jira tickets for debt items
- Recommended sprint debt budget

## Phase

Phase 2 (ships with Quality Guardian)
