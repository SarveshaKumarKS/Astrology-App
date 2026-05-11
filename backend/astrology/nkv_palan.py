"""
NKV (Nellai K. Vasanthan) Palan Prediction Engine

Rule-based analysis following the NKV system:
1. Current Saturn transit analysis from the rasi square
2. Saturn-Moon axis analysis with nakshatra lord overlay
3. Practical, karmic-focused prediction templates
"""

from datetime import date, time, timedelta
from typing import Dict, Any, List, Optional
from astrology.models import (
    HoroscopeResult, NKVPlanetaryContext, NKVPalanResult, NKVSaturnTransitResult
)
from astrology.constants import PLANET_NAMES, SIGNS, SIGNS_TAMIL

DUSTHANA_HOUSES = {6, 8, 12}
UPACHAYA_HOUSES = {3, 6, 10, 11}
MARAKA_HOUSES = {2, 7}

SATURN_ASPECTS = (3, 7, 10)

HOUSE_TRANSIT_TOPICS_TA: Dict[int, str] = {
    1: "உடல் நலம், தன்மை, மரியாதை, வாழ்க்கை திசை",
    2: "குடும்பம், பணம், பேச்சு, ஆவணங்கள்",
    3: "தைரியம், முயற்சி, சகோதரர்கள், குறுகிய பயணம்",
    4: "வீடு, வாகனம், தாய், மன அமைதி",
    5: "பிள்ளைகள், கல்வி, புத்தி, பூர்வ புண்ணியம்",
    6: "கடன், நோய், எதிரிகள், வேலை அழுத்தம்",
    7: "திருமணம், துணைவர், ஒப்பந்தம், வெளிப்படையான உறவுகள்",
    8: "காப்பீடு, ஆவணங்கள், மறைவு விஷயம், திடீர் மாற்றம்",
    9: "பாக்கியம், தந்தை, குரு, நீண்ட பயணம்",
    10: "தொழில், பதவி, பொறுப்பு, பொது நிலை",
    11: "லாபம், நண்பர்கள், மூத்த சகோதரர், ஆசை நிறைவு",
    12: "செலவு, வெளிநாடு, தூக்கம், ஆன்மீகம்",
}

PLANET_TRANSIT_RESULTS_TA: Dict[str, str] = {
    "Ascendant": "லக்னத்தை சனி பார்க்கும் போது உடல், பெயர், வாழ்க்கை முன்னேற்றத்தில் பொறுப்பு மற்றும் தாமதம் அதிகரிக்கும்.",
    "Sun": "சூரியனை சனி பார்க்கும் போது அதிகாரம், தந்தை, அரசு சம்பந்தமான விஷயங்களில் பொறுமை தேவை.",
    "Moon": "சந்திரனை சனி பார்க்கும் போது மன அழுத்தம், கவலை, தூக்கம், உணர்ச்சி கட்டுப்பாடு முக்கியமாகும்.",
    "Mars": "செவ்வாயை சனி பார்க்கும் போது நிலம், சகோதரர், கோபம், விபத்து விஷயங்களில் கவனம் தேவை.",
    "Mercury": "புதனை சனி பார்க்கும் போது ஆவணம், கல்வி, கணக்கு, பேச்சு, வியாபார முடிவுகள் மெதுவாக நகரும்.",
    "Jupiter": "குருவை சனி பார்க்கும் போது குரு, சட்டம், பிள்ளை, கல்வி, ஆலோசனை விஷயங்களில் கட்டுப்பாடு வரும்.",
    "Venus": "சுக்ரனை சனி பார்க்கும் போது திருமணம், உறவு, வசதி, வாகனம், கலை விஷயங்களில் தாமதம் அல்லது பொறுப்பு வரும்.",
    "Saturn": "சனி தன் தாக்கத்தை வலுப்படுத்துவதால் கடமை, உழைப்பு, நீண்டகால முடிவுகள் முக்கியமாகும்.",
}


def classify_house(house: int) -> str:
    if house in DUSTHANA_HOUSES:
        return "Dusthana"
    if house in MARAKA_HOUSES:
        return "Maraka"
    if house in UPACHAYA_HOUSES:
        return "Upachaya"
    return "Neutral"


def classify_house_tamil(house_type: str) -> str:
    mapping = {
        "Dusthana": "துஷ்டானம்",
        "Maraka": "மாரகம்",
        "Upachaya": "உபசயம்",
        "Neutral": "நடுநிலை",
    }
    return mapping.get(house_type, house_type)


