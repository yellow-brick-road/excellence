# Catalog: Tables, Graphs, Timelines & End Slide (Slides 93-119)

---

## Slide 93 — Section Divider "7. Tables"

Section divider. Use slide 21 or 37 instead.

---

## Slide 94 — Basic Data Table (5×10)

**Layout:** `Content Slide 1`
**Visual:** 5 columns × 10 data rows. Cyan header row ("Title row"), alternating light blue/white row shading, dark blue "Total" footer row.
**Use for:** Data tables, metrics, any tabular data.

| Shape | Name | Content to fill |
|-------|------|----------------|
| Title | `Title 5` (PH 0) | Slide title |
| Subtitle | `Subtitle 6` (PH 13) | Subtitle |
| Table | `Table 7` | Access via `shape.table` — iterate rows/columns/cells |

**Table access pattern:**
```python
for shape in slide.shapes:
    if shape.has_table:
        table = shape.table
        # table.rows[0] = header row
        # table.cell(row, col).text = "value"
```

---

## Slide 95 — Complex Table (Merged Headers)

**Layout:** `Content Slide 1`
**Visual:** Title row spanning sub-columns. 3 data rows with hierarchical bullet content (Level 1/2/3) in the first column. 6 data columns.
**Use for:** Multi-level data, grouped categories.

| Shape | Name | Content to fill |
|-------|------|----------------|
| Title | `Title 5` (PH 0) | Slide title |
| Subtitle | `Subtitle 6` (PH 13) | Subtitle |
| Table | Table shape | Merged header cells + data cells |

---

## Slide 96 — Dense Multi-Category Comparison Table

**Layout:** `Content Slide 1`
**Visual:** Row headers on left. 3 grouped column headers ("Title") each with 3 sub-columns ("Subtitle"). 5 data rows.
**Use for:** Multi-dimensional comparisons, benchmark tables.

Same access pattern as slide 94.

---

## Slide 97 — Table + Commentary Split

**Layout:** `Content Slide 1`
**Visual:** Left side: 3-column × 7-row color-coded table (cyan/navy/light blue). Right side: large bordered text box for commentary.
**Use for:** Data with narrative explanation.

| Shape | Name | Content to fill |
|-------|------|----------------|
| Title | `Title 2` (PH 0) | Slide title |
| Subtitle | `Subtitle 3` (PH 13) | Subtitle |
| Commentary | `Rectangle: Rounded Corners 11` | Commentary text |
| Table | Table shape (left side) | Table data |

---

## Slide 98 — Dual Table + Notes

**Layout:** `Content Slide 1`
**Visual:** Left: 3-column table (3 rows) + titled text box below. Right: 3-column × 6-row table. Two tables with supporting notes.
**Use for:** Comparing two datasets with annotations.

| Shape | Name | Content to fill |
|-------|------|----------------|
| Title | `Title 3` (PH 0) | Slide title |
| Subtitle | `Subtitle 5` (PH 13) | Subtitle |
| Note boxes | `Rectangle: Rounded Corners` shapes (3) | Section headers / notes |
| Tables | Table shapes (2) | Table data |

---

## Slide 99 — Action Tracker

**Layout:** `Content Slide 1`
**Visual:** 4 columns: Next Steps, Deadline, Responsible, Comments. 6 empty rows. Dark blue header row, alternating row colors.
**Use for:** Action item tracking, meeting follow-ups, task lists.

| Shape | Name | Content to fill |
|-------|------|----------------|
| Title | `Title 5` (PH 0) | Slide title |
| Subtitle | `Subtitle 6` (PH 13) | Subtitle |
| Table | `Tabelle 4` | 4-column action tracker table |

---

## Slide 100 — Financial / KPI Dashboard

**Layout:** `Content Slide 3`
**Visual:** 3 business segments (Hotels, Cruises, Tickets) with icons. Each shows Figure 1-3 metrics across H1, Q3, Q4, and Category Year with YoY percentage changes.
**Use for:** Financial updates, KPI dashboards, business reviews.

| Shape | Name | Content to fill |
|-------|------|----------------|
| Title | `Title 2` (PH 0) | Dashboard title |
| Segment headers | `Rectangle: Rounded Corners` shapes (3) | Segment names |
| Metrics | Multiple `Rectangle` + `TextBox` shapes | Metric values and labels |
| YoY changes | `TextBox` shapes | Percentage changes |

---

## Slide 101 — Section Divider "8. Graphs"

Section divider. Use slide 21 or 37 instead.

---

## Slide 102 — Bar Chart Comparison (FC vs Plan)

