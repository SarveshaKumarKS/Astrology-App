"""Check if large-error Mercury cases have rows crossing a retrograde boundary."""
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

engine = VakyaTableEngine(str(VAKYA_DIR))
with open(DATA_FILE, encoding="utf-8") as f: data = json.load(f)
with open(CLEAN_FILE, encoding="utf-8") as f: clean = json.load(f)
clean_cases = clean['clean_cases']

# For each Mercury case, get today and tomorrow raw arcsec
def get_mercury_info(ist):
    dt_utc = ist - timedelta(hours=5.5)
    vinadi, vakya_date = engine._vinadi_and_vakya_date(dt_utc, 11.6643, 78.146, 5.5)
    gy, tamil_month, day_in_month = engine._date_to_tamil_month_day(vakya_date)
    C, D, E, F = engine._ky_year_arithmetic(gy)
    t_month, t_day = engine._next_tamil_day(tamil_month, day_in_month)
    today = engine._planet_raw_arcsec('Mercury', C, D, E, F, tamil_month, day_in_month)
    tomorrow = engine._planet_raw_arcsec('Mercury', C, D, E, F, t_month, t_day)
    return today, tomorrow, vinadi

large_error = []
zero_error = []

for idx in clean_cases:
    rec = data[idx]
    pp = {p.get("planet","").replace("(R)","").strip(): p for p in rec.get("planetary_positions",[])}
    ics_lon = parse_lon(pp.get("Mercury",{}).get("absolute_longitude",""))
    if ics_lon is None: continue

    dd,mm,yy = map(int, rec["date_of_birth"].split("/"))
    h,m = parse_time(rec["time_of_birth"])
    ist = datetime(yy,mm,dd,h,m,0)

    try:
        today, tomorrow, vinadi = get_mercury_info(ist)
        raw = engine.compute(ist, 11.6643, 78.146, 5.5)
        eng_lon = raw['Mercury']['longitude']
        err = signed_diff(eng_lon, ics_lon)

        if today is None or tomorrow is None: continue

        # Check if today and tomorrow use the SAME direction (both forward or both backward)
        # Direction within lj_interpolate: is it going backward?
        going_back = today > tomorrow
        abs3 = abs(today - tomorrow)
        if abs3 > 180000:
            going_back = not going_back

        info = {
            'idx': idx,
            'err': err,
            'today': today,
            'tomorrow': tomorrow,
            'going_back': going_back,
            'abs3': abs3,
            'date': rec['date_of_birth'],
        }

        if abs(err) > 0.5:
            large_error.append(info)
        else:
            zero_error.append(info)
    except: pass

print(f"Large error cases: {len(large_error)}, Zero error cases: {len(zero_error)}")
print()

# Check going_back distribution
back_large = sum(1 for x in large_error if x['going_back'])
back_zero = sum(1 for x in zero_error if x['going_back'])
print(f"Large error - going backward: {back_large} ({100*back_large/max(1,len(large_error)):.1f}%)")
print(f"Zero error - going backward: {back_zero} ({100*back_zero/max(1,len(zero_error)):.1f}%)")
print()

# Check: for large error cases, what direction does ICS have?
print("Large error cases - engine vs ICS direction:")
ics_back = 0
for x in large_error:
    eng_today = x['today'] / 3600
    ics_lon = parse_lon(data[x['idx']].get("planetary_positions", [{}]))
    # Use err sign to determine ICS direction
    # If engine goes forward but ICS goes backward, err would be positive (eng > ics)
    # Actually let me just check: does ICS require retrograde motion?
    pass

# Compare today direction with error sign
print("Correlation: engine direction vs error sign for large errors:")
for x in large_error[:10]:
    direction = "BACKWARD" if x['going_back'] else "FORWARD"
    err_sign = "+" if x['err'] > 0 else "-"
    print(f"  idx={x['idx']} date={x['date']} dir={direction} err={x['err']:+.2f}°")

print()
print("Sample zero error cases:")
for x in zero_error[:5]:
    direction = "BACKWARD" if x['going_back'] else "FORWARD"
    print(f"  idx={x['idx']} date={x['date']} dir={direction} err={x['err']:+.4f}°")

print()
# Key question: for large error cases where engine goes FORWARD, what would
# be the ICS "today" and "tomorrow" values?
print("What ICS expects (computed from ICS lon and vinadi):")
for x in large_error[:5]:
    idx = x['idx']
    rec = data[idx]
    pp = {p.get("planet","").replace("(R)","").strip(): p for p in rec.get("planetary_positions",[])}
    ics_lon = parse_lon(pp.get("Mercury",{}).get("absolute_longitude",""))

    today = x['today'] / 3600  # engine today in degrees
    tomorrow = x['tomorrow'] / 3600  # engine tomorrow in degrees
    err = x['err']

    # ICS result = engine result - err
    ics_result = ics_lon

    # What today/tomorrow would give ics_result with the same vinadi?
    # If using same today, what tomorrow needed?
    dd,mm,yy = map(int, rec["date_of_birth"].split("/"))
    h,m = parse_time(rec["time_of_birth"])
    ist = datetime(yy,mm,dd,h,m,0)
    dt_utc = ist - timedelta(hours=5.5)
    vinadi, vd = engine._vinadi_and_vakya_date(dt_utc, 11.6643, 78.146, 5.5)[:2]

    # ICS formula: ics = today + (tomorrow-today)*vinadi/3600 (if forward)
    # tomorrow_ics = (ics - today) * 3600/vinadi + today
    # tomorrow_needed = today_arcsec + (ics_arcsec - today_arcsec) * 3600/vinadi
    today_arcsec = x['today']
    ics_arcsec = ics_lon * 3600
    if vinadi > 0:
        tomorrow_needed = today_arcsec + (ics_arcsec - today_arcsec) * 3600.0 / vinadi
    else:
        tomorrow_needed = today_arcsec

    print(f"  idx={idx}: today={today:.2f}°, tomorrow_engine={tomorrow:.2f}°, tomorrow_needed={tomorrow_needed/3600:.2f}°")
    print(f"    diff_engine={tomorrow-today:+.2f}°, diff_needed={(tomorrow_needed/3600-today):+.2f}°")
    # The diff between needed and engine tomorrow:
    delta = tomorrow_needed/3600 - tomorrow
    print(f"    tomorrow_delta (needed-engine) = {delta:+.4f}°")
