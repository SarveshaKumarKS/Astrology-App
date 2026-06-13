#!/usr/bin/env python3
"""
Comprehensive comparison of Python VakyaTableEngine vs ICS reference values
across all 729 horoscope cases in tests/astrology_data .json
"""
import sys
import json
import math
import traceback
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, 'backend')
from astrology.vakya_table_engine import VakyaTableEngine

# ── Nakshatra definitions ─────────────────────────────────────────────────────
NAKSHATRAS = [
    "Aswini","Barani","Krittika","Rohini","Mrigashirsha","Thiruvadirai",
    "Punarpoosam","Poosam","Ayilyam","Magam","Pooram","Uthiram","Hastam",
    "Chithirai","Swathi","Visakam","Anusham","Kettai","Moolam","Pooradam",
    "Uthiradam","Thiruvonam","Avittam","Sathayam","Poorattathi","Uthirattathi","Revathi"
]

NAK_SIZE_DEG = 360.0 / 27.0   # 13.333...° per nakshatra
PADA_SIZE_DEG = NAK_SIZE_DEG / 4.0  # 3.333...° per pada

def lon_to_nak_pada(lon_deg: float):
    """Convert longitude in degrees [0,360) to (nakshatra_name, pada 1-4)."""
    lon_deg = lon_deg % 360.0
    nak_idx = int(lon_deg / NAK_SIZE_DEG)
    if nak_idx >= 27:
        nak_idx = 26
    nak_name = NAKSHATRAS[nak_idx]
    frac = (lon_deg - nak_idx * NAK_SIZE_DEG) / PADA_SIZE_DEG
    pada = int(frac) + 1
    if pada > 4:
        pada = 4
    return nak_name, pada

def parse_dms(dms_str: str) -> float:
    """Parse 'DDD:MM:SS' into decimal degrees."""
    parts = dms_str.strip().split(':')
    if len(parts) == 3:
        d, m, s = int(parts[0]), int(parts[1]), int(parts[2])
    elif len(parts) == 2:
        d, m, s = int(parts[0]), int(parts[1]), 0
    else:
        d, m, s = int(parts[0]), 0, 0
    return d + m / 60.0 + s / 3600.0

def parse_birth_datetime(date_str: str, time_str: str) -> datetime:
    """Parse date like '6/1/2025' and time like '1:38AM' into datetime."""
    # Date: D/M/YYYY or DD/MM/YYYY
    parts = date_str.strip().split('/')
    day   = int(parts[0])
    month = int(parts[1])
    year  = int(parts[2])

    # Time: H:MMAM or H:MMPM (no space between digits and AM/PM)
    time_str = time_str.strip()
    if time_str.upper().endswith('AM'):
        ampm = 'AM'
        ts = time_str[:-2]
    elif time_str.upper().endswith('PM'):
        ampm = 'PM'
        ts = time_str[:-2]
    else:
        ampm = 'AM'
        ts = time_str

    tp = ts.split(':')
    hour   = int(tp[0])
    minute = int(tp[1]) if len(tp) > 1 else 0

    if ampm == 'AM':
        if hour == 12:
            hour = 0
    else:  # PM
        if hour != 12:
            hour += 12

    return datetime(year, month, day, hour, minute, 0)

def normalize_planet_name(raw: str) -> str:
    """Strip '(R)' suffix from planet names in JSON data."""
    return raw.replace('(R)', '').strip()

# Planets we compare (Mandhi is excluded - not computed by Python engine)
PLANETS_TO_COMPARE = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter',
                      'Venus', 'Saturn', 'Rahu', 'Ketu', 'Lagnam']

def angle_diff(a: float, b: float) -> float:
    """Signed angular difference a - b in [-180, 180]."""
    d = (a - b + 180.0) % 360.0 - 180.0
    return d

def abs_angle_diff(a: float, b: float) -> float:
    """Absolute minimum angular distance between two longitudes."""
    return abs(angle_diff(a, b))

# Distance from nearest pada boundary
def dist_to_pada_boundary(lon_deg: float) -> float:
    """Return distance (degrees) to the nearest pada boundary."""
    lon_deg = lon_deg % 360.0
    pos_in_pada = (lon_deg % PADA_SIZE_DEG)
    return min(pos_in_pada, PADA_SIZE_DEG - pos_in_pada)

def main():
    # Load test data
    data_path = 'tests/astrology_data .json'
    print(f"Loading test data from: {data_path}")
    with open(data_path, 'r', encoding='utf-8') as f:
        records = json.load(f)
    print(f"Loaded {len(records)} records")

    # Initialize engine (Salem, India default lat/lon and IST timezone)
    LAT = 11.6643
    LON = 78.185
    TZ  = 5.5
    engine = VakyaTableEngine('backend/astrology/data/vakya')
    print("Engine initialized\n")

    # Statistics storage per planet
    # planet -> list of (python_lon, ics_lon, error_deg, nak_match, pada_match)
    planet_stats = defaultdict(list)

    # All failure cases (pada mismatch)
    failures = []

    # Error tracking
    engine_errors = []

    # ── Main evaluation loop ──────────────────────────────────────────────────
    for case_idx, record in enumerate(records):
        date_str = record.get('date_of_birth', '')
        time_str = record.get('time_of_birth', '')

        try:
            birth_dt = parse_birth_datetime(date_str, time_str)
        except Exception as e:
            engine_errors.append((case_idx, date_str, time_str, f"Date parse error: {e}"))
            continue

        try:
            result = engine.compute(birth_dt, LAT, LON, TZ)
        except Exception as e:
            engine_errors.append((case_idx, date_str, time_str, f"Engine error: {e}\n{traceback.format_exc()}"))
            continue

        # Build ICS map: planet_name -> (longitude_deg, star_name, pada)
        ics_map = {}
        for pp in record.get('planetary_positions', []):
            raw_name = pp.get('planet', '')
            pname    = normalize_planet_name(raw_name)
            if pname == 'Mandhi':
                continue
            try:
                ics_lon  = parse_dms(pp['absolute_longitude'])
            except Exception:
                continue
            ics_star = pp.get('star_name', '')
            ics_pada = int(pp.get('pada', 0))
            ics_map[pname] = (ics_lon, ics_star, ics_pada)

        for pname in PLANETS_TO_COMPARE:
            if pname not in result:
                continue
            if pname not in ics_map:
                continue

            py_lon  = result[pname]['longitude']
            ics_lon, ics_star, ics_pada = ics_map[pname]

            err = abs_angle_diff(py_lon, ics_lon)

            py_nak, py_pada = lon_to_nak_pada(py_lon)

            nak_match  = (py_nak == ics_star)
            pada_match = (py_pada == ics_pada) and nak_match

            planet_stats[pname].append({
                'case_idx':  case_idx,
                'date_str':  date_str,
                'time_str':  time_str,
                'py_lon':    py_lon,
                'ics_lon':   ics_lon,
                'err':       err,
                'py_nak':    py_nak,
                'py_pada':   py_pada,
                'ics_nak':   ics_star,
                'ics_pada':  ics_pada,
                'nak_match': nak_match,
                'pada_match':pada_match,
            })

            if not pada_match:
                boundary_dist = dist_to_pada_boundary(py_lon)
                if err > 1.0:
                    category = 'large_error'
                elif boundary_dist < 0.3:
                    category = 'boundary'
                else:
                    category = 'other'

                failures.append({
                    'case_idx':  case_idx,
                    'date_str':  date_str,
                    'time_str':  time_str,
                    'planet':    pname,
                    'py_lon':    py_lon,
                    'ics_lon':   ics_lon,
                    'err':       err,
                    'py_nak':    py_nak,
                    'py_pada':   py_pada,
                    'ics_nak':   ics_star,
                    'ics_pada':  ics_pada,
                    'nak_match': nak_match,
                    'boundary_dist': boundary_dist,
                    'category':  category,
                })

    # ── Build report ──────────────────────────────────────────────────────────
    report_lines = []
    def W(s=''):
        report_lines.append(s)

    W("=" * 100)
    W("PYTHON VakyaTableEngine vs ICS Reference — Full Comparison Report")
    W(f"Dataset: {data_path}")
    W(f"Total records: {len(records)}")
    W(f"Engine errors: {len(engine_errors)}")
    W(f"Total failure cases (pada mismatch): {len(failures)}")
    W("=" * 100)
    W()

    # ── Per-planet statistics ─────────────────────────────────────────────────
    W("PER-PLANET STATISTICS")
    W("-" * 100)
    header = f"{'Planet':<12} {'N':>5} {'Nak%':>7} {'Pada%':>7} {'MeanErr°':>10} {'MaxErr°':>10} {'NakFail':>8} {'PadaFail':>9}"
    W(header)
    W("-" * 100)

    planet_summary = {}
    for pname in PLANETS_TO_COMPARE:
        rows = planet_stats[pname]
        if not rows:
            continue
        n = len(rows)
        nak_ok  = sum(1 for r in rows if r['nak_match'])
        pada_ok = sum(1 for r in rows if r['pada_match'])
        errs    = [r['err'] for r in rows]
        mean_e  = sum(errs) / n
        max_e   = max(errs)
        nak_pct  = 100.0 * nak_ok / n
        pada_pct = 100.0 * pada_ok / n
        nak_fail  = n - nak_ok
        pada_fail = n - pada_ok

        planet_summary[pname] = {
            'n': n, 'nak_ok': nak_ok, 'pada_ok': pada_ok,
            'nak_pct': nak_pct, 'pada_pct': pada_pct,
            'mean_err': mean_e, 'max_err': max_e,
            'nak_fail': nak_fail, 'pada_fail': pada_fail,
        }

        W(f"{pname:<12} {n:>5} {nak_pct:>6.2f}% {pada_pct:>6.2f}% {mean_e:>10.4f} {max_e:>10.4f} {nak_fail:>8} {pada_fail:>9}")

    W("-" * 100)
    W()

    # ── Error distribution ────────────────────────────────────────────────────
    W("ERROR DISTRIBUTION SUMMARY (all planets combined)")
    W("-" * 100)
    all_errs = [r['err'] for rows in planet_stats.values() for r in rows]
    if all_errs:
        bins = [(0, 0.1), (0.1, 0.3), (0.3, 0.5), (0.5, 1.0), (1.0, 2.0), (2.0, 5.0), (5.0, float('inf'))]
        for lo, hi in bins:
            cnt = sum(1 for e in all_errs if lo <= e < hi)
            pct = 100.0 * cnt / len(all_errs)
            label = f"[{lo:.1f}, {hi:.1f})" if hi != float('inf') else f"[{lo:.1f}, inf)"
            W(f"  {label:<18} {cnt:>6}  ({pct:.2f}%)")
    W()

    # ── Failure categories summary ────────────────────────────────────────────
    W("FAILURE CATEGORIES")
    W("-" * 100)
    categories = defaultdict(list)
    for f in failures:
        categories[f['category']].append(f)

    for cat in ['boundary', 'large_error', 'other']:
        W(f"  {cat:<15}: {len(categories[cat]):>5} failures")
    W()

    # ── Per-planet failure breakdown ─────────────────────────────────────────
    W("PER-PLANET FAILURE BREAKDOWN BY CATEGORY")
    W("-" * 100)
    for pname in PLANETS_TO_COMPARE:
        pf = [f for f in failures if f['planet'] == pname]
        if not pf:
            continue
        by_cat = defaultdict(int)
        for f in pf:
            by_cat[f['category']] += 1
        W(f"  {pname:<12}: total={len(pf):>4}  boundary={by_cat['boundary']:>4}  large_error={by_cat['large_error']:>4}  other={by_cat['other']:>4}")
    W()

    # ── Full failure case listing ─────────────────────────────────────────────
    W("=" * 100)
    W("FULL FAILURE CASE LISTING (pada mismatch)")
    W("=" * 100)
    W()

    for cat in ['large_error', 'boundary', 'other']:
        cf = categories[cat]
        if not cf:
            continue
        W(f"{'=' * 60}")
        W(f"CATEGORY: {cat.upper()} ({len(cf)} cases)")
        W(f"{'=' * 60}")

        # Sort by planet then case index
        cf_sorted = sorted(cf, key=lambda x: (x['planet'], x['case_idx']))

        for f in cf_sorted:
            W(f"  Case {f['case_idx']:>4} | {f['date_str']:<12} {f['time_str']:<10} | "
              f"Planet: {f['planet']:<10} | "
              f"Py: {f['py_lon']:>8.4f}° | ICS: {f['ics_lon']:>8.4f}° | "
              f"Err: {f['err']:>7.4f}° | "
              f"Py: {f['py_nak']:<15}P{f['py_pada']} | "
              f"ICS: {f['ics_nak']:<15}P{f['ics_pada']} | "
              f"NakOK: {'Y' if f['nak_match'] else 'N'} | "
              f"Boundary: {f['boundary_dist']:.4f}°")
        W()

    # ── Engine errors ─────────────────────────────────────────────────────────
    if engine_errors:
        W("=" * 100)
        W(f"ENGINE ERRORS ({len(engine_errors)} cases)")
        W("=" * 100)
        for idx, ds, ts, msg in engine_errors:
            W(f"  Case {idx:>4} | {ds} {ts}: {msg}")
        W()

    # ── Detailed per-planet failure tables ───────────────────────────────────
    W("=" * 100)
    W("DETAILED PER-PLANET FAILURE TABLES")
    W("=" * 100)

    for pname in PLANETS_TO_COMPARE:
        pf = [f for f in failures if f['planet'] == pname]
        if not pf:
            W(f"\n{pname}: No failures")
            continue
        W()
        W(f"{'─' * 100}")
        W(f"Planet: {pname}  ({len(pf)} pada failures)")
        W(f"{'─' * 100}")
        W(f"  {'Case':>5}  {'Date':<12} {'Time':<10} {'Py Lon':>10} {'ICS Lon':>10} "
          f"{'Err°':>8} {'Py Nak':<15} {'PP':>3} {'ICS Nak':<15} {'IP':>3} {'Nak':>4} {'Category':<15} {'BDist°':>8}")
        W(f"  {'-'*5}  {'-'*12} {'-'*10} {'-'*10} {'-'*10} {'-'*8} {'-'*15} {'-'*3} {'-'*15} {'-'*3} {'-'*4} {'-'*15} {'-'*8}")
        for f in sorted(pf, key=lambda x: x['case_idx']):
            W(f"  {f['case_idx']:>5}  {f['date_str']:<12} {f['time_str']:<10} "
              f"{f['py_lon']:>10.4f} {f['ics_lon']:>10.4f} {f['err']:>8.4f} "
              f"{f['py_nak']:<15} {f['py_pada']:>3} {f['ics_nak']:<15} {f['ics_pada']:>3} "
              f"{'Y' if f['nak_match'] else 'N':>4} {f['category']:<15} {f['boundary_dist']:>8.4f}")

    # ── Overall summary ───────────────────────────────────────────────────────
    W()
    W("=" * 100)
    W("OVERALL SUMMARY")
    W("=" * 100)
    total_comparisons = sum(len(rows) for rows in planet_stats.values())
    total_nak_ok  = sum(s['nak_ok']  for s in planet_summary.values())
    total_pada_ok = sum(s['pada_ok'] for s in planet_summary.values())
    W(f"Total planet-case comparisons : {total_comparisons}")
    W(f"Nakshatra match overall        : {total_nak_ok}/{total_comparisons} ({100.0*total_nak_ok/total_comparisons:.2f}%)")
    W(f"Pada match overall             : {total_pada_ok}/{total_comparisons} ({100.0*total_pada_ok/total_comparisons:.2f}%)")
    W(f"Total pada failures            : {len(failures)}")
    W(f"  - boundary (<0.3° from pada): {len(categories['boundary'])}")
    W(f"  - large error (>1°)         : {len(categories['large_error'])}")
    W(f"  - other                     : {len(categories['other'])}")
    W()

    # ── Top worst errors ─────────────────────────────────────────────────────
    W("TOP 30 WORST ERRORS (by |error| degrees)")
    W("-" * 100)
    all_rows = [(pname, r) for pname, rows in planet_stats.items() for r in rows]
    all_rows.sort(key=lambda x: x[1]['err'], reverse=True)
    W(f"  {'Case':>5}  {'Planet':<10} {'Date':<12} {'Time':<10} {'Py Lon':>10} "
      f"{'ICS Lon':>10} {'Err°':>8} {'Py Nak':<15} {'PP':>3} {'ICS Nak':<15} {'IP':>3}")
    W(f"  {'-'*5}  {'-'*10} {'-'*12} {'-'*10} {'-'*10} {'-'*10} {'-'*8} {'-'*15} {'-'*3} {'-'*15} {'-'*3}")
    for pname, r in all_rows[:30]:
        W(f"  {r['case_idx']:>5}  {pname:<10} {r['date_str']:<12} {r['time_str']:<10} "
          f"{r['py_lon']:>10.4f} {r['ics_lon']:>10.4f} {r['err']:>8.4f} "
          f"{r['py_nak']:<15} {r['py_pada']:>3} {r['ics_nak']:<15} {r['ics_pada']:>3}")
    W()

    report_text = '\n'.join(report_lines)

    # Save report
    out_path = '/tmp/python_vs_ics_report.txt'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report_text)
    print(f"\nFull report saved to: {out_path}")

    # Print summary to stdout
    print("\n" + "=" * 80)
    print("QUICK SUMMARY")
    print("=" * 80)
    print(f"Total records processed: {len(records)}")
    print(f"Engine errors: {len(engine_errors)}")
    print(f"Total pada failures: {len(failures)}")
    print()
    print(f"{'Planet':<12} {'N':>5} {'Nak%':>7} {'Pada%':>7} {'MeanErr°':>10} {'MaxErr°':>10}")
    print("-" * 55)
    for pname in PLANETS_TO_COMPARE:
        if pname not in planet_summary:
            continue
        s = planet_summary[pname]
        print(f"{pname:<12} {s['n']:>5} {s['nak_pct']:>6.2f}% {s['pada_pct']:>6.2f}% "
              f"{s['mean_err']:>10.4f} {s['max_err']:>10.4f}")

    return report_text

if __name__ == '__main__':
    main()
