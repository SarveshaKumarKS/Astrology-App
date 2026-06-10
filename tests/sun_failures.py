"""Dump all Sun cases with large error or nakshatra/pada mismatch."""
import json, re, sys
from datetime import datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from astrology.vakya_table_engine import VakyaTableEngine

DATA_FILE = Path(__file__).parent / "astrology_data .json"
VAKYA_DIR = Path(__file__).resolve().parents[1] / "backend/astrology/data/vakya"
LAT, LON = 11.6643, 78.146

NAKSHATRAS = ["Aswini", "Barani", "Krittika", "Rohini", "Mrigashirsha", "Thiruvadirai",
              "Punarpoosam", "Poosam", "Ayilyam", "Magam", "Pooram", "Uthiram",
              "Hastam", "Chithirai", "Swathi", "Visakam", "Anusham", "Kettai",
              "Moolam", "Pooradam", "Uthiradam", "Thiruvonam", "Avittam", "Sathayam",
              "Poorattathi", "Uthirattathi", "Revathi"]


def parse_lon(s):
    if not s: return None
    s = str(s).strip().replace(" ", "")
    parts = re.split(r"[:.]", s)
    try:
        d = float(parts[0]); m = float(parts[1]) if len(parts) > 1 else 0.0
        sec = float(parts[2]) if len(parts) > 2 else 0.0
        v = d + m / 60.0 + sec / 3600.0
        return v if 0.0 <= v < 360.0 else None
    except Exception:
        return None


def parse_time(tob):
    t = tob.upper().replace(" ", ""); pm = "PM" in t
    t2 = t.replace("PM", "").replace("AM", "")
    if ":" in t2: h, m = map(int, t2.split(":")[:2])
    else: h = int(t2[:-2]); m = int(t2[-2:])
    if pm and h < 12: h += 12
    elif not pm and h == 12: h = 0
    return h, m


def lon_to_nak_pada(lon):
    span = 360.0 / 27.0
    nak = int(lon // span) % 27
    pada = int((lon % span) // (span / 4.0)) + 1
    return NAKSHATRAS[nak], pada


def fmt_dms(lon):
    d = int(lon); mf = (lon - d) * 60; m = int(mf); s = (mf - m) * 60
    return f"{d}:{m:02d}:{s:04.1f}"


def main():
    engine = VakyaTableEngine(str(VAKYA_DIR))
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)

    rows = []
    for idx, rec in enumerate(data):
        try:
            dd, mm, yy = map(int, rec["date_of_birth"].split("/"))
            h, m = parse_time(rec["time_of_birth"])
            ist = datetime(yy, mm, dd, h, m, 0)
            result = engine.compute(ist, LAT, LON, 5.5)
        except Exception:
            continue

        pp = {p.get("planet", "").replace("(R)", "").strip(): p
              for p in rec.get("planetary_positions", [])}
        ics = pp.get("Sun")
        if not ics:
            continue
        ics_lon = parse_lon(ics.get("absolute_longitude", ""))
        if ics_lon is None:
            continue
        eng_lon = result.get("Sun", {}).get("longitude")
        if eng_lon is None:
            continue

        err = (eng_lon - ics_lon + 180.0) % 360.0 - 180.0
        ics_nak = ics.get("star_name", "").strip()
        ics_pada = str(ics.get("pada", "")).strip()
        eng_nak, eng_pada = lon_to_nak_pada(eng_lon)
        nak_ok = (eng_nak == ics_nak)
        pada_ok = nak_ok and (str(eng_pada) == ics_pada)

        if abs(err) > 0.5 or not pada_ok:
            rows.append((idx, rec['date_of_birth'], rec['time_of_birth'],
                         ics_lon, eng_lon, err, ics_nak, eng_nak, ics_pada, eng_pada,
                         "OK" if nak_ok else "NAK", "OK" if pada_ok else "PADA"))

    print(f"{'#':<4} {'Date':<12} {'TOB':<8} {'ICS_Lon':>12} {'Eng_Lon':>12} {'Err':>9} "
          f"{'ICS_Nak':<14} {'Eng_Nak':<14} {'P_ics':>5} {'P_eng':>5}")
    for r in rows:
        print(f"{r[0]:<4} {r[1]:<12} {r[2]:<8} {fmt_dms(r[3]):>12} {fmt_dms(r[4]):>12} "
              f"{r[5]:>+9.4f} {r[6]:<14} {r[7]:<14} {r[8]:>5} {r[9]:>5}  {r[10]}/{r[11]}")
    print(f"\nTotal flagged: {len(rows)}")

    # Group by error magnitude
    from collections import Counter
    buckets = Counter()
    for r in rows:
        e = r[5]
        if abs(e) > 100: buckets["corrupt(>100°)"] += 1
        elif abs(abs(e) - 2.0) < 0.02: buckets["±2°00'"] += 1
        else: buckets[f"{e:+.3f}"] += 1
    print("\nError buckets:")
    for k, v in sorted(buckets.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
