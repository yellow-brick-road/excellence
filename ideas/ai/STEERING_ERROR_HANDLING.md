# Steering: Error Handling

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


Failure patterns and recovery strategies for Excellence agent workflows. Loaded as steering by every Tier 1 agent.

## Principle

**Never silently fail. Never auto-retry. Always inform.**

When a subagent or tool fails, the agent MUST report what happened and let the user decide. Partial results are acceptable — silent failures are not.

## Subagent Failure

When a Tier 2 subagent returns an error or is unreachable:

| Scenario | Action |
|----------|--------|
| Subagent returns error | Report error details, continue with remaining subagents if workflow allows |
| Subagent unreachable (timeout) | Report timeout, skip that subagent's contribution, mark output as incomplete |
| Subagent returns partial data | Use what's available, flag which data is missing |
| MCP Gateway down | Hard stop — no subagents available. Report gateway status |

## Workflow Failure Patterns

### Sequential Workflows (step depends on previous)

Example: $dependency-scan (scan → changelog → impact → decision)

- If step N fails, stop the workflow at step N
- Report: what completed, what failed, what was skipped
- Do NOT attempt remaining steps with missing data

### Parallel Workflows (independent data gathering)

Example: @sprint-report (DevEx data + Quality data in parallel)

- If one branch fails, complete the other
- Generate partial report with clear indication of what's missing
- Example: "Sprint health: complete. Quality metrics: unavailable (SonarQube timeout)"

### Multi-Domain Workflows (multiple agents)

Example: @incident-report (Observability + Knowledge)

- If one agent fails, the other still produces its section
- Missing sections are marked: "⚠️ Confluence page not created (Confluence subagent error: ...)"
- The partial report is still valuable

## Output Marking

When output is incomplete due to errors, mark it clearly:

```markdown
## Report: $morning-scan (partial)

⚠️ Incomplete: Datadog returned timeout for service `b2c-node`. Frontend logs only.

### b2c-tuimusement-frontend
(normal report content)

### b2c-tuimusement-node
❌ Skipped: Datadog timeout after 30s
```

## Retry Policy

- **Automatic retry: NEVER** — agents do not retry failed subagent calls
- **User-initiated retry: YES** — user can re-run the prompt
- **Partial re-run: FUTURE** — Phase 3 could support "retry only the failed parts"

## MCP Gateway Errors

| Error | Meaning | Action |
|-------|---------|--------|
| 401 Unauthorized | SSO token expired | Ask user to re-authenticate: `tui ai config gateway` |
| 403 Forbidden | RBAC denied | Report which tool/action was denied and required role |
| 429 Rate Limited | Too many requests | Report rate limit, suggest waiting |
| 500 Gateway Error | Internal gateway failure | Report error, suggest checking gateway status |
| 503 Unavailable | Gateway or upstream down | Hard stop, report status |

## Escalation

If the same subagent fails consistently across multiple prompts:
1. Report the pattern to the user
2. Suggest checking the upstream service status
3. Do NOT attempt workarounds or alternative APIs