"""
NKV Palan PDF Generator — "Cosmic Blueprint" Edition

Generates a standalone Palan (prediction) PDF focused on current Saturn transit
results from the rasi square.

Header and colour palette are now unified with pdf_generator.py.
"""
# -*- coding: utf-8 -*-

import io
from typing import Dict, Any

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph,
)

# ── Import shared helpers & the unified draw_header ─────────────────────────
from astrology.pdf_generator import (
    tamil_image_flowable, get_font_name, draw_header,
    BG_IVORY, TEXT_NAVY, ACCENT_GOLD, HIGHLIGHT_PALE_GOLD,
    PIL_TEXT_NAVY, PIL_WHITE_TEXT,
)
from astrology.models import NKVPalanResult

PAGE_W, PAGE_H = A4
CONTENT_W = PAGE_W - 0.6 * inch


# ──────────────────────────────────────────────────────────────────────────────
# Section components — Cosmic Blueprint palette
# ──────────────────────────────────────────────────────────────────────────────

def _section_heading(title_ta: str) -> Table:
    """Render a styled section heading in Tamil — TEXT_NAVY text, ACCENT_GOLD underline."""
    heading_img = tamil_image_flowable(
        title_ta, font_size=16, is_bold=True,
        max_width=5.5 * inch, text_color=PIL_TEXT_NAVY,
    )
    data = [[heading_img]]
    tbl = Table(data, colWidths=[CONTENT_W])
    tbl.setStyle(TableStyle([
        ("ALIGN",         (0, 0), (-1, -1), "LEFT"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        # ACCENT_GOLD underline rule
        ("LINEBELOW", (0, -1), (-1, -1), 1.5, ACCENT_GOLD),
    ]))
    return tbl


def _placement_box(placement_ta: str) -> Table:
    """Render placement details — ivory background, ACCENT_GOLD left accent, TEXT_NAVY text."""
    ta_img = tamil_image_flowable(
        placement_ta, font_size=12,
        max_width=CONTENT_W - 20, text_color=PIL_TEXT_NAVY,
    )
    data = [[ta_img]]
    tbl = Table(data, colWidths=[CONTENT_W - 8])
    tbl.setStyle(TableStyle([
        ("ALIGN",         (0, 0), (-1, -1), "LEFT"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        # Ivory/pale-gold background
        ("BACKGROUND",    (0, 0), (-1, -1), HIGHLIGHT_PALE_GOLD),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        # ACCENT_GOLD left border accent (3 pt)
        ("LINEBEFORE",    (0, 0), (0, -1), 3, ACCENT_GOLD),
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
    """Render the prediction body text (Tamil, TEXT_NAVY)."""
    ta_lines = _wrap_tamil_lines(palan_ta, chars_per_line=65)
    rows = []
    for line in ta_lines:
        rows.append([tamil_image_flowable(
            line, font_size=12,
            max_width=CONTENT_W - 8, text_color=PIL_TEXT_NAVY,
        )])

    tbl = Table(rows, colWidths=[CONTENT_W - 8])
    tbl.setStyle(TableStyle([
        ("ALIGN",         (0, 0), (-1, -1), "LEFT"),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
        ("TOPPADDING",    (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    return tbl


def _birth_summary_table(summary: Dict[str, str]) -> Table:
    """Compact birth summary at the top of the Palan PDF — Cosmic Blueprint palette."""
    fields = [
        ("லக்கினம்",        summary.get("Lagna_Tamil", "")),
        ("ராசி",            summary.get("Moon_Sign_Tamil", "")),
        ("நட்சத்திரம்",      summary.get("Moon_Nakshatra_Tamil", "")),
        ("நட்சத்திர அதிபதி", summary.get("Moon_Star_Lord_Tamil", "")),
    ]
    rows = []
    for ta_label, ta_val in fields:
        rows.append([
            tamil_image_flowable(ta_label, font_size=11, is_bold=True,
                                 text_color=PIL_TEXT_NAVY),
            tamil_image_flowable(ta_val,   font_size=11,
                                 text_color=PIL_TEXT_NAVY),
        ])

    tbl = Table(rows, colWidths=[1.6 * inch, 2.4 * inch])
    tbl.setStyle(TableStyle([
        ("ALIGN",         (0, 0), (0, -1), "RIGHT"),
        ("ALIGN",         (1, 0), (1, -1), "LEFT"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        # Thin gold grid
        ("GRID",          (0, 0), (-1, -1), 0.5, ACCENT_GOLD),
        # Pale gold background on label column
        ("BACKGROUND",    (0, 0), (0, -1), HIGHLIGHT_PALE_GOLD),
        ("BACKGROUND",    (1, 0), (1, -1), BG_IVORY),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
        ("TOPPADDING",    (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return tbl


def _saturn_transit_table(palan: NKVPalanResult) -> Table:
    """Render current Saturn transit targets in a compact note-style table."""
    transit = palan.saturn_transit
    if not transit:
        return _placement_box("தற்போதைய சனி பார்வை பலன் கணிக்கப்படவில்லை.")

    rows = [[
        tamil_image_flowable("பார்வை", font_size=11, is_bold=True, text_color=PIL_WHITE_TEXT),
        tamil_image_flowable("ராசி / இடம்", font_size=11, is_bold=True, text_color=PIL_WHITE_TEXT),
        tamil_image_flowable("உள்ள கிரகங்கள்", font_size=11, is_bold=True, text_color=PIL_WHITE_TEXT),
        tamil_image_flowable("பலன் பொருள்", font_size=11, is_bold=True, text_color=PIL_WHITE_TEXT),
    ]]

    for item in transit.affected_houses:
        rows.append([
            tamil_image_flowable(f"{item.get('aspect')}ஆம்", font_size=10, text_color=PIL_TEXT_NAVY),
            tamil_image_flowable(
                f"{item.get('sign_tamil')} / {item.get('house')}ஆம் இடம்",
                font_size=10,
                text_color=PIL_TEXT_NAVY,
            ),
            tamil_image_flowable(str(item.get("planets_tamil", "")), font_size=10, text_color=PIL_TEXT_NAVY),
            tamil_image_flowable(str(item.get("topics_tamil", "")), font_size=10, text_color=PIL_TEXT_NAVY),
        ])

    tbl = Table(rows, colWidths=[0.7 * inch, 1.35 * inch, 1.35 * inch, CONTENT_W - 3.4 * inch])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TEXT_NAVY),
        ("BACKGROUND", (0, 1), (-1, -1), BG_IVORY),
        ("GRID", (0, 0), (-1, -1), 0.4, ACCENT_GOLD),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return tbl


# ──────────────────────────────────────────────────────────────────────────────
# Main PDF entry point
# ──────────────────────────────────────────────────────────────────────────────

def generate_palan_pdf(palan: NKVPalanResult, name: str = "") -> bytes:
    """Generate the NKV Palan PDF and return raw bytes."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        topMargin=0.2 * inch, bottomMargin=0.2 * inch,
        leftMargin=0.3 * inch, rightMargin=0.3 * inch,
    )

    story = []

    # ── 1. Unified "Cosmic Blueprint" header (identical to horoscope PDF) ──────
    story.append(draw_header())
    story.append(Spacer(1, 0.06 * inch))

    # ── 2. Section title: பலன் அறிக்கை ──────────────────────────────────────
    story.append(tamil_image_flowable(
        "பலன் அறிக்கை", font_size=18, is_bold=True,
        max_width=3.5 * inch, text_color=PIL_TEXT_NAVY,
    ))
    story.append(Spacer(1, 0.05 * inch))

    # ── 3. Name row (if provided) ─────────────────────────────────────────────
    if name:
        name_row = Table(
            [[
                tamil_image_flowable("பெயர்", font_size=12, is_bold=True,
                                     text_color=PIL_TEXT_NAVY),
                tamil_image_flowable(name, font_size=12,
                                     text_color=PIL_TEXT_NAVY),
            ]],
            colWidths=[1.0 * inch, 3.0 * inch],
        )
        name_row.setStyle(TableStyle([
            ("ALIGN",         (0, 0), (0, -1), "RIGHT"),
            ("ALIGN",         (1, 0), (1, -1), "LEFT"),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING",   (0, 0), (-1, -1), 4),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
            ("TOPPADDING",    (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))
        story.append(name_row)
        story.append(Spacer(1, 0.04 * inch))

    # ── 4. Birth summary ──────────────────────────────────────────────────────
    story.append(_birth_summary_table(palan.birth_summary))
    story.append(Spacer(1, 0.14 * inch))

    # ── 5. Current Saturn transit from rasi square ────────────────────────────
    if palan.saturn_transit:
        story.append(_section_heading("தற்போதைய சனி பார்வை பலன்"))
        story.append(Spacer(1, 0.05 * inch))
        story.append(_placement_box(palan.saturn_transit.placement_tamil))
        story.append(Spacer(1, 0.05 * inch))
        story.append(_placement_box(palan.saturn_transit.aspect_summary_tamil))
        story.append(Spacer(1, 0.05 * inch))
        story.append(_saturn_transit_table(palan))
        story.append(Spacer(1, 0.05 * inch))
        story.append(_palan_body(" ".join(palan.saturn_transit.result_lines_tamil)))
        story.append(Spacer(1, 0.14 * inch))

    # ── 6. Section 2: Mental Filter ───────────────────────────────────────────
    story.append(_section_heading(palan.section2_title_tamil))
    story.append(Spacer(1, 0.05 * inch))
    story.append(_placement_box(palan.section2_placement_tamil))
    story.append(Spacer(1, 0.05 * inch))
    story.append(_palan_body(palan.section2_palan_tamil))

    # ── Build ─────────────────────────────────────────────────────────────────
    doc.build(story)
    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes
