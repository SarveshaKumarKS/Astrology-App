"""Data integrity checker for the 729-case Vakya reference dataset.

Runs multi-level consistency checks on planetary_positions and exports
a JSON file listing clean case indices and per-planet bias statistics.

Usage:
    python3 data_integrity.py [--threshold DEG] [--out clean_cases.json]
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from astrology.vakya_table_engine import VakyaTableEngine

# ── Constants ─────────────────────────────────────────────────────────────────
DATA_FILE  = Path(__file__).parent / "astrology_data .json"
VAKYA_DIR  = Path(__file__).resolve().parents[1] / "backend/astrology/data/vakya"
PLANETS    = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

RASI_ALIASES = {
    "mesham": 1, "rishabam": 2, "mithunam": 3, "midhunam": 3,
    "kadakam": 4, "katakam": 4, "simmam": 5, "kanni": 6,
    "tulam": 7, "viruchigam": 8, "dhanusu": 9, "dhanus": 9,
    "magaram": 10, "makaram": 10, "kumbam": 11, "meenam": 12,
}
RASI_NAMES = ["Mesham","Rishabam","Midhunam","Katakam","Simmam","Kanni",
              "Tulam","Viruchigam","Dhanus","Makaram","Kumbam","Meenam"]

# Maximum plausible |engine − ICS| per planet (degrees).
# Based on the known algorithm differences + generous buffer.
PLAUSIBILITY_THRESHOLD = {
    "Sun":      3.0,
    "Moon":     3.0,
    "Mars":     3.0,
    "Mercury":  3.0,   # Mercury is fast; ICS occasionally differs more
    "Jupiter":  3.0,
    "Venus":    3.0,
    "Saturn":   3.0,
    "Rahu":     3.0,
    "Ketu":     3.0,
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def parse_lon(s: str):
    """Parse 'DDD:MM:SS' → float degrees. Returns None on failure."""
    if not s:
        return None
    s = str(s).strip().replace(" ", "")
    parts = re.split(r"[:.]", s)
    try:
        d   = float(parts[0])
        m   = float(parts[1]) if len(parts) > 1 else 0.0
        sec = float(parts[2]) if len(parts) > 2 else 0.0
        v   = d + m / 60.0 + sec / 3600.0
        return v if 0.0 <= v < 360.0 else None
    except (ValueError, IndexError):
        return None


def parse_time(tob: str):
    t  = tob.upper().replace(" ", "")
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


def signed_diff(a: float, b: float) -> float:
    """Shortest signed arc a − b in (−180, +180]."""
    return (a - b + 180.0) % 360.0 - 180.0


# ── Main ──────────────────────────────────────────────────────────────────────

def run_checks(threshold: float = 3.0, out_path: str = "clean_cases.json",
               verbose: bool = True):
    engine = VakyaTableEngine(str(VAKYA_DIR))
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)

    # ------------------------------------------------------------------
    # Pass 1 — compute engine positions for every case
    # ------------------------------------------------------------------
    engine_lons: dict = {}
    engine_errors: dict = {}
    for idx, rec in enumerate(data):
        dd, mm, yy = map(int, rec["date_of_birth"].split("/"))
        h, m = parse_time(rec["time_of_birth"])
        try:
            ist = datetime(yy, mm, dd, h, m, 0)
            raw = engine.compute(ist, 11.6643, 78.146, 5.5)
            engine_lons[idx] = {p: raw[p]["longitude"] for p in PLANETS if p in raw}
        except Exception as e:
            engine_errors[idx] = str(e)

    # ------------------------------------------------------------------
    # Pass 2 — integrity checks per case
    # ------------------------------------------------------------------
    corrupt: dict = defaultdict(list)   # idx → list of "(planet, reason)"

    for idx, rec in enumerate(data):
        pp_list = rec.get("planetary_positions", [])
        pp = {p.get("planet", "").replace("(R)", "").strip(): p for p in pp_list}

        lons: dict = {}
        for planet in PLANETS:
            if planet not in pp:
                continue
            raw_s = pp[planet].get("absolute_longitude", "")
            v = parse_lon(raw_s)
            if v is None:
                corrupt[idx].append((planet, f"UNPARSE: {raw_s!r}"))
            else:
                lons[planet] = v

        # ── Check 1: Rahu/Ketu must be exactly 180° apart (Vakyam rule) ──
        if "Rahu" in lons and "Ketu" in lons:
            # Use unsigned arc difference; signed_diff can return −180 for
            # perfect opposition, making (signed_diff − 180) incorrectly 360.
            diff = abs(((lons["Rahu"] - lons["Ketu"]) + 360.0) % 360.0 - 180.0)
            if diff > 0.5:
                corrupt[idx].append(("Rahu", f"RAHU_KETU_OPP {diff:.4f}°"))
                corrupt[idx].append(("Ketu", f"RAHU_KETU_OPP {diff:.4f}°"))

        # ── Check 2: Moon rasi must match rasi field ──────────────────────
        if "Moon" in lons:
            moon_rasi = int(lons["Moon"] / 30) + 1
            exp = RASI_ALIASES.get(rec.get("rasi", "").strip().lower(), 0)
            if exp and moon_rasi != exp:
                corrupt[idx].append(
                    ("Moon",
                     f"MOON_RASI rasi_field={rec['rasi']} "
                     f"lon_rasi={RASI_NAMES[moon_rasi-1]}"))

        # ── Check 3: Lagnam longitude must match lagnam field ─────────────
        if "Lagnam" in lons:
            lag_rasi = int(lons["Lagnam"] / 30) + 1
            exp = RASI_ALIASES.get(rec.get("lagnam", "").strip().lower(), 0)
            if exp and lag_rasi != exp:
                corrupt[idx].append(
                    ("Lagnam",
                     f"LAGNAM_RASI lagnam_field={rec['lagnam']} "
                     f"lon_rasi={RASI_NAMES[lag_rasi-1]}"))

        # ── Check 4: Plausibility vs engine output ────────────────────────
        if idx in engine_errors:
            corrupt[idx].append(("ENGINE", f"compute() failed: {engine_errors[idx]}"))
            continue

        eng = engine_lons.get(idx, {})
        for planet in PLANETS:
            if planet not in lons or planet not in eng:
                continue
            # Use .get() to avoid creating a defaultdict entry on read.
            if any(c[0] == planet for c in corrupt.get(idx, [])):
                continue
            gap = abs(signed_diff(eng[planet], lons[planet]))
            thr = PLAUSIBILITY_THRESHOLD.get(planet, threshold)
            if gap > thr:
                corrupt[idx].append(
                    (planet, f"PLAUSIBILITY gap={gap:.4f}° (threshold={thr}°)"))

    # ------------------------------------------------------------------
    # Pass 3 — build clean case list (all planets passed all checks)
    # ------------------------------------------------------------------
    corrupt_any = set(corrupt.keys())
    clean_cases = [i for i in range(len(data)) if i not in corrupt_any]

    # ------------------------------------------------------------------
    # Pass 4 — per-planet bias statistics on clean cases
    # ------------------------------------------------------------------
    biases: dict = defaultdict(list)
    for idx in clean_cases:
        rec = data[idx]
        pp_list = rec.get("planetary_positions", [])
        pp = {p.get("planet", "").replace("(R)", "").strip(): p for p in pp_list}
        eng = engine_lons.get(idx, {})
        for planet in PLANETS:
            if planet not in pp or planet not in eng:
                continue
            v = parse_lon(pp[planet].get("absolute_longitude", ""))
            if v is None:
                continue
            biases[planet].append(signed_diff(eng[planet], v))

    # ------------------------------------------------------------------
    # Report
    # ------------------------------------------------------------------
    if verbose:
        print(f"Total cases      : {len(data)}")
        print(f"Corrupted cases  : {len(corrupt_any)}")
        print(f"Clean cases      : {len(clean_cases)}")
        print()

        print("Corruption breakdown per planet:")
        pcnt: dict = defaultdict(int)
        for issues in corrupt.values():
            for p, _ in issues:
                pcnt[p] += 1
        for p in PLANETS + ["Lagnam", "ENGINE"]:
            if pcnt[p]:
                print(f"  {p:12s}: {pcnt[p]}")

        print()
        print("Per-planet accuracy on clean cases (engine − ICS):")
        print(f"  {'Planet':12} {'N':>6} {'Bias°':>9} {'MAE°':>8} "
              f"{'Max°':>8} {'%<0.1':>7} {'%<0.5':>7}")
        print("  " + "-" * 62)
        for planet in PLANETS:
            errs = biases[planet]
            if not errs:
                continue
            n    = len(errs)
            bias = sum(errs) / n
            mae  = sum(abs(e) for e in errs) / n
            maxe = max(abs(e) for e in errs)
            p01  = sum(1 for e in errs if abs(e) < 0.1) / n * 100
            p05  = sum(1 for e in errs if abs(e) < 0.5) / n * 100
            print(f"  {planet:12} {n:6d} {bias:+9.4f} {mae:8.4f} "
                  f"{maxe:8.4f} {p01:7.1f}% {p05:7.1f}%")

        print()
        print("Recommended bija corrections (to match ICS reference):")
        print("  (subtract bias from engine output = add -bias to bija)")
        for planet in PLANETS:
            errs = biases[planet]
            if not errs:
                continue
            bias = sum(errs) / len(errs)
            needed = -bias
            note = ""
            if abs(bias) < 0.05:
                note = "  ← already good"
            elif abs(needed) > 0.3:
                note = "  ← significant correction needed"
            print(f"  {planet:12}: current_bias={bias:+.4f}°  "
                  f"recommended_correction={needed:+.4f}°{note}")

    # ------------------------------------------------------------------
    # Save clean case list
    # ------------------------------------------------------------------
    result = {
        "total_cases":    len(data),
        "corrupted_cases": sorted(corrupt_any),
        "clean_cases":    clean_cases,
        "corruption_details": {
            str(k): [{"planet": p, "reason": r} for p, r in v]
            for k, v in corrupt.items()
        },
        "planet_bias_deg": {
            p: round(sum(biases[p]) / len(biases[p]), 6) if biases[p] else None
            for p in PLANETS
        },
    }
    out = Path(__file__).parent / out_path
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    if verbose:
        print(f"\nClean case list saved → {out}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=float, default=3.0,
                        help="Max plausible engine-vs-ICS gap in degrees (default 3.0)")
    parser.add_argument("--out", default="clean_cases.json",
                        help="Output file for clean case list")
    args = parser.parse_args()
    run_checks(threshold=args.threshold, out_path=args.out)
