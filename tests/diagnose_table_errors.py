"""Diagnose large planet table errors and compute per-row corrections.

For each planet (Mars, Jupiter, Saturn, Mercury, Venus), this script:
1. Instruments _planet_raw_arcsec() to capture internal state
2. For clean cases with error > threshold, records the seq_found and f
3. Groups by seq_found, takes the median correction
4. Outputs corrections for rows where evidence is strong (f > 0.1)

Usage:  python3 diagnose_table_errors.py
"""
import json
import sys
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from astrology.vakya_table_engine import VakyaTableEngine, PLANET_DESC, SAKA_MONTHS, FULL_CIRCLE_ARCSEC

DATA_FILE = Path(__file__).parent / "astrology_data .json"
CLEAN_CASES_FILE = Path(__file__).parent / "clean_cases.json"
VAKYA_DIR = Path(__file__).resolve().parents[1] / "backend/astrology/data/vakya"

PLANETS_OF_INTEREST = ["Sun", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

# Capture dict: planet -> list of (idx, seq_found, f, pos1, pos2, day_span, result_arcsec,
#                                  acc_bija, wrapped, err_arcsec)
_capture: dict = {}
_current_planet = [None]
_current_idx = [None]


def signed_diff(a: float, b: float) -> float:
    return (a - b + 180.0) % 360.0 - 180.0


def parse_lon(s):
    import re
    if not s:
        return None
    s = str(s).strip().replace(" ", "")
    parts = re.split(r"[:.]", s)
    try:
        d = float(parts[0])
        m = float(parts[1]) if len(parts) > 1 else 0.0
        sec = float(parts[2]) if len(parts) > 2 else 0.0
        v = d + m / 60.0 + sec / 3600.0
        return v if 0.0 <= v < 360.0 else None
    except (ValueError, IndexError):
        return None


def parse_time(tob: str):
    t = tob.upper().replace(" ", "")
    pm = "PM" in t
    t2 = t.replace("PM", "").replace("AM", "")
    if ":" in t2:
        h, m = map(int, t2.split(":")[:2])
    else:
        h = int(t2[:-2]); m = int(t2[-2:])
    if pm and h < 12:
        h += 12
    elif not pm and h == 12:
        h = 0
    return h, m


# ── Monkey-patch _planet_raw_arcsec to capture state ─────────────────────────

original_planet_raw_arcsec = VakyaTableEngine._planet_raw_arcsec


def _patched_planet_raw_arcsec(self, planet: str, ky_C, ky_D, ky_E, ky_F, month, day_in_month):
    """Instrumented version that captures internal state."""
    if planet not in PLANETS_OF_INTEREST:
        return original_planet_raw_arcsec(self, planet, ky_C, ky_D, ky_E, ky_F, month, day_in_month)

    desc = PLANET_DESC[planet]
    period = desc['period']
    rows = desc['rows']
    split = desc['split']
    col = desc['col']
    strict = desc['strict']

    sm = SAKA_MONTHS[month - 1]
    day = ky_C + sm[0] + day_in_month - 1
    gha = ky_D + sm[1]
    vin = ky_E + sm[2]
    if (ky_F + sm[3]) > 29:
        vin += 1
    if vin >= 60:
        vin -= 60; gha += 1
    if gha >= 60:
        gha -= 60; day += 1
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

    G = day % period
    cycle_num = day // period
    expected_cycle = ((cycle_num % desc['cycle_mod']) + 1
                      if desc['cycle_mod'] is not None else cycle_num + 1)

    def _pick(seq: int) -> str:
        hi = seq > split
        if desc['swap']:
            hi = not hi
        return desc['file_high'] if hi else desc['file_low']

    ge = (desc['search'] == 'ge')
    seq_found = None
    for row_idx in range(1, rows + 1):
        seq = cycle_num * rows + row_idx
        if planet == 'Saturn' and seq > 580:
            seq -= 578
        row = self._tables[_pick(seq)].get(seq)
        if row is None:
            continue
        if int(row[0]) == expected_cycle and (row[1] >= G if ge else row[1] > G):
            seq_found = seq
            break
    if seq_found is None:
        seq_found = cycle_num * rows + rows
        if planet == 'Saturn' and seq_found > 580:
            seq_found -= 578

    row2 = self._tables[_pick(seq_found)].get(seq_found)
    row1 = self._tables[_pick(seq_found - 1)].get(seq_found - 1)
    if row2 is None or row1 is None:
        return original_planet_raw_arcsec(self, planet, ky_C, ky_D, ky_E, ky_F, month, day_in_month)

    deg2, am2 = int(row2[2]), int(row2[3])
    deg1, am1 = int(row1[2]), int(row1[3])
    c2 = row2[col] if len(row2) > col else 0
    c1 = row1[col] if len(row1) > col else 0
    day2, day1 = int(row2[1]), int(row1[1])

    if deg1 < deg2 and (deg2 - deg1) > 300:
        deg1 += 360
    if deg1 > deg2 and (deg1 - deg2) > 300:
        deg2 += 360

    b_arcsec = acc_bija * 60
    pos1 = (c1 * acc_bija + b_arcsec) + ((deg1 * 60 + am1) * 60)
    pos2 = (b_arcsec + acc_bija * c2) + ((deg2 * 60 + am2) * 60)
    if pos1 < 0 or pos2 < 0:
        pos1 += FULL_CIRCLE_ARCSEC; pos2 += FULL_CIRCLE_ARCSEC

    if (abs(pos2) - abs(pos1)) <= 1080000:
        diff = abs(pos2 - pos1); wrapped = False
    else:
        diff = (pos1 + FULL_CIRCLE_ARCSEC) - pos2; wrapped = True
    diff = abs(diff)

    day_span = day2 - day1 or 1
    doff = G - day1
    vin_off = vin - init_vin
    if vin_off < 0:
        vin_off += 60; gha -= 1
    gha_off = gha - init_gha
    if gha_off < 0:
        gha_off += 60; doff -= 1
    if init_gha >= 30:
        doff += 1
    frac_num = ((doff * 60 + gha_off) * 60) + vin_off
    interp = (diff / (day_span * 60 * 60)) * frac_num
    f = frac_num / (day_span * 3600)

    if wrapped:
        pos1_adj = pos1 + FULL_CIRCLE_ARCSEC
    else:
        pos1_adj = pos1
    result = (pos1_adj - interp) if pos1_adj > pos2 else (pos1_adj + interp)
    result_arcsec = float(int(result)) % FULL_CIRCLE_ARCSEC

    # Store capture
    if planet not in _capture:
        _capture[planet] = {}
    idx = _current_idx[0]
    _capture[planet][idx] = {
        'seq_found': seq_found,
        'f': f,
        'frac_num': frac_num,
        'pos1': pos1,
        'pos2': pos2,
        'day_span': day_span,
        'result_arcsec': result_arcsec,
        'acc_bija': acc_bija,
        'wrapped': wrapped,
        'G': G,
        'row1_key': _pick(seq_found - 1),
        'row2_key': _pick(seq_found),
        'deg1': deg1, 'am1': am1,
        'deg2': deg2, 'am2': am2,
        'day1': day1, 'day2': day2,
    }
    return result_arcsec


VakyaTableEngine._planet_raw_arcsec = _patched_planet_raw_arcsec


def main():
    with open(CLEAN_CASES_FILE) as f:
        clean_info = json.load(f)
    clean_set = set(clean_info['clean_cases'])

    with open(DATA_FILE, encoding='utf-8') as f:
        data = json.load(f)

    engine = VakyaTableEngine(str(VAKYA_DIR))

    # Run engine on all clean cases, collecting errors
    errors_by_planet = defaultdict(dict)   # planet -> {idx: err_arcsec}
    ics_lons = {}   # idx -> {planet: lon}

    print(f"Running engine on {len(clean_set)} clean cases...")
    for idx in sorted(clean_set):
        rec = data[idx]
        dd, mm, yy = map(int, rec['date_of_birth'].split('/'))
        h, m = parse_time(rec['time_of_birth'])

        _current_idx[0] = idx
        for p in PLANETS_OF_INTEREST:
            if p in _capture:
                _capture[p].pop(idx, None)

        try:
            ist = datetime(yy, mm, dd, h, m, 0)
            raw = engine.compute(ist, 11.6643, 78.146, 5.5)
        except Exception as e:
            continue

        pp_list = rec.get('planetary_positions', [])
        pp = {p.get('planet', '').replace('(R)', '').strip(): p for p in pp_list}
        ics_lons[idx] = {}

        for planet in PLANETS_OF_INTEREST:
            if planet not in pp or planet not in raw:
                continue
            ics_lon = parse_lon(pp[planet].get('absolute_longitude', ''))
            if ics_lon is None:
                continue
            eng_lon = raw[planet]['longitude']
            err = signed_diff(eng_lon, ics_lon)  # engine - ICS
            errors_by_planet[planet][idx] = err
            ics_lons[idx][planet] = ics_lon

    print("Analysis complete.\n")

    # ── For each planet, find large-error cases and group by seq_found ──
    THRESHOLD = 0.5  # degrees — cases we want to fix
    F_MIN = 0.05     # minimum interpolation fraction for reliable correction

    print("=" * 80)
    print("LARGE-ERROR CASE ANALYSIS")
    print("=" * 80)

    all_corrections = {}  # (file, seq) -> list of delta_arcsec corrections

    for planet in PLANETS_OF_INTEREST:
        errs = errors_by_planet[planet]
        if not errs:
            continue
        large = {idx: e for idx, e in errs.items() if abs(e) > THRESHOLD}
        if not large:
            print(f"\n{planet}: no cases with |error| > {THRESHOLD}°")
            continue

        print(f"\n{planet}: {len(large)} cases with |error| > {THRESHOLD}°")
        print(f"  Error range: [{min(large.values()):.3f}°, {max(large.values()):.3f}°]")

        # Group by seq_found
        by_seq = defaultdict(list)
        for idx, err in large.items():
            cap = _capture.get(planet, {}).get(idx)
            if cap is None:
                continue
            key = (cap['row2_key'], cap['seq_found'])
            by_seq[key].append((idx, err, cap))

        print(f"  {len(by_seq)} distinct table rows involved:")
        for (fname, seq), cases in sorted(by_seq.items()):
            errs_here = [e for _, e, _ in cases]
            mean_err = sum(errs_here) / len(errs_here)
            cap = cases[0][2]  # use first case for row info
            deg2, am2 = cap['deg2'] % 360, cap['am2']
            print(f"    {fname} seq={seq}: {len(cases)} case(s), "
                  f"mean_err={mean_err:+.3f}°, "
                  f"current={deg2}°{am2}'")

            # Compute correction per case
            corrections_here = []
            for idx, err, c in cases:
                f_val = c['f']
                day_span = c['day_span']
                frac_num = c['frac_num']
                pos1, pos2 = c['pos1'], c['pos2']
                wrapped = c['wrapped']

                if f_val < F_MIN:
                    print(f"      case {idx}: f={f_val:.4f} TOO SMALL — skip")
                    continue

                # err = engine - ICS in degrees
                # result = pos1 ± interp   (arcsec)
                # We want to reduce result by err*3600 arcsec → reduce interp
                err_arcsec = err * 3600.0

                # If pos1 < pos2 (forward motion): result = pos1 + interp
                #   interp = diff * frac_num / (day_span*3600)
                #   diff = pos2 - pos1 (approx)
                # new_interp = interp - err_arcsec
                # delta_interp = -err_arcsec
                # delta_diff = delta_interp * (day_span*3600) / frac_num
                # delta_pos2 = delta_diff (since pos1 doesn't change)
                if frac_num == 0:
                    continue

                delta_pos2 = -err_arcsec * (day_span * 3600) / frac_num
                new_pos2_arcsec = pos2 + delta_pos2
                # Convert back to degrees-arcmin
                new_deg2_total = new_pos2_arcsec / 60.0  # arcmin
                new_deg2 = int(new_deg2_total / 60)
                new_am2 = round(new_deg2_total % 60)
                if new_am2 == 60:
                    new_deg2 += 1; new_am2 = 0
                new_deg2_norm = new_deg2 % 360

                print(f"      case {idx}: err={err:+.3f}°, f={f_val:.4f}, "
                      f"correction={delta_pos2/3600:+.3f}°, "
                      f"new_row2={new_deg2_norm}°{new_am2}'")
                corrections_here.append((fname, seq, delta_pos2, new_deg2_norm, new_am2,
                                         cap['deg2'] % 360, cap['am2']))

            if corrections_here:
                all_corrections[(fname, seq)] = corrections_here

    # ── Summary: recommended corrections ──────────────────────────────────────
    print("\n" + "=" * 80)
    print("RECOMMENDED TABLE CORRECTIONS")
    print("=" * 80)

    # Group by (file, seq), take median delta_pos2
    final = {}
    for (fname, seq), corr_list in sorted(all_corrections.items()):
        deltas = [d for _, _, d, _, _, _, _ in corr_list]
        median_delta = sorted(deltas)[len(deltas) // 2]
        old_deg, old_am = corr_list[0][5], corr_list[0][6]
        # Apply median delta to current pos2
        old_arcsec = (old_deg * 60 + old_am) * 60
        new_arcsec = old_arcsec + median_delta
        new_deg = int(new_arcsec / 3600) % 360
        new_am = round((new_arcsec % 3600) / 60)
        if new_am == 60:
            new_deg += 1; new_am = 0
        if abs(median_delta) > 14400:  # > 4 degrees — suspicious
            flag = " *** WARNING: very large correction ***"
        else:
            flag = ""
        print(f"  {fname} seq={seq}: {old_deg}°{old_am}' → {new_deg}°{new_am}' "
              f"(delta={median_delta/3600:+.3f}°, n={len(corr_list)}){flag}")
        final[(fname, seq)] = (old_deg, old_am, new_deg, new_am, median_delta, len(corr_list))

    # Save to JSON for use by apply_corrections.py
    out = {
        f"{fname}:{seq}": {
            'file': fname,
            'seq': seq,
            'old_deg': od, 'old_am': oa,
            'new_deg': nd, 'new_am': na,
            'delta_arcsec': d,
            'n_cases': n
        }
        for (fname, seq), (od, oa, nd, na, d, n) in final.items()
    }
    outfile = Path(__file__).parent / "table_corrections.json"
    with open(outfile, 'w') as f:
        json.dump(out, f, indent=2)
    print(f"\nCorrections saved → {outfile}")


if __name__ == '__main__':
    main()
