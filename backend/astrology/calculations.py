import math
from datetime import datetime, date, time, timedelta, timezone
from typing import Dict, List
import ephem
from dateutil.relativedelta import relativedelta

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

    def deg_to_dms(self, deg: float) -> str:
        """Convert degrees to DMS format (degrees:minutes:seconds) with proper carry-over."""
        d = int(deg)
        m_float = (deg - d) * 60
        m = int(m_float)
        s = round((m_float - m) * 60)
        # Handle carry-over
        if s == 60:
            s = 0
            m += 1
        if m == 60:
            m = 0
            d += 1
        return f"{d}:{m:02d}:{s:02d}"

    def get_nakshatra_pada(self, lon: float) -> int:
        """Get nakshatra pada (1-4) from longitude."""
        span = 360.0 / 27.0  # 13°20'
        part = ((lon % span) / (span / 4))
        return int(part) + 1

    def get_nakshatra_lord(self, nakshatra: int) -> str:
        """Get nakshatra lord from nakshatra number (1-27)."""
        nakshatra_lords = {
            1: 'Ketu', 2: 'Venus', 3: 'Sun', 4: 'Moon', 5: 'Mars', 6: 'Rahu', 7: 'Jupiter', 8: 'Saturn', 9: 'Mercury',
            10: 'Ketu', 11: 'Venus', 12: 'Sun', 13: 'Moon', 14: 'Mars', 15: 'Rahu', 16: 'Jupiter', 17: 'Saturn', 18: 'Mercury',
            19: 'Ketu', 20: 'Venus', 21: 'Sun', 22: 'Moon', 23: 'Mars', 24: 'Rahu', 25: 'Jupiter', 26: 'Saturn', 27: 'Mercury'
        }
        return nakshatra_lords.get(nakshatra, 'Sun')

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
        Ascendant (Lagna) sidereal ecliptic longitude.
        Uses the correct formula: x = sin(theta)*cos(eps) + tan(lat)*sin(eps), y = -cos(theta)
        followed by 180° adjustment to get the eastward rising point.
        """
        eps = math.radians(23.439291111)  # J2000 mean obliquity
        lst = self.get_sidereal_time(jd, longitude)
        theta = math.radians(lst)
        phi = math.radians(latitude)
        
        # CORRECT formula for ascendant (eastward rising point)
        x = math.sin(theta) * math.cos(eps) + math.tan(phi) * math.sin(eps)
        y = -math.cos(theta)  # Negative cosine for ascendant
        lam_trop = (math.degrees(math.atan2(y, x)) + 180.0) % 360.0
        
        # Convert to sidereal
        lam_sidereal = (lam_trop - self.calculate_lahiri_ayanamsa(jd)) % 360.0
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

    def _calculate_navamsa_sign(self, longitude: float) -> int:
        """Helper to calculate navamsa sign from any longitude.
        Uses element-based grouping:
        - Fire signs (Aries, Leo, Sagittarius) → base = 1 (Aries)
        - Earth signs (Taurus, Virgo, Capricorn) → base = 10 (Capricorn)
        - Air signs (Gemini, Libra, Aquarius) → base = 7 (Libra)
        - Water signs (Cancer, Scorpio, Pisces) → base = 4 (Cancer)
        """
        sign = self.get_sign_from_longitude(longitude)
        lon_in_sign = longitude % 30.0
        
        # D9 formula: divide sign into 9 parts of 3°20' each
        navamsa_part = int(lon_in_sign / 3.333333333333333)
        
        # Base calculation based on sign element
        if sign in [1, 5, 9]:  # Fire signs (Aries, Leo, Sagittarius)
            base = 1
        elif sign in [2, 6, 10]:  # Earth signs (Taurus, Virgo, Capricorn)
            base = 10
        elif sign in [3, 7, 11]:  # Air signs (Gemini, Libra, Aquarius)
            base = 7
        else:  # Water signs [4, 8, 12] (Cancer, Scorpio, Pisces)
            base = 4
        
        nav_sign = ((base - 1 + navamsa_part) % 12) + 1
        return nav_sign

    def calculate_navamsa(self, planetary_positions: Dict[str, Dict], ascendant_longitude: float = None) -> Dict[str, Dict]:
        """Calculate Navamsa (D9) chart positions.
        If ascendant_longitude is provided, it will also calculate navamsa ascendant.
        """
        navamsa_positions = {}
        
        # Calculate navamsa for all planets
        for planet, position in planetary_positions.items():
            lon = position['longitude']
            nav_sign = self._calculate_navamsa_sign(lon)
            
            navamsa_positions[planet] = {
                'longitude': lon,
                'sign': nav_sign,
                'nakshatra': position.get('nakshatra')
            }
        
        # Calculate navamsa ascendant if provided
        if ascendant_longitude is not None:
            nav_asc_sign = self._calculate_navamsa_sign(ascendant_longitude)
            navamsa_positions['Ascendant'] = {
                'longitude': ascendant_longitude,
                'sign': nav_asc_sign,
                'nakshatra': self.get_nakshatra_from_longitude(ascendant_longitude)
            }
        
        return navamsa_positions


    # ---------- Thirukkanitham (Drik) specific methods ----------
    
    def _true_obliquity(self, jd: float) -> float:
        """True obliquity of the ecliptic (degrees). Meeus approximation."""
        t = (jd - 2451545.0) / 36525.0
        # mean obliquity (arcseconds)
        eps0 = 84381.406 - 46.836769*t - 0.0001831*t*t + 0.00200340*t*t*t - 5.76e-7*t**4 - 4.34e-8*t**5
        # nutation in obliquity is small; PyEphem already includes nutation in body positions,
        # for ascendant formula we can use mean or add small correction. Keep mean here:
        return eps0 / 3600.0

    def _true_node_sidereal(self, jd: float, ayanamsa: float) -> float:
        """True lunar ascending node (sidereal) in degrees."""
        # PyEphem provides mean node only, so use standard series (approx):
        # Start from mean node omega (tropical):
        t = (jd - 2451545.0) / 36525.0
        omega = (125.04452 - 1934.136261*t + 0.0020708*t*t + (t**3)/450000.0) % 360.0
        # Apply a small periodic correction to get 'true' node (deg). A common quick term:
        # ΔΩ ≈ -0.00478° * sin(Ω)  (approx; there are more terms if you want higher accuracy)
        corr = -0.00478 * math.sin(math.radians(omega))
        true_tropical = (omega + corr) % 360.0
        return (true_tropical - ayanamsa) % 360.0

    def calculate_planetary_positions_topocentric(self, jd: float, latitude: float, longitude: float) -> Dict[str, Dict]:
        """Like calculate_planetary_positions, but with observer lat/lon (topocentric Moon/planets)."""
        obs = ephem.Observer()
        obs.date = self._ephem_date_from_jd(jd)
        obs.lat = str(latitude)
        obs.lon = str(longitude)

        ayanamsa = self.calculate_lahiri_ayanamsa(jd)
        positions = {}
        for name, body in self.planets.items():
            if body is None:
                continue
            body.compute(obs)
            ecl = ephem.Ecliptic(body)
            lon_trop = math.degrees(ecl.lon) % 360.0
            lat = math.degrees(ecl.lat)
            lon_sid = (lon_trop - ayanamsa) % 360.0
            positions[name] = {
                'longitude': lon_sid,
                'latitude': lat,
                'sign': self.get_sign_from_longitude(lon_sid),
                'nakshatra': self.get_nakshatra_from_longitude(lon_sid)
            }

        # Nodes: in Thirukkanitham we'll override with TRUE node
        true_rahu = self._true_node_sidereal(jd, ayanamsa)
        true_ketu = (true_rahu + 180.0) % 360.0
        positions['Rahu'] = {
            'longitude': true_rahu, 'latitude': 0.0,
            'sign': self.get_sign_from_longitude(true_rahu),
            'nakshatra': self.get_nakshatra_from_longitude(true_rahu)
        }
        positions['Ketu'] = {
            'longitude': true_ketu, 'latitude': 0.0,
            'sign': self.get_sign_from_longitude(true_ketu),
            'nakshatra': self.get_nakshatra_from_longitude(true_ketu)
        }
        return positions

    def calculate_ascendant_true_obliquity(self, jd: float, latitude: float, longitude: float) -> float:
        """Calculate ascendant with true obliquity (for Thirukkanitham/Drik system).
        Uses the correct formula: x = sin(theta)*cos(eps) + tan(lat)*sin(eps), y = -cos(theta)
        followed by 180° adjustment to get the eastward rising point.
        """
        eps = math.radians(self._true_obliquity(jd))
        lst = self.get_sidereal_time(jd, longitude)
        theta = math.radians(lst)
        phi = math.radians(latitude)
        
        # CORRECT formula for ascendant (eastward rising point)
        x = math.sin(theta) * math.cos(eps) + math.tan(phi) * math.sin(eps)
        y = -math.cos(theta)  # Negative cosine for ascendant
        lam_trop = (math.degrees(math.atan2(y, x)) + 180.0) % 360.0
        lam_sid = (lam_trop - self.calculate_lahiri_ayanamsa(jd)) % 360.0
        return lam_sid

    # ---------- Dasa Period Calculations ----------
    
    def _calculate_dasa_periods(self, birth_nakshatra: int, birth_date: date, moon_longitude_deg: float):
        """Vimshottari Mahadasha periods with first-dasha balance from Moon's position.
        Uses date arithmetic with relativedelta for accurate date calculations.
        """
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
        total_years = DASA_YEARS[starting_lord]
        remaining_years = total_years * (1.0 - f_elapsed)
        
        # Convert remaining_years to years, months, days
        years_int = int(remaining_years)
        months_float = (remaining_years - years_int) * 12
        months_int = int(months_float)
        days_float = (months_float - months_int) * 30.44  # Average days per month
        days_int = int(round(days_float))
        
        # Subtract approximately 9 months (gestation period) from first mahadasha
        gestation_months = 9
        if months_int >= gestation_months:
            months_int -= gestation_months
        else:
            # Need to borrow from years
            months_to_borrow = gestation_months - months_int
            years_int -= 1
            months_int = 12 - months_to_borrow
        
        dasa_periods = []
        cur_start = birth_date
        
        # Calculate first period end date using relativedelta
        first_end = cur_start + relativedelta(years=years_int, months=months_int, days=days_int)
        first_end_date = first_end - timedelta(days=1)  # End date is one day before next starts
        
        # Calculate actual duration in years, months, days from actual end_date
        delta = relativedelta(first_end_date, cur_start)
        actual_years = delta.years
        actual_months = delta.months
        actual_days = delta.days
        
        dasa_periods.append(DasaPeriod(
            planet=starting_lord,
            planet_tamil=PLANET_NAMES[starting_lord],
            start_date=cur_start,
            end_date=first_end_date,
            level="maha",
            years=actual_years + actual_months/12.0 + actual_days/365.2425,
            months=actual_years * 12 + actual_months,
            days=actual_days
        ))
        cur_start = first_end

        # Continue cycles (~120 years total)
        idx0 = DASA_ORDER.index(starting_lord)
        for k in range(1, 18):  # 2 cycles minus the first partial already added
            planet = DASA_ORDER[(idx0 + k) % 9]
            yrs = DASA_YEARS[planet]
            
            # Convert years to years, months, days
            yrs_int = int(yrs)
            mths_float = (yrs - yrs_int) * 12
            mths_int = int(mths_float)
            dys_float = (mths_float - mths_int) * 30.44
            dys_int = int(round(dys_float))
            
            # Calculate end date using relativedelta
            end = cur_start + relativedelta(years=yrs_int, months=mths_int, days=dys_int)
            end_date = end - timedelta(days=1)  # End date is one day before next starts
            
            # Calculate actual duration from actual end_date
            delta = relativedelta(end_date, cur_start)
            actual_years = delta.years
            actual_months = delta.months
            actual_days = delta.days
            
            dasa_periods.append(DasaPeriod(
                planet=planet,
                planet_tamil=PLANET_NAMES[planet],
                start_date=cur_start,
                end_date=end_date,
                level="maha",
                years=actual_years + actual_months/12.0 + actual_days/365.2425,
                months=actual_years * 12 + actual_months,
                days=actual_days
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
    
    def _calculate_sub_dasha_periods(self, maha_dasa):
        """Calculate bhukti (antar dasha) periods within a mahadasha.
        Divides the mahadasha into 9 sub-periods proportionally.
        """
        from astrology.models import DasaPeriod
        
        # Get the mahadasha planet and its position in DASA_ORDER
        maha_planet = maha_dasa.planet
        maha_idx = DASA_ORDER.index(maha_planet)
        
        # Total duration of mahadasha in days
        maha_duration_days = (maha_dasa.end_date - maha_dasa.start_date).days + 1
        
        # Total proportional years for all 9 bhuktis
        total_proportional = sum(DASA_YEARS[DASA_ORDER[(maha_idx + i) % 9]] for i in range(9))
        
        bhukti_periods = []
        cur_start = maha_dasa.start_date
        
        for i in range(9):
            bhukti_planet = DASA_ORDER[(maha_idx + i) % 9]
            bhukti_years = DASA_YEARS[bhukti_planet]
            
            # Calculate proportional duration
            bhukti_fraction = bhukti_years / total_proportional
            bhukti_duration_days = int(maha_duration_days * bhukti_fraction)
            
            # Calculate end date
            end_date = cur_start + timedelta(days=bhukti_duration_days - 1)
            
            # Make sure last bhukti ends exactly at mahadasha end
            if i == 8:
                end_date = maha_dasa.end_date
            
            # Calculate years, months, days
            delta = relativedelta(end_date, cur_start)
            
            bhukti_periods.append(DasaPeriod(
                planet=bhukti_planet,
                planet_tamil=PLANET_NAMES[bhukti_planet],
                start_date=cur_start,
                end_date=end_date,
                level="antar",
                years=delta.years + delta.months/12.0 + delta.days/365.2425,
                months=delta.years * 12 + delta.months,
                days=delta.days
            ))
            
            cur_start = end_date + timedelta(days=1)
        
        return bhukti_periods
    
    def _enhance_current_dasa(self, current_dasa, dasa_periods):
        """Enhance current dasa with balance, next dasa, and bhukti information."""
        from astrology.models import DasaPeriod
        today = date.today()
        
        # Calculate remaining balance
        if current_dasa and current_dasa.end_date >= today:
            delta = relativedelta(current_dasa.end_date, today)
            current_dasa.balance_years = delta.years
            current_dasa.balance_months = delta.months
            current_dasa.balance_days = delta.days
        
        # Find next mahadasha
        current_idx = None
        for idx, d in enumerate(dasa_periods):
            if d.planet == current_dasa.planet and d.start_date == current_dasa.start_date:
                current_idx = idx
                break
        
        if current_idx is not None and current_idx < len(dasa_periods) - 1:
            next_dasa = dasa_periods[current_idx + 1]
            current_dasa.next_dasa_planet = next_dasa.planet
            current_dasa.next_dasa_planet_tamil = next_dasa.planet_tamil
            # Store as string to avoid serialization issues
            current_dasa.next_dasa_end_date = str(next_dasa.end_date) if next_dasa.end_date else None
        
        # Calculate bhuktis and find current/next
        bhuktis = self._calculate_sub_dasha_periods(current_dasa)
        
        current_bhukti = None
        for idx, bhukti in enumerate(bhuktis):
            if bhukti.start_date <= today <= bhukti.end_date:
                current_bhukti = bhukti
                current_dasa.current_bhukti_planet = bhukti.planet
                current_dasa.current_bhukti_planet_tamil = bhukti.planet_tamil
                # Store as string to avoid serialization issues
                current_dasa.current_bhukti_end_date = str(bhukti.end_date) if bhukti.end_date else None
                
                # Set next bhukti
                if idx < len(bhuktis) - 1:
                    next_bhukti = bhuktis[idx + 1]
                    current_dasa.next_bhukti_planet = next_bhukti.planet
                    current_dasa.next_bhukti_planet_tamil = next_bhukti.planet_tamil
                    # Store as string to avoid serialization issues
                    current_dasa.next_bhukti_end_date = str(next_bhukti.end_date) if next_bhukti.end_date else None
                break
        
        return current_dasa
