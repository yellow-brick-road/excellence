---
name: qg-quality-check
description: "Quality report for $qg_quality-check. Use when: presenting quality scan results."
---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Quality Check — {DATE}
   Projects: {project1}, {project2}, ...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Per project:
| Project | Gate | Coverage | New Code Cov | Debt | New Issues |
|---------|------|----------|--------------|------|------------|

🔴 BLOCKERS/CRITICALS:
| # | Project | File | Rule | Message |
|---|---------|------|------|---------|

📈 Trends:
- {project}: coverage ↑/↓ X%
- {project}: debt ↑/↓ Xh

⚠️ Outliers:
- {description}

🚫 Blocked MRs:
- !{iid} blocked by failing quality gate in {project}

RULES: This is the COMPLETE output. Omit empty sections. Do NOT add commentary, recommendations, or follow-up questions.