def _planet_position_lookup(horoscope: HoroscopeResult) -> Dict[str, Any]:
    """Build a quick lookup of planet -> {sign, house, nakshatra, nakshatra_lord}."""
    lookup: Dict[str, Any] = {}
    for pp in horoscope.planetary_positions:
        if pp.planet == "Ascendant":
            continue
        lookup[pp.planet] = {
            "sign": pp.sign,
            "sign_name": pp.sign_name,
            "sign_name_tamil": pp.sign_name_tamil,
            "house": pp.house,
            "nakshatra": pp.nakshatra,
            "nakshatra_name": pp.nakshatra_name,
            "nakshatra_lord": pp.nakshatra_lord or "",
        }
    return lookup


def _sign_to_house(sign: int, ascendant_sign: int) -> int:
    """Whole-sign house from lagna sign."""
    return ((sign - ascendant_sign) % 12) + 1


def _saturn_aspected_signs(saturn_sign: int) -> List[Dict[str, int]]:
    """Saturn special aspects: 3rd, 7th, and 10th from Saturn's current sign."""
    return [
        {
            "aspect": aspect,
            "sign": ((saturn_sign - 1 + aspect - 1) % 12) + 1,
        }
        for aspect in SATURN_ASPECTS
    ]


def _format_planets_tamil(planets: List[str]) -> str:
    return ", ".join(PLANET_NAMES.get(planet, planet) for planet in planets)


def _current_positions_for_system(calculator: Any, horoscope: HoroscopeResult, as_of: date) -> Dict[str, Dict[str, Any]]:
    """Calculate current positions using the same calculator family as the report."""
    noon = time(12, 0)
    birth = horoscope.birth_details
    system_name = getattr(calculator, "system_name", horoscope.system).lower()

    if system_name == "vakkiam":
        jd = calculator.get_julian_day_lmt(as_of, noon, birth.longitude)
        positions = calculator.calculate_planetary_positions_vakya(as_of, noon, jd)
        prev_jd = calculator.get_julian_day_lmt(as_of - timedelta(days=1), noon, birth.longitude)
        prev_positions = calculator.calculate_planetary_positions_vakya(as_of - timedelta(days=1), noon, prev_jd)
    else:
        tz_offset = calculator._parse_timezone(birth.timezone)
        jd = calculator.get_julian_day(as_of, noon, tz_offset)
        positions = calculator.calculate_planetary_positions_thirukkanitham(jd, birth.latitude, birth.longitude)
        prev_jd = calculator.get_julian_day(as_of - timedelta(days=1), noon, tz_offset)
        prev_positions = calculator.calculate_planetary_positions_thirukkanitham(prev_jd, birth.latitude, birth.longitude)

    for planet, position in positions.items():
        if "speed" in position:
            position["retrograde"] = position["speed"] < 0
            continue
        prev = prev_positions.get(planet, {}).get("longitude", position["longitude"])
        curr = position["longitude"]
        position["retrograde"] = ((curr - prev + 540) % 360 - 180) < 0

    return positions


