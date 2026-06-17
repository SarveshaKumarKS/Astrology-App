#!/usr/bin/env python3
"""
Run the Python VakyaTableEngine against all 729 test cases and compare each
planet's nakshatra + pada against the STORED ICS reference values.

Mirrors run_java_vs_ics.py exactly (same nakshatra aliasing, same denominator
logic) so the Python-vs-ICS numbers are directly comparable to Java-vs-ICS.
"""
import json
import sys
import re
from datetime import datetime

sys.path.insert(0, '/home/user/Astrology-App/backend')
from astrology.vakya_table_engine import VakyaTableEngine

DATA_JSON  = '/home/user/Astrology-App/tests/astrology_data .json'
DATA_DIR   = '/home/user/Astrology-App/backend/astrology/data/vakya'
LAT, LON, TZ = 11.6643, 78.185, 5.5

PLANET_ORDER = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu']

NAKSHATRAS = [
    "Aswini","Bharani","Karthigai","Rohini","Mirugasirisha","Thiruvaathirai",
    "Punarpoosam","Poosam","Ayilyam","Magam","Pooram","Uthiram","Hastham",
    "Chithirai","Swathi","Visakam","Anusham","Kettai","Moolam","Pooradam",
    "Uthiradam","Thiruvonam","Avittam","Sathayam","Poorattathi","Uthirattathi",
    "Revathi"
]

# Map ICS stored star_name spellings → canonical nakshatra index (0-26).
NAK_INDEX = {n.lower(): i for i, n in enumerate(NAKSHATRAS)}
NAK_ALIASES = {
    'hastam': 12, 'hastham': 12,
    'barani': 1, 'bharani': 1,
    'mrigashirsha': 4, 'mirugasirisha': 4, 'mrigasira': 4, 'mirugasiridam': 4,
    'thiruvadirai': 5, 'thiruvaathirai': 5, 'thiruvathirai': 5, 'arudra': 5,
    'krittika': 2, 'karthigai': 2, 'kirthigai': 2,
    'punarpusam': 6, 'punarpoosam': 6, 'punarvasu': 6,
    'pusam': 7, 'poosam': 7, 'pushya': 7,
    'ayilyam': 8, 'aslesha': 8,
    'magam': 9, 'magha': 9,
    'pooram': 10, 'puram': 10, 'pubba': 10,
    'uthiram': 11, 'uttara': 11,
    'chithirai': 13, 'chitra': 13, 'chithra': 13,
    'swathi': 14, 'swati': 14,
    'visakam': 15, 'vishaka': 15, 'visaka': 15,
    'anusham': 16, 'anuradha': 16, 'anusam': 16,
    'kettai': 17, 'jyeshta': 17,
    'moolam': 18, 'moola': 18, 'mula': 18,
    'pooradam': 19, 'pooradhom': 19, 'purvashada': 19, 'puradam': 19,
    'uthiradam': 20, 'uttarashada': 20, 'uthiradhom': 20,
    'thiruvonam': 21, 'shravana': 21, 'sravanam': 21,
    'avittam': 22, 'dhanishta': 22, 'avitam': 22,
    'sathayam': 23, 'shatabhisha': 23, 'sadhayam': 23, 'chathayam': 23,
    'poorattathi': 24, 'purvabhadra': 24, 'pooratathi': 24,
    'uthirattathi': 25, 'uttarabhadra': 25, 'uthiratathi': 25,
    'revathi': 26, 'revati': 26,
    'aswini': 0, 'ashwini': 0, 'aswathi': 0,
    'rohini': 3,
}

def nak_to_index(name):
    if not name:
        return None
    key = name.strip().lower()
    if key in NAK_INDEX:
        return NAK_INDEX[key]
    if key in NAK_ALIASES:
        return NAK_ALIASES[key]
    return None

def lon_to_nak_pada(deg):
    deg = deg % 360.0
    total_pada = int(deg / (13.0 + 1/3.0) * 4)
    nak_idx = int(deg / (13.0 + 1/3.0))
    if nak_idx >= 27:
        nak_idx = 26
    pada = (total_pada % 4) + 1
    return nak_idx, pada

def parse_time(time_str):
    m = re.match(r'(\d+):(\d+)\s*(AM|PM|am|pm)', time_str.strip(), re.IGNORECASE)
    if not m:
        return None, None
    h, mn, ampm = int(m.group(1)), int(m.group(2)), m.group(3).upper()
    if ampm == 'PM' and h != 12:
        h += 12
    if ampm == 'AM' and h == 12:
        h = 0
    return h, mn

def parse_date(date_str):
    parts = date_str.strip().split('/')
    return int(parts[2]), int(parts[1]), int(parts[0])   # D/M/YYYY

def get_ics_planets(record):
    result = {}
    for pp in record.get('planetary_positions', []):
        pname = pp['planet'].replace('(R)', '').replace('(r)', '').strip()
        if pname in PLANET_ORDER:
            nak_name = pp.get('star_name', '').split()[0] if pp.get('star_name') else ''
            pada_str = pp.get('pada', '0')
            try:
                pada = int(pada_str)
            except (ValueError, TypeError):
                pada = 0
            result[pname] = {
                'nak_idx': nak_to_index(nak_name),
                'pada': pada,
                'nak_name': nak_name,
            }
    return result

