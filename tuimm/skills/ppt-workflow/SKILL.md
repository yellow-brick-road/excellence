---
name: ppt-workflow
description: TUI-branded PowerPoint generation using the official corporate template. Use when the user asks to create, modify, or plan a presentation.
---

# PPT Workflow

Commands for creating TUI-branded PowerPoint presentations programmatically. Uses the official TUI PowerPoint Template (Oct 2025) with 119 pre-designed slides.

## How It Works

Instead of building slides from scratch, the agent **clones** template slides that match the need and **replaces** placeholder text/images. This guarantees perfect TUI branding every time.

## Available Commands

- `$kn_create-presentation` — "make a presentation about X", "create a deck" — Full workflow: describe → plan slides → generate .pptx → visual review. Read the command from [commands/create-presentation.md](commands/create-presentation.md)
- `$kn_add-slides` — "add a slide about Y", "append slides" — Add slides to an existing .pptx. Read the command from [commands/add-slides.md](commands/add-slides.md)

## Templates

- [assets/templates/ppt-slide-plan.md](assets/templates/ppt-slide-plan.md) — Slide plan format (before generation)
- [assets/templates/ppt-result.md](assets/templates/ppt-result.md) — Output format after generation

## Quick Slide Picker

Use this table to find the right template slide to clone.

### Covers

| Need | Clone slide | Notes |
|------|-------------|-------|
| Photo cover, title bottom | **3** | Full-bleed hero, TUI smile overlay |
| Photo cover, title top | **4** | Hero image, title top-left |
| Radiant smile cover | **5** | TUI logo top-right, arc overlay |
| Custom photo + blue title | **6** | Picture placeholder |
| Solid sky blue | **7** | Clean, no photo |
| Solid white | **8** | Clean, no photo |
| Custom photo + white title | **9** | Picture placeholder |

### Section Dividers

| Need | Clone slide |
|------|-------------|
| Title + subtitle | **37** |
| Title only | **21** |

### Content Backgrounds

| Need | Clone slide | Notes |
|------|-------------|-------|
| White + gradient corner | **23** | Image left + title right |
| White minimal | **36** | Cleanest — just TUI logo |
| Sky blue full | **26** | Full background |
| Dark navy full | **30** | Full background |

### Split Layouts

| Need | Clone slide |
|------|-------------|
| Light blue / white (40/60) | **27** |
| Light blue / white (50/50) | **28** |
| Light blue / white (60/40) | **29** |
| Dark navy / white (40/60) | **31** |
| Dark navy / white (50/50) | **32** |
| Dark navy / white (60/40) | **33** |

### Agendas & Overviews

| Need | Clone slide |
|------|-------------|
| 6-item agenda sidebar | **39** |
| 12-item agenda 2-col | **40** |
| Schedule table | **44** |
| Decision template | **53** |
| Target checklist | **48** |

### Text Layouts

| Need | Clone slide |
|------|-------------|
| 2-column | **55** or **56** |
| Advantages vs Disadvantages | **57** |
| 3-column cards | **58** |
| 3-column + conclusion | **59** |

### Structure Charts

| Need | Clone slide |
|------|-------------|
| 8-card grid (4×2) | **62** |
| 6-card grid (3×2) | **63** |
| 4-quadrant (2×2) | **64** |
| 4 vertical cards | **65** |
| 4-step process (chevrons) | **67** |
| Hub-and-spoke | **83** |
| Funnel | **86** |
| Pyramid | **89** |
| Org chart (large) | **91** |

### Tables

| Need | Clone slide |
|------|-------------|
| Basic data table | **94** |
| Action tracker | **99** |
| Financial KPI dashboard | **100** |

### Timelines

| Need | Clone slide |
|------|-------------|
| Monthly timeline | **112** |
| Gantt chart | **114** |
| Annual roadmap | **115** |

### End Slide

| Need | Clone slide |
|------|-------------|
| Thank you / closing | **119** |

## References

For detailed shape data per slide, see:
- [references/catalog-covers-and-blanks.md](references/catalog-covers-and-blanks.md)
- [references/catalog-agendas-and-content.md](references/catalog-agendas-and-content.md)
- [references/catalog-structures.md](references/catalog-structures.md)
- [references/catalog-tables-graphs-timelines.md](references/catalog-tables-graphs-timelines.md)
- [references/technical-reference.md](references/technical-reference.md)
- [references/template-shapes.json](references/template-shapes.json)

## Prerequisites

- `python-pptx` installed: `pip install python-pptx`
- TUI template is bundled at `assets/TUI-Template.potx` (no manual setup needed)
