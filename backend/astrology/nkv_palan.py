"""
NKV (Nellai K. Vasanthan) Palan Prediction Engine

Rule-based analysis following the NKV system:
1. Lagna-based Kendra/Trikona classification
2. Rahu-Ketu axis analysis with dispositor strength
3. Saturn-Moon axis analysis with nakshatra lord overlay
4. Practical, karmic-focused prediction templates
"""

from typing import Dict, Any
from astrology.models import (
    HoroscopeResult, NKVPlanetaryContext, NKVPalanResult
)
from astrology.constants import PLANET_NAMES, SIGNS, SIGNS_TAMIL

# ---------------------------------------------------------------------------
# Sign Lord (Dispositor) mapping  -- sign number (1-12) -> ruling planet
# ---------------------------------------------------------------------------
SIGN_LORDS: Dict[int, str] = {
    1: "Mars",       # Aries
    2: "Venus",      # Taurus
    3: "Mercury",    # Gemini
    4: "Moon",       # Cancer
    5: "Sun",        # Leo
    6: "Mercury",    # Virgo
    7: "Venus",      # Libra
    8: "Mars",       # Scorpio
    9: "Jupiter",    # Sagittarius
    10: "Saturn",    # Capricorn
    11: "Saturn",    # Aquarius
    12: "Jupiter",   # Pisces
}

# Exaltation signs for each planet
EXALTATION_SIGNS: Dict[str, int] = {
    "Sun": 1,        # Aries
    "Moon": 2,       # Taurus
    "Mars": 10,      # Capricorn
    "Mercury": 6,    # Virgo
    "Jupiter": 4,    # Cancer
    "Venus": 12,     # Pisces
    "Saturn": 7,     # Libra
    "Rahu": 3,       # Gemini (traditional)
    "Ketu": 9,       # Sagittarius (traditional)
}

# Own signs for each planet
OWN_SIGNS: Dict[str, list] = {
    "Sun": [5],
    "Moon": [4],
    "Mars": [1, 8],
    "Mercury": [3, 6],
    "Jupiter": [9, 12],
    "Venus": [2, 7],
    "Saturn": [10, 11],
    "Rahu": [],
    "Ketu": [],
}

KENDRA_HOUSES = {1, 4, 7, 10}
TRIKONA_HOUSES = {1, 5, 9}
DUSTHANA_HOUSES = {6, 8, 12}
UPACHAYA_HOUSES = {3, 6, 10, 11}
MARAKA_HOUSES = {2, 7}


def classify_house(house: int) -> str:
    if house in KENDRA_HOUSES and house in TRIKONA_HOUSES:
        return "Kendra/Trikona"
    if house in KENDRA_HOUSES:
        return "Kendra"
    if house in TRIKONA_HOUSES:
        return "Trikona"
    if house in DUSTHANA_HOUSES:
        return "Dusthana"
    if house in MARAKA_HOUSES:
        return "Maraka"
    if house in UPACHAYA_HOUSES:
        return "Upachaya"
    return "Neutral"


def classify_house_tamil(house_type: str) -> str:
    mapping = {
        "Kendra/Trikona": "கேந்திரம்/திரிகோணம்",
        "Kendra": "கேந்திரம்",
        "Trikona": "திரிகோணம்",
        "Dusthana": "துஷ்டானம்",
        "Maraka": "மாரகம்",
        "Upachaya": "உபசயம்",
        "Neutral": "நடுநிலை",
    }
    return mapping.get(house_type, house_type)


def _is_dispositor_strong(planet: str, sign: int, house: int) -> bool:
    """Check if a planet is strong: own sign, exalted, or in a Kendra."""
    if sign in OWN_SIGNS.get(planet, []):
        return True
    if EXALTATION_SIGNS.get(planet) == sign:
        return True
    if house in KENDRA_HOUSES:
        return True
    return False


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


# ---------------------------------------------------------------------------
# Axis helpers
# ---------------------------------------------------------------------------

HOUSE_ORDINAL = {
    1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th", 6: "6th",
    7: "7th", 8: "8th", 9: "9th", 10: "10th", 11: "11th", 12: "12th",
}

