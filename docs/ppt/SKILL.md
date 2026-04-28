# TUI PowerPoint Generation Skill

Create branded TUI presentations programmatically using the official corporate template (Oct 2025).

## How It Works

The template (`TUI PowerPoint Template_Oct2025 2.potx`) has 119 pre-designed slides. Instead of building slides from scratch, you **clone** the template slide that matches your need and **replace** the placeholder text/images. This guarantees perfect branding every time.

## Files in This Skill

| File | Content |
|------|---------|
| `SKILL.md` | This file — overview, slide picker, workflow |
| `catalog-covers-and-blanks.md` | Slides 1-37: covers, blanks, splits, dividers |
| `catalog-agendas-and-content.md` | Slides 38-61: agendas, checklists, text boxes |
| `catalog-structures.md` | Slides 62-92: grids, processes, diagrams, org charts |
| `catalog-tables-graphs-timelines.md` | Slides 93-119: tables, graphs, timelines, end slide |
| `technical-reference.md` | python-pptx code, colors, fonts, clone functions |
| `template-shapes.json` | Raw shape data for all 119 slides (machine-readable) |

## Quick Slide Picker

When building a presentation, use this table to find the right slide to clone.

### Covers

| Need | Clone slide | Notes |
|------|-------------|-------|
| Photo cover, title at bottom | **3** | Full-bleed hero image with TUI smile overlay, title bottom-left |
| Photo cover, title at top | **4** | Same hero image style, title top-left |
| Photo cover with radiant smile | **5** | TUI logo top-right, radiant arc overlay |
| Custom photo + blue title | **6** | Has picture placeholder you can fill |
| Custom photo + white title | **9** | Picture placeholder + title at top |
| Solid sky blue cover | **7** | No photo, clean sky blue background |
| Solid white cover | **8** | No photo, clean white background |

### Section Dividers

| Need | Clone slide | Notes |
|------|-------------|-------|
| Section break | **37** | Blue gradient with arc pattern. Has Title + Subtitle |
| Section break (title only) | **21** | Same style, title only, no subtitle |

### Content Backgrounds (blank, add your own content)

| Need | Clone slide | Notes |
|------|-------------|-------|
| White + blue gradient corner | **23** | Has image placeholder left + title/subtitle right |
| White + blue gradient corner (alt) | **24** | Image placeholder left + title/subtitle/content right |
| White minimal | **36** | Cleanest blank — just TUI logo |
| Sky blue full | **26** | Full sky blue background + video placeholder |
| Dark navy full | **30** | Full dark navy background |
| Blue gradient full | **35** | Gradient sky blue, no placeholders |

### Split Layouts (image one side, text the other)

| Need | Clone slide | Left panel | Right panel |
|------|-------------|-----------|-------------|
| Light blue / white (40/60) | **27** | Light blue | White |
| Light blue / white (45/55) | **28** | Light blue | White |
| Light blue / white (60/40) | **29** | Light blue | White |
| Dark navy / white (40/60) | **31** | Dark navy | White |
| Dark navy / white (45/55) | **32** | Dark navy | White |
| Dark navy / white (60/40) | **33** | Dark navy | White |
| Light blue / dark navy (50/50) | **34** | Light blue | Dark navy |

### Agendas & Project Overviews

| Need | Clone slide | Notes |
|------|-------------|-------|
| 6-item agenda with sidebar | **39** | Navy sidebar "AGENDA", numbered circles + topic bars |
| 12-item agenda (2 columns) | **40** | Full-width, two columns of numbered topics |
| 6-item agenda (dark bg) | **41** | Dark navy background variant |
| 6-item agenda (white bg, circle badges) | **42** | White background, blue circle numbers |
| 9-item minimal list | **43** | Cyan highlight bar on active item |
| Schedule table (When/What/Who) | **44** | 3-column table with time slots |
| Key Statements + Rationale | **45** | 2 columns, 5 numbered rows |
| Topic summary + red sidebar | **46** | Color-coded topics left, red summary right |
| Key Topics horizontal bars | **47** | 5 navy-label + cyan-bar rows |
| Target checklist (7 items) | **48** | Status icons: ✓, ✗, ○ |
| Numbered checklist (9 items) | **49** | Cyan bars with pass/fail indicators |
| Three targets with bullseye | **50** | 1st/2nd/3rd priority + dartboard illustration |
| Strategy intro (3 icons → logo) | **51** | Globe, podium, org chart → TUI smile |
| Scope/Target/Responsible matrix | **52** | 3-column, 4-row matrix |
| Decision template | **53** | Problem → 3 Options (Pros/Cons) → Recommendation |

### Text Box Layouts

| Need | Clone slide | Notes |
|------|-------------|-------|
| 2-column (white + cyan) | **55** | Sub-headers + bullet areas |
| 2-column (white + white) | **56** | Uniform white, outlined |
| Advantages vs Disadvantages | **57** | Plus/minus icons + conclusion per column |
| 3-column colored cards | **58** | Cyan, navy, red headers |
| 3-column + conclusion bars | **59** | Gradient blue cards + navy conclusion |
| 3-column + results + next steps | **60** | Results bars + arrows + next steps |
| 3-column + results → summary | **61** | Results flow into red summary bar |

### Structure Charts

