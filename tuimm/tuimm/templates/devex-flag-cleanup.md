---
name: devex-flag-cleanup
description: "Flag cleanup report for $devex_flag-cleanup. Use when: presenting stale flags analysis."
---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚩 Flag Cleanup Report — {DATE}
   Total flags: {N}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏰ Stale (3+ months, no activity):
| # | Flag Key | Age | Last Toggle | Rollout |
|---|----------|-----|-------------|---------|

✅ 100% Rollout (remove from code):
| # | Flag Key | At 100% Since | Files Using It |
|---|----------|---------------|----------------|

👻 Orphan — in ConfigCat, not in code:
| # | Flag Key | Age |
|---|----------|-----|

💀 Orphan — in code, not in ConfigCat:
| # | Flag Key | Files |
|---|----------|-------|

📊 Summary:
- Cleanup candidates: {N}
- Estimated effort: {hours}

RULES: This is the COMPLETE output. Omit empty sections. Do NOT add commentary or follow-up questions.
