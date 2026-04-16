
# Tool Rules

Rules for tool usage in all TUIMM agents.

## Subagent Runtime Limitations (CRITICAL)

When an agent runs as a subagent (spawned by another agent), it has a REDUCED tool set. This is a Kiro CLI platform constraint.

**Available as subagent:** `read`, `write`, `shell`, `code`, MCP tools
**NOT available as subagent:** `subagent`, `grep`, `glob`, `web_search`, `web_fetch`, `thinking`, `introspect`, `todo_list`, `use_aws`

Implications:
- Subagents MUST use `shell` (`ls`, `find`) for directory listing — `glob` is not available
- Subagents CANNOT spawn other subagents — no nested delegation
- Subagents CANNOT use `grep` — use `shell` (`grep` command) or `code` (pattern_search) instead
- If an agent might run as a subagent, it needs direct MCP access, not delegation to Tier 2

Source: https://kiro.dev/docs/cli/chat/subagents/

## File Operations

- When running as a **main agent** (invoked directly): prefer `glob` over `ls`, prefer `read` over `cat`
- When running as a **subagent**: use `shell` (`ls`, `find`, `cat`) — `glob` and `grep` are not available

## Subagent Delegation

- Use subagents for their specialized tasks (see `SUBAGENTS.md`)
- ALWAYS use `use_subagent` for subagent delegation
- Never use a subagent outside its defined scope
- If a command belongs to another agent you can invoke, delegate to that agent with the instruction "execute $command_name" — don't read and execute the command yourself

All NEVER/ALWAYS rules apply unless the user explicitly says otherwise.
