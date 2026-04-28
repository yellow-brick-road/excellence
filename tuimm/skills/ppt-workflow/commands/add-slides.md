---
name: kn_add-slides
description: "Add slides to an existing presentation. Use when: user says 'add a slide about X', 'append slides', 'insert a slide'."
---

# Command: $kn_add-slides

Add slides to an existing .pptx file. Same review loop as `$kn_create-presentation`.

## Process

### 1. Identify Target

Ask the user:
- **Which .pptx** — path to the existing presentation
- **What to add** — topic, content, or slide type
- **Where** — append at end (default)

### 2. Plan New Slides

Pick slide types from the catalog in SKILL.md. Respect content length limits.

Present the plan using the `ppt-slide-plan` template. **Wait for user approval.**

### 3. Generate

Write a JSON spec with `"append_to"`:

```json
{
  "append_to": "/path/to/existing.pptx",
  "output": "/path/to/existing-updated.pptx",
  "slides": [
    {"type": "title", "title": "New Section", "body": "Content here"}
  ]
}
```

Run:
```bash
python3 ~/.kiro/skills/tuimm-ppt-workflow/scripts/ppt-generator.py --spec /tmp/ppt-spec.json
```

### 4. Visual Review & Deliver

Same review loop as `$kn_create-presentation` step 4:
- Render at 100 DPI, review max 3 slides per check
- Fix issues, re-render, repeat until perfect
- Clean up temp files before delivering

## Rules

- NEVER overwrite the original file — always save to a new path first
- Show the plan before generating
- Clean up temp files after delivery
- Enforce content length limits
