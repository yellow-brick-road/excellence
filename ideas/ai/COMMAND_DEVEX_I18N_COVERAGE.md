# Command: $i18n-coverage

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


> Command name: `devex_i18n_coverage`
> Description: Translation coverage report across Weblate modules and locales. Detect untranslated keys, placeholder mismatches, naming violations.
> Agent: DevEx

## Trigger

`$i18n-coverage` or "i18n coverage", "translation coverage", "translations"

## Workflow

1. `subagent_weblate` → get translation stats per module and locale
2. `subagent_weblate` → find untranslated keys per locale
3. `subagent_weblate` → detect placeholder mismatches ({0}, {1})
4. Scan codebase → find `$t('key')` calls and verify keys exist in Weblate
5. Detect hardcoded strings in Vue templates that should be i18n keys
6. Check key naming conventions (label., error., action. prefixes)
7. Generate coverage report

## Output

- Coverage % per module and locale
- Untranslated keys per locale (count + list)
- Placeholder mismatches
- Keys in code but not in Weblate
- Keys in Weblate but not in code
- Naming convention violations
- Hardcoded strings detected

## Phase

Phase 2 (requires Weblate subagent)