def main():
    with open(DATA_JSON) as f:
        records = json.load(f)

    engine = VakyaTableEngine(DATA_DIR)

    py_results = {}
    skipped = []
    errors = []
    for idx, rec in enumerate(records):
        year, month, day = parse_date(rec['date_of_birth'])
        h, mn = parse_time(rec['time_of_birth'])
        if h is None:
            skipped.append((idx, rec['date_of_birth'], rec['time_of_birth']))
            continue
        try:
            dt = datetime(year, month, day, h, mn)
            result = engine.compute(dt, LAT, LON, TZ)
            py_results[idx] = {
                p: result[p]['longitude'] for p in PLANET_ORDER if p in result
            }
        except Exception as e:
            errors.append((idx, str(e)))

    print(f"Total records:        {len(records)}")
    print(f"Python chart results: {len(py_results)}")
    print(f"Skipped (bad time):   {len(skipped)}")
    for idx, d, t in skipped:
        print(f"   - idx {idx}: {d} {t}")
    if errors:
        print(f"Engine errors:        {len(errors)}")
        for idx, e in errors:
            print(f"   - idx {idx}: {e}")
    print()

    nak_stats  = {p: {'total': 0, 'match': 0} for p in PLANET_ORDER}
    pada_stats = {p: {'total': 0, 'match': 0} for p in PLANET_ORDER}
    pada_fail_cases = []

    for idx in sorted(py_results.keys()):
        pr = py_results[idx]
        ics = get_ics_planets(records[idx])
        case_fails = []
        for pname in PLANET_ORDER:
            if pname not in ics or ics[pname]['nak_idx'] is None:
                continue
            plon = pr.get(pname)
            if plon is None:
                continue
            p_nak_idx, p_pada = lon_to_nak_pada(plon)
            i_nak_idx = ics[pname]['nak_idx']
            i_pada    = ics[pname]['pada']

            nak_stats[pname]['total'] += 1
            pada_stats[pname]['total'] += 1
            nak_ok  = (p_nak_idx == i_nak_idx)
            pada_ok = (p_nak_idx == i_nak_idx and p_pada == i_pada)
            if nak_ok:
                nak_stats[pname]['match'] += 1
            if pada_ok:
                pada_stats[pname]['match'] += 1
            else:
                case_fails.append({
                    'planet': pname, 'plon': plon,
                    'p_nak': NAKSHATRAS[p_nak_idx], 'p_pada': p_pada,
                    'i_nak': ics[pname]['nak_name'], 'i_pada': i_pada,
                    'nak_ok': nak_ok,
                })
        if case_fails:
            pada_fail_cases.append({'idx': idx, 'rec': records[idx], 'fails': case_fails})

    report = []
    report.append("=" * 78)
    report.append("PYTHON VakyaTableEngine vs STORED ICS REFERENCE — 729 cases")
    report.append("=" * 78)
    report.append("")
    report.append(f"{'Planet':<10} {'N':>5} {'Nak Match':>10} {'Nak%':>8} "
                  f"{'Pada Match':>11} {'Pada%':>8} {'PadaFail':>9}")
    report.append("-" * 70)
    tot_n = tot_nak = tot_pada = 0
    for p in PLANET_ORDER:
        n  = pada_stats[p]['total']
        nm = nak_stats[p]['match']
        pm = pada_stats[p]['match']
        nak_pct  = 100.0 * nm / n if n else 0.0
        pada_pct = 100.0 * pm / n if n else 0.0
        report.append(f"{p:<10} {n:>5} {nm:>10} {nak_pct:>7.2f}% "
                      f"{pm:>11} {pada_pct:>7.2f}% {n-pm:>9}")
        tot_n += n; tot_nak += nm; tot_pada += pm
    report.append("-" * 70)
    report.append(f"{'TOTAL':<10} {tot_n:>5} {tot_nak:>10} {100.0*tot_nak/tot_n:>7.2f}% "
                  f"{tot_pada:>11} {100.0*tot_pada/tot_n:>7.2f}% {tot_n-tot_pada:>9}")
    report.append("")
    report.append(f"Overall Nakshatra match: {tot_nak}/{tot_n} = {100.0*tot_nak/tot_n:.2f}%")
    report.append(f"Overall Pada match:      {tot_pada}/{tot_n} = {100.0*tot_pada/tot_n:.2f}%")
    report.append("")
    report.append(f"── Pada Mismatch Cases: {len(pada_fail_cases)} records ──")
    report.append("")
    for fc in pada_fail_cases:
        idx = fc['idx']
        rec = fc['rec']
        report.append(f"[idx {idx}] {rec['date_of_birth']} {rec['time_of_birth']}")
        for d in fc['fails']:
            tag = "" if d['nak_ok'] else "  [NAK DIFFERS]"
            report.append(f"   {d['planet']:<9} Py={d['plon']:8.4f}° "
                          f"({d['p_nak']} p{d['p_pada']})  vs  "
                          f"ICS=({d['i_nak']} p{d['i_pada']}){tag}")
        report.append("")

    text = "\n".join(report)
    print(text)

    out_path = "/home/user/Astrology-App/java_harness/python_vs_ics_729.txt"
    with open(out_path, 'w') as f:
        f.write(text + "\n")
    print(f"\nReport saved to: {out_path}")

if __name__ == '__main__':
    main()