def compute_saturn_transit_result(
    horoscope: HoroscopeResult,
    calculator: Any,
    as_of: Optional[date] = None,
) -> NKVSaturnTransitResult:
    """Build the handwritten-note style current Saturn transit result."""
    report_date = as_of or date.today()
    positions = _current_positions_for_system(calculator, horoscope, report_date)
    saturn = positions["Saturn"]
    saturn_sign = saturn["sign"]
    ascendant = next((p for p in horoscope.planetary_positions if p.planet == "Ascendant"), None)
    ascendant_sign = ascendant.sign if ascendant else 1
    saturn_house = _sign_to_house(saturn_sign, ascendant_sign)

    natal_by_sign: Dict[int, List[str]] = {sign: [] for sign in range(1, 13)}
    for planet_position in horoscope.planetary_positions:
        natal_by_sign.setdefault(planet_position.sign, []).append(planet_position.planet)

    affected_houses: List[Dict[str, Any]] = []
    result_lines: List[str] = []
    aspect_parts: List[str] = []

    for aspect_data in _saturn_aspected_signs(saturn_sign):
        aspect = aspect_data["aspect"]
        target_sign = aspect_data["sign"]
        target_house = _sign_to_house(target_sign, ascendant_sign)
        planets = [
            planet for planet in natal_by_sign.get(target_sign, [])
            if planet in PLANET_TRANSIT_RESULTS_TA
        ]
        planets_tamil = _format_planets_tamil(planets) if planets else "கிரகம் இல்லை"
        topics = HOUSE_TRANSIT_TOPICS_TA[target_house]

        aspect_parts.append(
            f"{aspect}ஆம் பார்வை {SIGNS_TAMIL[target_sign]} ({target_house}ஆம் இடம்)"
        )
        affected_houses.append({
            "aspect": aspect,
            "sign": target_sign,
            "sign_tamil": SIGNS_TAMIL[target_sign],
            "house": target_house,
            "topics_tamil": topics,
            "planets": planets,
            "planets_tamil": planets_tamil,
        })

        result_lines.append(
            f"சனியின் {aspect}ஆம் பார்வை {target_house}ஆம் இடமான {SIGNS_TAMIL[target_sign]}-ஐ பார்க்கிறது; "
            f"இதனால் {topics} சம்பந்தமான விஷயங்களில் தாமதம், பொறுப்பு, கவனம் தேவை."
        )
        for planet in planets:
            planet_result = PLANET_TRANSIT_RESULTS_TA.get(planet)
            if planet_result:
                result_lines.append(planet_result)

    retro_text = "வக்ரம்" if saturn.get("retrograde") else "நேர்கதி"
    placement = (
        f"தற்போதைய சனி {SIGNS_TAMIL[saturn_sign]} ராசியில், ஜாதக லக்கினத்திலிருந்து "
        f"{saturn_house}ஆம் இடத்தில் உள்ளது ({retro_text})."
    )

    return NKVSaturnTransitResult(
        report_date=report_date.isoformat(),
        current_saturn_sign=SIGNS[saturn_sign],
        current_saturn_sign_tamil=SIGNS_TAMIL[saturn_sign],
        current_saturn_house=saturn_house,
        current_saturn_retrograde=bool(saturn.get("retrograde")),
        placement_tamil=placement,
        aspect_summary_tamil="; ".join(aspect_parts),
        affected_houses=affected_houses,
        result_lines_tamil=result_lines,
    )


HOUSE_ORDINAL = {
    1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th", 6: "6th",
    7: "7th", 8: "8th", 9: "9th", 10: "10th", 11: "11th", 12: "12th",
}


def _saturn_moon_aspect(saturn_house: int, moon_house: int) -> str:
    diff = abs(saturn_house - moon_house)
    if diff > 6:
        diff = 12 - diff
    if diff == 0:
        return "Conjunction"
    if diff == 6:
        return "Opposition"
    if diff in (3, 9 % 6):
        return "Square"
    return "Other"


def _saturn_moon_aspect_tamil(aspect: str) -> str:
    mapping = {
        "Conjunction": "சேர்க்கை (Conjunction)",
        "Opposition": "எதிர்நிலை (Opposition)",
        "Square": "சதுரம் (Square)",
        "Other": "பிற கோண நிலை",
    }
    return mapping.get(aspect, aspect)


# ---------------------------------------------------------------------------
# compute_nkv_context  -- extract structured NKV payload from HoroscopeResult
# ---------------------------------------------------------------------------

def compute_nkv_context(horoscope: HoroscopeResult) -> Dict[str, Any]:
    lookup = _planet_position_lookup(horoscope)

    saturn = lookup.get("Saturn", {})
    moon = lookup.get("Moon", {})

    saturn_house = saturn.get("house", 1)
    moon_house = moon.get("house", 1)

    aspect = _saturn_moon_aspect(saturn_house, moon_house)

    moon_nk_lord = moon.get("nakshatra_lord", "")

    def _build_ctx(planet_name: str) -> NKVPlanetaryContext:
        p = lookup.get(planet_name, {})
        h = p.get("house", 1)
        ht = classify_house(h)
        return NKVPlanetaryContext(
            planet=planet_name,
            planet_tamil=PLANET_NAMES.get(planet_name, planet_name),
            sign=p.get("sign_name", SIGNS.get(p.get("sign", 1), "")),
            sign_tamil=p.get("sign_name_tamil", SIGNS_TAMIL.get(p.get("sign", 1), "")),
            house=h,
            house_type=ht,
            house_type_tamil=classify_house_tamil(ht),
        )

    planetary_context = {
        "Saturn": _build_ctx("Saturn"),
        "Moon": _build_ctx("Moon"),
    }

    return {
        "birth_summary": {
            "Lagna": horoscope.ascendant,
            "Lagna_Tamil": horoscope.ascendant_tamil,
            "Moon_Sign": horoscope.moon_sign,
            "Moon_Sign_Tamil": horoscope.moon_sign_tamil,
            "Moon_Nakshatra": horoscope.nakshatra,
            "Moon_Nakshatra_Tamil": horoscope.nakshatra_tamil,
            "Moon_Star_Lord": moon_nk_lord,
            "Moon_Star_Lord_Tamil": PLANET_NAMES.get(moon_nk_lord, moon_nk_lord),
        },
        "planetary_context": planetary_context,
        "saturn_house": saturn_house,
        "moon_house": moon_house,
        "saturn_moon_aspect": aspect,
        "saturn_moon_aspect_tamil": _saturn_moon_aspect_tamil(aspect),
        "moon_nakshatra_lord": moon_nk_lord,
    }


