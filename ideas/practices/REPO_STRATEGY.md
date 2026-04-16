# Repo Strategy & Shared Components

> Status: Idea
> Author: Javier Fernández
> Created: 2026-03-04

## The Pain

Frontend code at TUI Musement is scattered across too many repositories, owned by too many teams, with no shared home for common functionality.

### Symptoms

- **Cross-cutting changes are expensive** — adding a tracking pixel, updating an analytics config, or changing a shared behavior requires touching 3+ repos with different structures, different patterns, and different owners
- **No single source of truth for shared components** — each team builds their own version of common UI elements
- **Inconsistent patterns across repos** — different teams, different conventions, different architectures. Same company
- **Sub-repos pretending to be reusable** — some repos are structured as if they'll be published to npm, but they're private, used by one or two consumers. The overhead of "reusability" (generic configs, abstracted tokens, decoupled styles) adds complexity without delivering actual reuse
- **False generalization** — private components using generic design tokens instead of corporate ones, abstracting away brand identity that is constant across the entire organization. Reusability theater for code that will never leave the company
- **npm update fatigue** — shared code distributed as npm packages means every consumer must bump versions, update lockfiles, and redeploy. A one-line change becomes N merge requests

## The Principle

> Shared code should live in shared places. Private code should use private conventions. Don't optimize for a world that doesn't exist.

- If a component is used across verticals → it belongs in a shared library
- If a component is used by one team → it belongs in that team's repo
- If a component is private → it should use corporate tokens, not generic ones
- If a repo exists "for reusability" but has 1-2 consumers → it probably shouldn't be a separate repo

## Proposed Model

### 1. Shared Component Library (Nuxt Module)

A single Nuxt module — similar in concept to PrimeVue or Nuxt UI — that provides:

- **Shared UI components** — common elements used across verticals
- **Corporate design tokens** — colors, spacing, typography. The real ones, not abstracted placeholders
- **Shared configurations** — tracking, analytics, feature flag setup, error handling
- **Composables** — shared business logic (auth, i18n helpers, API patterns)

This is the evolution of `@dx/b2c-foundation` — a proper, well-structured Nuxt module that teams install and use.

#### Key Decisions

- **Nuxt module, not npm component library** — auto-imports, runtime config, server integration. Components without a framework are components without context
- **Corporate-first, not generic-first** — use TUI colors, TUI tokens, TUI conventions. This is not an open-source project
- **Versioned but not over-versioned** — semver for breaking changes, but don't force teams to pin patch versions

### 2. Repo Consolidation Criteria

Not every repo needs to die. But every repo needs to justify its existence:

| Question | If Yes | If No |
|----------|--------|-------|
| Is this used by 3+ teams? | Candidate for shared library | Stay in team repo |
| Is this a standalone deployable? | Keep as repo | Consider merging |
| Does this have its own release cycle? | Keep as repo | Consider merging |
| Is this structured for npm but private? | Evaluate — probably over-engineered | — |
| Does this duplicate something in another repo? | Consolidate | — |

### 3. Migration Strategy

No big bang. Migrate on touch:

1. **Audit** — inventory all frontend repos, map ownership, consumers, and overlap
2. **Classify** — shared (→ library), team-owned (→ stays), orphaned (→ archive), duplicated (→ consolidate)
3. **Build the shared module** — start with the most painful shared components (the ones causing the 3-repo changes)
4. **Migrate incrementally** — when a team touches a shared component, move it to the library
5. **Archive dead repos** — repos with no commits in 6+ months and no active consumers get archived

## Analysis Required

### Phase 1 — Audit

- [ ] Inventory all frontend repos (GitLab groups, subgroups)
- [ ] Map repo → team ownership
- [ ] Map repo → consumers (who depends on what)
- [ ] Identify duplicated components across repos
- [ ] Identify repos with < 2 consumers
- [ ] Identify repos with no commits in 6+ months
- [ ] Map current shared packages (`@dx/*`) and their actual usage

### Phase 2 — Propose

- [ ] Define the shared Nuxt module structure
- [ ] List first batch of components to migrate (highest pain, most consumers)
- [ ] Define contribution model (who can add to the shared library, review process)
- [ ] Define deprecation path for replaced repos/packages

### Phase 3 — Implement

- [ ] Create the shared Nuxt module repo
- [ ] Migrate first batch of components
- [ ] Set up CI/CD for the shared module (versioning, publishing, changelog)
- [ ] Pilot with one vertical
- [ ] Roll out

