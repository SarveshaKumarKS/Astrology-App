"""
PDF Generator for Tamil Astrology Horoscopes — "Cosmic Blueprint" Premium Design
Sacred, authoritative, and deeply personal layout with a luxurious spiritual palette.
"""
# -*- coding: utf-8 -*-

import io
import os
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

# ReportLab imports
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    Image as RLImage, KeepTogether,
)
from reportlab.graphics.shapes import Drawing, Line
from reportlab.graphics import renderPDF

# Pillow imports for Tamil text rendering
try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    print("⚠ Warning: Pillow not available. Tamil text will not render correctly.")

# ── Project paths ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent.parent

TSCU_FONT_PATH = PROJECT_ROOT / "TSCu_SaiIndira.ttf"

MURUGA_ICON_PATH = PROJECT_ROOT / "murugan.jpeg"

TAMIL_FONT_PATHS = [
    str(TSCU_FONT_PATH),
    str(PROJECT_ROOT / "TSCu_SaiIndira.ttf"),
    str(Path.cwd() / "TSCu_SaiIndira.ttf"),
    "/usr/share/fonts/truetype/noto/NotoSerifTamil-Regular.ttf",
    "/System/Library/Fonts/Supplemental/NotoSansTamil-Regular.ttf",
]

TAMIL_BOLD_FONT_PATHS = [
    str(TSCU_FONT_PATH),
    str(PROJECT_ROOT / "TSCu_SaiIndira.ttf"),
    str(Path.cwd() / "TSCu_SaiIndira.ttf"),
    "/usr/share/fonts/truetype/noto/NotoSerifTamil-Bold.ttf",
    "/System/Library/Fonts/Supplemental/NotoSansTamil-Bold.ttf",
]

ENGLISH_BOLD_FONT    = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ENGLISH_REGULAR_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# ── Cosmic Blueprint Color Palette ────────────────────────────────────────────
BG_IVORY            = colors.HexColor('#FDFBF7')   # Soft ivory page/table background
TEXT_NAVY           = colors.HexColor('#1A2A3A')   # Primary text — deep navy
ACCENT_GOLD         = colors.HexColor('#D4AF37')   # Borders, dividers, highlights
HIGHLIGHT_PALE_GOLD = colors.HexColor('#F9F1D8')   # Lagna cell fill

# Legacy (kept so nothing external breaks)
GREEN       = colors.HexColor('#008000')
YELLOW      = colors.HexColor('#FFFF00')
LIGHT_GREEN = colors.HexColor('#E8F5E9')

# Subtle zebra colour for planetary table
ZEBRA_OFF_WHITE = colors.HexColor('#F7F5F0')

# ── PIL (Pillow) color tuples ──────────────────────────────────────────────────
PIL_TEXT_NAVY           = (26,  42,  58,  255)   # RGBA
PIL_ACCENT_GOLD         = (212, 175, 55,  255)   # RGBA
PIL_ACCENT_GOLD_BORDER  = (212, 175, 55)         # RGB for PIL rectangles
PIL_HIGHLIGHT_PALE_GOLD = (249, 241, 216)         # RGB for cell fill
PIL_BG_IVORY            = (253, 251, 247)         # RGB for chart background
PIL_WHITE_TEXT          = (255, 255, 255, 255)    # RGBA — white text on dark bg
PIL_TRANSPARENT         = (255, 255, 255, 0)      # Transparent PNG background

# ── High-quality rendering DPI ────────────────────────────────────────────────
# All Tamil text is rendered at 300 DPI so TSCu_SaiIndira looks print-crisp.
RENDER_DPI = 300
_DPI_SCALE  = RENDER_DPI / 120.0   # = 2.5 — scale factor vs old 120-DPI baseline

# ── Caches ────────────────────────────────────────────────────────────────────
_tamil_image_cache: Dict = {}
_cached_tamil_font_path: Optional[str] = None
_cached_tamil_bold_font_path: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# Font helpers
# ─────────────────────────────────────────────────────────────────────────────

def find_tamil_font(is_bold: bool = False) -> Optional[str]:
    """Return the first available Tamil font path; prefer TSCu_SaiIndira.ttf."""
    global _cached_tamil_font_path, _cached_tamil_bold_font_path
    if is_bold and _cached_tamil_bold_font_path:
        return _cached_tamil_bold_font_path
    if not is_bold and _cached_tamil_font_path:
        return _cached_tamil_font_path
    paths = TAMIL_BOLD_FONT_PATHS if is_bold else TAMIL_FONT_PATHS
    for p in paths:
        if os.path.exists(p):
            if is_bold:
                _cached_tamil_bold_font_path = p
            else:
                _cached_tamil_font_path = p
            return p
    print("⚠ Warning: No Tamil font found!")
    return None


