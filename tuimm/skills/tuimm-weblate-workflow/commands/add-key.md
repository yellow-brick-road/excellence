---
name: weblate_add-key
description: |
  Add a translation key to a weblate module. Creates a draft MR for review.
  Use when: user says "add translation key", "añadir clave", "$weblate_add-key",
  or a parent agent needs to add i18n keys to a weblate module.
---

# Command: $weblate_add-key

> **Prerequisites**: Read `tuimm-weblate-conventions` skill FIRST before executing this command.

Add a translation key to a weblate module. Creates a draft MR for review.

## Inputs

- **module**: Weblate module name (exact). If not provided or not found, list available modules and ask.
- **key**: Translation key (e.g. `label.selectDate`)
- **value**: English translation value
- **task**: Jira ticket or description for branch/commit (optional, defaults to `no-ticket`)

## Steps

1. Clone repo to temp dir (see tuimm-weblate-conventions skill)
2. Verify module exists — if not, list modules and ask
3. Create branch: `feature/{task}-{key-with-dots-as-dashes}`
4. Add key using repo tooling (verify import paths match actual repo structure):
   ```bash
   npx ts-node --transpile-only -e "
     const { getModuleLangs } = require('./packages/xliff/commands/getModuleLangs');
     const { openXliffModule } = require('./packages/xliff/WeblateXliff/WeblateXliff');
     async function main() {
       const langs = getModuleLangs('{MODULE}');
       for (const lang of langs) {
         const xliff = await openXliffModule('{MODULE}', lang);
         if (lang.startsWith('en-')) {
           xliff.addFullTranslation('{KEY}', '{VALUE}');
         } else {
           xliff.addTranslationKey('{KEY}');
         }
         xliff.save();
       }
     }
     main();
   "
   ```
5. Verify: `grep resname="{KEY}" {MODULE}.en-GB.xliff`
6. Commit: `feat({task}): add {KEY} translation key to {MODULE}`
7. Push branch
8. Create draft MR via `tuimm_subagent_gitlab` (project: `dx/distribution/discovery/weblate-translations`, target: `master`)
9. Cleanup temp dir
10. Present result using the weblate-add-key template. Follow it EXACTLY — LAST STEP, nothing after this.
