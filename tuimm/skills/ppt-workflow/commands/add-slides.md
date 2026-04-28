---
name: kn_add-slides
description: "Add slides to an existing presentation. Use when: user says 'add a slide about X', 'append slides', 'insert a slide'."
---

# Command: $kn_add-slides

Add slides to an existing .pptx file.

## Process

### 1. Identify Target

Ask the user:
- **Which .pptx** — path to the existing presentation
- **What to add** — topic, content, or slide type
- **Where** — append at end (default), or insert at position N

### 2. Plan New Slides

Same as `$kn_create-presentation` step 2 — pick template slides, plan content.

Present the plan using the `ppt-slide-plan` template. **Wait for user approval.**

### 3. Generate

Write a JSON spec with `"append_to"` instead of `"output"`:

```json
{
  "template": "/tmp/tui-template.pptx",
  "append_to": "/path/to/existing.pptx",
  "insert_at": -1,
  "slides": [
    {
      "clone": 37,
      "content": {
        "Title 1": "New Section",
        "Subtitle 2": "Added content"
      }
    }
  ]
}
```

`insert_at`: -1 = append at end, 0 = beginning, N = after slide N.

Run:
```bash
python3 ~/.kiro/skills/tuimm-ppt-workflow/scripts/ppt-generator.py --spec /tmp/ppt-spec.json
```

### 4. Visual Review & Deliver

Same as `$kn_create-presentation` steps 5-7.

## Rules

- NEVER overwrite the original file — save to a new path first, let user confirm
- Show the plan before generating
- Preserve existing slides — only add, never modify what's already there
