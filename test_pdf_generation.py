#!/usr/bin/env python3
"""
Test script to generate PDF horoscope
"""

import sys
from datetime import date, time, datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from astrology.models import (
    BirthDetails, HoroscopeResult, PlanetaryPosition, 
    Chart, DasaPeriod
)
from astrology.pdf_generator import generate_horoscope_pdf

def create_test_horoscope():
    """Create a test horoscope with sample data"""
    
    # Birth details
    birth_details = BirthDetails(
        name="ராமன்",
        mother_name="சீதா",
        father_name="தசரதன்",
        date_of_birth=date(1990, 5, 15),
        time_of_birth=time(10, 30, 0),
        place_of_birth="சென்னை",
        latitude=13.0827,
        longitude=80.2707,
        timezone="Asia/Kolkata",
        time_correction=0
    )
    
    # Planetary positions
    planetary_positions = [
        PlanetaryPosition(
            planet="Sun",
            planet_tamil="சூரியன்",
            longitude=254.235,
            sign=9,
            sign_name="Sagittarius",
            sign_name_tamil="தனுசு",
            nakshatra=18,
            nakshatra_name="Pooradam",
            nakshatra_name_tamil="பூராடம்",
            house=9,
            retrograde=False,
            longitude_dms="254:14:09",
            longitude_in_sign=14.235,
            longitude_in_sign_dms="14:14:09",
            nakshatra_pada=1,
            nakshatra_lord="Jupiter",
            nakshatra_lord_tamil="குரு"
        ),
        PlanetaryPosition(
            planet="Moon",
            planet_tamil="சந்திரன்",
            longitude=122.061,
            sign=5,
            sign_name="Leo",
            sign_name_tamil="சிம்மம்",
            nakshatra=10,
            nakshatra_name="Magha",
            nakshatra_name_tamil="மகம்",
            house=5,
            retrograde=False,
            longitude_dms="122:03:40",
            longitude_in_sign=2.061,
            longitude_in_sign_dms="2:03:40",
            nakshatra_pada=1,
            nakshatra_lord="Ketu",
            nakshatra_lord_tamil="கேது"
        ),
        PlanetaryPosition(
            planet="Mars",
            planet_tamil="செவ்வாய்",
            longitude=97.536,
            sign=4,
            sign_name="Cancer",
            sign_name_tamil="கடகம்",
            house=4,
            retrograde=False,
            longitude_dms="97:32:11",
            longitude_in_sign=7.536,
            longitude_in_sign_dms="7:32:11",
            nakshatra=8,
            nakshatra_name="Pushya",
            nakshatra_name_tamil="பூசம்",
            nakshatra_pada=2,
            nakshatra_lord="Saturn",
            nakshatra_lord_tamil="சனி"
        ),
        PlanetaryPosition(
            planet="Mercury",
            planet_tamil="புதன்",
            longitude=0.264,
            sign=1,
            sign_name="Aries",
            sign_name_tamil="மேஷம்",
            house=1,
            retrograde=False,
            longitude_dms="0:15:50",
            longitude_in_sign=0.264,
            longitude_in_sign_dms="0:15:50",
            nakshatra=1,
            nakshatra_name="Ashwini",
            nakshatra_name_tamil="அஸ்வினி",
            nakshatra_pada=1,
            nakshatra_lord="Ketu",
            nakshatra_lord_tamil="கேது"
        ),
        PlanetaryPosition(
            planet="Jupiter",
            planet_tamil="குரு",
            longitude=162.434,
            sign=6,
            sign_name="Virgo",
            sign_name_tamil="கன்னி",
            house=6,
            retrograde=True,
            longitude_dms="162:26:04",
            longitude_in_sign=12.434,
            longitude_in_sign_dms="12:26:04",
            nakshatra=13,
            nakshatra_name="Hasta",
            nakshatra_name_tamil="ஹஸ்தம்",
            nakshatra_pada=1,
            nakshatra_lord="Moon",
            nakshatra_lord_tamil="சந்திரன்"
        ),
        PlanetaryPosition(
            planet="Venus",
            planet_tamil="சுக்ரன்",
            longitude=341.194,
            sign=12,
            sign_name="Pisces",
            sign_name_tamil="மீனம்",
            house=12,
            retrograde=False,
            longitude_dms="341:11:38",
            longitude_in_sign=11.194,
            longitude_in_sign_dms="11:11:38",
            nakshatra=26,
            nakshatra_name="Uttarabhadra",
            nakshatra_name_tamil="உத்திரட்டாதி",
            nakshatra_pada=3,
            nakshatra_lord="Saturn",
            nakshatra_lord_tamil="சனி"
        ),
        PlanetaryPosition(
            planet="Saturn",
            planet_tamil="சனி",
            longitude=305.245,
            sign=11,
            sign_name="Aquarius",
            sign_name_tamil="கும்பம்",
            house=11,
            retrograde=False,
            longitude_dms="305:14:43",
            longitude_in_sign=5.245,
            longitude_in_sign_dms="5:14:43",
            nakshatra=23,
            nakshatra_name="Dhanishta",
            nakshatra_name_tamil="அவிட்டம்",
            nakshatra_pada=4,
            nakshatra_lord="Mars",
            nakshatra_lord_tamil="செவ்வாய்"
        ),
        PlanetaryPosition(
            planet="Rahu",
            planet_tamil="ராகு",
            longitude=230.318,
            sign=8,
            sign_name="Scorpio",
            sign_name_tamil="விருச்சிகம்",
            house=8,
            retrograde=True,
            longitude_dms="230:19:05",
            longitude_in_sign=20.318,
            longitude_in_sign_dms="20:19:05",
            nakshatra=18,
            nakshatra_name="Jyeshta",
            nakshatra_name_tamil="கேட்டை",
            nakshatra_pada=2,
            nakshatra_lord="Mercury",
            nakshatra_lord_tamil="புதன்"
        ),
        PlanetaryPosition(
            planet="Ketu",
            planet_tamil="கேது",
            longitude=50.318,
            sign=2,
            sign_name="Taurus",
            sign_name_tamil="ரிஷபம்",
            house=2,
            retrograde=True,
            longitude_dms="50:19:05",
            longitude_in_sign=20.318,
            longitude_in_sign_dms="20:19:05",
            nakshatra=4,
            nakshatra_name="Rohini",
            nakshatra_name_tamil="ரோஹிணி",
            nakshatra_pada=4,
            nakshatra_lord="Moon",
            nakshatra_lord_tamil="சந்திரன்"
        ),
    ]
    
    # Rasi chart (houses 1-12 with planets)
    rasi_houses = {
        1: ["லக்", "புதன்"],
        2: ["கேது"],
        3: [],
        4: ["செவ்வாய்"],
        5: ["சந்திரன்"],
        6: ["குரு"],
        7: [],
        8: ["ராகு"],
        9: ["சூரியன்"],
        10: [],
        11: ["சனி"],
        12: ["சுக்ரன்"]
    }
    
    # Navamsa chart
    navamsa_houses = {
        1: ["லக்", "புதன்"],
        2: ["கேது"],
        3: [],
        4: ["செவ்வாய்"],
        5: ["சந்திரன்"],
        6: ["குரு"],
        7: [],
        8: ["ராகு"],
        9: ["சூரியன்"],
        10: [],
        11: ["சனி"],
        12: ["சுக்ரன்"]
    }
    
    rasi_chart = Chart(
        chart_type="rasi",
        houses={k: [p.replace("லக்", "Asc") if p == "லக்" else p for p in v] for k, v in rasi_houses.items()},
        houses_tamil=rasi_houses,
        ascendant_house=1
    )
    
    navamsa_chart = Chart(
        chart_type="navamsa",
        houses={k: [p.replace("லக்", "Asc") if p == "லக்" else p for p in v] for k, v in navamsa_houses.items()},
        houses_tamil=navamsa_houses,
        ascendant_house=1
    )
    
    # Dasa periods
    current_dasa = DasaPeriod(
        planet="Moon",
        planet_tamil="சந்திரன்",
        start_date=date(2025, 3, 30),
        end_date=date(2035, 3, 29),
        level="maha",
        years=10.0,
        months=0,
        days=0,
        balance_years=5,
        balance_months=11,
        balance_days=0,
        first_dasha_planet="Ketu",
        first_dasha_planet_tamil="கேது",
        next_dasa_planet="Mars",
        next_dasa_planet_tamil="செவ்வாய்",
        next_dasa_end_date="2035-03-29",
        current_bhukti_planet="Moon",
        current_bhukti_planet_tamil="சந்திரன்",
        current_bhukti_end_date="2026-01-26",
        next_bhukti_planet="Mars",
        next_bhukti_planet_tamil="செவ்வாய்",
        next_bhukti_end_date="2026-01-27"
    )
    
    dasa_periods = [current_dasa]
    
    # Create horoscope result
    horoscope = HoroscopeResult(
        system_type="Vakkiam",
        birth_details=birth_details,
        system="vakkiam",
        language="tamil",
        ascendant="Sagittarius",
        ascendant_tamil="தனுசு",
        moon_sign="Leo",
        moon_sign_tamil="சிம்மம்",
        nakshatra="Magha",
        nakshatra_tamil="மகம்",
        planetary_positions=planetary_positions,
        rasi_chart=rasi_chart,
        navamsa_chart=navamsa_chart,
        dasa_periods=dasa_periods,
        current_dasa=current_dasa,
        retrograde_planets=["Jupiter", "Rahu", "Ketu"],
        retrograde_planets_tamil=["குரு", "ராகு", "கேது"],
        bhava_maruthal={"Moon": 8, "Mercury": 4},
        bhava_maruthal_tamil={"சந்திரன்": 8, "புதன்": 4},
        sunrise_time="06:00",
        sunset_time="18:00",
        paksha="Krishna",
        tithi="Ekadashi",
        tithi_tamil="ஏகாதசி",
        yoga="Vishkumbha",
        yoga_tamil="விஷ்கும்ப",
        karana="Bava",
        karana_tamil="பவ",
        ayanamsa="23° 51'",
        tamil_month="வைகாசி",
        tamil_day=15,
        tamil_year=2025
    )
    
    return horoscope

