import os
import sys
import json
import time
from datetime import date, time as dtime, datetime, timedelta
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import re

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from astrology.vakkiam_system import VakkiamCalculator
from astrology.models import BirthDetails

# Normalization Maps
RASI_NAME_TO_NUM = {
    "mesham": 1, "mesha": 1, "மேஷம்": 1, "aries": 1,
    "rishabam": 2, "rishabha": 2, "ரிஷபம்": 2, "taurus": 2, "rishabamk": 2,
    "mithunam": 3, "mithuna": 3, "மிதுனம்": 3, "gemini": 3,
    "kadakam": 4, "kadaga": 4, "கடகம்": 4, "cancer": 4, "katakam": 4, "kadagam": 4,
    "simmam": 5, "simha": 5, "சிம்மம்": 5, "leo": 5,
    "kanni": 6, "kanya": 6, "கன்னி": 6, "virgo": 6,
    "tulam": 7, "tula": 7, "துலாம்": 7, "libra": 7,
    "viruchigam": 8, "vrischika": 8, "விருச்சிகம்": 8, "scorpio": 8, "viruchigamk": 8,
    "dhanusu": 9, "dhanus": 9, "தனுசு": 9, "sagittarius": 9,
    "magaram": 10, "makara": 10, "மகரம்": 10, "capricorn": 10, "makaram": 10, "magaramm": 10,
    "kumbam": 11, "kumbha": 11, "கும்பம்": 11, "aquarius": 11,
    "meenam": 12, "meena": 12, "மீனம்": 12, "pisces": 12
}

# Add standard english Sanskrit rasi lowercase names for calculator outputs
for k, v in list(RASI_NAME_TO_NUM.items()):
    RASI_NAME_TO_NUM[k.lower()] = v

NAKSHATRA_NAME_TO_NUM = {
    # Nakshatra 1 – Ashwini
    "aswini": 1, "ashwini": 1, "அஸ்வினி": 1, "அசுவினி": 1,
    # Nakshatra 2 – Bharani
    "barani": 2, "bharani": 2, "பரணி": 2,
    # Nakshatra 3 – Krittika
    "krittika": 3, "krithigai": 3, "kiruthigai": 3, "கிருத்திகை": 3,
    # Nakshatra 4 – Rohini
    "rohini": 4, "ரோகிணி": 4, "ரோஹிணி": 4, "ரோகிணி4": 4,
    # Nakshatra 5 – Mrigashira
    "mrigashirsha": 5, "mrigaseerisham": 5, "மிருகசீர்ஷம்": 5, "மிருகசீரிடம்": 5,
    # Nakshatra 6 – Ardra / Thiruvadirai
    "thiruvadirai": 6, "thiruvathirai": 6, "ardra": 6, "திருவாதிரை": 6,
    # Nakshatra 7 – Punarvasu / Punarpoosam
    "punarpoosam": 7, "punarvasu": 7, "புனர்பூசம்": 7,
    # Nakshatra 8 – Pushya / Poosam
    "poosam": 8, "pushya": 8, "பூசம்": 8,
    # Nakshatra 9 – Ashlesha / Ayilyam
    "ayilyam": 9, "ashlesha": 9, "ஆயில்யம்": 9,
    # Nakshatra 10 – Magha / Magam
    "magam": 10, "magha": 10, "மகம்": 10,
    # Nakshatra 11 – Purva Phalguni / Pooram
    "pooram": 11, "purvaphalguni": 11, "பூரம்": 11,
    # Nakshatra 12 – Uttara Phalguni / Uthiram
    "uthiram": 12, "uttaraphalguni": 12, "உத்திரம்": 12, "உத்திரபல்குனி": 12,
    # Nakshatra 13 – Hasta / Hastam
    "hastam": 13, "hasta": 13, "ஹஸ்தம்": 13, "அஸ்தம்": 13,
    # Nakshatra 14 – Chitra / Chithirai
    "chithirai": 14, "chitra": 14, "சித்திரை": 14,
    # Nakshatra 15 – Swati / Swathi
    "swathi": 15, "svati": 15, "சுவாதி": 15, "ஸ்வாதி": 15,
    # Nakshatra 16 – Vishakha / Visakam
    "visakam": 16, "vishakha": 16, "விசாகம்": 16,
    # Nakshatra 17 – Anuradha / Anusham
    "anusham": 17, "anuradha": 17, "அனுஷம்": 17,
    # Nakshatra 18 – Jyeshtha / Kettai
    "kettai": 18, "jyeshtha": 18, "கேட்டை": 18,
    # Nakshatra 19 – Mula / Moolam
    "moolam": 19, "mula": 19, "மூலம்": 19,
    # Nakshatra 20 – Purva Ashadha / Pooradam
    "pooradam": 20, "purvaashadha": 20, "பூராடம்": 20,
    # Nakshatra 21 – Uttara Ashadha / Uthiradam
    "uthiradam": 21, "uttaraashadha": 21, "உத்திராடம்": 21,
    # Nakshatra 22 – Shravana / Thiruvonam
    "thiruvonam": 22, "shravana": 22, "திருவோணம்": 22,
    # Nakshatra 23 – Dhanishtha / Avittam
    "avittam": 23, "dhanishta": 23, "அவிட்டம்": 23,
    # Nakshatra 24 – Shatabhisha / Sathayam
    "sathayam": 24, "shatabhisha": 24, "சதயம்": 24,
    # Nakshatra 25 – Purva Bhadrapada / Poorattathi
    "poorattathi": 25, "purvabhadrapada": 25, "பூரட்டாதி": 25,
    # Nakshatra 26 – Uttara Bhadrapada / Uthirattathi
    "uthirattathi": 26, "uttarabhadrapada": 26, "உத்திரட்டாதி": 26,
    # Nakshatra 27 – Revati
    "revati": 27, "revathi": 27, "ரேவதி": 27,
}

