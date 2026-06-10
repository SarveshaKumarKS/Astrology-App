"""
Test hypothesis: Java uses dynamic Tamil month lengths that differ by 1 day
from Python's fixed SAKA_MONTHS for certain dates.

For each case, try day_in_month-1 and see if it matches ICS better.
"""
import json, re, sys
from datetime import datetime, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from astrology.vakya_table_engine import VakyaTableEngine, PLANET_DESC, SAKA_MONTHS, FULL_CIRCLE_ARCSEC

DATA_FILE = Path(__file__).parent / "astrology_data .json"
CLEAN_FILE = Path(__file__).parent / "clean_cases.json"
VAKYA_DIR  = Path(__file__).resolve().parents[1] / "backend/astrology/data/vakya"

def parse_lon(s):
    if not s: return None
    s = str(s).strip().replace(" ", "")
    parts = re.split(r"[:.]", s)
    try:
        d=float(parts[0]); m=float(parts[1]) if len(parts)>1 else 0.0
        sec=float(parts[2]) if len(parts)>2 else 0.0
        v=d+m/60.0+sec/3600.0
        return v if 0.0<=v<360.0 else None
    except: return None

def parse_time(tob):
    t=tob.upper().replace(" ",""); pm="PM" in t
    t2=t.replace("PM","").replace("AM","")
    if ":" in t2: h,m=map(int,t2.split(":")[:2])
    else: h=int(t2[:-2]); m=int(t2[-2:])
    if pm and h<12: h+=12
    elif not pm and h==12: h=0
    return h,m

def signed_diff(a,b): return (a-b+180.0)%360.0-180.0

def lj_interp(today_deg, tomorrow_deg, vinadi):
    j = int(today_deg * 3600); j2 = int(tomorrow_deg * 3600)
    going_back = j > j2; abs3 = abs(j - j2)
    if abs3 > 180000:
        going_back = not going_back
        if going_back: abs3 = (FULL_CIRCLE_ARCSEC - abs(j2)) + abs(j)
        else: abs3 = (FULL_CIRCLE_ARCSEC - abs(j)) + abs(j2)
    d_interp = (abs3 / 3600.0) * vinadi
    d2 = (j - d_interp) if going_back else (j + d_interp)
    if d2 < 0: d2 += FULL_CIRCLE_ARCSEC
    result = d2 / 3600.0
    if result >= 360: result -= 360
    return result

engine = VakyaTableEngine(str(VAKYA_DIR))
with open(DATA_FILE, encoding="utf-8") as f: data = json.load(f)
with open(CLEAN_FILE, encoding="utf-8") as f: clean = json.load(f)
clean_cases = clean['clean_cases']

records = []

for idx in clean_cases:
    rec = data[idx]
    pp = {p.get("planet","").replace("(R)","").strip(): p for p in rec.get("planetary_positions",[])}
    ics_lon = parse_lon(pp.get("Mercury",{}).get("absolute_longitude",""))
    if ics_lon is None: continue

    dd,mm,yy = map(int, rec["date_of_birth"].split("/"))
    h,m = parse_time(rec["time_of_birth"])
    ist = datetime(yy,mm,dd,h,m,0)
    dt_utc = ist - timedelta(hours=5.5)

    try:
        vinadi, vakya_date = engine._vinadi_and_vakya_date(dt_utc, 11.6643, 78.146, 5.5)
        gy, tamil_month, day_in_month = engine._date_to_tamil_month_day(vakya_date)
        C, D, E, F = engine._ky_year_arithmetic(gy)

        # Compute today and tomorrow with day-1 offset
        def get_today_lon(dim):
            if dim < 1:
                # Go to previous Tamil month
                if tamil_month == 1:
                    prev_gy = gy - 1
                    pC, pD, pE, pF = engine._ky_year_arithmetic(prev_gy)
                    prev_month = 12
                    prev_dim = SAKA_MONTHS[11][0] + dim  # dim is 0 or negative
                    today_raw = engine._planet_raw_arcsec('Mercury', pC, pD, pE, pF, prev_month, max(1, prev_dim))
                else:
                    prev_month = tamil_month - 1
                    prev_month_days = SAKA_MONTHS[prev_month - 1]
                    prev_dim = SAKA_MONTHS[prev_month - 1 + 1][0] - SAKA_MONTHS[prev_month - 1][0] + dim
                    today_raw = engine._planet_raw_arcsec('Mercury', C, D, E, F, prev_month, max(1, prev_dim))
                return today_raw
            return engine._planet_raw_arcsec('Mercury', C, D, E, F, tamil_month, dim)

        # Standard (day_offset=0)
        t_month0, t_day0 = engine._next_tamil_day(tamil_month, day_in_month)
        today0 = engine._planet_raw_arcsec('Mercury', C, D, E, F, tamil_month, day_in_month)
        tom0 = engine._planet_raw_arcsec('Mercury', C, D, E, F, t_month0, t_day0)

        # day_in_month - 1 (Java uses 1 earlier)
        dim_m1 = day_in_month - 1
        t_month_m1, t_day_m1 = tamil_month, day_in_month  # tomorrow from Java's today = Python's today
        if dim_m1 >= 1:
            today_m1 = engine._planet_raw_arcsec('Mercury', C, D, E, F, tamil_month, dim_m1)
        else:
            # Previous month
            if tamil_month > 1:
                prev_m = tamil_month - 1
                prev_last_day = SAKA_MONTHS[tamil_month - 1][0] - SAKA_MONTHS[tamil_month - 2][0]
                today_m1 = engine._planet_raw_arcsec('Mercury', C, D, E, F, prev_m, prev_last_day)
            else:
                prev_gy = gy - 1
                pC, pD, pE, pF = engine._ky_year_arithmetic(prev_gy)
                prev_last_day = SAKA_MONTHS[12][0] - SAKA_MONTHS[11][0]
                today_m1 = engine._planet_raw_arcsec('Mercury', pC, pD, pE, pF, 12, prev_last_day)
        tom_m1 = today0  # tomorrow = Python's today

        if today0 is None or tom0 is None or today_m1 is None or tom_m1 is None:
            continue

        result0 = lj_interp(today0/3600.0, tom0/3600.0, vinadi)
        result_m1 = lj_interp(today_m1/3600.0, tom_m1/3600.0, vinadi)

        raw_result = engine.compute(ist, 11.6643, 78.146, 5.5)
        eng_lon = raw_result['Mercury']['longitude']

        err0 = abs(signed_diff(result0, ics_lon))
        err_m1 = abs(signed_diff(result_m1, ics_lon))
        err_eng = abs(signed_diff(eng_lon, ics_lon))

        records.append({
            'idx': idx,
            'date': rec['date_of_birth'],
            'time': rec['time_of_birth'],
            'ics': ics_lon,
            'eng': eng_lon,
            'err_eng': err_eng,
            'result_m1': result_m1,
            'err_m1': err_m1,
            'err0': err0,
            'vakya_date': str(vakya_date),
            'tamil_month': tamil_month,
            'day_in_month': day_in_month,
        })
    except Exception as e:
        pass

