---
name: obs-scan-summary
description: "EXACT output format for $obs_dd-scan. Follow this template literally — no additions, no modifications, no extra sections."
---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 Datadog Scan — {DAY} {DATE} {TIME}
   Window: {FROM} → {TO}
   Service: {service}
   Repo: {repo}
   Version: {version}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 REAL USERS:

🔔 NEEDS INVESTIGATION:
| # | Error | Count | Since | Status | Severity |
|---|-------|------:|-------|--------|----------|
| 1 | {error} | {n} | {since} | {status} | {severity} |

⚠️ WATCH:
| # | Error | Count | Status | Severity |
|---|-------|------:|--------|----------|
| 1 | {error} | {n} | {status} | {severity} |

✅ RESOLVED:
- "{error}" (was {n})

🤖 BOTS:
| # | Error | Count | Severity |
|---|-------|------:|----------|
| 1 | {error} | {n} | {severity} |

📊 Summary:
- Errors: {X} users + {Y} bots
- Patterns: {total} (new: {n}, recurring: {n}, spikes: {n}, resolved: {n})
- Service: {service} {🔴|🟡|🟢}

🎯 Actions:
- {one-line actionable recommendation per CRITICAL/HIGH item}

RULES: This is the COMPLETE output. Do NOT add sections (no time distribution, no bar charts, no extra columns). Do NOT use markdown headers (##). Do NOT add a "Notas" column. NEEDS INVESTIGATION = CRITICAL/HIGH or NEW/SPIKE. WATCH = MEDIUM/LOW and RECURRING. Omit empty sections. Keep each row to one line — no line breaks inside table cells.
