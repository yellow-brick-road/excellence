---
name: planner-decompose
description: "Decomposition summary for $planner_decompose. Use when: presenting task breakdown."
---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Task Decomposition — {topic}
   Tasks: {N} | Gates: {N}
   Estimated effort: {total}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| # | Task | Type | Estimate | Deps | Gate |
|---|------|------|----------|------|------|

Dependency graph:
{ASCII graph showing task order}

To execute:
  autobuild .plan/{topic}/tasks/ --bg

RULES: This is the COMPLETE output. Do NOT add commentary or follow-up questions. Wait for user approval.