large_eng = [r for r in records if r['err_eng'] > 0.5]
small_eng = [r for r in records if r['err_eng'] <= 0.5]

print(f"Total: {len(records)}, Large error: {len(large_eng)}, Small: {len(small_eng)}")
print()

# How many large-error cases are fixed by day_offset=-1?
fixed = sum(1 for r in large_eng if r['err_m1'] < 0.5)
broken = sum(1 for r in small_eng if r['err_m1'] > 0.5)
print(f"With day_offset=-1 (Java uses previous day as today):")
print(f"  Large errors FIXED: {fixed}/{len(large_eng)} ({100*fixed/max(1,len(large_eng)):.1f}%)")
print(f"  Small errors BROKEN: {broken}/{len(small_eng)} ({100*broken/max(1,len(small_eng)):.1f}%)")

# Combined: use day_offset=-1 for large-error cases, 0 for small-error cases
# (but we can't know this in advance) → check if ALWAYS using -1 is better
err_always_m1 = [r['err_m1'] for r in records]
err_always_0 = [r['err0'] for r in records]
print()
print(f"Mean abs error (always_offset=0): {sum(err_always_0)/len(err_always_0):.4f}°")
print(f"Mean abs error (always_offset=-1): {sum(err_always_m1)/len(err_always_m1):.4f}°")
large_m1 = sum(1 for e in err_always_m1 if e > 0.5)
print(f"Large errors with offset=-1: {large_m1}/{len(records)} ({100*large_m1/len(records):.1f}%)")

print()
print("Cases fixed by -1 (first 15):")
print(f"  {'idx':>5}  {'date':>12}  {'mon':>4}  {'day':>4}  {'ICS':>8}  {'eng':>8}  {'m-1':>8}  err_eng  err_m1")
for r in [r for r in large_eng if r['err_m1'] < 0.5][:15]:
    print(f"  {r['idx']:5d}  {r['date']:>12}  {r['tamil_month']:4d}  {r['day_in_month']:4d}  {r['ics']:8.4f}  {r['eng']:8.4f}  {r['result_m1']:8.4f}  {r['err_eng']:7.4f}  {r['err_m1']:6.4f}")

print()
print("Cases NOT fixed by -1 (first 15):")
for r in [r for r in large_eng if r['err_m1'] >= 0.5][:15]:
    print(f"  {r['idx']:5d}  {r['date']:>12}  {r['tamil_month']:4d}  {r['day_in_month']:4d}  {r['ics']:8.4f}  {r['eng']:8.4f}  {r['result_m1']:8.4f}  {r['err_eng']:7.4f}  {r['err_m1']:6.4f}")

print()
print("Cases broken by -1 (first 10):")
for r in [r for r in small_eng if r['err_m1'] > 0.5][:10]:
    print(f"  {r['idx']:5d}  {r['date']:>12}  {r['tamil_month']:4d}  {r['day_in_month']:4d}  {r['ics']:8.4f}  {r['eng']:8.4f}  {r['result_m1']:8.4f}  {r['err_eng']:7.4f}  {r['err_m1']:6.4f}")

# Distribution by Tamil month
print()
print("Error distribution by Tamil month:")
import collections
for month in range(1, 13):
    cases = [r for r in records if r['tamil_month'] == month]
    if not cases: continue
    large_in_month = sum(1 for r in cases if r['err_eng'] > 0.5)
    fixed_in_month = sum(1 for r in cases if r['err_eng'] > 0.5 and r['err_m1'] < 0.5)
    print(f"  Month {month:2d}: {len(cases):3d} cases, {large_in_month:3d} large errors, {fixed_in_month:3d} fixed by day-1")