| Need | Clone slide | Notes |
|------|-------------|-------|
| 8-card grid (4×2) | **62** | Gradient blue tones |
| 6-card grid (3×2) | **63** | Gradient blue tones |
| 4-quadrant (2×2) | **64** | Title + body per quadrant |
| 4 vertical cards | **65** | Tall cards, 3 bullets each |
| 4-quadrant with bullets | **66** | Sky blue cards, 3 bullets each |
| 4-step process (chevrons) | **67** | Navy chevron headers + content cards |
| 4-step process + summary | **68** | Same + white summary box per step |
| 4-step process + project banner | **69** | Red project name banner at top |
| 4 topic rows + summary sidebar | **70** | Alternating blue rows + red sidebar |
| Key Statements + Rationale (table) | **71** | 5 rows, alternating backgrounds |
| 3 topic cards on gradient | **72** | Dark cards connected by arrow timeline |
| 4 colored circles (pillars) | **73** | Red, navy, blue, light blue |
| Advantages vs Disadvantages (circles) | **74** | 6 navy circles vs 6 red circles |
| Quote/statement | **77** | Large impactful text + attribution |
| 2-column comparison + images | **79** | Image top, bullets middle, result bottom |
| 3-column comparison + images | **80** | Same pattern, 3 columns |
| Central topic + 2 panels | **82** | Central circle connecting left/right |
| Hub-and-spoke (4-way) | **83** | Central box + 4 connected blocks |
| 6-influence diagram | **84** | Central bar + 3 left + 3 right blocks |
| Concentric circles (4 layers) | **85** | Nested layers + numbered descriptions |
| Funnel (3 stages → result) | **86** | Narrowing bars + result bar |
| Illustrated list (4 items) | **87** | TUI illustrations (plane, cruise, bus, hotel) |
| 4-statement list + conclusion | **88** | Icons + pill bars + conclusion bar |
| Pyramid (4 levels) | **89** | Red top → dark blue → blue → light blue |
| Project status dashboard | **90** | Team, Objectives, RAG status, Next Steps |
| Large org chart | **91** | 5 departments × 7 rows |
| Small org chart | **92** | 3 departments × 3 rows |

### Tables

| Need | Clone slide | Notes |
|------|-------------|-------|
| Basic data table (5×10) | **94** | Cyan header, alternating rows, total footer |
| Complex table (merged headers) | **95** | Hierarchical content in first column |
| Dense comparison table | **96** | 3 grouped headers × 3 sub-columns |
| Table + commentary | **97** | Table left, text box right |
| Dual table + notes | **98** | Two tables + titled text boxes |
| Action tracker | **99** | Next steps / Deadline / Responsible / Comments |
| Financial KPI dashboard | **100** | 3 business segments with YoY metrics |

### Graphs

| Need | Clone slide | Notes |
|------|-------------|-------|
| Bar chart comparison | **102** | FC vs Plan, absolute + percentage |
| 4-chart sampler | **103** | Bar + donut + pie + descending bar |
| Donut chart + comments | **104** | Donut left, bullet comments right |
| Line chart + comments | **105** | Multi-year line chart left, comments right |
| Grouped bar chart + comments | **106** | Quarterly bars left, comments right |
| Simple 2-bar comparison | **107** | Before/after with growth annotation |
| Multi-series line + comments | **108** | 5 series over 3 years |
| Scatter/quadrant plot | **109** | 2×2 axis template |
| Heat map / matrix | **110** | 3×3 intensity grid |

**⚠️ Graph charts are OLE objects (think-cell). Not directly editable via python-pptx. Clone the slide and modify the surrounding text boxes, or create native pptx charts.**

### Timelines

| Need | Clone slide | Notes |
|------|-------------|-------|
| Monthly timeline | **112** | Jan-Feb with milestone callouts |
| Multi-year timeline | **113** | 2022-2025 with speech bubbles |
| Gantt chart (12 months) | **114** | Overlapping horizontal bars |
| Annual roadmap | **115** | "We Are Here" marker + swim lanes |
| Weekly Gantt | **116** | Color-coded workstreams + today marker |
| World map | **117** | Clickable countries with annotations |

### End Slide

| Need | Clone slide | Notes |
|------|-------------|-------|
| Thank you / closing | **119** | "Thank you." + name/dept/phone/email |

## Presentation Assembly Workflow

1. **User describes the presentation** — topic, audience, sections, key messages
2. **Agent plans the deck** — list of slides, each mapped to a template slide number from the picker above
3. **Agent generates content** — text for each shape in each slide
4. **Agent runs python-pptx script** — clones slides, fills content (see `technical-reference.md`)
5. **Agent converts to JPG for review** — `pdftoppm` via LibreOffice PDF export
6. **User approves or requests changes**
7. **Agent delivers final .pptx**

## Template Location

| What | Path |
|------|------|
| Original .potx | `C:\Users\javier.fernandez\OneDrive - TUI\Desktop\TUI PowerPoint Template_Oct2025 2.potx` |
| Converted .pptx | `/tmp/tui-template.pptx` (regenerate if missing — see technical-reference.md) |
| Slide JPGs | `C:\Users\javier.fernandez\OneDrive - TUI\Desktop\TUI-Template-Slides\slide-NNN.jpg` |
