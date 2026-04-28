# Technical Reference: python-pptx + TUI Template

## Prerequisites

```bash
pip install python-pptx  # v1.0.2+
```

## Converting .potx → .pptx

python-pptx cannot open `.potx` files. Convert first:

```python
import zipfile, os, shutil

def potx_to_pptx(potx_path, pptx_path):
    tmp = '/tmp/_potx_extract'
    shutil.copy2(potx_path, pptx_path)
    with zipfile.ZipFile(pptx_path, 'r') as z:
        z.extractall(tmp)
    ct = os.path.join(tmp, '[Content_Types].xml')
    with open(ct, 'r') as f:
        content = f.read()
    content = content.replace(
        'application/vnd.openxmlformats-officedocument.presentationml.template.main+xml',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml'
    )
    with open(ct, 'w') as f:
        f.write(content)
    os.remove(pptx_path)
    with zipfile.ZipFile(pptx_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(tmp):
            for file in files:
                fp = os.path.join(root, file)
                z.write(fp, os.path.relpath(fp, tmp))
    shutil.rmtree(tmp)
```

**Usage:**
```python
potx_to_pptx(
    "/mnt/c/Users/javier.fernandez/OneDrive - TUI/Desktop/TUI PowerPoint Template_Oct2025 2.potx",
    "/tmp/tui-template.pptx"
)
```

## Core Functions

### Clone a slide from template

```python
from copy import deepcopy
from pptx import Presentation

def clone_slide(target_prs, source_prs, slide_index):
    """Clone slide from source into target presentation.
    slide_index is 0-based (slide 3 = index 2)."""
    src_slide = source_prs.slides[slide_index]
    layout_name = src_slide.slide_layout.name
    
    # Find matching layout in target
    target_layout = None
    for layout in target_prs.slide_layouts:
        if layout.name == layout_name:
            target_layout = layout
            break
    if not target_layout:
        target_layout = target_prs.slide_layouts[0]
    
    new_slide = target_prs.slides.add_slide(target_layout)
    
    # Copy all shapes
    for shape in src_slide.shapes:
        new_slide.shapes._spTree.append(deepcopy(shape._element))
    
    return new_slide
```

### Fill text by shape name

```python
def fill_text(slide, shape_name, text):
    """Replace text in a shape found by name."""
    for shape in slide.shapes:
        if shape.name == shape_name and shape.has_text_frame:
            # Preserve formatting of first paragraph
            para = shape.text_frame.paragraphs[0]
            if para.runs:
                run = para.runs[0]
                run.text = text
                # Clear other runs
                for r in para.runs[1:]:
                    r.text = ""
            else:
                para.text = text
            # Clear other paragraphs
            for p in shape.text_frame.paragraphs[1:]:
                p.text = ""
            return True
    return False
```

### Fill placeholder by index

```python
def fill_placeholder(slide, ph_idx, text):
    """Fill a placeholder by its index number."""
    for shape in slide.placeholders:
        if shape.placeholder_format.idx == ph_idx:
            shape.text = text
            return True
    return False
```

### Fill table cells

```python
def fill_table(slide, data, shape_name=None):
    """Fill a table with 2D data array. Finds first table shape or by name."""
    for shape in slide.shapes:
        if shape.has_table:
            if shape_name and shape.name != shape_name:
                continue
            table = shape.table
            for r, row_data in enumerate(data):
                if r >= len(table.rows):
                    break
                for c, cell_text in enumerate(row_data):
                    if c >= len(table.columns):
                        break
                    table.cell(r, c).text = str(cell_text)
            return True
    return False
```

### Insert image into placeholder

```python
def fill_image(slide, ph_idx, image_path):
    """Insert an image into a picture placeholder."""
    for shape in slide.placeholders:
        if shape.placeholder_format.idx == ph_idx:
            shape.insert_picture(image_path)
            return True
    return False
```

### Find shapes by partial name

```python
def find_shapes(slide, name_contains):
    """Find all shapes whose name contains the given string."""
    return [s for s in slide.shapes if name_contains in s.name]
```

## Full Assembly Example

