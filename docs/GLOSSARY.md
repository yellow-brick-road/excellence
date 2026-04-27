# Glossary

Terms used across Excellence documentation.

| Term | Definition |
|------|-----------|
| **Agent** | AI assistant with a specific domain (Tier 1). User-facing, loads steering files |
| **Agent Guard** | ~~Enforcement table in STEERING_CONVENTIONS.md~~ — dropped during implementation. Domain enforcement is structural (only the owning agent loads the command) |
| **Command** | Single-agent targeted action. Lives inside workflow skills at `skills/tuimm-*/commands/`, loaded via progressive disclosure. Triggered with `$name` prefix |
| **Excellence** | Cross-cutting function within DP&T. Accelerator, not a delivery team |
| **TUIMM Default** | Concierge agent — guides users to the correct specialist agent, executes shared commands (jira, weblate) directly |
| **Guild** | Collaboration-based group (no authority). Excellence operates as a guild |
| **Helix** | TUI Musement's organizational model. Excellence is part of it |
| **MCP** | Model Context Protocol — standard for LLM tool integration |
| **MCP Gateway** | Planned single endpoint (`mcp.tui.internal`) for centralized auth and audit. Phase 3 — current implementation uses direct MCP connections |
| **Prompt** | Multi-domain orchestration owned by TUIMM Default. Coordinates 2+ specialist agents (none created yet) |
| **RBAC** | Role-Based Access Control — who can invoke what through the MCP Gateway |
| **Skill** | Knowledge reference material loaded by agents. Not executable — provides context |
| **Steering file** | Shared configuration loaded by all Tier 1 agents (conventions, rules, metrics, etc.) |
| **Subagent** | Tier 2 tool agent wrapping an external API (Jira, GitLab, etc.) or providing specialized analysis (Code Reviewer). Direct MCP connections per developer machine |
| **TARS** | Javier's personal agent ecosystem. Excellence architecture scales TARS to org-wide use |
| **Template** | Output format definition. Lives inside workflow skills at `skills/tuimm-*/assets/templates/`. Consumed by agents/commands for structured output |
| **Tier 1** | User-facing agents (9). Load steering, own commands |
| **Tier 2** | Tool subagents (10). Direct MCP connections, no steering, no direct user interaction |
| **TUI CLI** | Internal CLI (`@tui/cli`) — distribution mechanism for agents, skills, configs |