**Layout:** `Content Slide 1`
**Visual:** Two-column layout. Left: grouped bar chart showing "Portfolio" index data (FC 2022 vs Plan 2023) with absolute values. Right: same data as percentages. Summary banner at bottom.
**Use for:** Year-over-year comparisons, budget vs actual.

| Shape | Name | Content to fill |
|-------|------|----------------|
| Title | `Title 28` (PH 0) | Chart title |
| Subtitle | `Subtitle 29` (PH 13) | Subtitle |
| Index labels | `Rectangle: Rounded Corners` shapes | "Index" headers |
| Summary | `TextBox` shapes | Summary text |

**⚠️ Chart is an OLE object (think-cell). Not editable via python-pptx. Modify surrounding text boxes only.**

---

## Slide 103 — 4-Chart Sampler

**Layout:** `Content Slide 1`
**Visual:** 4 quadrants: (1) grouped bar chart over 6 years with growth annotations, (2) think-cell placeholder, (3) donut/pie chart by segment, (4) descending bar chart by category.
**Use for:** Multi-metric overview, dashboard-style data presentation.

| Shape | Name | Content to fill |
|-------|------|----------------|
| Title | `Title 48` (PH 0) | Slide title |
| Quadrant labels | `Rectangle 46` shapes | "Index" headers |
| Point labels | `TextBox` shapes | "Point 1" through "Point 4" |
| Data labels | `Rectangle` shapes | Year labels, segment names, percentages |

**⚠️ Charts are OLE objects. Text labels around them are editable.**

---

## Slide 104 — Donut Chart + Comments

**Layout:** `Content Slide 1`
**Visual:** Left: donut chart with stacked percentage legend (Germany 20%, Switzerland 8%, EU excl. Germany 62%, etc.). Right: light blue "Comments" panel with bullet placeholders.
**Use for:** Distribution/share data with narrative.

| Shape | Name | Content to fill |
|-------|------|----------------|
| Title | `Title 27` (PH 0) | Chart title |
| Comments | `TextBox 5` + `Rectangle: Rounded Corners 4` | Comments text |

---

## Slide 105 — Line Chart + Comments

**Layout:** `Content Slide 1`
**Visual:** Left: multi-year line chart (Oct-Sep, 4 series for 2022-2025). Right: "Comments" panel.
**Use for:** Trend data over time with commentary.

Same pattern as slide 104.

---

## Slide 106 — Grouped Bar Chart + Comments

**Layout:** `Content Slide 1`
**Visual:** Left: grouped bar chart (3 series: Lorem, Ipsum, Dolor across Q1-Q4). Right: "Comments" panel.
**Use for:** Quarterly comparisons across categories.

Same pattern as slide 104.

---

## Slide 107 — Simple 2-Bar Comparison

**Layout:** `Content Slide 1`
**Visual:** Left: two bars (2022 value ~230 vs 2023 value 471) with "2x EBITA Growth" annotation. Right: "Comments" panel.
**Use for:** Before/after, dramatic growth visualization.

| Shape | Name | Content to fill |
|-------|------|----------------|
| Title | `Title 18` (PH 0) | Chart title |
| Bar labels | `Rechteck` shapes | Year labels + values |
| Growth annotation | `Ellipse 13` | Growth text (e.g., "2x") |
| Comments | `TextBox` shapes | Commentary |

---

## Slide 108 — Multi-Series Line Chart + Comments

**Layout:** `Content Slide 1`
**Visual:** Left: 5 series line chart over 2022-2024. Right: "Comments" panel.
**Use for:** Multi-metric trend analysis.

Same pattern as slide 104.

---

## Slide 109 — Scatter / Quadrant Plot

**Layout:** `Content Slide 1`
**Visual:** Left: 2×2 quadrant template (Axis × Axis) for scatter/positioning. Right: "Comments" panel.
**Use for:** Strategic positioning, priority matrices, risk assessment.

Same pattern as slide 104.

---

## Slide 110 — Heat Map / Matrix (3×3)

**Layout:** `Content Slide 1`
**Visual:** Left: 3×3 grid (Title × Title, low/medium/high axes). Dark navy cells indicate intensity. Right: "Comments" panel.
**Use for:** Risk matrices, capability assessments, priority grids.

Same pattern as slide 104.

---

## Slide 111 — Section Divider "9. Timelines"

Section divider. Use slide 21 or 37 instead.

---

## Slide 112 — Monthly Timeline with Milestones

**Layout:** `Content Slide 1`
**Visual:** Horizontal timeline spanning Jan-Feb 2023. Month labels across the top. Milestone dots along the timeline with callout annotations above and below.
**Use for:** Short-term project timelines, sprint plans, event schedules.

