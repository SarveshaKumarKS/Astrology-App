"""Trace Mercury khanda reduction for cases with large vs small errors.
Identifies the specific algorithmic condition causing the ~38% systematic bias.
"""
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from astrology.vakya_table_engine import VakyaTableEngine, PLANET_DESC, SAKA_MONTHS, FULL_CIRCLE_ARCSEC

DATA_FILE  = Path(__file__).parent / "astrology_data .json"
CLEAN_FILE = Path(__file__).parent / "clean_cases.json"
VAKYA_DIR  = Path(__file__).resolve().parents[1] / "backend/astrology/data/vakya"

def parse_lon(s):
    if not s: return None
    s = str(s).strip().replace(" ", "")
    parts = re.split(r"[:.]", s)
    try:
        d = float(parts[0]); m = float(parts[1]) if len(parts) > 1 else 0.0
        sec = float(parts[2]) if len(parts) > 2 else 0.0
        v = d + m/60.0 + sec/3600.0
        return v if 0.0 <= v < 360.0 else None
    except: return None

def parse_time(tob):
    t = tob.upper().replace(" ", "")
    pm = "PM" in t
    t2 = t.replace("PM","").replace("AM","")
    if ":" in t2: h, m = map(int, t2.split(":")[:2])
    else: h = int(t2[:-2]); m = int(t2[-2:])
    if pm and h < 12: h += 12
    elif not pm and h == 12: h = 0
    return h, m

def signed_diff(a, b):
    return (a - b + 180.0) % 360.0 - 180.0

# Patch _planet_raw_arcsec to expose internal state
def _planet_raw_arcsec_traced(engine, planet, ky_C, ky_D, ky_E, ky_F, month, day_in_month):
    desc   = PLANET_DESC[planet]
    period = desc['period']
    rows   = desc['rows']
    split  = desc['split']
    col    = desc['col']
    strict = desc['strict']

    sm = SAKA_MONTHS[month - 1]
    day = ky_C + sm[0] + day_in_month - 1
    gha = ky_D + sm[1]
    vin = ky_E + sm[2]
    if (ky_F + sm[3]) > 29:
        vin += 1
    if vin >= 60: vin -= 60; gha += 1
    if gha >= 60: gha -= 60; day += 1
    init_gha, init_vin = gha, vin

    acc_bija = 0
    for khanda, gh, bija in zip(desc['khandas'], desc['gh'], desc['bija']):
        while (day - khanda > 0) if strict else (day - khanda >= 0):
            gha -= gh
            if gha >= 0 or day > 0:
                if gha < 0 and day > 0:
                    gha += 60; day -= 1
                day -= khanda
                acc_bija += bija
            else:
                gha += gh
                break
    if day < 0:
        day = 0

    G         = day % period
    cycle_num = day // period
    expected_cycle = ((cycle_num % desc['cycle_mod']) + 1
                      if desc['cycle_mod'] is not None else cycle_num + 1)

    def _pick(seq):
        return desc['file_high'] if seq > split else desc['file_low']

    ge = (desc['search'] == 'ge')
    seq_found = None
    for row_idx in range(1, rows + 1):
        seq = cycle_num * rows + row_idx
        if planet == 'Saturn' and seq > 580:
            seq -= 578
        row = engine._tables.get(_pick(seq), {}).get(seq)
        if row is None:
            continue
        if int(row[0]) == expected_cycle and (row[1] >= G if ge else row[1] > G):
            seq_found = seq
            break
    if seq_found is None:
        seq_found = cycle_num * rows + rows
        if planet == 'Saturn' and seq_found > 580:
            seq_found -= 578

    row2 = engine._tables.get(_pick(seq_found),     {}).get(seq_found)
    row1 = engine._tables.get(_pick(seq_found - 1), {}).get(seq_found - 1)

    return {
        'day_pre_clamp': day,
        'day': day if day >= 0 else 0,
        'gha': gha, 'vin': vin,
        'init_gha': init_gha, 'init_vin': init_vin,
        'G': G, 'cycle_num': cycle_num,
        'expected_cycle': expected_cycle,
        'acc_bija': acc_bija,
        'seq_found': seq_found,
        'row1_exists': row1 is not None,
        'row2_exists': row2 is not None,
        'row1': row1,
        'row2': row2,
        'sm': sm,
    }


engine = VakyaTableEngine(str(VAKYA_DIR))
with open(DATA_FILE, encoding="utf-8") as f:
    data = json.load(f)
with open(CLEAN_FILE, encoding="utf-8") as f:
    clean_data = json.load(f)

clean_cases = clean_data['clean_cases']

large_error = []
zero_error = []

