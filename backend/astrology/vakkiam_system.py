from datetime import date, timedelta, time, datetime, timezone
from dateutil.relativedelta import relativedelta
from typing import Dict, List, Optional
import math
import json
import os
import swisseph as swe
from astrology.calculations import AstronomicalCalculations
from astrology.vakya_table_engine import VakyaTableEngine
from astrology.models import (
    BirthDetails, HoroscopeResult, CompatibilityResult, PlanetaryPosition,
    DasaPeriod, Chart, CompatibilityFactor
)
from astrology.constants import (
    PLANETS, SIGNS, NAKSHATRAS, PLANET_NAMES, SIGNS_TAMIL, NAKSHATRAS_TAMIL,
    DASA_ORDER, DASA_YEARS, COMPATIBILITY_FACTORS
)

# Vakya Cycle Constants (days)
# These represent the cycle lengths for each planet's correction table
VAKYA_CYCLES = {
    'Sun': 365.258756,
    'Moon': 248.0,
    'Mars': 779.94,
    'Mercury': 115.88,
    'Jupiter': 398.88,
    'Venus': 583.92,
    'Saturn': 378.09,
    'Rahu': 6793.5,
    'Ketu': 6793.5
}


class VakyaEngine:
    """
    Vakya Engine for Parametric Epicyclic Model calculations based on Aryabhatiya.
    Loads calibrated physics constants from final_vakya_tables.json and performs
    trigonometric calculations for planetary positions.
    """
    
    def __init__(self, tables_file: Optional[str] = None):
        """
        Initialize VakyaEngine by loading calibrated constants.
        
        Args:
            tables_file: Path to final_vakya_tables.json. If None, looks in same directory.
        
        Raises:
            FileNotFoundError: If tables file is not found
            ValueError: If JSON is invalid or required keys/planets are missing
        """
        # Base Reference: Calibration uses "Days since 2000-01-01 00:00:00 UTC"
        self.BASE_EPOCH_DATETIME = datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        self.BASE_EPOCH_JD = 2451545.0  # Keep for compatibility with other calculations
        self.BASE_YEAR = 2000.0
        
        # Load tables file
        if tables_file is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            tables_file = os.path.join(script_dir, 'final_vakya_tables.json')
        
        try:
            if not os.path.exists(tables_file):
                print(f"⚠️  Warning: Vakya tables file not found: {tables_file}")
                self.tables = {}
                return
            
            with open(tables_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Store the raw data - handle varying JSON key names gracefully
            self.tables = data
            
            # Validate that we have all required planets
            required_planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
            missing_planets = [p for p in required_planets if p not in data]
            
            if missing_planets:
                print(f"⚠️  Warning: Missing planet data in tables file: {', '.join(missing_planets)}")
            
        except FileNotFoundError:
            print(f"⚠️  Warning: Vakya tables file not found: {tables_file}")
            self.tables = {}
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in tables file: {e}")
        except Exception as e:
            raise ValueError(f"Error loading tables file: {e}")
    
    def _normalize(self, angle: float) -> float:
        """Normalize angle to 0-360 range"""
        return angle % 360.0
    
    def _jd_to_datetime_utc(self, jd: float) -> datetime:
        """
        Convert Julian Day to UTC datetime.
        JD 2451545.0 = January 1, 2000, 12:00:00 TT (approximately UTC)
        """
        days_since_j2000 = jd - 2451545.0
        dt_utc = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc) + timedelta(days=days_since_j2000)
        return dt_utc
    
    def _to_utc_days(self, birth_dt: datetime) -> float:
        """
        CRITICAL: Convert birth datetime to days since 2000-01-01 00:00:00 UTC.
        This must match the calibration script exactly.
        
        If birth_dt has no timezone, assume it is IST (UTC+5:30) and convert to UTC.
        
        Args:
            birth_dt: Input datetime (timezone-naive or timezone-aware)
            
        Returns:
            Days since 2000-01-01 00:00:00 UTC as a float
        """
        # Handle timezone-naive datetime (assume IST)
        if birth_dt.tzinfo is None:
            # Assume IST (UTC+5:30) and convert to UTC
            birth_dt = birth_dt.replace(tzinfo=timezone(timedelta(hours=5, minutes=30)))
            birth_dt = birth_dt.astimezone(timezone.utc)
        else:
            # Convert to UTC if in different timezone
            birth_dt = birth_dt.astimezone(timezone.utc)
        
        # Calculate delta from base epoch
        delta = birth_dt - self.BASE_EPOCH_DATETIME
        return delta.total_seconds() / 86400.0
    
    def _get_days_since_2000(self, dt_input: datetime) -> float:
        """Alias for _to_utc_days for backward compatibility"""
        return self._to_utc_days(dt_input)
    
    def _get_planet_data(self, planet: str, key: str, default=None):
        """Get planet data with flexible key name handling"""
        if planet not in self.tables:
            return default
        
        planet_data = self.tables[planet]
        
        # Handle varying key names
        key_variants = {
            'L0': ['L0', 'epoch_l0', 'l0'],
            'Rate': ['Rate', 'mean_motion', 'rate'],
            'Apogee': ['Apogee', 'apogee_l0', 'apogee'],
            'Amp': ['Amp', 'amplitude', 'manda_coeff'],
            'A0': ['A0', 'apogee_l0', 'apogee'],
            'Rate_Apogee': ['Rate_Apogee', 'apogee_rate', 'rate_apogee'],
            'sun_l0_ref': ['sun_l0_ref', 'sun_L0', 'sun_l0'],
            'sun_rate_ref': ['sun_rate_ref', 'sun_Rate', 'sun_rate'],
            'manda_coeff': ['manda_coeff', 'MandaCoeff', 'manda'],
            'sighra_circ': ['sighra_circ', 'SighraCirc', 'sighra']
        }
        
        if key in key_variants:
            for variant in key_variants[key]:
                if variant in planet_data:
                    return planet_data[variant]
        
        # Direct key lookup
        return planet_data.get(key, default)
    
    def _calc_sun(self, t: float) -> float:
        """
        Calculate Sun longitude using simple epicycle model.
        
        Formula:
        Mean = (L0 + Rate * t) % 360
        Anomaly = Mean - Apogee
        Correction = -Amp * sin(Anomaly_rad)
        TrueLongitude = (Mean + Correction) % 360
        """
        L0 = self._get_planet_data('Sun', 'L0', 0.0)
        Rate = self._get_planet_data('Sun', 'Rate', 0.0)
        Apogee = self._get_planet_data('Sun', 'Apogee', 0.0)
        Amp = self._get_planet_data('Sun', 'Amp', 0.0)
        
        Mean = (L0 + Rate * t) % 360.0
        Anomaly = Mean - Apogee
        Anomaly_rad = math.radians(Anomaly)
        Correction = -Amp * math.sin(Anomaly_rad)
        TrueLongitude = (Mean + Correction) % 360.0
        
        return self._normalize(TrueLongitude)
    
    def _calc_moon(self, t: float) -> float:
        """
        Calculate Moon longitude using moving apogee epicycle model.
        
        Formula:
        Mean = (L0 + Rate * t) % 360
        TrueApogee = (ApogeeL0 + ApogeeRate * t) % 360
        Anomaly = Mean - TrueApogee
        Correction = Amplitude * sin(Anomaly_rad)
        TrueLongitude = (Mean + Correction) % 360
        """
        L0 = self._get_planet_data('Moon', 'L0', 0.0)
        Rate = self._get_planet_data('Moon', 'Rate', 0.0)
        A0 = self._get_planet_data('Moon', 'A0', 0.0)  # Apogee L0
        Rate_Apogee = self._get_planet_data('Moon', 'Rate_Apogee', 0.0)
        Amp = self._get_planet_data('Moon', 'Amp', 0.0)
        
        Mean = (L0 + Rate * t) % 360.0
        TrueApogee = (A0 + Rate_Apogee * t) % 360.0
        Anomaly = Mean - TrueApogee
        Anomaly_rad = math.radians(Anomaly)
        Correction = Amp * math.sin(Anomaly_rad)
        TrueLongitude = (Mean + Correction) % 360.0
        
        return self._normalize(TrueLongitude)
    
    def _calc_outer(self, planet: str, t: float) -> float:
        """
        Calculate outer planet (Mars, Jupiter, Saturn) longitude using double epicycle model.
        
        Formula:
        M_p = (L0_p + Rate_p * t) % 360
        M_s = (L0_sun + Rate_sun * t) % 360
        K_manda = M_p - Apogee
        Corr_manda = -MandaCoeff * sin(K_manda)
        TrueMean_p = M_p + Corr_manda
        K_sighra = M_s - TrueMean_p
        r = SighraCirc / 360.0
        y = r * sin(K_sighra)
        x = 1.0 + r * cos(K_sighra)
        Corr_sighra = arctan2(y, x) [in degrees]
        TrueLongitude = (TrueMean_p + Corr_sighra) % 360
        """
        L0_p = self._get_planet_data(planet, 'epoch_l0', 0.0)
        Rate_p = self._get_planet_data(planet, 'mean_motion', 0.0)
        L0_sun = self._get_planet_data(planet, 'sun_l0_ref', 0.0)
        Rate_sun = self._get_planet_data(planet, 'sun_rate_ref', 0.0)
        Apogee = self._get_planet_data(planet, 'apogee_l0', 0.0)
        MandaCoeff = self._get_planet_data(planet, 'manda_coeff', 0.0)
        SighraCirc = self._get_planet_data(planet, 'sighra_circ', 0.0)
        
        # Mean Position
        M_p = (L0_p + Rate_p * t) % 360.0
        
        # Mean Sun
        M_s = (L0_sun + Rate_sun * t) % 360.0
        
        # Manda Correction (Orbit Shape)
        K_manda = M_p - Apogee
        K_manda_rad = math.radians(K_manda)
        Corr_manda = -MandaCoeff * math.sin(K_manda_rad)
        TrueMean_p = M_p + Corr_manda
        
        # Sighra Correction (Retrograde Loop)
        K_sighra = M_s - TrueMean_p
        K_sighra_rad = math.radians(K_sighra)
        r = SighraCirc / 360.0
        y = r * math.sin(K_sighra_rad)
        x = 1.0 + r * math.cos(K_sighra_rad)
        Corr_sighra_rad = math.atan2(y, x)
        Corr_sighra = math.degrees(Corr_sighra_rad)
        
        TrueLongitude = (TrueMean_p + Corr_sighra) % 360.0
        
        return self._normalize(TrueLongitude)
    
    def _calc_inner(self, planet: str, t: float) -> float:
        """
        Calculate inner planet (Mercury, Venus) longitude using inverted double epicycle model.
        
        For inner planets, the "Mean Planet" is the Sun, and the "Sighra Ucca" is the Fast Planet.
        
        Formula:
        M_s = (L0_sun + Rate_sun * t) % 360
        U_sighra = (L0_p + Rate_p * t) % 360
        K_manda = M_s - Apogee
        Corr_manda = -MandaCoeff * sin(K_manda)
        TrueMean_sun = M_s + Corr_manda
        K_sighra = U_sighra - TrueMean_sun
        r = SighraCirc / 360.0
        y = r * sin(K_sighra)
        x = 1.0 + r * cos(K_sighra)
        Corr_sighra = arctan2(y, x) [in degrees]
        TrueLongitude = (TrueMean_sun + Corr_sighra) % 360
        """
        L0_sun = self._get_planet_data(planet, 'sun_l0_ref', 0.0)
        Rate_sun = self._get_planet_data(planet, 'sun_rate_ref', 0.0)
        L0_p = self._get_planet_data(planet, 'epoch_l0', 0.0)  # Sighra Ucca
        Rate_p = self._get_planet_data(planet, 'mean_motion', 0.0)
        Apogee = self._get_planet_data(planet, 'apogee_l0', 0.0)
        MandaCoeff = self._get_planet_data(planet, 'manda_coeff', 0.0)
        SighraCirc = self._get_planet_data(planet, 'sighra_circ', 0.0)
        
        # Mean Sun (Deferent Center)
        M_s = (L0_sun + Rate_sun * t) % 360.0
        
        # Sighra Ucca (Fast Planet)
        U_sighra = (L0_p + Rate_p * t) % 360.0
        
        # Manda Correction (Applied to Sun using Planet's Apogee!)
        K_manda = M_s - Apogee
        K_manda_rad = math.radians(K_manda)
        Corr_manda = -MandaCoeff * math.sin(K_manda_rad)
        TrueMean_sun = M_s + Corr_manda
        
        # Sighra Correction
        K_sighra = U_sighra - TrueMean_sun
        K_sighra_rad = math.radians(K_sighra)
        r = SighraCirc / 360.0
        y = r * math.sin(K_sighra_rad)
        x = 1.0 + r * math.cos(K_sighra_rad)
        Corr_sighra_rad = math.atan2(y, x)
        Corr_sighra = math.degrees(Corr_sighra_rad)
        
        TrueLongitude = (TrueMean_sun + Corr_sighra) % 360.0
        
        return self._normalize(TrueLongitude)
    
    def _calc_node(self, planet: str, t: float) -> float:
        """
        Calculate node (Rahu, Ketu) longitude using linear motion.
        
        Formula:
        True = (L0 + Rate * t) % 360
        """
        L0 = self._get_planet_data(planet, 'epoch_l0', 0.0)
        Rate = self._get_planet_data(planet, 'mean_motion', 0.0)
        
        TrueLongitude = (L0 + Rate * t) % 360.0
        
        return self._normalize(TrueLongitude)
    
    def calculate_longitude(self, planet: str, jd: float) -> float:
        """
        Calculate planet longitude using Parametric Epicyclic Model.
        
        Dispatches to appropriate calculation method based on planet type.
        
        Args:
            planet: Planet name
            jd: Julian Day (will be converted to UTC datetime, then to days since 2000)
            
        Returns:
            Longitude in degrees (0-360)
        """
        if planet not in self.tables:
            raise ValueError(f"Planet {planet} not found in tables")
        
        # Convert JD to UTC datetime, then to days since 2000-01-01 00:00:00 UTC
        dt_utc = self._jd_to_datetime_utc(jd)
        t = self._to_utc_days(dt_utc)
        
        # Dispatch to appropriate calculation method
        if planet == 'Sun':
            return self._calc_sun(t)
        elif planet == 'Moon':
            return self._calc_moon(t)
        elif planet in ['Mars', 'Jupiter', 'Saturn']:
            return self._calc_outer(planet, t)
        elif planet in ['Mercury', 'Venus']:
            return self._calc_inner(planet, t)
        elif planet in ['Rahu', 'Ketu']:
            return self._calc_node(planet, t)
        else:
            raise ValueError(f"Unknown planet: {planet}")
    
    def check_retrograde(self, planet: str, jd: float) -> bool:
        """
        Check if a planet is retrograde by calculating instantaneous velocity.
        
        Method:
        1. Calculate Pos1 at time t
        2. Calculate Pos2 at time t + (1/24.0) (1 hour later)
        3. Velocity = Pos2 - Pos1
        4. Handle 360-degree wrap (if vel < -300, it implies 359->0 wrap, so add 360)
        5. If Velocity < 0, return True
        
        Args:
            planet: Planet name
            jd: Julian Day
            
        Returns:
            True if planet is retrograde, False otherwise
        """
        if planet in ['Sun', 'Moon', 'Rahu', 'Ketu']:
            # These planets don't go retrograde
            return False
        
        # Calculate position at time t
        Pos1 = self.calculate_longitude(planet, jd)
        
        # Calculate position 1 hour later
        dt_utc = self._jd_to_datetime_utc(jd)
        dt_utc_next = dt_utc + timedelta(hours=1)
        jd_next = self._jd_to_julian_day(dt_utc_next)
        Pos2 = self.calculate_longitude(planet, jd_next)
        
        # Calculate velocity (change in position)
        Velocity = Pos2 - Pos1
        
        # Handle 360-degree wrap
        if Velocity < -300:
            # Likely wrapped from 359->0, so add 360
            Velocity += 360.0
        elif Velocity > 300:
            # Likely wrapped from 0->359, so subtract 360
            Velocity -= 360.0
        
        # Retrograde if velocity is negative
        return Velocity < 0
    
    def _jd_to_julian_day(self, dt_utc: datetime) -> float:
        """Convert UTC datetime to Julian Day"""
        # Simple conversion: days since J2000.0
        delta = dt_utc - datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        days = delta.total_seconds() / 86400.0
        return 2451545.0 + days
    
    def calculate_longitudes(self, jd: float) -> Dict[str, float]:
        """
        Calculate all planet longitudes using Parametric Epicyclic Model.
        
        Args:
            jd: Julian Day
            
        Returns:
            Dictionary of planet names to longitudes in degrees
        """
        results = {}
        
        # Calculate all planets
        for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']:
            try:
                results[planet] = self.calculate_longitude(planet, jd)
            except Exception as e:
                print(f"⚠️  Warning: Error calculating {planet}: {e}")
                results[planet] = 0.0
        
        return results


