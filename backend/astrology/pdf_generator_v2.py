"""
PDF Generator for Tamil Astrology Horoscopes - Version 2
Enhanced with colors, proper alignment, and complete field support
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
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.graphics.shapes import Drawing, Rect, Line, String
from reportlab.graphics import renderPDF

# Register fonts
pdfmetrics.registerFont(TTFont("TamilBold", "/usr/share/fonts/truetype/noto/NotoSerifTamil-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Tamil", "/usr/share/fonts/truetype/noto/NotoSansTamil-Regular.ttf"))
pdfmetrics.registerFont(TTFont("EnglishBold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("English", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))


def draw_header():
    """Draw the header with ASTRO NKV and Sanskrit verse"""
    header_drawing = Drawing(540, 80)
    
    # Title "ASTRO NKV" in large bold letters
    header_drawing.add(String(270, 60, "ASTRO NKV",
                              fontName='EnglishBold', fontSize=20,
                              fillColor=colors.HexColor('#8B0000'),  # Dark red
                              textAnchor='middle'))
    
    # Sanskrit verse line 1
    verse_line1 = "ஜனனீ ஜன்ம ஸௌக்யானாம் வர்த்தனீ குல ஸம்பதா ம்"
    header_drawing.add(String(270, 38, verse_line1,
                              fontName='Tamil', fontSize=10,
                              fillColor=colors.HexColor('#000080'),  # Navy blue
                              textAnchor='middle'))
    
    # Sanskrit verse line 2
    verse_line2 = "புத்ரீ பூர்வ புண்யானாம் லிக்யதே ஜன்ம பத்ரிகா."
    header_drawing.add(String(270, 24, verse_line2,
                              fontName='Tamil', fontSize=10,
                              fillColor=colors.HexColor('#000080'),  # Navy blue
                              textAnchor='middle'))
    
    # Decorative line
    header_drawing.add(Line(50, 15, 490, 15,
                           strokeColor=colors.HexColor('#DAA520'),  # Goldenrod
                           strokeWidth=2))
    
    return header_drawing


def draw_south_indian_chart_rotated(chart_data: Dict, chart_type: str, width: float = 160, height: float = 160):
    """
    Draw South Indian style chart - ROTATED 90 degrees counterclockwise
    """
    d = Drawing(width, height)
    
    # Colors
    border_color = colors.HexColor('#008000')  # Green borders
    planet_color = colors.HexColor('#0000FF')  # Blue planet text
    label_color = colors.HexColor('#FF1493')   # Deep pink center label
    
    cell_width = width / 4
    cell_height = height / 4
    
    # Draw outer border (2px)
    d.add(Rect(0, 0, width, height, strokeColor=border_color, fillColor=None, strokeWidth=2))
    
    # South Indian layout ROTATED 90° counterclockwise
    # Original: Top row = 12,1,2,3 -> Rotated: Left column = 12,1,2,3
    layout = [
        [3, 4, 5, 6],      # Top row (was right column)
        [2, 0, 0, 7],      # Second row (0 = center)
        [1, 0, 0, 8],      # Third row
        [12, 11, 10, 9]    # Bottom row (was left column)
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
                      strokeColor=border_color, fillColor=None, strokeWidth=1))
            
            # Get planets for this house
            planets = chart_data.get(house_num, [])
            
            if planets:
                # Handle multiple planets with smaller font
                if len(planets) > 2:
                    font_size = 6
                    planet_text = ", ".join(planets[:4])  # Max 4 planets
                elif len(planets) > 1:
                    font_size = 7
                    planet_text = ", ".join(planets)
                else:
                    font_size = 8
                    planet_text = planets[0]
                
                if len(planet_text) > 18:
                    planet_text = planet_text[:18] + "..."
                
                # Position text in center of cell
                text_x = x + cell_width / 2
                text_y = y + cell_height / 2 - 3
                
                d.add(String(text_x, text_y, planet_text,
                           fontName='Tamil', fontSize=font_size, fillColor=planet_color,
                           textAnchor='middle'))
    
    # Draw center label in pink
    center_x = width / 2
    center_y = height / 2 - 3
    d.add(String(center_x, center_y, chart_type,
                fontName='Tamil', fontSize=10, fillColor=label_color,
                textAnchor='middle', fontWeight='bold'))
    
    return d


def generate_horoscope_pdf(horoscope_result, personal_details: Dict[str, Any], system: str) -> bytes:
    """
    Generate a comprehensive horoscope PDF with all details
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, 
                           topMargin=0.3*inch, bottomMargin=0.3*inch,
                           leftMargin=0.5*inch, rightMargin=0.5*inch)
    
    story = []
    
    # Add header
    story.append(draw_header())
    story.append(Spacer(1, 0.1*inch))
    
    # === PERSONAL DETAILS SECTION ===
    # Correct Tamil labels from reference
    left_labels = [
        "பெயர்",           # Name
        "தாய் பெயர்",       # Mother's Name  
        "தந்தை பெயர்",     # Father's Name
        "ராசி",            # Rasi (Moon Sign)
        "லக்கினம்",        # Lagnam (Ascendant)
        "நட்சத்திரம்",     # Nakshatra (Star)
        "பட்சம்",          # Paksham
        "திதி",            # Thithi
        "யோகம்",           # Yogam
        "கரணம்",           # Karanam
        "அயனம்",           # Ayanam
        "சூரிய உதயம்",     # Sunrise
        "சூரிய அஸ்தமனம்"  # Sunset
    ]
    
    right_labels = [
        "பிறந்த தேதி",      # Date of Birth - Day
        "பிறந்த நேரம்",     # Time of Birth
        "தமிழ் தேதி",       # Tamil Date
        "பிறந்த ஊர்",       # Place of Birth
        "அட்ச தீர்க்கம்",    # Latitude, Longitude
        "அயனாம்சம்",        # Ayanamsa
        "",                 # Empty for alignment
        "",
        "",
        "",
        "",
        "",
        ""
    ]
    
    # Get values from horoscope_result
    mother_name = horoscope_result.birth_details.mother_name or "N/A"
    father_name = horoscope_result.birth_details.father_name or "N/A"
    
    # Build Paksha & Tithi string
    paksha = horoscope_result.paksha or ""
    tithi_tamil = horoscope_result.tithi_tamil or ""
    paksha_str = paksha if paksha else "N/A"
    tithi_str = tithi_tamil if tithi_tamil else "N/A"
    
    # Build Tamil date
    tamil_date_str = "N/A"
    if horoscope_result.tamil_month and horoscope_result.tamil_day:
        tamil_date_str = f"{horoscope_result.tamil_month} {horoscope_result.tamil_day}"
        if horoscope_result.tamil_year:
            tamil_date_str += f", {horoscope_result.tamil_year}"
    
    # Build lat/long string
    lat_long_str = f"{horoscope_result.birth_details.latitude}°, {horoscope_result.birth_details.longitude}°"
    
    left_vals = [
        horoscope_result.birth_details.name,
        mother_name,
        father_name,
        horoscope_result.moon_sign_tamil,
        horoscope_result.ascendant_tamil,
        horoscope_result.nakshatra_tamil,
        paksha_str,
        tithi_str,
        horoscope_result.yoga_tamil or "N/A",
        horoscope_result.karana_tamil or "N/A",
        horoscope_result.ayanamsa or "N/A",
        horoscope_result.sunrise_time or "06:00",
        horoscope_result.sunset_time or "18:00"
    ]
    
    right_vals = [
        horoscope_result.birth_details.date_of_birth.strftime("%d/%m/%Y"),
        horoscope_result.birth_details.time_of_birth.strftime("%H:%M:%S"),
        tamil_date_str,
        horoscope_result.birth_details.place_of_birth,
        lat_long_str,
        horoscope_result.ayanamsa or "23° 51'",
        "",
        "",
        "",
        "",
        "",
        "",
        ""
    ]
    
    # Create two-column table for personal details
    personal_data = []
    for i in range(max(len(left_labels), len(right_labels))):
        left_label = left_labels[i] if i < len(left_labels) else ""
        left_val = left_vals[i] if i < len(left_vals) else ""
        right_label = right_labels[i] if i < len(right_labels) else ""
        right_val = right_vals[i] if i < len(right_vals) else ""
        
        if left_label or right_label:  # Only add non-empty rows
            personal_data.append([left_label, left_val, right_label, right_val])
    
    personal_table = Table(personal_data, colWidths=[1.2*inch, 1.5*inch, 1.2*inch, 1.5*inch])
    personal_table.setStyle(TableStyle([
        # Header styling
        ('FONT', (0, 0), (0, -1), 'TamilBold', 9),  # Left labels
        ('FONT', (1, 0), (1, -1), 'Tamil', 9),      # Left values
        ('FONT', (2, 0), (2, -1), 'TamilBold', 9),  # Right labels
        ('FONT', (3, 0), (3, -1), 'Tamil', 9),      # Right values
        
        # Colors
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#8B4513')),  # Brown labels
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#000000')),  # Black values
        ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#8B4513')),  # Brown labels
        ('TEXTCOLOR', (3, 0), (3, -1), colors.HexColor('#000000')),  # Black values
        
        # Alignment
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('ALIGN', (3, 0), (3, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#C0C0C0')),  # Silver grid
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0E68C')),  # Light yellow bg for labels
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#F0E68C')),  # Light yellow bg for labels
        
        # Padding
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    story.append(personal_table)
    story.append(Spacer(1, 0.15*inch))
    
    # === PLANETARY POSITIONS TABLE ===
    # Create 6-column table (removed Lord column)
    planet_data = [["கிரகம்", "இருப்பு", "நட்சத்திரம்", "நட்.பாதம்", "ராசி அதிபதி", "நட்.அதிபதி"]]
    
    for planet in horoscope_result.planetary_positions:
        planet_data.append([
            planet.planet_tamil,
            planet.longitude_in_sign_dms or planet.longitude_dms or "N/A",
            planet.nakshatra_name_tamil or planet.nakshatra_name,
            str(planet.nakshatra_pada) if planet.nakshatra_pada else "N/A",
            planet.sign_name_tamil or planet.sign_name,
            planet.nakshatra_lord_tamil or planet.nakshatra_lord or "N/A"
        ])
    
    planet_table = Table(planet_data, colWidths=[0.9*inch, 0.9*inch, 0.9*inch, 0.7*inch, 0.9*inch, 0.9*inch])
    planet_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4169E1')),  # Royal blue
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONT', (0, 0), (-1, 0), 'TamilBold', 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        
        # Data rows
        ('FONT', (0, 1), (-1, -1), 'Tamil', 8),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#000000')),
        
        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F5F5DC'), colors.white]),  # Beige/White
        
        # Padding
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    story.append(planet_table)
    story.append(Spacer(1, 0.15*inch))
    
    # === CHARTS SECTION ===
    # Convert house data for charts
    rasi_houses = {}
    navamsa_houses = {}
    
    for planet in horoscope_result.planetary_positions:
        rasi_house = getattr(planet, 'rasi_house', 1)
        navamsa_house = getattr(planet, 'navamsa_house', 1)
        planet_abbr = planet.planet_tamil
        
        if rasi_house not in rasi_houses:
            rasi_houses[rasi_house] = []
        rasi_houses[rasi_house].append(planet_abbr)
        
        if navamsa_house not in navamsa_houses:
            navamsa_houses[navamsa_house] = []
        navamsa_houses[navamsa_house].append(planet_abbr)
    
    # Create charts side by side
    rasi_chart = draw_south_indian_chart_rotated(rasi_houses, "ராசி", width=160, height=160)
    navamsa_chart = draw_south_indian_chart_rotated(navamsa_houses, "நவாம்சம்", width=160, height=160)
    
    # Create table to place charts side by side
    chart_table = Table([[rasi_chart, navamsa_chart]], colWidths=[2.5*inch, 2.5*inch])
    chart_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(chart_table)
    story.append(Spacer(1, 0.1*inch))
    
    # === DASA DETAILS SECTION ===
    if horoscope_result.current_dasa:
        dasa = horoscope_result.current_dasa
        
        dasa_title_style = ParagraphStyle(
            'DasaTitle',
            fontName='TamilBold',
            fontSize=10,
            textColor=colors.HexColor('#8B0000'),  # Dark red
            alignment=1  # Center
        )
        
        dasa_text_style = ParagraphStyle(
            'DasaText',
            fontName='Tamil',
            fontSize=8,
            textColor=colors.black,
            alignment=0  # Left
        )
        
        story.append(Paragraph("விம்சோத்தரி தசா விவரம்", dasa_title_style))
        story.append(Spacer(1, 0.05*inch))
        
        # Dasa details
        dasa_info = [
            f"தற்போதைய திசை: {dasa.planet_tamil} ({dasa.start_date.strftime('%d/%m/%Y')} - {dasa.end_date.strftime('%d/%m/%Y')})",
            f"திசை இருப்பு: {dasa.balance_years or 'N/A'} ஆண்டுகள்"
        ]
        
        if dasa.next_dasa_planet_tamil:
            dasa_info.append(f"அடுத்த திசை: {dasa.next_dasa_planet_tamil}")
        
        if dasa.current_bhukti_planet_tamil:
            dasa_info.append(f"தற்போதைய புக்தி: {dasa.current_bhukti_planet_tamil}")
        
        if dasa.next_bhukti_planet_tamil:
            dasa_info.append(f"அடுத்த புக்தி: {dasa.next_bhukti_planet_tamil}")
        
        for info in dasa_info:
            story.append(Paragraph(info, dasa_text_style))
            story.append(Spacer(1, 0.03*inch))
    
    # Build PDF
    doc.build(story)
    pdf_bytes = buf.getvalue()
    buf.close()
    
    return pdf_bytes
