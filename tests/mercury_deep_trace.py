"""Deep trace of Mercury computation for a specific large-error case.
Compare step-by-step with what Java should produce.
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
    if ":"in t2: h,m=map(int,t2.split(":")[:2])
    else: h=int(t2[:-2]); m=int(t2[-2:])
    if pm and h<12: h+=12
    elif not pm and h==12: h=0
    return h,m

def signed_diff(a,b): return (a-b+180.0)%360.0-180.0

engine = VakyaTableEngine(str(VAKYA_DIR))
with open(DATA_FILE, encoding="utf-8") as f: data = json.load(f)
with open(CLEAN_FILE, encoding="utf-8") as f: clean = json.load(f)

# Look at a large-error case (idx=5) and zero-error case (idx=0) side by side
for idx, label in [(5, "LARGE_ERROR"), (0, "ZERO_ERROR"), (10, "LARGE_ERROR2")]:
    rec = data[idx]
    pp = {p.get("planet","").replace("(R)","").strip(): p for p in rec.get("planetary_positions",[])}
    ics_lon = parse_lon(pp.get("Mercury",{}).get("absolute_longitude",""))
    dd,mm,yy = map(int, rec["date_of_birth"].split("/"))
    h,m = parse_time(rec["time_of_birth"])
    ist = datetime(yy,mm,dd,h,m,0)
    dt_utc = ist - timedelta(hours=5.5)

    vinadi, vakya_date = engine._vinadi_and_vakya_date(dt_utc, 11.6643, 78.146, 5.5)
    gy, tamil_month, day_in_month = engine._date_to_tamil_month_day(vakya_date)
    C, D, E, F = engine._ky_year_arithmetic(gy)
    t_month, t_day = engine._next_tamil_day(tamil_month, day_in_month)

    print(f"\n{'='*60}")
    print(f"Case idx={idx} [{label}]")
    print(f"  Date: {rec['date_of_birth']} {rec['time_of_birth']}")
    print(f"  ICS Mercury lon: {ics_lon:.4f}°")
    print(f"  vakya_date: {vakya_date}, tamil_month={tamil_month}, day_in_month={day_in_month}")
    print(f"  C={C} D={D} E={E} F={F}")
    print(f"  vinadi={vinadi}")
    print(f"  t_month={t_month} t_day={t_day}")

    # Deep trace of _planet_raw_arcsec for Mercury (today)
    planet = "Mercury"
    desc = PLANET_DESC[planet]
    period=desc['period']; rows=desc['rows']; split=desc['split']; col=desc['col']

    sm = SAKA_MONTHS[tamil_month-1]
    day = C + sm[0] + day_in_month - 1
    gha = D + sm[1]
    vin = E + sm[2]
    if (F + sm[3]) > 29: vin += 1
    if vin >= 60: vin -= 60; gha += 1
    if gha >= 60: gha -= 60; day += 1
    init_gha, init_vin = gha, vin
    day_before_reduction = day

    print(f"\n  [_planet_raw_arcsec TODAY]")
    print(f"    day_before_reduction={day_before_reduction}, gha={gha}, vin={vin}")
    print(f"    init_gha={init_gha}, init_vin={init_vin}")

    acc_bija = 0
    for ki,(khanda,gh,bija) in enumerate(zip(desc['khandas'],desc['gh'],desc['bija'])):
        count = 0
        while (day - khanda > 0) if desc['strict'] else (day - khanda >= 0):
            gha -= gh
            if gha >= 0 or day > 0:
                if gha < 0 and day > 0: gha += 60; day -= 1
                day -= khanda; acc_bija += bija; count += 1
            else:
                gha += gh; break
        if count > 0:
            print(f"    khanda[{ki}]={khanda}: reduced {count} times → day={day}, gha={gha}, acc_bija={acc_bija}")
    if day < 0: day = 0

    G = day % period; cycle_num = day // period
    expected_cycle = cycle_num + 1  # cycle_mod=None for Mercury
    print(f"    After reduction: day={day}, G={G}, cycle_num={cycle_num}, expected_cycle={expected_cycle}")
    print(f"    Post-reduction gha={gha}, vin={vin}")
    print(f"    gha_change={gha-init_gha}, vin_change={vin-init_vin}")

    # Row search
    def _pick(seq): return desc['file_high'] if seq > split else desc['file_low']
    seq_found = None
    for row_idx in range(1, rows+1):
        seq = cycle_num * rows + row_idx
        row = engine._tables.get(_pick(seq),{}).get(seq)
        if row is None: continue
        if int(row[0]) == expected_cycle and row[1] > G:
            seq_found = seq; break
    if seq_found is None:
        seq_found = cycle_num * rows + rows
    row2 = engine._tables.get(_pick(seq_found),{}).get(seq_found)
    row1 = engine._tables.get(_pick(seq_found-1),{}).get(seq_found-1)
    print(f"    seq_found={seq_found}, row1={row1}, row2={row2}")

    if row1 is None or row2 is None:
        print("    MISSING ROW!"); continue

    deg2,am2 = int(row2[2]),int(row2[3]); c2=row2[col]
    deg1,am1 = int(row1[2]),int(row1[3]); c1=row1[col]
    day2,day1 = int(row2[1]),int(row1[1])

    if deg1 < deg2 and (deg2-deg1)>300: deg1 += 360
    if deg1 > deg2 and (deg1-deg2)>300: deg2 += 360

    b_arcsec = acc_bija * 60
    pos1 = (c1*acc_bija + b_arcsec) + ((deg1*60+am1)*60)
    pos2 = (b_arcsec + acc_bija*c2) + ((deg2*60+am2)*60)
    if pos1 < 0 or pos2 < 0: pos1 += FULL_CIRCLE_ARCSEC; pos2 += FULL_CIRCLE_ARCSEC

    if abs(abs(pos2)-abs(pos1)) <= 1080000: diff = abs(pos2-pos1); wrapped=False
    else: diff=(pos1+FULL_CIRCLE_ARCSEC)-pos2; wrapped=True
    diff = abs(diff)
    print(f"    pos1={pos1} ({pos1/3600:.4f}°), pos2={pos2} ({pos2/3600:.4f}°)")
    print(f"    diff={diff} ({diff/3600:.4f}°), day_span={day2-day1}")

    day_span = day2 - day1 or 1
    doff = G - day1
    vin_off = vin - init_vin
    if vin_off < 0: vin_off += 60; gha -= 1
    gha_off = gha - init_gha
    if gha_off < 0: gha_off += 60; doff -= 1
    if init_gha >= 30: doff += 1
    frac_num = ((doff*60+gha_off)*60)+vin_off
    interp = (diff / (day_span*60*60)) * frac_num

    print(f"    doff={doff} (G-day1={G}-{day1}), gha_off={gha_off}, vin_off={vin_off}")
    print(f"    init_gha={init_gha} (>=30: {init_gha>=30})")
    print(f"    frac_num={frac_num}")
    print(f"    interp={interp:.2f} ({interp/3600:.4f}°)")

    if wrapped: pos1 += FULL_CIRCLE_ARCSEC
    result_arcsec = (pos1-interp) if pos1>pos2 else (pos1+interp)
    result_arcsec = int(result_arcsec) % FULL_CIRCLE_ARCSEC
    result_deg = result_arcsec / 3600.0
    print(f"    raw_arcsec={result_arcsec} ({result_deg:.4f}°)")

    # Also call the real engine
    raw = engine.compute(ist, 11.6643, 78.146, 5.5)
    eng_lon = raw["Mercury"]["longitude"]
    print(f"  Engine Mercury lon: {eng_lon:.4f}°")
    print(f"  ICS Mercury lon: {ics_lon:.4f}°")
    print(f"  Error: {signed_diff(eng_lon, ics_lon):+.4f}°")

    # Now compute what happens if we use JAVA's frac_num interpretation
    # In Java: doff uses j13 (G = day%116) but what about the init_gha correction?
    # Let me check: if init_gha < 30 in some cases, the +1 is not added
    print(f"\n  [JAVA EQUIVALENT CHECK]")
    # Retrace without the init_gha>=30 correction
    doff_raw = G - day1
    gha_after_red = gha + (1 if vin_off < 0 else 0)  # vin borrow already applied
    gha_off_raw = gha_after_red - init_gha
    if gha_off_raw < 0: gha_off_raw += 60; doff_raw -= 1
    # No init_gha>=30 correction
    frac_num_noadj = ((doff_raw*60+gha_off_raw)*60) + (vin - init_vin if (vin-init_vin)>=0 else vin-init_vin+60)
    print(f"  frac_num WITHOUT init_gha>=30 correction: {frac_num_noadj}")
    print(f"  frac_num WITH init_gha>=30 correction: {frac_num}")
    print(f"  init_gha={init_gha}")