AXIS_NAMES: Dict[tuple, str] = {
    (1, 7): "The Identity/Relationship Axis",
    (2, 8): "The Wealth/Transformation Axis",
    (3, 9): "The Communication/Wisdom Axis",
    (4, 10): "The Home/Career Axis",
    (5, 11): "The Creativity/Community Axis",
    (6, 12): "The Service/Liberation Axis",
}

AXIS_NAMES_TAMIL: Dict[tuple, str] = {
    (1, 7): "ஆளுமை/உறவு அச்சு",
    (2, 8): "செல்வம்/மாற்றம் அச்சு",
    (3, 9): "தகவல் தொடர்பு/ஞானம் அச்சு",
    (4, 10): "வீடு/தொழில் அச்சு",
    (5, 11): "படைப்பாற்றல்/சமூகம் அச்சு",
    (6, 12): "சேவை/விடுதலை அச்சு",
}


def _axis_key(h1: int, h2: int) -> tuple:
    """Normalize two houses into a canonical axis key."""
    pair = sorted([h1, h2])
    for key in AXIS_NAMES:
        if set(key) == set(pair):
            return key
    lo = min(h1, h2)
    hi = max(h1, h2)
    if hi - lo == 6:
        return (lo, hi)
    return (h1, h2)


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

    rahu = lookup.get("Rahu", {})
    ketu = lookup.get("Ketu", {})
    saturn = lookup.get("Saturn", {})
    moon = lookup.get("Moon", {})

    rahu_house = rahu.get("house", 1)
    ketu_house = ketu.get("house", 7)
    saturn_house = saturn.get("house", 1)
    moon_house = moon.get("house", 1)

    rahu_sign = rahu.get("sign", 1)
    dispositor_name = SIGN_LORDS.get(rahu_sign, "Sun")
    disp_data = lookup.get(dispositor_name, {})
    disp_sign = disp_data.get("sign", 1)
    disp_house = disp_data.get("house", 1)
    disp_strong = _is_dispositor_strong(dispositor_name, disp_sign, disp_house)

    axis = _axis_key(rahu_house, ketu_house)
    axis_label = f"{HOUSE_ORDINAL.get(axis[0], str(axis[0]))}-{HOUSE_ORDINAL.get(axis[1], str(axis[1]))} Axis ({AXIS_NAMES.get(axis, 'Custom Axis')})"
    axis_label_tamil = f"{axis[0]}-{axis[1]} அச்சு ({AXIS_NAMES_TAMIL.get(axis, 'தனிப்பட்ட அச்சு')})"

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
        "Rahu": _build_ctx("Rahu"),
        "Ketu": _build_ctx("Ketu"),
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
        "rahu_ketu_axis": axis_label,
        "rahu_ketu_axis_tamil": axis_label_tamil,
        "rahu_house": rahu_house,
        "ketu_house": ketu_house,
        "saturn_house": saturn_house,
        "moon_house": moon_house,
        "saturn_moon_aspect": aspect,
        "saturn_moon_aspect_tamil": _saturn_moon_aspect_tamil(aspect),
        "moon_nakshatra_lord": moon_nk_lord,
        "rahu_dispositor": dispositor_name,
        "rahu_dispositor_tamil": PLANET_NAMES.get(dispositor_name, dispositor_name),
        "rahu_dispositor_strong": disp_strong,
        "axis_key": axis,
        "rahu_in_kendra": rahu_house in KENDRA_HOUSES,
        "rahu_in_trikona": rahu_house in TRIKONA_HOUSES,
    }


# ---------------------------------------------------------------------------
# Prediction Templates
# ---------------------------------------------------------------------------

# ---- Section 1: Karmic Blueprint (Rahu-Ketu axis) ----

