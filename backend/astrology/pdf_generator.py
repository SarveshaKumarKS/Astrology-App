"""
PDF Generator for Tamil Astrology Horoscopes
Generates single-page horoscope PDFs with Tamil text support
"""

import io
from datetime import datetime
from typing import Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, 
    Spacer, Flowable, PageBreak
)
from reportlab.graphics.shapes import Drawing, Rect, Line, String
from reportlab.graphics import renderPDF

# Register fonts
pdfmetrics.registerFont(TTFont("TamilBold", "/usr/share/fonts/truetype/noto/NotoSerifTamil-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Tamil", "/usr/share/fonts/truetype/noto/NotoSansTamil-Regular.ttf"))
pdfmetrics.registerFont(TTFont("EnglishBold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("English", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))


def choose_font(text: str) -> str:
    """Choose appropriate font based on text content"""
    if not text:
        return "English"
    # Check if text contains Tamil characters (Unicode range U+0B80 to U+0BFF)
    has_tamil = any('\u0B80' <= c <= '\u0BFF' for c in text)
    if has_tamil:
        return "Tamil"
    return "English"


def draw_south_indian_chart_square(chart_data: Dict, chart_type: str, width: float = 180, height: float = 180):
    """
    Draw South Indian style chart with 4x4 SQUARE grid layout (not diamond)
    Matches the SouthIndianChart.tsx component exactly
    chart_data: dictionary with houses (1-12) mapping to list of planet names  
    chart_type: "ராசி" or "நவாம்சம்"
    """
    d = Drawing(width, height)
    
    # Colors - matching bala.pdf
    border_color = colors.HexColor('#008000')  # Green borders
    planet_color = colors.HexColor('#0000FF')  # Blue planet text
    label_color = colors.HexColor('#FF1493')   # Pink center label
    
    # Cell dimensions for 4x4 grid
    cell_width = width / 4
    cell_height = height / 4
    
    # Draw outer border (2px)
    d.add(Rect(0, 0, width, height, strokeColor=border_color, fillColor=None, strokeWidth=2))
    
    # South Indian layout - same as SouthIndianChart.tsx
    # Row 1: Houses 12, 1, 2, 3 (top row)
    # Row 2: House 11, [center], House 4
    # Row 3: House 10, [center], House 5
    # Row 4: Houses 9, 8, 7, 6 (bottom row)
    
    layout = [
        [12, 1, 2, 3],      # Top row
        [11, 0, 0, 4],      # Second row (0 = center)
        [10, 0, 0, 5],      # Third row
        [9, 8, 7, 6]        # Bottom row
    ]
    
    # Draw grid lines and cells
    for row_idx, row in enumerate(layout):
        for col_idx, house_num in enumerate(row):
            x = col_idx * cell_width
            y = row_idx * cell_height
            
            # Skip center cells
            if house_num == 0:
                continue
            
            # Draw cell border
            d.add(Rect(x, y, cell_width, cell_height, 
                      strokeColor=border_color, fillColor=None, strokeWidth=1))
            
            # Get planets for this house
            planets = chart_data.get(house_num, [])
            
            if planets:
                # Draw planet text in blue
                planet_text = ", ".join(planets[:3])  # Max 3 planets per cell
                if len(planet_text) > 12:
                    planet_text = planet_text[:12] + "..."
                
                # Position text in center of cell
                text_x = x + cell_width / 2
                text_y = y + cell_height / 2 - 3
                
                d.add(String(text_x, text_y, planet_text,
                           fontName='Tamil', fontSize=8, fillColor=planet_color,
                           textAnchor='middle'))
    
    # Draw center label in pink
    center_x = width / 2
    center_y = height / 2 - 3
    d.add(String(center_x, center_y, chart_type,
                fontName='Tamil', fontSize=10, fillColor=label_color,
                textAnchor='middle'))
    
    return d


def generate_horoscope_pdf(horoscope_result, personal_details: Dict[str, Any], system: str) -> bytes:
    """
    Generate a single-page horoscope PDF
    
    Args:
        horoscope_result: HoroscopeResult object from calculator
        personal_details: Dictionary with personal info
        system: "thirukkanitham" or "vakkiam"
    
    Returns:
        bytes: PDF file content
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, 
        pagesize=A4,
        leftMargin=30,
        rightMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName='EnglishBold',
        fontSize=18,
        textColor=colors.HexColor('#000080'),
        alignment=1,  # Center
        spaceAfter=12
    )
    story.append(Paragraph("ASTRO NKV", title_style))
    story.append(Spacer(1, 6))
    
    # System subtitle
    system_text = "திருக்கணித முறை" if system == "thirukkanitham" else "வாக்கிய முறை"
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontName='Tamil',
        fontSize=12,
        alignment=1,
        spaceAfter=10
    )
    story.append(Paragraph(system_text, subtitle_style))
    story.append(Spacer(1, 8))
    
    # Personal Details Table (2 columns x 4 rows layout)
    left_labels = ["பெயர்", "லக்னம்", "நட்சத்திரம்", "ராசி", 
                   "பக்ஷம் & திதி", "யோகம்", "கரணம்", "அயனாம்சம்"]
    right_labels = ["சூரிய உதயம்", "சூரிய அஸ்தம்", "தேதி", "நேரம்",
                    "தமிழ் தேதி", "உதயாதி நாழிகை", "இடம்", "தீர்க்க ரேகை",
                    "அட்ச ரேகை", "பொது நேரம்", "நேர திருத்தம்", "யோகி-அவயோகி"]
    
    # Build Paksha & Tithi string
    paksha = horoscope_result.paksha or ""
    tithi_tamil = horoscope_result.tithi_tamil or ""
    paksha_tithi_str = f"{paksha} - {tithi_tamil}" if paksha and tithi_tamil else (tithi_tamil or paksha or "")
    
    # Build Tamil date string (if available)
    tamil_date_str = "N/A"
    if horoscope_result.tamil_day and horoscope_result.tamil_month:
        tamil_date_str = f"{horoscope_result.tamil_month} {horoscope_result.tamil_day}"
        if horoscope_result.tamil_year:
            tamil_date_str += f", {horoscope_result.tamil_year}"
    
    # Build Yogi-Avayogi string
    yogi_avayogi_str = ""
    if horoscope_result.yogi_planet_tamil and horoscope_result.avayogi_planet_tamil:
        yogi_avayogi_str = f"{horoscope_result.yogi_planet_tamil} - {horoscope_result.avayogi_planet_tamil}"
    
    left_vals = [
        personal_details.get("name", horoscope_result.birth_details.name),
        horoscope_result.ascendant_tamil,
        f"{horoscope_result.nakshatra_tamil}",
        horoscope_result.moon_sign_tamil,
        paksha_tithi_str,
        horoscope_result.yoga_tamil or "",
        horoscope_result.karana_tamil or "",
        horoscope_result.ayanamsa or "23° 51'"
    ]
    
    right_vals = [
        horoscope_result.sunrise_time or "06:00",
        horoscope_result.sunset_time or "18:00",
        horoscope_result.birth_details.date_of_birth.strftime("%d/%m/%Y"),
        horoscope_result.birth_details.time_of_birth.strftime("%H:%M:%S"),
        tamil_date_str,
        horoscope_result.udayadi_nazhigai or "",
        horoscope_result.birth_details.place_of_birth,
        f"{horoscope_result.birth_details.longitude}°",
        f"{horoscope_result.birth_details.latitude}°",
        horoscope_result.birth_details.timezone,
        str(horoscope_result.birth_details.time_correction),
        yogi_avayogi_str
    ]
    
    # Build personal details table
    table_data = []
    max_rows = max(len(left_labels), len(right_labels))
    
    for i in range(max_rows):
        row = []
        # Left side
        if i < len(left_labels):
            label_font = "TamilBold"
            val = left_vals[i] if i < len(left_vals) else ""
            val_font = choose_font(val)
            row.append(Paragraph(f"<font name='{label_font}' size='9'>{left_labels[i]}</font>", styles['Normal']))
            row.append(Paragraph(f"<font name='{val_font}' size='9'>{val}</font>", styles['Normal']))
        else:
            row.extend(["", ""])
        
        # Right side
        if i < len(right_labels):
            label_font = "TamilBold"
            val = right_vals[i] if i < len(right_vals) else ""
            val_font = choose_font(val)
            row.append(Paragraph(f"<font name='{label_font}' size='9'>{right_labels[i]}</font>", styles['Normal']))
            row.append(Paragraph(f"<font name='{val_font}' size='9'>{val}</font>", styles['Normal']))
        else:
            row.extend(["", ""])
        
        table_data.append(row)
    
    personal_table = Table(table_data, colWidths=[70, 120, 95, 150])
    personal_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(personal_table)
    story.append(Spacer(1, 10))
    
    # Horizontal line
    story.append(Spacer(1, 2))
    
    # Planetary Positions Table (6 columns, no Lord column)
    planet_headers = ["கிரகம்", "பாகை", "நட்சத்திரம்", "பாதம்", "ராசி பாகை", "ராசி"]
    planet_data = [planet_headers]
    
    for pos in horoscope_result.planetary_positions:
        planet_data.append([
            pos.planet_tamil or pos.planet,
            pos.longitude_dms or "",
            pos.nakshatra_name_tamil or pos.nakshatra_name,
            str(pos.nakshatra_pada) if pos.nakshatra_pada else "",
            pos.longitude_in_sign_dms or "",
            pos.sign_name_tamil or pos.sign_name
        ])
    
    planets_table = Table(planet_data, colWidths=[65, 70, 100, 40, 75, 85])
    planets_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E0E0E0')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'TamilBold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTNAME', (0, 1), (-1, -1), 'Tamil'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(planets_table)
    story.append(Spacer(1, 12))
    
    # Charts section - Rasi and Navamsa side by side
    # Convert chart data to proper format
    rasi_houses = {}
    for house_num, planets in horoscope_result.rasi_chart.houses_tamil.items():
        rasi_houses[house_num] = planets
    
    navamsa_houses = {}
    for house_num, planets in horoscope_result.navamsa_chart.houses_tamil.items():
        navamsa_houses[house_num] = planets
    
    # Create chart drawings - using square layout like bala.pdf
    rasi_drawing = draw_south_indian_chart_square(rasi_houses, "ராசி", width=180, height=180)
    navamsa_drawing = draw_south_indian_chart_square(navamsa_houses, "நவாம்சம்", width=180, height=180)
    
    # Create table to place charts side by side
    charts_data = [[rasi_drawing, navamsa_drawing]]
    charts_table = Table(charts_data, colWidths=[200, 200])
    charts_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(charts_table)
    story.append(Spacer(1, 12))
    
    # Dasha and additional details
    cur = horoscope_result.current_dasa
    
    # Retrograde planets
    retro_planets = horoscope_result.retrograde_planets_tamil or horoscope_result.retrograde_planets or []
    retro_text = ", ".join(retro_planets) if retro_planets else "இல்லை"
    
    # Bhava Maruthal
    bhava = horoscope_result.bhava_maruthal_tamil or horoscope_result.bhava_maruthal or {}
    bhava_text = ", ".join([f"{k}-{v}" for k, v in bhava.items()]) if bhava else "N/A"
    
    # Build details lines
    details_style = ParagraphStyle(
        'Details',
        parent=styles['Normal'],
        fontName='Tamil',
        fontSize=9,
        leading=14
    )
    
    details_lines = [
        f"<b>கிரக வக்கிர நிலை:</b> {retro_text}",
    ]
    
    if cur.balance_years is not None:
        details_lines.append(
            f"<b>திசை இருப்பு:</b> {cur.planet_tamil} திசை {cur.balance_years} வருடம், "
            f"{cur.balance_months} மாதம், {cur.balance_days} நாள்"
        )
    
    if cur.current_bhukti_planet:
        details_lines.append(
            f"<b>நடப்பு திசை-புக்தி:</b> {cur.planet_tamil} திசை {cur.end_date} வரை, "
            f"{cur.current_bhukti_planet_tamil} புக்தி {cur.current_bhukti_end_date} வரை"
        )
    
    details_lines.append(f"<b>பாவக மாற்றுதல்:</b> {bhava_text}")
    
    for line in details_lines:
        story.append(Paragraph(line, details_style))
        story.append(Spacer(1, 4))
    
    # Build PDF
    doc.build(story)
    pdf_bytes = buf.getvalue()
    buf.close()
    
    return pdf_bytes
