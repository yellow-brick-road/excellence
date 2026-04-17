# Steering

Shared behavioral rules loaded by **all** agents at startup.

Every agent JSON includes `file://~/.kiro/tuimm/steering/*.md` in its resources — so these files are read before the agent processes any request. They're non-negotiable: agents must follow them.

## Files

| File | What it governs |
|------|-----------------|
| `1_AGENT_RULES.md` | Hub — references all other steering files. Read first by every agent |
| `OPERATING_MODE.md` | How agents process requests: understand → plan → execute → verify |
| `GIT.md` | Branch naming (`feature/DIS-1234_desc`), commit format, workspace conventions |
| `COMMUNICATION.md` | Tone, language, how to report results |
| `TOOL_RULES.md` | When to use which tool, subagent delegation rules |
| `CONVENTIONS.md` | File naming, code style, BEM, TypeScript, Vue, testing standards |
| `TECH_STACK.md` | Current versions: Nuxt 4.3, Vue 3.5, Node 22/24, tooling |
| `SUBAGENTS.md` | Which Tier 2 subagents exist, who delegates to whom |
| `ARTIFACTS.md` | Registry of all commands, skills, templates, tools |
| `ERROR_HANDLING.md` | Never auto-retry, always inform the user, partial results OK |
| `AI_USAGE_TRACKING.md` | Jira AI usage fields — what to set after agent work |

## How they load

Agents reference them with a glob in their JSON config:

```json
{
  "resources": [
    { "type": "file", "path": "~/.kiro/tuimm/steering/*.md" }
  ]
}
```

All 11 files are loaded at startup. The agent reads them before responding to anything.