def register_english_fonts():
    """Register DejaVu fonts for ReportLab (Latin glyphs)."""
    registered = {'EnglishBold': False, 'English': False}
    for key, path in [('EnglishBold', ENGLISH_BOLD_FONT), ('English', ENGLISH_REGULAR_FONT)]:
        try:
            if os.path.exists(path):
                pdfmetrics.registerFont(TTFont(key, path))
                registered[key] = True
        except Exception as e:
            print(f"Warning: Could not register {key} font: {e}")
    return registered


_english_fonts_registered = register_english_fonts()


def get_font_name(font_key: str) -> str:
    """Return registered font name or Helvetica fallback."""
    if font_key in pdfmetrics.getRegisteredFontNames():
        return font_key
    return {'EnglishBold': 'Helvetica-Bold', 'English': 'Helvetica'}.get(font_key, 'Helvetica')


# ─────────────────────────────────────────────────────────────────────────────
# Tamil-text → PNG pipeline
# ─────────────────────────────────────────────────────────────────────────────

def render_tamil_to_png(
    text: str,
    font_path: Optional[str] = None,
    font_size: int = 16,
    text_color: Tuple[int, int, int, int] = (26, 42, 58, 255),   # TEXT_NAVY default
    bg_color: Tuple[int, int, int, int] = (255, 255, 255, 0),    # transparent default
    padding: int = 6,
    is_bold: bool = False,
) -> Tuple[io.BytesIO, int, int]:
    """
    Render a Tamil Unicode string into a PNG BytesIO.
    Returns (buf, width_px, height_px).
    font_size is in *pixels* (already pre-scaled for the desired DPI).
    """
    if not PILLOW_AVAILABLE:
        img = Image.new("RGBA", (10, 10), bg_color)
        buf = io.BytesIO(); img.save(buf, "PNG"); buf.seek(0)
        return buf, 10, 10

    if not text or not text.strip():
        img = Image.new("RGBA", (1, max(font_size, 1)), bg_color)
        buf = io.BytesIO(); img.save(buf, "PNG"); buf.seek(0)
        return buf, 1, max(font_size, 1)

    if font_path is None:
        font_path = find_tamil_font(is_bold)

    if font_path is None:
        img = Image.new("RGBA", (10, 10), bg_color)
        buf = io.BytesIO(); img.save(buf, "PNG"); buf.seek(0)
        return buf, 10, 10

    # Load font; fall back gracefully
    font = None
    for try_path in [font_path,
                     str(PROJECT_ROOT / "TSCu_SaiIndira.ttf"),
                     str(Path.cwd() / "TSCu_SaiIndira.ttf")]:
        try:
            if os.path.exists(try_path):
                font = ImageFont.truetype(try_path, font_size)
                break
        except Exception:
            continue
    if font is None:
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None

    # Measure
    dummy = Image.new("RGBA", (10, 10), bg_color)
    d = ImageDraw.Draw(dummy)
    if font:
        bbox   = d.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
    else:
        text_w = int(len(text) * font_size * 0.6)
        text_h = font_size

    # Add 2px per side to accommodate stroke without clipping
    stroke_px = 1
    img_w = max(int(text_w) + 2 * padding + 2 * stroke_px, 1)
    img_h = max(int(text_h) + 2 * padding + 2 * stroke_px, 1)

    img  = Image.new("RGBA", (img_w, img_h), bg_color)
    draw = ImageDraw.Draw(img)
    if font:
        # stroke_width=1 gives Tamil glyphs the same visual weight as numbers
        draw.text((padding, padding), text, font=font, fill=text_color,
                  stroke_width=stroke_px, stroke_fill=text_color)
    else:
        draw.text((padding, padding), text, fill=text_color)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf, img_w, img_h


