---
name: mr-comment-item
description: "Per-comment presentation for $mr_comments. Use when: presenting each individual review comment."
---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Comment #{X} of {Y} by {name} {🤖 BOT / 👤 HUMAN}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 File: {path}:{line} ({function or component name})
💬 Comment: "{text}"
🤔 Analysis: {your independent technical assessment — not a restatement of the comment}
✓ Valid? {Yes / No / Partially}
🏷️ Type: {Question / Suggestion / Required / Nitpick}

📄 Code:
```{lang}
// Current
{relevant lines as they are now}

// Proposed change
{what the fix would look like — omit this block entirely if no code change applies}
```

Action?
1. ✅ Apply fix
2. 💬 Respond
3. 💬 Apply + respond
4. ✔️ Resolve (no reply)
5. ⏭️ Skip
6. 👎 Disagree
← 👈 {recommended action number + one-line reason — place this marker on the recommended option only}

RULES: Reproduce this structure EXACTLY for every comment — field by field, line by line. Do NOT use markdown tables, headers (###), "Importance" scores, "Proposed response" sections, or any field not listed above. The ← 👈 marker goes on ONE action only (your recommendation). Do NOT add commentary after the action list.
