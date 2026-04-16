---
name: devex-i18n-coverage
description: "i18n coverage report for $devex_i18n-coverage. Use when: presenting codebase i18n analysis."
---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 i18n Coverage — {DATE}
   Project: {project}
   Module(s): {modules}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Keys in code: {N}
Keys in weblate: {N}

❌ Missing (in code, not in weblate):
| # | Key | File(s) |
|---|-----|---------|

🗑️ Unused (in weblate, not in code):
| # | Key |
|---|-----|

📝 Hardcoded strings (candidates for i18n):
| # | File | Line | Text | Element |
|---|------|------|------|---------|

⚠️ Naming convention violations:
| # | Key | Issue |
|---|-----|-------|

📊 Summary:
- Coverage: {N}% of code keys have translations
- Unused keys: {N}
- Hardcoded strings: {N}
- Naming violations: {N}

RULES: This is the COMPLETE output. Omit empty sections. Do NOT add commentary or follow-up questions.
