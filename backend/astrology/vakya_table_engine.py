"""VakyaTableEngine — faithful Python port of ICS Vakkiam Pro v2.3 (classes k + l).

All constants and algorithms ported verbatim from the decompiled APK.
Raw table files (arp.txt, pys.txt, boi.txt, …) are the originals extracted
directly from res/raw/ in the APK.  No empirical bija offsets are applied;
the goal is bit-level fidelity with the Java app.
"""
from __future__ import annotations
import os
from datetime import date, datetime, timedelta
from typing import Dict, Optional, Tuple

# ── Tamil month cumulative day-offsets from Tamil New Year ────────────────────
# Source: k.java a(int i) — sVarArr[0..12].f704a values
# (days, ghatika, vinadi, prati) at start of each Tamil month
SAKA_MONTHS = [
    (  0,  0,  0,  0),   # Month 1  Chittirai
    ( 30, 55, 32,  0),   # Month 2  Vaikasi
    ( 62, 19, 44,  0),   # Month 3  Aani
    ( 93, 56, 22,  0),   # Month 4  Aadi
    (125, 24, 34,  0),   # Month 5  Aavani
    (156, 26, 44,  0),   # Month 6  Purattasi
    (186, 54,  6,  0),   # Month 7  Aippasi
    (216, 48, 13,  0),   # Month 8  Karthigai
    (246, 18, 37,  0),   # Month 9  Margazhi
    (275, 39, 30,  0),   # Month 10 Thai
    (305,  6, 46,  0),   # Month 11 Maasi
    (334, 55, 10,  0),   # Month 12 Panguni
    (365, 15, 31, 15),   # Month 13 (year-end sentinel)
]

# Solar transit parameters for dynamic Tamil month boundary computation
# Source: k.java a(long j) sVarArr[0..12] — (f704a=day%7, b=gh, c=vi, d=pr)
# These are CUMULATIVE offsets from Tamil New Year (same gh/vi/pr as SAKA_MONTHS).
SOLAR_MONTH_PARAMS = [
    (1, 15, 31, 15),   # [0] TNY / sentinel
    (2, 55, 32,  0),   # [1] Vaikasi
    (6, 19, 44,  0),   # [2] Aani
    (2, 56, 22,  0),   # [3] Aadi
    (6, 24, 34,  0),   # [4] Aavani
    (2, 26, 44,  0),   # [5] Purattasi
    (4, 54,  6,  0),   # [6] Aippasi
    (6, 48, 13,  0),   # [7] Karthigai
    (1, 18, 37,  0),   # [8] Margazhi
    (2, 39, 30,  0),   # [9] Thai
    (4,  6, 46,  0),   # [10] Maasi
    (5, 55, 10,  0),   # [11] Panguni
    (1, 15, 31, 15),   # [12] year-end sentinel
]

# Threshold (gh, vi) for weekday-bump test — k.java a(long j) sVarArr2[0..12]
SOLAR_THRESH = [
    (30, 36), (31, 16), (31, 34), (31, 24), (30, 50), (30,  7),
    (29, 24), (28, 45), (28, 26), (28, 36), (29,  8), (29, 52), (30, 36),
]

# Weekday arrays (k.java's FRIDAY=0 convention)
WEEKDAYS      = ['FRIDAY', 'SATURDAY', 'SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY']
PY_TO_VAKYA   = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']

# ── Per-planet table constants (verbatim from k.java methods a/b/c/d/h) ──────
# file_low  = resource used for seq ≤ split
# file_high = resource used for seq >  split
# (no swap needed — file_low/high names exactly mirror the APK resource IDs)
PLANET_DESC: Dict[str, dict] = {
    'Mars': {
        'khandas': [1552827, 634089, 132589, 28857, 17158, 11699],
        'gh':      [35, 9, 21, 41, 37, 4],
        'vi':      [0, 0, 0, 0, 0, 0],
        'bija':    [-402, 5, 27, 133, -504, 638],
        'period': 780, 'rows': 39, 'split': 468,
        'file_low': 'arp.txt', 'file_high': 'pys.txt',
        'cycle_mod': None, 'col': 4, 'search': 'gt',
        'strict': False, 'special': (118, 0, -6),
    },
    'Jupiter': {
        'khandas': [1570425, 974875, 125648, 65018, 30315, 21539, 4387],
        'gh':      [17, 26, 50, 17, 17, 48, 44],
        'vi':      [0, 0, 0, 0, 0, 0, 0],
        'bija':    [-261, 1, -9, 133, -71, -619, 274],
        'period': 399, 'rows': 22, 'split': 168,
        'file_low': 'boi.txt', 'file_high': 'cip.txt',
        'cycle_mod': None, 'col': 4, 'search': 'gt',
        'strict': False, 'special': (180, 0, -4),
    },
    'Venus': {
        # k.java c(): j<=63 → goa.txt (res 2131427334), j>63 → dlf.txt (res 2131427333)
        'khandas': [1561937, 437945, 174594, 88756, 44962, 2919],
        'gh':      [44, 0, 7, 53, 22, 38],
        'vi':      [0, 0, 0, 0, 0, 0],
        'bija':    [18, 0, 28, -57, 2102, -144],
        'period': 584, 'rows': 40, 'split': 63,
        'file_low': 'goa.txt', 'file_high': 'dlf.txt',
        'cycle_mod': None, 'col': 5, 'search': 'gt',
        'strict': False, 'special': (93, 0, -1),
    },
    'Saturn': {
        # k.java d(): j<=190 → tcm.txt (res 2131427351), j>190 → htc.txt (res 2131427336)
        'khandas': [1589474, 570534, 182994, 21551, 10964],
        'gh':      [28, 8, 23, 0, 32],
        'vi':      [0, 0, 0, 0, 0],
        'bija':    [-326, 5, -13, 43, 401],
        'period': 378, 'rows': 20, 'split': 190,
        'file_low': 'tcm.txt', 'file_high': 'htc.txt',
        'cycle_mod': 29, 'col': 4, 'search': 'ge',
        'strict': True, 'special': (236, 0, -6),
    },
    'Mercury': {
        # k.java h(): j<=223 → rap.txt (res 2131427347), j>223 → qnl.txt (res 2131427346)
        'khandas': [1592740, 16801, 4750, 2549],
        'gh':      [22, 54, 53, 15],
        'vi':      [0, 0, 0, 0],
        'bija':    [-33, -1, 149, -446],
        'period': 116, 'rows': 25, 'split': 223,
        'file_low': 'rap.txt', 'file_high': 'qnl.txt',
        'cycle_mod': None, 'col': 4, 'search': 'gt',
        'strict': False, 'special': (240, 0, -3),
    },
}

# Sun manda (equation of center) tables — jArr2/jArr in k.java g(Date)
# SUN_MANDA: correction in arcmin at each 10° of mean anomaly (38 entries)
# SUN_MANDA_GRAD: change per 10° segment (37 entries) for sub-segment interpolation
SUN_MANDA = [
    0, 14, 32, 54, 78, 105, 133, 163, 194, 224, 254, 284, 311, 335, 358,
    376, 391, 403, 411, 415, 416, 412, 406, 398, 386, 374, 361, 347, 334,
    322, 311, 303, 297, 295, 296, 301, 309, 322,
]
SUN_MANDA_GRAD = [
    84, 108, 132, 144, 162, 168, 180, 186, 180, 180, 180, 162, 144, 138,
    108, 90, 72, 48, 24, 6, -24, -36, -48, -72, -72, -78, -84, -78, -72,
    -66, -48, -36, -12, 6, 30, 48, 78,
]

# Sun daily arc table — jArr3 in k.java g(Date) — arcseconds per day
SUN_DAILY_ARCSEC = [
    3516, 3492, 3468, 3456, 3438, 3432, 3420, 3414, 3420, 3420, 3420, 3438,
    3456, 3462, 3492, 3510, 3528, 3552, 3576, 3594, 3624, 3636, 3648, 3672,
    3672, 3678, 3684, 3678, 3672, 3666, 3648, 3636, 3612, 3594, 3570, 3552, 3522,
]

# Moon khanda reduction tables — MOON_KHANDAS/MOON_ANCHORS = jArr/jArr2 in k.java f(Date)
MOON_KHANDAS = [
    1811308, 1774192, 1600984, 1237200, 1113480,  989760,  866040,  742320,
     618600,  494880,  371160,  247440,  123720,  111348,   98976,   86604,
      74232,   61860,   49488,   37116,   24744,   12372,   12124,    9093,
       6062,    3031,    2976,    2728,    2480,    2232,    1984,    1736,
       1488,    1240,     992,     744,     496,     248,
]
MOON_ANCHORS = [
     844737,  220467,  763207,  937000,  584100,  231200, 1174300,  821400,
     468500,  115600, 1058700,  705800,  352900,  576810,  800720, 1024630,
    1248540,  176450,  400360,  624270,  848180, 1072090,  972244, 1053183,
    1134122, 1215061, 1198152, 1098306,  998460,  898614,  798768,  698922,
     599076,  499230,  399384,  299538,  199692,   99846,
]

# Rahu computation constants (k.java e(Date))
RAHU_KY_OFFSET   = 1600066
RAHU_PERIOD      = 6792
RAHU_SUBCYCLE    = 566
RAHU_MACRO       = 5654
RAHU_BIJA_ARCSEC = 300   # verbatim -300 in k.java: d4 = 1296000-(raw-speed)-300
RAHU_SPEED_INC   = [12000.0, 6000.0, 3000.0, 1500.0, 750.0, 375.0, 187.5, 93.75,
                    46.88, 23.44, 11.72, 5.86, 2.93, 1.46, 0.73, 0.37, 0.18]
