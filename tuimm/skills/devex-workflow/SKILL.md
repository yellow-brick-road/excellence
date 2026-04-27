---
name: devex-workflow
description: Developer experience workflow commands for feature flags, i18n, and content model management. Use when auditing flags, translation coverage, or Contentful models.
---

# DevEx Workflow

Commands for the tuimm-devex agent: feature flag lifecycle, translation management, and content model auditing.

## Available Commands

- `$devex_flag-cleanup` — "flag cleanup", "stale flags" — Detect stale and orphan feature flags. Read the command from [commands/flag-cleanup.md](commands/flag-cleanup.md)
- `$devex_i18n-coverage` — "i18n coverage", "translation audit" — Translation coverage analysis per module and locale. Read the command from [commands/i18n-coverage.md](commands/i18n-coverage.md)
- `$devex_content-audit` — "content audit", "contentful check" — Contentful content model audit. Read the command from [commands/content-audit.md](commands/content-audit.md)

## Templates

- [assets/templates/devex-flag-cleanup.md](assets/templates/devex-flag-cleanup.md)
- [assets/templates/devex-i18n-coverage.md](assets/templates/devex-i18n-coverage.md)
- [assets/templates/devex-content-audit.md](assets/templates/devex-content-audit.md)
