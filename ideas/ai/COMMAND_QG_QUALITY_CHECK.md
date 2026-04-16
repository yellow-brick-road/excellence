# Command: $quality-check

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


> Command name: `qg_quality_check`
> Description: Full quality scan across all configured projects. Quality gate status, new issues, coverage trends, cross-project comparison.
> Agent: Quality Guardian

## Trigger

`$quality-check` or "quality check", "quality scan", "check quality"

## Workflow

1. `subagent_sonar` → get quality gate status for all projects
2. `subagent_sonar` → get new issues since last analysis (by severity)
3. `subagent_sonar` → get coverage trends
4. `subagent_sonar` → get tech debt metrics
5. Compare across projects (detect outliers)
6. `subagent_gitlab` → check if failing quality gates block any MRs
7. Generate quality report with priorities

## Output

- Quality gate status per project (PASS/FAIL)
- New issues by severity (blocker, critical, major)
- Coverage trends (improving/declining)
- Tech debt hotspots
- Cross-project comparison
- Recommended actions

## Phase

Phase 2 (ships with Quality Guardian)