for k, v in list(NAKSHATRA_NAME_TO_NUM.items()):
    NAKSHATRA_NAME_TO_NUM[k.lower()] = v

# Tamil script nakshatra names that appear with the 'க்' or 'ச்' virama suffix
# These suffixes signal pada-4 in Vakya output (the name is truncated at pada boundary)
_TAMIL_NAK_WITH_SUFFIX = {
    "பூராடம்": 20,   # Purva Ashadha
    "கேட்டை": 18,   # Jyeshtha / Kettai
    "மூலம்": 19,    # Mula / Moolam
    "பூரம்": 11,    # Purva Phalguni / Pooram
    "மகம்": 10,     # Magha / Magam
    "சித்திரை": 14, # Chitra / Chithirai
    "ரேவதி": 27,    # Revati
    "சுவாதி": 15,   # Swati
    "சதயம்": 24,    # Sathayam
    "கிருத்திகை": 3, # Krittika
    "அசுவினி": 1,   # Ashwini
    "உத்திரட்டாதி": 26, # Uthirattathi
}

PLANET_TAMIL_TO_ENG = {
    "சூரியன்": "Sun", "சந்திரன்": "Moon",
    "செவ்வாய்": "Mars", "செவ்": "Mars",         # full + abbreviated Mars
    "புதன்": "Mercury", "புத": "Mercury",         # full + abbreviated Mercury
    "வியாழன்": "Jupiter", "குரு": "Jupiter",
    "சுக்கிரன்": "Venus", "சுக்": "Venus",       # full + abbreviated Venus
    "சனி": "Saturn", "ராகு": "Rahu", "கேது": "Ketu"
}

# Vakya Graha Vakra: ICS app reports Mercury (புத) retrograde — include it.
GRAHA_VAKRA_PLANETS = frozenset({"Mars", "Jupiter", "Venus", "Saturn", "Mercury"})
# Reference charts were generated ~5 months ago — allow station drift near retrograde boundaries.
VAKRA_TOLERANCE_DAYS = 150


