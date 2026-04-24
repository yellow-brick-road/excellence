---
name: get-commands
description: "List all available commands — own and from specialist agents. Use when: user asks what commands are available, what you can do, or lists capabilities."
---

# Command: $get-commands

List all available commands for this agent and its specialist agents.

## Steps

1. Read the TUIMM_ARTIFACTS steering file to get the full command registry

2. Identify which TUIMM Tier 1 agents you can invoke (from TUIMM_SUBAGENTS steering)

3. Present results using the get-commands-output template. Follow it EXACTLY

4. If the user asks about a specific command, read its command file and explain what it does
