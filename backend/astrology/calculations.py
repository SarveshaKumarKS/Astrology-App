import math
from datetime import datetime, date, time, timedelta, timezone
from typing import Dict, List
import ephem

from astrology.constants import (
    PLANETS, SIGNS, NAKSHATRAS, HOUSES,
    PLANETS_TAMIL, SIGNS_TAMIL, NAKSHATRAS_TAMIL,
    DASA_ORDER, DASA_YEARS, PLANET_NAMES
)

class AstronomicalCalculations:
    """Base class for astronomical calculations used by both systems"""

    def __init__(self):
        # PyEphem planet objects for geocentric calculations
        self.planets = {
            'Sun': ephem.Sun(),
            'Moon': ephem.Moon(),
            'Mercury': ephem.Mercury(),
            'Venus': ephem.Venus(),
            'Mars': ephem.Mars(),
            'Jupiter': ephem.Jupiter(),
            'Saturn': ephem.Saturn(),
            'Rahu': None,  # Calculated separately (mean node)
            'Ketu': None   # Calculated separately (mean node + 180°)
        }

    # ---------- Time & JD helpers ----------

    def get_julian_day(self, birth_date: date, birth_time: time, timezone_offset: float) -> float:
        """Calculate (UTC) Julian Day Number from local date/time and tz offset (hours)."""
        # Local datetime
        dt_local = datetime.combine(birth_date, birth_time)
        # convert to UTC by subtracting the local offset
        dt_utc = dt_local - timedelta(hours=timezone_offset)
        # Astronomical JD: days since -4713-11-24 12:00 TT approx; good enough to treat UTC as proxy here
        a = (14 - dt_utc.month) // 12
        y = dt_utc.year + 4800 - a
        m = dt_utc.month + 12 * a - 3
        jdn = dt_utc.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
        time_fraction = (dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0) / 24.0
        # JD starts at noon; subtract 0.5 to pivot day boundary at 00:00
        return jdn + time_fraction - 0.5

    def _ephem_date_from_jd(self, jd: float) -> ephem.Date:
        """Convert JD (UTC) to ephem.Date."""
        # JD 2451545.0 == 2000-01-01 12:00:00 UTC
        days = jd - 2451545.0
        dt_utc = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc) + timedelta(days=days)
        return ephem.Date(dt_utc)

    # ---------- Sidereal helpers ----------

    def get_sidereal_time(self, jd: float, longitude: float) -> float:
        """Greenwich sidereal time + longitude (east positive), in degrees 0..360."""
        t = (jd - 2451545.0) / 36525.0
        gst = 280.46061837 + 360.98564736629 * (jd - 2451545.0) + 0.000387933 * t * t - t * t * t / 38710000.0
        gst = gst % 360.0
        lst = (gst + longitude) % 360.0
        return lst

    def calculate_lahiri_ayanamsa(self, jd: float) -> float:
        """
        Approximate Lahiri ayanamsa (degrees) around J2000 with correct units.
        For high-precision, swap to Swiss Ephemeris.
        """
        t = (jd - 2451545.0) / 36525.0  # Julian centuries since J2000
        base = 23.852_583_333  # 23°51'9.3" at J2000
        drift_deg_per_century = 5029.0966 / 3600.0  # arcsec/century -> deg/century
        ayanamsa = (base + drift_deg_per_century * t) % 360.0
        return ayanamsa

    # ---------- Longitudes, signs, nakshatras ----------

    def get_sign_from_longitude(self, longitude: float) -> int:
        """Zodiac sign index (1..12) from a sidereal ecliptic longitude (deg)."""
        return int(longitude // 30) + 1

    def get_nakshatra_from_longitude(self, longitude: float) -> int:
        """Nakshatra index (1..27) from sidereal ecliptic longitude (deg)."""
        span = 360.0 / 27.0  # 13°20'
        return int((longitude % 360.0) // span) + 1

    # ---------- Planetary positions ----------

    def calculate_planetary_positions(self, jd: float) -> Dict[str, Dict]:
        """
        Return per-planet dict with sidereal ecliptic longitude, latitude, sign, nakshatra.
        Uses geocentric ecliptic of date via ephem.Ecliptic(body).
        """
        observer = ephem.Observer()
        observer.date = self._ephem_date_from_jd(jd)
        # If you want true topocentric Moon, set observer.lat/lon; for now geocentric is sufficient.

        ayanamsa = self.calculate_lahiri_ayanamsa(jd)
        positions: Dict[str, Dict] = {}

        for planet_name, planet_obj in self.planets.items():
            if planet_obj is None:
                continue
            planet_obj.compute(observer)
            # Geocentric ecliptic of date
            ecl = ephem.Ecliptic(planet_obj)
            tropical_longitude = math.degrees(ecl.lon) % 360.0
            latitude = math.degrees(ecl.lat)
            # Convert to sidereal
            sidereal_longitude = (tropical_longitude - ayanamsa) % 360.0

            positions[planet_name] = {
                'longitude': sidereal_longitude,
                'latitude': latitude,
                'sign': self.get_sign_from_longitude(sidereal_longitude),
                'nakshatra': self.get_nakshatra_from_longitude(sidereal_longitude)
            }

        # Mean node (Rahu/Ketu) from mean ascending node (tropical)
        t = (jd - 2451545.0) / 36525.0
        omega = (125.04452 - 1934.136261 * t + 0.0020708 * t * t + (t ** 3) / 450000.0) % 360.0
        rahu_sidereal = (omega - ayanamsa) % 360.0
        ketu_sidereal = (rahu_sidereal + 180.0) % 360.0

        positions['Rahu'] = {
            'longitude': rahu_sidereal,
            'latitude': 0.0,
            'sign': self.get_sign_from_longitude(rahu_sidereal),
            'nakshatra': self.get_nakshatra_from_longitude(rahu_sidereal)
        }
        positions['Ketu'] = {
            'longitude': ketu_sidereal,
            'latitude': 0.0,
            'sign': self.get_sign_from_longitude(ketu_sidereal),
            'nakshatra': self.get_nakshatra_from_longitude(ketu_sidereal)
        }

        return positions

    # ---------- Ascendant / Houses ----------

    def calculate_ascendant(self, jd: float, latitude: float, longitude: float) -> float:
        """
        Ascendant (Lagna) sidereal ecliptic longitude using standard quick formula.
        """
        # Obliquity (can compute true obliquity for jd; J2000 fixed is acceptable here)
        eps = math.radians(23.439291111)
        theta = math.radians(self.get_sidereal_time(jd, longitude))  # LST in radians
        phi = math.radians(latitude)

        y = -math.cos(theta)
        x = math.sin(theta) * math.cos(eps) + math.tan(phi) * math.sin(eps)
        lam = math.degrees(math.atan2(y, x)) % 360.0

        # Convert to sidereal ecliptic by subtracting ayanamsa (LST was tropical)
        lam_sidereal = (lam - self.calculate_lahiri_ayanamsa(jd)) % 360.0
        return lam_sidereal

    def calculate_houses(self, ascendant: float, system: str = "equal") -> List[float]:
        """Equal-house cusps from ascendant; return 12 cusp longitudes."""
        houses = []
        for i in range(12):
            house_cusp = (ascendant + i * 30.0) % 360.0
            houses.append(house_cusp)
        return houses

    def get_planet_house(self, planet_longitude: float, house_cusps: List[float]) -> int:
        """Determine which house a planet is in given cusp longitudes (ascending order)."""
        for i in range(12):
            start = house_cusps[i]
            end = house_cusps[(i + 1) % 12]
            if start <= end:
                if start <= planet_longitude < end:
                    return i + 1
            else:
                # crosses 0°
                if planet_longitude >= start or planet_longitude < end:
                    return i + 1
        return 1

    # ---------- Divisional charts ----------

    def calculate_navamsa(self, rasi_positions: Dict[str, Dict]) -> Dict[str, Dict]:
        """Calculate Navamsa (D9) positions by sign mapping."""
        navamsa_positions: Dict[str, Dict] = {}
        for planet, position in rasi_positions.items():
            lon = position['longitude'] % 360.0
            sign = self.get_sign_from_longitude(lon)  # 1..12
            within = (lon % 30.0) / (30.0 / 9.0)      # 0..9
            nav_index = int(within)                   # 0..8

            # Fire signs start at same sign; Earth +3, Air +6, Water +9 (mod 12)
            if sign in [1, 5, 9]:       # Aries, Leo, Sagittarius
                base = 0
            elif sign in [2, 6, 10]:    # Taurus, Virgo, Capricorn
                base = 3
            elif sign in [3, 7, 11]:    # Gemini, Libra, Aquarius
                base = 6
            else:                       # Cancer, Scorpio, Pisces
                base = 9

            nav_sign = ((base + nav_index) % 12) + 1

            navamsa_positions[planet] = {
                'longitude': lon,  # keep rasi longitude for reference
                'sign': nav_sign,
                'nakshatra': position['nakshatra']
            }
        return navamsa_positions

    # ---------- Dasa Period Calculations ----------
    
    def _calculate_dasa_periods(self, birth_nakshatra: int, birth_date: date, moon_longitude_deg: float):
        """Vimshottari Mahadasha periods with first-dasha balance from Moon's position."""
        from astrology.models import DasaPeriod
        
        # Nakshatra lords (1..27)
        nakshatra_lords = {
            1: 'Ketu', 2: 'Venus', 3: 'Sun', 4: 'Moon', 5: 'Mars', 6: 'Rahu', 7: 'Jupiter', 8: 'Saturn', 9: 'Mercury',
            10: 'Ketu', 11: 'Venus', 12: 'Sun', 13: 'Moon', 14: 'Mars', 15: 'Rahu', 16: 'Jupiter', 17: 'Saturn', 18: 'Mercury',
            19: 'Ketu', 20: 'Venus', 21: 'Sun', 22: 'Moon', 23: 'Mars', 24: 'Rahu', 25: 'Jupiter', 26: 'Saturn', 27: 'Mercury'
        }
        span = 360.0 / 27.0  # 13°20'
        nk_start = ((birth_nakshatra - 1) * span) % 360.0
        f_elapsed = ((moon_longitude_deg - nk_start) % 360.0) / span  # 0..1
        starting_lord = nakshatra_lords[birth_nakshatra]

        # First (truncated) mahadasha
        remaining_years = DASA_YEARS[starting_lord] * (1.0 - f_elapsed)

        dasa_periods = []
        cur_start = birth_date
        first_end = cur_start + timedelta(days=remaining_years * 365.2425)
        dasa_periods.append(DasaPeriod(
            planet=starting_lord,
            planet_tamil=PLANET_NAMES[starting_lord],
            start_date=cur_start,
            end_date=first_end,
            level="maha",
            years=remaining_years,
            months=int(round(remaining_years * 12)),
            days=int(round(remaining_years * 365.2425))
        ))
        cur_start = first_end

        # Continue cycles (~120 years total)
        idx0 = DASA_ORDER.index(starting_lord)
        for k in range(1, 18):  # 2 cycles minus the first partial already added
            planet = DASA_ORDER[(idx0 + k) % 9]
            yrs = DASA_YEARS[planet]
            end = cur_start + timedelta(days=yrs * 365.2425)
            dasa_periods.append(DasaPeriod(
                planet=planet,
                planet_tamil=PLANET_NAMES[planet],
                start_date=cur_start,
                end_date=end,
                level="maha",
                years=yrs,
                months=int(yrs * 12),
                days=int(yrs * 365.2425)
            ))
            cur_start = end

        return dasa_periods

    def _get_current_dasa(self, dasa_periods):
        """Get current running mahadasha (by today's date)."""
        from astrology.models import DasaPeriod
        today = date.today()
        for d in dasa_periods:
            if d.start_date <= today <= d.end_date:
                return d
        return dasa_periods[0] if dasa_periods else None

        return navamsa_positions
