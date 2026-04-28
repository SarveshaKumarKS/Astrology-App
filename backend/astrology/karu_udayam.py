import json
import logging
import re
from datetime import timedelta, date
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from astrology.models import BirthDetails, Chart

logger = logging.getLogger(__name__)

_LOOKUP_PATH = Path(__file__).parent / "data" / "karu_udayam_lookup.json"
_OFFSET_DAYS = 300
_MAX_BACKWARD_SEARCH_DAYS = 420

_MONTH_ALIASES = {
    "chithirai": "சித்திரை",
    "chitirai": "சித்திரை",
    "chitthirai": "சித்திரை",
    "chihirai": "சித்திரை",
    "vaikasi": "வைகாசி",
    "vaigasi": "வைகாசி",
    "aani": "ஆனி",
    "ani": "ஆனி",
    "aadi": "ஆடி",
    "adi": "ஆடி",
    "aavani": "ஆவணி",
    "avani": "ஆவணி",
    "purattasi": "புரட்டாசி",
    "puratassi": "புரட்டாசி",
    "aippasi": "ஐப்பசி",
    "aipasi": "ஐப்பசி",
    "aipassi": "ஐப்பசி",
    "karthigai": "கார்த்திகை",
    "karthikai": "கார்த்திகை",
    "karthigaii": "கார்த்திகை",
    "margazhi": "மார்கழி",
    "maarghazi": "மார்கழி",
    "maargazhi": "மார்கழி",
    "thai": "தை",
    "maasi": "மாசி",
    "masi": "மாசி",
    "panguni": "பங்குனி",
    "சித்திரை": "சித்திரை",
    "வைகாசி": "வைகாசி",
    "ஆனி": "ஆனி",
    "ஆடி": "ஆடி",
    "ஆவணி": "ஆவணி",
    "புரட்டாசி": "புரட்டாசி",
    "ஐப்பசி": "ஐப்பசி",
    "கார்த்திகை": "கார்த்திகை",
    "மார்கழி": "மார்கழி",
    "தை": "தை",
    "மாசி": "மாசி",
    "பங்குனி": "பங்குனி",
}

_LAGNA_MARKERS = {"Asc", "Lagna", "லக்", "லக்னம்"}


def _normalize_month_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z\u0B80-\u0BFF]", "", value or "").lower()
    if cleaned not in _MONTH_ALIASES:
        raise ValueError(f"Unsupported Tamil month alias: {value}")
    return _MONTH_ALIASES[cleaned]


def _parse_date_tokens(value: str) -> List[Tuple[str, int]]:
    tokens = [part.strip() for part in re.split(r"[&,]", value) if part and part.strip()]
    parsed: List[Tuple[str, int]] = []
    current_month: Optional[str] = None
    pattern = re.compile(r"([A-Za-z\u0B80-\u0BFF]+)?\s*(\d{1,2})$")
    for token in tokens:
        token = token.replace("-", " ").strip()
        match = pattern.search(token)
        if not match:
            continue
        month_raw, day_raw = match.groups()
        if month_raw:
            try:
                current_month = _normalize_month_name(month_raw)
            except ValueError:
                logger.warning("Skipping unknown month token in lookup: %s", month_raw)
                continue
        if not current_month:
            continue
        parsed.append((current_month, int(day_raw)))
    return parsed


def _load_lookup() -> Dict[Tuple[str, int], Tuple[str, int]]:
    if not _LOOKUP_PATH.exists():
        raise FileNotFoundError(f"Karu Udayam lookup file missing: {_LOOKUP_PATH}")

    rows = json.loads(_LOOKUP_PATH.read_text(encoding="utf-8"))
    lookup: Dict[Tuple[str, int], Tuple[str, int]] = {}
    for row in rows:
        karu_tokens = _parse_date_tokens(row.get("karu_udayam", ""))
        birth_tokens = _parse_date_tokens(row.get("birth_tamil_date", ""))
        if not karu_tokens:
            continue
        karu_date = karu_tokens[0]
        for birth_date in birth_tokens:
            lookup[birth_date] = karu_date
    return lookup


LOOKUP_BY_BIRTH = _load_lookup()


def get_karu_udayam_tamil_date(birth_tamil_month: str, birth_tamil_day: int) -> Optional[Tuple[str, int]]:
    try:
        month = _normalize_month_name(birth_tamil_month)
    except ValueError:
        logger.warning("Unknown Tamil birth month for Karu Udayam: %s", birth_tamil_month)
        return None
    return LOOKUP_BY_BIRTH.get((month, int(birth_tamil_day)))


def resolve_karu_udayam_gregorian_date(
    calculator,
    birth_details: BirthDetails,
    karu_tamil_month: str,
    karu_tamil_day: int,
) -> Optional[Tuple[date, int]]:
    # Infer Gregorian date from the *Tamil* Karu Udayam month/day by scanning backward
    # from the birth date. Use the calculator's full horoscope pipeline so the
    # matching Tamil date follows the same system-specific rules as the final chart.
    # The 300-day offset is used only as a cross-validation metric.
    for back in range(1, _MAX_BACKWARD_SEARCH_DAYS + 1):
        cur = birth_details.date_of_birth - timedelta(days=back)
        candidate_details = BirthDetails(
            name=birth_details.name,
            mother_name=birth_details.mother_name,
            father_name=birth_details.father_name,
            date_of_birth=cur,
            time_of_birth=birth_details.time_of_birth,
            place_of_birth=birth_details.place_of_birth,
            latitude=birth_details.latitude,
            longitude=birth_details.longitude,
            timezone=birth_details.timezone,
            time_correction=birth_details.time_correction,
        )
        candidate_horoscope = calculator.generate_horoscope(candidate_details, "tamil")
        if (
            candidate_horoscope.tamil_month == karu_tamil_month
            and candidate_horoscope.tamil_day == int(karu_tamil_day)
        ):
            diff_days = abs(back - _OFFSET_DAYS)
            return cur, diff_days

    return None


def strip_lagnam_from_chart(chart: Chart) -> Chart:
    houses = {}
    houses_tamil = {}
    for house_no, labels in chart.houses.items():
        houses[house_no] = [x for x in labels if x not in _LAGNA_MARKERS]
    for house_no, labels in chart.houses_tamil.items():
        houses_tamil[house_no] = [x for x in labels if x not in _LAGNA_MARKERS]
    return Chart(
        chart_type=chart.chart_type,
        houses=houses,
        houses_tamil=houses_tamil,
        ascendant_house=chart.ascendant_house,
        image_base64=chart.image_base64,
    )
