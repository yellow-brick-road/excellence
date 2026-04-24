---
name: weblate_validate
description: |
  Validate XLIFF files in a weblate module. Reports structural errors without modifying anything.
  Use when: user says "validate translations", "validar traducciones", "$weblate_validate",
  or a parent agent needs to check XLIFF integrity before a release.
---

# Command: $weblate_validate

> **Prerequisites**: Read `weblate-conventions` skill FIRST before executing this command.

Validate XLIFF files in a weblate module. Reports structural errors without modifying anything.

## Inputs

- **module**: Weblate module name (exact). If not provided, ask. Use `all` to check all modules.

## Steps

1. Clone repo to temp dir (see weblate-conventions skill)
2. Verify module exists — if `all`, iterate all modules
3. For each module, check all locale XLIFF files:
   - XML well-formedness (parse with xmllint or similar)
   - All `<trans-unit>` have `resname` attribute
   - All `<target>` have valid `state` attribute (`translated`, `new`, `needs-review-translation`)
   - Placeholder consistency: `{0}`, `{1}`, `%s`, `%d` in source must appear in target
   - No duplicate `resname` within a file
   - Key exists in ALL locales of the module (no missing keys per locale)
4. Cleanup temp dir
5. Present results using the weblate-validate template. Follow it EXACTLY — LAST STEP, nothing after this.
