---
name: devex-content-audit
description: "Content audit report for $devex_content-audit. Use when: presenting Contentful health check."
---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Content Audit — {DATE}
   Space: {space_id}
   Environments: {env1}, {env2}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Content Types: {N}

⚠️ Environment Drift:
| # | Content Type | Issue | Env A | Env B |
|---|-------------|-------|-------|-------|

🗑️ Unused (0 entries):
| # | Content Type | Created | Last Updated |
|---|-------------|---------|--------------|

⏰ Stale (6+ months no updates):
| # | Content Type | Entries | Last Updated |
|---|-------------|---------|--------------|

📊 Summary:
- Total types: {N}
- Drift issues: {N}
- Unused: {N}
- Stale: {N}
- TypeScript interfaces generated: {path}

RULES: This is the COMPLETE output. Omit empty sections. Do NOT add commentary or follow-up questions.
