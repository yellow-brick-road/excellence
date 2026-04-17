# Decisions

Settled architectural and organizational decisions. If it's here, it's closed — don't re-discuss unless new information surfaces.

## Architecture

### 1. Nitro as HTTP framework

**Date:** 2026-03-03
**Decision:** Nitro replaces Hono/Express for all Excellence server-side components (MCP Gateway, Bot Service).
**Reason:** Already used inside Nuxt, file-based routing, deploy presets, auto-imports, same DX as Nuxt server routes.
**Affects:** `TASK_005_MCP_GATEWAY.md`, `AUTONOMOUS_BOT_SERVICE.md`

### 2. Teams, not Telegram

**Date:** 2026-03-03
**Decision:** All bot/notification integrations target Microsoft Teams. No Telegram.
**Reason:** TUI uses Teams org-wide.
**Affects:** `AUTONOMOUS_BOT_SERVICE.md`

### 3. LLM API direct in production, ACP for POC only

**Date:** 2026-03-03
**Decision:** The Excellence Bot Service uses Vercel AI SDK + Anthropic/OpenAI directly. kiro-cli ACP is only for POC/demos.
**Reason:** kiro-cli has interactive auth, heavy process footprint, black box behavior, uncertain server license.
**Affects:** `AUTONOMOUS_BOT_SERVICE.md`, `ARCHITECTURE.md`

### 4. Quality Guardian owns dependency workflows

**Date:** 2026-03-03
**Decision:** All dependency-related commands (`$dependency-review`, `$dependency-scan`, `$release`) belong to Quality Guardian.
**Reason:** QG has all needed subagents (GitLab, Jira, SonarQube) and dependency health is a quality concern.
**Affects:** `AGENT_QUALITY_GUARDIAN.md`, `COMMAND_QG_DEPENDENCY_REVIEW.md`, `COMMAND_QG_DEPENDENCY_SCAN.md`, `COMMAND_QG_RELEASE.md`

### 5. Commands as separate artifact type

**Date:** 2026-03-04 (updated 2026-03-30)
**Decision:** Single-agent targeted actions are commands (`~/.kiro/commands/`), not skills or prompts. Only multi-domain orchestrations stay as prompts. Output format templates are a third artifact type (`~/.kiro/templates/`).
**Reason:** Domain enforcement is structural (only the owning agent loads the command). Agent Guard was dropped during implementation — unnecessary given structural enforcement. Templates separate format from logic.
**Result:** 36 commands (11 domain prefixes + 1 meta) + 14 skills + 37 templates. 0 prompts (folder empty — multi-domain orchestration deferred).
**Affects:** All `AGENT_*.md`, `STEERING_PROMPTS.md`, `STEERING_CONVENTIONS.md`, `ARCHITECTURE.md`, `COMMAND_*.md`

### 6. $runbook delegates to Observability for incident data

**Date:** 2026-03-04
**Decision:** The Knowledge Agent's `$runbook` command does not call Datadog directly. It delegates incident data retrieval to the Observability Agent.
**Reason:** Keeps domain boundaries clean. Datadog is Observability's domain.
**Affects:** `AGENT_KNOWLEDGE.md`, `COMMAND_KN_RUNBOOK.md`

## Organizational

### 7. Bot Service is Phase 3

**Date:** 2026-03-03
**Decision:** The Excellence Bot Service (autonomous webhook-triggered agents) is Phase 3 of the implementation. Not part of the initial rollout.
**Reason:** Requires stable agents (Phase 1-2) before automation makes sense.
**Affects:** `AUTONOMOUS_BOT_SERVICE.md`, `STEERING_IMPLEMENTATION_PRIORITY.md`
