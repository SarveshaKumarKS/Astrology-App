"""
PDF Generator for Tamil Astrology Horoscopes
Fixed Tamil compound character rendering with proper UTF-8 Unicode support
"""
# -*- coding: utf-8 -*-

import io
import os
from datetime import datetime
from typing import Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.graphics.shapes import Drawing, Rect, Line, String
from reportlab.graphics import renderPDF

# Font paths - Noto Serif Tamil for proper Unicode Tamil support
TAMIL_BOLD_FONT = "/usr/share/fonts/truetype/noto/NotoSerifTamil-Bold.ttf"
TAMIL_REGULAR_FONT = "/usr/share/fonts/truetype/noto/NotoSerifTamil-Regular.ttf"
ENGLISH_BOLD_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ENGLISH_REGULAR_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# Register fonts with proper error handling
def register_fonts():
    """Register Tamil and English fonts for PDF generation"""
    fonts_registered = {
        'TamilBold': False,
        'Tamil': False,
        'EnglishBold': False,
        'English': False
    }
    
    try:
        if os.path.exists(TAMIL_BOLD_FONT):
            pdfmetrics.registerFont(TTFont("TamilBold", TAMIL_BOLD_FONT))
            fonts_registered['TamilBold'] = True
    except Exception as e:
        print(f"Warning: Could not register TamilBold font: {e}")
    
    try:
        if os.path.exists(TAMIL_REGULAR_FONT):
            pdfmetrics.registerFont(TTFont("Tamil", TAMIL_REGULAR_FONT))
            fonts_registered['Tamil'] = True
    except Exception as e:
        print(f"Warning: Could not register Tamil font: {e}")
    
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
_fonts_registered = register_fonts()

# Helper function to get font name with fallback
def get_font_name(font_key):
    """Get font name, fallback to Helvetica if not available"""
    registered = pdfmetrics.getRegisteredFontNames()
    if font_key in registered:
        return font_key
    # Fallback mapping
    fallbacks = {
        'TamilBold': 'Helvetica-Bold',
        'Tamil': 'Helvetica',
        'EnglishBold': 'Helvetica-Bold',
        'English': 'Helvetica'
    }
    return fallbacks.get(font_key, 'Helvetica')


def draw_header():
    """Draw the header with ASTRO NKV and Sanskrit verse"""
    header_drawing = Drawing(540, 70)
    
    # Title "ASTRO NKV" in large bold letters
    header_drawing.add(String(270, 52, "ASTRO NKV",
                              fontName=get_font_name('EnglishBold'), fontSize=18,
                              fillColor=colors.HexColor('#8B0000'),
                              textAnchor='middle'))
    
    # Sanskrit verse line 1
    verse_line1 = "ஜனனீ ஜன்ம ஸௌக்யானாம் வர்த்தனீ குல ஸம்பதாம்"
    header_drawing.add(String(270, 32, verse_line1,
                              fontName=get_font_name('Tamil'), fontSize=9,
                              fillColor=colors.HexColor('#000080'),
                              textAnchor='middle'))
    
    # Sanskrit verse line 2
    verse_line2 = "புத்ரீ பூர்வ புண்யானாம் லிக்யதே ஜன்ம பத்ரிகா."
    header_drawing.add(String(270, 18, verse_line2,
                              fontName=get_font_name('Tamil'), fontSize=9,
                              fillColor=colors.HexColor('#000080'),
                              textAnchor='middle'))
    
    # Decorative line
    header_drawing.add(Line(50, 8, 490, 8,
                           strokeColor=colors.HexColor('#DAA520'),
                           strokeWidth=1.5))
    
    return header_drawing


