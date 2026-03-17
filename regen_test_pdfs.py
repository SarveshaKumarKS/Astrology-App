"""
Regenerate horoscope PDFs for the four canonical test cases
using the current backend logic (Vakkiam + Thirukkanitham).

Usage (from project root):

    python regen_test_pdfs.py

Outputs files into the existing test_pdfs/ folder:
    - horoscope_Raj_19890406_vakkiam.pdf
    - horoscope_Raj_19890406_thirukkanitham.pdf
    - horoscope_case1_20000114_vakkiam.pdf
    - horoscope_case1_20000114_thirukkanitham.pdf
    - horoscope_Kishan_19961215_vakkiam.pdf
    - horoscope_Kishan_19961215_thirukkanitham.pdf
    - horoscope_case2_19901214_vakkiam.pdf
    - horoscope_case2_19901214_thirukkanitham.pdf
"""

from __future__ import annotations

import os
from datetime import date, time
from pathlib import Path

import sys


def main() -> None:
    # Ensure backend is on path
    root = Path(__file__).parent
    backend_dir = root / "backend"
    sys.path.insert(0, str(backend_dir))

    from astrology.vakkiam_system import VakkiamCalculator
    from astrology.thirukkanitham_system import ThirukkanithamCalculator
    from astrology.models import BirthDetails
    from astrology.pdf_generator import generate_horoscope_pdf

    cases = [
        ("Raj", date(1989, 4, 6), time(18, 40, 0), "Palayankottai", 8.5706, 77.9000),
        ("case1", date(2000, 1, 14), time(22, 48, 0), "Salem", 11.6643, 78.1460),
        ("Kishan", date(1996, 12, 15), time(23, 37, 0), "Trichy", 10.7905, 78.7047),
        ("case2", date(1990, 12, 14), time(22, 20, 0), "Salem", 11.6643, 78.1460),
    ]

    out_dir = root / "test_pdfs"
    out_dir.mkdir(exist_ok=True)

    calculators = [
        ("vakkiam", VakkiamCalculator),
        ("thirukkanitham", ThirukkanithamCalculator),
    ]

    print(f"Writing PDFs to: {out_dir}")

    for name, dob, tob, place, lat, lon in cases:
        birth = BirthDetails(
            name=name,
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

        for system_name, CalcCls in calculators:
            calc = CalcCls()
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

            pdf_bytes = generate_horoscope_pdf(h, personal_details, system_name)
            filename = f"horoscope_{name}_{dob.strftime('%Y%m%d')}_{system_name}.pdf"
            out_path = out_dir / filename
            out_path.write_bytes(pdf_bytes)

            print(
                f"- {filename} | size={len(pdf_bytes)} bytes | "
                f"paksha={h.paksha_tamil} | "
                f"tamil_date={h.tamil_month} {h.tamil_day}, {h.tamil_year_name}"
            )


if __name__ == "__main__":
    main()