def tamil_image_flowable(
    text: str,
    font_size: int = 12,
    max_width: Optional[float] = None,   # in PDF points
    is_bold: bool = False,
    text_color: Tuple[int, int, int, int] = PIL_TEXT_NAVY,  # TEXT_NAVY default
) -> RLImage:
    """
    Create a ReportLab Image flowable from Tamil text, rendered at RENDER_DPI for
    print-quality crispness.  font_size is treated as a *point* size — it is scaled
    up internally to RENDER_DPI pixels, then the resulting image is scaled back down.
    """
    if not text or not text.strip():
        buf, w_px, h_px = render_tamil_to_png("", font_size=int(font_size * _DPI_SCALE),
                                               is_bold=is_bold, text_color=text_color)
        return RLImage(buf, width=w_px * 72.0 / RENDER_DPI, height=h_px * 72.0 / RENDER_DPI)

    cache_key = (text, font_size, max_width, is_bold, text_color)
    if cache_key in _tamil_image_cache:
        buf, w_pt, h_pt = _tamil_image_cache[cache_key]
        buf.seek(0)
        return RLImage(buf, width=w_pt, height=h_pt)

    # Scale font up to RENDER_DPI pixels, then convert back to points
    internal_font_size = max(int(font_size * _DPI_SCALE), 1)
    buf, w_px, h_px = render_tamil_to_png(
        text, font_size=internal_font_size, is_bold=is_bold, text_color=text_color
    )
    w_pt = w_px * 72.0 / RENDER_DPI
    h_pt = h_px * 72.0 / RENDER_DPI

    if max_width and w_pt > max_width:
        scale = max_width / w_pt
        w_pt *= scale
        h_pt *= scale

    _tamil_image_cache[cache_key] = (buf, w_pt, h_pt)
    buf.seek(0)
    return RLImage(buf, width=w_pt, height=h_pt)


# ─────────────────────────────────────────────────────────────────────────────
# Header — 3-column divine layout
# ─────────────────────────────────────────────────────────────────────────────