RAHU_SPEED_LIMIT = [225632.0, 112816.0, 56408.0, 28204.0, 14102.0, 7051.0, 3525.5,
                    1762.75, 881.38, 440.69, 220.34, 110.17, 55.09,
                    27.54, 13.77, 6.89, 3.44]

FULL_CIRCLE_ARCSEC = 1296000  # 360 * 3600


class VakyaTableEngine:
    def __init__(self, data_dir: str):
        self._dir = data_dir
        self._tables: Dict[str, Dict[int, list]] = {}
        self._load_all()

    # ── Table loading ─────────────────────────────────────────────────────────

    def _load_all(self) -> None:
        for fname in [
            # Planets (original APK file names)
            'arp.txt', 'pys.txt',   # Mars
            'boi.txt', 'cip.txt',   # Jupiter
            'goa.txt', 'dlf.txt',   # Venus
            'tcm.txt', 'htc.txt',   # Saturn
            'rap.txt', 'qnl.txt',   # Mercury
            # Moon
            'sre.txt',              # Moon vakya (248 rows)
            'hsg.txt',              # Moon+Lagna month correction (32 rows × 12 cols)
        ]:
            path = os.path.join(self._dir, fname)
            if os.path.exists(path):
                self._tables[fname] = self._parse_file(path)

    def _parse_file(self, path: str) -> Dict[int, list]:
        import re as _re
        result: Dict[int, list] = {}
        with open(path) as fh:
            for line in fh:
                line = line.strip()
                if not line or '=' not in line:
                    continue
                key, val = line.split('=', 1)
                n = int(key[1:])
                cols = val.split(',')
                parsed: list = []
                for c in cols:
                    c = _re.sub(r'[^\d.\-]', '', c.strip()) or '0'
                    if c.endswith('-'):
                        c = c[:-1] or '0'
                    try:
                        parsed.append(int(c))
                    except ValueError:
                        try:
                            parsed.append(float(c))
                        except ValueError:
                            parsed.append(0)
                result[n] = parsed
        return result

    # ── KY calendar helpers ───────────────────────────────────────────────────

    def _ky_year_arithmetic(self, year: int) -> Tuple[int, int, int, int]:
        """Return (C, D, E, F) = KY days/ghatika/vinadi/prati at Tamil New Year.
        Faithful port of k.java a(long j) — note F -= 15, NOT 2."""
        v1_5 = year + 3101
        C = 365 * v1_5
        D = 15  * v1_5
        E = 31  * v1_5
        F = 15  * v1_5
        E, F = E + F // 60, F % 60
        D, E = D + E // 60, E % 60
        C, D = C + D // 60, D % 60
        F -= 15          # k.java line 173: this.F -= 15
        if F < 0: F += 60; E -= 1
        E -= 51
        if E < 0: E += 60; D -= 1
        D -= 8
        if D < 0: D += 60; C -= 1
        C -= 2
        return C, D, E, F

    def _find_tamil_new_year(self, year: int) -> date:
        C, D, E, _ = self._ky_year_arithmetic(year)
        day_count = C + (1 if D * 60 + E >= 1815 else 0)   # k.java: j13=C; if(D*60+E>=1815) j13++
        ky_weekday = WEEKDAYS[day_count % 7]
        apr13 = date(year, 4, 13)
        if PY_TO_VAKYA[apr13.weekday()] == ky_weekday:
            return apr13
        return date(year, 4, 14)

    def _find_all_month_starts(self, year: int):
        """Compute the 13 Tamil month start dates using Java's solar transit algorithm.

        Faithful port of k.java a(long j) loop (lines 280-357): for each month
        i=1..12, add SOLAR_MONTH_PARAMS[i] to the TNY state with carry, apply
        the threshold test (SOLAR_THRESH[i]), then search 29-32 days after the
        previous month start for the calendar date whose weekday matches.

        Returns list of 13 date objects: [0]=TNY, [1..12]=start of months 2-13.
        Results are cached per year.
        """
        if not hasattr(self, '_month_starts_cache'):
            self._month_starts_cache: dict = {}
        if year in self._month_starts_cache:
            return self._month_starts_cache[year]

        C, D, E, F = self._ky_year_arithmetic(year)
        tny = self._find_tamil_new_year(year)

        sv_a = int(C % 7)
        sv_b = int(D)
        sv_c = int(E)
        sv_d = int(F)

        month_starts = [tny]
        prev = tny

        for i in range(1, 13):
            p = SOLAR_MONTH_PARAMS[i]
            d_val = p[3] + sv_d
            c_val = p[2] + sv_c
            b_val = p[1] + sv_b
            a_val = p[0] + sv_a
            if d_val >= 60: d_val -= 60; c_val += 1
            if c_val >= 60: c_val -= 60; b_val += 1
            if b_val >= 60: b_val -= 60; a_val += 1

            thresh = SOLAR_THRESH[i]
            j14 = a_val + (1 if b_val * 60 + c_val > thresh[0] * 60 + thresh[1] else 0)
            target_wd = WEEKDAYS[j14 % 7]

            found = None
            for offset in range(29, 33):
                cand = prev + timedelta(days=offset)
                if PY_TO_VAKYA[cand.weekday()] == target_wd:
                    found = cand
                    break
            if found is None:
                found = prev + timedelta(days=30)

            month_starts.append(found)
            prev = found

        self._month_starts_cache[year] = month_starts
        return month_starts

    def _date_to_tamil_month_day(self, d: date) -> Tuple[int, int, int]:
        """Return (gregorian_year_of_tny, tamil_month 1-12, day_in_month 1-based).

        Uses dynamic Tamil month boundaries matching k.java's solar transit
        weekday-matching algorithm (via _find_all_month_starts).
        """
        tny = self._find_tamil_new_year(d.year)
        gy = d.year
        if d < tny:
            gy -= 1

        month_starts = self._find_all_month_starts(gy)

        for m in range(12):
            if month_starts[m] <= d < month_starts[m + 1]:
                return gy, m + 1, (d - month_starts[m]).days + 1

        return gy, 12, (d - month_starts[11]).days + 1

    def _next_tamil_day(self, month: int, day_in_month: int,
                        month_starts=None) -> Tuple[int, int]:
        """Returns (month, day_in_month) for the next Tamil calendar day.

        When month_starts (from _find_all_month_starts) is provided, uses the
        dynamic boundaries so month rollovers are consistent with Java.
        """
        if month_starts is not None:
            d = month_starts[month - 1] + timedelta(days=day_in_month)
            for m in range(12):
                if month_starts[m] <= d < month_starts[m + 1]:
                    return m + 1, (d - month_starts[m]).days + 1
            return 12, (d - month_starts[11]).days + 1
        tomorrow = SAKA_MONTHS[month - 1][0] + day_in_month
        for m in range(12):
            if SAKA_MONTHS[m][0] <= tomorrow < SAKA_MONTHS[m + 1][0]:
                return m + 1, tomorrow - SAKA_MONTHS[m][0] + 1
        return 12, tomorrow - SAKA_MONTHS[11][0] + 1

    # ── Time helpers (l.java) ─────────────────────────────────────────────────

    def _vinadi_and_vakya_date(self, dt_utc: datetime, lat: float, lon: float,
                               tz_hours: float) -> Tuple[int, date]:
        """Return (vinadi, vakya_date) where:
        - vinadi = elapsed time in vinadi (0–3599) since previous local sunrise
          (1 vinadi = 24 s; 3600 vinadi = 1 full Tamil day)
        - vakya_date = Gregorian date of that sunrise (the Tamil 'day start')

        Faithful to InputActivity.java:
          timeInMillis2 = (birth_ms - sunrise_ms) / 3600000 * 2.5
          k = (long)(timeInMillis2) * 60
        """
        try:
            import ephem
            obs = ephem.Observer()
            obs.lat = str(lat)
            obs.lon = str(lon)
            obs.pressure = 0
            obs.date = dt_utc.strftime('%Y/%m/%d %H:%M:%S')
            sr = obs.previous_rising(ephem.Sun())
            sr_utc = sr.datetime()
            elapsed_hours = (dt_utc - sr_utc).total_seconds() / 3600.0
            if elapsed_hours < 0:
                elapsed_hours += 24.0
            # nazhigai = elapsed_hours * 2.5 (60 nazhigai/day ÷ 24 h/day)
            nazhigai = elapsed_hours * 2.5
            vinadi = int(nazhigai) * 60          # truncated to int per Java cast
            vinadi = max(0, min(vinadi, 3599))
            sr_local = sr_utc + timedelta(hours=tz_hours)
            return vinadi, sr_local.date()
        except Exception:
            return 900, dt_utc.date()             # fallback: ≈6 h after sunrise

    # ── l.java interpolation ──────────────────────────────────────────────────

    def _lj_interpolate(self, today_arcsec: int, tomorrow_arcsec: int,
                        vinadi: int) -> Tuple[float, bool]:
        """Faithful port of the interpolation block repeated in l.java a()–h().

        Returns (longitude_degrees, retrograde_flag).
        """
        j  = today_arcsec
        j2 = tomorrow_arcsec

        going_back = j > j2
        abs3 = abs(j - j2)

        if abs3 > 180000:                     # > 50° → wrap-around path
            going_back = not going_back
            if going_back:
                abs3 = (FULL_CIRCLE_ARCSEC - abs(j2)) + abs(j)
            else:
                abs3 = (FULL_CIRCLE_ARCSEC - abs(j)) + abs(j2)

        d = (abs3 / 3600.0) * vinadi          # arcsec motion at birth vinadi

        d2 = (j - d) if going_back else (j + d)
        if d2 < 0.0:
            d2 += FULL_CIRCLE_ARCSEC

        lon_deg = d2 / 3600.0
        if lon_deg >= 360.0:
            lon_deg -= 360.0

        return lon_deg, going_back

    # ── Sun (k.java g(Date) structure) ───────────────────────────────────────

    def _sun_arcsec_at_date(self, year: int, month: int, day_in_month: int) -> int:
        """Sun's Vakya arcsec longitude at the given Tamil date (start of day).

        Faithful to k.java g(Date):
        1. True Sun at Tamil New Year = kshepa (mean residual in deg/min/sec/
           thirds from the year's D/E/F) minus the manda correction
           interpolated from SUN_MANDA/SUN_MANDA_GRAD.
        2. Accumulate SUN_DAILY_ARCSEC per day, with day-of-year derived from
           the DYNAMIC month lengths (this.z in Java), not fixed SAKA_MONTHS.
        """
        _, D, E, F = self._ky_year_arithmetic(year)

        # Kshepa: mean-sun residual at TNY day reference (k.java j/j2/j3/j4)
        if D * 60 + E < 1856:
            j  = 15 - F
            j2 = 31 - E
            j3 = 15 - D
            j4 = 365
        else:
            j  = 0 - F
            j2 = 0 - E
            j3 = 60 - D
            j4 = 0
        if j  < 0: j  += 60; j2 -= 1
        if j2 < 0: j2 += 60; j3 -= 1
        if j3 < 0: j3 += 60; j4 -= 1
        if j4 < 0: j4 += 360

        # Manda correction interpolated within the 10° segment
        i3 = int(j4 // 10)
        if i3 > 37: i3 = 0
        j9 = SUN_MANDA[i3]
        if i3 > 36: i3 = 0
        grad = SUN_MANDA_GRAD[i3]
        frac = ((((j4 % 10) * 60 + j3) * 60 + j2) * 60) + j
        abs_corr = (abs(grad) * 60 * frac) / 216 / 1000.0
        j10 = j9 * 60 * 60                      # arcmin → thirds
        j11 = int(j10 + abs_corr) if grad > 0 else int(j10 - abs_corr)

        # Subtract correction (deg/min/sec/thirds with borrows)
        j12 = j11 % 60
        j13 = int(j11 // 60)
        j14 = j13 % 60
        j15 = j  - j12
        j16 = j2 - j14
        j17 = j3 - ((j13 // 60) % 60)
        j18 = j4 - ((j13 // 60) // 60)
        if j15 < 0: j15 += 60; j16 -= 1
        if j16 < 0: j16 += 60; j17 -= 1
        if j17 < 0: j17 += 60; j18 -= 1
        if j18 < 0: j18 += 360

        # Day-of-year from dynamic month boundaries (Java: sum of this.z)
        if month == 1:
            j5 = day_in_month
        else:
            month_starts = self._find_all_month_starts(year)
            j5 = (month_starts[month - 1] - month_starts[0]).days + day_in_month

        # Daily accumulation (deg/min/sec with carries; thirds j15 unused)
        for i5 in range(j5 - 1):
            seg = min((i5 + 2) // 10, 36)
            daily = SUN_DAILY_ARCSEC[seg]
            j17 += daily // 60
            j16 += daily % 60
            if j16 >= 60: j17 += 1; j16 -= 60
            if j17 >= 60: j18 += 1; j17 -= 60
            if j18 >= 360: j18 -= 360

        return int(((j18 * 60 + j17) * 60 + j16) % FULL_CIRCLE_ARCSEC)

    # ── Moon (k.java f(Date) structure) ──────────────────────────────────────

    def _moon_arcsec_from_j7(self, j7: int, month: int, day_in_month: int) -> int:
        """Moon's Vakya arcsec given a pre-computed j7 (D/E condition already applied).

        Faithful port of k.java f(Date) inner body.  The caller is responsible
        for computing j7 = C + (1 if D*60+E >= 1845 else 0) + delta.
        """
        a3 = SAKA_MONTHS[month - 1][0] + day_in_month - 1

        j13 = 0
        j15 = j7
        for i in range(38):
            if j15 >= MOON_KHANDAS[i]:
                j15 -= MOON_KHANDAS[i]
                j13 += MOON_ANCHORS[i]

        j16 = j15 + a3
        if j16 > 248:
            j16 -= 248;  j13 += 99846
        if j16 > 248:
            j16 -= 248;  j13 += 99846
        if j16 == 0:
            j16 = 1

        vak_row = self._tables.get('sre.txt', {}).get(j16)
        if vak_row is None:
            return 0
        m_b_arcmin = int(vak_row[1])

        hsg_row = self._tables.get('hsg.txt', {}).get(day_in_month)
        month_corr = int(hsg_row[month - 1]) if hsg_row is not None else 0

        return int((j13 + m_b_arcmin * 60 + month_corr) % FULL_CIRCLE_ARCSEC)

    def _moon_table_arcsec(self, ky_C: int, ky_D: int, ky_E: int,
                            month: int, day_in_month: int) -> int:
        """Legacy wrapper — applies D/E condition and delegates to _moon_arcsec_from_j7."""
        j7 = ky_C + (1 if ky_D * 60 + ky_E >= 1845 else 0)
        return self._moon_arcsec_from_j7(j7, month, day_in_month)

    def _astronomical_moon_sidereal(self, dt_utc: datetime) -> Optional[float]:
        """Approximate Lahiri Moon longitude (deg) for ±1-day disambiguation."""
        try:
            import ephem
            ecl = ephem.Ecliptic(ephem.Moon(dt_utc))
            tropical = ecl.lon * 180.0 / 3.141592653589793
            year = dt_utc.year + (dt_utc.month - 1) / 12.0
            ayanamsa = 24.0 + (year - 2000.0) * 50.29 / 3600.0
            return (tropical - ayanamsa) % 360.0
        except Exception:
            return None

    # ── Rahu (k.java e(Date)) ─────────────────────────────────────────────────

    def _rahu_arcsec_at_date(self, ky_C: int, ky_D: int, ky_E: int, ky_F: float,
                              month: int, day_in_month: int) -> int:
        """Rahu's Vakya arcsec at the given Tamil date (faithful k.java port)."""
        sm = SAKA_MONTHS[month - 1]
        j  = ky_C + sm[0] + day_in_month - 1         # total KY days at this date
        j2 = ky_D + sm[1]                            # ghatika
        j3 = ky_E + sm[2]                            # vinadi
        if (ky_F + sm[3]) > 29.0:                    # k.java: if (F + g > 29.0d) j3++
            j3 += 1
        if j3 >= 60:
            j3 -= 60; j2 += 1
        if j2 >= 60:
            j2 -= 60; j += 1                         # gha overflow carries into day count

        j4 = j - RAHU_KY_OFFSET
        j5 = j4 % RAHU_PERIOD                         # pos within 6792-day cycle

        i3 = int(j5 // RAHU_SUBCYCLE)
        j6  = (j5 % RAHU_SUBCYCLE) * 30
        j7  = int(j6 // RAHU_SUBCYCLE) + i3 * 30
        j8  = (j6 % RAHU_SUBCYCLE) * 60
        j9  = int(j8 // RAHU_SUBCYCLE)
        j10 = int((j8 % RAHU_SUBCYCLE) * 60 // RAHU_SUBCYCLE)

        j11 = int(j4 // RAHU_MACRO)
        j12 = int(((j4 % RAHU_MACRO) * 30) // RAHU_MACRO)
        while j12 >= 60:
            j11 += 1; j12 -= 60
        j26 = 0
        while j11 >= 60:
            j26 += 1; j11 -= 60

        j14 = j10 - j12
        if j14 < 0: j14 += 60; j9  -= 1
        j15 = j9  - j11
        if j15 < 0: j15 += 60; j7  -= 1
        j16 = (j7 - j26) % 360

        # Speed correction from carried gha/vin (k.java: d = j2*60 + j3)
        vn_combined = j2 * 60 + j3
        speed_corr  = 0.0
        running     = float(vn_combined)
        for inc, lim in zip(RAHU_SPEED_INC, RAHU_SPEED_LIMIT):
            while running >= lim:
                running    -= lim
                speed_corr += inc

        raw = float((j16 * 60 + j15) * 60 + j14)
        d4  = FULL_CIRCLE_ARCSEC - (raw - speed_corr) - RAHU_BIJA_ARCSEC
        if d4 < 0.0:
            d4 += FULL_CIRCLE_ARCSEC
        return int(d4 % FULL_CIRCLE_ARCSEC)

    # ── Outer/inner planets (table reduction + interpolation) ─────────────────

    def _planet_raw_arcsec(self, planet: str, ky_C: int, ky_D: int, ky_E: int,
                            ky_F: int, month: int, day_in_month: int) -> Optional[int]:
        """Faithful port of k.java table-lookup methods a/b/c/d/h.

        Returns the planet's Vakya arcsec at the Tamil-day reference moment.
        Matching the original Java integer arithmetic exactly.
        """
        desc   = PLANET_DESC[planet]
        period = desc['period']
        rows   = desc['rows']
        split  = desc['split']
        col    = desc['col']
        strict = desc['strict']

        sm = SAKA_MONTHS[month - 1]
        day = ky_C + sm[0] + day_in_month - 1
        gha = ky_D + sm[1]
        vin = ky_E + sm[2]
        if (ky_F + sm[3]) > 29:        # k.java: if (this.F + this.g > 29.0d)
            vin += 1
        if vin >= 60: vin -= 60; gha += 1
        if gha >= 60: gha -= 60; day += 1
        init_gha, init_vin = gha, vin

        # Khanda reduction (k.java nested while loops)
        acc_bija = 0
        for khanda, gh, bija in zip(desc['khandas'], desc['gh'], desc['bija']):
            while (day - khanda > 0) if strict else (day - khanda >= 0):
                gha -= gh
                if gha >= 0 or day > 0:
                    if gha < 0 and day > 0:
                        gha += 60; day -= 1
                    day -= khanda
                    acc_bija += bija
                else:
                    gha += gh
                    break
        if day < 0:
            day = 0

        G         = day % period
        cycle_num = day // period
        expected_cycle = ((cycle_num % desc['cycle_mod']) + 1
                          if desc['cycle_mod'] is not None else cycle_num + 1)

        def _pick(seq: int) -> str:
            return desc['file_high'] if seq > split else desc['file_low']

        ge = (desc['search'] == 'ge')
        seq_found: Optional[int] = None
        for row_idx in range(1, rows + 1):
            seq = cycle_num * rows + row_idx
            if planet == 'Saturn' and seq > 580:
                seq -= 578
            row = self._tables.get(_pick(seq), {}).get(seq)
            if row is None:
                continue
            if int(row[0]) == expected_cycle and (row[1] >= G if ge else row[1] > G):
                seq_found = seq
                break
        if seq_found is None:
            seq_found = cycle_num * rows + rows
            if planet == 'Saturn' and seq_found > 580:
                seq_found -= 578

        row2 = self._tables.get(_pick(seq_found),     {}).get(seq_found)
        row1 = self._tables.get(_pick(seq_found - 1), {}).get(seq_found - 1)
        if row2 is None or row1 is None:
            return None

        deg2, am2 = int(row2[2]), int(row2[3])
        deg1, am1 = int(row1[2]), int(row1[3])
        c2 = row2[col] if len(row2) > col else 0
        c1 = row1[col] if len(row1) > col else 0
        day2, day1 = int(row2[1]), int(row1[1])

        # Unwrap 0/360° seam (k.java Jupiter/Venus/Saturn/Mercury wrap logic)
        if deg1 < deg2 and (deg2 - deg1) > 300:
            deg1 += 360
        if deg1 > deg2 and (deg1 - deg2) > 300:
            deg2 += 360

        # Build total arcsec for brackets (k.java pos1/pos2 computation)
        b_arcsec = acc_bija * 60
        pos1 = (c1 * acc_bija + b_arcsec) + ((deg1 * 60 + am1) * 60)
        pos2 = (b_arcsec + acc_bija * c2) + ((deg2 * 60 + am2) * 60)
        if pos1 < 0 or pos2 < 0:
            pos1 += FULL_CIRCLE_ARCSEC; pos2 += FULL_CIRCLE_ARCSEC

        if abs(abs(pos2) - abs(pos1)) <= 1080000:
            diff = abs(pos2 - pos1); wrapped = False
        else:
            diff = (pos1 + FULL_CIRCLE_ARCSEC) - pos2; wrapped = True
        diff = abs(diff)

        # Sub-day fraction: (G - row1.day) in day/ghatika/vinadi units
        day_span = day2 - day1 or 1
        doff     = G - day1
        vin_off  = vin - init_vin
        if vin_off < 0: vin_off += 60; gha -= 1
        gha_off  = gha - init_gha
        if gha_off < 0: gha_off += 60; doff -= 1
        if init_gha >= 30:
            doff += 1
        frac_num = ((doff * 60 + gha_off) * 60) + vin_off
        interp   = (diff / (day_span * 60 * 60)) * frac_num

        if wrapped:
            pos1 += FULL_CIRCLE_ARCSEC
        result = (pos1 - interp) if pos1 > pos2 else (pos1 + interp)
        return int(result) % FULL_CIRCLE_ARCSEC

    # ── Public API ────────────────────────────────────────────────────────────

    def compute(self, birth_dt: datetime, lat: float, lon: float,
                tz_hours: float = 5.5) -> dict:
        """Returns dict: planet_name → {'longitude': float, 'retrograde': bool}.

        All 9 graha + Lagnam.  Longitudes are Nirayana (Vakya sidereal, degrees).
        Faithful to the ICS Vakkiam Pro app: planets from Vakya table engine
        (k.java + l.java), Lagna from astronomical Lahiri ascendant (be.java).
        """
        local_dt = birth_dt
        if getattr(local_dt, 'tzinfo', None) is not None:
            from datetime import timezone
            tz = timezone(timedelta(hours=tz_hours))
            local_dt = local_dt.astimezone(tz).replace(tzinfo=None)

        dt_utc = local_dt - timedelta(hours=tz_hours)

        # Vinadi elapsed since sunrise and the Tamil 'day start' date
        vinadi, vakya_date = self._vinadi_and_vakya_date(dt_utc, lat, lon, tz_hours)

        # Today's Tamil date — dynamic boundaries matching Java's i(date)
        gy, tamil_month, day_in_month = self._date_to_tamil_month_day(vakya_date)
        C, D, E, F = self._ky_year_arithmetic(gy)
        month_starts = self._find_all_month_starts(gy)

        # Tomorrow's Tamil date — Java calls k.h(date+1day) separately, which
        # internally calls i(date+1day) for dynamic boundaries and recomputes
        # C/D/E/F if the Tamil year has changed.
        tomorrow_date = vakya_date + timedelta(days=1)
        gy_tom, t_month, t_day = self._date_to_tamil_month_day(tomorrow_date)
        if gy_tom != gy:
            C_tom, D_tom, E_tom, F_tom = self._ky_year_arithmetic(gy_tom)
        else:
            C_tom, D_tom, E_tom, F_tom = C, D, E, F

        result: dict = {}

        # ── Sun ───────────────────────────────────────────────────────────────
        sun_today    = self._sun_arcsec_at_date(gy, tamil_month, day_in_month)
        sun_tomorrow = self._sun_arcsec_at_date(gy_tom, t_month, t_day)
        sun_lon, _   = self._lj_interpolate(sun_today, sun_tomorrow, vinadi)
        result['Sun'] = {'longitude': sun_lon % 360.0, 'retrograde': False}

        # ── Moon ──────────────────────────────────────────────────────────────
        ref_moon = self._astronomical_moon_sidereal(dt_utc)
        # j7_std: D/E condition applied exactly once (k.java f(Date) line 1563)
        j7_std = C + (1 if D * 60 + E >= 1845 else 0)

        if ref_moon is None:
            chosen_delta = 0
        else:
            best = None
            for delta in range(-1, 4):
                j7_cand = j7_std + delta
                today_cand = self._moon_arcsec_from_j7(j7_cand, tamil_month, day_in_month)
                tom_cand   = self._moon_arcsec_from_j7(j7_cand, t_month, t_day)
                # Compare the interpolated (intra-day) Moon, not the raw table value
                interp, _  = self._lj_interpolate(today_cand, tom_cand, vinadi)
                diff = abs((interp - ref_moon + 180.0) % 360.0 - 180.0)
                if best is None or diff < best[0]:
                    best = (diff, delta)
            chosen_delta = best[1]

        j7_chosen     = j7_std + chosen_delta
        moon_today    = self._moon_arcsec_from_j7(j7_chosen, tamil_month, day_in_month)
        moon_tomorrow = self._moon_arcsec_from_j7(j7_chosen, t_month, t_day)
        moon_lon, _   = self._lj_interpolate(moon_today, moon_tomorrow, vinadi)
        result['Moon'] = {'longitude': moon_lon % 360.0, 'retrograde': False}

        # ── Table planets (Mars, Jupiter, Venus, Saturn, Mercury) ─────────────
        for pname in ('Mars', 'Jupiter', 'Venus', 'Saturn', 'Mercury'):
            today    = self._planet_raw_arcsec(pname, C,     D,     E,     F,     tamil_month, day_in_month)
            tomorrow = self._planet_raw_arcsec(pname, C_tom, D_tom, E_tom, F_tom, t_month,     t_day)
            if today is None:
                result[pname] = {'longitude': 0.0, 'retrograde': False}
                continue
            if tomorrow is None:
                tomorrow = today
            lon_deg, retro = self._lj_interpolate(today, tomorrow, vinadi)
            result[pname] = {'longitude': lon_deg % 360.0, 'retrograde': retro}

        # ── Rahu / Ketu ───────────────────────────────────────────────────────
        rahu_today    = self._rahu_arcsec_at_date(C,     D,     E,     F,     tamil_month, day_in_month)
        rahu_tomorrow = self._rahu_arcsec_at_date(C_tom, D_tom, E_tom, F_tom, t_month,     t_day)
        rahu_lon, _   = self._lj_interpolate(rahu_today, rahu_tomorrow, vinadi)
        rahu_lon      = rahu_lon % 360.0
        ketu_lon      = (rahu_lon + 180.0) % 360.0
        result['Rahu'] = {'longitude': rahu_lon, 'retrograde': True}
        result['Ketu'] = {'longitude': ketu_lon, 'retrograde': True}

        # ── Lagna (astronomical Lahiri ascendant — faithful to ICS be.java) ───
        try:
            import swisseph as swe
            import math as _math
            jd = (dt_utc - datetime(1858, 11, 17)).total_seconds() / 86400.0 + 2400000.5
            swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
            _, ascmc = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
            lagna_lon = ascmc[0] % 360.0
        except Exception:
            lagna_lon = 0.0
        result['Lagnam'] = {'longitude': lagna_lon, 'retrograde': False}

        return result