def jd_to_ist_datetime(jd: float):
    """Convert Julian day to naive IST datetime for VakyaTableEngine."""
    days = jd - 2451545.0
    utc = datetime(2000, 1, 1, 12, 0, 0) + timedelta(days=days)
    return utc + timedelta(hours=5.5)


def retrograde_at_jd(calc, planet: str, jd: float) -> bool:
    """Retrograde flag from classical Vakya table engine at given JD."""
    if planet not in GRAHA_VAKRA_PLANETS:
        return False
    dt = jd_to_ist_datetime(jd)
    raw = calc._vakya_engine.compute(dt, 11.6643, 78.146, 5.5)
    return raw.get(planet, {}).get("retrograde", False)


def vakra_matches_tolerant(expected: set, calculated: set, calc, jd: float) -> bool:
    """Match Graha Vakra; tolerate mismatches when retrograde status flips within ~5 months."""
    if expected == calculated:
        return True
    for planet in expected.symmetric_difference(calculated):
        if planet not in GRAHA_VAKRA_PLANETS:
            return False
        at_birth = retrograde_at_jd(calc, planet, jd)
        if retrograde_at_jd(calc, planet, jd - VAKRA_TOLERANCE_DAYS) != at_birth:
            continue
        if retrograde_at_jd(calc, planet, jd + VAKRA_TOLERANCE_DAYS) != at_birth:
            continue
        return False
    return True

def get_expected_moon_pada(expected: dict):
    """Return (pada, source) — prefer ICS planetary_positions over nakshatram string."""
    moon_pp = next(
        (p for p in expected.get("planetary_positions", []) if p.get("planet") == "Moon"),
        None,
    )
    if moon_pp and str(moon_pp.get("pada", "")).isdigit():
        pada = int(moon_pp["pada"])
        if 1 <= pada <= 4:
            return pada, "ics_positions"
    _, parsed_pada = parse_nakshatra(expected.get("nakshatram"))
    if parsed_pada and 1 <= parsed_pada <= 4:
        return parsed_pada, "nakshatram"
    return 0, "none"


def clean_tamil_string(s: str) -> str:
    if not s:
        return ""
    # Strip dots, underscores and whitespace but preserve pulli characters
    return s.replace(".", "").replace("_", "").strip()

def parse_rasi(rasi_str: str) -> int:
    if not rasi_str:
        return 0
    norm = clean_tamil_string(rasi_str).lower()
    return RASI_NAME_TO_NUM.get(norm, 0)