## Auto-Propagation (AI-Powered Updates)

When the shared library publishes a new version (via `$release`), consumer repos should update themselves — not like dumb Renovate that bumps a number, but with full AI intelligence.

### The Flow

1. **Shared library publishes** → `$release` generates rich changelog (AST diff, Jira context, breaking change details)
2. **Bot Service detects** → webhook on npm publish or GitLab tag
3. **Per consumer repo, the bot:**
   a. Reads the changelog — knows exactly what changed (new props, removed exports, changed interfaces)
   b. Scans consumer codebase for usage of changed APIs
   c. Classifies impact: SAFE / AUTO-FIXABLE / NEEDS MIGRATION

4. **Creates MR with intelligence:**

| Impact | MR Content |
|--------|-----------|
| SAFE | Version bump + comment explaining why it's safe ("you don't use any changed APIs") |
| AUTO-FIXABLE | Version bump + code changes already applied + comment explaining each fix |
| NEEDS MIGRATION | Version bump draft + migration guide + Jira ticket with effort estimate |

### What Makes This Different from Renovate

- **Full context on both sides** — the agent published the library AND knows the consumer. Renovate only sees version numbers
- **Auto-fix capability** — if a prop was renamed from `isOpen` to `open`, the agent finds every `<Modal :is-open="...">` and rewrites it. Renovate can't touch your code
- **Rich MR comments** — not "bumps @dx/shared from 2.1.0 to 2.2.0" but "2.2.0 adds `useBooking` composable and deprecates `isOpen` prop on Modal (renamed to `open`). Your repo uses Modal in 3 files — all updated in this MR"
- **Cross-consumer awareness** — if 8 repos consume the library, the bot knows which ones are affected and which aren't. No noise

### Auto-Fix Scope

The agent can auto-fix:
- Renamed props/events/slots (find & replace with AST awareness)
- Renamed exports/composables
- Changed import paths
- Deprecated API replaced by new equivalent
- Added required props with sensible defaults

The agent should NOT auto-fix:
- Removed features with no replacement
- Changed behavior (same API, different result)
- Major architectural changes

### Progressive Autonomy

Same 3 levels as Release Strategy:

1. **Level 1** — Bot creates MR, human reviews and merges
2. **Level 2** — SAFE updates auto-merge after CI passes. AUTO-FIXABLE wait for human
3. **Level 3** — SAFE and AUTO-FIXABLE auto-merge. Only NEEDS MIGRATION requires human

### Connection to Existing Skills

- `$release` (Quality Guardian) → publishes with rich context, feeds the changelog
- `$dependency-scan` (Quality Guardian) → proactive scanning, extended for internal packages
- `$dependency-review` (Quality Guardian) → triages the generated MRs
- Autonomous Bot Service → event-driven trigger on publish
- `DEPENDENCY_DECISIONS.md` → blocked updates tracked in governance log

## Antipatterns to Eliminate

- **"Reusable" repos with 1 consumer** — if nobody else uses it, it's not reusable, it's isolated
- **Generic tokens in private code** — your brand colors are your brand colors. Don't abstract them behind `--color-neutral-400` when you mean `--tui-grey`
- **Sub-repos for the sake of separation** — splitting code into repos adds coordination cost. Only worth it when the code has genuinely independent lifecycles
- **npm-as-deployment for internal code** — every version bump is a tax on every consumer. Nuxt layers/modules with direct git references can reduce this friction

## Connection to Excellence

This is core Excellence territory:

- **Cross-cutting problem** — repo fragmentation affects every vertical
- **Reusable solution** — one shared library, not N per-team copies
- **Reduces friction** — cross-cutting changes go from N repos to 1
- **Measurable** — number of repos, time to implement cross-cutting changes, duplication ratio
- **Guild-driven** — Excellence defines the model, teams adopt incrementally

### KPIs

- Time to implement a cross-cutting change (tracking, config, shared component update)
- Number of active frontend repos (target: reduce by consolidation)
- Shared library adoption rate (% of verticals using it)
- Duplicated component count across repos

## Open Questions

- [ ] What's the full inventory of frontend repos today? How many are active?
- [ ] Who owns `@dx/b2c-foundation` and the existing shared packages?
- [ ] Is there appetite for a monorepo approach, or do teams prefer separate repos consuming a shared module?
- [ ] What's the governance model for the shared library? Open contribution with review, or Excellence-owned?
- [ ] How do we handle the transition period where both old repos and new library coexist?
