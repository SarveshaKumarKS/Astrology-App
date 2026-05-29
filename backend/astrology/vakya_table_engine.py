"""VakyaTableEngine — classical Vakya table-lookup planetary calculator.

All constants extracted from decompiled Android app (ICS Vakkiam Pro v2.3),
Java classes k, l, and i.  Covers all 9 bodies.
"""
from __future__ import annotations
import os
from datetime import date, datetime, timedelta
from typing import Dict, Optional, Tuple

# ── Saka month cumulative day-offsets from Tamil New Year ─────────────────────
# (days, ghatika, vinadi, prati)  — source: k.a(int p18), table v2[0..12]
SAKA_MONTHS = [
    (  0,  0,  0,  0),
    ( 30, 55, 32,  0),
    ( 62, 19, 44,  0),
    ( 93, 56, 22,  0),
    (125, 24, 34,  0),
    (156, 26, 44,  0),
    (186, 54,  6,  0),
    (216, 48, 13,  0),
    (246, 18, 37,  0),
    (275, 39, 30,  0),
    (305,  6, 46,  0),
    (334, 55, 10,  0),
    (365, 15, 31, 15),
]

WEEKDAYS = ['FRIDAY', 'SATURDAY', 'SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY']
PY_TO_VAKYA = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']

# ── Per-planet reduction constants ────────────────────────────────────────────
PLANET_DESC: Dict[str, dict] = {
    'Mars': {
        'khandas': [1552827, 634089, 132589, 28857, 17158, 11699],
        'gh':      [35, 9, 21, 41, 37, 4],
        'bija':    [-402, 5, 27, 133, -504, 638],
        'period': 780, 'rows': 39, 'split': 468,
        'file_low': 'mars_low.txt', 'file_high': 'mars_high.txt',
        'cycle_mod': None,
    },
    'Jupiter': {
        'khandas': [1570425, 974875, 125648, 65018, 30315, 21539, 4387],
        'gh':      [17, 26, 50, 17, 17, 48, 44],
        'bija':    [-261, 1, -9, 133, -71, -619, 274],
        'period': 399, 'rows': 22, 'split': 168,
        'file_low': 'jupiter_low.txt', 'file_high': 'jupiter_high.txt',
        'cycle_mod': None,
    },
    'Venus': {
        'khandas': [1561937, 437945, 174594, 88756, 44962, 2919],
        'gh':      [44, 0, 7, 53, 22, 38],
        'bija':    [18, 0, 28, -57, 2102, -144],
        'period': 584, 'rows': 40, 'split': 63,
        'file_low': 'venus_low.txt', 'file_high': 'venus_high.txt',
        'cycle_mod': None,
    },
    'Saturn': {
        'khandas': [1589474, 570534, 182994, 21551, 10964],
        'gh':      [28, 8, 23, 0, 32],
        'bija':    [-326, 5, -13, 43, 401],
        'period': 378, 'rows': 20, 'split': 190,
        'file_low': 'saturn_low.txt', 'file_high': 'saturn_high.txt',
        'cycle_mod': 29,
    },
    'Mercury': {
        'khandas': [1592740, 16801, 4750, 2549],
        'gh':      [22, 54, 53, 15],
        'bija':    [-33, -1, 149, -446],
        'period': 116, 'rows': 25, 'split': 223,
        'file_low': 'mercury_low.txt', 'file_high': 'mercury_high.txt',
        'cycle_mod': None,
    },
}

# Sun daily motion table (arcseconds/day per 10-degree segment)
SUN_DAILY_ARCSEC = [
    3516, 3492, 3468, 3456, 3438, 3432, 3420, 3414, 3420, 3420, 3420, 3438,
    3456, 3462, 3492, 3510, 3528, 3552, 3576, 3594, 3624, 3636, 3648, 3672,
    3672, 3678, 3684, 3678, 3672, 3666, 3648, 3636, 3612, 3594, 3570, 3552, 3522,
]

# Rahu constants
RAHU_PERIOD      = 6792
RAHU_SUBCYCLE    = 566
RAHU_MACRO       = 5654
RAHU_KY_OFFSET   = 1600066
RAHU_BIJA_ARCSEC = 300
RAHU_SPEED_INC   = [12000, 6000, 3000, 1500, 750, 375, 187.5, 93.75,
                    46.88, 23.44, 11.72, 5.86, 2.93, 1.46, 0.73, 0.37, 0.18]