_AXIS_PALAN_EN: Dict[tuple, str] = {
    (1, 7): (
        "Because your Rahu-Ketu axis falls in Kendras, your life will be defined by visible, "
        "external changes. Rahu in the {rahu_h} house suggests a partner or public role that "
        "brings sudden growth and unconventional perspectives. Ketu in the {ketu_h} house "
        "indicates past-life mastery over self-identity; this life demands that you learn to "
        "merge with others. Relationships are the crucible of your karmic evolution."
    ),
    (2, 8): (
        "Your Rahu-Ketu axis spans the Wealth/Transformation corridor. Rahu in the {rahu_h} "
        "house drives an intense hunger for financial security or hidden knowledge, while Ketu "
        "in the {ketu_h} house shows detachment from the opposite resource. Inheritance, "
        "insurance, or sudden windfalls may mark turning points. The NKV principle here: "
        "what you chase financially will transform you spiritually."
    ),
    (3, 9): (
        "With the Rahu-Ketu axis on the Communication/Wisdom corridor, your soul journey "
        "oscillates between practical skills (Rahu in the {rahu_h} house) and higher philosophy "
        "(Ketu in the {ketu_h} house). Siblings, short travels, and media may play pivotal "
        "roles. The NKV reading: use everyday communication as a vehicle for deeper truth."
    ),
    (4, 10): (
        "The Home/Career axis is activated. Rahu in the {rahu_h} house amplifies ambition in "
        "one domain while Ketu in the {ketu_h} house creates detachment in the other. Expect "
        "a tug-of-war between domestic comfort and professional achievement. The NKV key: "
        "balance is not compromise—it is conscious prioritization at each life stage."
    ),
    (5, 11): (
        "Your Rahu-Ketu axis lies on the Creativity/Community corridor. Rahu in the {rahu_h} "
        "house magnifies desire for recognition through creative or speculative pursuits, while "
        "Ketu in the {ketu_h} house detaches you from large networks or elder siblings. "
        "Children, romance, and community service become intertwined karmic themes."
    ),
    (6, 12): (
        "The Service/Liberation axis is your karmic battlefield. Rahu in the {rahu_h} house "
        "drives you toward problem-solving, health optimization, or competitive environments. "
        "Ketu in the {ketu_h} house grants intuitive access to spiritual realms but may bring "
        "hidden expenses. The NKV principle: serve selflessly and liberation follows naturally."
    ),
}

