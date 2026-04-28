---
name: kn_create-presentation
description: "Full presentation workflow. Use when: user says 'make a presentation', 'create a deck', 'presentation about X'."
---

# Command: $kn_create-presentation

Create a TUI-branded PowerPoint from a topic description.

## Process

### 1. Gather Requirements

Ask the user (if not already provided):
- **Topic** — what is the presentation about?
- **Audience** — who will see it? (executives, engineers, mixed)
- **Key messages** — what are the 3-5 things the audience should remember?
- **Sections** — rough structure (or let the agent propose one)
- **Language** — default English, can be es/it/de
- **Length** — target number of slides (default: 10-15)

### 2. Plan the Deck

For each slide, determine:
- Which template slide to clone (use the Quick Slide Picker in SKILL.md)
- What content goes in each shape
- Speaker notes (optional)

If the slide needs a layout not in the picker, consult the detailed catalogs in `references/`.

Present the plan using the `ppt-slide-plan` template. **Wait for user approval.**

### 3. Prepare the Template

```bash
python3 -c "
import os
if not os.path.exists('/tmp/tui-template.pptx'):
    print('Converting .potx to .pptx...')
    exec(open('$(find ~/.kiro/skills/tuimm-ppt-workflow/scripts/ppt-generator.py -maxdepth 0 2>/dev/null || echo scripts/ppt-generator.py)').read())
else:
    print('Template ready at /tmp/tui-template.pptx')
"
```

If the template doesn't exist at `/tmp/tui-template.pptx`, the generator script will convert it automatically from the .potx source.

### 4. Generate the Presentation

Write a JSON spec file at `/tmp/ppt-spec.json`:

```json
{
  "template": "/tmp/tui-template.pptx",
  "output": "/tmp/presentation-TOPIC.pptx",
  "slides": [
    {
      "clone": 7,
      "content": {
        "Title 5": "Presentation Title",
        "Subtitle 6": "Subtitle text"
      },
      "notes": "Optional speaker notes"
    }
  ]
}
```

Run the generator:
```bash
python3 ~/.kiro/skills/tuimm-ppt-workflow/scripts/ppt-generator.py --spec /tmp/ppt-spec.json
```

### 5. Visual Review

Convert to images for review:
```bash
soffice --headless --convert-to pdf --outdir /tmp "/tmp/presentation-TOPIC.pptx"
pdftoppm -jpeg -r 200 "/tmp/presentation-TOPIC.pdf" /tmp/review-slide
```

Show the generated slide images to the user. Ask for feedback.

### 6. Iterate

If the user wants changes:
- Modify the JSON spec
- Re-run the generator
- Show updated slides

### 7. Deliver

Move the final .pptx to the user's preferred location. Default: the current working directory.

Present results using the `ppt-result` template.

## Shape Name Reference

To find shape names for a specific template slide:
1. Check `references/template-shapes.json` — has all 119 slides with shape IDs and names
2. Check the catalog files in `references/` — human-readable descriptions per slide
3. Shapes with `ph_idx` are placeholders (use `fill_placeholder`)
4. Shapes without `ph_idx` are free shapes (use `fill_text` by name)

## Rules

- ALWAYS show the slide plan before generating — never generate without approval
- Use the Quick Slide Picker first, detailed catalogs only when needed
- Slide numbers in catalogs are 1-based; python-pptx uses 0-based (slide 7 = index 6)
- Preserve TUI branding — never modify background shapes, logos, or decorative elements
- If a slide type doesn't exist in the template, compose from the closest match
