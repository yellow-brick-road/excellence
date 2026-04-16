# Steering: Agent Rules

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


Shared rules for all Excellence agents. Loaded as steering by every Tier 1 agent.

## Error Handling

On ANY error from a subagent or tool:
- NEVER auto-fallback or retry silently
- ALWAYS return detailed error info (what failed, where, why)
- Let user decide what to do
- See `STEERING_ERROR_HANDLING.md` for workflow-specific failure patterns

## Delegation

- Use Tier 2 subagents for their specialized tasks — agents orchestrate, subagents execute
- NEVER bypass a subagent to call an API directly
- All tool access goes through the MCP Gateway
- If a subagent is unavailable, report it — don't improvise

## Git

Direct git commands allowed:
- `git status`, `git diff`, `git log`, `git branch`, `git fetch`, `git pull`

For commits → use commit subagent or equivalent
For push → user does manually

## Tool Rules

- When running as a **main agent**: prefer `glob` over `ls` for directory listing
- When running as a **subagent**: use `shell` (ls, find) — `glob`, `grep`, `subagent`, `web_search`, `thinking` are NOT available in the subagent runtime
- Use `use_subagent` for subagent delegation, never `delegate`
- Save reports to standard output path with timestamp naming

## Agent Guard Enforcement

Every agent MUST check the `## Agent Guard` header before executing a prompt:
1. Read the `Required:` field
2. If current agent matches → execute
3. If current agent is `excellence_default` → execute (master key)
4. Otherwise → hard stop, respond with redirect message

See `STEERING_CONVENTIONS.md` for full Agent Guard specification.

## Communication

- Be direct, no fluff
- Report facts, not opinions (unless asked)
- When aggregating data from multiple subagents, cite which subagent provided what
- If data is stale or incomplete, say so explicitly