```python
from pptx import Presentation

# Load template
template = Presentation("/tmp/tui-template.pptx")

# Start from template (keeps all layouts)
prs = Presentation("/tmp/tui-template.pptx")

# Remove all existing slides
while len(prs.slides) > 0:
    rId = prs.slides._sldIdLst[0].get('r:id')
    prs.part.drop_rel(rId)
    prs.slides._sldIdLst.remove(prs.slides._sldIdLst[0])

# 1. Cover (slide 7 = solid sky blue, index 6)
cover = clone_slide(prs, template, 6)
fill_placeholder(cover, 0, "Excellence Tech")
fill_placeholder(cover, 13, "Frontend Engineering Guild — Q2 2026")

# 2. Section divider (slide 37, index 36)
div1 = clone_slide(prs, template, 36)
fill_placeholder(div1, 0, "1. The Problem")
fill_placeholder(div1, 13, "Frontend fragmentation across verticals")

# 3. Two-column comparison (slide 57, index 56)
compare = clone_slide(prs, template, 56)
fill_placeholder(compare, 0, "Current vs Target State")
fill_text(compare, "TextBox 5", "Advantages")
fill_text(compare, "TextBox 6", "• Shared standards\n• Reusable patterns\n• Faster delivery")

# 4. 4-step process (slide 67, index 66)
process = clone_slide(prs, template, 66)
fill_placeholder(process, 0, "Implementation Phases")
# Fill step headers and content...

# 5. Thank you (slide 119, index 118)
thanks = clone_slide(prs, template, 118)
fill_text(thanks, "Titel 2", "Thank you.")
fill_text(thanks, "Textplatzhalter 6",
          "Javier Fernández\x0bFrontend Engineering Guild Lead\x0bjavier.fernandez@tui.com")

# Save
output = "/tmp/excellence-presentation.pptx"
prs.save(output)
print(f"Saved to {output}")
```

## Visual Verification

After generating, convert to images for review:

```bash
# Convert to PDF
soffice --headless --convert-to pdf --outdir /tmp "$OUTPUT_PPTX"

# Convert PDF pages to JPG
pdftoppm -jpeg -r 200 /tmp/output.pdf /tmp/review-slide
```

## TUI Brand Colors (RGB)

```python
from pptx.dml.color import RGBColor

# Primary
TUI_SKY_BLUE     = RGBColor(112, 203, 244)  # Main brand blue
TUI_DEEP_BLUE    = RGBColor(27, 17, 92)     # Dark navy (text, headers)
TUI_ENERGY_BLUE  = RGBColor(53, 103, 246)   # Accent blue
TUI_RED          = RGBColor(212, 14, 20)    # TUI red (logo, accents)
TUI_WHITE        = RGBColor(255, 255, 255)

# Sky Blue tints (for backgrounds, cards)
TUI_SKY_60       = RGBColor(169, 224, 248)
TUI_SKY_40       = RGBColor(198, 234, 251)
TUI_SKY_20       = RGBColor(226, 245, 253)
TUI_SKY_10       = RGBColor(241, 250, 254)

# Functional greens (success, positive)
TUI_DEEP_GREEN   = RGBColor(5, 66, 61)
TUI_BRIGHT_GREEN = RGBColor(48, 182, 117)
TUI_LIGHT_GREEN  = RGBColor(197, 228, 205)

# Alert colors (warning, attention)
TUI_ALERT_DEEP   = RGBColor(243, 147, 0)    # Orange
TUI_ALERT_BRIGHT = RGBColor(243, 203, 71)   # Yellow
TUI_ALERT_LIGHT  = RGBColor(255, 239, 189)  # Light yellow
```

## Font Reference

| Element | Font | Size | Weight | Color |
|---------|------|------|--------|-------|
| Cover title | Ambit | 64pt | Bold | TUI Deep Blue |
| Cover subtitle | Ambit | 40pt | Regular | TUI Deep Blue |
| Content title | Ambit | 36pt | Bold | TUI Deep Blue |
| Content subtitle | Ambit | 28pt | Regular | TUI Deep Blue |
| Heading | Ambit | 20pt | Bold | TUI Deep Blue |
| Body copy | TUI Type Light | 14pt | Regular | TUI Deep Blue |

**Note:** If Ambit font is not installed, text will fall back to the system default. The font should be pre-installed on TUI corporate machines. Download link is on slide 20 of the template.

## Template Dimensions

- **Width:** 13.3" (widescreen 16:9)
- **Height:** 7.5"
- **EMU values:** width=12192000, height=6858000

## Slide Index Reference

All slide numbers in the catalog are **1-based** (as shown in the JPGs and PowerPoint).
python-pptx uses **0-based** indexing. So slide 3 in the catalog = `template.slides[2]` in code.

## File Locations

| What | Path |
|------|------|
| Original .potx | `C:\Users\javier.fernandez\OneDrive - TUI\Desktop\TUI PowerPoint Template_Oct2025 2.potx` |
| WSL path | `/mnt/c/Users/javier.fernandez/OneDrive - TUI/Desktop/TUI PowerPoint Template_Oct2025 2.potx` |
| Converted .pptx | `/tmp/tui-template.pptx` |
| Slide JPGs | `/mnt/c/Users/javier.fernandez/OneDrive - TUI/Desktop/TUI-Template-Slides/slide-NNN.jpg` |
| Shape data (JSON) | `excellence/docs/ppt/template-shapes.json` |