def draw_header() -> Table:
    """
    Returns a 3-column Table:
      Left  — Lord Muruga icon (1.4 in)
      Centre — Tamil shloka verse (4.5 in)
      Right  — ASTRO NKV brand name (1.5 in)
    """
    # ── Left column: Muruga icon ──────────────────────────────────────────────
    if os.path.exists(str(MURUGA_ICON_PATH)):
        left_cell = RLImage(str(MURUGA_ICON_PATH), width=1.0 * inch, height=1.0 * inch)
    else:
        # Graceful fallback: gold decorative placeholder paragraph
        left_cell = Paragraph(
            "✦",
            ParagraphStyle(
                'IconPlaceholder',
                fontName=get_font_name('EnglishBold'),
                fontSize=28,
                textColor=ACCENT_GOLD,
                alignment=1,   # centre
            )
        )

    # ── Centre column: shloka (two lines) ────────────────────────────────────
    verse1 = tamil_image_flowable(
        "ஜனனீ ஜன்ம ஸௌக்யானாம் வர்த்தனீ குல ஸம்பதாம்",
        font_size=15, max_width=4.3 * inch, text_color=PIL_TEXT_NAVY,
    )
    verse2 = tamil_image_flowable(
        "புத்ரீ பூர்வ புண்யானாம் விக்யேத ஜன்ம பத்ரிகா.",
        font_size=15, max_width=4.3 * inch, text_color=PIL_TEXT_NAVY,
    )
    centre_inner = Table([[verse1], [verse2]], colWidths=[4.3 * inch])
    centre_inner.setStyle(TableStyle([
        ('ALIGN',         (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',   (0, 0), (-1, -1), 0),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 0),
        ('TOPPADDING',    (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ]))

    # ── Right column: ASTRO NKV ───────────────────────────────────────────────
    name_style = ParagraphStyle(
        'AstroName',
        fontName=get_font_name('EnglishBold'),
        fontSize=14,
        textColor=TEXT_NAVY,
        alignment=2,   # right
        spaceAfter=2,
    )
    tagline_style = ParagraphStyle(
        'Tagline',
        fontName=get_font_name('English'),
        fontSize=8,
        textColor=ACCENT_GOLD,
        alignment=2,
    )
    right_inner = Table(
        [[Paragraph("ASTRO NKV", name_style)],
         [Paragraph("Jyotish Shastra", tagline_style)]],
        colWidths=[1.4 * inch],
    )
    right_inner.setStyle(TableStyle([
        ('ALIGN',         (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',   (0, 0), (-1, -1), 0),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 0),
        ('TOPPADDING',    (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))

    # ── Outer 3-column header table ───────────────────────────────────────────
    header_table = Table(
        [[left_cell, centre_inner, right_inner]],
        colWidths=[1.2 * inch, 4.6 * inch, 1.4 * inch],
    )
    header_table.setStyle(TableStyle([
        ('ALIGN',         (0, 0), (0, 0), 'LEFT'),
        ('ALIGN',         (1, 0), (1, 0), 'CENTER'),
        ('ALIGN',         (2, 0), (2, 0), 'RIGHT'),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',   (0, 0), (-1, -1), 2),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 2),
        ('TOPPADDING',    (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        # Gold bottom border beneath header
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, ACCENT_GOLD),
    ]))
    return header_table


# ─────────────────────────────────────────────────────────────────────────────
# Astrological chart renderer (PIL)
# ─────────────────────────────────────────────────────────────────────────────

def render_chart_as_pil_image(
    chart_data: Dict[int, list],
    chart_type: str,
    width_px: int = 360,
    height_px: int = 360,
    dpi_scale: float = 1.0,
) -> io.BytesIO:
    """
    Render a South Indian 4×4 grid chart as a PIL image.
    Design: ivory background, gold borders, pale-gold Lagna cell highlight.
    """
    if not PILLOW_AVAILABLE:
        img = Image.new("RGB", (width_px, height_px), PIL_BG_IVORY)
        buf = io.BytesIO(); img.save(buf, "PNG"); buf.seek(0)
        return buf

    # ── Identify Lagna house (for special highlight) ──────────────────────────
    lagna_house = None
    LAGNA_LABELS = {"Asc", "Lagna", "லக்", "லக்னம்"}
    for house_num, planets in chart_data.items():
        if any(p in LAGNA_LABELS for p in (planets or [])):
            lagna_house = house_num
            break

    # ── Canvas ────────────────────────────────────────────────────────────────
    img  = Image.new("RGB", (width_px, height_px), PIL_BG_IVORY)
    draw = ImageDraw.Draw(img)

    gold_border  = PIL_ACCENT_GOLD_BORDER
    text_color   = (26, 42, 58)              # TEXT_NAVY as RGB

    BORDER      = max(2, int(2 * dpi_scale))
    CELL_BORDER = 1                              # delicate inner grid — always 1px
    CELL_SIZE   = (width_px - BORDER * 2 - CELL_BORDER * 3) / 4
    CENTER_SIZE = CELL_SIZE * 2 + CELL_BORDER * 2

    # Font sizes scale with DPI
    base_regular = max(10, int(13 * dpi_scale))
    base_bold    = max(12, int(22 * dpi_scale))  # larger centre label

    tamil_font_path      = find_tamil_font(False)
    tamil_bold_font_path = find_tamil_font(True)
    try:
        tamil_font      = ImageFont.truetype(tamil_font_path, base_regular)      if tamil_font_path      else None
        tamil_bold_font = ImageFont.truetype(tamil_bold_font_path, base_bold) if tamil_bold_font_path else None
    except Exception:
        tamil_font = tamil_bold_font = None

    # ── Draw inner cells first, then overlay the strong outer frame ───────────
    # (outer frame drawn last so it is never clipped by cell borders)

    # Padding constants
    PAD_NUM   = int(4 * dpi_scale)    # house number: 4px from top-left corner
    PAD_LAGNA = int(5 * dpi_scale)    # lagna label: ≥5px padding from border
    NUM_COLOR = (160, 160, 160)        # subtle light-grey for house numbers

    def draw_cell(house_num: int, x: int, y: int):
        """Draw one house cell with background, border, sign number, and planet labels."""
        # Cell background: pale gold for Lagna house, ivory for all others
        cell_bg = PIL_HIGHLIGHT_PALE_GOLD if house_num == lagna_house else PIL_BG_IVORY
        draw.rectangle(
            [(x, y), (x + int(CELL_SIZE) - 1, y + int(CELL_SIZE) - 1)],
            fill=cell_bg, outline=gold_border, width=CELL_BORDER,
        )

        planets = chart_data.get(house_num, [])
        asc_label    = None
        planet_labels = []
        for label in planets:
            if label in LAGNA_LABELS:
                asc_label = label
            else:
                planet_labels.append(label)

        # House number — top-LEFT corner in subtle grey so it doesn't compete
        sign_text = str(house_num)
        num_x = int(x + PAD_NUM)
        num_y = int(y + PAD_NUM)
        draw.text((num_x, num_y), sign_text, fill=NUM_COLOR)

        # Lagna label — top-CENTER of the cell, at least PAD_LAGNA from the top border
        if asc_label:
            if tamil_font:
                bb = draw.textbbox((0, 0), asc_label, font=tamil_font)
                lw = bb[2] - bb[0]; lh = bb[3] - bb[1]
            else:
                lw = int(len(asc_label) * 9 * dpi_scale); lh = int(14 * dpi_scale)
            lx = int(x + CELL_SIZE / 2 - lw / 2)
            ly = int(y + PAD_LAGNA)
            if tamil_font:
                draw.text((lx, ly), asc_label, fill=text_color, font=tamil_font)
            else:
                draw.text((lx, ly), asc_label, fill=text_color)

        # Planet labels — mathematically centered in the exact middle of the cell
        if planet_labels:
            line_h = int(18 * dpi_scale)
            visible = []
            for pl in planet_labels[:4]:
                if not pl or not pl.strip():
                    continue
                if tamil_font:
                    bb = draw.textbbox((0, 0), pl, font=tamil_font)
                    tw = bb[2] - bb[0]
                    th = bb[3] - bb[1]
                else:
                    tw = int(len(pl) * 9 * dpi_scale)
                    th = int(14 * dpi_scale)
                visible.append((pl, tw, th))

            # Total text block height → anchor at true vertical centre
            total_text_height = len(visible) * line_h
            start_y = int(y + (CELL_SIZE - total_text_height) / 2)

            for i, (pl, tw, th) in enumerate(visible):
                tx = int(x + CELL_SIZE / 2 - tw / 2)
                ty = int(start_y + i * line_h)
                if tamil_font:
                    draw.text((tx, ty), pl, fill=text_color, font=tamil_font)
                else:
                    draw.text((tx, ty), pl, fill=text_color)

    # ── Draw 12 cells in South Indian layout ─────────────────────────────────
    B = BORDER; S = CELL_SIZE; CB = CELL_BORDER

    row1_y = int(B)
    draw_cell(12, int(B),               row1_y)
    draw_cell(1,  int(B +   (S + CB)), row1_y)
    draw_cell(2,  int(B + 2*(S + CB)), row1_y)
    draw_cell(3,  int(B + 3*(S + CB)), row1_y)

    row2_y = int(B + (S + CB))
    draw_cell(11, int(B), row2_y)
    # Centre label (chart type) — large, commanding the empty central space
    cx = int(B + (S + CB) + CENTER_SIZE / 2)
    cy = int(row2_y + CENTER_SIZE / 2)
    if tamil_bold_font:
        bb = draw.textbbox((0, 0), chart_type, font=tamil_bold_font)
        cw = bb[2] - bb[0]; ch = bb[3] - bb[1]
        draw.text((int(cx - cw / 2), int(cy - ch / 2)), chart_type,
                  fill=text_color, font=tamil_bold_font)
    elif tamil_font:
        bb = draw.textbbox((0, 0), chart_type, font=tamil_font)
        cw = bb[2] - bb[0]; ch = bb[3] - bb[1]
        draw.text((int(cx - cw / 2), int(cy - ch / 2)), chart_type,
                  fill=text_color, font=tamil_font)
    else:
        draw.text((cx - 20, cy - 8), chart_type, fill=text_color)
    draw_cell(4, int(B + 3*(S + CB)), row2_y)

    row3_y = int(B + 2*(S + CB))
    draw_cell(10, int(B), row3_y)
    draw_cell(5,  int(B + 3*(S + CB)), row3_y)

    row4_y = int(B + 3*(S + CB))
    draw_cell(9, int(B),               row4_y)
    draw_cell(8, int(B +   (S + CB)), row4_y)
    draw_cell(7, int(B + 2*(S + CB)), row4_y)
    draw_cell(6, int(B + 3*(S + CB)), row4_y)

    # Strong outer frame drawn LAST so it is never clipped by inner cells
    outer_w = max(3, int(3 * dpi_scale))
    draw.rectangle(
        [(outer_w // 2, outer_w // 2),
         (width_px - 1 - outer_w // 2, height_px - 1 - outer_w // 2)],
        outline=gold_border, width=outer_w,
    )

    buf = io.BytesIO()
    img.save(buf, format="PNG", dpi=(RENDER_DPI, RENDER_DPI))
    buf.seek(0)
    return buf


def draw_south_indian_chart_exact(
    chart_data: Dict[int, list],
    chart_type: str,
    width: float = 250,
    height: float = 250,
) -> RLImage:
    """
    Render a South Indian chart at RENDER_DPI and return a ReportLab Image flowable.
    """
    width_px  = int(width  * RENDER_DPI / 72)
    height_px = int(height * RENDER_DPI / 72)
    img_buf   = render_chart_as_pil_image(
        chart_data, chart_type, width_px, height_px, dpi_scale=_DPI_SCALE
    )
    return RLImage(img_buf, width=width, height=height)


# ─────────────────────────────────────────────────────────────────────────────
# Main PDF generator
# ─────────────────────────────────────────────────────────────────────────────

def generate_horoscope_pdf(horoscope_result, personal_details: Dict[str, Any], system: str) -> bytes:
    """
    Generate a premium single-page A4 Tamil horoscope PDF.
    Design: Cosmic Blueprint — ivory, navy, gold palette.
    """
    buf = io.BytesIO()

    # Tight margins to maximise usable space on A4
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        topMargin=0.2 * inch, bottomMargin=0.2 * inch,
        leftMargin=0.2 * inch, rightMargin=0.2 * inch,
    )

    story = []

    # ── 1. Divine Header ──────────────────────────────────────────────────────
    story.append(draw_header())
    story.append(Spacer(1, 0.02 * inch))

    # ── 2. Personal Details ───────────────────────────────────────────────────
    # Helper: right-aligned label image
    def lbl(text, size=10):
        return tamil_image_flowable(text, font_size=size, is_bold=True,
                                    text_color=PIL_TEXT_NAVY)

    # Helper: value image
    def val(text, size=10):
        return tamil_image_flowable(text, font_size=size,
                                    text_color=PIL_TEXT_NAVY)

    def eng(text, size=10):
        return Paragraph(
            text,
            ParagraphStyle('Eng', fontName=get_font_name('English'), fontSize=size,
                           textColor=TEXT_NAVY),
        )

    mother_name   = getattr(horoscope_result.birth_details, 'mother_name', None) or "N/A"
    father_name   = getattr(horoscope_result.birth_details, 'father_name', None) or "N/A"
    paksha_ta     = getattr(horoscope_result, 'paksha_tamil', None)
    paksha        = paksha_ta or getattr(horoscope_result, 'paksha', None) or "N/A"
    tithi_tamil   = getattr(horoscope_result, 'tithi_tamil', None) or "N/A"

    tamil_date_str = "N/A"
    t_month = getattr(horoscope_result, 'tamil_month', None)
    t_day   = getattr(horoscope_result, 'tamil_day', None)
    t_yname = getattr(horoscope_result, 'tamil_year_name', None)
    t_year  = getattr(horoscope_result, 'tamil_year', None)
    if t_month and t_day:
        suffix = t_yname or t_year or ""
        tamil_date_str = f"{t_month} {t_day}, {suffix}".strip(", ")

    # Left block (13 rows)
    left_labels = [
        lbl("பெயர்"),          lbl("தாய் பெயர்"),     lbl("தந்தை பெயர்"),
        lbl("ராசி"),           lbl("லக்கினம்"),        lbl("நட்சத்திரம்"),
        lbl("பட்சம்"),         lbl("திதி"),            lbl("யோகம்"),
        lbl("கரணம்"),          lbl("சூரிய உதயம்"),    lbl("சூரிய அஸ்தமனம்"),
        lbl("அயனாம்சம்"),
    ]
    left_vals = [
        val(horoscope_result.birth_details.name),
        val(mother_name), val(father_name),
        val(horoscope_result.moon_sign_tamil),
        val(horoscope_result.ascendant_tamil),
        val(horoscope_result.nakshatra_tamil),
        val(paksha), val(tithi_tamil),
        val(getattr(horoscope_result, 'yoga_tamil',  None) or "N/A"),
        val(getattr(horoscope_result, 'karana_tamil', None) or "N/A"),
        eng(getattr(horoscope_result, 'sunrise_time', None) or "06:00"),
        eng(getattr(horoscope_result, 'sunset_time',  None) or "18:00"),
        eng(getattr(horoscope_result, 'ayanamsa',     None) or "23° 51'"),
    ]

    # Right block
    right_labels = [
        lbl("பிறந்த தேதி", 10), lbl("பிறந்த நேரம்", 10),
        lbl("தமிழ் தேதி",  10), lbl("பிறந்த ஊர்",  10),
        lbl("அட்சம்",       10), lbl("தீர்க்கம்",   10),
    ] + [Paragraph("", ParagraphStyle('E')) for _ in range(7)]

    right_vals = [
        eng(horoscope_result.birth_details.date_of_birth.strftime("%d/%m/%Y")),
        eng(horoscope_result.birth_details.time_of_birth.strftime("%H:%M:%S")),
        val(tamil_date_str, 10),
        val(horoscope_result.birth_details.place_of_birth, 10),
        eng(f"{horoscope_result.birth_details.latitude}°"),
        eng(f"{horoscope_result.birth_details.longitude}°"),
    ] + [Paragraph("", ParagraphStyle('E')) for _ in range(7)]

    personal_data = [
        [left_labels[i], left_vals[i], right_labels[i], right_vals[i]]
        for i in range(13)
    ]

    personal_table = Table(
        personal_data,
        colWidths=[1.3 * inch, 2.3 * inch, 1.3 * inch, 2.3 * inch],
    )
    personal_table.setStyle(TableStyle([
        # Alignment
        ('ALIGN',         (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN',         (1, 0), (1, -1), 'LEFT'),
        ('ALIGN',         (2, 0), (2, -1), 'RIGHT'),
        ('ALIGN',         (3, 0), (3, -1), 'LEFT'),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        # No vertical dividers — only faint horizontal gold lines
        ('LINEBELOW',     (0, 0), (-1, -1), 0.25, ACCENT_GOLD),
        # Comfortable padding (gutter between label and value)
        ('LEFTPADDING',   (0, 0), (-1, -1), 4),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 4),
        ('TOPPADDING',    (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ]))
    story.append(personal_table)
    story.append(Spacer(1, 0.01 * inch))

    # ── 3. Planetary Positions Matrix ─────────────────────────────────────────
    # Column widths defined once — used for both the Table and max_width capping
    # so PIL images can NEVER be wider than their cell (prevents left-clipping).
    # Cols sum to ~7.0in: wide enough for நட்சத்திரம் (longest header)
    PCOL = [1.0 * inch, 1.0 * inch, 1.6 * inch,
            0.6 * inch, 1.35 * inch, 1.2 * inch]
    PAD_CELL = 8  # left+right padding in points (4 each side)

    def hdr(text, col_idx):
        """Header cell: white text on TEXT_NAVY background, width-capped."""
        return tamil_image_flowable(
            text, font_size=10, is_bold=True,
            text_color=PIL_WHITE_TEXT,
            max_width=PCOL[col_idx] - PAD_CELL,
        )

    def tval(text, col_idx, size=10):
        """Tamil value cell, width-capped to its column."""
        return tamil_image_flowable(
            text, font_size=size,
            text_color=PIL_TEXT_NAVY,
            max_width=PCOL[col_idx] - PAD_CELL,
        )

    planet_data = [[
        hdr("கிரகம்", 0), hdr("பாகை", 1), hdr("நட்சத்திரம்", 2),
        hdr("பாதம்", 3),  hdr("ராசி பாகை", 4), hdr("ராசி", 5),
    ]]

    for planet in horoscope_result.planetary_positions:
        full_lon = getattr(planet, 'longitude_dms',         None) or "N/A"
        rasi_deg = getattr(planet, 'longitude_in_sign_dms', None) or "N/A"
        pada     = str(getattr(planet, 'nakshatra_pada', None) or "N/A")

        if planet.planet == "Sun":
            print(f"DEBUG — Sun: {full_lon} | rasi: {rasi_deg}")

        planet_data.append([
            tval(planet.planet_tamil, 0),
            eng(full_lon, 9),
            tval(planet.nakshatra_name_tamil or planet.nakshatra_name, 2),
            eng(pada, 9),
            eng(rasi_deg, 9),
            tval(planet.sign_name_tamil or planet.sign_name, 5),
        ])

    planet_table = Table(
        planet_data,
        colWidths=PCOL,
    )
    planet_table.setStyle(TableStyle([
        # ── Header row ──
        ('BACKGROUND',    (0, 0), (-1, 0),  TEXT_NAVY),
        # Thick ACCENT_GOLD line separating header from data
        ('LINEBELOW',     (0, 0), (-1, 0),  2,   ACCENT_GOLD),
        # Top border of the entire table
        ('LINEABOVE',     (0, 0), (-1, 0),  1.0, TEXT_NAVY),

        # ── Data rows — clean white background ──
        ('BACKGROUND',    (0, 1), (-1, -1), colors.white),
        # Very faint light-grey horizontal dividers between rows (no vertical lines)
        ('LINEBELOW',     (0, 1), (-1, -1), 0.5, colors.HexColor('#E5E5E5')),
        # Bottom anchor border
        ('LINEBELOW',     (0, -1), (-1, -1), 1.0, TEXT_NAVY),

        # ── Alignment ──
        # First column (planet name) left-aligned
        ('ALIGN',         (0, 0), (0, -1),  'LEFT'),
        # All data columns centred for clean vertical number columns
        ('ALIGN',         (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),

        # ── Breathing room ──
        ('LEFTPADDING',   (0, 0), (-1, -1), 4),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 4),
        ('TOPPADDING',    (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(planet_table)
    story.append(Spacer(1, 0.01 * inch))

    # ── 4. Astrological Charts ────────────────────────────────────────────────
    rasi_houses    = {}
    navamsa_houses = {}

    if hasattr(horoscope_result, 'rasi_chart') and horoscope_result.rasi_chart:
        for k, v in horoscope_result.rasi_chart.houses_tamil.items():
            hk = int(k) if isinstance(k, str) else k
            rasi_houses[hk] = v if isinstance(v, list) else ([v] if v else [])

    if hasattr(horoscope_result, 'navamsa_chart') and horoscope_result.navamsa_chart:
        for k, v in horoscope_result.navamsa_chart.houses_tamil.items():
            hk = int(k) if isinstance(k, str) else k
            navamsa_houses[hk] = v if isinstance(v, list) else ([v] if v else [])

    # Debug logs
    print("\n" + "="*60)
    print("DEBUG — NAVAMSA CHART DATA (houses_tamil):")
    for hn in sorted(navamsa_houses): print(f"  House {hn:2d}: {navamsa_houses[hn]}")
    print("DEBUG — RASI CHART DATA (houses_tamil):")
    for hn in sorted(rasi_houses):    print(f"  House {hn:2d}: {rasi_houses[hn]}")
    print("="*60 + "\n")

    CHART_SIZE = 3.0 * inch   # large enough to command the space, fits on one page

    rasi_img    = draw_south_indian_chart_exact(rasi_houses,    "ராசி",     width=CHART_SIZE, height=CHART_SIZE)
    navamsa_img = draw_south_indian_chart_exact(navamsa_houses, "நவாம்சம்", width=CHART_SIZE, height=CHART_SIZE)

    chart_table = Table([[rasi_img, navamsa_img]],
                        colWidths=[CHART_SIZE, CHART_SIZE])
    chart_table.setStyle(TableStyle([
        ('ALIGN',         (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',   (0, 0), (-1, -1), 2),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 2),
        ('TOPPADDING',    (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(chart_table)
    story.append(Spacer(1, 0.02 * inch))

    # ── 5. The Path Ahead — Dasa / Bhukti Footer ─────────────────────────────
    if horoscope_result.current_dasa:
        dasa = horoscope_result.current_dasa

        # Render dasa text with white color (transparent bg) so it sits cleanly
        # on the TEXT_NAVY table-cell background drawn by ReportLab.
        def dasa_img(text, size=14):
            return tamil_image_flowable(text, font_size=size, max_width=6.8 * inch,
                                        text_color=PIL_WHITE_TEXT)

        dasa_rows = []

        # Title row
        dasa_rows.append([dasa_img("தசா காலங்கள்", size=16)])

        # Retrograde
        retro = horoscope_result.retrograde_planets_tamil or []
        if retro:
            dasa_rows.append([dasa_img(f"கிரக வக்ர நிலை : {retro[0]}")])

        # Balance
        if hasattr(dasa, 'balance_years') and dasa.balance_years is not None:
            fp = getattr(dasa, 'first_dasha_planet_tamil', None) or \
                 getattr(dasa, 'planet_tamil', '')
            bm = getattr(dasa, 'balance_months', 0) or 0
            bd = getattr(dasa, 'balance_days',   0) or 0
            dasa_rows.append([dasa_img(
                f"திசை இருப்பு : {fp} திசை {dasa.balance_years} வருஷம், "
                f"{bm} மாதம், {bd} நாள்"
            )])

        # Current Dasa-Bhukti
        if getattr(dasa, 'current_bhukti_planet_tamil', None):
            dasa_end = dasa.end_date.strftime('%d/%m/%Y') \
                if hasattr(dasa.end_date, 'strftime') else str(dasa.end_date)

            bhukti_end = ""
            raw_be = getattr(dasa, 'current_bhukti_end_date', None)
            if raw_be:
                if hasattr(raw_be, 'strftime'):
                    bhukti_end = raw_be.strftime('%d/%m/%Y')
                else:
                    raw_str = str(raw_be).split('T')[0]
                    for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
                        try:
                            bhukti_end = datetime.strptime(raw_str, fmt).strftime('%d/%m/%Y')
                            break
                        except ValueError:
                            continue
                    if not bhukti_end:
                        bhukti_end = str(raw_be)

            pt = getattr(dasa, 'planet_tamil', '')
            bt = dasa.current_bhukti_planet_tamil
            dasa_rows.append([dasa_img(
                f"நடப்பு திசை-புக்தி : {pt} திசை {dasa_end} வரை, "
                f"{bt} புக்தி {bhukti_end} வரை."
            )])

        # Bhava Maruthal
        bhava = getattr(horoscope_result, 'bhava_maruthal_tamil', None) or {}
        if bhava and isinstance(bhava, dict):
            parts = [f"{p}-{h}" for p, h in bhava.items()]
            if parts:
                dasa_rows.append([dasa_img(f"பாவக மாறுதல் : {', '.join(parts)}")])

        if dasa_rows:
            # Solid TEXT_NAVY background throughout — all rows use white text
            # (already rendered with PIL_WHITE_TEXT above)
            dasa_table = Table(dasa_rows, colWidths=[7.0 * inch])
            dasa_style = [
                ('BACKGROUND',    (0, 0), (-1, -1), TEXT_NAVY),     # solid navy entire block
                ('ALIGN',         (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING',   (0, 0), (-1, -1), 8),
                ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
                ('TOPPADDING',    (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                # ACCENT_GOLD 1.5pt outer box border
                ('BOX',        (0, 0), (-1, -1), 1.5, ACCENT_GOLD),
            ]
            dasa_table.setStyle(TableStyle(dasa_style))
            story.append(KeepTogether(dasa_table))

    # ── Build PDF ─────────────────────────────────────────────────────────────
    doc.build(story)
    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes
