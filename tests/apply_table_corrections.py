"""Apply computed corrections to Vakya table files.

Steps:
1. Fix day-field anomalies (R61 day=42→52, R158 day=40→43 in mercury_high.txt)
2. Apply position corrections for Mercury rows with std < threshold
3. Apply position corrections for Venus rows with std < threshold
4. Apply position corrections for Jupiter/Saturn/Mars rows

Usage:  python3 apply_table_corrections.py [--dry-run] [--std-max 0.15]
"""
import argparse
import json
import re
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from astrology.vakya_table_engine import VakyaTableEngine, PLANET_DESC, SAKA_MONTHS, FULL_CIRCLE_ARCSEC

DATA_FILE = Path(__file__).parent / "astrology_data .json"
CLEAN_CASES_FILE = Path(__file__).parent / "clean_cases.json"
VAKYA_DIR = Path(__file__).resolve().parents[1] / "backend/astrology/data/vakya"

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

# ── Day-field anomaly fixes ──────────────────────────────────────────────────
# These are OCR/transcription errors where the day column has the wrong value.
# Format: (file, seq, old_day, correct_day, note)
DAY_FIXES = [
    ("mercury_high.txt", 61,  42,  52, "digit transposition: 42→52"),
    ("mercury_high.txt", 158, 40,  43, "duplicate day: 40→43 (3-day increment)"),
]


def parse_lon(s: str):
    if not s:
        return None
    s = str(s).strip().replace(" ", "")
    parts = re.split(r"[:.]", s)
    try:
        d = float(parts[0])
        m = float(parts[1]) if len(parts) > 1 else 0.0
        sec = float(parts[2]) if len(parts) > 2 else 0.0
        v = d + m / 60.0 + sec / 3600.0
        return v if 0.0 <= v < 360.0 else None
    except (ValueError, IndexError):
        return None


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


def signed_diff(a: float, b: float) -> float:
    return (a - b + 180.0) % 360.0 - 180.0


def compute_per_row_corrections(planet: str, std_max: float = 0.20, n_min: int = 3) -> dict:
    """Compute per-row position corrections for a planet.
    Returns dict: {(file, seq): (E_row, n, std, old_deg, old_am, new_deg, new_am)}
    """
    engine = VakyaTableEngine(str(VAKYA_DIR))
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    with open(CLEAN_CASES_FILE) as f:
        clean = set(json.load(f)["clean_cases"])

    desc = PLANET_DESC[planet]
    period = desc["period"]
    rows = desc["rows"]
    split = desc["split"]

    def _pick(seq: int) -> str:
        hi = seq > split
        if desc["swap"]:
            hi = not hi
        return desc["file_high"] if hi else desc["file_low"]

    # row_appearances: row_seq -> list of (f, err, file)
    row_appearances: dict = defaultdict(list)

    for idx in sorted(clean):
        rec = data[idx]
        dd, mm, yy = map(int, rec["date_of_birth"].split("/"))
        h, m = parse_time(rec["time_of_birth"])
        ist = datetime(yy, mm, dd, h, m, 0)
        dt_utc = ist - timedelta(hours=5.5)
        ghatika, vakya_date = engine._ghatika_and_vakya_date(dt_utc, 11.6643, 78.146, 5.5)
        gy, tm, dim = engine._date_to_tamil_month_day(vakya_date)
        C, D, E, F = engine._ky_year_arithmetic(gy)

        sm = SAKA_MONTHS[tm - 1]
        day = C + sm[0] + dim - 1
        gha = D + sm[1]
        vin = E + sm[2]
        if (F + sm[3]) > 29:
            vin += 1
        if vin >= 60:
            vin -= 60
            gha += 1
        if gha >= 60:
            gha -= 60
            day += 1
        init_gha, init_vin = gha, vin
        acc_bija = 0
        for khanda, gh, bija in zip(desc["khandas"], desc["gh"], desc["bija"]):
            while (day - khanda > 0) if desc["strict"] else (day - khanda >= 0):
                gha -= gh
                if gha >= 0 or day > 0:
                    if gha < 0 and day > 0:
                        gha += 60
                        day -= 1
                    day -= khanda
                    acc_bija += bija
                else:
                    gha += gh
                    break
        if day < 0:
            day = 0

        G = day % period
        cycle_num = day // period
        expected_cycle = (
            (cycle_num % desc["cycle_mod"]) + 1 if desc["cycle_mod"] else cycle_num + 1
        )

        seq_found = None
        for ri in range(1, rows + 1):
            seq = cycle_num * rows + ri
            if planet == "Saturn" and seq > 580:
                seq -= 578
            row = engine._tables[_pick(seq)].get(seq)
            if row is None:
                continue
            ge = desc["search"] == "ge"
            if int(row[0]) == expected_cycle and (row[1] >= G if ge else row[1] > G):
                seq_found = seq
                break
        if seq_found is None:
            seq_found = cycle_num * rows + rows
            if planet == "Saturn" and seq_found > 580:
                seq_found -= 578

        row2 = engine._tables[_pick(seq_found)].get(seq_found)
        row1 = engine._tables[_pick(seq_found - 1)].get(seq_found - 1)
        if row2 is None or row1 is None:
            continue

        day2, day1 = int(row2[1]), int(row1[1])
        day_span = day2 - day1 or 1
        doff = G - day1
        vin_off = vin - init_vin
        if vin_off < 0:
            vin_off += 60
            gha -= 1
        gha_off = gha - init_gha
        if gha_off < 0:
            gha_off += 60
            doff -= 1
        if init_gha >= 30:
            doff += 1
        frac_num = ((doff * 60 + gha_off) * 60) + vin_off
        f = frac_num / (day_span * 3600)

        # Get ICS longitude
        pp = {p.get("planet", "").replace("(R)", "").strip(): p for p in rec.get("planetary_positions", [])}
        if planet not in pp:
            continue
        ics = parse_lon(pp[planet].get("absolute_longitude", ""))
        if ics is None:
            continue

        raw = engine.compute(ist, 11.6643, 78.146, 5.5)
        eng_lon = raw.get(planet, {}).get("longitude", 0)
        err = signed_diff(eng_lon, ics)

        # row2 (seq_found): weight = f in the error
        row_appearances[seq_found].append((f, err, _pick(seq_found)))
        # row1 (seq_found-1): weight = (1-f) in the error
        row_appearances[seq_found - 1].append((f, err, _pick(seq_found - 1)))

    # Compute per-row correction
    corrections = {}
    for row_seq, cases in sorted(row_appearances.items()):
        if len(cases) < n_min:
            continue
        errs = [e for _, e, _ in cases]
        n = len(errs)
        mean = sum(errs) / n
        mae = sum(abs(e) for e in errs) / n
        std = (sum((e - mean) ** 2 for e in errs) / n) ** 0.5
        consistency = abs(mean) / mae if mae > 0.001 else 0

        if consistency < 0.5 or mae < 0.25:
            continue

        fname = cases[0][2]
        row = engine._tables[fname].get(row_seq)
        if row is None:
            continue

        # Apply correction: subtract mean error
        E_row = mean
        old_deg = int(row[2]) % 360
        old_am = int(row[3])
        corr_arcsec = -E_row * 3600
        old_arcsec = (old_deg * 60 + old_am) * 60
        new_arcsec = old_arcsec + corr_arcsec
        new_deg = int(new_arcsec / 3600) % 360
        new_am = round((new_arcsec % 3600) / 60)
        if new_am == 60:
            new_deg += 1
            new_am = 0
        new_deg = new_deg % 360

        if std <= std_max:
            corrections[(fname, row_seq)] = {
                "file": fname, "seq": row_seq,
                "E_row": E_row, "n": n, "std": std, "consistency": consistency,
                "old_deg": old_deg, "old_am": old_am,
                "new_deg": new_deg, "new_am": new_am,
            }

    return corrections


