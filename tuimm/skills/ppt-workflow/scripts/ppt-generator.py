#!/usr/bin/env python3
"""TUI PowerPoint Generator v2 — explicit shape builders, no template cloning.

Usage:
    python3 ppt-generator.py --spec /tmp/ppt-spec.json
    python3 ppt-generator.py --convert-template

Spec JSON: see each slide type builder for its expected fields.
"""

import argparse
import json
import os
import shutil
import sys
import zipfile
from copy import deepcopy
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# === Paths ===
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
POTX_BUNDLED = SKILL_DIR / "assets" / "TUI-Template.potx"
POTX_FALLBACK = Path("/mnt/c/Users/javier.fernandez/OneDrive - TUI/Desktop/TUI PowerPoint Template_Oct2025 2.potx")
PPTX_CACHE = Path("/tmp/tui-template.pptx")

# === Brand Colors ===
DEEP_BLUE = RGBColor(27, 17, 92)
SKY_BLUE = RGBColor(112, 203, 244)
ENERGY_BLUE = RGBColor(53, 103, 246)
TUI_RED = RGBColor(212, 14, 20)
SKY_20 = RGBColor(226, 245, 253)
WHITE = RGBColor(255, 255, 255)
TERM_BG = RGBColor(30, 30, 30)
TERM_GREEN = RGBColor(80, 250, 123)
TERM_YELLOW = RGBColor(241, 250, 140)
TERM_CYAN = RGBColor(139, 233, 253)
TERM_RED = RGBColor(255, 85, 85)
TERM_GRAY = RGBColor(150, 150, 150)

# === Slide dimensions ===
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)
MARGIN = Inches(0.5)
CONTENT_W = SLIDE_W - 2 * MARGIN


# === Template conversion ===

