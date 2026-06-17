#!/usr/bin/env python3
"""
Compare engine output for the 10 uploaded cases against the EXPECTED reference
output (Tamil nakshatra+pada from 8d965391-geminicode...json).
"""
import sys
from datetime import datetime, timedelta

sys.path.insert(0, '/home/user/Astrology-App/backend')
from astrology.vakya_table_engine import VakyaTableEngine

DATA_DIR = '/home/user/Astrology-App/backend/astrology/data/vakya'
TZ = 5.5

PLANET_ORDER = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu']
NAKSHATRAS = [
    "Aswini","Bharani","Karthigai","Rohini","Mirugasirisha","Thiruvaathirai",
    "Punarpoosam","Poosam","Ayilyam","Magam","Pooram","Uthiram","Hastham",
    "Chithirai","Swathi","Visakam","Anusham","Kettai","Moolam","Pooradam",
    "Uthiradam","Thiruvonam","Avittam","Sathayam","Poorattathi","Uthirattathi",
    "Revathi"
]

# Tamil nakshatra → canonical index
TA_NAK = {
    "அஸ்வினி":0, "பரணி":1, "கிருத்திகை":2, "ரோஹிணி":3, "மிருகசீர்ஷம்":4,
    "திருவாதிரை":5, "புனர்பூசம்":6, "பூசம்":7, "ஆயில்யம்":8, "மகம்":9,
    "பூரம்":10, "உத்திரம்":11, "உத்திரபல்குனி":11, "ஹஸ்தம்":12, "சித்திரை":13,
    "ஸ்வாதி":14, "சுவாதி":14, "விசாகம்":15, "வீசாகம்":15, "அனுஷம்":16,
    "கேட்டை":17, "மூலம்":18, "பூராடம்":19, "உத்திராடம்":20, "திருவோணம்":21,
    "அவிட்டம்":22, "சதயம்":23, "பூரட்டாதி":24, "உத்திரட்டாதி":25, "ரேவதி":26,
}
# Tamil planet → English
TA_PLANET = {
    "லக்னம்":"Lagnam", "சூரியன்":"Sun", "சந்திரன்":"Moon", "செவ்வாய்":"Mars",
    "குரு":"Jupiter", "சுக்ரன்":"Venus", "சனி":"Saturn", "புதன்":"Mercury",
    "ராகு":"Rahu", "கேது":"Ketu",
}

def lon_to_nak_pada(deg):
    deg = deg % 360.0
    nak_idx = int(deg / (40.0/3.0))
    if nak_idx >= 27: nak_idx = 26
    pada = (int(deg / (40.0/3.0) * 4) % 4) + 1
    return nak_idx, pada

# ── 10 cases (same as run_10_cases.py) ──
CASES = [
    {"label":"Case 1  Tamil New Year Day", "date":"14/04/1985","time":"06:00","place":"Chennai","lat":13.0827,"lon":80.2707},
    {"label":"Case 2  Pre-sunrise",         "date":"06/01/1995","time":"01:30","place":"Salem","lat":11.6643,"lon":78.1850},
    {"label":"Case 3  Month Boundary",      "date":"15/06/2010","time":"09:00","place":"Trichy","lat":10.7905,"lon":78.7047},
    {"label":"Case 4  Last Day Tamil Year", "date":"13/04/2019","time":"20:00","place":"Coimbatore","lat":11.0168,"lon":76.9558},
    {"label":"Case 6  Pre-Fourier Year",    "date":"15/11/1963","time":"16:00","place":"Madurai","lat":9.9252,"lon":78.1198},
    {"label":"Case 7  Post-Fourier (2026)", "date":"06/06/2026","time":"12:00","place":"Delhi","lat":28.6139,"lon":77.2090},
    {"label":"Case 8  High Latitude",       "date":"21/06/2005","time":"07:00","place":"Chandigarh","lat":30.7333,"lon":76.7794},
    {"label":"Case 9  Low Latitude",        "date":"22/12/2015","time":"17:30","place":"Kanyakumari","lat":8.0883,"lon":77.5385},
    {"label":"Case 10 Independence Midnight","date":"15/08/1947","time":"00:00","place":"Bombay","lat":19.0760,"lon":72.8777},
]

