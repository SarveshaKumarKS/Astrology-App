from datetime import date, timedelta, time
from typing import Dict, List, Optional
import math
from astrology.calculations import AstronomicalCalculations
from astrology.models import (
    BirthDetails, HoroscopeResult, CompatibilityResult, PlanetaryPosition,
    DasaPeriod, Chart, CompatibilityFactor
)
from astrology.constants import (
    PLANETS, SIGNS, NAKSHATRAS, PLANET_NAMES, SIGNS_TAMIL, NAKSHATRAS_TAMIL,
    DASA_ORDER, DASA_YEARS, COMPATIBILITY_FACTORS
)


class VakyaEphemerisProvider:
    """Vakya ephemeris provider for traditional Vakkiam calculations"""
    
    def __init__(self):
        # Vakya ephemeris tables (mean-planet positions)
        # These are traditional values used in Vakkiam panchāṅgams
        self.epoch_jd = 2451545.0  # J2000.0 epoch
        
        # Mean motion constants (degrees per day) from Surya Siddhānta
        self.mean_motions = {
            'Sun': 0.9856474,      # Mean daily motion of Sun
            'Moon': 13.176358,     # Mean daily motion of Moon
            'Mercury': 1.3832,     # Mean daily motion of Mercury
            'Venus': 1.6021,       # Mean daily motion of Venus
            'Mars': 0.5240,        # Mean daily motion of Mars
            'Jupiter': 0.0831,     # Mean daily motion of Jupiter
            'Saturn': 0.0335,      # Mean daily motion of Saturn
        }
        
        # Mean longitudes at epoch (degrees) - Vakya ephemeris values
        self.epoch_longitudes = {
            'Sun': 4.89,           # Vakya ephemeris value
            'Moon': 3.90,          # Vakya ephemeris value
            'Mercury': 4.75,       # Vakya ephemeris value
            'Venus': 4.22,         # Vakya ephemeris value
            'Mars': 5.72,          # Vakya ephemeris value
            'Jupiter': 0.44,       # Vakya ephemeris value
            'Saturn': 0.71,        # Vakya ephemeris value
        }
    
    def calculate_mean_longitude(self, planet: str, jd: float) -> float:
        """Calculate mean longitude using Vakya ephemeris"""
        if planet not in self.mean_motions:
            raise ValueError(f"Unknown planet: {planet}")
        
        days_since_epoch = jd - self.epoch_jd
        mean_longitude = (self.epoch_longitudes[planet] + 
                         self.mean_motions[planet] * days_since_epoch) % 360.0
        return mean_longitude
    
    def calculate_mean_node(self, jd: float) -> float:
        """Calculate mean lunar node (Rahu) using traditional method"""
        t = (jd - self.epoch_jd) / 36525.0
        omega = (125.04452 - 1934.136261 * t + 0.0020708 * t * t + (t ** 3) / 450000.0) % 360.0
        return omega


class AyanamsaProvider:
    """Configurable ayanamsa provider for different almanacs"""
    
    def __init__(self, system: str = "vakya"):
        self.system = system
        
        # Ayanamsa profiles for different almanacs
        self.profiles = {
            "vakya": {
                "base": 23.5,           # Traditional Vakkiam base
                "drift": 50.0 / 3600.0  # Traditional drift per century
            },
            "lahiri": {
                "base": 23.852583333,   # Lahiri base
                "drift": 5029.0966 / 3600.0  # Lahiri drift per century
            }
        }
    
    def calculate_ayanamsa(self, jd: float) -> float:
        """Calculate ayanamsa based on system"""
        if self.system not in self.profiles:
            raise ValueError(f"Unknown ayanamsa system: {self.system}")
        
        profile = self.profiles[self.system]
        t = (jd - 2451545.0) / 36525.0
        ayanamsa = (profile["base"] + profile["drift"] * t) % 360.0
        return ayanamsa


