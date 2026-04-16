---
name: mr-list-summary
description: "MR briefing output format. Use when: presenting $mr_list results."
---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 MR Briefing — {DAY} {DATE} {TIME}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔔 NEEDS YOUR ATTENTION:

| MR | Repo | Title | Author | Why |
|----|------|-------|--------|-----|

⏳ WAITING (no action needed):

| MR | Repo | Title | Author | Status |
|----|------|-------|--------|--------|

🤖 Bot MRs:

| MR | Repo | Title | Days | Issue |
|----|------|-------|------|-------|

📬 My MRs:

| MR | Repo | Title | Approvals | Status |
|----|------|-------|-----------|--------|

📊 Summary:
- Action needed: X MRs to review across Y repos
- Waiting: X MRs (details)
- Bot MRs: X (details)
- My MRs: X active, X drafts

RULES: MR column = plain number only (e.g. `77`), never a markdown link. This is the COMPLETE output. Do NOT add anything after the Summary section. No commentary, no recommendations, no "things that stand out", no follow-up suggestions, no questions. Omit empty sections. End output immediately after the last Summary bullet.
