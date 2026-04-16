# Practice: Confluence Restructuring

## Guild Position

> Current Confluence is unusable as a knowledge source — for humans and for AI agents. Before building a Knowledge Agent, we need a knowledge base worth querying. Structure first, tooling second.

## The Problem

- Pages are unstructured free-form — no enforced templates, no consistent format
- Content is stale — pages written months/years ago, never reviewed, never archived
- Everything is mixed — architecture docs next to meeting notes next to abandoned drafts
- No labeling strategy — labels are absent, inconsistent, or meaningless
- No ownership — pages belong to nobody, so nobody maintains them
- No lifecycle — pages are created and forgotten, never reviewed or retired
- Hierarchy is flat or chaotic — no predictable structure across spaces
- AI agents can't parse it — no structured sections, no metadata, no machine-readable patterns

The result: developers don't trust Confluence, so they don't use it. Knowledge lives in Slack threads, heads, and tribal memory. The Knowledge Agent (ideas/ai/AGENT_KNOWLEDGE.md) can't work with garbage in.

## The Principle

**Make knowledge structured, owned, and alive.**

A page is useful when it has a clear type, a known owner, a review date, and structured sections an agent can parse. A page is waste when it's an undated wall of text that nobody maintains.

## Approach

Three phases. Each builds on the previous. No big-bang migration — the old structure stays as-is (legacy), the new structure grows alongside it. Pages migrate when they're touched, not in bulk.

---

## Phase 1 — Audit: What Do We Actually Have?

Before proposing anything, we need data. Not opinions — numbers.

### What to Map

| Dimension | What to measure | How |
|---|---|---|
| Inventory | Spaces, page count per space, total pages | CQL queries via Confluence API |
| Staleness | Last-edit distribution (30d, 90d, 6m, 1y, 2y+) | Page metadata |
| Structure | Hierarchy depth per space, orphan pages (no incoming links), broken links | API traversal |
| Content types | What's actually there — tech docs, meeting notes, onboarding, runbooks, decisions, drafts | Manual sampling + keyword analysis |
| Labels | Usage rate, most common labels, spaces with zero labels | API query |
| Ownership | Creator distribution, pages with no recent editor | Page metadata |
| Usage | Most/least viewed pages (if analytics available) | Confluence analytics API |

### Output

An audit report: `CONFLUENCE_AUDIT_REPORT.md` — numbers, not opinions. The report answers:
- How big is the problem? (total pages, % stale)
- Where is the problem? (which spaces are worst)
- What's worth saving? (high-traffic pages that need restructuring vs dead pages)
- What content types exist? (so we know what templates to create)

### Tooling

This audit can be partially automated with the Confluence subagent (Atlassian MCP):
- CQL queries for page counts, staleness, labels
- Space listing and hierarchy traversal
- Bulk metadata extraction

The qualitative analysis ("is this page useful?") needs human judgment — but the agent can surface candidates.

---

## Phase 2 — New Structure: AI-Friendly Knowledge Base

A v2 structure that coexists with legacy. New pages follow v2 from day one. Old pages migrate when touched.

### Page Templates

Every page has a type. Every type has a template. Templates enforce structure.

| Type | Purpose | Key sections |
|---|---|---|
| **Reference** | Stable technical documentation (APIs, architecture, conventions) | Summary, Details, Related, Owner, Last Reviewed |
| **ADR** | Architecture Decision Record | Context, Decision, Consequences, Status, Date |
| **Runbook** | Operational procedure for incidents/tasks | Trigger, Steps, Rollback, Owner, Last Tested |
| **How-To** | Step-by-step guide for a specific task | Prerequisites, Steps, Troubleshooting, Owner |
| **Onboarding** | New joiner guide per team/domain | Overview, Setup, Key Contacts, First Tasks |
| **Meeting Notes** | Meeting outcomes (NOT mixed with docs) | Date, Attendees, Decisions, Action Items |
| **Retrospective** | Sprint/project retrospective | What Went Well, What Didn't, Actions, Sprint |
| **RFC** | Request for Comments / proposal | Problem, Proposal, Alternatives, Decision, Status |

### Structured Sections

Templates use consistent section headers so agents can parse predictably:
- `## Summary` — always first, always present, 2-3 sentences max
- `## Owner` — person or team responsible
- `## Status` — draft / active / deprecated / archived
- `## Last Reviewed` — date of last human review
- Content sections vary by template type

### Label Taxonomy

Consistent, enforced labels across all v2 pages:

| Category | Labels | Purpose |
|---|---|---|
| Type | `type:reference`, `type:adr`, `type:runbook`, `type:howto`, `type:onboarding`, `type:meeting`, `type:retro`, `type:rfc` | Content classification |
| Domain | `domain:frontend`, `domain:backend`, `domain:infra`, `domain:design`, `domain:process` | Technical domain |
| Team | `team:{name}` | Owning team |
| Status | `status:draft`, `status:active`, `status:deprecated`, `status:archived` | Lifecycle state |
| AI | `ai:indexed`, `ai:excluded` | Whether the Knowledge Agent should index this page |