# ---------------------------------------------------------------------------
# Prediction Templates
# ---------------------------------------------------------------------------

# ---- Section 2: Mental Filter (Saturn-Moon) ----

_SATMOON_EN: Dict[str, str] = {
    "Conjunction": (
        "Saturn and Moon occupy the same house, forming a Vairagya Yoga pattern. "
        "This grants emotional restraint and a serious, disciplined temperament from a young age. "
        "You process feelings slowly but deeply. Early life may feel heavy with responsibility, "
        "but this conjunction builds an unshakeable inner core. Middle age onward brings "
        "the harvest of patience—material stability and earned respect."
    ),
    "Opposition": (
        "Saturn and Moon face each other across the chart, creating a Dharma Patience axis. "
        "Partnerships and emotional fulfilment experience delays, but these are not denials—"
        "they are cosmic quality-control. The NKV reading: every relationship that survives "
        "Saturn's test becomes a pillar of your life. Expect the most meaningful bonds "
        "to form after age 30."
    ),
    "Square": (
        "Saturn and Moon are in a square aspect, creating a Peace/Partner tension pattern. "
        "There is friction between your need for emotional security (Moon) and the demands "
        "of duty and discipline (Saturn). This aspect sharpens your decision-making under "
        "pressure. The NKV principle: the tension is productive—it prevents complacency "
        "and pushes you toward earned achievements rather than inherited comfort."
    ),
    "Other": (
        "Saturn and Moon are not in a major aspect (conjunction, opposition, or square), "
        "suggesting the mental filter operates with moderate intensity. Saturn's discipline "
        "influences your emotional world indirectly. The NKV view: you have more freedom in "
        "how you process emotions, but must consciously cultivate Saturn's structure to "
        "avoid scattered mental energy."
    ),
}

_SATMOON_TA: Dict[str, str] = {
    "Conjunction": (
        "சனியும் சந்திரனும் ஒரே வீட்டில் இருப்பதால், வைராக்ய யோகம் அமைகிறது. "
        "இது இளம் வயதிலிருந்தே உணர்ச்சி கட்டுப்பாடு மற்றும் தீவிரமான, ஒழுக்கமான "
        "குணத்தை வழங்குகிறது. நீங்கள் உணர்வுகளை மெதுவாக ஆனால் ஆழமாக செயலாக்குகிறீர்கள். "
        "ஆரம்ப வாழ்க்கை பொறுப்புடன் கனமாக உணரலாம், ஆனால் இந்த சேர்க்கை அசைக்க "
        "முடியாத உள்ளார்ந்த வலிமையை உருவாக்குகிறது. நடுத்தர வயதிலிருந்து பொறுமையின் "
        "அறுவடை வரும்—பொருள் நிலைத்தன்மை மற்றும் சம்பாதித்த மரியாதை."
    ),
    "Opposition": (
        "சனியும் சந்திரனும் ஜாதகத்தில் எதிர் எதிராக இருப்பதால், தர்ம பொறுமை அச்சு "
        "உருவாகிறது. கூட்டாண்மை மற்றும் உணர்ச்சி நிறைவு தாமதமாகும், ஆனால் இவை "
        "மறுப்புகள் அல்ல—அவை பிரபஞ்ச தரக் கட்டுப்பாடு. NKV வாசிப்பு: சனியின் "
        "சோதனையில் தப்பிய ஒவ்வொரு உறவும் உங்கள் வாழ்க்கையின் தூணாக மாறும். "
        "30 வயதுக்குப் பிறகு மிகவும் அர்த்தமுள்ள பிணைப்புகள் உருவாகும்."
    ),
    "Square": (
        "சனியும் சந்திரனும் சதுர கோணத்தில் இருப்பதால், அமைதி/துணை பதற்ற முறை "
        "உருவாகிறது. உணர்ச்சி பாதுகாப்பு (சந்திரன்) மற்றும் கடமை ஒழுக்கத்தின் "
        "கோரிக்கைகள் (சனி) இடையே உராய்வு உள்ளது. இந்த கோணம் அழுத்தத்தின் கீழ் "
        "உங்கள் முடிவெடுக்கும் திறனை கூர்மையாக்குகிறது. NKV கொள்கை: பதற்றம் "
        "உற்பத்தியானது—இது தன்னிறைவைத் தடுக்கிறது மற்றும் பரம்பரை சுகத்திற்கு "
        "பதிலாக சம்பாதித்த சாதனைகளை நோக்கி உங்களைத் தள்ளுகிறது."
    ),
    "Other": (
        "சனியும் சந்திரனும் பெரிய கோணத்தில் (சேர்க்கை, எதிர்நிலை அல்லது சதுரம்) "
        "இல்லை, மன வடிகட்டி மிதமான தீவிரத்துடன் செயல்படுகிறது. சனியின் ஒழுக்கம் "
        "உங்கள் உணர்ச்சி உலகை மறைமுகமாக பாதிக்கிறது. NKV பார்வை: உணர்வுகளை "
        "எவ்வாறு செயலாக்குவது என்பதில் உங்களுக்கு அதிக சுதந்திரம் உள்ளது, ஆனால் "
        "சிதறிய மன ஆற்றலைத் தவிர்க்க சனியின் கட்டமைப்பை உணர்வுபூர்வமாக "
        "வளர்க்க வேண்டும்."
    ),
}