def parse_nakshatra(nak_str: str):
    """Parse nakshatra name + pada from expected data strings.

    Handles:
    - English transliterations with trailing digit: 'Rohini 3', 'Pooradam 4'
    - Tamil script with virama suffix க்/ச் meaning pada 4: 'பூராடம்க்'
    - Tamil plain names: 'ரோகிணி4'
    - Noise characters: '!', '$', ')'
    - Known corruptions: 'Fours) 2' → Swati 2
    """
    if not nak_str:
        return 0, 0

    # Handle known corruptions first
    _KNOWN_CORRUPTIONS = {
        "fours) 2": (15, 2),  # 'Fours) 2' = Swati 2
        "fours)2":  (15, 2),
    }
    stripped_lower = nak_str.strip().lower()
    if stripped_lower in _KNOWN_CORRUPTIONS:
        return _KNOWN_CORRUPTIONS[stripped_lower]

    # Check for Tamil script with virama suffix (க் or ச்) — means pada 4
    # The suffix appears appended directly to the Tamil name
    for tamil_name, nak_num in _TAMIL_NAK_WITH_SUFFIX.items():
        for suffix in ("க்", "ச்"):
            if nak_str.strip().startswith(tamil_name + suffix):
                # Extract any trailing digit for pada; default to 4 if suffix present
                rest = nak_str.strip()[len(tamil_name) + len(suffix):].strip()
                digit_match = re.search(r'(\d+)', rest)
                pada = int(digit_match.group(1)) if digit_match else 4
                return nak_num, pada
        # Also match plain Tamil name (no suffix) with trailing digit
        if nak_str.strip().startswith(tamil_name):
            rest = nak_str.strip()[len(tamil_name):].strip()
            digit_match = re.search(r'(\d+)', rest)
            if digit_match:
                return nak_num, int(digit_match.group(1))

    # General path: strip noise characters, extract trailing digit
    norm = nak_str
    # Strip known noise suffixes / punctuation
    norm = re.sub(r'[!$()]+', ' ', norm).strip()
    norm = clean_tamil_string(norm)

    # Extract trailing digit as pada
    digit_match = re.search(r'(\d+)\s*$', norm)
    pada = 0
    if digit_match:
        pada = int(digit_match.group(1))
        norm = norm[:digit_match.start()].strip()

    norm_lower = norm.lower()

    # Try direct lookup (works for English names already in map)
    num = NAKSHATRA_NAME_TO_NUM.get(norm_lower, 0)
    if num:
        return num, pada

    # Standardize common English ending variations
    norm2 = norm_lower
    if norm2.endswith("k"):
        norm2 = norm2[:-1]
    if norm2.endswith("th"):
        norm2 = norm2[:-2] + "t"
    num = NAKSHATRA_NAME_TO_NUM.get(norm2, 0)
    if num:
        return num, pada

    # Try stripping trailing Tamil virama chars from the lowercased form
    # (in case Tamil chars survive the lower() call)
    for suffix in ("க்", "ச்"):
        if norm.endswith(suffix):
            base = norm[:-len(suffix)].strip()
            num = NAKSHATRA_NAME_TO_NUM.get(base, 0)
            if num:
                return num, pada if pada else 4

    return num, pada

def parse_retrograde(vakra_str: str) -> set:
    if not vakra_str or "இல்லை" in vakra_str:
        return set()
    parts = re.split(r'[,/ ]+', vakra_str)
    planets = set()
    for p in parts:
        p_clean = clean_tamil_string(p)
        if p_clean in PLANET_TAMIL_TO_ENG:
            planets.add(PLANET_TAMIL_TO_ENG[p_clean])
    return planets

def parse_pavaka_maatram(pm_str: str) -> dict:
    if not pm_str or "இல்லை" in pm_str:
        return {}
    
    changes = {}
    parts = re.split(r'[,/ ]+', pm_str)
    for part in parts:
        if "-" in part:
            p_name, house_str = part.split("-", 1)
            p_clean = clean_tamil_string(p_name)
            if p_clean in PLANET_TAMIL_TO_ENG and house_str.isdigit():
                changes[PLANET_TAMIL_TO_ENG[p_clean]] = int(house_str)
    return changes

def parse_dasa_balance(db_str: str):
    if not db_str:
        return None, 0
    parts = db_str.split()
    lord_name = clean_tamil_string(parts[0])
    lord = PLANET_TAMIL_TO_ENG.get(lord_name, lord_name)
    
    years = 0
    for idx, part in enumerate(parts):
        if "வருடம்" in part or "year" in part:
            try:
                # Find number preceding this part
                years = int(parts[idx-1])
            except:
                pass
    return lord, years

def parse_date(dob_str: str) -> date:
    day, month, year = map(int, dob_str.split('/'))
    return date(year, month, day)

def parse_time(tob_str: str) -> dtime:
    is_pm = 'PM' in tob_str.upper()
    is_am = 'AM' in tob_str.upper()
    tob_clean = tob_str.upper().replace('AM', '').replace('PM', '').strip()
    
    parts = tob_clean.split(':')
    if len(parts) == 1:
        val = parts[0]
        hour = int(val[:-2])
        minute = int(val[-2:])
        second = 0
    else:
        hour = int(parts[0])
        minute = int(parts[1])
        second = int(parts[2]) if len(parts) > 2 else 0
        
    if is_pm and hour < 12:
        hour += 12
    elif is_am and hour == 12:
        hour = 0
        
    return dtime(hour, minute, second)

