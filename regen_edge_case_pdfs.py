"""
Generate horoscope PDFs for the 10 canonical edge cases using the
modified Vakkiam system (VakyaTableEngine with Rahu carry-propagation,
Sun kshepa+manda, and dynamic Tamil month boundary fixes).

Edge cases covered:
  01 Tamil New Year Day        — day 1, Sun resets to Aries
  02 Pre-sunrise UTC rollover  — 1:30 AM IST falls on previous UTC day
  03 Tamil month boundary      — first day of Aani (month 3)
  04 Last day of Tamil year    — ~365 days in
  05 Leap day                  — Feb 29 in a leap century year
  06 Pre-Fourier (1963)        — before calibration range, constant bija only
  07 Post-Fourier (2026)       — after calibration range, constant bija only
  08 High latitude 30.7°N      — Chandigarh, summer solstice
  09 Low latitude 8.1°N        — Kanyakumari, winter solstice
  10 Historical midnight       — 15/08/1947 12 AM IST, Tamil day = Aug 14

Usage (from project root):

    python regen_edge_case_pdfs.py

Outputs files into test_pdfs/edge_cases/.
"""

from __future__ import annotations

import sys
from datetime import date, time
from pathlib import Path


def main() -> None:
    root = Path(__file__).parent
    backend_dir = root / "backend"
    sys.path.insert(0, str(backend_dir))

    from astrology.vakkiam_system import VakkiamCalculator
    from astrology.models import BirthDetails
    from astrology.pdf_generator import generate_horoscope_pdf

    # (label, dob, tob, place, lat, lon, edge case description)
    cases = [
        ("edge01_tamil_new_year", date(1985, 4, 14), time(6, 0, 0),
         "Chennai", 13.0827, 80.2707, "Tamil New Year Day"),
        ("edge02_presunrise_utc", date(1995, 1, 6), time(1, 30, 0),
         "Salem", 11.6643, 78.1460, "Pre-sunrise UTC rollover"),
        ("edge03_month_boundary", date(2010, 6, 15), time(9, 0, 0),
         "Trichy", 10.7905, 78.7047, "Tamil month boundary (Aani 1)"),
        ("edge04_year_end", date(2019, 4, 13), time(20, 0, 0),
         "Coimbatore", 11.0168, 76.9558, "Last day of Tamil year"),
        ("edge05_leap_day", date(2000, 2, 29), time(15, 30, 0),
         "Bangalore", 12.9716, 77.5946, "Leap day (century leap year)"),
        ("edge06_pre_fourier", date(1963, 11, 15), time(16, 0, 0),
         "Madurai", 9.9252, 78.1198, "Pre-Fourier calibration (1963)"),
        ("edge07_post_fourier", date(2026, 6, 6), time(12, 0, 0),
         "Delhi", 28.6139, 77.2090, "Post-Fourier calibration (2026)"),
        ("edge08_high_latitude", date(2005, 6, 21), time(7, 0, 0),
         "Chandigarh", 30.7333, 76.7794, "High latitude 30.7N, summer solstice"),
        ("edge09_low_latitude", date(2015, 12, 22), time(17, 30, 0),
         "Kanyakumari", 8.0883, 77.5385, "Low latitude 8.1N, winter solstice"),
        ("edge10_midnight_1947", date(1947, 8, 15), time(0, 0, 0),
         "Bombay", 19.0760, 72.8777, "Historical midnight, pre-sunrise"),
    ]

    out_dir = root / "test_pdfs" / "edge_cases"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Writing PDFs to: {out_dir}")

    for label, dob, tob, place, lat, lon, desc in cases:
        birth = BirthDetails(
            name=label,
            date_of_birth=dob,
            time_of_birth=tob,
            place_of_birth=place,
            latitude=lat,
            longitude=lon,
            timezone="IST",
            time_correction=0,
            mother_name="Mother",
            father_name="Father",
        )

        calc = VakkiamCalculator()
        h = calc.generate_horoscope(birth, "tamil")

        personal_details = {
            "name": birth.name,
            "lagnam": h.ascendant_tamil,
            "star_pada": h.nakshatra_tamil,
            "rasi": h.moon_sign_tamil,
            "date": dob.strftime("%d/%m/%Y"),
            "time": tob.strftime("%H:%M:%S"),
            "place": place,
            "longitude": str(lon),
            "latitude": str(lat),
            "timezone": birth.timezone,
            "time_correction": str(birth.time_correction),
        }

        pdf_bytes = generate_horoscope_pdf(h, personal_details, "vakkiam")
        filename = f"horoscope_{label}_{dob.strftime('%Y%m%d')}_vakkiam.pdf"
        out_path = out_dir / filename
        out_path.write_bytes(pdf_bytes)

        sun = next((p for p in h.planetary_positions if p.planet == "Sun"), None)
        sun_str = f"{sun.longitude:.4f}" if sun else "?"
        print(
            f"- {filename} | {desc} | size={len(pdf_bytes)} bytes | "
            f"Sun={sun_str} | tamil_date={h.tamil_month} {h.tamil_day}, {h.tamil_year_name}"
        )


if __name__ == "__main__":
    main()
