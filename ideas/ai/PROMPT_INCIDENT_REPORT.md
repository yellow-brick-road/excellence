# Prompt: @incident-report

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


> Multi-domain prompt owned by Excellence Default.
> Orchestrates: Observability Agent + Knowledge Agent.

## Agent Guard

Required: excellence_default

## Trigger

`@incident-report` or "incident report", "post-mortem", "write incident"

## Purpose

Generate a structured incident report from an error investigation. Creates a Confluence page with timeline, root cause, impact, and action items.

## Workflow

1. Gather context from current/recent investigation
2. Delegate to **Observability Agent** → build timeline (when started, when detected, when resolved), identify causal MR/deploy, estimate impact
3. Compile root cause analysis
4. Generate action items (prevent recurrence)
5. Delegate to **Knowledge Agent** → create incident page in Confluence from template

## Output

Confluence page with:
- Incident summary (severity, duration, impact)
- Timeline of events
- Root cause analysis
- Impact assessment
- Action items with owners
- Lessons learned

## Phase

Phase 2 (requires Confluence subagent)