for idx in clean_cases:
    rec = data[idx]
    pp_list = rec.get("planetary_positions", [])
    pp = {p.get("planet","").replace("(R)","").strip(): p for p in pp_list}
    if "Mercury" not in pp:
        continue

    ics_lon = parse_lon(pp["Mercury"].get("absolute_longitude",""))
    if ics_lon is None:
        continue

    dd, mm, yy = map(int, rec["date_of_birth"].split("/"))
    h, m = parse_time(rec["time_of_birth"])
    ist = datetime(yy, mm, dd, h, m, 0)

    try:
        from datetime import timedelta
        dt_utc = ist - timedelta(hours=5.5)
        vinadi, vakya_date = engine._vinadi_and_vakya_date(dt_utc, 11.6643, 78.146, 5.5)
        gy, tamil_month, day_in_month = engine._date_to_tamil_month_day(vakya_date)
        C, D, E, F = engine._ky_year_arithmetic(gy)

        raw = engine.compute(ist, 11.6643, 78.146, 5.5)
        eng_lon = raw["Mercury"]["longitude"]
        err = signed_diff(eng_lon, ics_lon)

        info = _planet_raw_arcsec_traced(engine, "Mercury", C, D, E, F, tamil_month, day_in_month)
        info['idx'] = idx
        info['err'] = err
        info['eng_lon'] = eng_lon
        info['ics_lon'] = ics_lon
        info['date'] = rec["date_of_birth"]
        info['time'] = rec["time_of_birth"]
        info['G'] = info['G']

        if abs(err) > 0.5:
            large_error.append(info)
        else:
            zero_error.append(info)
    except Exception as e:
        pass

print(f"Cases with |error| > 0.5°: {len(large_error)}")
print(f"Cases with |error| <= 0.5°: {len(zero_error)}")
print()

# Analyze distribution of G and cycle_num for error vs clean
print("=== Large error cases: G value distribution ===")
from collections import Counter
g_dist_large = Counter(info['G'] for info in large_error)
g_dist_clean = Counter(info['G'] for info in zero_error)

print(f"Large error G range: [{min(g_dist_large.keys())}, {max(g_dist_large.keys())}]")
print(f"Clean G range: [{min(g_dist_clean.keys())}, {max(g_dist_clean.keys())}]")
print()

# Analyze acc_bija distribution
print("=== Large error cases: acc_bija distribution ===")
bija_large = Counter(info['acc_bija'] for info in large_error)
bija_clean = Counter(info['acc_bija'] for info in zero_error)
print("Large error bija values:", sorted(bija_large.keys())[:20])
print("Clean bija values:", sorted(bija_clean.keys())[:20])
print()

# Analyze cycle_num distribution
print("=== cycle_num distribution ===")
cyc_large = Counter(info['cycle_num'] for info in large_error)
cyc_clean = Counter(info['cycle_num'] for info in zero_error)
print("Large error cycle_num values (top 10):", sorted(cyc_large.items(), key=lambda x: -x[1])[:10])
print("Clean cycle_num values (top 10):", sorted(cyc_clean.items(), key=lambda x: -x[1])[:10])
print()

# Analyze seq_found distribution
print("=== seq_found distribution ===")
seq_large = Counter(info['seq_found'] for info in large_error)
seq_clean = Counter(info['seq_found'] for info in zero_error)
print("Large error seq_found values (top 10):", sorted(seq_large.items(), key=lambda x: -x[1])[:10])
print("Clean seq_found values (top 10):", sorted(seq_clean.items(), key=lambda x: -x[1])[:10])
print()

# Print a few large error cases in detail
print("=== First 5 large error cases ===")
for info in large_error[:5]:
    print(f"  idx={info['idx']} date={info['date']} time={info['time']}")
    print(f"    eng_lon={info['eng_lon']:.4f} ics_lon={info['ics_lon']:.4f} err={info['err']:+.4f}°")
    print(f"    G={info['G']} cycle_num={info['cycle_num']} expected_cycle={info['expected_cycle']}")
    print(f"    acc_bija={info['acc_bija']} seq_found={info['seq_found']}")
    print(f"    row1={info['row1']} row2={info['row2']}")
    print()

print("=== First 5 zero error cases ===")
for info in zero_error[:5]:
    print(f"  idx={info['idx']} date={info['date']} time={info['time']}")
    print(f"    eng_lon={info['eng_lon']:.4f} ics_lon={info['ics_lon']:.4f} err={info['err']:+.4f}°")
    print(f"    G={info['G']} cycle_num={info['cycle_num']} expected_cycle={info['expected_cycle']}")
    print(f"    acc_bija={info['acc_bija']} seq_found={info['seq_found']}")
    print(f"    row1={info['row1']} row2={info['row2']}")
    print()
