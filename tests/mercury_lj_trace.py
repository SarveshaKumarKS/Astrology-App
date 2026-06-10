"""Trace what today/tomorrow are passed to _lj_interpolate for Mercury."""
import json, re, sys
from datetime import datetime, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from astrology.vakya_table_engine import VakyaTableEngine, PLANET_DESC, SAKA_MONTHS, FULL_CIRCLE_ARCSEC

DATA_FILE = Path(__file__).parent / "astrology_data .json"
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
    if ":"in t2: h,m=map(int,t2.split(":")[:2])
    else: h=int(t2[:-2]); m=int(t2[-2:])
    if pm and h<12: h+=12
    elif not pm and h==12: h=0
    return h,m

def signed_diff(a,b): return (a-b+180.0)%360.0-180.0

engine = VakyaTableEngine(str(VAKYA_DIR))

# Patch _planet_raw_arcsec to expose today/tomorrow
original_compute = engine.compute

def patched_compute(birth_dt, lat, lon, tz_hours=5.5):
    from datetime import timedelta, date
    local_dt = birth_dt
    dt_utc = local_dt - timedelta(hours=tz_hours)
    vinadi, vakya_date = engine._vinadi_and_vakya_date(dt_utc, lat, lon, tz_hours)
    gy, tamil_month, day_in_month = engine._date_to_tamil_month_day(vakya_date)
    C, D, E, F = engine._ky_year_arithmetic(gy)
    t_month, t_day = engine._next_tamil_day(tamil_month, day_in_month)

    today_merc    = engine._planet_raw_arcsec('Mercury', C, D, E, F, tamil_month, day_in_month)
    tomorrow_merc = engine._planet_raw_arcsec('Mercury', C, D, E, F, t_month, t_day)

    return {
        'vinadi': vinadi, 'vakya_date': vakya_date,
        'tamil_month': tamil_month, 'day_in_month': day_in_month,
        't_month': t_month, 't_day': t_day,
        'C': C, 'D': D, 'E': E, 'F': F,
        'today_merc': today_merc, 'tomorrow_merc': tomorrow_merc,
    }

with open(DATA_FILE, encoding="utf-8") as f: data = json.load(f)

# Test cases: idx=5 (large error) and idx=0 (zero error)
for idx in [0, 5, 10, 11, 12, 3]:
    rec = data[idx]
    pp = {p.get("planet","").replace("(R)","").strip(): p for p in rec.get("planetary_positions",[])}
    ics_lon = parse_lon(pp.get("Mercury",{}).get("absolute_longitude",""))
    dd,mm,yy = map(int, rec["date_of_birth"].split("/"))
    h,m = parse_time(rec["time_of_birth"])
    ist = datetime(yy,mm,dd,h,m,0)

    info = patched_compute(ist, 11.6643, 78.146, 5.5)
    raw = engine.compute(ist, 11.6643, 78.146, 5.5)
    eng_lon = raw['Mercury']['longitude']

    today = info['today_merc']
    tomorrow = info['tomorrow_merc']
    vinadi = info['vinadi']

    if today is None: today = 0
    if tomorrow is None: tomorrow = today

    # Manually run _lj_interpolate logic
    j = today; j2 = tomorrow
    going_back = j > j2
    abs3 = abs(j - j2)
    if abs3 > 180000:
        going_back = not going_back
        if going_back: abs3 = (FULL_CIRCLE_ARCSEC - abs(j2)) + abs(j)
        else: abs3 = (FULL_CIRCLE_ARCSEC - abs(j)) + abs(j2)
    d_interp = (abs3 / 3600.0) * vinadi
    d2 = (j - d_interp) if going_back else (j + d_interp)
    if d2 < 0: d2 += FULL_CIRCLE_ARCSEC
    manual_lon = d2 / 3600.0
    if manual_lon >= 360: manual_lon -= 360

    err = signed_diff(eng_lon, ics_lon)

    print(f"idx={idx} [{rec['date_of_birth']} {rec['time_of_birth']}]")
    print(f"  ICS: {ics_lon:.4f}°  Engine: {eng_lon:.4f}°  Error: {err:+.4f}°")
    print(f"  vinadi={vinadi}, vakya={info['vakya_date']}, tm={info['tamil_month']}, day={info['day_in_month']}")
    print(f"  today={today} ({today/3600:.4f}°), tomorrow={tomorrow} ({tomorrow/3600:.4f}°)")
    print(f"  going_back={going_back}, abs3={abs3}, d_interp={d_interp:.2f}")
    print(f"  manual_lon={manual_lon:.4f}° (vs engine {eng_lon:.4f}°)")

    # What tomorrow would need to be for ICS result
    ics_arcsec = ics_lon * 3600
    # If going backward to get ICS: ics_arcsec = today - d_needed
    # d_needed = today - ics_arcsec
    d_needed = today - ics_arcsec
    abs3_needed = abs(d_needed) * 3600 / vinadi if vinadi > 0 else 0
    if d_needed > 0:
        tomorrow_needed = today - abs3_needed  # going backward
        print(f"  For ICS result: need today={today/3600:.2f}°, tomorrow={tomorrow_needed/3600:.2f}° (going backward)")
    else:
        tomorrow_needed = today + abs3_needed  # going forward
        print(f"  For ICS result: need today={today/3600:.2f}°, tomorrow={tomorrow_needed/3600:.2f}° (going forward)")
    print()
