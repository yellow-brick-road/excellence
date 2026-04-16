# Command: $content-audit

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


> Command name: `devex_content_audit`
> Description: Audit Contentful content models and entries. Detect environment drift, unused content types, generate TypeScript interfaces.
> Agent: DevEx

## Trigger

`$content-audit` or "content audit", "content health", "contentful check"

## Workflow

1. `subagent_contentful` → list content types per environment
2. `subagent_contentful` → compare content models across environments (dev, staging, prod)
3. `subagent_contentful` → detect unused content types (no entries)
4. `subagent_contentful` → find empty or incomplete entries
5. `subagent_contentful` → check content freshness (last updated)
6. Detect breaking changes between environments
7. Generate TypeScript interfaces from content types

## Output

- Content types per environment
- Environment drift (differences between dev/staging/prod)
- Unused content types
- Empty/incomplete entries
- Content freshness report
- Breaking changes detected
- Generated TypeScript interfaces

## Phase

Phase 2 (requires Contentful subagent)
