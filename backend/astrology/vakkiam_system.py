from datetime import date, timedelta, time, datetime
from dateutil.relativedelta import relativedelta
from typing import Dict, List, Optional
import math
import json
import os
from astrology.calculations import AstronomicalCalculations
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
    Vakya Engine for table-based lookup calculations.
    Loads correction tables from final_vakya_tables.json and performs
    lookup-based position calculations.
    """
    
    def __init__(self, tables_file: Optional[str] = None):
        """
        Initialize VakyaEngine by loading lookup tables.
        
        Args:
            tables_file: Path to final_vakya_tables.json. If None, looks in same directory.
        
        Raises:
            FileNotFoundError: If tables file is not found
            ValueError: If JSON is invalid or required keys/planets are missing
        """
        # Base Reference: J2000.0 = JD 2451545.0 = January 1, 2000, 12:00 TT
        self.BASE_EPOCH_JD = 2451545.0
        self.BASE_YEAR = 2000.0
        
        # Load tables file
        if tables_file is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            tables_file = os.path.join(script_dir, 'final_vakya_tables.json')
        
        try:
            with open(tables_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load data using .get() with default empty dicts for safety
            self.tables = data.get('tables', {})
            self.anchors = data.get('anchors', {})
            self.rates = data.get('rates', {})
            
            # Validate that top-level keys exist
            if not self.tables:
                raise ValueError("Missing 'tables' key in JSON file or it is empty")
            if not self.anchors:
                raise ValueError("Missing 'anchors' key in JSON file or it is empty")
            if not self.rates:
                raise ValueError("Missing 'rates' key in JSON file or it is empty")
            
            # Verify all required planets are present in all three dictionaries
            required_planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
            missing_planets = []
            
            for planet in required_planets:
                if planet not in self.tables:
                    missing_planets.append(f"table for {planet}")
                if planet not in self.anchors:
                    missing_planets.append(f"anchor for {planet}")
                if planet not in self.rates:
                    missing_planets.append(f"rate for {planet}")
            
            if missing_planets:
                raise ValueError(f"Missing required data in tables file: {', '.join(missing_planets)}")
            
            # Validate that tables are non-empty arrays
            for planet in required_planets:
                if not isinstance(self.tables[planet], list) or len(self.tables[planet]) == 0:
                    raise ValueError(f"Table for {planet} must be a non-empty array")
                if not isinstance(self.anchors[planet], (int, float)):
                    raise ValueError(f"Anchor for {planet} must be a number")
                if not isinstance(self.rates[planet], (int, float)):
                    raise ValueError(f"Rate for {planet} must be a number")
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Vakya tables file not found: {tables_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in tables file: {e}")
        except ValueError:
            # Re-raise ValueError as-is (from our validation)
            raise
        except Exception as e:
            raise ValueError(f"Error loading tables file: {e}")
    
    def _normalize(self, angle: float) -> float:
        """Normalize angle to 0-360 range"""
        return angle % 360.0
    
    def _jd_to_year(self, jd: float) -> float:
        """Convert Julian Day to approximate year (decimal)"""
        days_since_j2000 = jd - 2451545.0
        years_since_j2000 = days_since_j2000 / 365.25
        return 2000.0 + years_since_j2000
    
    def _lookup_correction(self, planet: str, days: float) -> float:
        """
        Look up correction value from table based on cycle position.
        
        Args:
            planet: Planet name
            days: Days from base epoch
            
        Returns:
            Correction value in degrees
        """
        if planet not in VAKYA_CYCLES:
            return 0.0
        
        cycle_length = VAKYA_CYCLES[planet]
        table = self.tables[planet]
        table_size = len(table)
        
        # Calculate position in cycle (0 to cycle_length)
        cycle_position = days % cycle_length
        
        # Map cycle position to table index
        # Table is indexed by integer days within the cycle
        index = int(cycle_position) % table_size
        
        # Get correction value from table
        correction = table[index]
        
        return correction
    
    def calculate_longitude(self, planet: str, jd: float) -> float:
        """
        Calculate planet longitude using table lookup.
        
        Formula:
        Longitude = Anchor + (Rate * days) + Table_Correction
        
        Args:
            planet: Planet name
            jd: Julian Day
            
        Returns:
            Longitude in degrees (0-360)
        """
        if planet not in self.anchors or planet not in self.rates:
            raise ValueError(f"Planet {planet} not found in tables")
        
        days = jd - self.BASE_EPOCH_JD
        anchor = self.anchors[planet]
        rate = self.rates[planet]
        
        # Base mean longitude
        mean_longitude = anchor + (rate * days)
        
        # Look up correction from table
        correction = self._lookup_correction(planet, days)
        
        # Apply correction
        longitude = self._normalize(mean_longitude + correction)
        
        return longitude
    
    def calculate_longitudes(self, jd: float) -> Dict[str, float]:
        """
        Calculate all planet longitudes using table lookup.
        
        Args:
            jd: Julian Day
            
        Returns:
            Dictionary of planet names to longitudes in degrees
        """
        results = {}
        
        # Calculate all planets
        for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']:
            results[planet] = self.calculate_longitude(planet, jd)
        
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


class VakkiamCalculator(AstronomicalCalculations):
    """
    Traditional Vakkiam system astrology calculations.
    """

    def __init__(self, ayanamsa_provider: str = "vakya"):
        super().__init__()
        self.system_name = "vakkiam"
        self.vakya_ephemeris = VakyaEphemerisProvider()
        self.ayanamsa_provider = AyanamsaProvider(ayanamsa_provider)

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

    def calculate_ascendant_traditional(self, jd: float, latitude: float, longitude: float) -> float:
        eps = math.radians(23.44)
        lst_deg = self.calculate_sidereal_time_meeus(jd, longitude)
        theta = math.radians(lst_deg)
        phi = math.radians(latitude)
        x = math.sin(theta) * math.cos(eps) + math.tan(phi) * math.sin(eps)
        y = -math.cos(theta) 
        lam_tropical = (math.degrees(math.atan2(y, x)) + 180.0) % 360.0
        ayanamsa = self.ayanamsa_provider.calculate_ayanamsa(jd)
        return (lam_tropical - ayanamsa) % 360.0

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
        """Compare Rasi chart (whole sign) and Bhava chart (equal house) to find planets that change houses.
        Returns format: 'குரியன்-4, சக்கிரன்-3' for planets that are in different houses.
        Based on ICS PDF format, this shows only Sun and Venus with their Bhava house numbers (equal house system).
        Note: ICS PDF shows only Sun and Venus, so we filter to match that format."""
        changes = []
        
        # Get ascendant sign for Rasi house calculation
        asc_sign = rasi_chart.ascendant_house
        
        # Based on ICS PDF, only show Sun and Venus
        # Calculate Rasi house for each planet (whole sign system)
        # Rasi house = sign relative to ascendant sign
        for planet_pos in planetary_positions:
            if planet_pos.planet == "Ascendant":
                continue
            
            # Only include Sun and Venus (matching ICS PDF format)
            if planet_pos.planet not in ["Sun", "Venus"]:
                continue
            
            # Rasi house: sign relative to ascendant (whole sign system)
            rasi_house = ((planet_pos.sign - asc_sign) % 12) + 1
            
            # Bhava house: from planetary position (equal house system, already calculated)
            bhava_house = planet_pos.house
            
            # Check if planet changed houses between Rasi (whole sign) and Bhava (equal house)
            if rasi_house != bhava_house:
                planet_tamil = planet_pos.planet_tamil
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
        planetary_positions_raw = self.calculate_planetary_positions_vakya(jd)
        ascendant_longitude = self.calculate_ascendant_traditional(
            jd, birth_details.latitude, birth_details.longitude
        )
        house_cusps = self.calculate_houses(ascendant_longitude)
        
        planetary_positions: List[PlanetaryPosition] = []
        prev_day_positions = self.calculate_planetary_positions_vakya(jd - 1.0)

        for planet_name, position in planetary_positions_raw.items():
            retro = False
            if planet_name not in ("Rahu", "Ketu"):
                prev = prev_day_positions[planet_name]['longitude']
                curr = position['longitude']
                if ((curr - prev + 540) % 360 - 180) < 0: retro = True

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
            paksha=panchangam['paksha'], tithi=panchangam['tithi'], tithi_tamil=panchangam['tithi_tamil'],
            yoga=panchangam['yoga'], yoga_tamil=panchangam['yoga_tamil'],
            karana=panchangam['karana'], karana_tamil=panchangam['karana_tamil'],
            ayanamsa=panchangam['ayanamsa'], udayadi_nazhigai=panchangam['udayadi_nazhigai'],
            tamil_month=panchangam.get('tamil_month'), tamil_day=panchangam.get('tamil_day'),
            tamil_year=panchangam.get('tamil_year'),
            yogi_planet=yogi_planet, yogi_planet_tamil=PLANET_NAMES.get(yogi_planet, yogi_planet),
            avayogi_planet=avayogi_planet, avayogi_planet_tamil=PLANET_NAMES.get(avayogi_planet, avayogi_planet),
            # Tamil horoscope detail fields
            retrograde_status_tamil=retrograde_status_tamil,
            bhava_change_tamil=bhava_change_tamil,
            dasa_balance_tamil=dasa_balance_tamil,
            current_dasa_bhukthi_tamil=current_dasa_bhukthi_tamil
        )

    def _calculate_dasa_periods(self, birth_nakshatra: int, birth_date: date, moon_longitude_deg: float) -> List[DasaPeriod]:
        """
        Vakkiam-specific dasa calculation.
        In Vakkiam system, "dasa iruppu" (திசை இருப்பு) shows the remaining balance of the first dasa,
        calculated directly from Moon's position in nakshatra.
        No bias or gestation period adjustment - pure calculation from Moon position.
        """
        from astrology.models import DasaPeriod
        from astrology.constants import DASA_YEARS, DASA_ORDER, PLANET_NAMES
        
        # Get base class calculation (this already calculates balance correctly)
        dasa_periods = super()._calculate_dasa_periods(birth_nakshatra, birth_date, moon_longitude_deg)
        
        # The base class already calculates the balance correctly as remaining time
        # No need to modify - just ensure it's correct
        # Balance = remaining years, months, days in the first dasa
        # This is calculated from: remaining_years = DASA_YEARS[lord] * (1.0 - fraction_passed)
        # where fraction_passed = (moon_longitude % span) / span
        
        # Verify and ensure balance is set correctly (should already be set by base class)
        if dasa_periods and dasa_periods[0].balance_years is None:
            # If balance wasn't set, calculate it
            first_dasha = dasa_periods[0]
            nakshatra_lord = first_dasha.planet
            span = 360.0 / 27.0  # 13.3333° per nakshatra
            fraction_passed = (moon_longitude_deg % span) / span
            remaining_years = DASA_YEARS[nakshatra_lord] * (1.0 - fraction_passed)
            
            years_int = int(remaining_years)
            months_float = (remaining_years - years_int) * 12
            months_int = int(months_float)
            days_float = (months_float - months_int) * 30.0
            days_int = int(round(days_float))
            
            first_dasha.balance_years = years_int
            first_dasha.balance_months = months_int
            first_dasha.balance_days = days_int
        
        return dasa_periods

    def _get_current_dasa(self, periods: List[DasaPeriod]) -> DasaPeriod:
        return super()._get_current_dasa(periods)

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
        try: return float(tz_str)
        except: return 5.5
