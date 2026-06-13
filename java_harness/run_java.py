#!/usr/bin/env python3
"""Run 729 test cases through the Java VakkiamEngine harness.

Reads tests/astrology_data .json, pipes all cases to the Java harness via stdin,
captures output, saves to java_harness/java_output.txt.

Format sent to Java:   idx|YYYY|MM|DD|HH|MM
Format received back:  idx|Sun|Moon|Mars|Mercury|Jupiter|Venus|Saturn|Rahu|Ketu
"""
import json
import subprocess
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE  = os.path.join(ROOT, "tests", "astrology_data .json")
DATA_DIR   = os.path.join(ROOT, "backend", "astrology", "data", "vakya")
CLASS_DIR  = os.path.join(ROOT, "java_harness", "out")
OUTPUT     = os.path.join(ROOT, "java_harness", "java_output.txt")


def parse_time(tob: str):
    """Parse '1:38AM' / '10:15PM' / '917PM' → (hour, minute)."""
    t = tob.upper().replace(" ", "")
    pm = "PM" in t
    t2 = t.replace("PM", "").replace("AM", "")
    if ":" in t2:
        h, m = map(int, t2.split(":")[:2])
    else:
        # Format like '917' → h=9, m=17
        h = int(t2[:-2])
        m = int(t2[-2:])
    if pm and h < 12:
        h += 12
    elif not pm and h == 12:
        h = 0
    return h, m


def main():
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)

    # Build stdin input: one line per case
    lines = []
    for idx, case in enumerate(data):
        # Date format in JSON: dd/mm/yyyy
        dd, mm, yy = map(int, case["date_of_birth"].split("/"))
        hour, minute = parse_time(case["time_of_birth"])
        lines.append(f"{idx}|{yy}|{mm}|{dd}|{hour}|{minute}")

    stdin_data = "\n".join(lines) + "\n"

    print(f"Running Java harness on {len(data)} cases...", flush=True)
    proc = subprocess.run(
        ["java", "-cp", CLASS_DIR, "VakkiamEngine", DATA_DIR],
        input=stdin_data,
        capture_output=True,
        text=True,
        timeout=600,
    )

    if proc.returncode != 0:
        print("Java stderr:", proc.stderr[:2000], file=sys.stderr)
        sys.exit(1)

    if proc.stderr:
        # Print stderr warnings (non-fatal)
        print("Java warnings:", proc.stderr[:500], file=sys.stderr)

    with open(OUTPUT, "w") as f:
        f.write(proc.stdout)

    lines_out = proc.stdout.strip().split("\n")
    print(f"Java harness produced {len(lines_out)} output lines.")
    print(f"Saved to {OUTPUT}")


if __name__ == "__main__":
    main()
