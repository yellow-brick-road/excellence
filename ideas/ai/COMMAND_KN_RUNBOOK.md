# Command: $runbook

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


> Command name: `kn_runbook`
> Description: Generate a runbook for a specific topic from existing knowledge — incident history, code context, documentation. Creates Confluence page.
> Agent: Knowledge

## Trigger

`$runbook [topic]` or "create runbook", "generate runbook"

## Workflow

1. `subagent_confluence` → search existing docs related to the topic
2. Delegate to **Observability Agent** → get historical incidents related to the topic (Observability owns Datadog access)
3. `subagent_gitlab` → find relevant code and configuration
4. Synthesize: combine existing knowledge into structured runbook
5. `subagent_confluence` → create runbook page from template

## Output

Confluence page with:
- Runbook title and scope
- Prerequisites (access, tools, permissions)
- Step-by-step procedure
- Troubleshooting section
- Escalation path
- Related documentation links

## Phase

Phase 2 (requires Confluence subagent)
