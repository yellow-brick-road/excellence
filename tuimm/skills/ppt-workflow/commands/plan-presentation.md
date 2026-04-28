---
name: kn_plan-presentation
description: "Plan a presentation without generating it. Use when: user says 'plan a presentation', 'outline a deck', or wants to review slide structure before generating."
---

# Command: $kn_plan-presentation

Plan a TUI-branded presentation: gather requirements, choose slide types, write content, output a JSON spec. Does NOT generate the .pptx — use `$kn_create-presentation` for that.

## Process

### 1. Gather Requirements

Ask the user (if not already provided):
- **Topic** — what is the presentation about?
- **Audience** — who will see it? (executives, engineers, mixed)
- **Key messages** — 3-5 things the audience should remember
- **Source material** — existing docs, notes, slide specs (folder path or inline)
- **Language** — default English, can be es/it/de
- **Length** — target number of slides (default: 10-15)

If the user provides source material (a folder with docs), read and synthesize it.

### 2. Plan the Deck

For each slide, determine:
- **Type** — from the Slide Type Catalog in SKILL.md
- **Content** — text for each field, respecting content limits per type
- **Speaker notes** — what the presenter will SAY (not what's on screen)

**Content length rules (ENFORCE STRICTLY):**
- `terminal`: max 18 lines, ~70 chars/line
- `two_col`: body max 6-8 lines per column
- `chevron`: card text max 4-5 lines
- `three_cards`: body max 4-5 lines per card
- `table`: max 8 rows, ~40 chars/cell for 3-col
- `title`: body max 12-14 lines
- `quote`: max 2 lines
- `diagram`: box text max ~25 chars

If content exceeds limits, split into multiple slides or reduce text. NEVER overflow.

### 3. Present Plan

Present the plan using the `ppt-slide-plan` template. **Wait for user approval.**

User can:
- **Approve** → proceed to step 4
- **Adjust** → modify slides, reorder, add/remove
- **Iterate** → go back to step 2 with feedback

### 4. Save Spec

Write the approved JSON spec to `/tmp/ppt-spec.json`:

```json
{
  "output": "/tmp/presentation-TOPIC.pptx",
  "slides": [
    {"type": "cover", "title": "...", "subtitle": "...", "notes": "..."},
    {"type": "title", "title": "...", "body": "...", "notes": "..."}
  ]
}
```

Tell the user:

```
Spec saved to /tmp/ppt-spec.json

To generate the presentation:
  $kn_create-presentation --spec /tmp/ppt-spec.json

Or edit the spec manually and then generate.
```

## Rules

- ENFORCE content length limits — don't let text overflow
- Speaker notes drive content decisions — what's on screen supports what's said
- If the user doesn't have content ready for all slides, plan what you can and note gaps
- The spec is a standalone JSON file — it can be edited, shared, versioned