# ── Expected reference tables (planet → (nak_idx, pada)) keyed by case label ──
def E(rows):
    """rows: list of (tamil_planet, tamil_nak, pada)"""
    out = {}
    for tp, tn, pd in rows:
        out[TA_PLANET[tp]] = (TA_NAK[tn], int(pd))
    return out

EXPECTED = {
 "Case 1  Tamil New Year Day": E([
    ("லக்னம்","அஸ்வினி",1),("சூரியன்","அஸ்வினி",1),("சந்திரன்","திருவோணம்",3),
    ("செவ்வாய்","கிருத்திகை",1),("குரு","திருவோணம்",3),("சுக்ரன்","ரேவதி",2),
    ("சனி","வீசாகம்",3),("புதன்","உத்திரட்டாதி",1),("ராகு","பரணி",4),("கேது","விசாகம்",2)]),
 "Case 2  Pre-sunrise": E([
    ("லக்னம்","ஸ்வாதி",1),("சூரியன்","பூராடம்",3),("சந்திரன்","சதயம்",3),
    ("செவ்வாய்","மகம்",2),("குரு","அனுஷம்",3),("சுக்ரன்","அனுஷம்",1),
    ("சனி","அவிட்டம்",4),("புதன்","உத்திராடம்",4),("ராகு","ஸ்வாதி",3),("கேது","பரணி",2)]),
 "Case 3  Month Boundary": E([
    ("லக்னம்","பூசம்",3),("சூரியன்","மிருகசீர்ஷம்",2),("சந்திரன்","பூசம்",1),
    ("செவ்வாய்","மகம்",3),("குரு","உத்திரட்டாதி",2),("சுக்ரன்","பூசம்",1),
    ("புதன்","மிருகசீர்ஷம்",2),("ராகு","பூராடம்",2),("கேது","திருவாதிரை",4)]),
 # Case 3 "Unknown" = Saturn உத்திரபல்குனி p2
 "Case 4  Last Day Tamil Year": E([
    ("லக்னம்","விசாகம்",1),("சூரியன்","ரேவதி",4),("சந்திரன்","ஆயில்யம்",1),
    ("செவ்வாய்","ரோஹிணி",2),("குரு","மூலம்",1),("சுக்ரன்","பூரட்டாதி",3),
    ("புதன்","உத்திரட்டாதி",2),("ராகு","புனர்பூசம்",3),("கேது","உத்திராடம்",1)]),
 # Case 4 "Unknown" = Saturn பூராடம் p2
 "Case 6  Pre-Fourier Year": E([
    ("லக்னம்","ரேவதி",4),("சூரியன்","விசாகம்",3),("சந்திரன்","ஸ்வாதி",4),
    ("செவ்வாய்","கேட்டை",2),("குரு","ரேவதி",1),("சுக்ரன்","கேட்டை",1),
    ("சனி","திருவோணம்",2),("புதன்","அனுஷம்",3),("ராகு","திருவாதிரை",4),("கேது","பூராடம்",2)]),
 "Case 7  Post-Fourier (2026)": E([
    ("லக்னம்","பூரம்",1),("சூரியன்","ரோஹிணி",4),("சந்திரன்","அவிட்டம்",2),
    ("செவ்வாய்","பரணி",3),("குரு","புனர்பூசம்",4),("சுக்ரன்","புனர்பூசம்",2),
    ("சனி","உத்திரட்டாதி",2),("புதன்","திருவாதிரை",3),("ராகு","சதயம்",1),("கேது","மகம்",3)]),
 "Case 8  High Latitude": E([
    ("லக்னம்","புனர்பூசம்",3),("சூரியன்","மிருகசீர்ஷம்",4),("சந்திரன்","கேட்டை",2),
    ("செவ்வாய்","உத்திரட்டாதி",3),("குரு","ஹஸ்தம்",3),("சுக்ரன்","புனர்பூசம்",2),
    ("சனி","புனர்பூசம்",3),("புதன்","புனர்பூசம்",3),("ராகு","ரேவதி",3),("கேது","சித்திரை",1)]),
 "Case 9  Low Latitude": E([
    ("லக்னம்","மிருகசீர்ஷம்",3),("சூரியன்","மூலம்",2),("சந்திரன்","கிருத்திகை",1),
    ("செவ்வாய்","சித்திரை",2),("குரு","உத்திரபல்குனி",2),("சுக்ரன்","விசாகம்",2),
    ("சனி","அனுஷம்",3),("புதன்","பூராடம்",3),("ராகு","உத்திரபல்குனி",2),("கேது","பூரட்டாதி",4)]),
 "Case 10 Independence Midnight": E([
    ("லக்னம்","கிருத்திகை",2),("சூரியன்","ஆயில்யம்",4),("சந்திரன்","பூசம்",1),
    ("செவ்வாய்","திருவாதிரை",1),("குரு","விசாகம்",3),("சுக்ரன்","ஆயில்யம்",2),
    ("சனி","ஆயில்யம்",1),("புதன்","ஆயில்யம்",4),("ராகு","கிருத்திகை",3),("கேது","அனுஷம்",1)]),
}
# Add the "Unknown"=Saturn entries
EXPECTED["Case 3  Month Boundary"]["Saturn"] = (TA_NAK["உத்திரபல்குனி"], 2)
EXPECTED["Case 4  Last Day Tamil Year"]["Saturn"] = (TA_NAK["பூராடம்"], 2)

