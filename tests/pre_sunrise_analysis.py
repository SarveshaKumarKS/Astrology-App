"""Check correlation between pre-sunrise births and Mercury errors."""
import json, re, sys
from datetime import datetime, timedelta, date
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

try:
    import ephem
    HAS_EPHEM = True
except ImportError:
    HAS_EPHEM = False

LAT, LON = 11.6643, 78.146

def get_sunrise_info(dt_utc):
    """Returns (is_pre_sunrise, vinadi, vakya_date)"""
    if not HAS_EPHEM:
        return False, 0, dt_utc.date()
    obs = ephem.Observer()
    obs.lat = str(LAT); obs.lon = str(LON); obs.pressure = 0
    obs.date = dt_utc.strftime('%Y/%m/%d %H:%M:%S')
    sr = obs.previous_rising(ephem.Sun())
    sr_utc = sr.datetime()
    elapsed_hours = (dt_utc - sr_utc).total_seconds() / 3600.0
    if elapsed_hours < 0: elapsed_hours += 24.0
    vinadi = int(elapsed_hours * 2.5) * 60
    sr_local = sr_utc + timedelta(hours=5.5)
    # Check if birth is pre-sunrise on its own day
    obs2 = ephem.Observer()
    obs2.lat = str(LAT); obs2.lon = str(LON); obs2.pressure = 0
    birth_local_date = (dt_utc + timedelta(hours=5.5)).date()
    obs2.date = f'{birth_local_date.year}/{birth_local_date.month}/{birth_local_date.day} 00:00:00'
    sr_today = obs2.next_rising(ephem.Sun()).datetime()
    sr_today_local = sr_today + timedelta(hours=5.5)
    birth_local = dt_utc + timedelta(hours=5.5)
    is_pre_sunrise = birth_local < sr_today_local
    return is_pre_sunrise, vinadi, sr_local.date()

engine = VakyaTableEngine(str(VAKYA_DIR))
with open(DATA_FILE, encoding="utf-8") as f: data = json.load(f)
with open(CLEAN_FILE, encoding="utf-8") as f: clean = json.load(f)
clean_cases = clean['clean_cases']

pre_large = pre_small = post_large = post_small = 0
pre_errors = []; post_errors = []

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
        raw = engine.compute(ist, LAT, LON, 5.5)
        eng_lon = raw['Mercury']['longitude']
        err = abs(signed_diff(eng_lon, ics_lon))
        is_pre, vinadi, vd = get_sunrise_info(dt_utc)

        if is_pre:
            pre_errors.append(err)
            if err > 0.5: pre_large += 1
            else: pre_small += 1
        else:
            post_errors.append(err)
            if err > 0.5: post_large += 1
            else: post_small += 1
    except: pass

total_pre = pre_large + pre_small
total_post = post_large + post_small
print(f"Pre-sunrise births: {total_pre} total")
print(f"  Large error (>0.5°): {pre_large} ({100*pre_large/max(1,total_pre):.1f}%)")
print(f"  Small error (≤0.5°): {pre_small} ({100*pre_small/max(1,total_pre):.1f}%)")
if pre_errors: print(f"  Mean abs error: {sum(pre_errors)/len(pre_errors):.4f}°, Max: {max(pre_errors):.4f}°")

print(f"\nPost-sunrise births: {total_post} total")
print(f"  Large error (>0.5°): {post_large} ({100*post_large/max(1,total_post):.1f}%)")
print(f"  Small error (≤0.5°): {post_small} ({100*post_small/max(1,total_post):.1f}%)")
if post_errors: print(f"  Mean abs error: {sum(post_errors)/len(post_errors):.4f}°, Max: {max(post_errors):.4f}°")
