# Idea: Excellence Bot Service

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


## Title

Event-driven autonomous agent invocation — external events trigger Excellence agents without human intervention.

## Context

Phases 1 and 2 of the Excellence AI architecture are human-invoked: a developer opens a chat, talks to an agent, gets results. Phase 3 removes the human from the loop for predictable, repeatable scenarios.

The Excellence Bot Service is a lightweight Nitro server that receives external events (webhooks, alerts, schedules) and invokes the correct Excellence agent programmatically. The bot has no intelligence — it's a dispatcher. All reasoning lives in the agents.

## The Problem

```
TODAY (Phase 1-2):

Renovate creates MR → sits there → someone remembers → reviews manually
Datadog fires alert → someone checks Slack → investigates manually
SonarQube gate fails → CI shows red → someone looks at it eventually
Stale docs → nobody notices → knowledge rots

Every reaction depends on a human noticing and acting.
```

## The Solution

```
PHASE 3:

Renovate creates MR → bot → Quality Guardian reviews automatically
Datadog fires alert → bot → Observability investigates automatically
SonarQube gate fails → bot → Quality Guardian analyzes automatically
Schedule (weekly) → bot → Knowledge Agent audits docs automatically

Humans only intervene when the agent flags something that needs a brain.
```

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  EVENT SOURCES                                               │
│                                                              │
│  GitLab webhooks · Datadog monitors · SonarQube webhooks     │
│  Cron schedules · Teams commands (future)                    │
└──────────────────────┬───────────────────────────────────────┘
                       │ HTTP POST / cron trigger
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  EXCELLENCE BOT SERVICE (Nitro, AWS ECS Fargate)             │
│                                                              │
│  routes/                                                     │
│  ├── webhook/gitlab.post.ts      ← MR events, pipeline      │
│  ├── webhook/datadog.post.ts     ← Monitor alerts            │
│  ├── webhook/sonarqube.post.ts   ← Quality gate events       │
│  └── cron/weekly-audit.ts        ← Scheduled tasks           │
│                                                              │
│  1. Receive event                                            │
│  2. Filter: is this relevant?                                │
│  3. Route: which agent + prompt?                             │
│  4. Invoke LLM with agent's system prompt + MCP Gateway tools│
│  5. Forward result (Teams notification if needed)            │
└──────────────────────┬───────────────────────────────────────┘
                       │ tool calls
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  MCP GATEWAY                                                 │
│  https://mcp.tui.internal/v1/sse                             │
│                                                              │
│  GitLab · Jira · SonarQube · Datadog · Confluence · ...      │
└──────────────────────────────────────────────────────────────┘
```

## Use Cases

### Reactive (webhook-triggered)

| Source | Event | Agent | Command | Action |
|---|---|---|---|---|
| GitLab | Renovate MR created | Quality Guardian | $dependency-review | Analyze changelog, assess impact, approve/block, comment on MR |
| GitLab | Quality gate MR label | Quality Guardian | $quality-check | Run quality analysis on MR changes |
| Datadog | Monitor alert (error spike) | Observability | $investigate | Investigate error, correlate with recent deploys, post findings |
| Datadog | Monitor alert (latency) | Observability | $investigate | Analyze latency source, check recent changes |
| SonarQube | Quality gate failure | Quality Guardian | $quality-check | Identify new issues, assess severity, notify team |
| GitLab | MR ready for review | Excellence MR | $review (future) | Automated first-pass review |

### Proactive (scheduled)

| Schedule | Agent | Command | Action |
|---|---|---|---|
| Weekly | Knowledge Agent | $doc-health | Audit Confluence staleness, report gaps |
| Weekly | Quality Guardian | $dependency-scan | Scan all repos for outdated deps |
| Weekly | Quality Guardian | $tech-debt-report | Generate tech debt summary across projects |
| Daily | Observability | $morning-scan | Scan overnight errors, summarize for team |
| Monthly | DevEx | $i18n-coverage | Report translation coverage gaps |

### Conversational (future)

| Source | Trigger | Agent | Action |
|---|---|---|---|
| Teams | "@excellence scan errors" | Observability | On-demand investigation from Teams |
| Teams | "@excellence review MR !123" | Excellence MR | On-demand MR review from Teams |

## Tech Stack

### Production (recommended)

- **Nitro** — HTTP server, file-based routing, deploy presets
- **Vercel AI SDK** (`ai` + `@ai-sdk/anthropic`) — LLM calls with tool-calling loop
- **MCP Gateway client** — tool definitions from gateway, execute via HTTP
- **Docker** on **ECS Fargate** — same infra as MCP Gateway

The bot calls the LLM API directly (not through kiro-cli). This gives full control over model selection, cost, system prompts, and tool definitions.

```ts
// Simplified: how the bot invokes an agent
import { generateText } from 'ai'
import { anthropic } from '@ai-sdk/anthropic'

