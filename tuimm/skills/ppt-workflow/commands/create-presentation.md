---
name: kn_create-presentation
description: "Full presentation workflow. Use when: user says 'make a presentation', 'create a deck', 'presentation about X'."
---

# Command: $kn_create-presentation

Create a TUI-branded PowerPoint from a spec or from scratch. Uses explicit shape builders — no template cloning.

## Process

### 1. Check for Existing Spec

If the user provides `--spec /path/to/spec.json` or a spec file exists at `/tmp/ppt-spec.json` (from `$kn_plan-presentation`), skip to step 4.

If no spec exists, do steps 2-3 inline (or suggest `$kn_plan-presentation` first for complex decks).

### 2. Gather Requirements

Ask the user (if not already provided):
- **Topic** — what is the presentation about?
- **Audience** — who will see it? (executives, engineers, mixed)
- **Key messages** — 3-5 things the audience should remember
- **Source material** — existing docs, notes, slide specs (folder path or inline)
- **Language** — default English, can be es/it/de
- **Length** — target number of slides (default: 10-15)

If the user provides source material (a folder with docs), read and synthesize it.

If the user doesn't have slide content ready, suggest using `$kn_add-slides` iteratively — build the deck slide by slide as content becomes available.

### 3. Plan the Deck

For each slide, determine:
- **Type** — from the Slide Type Catalog in SKILL.md
- **Content** — text for each field, respecting content limits per type
- **Speaker notes** — what the presenter will SAY (not what's on screen)

**Content length rules (ENFORCE STRICTLY — reject before generating):**
- `terminal`: max 16 lines, ~70 chars/line at 12pt Consolas
- `two_col`: body max 6-8 lines per column at 20pt
- `chevron`: card text max 4-5 lines at 18pt
- `three_cards`: body max 4-5 lines per card at 20pt
- `table`: max 8 rows, ~40 chars/cell for 3-col, ~60 chars for 2-col
- `title`: body max 12-14 lines at 19pt
- `quote`: max 2 lines at 36pt
- `diagram`: box text max ~25 chars at 13pt

If content exceeds limits, split into multiple slides or reduce text. NEVER generate a slide that will overflow.

Present the plan using the `ppt-slide-plan` template. **Wait for user approval.**

### 4. Generate the Presentation

Write the JSON spec to `/tmp/ppt-spec.json` (if not already there).

Run the generator:
```bash
python3 ~/.kiro/skills/tuimm-ppt-workflow/scripts/ppt-generator.py --spec /tmp/ppt-spec.json
```

**Critical**: Always use layouts from master 0 only (Cover: Radiant, White/SkyBlue background). NEVER master 1 — it has a pool photo that contaminates all slides.

### 5. Render to Images

```bash
mkdir -p /tmp/ppt-review
soffice --headless --convert-to pdf --outdir /tmp "/tmp/presentation-TOPIC.pptx"
pdftoppm -jpeg -r 100 "/tmp/presentation-TOPIC.pdf" /tmp/ppt-review/slide
rm -f /tmp/presentation-TOPIC.pdf
```

Use **100 DPI** — keeps images small enough for subagent review. Delete the PDF immediately.

### 6. Visual Review Loop

#### 6.1 Launch ONE subagent per slide (all in parallel)

Use the `subagent` tool to launch one reviewer per slide. **Never send more than 1 image per subagent** — multiple images cause timeouts and hallucinated reviews.

Each subagent receives this prompt:

```
Review slide {N} of a TUI-branded presentation.

Image: /tmp/ppt-review/slide-{NN}.jpg

SLIDE TYPE: {type}

EXPECTED CONTENT (this exact text should be visible on the slide):
{paste the full text content from the spec for this slide — title, body, headers, card text, table data, terminal lines — everything}

SPEAKER NOTES (what the presenter will say — the slide should support this):
{paste speaker notes}

=== ROUND 1 — Content completeness ===
Compare the image against EXPECTED CONTENT:
- Is ALL expected text visible and complete (not cut off at any edge)?
- Is any text truncated, missing, or incorrectly hyphenated/broken?
- Do all table cells show their full content?
- Are all terminal lines visible?

=== ROUND 2 — Visual quality ===
- Does content fill the slide appropriately (no huge empty areas)?
- Is text readable at projection size (not too small)?
- Does the visual layout support what the presenter will say?
- Does it look professional and balanced?

VERDICT: Reply PERFECT if both rounds pass. Otherwise list SPECIFIC fixes with exact details (which text is cut off, which area is empty, etc.).
```

#### 6.2 Collect Results

Gather all subagent responses. Separate PERFECT slides from those needing fixes.

#### 6.3 Apply Fixes to Spec JSON

For each non-PERFECT slide, modify the **spec JSON** — NOT the .pptx file. python-pptx cannot reliably edit existing shapes (save persistence bug). Always regenerate from spec.

**Common fixes:**
- "text cut off" → reduce content lines or split into 2 slides
- "too much empty space" → increase font size in spec or add more content
- "text overflows box" → shorten text
- "words hyphenated/broken" → shorten the line or use shorter words
- "not readable" → increase font size, reduce content density

#### 6.4 Re-generate and Re-review

If any fixes were applied:
1. Regenerate the full deck from the updated spec
2. Re-render ONLY the affected slides to images
3. Re-launch subagent review ONLY for the affected slides (1 per slide, parallel)
4. Repeat until all slides are PERFECT or **max 3 iterations** reached

If after 3 iterations some slides still have issues, report them to the user with the specific problems and let them decide.

### 7. Cleanup & Deliver

Delete ALL temporary files:
```bash
rm -rf /tmp/ppt-review/ /tmp/ppt-spec.json /tmp/presentation-TOPIC.pdf
```

Move the final .pptx to the user's preferred location (default: current working directory).

Present results using the `ppt-result` template.

## Rules

- ALWAYS show the slide plan before generating — never generate without approval
- ENFORCE content length limits during planning — reject before generating, never overflow
- ONE image per subagent reviewer — never batch multiple slides
- The reviewer MUST receive the expected text content — without it, truncation goes undetected
- Fixes go to the spec JSON, then regenerate — never patch the .pptx directly
- Max 3 review iterations — after that, report remaining issues to user
- Clean up ALL temp files before delivering
- Always use master 0 layouts — never master 1
- If the user doesn't have content ready, suggest `$kn_add-slides` to build incrementally
- Speaker notes drive content decisions — what's on screen supports what's said
