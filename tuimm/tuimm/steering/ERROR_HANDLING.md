
# Error Handling

Failure patterns and recovery strategies for TUIMM agent workflows.

## Principle

**Never silently fail. Never auto-retry. Always inform.**

Partial results are acceptable — silent failures are not.

## Subagent Failure

| Scenario | Action |
|----------|--------|
| Subagent returns error | Report error details, continue with remaining subagents if workflow allows |
| Subagent unreachable (timeout) | Report timeout, skip that subagent's contribution, mark output as incomplete |
| Subagent returns partial data | Use what's available, flag which data is missing |
| MCP server down | Report which MCP server is unavailable and what functionality is affected |

## Workflow Patterns

### Sequential (step depends on previous)

Example: scan → changelog → impact → decision

- If step N fails, stop at step N
- Report: what completed, what failed, what was skipped
- Do NOT attempt remaining steps with missing data

### Parallel (independent data gathering)

Example: sprint report (DevEx data + Quality data)

- If one branch fails, complete the other
- Generate partial report with clear indication of what's missing

### Multi-Agent (multiple agents contribute)

- If one agent fails, the other still produces its section
- Missing sections are marked with ⚠️ and the error details

## Output Marking

When output is incomplete due to errors:

```markdown
## Report: $obs_dd-scan (partial)

⚠️ Incomplete: Datadog returned timeout for service `service-b`.

### service-a
(normal report content)

### service-b
❌ Skipped: Datadog timeout after 30s
```

## Retry Policy

- **Automatic retry: NEVER**
- **User-initiated retry: YES** — user can re-run the command
- Agents do not retry failed subagent calls on their own
