#!/usr/bin/env python3
"""Compare Java and Python engine outputs for 729 test cases.

Produces comparison.txt showing side-by-side differences for every case
where any planet differs by more than 0.01 degrees.

Also prints a summary of how both engines compare against the ICS reference data.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

JAVA_OUT   = os.path.join(ROOT, "java_harness", "java_output.txt")
PYTHON_OUT = os.path.join(ROOT, "java_harness", "python_output.txt")
DATA_FILE  = os.path.join(ROOT, "tests", "astrology_data .json")
COMP_OUT   = os.path.join(ROOT, "java_harness", "comparison.txt")

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
THRESHOLD = 0.01  # degrees


def parse_dms(s: str) -> float:
    parts = s.split(":")
    d, m, sec = int(parts[0]), int(parts[1]), int(parts[2])
    return d + m / 60.0 + sec / 3600.0


def parse_time(tob: str):
    t = tob.upper().replace(" ", "")
    pm = "PM" in t
    t2 = t.replace("PM", "").replace("AM", "")
    if ":" in t2:
        h, m = map(int, t2.split(":")[:2])
    else:
        h = int(t2[:-2]); m = int(t2[-2:])
    if pm and h < 12: h += 12
    elif not pm and h == 12: h = 0
    return h, m


def load_output(path: str) -> dict:
    """Load engine output into {idx: [Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu]}."""
    result = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("|")
            idx = int(parts[0])
            values = [float(x) for x in parts[1:10]]
            result[idx] = values
    return result


def angle_diff(a: float, b: float) -> float:
    """Smallest angular difference (0–180)."""
    return abs((a - b + 180.0) % 360.0 - 180.0)


def main():
    java   = load_output(JAVA_OUT)
    python = load_output(PYTHON_OUT)

    with open(DATA_FILE, encoding="utf-8") as f:
        ref_data = json.load(f)

    # Build reference planet values
    ref_planets = {}
    for idx, case in enumerate(ref_data):
        pp = {p["planet"].replace("(R)", "").strip(): p for p in case.get("planetary_positions", [])}
        ref_planets[idx] = pp

    diff_cases = []  # cases with java vs python diff > THRESHOLD

    for idx in sorted(java.keys()):
        if idx not in python:
            continue
        j_vals = java[idx]
        p_vals = python[idx]

        diffs = [angle_diff(j, p) for j, p in zip(j_vals, p_vals)]
        max_diff = max(diffs)

        if max_diff > THRESHOLD:
            diff_cases.append({
                "idx":   idx,
                "case":  ref_data[idx],
                "java":  j_vals,
                "python": p_vals,
                "diffs": diffs,
                "max_diff": max_diff,
            })

    # Summary stats vs reference
    java_err   = {p: [] for p in PLANETS}
    python_err = {p: [] for p in PLANETS}
    for idx, case in enumerate(ref_data):
        if idx not in java or idx not in python:
            continue
        pp = {p["planet"].replace("(R)", "").strip(): p for p in case.get("planetary_positions", [])}
        j_vals = java[idx]
        p_vals = python[idx]
        for pi, planet in enumerate(PLANETS):
            if planet not in pp:
                continue
            ref_lon = parse_dms(pp[planet]["absolute_longitude"])
            java_err[planet].append(angle_diff(j_vals[pi], ref_lon))
            python_err[planet].append(angle_diff(p_vals[pi], ref_lon))

    # Write comparison.txt
    with open(COMP_OUT, "w") as f:
        f.write("=" * 100 + "\n")
        f.write("JAVA vs PYTHON ENGINE COMPARISON — 729 test cases\n")
        f.write(f"Threshold: {THRESHOLD}° — only cases with max diff > {THRESHOLD}° shown\n")
        f.write("=" * 100 + "\n\n")

        f.write(f"Total cases with Java/Python diff > {THRESHOLD}°: {len(diff_cases)} / {len(java)}\n\n")

        if diff_cases:
            f.write("-" * 100 + "\n")
            f.write("CASES WITH DIFFERENCES:\n")
            f.write("-" * 100 + "\n\n")
            for dc in diff_cases:
                idx  = dc["idx"]
                case = dc["case"]
                f.write(f"Case {idx:4d}: {case['date_of_birth']} {case['time_of_birth']}\n")
                f.write(f"  {'Planet':<12} {'Java':>12} {'Python':>12} {'Diff':>10} {'ICS Ref':>12}\n")
                f.write(f"  {'-'*12} {'-'*12} {'-'*12} {'-'*10} {'-'*12}\n")
                pp = {p["planet"].replace("(R)", "").strip(): p for p in case.get("planetary_positions", [])}
                for pi, planet in enumerate(PLANETS):
                    j_val = dc["java"][pi]
                    p_val = dc["python"][pi]
                    diff  = dc["diffs"][pi]
                    ref   = parse_dms(pp[planet]["absolute_longitude"]) if planet in pp else float("nan")
                    marker = " <--" if diff > THRESHOLD else ""
                    f.write(f"  {planet:<12} {j_val:>12.4f} {p_val:>12.4f} {diff:>10.4f} {ref:>12.4f}{marker}\n")
                f.write("\n")

        f.write("=" * 100 + "\n")
        f.write("ACCURACY VS ICS REFERENCE DATA\n")
        f.write("=" * 100 + "\n\n")
        f.write(f"  {'Planet':<12} {'N':>5} {'Java Mean':>10} {'Java Max':>10} {'Py Mean':>10} {'Py Max':>10}\n")
        f.write(f"  {'-'*12} {'-'*5} {'-'*10} {'-'*10} {'-'*10} {'-'*10}\n")
        for planet in PLANETS:
            je = java_err[planet]
            pe = python_err[planet]
            if not je:
                continue
            f.write(f"  {planet:<12} {len(je):>5} "
                    f"{sum(je)/len(je):>10.4f} {max(je):>10.4f} "
                    f"{sum(pe)/len(pe):>10.4f} {max(pe):>10.4f}\n")
        f.write("\n")

    print(f"Comparison written to {COMP_OUT}")
    print(f"Cases with Java/Python diff > {THRESHOLD}°: {len(diff_cases)}")
    if diff_cases:
        print("\nTop 10 worst cases:")
        for dc in sorted(diff_cases, key=lambda x: -x["max_diff"])[:10]:
            print(f"  Case {dc['idx']:4d}: {dc['case']['date_of_birth']} {dc['case']['time_of_birth']}  max_diff={dc['max_diff']:.4f}°")

    # Print summary
    print("\n--- Accuracy vs ICS Reference ---")
    print(f"  {'Planet':<12} {'N':>5} {'Java Mean':>10} {'Java Max':>10} {'Py Mean':>10} {'Py Max':>10}")
    for planet in PLANETS:
        je = java_err[planet]
        pe = python_err[planet]
        if not je:
            continue
        print(f"  {planet:<12} {len(je):>5} "
              f"{sum(je)/len(je):>10.4f} {max(je):>10.4f} "
              f"{sum(pe)/len(pe):>10.4f} {max(pe):>10.4f}")


if __name__ == "__main__":
    main()