class VakyaEphemerisProvider:
    """
    Table-Lookup Based Vakya Ephemeris Provider.
    Uses J2000.0 (JD 2451545.0 = January 1, 2000, 12:00 TT) as the base epoch.
    Uses reverse-engineered lookup tables from final_vakya_tables.json for all calculations.
    
    The system uses table-based lookup:
    - Longitude = Anchor + (Rate * days) + Table_Correction[cycle_position]
    """

    def __init__(self, tables_file: Optional[str] = None):
        """
        Initialize VakyaEphemerisProvider with table-based lookup engine.
        
        Args:
            tables_file: Path to final_vakya_tables.json. If None, uses default location.
        """
        # Initialize the VakyaEngine for table-based calculations
        self.engine = VakyaEngine(tables_file)

    def calculate_longitudes(self, jd: float) -> Dict[str, float]:
        """
        Calculate sidereal longitudes using table-based lookup.
        
        Uses the VakyaEngine to perform all calculations via table lookup.
        All corrections are retrieved from pre-computed tables based on cycle position.
        
        Args:
            jd: Julian Day of birth
            
        Returns:
            Dictionary of planet names to longitudes in degrees
        """
        return self.engine.calculate_longitudes(jd)


class AyanamsaProvider:
    """Configurable ayanamsa provider for different almanacs"""
    
    def __init__(self, system: str = "vakya"):
        self.system = system
        # Use Lahiri as standard reference for geometric calculations
        self.profiles = {
            "vakya": {"base": 23.85, "drift": 5029.0966 / 3600.0},
            "lahiri": {"base": 23.852583333, "drift": 5029.0966 / 3600.0}
        }
    
    def calculate_ayanamsa(self, jd: float) -> float:
        if self.system not in self.profiles:
            profile = self.profiles["lahiri"]
        else:
            profile = self.profiles[self.system]
        t = (jd - 2451545.0) / 36525.0
        return (profile["base"] + profile["drift"] * t) % 360.0


