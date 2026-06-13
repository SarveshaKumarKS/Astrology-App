#!/usr/bin/env python3
"""
Run both Java harness and Python VakyaTableEngine against 729 test cases,
then produce a side-by-side comparison report.
"""
import json
import subprocess
import sys
import os
import re

sys.path.insert(0, '/home/user/Astrology-App/backend')

from astrology.vakya_table_engine import VakyaTableEngine

DATA_JSON  = '/home/user/Astrology-App/tests/astrology_data .json'
JAVA_HARNESS_DIR = '/home/user/Astrology-App/java_harness'
DATA_DIR   = '/home/user/Astrology-App/backend/astrology/data/vakya'
LAT, LON   = 11.6643, 78.185

PLANET_ORDER = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu']

NAKSHATRAS = [
    "Aswini","Bharani","Karthigai","Rohini","Mirugasirisha","Thiruvaathirai",
    "Punarpoosam","Poosam","Ayilyam","Magam","Pooram","Uthiram","Hastham",
    "Chithirai","Swathi","Visakam","Anusham","Kettai","Moolam","Pooradam",
    "Uthiradam","Thiruvonam","Avittam","Sathayam","Poorattathi","Uthirattathi",
    "Revathi"
]

def lon_to_nak_pada(deg):
    deg = deg % 360.0
    total_pada = int(deg / (13.0 + 1/3.0) * 4)
    nak_idx = int(deg / (13.0 + 1/3.0))
    if nak_idx >= 27: nak_idx = 26
    pada = (total_pada % 4) + 1
    return NAKSHATRAS[nak_idx], pada

def parse_time(time_str):
    """Return (hour, minute) from '1:38AM' style strings."""
    time_str = time_str.strip()
    m = re.match(r'(\d+):(\d+)\s*(AM|PM|am|pm)', time_str, re.IGNORECASE)
    if not m:
        return None, None
    h, mn, ampm = int(m.group(1)), int(m.group(2)), m.group(3).upper()
    if ampm == 'PM' and h != 12:
        h += 12
    if ampm == 'AM' and h == 12:
        h = 0
    return h, mn

def parse_date(date_str):
    """Return (year, month, day) from 'D/M/YYYY' format (Indian date convention)."""
    parts = date_str.strip().split('/')
    return int(parts[2]), int(parts[1]), int(parts[0])

def parse_ics_lon(lon_str):
    """Parse 'DDD:MM:SS' to decimal degrees."""
    parts = lon_str.strip().split(':')
    if len(parts) != 3:
        return None
    d, m, s = int(parts[0]), int(parts[1]), int(parts[2])
    return d + m/60.0 + s/3600.0

def get_ics_planets(record):
    """Extract ICS planet longitudes from JSON record."""
    result = {}
    for pp in record.get('planetary_positions', []):
        pname = pp['planet'].replace('(R)','').replace('(r)','').strip()
        if pname in PLANET_ORDER:
            lon = parse_ics_lon(pp['absolute_longitude'])
            nak = pp.get('star_name','').split()[0]
            pada_str = pp.get('pada','0')
            try:
                pada = int(pada_str)
            except:
                pada = 0
            result[pname] = {'lon': lon, 'nak': nak, 'pada': pada}
    return result