const result = await generateText({
  model: anthropic('claude-sonnet-4-20250514'),
  system: loadAgentPrompt('quality_guardian'),
  prompt: `Run $dependency-review for MR !${iid} in ${project}`,
  tools: getMcpGatewayTools(),
  maxSteps: 20,
})
```

### POC alternative

For early validation, `kiro-cli acp` can be used instead of direct LLM calls:
- Spawn `kiro-cli acp` as subprocess
- Communicate via ACP protocol (JSON-RPC over stdin/stdout)
- Reuses existing agent configs without changes
- Not recommended for production (interactive auth, heavy process spawn, less control)

## Agent System Prompts

Each agent's system prompt is composed from:
1. **Agent-specific instructions** — from agent config (purpose, domain, behavior)
2. **Steering files** — shared conventions, rules, subagent references
3. **Skills** — domain knowledge (testing philosophy, dependency governance, etc.)
4. **Prompt workflow** — the specific prompt being executed ($dependency-review steps)

These are the same files distributed by TUI CLI. The bot loads them from disk or from the registry.

## Event Filtering

The bot only acts on relevant events. Examples:

**GitLab webhook filtering:**
- `object_kind === 'merge_request'` AND `user.username === 'renovate-bot'` AND `action === 'open'` → $dependency-review
- `object_kind === 'merge_request'` AND `action === 'update'` AND `labels includes 'review-requested'` → $review (future)
- Everything else → ignore

**Datadog alert filtering:**
- `alert_type === 'error'` AND `priority === 'P1'` → $investigate immediately
- `alert_type === 'error'` AND `priority === 'P2'` → $investigate (batched)
- `alert_type === 'warning'` → ignore (handled in morning scan)

**SonarQube webhook filtering:**
- `qualityGate.status === 'ERROR'` → $quality-check
- `qualityGate.status === 'OK'` → ignore

## Notifications

The bot sends Teams notifications only when human attention is needed:

| Agent Decision | Notification |
|---|---|
| APPROVE (dependency) | None — comment on MR is enough |
| NEEDS ATTENTION | Teams message to team channel |
| BLOCK | Teams message to team channel + tag relevant people |
| Error investigation complete | Teams summary with findings |
| Quality gate analysis | Teams message if critical issues found |

Teams integration via incoming webhook (simple HTTP POST, no bot framework needed).

## Deployment

```
AWS ECS Fargate
├── mcp-gateway          ← mcp.tui.internal (Phase 1)
└── excellence-bot       ← bot.excellence.internal (Phase 3)
```

Both services share the same infrastructure pattern: Docker container, ECS Fargate, internal DNS. The bot authenticates to MCP Gateway with a service account (not SSO — it's a machine, not a human).

## Security

- Bot has a **service account** with specific RBAC permissions in MCP Gateway
- Bot can only invoke tools its agents need (not full admin access)
- All actions are audit-logged in MCP Gateway (who = "excellence-bot", what, when)
- LLM API key stored in AWS Secrets Manager
- Webhook endpoints validate signatures (GitLab secret token, Datadog signature)
- Rate limiting on webhook endpoints to prevent abuse

## Spec-Driven Execution

The bot follows Spec-Driven Dev (`SPEC_DRIVEN_DEV.md`). Before executing, the agent produces a plan. Since there is no human in the loop, a specialized **reviewer agent** evaluates the plan:

- Reviewer approves → agent executes → result notified to Teams
- Reviewer rejects → bot notifies Teams with the plan and rejection reason → human intervenes

This provides audit trail and safety without requiring human approval for every automated action.

## Implementation Phases

### Phase 3a: First automation
- Bot service deployed (Nitro, ECS Fargate)
- GitLab webhook → $dependency-review (Renovate MRs)
- Datadog webhook → $investigate (P1 alerts)
- Teams notifications for BLOCK/NEEDS ATTENTION

### Phase 3b: Expanded automation
- SonarQube webhook → $quality-check
- Scheduled tasks (weekly dependency scan, doc health, tech debt)
- Daily morning scan

### Phase 3c: Conversational (future)
- Teams bot integration (respond to @excellence commands in Teams)
- On-demand agent invocation from chat

## Open Questions

- [ ] Which LLM provider for production? Anthropic (Claude), OpenAI (GPT), or configurable?
- [ ] Service account RBAC: what permissions does the bot need per agent?
- [ ] How to handle long-running agent sessions? (timeout, retry, partial results)
- [ ] Cost monitoring: how to track and cap LLM spend from the bot?
- [ ] Should the bot have its own dashboard? (events received, agents invoked, results)
- [ ] How to test the bot? (mock webhooks, mock LLM responses, integration tests)
- [ ] GitLab webhook secret rotation strategy?
- [ ] Should scheduled tasks run from the bot or from a separate cron service?