def main():
    """Main function to generate PDF"""
    print("Creating test horoscope data...")
    horoscope = create_test_horoscope()
    
    print("Generating PDF...")
    try:
        personal_details = {
            "name": horoscope.birth_details.name,
            "lagnam": horoscope.ascendant_tamil,
            "star_pada": horoscope.nakshatra_tamil,
            "rasi": horoscope.moon_sign_tamil,
            "date": horoscope.birth_details.date_of_birth.strftime("%d/%m/%Y"),
            "time": horoscope.birth_details.time_of_birth.strftime("%H:%M:%S"),
            "place": horoscope.birth_details.place_of_birth,
            "longitude": f"{horoscope.birth_details.longitude}°",
            "latitude": f"{horoscope.birth_details.latitude}°",
            "timezone": horoscope.birth_details.timezone,
            "time_correction": str(horoscope.birth_details.time_correction),
        }
        
        pdf_bytes = generate_horoscope_pdf(horoscope, personal_details, "vakkiam")
        
        # Save PDF to file
        output_path = Path(__file__).parent / "test_horoscope.pdf"
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
        
        print(f"✓ PDF generated successfully!")
        print(f"✓ Saved to: {output_path.absolute()}")
        print(f"✓ File size: {len(pdf_bytes)} bytes")
        
    except Exception as e:
        print(f"✗ Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

