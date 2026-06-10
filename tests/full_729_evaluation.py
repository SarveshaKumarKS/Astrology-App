"""Full evaluation: rasi / nakshatra / pada match rates for all planets, all 729 cases."""
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

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu", "Lagnam"]


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


def norm_star(s):
    return s.strip()


def main():
    engine = VakyaTableEngine(str(VAKYA_DIR))
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)

    stats = {p: {"total": 0, "rasi_ok": 0, "nak_ok": 0, "pada_ok": 0,
                 "err_sum": 0.0, "err_max": 0.0, "large": 0} for p in PLANETS}
    failed_cases = 0

    for idx, rec in enumerate(data):
        try:
            dd, mm, yy = map(int, rec["date_of_birth"].split("/"))
            h, m = parse_time(rec["time_of_birth"])
            ist = datetime(yy, mm, dd, h, m, 0)
            result = engine.compute(ist, LAT, LON, 5.5)
        except Exception:
            failed_cases += 1
            continue

        pp = {p.get("planet", "").replace("(R)", "").strip(): p
              for p in rec.get("planetary_positions", [])}

        for planet in PLANETS:
            ics = pp.get(planet)
            if not ics:
                continue
            ics_lon = parse_lon(ics.get("absolute_longitude", ""))
            if ics_lon is None:
                continue
            eng_lon = result.get(planet, {}).get("longitude")
            if eng_lon is None:
                continue

            st = stats[planet]
            st["total"] += 1
            err = abs((eng_lon - ics_lon + 180.0) % 360.0 - 180.0)
            st["err_sum"] += err
            st["err_max"] = max(st["err_max"], err)
            if err > 0.5:
                st["large"] += 1

            if lon_to_rasi(eng_lon) == ics.get("rasi", "").strip():
                st["rasi_ok"] += 1
            nak, pada = lon_to_nak_pada(eng_lon)
            ics_star = norm_star(ics.get("star_name", ""))
            if nak == ics_star:
                st["nak_ok"] += 1
                try:
                    if pada == int(str(ics.get("pada", "")).strip()):
                        st["pada_ok"] += 1
                except ValueError:
                    pass

    print(f"Dataset: {len(data)} cases, {failed_cases} failed to compute")
    print()
    print(f"{'Planet':<9} {'N':>4} {'Rasi':>11} {'Nakshatra':>11} {'Pada':>11} "
          f"{'MeanErr':>8} {'MaxErr':>8} {'>0.5°':>7}")
    print("-" * 78)
    for planet in PLANETS:
        st = stats[planet]
        n = st["total"]
        if n == 0:
            print(f"{planet:<9} {'--':>4}")
            continue
        print(f"{planet:<9} {n:>4} "
              f"{st['rasi_ok']:>5}({100*st['rasi_ok']/n:4.1f}%) "
              f"{st['nak_ok']:>5}({100*st['nak_ok']/n:4.1f}%) "
              f"{st['pada_ok']:>5}({100*st['pada_ok']/n:4.1f}%) "
              f"{st['err_sum']/n:>7.4f}° {st['err_max']:>7.3f}° "
              f"{st['large']:>4} ({100*st['large']/n:4.1f}%)")


if __name__ == "__main__":
    main()
