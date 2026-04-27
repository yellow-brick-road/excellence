---
name: template-blueprint
description: "Reference structure for creating new TUIMM templates. Use when: creating a new template for a command."
---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{Icon} {Title} — {identifier}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{Key metadata fields as single lines, each with an emoji prefix}

{Summary or assessment paragraph — 1-3 sentences max}

{Data table if applicable — keep columns minimal, no Notes column}

| Column A | Column B | Column C |
|----------|----------|----------|
| {data}   | {data}   | {data}   |

📄 Code (when showing current vs proposed):
```{lang}
// Current
{relevant lines}

// Proposed
{changed lines — omit section if no change}
```

Action? (when user input needed — numbered list, one per line):
1. {Option}
2. {Option}
3. {Option} ← 👈 {recommended option + one-line reason}

RULES: This is the COMPLETE output. Do NOT add sections, commentary, follow-up questions, recommendations, bar charts, or any content not defined above. Omit sections that have no data.