# Graha Vakra in Vakya/ICS charts: Mars, Jupiter, Venus, Saturn only (not Mercury).
VAKRA_PLANETS = frozenset({"Mars", "Jupiter", "Venus", "Saturn"})

# ICS Vakkiam Pro uses strict 3°20' pada boundaries with no lag.
# Reference: Venus at 236°53'56" (13.93' into Kettai 4) and Sun at 247°16'34"
# (13.93' into Mulam 3) both display the current pada, proving no meaningful lag.
NAKSHATRA_PADA_BOUNDARY_EPS = 0.0
NAKSHATRA_PADA_LAG_INTS = (1, 2, 3)  # retained but EPS=0 disables the lag


class VakkiamCalculator(AstronomicalCalculations):
    """
    Traditional Vakkiam system astrology calculations.
    """

    def __init__(self, ayanamsa_provider: str = "vakya"):
        super().__init__()
        self.system_name = "vakkiam"
        self.vakya_ephemeris = VakyaEphemerisProvider()
        self.ayanamsa_provider = AyanamsaProvider(ayanamsa_provider)
        _data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'vakya')
        self._vakya_engine = VakyaTableEngine(_data_dir)

    def calculate_planetary_positions_vakya(self, jd: float) -> Dict[str, Dict]:
        """Calculate planetary positions using generalized Vakya engine"""
        raw_longitudes = self.vakya_ephemeris.calculate_longitudes(jd)
        positions = {}
        for planet in PLANETS.values():
            if planet not in raw_longitudes: continue
            lon = raw_longitudes[planet]
            positions[planet] = {
                'longitude': lon,
                'latitude': 0.0,
                'sign': self.get_sign_from_longitude(lon),
                'nakshatra': self.get_nakshatra_from_longitude(lon)
            }
        return positions

    def get_julian_day_lmt(self, birth_date: date, birth_time: time, longitude: float) -> float:
        # Standardize on IST input
        dt_local = datetime.combine(birth_date, birth_time)
        dt_utc = dt_local - timedelta(hours=5.5)
        return self.get_julian_day(dt_utc.date(), dt_utc.time(), 0.0)

    def get_nakshatra_pada(self, lon: float) -> int:
        """Vakya/ICS nakshatra pada for Moon (ICS quarter-entry lag)."""
        return self._ics_nakshatra_pada(lon)

    def _ics_nakshatra_pada(self, lon: float) -> int:
        """ICS-style pada: 3°20' quarters with lag at pada 2/3/4 entry."""
        span = 360.0 / 27.0
        pada_span = span / 4.0
        pos_in_nak = lon % span
        q = pos_in_nak / pada_span
        pada = int(q) + 1
        frac = q - int(q)
        if int(q) in NAKSHATRA_PADA_LAG_INTS and frac < NAKSHATRA_PADA_BOUNDARY_EPS:
            pada -= 1
        return min(4, max(1, pada))

    def _is_retrograde_vakya(self, planet: str, jd: float) -> bool:
        """Retrograde via hourly Vakya velocity; only outer grahas appear in Graha Vakra."""
        if planet not in VAKRA_PLANETS:
            return False
        return self.vakya_ephemeris.engine.check_retrograde(planet, jd)

    # Vakyakarana ayanamsa (Vakyakarana, IJHS 36.3-4 (2001), p.129):
    #   dY = Kali year - 3600
    #   ayanamsa = [dY - dY/121] / 60  degrees   (= dY * (120/121) / 60)
    # i.e. zero at Kali 3600 and ~59.5"/yr. Verified against the treatise:
    #   K4383 (AD 1282) -> 12.942 deg = 12 deg 56' 31", matching the paper.
    VAKYAKARANA_KALI_EPOCH_JD = 588465.5      # Kali Yuga start (18 Feb 3102 BCE)
    VAKYAKARANA_SIDEREAL_YEAR = 365.258681    # treatise solar year (365.25 + 5/576)

    def vakyakarana_ayanamsa(self, jd: float) -> float:
        """Ayanamsa in degrees as prescribed by the Vakyakarana treatise."""
        kali_year = (jd - self.VAKYAKARANA_KALI_EPOCH_JD) / self.VAKYAKARANA_SIDEREAL_YEAR
        return (kali_year - 3600.0) * (120.0 / 121.0) / 60.0

    def calculate_ascendant_traditional(self, jd: float, latitude: float, longitude: float) -> float:
        """Lagna using the Vakyakarana treatise's own ayanamsa.

        The ascendant is the astronomical (Placidus) rising point, converted to
        the sidereal (nirayana) frame with the ayanamsa prescribed by the
        Vakyakarana itself — NOT Lahiri.  We therefore take the *tropical*
        ascendant from Swiss Ephemeris and subtract `vakyakarana_ayanamsa(jd)`.

        (Previously this used Swiss Ephemeris' Lahiri sidereal ascendant to match
        ICS Vakkiam Pro; it now follows the treatise, which runs ~1 deg higher in
        ayanamsa than Lahiri for modern dates.)  jd here is already UT-based.
        Planets remain Vakya-table values (that is what the Vakya system uses).
        """
        _, ascmc = swe.houses_ex(jd, latitude, longitude, b'P')  # tropical cusps
        tropical_asc = ascmc[0] % 360.0
        return (tropical_asc - self.vakyakarana_ayanamsa(jd)) % 360.0

    def get_daily_panchangam(self, target_date: date, language: str = "tamil") -> Dict:
        """Vakya (Vakkiyam) daily Panchangam — identical field structure to the
        Thirukkanitham panchangam, but tithi / nakshatra / yoga / karana are
        derived from the Vakya (table-based, nirayana) Sun & Moon rather than
        the Drik ephemeris. Rise/set and muhurta timings are physical events,
        computed astronomically as in the Thirukkanitham version."""
        latitude, longitude, timezone_offset = 13.0827, 80.2707, 5.5
        local_noon = time(12, 0)

        # Vakya Sun & Moon at local noon (nirayana longitudes from the tables)
        vres = self._vakya_engine.compute(
            datetime.combine(target_date, local_noon), latitude, longitude, timezone_offset
        )
        vakya_sun = vres['Sun']['longitude'] % 360.0
        vakya_moon = vres['Moon']['longitude'] % 360.0

        # Tithi / yoga / karana / sunrise / sunset from the Vakya Sun & Moon
        details = self.calculate_panchangam_details(
            target_date, local_noon, latitude, longitude, timezone_offset,
            sun_longitude=vakya_sun, moon_longitude=vakya_moon,
        )
        nakshatra_number = self.get_nakshatra_from_longitude(vakya_moon)

        # Moonrise / moonset — physical events (astronomical, as in Thirukkanitham)
        utc_midnight = datetime.combine(target_date, time.min) - timedelta(hours=timezone_offset)
        jd_midnight = swe.julday(
            utc_midnight.year, utc_midnight.month, utc_midnight.day,
            utc_midnight.hour + utc_midnight.minute / 60.0,
        )

        def event_time(body: int, event: int) -> str:
            try:
                result = swe.rise_trans(jd_midnight, body, event, (longitude, latitude, 0.0))[1][0]
                local = swe.revjul(result + timezone_offset / 24.0)[3]
                hours = int(local) % 24
                mins = int(round((local % 1) * 60))
                if mins == 60:
                    hours = (hours + 1) % 24
                    mins = 0
                return f"{hours:02d}:{mins:02d}"
            except Exception:
                return "--:--"

        moonrise = event_time(swe.MOON, swe.CALC_RISE)
        moonset = event_time(swe.MOON, swe.CALC_SET)

        def to_minutes(value: str) -> int:
            h, m = value.split(":")
            return int(h) * 60 + int(m)

        def clock(value: float) -> str:
            total = int(round(value)) % (24 * 60)
            return f"{total // 60:02d}:{total % 60:02d}"

        sunrise_minutes = to_minutes(details["sunrise_time"])
        sunset_minutes = to_minutes(details["sunset_time"])
        daylight_segment = (sunset_minutes - sunrise_minutes) / 8.0

        def segment(index: int) -> Dict:
            start = sunrise_minutes + daylight_segment * index
            return {"start": clock(start), "end": clock(start + daylight_segment)}

        weekday = target_date.weekday()  # Monday = 0
        rahu_indices = [1, 6, 4, 5, 3, 2, 7]
        yama_indices = [3, 2, 1, 0, 6, 5, 4]
        gulika_indices = [5, 4, 3, 2, 1, 0, 6]
        rahu_kalam = segment(rahu_indices[weekday])
        yama_gandam = segment(yama_indices[weekday])
        gulika_kalam = segment(gulika_indices[weekday])

        solar_noon = (sunrise_minutes + sunset_minutes) / 2.0
        abhijit_muhurta = {"start": clock(solar_noon - 24), "end": clock(solar_noon + 24)}

        return {
            "date": target_date.isoformat(),
            "system": "vakkiam",
            "tithi": details["tithi"],
            "tithi_tamil": details["tithi_tamil"],
            "nakshatra": NAKSHATRAS[nakshatra_number],
            "nakshatra_tamil": NAKSHATRAS_TAMIL[nakshatra_number],
            "yoga": details["yoga"],
            "yoga_tamil": details["yoga_tamil"],
            "karana": details["karana"],
            "karana_tamil": details["karana_tamil"],
            "sunrise": details["sunrise_time"],
            "sunset": details["sunset_time"],
            "moonrise": moonrise,
            "moonset": moonset,
            "rahu_kalam": rahu_kalam,
            "yama_gandam": yama_gandam,
            "gulika_kalam": gulika_kalam,
            "abhijit_muhurta": abhijit_muhurta,
            "auspicious_times": [
                {"name": "Abhijit Muhurta", "tamil": "அபிஜித் முகூர்த்தம்",
                 "description": f"{abhijit_muhurta['start']} - {abhijit_muhurta['end']}"},
            ],
            "inauspicious_times": [
                {"name": "Rahu Kalam", "tamil": "ராகு காலம்",
                 "description": f"{rahu_kalam['start']} - {rahu_kalam['end']}"},
                {"name": "Yama Gandam", "tamil": "எமகண்டம்",
                 "description": f"{yama_gandam['start']} - {yama_gandam['end']}"},
                {"name": "Gulika Kalam", "tamil": "குளிகை காலம்",
                 "description": f"{gulika_kalam['start']} - {gulika_kalam['end']}"},
            ],
        }

    def calculate_sidereal_time_meeus(self, jd: float, longitude: float) -> float:
        """Calculate Local Sidereal Time using Meeus formula"""
        t = (jd - 2451545.0) / 36525.0
        theta_g = (280.46061837 + 360.98564736629 * (jd - 2451545.0) + 
                   0.000387933 * t * t - t * t * t / 38710000.0) % 360.0
        lst = (theta_g + longitude) % 360.0
        return lst

    def calculate_navamsa_position(self, longitude: float) -> int:
        """
        Calculate Navamsa position (D9).
        Rule:
        - Movable (1,4,7,10): Starts from Self
        - Fixed (2,5,8,11): Starts from 9th
        - Dual (3,6,9,12): Starts from 5th
        """
        sign = int(longitude // 30) + 1
        degree_in_sign = longitude % 30
        navamsa_segment = int(degree_in_sign // (30/9)) # 0-8
        
        if sign in [1, 4, 7, 10]:
            start_sign = sign
        elif sign in [2, 5, 8, 11]:
            start_sign = ((sign - 1 + 8) % 12) + 1
        else:
            start_sign = ((sign - 1 + 4) % 12) + 1
        
        return ((start_sign - 1 + navamsa_segment) % 12) + 1

    def _calculate_navamsa_sign(self, longitude: float) -> int:
        return self.calculate_navamsa_position(longitude)

    def _format_date_tamil(self, date_obj: date) -> str:
        """Format date as DD/MM/YYYY for Tamil display"""
        return f"{date_obj.day:02d}/{date_obj.month:02d}/{date_obj.year}"

    def _calculate_retrograde_status_tamil(self, planetary_positions: List[PlanetaryPosition]) -> str:
        """Identify retrograde planets and return Tamil status string"""
        retrograde_planets = [p for p in planetary_positions if p.retrograde and p.planet != "Ascendant"]
        if not retrograde_planets:
            return "இல்லை"
        # Format as comma-separated Tamil planet names
        planet_names = [p.planet_tamil for p in retrograde_planets]
        return ", ".join(planet_names)

    def _create_bhava_chalit_chart(self, positions: Dict, ascendant_longitude: float) -> Chart:
        """Create Bhava chart using Whole Sign House system (House 1 = Ascendant Sign)"""
        asc_sign = self.get_sign_from_longitude(ascendant_longitude)
        houses = {i: [] for i in range(1, 13)}
        houses_tamil = {i: [] for i in range(1, 13)}
        
        # Ascendant in House 1
        houses[1].append("Asc")
        houses_tamil[1].append("லக்")
        
        # Place planets in houses based on whole sign system
        for planet, pos in positions.items():
            planet_sign = self.get_sign_from_longitude(pos['longitude'])
            # House index relative to ascendant sign (1-based)
            house_idx = ((planet_sign - asc_sign) % 12) + 1
            houses[house_idx].append(planet)
            houses_tamil[house_idx].append(PLANET_NAMES.get(planet, planet))
        
        return Chart(
            chart_type="bhava_whole_sign",
            houses=houses,
            houses_tamil=houses_tamil,
            ascendant_house=1
        )

    def _calculate_bhava_change_tamil(self, rasi_chart: Chart, bhava_chart: Chart, planetary_positions: List[PlanetaryPosition]) -> str:
        """Bhava Chalit: identify planets whose bhava house differs from their whole-sign (rasi) house.

        The bhava cusp of each house falls at the same degree as the ascendant within each sign.
        A planet 'moves' from its rasi (whole-sign) house when:
          - its degree within its sign > ascendant's degree-in-sign → planet is in the NEXT bhava
          - its degree within its sign < ascendant's degree-in-sign → planet is in the PREVIOUS bhava

        Sun is excluded per Vakya tradition (Vakya Sun is less reliable near cusps).
        Returns Tamil string like 'சந்திரன்-7, செவ்வாய்-8' for planets in a changed bhava.
        """
        changes = []

        # Ascendant's degree within its sign (the bhava cusp degree)
        asc_lon = next(
            (p.longitude for p in planetary_positions if p.planet == "Ascendant"), None
        )
        if asc_lon is None:
            return "இல்லை"

        asc_sign = rasi_chart.ascendant_house
        asc_deg_in_sign = asc_lon % 30.0  # 0..30°, the cusp degree within each sign

        _FULL_NAMES = {
            'Moon':    'சந்திரன்',
            'Mars':    'செவ்வாய்',
            'Mercury': 'புதன்',
            'Jupiter': 'குரு',
            'Venus':   'சுக்கிரன்',
            'Saturn':  'சனி',
            'Rahu':    'ராகு',
            'Ketu':    'கேது',
        }

        for planet_pos in planetary_positions:
            if planet_pos.planet in ("Ascendant", "Sun"):
                continue  # Sun excluded; Ascendant is the reference

            lon = planet_pos.longitude
            sign = planet_pos.sign
            planet_deg_in_sign = lon % 30.0

            # Whole-sign (rasi) house
            rasi_house = ((sign - asc_sign) % 12) + 1

            # Bhava Chalit house
            if planet_deg_in_sign > asc_deg_in_sign:
                bhava_house = (rasi_house % 12) + 1       # moves to next bhava
            elif planet_deg_in_sign < asc_deg_in_sign:
                bhava_house = ((rasi_house - 2) % 12) + 1  # moves to previous bhava
            else:
                bhava_house = rasi_house                   # exactly on cusp — stays

            if bhava_house != rasi_house:
                planet_tamil = _FULL_NAMES.get(planet_pos.planet, planet_pos.planet_tamil)
                changes.append(f"{planet_tamil}-{bhava_house}")

        if not changes:
            return "இல்லை"
        return ", ".join(changes)

    def _calculate_dasa_balance_tamil(self, dasa_periods: List[DasaPeriod]) -> str:
        """Format the first Dasa period's balance into Tamil string"""
        if not dasa_periods:
            return "இல்லை"
        
        first_dasa = dasa_periods[0]
        if first_dasa.balance_years is None or first_dasa.balance_months is None or first_dasa.balance_days is None:
            return "இல்லை"
        
        lord_tamil = first_dasa.planet_tamil
        years = first_dasa.balance_years
        months = first_dasa.balance_months
        days = first_dasa.balance_days
        
        return f"{lord_tamil} திசை {years} வருடம் {months} மாதம் {days} நாள்"

    def _calculate_current_dasa_bhukthi_tamil(self, current_dasa: DasaPeriod) -> str:
        """Format current Dasa and Bhukthi end dates into Tamil string"""
        if not current_dasa:
            return "இல்லை"
        
        dasa_lord_tamil = current_dasa.planet_tamil
        dasa_end_date_str = self._format_date_tamil(current_dasa.end_date) if current_dasa.end_date else "N/A"
        
        # Get bhukthi information if available
        if current_dasa.current_bhukti_planet_tamil and current_dasa.current_bhukti_end_date:
            bhukthi_lord_tamil = current_dasa.current_bhukti_planet_tamil
            # Parse and format bhukthi end date (stored as ISO format string: YYYY-MM-DD)
            try:
                if isinstance(current_dasa.current_bhukti_end_date, str):
                    # Parse ISO format date string (YYYY-MM-DD)
                    from datetime import datetime
                    bhukthi_date = datetime.strptime(current_dasa.current_bhukti_end_date.split('T')[0], '%Y-%m-%d').date()
                    bhukthi_end_date_str = self._format_date_tamil(bhukthi_date)
                elif hasattr(current_dasa.current_bhukti_end_date, 'year'):
                    # It's already a date object
                    bhukthi_end_date_str = self._format_date_tamil(current_dasa.current_bhukti_end_date)
                else:
                    bhukthi_end_date_str = str(current_dasa.current_bhukti_end_date)
            except (ValueError, AttributeError):
                # If parsing fails, use as-is
                bhukthi_end_date_str = current_dasa.current_bhukti_end_date
            return f"{dasa_lord_tamil} திசை {dasa_end_date_str} வரை , {bhukthi_lord_tamil} புக்தி {bhukthi_end_date_str} வரை"
        else:
            return f"{dasa_lord_tamil} திசை {dasa_end_date_str} வரை"

    def generate_horoscope(self, birth_details: BirthDetails, language: str = "tamil") -> HoroscopeResult:
        jd = self.get_julian_day_lmt(
            birth_details.date_of_birth, birth_details.time_of_birth, birth_details.longitude
        )
        tz_hours = self._parse_timezone(birth_details.timezone)
        birth_dt_local = datetime.combine(birth_details.date_of_birth, birth_details.time_of_birth)
        table_result = self._vakya_engine.compute(
            birth_dt_local, birth_details.latitude, birth_details.longitude, tz_hours
        )
        planetary_positions_raw = {}
        _retro_flags: Dict[str, bool] = {}
        for pname, pdata in table_result.items():
            # Planets come from the Vakya tables (this is what ICS itself uses).
            # The Lagna does NOT — ICS computes it astronomically, so the Vakya
            # engine's 'Lagnam' entry is intentionally discarded here.
            if pname == 'Lagnam':
                continue
            lon = pdata['longitude']
            planetary_positions_raw[pname] = {
                'longitude': lon,
                'latitude': 0.0,
                'sign': self.get_sign_from_longitude(lon),
                'nakshatra': self.get_nakshatra_from_longitude(lon),
            }
            _retro_flags[pname] = pdata['retrograde']
        # Lagna via ICS's real algorithm: astronomical sidereal (Lahiri) ascendant.
        ascendant_longitude = self.calculate_ascendant_traditional(
            jd, birth_details.latitude, birth_details.longitude
        )
        house_cusps = self.calculate_houses(ascendant_longitude)

        planetary_positions: List[PlanetaryPosition] = []

        for planet_name, position in planetary_positions_raw.items():
            retro = _retro_flags.get(planet_name, False)

            lon = position['longitude']
            
            # Navamsa calculation
            nav_sign = self.calculate_navamsa_position(lon)
            
            planet_pos = PlanetaryPosition(
                planet=planet_name,
                planet_tamil=PLANET_NAMES.get(planet_name, planet_name),
                longitude=lon,
                sign=position['sign'],
                sign_name=SIGNS[position['sign']],
                sign_name_tamil=SIGNS_TAMIL[position['sign']],
                nakshatra=position['nakshatra'],
                nakshatra_name=NAKSHATRAS[position['nakshatra']],
                nakshatra_name_tamil=NAKSHATRAS_TAMIL[position['nakshatra']],
                house=self.get_planet_house(lon, house_cusps),
                retrograde=retro,
                longitude_dms=self.deg_to_dms(lon),
                longitude_in_sign=lon % 30.0,
                longitude_in_sign_dms=self.deg_to_dms(lon % 30.0),
                nakshatra_pada=self.get_nakshatra_pada(lon),
                nakshatra_lord=self.get_nakshatra_lord(position['nakshatra']),
                nakshatra_lord_tamil=PLANET_NAMES.get(self.get_nakshatra_lord(position['nakshatra']))
            )
            planetary_positions.append(planet_pos)

        asc_sign = self.get_sign_from_longitude(ascendant_longitude)
        asc_pos = PlanetaryPosition(
            planet="Ascendant",
            planet_tamil="லக்னம்",
            longitude=ascendant_longitude,
            sign=asc_sign,
            sign_name=SIGNS[asc_sign],
            sign_name_tamil=SIGNS_TAMIL[asc_sign],
            nakshatra=self.get_nakshatra_from_longitude(ascendant_longitude),
            nakshatra_name=NAKSHATRAS[self.get_nakshatra_from_longitude(ascendant_longitude)],
            nakshatra_name_tamil=NAKSHATRAS_TAMIL[self.get_nakshatra_from_longitude(ascendant_longitude)],
            house=1,
            longitude_dms=self.deg_to_dms(ascendant_longitude),
            longitude_in_sign=ascendant_longitude % 30.0,
            longitude_in_sign_dms=self.deg_to_dms(ascendant_longitude % 30.0),
            nakshatra_pada=self.get_nakshatra_pada(ascendant_longitude),
            nakshatra_lord=self.get_nakshatra_lord(self.get_nakshatra_from_longitude(ascendant_longitude)),
            nakshatra_lord_tamil=PLANET_NAMES.get(self.get_nakshatra_lord(self.get_nakshatra_from_longitude(ascendant_longitude)))
        )
        planetary_positions.insert(0, asc_pos)

        rasi_chart = self._create_rasi_chart(planetary_positions_raw, ascendant_longitude)
        navamsa_positions = self.calculate_navamsa(planetary_positions_raw, ascendant_longitude)
        nav_lagna_sign = self._calculate_navamsa_sign(ascendant_longitude)
        navamsa_chart = self._create_navamsa_chart(navamsa_positions, nav_lagna_sign)

        # Create Bhava chart for bhava change calculation
        bhava_chart = self._create_bhava_chalit_chart(planetary_positions_raw, ascendant_longitude)

        moon_position = planetary_positions_raw['Moon']
        dasa_periods = self._calculate_dasa_periods(
            moon_position['nakshatra'], birth_details.date_of_birth, moon_position['longitude']
        )
        current_dasa = self._get_current_dasa(dasa_periods)
        
        # Enhance current dasa with balance, next dasa, and bhukti information
        current_dasa = self._enhance_current_dasa(current_dasa, dasa_periods)

        # Helpers
        retrograde_planets = [p.planet for p in planetary_positions if p.retrograde and p.planet != "Ascendant"]
        retrograde_planets_tamil = [p.planet_tamil for p in planetary_positions if p.retrograde and p.planet != "Ascendant"]
        bhava_maruthal = {p.planet: p.house for p in planetary_positions if p.planet in ["Moon", "Mercury"]}
        bhava_maruthal_tamil = {p.planet_tamil: p.house for p in planetary_positions if p.planet in ["Moon", "Mercury"]}
        
        # Calculate Tamil horoscope detail fields
        retrograde_status_tamil = self._calculate_retrograde_status_tamil(planetary_positions)
        bhava_change_tamil = self._calculate_bhava_change_tamil(rasi_chart, bhava_chart, planetary_positions)
        dasa_balance_tamil = self._calculate_dasa_balance_tamil(dasa_periods)
        current_dasa_bhukthi_tamil = self._calculate_current_dasa_bhukthi_tamil(current_dasa)
        
        tz_offset = self._parse_timezone(birth_details.timezone)
        # Use Vakkiam-calculated Sun and Moon positions for panchangam
        sun_longitude = planetary_positions_raw.get('Sun', {}).get('longitude')
        moon_longitude = planetary_positions_raw.get('Moon', {}).get('longitude')
        # Get Vakkiam ayanamsa for the birth time
        jd = self.get_julian_day_lmt(
            birth_details.date_of_birth, birth_details.time_of_birth, birth_details.longitude
        )
        ayanamsa_value = self.ayanamsa_provider.calculate_ayanamsa(jd)
        panchangam = self.calculate_panchangam_details(
            birth_details.date_of_birth, birth_details.time_of_birth, 
            birth_details.latitude, birth_details.longitude, tz_offset,
            sun_longitude=sun_longitude, moon_longitude=moon_longitude,
            ayanamsa_value=ayanamsa_value
        )

        yogi_seq = ["Moon", "Sun", "Jupiter", "Mars", "Mercury", "Saturn", "Venus", "Rahu", "Ketu"]
        yogi_idx = (moon_position['nakshatra'] * 8) % 9
        yogi_planet = yogi_seq[yogi_idx]
        avayogi_planet = yogi_seq[(yogi_idx + 11) % 9]

        return HoroscopeResult(
            birth_details=birth_details.model_dump() if hasattr(birth_details, 'model_dump') else birth_details.dict() if hasattr(birth_details, 'dict') else birth_details, 
            system=self.system_name, language=language,
            ascendant=SIGNS[asc_sign], ascendant_tamil=SIGNS_TAMIL[asc_sign],
            moon_sign=SIGNS[moon_position['sign']], moon_sign_tamil=SIGNS_TAMIL[moon_position['sign']],
            nakshatra=NAKSHATRAS[moon_position['nakshatra']], nakshatra_tamil=NAKSHATRAS_TAMIL[moon_position['nakshatra']],
            planetary_positions=planetary_positions, rasi_chart=rasi_chart, navamsa_chart=navamsa_chart,
            dasa_periods=dasa_periods, current_dasa=current_dasa,
            retrograde_planets=retrograde_planets, retrograde_planets_tamil=retrograde_planets_tamil,
            bhava_maruthal=bhava_maruthal, bhava_maruthal_tamil=bhava_maruthal_tamil,
            sunrise_time=panchangam['sunrise_time'], sunset_time=panchangam['sunset_time'],
            paksha=panchangam['paksha'], paksha_tamil=panchangam['paksha_tamil'],
            tithi=panchangam['tithi'], tithi_tamil=panchangam['tithi_tamil'],
            yoga=panchangam['yoga'], yoga_tamil=panchangam['yoga_tamil'],
            karana=panchangam['karana'], karana_tamil=panchangam['karana_tamil'],
            ayanamsa=panchangam['ayanamsa'], udayadi_nazhigai=panchangam['udayadi_nazhigai'],
            tamil_month=panchangam.get('tamil_month'), tamil_day=panchangam.get('tamil_day'),
            tamil_year=panchangam.get('tamil_year'), tamil_year_name=panchangam.get('tamil_year_name'),
            yogi_planet=yogi_planet, yogi_planet_tamil=PLANET_NAMES.get(yogi_planet, yogi_planet),
            avayogi_planet=avayogi_planet, avayogi_planet_tamil=PLANET_NAMES.get(avayogi_planet, avayogi_planet),
            # Tamil horoscope detail fields
            retrograde_status_tamil=retrograde_status_tamil,
            bhava_change_tamil=bhava_change_tamil,
            dasa_balance_tamil=dasa_balance_tamil,
            current_dasa_bhukthi_tamil=current_dasa_bhukthi_tamil
        )

    # ── Vimshottari dasa: shared methodology (identical to Thirukkanitham) ──
    # Both systems use the SAME base-class dasa/bhukti computation; only the
    # Moon longitude differs (Vakya Moon here, Drik Moon for Thirukkanitham).
    # (Previously this class carried a divergent copy with hardcoded per-
    #  nakshatra Moon calibrations and hardcoded dates — removed so Vakkiam and
    #  Thirukkanitham share one methodology.)
    def _calculate_dasa_periods(self, birth_nakshatra: int, birth_date: date, moon_longitude_deg: float) -> List[DasaPeriod]:
        return super()._calculate_dasa_periods(birth_nakshatra, birth_date, moon_longitude_deg)

    def _get_current_dasa(self, periods: List[DasaPeriod]) -> DasaPeriod:
        return super()._get_current_dasa(periods)

    def _calculate_sub_dasha_periods(self, maha_dasa):
        return super()._calculate_sub_dasha_periods(maha_dasa)

    def check_compatibility(self, male_details, female_details, language="tamil"):
        male_h = self.generate_horoscope(male_details, language)
        female_h = self.generate_horoscope(female_details, language)
        # Use base class compatibility if available, or placeholder
        if hasattr(super(), 'check_compatibility'):
            return super().check_compatibility(male_details, female_details, language)
        return CompatibilityResult(
            male_details=male_details, female_details=female_details,
            system=self.system_name, language=language, total_points=0, max_points=36,
            percentage=0, overall_rating="", overall_rating_tamil="", factors=[],
            dosha_analysis={}, recommendation="", recommendation_tamil=""
        )

    # Required helpers for chart generation
    def _create_rasi_chart(self, positions, asc_lon):
        signs = {i: [] for i in range(1, 13)}
        signs_tamil = {i: [] for i in range(1, 13)}
        asc_sign = self.get_sign_from_longitude(asc_lon)
        signs[asc_sign].append("Asc")
        signs_tamil[asc_sign].append("லக்")
        for p, pos in positions.items():
            s = self.get_sign_from_longitude(pos['longitude'])
            signs[s].append(p)
            signs_tamil[s].append(PLANET_NAMES.get(p, p))
        return Chart(chart_type="rasi", houses=signs, houses_tamil=signs_tamil, ascendant_house=asc_sign)

    def _create_navamsa_chart(self, nav_positions, nav_asc_sign):
        signs = {i: [] for i in range(1, 13)}
        signs_tamil = {i: [] for i in range(1, 13)}
        signs[nav_asc_sign].append("Asc")
        signs_tamil[nav_asc_sign].append("லக்")
        for p, pos in nav_positions.items():
            if p == "Ascendant": continue
            s = pos['sign']
            signs[s].append(p)
            signs_tamil[s].append(PLANET_NAMES.get(p, p))
        return Chart(chart_type="navamsa", houses=signs, houses_tamil=signs_tamil, ascendant_house=nav_asc_sign)

    def _parse_timezone(self, tz_str):
        try:
            return float(tz_str)
        except (TypeError, ValueError):
            return 5.5
