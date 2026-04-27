---
name: weblate_translate-missing
description: |
  Detect untranslated keys in a module and propose translations using LLM. Creates a draft MR.
  Use when: user says "translate missing keys", "traducir claves pendientes", "$weblate_translate-missing",
  or a parent agent needs to fill in missing translations for a locale.
---

# Command: $weblate_translate-missing

> **Prerequisites**: Read `weblate-conventions` skill FIRST before executing this command.

Detect untranslated keys in a module and propose translations using LLM. Creates a draft MR.

## Inputs

- **module**: Weblate module name (exact). Required.
- **locale**: Target locale (e.g. `es-ES`, `de-DE`). If not provided, ask.
- **task**: Jira ticket or description for branch/commit (optional, defaults to `no-ticket`)

## Steps

1. Clone repo to temp dir (see weblate-conventions skill)
2. Verify module and locale exist
3. Find keys with `state="new"` in the target locale file
4. For each untranslated key:
   - Get the English source value (`en-GB`)
   - Use LLM to propose a translation to the target locale
   - Consider context from the key name (e.g. `label.`, `error.`, `action.` prefixes)
5. Present proposed translations to the parent agent for review:
   ```
   key: label.selectDate
   en-GB: "Select date"
   proposed (es-ES): "Seleccionar fecha"
   ```
6. After approval, update the XLIFF: set `<target>` value and `state="needs-review-translation"`
   (NOT `translated` — human must review LLM translations)
7. Commit: `feat({task}): add {locale} translations for {MODULE} ({N} keys)`
8. Push branch, create draft MR via `tuimm_subagent_gitlab`
9. Cleanup temp dir
10. Present result using the weblate-translate-missing template. Follow it EXACTLY — LAST STEP, nothing after this.

## Important

- LLM translations get `state="needs-review-translation"` (fuzzy), NEVER `translated`
- Always show proposed translations before applying — parent agent decides
- If more than 50 missing keys, ask if user wants to proceed (large MR)