def parse_case(c):
    d,m,y = c["date"].split("/"); h,mn = c["time"].split(":")
    return int(y),int(m),int(d),int(h),int(mn)

engine = VakyaTableEngine(DATA_DIR)

SEP = "=" * 88
grand_total = grand_match = 0
case_summaries = []

for c in CASES:
    y,mo,d,h,mn = parse_case(c)
    dt = datetime(y,mo,d,h,mn)
    result = engine.compute(dt, c['lat'], c['lon'], TZ)
    exp = EXPECTED[c['label']]

    print(SEP)
    print(f"  {c['label']}   {c['date']} {c['time']} IST  |  {c['place']}")
    print("  " + "-"*84)
    print(f"  {'Planet':<9} {'Engine Lon':>11}  {'Engine Nak+P':<22} {'Expected Nak+P':<22} Match")
    print("  " + "-"*84)

    n_tot = n_match = 0
    fails = []
    for p in PLANET_ORDER:    # planets only (Lagnam handled separately)
        if p not in result or p not in exp:
            continue
        elon = result[p]['longitude']
        e_nak_idx, e_pada = lon_to_nak_pada(elon)
        x_nak_idx, x_pada = exp[p]
        ok = (e_nak_idx == x_nak_idx and e_pada == x_pada)
        n_tot += 1
        if ok: n_match += 1
        else: fails.append(p)
        mark = "✓" if ok else "✗"
        print(f"  {p:<9} {elon:9.4f}°  {NAKSHATRAS[e_nak_idx]+' p'+str(e_nak_idx and e_pada or e_pada):<22} "
              f"{NAKSHATRAS[x_nak_idx]+' p'+str(x_pada):<22} {mark}")

    # Lagnam (informational — astronomical Lahiri ascendant)
    lag = result.get('Lagnam') or result.get('lagnam')
    if lag and 'Lagnam' in exp:
        llon = lag['longitude']
        l_nak_idx, l_pada = lon_to_nak_pada(llon)
        x_nak_idx, x_pada = exp['Lagnam']
        ok = (l_nak_idx == x_nak_idx and l_pada == x_pada)
        mark = "✓" if ok else "✗ (info)"
        print(f"  {'Lagnam':<9} {llon:9.4f}°  {NAKSHATRAS[l_nak_idx]+' p'+str(l_pada):<22} "
              f"{NAKSHATRAS[x_nak_idx]+' p'+str(x_pada):<22} {mark}")

    grand_total += n_tot; grand_match += n_match
    status = "ALL 9 PLANETS MATCH ✓" if not fails else f"MISMATCH: {', '.join(fails)}"
    print(f"\n  → {n_match}/{n_tot} planets match.  {status}\n")
    case_summaries.append((c['label'], n_match, n_tot, fails))

print(SEP)
print("  SUMMARY (9 grahas per case, Lagnam excluded)")
print("  " + "-"*84)
for label, m, t, fails in case_summaries:
    s = "✓ perfect" if not fails else f"✗ {', '.join(fails)}"
    print(f"  {label:<34} {m}/{t}   {s}")
print("  " + "-"*84)
print(f"  GRAND TOTAL: {grand_match}/{grand_total} = {100.0*grand_match/grand_total:.2f}% planet nak+pada match vs expected")
print(SEP)
