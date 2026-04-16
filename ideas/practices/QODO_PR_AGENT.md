# Qodo PR Agent Optimization

> Status: Idea
> Author: Javier Fernández
> Created: 2026-03-05

## The Pain

TUI uses Qodo PR Agent (formerly CodiumAI / PR-Agent) org-wide for automated MR reviews. Nobody has configured it properly. The result:

- **Noise everywhere** — generic suggestions on style, naming, obvious patterns. Developers learn to ignore it
- **No team context** — Qodo doesn't know about BEM, Composition API, Nuxt conventions, or TUI-specific patterns
- **Default severity** — everything surfaces with equal weight. A missing null check looks the same as a nitpick about variable naming
- **No ignore rules** — bot PRs, bump PRs, generated code all get reviewed. Wasted compute, wasted attention
- **Zero trust** — developers dismiss Qodo comments reflexively because the signal-to-noise ratio is terrible

The tool isn't bad. The configuration is.

## The Principle

> An unconfigured AI reviewer is worse than no AI reviewer — it trains developers to ignore automated feedback.

Qodo becomes valuable when it:
1. Only speaks when it has something meaningful to say
2. Knows your team's actual standards (not generic best practices)
3. Ignores what doesn't matter
4. Enforces what does

## Current State (Audit Required)

Before changing anything, Excellence needs to understand what's deployed:

- [ ] Which Qodo version is running? (v1 / v2 — different config models)
- [ ] Is there an org-level `pr-agent-settings` repo? What's in it?
- [ ] Do any repos have local `.pr_agent.toml` files?
- [ ] Which commands run automatically on MR open? (`/describe`, `/review`, `/improve`?)
- [ ] What's the current dismissal rate? (How many Qodo comments get ignored vs acted on?)
- [ ] Is the wiki config enabled on any repo?
- [ ] What model is Qodo using? (Default or custom?)

## Proposed Configuration

### Layer 1 — Org/Group-Level Config

Create a `pr-agent-settings` repo at the GitLab group level with a shared `.pr_agent.toml`. This becomes the default for all repos unless overridden.

```toml
# ============================================================
# TUI Musement — Qodo PR Agent Configuration
# Maintained by: Excellence Frontend Guild
# Scope: All frontend repos (org/group default)
# ============================================================

# --- Commands to run on MR open ---
[gitlab]
pr_commands = [
    "/agentic_describe",
    "/agentic_review"
]

# --- Review behavior ---
[review_agent]
# Severity threshold for inline comments:
#   3 = action_required (bugs, security, logic errors)
#   2 = remediation_recommended
#   1 = informational
# Start strict. Lower to 2 once trust is established.
inline_comments_severity_threshold = 3

# Summary only — keeps the diff clean
comments_location_policy = "summary"

# Custom instructions — tell Qodo what matters
issues_user_guidelines = """
You are reviewing a Nuxt 4 / Vue 3 / TypeScript frontend codebase.

FOCUS ON:
- Bugs, logic errors, off-by-one, null/undefined access
- Security issues (XSS, injection, exposed secrets, unsafe innerHTML)
- Missing error handling (uncaught promises, missing try/catch on API calls)
- Breaking changes to public APIs (props, emits, composable return types)
- Performance regressions (unnecessary re-renders, missing key in v-for, watchers without cleanup)
- Accessibility violations (missing alt, missing aria-label, non-interactive elements with click handlers)

DO NOT COMMENT ON:
- Style preferences (naming, formatting, whitespace) — ESLint and Prettier handle this
- Minor refactoring suggestions that don't fix a bug or improve readability significantly
- Obvious code that doesn't need explanation
- Test file structure or test naming conventions
- Import ordering — auto-sorted by tooling
- Generic TypeScript advice (use unknown vs any) — covered by strict mode
"""

# --- Ignore rules ---
[config]
# Skip auto-generated PRs
ignore_pr_title = ["\\[Bump\\]", "\\[Auto\\]", "^Auto", "^chore\\(deps\\)"]

# Skip bot users
ignore_pr_authors = ["renovate-bot", "dependabot", "gitlab-bot"]

# Skip PRs with these labels
ignore_pr_labels = ["skip-review", "chore", "dependencies"]

# Skip branch-to-branch merges that aren't feature work
ignore_pr_source_branches = ["main", "master"]
ignore_pr_target_branches = ["develop"]

[ignore]
# Skip generated/vendored/build artifacts
glob = [
    "*.lock",
    "*.min.js",
    "*.min.css",
    "dist/**",
    ".nuxt/**",
    ".output/**",
    "node_modules/**",
    "coverage/**",
    "**/*.snap",
    "**/__snapshots__/**"
]
```

### Layer 2 — Best Practices File (The Big Win)

