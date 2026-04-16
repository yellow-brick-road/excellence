---
name: qg-dependency-review
description: "Dependency review report for $qg_dependency-review. Use when: presenting Renovate MR triage."
---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Dependency Review — {DATE}
   Project: {project}
   Renovate MRs: {total}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Per MR:
📦 {package} {old} → {new} ({type})
   Pipeline: ✅/❌ | Quality: ✅/❌
   Usage: {N} files
   Breaking changes: {None / list}
   Decision: {APPROVE / NEEDS ATTENTION / BLOCK}
   Reason: {reasoning}

Summary:
✅ APPROVE ({N}): {list}
⚠️ NEEDS ATTENTION ({N}): {list}
🚫 BLOCK ({N}): {list}

RULES: This is the COMPLETE output. Do NOT add commentary or follow-up questions. Wait for user to decide actions.