_AXIS_PALAN_TA: Dict[tuple, str] = {
    (1, 7): (
        "உங்கள் ராகு-கேது அச்சு கேந்திரங்களில் விழுவதால், உங்கள் வாழ்க்கை வெளிப்படையான, "
        "புறமாற்றங்களால் வரையறுக்கப்படும். {rahu_h}ஆம் இடத்தில் ராகு, திடீர் வளர்ச்சியையும் "
        "வழக்கத்திற்கு மாறான கண்ணோட்டங்களையும் தரும் துணையை அல்லது பொது பாத்திரத்தை சுட்டிக்காட்டுகிறது. "
        "{ketu_h}ஆம் இடத்தில் கேது, சுய அடையாளத்தில் முற்பிறவி தேர்ச்சியைக் குறிக்கிறது; "
        "இந்த பிறவி மற்றவர்களுடன் இணையக் கற்றுக்கொள்ள வேண்டும் என்று கோருகிறது. "
        "உறவுகளே உங்கள் கர்ம பரிணாமத்தின் சூளையாகும்."
    ),
    (2, 8): (
        "உங்கள் ராகு-கேது அச்சு செல்வம்/மாற்றம் பாதையில் பரவுகிறது. {rahu_h}ஆம் இடத்தில் "
        "ராகு நிதி பாதுகாப்பு அல்லது மறைந்த அறிவின் மீது தீவிர ஆர்வத்தைத் தூண்டுகிறது, "
        "{ketu_h}ஆம் இடத்தில் கேது எதிர் வளத்தில் பற்றின்மையைக் காட்டுகிறது. பரம்பரை சொத்து, "
        "காப்பீடு அல்லது திடீர் அதிர்ஷ்டம் திருப்புமுனைகளாக இருக்கலாம். NKV கொள்கை: "
        "நீங்கள் நிதி ரீதியாக தொடர்வது ஆன்மீக ரீதியாக உங்களை மாற்றும்."
    ),
    (3, 9): (
        "ராகு-கேது அச்சு தகவல் தொடர்பு/ஞானம் பாதையில் உள்ளது. {rahu_h}ஆம் இடத்தில் ராகு "
        "நடைமுறை திறன்களையும், {ketu_h}ஆம் இடத்தில் கேது உயர் தத்துவத்தையும் குறிக்கிறது. "
        "உடன்பிறப்புகள், குறுகிய பயணங்கள், ஊடகங்கள் முக்கிய பங்கு வகிக்கலாம். "
        "NKV வாசிப்பு: அன்றாட தகவல் தொடர்பை ஆழமான உண்மைக்கான வாகனமாகப் பயன்படுத்துங்கள்."
    ),
    (4, 10): (
        "வீடு/தொழில் அச்சு செயல்படுத்தப்பட்டுள்ளது. {rahu_h}ஆம் இடத்தில் ராகு ஒரு துறையில் "
        "லட்சியத்தை பெருக்குகிறது, {ketu_h}ஆம் இடத்தில் கேது மற்றொரு துறையில் பற்றின்மையை "
        "உருவாக்குகிறது. வீட்டு சுகமும் தொழில் சாதனையும் இடையே இழுபறி எதிர்பாருங்கள். "
        "NKV திறவுகோல்: சமநிலை என்பது சமரசம் அல்ல—ஒவ்வொரு வாழ்க்கை நிலையிலும் "
        "உணர்வுபூர்வமான முன்னுரிமையாகும்."
    ),
    (5, 11): (
        "உங்கள் ராகு-கேது அச்சு படைப்பாற்றல்/சமூகம் பாதையில் உள்ளது. {rahu_h}ஆம் இடத்தில் "
        "ராகு படைப்பு அல்லது ஊகத்தின் மூலம் அங்கீகாரத்திற்கான ஆர்வத்தை பெருக்குகிறது, "
        "{ketu_h}ஆம் இடத்தில் கேது பெரிய வலையமைப்புகளிலிருந்து உங்களைப் பிரிக்கிறது. "
        "குழந்தைகள், காதல், சமூக சேவை ஆகியவை பின்னிப்பிணைந்த கர்ம கருப்பொருள்களாகும்."
    ),
    (6, 12): (
        "சேவை/விடுதலை அச்சு உங்கள் கர்ம போர்க்களமாகும். {rahu_h}ஆம் இடத்தில் ராகு "
        "சிக்கல் தீர்வு, உடல்நல மேம்பாடு அல்லது போட்டிச் சூழலை நோக்கி உங்களைத் "
        "தூண்டுகிறது. {ketu_h}ஆம் இடத்தில் கேது ஆன்மீக உலகங்களுக்கு உள்ளுணர்வு அணுகலை "
        "வழங்குகிறது ஆனால் மறைந்த செலவுகளைக் கொண்டுவரலாம். NKV கொள்கை: "
        "தன்னலமின்றி சேவை செய்யுங்கள், விடுதலை இயற்கையாகவே தொடரும்."
    ),
}

# Kendra vs Trikona overlay
_KENDRA_OVERLAY_EN = (
    " Since Rahu-Ketu occupies Kendra houses, the focus is on career, public status, "
    "and marriage. External life events will be the primary agents of karmic growth."
)
_TRIKONA_OVERLAY_EN = (
    " Since Rahu-Ketu occupies Trikona houses, the focus is on past-life merits, children, "
    "and spiritual wisdom. Internal transformation will drive your evolution."
)
_KENDRA_OVERLAY_TA = (
    " ராகு-கேது கேந்திர இடங்களில் இருப்பதால், தொழில், பொது நிலை மற்றும் "
    "திருமணம் ஆகியவற்றில் கவனம் செலுத்தப்படும். வெளி வாழ்க்கை நிகழ்வுகளே "
    "கர்ம வளர்ச்சியின் முதன்மை காரணிகளாக இருக்கும்."
)
_TRIKONA_OVERLAY_TA = (
    " ராகு-கேது திரிகோண இடங்களில் இருப்பதால், முற்பிறவி புண்ணியம், குழந்தைகள் "
    "மற்றும் ஆன்மீக ஞானம் ஆகியவற்றில் கவனம் செலுத்தப்படும். உள்ளார்ந்த "
    "மாற்றமே உங்கள் பரிணாமத்தை இயக்கும்."
)

