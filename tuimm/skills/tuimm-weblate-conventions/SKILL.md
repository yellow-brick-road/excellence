---
name: tuimm-weblate-conventions
description: |
  Weblate translations repo reference for TUI Musement i18n workflow.
  Use when: executing weblate commands ($weblate_add-key, $weblate_validate, $weblate_coverage, $weblate_translate-missing).
  Contains: repo URL, clone pattern, module discovery, XLIFF tooling, branch/MR conventions, XLIFF format reference.
---

# Weblate Conventions

## Repo

- URL: `git@ssh.source.tui:dx/distribution/discovery/weblate-translations.git`
- 78 modules (as of Apr 2026)
- Each module = set of XLIFF files, one per locale (e.g. `b2c-tui-fe.en-GB.xliff`)

## Clone Pattern

All weblate commands use a disposable temp clone under `~/.kiro/temp/weblate/` (see TUIMM_GIT.md § Workspace Conventions):

```bash
WORK_DIR="$HOME/.kiro/temp/weblate/weblate-$(date +%s)"
mkdir -p "$HOME/.kiro/temp/weblate"
git clone git@ssh.source.tui:dx/distribution/discovery/weblate-translations.git "$WORK_DIR"
cd "$WORK_DIR"
```

Cleanup after: `rm -rf "$WORK_DIR"`

## Module Discovery

```bash
# List all modules
find . -maxdepth 1 -name "*.en-GB.xliff" | sed 's|./||; s/.en-GB.xliff$//'

# Check if module exists
test -f "${MODULE}.en-GB.xliff" && echo "exists" || echo "not found"
```

Module name must be exact (e.g. `search-component-fe`, NOT `search-component`).

## Tooling

The repo includes `packages/xliff/` with TypeScript utilities:

| Command | Description |
|---------|-------------|
| `getModuleNames` | List all module names |
| `getModuleLangs` | List locales for a module |
| `addFullTranslationsToModule` | Add key with translated value |
| `addTranslationsToModule` | Add key (state=new, pending) |
| `removeTranslationsFromModule` | Remove key from all locales |
| `cloneModule` | Clone a module to a new name |
| `cloneTranslationsBetweenModules` | Copy translations between modules |
| `createNewModule` | Create a new empty module |
| `deleteModule` | Delete a module |

Run via: `npx ts-node --transpile-only packages/xliff/commands/<command>.ts`

## Branch & MR

- Branch: `feature/{task}-{description}`
- Commit: `feat({task}): {description}`
- MR: always DRAFT, target `master`
- Push from temp clone is safe (disposable)
- Create MR via `tuimm_subagent_gitlab` (project: `dx/distribution/discovery/weblate-translations`)

## XLIFF Format

Each file is XLIFF 1.2. Translation units:
```xml
<trans-unit id="..." resname="label.myKey">
  <source>Source text</source>
  <target state="translated">Translated text</target>
</trans-unit>
```

States: `translated`, `new` (pending), `needs-review-translation` (fuzzy)