A `best_practices.md` file teaches Qodo your actual standards. When code violates them, suggestions get labeled "Organization best practice" — not generic AI noise.

Qodo supports hierarchical best practices via the `pr-agent-settings` repo:

```
pr-agent-settings/
├── .pr_agent.toml                     # Config from Layer 1
├── metadata.yaml                      # Maps repos to best practice paths
└── codebase_standards/
    ├── global/
    │   └── best_practices.md          # All frontend repos
    ├── groups/
    │   ├── nuxt_apps/
    │   │   └── best_practices.md      # Nuxt application repos
    │   └── shared_libraries/
    │       └── best_practices.md      # @dx/* packages
    └── b2c-tuimusement-frontend/
        └── best_practices.md          # Repo-specific overrides
```

With `metadata.yaml`:

```yaml
# Standalone repos
b2c-tuimusement-frontend:
  best_practices_paths:
    - "b2c-tuimusement-frontend"
    - "groups/nuxt_apps"

# Library repos
b2c-nuxt-libraries:
  best_practices_paths:
    - "groups/shared_libraries"

# Other Nuxt apps get the group default
search-component-fe:
  best_practices_paths:
    - "groups/nuxt_apps"
```

#### Global `best_practices.md` (Draft)

Content sourced from existing TUI conventions. Under 800 lines, with before/after examples.

```markdown
# TUI Frontend Best Practices

## Vue Components

### Use Composition API with `<script setup>`
All new components must use `<script setup>` with TypeScript.

Before:
```vue
<script>
export default {
  props: { title: String },
  data() { return { count: 0 } }
}
</script>
```

After:
```vue
<script setup lang="ts">
interface Props {
  title: string
}
defineProps<Props>()
const count = ref(0)
</script>
```

### Define props with TypeScript interface
Never use runtime prop validation. Use `defineProps<T>()`.

Before:
```ts
const props = defineProps({
  items: { type: Array, required: true },
  loading: { type: Boolean, default: false }
})
```

After:
```ts
interface Props {
  items: Item[]
  loading?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  loading: false
})
```

### Emit events with typed interface
Use `defineEmits<T>()` with explicit event signatures.

Before:
```ts
const emit = defineEmits(['update', 'close'])
```

After:
```ts
interface Emits {
  update: [value: string]
  close: []
}
const emit = defineEmits<Emits>()
```

## Error Handling

### Always handle async errors
API calls and async operations must have error handling.

Before:
```ts
const data = await $fetch('/api/bookings')
```

After:
```ts
try {
  const data = await $fetch('/api/bookings')
} catch (error) {
  logger.error('Failed to fetch bookings', { error })
  throw createError({ statusCode: 500, message: 'Booking fetch failed' })
}
```

### Never swallow errors silently
Empty catch blocks are not acceptable.

Before:
```ts
try { await save() } catch (e) {}
```

After:
```ts
try {
  await save()
} catch (error) {
  logger.error('Save failed', { error })
  showErrorNotification('Could not save changes')
}
```

## CSS / BEM

### Follow BEM naming convention
CSS classes must follow `block__element--modifier` pattern.

Before:
```scss
.booking-card .title { }
.booking-card .title.active { }
```

After:
```scss
.booking-card__title { }
.booking-card__title--active { }
```

## Accessibility

### Interactive elements must be keyboard accessible
Click handlers on non-interactive elements need keyboard equivalents.

Before:
```vue
<div @click="handleAction">Click me</div>
```

After:
```vue
<button type="button" @click="handleAction">Click me</button>
```

### Images must have alt text
All `<img>` tags require meaningful alt text or empty alt for decorative images.

Before:
```vue
<img :src="hotel.image" />
```

After:
```vue
<img :src="hotel.image" :alt="hotel.name" />
```

## Reactivity

### Don't mutate props
Never modify props directly. Emit events or use local state.

Before:
```ts
props.items.push(newItem)
```

After:
```ts
emit('update:items', [...props.items, newItem])
```

### Clean up watchers and listeners
Side effects in composables must be cleaned up.

Before:
```ts
onMounted(() => {
  window.addEventListener('resize', handleResize)
})
```

After:
```ts
onMounted(() => {
  window.addEventListener('resize', handleResize)
})
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
```
```

### Layer 3 — Repo-Level Overrides

Individual repos can add a local `.pr_agent.toml` to override specific settings. For example, a library repo might want stricter thresholds:

```toml
[review_agent]
# Libraries need stricter review — they're shared across teams
inline_comments_severity_threshold = 2
comments_location_policy = "both"
```

### Layer 4 — Rules System (Future — Track)

Qodo 2.1 introduced a Rules System that auto-generates enforcement rules from accepted suggestions and manages them via a central portal. Key capabilities:

- Auto-discovers patterns from accepted code suggestions
- Generates rules from natural language or existing standards
- Scoped enforcement: org → group → repo
- Analytics on rule impact and health
- Detects duplicates, conflicts, and outdated rules

**Caveat:** Currently in beta, GitHub only. GitLab support announced but not shipped. When it lands, this becomes the evolution of the `best_practices.md` approach — same intent, better tooling.

**Action:** Monitor [Qodo changelog](https://docs.qodo.ai/qodo-documentation/whats-new/changelog) for GitLab Rules System support.

## Rollout Plan

### Phase 1 — Audit (Week 1)

- [ ] Check current Qodo version and deployment model
- [ ] Inventory existing `.pr_agent.toml` files across repos
- [ ] Collect developer feedback: what Qodo comments are useful vs noise?
- [ ] Measure current dismissal rate if possible
- [ ] Identify who has admin access to Qodo org settings

### Phase 2 — Configure (Week 2)

- [ ] Create `pr-agent-settings` repo at GitLab group level
- [ ] Deploy org-level `.pr_agent.toml` (Layer 1)
- [ ] Write and deploy global `best_practices.md` (Layer 2)
- [ ] Set up `metadata.yaml` with repo-to-group mappings
- [ ] Test on one repo first — validate noise reduction

### Phase 3 — Pilot (Weeks 3-4)

- [ ] Enable on 2-3 repos across different teams
- [ ] Collect feedback: is the signal-to-noise ratio better?
- [ ] Iterate on `best_practices.md` based on false positives
- [ ] Adjust severity threshold if needed (3 → 2 if trust improves)
- [ ] Document any repo-specific overrides needed

### Phase 4 — Rollout (Week 5+)

- [ ] Enable for all frontend repos
- [ ] Communicate changes to all teams (guild channel, all-hands)
- [ ] Publish guide: "How to customize Qodo for your repo"
- [ ] Set up quarterly review cycle for `best_practices.md` updates

## Measuring Success

| Metric | Before | Target |
|--------|--------|--------|
| Qodo comment dismissal rate | ~80%+ (estimated) | < 30% |
| Actionable suggestions per MR | Unknown | Track and trend upward |
| Developer sentiment ("is Qodo useful?") | Negative / ignored | Neutral → Positive |
| Time from MR open to first human review | No change expected | Qodo catches blockers before human reviews |
| False positive rate | High | < 20% of inline comments |

## Connection to Excellence

This is textbook Excellence:

- **Cross-cutting** — one config improves all repos, all teams
- **No product ownership** — tooling configuration, not features
- **Reusable** — `best_practices.md` encodes guild knowledge once, enforced everywhere
- **Measurable** — dismissal rate, sentiment, false positives
- **Low effort, high impact** — a few files in one repo change the experience for every developer
- **Prevents fragmentation** — shared standards instead of per-team guessing

### Synergy with Other Practices

- **Testing Philosophy** → `best_practices.md` can reference testing patterns (behavior over implementation)
- **Pipeline Optimization** → Qodo review runs in CI; lean config = faster pipeline
- **Repo Strategy** → shared `pr-agent-settings` repo aligns with centralized config approach
- **Excellence MR Agent** → Qodo handles automated first-pass; Excellence MR handles deep human-like review. Complementary, not competing

## Open Questions

- [ ] Which Qodo version is deployed? v1 and v2 have different config models
- [ ] Who manages the Qodo license/deployment? DevOps? Platform?
- [ ] Is there budget/appetite to upgrade to Qodo 2.1 for the Rules System?
- [ ] Can we get access to Qodo analytics/portal to measure dismissal rates?
- [ ] Should `best_practices.md` be maintained by Excellence alone or accept PRs from teams?
- [ ] How does Qodo interact with existing SonarQube quality gates? Overlap? Complement?
- [ ] Are there other verticals (backend, mobile) that could benefit from the same approach?

## References

- [Qodo Configuration Overview](https://docs.qodo.ai/qodo-documentation/code-review/concepts/configuration-overview)
- [Qodo Configuration File](https://docs.qodo.ai/qodo-documentation/code-review/concepts/configuration/configuration-file)
- [Qodo Best Practices](https://docs.qodo.ai/qodo-documentation/code-review/qodo-merge/features/best-practices)
- [Qodo Rule Enforcement](https://docs.qodo.ai/qodo-documentation/code-review/concepts/rule-enforcement)
- [Qodo Ignore Content](https://docs.qodo.ai/qodo-documentation/code-review/concepts/ignore-content-from-analysis)
- [Lean vs Verbose Tutorial](https://docs.qodo.ai/qodo-documentation/code-review/tutorials/shape-the-review-experience-lean-vs-verbose)