# Kingmaker overlay when dispositor is strong
_KINGMAKER_EN = (
    " The dispositor of Rahu ({dispositor}) is strong in your chart. "
    "According to the NKV system, Rahu acts as a Kingmaker here—amplifying the "
    "positive significations of {dispositor} and channeling them into tangible success."
)
_KINGMAKER_TA = (
    " ராகுவின் அதிபதி ({dispositor}) உங்கள் ஜாதகத்தில் வலிமையானது. "
    "NKV அமைப்பின்படி, ராகு இங்கு ஒரு அரசனை உருவாக்குபவராகச் செயல்படுகிறது—"
    "{dispositor}-இன் நேர்மறை குறிப்புகளைப் பெருக்கி, உறுதியான வெற்றியாக மாற்றுகிறது."
)

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

# Diamond Mind overlay when Moon's nakshatra lord is Saturn or Ketu
_DIAMOND_MIND_EN = (
    " Your Moon's nakshatra lord is {lord}, placing the Moon under a Saturn/Ketu star. "
    "The NKV system calls this the \"Diamond Mind\"—hardened by responsibility but capable "
    "of great beauty. Expect delays in early life that turn into solid foundations in middle age."
)
_DIAMOND_MIND_TA = (
    " உங்கள் சந்திரனின் நட்சத்திர அதிபதி {lord} ஆவார், சந்திரனை சனி/கேது நட்சத்திரத்தின் "
    "கீழ் வைக்கிறது. NKV அமைப்பு இதை \"வைர மனம்\" என்று அழைக்கிறது—பொறுப்பால் "
    "கடினப்படுத்தப்பட்டது ஆனால் பெரும் அழகை உருவாக்கும் திறன் கொண்டது. ஆரம்ப "
    "வாழ்க்கையில் தாமதங்கள் நடுத்தர வயதில் உறுதியான அடித்தளமாக மாறும்."
)

# ---- Section 3: Key Advice (based on Rahu's dispositor) ----

_ADVICE_EN: Dict[str, str] = {
    "Sun": (
        "The dispositor of Rahu is the Sun. Focus on leadership, government-related activities, "
        "and building personal authority. Cultivate self-confidence without arrogance. "
        "Sun-related remedies—early morning routines, connecting with father figures, and "
        "public service—will unlock the Rahu-Ketu axis's power in your chart."
    ),
    "Moon": (
        "The dispositor of Rahu is the Moon. Focus on nurturing, emotional intelligence, and "
        "care-giving professions. Strengthening the bond with your mother and engaging in "
        "water-related activities will harmonize the axis. Moon-related remedies—meditation, "
        "dairy donations on Mondays, and artistic expression—are your keys."
    ),
    "Mars": (
        "The dispositor of Rahu is Mars. Focus on physical discipline, engineering, real estate, "
        "or martial pursuits. Channel aggression into structured competition. Mars-related "
        "remedies—regular exercise, land-related charity, and Tuesday fasting—will strengthen "
        "the axis. Courage, not recklessness, is your NKV mantra."
    ),
    "Mercury": (
        "The dispositor of Rahu is Mercury. Focus on communication, writing, commerce, and "
        "analytical skills. Learning new languages or technologies accelerates karmic progress. "
        "Mercury-related remedies—green charity on Wednesdays, intellectual pursuits, and "
        "maintaining honest speech—are your anchors."
    ),
    "Jupiter": (
        "The dispositor of Rahu is Jupiter. Focus on teaching, spiritual wisdom, law, and "
        "advisory roles. Expanding knowledge through formal education or mentorship unlocks "
        "the axis. Jupiter-related remedies—Thursday prayers, yellow clothing, and serving "
        "teachers or gurus—will amplify the positive potential."
    ),
    "Venus": (
        "The dispositor of Rahu is Venus. Focus on harmony, art, beauty, and relationship "
        "building. Creative professions, diplomacy, and luxury-related businesses are favored. "
        "Venus-related remedies—Friday observances, white clothing, and supporting women's "
        "causes—will balance the axis and attract abundance."
    ),
    "Saturn": (
        "The dispositor of Rahu is Saturn. Focus on discipline, long-term planning, service to "
        "the elderly, and structural work (construction, law, administration). Saturn rewards "
        "patience above all. Saturn-related remedies—Saturday charity, serving the underprivileged, "
        "and iron/sesame donations—will slowly but permanently activate the axis."
    ),
    "Rahu": (
        "Rahu is its own dispositor (in a sign without a traditional owner, or self-referencing). "
        "This amplifies Rahu's unconventional energy. Focus on foreign connections, technology, "
        "and breaking conventional boundaries. The NKV caution: without a strong dispositor anchor, "
        "Rahu can create illusions. Ground yourself through meditation and ethical clarity."
    ),
    "Ketu": (
        "The dispositor of Rahu traces back to Ketu's influence, creating a closed karmic loop. "
        "Focus on spiritual practices, research, and detachment from material obsession. "
        "Ketu-related remedies—dog charity, muted colors, and pilgrimage—will help resolve "
        "the loop and bring clarity to your life direction."
    ),
}

