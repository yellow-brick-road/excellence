
# Conventions

Naming, git, code style, and agent artifact conventions. Loaded by all TUIMM agents.

## Naming

### Files & Folders
- `kebab-case` for files and folders
- Documentation files: `SCREAMING_SNAKE_CASE.md` (e.g., `BRANCH_RULES.md`, `DECISIONS.md`)
- Vue components: `PascalCase.vue`
- Composables: `use{Name}.ts`
- Stores: `{name}.store.ts`
- Tests: `{name}.spec.ts` (colocated) or `__tests__/{name}.spec.ts`

### Code
- Variables/functions: `camelCase`
- Constants: `SCREAMING_SNAKE_CASE`
- Types/Interfaces: `PascalCase`
- CSS classes: BEM (`block__element--modifier`)

## Git

### Branches

See `GIT.md` steering for the full branch naming flow (includes CI template and semantic-release checks).

- Feature: `feature/{TICKET-ID}-{short-description}`
- Bugfix: `bugfix/{TICKET-ID}-{short-description}`
- Hotfix: `hotfix/{TICKET-ID}-{short-description}`

Example: `feature/DIS-1234-my-feature`, `feature/CDT-567-add-filter`

### Feature Branch URL

Pattern: `https://tuimusement-{BRANCH}.dev.musement.com`

Replace `/` and `_` with `-` in branch name (TUIMM enforces hyphens-only, but external branches may have underscores).
Example: `feature/DIS-1234-my-feature` → `https://tuimusement-feature-DIS-1234-my-feature.dev.musement.com`

### Commits

See `commit-conventions` skill for full format, types, and process.

### ⚠️ Semantic Release (MANDATORY)

Before creating branches, commits, or MRs: check the semantic-release config for the target repo (typically `release.config.js` or `.releaserc`). Configs vary per repo (prerelease patterns, branch naming, commit types that trigger releases). Getting it wrong breaks the release chain.

## Code Style

### TypeScript
- Strict mode enabled
- Explicit return types on public functions
- Prefer `interface` over `type` for objects
- Use `unknown` over `any`

### Vue
- Composition API with `<script setup>`
- Props: define with `defineProps<T>()`
- Emits: define with `defineEmits<T>()`
- Prefer composables over mixins

### CSS/SCSS
- BEM methodology
- Design system prefix: `hc-`
- No inline styles
- Variables in `_variables.scss`

## Testing

- Unit tests: Vitest + Vue Test Utils
- Environment: `nuxt` (auto-imports available)
- Coverage: 80% (libraries), 40-80% (frontend)
- Mock only when necessary

## Documentation

- README.md in each package/layer
- JSDoc for public APIs
- Inline comments for complex logic only