def apply_day_fixes(dry_run: bool = False):
    """Fix day-column anomalies in table files."""
    print("\n── Day-field fixes ─────────────────────────────────────")
    for fname, seq, old_day, new_day, note in DAY_FIXES:
        fpath = VAKYA_DIR / fname
        text = fpath.read_text()
        # Match pattern R{seq}={cycle},{old_day},{rest}
        pattern = rf"^(R{seq}=\d+,){old_day}(,.+)$"
        new_text = re.sub(pattern, rf"\g<1>{new_day}\g<2>", text, flags=re.MULTILINE)
        if new_text == text:
            print(f"  {fname} R{seq}: NO MATCH (already fixed?)")
        else:
            print(f"  {fname} R{seq}: day {old_day} → {new_day}  [{note}]")
            if not dry_run:
                fpath.write_text(new_text)


def apply_position_corrections(planet: str, corrections: dict, dry_run: bool = False):
    """Apply position corrections for a planet's table rows."""
    if not corrections:
        print(f"  No corrections for {planet}")
        return

    # Group by file
    by_file: dict = defaultdict(dict)
    for (fname, seq), c in corrections.items():
        by_file[fname][seq] = c

    for fname, row_corrs in by_file.items():
        fpath = VAKYA_DIR / fname
        lines = fpath.read_text().splitlines()
        changes = 0
        for i, line in enumerate(lines):
            m = re.match(r"^(R(\d+)=)(\d+),(\d+),(\d+),(\d+),(.*)", line)
            if not m:
                continue
            seq = int(m.group(2))
            if seq not in row_corrs:
                continue
            c = row_corrs[seq]
            cycle = m.group(3)
            day = m.group(4)
            old_deg_str = m.group(5)
            old_am_str = m.group(6)
            rest = m.group(7)

            # Verify the old values match
            if int(old_deg_str) != c["old_deg"] or int(old_am_str) != c["old_am"]:
                print(f"  MISMATCH at {fname} R{seq}: expected {c['old_deg']}°{c['old_am']:02d}' "
                      f"got {old_deg_str}°{old_am_str}'  [skip]")
                continue

            new_line = (f"{m.group(1)}{cycle},{day},"
                        f"{c['new_deg']},{c['new_am']},{rest}")
            lines[i] = new_line
            changes += 1

        if changes > 0:
            print(f"  {fname}: {changes} row(s) updated")
            if not dry_run:
                fpath.write_text("\n".join(lines) + "\n")
        else:
            print(f"  {fname}: 0 changes (all already correct or mismatched)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would change without writing files")
    parser.add_argument("--std-max", type=float, default=0.15,
                        help="Max std-dev threshold for position corrections (default 0.15)")
    parser.add_argument("--planets", nargs="*",
                        default=["Mercury", "Venus", "Mars", "Jupiter", "Saturn"],
                        help="Planets to process")
    args = parser.parse_args()

    if args.dry_run:
        print("DRY RUN — no files will be modified")

    # Step 1: Fix day anomalies
    apply_day_fixes(dry_run=args.dry_run)

    # Step 2: Per-planet position corrections
    print(f"\n── Position corrections (std_max={args.std_max}°) ─────────────────────")
    for planet in args.planets:
        print(f"\n{planet}:")
        corrs = compute_per_row_corrections(planet, std_max=args.std_max)
        print(f"  Found {len(corrs)} rows to correct")
        for (fname, seq), c in sorted(corrs.items()):
            print(f"    R{seq:5d} ({fname:22s}): "
                  f"{c['old_deg']}°{c['old_am']:02d}' → {c['new_deg']}°{c['new_am']:02d}' "
                  f"(E={c['E_row']:+.3f}°, n={c['n']}, std={c['std']:.3f})")
        apply_position_corrections(planet, corrs, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