_ADVICE_TA: Dict[str, str] = {
    "Sun": (
        "ராகுவின் அதிபதி சூரியன். தலைமைத்துவம், அரசாங்க சம்பந்தமான செயல்பாடுகள் "
        "மற்றும் தனிப்பட்ட அதிகாரத்தை கட்டியெழுப்புவதில் கவனம் செலுத்துங்கள். "
        "ஆணவமின்றி தன்னம்பிக்கையை வளர்த்துக்கொள்ளுங்கள். சூரிய சம்பந்தமான "
        "பரிகாரங்கள்—அதிகாலை வழக்கம், தந்தை உருவங்களுடன் இணைவு, பொது சேவை—"
        "உங்கள் ஜாதகத்தில் ராகு-கேது அச்சின் சக்தியைத் திறக்கும்."
    ),
    "Moon": (
        "ராகுவின் அதிபதி சந்திரன். பராமரிப்பு, உணர்ச்சி நுண்ணறிவு மற்றும் "
        "பராமரிப்பு தொழில்களில் கவனம் செலுத்துங்கள். தாயாருடன் உள்ள பிணைப்பை "
        "வலுப்படுத்துவதும் நீர் சம்பந்தமான செயல்பாடுகளில் ஈடுபடுவதும் அச்சை "
        "இணக்கமாக்கும். சந்திர பரிகாரங்கள்—தியானம், திங்கள் கிழமை பால் தானம், "
        "கலை வெளிப்பாடு—உங்கள் திறவுகோல்கள்."
    ),
    "Mars": (
        "ராகுவின் அதிபதி செவ்வாய். உடல் ஒழுக்கம், பொறியியல், நிலம் சம்பந்தமான "
        "செயல்பாடுகள் அல்லது போர்க்கலை முயற்சிகளில் கவனம் செலுத்துங்கள். "
        "ஆக்ரோஷத்தை கட்டமைக்கப்பட்ட போட்டியில் செலுத்துங்கள். செவ்வாய் "
        "பரிகாரங்கள்—வழக்கமான உடற்பயிற்சி, நில தானம், செவ்வாய் கிழமை விரதம்—"
        "அச்சை வலுப்படுத்தும். துணிச்சல், பொறுப்பற்ற தன்மை அல்ல, உங்கள் NKV மந்திரம்."
    ),
    "Mercury": (
        "ராகுவின் அதிபதி புதன். தகவல் தொடர்பு, எழுத்து, வணிகம் மற்றும் "
        "பகுப்பாய்வு திறன்களில் கவனம் செலுத்துங்கள். புதிய மொழிகள் அல்லது "
        "தொழில்நுட்பங்களைக் கற்றுக்கொள்வது கர்ம முன்னேற்றத்தை துரிதப்படுத்தும். "
        "புதன் பரிகாரங்கள்—புதன் கிழமை பச்சை தானம், அறிவு முயற்சிகள், "
        "நேர்மையான பேச்சு—உங்கள் நங்கூரங்கள்."
    ),
    "Jupiter": (
        "ராகுவின் அதிபதி குரு. கற்பித்தல், ஆன்மீக ஞானம், சட்டம் மற்றும் "
        "ஆலோசனை பாத்திரங்களில் கவனம் செலுத்துங்கள். முறையான கல்வி அல்லது "
        "வழிகாட்டுதல் மூலம் அறிவை விரிவுபடுத்துவது அச்சைத் திறக்கும். குரு "
        "பரிகாரங்கள்—வியாழன் பிரார்த்தனை, மஞ்சள் ஆடை, ஆசிரியர்கள் அல்லது "
        "குருக்களுக்கு சேவை—நேர்மறை திறனை பெருக்கும்."
    ),
    "Venus": (
        "ராகுவின் அதிபதி சுக்ரன். இணக்கம், கலை, அழகு மற்றும் உறவு "
        "கட்டிடத்தில் கவனம் செலுத்துங்கள். படைப்பு தொழில்கள், இராஜதந்திரம், "
        "ஆடம்பரம் சம்பந்தமான வணிகங்கள் சாதகமானவை. சுக்ர பரிகாரங்கள்—வெள்ளி "
        "கிழமை ஆசாரங்கள், வெள்ளை ஆடை, பெண்கள் காரணங்களை ஆதரிப்பது—"
        "அச்சை சமப்படுத்தி செழிப்பை ஈர்க்கும்."
    ),
    "Saturn": (
        "ராகுவின் அதிபதி சனி. ஒழுக்கம், நீண்டகால திட்டமிடல், முதியோர் சேவை "
        "மற்றும் கட்டமைப்பு வேலை (கட்டிடம், சட்டம், நிர்வாகம்) ஆகியவற்றில் "
        "கவனம் செலுத்துங்கள். சனி எல்லாவற்றிற்கும் மேலாக பொறுமையை வெகுமதி "
        "அளிக்கிறது. சனி பரிகாரங்கள்—சனி கிழமை தானம், ஆதரவற்றோருக்கு சேவை, "
        "இரும்பு/எள் தானம்—மெதுவாக ஆனால் நிரந்தரமாக அச்சை செயல்படுத்தும்."
    ),
    "Rahu": (
        "ராகு தனக்கே அதிபதியாக உள்ளது. இது ராகுவின் வழக்கத்திற்கு மாறான "
        "ஆற்றலை பெருக்குகிறது. வெளிநாட்டு தொடர்புகள், தொழில்நுட்பம் மற்றும் "
        "வழக்கமான எல்லைகளை உடைப்பதில் கவனம் செலுத்துங்கள். NKV எச்சரிக்கை: "
        "வலுவான அதிபதி நங்கூரம் இல்லாமல், ராகு மாயைகளை உருவாக்கலாம். "
        "தியானம் மற்றும் நெறிமுறை தெளிவு மூலம் உங்களை நிலைநிறுத்துங்கள்."
    ),
    "Ketu": (
        "ராகுவின் அதிபதி கேதுவின் தாக்கத்திற்கு இட்டுச் செல்கிறது, ஒரு மூடிய "
        "கர்ம வளையத்தை உருவாக்குகிறது. ஆன்மீக நடைமுறைகள், ஆராய்ச்சி மற்றும் "
        "பொருள் ஆசையிலிருந்து விலகுவதில் கவனம் செலுத்துங்கள். கேது பரிகாரங்கள்—"
        "நாய் தானம், மென்மையான வண்ணங்கள், புனித யாத்திரை—வளையத்தை "
        "தீர்க்கவும் உங்கள் வாழ்க்கை திசையில் தெளிவைக் கொண்டுவரவும் உதவும்."
    ),
}


