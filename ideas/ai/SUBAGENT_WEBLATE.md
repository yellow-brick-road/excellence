# Idea: Weblate Subagent

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


## Title

Tool subagent for Weblate translation management via TUI MCP Gateway.

## Context

API wrapper for Weblate. Handles translation keys, locales, and i18n workflow. Connected through the centralized MCP Gateway. Weblate manages translations for all TUI Musement frontend modules.

Based on existing `subagent_weblate` which uses a bash script (`add-key.sh`) to add keys. The MCP version would use the Weblate API directly for full CRUD operations.

## MCP Connection

Via TUI MCP Gateway → Weblate API

## Capabilities

### Keys
- Add translation keys (across all locales, source locale translated, others state=new)
- Remove translation keys
- Rename keys with propagation across all locales
- Bulk key operations (add/remove/rename multiple)
- Get key details (value per locale, state, last updated)
- Search keys by name, value, or state

### Translations
- Get translations per locale
- Update translation values
- Get translation state (translated, fuzzy, new, approved)
- Mark translations as reviewed/approved
- Get untranslated keys per locale

### Modules/Components
- List Weblate components (modules)
- Get component statistics (coverage per locale)
- Get component configuration
- Compare translations across components

### Locales
- List configured locales
- Get locale statistics (% translated, % reviewed)
- Get locale-specific issues (placeholder mismatches, length violations)

### Intelligence (light)
- Detect untranslated keys per locale and module
- Find inconsistent translations (same source, different translations)
- Detect placeholder mismatches ({0}, {1} in source but not in translation)
- Key naming convention validation (label., error., action. prefixes)
- Calculate translation coverage per module and locale
- Detect duplicate keys across modules

## Available Modules

Current known modules (check with `glob ~/work/weblate-translations/*.en-GB.xliff`):
- `search-component-fe` — Base search component (shared)
- `search-component-b2c-msm-fe` — B2C MSM specific
- `b2c-tui-fe` — Main B2C frontend
- `activity-card-fe` — Activity cards

## Used By

- DevEx Agent → translation management, i18n coverage, key lifecycle
- Design System Agent → extract text from Figma and create keys
- Excellence Default → ad-hoc translation operations
