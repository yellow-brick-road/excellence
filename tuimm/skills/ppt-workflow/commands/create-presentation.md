---
name: kn_create-presentation
description: "Full presentation workflow. Use when: user says 'make a presentation', 'create a deck', 'presentation about X'."
---

# Command: $kn_create-presentation

Create a TUI-branded PowerPoint from a topic description. Uses explicit shape builders — no template cloning.

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

If the user doesn't have slide content ready, suggest using `$kn_add-slides` iteratively — build the deck slide by slide as content becomes available.

### 2. Plan the Deck

For each slide, determine:
- **Type** — from the Slide Type Catalog in SKILL.md (terminal, two_col, chevron, etc.)
- **Content** — text for each field, respecting the content limits per type
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

Present the plan using the `ppt-slide-plan` template. **Wait for user approval.**

### 3. Generate the Presentation

Write the JSON spec to `/tmp/ppt-spec.json` following the format in SKILL.md.

Run the generator:
```bash
python3 ~/.kiro/skills/tuimm-ppt-workflow/scripts/ppt-generator.py --spec /tmp/ppt-spec.json
```

### 4. Visual Review Loop

**This is the critical step.** Render and review every slide.

```bash
soffice --headless --convert-to pdf --outdir /tmp "/tmp/presentation-TOPIC.pptx"
pdftoppm -jpeg -r 100 "/tmp/presentation-TOPIC.pdf" /tmp/ppt-review
```

**Use 100 DPI** (not 200) — keeps images small enough for review without timeouts. Delete the PDF immediately after conversion:
```bash
rm -f /tmp/presentation-TOPIC.pdf
```

For each slide image, verify:
1. Is ALL expected text visible and complete (not cut off)?
2. Are words correctly displayed (no incorrect hyphenation)?
3. Does content stay inside its boxes/cards?
4. Are table cells complete?
5. Is it readable at projection size?

**Review max 3 slides per check** to avoid large image payloads.

If issues found:
- Adjust the JSON spec (reduce text, change type, adjust content)
- Re-run generator
- Re-render only affected slides

Repeat until all slides pass.

### 5. Cleanup & Deliver

Delete all temporary files:
```bash
rm -f /tmp/ppt-review-*.jpg /tmp/ppt-spec.json /tmp/presentation-TOPIC.pdf
```

Move the final .pptx to the user's preferred location (default: current working directory).

Present results using the `ppt-result` template.

## Rules

- ALWAYS show the slide plan before generating — never generate without approval
- ENFORCE content length limits during planning — don't let text overflow
- Use 100 DPI for review images — 200 DPI is too large for subagent review
- Review max 3 slides per image check to avoid timeouts
- Clean up ALL temp files (/tmp/ppt-review-*, /tmp/ppt-spec.json, PDFs) before delivering
- If the user doesn't have content ready, suggest `$kn_add-slides` to build incrementally
- Speaker notes drive content decisions — what's on screen supports what's said
