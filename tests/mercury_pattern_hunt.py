"""
Find the distinguishing pattern between correct (zero-error) and wrong (large-error)
Mercury computation cases.

Dumps ALL intermediate values from _planet_raw_arcsec for each case.
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

def detailed_trace(engine, planet, C, D, E, F, tamil_month, day_in_month):
    """Returns a dict of ALL intermediate values."""
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

    final_gha = gha
    final_vin = vin
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
        return None

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
    j3 = 1
    if vin_off < 0:
        vin_off += 60; gha -= 1

    gha_off_raw = gha - init_gha  # before adding 60
    gha_off = gha - init_gha
    borrow_fired = gha_off < 0
    if gha_off < 0:
        gha_off += 60
        doff -= j3

    doff_adj = doff
    correction_fired = init_gha >= 30
    if init_gha >= 30:
        doff_adj += j3

    frac_num = ((doff_adj * 60 + gha_off) * 60) + vin_off
    interp = (diff / (day_span * 60 * 60)) * frac_num

    if wrapped: pos1 += FULL_CIRCLE_ARCSEC
    result_arcsec = (pos1 - interp) if pos1 > pos2 else (pos1 + interp)
    result_arcsec = int(result_arcsec) % FULL_CIRCLE_ARCSEC

    # Also compute WITHOUT init_gha correction:
    doff_no_corr = doff  # after borrow but no correction
    frac_num_no_corr = ((doff_no_corr * 60 + gha_off) * 60) + vin_off
    interp_no_corr = (diff / (day_span * 60 * 60)) * frac_num_no_corr
    result_no_corr = (pos1 - interp_no_corr) if pos1 > pos2 else (pos1 + interp_no_corr)
    result_no_corr = int(result_no_corr) % FULL_CIRCLE_ARCSEC

    return {
        'G': G, 'cycle_num': cycle_num, 'day': day,
        'init_gha': init_gha, 'init_vin': init_vin,
        'final_gha': final_gha, 'gha_off_raw': gha_off_raw,
        'gha_off': gha_off, 'borrow_fired': borrow_fired,
        'correction_fired': correction_fired,
        'doff_raw': G - day1, 'doff': doff, 'doff_adj': doff_adj,
        'frac_num': frac_num, 'frac_num_no_corr': frac_num_no_corr,
        'diff': diff, 'day_span': day_span, 'day1': day1, 'day2': day2,
        'pos1': pos1, 'pos2': pos2, 'going_backward': pos1 > pos2,
        'acc_bija': acc_bija, 'c1': c1, 'c2': c2,
        'seq_found': seq_found, 'wrapped': wrapped,
        'result_arcsec': result_arcsec,
        'result_deg': result_arcsec / 3600.0,
        'result_no_corr_deg': result_no_corr / 3600.0,
    }

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
        t_month, t_day = engine._next_tamil_day(tamil_month, day_in_month)

        tr = detailed_trace(engine, 'Mercury', C, D, E, F, tamil_month, day_in_month)
        if tr is None: continue

        raw = engine.compute(ist, 11.6643, 78.146, 5.5)
        eng_lon = raw['Mercury']['longitude']
        err = abs(signed_diff(eng_lon, ics_lon))
        err_no_corr = abs(signed_diff(tr['result_no_corr_deg'], ics_lon))

        records.append({
            'idx': idx, 'date': rec['date_of_birth'], 'time': rec['time_of_birth'],
            'ics': ics_lon, 'eng': eng_lon, 'err': err,
            'err_no_corr': err_no_corr,
            'vinadi': vinadi, 'vakya_date': str(vakya_date),
            **tr
        })
    except Exception as e:
        pass

print(f"Total Mercury cases: {len(records)}")
large = [r for r in records if r['err'] > 0.5]
small = [r for r in records if r['err'] <= 0.5]
print(f"Large error: {len(large)}, Small error: {len(small)}")
print()

# Now look at patterns
print("=" * 70)
print("PATTERN ANALYSIS: What distinguishes large vs small error?")
print("=" * 70)

def show_dist(label, field, records):
    vals_large = [r[field] for r in large]
    vals_small = [r[field] for r in small]
    print(f"\n{label} ({field}):")
    for val in sorted(set(vals_large + vals_small)):
        nl = vals_large.count(val)
        ns = vals_small.count(val)
        print(f"  {val}: large={nl}, small={ns}")

# Binary fields
for field in ['borrow_fired', 'correction_fired', 'going_backward', 'wrapped']:
    show_dist(field, field, records)

# Numeric patterns
print("\n\ngha_off_raw distribution:")
import collections
gho_large = collections.Counter(r['gha_off_raw'] for r in large)
gho_small = collections.Counter(r['gha_off_raw'] for r in small)
all_gho = sorted(set(list(gho_large.keys()) + list(gho_small.keys())))
print(f"  {'gho':>6}  {'large':>6}  {'small':>6}")
for v in all_gho:
    if gho_large[v] > 0 or gho_small[v] > 0:
        print(f"  {v:6d}  {gho_large[v]:6d}  {gho_small[v]:6d}")

print("\n\nTable direction (pos1 > pos2 = retrograde):")
retro_large = sum(1 for r in large if r['going_backward'])
retro_small = sum(1 for r in small if r['going_backward'])
print(f"  Retrograde rows: large={retro_large} ({100*retro_large/max(1,len(large)):.0f}%), small={retro_small} ({100*retro_small/max(1,len(small)):.0f}%)")

print("\n\nc1 (bija col value) distribution:")
c1_large = collections.Counter(r['c1'] for r in large)
c1_small = collections.Counter(r['c1'] for r in small)
for v in sorted(set(list(c1_large.keys()) + list(c1_small.keys()))):
    if c1_large[v] > 0 or c1_small[v] > 0:
        print(f"  c1={v}: large={c1_large[v]}, small={c1_small[v]}")

print("\n\nNo-correction accuracy:")
fixed_by_no_corr = sum(1 for r in large if r['err_no_corr'] < 0.5)
broken_by_no_corr = sum(1 for r in small if r['err_no_corr'] > 0.5)
print(f"  Large errors FIXED by removing correction: {fixed_by_no_corr}/{len(large)} ({100*fixed_by_no_corr/max(1,len(large)):.0f}%)")
print(f"  Small errors BROKEN by removing correction: {broken_by_no_corr}/{len(small)} ({100*broken_by_no_corr/max(1,len(small)):.0f}%)")

# Show specific large-error cases that are NOT fixed by removing correction
not_fixed = [r for r in large if r['err_no_corr'] >= 0.5]
print(f"\n  Large-error cases NOT fixed by removing correction: {len(not_fixed)}")
print(f"  {'idx':>5}  {'date':>12}  {'init_gha':>8}  {'gho_raw':>7}  {'borrow':>6}  {'err':>6}  {'err_no_c':>8}  {'c1':>4}")
for r in not_fixed[:20]:
    print(f"  {r['idx']:5d}  {r['date']:>12}  {r['init_gha']:8d}  {r['gha_off_raw']:7d}  {str(r['borrow_fired']):6}  {r['err']:6.3f}  {r['err_no_corr']:8.3f}  {r['c1']:4}")

# Show cases fixed by no-corr
fixed = [r for r in large if r['err_no_corr'] < 0.5]
print(f"\n  Large-error cases FIXED by removing correction: {len(fixed)}")
print(f"  {'idx':>5}  {'date':>12}  {'init_gha':>8}  {'gho_raw':>7}  {'borrow':>6}  {'err':>6}  {'err_no_c':>8}  {'c1':>4}")
for r in fixed[:20]:
    print(f"  {r['idx']:5d}  {r['date']:>12}  {r['init_gha']:8d}  {r['gha_off_raw']:7d}  {str(r['borrow_fired']):6}  {r['err']:6.3f}  {r['err_no_corr']:8.3f}  {r['c1']:4}")

# Combined pattern: borrow AND correction
print("\n\nCross-tabulation: borrow_fired x correction_fired:")
for borrow in [False, True]:
    for corr in [False, True]:
        nl = sum(1 for r in large if r['borrow_fired']==borrow and r['correction_fired']==corr)
        ns = sum(1 for r in small if r['borrow_fired']==borrow and r['correction_fired']==corr)
        print(f"  borrow={borrow}, corr={corr}: large={nl}, small={ns}")

# Print a couple of the "not fixed" cases in detail
print("\n\nDETAIL of first 5 NOT-FIXED large-error cases:")
for r in not_fixed[:5]:
    print(f"\n  idx={r['idx']} date={r['date']} {r['time']}")
    print(f"    ICS={r['ics']:.4f}°, engine={r['eng']:.4f}°, err={r['err']:.4f}°")
    print(f"    init_gha={r['init_gha']}, gha_off_raw={r['gha_off_raw']}, borrow={r['borrow_fired']}, correction={r['correction_fired']}")
    print(f"    G={r['G']}, day1={r['day1']}, doff_raw={r['doff_raw']}, doff_adj={r['doff_adj']}")
    print(f"    frac_num={r['frac_num']}, frac_num_no_corr={r['frac_num_no_corr']}")
    print(f"    pos1={r['pos1']} ({r['pos1']/3600:.4f}°), going_backward={r['going_backward']}")
    print(f"    c1={r['c1']}, c2={r['c2']}, acc_bija={r['acc_bija']}, seq={r['seq_found']}")
    print(f"    result (with_corr)={r['result_deg']:.4f}°, result (no_corr)={r['result_no_corr_deg']:.4f}°")
