---
name: qg-dependency-scan
description: "Dependency scan report for $qg_dependency-scan. Use when: presenting proactive dependency analysis."
---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 Dependency Scan — {DATE}
   Project: {project}
   Total dependencies: {N}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Up to date: {N}
📦 Outdated: {N}

SAFE updates (propose MR):
| # | Package | Current | Latest | Type | Usage |
|---|---------|---------|--------|------|-------|

⚠️ NEEDS MIGRATION (propose Jira ticket):
| # | Package | Current | Latest | Breaking Change | Affected Files |
|---|---------|---------|--------|-----------------|----------------|

🚫 BLOCKED:
| # | Package | Current | Latest | Reason |
|---|---------|---------|--------|--------|

🔒 Security fixes (priority):
| # | Package | CVE | Severity | Current | Fixed In |
|---|---------|-----|----------|---------|----------|

RULES: This is the COMPLETE output. Omit empty sections. Do NOT add commentary or follow-up questions. Wait for user to decide actions.
