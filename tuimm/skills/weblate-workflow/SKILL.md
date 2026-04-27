---
name: weblate-workflow
description: Shared Weblate commands for translation key management, coverage analysis, and validation. Available from tuimm_dev, tuimm_mr, tuimm_devex, and tuimm_design_system.
---

# Weblate Workflow

Shared commands for Weblate translation management. No MCP subagent — these commands work via repo cloning, XLIFF parsing, and GitLab MRs.

## Available Commands

- `$weblate_add-key` — "add translation key" — Add a translation key to a weblate module. Read the command from [commands/add-key.md](commands/add-key.md)
- `$weblate_validate` — "validate translations" — Validate translation files for consistency. Read the command from [commands/validate.md](commands/validate.md)
- `$weblate_coverage` — "translation coverage" — Translation coverage analysis per module and locale. Read the command from [commands/coverage.md](commands/coverage.md)
- `$weblate_translate-missing` — "translate missing keys" — Translate missing keys using AI. Read the command from [commands/translate-missing.md](commands/translate-missing.md)

## Templates

- [assets/templates/weblate-add-key.md](assets/templates/weblate-add-key.md)
- [assets/templates/weblate-coverage.md](assets/templates/weblate-coverage.md)
- [assets/templates/weblate-translate-missing.md](assets/templates/weblate-translate-missing.md)
- [assets/templates/weblate-validate.md](assets/templates/weblate-validate.md)