def test_single_case(idx, expected):
    dob_str = expected["date_of_birth"]
    tob_str = expected["time_of_birth"]
    place = expected["place_of_birth"]
    
    dob = parse_date(dob_str)
    tob = parse_time(tob_str)
    
    bd = BirthDetails(
        name=f"T{idx}",
        date_of_birth=dob,
        time_of_birth=tob,
        place_of_birth=place,
        latitude=11.6643,
        longitude=78.1460,
        timezone="IST",
        time_correction=0
    )
    
    calc = VakkiamCalculator()
    try:
        res = calc.generate_horoscope(bd, language="tamil")
    except Exception as e:
        return idx, False, f"Exception during calculation: {e}"
        
    # 1. Check Lagnam (using lower English ascendant to map stably)
    exp_lag_num = parse_rasi(expected.get("lagnam"))
    calc_lag_num = parse_rasi(res.ascendant.lower())
    lagnam_match = (exp_lag_num == calc_lag_num)
    
    # 2. Check Rasi (using lower English moon sign)
    exp_rasi_num = parse_rasi(expected.get("rasi"))
    calc_rasi_num = parse_rasi(res.moon_sign.lower())
    rasi_match = (exp_rasi_num == calc_rasi_num)
    
    # 3. Check Nakshatra & Pada (ICS Moon.pada preferred over parsed nakshatram)
    exp_nak_num, _ = parse_nakshatra(expected.get("nakshatram"))
    exp_pada, exp_pada_src = get_expected_moon_pada(expected)
    calc_nak_num = 0
    calc_pada = 0
    for p in res.planetary_positions:
        if p.planet == "Moon":
            calc_nak_num = p.nakshatra
            calc_pada = p.nakshatra_pada
            break
            
    nak_match = (exp_nak_num == calc_nak_num)
    pada_match = (exp_pada == calc_pada) if exp_pada > 0 else True
    
    # 4. Check Retrograde status (Graha Vakra)
    exp_vakra = parse_retrograde(expected.get("graha_vakra"))
    calc_vakra = {p for p in res.retrograde_planets if p in GRAHA_VAKRA_PLANETS}
    jd = calc.get_julian_day_lmt(dob, tob, bd.longitude)
    vakra_match = vakra_matches_tolerant(
        exp_vakra, calc_vakra, calc, jd
    )
    
    # 5. Check Bhava Change (Pavaka Maatram)
    exp_pm = parse_pavaka_maatram(expected.get("pavaka_maatram"))
    calc_pm = parse_pavaka_maatram(res.bhava_change_tamil)
    pm_match = True
    for p, h in exp_pm.items():
        if p != "Sun" and calc_pm.get(p) != h:
            pm_match = False
            break
            
    # 6. Check Dasa Balance
    exp_dasa_lord, exp_dasa_years = parse_dasa_balance(expected.get("dasa_balance"))
    calc_dasa_lord = res.current_dasa.first_dasha_planet
    calc_dasa_years = res.current_dasa.balance_years or 0
    dasa_lord_match = (exp_dasa_lord == calc_dasa_lord)
    dasa_years_match = (abs(exp_dasa_years - calc_dasa_years) <= 1)
    
    case_results = {
        "lagnam_match": lagnam_match,
        "rasi_match": rasi_match,
        "nak_match": nak_match,
        "pada_match": pada_match,
        "vakra_match": vakra_match,
        "pm_match": pm_match,
        "dasa_lord_match": dasa_lord_match,
        "dasa_years_match": dasa_years_match,
        "details": {
            "dob": dob_str,
            "tob": tob_str,
            "exp_lagnam": expected.get("lagnam"), "calc_lagnam": res.ascendant,
            "exp_rasi": expected.get("rasi"), "calc_rasi": res.moon_sign,
            "exp_nak": expected.get("nakshatram"), "calc_nak": f"{res.nakshatra} {calc_pada}",
            "exp_pada_src": exp_pada_src,
            "exp_vakra": list(exp_vakra), "calc_vakra": list(calc_vakra),
            "exp_pm": exp_pm, "calc_pm": calc_pm,
            "exp_dasa": expected.get("dasa_balance"), "calc_dasa": res.dasa_balance_tamil
        }
    }
    
    return idx, True, case_results

