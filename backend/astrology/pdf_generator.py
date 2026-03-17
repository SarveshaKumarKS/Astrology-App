"""
PDF Generator for Tamil Astrology Horoscopes
Refactored to render Tamil text as PNG images using Pillow for proper Unicode shaping.
Charts match frontend SouthIndianChart.tsx implementation exactly.
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
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.graphics.shapes import Drawing, Rect, Line, String
from reportlab.graphics import renderPDF

# Pillow imports for Tamil text rendering
try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    print("⚠ Warning: Pillow not available. Tamil text will not render correctly.")

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Tamil font paths - prioritize TSCu_SaiIndira.ttf
TSCU_FONT_PATH = PROJECT_ROOT / "TSCu_SaiIndira.ttf"

TAMIL_FONT_PATHS = [
    str(TSCU_FONT_PATH),  # Primary font
    str(PROJECT_ROOT / "TSCu_SaiIndira.ttf"),
    str(Path.cwd() / "TSCu_SaiIndira.ttf"),
    "/usr/share/fonts/truetype/noto/NotoSerifTamil-Regular.ttf",
    "/System/Library/Fonts/Supplemental/NotoSansTamil-Regular.ttf",
]

TAMIL_BOLD_FONT_PATHS = [
    str(TSCU_FONT_PATH),  # Primary font (use same for bold)
    str(PROJECT_ROOT / "TSCu_SaiIndira.ttf"),
    str(Path.cwd() / "TSCu_SaiIndira.ttf"),
    "/usr/share/fonts/truetype/noto/NotoSerifTamil-Bold.ttf",
    "/System/Library/Fonts/Supplemental/NotoSansTamil-Bold.ttf",
]

# English fonts
ENGLISH_BOLD_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ENGLISH_REGULAR_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# ── ICS-style color palette (matches 1988.pdf reference) ──────────────────────
GREEN       = colors.HexColor('#008000')
YELLOW      = colors.HexColor('#FFFF00')
LIGHT_GREEN = colors.HexColor('#E8F5E9')

# Cache for rendered Tamil text images
# Note: Cache is cleared on each PDF generation to ensure fresh rendering
_tamil_image_cache: Dict[Tuple[str, int, Optional[float]], Tuple[io.BytesIO, float, float]] = {}


# Cache for font path to avoid repeated lookups
_cached_tamil_font_path: Optional[str] = None
_cached_tamil_bold_font_path: Optional[str] = None

def find_tamil_font(is_bold: bool = False) -> Optional[str]:
    """Find available Tamil font path - prioritize TSCu_SaiIndira.ttf"""
    global _cached_tamil_font_path, _cached_tamil_bold_font_path
    
    # Check cache first
    if is_bold and _cached_tamil_bold_font_path:
        return _cached_tamil_bold_font_path
    if not is_bold and _cached_tamil_font_path:
        return _cached_tamil_font_path
    
    paths = TAMIL_BOLD_FONT_PATHS if is_bold else TAMIL_FONT_PATHS
    for path in paths:
        if os.path.exists(path):
            if is_bold:
                _cached_tamil_bold_font_path = path
            else:
                _cached_tamil_font_path = path
            if _cached_tamil_font_path is None or _cached_tamil_bold_font_path is None:
                print(f"✓ Using Tamil font: {path}")
            return path
    
    if not _cached_tamil_font_path and not _cached_tamil_bold_font_path:
        print("⚠ Warning: No Tamil font found!")
    return None


def render_tamil_to_png(
    text: str,
    font_path: Optional[str] = None,
    font_size: int = 16,
    text_color: Tuple[int, int, int, int] = (0, 0, 0, 255),
    bg_color: Tuple[int, int, int, int] = (255, 255, 255, 0),  # transparent
    padding: int = 6,  # Increased padding for better quality
    is_bold: bool = False,
) -> Tuple[io.BytesIO, int, int]:
    """
    Render a Tamil Unicode string into a PNG (in-memory BytesIO).
    Returns (buf, width_px, height_px).
    """
    if not PILLOW_AVAILABLE:
        # Fallback: return empty image
        img = Image.new("RGBA", (10, 10), bg_color)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf, 10, 10
    
    if not text or not text.strip():
        # Empty text - return minimal image
        img = Image.new("RGBA", (1, font_size), bg_color)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf, 1, font_size
    
    # Find font
    if font_path is None:
        font_path = find_tamil_font(is_bold)
    
    if font_path is None:
        # No font found - return empty image
        img = Image.new("RGBA", (10, 10), bg_color)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf, 10, 10
    
    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception as e:
        # Try alternative paths
        alt_paths = [
            str(PROJECT_ROOT / "TSCu_SaiIndira.ttf"),
            str(Path.cwd() / "TSCu_SaiIndira.ttf"),
            "TSCu_SaiIndira.ttf"
        ]
        font = None
        for alt_path in alt_paths:
            try:
                if os.path.exists(alt_path):
                    font = ImageFont.truetype(alt_path, font_size)
                    break
            except:
                continue
        
        if font is None:
            # Fallback to default font
            try:
                font = ImageFont.load_default()
            except:
                font = None
    
    # Measure text
    dummy_img = Image.new("RGBA", (10, 10), bg_color)
    draw = ImageDraw.Draw(dummy_img)
    
    if font:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
    else:
        # Fallback measurement
        text_w = len(text) * font_size * 0.6
        text_h = font_size
    
    img_w = max(int(text_w) + 2 * padding, 1)
    img_h = max(int(text_h) + 2 * padding, 1)
    
    # Create image and draw text
    img = Image.new("RGBA", (img_w, img_h), bg_color)
    draw = ImageDraw.Draw(img)
    
    if font:
        draw.text((padding, padding), text, font=font, fill=text_color)
    else:
        # Fallback: draw without font
        draw.text((padding, padding), text, fill=text_color)
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    
    return buf, img_w, img_h


def tamil_image_flowable(
    text: str,
    font_size: int = 12,
    max_width: Optional[float] = None,  # in points
    is_bold: bool = False,
    text_color: Tuple[int, int, int, int] = (0, 128, 0, 255),  # green by default (matches 1988.pdf)
) -> RLImage:
    """
    Create a ReportLab Image flowable from Tamil text.
    Optionally scale image to max_width (in points).
    Uses caching to avoid re-rendering identical strings.
    """
    if not text or not text.strip():
        # Return minimal empty image
        buf, w_px, h_px = render_tamil_to_png("", font_size=font_size, is_bold=is_bold, text_color=text_color)
        w_pt = w_px * 72.0 / 96.0
        h_pt = h_px * 72.0 / 96.0
        return RLImage(buf, width=w_pt, height=h_pt)

    # Check cache
    cache_key = (text, font_size, max_width, is_bold, text_color)
    if cache_key in _tamil_image_cache:
        buf, w_pt, h_pt = _tamil_image_cache[cache_key]
        buf.seek(0)  # Reset buffer position
        return RLImage(buf, width=w_pt, height=h_pt)

    # Render text to PNG
    buf, w_px, h_px = render_tamil_to_png(text, font_size=font_size, is_bold=is_bold, text_color=text_color)
    
    # Convert pixels to points - use higher DPI for better quality (120 DPI for sharper rendering)
    w_pt = w_px * 72.0 / 120.0
    h_pt = h_px * 72.0 / 120.0
    
    # Scale if max_width specified
    if max_width and w_pt > max_width:
        scale = max_width / w_pt
        w_pt *= scale
        h_pt *= scale
    
    # Cache result
    _tamil_image_cache[cache_key] = (buf, w_pt, h_pt)
    buf.seek(0)  # Reset buffer position
    
    return RLImage(buf, width=w_pt, height=h_pt)


# Register English fonts for ReportLab
def register_english_fonts():
    """Register English fonts for PDF generation"""
    fonts_registered = {
        'EnglishBold': False,
        'English': False
    }
    
    try:
        if os.path.exists(ENGLISH_BOLD_FONT):
            pdfmetrics.registerFont(TTFont("EnglishBold", ENGLISH_BOLD_FONT))
            fonts_registered['EnglishBold'] = True
    except Exception as e:
        print(f"Warning: Could not register EnglishBold font: {e}")
    
    try:
        if os.path.exists(ENGLISH_REGULAR_FONT):
            pdfmetrics.registerFont(TTFont("English", ENGLISH_REGULAR_FONT))
            fonts_registered['English'] = True
    except Exception as e:
        print(f"Warning: Could not register English font: {e}")
    
    return fonts_registered


# Register fonts at module load
_english_fonts_registered = register_english_fonts()


def get_font_name(font_key: str) -> str:
    """Get font name, fallback to Helvetica if not available"""
    registered = pdfmetrics.getRegisteredFontNames()
    if font_key in registered:
        return font_key
    # Fallback mapping
    fallbacks = {
        'EnglishBold': 'Helvetica-Bold',
        'English': 'Helvetica'
    }
    return fallbacks.get(font_key, 'Helvetica')


def draw_header():
    """Draw the header with ASTRO NKV and Sanskrit verse (Tamil verses as images)"""
    header_drawing = Drawing(540, 50)  # Reduced height
    
    # Title "ASTRO NKV" in large bold letters (English - keep as text)
    header_drawing.add(String(270, 35, "ASTRO NKV",
                              fontName=get_font_name('EnglishBold'), fontSize=16,
                              fillColor=GREEN,
                              textAnchor='middle'))

    # Decorative line - green
    header_drawing.add(Line(50, 8, 490, 8,
                           strokeColor=GREEN,
                           strokeWidth=1))
    
    return header_drawing




def render_chart_as_pil_image(
    chart_data: Dict[int, list],
    chart_type: str,
    width_px: int = 360,
    height_px: int = 360
) -> io.BytesIO:
    """
    Render the entire South Indian chart as a PIL image with all Tamil text properly rendered.
    Returns PNG bytes.
    """
    if not PILLOW_AVAILABLE:
        # Fallback: return empty image
        img = Image.new("RGB", (width_px, height_px), (255, 255, 255))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf
    
    # Create image with yellow background
    img = Image.new("RGB", (width_px, height_px), (255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Colors — ICS style: green borders, yellow cell background
    border_color = (0, 128, 0)    # #008000 green
    bg_color = (255, 255, 0)      # #FFFF00 yellow
    text_color = (51, 51, 51)     # #333333 dark for readability
    
    # Calculate dimensions (matching frontend)
    BORDER = 2
    CELL_BORDER = 1
    CELL_SIZE = (width_px - BORDER * 2 - CELL_BORDER * 3) / 4
    CENTER_SIZE = CELL_SIZE * 2 + CELL_BORDER * 2
    
    # Load fonts - larger for better quality
    tamil_font_path = find_tamil_font(False)
    tamil_bold_font_path = find_tamil_font(True)
    try:
        tamil_font = ImageFont.truetype(tamil_font_path, 14) if tamil_font_path else None  # Increased from 12
        tamil_bold_font = ImageFont.truetype(tamil_bold_font_path, 18) if tamil_bold_font_path else None  # Increased from 16
    except:
        tamil_font = None
        tamil_bold_font = None
    
    # Draw outer border
    draw.rectangle([(0, 0), (width_px - 1, height_px - 1)], outline=border_color, width=BORDER)
    
    # Helper to draw a cell
    def draw_cell(house_num: int, x: int, y: int):
        """Draw a single cell"""
        # Draw cell with yellow fill and green border
        draw.rectangle([(x, y), (x + CELL_SIZE - 1, y + CELL_SIZE - 1)],
                      fill=bg_color, outline=border_color, width=CELL_BORDER)
        
        # Get planets for this house
        planets = chart_data.get(house_num, [])
        
        # Find Lagna/Ascendant
        asc_label = None
        planet_labels = []
        for label in planets:
            if label in ["Asc", "Lagna", "லக்", "லக்னம்"]:
                asc_label = label
            else:
                planet_labels.append(label)
        
        # Draw sign number in top-right
        sign_text = str(house_num)
        try:
            # Use default font for numbers
            bbox = draw.textbbox((0, 0), sign_text)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
        except:
            text_w, text_h = 20, 10
        sign_x = int(x + CELL_SIZE - 6 - text_w)
        sign_y = int(y + 4)
        draw.text((sign_x, sign_y), sign_text, fill=text_color, font=None)
        
        # Draw planet labels (stacked vertically, centered) - matching frontend alignment
        if planet_labels:
            line_height = 18  # Increased from 16 for better spacing
            total_height = len(planet_labels) * line_height
            # Center vertically in cell, but leave space for Lagna at bottom
            available_height = CELL_SIZE - 20  # Reserve 20px for Lagna
            start_y = int(y + (CELL_SIZE - available_height) / 2 + line_height / 2)
            
            for i, planet_label in enumerate(planet_labels[:4]):
                if planet_label and planet_label.strip():
                    if tamil_font:
                        bbox = draw.textbbox((0, 0), planet_label, font=tamil_font)
                        text_w = bbox[2] - bbox[0]
                        text_h = bbox[3] - bbox[1]
                    else:
                        text_w = len(planet_label) * 10
                        text_h = 14
                    # Center horizontally
                    text_x = int(x + CELL_SIZE / 2 - text_w / 2)
                    # Align baseline properly
                    text_y = int(start_y + i * line_height - text_h if tamil_font else start_y + i * line_height)
                    if tamil_font:
                        draw.text((text_x, text_y), planet_label, fill=text_color, font=tamil_font)
                    else:
                        draw.text((text_x, text_y), planet_label, fill=text_color)
        
        # Draw Lagna label in bottom-right corner - ensure no overlap
        if asc_label:
            if tamil_font:
                bbox = draw.textbbox((0, 0), asc_label, font=tamil_font)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
            else:
                text_w = len(asc_label) * 10
                text_h = 14
            # Position in bottom-right corner with padding
            lagna_x = int(x + CELL_SIZE - 8 - text_w)
            lagna_y = int(y + CELL_SIZE - 8 - text_h)  # Bottom with padding
            if tamil_font:
                draw.text((lagna_x, lagna_y), asc_label, fill=text_color, font=tamil_font)
            else:
                draw.text((lagna_x, lagna_y), asc_label, fill=text_color)
    
    # Draw cells row by row
    # Row 1: [12, 1, 2, 3]
    row1_y = int(BORDER)
    draw_cell(12, int(BORDER), row1_y)
    draw_cell(1, int(BORDER + CELL_SIZE + CELL_BORDER), row1_y)
    draw_cell(2, int(BORDER + 2 * (CELL_SIZE + CELL_BORDER)), row1_y)
    draw_cell(3, int(BORDER + 3 * (CELL_SIZE + CELL_BORDER)), row1_y)
    
    # Row 2: [11, center (2x2), 4]
    row2_y = int(BORDER + CELL_SIZE + CELL_BORDER)
    draw_cell(11, int(BORDER), row2_y)
    # Center: draw chart type
    center_x = int(BORDER + CELL_SIZE + CELL_BORDER + CENTER_SIZE / 2)
    center_y = int(row2_y + CENTER_SIZE / 2)
    if tamil_bold_font:
        bbox = draw.textbbox((0, 0), chart_type, font=tamil_bold_font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        text_x = center_x - text_w / 2
        text_y = center_y - text_h / 2
        draw.text((int(text_x), int(text_y)), chart_type, fill=text_color, font=tamil_bold_font)
    else:
        draw.text((center_x - 20, center_y - 8), chart_type, fill=text_color)
    draw_cell(4, int(BORDER + 3 * (CELL_SIZE + CELL_BORDER)), row2_y)
    
    # Row 3: [10, spacer (empty), 5]
    row3_y = int(BORDER + 2 * (CELL_SIZE + CELL_BORDER))
    draw_cell(10, int(BORDER), row3_y)
    draw_cell(5, int(BORDER + 3 * (CELL_SIZE + CELL_BORDER)), row3_y)
    
    # Row 4: [9, 8, 7, 6]
    row4_y = int(BORDER + 3 * (CELL_SIZE + CELL_BORDER))
    draw_cell(9, int(BORDER), row4_y)
    draw_cell(8, int(BORDER + CELL_SIZE + CELL_BORDER), row4_y)
    draw_cell(7, int(BORDER + 2 * (CELL_SIZE + CELL_BORDER)), row4_y)
    draw_cell(6, int(BORDER + 3 * (CELL_SIZE + CELL_BORDER)), row4_y)
    
    # Convert to bytes
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def draw_south_indian_chart_exact(
    chart_data: Dict[int, list],
    chart_type: str,
    width: float = 250,
    height: float = 250
):
    """
    Draw South Indian style chart matching frontend SouthIndianChart.tsx exactly.
    Renders entire chart as PIL image for proper Tamil text rendering.
    Returns a ReportLab Image flowable.
    """
    # Convert points to pixels - use higher DPI (120) for better print quality
    width_px = int(width * 120 / 72)
    height_px = int(height * 120 / 72)
    
    # Render chart as PIL image
    img_buf = render_chart_as_pil_image(chart_data, chart_type, width_px, height_px)
    
    # Return as ReportLab Image flowable
    return RLImage(img_buf, width=width, height=height)


def generate_horoscope_pdf(horoscope_result, personal_details: Dict[str, Any], system: str) -> bytes:
    """
    Generate comprehensive horoscope PDF with Tamil text rendered as images.
    Charts match frontend SouthIndianChart.tsx implementation exactly.
    """
    buf = io.BytesIO()
    
    # Minimal margins to fit on one page
    doc = SimpleDocTemplate(buf, pagesize=A4, 
                           topMargin=0.2*inch, bottomMargin=0.2*inch,
                           leftMargin=0.3*inch, rightMargin=0.3*inch)
    
    story = []
    
    # Add header
    story.append(draw_header())
    story.append(Spacer(1, 0.02*inch))  # Minimal spacing
    
    # Add Tamil verse lines as images (centered) - render large and resize for quality
    # Match exact text from ICS PDF
    verse_line1_img = tamil_image_flowable("ஜனனீ ஜன்ம ஸௌக்யானாம் வர்த்தனீ குல ஸம்பதாம்", 
                                          font_size=18, max_width=5.0*inch)  # Large font, resize to fit
    verse_line2_img = tamil_image_flowable("புத்ரீ பூர்வ புண்யானாம் விக்யேத ஜன்ம பத்ரிகா.", 
                                          font_size=18, max_width=5.0*inch)  # Large font, resize to fit
    
    verse_table = Table([[verse_line1_img], [verse_line2_img]], colWidths=[5.0*inch])
    verse_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.5),
    ]))
    story.append(verse_table)
    story.append(Spacer(1, 0.02*inch))  # Minimal spacing
    
    # === PERSONAL DETAILS SECTION ===
    # Tamil labels as images - increased font size to match charts (12pt)
    left_labels = [
        tamil_image_flowable("பெயர்", font_size=12, is_bold=True),
        tamil_image_flowable("தாய் பெயர்", font_size=12, is_bold=True),
        tamil_image_flowable("தந்தை பெயர்", font_size=12, is_bold=True),
        tamil_image_flowable("ராசி", font_size=12, is_bold=True),
        tamil_image_flowable("லக்கினம்", font_size=12, is_bold=True),
        tamil_image_flowable("நட்சத்திரம்", font_size=12, is_bold=True),
        tamil_image_flowable("பட்சம்", font_size=12, is_bold=True),
        tamil_image_flowable("திதி", font_size=12, is_bold=True),
        tamil_image_flowable("யோகம்", font_size=12, is_bold=True),
        tamil_image_flowable("கரணம்", font_size=12, is_bold=True),
        tamil_image_flowable("சூரிய உதயம்", font_size=12, is_bold=True),
        tamil_image_flowable("சூரிய அஸ்தமனம்", font_size=12, is_bold=True),
        tamil_image_flowable("அயனாம்சம்", font_size=12, is_bold=True),
    ]
    
    right_labels = [
        tamil_image_flowable("பிறந்த தேதி", font_size=10, is_bold=True),
        tamil_image_flowable("பிறந்த நேரம்", font_size=10, is_bold=True),
        tamil_image_flowable("தமிழ் தேதி", font_size=10, is_bold=True),
        tamil_image_flowable("பிறந்த ஊர்", font_size=10, is_bold=True),
        tamil_image_flowable("அட்சம்", font_size=10, is_bold=True),
        tamil_image_flowable("தீர்க்கம்", font_size=10, is_bold=True),
        Paragraph("", ParagraphStyle('Empty')),
        Paragraph("", ParagraphStyle('Empty')),
        Paragraph("", ParagraphStyle('Empty')),
        Paragraph("", ParagraphStyle('Empty')),
        Paragraph("", ParagraphStyle('Empty')),
        Paragraph("", ParagraphStyle('Empty')),
        Paragraph("", ParagraphStyle('Empty')),
    ]
    
    # Build values
    mother_name = getattr(horoscope_result.birth_details, 'mother_name', None) or "N/A"
    father_name = getattr(horoscope_result.birth_details, 'father_name', None) or "N/A"
    paksha_ta = getattr(horoscope_result, 'paksha_tamil', None)
    paksha = paksha_ta or getattr(horoscope_result, 'paksha', None) or "N/A"
    tithi_tamil = getattr(horoscope_result, 'tithi_tamil', None) or "N/A"
    
    # Build Tamil date
    tamil_date_str = "N/A"
    tamil_month = getattr(horoscope_result, 'tamil_month', None)
    tamil_day = getattr(horoscope_result, 'tamil_day', None)
    tamil_year = getattr(horoscope_result, 'tamil_year', None)
    tamil_year_name = getattr(horoscope_result, 'tamil_year_name', None)
    if tamil_month and tamil_day:
        if tamil_year_name:
            tamil_date_str = f"{tamil_month} {tamil_day}, {tamil_year_name}"
        elif tamil_year:
            tamil_date_str = f"{tamil_month} {tamil_day}, {tamil_year}"
        else:
            tamil_date_str = f"{tamil_month} {tamil_day}"
    
    left_vals = [
        tamil_image_flowable(horoscope_result.birth_details.name, font_size=10),
        tamil_image_flowable(mother_name, font_size=10),
        tamil_image_flowable(father_name, font_size=10),
        tamil_image_flowable(horoscope_result.moon_sign_tamil, font_size=10),
        tamil_image_flowable(horoscope_result.ascendant_tamil, font_size=10),
        tamil_image_flowable(horoscope_result.nakshatra_tamil, font_size=10),
        tamil_image_flowable(paksha, font_size=10),
        tamil_image_flowable(tithi_tamil, font_size=10),
        tamil_image_flowable(getattr(horoscope_result, 'yoga_tamil', None) or "N/A", font_size=10),
        tamil_image_flowable(getattr(horoscope_result, 'karana_tamil', None) or "N/A", font_size=10),
        Paragraph(getattr(horoscope_result, 'sunrise_time', None) or "06:00", 
                 ParagraphStyle('Time', fontName=get_font_name('English'), fontSize=10)),
        Paragraph(getattr(horoscope_result, 'sunset_time', None) or "18:00",
                 ParagraphStyle('Time', fontName=get_font_name('English'), fontSize=10)),
        Paragraph(getattr(horoscope_result, 'ayanamsa', None) or "23° 51'",
                 ParagraphStyle('Time', fontName=get_font_name('English'), fontSize=10)),
    ]
    
    right_vals = [
        Paragraph(horoscope_result.birth_details.date_of_birth.strftime("%d/%m/%Y"),
                 ParagraphStyle('Date', fontName=get_font_name('English'), fontSize=10)),
        Paragraph(horoscope_result.birth_details.time_of_birth.strftime("%H:%M:%S"),
                 ParagraphStyle('Time', fontName=get_font_name('English'), fontSize=10)),
        tamil_image_flowable(tamil_date_str, font_size=10),
        tamil_image_flowable(horoscope_result.birth_details.place_of_birth, font_size=10),
        Paragraph(f"{horoscope_result.birth_details.latitude}°",
                 ParagraphStyle('Coord', fontName=get_font_name('English'), fontSize=10)),
        Paragraph(f"{horoscope_result.birth_details.longitude}°",
                 ParagraphStyle('Coord', fontName=get_font_name('English'), fontSize=10)),
        Paragraph("", ParagraphStyle('Empty')),
        Paragraph("", ParagraphStyle('Empty')),
        Paragraph("", ParagraphStyle('Empty')),
        Paragraph("", ParagraphStyle('Empty')),
        Paragraph("", ParagraphStyle('Empty')),
        Paragraph("", ParagraphStyle('Empty')),
        Paragraph("", ParagraphStyle('Empty')),
    ]
    
    # Create two-column table
    personal_data = []
    for i in range(max(len(left_labels), len(right_labels))):
        left_label = left_labels[i] if i < len(left_labels) else Paragraph("", ParagraphStyle('Empty'))
        left_val = left_vals[i] if i < len(left_vals) else Paragraph("", ParagraphStyle('Empty'))
        right_label = right_labels[i] if i < len(right_labels) else Paragraph("", ParagraphStyle('Empty'))
        right_val = right_vals[i] if i < len(right_vals) else Paragraph("", ParagraphStyle('Empty'))
        
        personal_data.append([left_label, left_val, right_label, right_val])
    
    # Compact column widths to fit on one page
    personal_table = Table(personal_data, colWidths=[1.0*inch, 1.4*inch, 1.0*inch, 1.4*inch])
    personal_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('ALIGN', (3, 0), (3, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, GREEN),  # green grid
        # No gray background — white cells match 1988.pdf
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ]))
    
    story.append(personal_table)
    story.append(Spacer(1, 0.015*inch))  # Minimal spacing
    
    # === PLANETARY POSITIONS TABLE ===
    # Headers as Tamil images - match UI exactly (no nakshatra lord column)
    planet_data = [[
        tamil_image_flowable("கிரகம்", font_size=10, is_bold=True),
        tamil_image_flowable("பாகை", font_size=10, is_bold=True),
        tamil_image_flowable("நட்சத்திரம்", font_size=10, is_bold=True),
        tamil_image_flowable("பாதம்", font_size=10, is_bold=True),
        tamil_image_flowable("ராசி பாகை", font_size=10, is_bold=True),
        tamil_image_flowable("ராசி", font_size=10, is_bold=True),
    ]]
    
    for planet in horoscope_result.planetary_positions:
        # Use exact same fields as UI displays - ensure we get the data directly from the object
        # UI shows: planet.longitude_dms and planet.longitude_in_sign_dms
        full_longitude = getattr(planet, 'longitude_dms', None) or "N/A"
        rasi_degree = getattr(planet, 'longitude_in_sign_dms', None) or "N/A"
        pada = str(getattr(planet, 'nakshatra_pada', None)) if getattr(planet, 'nakshatra_pada', None) is not None else "N/A"
        
        # Debug: Print first planet to verify data
        if planet.planet == "Sun" or planet.planet_tamil == "சூரியன்":
            print(f"DEBUG - Sun: longitude_dms={full_longitude}, longitude_in_sign_dms={rasi_degree}")
        
        planet_data.append([
            tamil_image_flowable(planet.planet_tamil, font_size=10),
            Paragraph(full_longitude, ParagraphStyle('Coord', fontName=get_font_name('English'), fontSize=10)),
            tamil_image_flowable(planet.nakshatra_name_tamil or planet.nakshatra_name, font_size=10),
            Paragraph(pada, ParagraphStyle('Number', fontName=get_font_name('English'), fontSize=10)),
            Paragraph(rasi_degree, ParagraphStyle('Coord', fontName=get_font_name('English'), fontSize=10)),
            tamil_image_flowable(planet.sign_name_tamil or planet.sign_name, font_size=10),
        ])
    
    # Compact column widths to fit on one page
    planet_table = Table(planet_data, colWidths=[0.7*inch, 0.85*inch, 0.9*inch, 0.45*inch, 0.85*inch, 0.7*inch])
    planet_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GREEN),          # green header
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),    # white header text
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, GREEN),          # green grid
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GREEN]),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ]))
    
    story.append(planet_table)
    story.append(Spacer(1, 0.02*inch))  # Minimal spacing
    
    # === CHARTS SECTION ===
    # Convert houses_tamil dict to int keys - ensure we use the correct chart data
    rasi_houses = {}
    navamsa_houses = {}
    
    # Rasi chart data - use houses_tamil from rasi_chart
    if hasattr(horoscope_result, 'rasi_chart') and horoscope_result.rasi_chart:
        rasi_chart_obj = horoscope_result.rasi_chart
        if hasattr(rasi_chart_obj, 'houses_tamil'):
            for house_num, planets in rasi_chart_obj.houses_tamil.items():
                house_key = int(house_num) if isinstance(house_num, str) else house_num
                if isinstance(planets, list):
                    rasi_houses[house_key] = planets
                elif planets:
                    rasi_houses[house_key] = [planets]
                else:
                    rasi_houses[house_key] = []
    
    # Navamsa chart data - use houses_tamil from navamsa_chart (different from Rasi)
    if hasattr(horoscope_result, 'navamsa_chart') and horoscope_result.navamsa_chart:
        navamsa_chart_obj = horoscope_result.navamsa_chart
        if hasattr(navamsa_chart_obj, 'houses_tamil'):
            for house_num, planets in navamsa_chart_obj.houses_tamil.items():
                house_key = int(house_num) if isinstance(house_num, str) else house_num
                if isinstance(planets, list):
                    navamsa_houses[house_key] = planets
                elif planets:
                    navamsa_houses[house_key] = [planets]
                else:
                    navamsa_houses[house_key] = []
    
    # Debug: Print ALL Navamsa chart data
    print("\n" + "="*60)
    print("DEBUG - NAVAMSA CHART DATA (houses_tamil):")
    print("="*60)
    for house_num in sorted(navamsa_houses.keys()):
        planets = navamsa_houses.get(house_num, [])
        print(f"  House {house_num:2d}: {planets}")
    print("="*60)
    print("\nDEBUG - RASI CHART DATA (houses_tamil):")
    print("="*60)
    for house_num in sorted(rasi_houses.keys()):
        planets = rasi_houses.get(house_num, [])
        print(f"  House {house_num:2d}: {planets}")
    print("="*60 + "\n")
    
    # Create charts side by side - smaller to fit on one page
    # Content width ~7.4 inches, use 2.4 inches per chart to save space
    chart_width_pt = 2.4 * 72  # Convert inches to points
    chart_height_pt = 2.4 * 72
    
    rasi_chart = draw_south_indian_chart_exact(rasi_houses, "ராசி", 
                                               width=chart_width_pt, height=chart_height_pt)
    navamsa_chart = draw_south_indian_chart_exact(navamsa_houses, "நவாம்சம்",
                                                  width=chart_width_pt, height=chart_height_pt)
    
    chart_table = Table([[rasi_chart, navamsa_chart]], 
                       colWidths=[2.4*inch, 2.4*inch])
    chart_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    story.append(chart_table)
    story.append(Spacer(1, 0.02*inch))  # Further reduced spacing
    
    # === DASA DETAILS SECTION ===
    if horoscope_result.current_dasa:
        dasa = horoscope_result.current_dasa
        
        # Title as Tamil image - render large and resize for quality
        story.append(tamil_image_flowable("தசா காலங்கள்", font_size=14, is_bold=True, max_width=1.8*inch))
        story.append(Spacer(1, 0.01*inch))  # Minimal spacing
        
        # Build dasa info lines - render large and resize to fit
        dasa_info_lines = []
        
        # 1. கிரக வக்ர நிலை - match UI: show first retrograde planet only
        retrograde_planets = horoscope_result.retrograde_planets_tamil or []
        if retrograde_planets and len(retrograde_planets) > 0:
            first_retro = retrograde_planets[0]  # UI shows only first one
            dasa_info_lines.append(tamil_image_flowable(
                f"கிரக வக்ர நிலை : {first_retro}", 
                font_size=14, max_width=5.0*inch  # Large font, resize to fit
            ))
        
        # 2. திசை இருப்பு - match UI format exactly
        if hasattr(dasa, 'balance_years') and dasa.balance_years is not None:
            first_dasha_planet = getattr(dasa, 'first_dasha_planet_tamil', None) or ""
            if not first_dasha_planet:
                # Fallback to current dasa planet if first_dasha not available
                first_dasha_planet = getattr(dasa, 'planet_tamil', '')
            balance_months = getattr(dasa, 'balance_months', 0) or 0
            balance_days = getattr(dasa, 'balance_days', 0) or 0
            dasa_info_lines.append(
                tamil_image_flowable(
                    f"திசை இருப்பு : {first_dasha_planet} திசை {dasa.balance_years} வருஷம், "
                    f"{balance_months} மாதம், {balance_days} நாள்",
                    font_size=14, max_width=5.0*inch  # Large font, resize to fit
                )
            )
        
        # 3. நடப்பு திசை-புக்தி - match UI format exactly
        if hasattr(dasa, 'current_bhukti_planet_tamil') and dasa.current_bhukti_planet_tamil:
            # Format dates as DD/MM/YYYY
            current_dasa_end = dasa.end_date.strftime('%d/%m/%Y') if hasattr(dasa.end_date, 'strftime') else str(dasa.end_date)
            current_bhukti_end = ""
            if hasattr(dasa, 'current_bhukti_end_date') and dasa.current_bhukti_end_date:
                if isinstance(dasa.current_bhukti_end_date, str):
                    try:
                        # Try parsing different date formats
                        for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%Y-%m-%dT%H:%M:%S']:
                            try:
                                dt = datetime.strptime(dasa.current_bhukti_end_date.split('T')[0], fmt)
                                current_bhukti_end = dt.strftime('%d/%m/%Y')
                                break
                            except:
                                continue
                        if not current_bhukti_end:
                            current_bhukti_end = dasa.current_bhukti_end_date
                    except:
                        current_bhukti_end = dasa.current_bhukti_end_date
                elif hasattr(dasa.current_bhukti_end_date, 'strftime'):
                    current_bhukti_end = dasa.current_bhukti_end_date.strftime('%d/%m/%Y')
                else:
                    current_bhukti_end = str(dasa.current_bhukti_end_date)
            
            if current_bhukti_end:
                planet_tamil = getattr(dasa, 'planet_tamil', '')
                bhukti_tamil = dasa.current_bhukti_planet_tamil
                dasa_info_lines.append(
                    tamil_image_flowable(
                        f"நடப்பு திசை-புக்தி : {planet_tamil} திசை {current_dasa_end} வரை, "
                        f"{bhukti_tamil} புக்தி {current_bhukti_end} வரை.",
                        font_size=14, max_width=5.0*inch  # Large font, resize to fit
                    )
                )
        
        # 4. பாவக மாறுதல் - match UI format
        bhava_maruthal = getattr(horoscope_result, 'bhava_maruthal_tamil', None) or {}
        if bhava_maruthal and isinstance(bhava_maruthal, dict):
            bhava_parts = []
            for planet, house in bhava_maruthal.items():
                bhava_parts.append(f"{planet}-{house}")
            if bhava_parts:
                dasa_info_lines.append(
                    tamil_image_flowable(
                        f"பாவக மாறுதல் : {', '.join(bhava_parts)}", 
                        font_size=14, max_width=5.0*inch  # Large font, resize to fit
                    )
                )
        
        # Create info box with neutral gray background - compact to fit on one page
        if dasa_info_lines:
            info_data = [[line] for line in dasa_info_lines]
            info_table = Table(info_data, colWidths=[5.0*inch])
            info_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                # No gray background — white matches 1988.pdf
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                ('TOPPADDING', (0, 0), (-1, -1), 1.5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
                ('LINEBEFORE', (0, 0), (-1, -1), 2, GREEN),  # green left border
            ]))
            story.append(info_table)
    
    # Build PDF
    doc.build(story)
    pdf_bytes = buf.getvalue()
    buf.close()
    
    return pdf_bytes