def main():
    with open(DATA_JSON) as f:
        records = json.load(f)

    # ── Prepare Java input ──────────────────────────────────────────────────
    java_input_lines = []
    valid_idxs = []
    for idx, rec in enumerate(records):
        year, month, day = parse_date(rec['date_of_birth'])
        h, mn = parse_time(rec['time_of_birth'])
        if h is None:
            continue
        java_input_lines.append(f"{idx}|{year}|{month}|{day}|{h}|{mn}")
        valid_idxs.append(idx)

    # ── Run Java harness ────────────────────────────────────────────────────
    print(f"Running Java harness on {len(java_input_lines)} cases...", flush=True)
    java_proc = subprocess.run(
        ['java', '-cp', f'{JAVA_HARNESS_DIR}/out', 'VakkiamEngine', DATA_DIR],
        input='\n'.join(java_input_lines),
        capture_output=True, text=True, timeout=300
    )
    if java_proc.returncode != 0:
        print("Java harness errors:", java_proc.stderr[:2000])

    # Parse Java output
    java_results = {}
    for line in java_proc.stdout.strip().split('\n'):
        if not line.strip():
            continue
        parts = line.split('|')
        if len(parts) < 10:
            continue
        idx = int(parts[0])
        java_results[idx] = {
            PLANET_ORDER[i]: float(parts[i+1]) for i in range(9)
        }

    print(f"Java produced {len(java_results)} results", flush=True)

    # ── Run Python engine ───────────────────────────────────────────────────
    print("Running Python VakyaTableEngine...", flush=True)
    engine = VakyaTableEngine(DATA_DIR)
    py_results = {}
    errors = []
    for idx, rec in enumerate(records):
        year, month, day = parse_date(rec['date_of_birth'])
        h, mn = parse_time(rec['time_of_birth'])
        if h is None:
            errors.append(f"idx {idx}: unparseable time '{rec['time_of_birth']}'")
            continue
        try:
            from datetime import datetime
            dt = datetime(year, month, day, h, mn)
            result = engine.compute(dt, LAT, LON)
            py_results[idx] = {}
            for pname in PLANET_ORDER:
                if pname in result:
                    py_results[idx][pname] = result[pname].get('longitude', 0.0)
                else:
                    py_results[idx][pname] = 0.0
        except Exception as e:
            errors.append(f"idx {idx}: {e}")

    print(f"Python produced {len(py_results)} results, {len(errors)} errors", flush=True)
    if errors:
        for e in errors[:10]:
            print(f"  ERR: {e}")

    # ── Compare Java vs Python ──────────────────────────────────────────────
    diff_cases = []
    both_idxs = set(java_results.keys()) & set(py_results.keys())

    for idx in sorted(both_idxs):
        jr = java_results[idx]
        pr = py_results[idx]
        case_diffs = []
        for pname in PLANET_ORDER:
            jlon = jr.get(pname, 0.0)
            plon = pr.get(pname, 0.0)
            diff = abs(jlon - plon)
            if diff > 180: diff = 360 - diff  # wrap
            j_nak, j_pada = lon_to_nak_pada(jlon)
            p_nak, p_pada = lon_to_nak_pada(plon)
            nak_match  = (j_nak == p_nak)
            pada_match = (j_nak == p_nak and j_pada == p_pada)
            if not pada_match:
                case_diffs.append({
                    'planet': pname,
                    'java_lon': jlon, 'py_lon': plon, 'diff_deg': diff,
                    'java_nak': j_nak, 'java_pada': j_pada,
                    'py_nak': p_nak,   'py_pada': p_pada,
                    'nak_match': nak_match
                })
        if case_diffs:
            ics = get_ics_planets(records[idx])
            diff_cases.append({'idx': idx, 'diffs': case_diffs, 'ics': ics,
                               'rec': records[idx]})

    # ── Build summary stats ─────────────────────────────────────────────────
    planet_stats = {p: {'total': 0, 'pada_match': 0} for p in PLANET_ORDER}
    for idx in sorted(both_idxs):
        jr = java_results[idx]
        pr = py_results[idx]
        for pname in PLANET_ORDER:
            jlon = jr.get(pname, 0.0)
            plon = pr.get(pname, 0.0)
            j_nak, j_pada = lon_to_nak_pada(jlon)
            p_nak, p_pada = lon_to_nak_pada(plon)
            planet_stats[pname]['total'] += 1
            if j_nak == p_nak and j_pada == p_pada:
                planet_stats[pname]['pada_match'] += 1

    # ── Write report ─────────────────────────────────────────────────────────
    report_path = '/home/user/Astrology-App/java_harness/java_vs_python_comparison.txt'
    with open(report_path, 'w') as out:
        out.write("=" * 80 + "\n")
        out.write("JAVA HARNESS vs PYTHON VakyaTableEngine — ACTUAL EXECUTION COMPARISON\n")
        out.write("=" * 80 + "\n\n")
        out.write(f"Cases run:     {len(both_idxs)}\n")
        out.write(f"Java results:  {len(java_results)}\n")
        out.write(f"Python results:{len(py_results)}\n\n")

        out.write("── Per-Planet Summary (Java vs Python) ──\n\n")
        out.write(f"{'Planet':<12} {'N':>5} {'Pada Match':>10} {'Pada%':>8} {'Failures':>9}\n")
        out.write("-" * 50 + "\n")
        total_checks = 0
        total_matches = 0
        for pname in PLANET_ORDER:
            s = planet_stats[pname]
            n = s['total']
            m = s['pada_match']
            f = n - m
            pct = 100.0 * m / n if n else 0
            out.write(f"{pname:<12} {n:>5} {m:>10} {pct:>8.2f} {f:>9}\n")
            total_checks += n
            total_matches += m
        out.write("-" * 50 + "\n")
        out.write(f"{'TOTAL':<12} {total_checks:>5} {total_matches:>10} "
                  f"{100.0*total_matches/total_checks:>8.2f} {total_checks-total_matches:>9}\n\n")

        out.write(f"── Discrepant Cases: {len(diff_cases)} records with pada mismatch ──\n\n")
        for dc in diff_cases:
            idx = dc['idx']
            rec = dc['rec']
            out.write(f"[idx {idx}] {rec['date_of_birth']} {rec['time_of_birth']}\n")
            for d in dc['diffs']:
                out.write(f"  {d['planet']:<10} Java={d['java_lon']:.4f}° ({d['java_nak']} p{d['java_pada']}) "
                          f"  Py={d['py_lon']:.4f}° ({d['py_nak']} p{d['py_pada']})  "
                          f"diff={d['diff_deg']*60:.1f}'\n")
            # Also show ICS reference
            ics = dc['ics']
            if ics:
                out.write("  ICS reference:\n")
                for pname in PLANET_ORDER:
                    if pname in ics:
                        entry = ics[pname]
                        out.write(f"    {pname:<10} {entry['lon']:.4f}° ({entry['nak']} p{entry['pada']})\n")
            out.write("\n")

        out.write("── Java stderr (first 2000 chars) ──\n")
        out.write(java_proc.stderr[:2000] + "\n")

    print(f"\nReport written to: {report_path}")
    print(f"\nSummary: {len(diff_cases)} records with Java vs Python pada discrepancies")
    print(f"Overall pada match: {100.0*total_matches/total_checks:.2f}% ({total_matches}/{total_checks})")

if __name__ == '__main__':
    main()