| Shape | Name | Content to fill |
|-------|------|----------------|
| Title | `Title 106` (PH 0) | Timeline title |
| Subtitle | `Subtitle 107` (PH 13) | Subtitle |
| Month labels | `Rectangle` shapes (12) | "January" through "November" + "Feb 2023" |
| Callout text | `TextBox` shapes (6+) | "Add all relevant information here" — replace with milestone descriptions |
| Timeline arrow | `Arrow: Right 3` | Keep as-is |

---

## Slide 113 — Multi-Year Timeline (4 Years)

**Layout:** `Content Slide 1`
**Visual:** Horizontal timeline spanning 2022-2025. Four speech-bubble callout boxes (two above, two below the line) for yearly highlights with bullet-point placeholders.
**Use for:** Strategic roadmaps, multi-year plans.

| Shape | Name | Content to fill |
|-------|------|----------------|
| Title | `Title 21` (PH 0) | Timeline title |
| Subtitle | `Subtitle 22` (PH 13) | Subtitle |
| Year callouts | `AutoShape` + `TextBox` shapes | Year highlights |

---

## Slide 114 — Gantt Chart (12 Months)

**Layout:** `Content Slide 1`
**Visual:** 12-month grid (Jan-Dec). Staggered horizontal bars (dark navy above, light blue below) representing overlapping project phases or workstreams.
**Use for:** Project Gantt charts, resource planning.

| Shape | Name | Content to fill |
|-------|------|----------------|
| Month headers | `Rectangle 44` shapes (12) | Month names |
| Task bars | `Rectangle 44` shapes (colored) | Task/phase names |

**Note:** Bars are individual rectangles. Resize width to change duration, reposition to change start date.

---

## Slide 115 — Annual Roadmap with "We Are Here" Marker

**Layout:** `Content Slide 1`
**Visual:** Jan-Dec timeline with "We Are Here" pin marker. Two grouped swim lanes (dotted-border sections) each containing four overlapping horizontal task bars.
**Use for:** Product roadmaps, annual planning with current position.

| Shape | Name | Content to fill |
|-------|------|----------------|
| Title | `Title 2` (PH 0) | Roadmap title |
| Subtitle | `Subtitle 3` (PH 13) | Subtitle |
| Swim lane headers | `Rectangle: Rounded Corners` shapes | Workstream names |
| Task bars | `Rectangle` shapes | Task names + durations |

---

## Slide 116 — Weekly Gantt with Workstreams

**Layout:** `Content Slide 1`
**Visual:** Weekly grid (Feb-May). Two labeled workstreams with color-coded task bars (light blue and blue). Red vertical "today" marker.
**Use for:** Sprint-level planning, weekly task tracking.

| Shape | Name | Content to fill |
|-------|------|----------------|
| Title | `Title 1` (PH 0) | Gantt title |
| Subtitle | `Subtitle 2` (PH 13) | Subtitle |
| Week headers | `Rectangle 44` shapes | Week/month labels |
| Task bars | `Rectangle 44` shapes (colored) | Task names |

---

## Slide 117 — Interactive World Map

**Layout:** `Content Slide 3`
**Visual:** World map on light blue background. Some countries highlighted in dark navy (e.g., Brazil, France, Indonesia). Text placeholder for geographic data annotation.
**Use for:** Geographic data, market presence, expansion plans.

| Shape | Name | Content to fill |
|-------|------|----------------|
| Title | `Title 3` (PH 0) | Map title |
| Subtitle | `Subtitle 194` (PH 13) | Subtitle |
| Annotation | `TextBox 7` | Geographic data text |
| Map | `Google Shape` | Map shape — countries are sub-elements |

---

## Slide 118 — Section Divider "10. End Slide"

Section divider. Use slide 21 or 37 instead.

---

## Slide 119 — Thank You / Closing

**Layout:** `Content Slide 6`
**Visual:** Gradient blue background. Large bold "Thank you." text. Presenter contact details (name, department, phone, email) in bottom-left. TUI smiley logo bottom-right.
**Use for:** Final slide of every presentation.

| Shape | Name | Content to fill |
|-------|------|----------------|
| Title | `Titel 2` | "Thank you." (or custom closing text) |
| Contact | `Textplatzhalter 6` | Multi-line: Name, Department, Phone, Email (separated by line breaks `\x0b`) |

**Example:**
```python
fill_text(slide, "Textplatzhalter 6", "Javier Fernández\x0bFrontend Engineering Guild\x0bPhone +34 XXX XXX XXX\x0bjavier.fernandez@tui.com")
fill_text(slide, "Titel 2", "Thank you.")
```
