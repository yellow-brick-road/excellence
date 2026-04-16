# Command: $release

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


> Command name: `qg_release`
> Description: Analyze changes since last release, propose version bump with reasoning, generate changelog, and execute publish workflow.
> Agent: Quality Guardian

## Trigger

`$release` or `$release [package-name]` (for monorepos)

## Workflow

1. Determine scope: single package or monorepo package
2. `subagent_gitlab` → find last release tag, get all MRs merged since
3. Analyze actual code diff (last tag → HEAD):
   - New/removed/changed exports
   - Modified type signatures and interfaces
   - Added/removed component props
   - Dependency changes in `package.json`
4. `subagent_jira` → fetch ticket details for linked MRs (context for changelog)
5. Classify changes:
   - **Major** — removed exports, changed public interfaces, breaking prop changes
   - **Minor** — new exports, new features, new component props
   - **Patch** — bug fixes, internal refactors, dependency bumps
6. Propose version bump with reasoning (show what triggered the classification)
7. Generate changelog grouped by: Breaking Changes, Features, Fixes, Internal
8. Present proposal to user for review/adjustment
9. On approval:
   - Bump `package.json` version
   - Update `CHANGELOG.md`
   - Commit + tag via `subagent_gitlab`
   - Publish via `subagent_npm` (existing TARS subagent — bash wrapper for npm/pnpm, no dedicated spec needed)
   - `subagent_jira` → comment on related tickets with release info

## Output

- Version proposal with reasoning
- Generated changelog (markdown)
- On approval: published package, git tag, updated changelog, Jira comments

## Monorepo Behavior

When run in a monorepo (e.g., `b2c-nuxt-libraries`):
- Without package name: analyze all packages, propose releases for those with changes
- With package name: scope to that package only
- Cross-package impact: if package A changed and package B depends on A, flag B for potential bump

## Phase

Phase 2 (ships with Quality Guardian)