# Diamond Mind overlay when Moon's nakshatra lord is Saturn
_DIAMOND_MIND_EN = (
    " Your Moon's nakshatra lord is {lord}, placing the Moon under a Saturn star. "
    "The NKV system calls this the \"Diamond Mind\"—hardened by responsibility but capable "
    "of great beauty. Expect delays in early life that turn into solid foundations in middle age."
)
_DIAMOND_MIND_TA = (
    " உங்கள் சந்திரனின் நட்சத்திர அதிபதி {lord} ஆவார், சந்திரனை சனி நட்சத்திரத்தின் "
    "கீழ் வைக்கிறது. NKV அமைப்பு இதை \"வைர மனம்\" என்று அழைக்கிறது—பொறுப்பால் "
    "கடினப்படுத்தப்பட்டது ஆனால் பெரும் அழகை உருவாக்கும் திறன் கொண்டது. ஆரம்ப "
    "வாழ்க்கையில் தாமதங்கள் நடுத்தர வயதில் உறுதியான அடித்தளமாக மாறும்."
)

# ---------------------------------------------------------------------------
# generate_nkv_predictions  -- assemble predictions from context
# ---------------------------------------------------------------------------

def generate_nkv_predictions(
    context: Dict[str, Any],
    saturn_transit: Optional[NKVSaturnTransitResult] = None,
) -> NKVPalanResult:
    aspect = context["saturn_moon_aspect"]
    s2_en = _SATMOON_EN.get(aspect, _SATMOON_EN["Other"])
    s2_ta = _SATMOON_TA.get(aspect, _SATMOON_TA["Other"])

    nk_lord = context["moon_nakshatra_lord"]
    if nk_lord == "Saturn":
        lord_ta = PLANET_NAMES.get(nk_lord, nk_lord)
        s2_en += _DIAMOND_MIND_EN.format(lord=nk_lord)
        s2_ta += _DIAMOND_MIND_TA.format(lord=lord_ta)

    saturn_ctx = context["planetary_context"]["Saturn"]
    moon_ctx = context["planetary_context"]["Moon"]

    sat_h = context["saturn_house"]
    moon_h = context["moon_house"]
    s2_placement_en = (
        f"Saturn in {saturn_ctx.sign} ({HOUSE_ORDINAL[sat_h]} house) — "
        f"Moon in {moon_ctx.sign} ({HOUSE_ORDINAL[moon_h]} house) — "
        f"Aspect: {aspect}"
    )
    s2_placement_ta = (
        f"சனி {saturn_ctx.sign_tamil}-ல் ({sat_h}ஆம் இடம்) — "
        f"சந்திரன் {moon_ctx.sign_tamil}-ல் ({moon_h}ஆம் இடம்) — "
        f"கோணம்: {context['saturn_moon_aspect_tamil']}"
    )

    return NKVPalanResult(
        birth_summary=context["birth_summary"],
        planetary_context=context["planetary_context"],
        saturn_moon_aspect=context["saturn_moon_aspect"],
        saturn_moon_aspect_tamil=context["saturn_moon_aspect_tamil"],
        section2_title="The Mental Filter (Saturn-Moon)",
        section2_title_tamil="மன வடிகட்டி (சனி-சந்திரன்)",
        section2_placement=s2_placement_en,
        section2_placement_tamil=s2_placement_ta,
        section2_palan=s2_en,
        section2_palan_tamil=s2_ta,
        saturn_transit=saturn_transit,
    )