def draw_south_indian_chart_rotated(chart_data: Dict, chart_type: str, width: float = 150, height: float = 150):
    """
    Draw South Indian style chart with standard layout
    Matches SouthIndianChart.tsx component
    With support for multiple planets per cell
    """
    d = Drawing(width, height)
    
    # Colors
    border_color = colors.HexColor('#008000')  # Green borders
    planet_color = colors.HexColor('#0000FF')  # Blue planet text
    label_color = colors.HexColor('#FF1493')   # Deep pink center label
    
    cell_width = width / 4
    cell_height = height / 4
    
    # Draw outer border (1.5px)
    d.add(Rect(0, 0, width, height, strokeColor=border_color, fillColor=None, strokeWidth=1.5))
    
    # Standard South Indian layout (matching SouthIndianChart.tsx)
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
    
    # Draw grid and planets
    for row_idx, row in enumerate(layout):
        for col_idx, house_num in enumerate(row):
            x = col_idx * cell_width
            y = row_idx * cell_height
            
            if house_num == 0:
                continue
            
            # Draw cell border
            d.add(Rect(x, y, cell_width, cell_height,
                      strokeColor=border_color, fillColor=None, strokeWidth=0.8))
            
            # Get planets for this house
            planets = chart_data.get(house_num, [])
            
            if planets:
                # Handle multiple planets with adaptive font sizing
                num_planets = len(planets)
                if num_planets > 3:
                    font_size = 5.5
                    planet_text = ", ".join(planets[:5])
                elif num_planets > 2:
                    font_size = 6
                    planet_text = ", ".join(planets[:4])
                elif num_planets > 1:
                    font_size = 6.5
                    planet_text = ", ".join(planets[:3])
                else:
                    font_size = 7
                    planet_text = planets[0]
                
                # Center text in cell
                text_x = x + cell_width / 2
                text_y = y + cell_height / 2 - 2.5
                
                d.add(String(text_x, text_y, planet_text,
                           fontName=get_font_name('Tamil'), fontSize=font_size, fillColor=planet_color,
                           textAnchor='middle'))
    
    # Draw center label in pink
    center_x = width / 2
    center_y = height / 2 - 2.5
    d.add(String(center_x, center_y, chart_type,
                fontName=get_font_name('TamilBold'), fontSize=9, fillColor=label_color,
                textAnchor='middle'))
    
    return d