### Naming Conventions

Predictable page titles:
- Reference: `[Domain] Topic` — e.g., `[Frontend] BEM Naming Conventions`
- ADR: `ADR-NNN: Decision Title` — e.g., `ADR-012: Adopt Nuxt 4`
- Runbook: `Runbook: Scenario` — e.g., `Runbook: Production Deployment Rollback`
- How-To: `How to: Task` — e.g., `How to: Add a Translation Key`

### Space Organization

Clear separation by purpose, not by team:

| Space | Content | Who writes |
|---|---|---|
| **Engineering Reference** | Technical docs, conventions, architecture | All engineers |
| **Decisions** | ADRs, RFCs | Tech leads, architects |
| **Runbooks** | Operational procedures | SRE, on-call engineers |
| **Onboarding** | Team-specific onboarding guides | Team leads |
| **Meeting Notes** | Meeting outcomes only | Anyone (but isolated from docs) |
| **Team Spaces** | Team-specific working docs | Individual teams |

### Lifecycle

Every v2 page has a lifecycle:
1. **Draft** → being written, not reliable
2. **Active** → reviewed, current, trustworthy
3. **Stale** → not reviewed in X months, flagged for review
4. **Deprecated** → superseded, kept for reference with link to replacement
5. **Archived** → removed from active navigation, searchable but hidden

Automation: pages not reviewed in 6 months get auto-labeled `status:stale`. Owner gets notified. After 3 more months without action → `status:deprecated`.

### Migration Strategy

- **No bulk migration** — old pages stay as-is in legacy spaces
- **Migrate on touch** — when someone edits a legacy page, they restructure it to v2
- **Priority migration** — high-traffic pages and pages needed by Knowledge Agent get migrated first
- **Agent-assisted** — a `$doc-migrate` command helps restructure legacy pages to v2 format

---

## Phase 3 — Tooling: Skills, Prompts, and Agent Integration

The Knowledge Agent (ideas/ai/AGENT_KNOWLEDGE.md) already defines the agent. This phase creates the supporting skills and prompts that make it effective.

### Skills

> **Note:** The skills and commands below are planned but not yet specced (no COMMAND_*.md files, not in STEERING_PROMPTS.md). They will be formalized when Confluence Restructuring moves from ideation to implementation. Only `$doc-health` exists as `COMMAND_KN_DOC_HEALTH.md`.

| Skill | Purpose |
|---|---|
| `skill_confluence_structure` | V2 structure reference: spaces, templates, labels, naming conventions. Loaded by Knowledge Agent so it knows where things go |
| `skill_confluence_templates` | Page templates per content type. Used when creating new pages to enforce structure |

### Commands

| Skill | Agent | Purpose |
|---|---|---|
| `$doc-audit` | Knowledge Agent | Analyze a Confluence space — staleness, orphans, missing labels, structure compliance. Outputs health report |
| `$doc-create` | Knowledge Agent | Create a new page following v2 template. Asks: type, space, title. Applies template + labels + metadata |
| `$doc-migrate` | Knowledge Agent | Takes a legacy page URL, reads content, proposes restructured v2 version with proper template, labels, and sections |
| `$doc-health` | Knowledge Agent | Already defined in `COMMAND_KN_DOC_HEALTH.md` — enhanced with v2 structure awareness |

### Integration with Existing Architecture

- **Knowledge Agent** → primary consumer. Uses skills to know the structure, prompts to operate on it
- **Observability Agent** → creates runbook pages from incident investigations (using runbook template)
- **DevEx Agent** → creates retrospective pages from sprint data (using retro template)
- **Excellence Default** → ad-hoc Confluence queries, delegates to Knowledge Agent for structured operations

---

## What This Enables

With structured Confluence + Knowledge Agent:
- "Find the runbook for production rollback" → agent searches `type:runbook` pages, returns structured steps
- "Is there documentation for the search component?" → agent searches by domain and component, reports gaps
- "Create an ADR for adopting Pinia" → agent creates page with ADR template, proper labels, in Decisions space
- "How stale is our documentation?" → agent runs audit, reports numbers by space/team
- "Migrate this old page" → agent reads legacy content, proposes v2 structure

Without it, the Knowledge Agent is just a Confluence search wrapper. With it, it's an actual knowledge management system.

---

## Open Questions

- [ ] Do we have access to Confluence analytics API? (page views, search queries)
- [ ] Who approves the v2 structure? Just Excellence, or needs buy-in from all teams?
- [ ] How to handle pages that don't fit any template? (catch-all "General" type?)
- [ ] Should meeting notes even be in Confluence, or move to another tool?
- [ ] How to enforce templates? Confluence admin restrictions, or just convention + agent auditing?
- [ ] What's the minimum viable structure for Phase 1 of Knowledge Agent? (don't need everything on day 1)
- [ ] How many spaces exist today? Is the audit feasible with current API access?
- [ ] Label taxonomy — should it be flat or hierarchical? (e.g., `domain:frontend:vue` vs just `domain:frontend`)
