#!/usr/bin/env python3
"""
Run the 10 uploaded test cases through both Python VakyaTableEngine and Java harness.
Prints nakshatra + pada for every planet from both engines, with match status.
"""
import subprocess, sys, re
from datetime import datetime

sys.path.insert(0, '/home/user/Astrology-App/backend')
from astrology.vakya_table_engine import VakyaTableEngine

JAVA_HARNESS_DIR = '/home/user/Astrology-App/java_harness'
DATA_DIR         = '/home/user/Astrology-App/backend/astrology/data/vakya'
TZ               = 5.5   # IST for all cities

PLANET_ORDER = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu']
NAKSHATRAS = [
    "Aswini","Bharani","Karthigai","Rohini","Mirugasirisha","Thiruvaathirai",
    "Punarpoosam","Poosam","Ayilyam","Magam","Pooram","Uthiram","Hastham",
    "Chithirai","Swathi","Visakam","Anusham","Kettai","Moolam","Pooradam",
    "Uthiradam","Thiruvonam","Avittam","Sathayam","Poorattathi","Uthirattathi",
    "Revathi"
]

def lon_to_nak_pada(deg):
    deg = deg % 360.0
    nak_idx = int(deg / (40.0/3.0))
    if nak_idx >= 27: nak_idx = 26
    pada = (int(deg / (40.0/3.0) * 4) % 4) + 1
    return NAKSHATRAS[nak_idx], pada

# ── 10 test cases (date DD/MM/YYYY) ──────────────────────────────────────────
CASES = [
    {"label": "Case 1  Tamil New Year Day",          "date": "14/04/1985", "time": "06:00", "place": "Chennai",     "lat": 13.0827, "lon": 80.2707},
    {"label": "Case 2  Pre-sunrise",                  "date": "06/01/1995", "time": "01:30", "place": "Salem",       "lat": 11.6643, "lon": 78.1850},
    {"label": "Case 3  Month Boundary",               "date": "15/06/2010", "time": "09:00", "place": "Trichy",      "lat": 10.7905, "lon": 78.7047},
    {"label": "Case 4  Last Day Tamil Year",          "date": "13/04/2019", "time": "20:00", "place": "Coimbatore",  "lat": 11.0168, "lon": 76.9558},
    {"label": "Case 6  Pre-Fourier Year",             "date": "15/11/1963", "time": "16:00", "place": "Madurai",     "lat":  9.9252, "lon": 78.1198},
    {"label": "Case 7  Post-Fourier Year (2026)",     "date": "06/06/2026", "time": "12:00", "place": "Delhi",       "lat": 28.6139, "lon": 77.2090},
    {"label": "Case 8  High Latitude",                "date": "21/06/2005", "time": "07:00", "place": "Chandigarh",  "lat": 30.7333, "lon": 76.7794},
    {"label": "Case 9  Low Latitude",                 "date": "22/12/2015", "time": "17:30", "place": "Kanyakumari", "lat":  8.0883, "lon": 77.5385},
    {"label": "Case 10 Independence Midnight",        "date": "15/08/1947", "time": "00:00", "place": "Bombay",      "lat": 19.0760, "lon": 72.8777},
]

def parse_case(c):
    d, m, y = c["date"].split("/")
    h, mn   = c["time"].split(":")
    return int(y), int(m), int(d), int(h), int(mn)

# ── Java harness ──────────────────────────────────────────────────────────────
java_input = []
for i, c in enumerate(CASES):
    y, mo, d, h, mn = parse_case(c)
    java_input.append(f"{i}|{y}|{mo}|{d}|{h}|{mn}|{c['lat']}|{c['lon']}|{TZ}")

proc = subprocess.run(
    ['java', '-cp', f'{JAVA_HARNESS_DIR}/out', 'VakkiamEngine', DATA_DIR],
    input='\n'.join(java_input), capture_output=True, text=True, timeout=60
)
java_out = {}
for line in proc.stdout.strip().split('\n'):
    if not line.strip(): continue
    parts = line.split('|')
    if len(parts) < 10: continue
    idx = int(parts[0])
    java_out[idx] = {PLANET_ORDER[i]: float(parts[i+1]) for i in range(9)}

# ── Python engine ─────────────────────────────────────────────────────────────
engine   = VakyaTableEngine(DATA_DIR)
py_out   = {}
py_vinfo = {}   # vinadi + vakya_date
from datetime import timedelta
for i, c in enumerate(CASES):
    y, mo, d, h, mn = parse_case(c)
    dt = datetime(y, mo, d, h, mn)
    result = engine.compute(dt, c['lat'], c['lon'], TZ)
    py_out[i]   = {p: result[p]['longitude'] for p in PLANET_ORDER if p in result}
    dt_utc = dt - timedelta(hours=TZ)
    vinadi, vdate = engine._vinadi_and_vakya_date(dt_utc, c['lat'], c['lon'], TZ)
    py_vinfo[i] = (vinadi, vdate)

# ── Print results ─────────────────────────────────────────────────────────────
SEP = "=" * 85

for i, c in enumerate(CASES):
    y, mo, d, h, mn = parse_case(c)
    vinadi, vdate = py_vinfo[i]

    print(SEP)
    print(f"  {c['label']}")
    print(f"  {d:02d}/{mo:02d}/{y}  {h:02d}:{mn:02d} IST  |  {c['place']} "
          f"(lat={c['lat']}, lon={c['lon']})")
    print(f"  Vinadi: {vinadi}  |  Vakya date: {vdate}")
    print()
    print(f"  {'Planet':<10} {'Python Lon':>11}  {'Py Nak+Pada':<24} "
          f"{'Java Lon':>10}  {'Java Nak+Pada':<24} Match")
    print("  " + "-" * 82)

    all_match = True
    for p in PLANET_ORDER:
        plon = py_out[i].get(p)
        jlon = java_out.get(i, {}).get(p)
        if plon is None and jlon is None:
            continue
        py_nak, py_pada = lon_to_nak_pada(plon) if plon is not None else ("?", 0)
        jv_nak, jv_pada = lon_to_nak_pada(jlon)  if jlon is not None else ("?", 0)

        match = "✓" if (py_nak == jv_nak and py_pada == jv_pada) else "✗"
        if match == "✗": all_match = False

        py_str = f"{py_nak} p{py_pada}" if plon is not None else "—"
        jv_str = f"{jv_nak} p{jv_pada}" if jlon is not None else "—"
        py_lon_str = f"{plon:9.4f}°" if plon is not None else "         "
        jv_lon_str = f"{jlon:9.4f}°" if jlon is not None else "         "

        print(f"  {p:<10} {py_lon_str}  {py_str:<24} {jv_lon_str}  {jv_str:<24} {match}")

    print(f"\n  → {'ALL PLANETS MATCH ✓' if all_match else 'MISMATCH DETECTED ✗'}")
    print()

print(SEP)
print("DONE")