def generate_horoscope_pdf(horoscope_result, personal_details: Dict[str, Any], system: str) -> bytes:
    """
    Generate comprehensive horoscope PDF with proper Tamil rendering and full page usage
    """
    buf = io.BytesIO()
    
    # Tighter margins for full page usage
    doc = SimpleDocTemplate(buf, pagesize=A4, 
                           topMargin=0.25*inch, bottomMargin=0.25*inch,
                           leftMargin=0.4*inch, rightMargin=0.4*inch)
    
    story = []
    
    # Add header
    story.append(draw_header())
    story.append(Spacer(1, 0.08*inch))
    
    # === PERSONAL DETAILS SECTION ===
    # Using exact Tamil labels from reference (with proper compound characters)
    left_labels = [
        "பெயர்",              # Name
        "தாய் பெயர்",         # Mother's Name  
        "தந்தை பெயர்",       # Father's Name
        "ராசி",               # Rasi
        "லக்கினம்",           # Lagna
        "நட்சத்திரம்",        # Nakshatra
        "பட்சம்",             # Paksham
        "திதி",               # Thithi
        "யோகம்",              # Yogam
        "கரணம்",              # Karanam
        "சூரிய உதயம்",        # Sunrise
        "சூரிய அஸ்தமனம்",    # Sunset
        "அயனாம்சம்"          # Ayanamsa
    ]
    
    right_labels = [
        "பிறந்த தேதி",        # Date of Birth
        "பிறந்த நேரம்",       # Time of Birth
        "தமிழ் தேதி",         # Tamil Date
        "பிறந்த ஊர்",         # Place of Birth
        "அட்சம்",             # Latitude
        "தீர்க்கம்",           # Longitude
        "",
        "",
        "",
        "",
        "",
        "",
        ""
    ]
    
    # Build values from horoscope_result
    mother_name = getattr(horoscope_result.birth_details, 'mother_name', None) or "N/A"
    father_name = getattr(horoscope_result.birth_details, 'father_name', None) or "N/A"
    
    paksha = getattr(horoscope_result, 'paksha', None) or "N/A"
    tithi_tamil = getattr(horoscope_result, 'tithi_tamil', None) or "N/A"
    
    # Build Tamil date
    tamil_date_str = "N/A"
    tamil_month = getattr(horoscope_result, 'tamil_month', None)
    tamil_day = getattr(horoscope_result, 'tamil_day', None)
    tamil_year = getattr(horoscope_result, 'tamil_year', None)
    if tamil_month and tamil_day:
        tamil_date_str = f"{tamil_month} {tamil_day}"
        if tamil_year:
            tamil_date_str += f", {tamil_year}"
    
    left_vals = [
        horoscope_result.birth_details.name,
        mother_name,
        father_name,
        horoscope_result.moon_sign_tamil,
        horoscope_result.ascendant_tamil,
        horoscope_result.nakshatra_tamil,
        paksha,
        tithi_tamil,
        getattr(horoscope_result, 'yoga_tamil', None) or "N/A",
        getattr(horoscope_result, 'karana_tamil', None) or "N/A",
        getattr(horoscope_result, 'sunrise_time', None) or "06:00",
        getattr(horoscope_result, 'sunset_time', None) or "18:00",
        getattr(horoscope_result, 'ayanamsa', None) or "23° 51'"
    ]
    
    right_vals = [
        horoscope_result.birth_details.date_of_birth.strftime("%d/%m/%Y"),
        horoscope_result.birth_details.time_of_birth.strftime("%H:%M:%S"),
        tamil_date_str,
        horoscope_result.birth_details.place_of_birth,
        f"{horoscope_result.birth_details.latitude}°",
        f"{horoscope_result.birth_details.longitude}°",
        "",
        "",
        "",
        "",
        "",
        "",
        ""
    ]
    
    # Create two-column table
    personal_data = []
    for i in range(max(len(left_labels), len(right_labels))):
        left_label = left_labels[i] if i < len(left_labels) else ""
        left_val = left_vals[i] if i < len(left_vals) else ""
        right_label = right_labels[i] if i < len(right_labels) else ""
        right_val = right_vals[i] if i < len(right_vals) else ""
        
        if left_label or right_label:
            personal_data.append([left_label, left_val, right_label, right_val])
    
    personal_table = Table(personal_data, colWidths=[1.1*inch, 1.4*inch, 1.1*inch, 1.4*inch])
    personal_table.setStyle(TableStyle([
        ('FONT', (0, 0), (0, -1), get_font_name('TamilBold'), 8),
        ('FONT', (1, 0), (1, -1), get_font_name('Tamil'), 8),
        ('FONT', (2, 0), (2, -1), get_font_name('TamilBold'), 8),
        ('FONT', (3, 0), (3, -1), get_font_name('Tamil'), 8),
        
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#8B4513')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#000000')),
        ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#8B4513')),
        ('TEXTCOLOR', (3, 0), (3, -1), colors.HexColor('#000000')),
        
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('ALIGN', (3, 0), (3, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#C0C0C0')),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0E68C')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#F0E68C')),
        
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ]))
    
    story.append(personal_table)
    story.append(Spacer(1, 0.1*inch))
    
    # === PLANETARY POSITIONS TABLE (6 columns - matching reference) ===
    planet_data = [["கிரகம்", "இருப்பு", "நட்சத்திரம்", "நட்.பாதம்", "ராசி அதிபதி", "நட்.அதிபதி"]]
    
    for planet in horoscope_result.planetary_positions:
        planet_data.append([
            planet.planet_tamil,
            planet.longitude_in_sign_dms or planet.longitude_dms or "",
            planet.nakshatra_name_tamil or planet.nakshatra_name,
            str(planet.nakshatra_pada) if planet.nakshatra_pada else "",
            planet.sign_name_tamil or planet.sign_name,
            planet.nakshatra_lord_tamil or planet.nakshatra_lord or ""
        ])
    
    # Optimized column widths for 6 columns
    planet_table = Table(planet_data, colWidths=[0.85*inch, 0.85*inch, 0.85*inch, 0.65*inch, 0.85*inch, 0.85*inch])
    planet_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4169E1')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONT', (0, 0), (-1, 0), get_font_name('TamilBold'), 8),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        
        # Data rows
        ('FONT', (0, 1), (-1, -1), get_font_name('Tamil'), 7),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#000000')),
        
        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F5F5DC'), colors.white]),
        
        # Padding
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    story.append(planet_table)
    story.append(Spacer(1, 0.1*inch))
    
    # === CHARTS SECTION ===
    # Use chart data directly from horoscope_result
    rasi_houses = {}
    navamsa_houses = {}
    
    # Convert houses_tamil dict (keys may be strings) to int keys
    for house_num, planets in horoscope_result.rasi_chart.houses_tamil.items():
        house_key = int(house_num) if isinstance(house_num, str) else house_num
        rasi_houses[house_key] = planets
    
    for house_num, planets in horoscope_result.navamsa_chart.houses_tamil.items():
        house_key = int(house_num) if isinstance(house_num, str) else house_num
        navamsa_houses[house_key] = planets
    
    # Create charts side by side
    rasi_chart = draw_south_indian_chart_rotated(rasi_houses, "ராசி", width=150, height=150)
    navamsa_chart = draw_south_indian_chart_rotated(navamsa_houses, "நவாம்சம்", width=150, height=150)
    
    chart_table = Table([[rasi_chart, navamsa_chart]], colWidths=[2.3*inch, 2.3*inch])
    chart_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(chart_table)
    story.append(Spacer(1, 0.08*inch))
    
    # === DASA DETAILS SECTION ===
    if horoscope_result.current_dasa:
        dasa = horoscope_result.current_dasa
        
        # Title style - centered, bold, dark red
        dasa_title_style = ParagraphStyle(
            'DasaTitle',
            fontName=get_font_name('TamilBold'),
            fontSize=12,
            textColor=colors.HexColor('#000000'),
            alignment=1,  # Center
            spaceAfter=8
        )
        
        # Text style for dasa info box
        dasa_text_style = ParagraphStyle(
            'DasaText',
            fontName=get_font_name('Tamil'),
            fontSize=9,
            textColor=colors.black,
            alignment=0,  # Left
            leading=12
        )
        
        # Add title
        story.append(Paragraph("தசா காலங்கள்", dasa_title_style))
        story.append(Spacer(1, 0.06*inch))
        
        # Build dasa info lines
        dasa_info_lines = []
        
        # 1. கிரக வக்ர நிலை (Retrograde planets)
        retrograde_planets = horoscope_result.retrograde_planets_tamil or []
        if retrograde_planets:
            retro_text = ", ".join(retrograde_planets)
            dasa_info_lines.append(f"கிரக வக்ர நிலை : {retro_text}")
        
        # 2. திசை இருப்பு (First dasha balance)
        if hasattr(dasa, 'balance_years') and dasa.balance_years is not None:
            first_dasha_planet = getattr(dasa, 'first_dasha_planet_tamil', None) or getattr(dasa, 'planet_tamil', '')
            balance_months = getattr(dasa, 'balance_months', 0) or 0
            balance_days = getattr(dasa, 'balance_days', 0) or 0
            dasa_info_lines.append(
                f"திசை இருப்பு : {first_dasha_planet} திசை {dasa.balance_years} வருஷம், "
                f"{balance_months} மாதம், {balance_days} நாள்"
            )
        
        # 3. நடப்பு திசை-புக்தி (Current Dasha-Bhukti)
        if hasattr(dasa, 'current_bhukti_planet_tamil') and dasa.current_bhukti_planet_tamil:
            current_dasa_end = dasa.end_date.strftime('%d/%m/%Y')
            current_bhukti_end = ""
            if hasattr(dasa, 'current_bhukti_end_date') and dasa.current_bhukti_end_date:
                # Parse date string if needed
                if isinstance(dasa.current_bhukti_end_date, str):
                    try:
                        from datetime import datetime
                        dt = datetime.strptime(dasa.current_bhukti_end_date, '%Y-%m-%d')
                        current_bhukti_end = dt.strftime('%d/%m/%Y')
                    except:
                        current_bhukti_end = dasa.current_bhukti_end_date
                else:
                    current_bhukti_end = dasa.current_bhukti_end_date.strftime('%d/%m/%Y')
            
            if current_bhukti_end:
                dasa_info_lines.append(
                    f"நடப்பு திசை-புக்தி : {dasa.planet_tamil} திசை {current_dasa_end} வரை, "
                    f"{dasa.current_bhukti_planet_tamil} புக்தி {current_bhukti_end} வரை."
                )
        
        # 4. பாவக மாறுதல் (Bhava Maruthal)
        bhava_maruthal = horoscope_result.bhava_maruthal_tamil or {}
        if bhava_maruthal:
            bhava_parts = [f"{planet}-{house}" for planet, house in bhava_maruthal.items()]
            if bhava_parts:
                dasa_info_lines.append(f"பாவக மாறுதல் : {', '.join(bhava_parts)}")
        
        # Create info box with light blue background and left border
        if dasa_info_lines:
            # Create table for the info box
            info_data = [[Paragraph(line, dasa_text_style)] for line in dasa_info_lines]
            info_table = Table(info_data, colWidths=[4.8*inch])
            info_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), get_font_name('Tamil'), 9),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#E8F4FD')),  # Light blue
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LINEBELOW', (0, 0), (-1, -1), 0, colors.transparent),
                # Left border line
                ('LINEBEFORE', (0, 0), (-1, -1), 4, colors.HexColor('#4A90E2')),  # Blue left border
            ]))
            story.append(info_table)
    
    # Build PDF
    doc.build(story)
    pdf_bytes = buf.getvalue()
    buf.close()
    
    return pdf_bytes