# ---------------------------------------------------------------------------
# generate_nkv_predictions  -- assemble predictions from context
# ---------------------------------------------------------------------------

def generate_nkv_predictions(context: Dict[str, Any]) -> NKVPalanResult:
    axis_key = context["axis_key"]
    rahu_h = context["rahu_house"]
    ketu_h = context["ketu_house"]

    # Section 1
    base_en = _AXIS_PALAN_EN.get(axis_key, _AXIS_PALAN_EN.get((1, 7), ""))
    base_ta = _AXIS_PALAN_TA.get(axis_key, _AXIS_PALAN_TA.get((1, 7), ""))

    s1_en = base_en.format(
        rahu_h=HOUSE_ORDINAL.get(rahu_h, str(rahu_h)),
        ketu_h=HOUSE_ORDINAL.get(ketu_h, str(ketu_h)),
    )
    s1_ta = base_ta.format(rahu_h=rahu_h, ketu_h=ketu_h)

    if context["rahu_in_kendra"] or context.get("planetary_context", {}).get("Ketu", None) and context["planetary_context"]["Ketu"].house in KENDRA_HOUSES:
        s1_en += _KENDRA_OVERLAY_EN
        s1_ta += _KENDRA_OVERLAY_TA
    elif context["rahu_in_trikona"]:
        s1_en += _TRIKONA_OVERLAY_EN
        s1_ta += _TRIKONA_OVERLAY_TA

    if context["rahu_dispositor_strong"]:
        disp = context["rahu_dispositor"]
        disp_ta = context["rahu_dispositor_tamil"]
        s1_en += _KINGMAKER_EN.format(dispositor=disp)
        s1_ta += _KINGMAKER_TA.format(dispositor=disp_ta)

    # Section 2
    aspect = context["saturn_moon_aspect"]
    s2_en = _SATMOON_EN.get(aspect, _SATMOON_EN["Other"])
    s2_ta = _SATMOON_TA.get(aspect, _SATMOON_TA["Other"])

    nk_lord = context["moon_nakshatra_lord"]
    if nk_lord in ("Saturn", "Ketu"):
        lord_ta = PLANET_NAMES.get(nk_lord, nk_lord)
        s2_en += _DIAMOND_MIND_EN.format(lord=nk_lord)
        s2_ta += _DIAMOND_MIND_TA.format(lord=lord_ta)

    # Section 3
    disp_name = context["rahu_dispositor"]
    s3_en = _ADVICE_EN.get(disp_name, _ADVICE_EN["Sun"])
    s3_ta = _ADVICE_TA.get(disp_name, _ADVICE_TA["Sun"])

    rahu_ctx = context["planetary_context"]["Rahu"]
    ketu_ctx = context["planetary_context"]["Ketu"]
    saturn_ctx = context["planetary_context"]["Saturn"]
    moon_ctx = context["planetary_context"]["Moon"]

    s1_placement_en = (
        f"Rahu in {rahu_ctx.sign} ({HOUSE_ORDINAL[rahu_h]} house, {rahu_ctx.house_type}) — "
        f"Ketu in {ketu_ctx.sign} ({HOUSE_ORDINAL[ketu_h]} house, {ketu_ctx.house_type})"
    )
    s1_placement_ta = (
        f"ராகு {rahu_ctx.sign_tamil}-ல் ({rahu_h}ஆம் இடம், {rahu_ctx.house_type_tamil}) — "
        f"கேது {ketu_ctx.sign_tamil}-ல் ({ketu_h}ஆம் இடம், {ketu_ctx.house_type_tamil})"
    )

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
        rahu_ketu_axis=context["rahu_ketu_axis"],
        rahu_ketu_axis_tamil=context["rahu_ketu_axis_tamil"],
        saturn_moon_aspect=context["saturn_moon_aspect"],
        saturn_moon_aspect_tamil=context["saturn_moon_aspect_tamil"],
        rahu_dispositor=context["rahu_dispositor"],
        rahu_dispositor_tamil=context["rahu_dispositor_tamil"],
        rahu_dispositor_strong=context["rahu_dispositor_strong"],
        section1_title="The Karmic Blueprint (Rahu-Ketu)",
        section1_title_tamil="கர்ம வரைபடம் (ராகு-கேது)",
        section1_placement=s1_placement_en,
        section1_placement_tamil=s1_placement_ta,
        section1_palan=s1_en,
        section1_palan_tamil=s1_ta,
        section2_title="The Mental Filter (Saturn-Moon)",
        section2_title_tamil="மன வடிகட்டி (சனி-சந்திரன்)",
        section2_placement=s2_placement_en,
        section2_placement_tamil=s2_placement_ta,
        section2_palan=s2_en,
        section2_palan_tamil=s2_ta,
        section3_title="The NKV Key Advice",
        section3_title_tamil="NKV முக்கிய ஆலோசனை",
        section3_advice=s3_en,
        section3_advice_tamil=s3_ta,
    )
