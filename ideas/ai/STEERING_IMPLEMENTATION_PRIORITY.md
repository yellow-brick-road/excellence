# Steering: Implementation Priority

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


Value/effort matrix for Excellence AI architecture rollout. Guides what to build first.

## Priority Matrix

```
                        HIGH VALUE
                            │
         ┌───────────────┼───────────────┐
         │                 │               │
         │  DO SECOND      │  DO FIRST     │
         │                 │               │
         │  Quality Guard. │  MCP Gateway  │
         │  Design System  │  Observability│
         │  Knowledge      │  Excel. Dev   │
         │                 │  Excel. MR    │
         │                 │  Excel. Deflt │
 HIGH    │                 │               │
EFFORT ──┼───────────────┼───────────────┼── LOW
         │                 │               │   EFFORT
         │  RECONSIDER     │  QUICK WINS   │
         │                 │               │
         │  (none yet)     │  DevEx        │
         │                 │  Steering     │
         │                 │  TUI CLI (v1) │
         │                 │               │
         └───────────────┼───────────────┘
                            │
                        LOW VALUE
```

## Rationale

### DO FIRST (high value, low effort)

| Component | Why high value | Why low effort |
|-----------|---------------|----------------|
| MCP Gateway (core) | Unlocks everything — no gateway, no agents | SSO proxy + 4 APIs (Jira, GitLab, Sonar, Datadog). Proven pattern |
| Observability Agent | Most mature — direct port from tui_datadog. Immediate ROI on prod errors | 80% of code exists. Port + multi-project config |
| Excellence Dev | Ticket-to-MR is the highest-frequency workflow | Direct port from tui_dev. Add project awareness |
| Excellence MR | MR review saves hours per week per developer | Direct port from tui_mr. Add team conventions |
| Excellence Default | Required as router + master key for multi-domain prompts | Lightweight — mostly routing logic + steering |

### QUICK WINS (high value, very low effort)

| Component | Why |
|-----------|-----|
| DevEx Agent | Flag cleanup + i18n coverage are low-hanging fruit. Immediate visibility |
| Steering files | Define once, loaded by all agents. High leverage, just markdown |
| TUI CLI v1 | `tui ai install agents` alone justifies v1. Scaffolding can wait |

### DO SECOND (high value, high effort)

| Component | Why high effort |
|-----------|----------------|
| Quality Guardian | SonarQube integration is deep — rule management, cross-project analysis, dependency governance |
| Design System Agent | Figma → code alignment requires sophisticated comparison logic |
| Knowledge Agent | Confluence integration + doc health scoring is complex |

### Dependencies

```
MCP Gateway ───┬───→ All subagents
               │
               ├───→ Observability (port tui_datadog)
               ├───→ Excellence Dev (port tui_dev)
               ├───→ Excellence MR (port tui_mr)
               └───→ Excellence Default (router)
                         │
                         ├───→ DevEx (quick win)
                         ├───→ Quality Guardian
                         ├───→ Design System
                         └───→ Knowledge

Steering + TUI CLI v1 ───→ parallel, no dependencies
```

## Recommended Rollout

> **Mapping to ARCHITECTURE.md phases:** Orders 1-4 = Phase 1 (Foundation), Orders 5-8 = Phase 2 (Specialists), Order 9 = Phase 3 (Autonomous). This doc uses finer-grained ordering by value/effort within each phase.

| Order | What | Timeline | Milestone |
|-------|------|----------|-----------|
| 1 | Steering files + TUI CLI v1 | Week 1-2 | Agents installable, conventions defined |
| 2 | MCP Gateway (Jira, GitLab, Sonar, Datadog) | Week 3-6 | Secure tool access |
| 3 | Excellence Default + Observability | Week 5-7 | First agents live |
| 4 | Excellence Dev + Excellence MR | Week 7-9 | Core workflow agents |
| 5 | DevEx Agent | Week 9-10 | Quick win specialist |
| 6 | Quality Guardian | Week 11-14 | Deep quality integration |
| 7 | Design System + Knowledge | Week 15-18 | Full specialist coverage |
| 8 | MCP Gateway Phase 2 (remaining tools) | Week 14-18 | Full tool coverage |
| 9 | Autonomous layer (Phase 3) | Week 19+ | Webhook-triggered agents |

## Success Gate Per Phase

Before moving to next phase, validate:
1. **Phase 1 gate**: Gateway authenticates, 4 subagents respond, Default routes correctly
2. **Phase 2 gate**: Observability scans work, Dev creates MRs, MR reviews complete
3. **Phase 3 gate**: DevEx flags/i18n work, Quality Guardian scans run
4. **Phase 4 gate**: All 9 agents operational, >50% developer adoption
5. **Phase 5 gate**: Autonomous alerts trigger agent sessions