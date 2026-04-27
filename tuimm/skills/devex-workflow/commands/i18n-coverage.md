---
name: devex_i18n-coverage
description: "Codebase-level i18n analysis. Use when: user says 'i18n coverage', 'i18n audit', or 'translation audit'."
---

# Command: $devex_i18n-coverage

Codebase-level i18n analysis — cross-reference code with weblate, detect hardcoded strings, naming conventions.

Different from `$weblate_coverage` which reports translation stats per locale. This command analyzes how the project uses translations.

## Services

Ask the user which project and weblate module to analyze. If not specified, ask before proceeding.

## Process

### 1. Scan Code for Translation Keys

Search the project codebase for i18n usage patterns:
- `$t('key')` and `t('key')` calls in `.vue` and `.ts` files
- `:label="$t('key')"` and similar template bindings
- `i18n.t('key')` calls
- Collect all unique keys referenced in code

### 2. Get Weblate Keys

Clone weblate repo to temp dir (see weblate-conventions skill):
- Parse XLIFF files for the relevant module(s)
- Collect all defined translation keys from `en-GB` (source locale)

### 3. Cross-Reference

Compare code keys vs weblate keys:
- **In code, not in weblate** → missing translations, will show raw key to users
- **In weblate, not in code** → unused keys, cleanup candidates

### 4. Detect Hardcoded Strings

Scan Vue templates for likely hardcoded user-facing strings:
- Text content in elements (`<p>`, `<span>`, `<h1>`-`<h6>`, `<button>`, `<label>`, `<a>`)
- `placeholder`, `title`, `alt`, `aria-label` attributes with literal strings
- Exclude: CSS classes, data attributes, component names, boolean attributes
- Flag as candidates for i18n extraction

### 5. Naming Conventions

Check collected keys against naming conventions:
- Expected prefixes: `label.`, `error.`, `action.`, `placeholder.`, `message.`
- Detect inconsistencies: same concept with different prefixes across modules
- Flag keys with no prefix or non-standard prefix

### 6. Cleanup Temp Dir

Remove cloned weblate repo.

### 7. Output

Present results using the devex-i18n-coverage template. Follow it EXACTLY — LAST STEP, nothing after this.
