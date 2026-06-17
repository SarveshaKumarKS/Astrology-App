"""
Generate horoscope PDFs for the 9 uploaded test cases, named by date.

Output: test_pdfs/by_date/<DD-MM-YYYY>_<Place>.pdf
"""

from __future__ import annotations

import sys
from datetime import date, time
from pathlib import Path


def main() -> None:
    root = Path(__file__).parent
    sys.path.insert(0, str(root / "backend"))

    from astrology.vakkiam_system import VakkiamCalculator
    from astrology.models import BirthDetails
    from astrology.pdf_generator import generate_horoscope_pdf

    cases = [
        (date(1985,  4, 14), time( 6,  0), "Chennai",     13.0827,  80.2707),
        (date(1995,  1,  6), time( 1, 30), "Salem",       11.6643,  78.1850),
        (date(2010,  6, 15), time( 9,  0), "Trichy",      10.7905,  78.7047),
        (date(2019,  4, 13), time(20,  0), "Coimbatore",  11.0168,  76.9558),
        (date(1963, 11, 15), time(16,  0), "Madurai",      9.9252,  78.1198),
        (date(2026,  6,  6), time(12,  0), "Delhi",       28.6139,  77.2090),
        (date(2005,  6, 21), time( 7,  0), "Chandigarh",  30.7333,  76.7794),
        (date(2015, 12, 22), time(17, 30), "Kanyakumari",  8.0883,  77.5385),
        (date(1947,  8, 15), time( 0,  0), "Bombay",      19.0760,  72.8777),
    ]

    out_dir = root / "test_pdfs" / "by_date"
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Writing PDFs to: {out_dir}\n")

    calc = VakkiamCalculator()

    for dob, tob, place, lat, lon in cases:
        filename = f"{dob.strftime('%d-%m-%Y')}_{place}.pdf"
        birth = BirthDetails(
            name=place,
            date_of_birth=dob,
            time_of_birth=tob,
            place_of_birth=place,
            latitude=lat,
            longitude=lon,
            timezone="IST",
            time_correction=0,
            mother_name="",
            father_name="",
        )

        h = calc.generate_horoscope(birth, "tamil")

        personal_details = {
            "name": place,
            "lagnam": h.ascendant_tamil,
            "star_pada": h.nakshatra_tamil,
            "rasi": h.moon_sign_tamil,
            "date": dob.strftime("%d/%m/%Y"),
            "time": tob.strftime("%H:%M:%S"),
            "place": place,
            "longitude": str(lon),
            "latitude": str(lat),
            "timezone": "IST",
            "time_correction": "0",
        }

        pdf_bytes = generate_horoscope_pdf(h, personal_details, "vakkiam")
        out_path = out_dir / filename
        out_path.write_bytes(pdf_bytes)

        sun = next((p for p in h.planetary_positions if p.planet == "Sun"), None)
        moon = next((p for p in h.planetary_positions if p.planet == "Moon"), None)
        print(f"  {filename}  ({len(pdf_bytes):,} bytes)")
        if sun:
            print(f"    Sun  {sun.longitude:.4f}°  {sun.nakshatra_name} p{sun.nakshatra_pada}")
        if moon:
            print(f"    Moon {moon.longitude:.4f}°  {moon.nakshatra_name} p{moon.nakshatra_pada}")


if __name__ == "__main__":
    main()
