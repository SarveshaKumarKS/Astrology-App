"""Investigate failing nakshatra/pada cases for Rahu, Ketu, and Lagnam."""
import json, re, sys
from datetime import datetime, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from astrology.vakya_table_engine import VakyaTableEngine

DATA_FILE = Path(__file__).parent / "astrology_data .json"
VAKYA_DIR = Path(__file__).resolve().parents[1] / "backend/astrology/data/vakya"

LAT, LON = 11.6643, 78.146

RASIS = ["Mesham", "Rishabam", "Mithunam", "Kadakam", "Simmam", "Kanni",
         "Tulam", "Viruchigam", "Dhanusu", "Magaram", "Kumbam", "Meenam"]

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


def lon_to_rasi(lon): return RASIS[int(lon // 30) % 12]


def lon_to_nak_pada(lon):
    span = 360.0 / 27.0
    nak = int(lon // span) % 27
    pada = int((lon % span) // (span / 4.0)) + 1
    return NAKSHATRAS[nak], pada


def main():
    engine = VakyaTableEngine(str(VAKYA_DIR))
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)

    targets = ["Rahu", "Ketu", "Lagnam", "Moon"]

    for planet in targets:
        print(f"\n{'='*80}")
        print(f"FAILURES: {planet}")
        print(f"{'='*80}")
        print(f"{'#':<4} {'Date':<12} {'TOB':<8} {'ICS_Lon':>10} {'Eng_Lon':>10} {'Err':>8} {'ICS_Nak':<15} {'Eng_Nak':<15} {'ICS_P':>5} {'Eng_P':>5} {'Issue'}")
        count = 0
        for idx, rec in enumerate(data):
            try:
                dd, mm, yy = map(int, rec["date_of_birth"].split("/"))
                h, m = parse_time(rec["time_of_birth"])
                ist = datetime(yy, mm, dd, h, m, 0)
                result = engine.compute(ist, LAT, LON, 5.5)
            except Exception as e:
                continue

            pp = {p.get("planet", "").replace("(R)", "").strip(): p
                  for p in rec.get("planetary_positions", [])}

            ics = pp.get(planet)
            if not ics:
                continue
            ics_lon = parse_lon(ics.get("absolute_longitude", ""))
            if ics_lon is None:
                continue
            eng_lon = result.get(planet, {}).get("longitude")
            if eng_lon is None:
                continue

            err = abs((eng_lon - ics_lon + 180.0) % 360.0 - 180.0)
            ics_nak = ics.get("star_name", "").strip()
            ics_pada = ics.get("pada", "")
            eng_nak, eng_pada = lon_to_nak_pada(eng_lon)

            nak_ok = (eng_nak == ics_nak)
            try:
                pada_ok = nak_ok and (eng_pada == int(str(ics_pada).strip()))
            except:
                pada_ok = False

            if not nak_ok or not pada_ok:
                issue = []
                if not nak_ok: issue.append("NAK")
                if not pada_ok: issue.append("PADA")
                print(f"{idx:<4} {rec['date_of_birth']:<12} {rec['time_of_birth']:<8} "
                      f"{ics_lon:>10.4f} {eng_lon:>10.4f} {err:>8.4f} "
                      f"{ics_nak:<15} {eng_nak:<15} {str(ics_pada):>5} {eng_pada:>5}  {'+'.join(issue)}")
                count += 1
        print(f"Total failures: {count}")


if __name__ == "__main__":
    main()