def potx_to_pptx(potx_path, pptx_path):
    tmp = "/tmp/_potx_extract"
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
    shutil.copy2(str(potx_path), str(pptx_path))
    with zipfile.ZipFile(str(pptx_path), "r") as z:
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
    os.remove(str(pptx_path))
    with zipfile.ZipFile(str(pptx_path), "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(tmp):
            for file in files:
                fp = os.path.join(root, file)
                z.write(fp, os.path.relpath(fp, tmp))
    shutil.rmtree(tmp)


def ensure_template():
    if PPTX_CACHE.exists():
        return str(PPTX_CACHE)
    potx = POTX_BUNDLED if POTX_BUNDLED.exists() else POTX_FALLBACK
    if not potx.exists():
        print(f"ERROR: Template not found at {POTX_BUNDLED} or {POTX_FALLBACK}", file=sys.stderr)
        sys.exit(1)
    potx_to_pptx(str(potx), str(PPTX_CACHE))
    return str(PPTX_CACHE)


# === Helpers ===

def get_clean_layout(prs, sky_blue=False):
    """Get a layout from master 0 (no background images)."""
    target = "Cover: Radiant, SkyBlue background" if sky_blue else "Cover: Radiant, White background"
    for layout in prs.slide_masters[0].slide_layouts:
        if layout.name == target:
            return layout
    return prs.slide_masters[0].slide_layouts[0]


def add_clean_slide(prs, sky_blue=False):
    """Add a slide with clean layout, remove all default shapes."""
    layout = get_clean_layout(prs, sky_blue)
    slide = prs.slides.add_slide(layout)
    for shape in list(slide.shapes):
        shape._element.getparent().remove(shape._element)
    return slide


def add_textbox(slide, left, top, width, height, text, font_size=14,
                font_color=DEEP_BLUE, bold=False, font_name="Ambit",
                alignment=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    """Add a textbox with explicit formatting."""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = font_color
    p.font.bold = bold
    p.font.name = font_name
    p.alignment = alignment
    p.space_after = Pt(4)
    return txBox


def add_multiline_textbox(slide, left, top, width, height, lines, font_size=14,
                          font_color=DEEP_BLUE, bold=False, font_name="Ambit",
                          alignment=PP_ALIGN.LEFT, line_spacing=1.15):
    """Add a textbox with multiple paragraphs."""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    for i, line in enumerate(lines):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        # Support (text, color) tuples
        if isinstance(line, tuple):
            p.text, color = line
            p.font.color.rgb = color
        else:
            p.text = line
            p.font.color.rgb = font_color
        p.font.size = Pt(font_size)
        p.font.bold = bold
        p.font.name = font_name
        p.alignment = alignment
        p.space_after = Pt(2)
    return txBox


def add_rounded_rect(slide, left, top, width, height, fill_color):
    """Add a rounded rectangle with solid fill."""
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.fill.background()
    # Smaller corner radius
    shape.adjustments[0] = 0.05
    return shape


def add_arrow(slide, left, top, width, height, fill_color=ENERGY_BLUE):
    """Add a right arrow shape."""
    shape = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.fill.background()
    return shape


def set_notes(slide, text):
    if not slide.has_notes_slide:
        slide.notes_slide
    slide.notes_slide.notes_text_frame.text = text


def remove_all_slides(prs):
    from lxml import etree
    while len(prs.slides._sldIdLst) > 0:
        sldId = prs.slides._sldIdLst[0]
        rId = sldId.get(etree.QName(
            "http://schemas.openxmlformats.org/officeDocument/2006/relationships", "id"))
        if rId is None:
            rId = sldId.get("r:id")
        if rId and rId in prs.part.rels:
            prs.part.drop_rel(rId)
        prs.slides._sldIdLst.remove(sldId)


# === SLIDE TYPE BUILDERS ===
# Each builder takes (prs, spec) and returns the slide.
# Builders are registered in BUILDERS dict at the bottom.

BUILDERS = {}  # populated after builder definitions


def build_cover(prs, spec):
    """Cover slide: sky blue bg, large title, subtitle block."""
    slide = add_clean_slide(prs, sky_blue=True)
    add_textbox(slide, MARGIN, Inches(2.0), CONTENT_W, Inches(1.5),
                spec.get("title", ""), font_size=44, bold=True, font_color=DEEP_BLUE)
    subtitle = spec.get("subtitle", "")
    if subtitle:
        add_textbox(slide, MARGIN, Inches(4.0), CONTENT_W, Inches(2.0),
                    subtitle, font_size=20, font_color=DEEP_BLUE)
    if spec.get("notes"):
        set_notes(slide, spec["notes"])
    return slide


def build_thank_you(prs, spec):
    """Thank you slide: sky blue bg, large text, contact info."""
    slide = add_clean_slide(prs, sky_blue=True)
    add_textbox(slide, MARGIN, Inches(1.0), CONTENT_W, Inches(2.0),
                "Thank you.", font_size=52, bold=True, font_color=DEEP_BLUE)
    contact = spec.get("contact", "")
    if contact:
        add_textbox(slide, MARGIN, Inches(4.5), Inches(6), Inches(2.0),
                    contact, font_size=18, font_color=DEEP_BLUE)
    if spec.get("notes"):
        set_notes(slide, spec["notes"])
    return slide


def build_title(prs, spec):
    """Title + body text slide. White bg."""
    slide = add_clean_slide(prs, sky_blue=False)
    add_textbox(slide, MARGIN, Inches(0.4), CONTENT_W, Inches(1.0),
                spec.get("title", ""), font_size=34, bold=True, font_color=DEEP_BLUE)
    subtitle = spec.get("subtitle", "")
    if subtitle:
        add_textbox(slide, MARGIN, Inches(1.2), CONTENT_W, Inches(0.5),
                    subtitle, font_size=20, font_color=ENERGY_BLUE)
    body = spec.get("body", "")
    body_top = Inches(1.9) if subtitle else Inches(1.5)
    if body:
        lines = body.split("\n") if isinstance(body, str) else body
        add_multiline_textbox(slide, MARGIN, body_top, CONTENT_W, Inches(5.0),
                              lines, font_size=19, font_color=DEEP_BLUE, font_name="TUI Type Light")
    if spec.get("notes"):
        set_notes(slide, spec["notes"])
    return slide


def build_quote(prs, spec):
    """Quote slide: sky blue bg, large centered text + attribution."""
    slide = add_clean_slide(prs, sky_blue=True)
    add_textbox(slide, Inches(1.5), Inches(2.0), Inches(10.3), Inches(2.5),
                spec.get("quote", ""), font_size=36, bold=True,
                font_color=DEEP_BLUE, alignment=PP_ALIGN.CENTER)
    attribution = spec.get("attribution", "")
    if attribution:
        add_textbox(slide, Inches(1.5), Inches(4.8), Inches(10.3), Inches(0.8),
                    attribution, font_size=18, font_color=ENERGY_BLUE,
                    alignment=PP_ALIGN.CENTER)
    if spec.get("notes"):
        set_notes(slide, spec["notes"])
    return slide



def build_terminal(prs, spec):
    """Terminal/CLI slide: dark bg, monospace, colored lines."""
    slide = add_clean_slide(prs, sky_blue=False)
    # Title
    add_textbox(slide, MARGIN, Inches(0.3), CONTENT_W, Inches(0.7),
                spec.get("title", ""), font_size=28, bold=True, font_color=DEEP_BLUE)
    # Terminal background
    term_left = Inches(0.4)
    term_top = Inches(1.1)
    term_w = Inches(12.5)
    term_h = Inches(5.8)
    add_rounded_rect(slide, term_left, term_top, term_w, term_h, TERM_BG)
    # Traffic light dots
    dot_y = term_top + Inches(0.15)
    for i, color in enumerate([RGBColor(255, 95, 86), RGBColor(255, 189, 46), RGBColor(39, 201, 63)]):
        dot = slide.shapes.add_shape(MSO_SHAPE.OVAL,
                                     term_left + Inches(0.25 + i * 0.3), dot_y,
                                     Inches(0.18), Inches(0.18))
        dot.fill.solid()
        dot.fill.fore_color.rgb = color
        dot.line.fill.background()
    # Terminal lines
    lines = spec.get("lines", [])
    color_map = {
        "cyan": TERM_CYAN, "yellow": TERM_YELLOW, "green": TERM_GREEN,
        "red": TERM_RED, "gray": TERM_GRAY, "white": WHITE,
    }
    line_top = term_top + Inches(0.55)
    line_h = Inches(0.28)
    for line_spec in lines[:18]:  # max 18 lines
        if isinstance(line_spec, dict):
            text = line_spec.get("text", "")
            color = color_map.get(line_spec.get("color", "white"), WHITE)
        elif isinstance(line_spec, list) and len(line_spec) == 2:
            text, color_name = line_spec
            color = color_map.get(color_name, WHITE)
        else:
            text = str(line_spec)
            color = WHITE
        if text:
            add_textbox(slide, term_left + Inches(0.3), line_top,
                        term_w - Inches(0.6), line_h,
                        text, font_size=12, font_color=color,
                        font_name="Consolas")
        line_top += line_h
    if spec.get("notes"):
        set_notes(slide, spec["notes"])
    return slide



def build_two_col(prs, spec):
    """Two-column slide: left card (white) + right card (sky blue)."""
    slide = add_clean_slide(prs, sky_blue=False)
    add_textbox(slide, MARGIN, Inches(0.3), CONTENT_W, Inches(0.7),
                spec.get("title", ""), font_size=30, bold=True, font_color=DEEP_BLUE)
    subtitle = spec.get("subtitle", "")
    if subtitle:
        add_textbox(slide, MARGIN, Inches(1.0), CONTENT_W, Inches(0.4),
                    subtitle, font_size=18, font_color=ENERGY_BLUE)
    card_top = Inches(1.6)
    card_h = Inches(5.3)
    card_w = Inches(5.9)
    gap = Inches(0.4)
    # Left card
    left_col = spec.get("left", {})
    add_rounded_rect(slide, MARGIN, card_top, card_w, card_h, WHITE)
    add_textbox(slide, MARGIN + Inches(0.3), card_top + Inches(0.2), card_w - Inches(0.6), Inches(0.5),
                left_col.get("header", ""), font_size=24, bold=True, font_color=DEEP_BLUE)
    left_body = left_col.get("body", "")
    if left_body:
        lines = left_body.split("\n") if isinstance(left_body, str) else left_body
        add_multiline_textbox(slide, MARGIN + Inches(0.3), card_top + Inches(0.8),
                              card_w - Inches(0.6), card_h - Inches(1.0),
                              lines, font_size=20, font_color=DEEP_BLUE, font_name="TUI Type Light")
    # Right card
    right_col = spec.get("right", {})
    right_left = MARGIN + card_w + gap
    add_rounded_rect(slide, right_left, card_top, card_w, card_h, SKY_20)
    add_textbox(slide, right_left + Inches(0.3), card_top + Inches(0.2), card_w - Inches(0.6), Inches(0.5),
                right_col.get("header", ""), font_size=24, bold=True, font_color=DEEP_BLUE)
    right_body = right_col.get("body", "")
    if right_body:
        lines = right_body.split("\n") if isinstance(right_body, str) else right_body
        add_multiline_textbox(slide, right_left + Inches(0.3), card_top + Inches(0.8),
                              card_w - Inches(0.6), card_h - Inches(1.0),
                              lines, font_size=20, font_color=DEEP_BLUE, font_name="TUI Type Light")
    if spec.get("notes"):
        set_notes(slide, spec["notes"])
    return slide


def build_chevron(prs, spec):
    """Chevron process slide: N columns with dark headers + light cards."""
    slide = add_clean_slide(prs, sky_blue=False)
    add_textbox(slide, MARGIN, Inches(0.3), CONTENT_W, Inches(0.7),
                spec.get("title", ""), font_size=28, bold=True, font_color=DEEP_BLUE)
    steps = spec.get("steps", [])
    n = len(steps)
    if n == 0:
        return slide
    gap = Inches(0.25)
    total_gap = gap * (n - 1)
    card_w = int((CONTENT_W - total_gap) / n)
    card_top = Inches(1.3)
    header_h = Inches(0.6)
    body_h = Inches(5.2)
    # Gradient from sky blue to sky 20
    colors = [SKY_BLUE, RGBColor(140, 215, 247), RGBColor(183, 232, 250), SKY_20]
    for i, step in enumerate(steps):
        x = MARGIN + i * (card_w + gap)
        bg_color = colors[i % len(colors)]
        # Header (dark blue)
        add_rounded_rect(slide, x, card_top, card_w, header_h, DEEP_BLUE)
        add_textbox(slide, x + Inches(0.15), card_top + Inches(0.1),
                    card_w - Inches(0.3), header_h - Inches(0.2),
                    step.get("header", f"Step {i+1}"), font_size=15, bold=True,
                    font_color=WHITE)
        # Arrow between headers
        if i < n - 1:
            add_arrow(slide, x + card_w - Inches(0.05), card_top + Inches(0.1),
                      gap + Inches(0.1), Inches(0.4), DEEP_BLUE)
        # Body card
        add_rounded_rect(slide, x, card_top + header_h + Inches(0.1), card_w, body_h, bg_color)
        body = step.get("body", "")
        if body:
            lines = body.split("\n") if isinstance(body, str) else body
            add_multiline_textbox(slide, x + Inches(0.2), card_top + header_h + Inches(0.25),
                                  card_w - Inches(0.4), body_h - Inches(0.3),
                                  lines, font_size=18, font_color=DEEP_BLUE, font_name="TUI Type Light")
    if spec.get("notes"):
        set_notes(slide, spec["notes"])
    return slide


def build_three_cards(prs, spec):
    """Three colored cards slide."""
    slide = add_clean_slide(prs, sky_blue=False)
    add_textbox(slide, MARGIN, Inches(0.3), CONTENT_W, Inches(0.7),
                spec.get("title", ""), font_size=30, bold=True, font_color=DEEP_BLUE)
    cards = spec.get("cards", [])
    card_colors = [SKY_BLUE, DEEP_BLUE, TUI_RED]
    text_colors = [DEEP_BLUE, WHITE, WHITE]
    n = min(len(cards), 3)
    gap = Inches(0.35)
    card_w = int((CONTENT_W - gap * (n - 1)) / n)
    card_top = Inches(1.4)
    card_h = Inches(5.5)
    for i, card in enumerate(cards[:3]):
        x = MARGIN + i * (card_w + gap)
        add_rounded_rect(slide, x, card_top, card_w, card_h, card_colors[i % 3])
        tc = text_colors[i % 3]
        add_textbox(slide, x + Inches(0.3), card_top + Inches(0.3), card_w - Inches(0.6), Inches(0.6),
                    card.get("header", ""), font_size=24, bold=True, font_color=tc)
        body = card.get("body", "")
        if body:
            lines = body.split("\n") if isinstance(body, str) else body
            add_multiline_textbox(slide, x + Inches(0.3), card_top + Inches(1.0),
                                  card_w - Inches(0.6), card_h - Inches(1.3),
                                  lines, font_size=20, font_color=tc, font_name="TUI Type Light")
    if spec.get("notes"):
        set_notes(slide, spec["notes"])
    return slide



def build_table(prs, spec):
    """Table slide: header row + data rows."""
    slide = add_clean_slide(prs, sky_blue=False)
    add_textbox(slide, MARGIN, Inches(0.3), CONTENT_W, Inches(0.7),
                spec.get("title", ""), font_size=28, bold=True, font_color=DEEP_BLUE)
    headers = spec.get("headers", [])
    rows = spec.get("rows", [])
    if not headers:
        return slide
    n_cols = len(headers)
    n_rows = len(rows) + 1  # +1 for header
    tbl_left = MARGIN
    tbl_top = Inches(1.3)
    tbl_w = CONTENT_W
    tbl_h = Inches(0.45) * n_rows
    table_shape = slide.shapes.add_table(n_rows, n_cols, tbl_left, tbl_top, tbl_w, tbl_h)
    table = table_shape.table
    # Header row
    for c, h in enumerate(headers):
        cell = table.cell(0, c)
        cell.text = str(h)
        cell.fill.solid()
        cell.fill.fore_color.rgb = DEEP_BLUE
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(16)
            p.font.color.rgb = WHITE
            p.font.bold = True
            p.font.name = "Ambit"
    # Data rows
    for r, row in enumerate(rows):
        bg = SKY_20 if r % 2 == 0 else WHITE
        for c, val in enumerate(row):
            if c >= n_cols:
                break
            cell = table.cell(r + 1, c)
            cell.text = str(val)
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(15)
                p.font.color.rgb = DEEP_BLUE
                p.font.name = "TUI Type Light"
    if spec.get("notes"):
        set_notes(slide, spec["notes"])
    return slide


def build_diagram(prs, spec):
    """Diagram slide: boxes + arrows + labels. Flexible positioning."""
    slide = add_clean_slide(prs, sky_blue=False)
    add_textbox(slide, MARGIN, Inches(0.3), CONTENT_W, Inches(0.7),
                spec.get("title", ""), font_size=28, bold=True, font_color=DEEP_BLUE)
    color_map = {
        "deep_blue": DEEP_BLUE, "sky_blue": SKY_BLUE, "energy_blue": ENERGY_BLUE,
        "red": TUI_RED, "sky_20": SKY_20, "white": WHITE,
    }
    # Boxes
    for box in spec.get("boxes", []):
        x, y = Inches(box["x"]), Inches(box["y"])
        w, h = Inches(box.get("w", 2.0)), Inches(box.get("h", 0.6))
        fill = color_map.get(box.get("color", "sky_blue"), SKY_BLUE)
        text_color = color_map.get(box.get("text_color", "deep_blue"), DEEP_BLUE)
        rect = add_rounded_rect(slide, x, y, w, h, fill)
        add_textbox(slide, x + Inches(0.1), y + Inches(0.05), w - Inches(0.2), h - Inches(0.1),
                    box.get("text", ""), font_size=box.get("font_size", 13),
                    bold=box.get("bold", False), font_color=text_color,
                    alignment=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    # Arrows
    for arrow in spec.get("arrows", []):
        x, y = Inches(arrow["x"]), Inches(arrow["y"])
        w = Inches(arrow.get("w", 0.4))
        h = Inches(arrow.get("h", 0.3))
        fill = color_map.get(arrow.get("color", "energy_blue"), ENERGY_BLUE)
        shape_type = MSO_SHAPE.DOWN_ARROW if arrow.get("direction") == "down" else MSO_SHAPE.RIGHT_ARROW
        shape = slide.shapes.add_shape(shape_type, x, y, w, h)
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill
        shape.line.fill.background()
    # Labels
    for label in spec.get("labels", []):
        add_textbox(slide, Inches(label["x"]), Inches(label["y"]),
                    Inches(label.get("w", 3.0)), Inches(label.get("h", 0.4)),
                    label.get("text", ""), font_size=label.get("font_size", 16),
                    bold=label.get("bold", True), font_color=color_map.get(label.get("color", "deep_blue"), DEEP_BLUE))
    if spec.get("notes"):
        set_notes(slide, spec["notes"])
    return slide


def build_hybrid_tree(prs, spec):
    """Hybrid tree: compact terminal block at top + categorized boxes below."""
    slide = add_clean_slide(prs, sky_blue=False)
    add_textbox(slide, MARGIN, Inches(0.3), CONTENT_W, Inches(0.6),
                spec.get("title", ""), font_size=26, bold=True, font_color=DEEP_BLUE)
    # Terminal block (compact)
    term_top = Inches(1.0)
    term_h = Inches(2.3)
    add_rounded_rect(slide, MARGIN, term_top, CONTENT_W, term_h, TERM_BG)
    lines = spec.get("tree_lines", [])
    color_map = {"cyan": TERM_CYAN, "yellow": TERM_YELLOW, "green": TERM_GREEN,
                 "gray": TERM_GRAY, "white": WHITE}
    line_y = term_top + Inches(0.15)
    for line_spec in lines[:10]:
        if isinstance(line_spec, list) and len(line_spec) == 2:
            text, color = line_spec[0], color_map.get(line_spec[1], WHITE)
        else:
            text, color = str(line_spec), WHITE
        add_textbox(slide, MARGIN + Inches(0.2), line_y, CONTENT_W - Inches(0.4), Inches(0.2),
                    text, font_size=10, font_color=color, font_name="Consolas")
        line_y += Inches(0.2)
    # Category boxes below
    categories = spec.get("categories", [])
    if categories:
        cat_top = Inches(3.5)
        n = len(categories)
        gap = Inches(0.25)
        cat_w = int((CONTENT_W - gap * (n - 1)) / n)
        cat_colors = [SKY_BLUE, ENERGY_BLUE, DEEP_BLUE, TUI_RED]
        for i, cat in enumerate(categories):
            x = MARGIN + i * (cat_w + gap)
            add_rounded_rect(slide, x, cat_top, cat_w, Inches(3.5), cat_colors[i % len(cat_colors)])
            tc = WHITE if i > 0 else DEEP_BLUE
            add_textbox(slide, x + Inches(0.2), cat_top + Inches(0.15), cat_w - Inches(0.4), Inches(0.4),
                        cat.get("header", ""), font_size=16, bold=True, font_color=tc)
            items = cat.get("items", [])
            if items:
                add_multiline_textbox(slide, x + Inches(0.2), cat_top + Inches(0.6),
                                      cat_w - Inches(0.4), Inches(2.7),
                                      items, font_size=12, font_color=tc, font_name="TUI Type Light")
    if spec.get("notes"):
        set_notes(slide, spec["notes"])
    return slide


# === Builder registry ===

BUILDERS = {
    "cover": build_cover,
    "thank_you": build_thank_you,
    "title": build_title,
    "quote": build_quote,
    "terminal": build_terminal,
    "two_col": build_two_col,
    "chevron": build_chevron,
    "three_cards": build_three_cards,
    "table": build_table,
    "diagram": build_diagram,
    "hybrid_tree": build_hybrid_tree,
}


# === Main generation ===

def generate(spec):
    template_path = spec.get("template", str(PPTX_CACHE))
    if not os.path.exists(template_path):
        template_path = ensure_template()

    append_to = spec.get("append_to")
    if append_to:
        prs = Presentation(append_to)
    else:
        prs = Presentation(template_path)
        remove_all_slides(prs)

    slides_spec = spec.get("slides", [])
    for i, slide_spec in enumerate(slides_spec):
        slide_type = slide_spec.get("type", "title")
        builder = BUILDERS.get(slide_type)
        if not builder:
            print(f"  WARNING: unknown slide type '{slide_type}', using 'title'")
            builder = build_title
        print(f"  Slide {i+1}: {slide_type}")
        builder(prs, slide_spec)

    output_path = spec.get("output", append_to or "/tmp/presentation.pptx")
    prs.save(output_path)
    size = os.path.getsize(output_path)
    print(f"\n✅ Saved: {output_path} ({len(slides_spec)} slides, {size/1024/1024:.1f} MB)")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="TUI PowerPoint Generator v2")
    parser.add_argument("--spec", help="Path to JSON spec file")
    parser.add_argument("--convert-template", action="store_true", help="Just convert .potx → .pptx")
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