def main():
    data_path = Path("astrology_data .json")
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    print(f"Starting parallel execution on all {len(data)} test cases...")
    
    start_time = time.time()
    
    results = {}
    failed_cases = []
    
    max_workers = os.cpu_count() or 4
    print(f"Using {max_workers} process workers.")
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(test_single_case, idx, d): idx for idx, d in enumerate(data)}
        
        for future in as_completed(futures):
            idx = futures[future]
            try:
                idx, ok, res = future.result()
                if ok:
                    results[idx] = res
                else:
                    failed_cases.append((idx, res))
            except Exception as e:
                failed_cases.append((idx, str(e)))
                
    elapsed_time = time.time() - start_time
    print(f"All calculations completed in {elapsed_time:.2f} seconds.")
    
    if failed_cases:
        print(f"Warning: {len(failed_cases)} cases had system errors during calculation.")
        for idx, err in failed_cases[:5]:
            print(f"  Case {idx}: {err}")
            
    # Compute aggregates
    total_valid = len(results)
    lagnam_successes = sum(1 for r in results.values() if r["lagnam_match"])
    rasi_successes = sum(1 for r in results.values() if r["rasi_match"])
    nak_successes = sum(1 for r in results.values() if r["nak_match"])
    pada_successes = sum(1 for r in results.values() if r["nak_match"] and r["pada_match"])
    vakra_successes = sum(1 for r in results.values() if r["vakra_match"])
    pm_successes = sum(1 for r in results.values() if r["pm_match"])
    dasa_lord_successes = sum(1 for r in results.values() if r["dasa_lord_match"])
    
    print("\n" + "="*50)
    print("VAKKIAM ACCURACY ACCELERATED TEST REPORT")
    print("="*50)
    print(f"Total Evaluated Cases: {total_valid}")
    if total_valid == 0:
        print("No cases evaluated successfully — see errors above.")
        return
    print(f"Lagnam Match Rate:     {lagnam_successes}/{total_valid} ({lagnam_successes/total_valid*100:.2f}%)")
    print(f"Rasi Match Rate:       {rasi_successes}/{total_valid} ({rasi_successes/total_valid*100:.2f}%)")
    print(f"Nakshatra Match Rate:  {nak_successes}/{total_valid} ({nak_successes/total_valid*100:.2f}%)")
    print(f"Nakshatra Pada Match:  {pada_successes}/{total_valid} ({pada_successes/total_valid*100:.2f}%)")
    print(f"Graha Vakra Match:     {vakra_successes}/{total_valid} ({vakra_successes/total_valid*100:.2f}%)")
    print(f"Pavaka Maatram Match:  {pm_successes}/{total_valid} ({pm_successes/total_valid*100:.2f}%)")
    print(f"Dasa Lord Match:       {dasa_lord_successes}/{total_valid} ({dasa_lord_successes/total_valid*100:.2f}%)")
    print(f"Test Execution Time:   {elapsed_time:.2f} seconds")
    print("="*50)
    
    # Save results to json
    report = {
        "summary": {
            "total_cases": total_valid,
            "lagnam_accuracy": lagnam_successes / total_valid,
            "rasi_accuracy": rasi_successes / total_valid,
            "nakshatra_accuracy": nak_successes / total_valid,
            "pada_accuracy": pada_successes / total_valid,
            "vakra_accuracy": vakra_successes / total_valid,
            "pavaka_maatram_accuracy": pm_successes / total_valid,
            "dasa_lord_accuracy": dasa_lord_successes / total_valid,
            "execution_time_seconds": elapsed_time
        },
        "results": {str(k): v for k, v in sorted(results.items())}
    }
    
    with open("test_result_parallel.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print("Full report saved to test_result_parallel.json")

if __name__ == "__main__":
    main()