RAHU_SPEED_LIMIT = [225632, 112816, 56408, 28204, 14102, 7051, 3525.5,
                    1762.75, 881.38, 440.69, 220.34, 110.17, 55.09,
                    27.54, 13.77, 6.89, 3.44]

# Moon 38-element reduction table
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

FULL_CIRCLE_ARCSEC = 1296000  # 360 * 3600

# Moon bija: residual offset after ghatika interpolation, calibrated across
# the 729-case reference set.  Adjusted when ghatika correction is active.
MOON_BIJA_DEG = 0.38


class VakyaTableEngine:
    def __init__(self, data_dir: str):
        self._dir = data_dir
        self._tables: Dict[str, Dict[int, list]] = {}
        self._load_all()

    # ── File loading ──────────────────────────────────────────────────────────

    def _load_all(self) -> None:
        for fname in [
            'mars_low.txt', 'mars_high.txt',
            'jupiter_low.txt', 'jupiter_high.txt',
            'venus_low.txt', 'venus_high.txt',
            'saturn_low.txt', 'saturn_high.txt',
            'mercury_low.txt', 'mercury_high.txt',
            'moon_low.txt', 'moon_high.txt',
            'lagna_aux.txt',
        ]:
            self._tables[fname] = self._parse_file(os.path.join(self._dir, fname))

    def _parse_file(self, path: str) -> Dict[int, list]:
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
                    c = c.strip()
                    # strip stray non-numeric chars (decompilation artefacts)
                    import re as _re
                    c = _re.sub(r'[^\d.\-]', '', c) or '0'
                    try:
                        parsed.append(int(c))
                    except ValueError:
                        parsed.append(float(c))
                result[n] = parsed
        return result

    # ── KY calendar helpers ───────────────────────────────────────────────────

    def _ky_year_arithmetic(self, year: int) -> Tuple[int, int, int, int]:
        """Return (C, D, E, F) = KY days/ghatika/vinadi/prati at Tamil New Year."""
        v1_5 = year + 3101
        C = 365 * v1_5
        D = 15  * v1_5
        E = 31  * v1_5
        F = 15  * v1_5
        E, F = E + F // 60, F % 60
        D, E = D + E // 60, E % 60
        C, D = C + D // 60, D % 60
        F -= 2
        if F < 0: F += 60; E -= 1
        E -= 51
        if E < 0: E += 60; D -= 1
        D -= 8
        if D < 0: D += 60; C -= 1
        C -= 2
        return C, D, E, F

    def _find_tamil_new_year(self, year: int) -> date:
        C, D, E, F = self._ky_year_arithmetic(year)
        day_count = C + 1 + (1 if D * 60 + E >= 1815 else 0)
        ky_weekday = WEEKDAYS[day_count % 7]
        apr13 = date(year, 4, 13)
        if PY_TO_VAKYA[apr13.weekday()] == ky_weekday:
            return apr13
        return date(year, 4, 14)

    def _date_to_tamil_month_day(self, d: date) -> Tuple[int, int, int]:
        """Return (gregorian_year_of_tny, tamil_month 1-12, day_in_month 1-based)."""
        tny = self._find_tamil_new_year(d.year)
        gy = d.year
        if d < tny:
            gy -= 1
            tny = self._find_tamil_new_year(gy)

        days_since_tny = (d - tny).days

        for m in range(12):
            if SAKA_MONTHS[m][0] <= days_since_tny < SAKA_MONTHS[m + 1][0]:
                day_in_month = days_since_tny - SAKA_MONTHS[m][0] + 1
                return gy, m + 1, day_in_month

        return gy, 12, days_since_tny - SAKA_MONTHS[11][0] + 1

    # ── Sunrise helper ────────────────────────────────────────────────────────

    def _ghatika_and_vakya_date(self, dt_utc: datetime, lat: float, lon: float,
                                tz_hours: float) -> tuple:
        """Return (ghatika, vakya_date) where vakya_date is the local date of the
        most-recent sunrise (= the start of the current Vakya day).
        1 ghatika = 24 minutes.  dt_utc must be a naive UTC datetime."""
        try:
            import ephem
            obs = ephem.Observer()
            obs.lat = str(lat)
            obs.lon = str(lon)
            obs.pressure = 0
            obs.date = dt_utc.strftime('%Y/%m/%d %H:%M:%S')
            sr = obs.previous_rising(ephem.Sun())
            sr_utc = sr.datetime()
            elapsed_min = (dt_utc - sr_utc).total_seconds() / 60.0
            if elapsed_min < 0:
                elapsed_min += 1440.0
            ghatika = max(0, min(int(elapsed_min / 24.0), 59))
            # Vakya day = the calendar date in local time when the last sunrise occurred
            sr_local = sr_utc + timedelta(hours=tz_hours)
            return ghatika, sr_local.date()
        except Exception:
            return 15, dt_utc.date()

    def _ghatika_since_sunrise(self, dt_utc: datetime, lat: float, lon: float) -> int:
        """1 ghatika = 24 minutes.  dt_utc must be a naive UTC datetime."""
        ghatika, _ = self._ghatika_and_vakya_date(dt_utc, lat, lon, 5.5)
        return ghatika

    def _astronomical_moon_sidereal(self, dt_utc: datetime) -> Optional[float]:
        """Approximate Nirayana (Lahiri-sidereal) Moon longitude in degrees, used
        only to disambiguate the tabular day count.  Precision of a couple of
        degrees is sufficient since the candidate days differ by ~13.3°.
        Returns None if ephem is unavailable."""
        try:
            import ephem
            ecl = ephem.Ecliptic(ephem.Moon(dt_utc))
            tropical = ecl.lon * 180.0 / 3.141592653589793
            # Lahiri ayanamsa: ~24.0° at J2000, precessing ~50.29 arcsec/yr.
            year = dt_utc.year + (dt_utc.month - 1) / 12.0
            ayanamsa = 24.0 + (year - 2000.0) * 50.29 / 3600.0
            return (tropical - ayanamsa) % 360.0
        except Exception:
            return None

    # ── Sun ───────────────────────────────────────────────────────────────────

    def _calc_sun(self, year: int, month: int, day_in_month: int, ghatika: int) -> float:
        tny = self._find_tamil_new_year(year)
        birth_date = tny + timedelta(days=SAKA_MONTHS[month - 1][0] + day_in_month - 1)
        days_since_tny = (birth_date - tny).days

        sun_arcsec = 0.0
        for d in range(days_since_tny):
            seg = min((d + 2) // 10, 36)
            sun_arcsec += SUN_DAILY_ARCSEC[seg]

        seg = min((days_since_tny + 2) // 10, 36)
        sun_arcsec += SUN_DAILY_ARCSEC[seg] * ghatika / 60.0

        return (sun_arcsec % FULL_CIRCLE_ARCSEC) / 3600.0

    # ── Moon ──────────────────────────────────────────────────────────────────

    def _moon_for_total_days(self, total_days: int, month: int,
                             day_in_month: int,
                             ghatika: Optional[int] = None) -> float:
        """Tabular Vakya Moon longitude (decimal degrees).

        When ghatika is supplied the table value (which represents the Moon at
        the *next* sunrise, i.e. ghatika 60) is interpolated back to the birth
        ghatika by subtracting (60 − ghatika) × daily_increment.
        When ghatika is None the legacy lagna_aux correction is used instead.
        No bija is applied here — that is added by the caller.
        """
        v14_1 = total_days
        v30 = 0
        for i in range(38):
            if v14_1 >= MOON_KHANDAS[i]:
                v14_1 -= MOON_KHANDAS[i]
                v30   += MOON_ANCHORS[i]

        # NOTE: the decompiled "special band" path (triggered when an intermediate
        # residual lands in [2665, 3031]) was designed for the ky_C-only input.
        # With the total_days input it fires spuriously and corrupts results,
        # so it is intentionally omitted here.
        v14_3 = v14_1
        if v14_3 > 248:
            v14_3 -= 248
            v30   += 99846
            if v14_3 > 248:
                v30   += 99846
                v14_3 -= 248

        if v14_3 == 0:
            v14_3 = 1

        vak_row = self._tables['moon_low.txt'].get(v14_3)
        if vak_row is None:
            return 0.0
        m_base = int(vak_row[1]) * 60  # arcminutes → arcseconds

        if ghatika is not None:
            # Intra-day interpolation back to birth ghatika.
            # vak_row[2] is arcmin/day = arcsec/ghatika (after unit conversion).
            increment = int(vak_row[2])
            moon_arcsec = (v30 + m_base - (60 - ghatika) * increment) % FULL_CIRCLE_ARCSEC
        else:
            hsg_row = self._tables['lagna_aux.txt'].get(day_in_month)
            if hsg_row is None:
                return 0.0
            daily_motion = int(hsg_row[month - 1])
            moon_arcsec = (daily_motion + v30 + m_base) % FULL_CIRCLE_ARCSEC

        return moon_arcsec / 3600.0

    def _calc_moon(self, ky_C: int, ky_D: int, ky_E: int,
                   month: int, day_in_month: int,
                   ref_moon_lon: Optional[float] = None,
                   ghatika: Optional[int] = None) -> float:
        """Vakya Moon longitude (Nirayana, decimal degrees).

        The tabular value represents the Moon at *next sunrise* (ghatika 60).
        When ghatika is provided, intra-day interpolation corrects to birth time.
        Ephemeris disambiguation resolves ±1-day ambiguity at day boundaries.
        """
        sm = SAKA_MONTHS[month - 1]
        base_days = ky_C + sm[0] + day_in_month - 1
        default_bump = 1 if ky_D * 60 + ky_E >= 1845 else 0

        if ref_moon_lon is None:
            chosen = base_days + default_bump
        else:
            best = None
            # With ghatika correction the optimal day can be up to +2 above
            # default_bump for PM/evening births where default_bump=0.
            bump_range = (range(default_bump - 1, default_bump + 3)
                          if ghatika is not None
                          else range(default_bump - 1, default_bump + 2))
            for bump in bump_range:
                # Use ghatika-corrected value for disambiguation so the right
                # day is selected for both AM and PM births.
                clon = self._moon_for_total_days(
                    base_days + bump, month, day_in_month, ghatika)
                diff = abs((clon - ref_moon_lon + 180.0) % 360.0 - 180.0)
                if best is None or diff < best[0]:
                    best = (diff, base_days + bump)
            chosen = best[1]

        moon_deg = self._moon_for_total_days(chosen, month, day_in_month, ghatika)
        return (moon_deg + MOON_BIJA_DEG) % 360.0

    # ── Rahu ──────────────────────────────────────────────────────────────────

    def _calc_rahu(self, ky_C: int, ky_D: int, ky_E: int,
                   month: int, day_in_month: int) -> float:
        sm = SAKA_MONTHS[month - 1]
        d_days   = sm[0]
        e_arcmin = sm[1]

        v7_4 = ky_C + d_days + day_in_month - 1
        v7_6 = v7_4 - RAHU_KY_OFFSET
        v14_9 = v7_6 % RAHU_PERIOD

        v14_11 = (v14_9 % RAHU_SUBCYCLE) * 30
        v1_6   = v14_11 // RAHU_SUBCYCLE + (v14_9 // RAHU_SUBCYCLE) * 30
        v14_13 = (v14_11 % RAHU_SUBCYCLE) * 60
        v5_8   = v14_13 // RAHU_SUBCYCLE

        v13_2 = v7_6 // RAHU_MACRO
        v7_12 = ((v7_6 % RAHU_MACRO) * 30) // RAHU_MACRO
        while v7_12 >= 60:
            v7_12 -= 60
            v13_2 += 1
        v26 = 0
        while v13_2 >= 60:
            v13_2 -= 60
            v26 += 1

        v7_13 = ((v14_13 % RAHU_SUBCYCLE) * 60 // RAHU_SUBCYCLE) - v7_12
        if v7_13 < 0:
            v7_13 += 60
            v5_8  -= 1
        v5_9 = v5_8 - v13_2
        if v5_9 < 0:
            v5_9 += 60
            v1_6 -= 1
        v1_7 = (v1_6 - v26) % 360

        vn_combined  = (ky_D + e_arcmin) * 60 + ky_E
        speed_corr   = 0.0
        running      = float(vn_combined)
        for inc, lim in zip(RAHU_SPEED_INC, RAHU_SPEED_LIMIT):
            while running >= lim:
                running   -= lim
                speed_corr += inc

        raw_arcsec  = float((v1_7 * 60 + v5_9) * 60 + v7_13)
        rahu_arcsec = int(FULL_CIRCLE_ARCSEC - (raw_arcsec - speed_corr) - RAHU_BIJA_ARCSEC)
        rahu_arcsec = rahu_arcsec % FULL_CIRCLE_ARCSEC
        return rahu_arcsec / 3600.0

    # ── Outer/inner planets (table reduction + interpolation) ─────────────────

    def _next_tamil_day(self, month: int, day_in_month: int) -> Tuple[int, int]:
        """Returns (month, day_in_month) for the next Tamil calendar day."""
        tomorrow = SAKA_MONTHS[month - 1][0] + day_in_month  # tomorrow's 0-indexed day from TNY
        for m in range(12):
            if SAKA_MONTHS[m][0] <= tomorrow < SAKA_MONTHS[m + 1][0]:
                return m + 1, tomorrow - SAKA_MONTHS[m][0] + 1
        return 12, tomorrow - SAKA_MONTHS[11][0] + 1

    def _planet_raw_arcsec(self, planet: str, ky_C: int, ky_D: int, ky_E: int,
                            month: int, day_in_month: int) -> Optional[float]:
        """Planet longitude in arcseconds at ghatika=0 (sunrise) for the given Tamil calendar day."""
        desc   = PLANET_DESC[planet]
        period = desc['period']
        rows   = desc['rows']
        split  = desc['split']

        sm    = SAKA_MONTHS[month - 1]
        v10_0 = ky_C + sm[0] + day_in_month - 1
        v12   = ky_D + sm[1]

        accumulated_bija = 0
        # Saturn uses strict > (not >=) per decompiled Java l.g()
        saturn = (planet == 'Saturn')
        for khanda, gh, bija in zip(desc['khandas'], desc['gh'], desc['bija']):
            while (v10_0 > khanda if saturn else v10_0 >= khanda):
                v10_0 -= khanda
                v12   -= gh
                while v12 < 0:
                    v12   += 60
                    v10_0 -= 1
                accumulated_bija += bija

        G         = v10_0 % period
        cycle_num = v10_0 // period
        expected_cycle = ((cycle_num % desc['cycle_mod']) + 1
                          if desc['cycle_mod'] is not None else cycle_num + 1)

        seq_found: Optional[int] = None
        for row_idx in range(1, rows + 1):
            seq = cycle_num * rows + row_idx
            if planet == 'Saturn' and seq > 580:
                seq -= 578
            fname = desc['file_high'] if seq > split else desc['file_low']
            row = self._tables[fname].get(seq)
            if row is None:
                continue
            if int(row[0]) == expected_cycle and row[1] > G:
                seq_found = seq
                break

        if seq_found is None:
            seq_found = cycle_num * rows + rows
            if planet == 'Saturn' and seq_found > 580:
                seq_found -= 578

        seq_prev = seq_found - 1
        fname2 = desc['file_high'] if seq_found > split else desc['file_low']
        fname1 = desc['file_high'] if seq_prev  > split else desc['file_low']

        row2 = self._tables[fname2].get(seq_found)
        row1 = self._tables[fname1].get(seq_prev)
        if row2 is None or row1 is None:
            return None

        # field4 (5th column) carries a per-row latitude correction scaled by bija:
        #   pos = deg*3600 + arcmin*60 + bija_arcmin*60 + field4*bija_arcmin
        bija_arcmin = accumulated_bija
        bija_arcsec = accumulated_bija * 60
        f4_1 = row1[4] if len(row1) > 4 else 0
        f4_2 = row2[4] if len(row2) > 4 else 0
        pos1 = int(row1[2]) * 3600 + int(row1[3]) * 60 + bija_arcsec + f4_1 * bija_arcmin
        pos2 = int(row2[2]) * 3600 + int(row2[3]) * 60 + bija_arcsec + f4_2 * bija_arcmin

        if abs(pos2 - pos1) > 1080000:
            if pos2 < pos1:
                pos2 += FULL_CIRCLE_ARCSEC
            else:
                pos1 += FULL_CIRCLE_ARCSEC

        day_span = int(row2[1]) - int(row1[1])
        if day_span <= 0:
            day_span = 1

        G_offset = G - int(row1[1])  # days since row1 entry
        pos = pos1 + (pos2 - pos1) * G_offset / day_span
        return pos % FULL_CIRCLE_ARCSEC

    def _calc_planet(self, planet: str, ky_C: int, ky_D: int, ky_E: int,
                     month: int, day_in_month: int, ghatika: int) -> Tuple[float, bool]:
        today_arcsec = self._planet_raw_arcsec(planet, ky_C, ky_D, ky_E, month, day_in_month)
        if today_arcsec is None:
            return 0.0, False

        t_month, t_day = self._next_tamil_day(month, day_in_month)
        tomorrow_arcsec = self._planet_raw_arcsec(planet, ky_C, ky_D, ky_E, t_month, t_day)
        if tomorrow_arcsec is None:
            return today_arcsec / 3600.0, False

        retrograde = today_arcsec > tomorrow_arcsec
        daily_motion = abs(today_arcsec - tomorrow_arcsec)

        if daily_motion > 180000:  # > 50° wrap-around
            retrograde = not retrograde
            if retrograde:
                daily_motion = (FULL_CIRCLE_ARCSEC - tomorrow_arcsec) + today_arcsec
            else:
                daily_motion = (FULL_CIRCLE_ARCSEC - today_arcsec) + tomorrow_arcsec

        vinadi = ghatika * 60  # vinadi_since_sunrise = ghatika × 60
        frac_arcsec = (daily_motion / 3600.0) * vinadi

        if not retrograde:
            result_arcsec = today_arcsec + frac_arcsec
        else:
            result_arcsec = today_arcsec - frac_arcsec

        if result_arcsec < 0:
            result_arcsec += FULL_CIRCLE_ARCSEC
        result_arcsec = result_arcsec % FULL_CIRCLE_ARCSEC

        return result_arcsec / 3600.0, retrograde

    # ── Public API ────────────────────────────────────────────────────────────

    def compute(self, birth_dt: datetime, lat: float, lon: float,
                tz_hours: float = 5.5) -> dict:
        """
        Returns dict: planet_name -> {'longitude': float, 'retrograde': bool}
        All 9 bodies: Sun Moon Mars Mercury Jupiter Venus Saturn Rahu Ketu
        Longitudes are Nirayana (Vakya sidereal), decimal degrees.
        """
        local_dt = birth_dt
        if getattr(local_dt, 'tzinfo', None) is not None:
            from datetime import timezone
            tz = timezone(timedelta(hours=tz_hours))
            local_dt = local_dt.astimezone(tz).replace(tzinfo=None)

        dt_utc = local_dt - timedelta(hours=tz_hours)
        ghatika, _ = self._ghatika_and_vakya_date(dt_utc, lat, lon, tz_hours)

        gy, tamil_month, day_in_month = self._date_to_tamil_month_day(local_dt.date())
        C, D, E, F = self._ky_year_arithmetic(gy)

        result: dict = {}

        sun_lon = self._calc_sun(gy, tamil_month, day_in_month, ghatika)
        result['Sun'] = {'longitude': sun_lon, 'retrograde': False}

        # Approximate astronomical Moon settles the ±1-day day-count ambiguity.
        # Ghatika enables intra-day interpolation (critical for PM/non-AM births).
        ref_moon = self._astronomical_moon_sidereal(dt_utc)
        moon_lon = self._calc_moon(C, D, E, tamil_month, day_in_month,
                                   ref_moon, ghatika)
        result['Moon'] = {'longitude': moon_lon, 'retrograde': False}

        for pname in ('Mars', 'Jupiter', 'Venus', 'Saturn', 'Mercury'):
            lon_deg, retro = self._calc_planet(pname, C, D, E, tamil_month, day_in_month, ghatika)
            result[pname] = {'longitude': lon_deg, 'retrograde': retro}

        rahu_lon = self._calc_rahu(C, D, E, tamil_month, day_in_month)
        result['Rahu'] = {'longitude': rahu_lon, 'retrograde': True}

        ketu_lon = (rahu_lon + 180.0) % 360.0
        result['Ketu'] = {'longitude': ketu_lon, 'retrograde': True}

        return result
