---
name: planner-analyze
description: "Analysis report for $planner_analyze. Use when: presenting requirement analysis."
---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 Requirement Analysis
   Source: {ticket_id or description}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Summary: {one-line summary}

📐 Scope:
- Files affected: ~{N}
- Modules: {list}
- Cross-cutting: Yes/No
- New patterns: Yes/No

⚠️ Risks:
- {risk}

📊 Quality context:
- Coverage in affected area: {%}
- Known debt: {issues}

🎯 Planning Level: {0/1/2/3} — {name}
   Recommended handler: {agent}
   Reason: {why this level}

RULES: This is the COMPLETE output. Do NOT add commentary or follow-up questions. Wait for user to decide next step.
