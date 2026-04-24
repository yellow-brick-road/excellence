---
name: weblate_coverage
description: |
  Report translation coverage per module and locale.
  Use when: user says "translation coverage", "cobertura de traducciones", "$weblate_coverage",
  or a parent agent needs i18n coverage metrics for a sprint report or audit.
---

# Command: $weblate_coverage

> **Prerequisites**: Read `weblate-conventions` skill FIRST before executing this command.

Report translation coverage per module and locale.

## Inputs

- **module**: Weblate module name (exact). If not provided, report all modules. Use `all` for full report.

## Steps

1. Clone repo to temp dir (see tuimm-weblate-conventions skill)
2. For each module, for each locale:
   - Count total `<trans-unit>` entries
   - Count by state: `translated`, `new`, `needs-review-translation`
   - Calculate % translated
3. Cleanup temp dir
4. Present results using the weblate-coverage template. Follow it EXACTLY — LAST STEP, nothing after this.
