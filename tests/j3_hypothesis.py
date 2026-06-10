"""Test hypothesis: j3=0 when vin_off>=0, j3=1 when vin_off<0.
If the JADX decompilation incorrectly set j3=1 in the else branch,
then the init_gha>=30 correction only fires when vin_off<0.
This would explain bimodal distribution: 62% correct vs 38% wrong.
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

def compute_raw_arcsec_j3variant(engine, planet, C, D, E, F, tamil_month, day_in_month, j3_mode='always1'):
    """
    Reimplements _planet_raw_arcsec with configurable j3 behavior:
    j3_mode='always1'  → j3=1 always (current Python/Java as decompiled)
    j3_mode='vin_only' → j3=1 only when vin_off<0 (hypothesis)
    j3_mode='never'    → j3=0 always (no init_gha correction)
    """
    desc = PLANET_DESC[planet]
    period = desc['period']; rows_count = desc['rows']
    split = desc['split']; col = desc['col']

    sm = SAKA_MONTHS[tamil_month - 1]
    day = C + sm[0] + day_in_month - 1
    gha = D + sm[1]
    vin = E + sm[2]
    if (F + sm[3]) > 29:
        vin += 1
    if vin >= 60: vin -= 60; gha += 1
    if gha >= 60: gha -= 60; day += 1
    init_gha = gha
    init_vin = vin

    acc_bija = 0
    for khanda, gh, bija in zip(desc['khandas'], desc['gh'], desc['bija']):
        while (day - khanda > 0) if desc['strict'] else (day - khanda >= 0):
            gha -= gh
            if gha >= 0 or day > 0:
                if gha < 0 and day > 0: gha += 60; day -= 1
                day -= khanda; acc_bija += bija
            else:
                gha += gh; break
    if day < 0: day = 0

    G = day % period
    cycle_num = day // period

    def _pick(seq): return desc['file_high'] if seq > split else desc['file_low']

    expected_cycle = cycle_num + 1
    seq_found = None
    for row_idx in range(1, rows_count + 1):
        seq = cycle_num * rows_count + row_idx
        row = engine._tables.get(_pick(seq), {}).get(seq)
        if row is None: continue
        if int(row[0]) == expected_cycle and row[1] > G:
            seq_found = seq; break
    if seq_found is None:
        seq_found = cycle_num * rows_count + rows_count

    row2 = engine._tables.get(_pick(seq_found), {}).get(seq_found)
    row1 = engine._tables.get(_pick(seq_found - 1), {}).get(seq_found - 1)
    if row1 is None or row2 is None:
        return None, None, None

    deg2, am2 = int(row2[2]), int(row2[3]); c2 = row2[col]
    deg1, am1 = int(row1[2]), int(row1[3]); c1 = row1[col]
    day2, day1 = int(row2[1]), int(row1[1])

    if deg1 < deg2 and (deg2 - deg1) > 300: deg1 += 360
    if deg1 > deg2 and (deg1 - deg2) > 300: deg2 += 360

    b_arcsec = acc_bija * 60
    pos1 = (c1 * acc_bija + b_arcsec) + ((deg1 * 60 + am1) * 60)
    pos2 = (b_arcsec + acc_bija * c2) + ((deg2 * 60 + am2) * 60)
    if pos1 < 0 or pos2 < 0:
        pos1 += FULL_CIRCLE_ARCSEC; pos2 += FULL_CIRCLE_ARCSEC

    if abs(abs(pos2) - abs(pos1)) <= 1080000:
        diff = abs(pos2 - pos1); wrapped = False
    else:
        diff = (pos1 + FULL_CIRCLE_ARCSEC) - pos2; wrapped = True
    diff = abs(diff)

    day_span = day2 - day1 or 1
    doff = G - day1
    vin_off = vin - init_vin

    # KEY: j3 behavior
    if vin_off < 0:
        vin_off += 60
        gha -= 1
        j3 = 1  # always borrow correction
    else:
        j3 = 1 if j3_mode == 'always1' else 0  # hypothesis: 0 when vin_off>=0

    gha_off = gha - init_gha
    if gha_off < 0:
        gha_off += 60
        doff -= j3  # j3 controls whether we subtract 1 day

    doff_adj = doff
    if init_gha >= 30:
        doff_adj += j3  # j3 controls whether we add 1 day

    frac_num = ((doff_adj * 60 + gha_off) * 60) + vin_off
    interp = (diff / (day_span * 60 * 60)) * frac_num

    if wrapped: pos1 += FULL_CIRCLE_ARCSEC
    result_arcsec = (pos1 - interp) if pos1 > pos2 else (pos1 + interp)
    result_arcsec = int(result_arcsec) % FULL_CIRCLE_ARCSEC
    return result_arcsec / 3600.0, vin_off, init_gha

engine = VakyaTableEngine(str(VAKYA_DIR))
with open(DATA_FILE, encoding="utf-8") as f: data = json.load(f)
with open(CLEAN_FILE, encoding="utf-8") as f: clean = json.load(f)
clean_cases = clean['clean_cases']

# Test all three modes
results = {'always1': [], 'vin_only': [], 'never': []}
details = []

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
        t_month, t_day = engine._next_tamil_day(tamil_month, day_in_month)

        row = {}
        for mode in ['always1', 'vin_only', 'never']:
            today_lon, vin_off, init_gha = compute_raw_arcsec_j3variant(
                engine, 'Mercury', C, D, E, F, tamil_month, day_in_month, j3_mode=mode)
            tomorrow_lon, _, _ = compute_raw_arcsec_j3variant(
                engine, 'Mercury', C, D, E, F, t_month, t_day, j3_mode=mode)
            if today_lon is None or tomorrow_lon is None: continue

            # lj_interpolate
            j = today_lon * 3600; j2 = tomorrow_lon * 3600
            going_back = j > j2
            abs3 = abs(j - j2)
            if abs3 > 180000:
                going_back = not going_back
                if going_back: abs3 = (FULL_CIRCLE_ARCSEC - abs(j2)) + abs(j)
                else: abs3 = (FULL_CIRCLE_ARCSEC - abs(j)) + abs(j2)
            d_interp = (abs3 / 3600.0) * vinadi
            d2 = (j - d_interp) if going_back else (j + d_interp)
            if d2 < 0: d2 += FULL_CIRCLE_ARCSEC
            lon_result = d2 / 3600.0
            if lon_result >= 360: lon_result -= 360

            err = abs(signed_diff(lon_result, ics_lon))
            row[mode] = {'err': err, 'lon': lon_result, 'vin_off_raw': vin_off, 'init_gha': init_gha}
            results[mode].append(err)

        if len(row) == 3:
            details.append({'idx': idx, **row, 'ics': ics_lon,
                           'vin_off_raw': row['always1']['vin_off_raw'],
                           'init_gha': row['always1']['init_gha'],
                           'date': rec['date_of_birth']})
    except: pass

# Summary
print("=" * 60)
print("ACCURACY COMPARISON (Mercury, clean cases)")
print("=" * 60)
for mode in ['always1', 'vin_only', 'never']:
    errs = results[mode]
    if not errs: continue
    large = sum(1 for e in errs if e > 0.5)
    small = sum(1 for e in errs if e <= 0.5)
    mean = sum(errs)/len(errs)
    print(f"\nMode: {mode}")
    print(f"  Total: {len(errs)}")
    print(f"  Large error (>0.5°): {large} ({100*large/len(errs):.1f}%)")
    print(f"  Small error (≤0.5°): {small} ({100*small/len(errs):.1f}%)")
    print(f"  Mean abs error: {mean:.4f}°")

print()
print("=" * 60)
print("CORRELATION: vin_off vs error distribution")
print("=" * 60)
vin_zero_large = vin_zero_small = vin_neg_large = vin_neg_small = 0
for d in details:
    vin_off = d['vin_off_raw']  # after always1 mode vin correction
    err_a1 = d['always1']['err']
    err_vo = d['vin_only']['err']
    if vin_off == 0:
        if err_a1 > 0.5: vin_zero_large += 1
        else: vin_zero_small += 1
    else:  # vin_off was negative (got corrected)
        if err_a1 > 0.5: vin_neg_large += 1
        else: vin_neg_small += 1

tz = vin_zero_large + vin_zero_small
tn = vin_neg_large + vin_neg_small
print(f"vin_off was 0 (no borrow): {tz} cases")
print(f"  Large error (always1): {vin_zero_large} ({100*vin_zero_large/max(1,tz):.1f}%)")
print(f"  Small error (always1): {vin_zero_small} ({100*vin_zero_small/max(1,tz):.1f}%)")
print(f"vin_off was <0 (borrow): {tn} cases")
print(f"  Large error (always1): {vin_neg_large} ({100*vin_neg_large/max(1,tn):.1f}%)")
print(f"  Small error (always1): {vin_neg_small} ({100*vin_neg_small/max(1,tn):.1f}%)")

# Detailed comparison for the paradox cases
print()
print("=" * 60)
print("SPOT CHECK: large-error cases, compare modes")
print("=" * 60)
large_error_cases = [d for d in details if d['always1']['err'] > 0.5]
for d in large_error_cases[:8]:
    a1 = d['always1']
    vo = d['vin_only']
    ne = d['never']
    print(f"idx={d['idx']} date={d['date']} vin_off={d['vin_off_raw']} init_gha={d['init_gha']}")
    print(f"  ICS: {d['ics']:.4f}°")
    print(f"  always1: {a1['lon']:.4f}° (err={a1['err']:.4f}°)")
    print(f"  vin_only: {vo['lon']:.4f}° (err={vo['err']:.4f}°)")
    print(f"  never:    {ne['lon']:.4f}° (err={ne['err']:.4f}°)")

print()
print("SPOT CHECK: small-error cases, verify vin_only doesn't break them")
small_error_cases = [d for d in details if d['always1']['err'] <= 0.1]
for d in small_error_cases[:8]:
    a1 = d['always1']
    vo = d['vin_only']
    ne = d['never']
    print(f"idx={d['idx']} date={d['date']} vin_off={d['vin_off_raw']} init_gha={d['init_gha']}")
    print(f"  ICS: {d['ics']:.4f}°")
    print(f"  always1: {a1['lon']:.4f}° (err={a1['err']:.4f}°)")
    print(f"  vin_only: {vo['lon']:.4f}° (err={vo['err']:.4f}°)")
    print(f"  never:    {ne['lon']:.4f}° (err={ne['err']:.4f}°)")
