#!/usr/bin/env python3
"""TUI PowerPoint Generator — clone template slides and fill content.

Usage:
    python3 ppt-generator.py --spec /tmp/ppt-spec.json
    python3 ppt-generator.py --convert-template  # just convert .potx → .pptx

Spec JSON format:
{
    "template": "/tmp/tui-template.pptx",
    "output": "/tmp/my-presentation.pptx",     # new file
    "append_to": "/path/to/existing.pptx",      # OR append to existing
    "insert_at": -1,                             # -1=end, 0=start, N=after slide N
    "slides": [
        {
            "clone": 7,                          # 1-based slide number from template
            "content": {
                "Title 5": "My Title",           # shape name → text
                "ph:0": "Alt title via PH index", # ph:N → placeholder index
                "table:0": [["A","B"],["1","2"]] # table:N → 2D array (Nth table)
            },
            "notes": "Speaker notes text"
        }
    ]
}
"""

import argparse
import json
import os
import shutil
import sys
import zipfile
from copy import deepcopy
from pathlib import Path

POTX_PATH = "/mnt/c/Users/javier.fernandez/OneDrive - TUI/Desktop/TUI PowerPoint Template_Oct2025 2.potx"
PPTX_CACHE = "/tmp/tui-template.pptx"


def potx_to_pptx(potx_path, pptx_path):
    """Convert .potx template to .pptx (python-pptx can't open .potx)."""
    tmp = "/tmp/_potx_extract"
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
    shutil.copy2(potx_path, pptx_path)
    with zipfile.ZipFile(pptx_path, "r") as z:
        z.extractall(tmp)
    ct = os.path.join(tmp, "[Content_Types].xml")
    with open(ct, "r") as f:
        content = f.read()
    content = content.replace(
        "application/vnd.openxmlformats-officedocument.presentationml.template.main+xml",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml",
    )
    with open(ct, "w") as f:
        f.write(content)
    os.remove(pptx_path)
    with zipfile.ZipFile(pptx_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(tmp):
            for file in files:
                fp = os.path.join(root, file)
                z.write(fp, os.path.relpath(fp, tmp))
    shutil.rmtree(tmp)
    print(f"Converted {potx_path} → {pptx_path}")


def ensure_template():
    """Ensure the .pptx template exists, converting from .potx if needed."""
    if os.path.exists(PPTX_CACHE):
        return PPTX_CACHE
    if not os.path.exists(POTX_PATH):
        print(f"ERROR: Template not found at {POTX_PATH}", file=sys.stderr)
        sys.exit(1)
    potx_to_pptx(POTX_PATH, PPTX_CACHE)
    return PPTX_CACHE


def clone_slide(target_prs, source_prs, slide_num):
    """Clone slide from source into target. slide_num is 1-based."""
    from pptx.oxml.ns import qn

    src_slide = source_prs.slides[slide_num - 1]
    layout_name = src_slide.slide_layout.name

    target_layout = None
    for layout in target_prs.slide_layouts:
        if layout.name == layout_name:
            target_layout = layout
            break
    if not target_layout:
        target_layout = target_prs.slide_layouts[0]

    new_slide = target_prs.slides.add_slide(target_layout)

    # Remove default placeholder shapes from new slide
    for shape in list(new_slide.shapes):
        sp = shape._element
        sp.getparent().remove(sp)

    # Copy all shapes from source
    for shape in src_slide.shapes:
        new_slide.shapes._spTree.append(deepcopy(shape._element))

    # Copy slide background if present
    src_bg = src_slide.background._element
    if src_bg is not None:
        new_bg = deepcopy(src_bg)
        new_slide.background._element.getparent().replace(
            new_slide.background._element, new_bg
        )

    return new_slide


def fill_text(slide, shape_name, text):
    """Replace text in a shape by name, preserving formatting."""
    for shape in slide.shapes:
        if shape.name == shape_name and shape.has_text_frame:
            tf = shape.text_frame
            # Handle multi-line with \n
            lines = text.split("\n")
            # First line: preserve formatting of first run
            if tf.paragraphs and tf.paragraphs[0].runs:
                tf.paragraphs[0].runs[0].text = lines[0]
                for r in tf.paragraphs[0].runs[1:]:
                    r.text = ""
            else:
                tf.paragraphs[0].text = lines[0]
            # Clear remaining original paragraphs
            for p in tf.paragraphs[1:]:
                p.clear()
                p.text = ""
            # Add extra lines as new paragraphs (copy format from first)
            if len(lines) > 1:
                from pptx.oxml.ns import qn

                for line in lines[1:]:
                    new_p = deepcopy(tf.paragraphs[0]._element)
                    # Set text of first run in the new paragraph
                    runs = new_p.findall(qn("a:r"))
                    if runs:
                        runs[0].find(qn("a:t")).text = line
                        for r in runs[1:]:
                            r.find(qn("a:t")).text = ""
                    tf._txBody.append(new_p)
            return True
    return False


def fill_placeholder(slide, ph_idx, text):
    """Fill a placeholder by index."""
    for shape in slide.placeholders:
        if shape.placeholder_format.idx == ph_idx:
            shape.text = text
            return True
    return False


def fill_table(slide, data, table_index=0):
    """Fill a table with 2D data. table_index selects which table on the slide."""
    tables_found = 0
    for shape in slide.shapes:
        if shape.has_table:
            if tables_found == table_index:
                table = shape.table
                for r, row_data in enumerate(data):
                    if r >= len(table.rows):
                        break
                    for c, cell_text in enumerate(row_data):
                        if c >= len(table.columns):
                            break
                        table.cell(r, c).text = str(cell_text)
                return True
            tables_found += 1
    return False


def set_notes(slide, text):
    """Set speaker notes on a slide."""
    from pptx.oxml.ns import qn

    if not slide.has_notes_slide:
        slide.notes_slide  # creates it
    notes_slide = slide.notes_slide
    notes_tf = notes_slide.notes_text_frame
    notes_tf.text = text


def remove_all_slides(prs):
    """Remove all slides from a presentation (keep layouts)."""
    from lxml import etree

    while len(prs.slides._sldIdLst) > 0:
        sldId = prs.slides._sldIdLst[0]
        rId = sldId.get(etree.QName("http://schemas.openxmlformats.org/officeDocument/2006/relationships", "id"))
        if rId is None:
            rId = sldId.get("r:id")
        if rId and rId in prs.part.rels:
            prs.part.drop_rel(rId)
        prs.slides._sldIdLst.remove(sldId)


def process_content(slide, content):
    """Process a content dict, routing to the right fill function."""
    for key, value in content.items():
        if key.startswith("ph:"):
            ph_idx = int(key.split(":")[1])
            if not fill_placeholder(slide, ph_idx, value):
                print(f"  WARNING: placeholder {ph_idx} not found")
        elif key.startswith("table:"):
            table_idx = int(key.split(":")[1])
            if not fill_table(slide, value, table_idx):
                print(f"  WARNING: table {table_idx} not found")
        else:
            if not fill_text(slide, key, value):
                # Try as placeholder name fallback
                print(f"  WARNING: shape '{key}' not found")


def generate(spec):
    """Generate presentation from spec dict."""
    from pptx import Presentation

    template_path = spec.get("template", PPTX_CACHE)
    if not os.path.exists(template_path):
        template_path = ensure_template()

    template = Presentation(template_path)

    append_to = spec.get("append_to")
    if append_to:
        prs = Presentation(append_to)
        insert_at = spec.get("insert_at", -1)
    else:
        prs = Presentation(template_path)
        remove_all_slides(prs)
        insert_at = -1

    slides_spec = spec.get("slides", [])
    for i, slide_spec in enumerate(slides_spec):
        clone_num = slide_spec["clone"]
        print(f"  Slide {i+1}: cloning template slide {clone_num}")
        new_slide = clone_slide(prs, template, clone_num)

        content = slide_spec.get("content", {})
        if content:
            process_content(new_slide, content)

        notes = slide_spec.get("notes")
        if notes:
            set_notes(new_slide, notes)

    output_path = spec.get("output", append_to or "/tmp/presentation.pptx")
    prs.save(output_path)
    size = os.path.getsize(output_path)
    print(f"\n✅ Saved: {output_path} ({len(slides_spec)} slides, {size/1024/1024:.1f} MB)")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="TUI PowerPoint Generator")
    parser.add_argument("--spec", help="Path to JSON spec file")
    parser.add_argument(
        "--convert-template",
        action="store_true",
        help="Just convert .potx → .pptx",
    )
    args = parser.parse_args()

    if args.convert_template:
        ensure_template()
        return

    if not args.spec:
        parser.print_help()
        sys.exit(1)

    with open(args.spec) as f:
        spec = json.load(f)

    generate(spec)


if __name__ == "__main__":
    main()