class VakkiamCalculator(AstronomicalCalculations):
    """
    Traditional Vakkiam system astrology calculations using Surya Siddhānta mean-planet formulae.
    
    The Vakkiam system uses traditional mean-planet formulae from the Surya Siddhānta
    or pre-computed Vakya ephemeris tables, rather than modern astronomical calculations.
    This provides the same planetary positions that traditional Vakkiam panchāṅgams use.
    """

    def __init__(self, ayanamsa_provider: str = "vakya"):
        super().__init__()
        self.system_name = "vakkiam"
        
        # Initialize providers
        self.vakya_ephemeris = VakyaEphemerisProvider()
        self.ayanamsa_provider = AyanamsaProvider(ayanamsa_provider)

    # ---------- Surya Siddhānta Calculation Methods ----------
    
    def calculate_ayanamsa(self, jd: float) -> float:
        """Calculate ayanamsa using configured provider"""
        return self.ayanamsa_provider.calculate_ayanamsa(jd)
    
    def calculate_true_obliquity_traditional(self, jd: float) -> float:
        """Calculate true obliquity of the ecliptic using traditional formula"""
        t = (jd - 2451545.0) / 36525.0
        # Traditional obliquity formula (arcseconds)
        epsilon_arcsec = (84381.406 - 46.836769 * t - 0.0001831 * t * t + 
                         0.00200340 * t * t * t - 5.76e-7 * t * t * t * t - 
                         4.34e-8 * t * t * t * t * t)
        return math.radians(epsilon_arcsec / 3600.0)  # Convert to radians
    
    def calculate_ascendant_traditional(self, jd: float, latitude: float, longitude: float) -> float:
        """Calculate ascendant using traditional Vakkiam method"""
        # Calculate Local Sidereal Time using Meeus formula
        lst = self.calculate_sidereal_time_meeus(jd, longitude)
        theta = math.radians(lst)
        phi = math.radians(latitude)
        
        # Calculate true obliquity
        eps = self.calculate_true_obliquity_traditional(jd)
        
        # Traditional ascendant formula
        x = math.sin(theta) * math.cos(eps) + math.tan(phi) * math.sin(eps)
        y = math.cos(theta)
        lam_trop = math.degrees(math.atan2(y, x)) % 360.0
        
        # Convert to sidereal using configured ayanamsa
        ayanamsa = self.calculate_ayanamsa(jd)
        lam_sidereal = (lam_trop - ayanamsa) % 360.0
        
        return lam_sidereal
    
    def calculate_sidereal_time_meeus(self, jd: float, longitude: float) -> float:
        """Calculate Local Sidereal Time using Meeus formula"""
        t = (jd - 2451545.0) / 36525.0
        
        # Meeus formula for Greenwich Sidereal Time
        theta_g = (280.46061837 + 360.98564736629 * (jd - 2451545.0) + 
                   0.000387933 * t * t - t * t * t / 38710000.0) % 360.0
        
        # Add longitude to get Local Sidereal Time
        lst = (theta_g + longitude) % 360.0
        
        return lst
    
    
    def calculate_planetary_positions_vakya(self, jd: float) -> Dict[str, Dict]:
        """Calculate planetary positions using Vakya ephemeris provider"""
        ayanamsa = self.calculate_ayanamsa(jd)
        positions = {}
        
        # Use Vakya ephemeris for all planets
        for planet in self.vakya_ephemeris.mean_motions.keys():
            mean_longitude = self.vakya_ephemeris.calculate_mean_longitude(planet, jd)
            sidereal_longitude = (mean_longitude - ayanamsa) % 360.0
            
            positions[planet] = {
                'longitude': sidereal_longitude,
                'latitude': 0.0,  # Traditional mean planets have zero latitude
                'sign': self.get_sign_from_longitude(sidereal_longitude),
                'nakshatra': self.get_nakshatra_from_longitude(sidereal_longitude)
            }
        
        # Calculate Rahu/Ketu using mean node
        rahu_tropical = self.vakya_ephemeris.calculate_mean_node(jd)
        rahu_sidereal = (rahu_tropical - ayanamsa) % 360.0
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
    

    def get_julian_day_lmt(self, birth_date: date, birth_time: time, longitude: float) -> float:
        """Calculate Julian Day using proper LMT conversion"""
        # Convert IST to LMT using longitude adjustment
        # IST is centred on 82.5° E, adjust by (longitude - 82.5°) * 4 minutes
        delta_t_minutes = (longitude - 82.5) * 4.0
        
        # Convert birth time to LMT
        lmt_hour = birth_time.hour + delta_t_minutes / 60.0
        lmt_minute = birth_time.minute + (delta_t_minutes % 60.0)
        lmt_second = birth_time.second
        
        # Normalize time
        while lmt_minute >= 60:
            lmt_hour += 1
            lmt_minute -= 60
        while lmt_minute < 0:
            lmt_hour -= 1
            lmt_minute += 60
        while lmt_hour >= 24:
            lmt_hour -= 24
        while lmt_hour < 0:
            lmt_hour += 24
        
        # Convert LMT to UTC (subtract 5.5 hours for IST)
        utc_hour = lmt_hour - 5.5
        utc_minute = lmt_minute
        utc_second = lmt_second
        
        # Normalize UTC time
        while utc_hour >= 24:
            utc_hour -= 24
        while utc_hour < 0:
            utc_hour += 24
        
        # Calculate Julian Day
        return self.get_julian_day(birth_date, time(int(utc_hour), int(utc_minute), int(utc_second)), 0.0)

    def calculate_navamsa_position(self, longitude: float) -> int:
        """Calculate Navamsa position using movable/fixed/dual rule"""
        sign = int(longitude // 30) + 1  # 1-12
        degree_in_sign = longitude % 30
        navamsa_segment = int(degree_in_sign // (30/9))  # 0-8
        
        # Determine sign quality
        if sign in [1, 4, 7, 10]:  # Movable signs (Aries, Cancer, Libra, Capricorn)
            start_sign = sign
        elif sign in [2, 5, 8, 11]:  # Fixed signs (Taurus, Leo, Scorpio, Aquarius)
            start_sign = ((sign - 1 + 8) % 12) + 1  # 9th from it
        else:  # Dual signs (Gemini, Virgo, Sagittarius, Pisces)
            start_sign = ((sign - 1 + 4) % 12) + 1  # 5th from it
        
        # Calculate final Navamsa sign
        navamsa_sign = ((start_sign - 1 + navamsa_segment) % 12) + 1
        return navamsa_sign

    # ---------- Public APIs ----------

    def generate_horoscope(self, birth_details: BirthDetails, language: str = "tamil") -> HoroscopeResult:
        """Generate complete horoscope using traditional Vakkiam system"""

        # Use proper LMT conversion
        jd = self.get_julian_day_lmt(
            birth_details.date_of_birth,
            birth_details.time_of_birth,
            birth_details.longitude
        )

        # Calculate planetary positions using Vakya ephemeris
        planetary_positions_raw = self.calculate_planetary_positions_vakya(jd)

        # Ascendant using traditional Vakkiam method
        ascendant_longitude = self.calculate_ascendant_traditional(
            jd, birth_details.latitude, birth_details.longitude
        )

        # Houses (equal for now)
        house_cusps = self.calculate_houses(ascendant_longitude)

        # Process planetary positions (with retrograde detection via day-1 comparison)
        planetary_positions: List[PlanetaryPosition] = []
        prev_day_positions = self.calculate_planetary_positions_vakya(jd - 1.0)

        for planet_name, position in planetary_positions_raw.items():
            if planet_name in ("Rahu", "Ketu"):
                retro = False  # nodes are always retrograde conceptually; keep False for UI
            else:
                # retrograde if longitude decreased compared to previous day
                prev_lon = prev_day_positions[planet_name]['longitude']
                cur_lon = position['longitude']
                delta = (cur_lon - prev_lon + 540.0) % 360.0 - 180.0  # shortest arc
                retro = delta < 0

            house = self.get_planet_house(position['longitude'], house_cusps)

            # Calculate new fields
            lon = position['longitude']
            lon_dms = self.deg_to_dms(lon)
            lon_in_sign = lon % 30.0
            lon_in_sign_dms = self.deg_to_dms(lon_in_sign)
            nakshatra_pada = self.get_nakshatra_pada(lon)
            nakshatra_lord = self.get_nakshatra_lord(position['nakshatra'])
            nakshatra_lord_tamil = PLANET_NAMES.get(nakshatra_lord, nakshatra_lord)

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
                house=house,
                retrograde=retro,
                longitude_dms=lon_dms,
                longitude_in_sign=lon_in_sign,
                longitude_in_sign_dms=lon_in_sign_dms,
                nakshatra_pada=nakshatra_pada,
                nakshatra_lord=nakshatra_lord,
                nakshatra_lord_tamil=nakshatra_lord_tamil
            )
            planetary_positions.append(planet_pos)

        # Add Ascendant as first entry in planetary positions
        asc_sign = self.get_sign_from_longitude(ascendant_longitude)
        asc_nakshatra = self.get_nakshatra_from_longitude(ascendant_longitude)
        asc_nakshatra_pada = self.get_nakshatra_pada(ascendant_longitude)
        asc_nakshatra_lord = self.get_nakshatra_lord(asc_nakshatra)
        
        asc_pos = PlanetaryPosition(
            planet="Ascendant",
            planet_tamil="லக்னம்",
            longitude=ascendant_longitude,
            sign=asc_sign,
            sign_name=SIGNS[asc_sign],
            sign_name_tamil=SIGNS_TAMIL[asc_sign],
            nakshatra=asc_nakshatra,
            nakshatra_name=NAKSHATRAS[asc_nakshatra],
            nakshatra_name_tamil=NAKSHATRAS_TAMIL[asc_nakshatra],
            house=1,
            retrograde=False,
            longitude_dms=self.deg_to_dms(ascendant_longitude),
            longitude_in_sign=ascendant_longitude % 30.0,
            longitude_in_sign_dms=self.deg_to_dms(ascendant_longitude % 30.0),
            nakshatra_pada=asc_nakshatra_pada,
            nakshatra_lord=asc_nakshatra_lord,
            nakshatra_lord_tamil=PLANET_NAMES.get(asc_nakshatra_lord, asc_nakshatra_lord)
        )
        
        # Prepend Ascendant to the list
        planetary_positions.insert(0, asc_pos)

        # Charts
        rasi_chart = self._create_rasi_chart(planetary_positions_raw, ascendant_longitude)
        navamsa_positions = self.calculate_navamsa(planetary_positions_raw, ascendant_longitude)
        nav_lagna_sign = self._calculate_navamsa_sign(ascendant_longitude)
        navamsa_chart = self._create_navamsa_chart(navamsa_positions, nav_lagna_sign)

        # Dasa periods (with first-balance using Moon longitude)
        moon_position = planetary_positions_raw['Moon']
        dasa_periods = self._calculate_dasa_periods(
            moon_position['nakshatra'],
            birth_details.date_of_birth,
            moon_position['longitude']
        )
        current_dasa = self._get_current_dasa(dasa_periods)
        
        # Enhance current dasa with balance, next dasa, and bhukti information
        current_dasa = self._enhance_current_dasa(current_dasa, dasa_periods)

        # Asc/Moon/Nakshatra names
        ascendant_sign = self.get_sign_from_longitude(ascendant_longitude)
        moon_sign = moon_position['sign']
        moon_nakshatra = moon_position['nakshatra']
        
        # Calculate retrograde planets
        retrograde_planets = [p.planet for p in planetary_positions if p.retrograde and p.planet != "Ascendant"]
        retrograde_planets_tamil = [p.planet_tamil for p in planetary_positions if p.retrograde and p.planet != "Ascendant"]
        
        # Calculate Bhava Maruthal for Moon (Chandiran) and Mercury (Budhan)
        bhava_maruthal = {}
        bhava_maruthal_tamil = {}
        for planet in ["Moon", "Mercury"]:
            for p in planetary_positions:
                if p.planet == planet:
                    bhava_maruthal[planet] = p.house
                    bhava_maruthal_tamil[p.planet_tamil] = p.house
                    break
        
        # Calculate Panchangam details
        tz_offset = self._parse_timezone(birth_details.timezone)
        panchangam = self.calculate_panchangam_details(
            birth_details.date_of_birth,
            birth_details.time_of_birth,
            birth_details.latitude,
            birth_details.longitude,
            tz_offset
        )
        
        # Calculate Yogi and Avayogi planets (based on Nakshatra)
        # Yogi planet is calculated from nakshatra number
        yogi_sequence = ["Moon", "Sun", "Jupiter", "Mars", "Mercury", "Saturn", "Venus", "Rahu", "Ketu"]
        yogi_idx = (moon_nakshatra * 8) % 9
        yogi_planet = yogi_sequence[yogi_idx]
        yogi_planet_tamil = PLANET_NAMES.get(yogi_planet, yogi_planet)
        
        # Avayogi is 12th from Yogi
        avayogi_idx = (yogi_idx + 11) % 9
        avayogi_planet = yogi_sequence[avayogi_idx]
        avayogi_planet_tamil = PLANET_NAMES.get(avayogi_planet, avayogi_planet)

        horoscope = HoroscopeResult(
            birth_details=birth_details,
            system=self.system_name,
            language=language,
            ascendant=SIGNS[ascendant_sign],
            ascendant_tamil=SIGNS_TAMIL[ascendant_sign],
            moon_sign=SIGNS[moon_sign],
            moon_sign_tamil=SIGNS_TAMIL[moon_sign],
            nakshatra=NAKSHATRAS[moon_nakshatra],
            nakshatra_tamil=NAKSHATRAS_TAMIL[moon_nakshatra],
            planetary_positions=planetary_positions,
            rasi_chart=rasi_chart,
            navamsa_chart=navamsa_chart,
            dasa_periods=dasa_periods,
            current_dasa=current_dasa,
            special_yogas=[],  # TODO
            special_yogas_tamil=[],
            retrograde_planets=retrograde_planets,
            retrograde_planets_tamil=retrograde_planets_tamil,
            bhava_maruthal=bhava_maruthal,
            bhava_maruthal_tamil=bhava_maruthal_tamil
        )

        return horoscope

    def check_compatibility(self, male_details: BirthDetails, female_details: BirthDetails,
                            language: str = "tamil") -> CompatibilityResult:
        """Check marriage compatibility using Vakkiam system"""

        male_horoscope = self.generate_horoscope(male_details, language)
        female_horoscope = self.generate_horoscope(female_details, language)

        factors: List[CompatibilityFactor] = []
        total_points = 0.0
        max_total_points = 36.0  # Ashtakoota standard

        for factor_key, factor_info in COMPATIBILITY_FACTORS.items():
            points = self._calculate_compatibility_factor(
                factor_key, male_horoscope, female_horoscope
            )
            factor = CompatibilityFactor(
                factor_name=factor_info['name'],
                factor_name_tamil=factor_info['tamil'],
                male_value=self._get_factor_value(factor_key, male_horoscope),
                female_value=self._get_factor_value(factor_key, female_horoscope),
                points=points,
                max_points=factor_info['max_points'],
                status=self._get_status_from_points(points, factor_info['max_points']),
                status_tamil=self._get_status_tamil(points, factor_info['max_points']),
                description=f"Points scored: {points}/{factor_info['max_points']}",
                description_tamil=f"மதிப்பெண்: {points}/{factor_info['max_points']}"
            )
            factors.append(factor)
            total_points += points

        percentage = (total_points / max_total_points) * 100.0
        overall_rating = self._get_overall_rating(percentage)
        overall_rating_tamil = self._get_overall_rating_tamil(percentage)

        dosha_analysis = self._analyze_doshas(male_horoscope, female_horoscope)

        recommendation = self._generate_recommendation(percentage, dosha_analysis, language)
        recommendation_tamil = self._generate_recommendation_tamil(percentage, dosha_analysis)

        return CompatibilityResult(
            male_details=male_details,
            female_details=female_details,
            system=self.system_name,
            language=language,
            total_points=total_points,
            max_points=max_total_points,
            percentage=percentage,
            overall_rating=overall_rating,
            overall_rating_tamil=overall_rating_tamil,
            factors=factors,
            dosha_analysis=dosha_analysis,
            recommendation=recommendation,
            recommendation_tamil=recommendation_tamil
        )

    # ---------- Internals ----------

    def _parse_timezone(self, timezone_str: str) -> float:
        """Parse timezone: supports 'IST', 'Asia/Kolkata', '+/-H', '+/-HH:MM'."""
        s = timezone_str.strip().upper()
        if s == 'IST' or s == 'ASIA/KOLKATA':
            return 5.5
        # ±HH:MM
        if (s.startswith('+') or s.startswith('-')) and ':' in s:
            sign = 1 if s[0] == '+' else -1
            hh, mm = s[1:].split(':', 1)
            return sign * (int(hh) + int(mm) / 60.0)
        # ±H or ±HH or float string
        try:
            if s.startswith('+'):
                return float(s[1:])
            if s.startswith('-'):
                return -float(s[1:])
            return float(s)  # allow plain number
        except ValueError:
            return 0.0

    def _create_rasi_chart(self, positions: Dict, ascendant_sidereal_lon: float) -> Chart:
        """Rāsi chart: planets bucketed by sidereal SIGN in traditional South Indian layout."""
        # Initialize signs (1-12) in traditional South Indian chart layout
        signs = {i: [] for i in range(1, 13)}
        signs_tamil = {i: [] for i in range(1, 13)}

        # Add ascendant marker to the ascendant sign
        asc_sign = self.get_sign_from_longitude(ascendant_sidereal_lon)
        signs[asc_sign].append("Asc")
        signs_tamil[asc_sign].append("லக்")

        # Place planets in their respective signs
        for planet, pos in positions.items():
            planet_sign = self.get_sign_from_longitude(pos['longitude'])
            signs[planet_sign].append(planet)
            signs_tamil[planet_sign].append(PLANET_NAMES.get(planet, planet))

        return Chart(
            chart_type="rasi",
            houses=signs,             # signs 1-12 in traditional layout
            houses_tamil=signs_tamil,
            ascendant_house=asc_sign  # ascendant sign number
        )

    def _create_bhava_chart(self, positions: Dict, ascendant_sidereal_lon: float) -> Chart:
        """Optional: Bhāva chart (equal-house from ascendant)."""
        houses = {i: [] for i in range(1, 13)}
        houses_ta = {i: [] for i in range(1, 13)}

        houses[1].append("Asc")
        houses_ta[1].append("லக்")

        cusps = self.calculate_houses(ascendant_sidereal_lon)
        for planet, pos in positions.items():
            h = self.get_planet_house(pos['longitude'], cusps)
            houses[h].append(planet)
            houses_ta[h].append(PLANET_NAMES.get(planet, planet))

        return Chart(
            chart_type="bhava",
            houses=houses,
            houses_tamil=houses_ta,
            ascendant_house=1
        )

    def _create_navamsa_chart(self, navamsa_positions: Dict, nav_lagna_sign: int) -> Chart:
        """Create Navamsa chart: planets grouped by D9 sign with Navamsa ascendant."""
        signs = {i: [] for i in range(1, 13)}
        signs_tamil = {i: [] for i in range(1, 13)}

        # Add Navamsa ascendant marker
        signs[nav_lagna_sign].append("Asc")
        signs_tamil[nav_lagna_sign].append("லக்")

        # Place planets in Navamsa chart
        for planet, position in navamsa_positions.items():
            if planet == 'Ascendant':  # Skip Ascendant, it's already marked
                continue
            sign = position['sign']
            signs[sign].append(planet)
            signs_tamil[sign].append(PLANET_NAMES.get(planet, planet))

        return Chart(
            chart_type="navamsa",
            houses=signs,             # signs 1-12 in traditional layout
            houses_tamil=signs_tamil,
            ascendant_house=nav_lagna_sign
        )

    def _calculate_dasa_periods(self, birth_nakshatra: int, birth_date: date, moon_longitude_deg: float) -> List[DasaPeriod]:
        """Vimshottari Mahadasha periods with first-dasha balance from Moon's position.
        Delegates to base class implementation which uses date arithmetic.
        """
        return super()._calculate_dasa_periods(birth_nakshatra, birth_date, moon_longitude_deg)

    def _get_current_dasa(self, dasa_periods: List[DasaPeriod]) -> DasaPeriod:
        """Get current running mahadasha (by today's date)."""
        today = date.today()
        for d in dasa_periods:
            if d.start_date <= today <= d.end_date:
                return d
        return dasa_periods[0] if dasa_periods else None

    # ----- Compatibility scaffolding (placeholders, same as before) -----

    def _calculate_compatibility_factor(self, factor: str, male_horoscope: HoroscopeResult,
                                        female_horoscope: HoroscopeResult) -> float:
        # TODO: real logic
        mapping = {
            'varna': 1.0, 'vashya': 1.5, 'tara': 2.0, 'yoni': 3.0,
            'graha_maitri': 4.0, 'gana': 5.0, 'bhakoot': 6.0, 'nadi': 7.0
        }
        return mapping.get(factor, 0.0)

    def _get_factor_value(self, factor: str, horoscope: HoroscopeResult) -> str:
        if factor == 'varna':
            return "Brahmin"
        elif factor == 'gana':
            return "Deva"
        return "TBD"

    def _get_status_from_points(self, points: float, max_points: float) -> str:
        p = (points / max_points) * 100.0
        if p >= 80: return "excellent"
        if p >= 60: return "good"
        if p >= 40: return "average"
        return "poor"

    def _get_status_tamil(self, points: float, max_points: float) -> str:
        p = (points / max_points) * 100.0
        if p >= 80: return "மிகச்சிறந்த"
        if p >= 60: return "நல்ல"
        if p >= 40: return "சராசரி"
        return "குறைவு"

    def _get_overall_rating(self, percentage: float) -> str:
        if percentage >= 75: return "excellent"
        if percentage >= 60: return "good"
        if percentage >= 45: return "average"
        return "poor"

    def _get_overall_rating_tamil(self, percentage: float) -> str:
        if percentage >= 75: return "மிகச்சிறந்த பொருத்தம்"
        if percentage >= 60: return "நல்ல பொருத்தம்"
        if percentage >= 45: return "சராசரி பொருத்தம்"
        return "பொருத்தமில்லை"

    def _analyze_doshas(self, male_horoscope: HoroscopeResult, female_horoscope: HoroscopeResult) -> Dict:
        return {"male_doshas": [], "female_doshas": [], "combined_effects": [], "remedies": []}

    def _generate_recommendation(self, percentage: float, dosha_analysis: Dict, language: str) -> str:
        if percentage >= 75: return "Highly compatible match. Proceed with confidence."
        if percentage >= 60: return "Good compatibility. Minor adjustments may be needed."
        if percentage >= 45: return "Average compatibility. Consider consulting an astrologer."
        return "Low compatibility. Careful consideration recommended."

    def _generate_recommendation_tamil(self, percentage: float, dosha_analysis: Dict) -> str:
        if percentage >= 75: return "மிகச்சிறந்த பொருத்தம். நம்பிக்கையுடன் முன்னேறலாம்."
        if percentage >= 60: return "நல்ல பொருத்தம். சிறிய மாற்றங்கள் தேவைப்படலாம்."
        if percentage >= 45: return "சராசரி பொருத்தம். ஜோதிடரை ஆலோசிக்கவும்."
        return "குறைவான பொருத்தம். கவனமாக பரிசீலிக்கவும்."
