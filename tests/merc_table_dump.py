"""Dump Mercury table rows around the error region and check for retrograde patterns."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from astrology.vakya_table_engine import VakyaTableEngine

VAKYA_DIR = Path(__file__).resolve().parents[1] / "backend/astrology/data/vakya"
engine = VakyaTableEngine(str(VAKYA_DIR))

# Mercury: file_low='rap.txt' (seq<=223), file_high='qnl.txt' (seq>223)
print("Mercury table rows (qnl.txt, seq 250-310):")
print(f"  {'seq':>5}  {'cyc':>4}  {'day':>5}  {'deg':>5}  {'am':>4}  {'sec':>4}")
print("  " + "-" * 40)
for seq in range(250, 315):
    row = engine._tables.get('qnl.txt', {}).get(seq)
    if row is None:
        print(f"  {seq:5d}  MISSING")
        continue
    cyc, day, deg, am, sec = int(row[0]), int(row[1]), int(row[2]), int(row[3]), int(row[4])
    print(f"  {seq:5d}  {cyc:4d}  {day:5d}  {deg:5d}  {am:4d}  {sec:4d}")

print()
print("Mercury table rows (rap.txt, seq 220-228):")
for seq in range(220, 228):
    row = engine._tables.get('rap.txt', {}).get(seq)
    if row is None:
        print(f"  {seq:5d}  MISSING")
        continue
    cyc, day, deg, am, sec = int(row[0]), int(row[1]), int(row[2]), int(row[3]), int(row[4])
    print(f"  {seq:5d}  {cyc:4d}  {day:5d}  {deg:5d}  {am:4d}  {sec:4d}")

# Now check: for the retrograde Mercury cases, what does the table look like?
# For cycle_num=11 (cycle 12 in 1-indexed), seq = 11*25+1=276 to 11*25+25=300
# Let's see if the table values go backward anywhere
print()
print("Cycle 12 rows (cycle_num=11, seq=276-300):")
print(f"  {'seq':>5}  {'cyc':>4}  {'day':>5}  {'lon':>10}  note")
prev_deg = None
for seq in range(276, 301):
    row = engine._tables.get('qnl.txt', {}).get(seq)
    if row is None:
        row = engine._tables.get('rap.txt', {}).get(seq)
    if row is None:
        print(f"  {seq:5d}  MISSING")
        continue
    cyc, day, deg, am, sec = int(row[0]), int(row[1]), int(row[2]), int(row[3]), int(row[4])
    lon = deg + am/60.0 + sec/3600.0
    note = ""
    if prev_deg is not None:
        diff = lon - prev_deg
        if abs(diff) > 300: diff = diff - 360 if diff > 0 else diff + 360
        if diff < 0: note = f" ← RETROGRADE! ({diff:+.2f}°)"
        else: note = f" (+{diff:.2f}°)"
    prev_deg = lon
    print(f"  {seq:5d}  {cyc:4d}  {day:5d}  {lon:10.4f}°{note}")
