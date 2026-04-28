---
name: ppt-workflow
description: TUI-branded PowerPoint generation using the official corporate template. Use when the user asks to create, modify, or plan a presentation.
---

# PPT Workflow

Create TUI-branded PowerPoint presentations programmatically. Uses explicit shape builders with TUI brand colors, fonts, and proportions — no manual template editing needed.

## Available Commands

- `$kn_plan-presentation` — "plan a presentation", "outline a deck" — Gather requirements, choose slide types, write content, output a JSON spec for review. Read the command from [commands/plan-presentation.md](commands/plan-presentation.md)
- `$kn_create-presentation` — "make a presentation", "create a deck" — Generate .pptx from spec or from scratch (gather + plan + generate + review loop). Read the command from [commands/create-presentation.md](commands/create-presentation.md)
- `$kn_add-slides` — "add a slide about Y", "append slides" — Add slides to an existing .pptx with the same review loop. Read the command from [commands/add-slides.md](commands/add-slides.md)

## Templates

- [assets/templates/ppt-slide-plan.md](assets/templates/ppt-slide-plan.md) — Slide plan format (before generation)
- [assets/templates/ppt-result.md](assets/templates/ppt-result.md) — Output format after generation

## Slide Type Catalog

Pick the right type for each slide based on the content.

| Type | Use for | Max content |
|------|---------|-------------|
| `cover` | Opening slide | Title (44pt) + subtitle block (20pt) |
| `thank_you` | Closing slide | "Thank you." + contact info |
| `title` | Text-heavy explanations, lists | Body max 12-14 lines at 19pt |
| `quote` | Key statements, testimonials | Quote max 2 lines at 36pt |
| `terminal` | CLI demos, code, file trees | Max 18 lines, ~70 chars/line at 12pt Consolas |
| `two_col` | Comparisons, problem/solution | 6-8 lines per column at 20pt |
| `chevron` | Process steps, phases | Card text max 4-5 lines at 18pt |
| `three_cards` | 3 pillars, options, categories | Body max 4-5 lines at 20pt per card |
| `table` | Structured data, feature lists | Max 8 rows, ~40 chars/cell at 15pt |
| `diagram` | Architecture, flows, org charts | Max ~25 elements, box text ~25 chars |
| `hybrid_tree` | Code structure + categorized items | Terminal 10 lines + category boxes |

### Selection Rules

- Code/CLI flows → `terminal`
- Side-by-side comparison → `two_col`
- 3-4 step process → `chevron`
- 3 options/pillars → `three_cards`
- Data with columns → `table`
- Architecture/relationships → `diagram`
- Code structure + inventory → `hybrid_tree`
- Impactful quote → `quote`
- Text explanation → `title`
- Opening → `cover`
- Closing → `thank_you`

## JSON Spec Format

Each slide is a typed object. The `type` field selects the builder.

```json
{"type": "cover", "title": "...", "subtitle": "...", "notes": "..."}
{"type": "terminal", "title": "...", "lines": [["$ cmd", "cyan"], ["output", "white"]], "notes": "..."}
{"type": "two_col", "title": "...", "left": {"header": "...", "body": "..."}, "right": {"header": "...", "body": "..."}}
{"type": "chevron", "title": "...", "steps": [{"header": "Step 1", "body": "..."}]}
{"type": "three_cards", "title": "...", "cards": [{"header": "...", "body": "..."}]}
{"type": "table", "title": "...", "headers": ["A", "B"], "rows": [["1", "2"]]}
{"type": "diagram", "title": "...", "boxes": [{"x": 1, "y": 2, "w": 2, "h": 0.6, "text": "...", "color": "sky_blue"}], "arrows": [...], "labels": [...]}
{"type": "quote", "quote": "...", "attribution": "..."}
{"type": "title", "title": "...", "body": "line1\nline2"}
{"type": "thank_you", "contact": "Name\nDept\nEmail"}
```

### Terminal line colors

`cyan` (prompts), `yellow` (user input), `green` (success), `red` (errors), `gray` (secondary), `white` (output)

### Diagram colors

`deep_blue`, `sky_blue`, `energy_blue`, `red`, `sky_20`, `white`

## Brand Reference

| Element | Font | Size | Color |
|---------|------|------|-------|
| Cover title | Ambit | 44pt Bold | Deep Blue (27,17,92) |
| Slide title | Ambit | 28-34pt Bold | Deep Blue |
| Subtitle | Ambit | 18-20pt | Energy Blue (53,103,246) |
| Body text | TUI Type Light | 18-20pt | Deep Blue |
| Terminal | Consolas | 12pt | Various (see above) |
| Table header | Ambit | 16pt Bold | White on Deep Blue |
| Table data | TUI Type Light | 15pt | Deep Blue |

## Prerequisites

- `python-pptx` installed: `pip install python-pptx`
- TUI template is bundled at `assets/TUI-Template.potx` (no manual setup needed)

## References

For the original 119-slide template catalog (visual reference only — we don't clone from it):
- [references/catalog-covers-and-blanks.md](references/catalog-covers-and-blanks.md)
- [references/catalog-agendas-and-content.md](references/catalog-agendas-and-content.md)
- [references/catalog-structures.md](references/catalog-structures.md)
- [references/catalog-tables-graphs-timelines.md](references/catalog-tables-graphs-timelines.md)
- [references/technical-reference.md](references/technical-reference.md)
