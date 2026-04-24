# TUIMM Knowledge Base Index

This directory is the knowledgeBase index target for TUIMM agents. It exists so agents can use semantic search across TUIMM documentation.

## Where the actual content lives

After installation, TUIMM content is distributed across `~/.kiro/`:

- `~/.kiro/steering/TUIMM_*.md` — 11 behavioral rules
- `~/.kiro/skills/tuimm-*/` — 25 skills (commands, templates, references)
- `~/.kiro/tools/` — Python scripts and utilities
- `~/.kiro/agents/tuimm_*.json` — 19 agent configurations

This directory is intentionally lightweight. Agent JSONs point their `knowledgeBase` source here for indexing purposes.
