#!/usr/bin/env python3
"""Run 729 test cases through the Python VakyaTableEngine.

Reads tests/astrology_data .json, computes planets for each case,
saves to java_harness/python_output.txt.

Output format: idx|Sun|Moon|Mars|Mercury|Jupiter|Venus|Saturn|Rahu|Ketu
All longitudes in decimal degrees, 6 decimal places.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "backend"))

from astrology.vakya_table_engine import VakyaTableEngine
from datetime import datetime

DATA_FILE = os.path.join(ROOT, "tests", "astrology_data .json")
VAKYA_DIR = os.path.join(ROOT, "backend", "astrology", "data", "vakya")
OUTPUT    = os.path.join(ROOT, "java_harness", "python_output.txt")

LAT, LON, TZ = 11.6643, 78.185, 5.5

PLANET_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]


def parse_time(tob: str):
    t = tob.upper().replace(" ", "")
    pm = "PM" in t
    t2 = t.replace("PM", "").replace("AM", "")
    if ":" in t2:
        h, m = map(int, t2.split(":")[:2])
    else:
        h = int(t2[:-2])
        m = int(t2[-2:])
    if pm and h < 12:
        h += 12
    elif not pm and h == 12:
        h = 0
    return h, m


def main():
    engine = VakyaTableEngine(VAKYA_DIR)

    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)

    print(f"Running Python engine on {len(data)} cases...", flush=True)

    results = []
    for idx, case in enumerate(data):
        if idx % 100 == 0:
            print(f"  Processing case {idx}...", flush=True)
        # Date format: dd/mm/yyyy
        dd, mm, yy = map(int, case["date_of_birth"].split("/"))
        hour, minute = parse_time(case["time_of_birth"])
        dt = datetime(yy, mm, dd, hour, minute, 0)

        try:
            r = engine.compute(dt, LAT, LON, TZ)
            parts = [str(idx)]
            for p in PLANET_ORDER:
                lon = r.get(p, {}).get("longitude", 0.0)
                parts.append(f"{lon:.6f}")
            results.append("|".join(parts))
        except Exception as e:
            print(f"Error on case {idx}: {e}", file=sys.stderr)
            results.append("|".join([str(idx)] + ["0.000000"] * 9))

    with open(OUTPUT, "w") as f:
        f.write("\n".join(results) + "\n")

    print(f"Python engine produced {len(results)} lines.")
    print(f"Saved to {OUTPUT}")


if __name__ == "__main__":
    main()
