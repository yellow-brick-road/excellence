---
name: obs-investigate
description: "Investigation report for $obs_dd-investigate. Use when: presenting root cause analysis."
---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 Investigation — {error_pattern}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Error Profile:
- Service: {service}
- First seen: {timestamp}
- Frequency: {count} in {time_range}
- Affected: {endpoints/pages}

🔗 Probable Cause:
{hypothesis with evidence}

📝 Timeline:
- {timestamp} — {event}

🛠️ Recommended Action:
{what to do — fix, rollback, flag toggle, or escalate}

📎 References:
- Datadog: {log_url}
- MR: {mr_url or "—"}
- File: {file:line}

RULES: This is the COMPLETE output. Do NOT add commentary, follow-up suggestions, or questions after References.
