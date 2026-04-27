---
name: jira_set-ai-usage
agent: any
trigger: "$jira_set-ai-usage"
description: "Set AI usage tracking fields on a Jira ticket. Use when: manually recording AI contribution level after completing work, or when the automated post-MR step was skipped."
---

Set AI usage tracking fields on a Jira ticket.

## Input

User provides:
- Ticket ID (e.g. DIS-1234)
- Optionally: which phase(s) and band. If not specified, ask.

## Process

### 1. Determine phase and band

Ask the user (if not provided):

**Phase** — which stage of work had AI involvement?
- **Refinement** — requirement elaboration, story shaping, analysis, design
- **Development** — coding, unit testing, refactoring, code reviews
- **Test & Release** — non-dev testing, release prep, deployment

**Band** — how much did AI contribute?
- No AI used (0%)
- Minimal AI assistance (~10%)
- Some AI assistance (~25%)
- Moderate AI assistance (~50%)
- Mostly AI delivered (~75%)
- Fully AI delivered (90-100%)

### 2. Set the field

Delegate to `tuimm-subagent_jira`:

> Update issue {TICKET}, set field "AI usage during {Phase}" to "{Band}"

Field names (exact):
- `AI usage during Refinement`
- `AI usage during Development`
- `AI usage during Test & Release`

Band values (exact strings):
- `No AI used`
- `Minimal AI assistance`
- `Some AI assistance`
- `Moderate AI assistance`
- `Mostly AI delivered`
- `Fully AI delivered`

### 3. Handle errors

- If the field doesn't exist → inform user: "AI usage fields not available on this issue (may not be a standard type: Story/Task/Bug/Debt/Risk)"
- If the update fails → report error, don't retry
- Do NOT set on sub-tasks, Epics, or Initiatives

### 4. Confirm

Report: "✅ Set 'AI usage during {Phase}' = '{Band}' on {TICKET}"

## Examples

- `$jira_set-ai-usage DIS-1234 development fully` → sets Development to "Fully AI delivered"
- `$jira_set-ai-usage DIS-1234` → asks which phase and band
- `$jira_set-ai-usage DIS-1234 refinement some, development mostly` → sets both fields
