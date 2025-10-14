import math
import swisseph as swe
from datetime import datetime, date, time, timedelta
from typing import Dict, Tuple, List
from astrology.constants import (
    PLANETS, SIGNS, NAKSHATRAS, HOUSES,
    PLANETS_TAMIL, SIGNS_TAMIL, NAKSHATRAS_TAMIL,
    DASA_ORDER, DASA_YEARS, PLANET_NAMES
)

# Swiss Ephemeris planet constants
SWE_PLANETS = {
    'Sun': swe.SUN,
    'Moon': swe.MOON,
    'Mars': swe.MARS,
    'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER,
    'Venus': swe.VENUS,
    'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE,
    'Ketu': swe.MEAN_NODE  # Ketu = Rahu + 180°
}

class AstronomicalCalculations:
    """Base class for astronomical calculations using Swiss Ephemeris"""

    def __init__(self):
        # Set Swiss Ephemeris to use Lahiri ayanamsa (sidereal mode)
        swe.set_sid_mode(swe.SIDM_LAHIRI)

    # ---------- Time & JD helpers ----------

    def _parse_timezone(self, tz_str: str) -> float:
        """Parse timezone string to offset hours."""
        if isinstance(tz_str, (int, float)):
            return float(tz_str)
        tz_str = tz_str.strip().upper()
        if tz_str == 'IST':
            return 5.5
        if tz_str.startswith(('+', '-')):
            parts = tz_str[1:].split(':')
            hours = int(parts[0])
            minutes = int(parts[1]) if len(parts) > 1 else 0
            offset = hours + minutes / 60.0
            return offset if tz_str[0] == '+' else -offset
        return 0.0

    def get_julian_day(self, birth_date: date, birth_time: time, timezone_offset: float) -> float:
        """Calculate Julian Day (UT) using Swiss Ephemeris."""
        # Convert local time to UTC
        local_datetime = datetime.combine(birth_date, birth_time)
        utc_datetime = local_datetime - timedelta(hours=timezone_offset)
        
        # Swiss Ephemeris julday function
        jd = swe.julday(
            utc_datetime.year,
            utc_datetime.month,
            utc_datetime.day,
            utc_datetime.hour + utc_datetime.minute / 60.0 + utc_datetime.second / 3600.0
        )
        return jd
    
    def get_julian_day_lmt(self, birth_date: date, birth_time: time, timezone_offset: float, longitude: float) -> float:
        """Calculate Julian Day with Local Mean Time (LMT) correction for Traditional Vakkiam.
        LMT correction: (longitude - 82.5) * 4 minutes
        82.5° E is the Indian Standard Time meridian.
        """
        # LMT correction in minutes
        lmt_correction_minutes = (longitude - 82.5) * 4.0
        
        # Apply LMT correction to birth time
        local_datetime = datetime.combine(birth_date, birth_time)
        lmt_datetime = local_datetime - timedelta(minutes=lmt_correction_minutes)
        
        # Convert to UTC
        utc_datetime = lmt_datetime - timedelta(hours=timezone_offset)
        
        # Calculate JD
        jd = swe.julday(
            utc_datetime.year,
            utc_datetime.month,
            utc_datetime.day,
            utc_datetime.hour + utc_datetime.minute / 60.0 + utc_datetime.second / 3600.0
        )
        return jd

    def get_sidereal_time(self, jd: float, longitude: float) -> float:
        """Calculate local sidereal time in degrees using Swiss Ephemeris."""
        # Get sidereal time at Greenwich
        sidt = swe.sidtime(jd)  # in hours
        # Add longitude correction (15 degrees per hour)
        local_sidt = sidt + longitude / 15.0
        # Convert to degrees
        return (local_sidt * 15.0) % 360.0

    def calculate_lahiri_ayanamsa(self, jd: float) -> float:
        """Calculate Lahiri ayanamsa using Swiss Ephemeris."""
        return swe.get_ayanamsa_ut(jd)
    
    def calculate_traditional_ayanamsa(self, jd: float) -> float:
        """Calculate Traditional Vakkiam ayanamsa.
        Formula: Base 23.5° + drift of 50 arcseconds per century from epoch.
        """
        # Epoch: J2000.0 = JD 2451545.0
        epoch_jd = 2451545.0
        centuries_from_epoch = (jd - epoch_jd) / 36525.0
        
        # Base ayanamsa at epoch
        base_ayanamsa = 23.5  # degrees
        
        # Drift: 50 arcseconds per century = 50/3600 degrees per century
        drift_per_century = 50.0 / 3600.0
        
        # Calculate ayanamsa
        ayanamsa = base_ayanamsa + (drift_per_century * centuries_from_epoch)
        
        return ayanamsa

    # ---------- Core calculations ----------

    def calculate_planetary_positions(self, jd: float, use_traditional_ayanamsa: bool = False) -> Dict[str, Dict]:
        """Calculate geocentric sidereal planetary positions using Swiss Ephemeris.
        If use_traditional_ayanamsa=True, manually applies Traditional Vakkiam ayanamsa to tropical positions.
        Otherwise uses Swiss Ephemeris built-in sidereal mode (Lahiri).
        """
        positions = {}
        
        if use_traditional_ayanamsa:
            # Calculate tropical positions and manually apply traditional ayanamsa
            iflag = swe.FLG_SWIEPH  # Tropical
            ayanamsa = self.calculate_traditional_ayanamsa(jd)
        else:
            # Use Swiss Ephemeris sidereal mode (Lahiri)
            iflag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
            ayanamsa = 0.0  # Not needed, already sidereal

        for planet_name, planet_id in SWE_PLANETS.items():
            if planet_name == 'Ketu':
                continue  # Handle after Rahu
            
            # Calculate position
            result = swe.calc_ut(jd, planet_id, iflag)
            pos_data = result[0]
            longitude_calc = pos_data[0]
            latitude = pos_data[1]
            
            # Apply traditional ayanamsa if needed
            if use_traditional_ayanamsa:
                longitude = (longitude_calc - ayanamsa) % 360.0
            else:
                longitude = longitude_calc
            
            # Handle Rahu
            if planet_name == 'Rahu':
                positions['Rahu'] = {
                    'longitude': longitude,
                    'latitude': 0.0,
                    'sign': self.get_sign_from_longitude(longitude),
                    'nakshatra': self.get_nakshatra_from_longitude(longitude)
                }
                # Ketu is 180° opposite
                ketu_lon = (longitude + 180.0) % 360.0
                positions['Ketu'] = {
                    'longitude': ketu_lon,
                    'latitude': 0.0,
                    'sign': self.get_sign_from_longitude(ketu_lon),
                    'nakshatra': self.get_nakshatra_from_longitude(ketu_lon)
                }
            else:
                positions[planet_name] = {
                    'longitude': longitude,
                    'latitude': latitude,
                    'sign': self.get_sign_from_longitude(longitude),
                    'nakshatra': self.get_nakshatra_from_longitude(longitude)
                }

        return positions

    def calculate_ascendant(self, jd: float, latitude: float, longitude: float) -> float:
        """Calculate ascendant (eastern horizon point) with correct formula.
        Uses: x = sin(LST)*cos(ε) + tan(lat)*sin(ε), y = -cos(LST)
        Then: ascendant = (atan2(y,x) + 180°) % 360° - ayanamsa
        """
        eps = math.radians(23.439291111)  # J2000 mean obliquity
        lst = self.get_sidereal_time(jd, longitude)
        theta = math.radians(lst)
        phi = math.radians(latitude)
        
        # Correct formula for ASCENDANT (eastern point, not descendant)
        x = math.sin(theta) * math.cos(eps) + math.tan(phi) * math.sin(eps)
        y = -math.cos(theta)
        
        # Add 180° to get the eastern (rising) point
        lam_tropical = (math.degrees(math.atan2(y, x)) + 180.0) % 360.0
        
        # Convert to sidereal
        ayanamsa = self.calculate_lahiri_ayanamsa(jd)
        asc_sidereal = (lam_tropical - ayanamsa) % 360.0
        
        return asc_sidereal

    def calculate_houses(self, ascendant_longitude: float, system: str = "equal") -> List[float]:
        """Calculate house cusps from ascendant (equal house system)."""
        cusps = []
        for i in range(12):
            cusp = (ascendant_longitude + i * 30.0) % 360.0
            cusps.append(cusp)
        return cusps

    def get_planet_house(self, planet_longitude: float, house_cusps: List[float]) -> int:
        """Determine which house a planet is in."""
        for i in range(12):
            start = house_cusps[i]
            end = house_cusps[(i + 1) % 12]
            
            if start < end:
                if start <= planet_longitude < end:
                    return i + 1
            else:  # Wraps around 0°
                if planet_longitude >= start or planet_longitude < end:
                    return i + 1
        return 1

    # ---------- Thirukkanitham (Drik) specific methods ----------

    def _true_obliquity(self, jd: float) -> float:
        """True obliquity using Swiss Ephemeris."""
        # Swiss Ephemeris can calculate this, but for compatibility:
        t = (jd - 2451545.0) / 36525.0
        eps0 = 84381.406 - 46.836769*t - 0.0001831*t*t + 0.00200340*t*t*t - 5.76e-7*t**4 - 4.34e-8*t**5
        return eps0 / 3600.0

    def _true_node_sidereal(self, jd: float, ayanamsa: float) -> float:
        """Calculate true lunar node (sidereal) using Swiss Ephemeris."""
        iflag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
        result = swe.calc_ut(jd, swe.TRUE_NODE, iflag)
        return result[0]  # Already sidereal

    def calculate_planetary_positions_topocentric(self, jd: float, latitude: float, longitude: float) -> Dict[str, Dict]:
        """Calculate topocentric sidereal planetary positions using Swiss Ephemeris."""
        positions = {}
        iflag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_TOPOCTR
        
        # Set topocentric location
        swe.set_topo(longitude, latitude, 0)  # 0 = altitude in meters

        for planet_name, planet_id in SWE_PLANETS.items():
            if planet_name == 'Ketu':
                continue
            
            # For TRUE node in Thirukkanitham
            if planet_name == 'Rahu':
                result = swe.calc_ut(jd, swe.TRUE_NODE, iflag)
            else:
                result = swe.calc_ut(jd, planet_id, iflag)
            
            pos_data = result[0]  # First element is the position tuple
            longitude_val = pos_data[0]
            latitude_val = pos_data[1]
            
            if planet_name == 'Rahu':
                positions['Rahu'] = {
                    'longitude': longitude_val,
                    'latitude': 0.0,
                    'sign': self.get_sign_from_longitude(longitude_val),
                    'nakshatra': self.get_nakshatra_from_longitude(longitude_val)
                }
                ketu_lon = (longitude_val + 180.0) % 360.0
                positions['Ketu'] = {
                    'longitude': ketu_lon,
                    'latitude': 0.0,
                    'sign': self.get_sign_from_longitude(ketu_lon),
                    'nakshatra': self.get_nakshatra_from_longitude(ketu_lon)
                }
            else:
                positions[planet_name] = {
                    'longitude': longitude_val,
                    'latitude': latitude_val,
                    'sign': self.get_sign_from_longitude(longitude_val),
                    'nakshatra': self.get_nakshatra_from_longitude(longitude_val)
                }

        return positions

    def calculate_ascendant_true_obliquity(self, jd: float, latitude: float, longitude: float) -> float:
        """Calculate ascendant with true obliquity (for Thirukkanitham/Drik system).
        Uses true obliquity instead of fixed J2000 value.
        """
        eps = math.radians(self._true_obliquity(jd))  # TRUE obliquity
        lst = self.get_sidereal_time(jd, longitude)
        theta = math.radians(lst)
        phi = math.radians(latitude)
        
        # Correct formula for ASCENDANT (eastern point)
        x = math.sin(theta) * math.cos(eps) + math.tan(phi) * math.sin(eps)
        y = -math.cos(theta)
        
        # Add 180° to get the eastern (rising) point
        lam_tropical = (math.degrees(math.atan2(y, x)) + 180.0) % 360.0
        
        # Convert to sidereal
        ayanamsa = self.calculate_lahiri_ayanamsa(jd)
        asc_sidereal = (lam_tropical - ayanamsa) % 360.0
        
        return asc_sidereal

    # ---------- Sign & Nakshatra helpers ----------

    def get_sign_from_longitude(self, longitude: float) -> int:
        """Get zodiac sign (1-12) from ecliptic longitude."""
        return int(longitude / 30.0) + 1

    def get_nakshatra_from_longitude(self, longitude: float) -> int:
        """Get nakshatra (1-27) from ecliptic longitude."""
        return int(longitude / 13.333333333333334) + 1

    # ---------- Navamsa (D9) ----------

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
                'nakshatra': position['nakshatra']
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
    
    def _calculate_navamsa_sign(self, longitude: float) -> int:
        """Helper to calculate navamsa sign from any longitude."""
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
        today = date.today()
        for d in dasa_periods:
            if d.start_date <= today <= d.end_date:
                return d
        return dasa_periods[0] if dasa_periods else None
