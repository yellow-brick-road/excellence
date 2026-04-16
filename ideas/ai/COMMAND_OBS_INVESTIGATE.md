# Command: $investigate

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


> Command name: `obs_dd-investigate`
> Description: Deep root cause analysis of a specific production error. Traces across services, correlates with code changes, suggests fixes.
> Agent: Observability

## Trigger

`$investigate [error]` or "investigate", "root cause", "why is this failing"

## Workflow

1. `subagent_datadog` → search logs for the error pattern, get full context
2. `subagent_datadog` → trace across services (frontend → API → database)
3. `subagent_gitlab` → find recent MRs/deploys that could have introduced it
4. `subagent_sonar` → check if related code has quality issues
5. `subagent_configcat` → check if error correlates with flag changes *(optional — Phase 2, skip if ConfigCat unavailable)*
6. Analyze all evidence, propose root cause
7. Suggest fix with affected files and approach

## Output

- Error pattern and frequency
- Cross-service trace (if applicable)
- Probable root cause with evidence
- Related deployments/MRs
- Suggested fix approach
- Affected files

## Phase

Phase 1 (ships with Observability Agent)
