---
name: ds-design-audit
description: "Design system audit report for $ds_design-audit. Use when: presenting DS compliance check."
---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎨 Design System Audit — {DATE}
   Project: {project}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DS Components: {N} in Figma, {N} in code

📐 Drift (Figma ≠ code):
| # | Component | Issue | Figma | Code |
|---|-----------|-------|-------|------|

🔧 Custom components (should use DS):
| # | Component | File | DS Equivalent |
|---|-----------|------|---------------|

⚠️ Deprecated (still in use):
| # | Component | Usage Count | Files |
|---|-----------|-------------|-------|

🎯 Hardcoded values (should use tokens):
| # | File | Line | Value | Token |
|---|------|------|-------|-------|

📊 Adoption:
| Project | DS Usage | Custom | Adoption % |
|---------|----------|--------|------------|

🔍 Quality (SonarQube):
| Component | Coverage | Bugs | Debt |
|-----------|----------|------|------|

RULES: This is the COMPLETE output. Omit empty sections. Do NOT add commentary or follow-up questions.
