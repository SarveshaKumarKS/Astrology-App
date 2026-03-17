"""
NKV Palan PDF Generator

Generates a standalone Palan (prediction) PDF with three sections:
  1. The Karmic Blueprint (Rahu-Ketu)
  2. The Mental Filter (Saturn-Moon)
  3. The NKV Key Advice

Reuses Tamil text rendering helpers from pdf_generator.py.
"""
# -*- coding: utf-8 -*-

import io
from typing import Dict, Any

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Spacer,
)
from reportlab.graphics.shapes import Drawing, Line, String

from astrology.pdf_generator import (
    tamil_image_flowable, get_font_name,
)
from astrology.models import NKVPalanResult

PAGE_W, PAGE_H = A4
CONTENT_W = PAGE_W - 0.6 * inch


def _section_heading(title_ta: str) -> Table:
    """Render a styled section heading in Tamil."""
    heading_img = tamil_image_flowable(title_ta, font_size=16, is_bold=True, max_width=5.5 * inch)
    data = [[heading_img]]
    tbl = Table(data, colWidths=[CONTENT_W])
    tbl.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("LINEBELOW", (0, -1), (-1, -1), 1, colors.HexColor("#999999")),
    ]))
    return tbl


def _placement_box(placement_ta: str) -> Table:
    """Render placement details in a highlighted box (Tamil only)."""
    ta_img = tamil_image_flowable(placement_ta, font_size=12, max_width=CONTENT_W - 12)
    data = [[ta_img]]
    tbl = Table(data, colWidths=[CONTENT_W - 8])
    tbl.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F0F4F8")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEBEFORE", (0, 0), (0, -1), 3, colors.HexColor("#6B8EC7")),
    ]))
    return tbl


def _wrap_tamil_lines(text: str, chars_per_line: int = 70) -> list:
    """Split Tamil text into wrapped lines for rendering."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip() if current else word
        if len(test) > chars_per_line and current:
            lines.append(current)
            current = word
        else:
            current = test
    if current:
        lines.append(current)
    return lines


def _palan_body(palan_ta: str) -> Table:
    """Render the prediction body text (Tamil only)."""
    ta_lines = _wrap_tamil_lines(palan_ta, chars_per_line=65)
    rows = []
    for line in ta_lines:
        rows.append([tamil_image_flowable(line, font_size=12, max_width=CONTENT_W - 8)])

    tbl = Table(rows, colWidths=[CONTENT_W - 8])
    tbl.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    return tbl


def _birth_summary_table(summary: Dict[str, str]) -> Table:
    """Compact birth summary at the top of the Palan PDF (Tamil only)."""
    fields = [
        ("லக்கினம்", summary.get("Lagna_Tamil", "")),
        ("ராசி", summary.get("Moon_Sign_Tamil", "")),
        ("நட்சத்திரம்", summary.get("Moon_Nakshatra_Tamil", "")),
        ("நட்சத்திர அதிபதி", summary.get("Moon_Star_Lord_Tamil", "")),
    ]
    rows = []
    for ta_label, ta_val in fields:
        rows.append([
            tamil_image_flowable(ta_label, font_size=11, is_bold=True),
            tamil_image_flowable(ta_val, font_size=11),
        ])

    tbl = Table(rows, colWidths=[1.6 * inch, 2.4 * inch])
    tbl.setStyle(TableStyle([
        ("ALIGN", (0, 0), (0, -1), "RIGHT"),
        ("ALIGN", (1, 0), (1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F5F5F5")),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return tbl


def _palan_header() -> Drawing:
    """Draw Palan-specific header."""
    d = Drawing(540, 45)
    d.add(String(270, 30, "ASTRO NKV",
                 fontName=get_font_name("EnglishBold"), fontSize=18,
                 fillColor=colors.HexColor("#333333"),
                 textAnchor="middle"))
    d.add(Line(50, 8, 490, 8,
               strokeColor=colors.HexColor("#666666"), strokeWidth=1))
    return d


def generate_palan_pdf(palan: NKVPalanResult, name: str = "") -> bytes:
    """Generate the NKV Palan PDF and return raw bytes."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        topMargin=0.3 * inch, bottomMargin=0.3 * inch,
        leftMargin=0.3 * inch, rightMargin=0.3 * inch,
    )

    story = []

    # Header
    story.append(_palan_header())
    story.append(Spacer(1, 0.04 * inch))

    # Tamil sub-header
    story.append(tamil_image_flowable("பலன் அறிக்கை", font_size=18, is_bold=True, max_width=3.0 * inch))
    story.append(Spacer(1, 0.04 * inch))

    # Name (if provided)
    if name:
        name_row = Table(
            [[
                tamil_image_flowable("பெயர்", font_size=12, is_bold=True),
                tamil_image_flowable(name, font_size=12),
            ]],
            colWidths=[1.0 * inch, 3.0 * inch],
        )
        name_row.setStyle(TableStyle([
            ("ALIGN", (0, 0), (0, -1), "RIGHT"),
            ("ALIGN", (1, 0), (1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))
        story.append(name_row)
        story.append(Spacer(1, 0.03 * inch))

    # Birth summary
    story.append(_birth_summary_table(palan.birth_summary))
    story.append(Spacer(1, 0.12 * inch))

    # --- Section 1: Karmic Blueprint ---
    story.append(_section_heading(palan.section1_title_tamil))
    story.append(Spacer(1, 0.04 * inch))
    story.append(_placement_box(palan.section1_placement_tamil))
    story.append(Spacer(1, 0.04 * inch))
    story.append(_palan_body(palan.section1_palan_tamil))
    story.append(Spacer(1, 0.12 * inch))

    # --- Section 2: Mental Filter ---
    story.append(_section_heading(palan.section2_title_tamil))
    story.append(Spacer(1, 0.04 * inch))
    story.append(_placement_box(palan.section2_placement_tamil))
    story.append(Spacer(1, 0.04 * inch))
    story.append(_palan_body(palan.section2_palan_tamil))
    story.append(Spacer(1, 0.12 * inch))

    # --- Section 3: Key Advice ---
    story.append(_section_heading(palan.section3_title_tamil))
    story.append(Spacer(1, 0.04 * inch))

    # Dispositor info box
    disp_text_ta = f"ராகுவின் அதிபதி: {palan.rahu_dispositor_tamil}"
    if palan.rahu_dispositor_strong:
        disp_text_ta += " (வலிமையானது — அரசனை உருவாக்குபவர்)"
    story.append(_placement_box(disp_text_ta))
    story.append(Spacer(1, 0.04 * inch))
    story.append(_palan_body(palan.section3_advice_tamil))

    # Build
    doc.build(story)
    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes
