from datetime import date, timedelta
from typing import Dict, List
from astrology.calculations import AstronomicalCalculations
from astrology.models import (
    BirthDetails, HoroscopeResult, CompatibilityResult, PlanetaryPosition,
    DasaPeriod, Chart, CompatibilityFactor
)
from astrology.constants import (
    PLANETS, SIGNS, NAKSHATRAS, PLANET_NAMES, SIGNS_TAMIL, NAKSHATRAS_TAMIL,
    DASA_ORDER, DASA_YEARS, COMPATIBILITY_FACTORS
)

class VakkiamCalculator(AstronomicalCalculations):
    """Vakkiam system astrology calculations"""

    def __init__(self):
        super().__init__()
        self.system_name = "vakkiam"

    # ---------- Public APIs ----------

    def generate_horoscope(self, birth_details: BirthDetails, language: str = "tamil") -> HoroscopeResult:
        """Generate complete horoscope using Vakkiam system"""

        # Parse timezone
        timezone_offset = self._parse_timezone(birth_details.timezone)

        # Calculate Julian Day (UTC)
        jd = self.get_julian_day(
            birth_details.date_of_birth,
            birth_details.time_of_birth,
            timezone_offset
        )

        # Calculate planetary positions (sidereal)
        planetary_positions_raw = self.calculate_planetary_positions(jd)

        # Ascendant
        ascendant_longitude = self.calculate_ascendant(
            jd, birth_details.latitude, birth_details.longitude
        )

        # Houses (equal for now)
        house_cusps = self.calculate_houses(ascendant_longitude)

        # Process planetary positions (with retrograde detection via day-1 comparison)
        planetary_positions: List[PlanetaryPosition] = []
        prev_day_positions = self.calculate_planetary_positions(jd - 1.0)

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

            planet_pos = PlanetaryPosition(
                planet=planet_name,
                planet_tamil=PLANET_NAMES.get(planet_name, planet_name),
                longitude=position['longitude'],
                sign=position['sign'],
                sign_name=SIGNS[position['sign']],
                sign_name_tamil=SIGNS_TAMIL[position['sign']],
                nakshatra=position['nakshatra'],
                nakshatra_name=NAKSHATRAS[position['nakshatra']],
                nakshatra_name_tamil=NAKSHATRAS_TAMIL[position['nakshatra']],
                house=house,
                retrograde=retro
            )
            planetary_positions.append(planet_pos)

        # Charts
        rasi_chart = self._create_rasi_chart(planetary_positions_raw, ascendant_longitude)
        navamsa_positions = self.calculate_navamsa(planetary_positions_raw, ascendant_longitude, jd)
        navamsa_chart = self._create_navamsa_chart(navamsa_positions, ascendant_longitude)

        # Dasa periods (with first-balance using Moon longitude)
        moon_position = planetary_positions_raw['Moon']
        dasa_periods = self._calculate_dasa_periods(
            moon_position['nakshatra'],
            birth_details.date_of_birth,
            moon_position['longitude']
        )
        current_dasa = self._get_current_dasa(dasa_periods)

        # Asc/Moon/Nakshatra names
        ascendant_sign = self.get_sign_from_longitude(ascendant_longitude)
        moon_sign = moon_position['sign']
        moon_nakshatra = moon_position['nakshatra']

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
            special_yogas_tamil=[]
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
        """Parse timezone: supports 'IST', '+/-H', '+/-HH:MM'."""
        s = timezone_str.strip().upper()
        if s == 'IST':
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
        """Rāsi chart: planets bucketed by sidereal SIGN (not by house)."""
        signs = {i: [] for i in range(1, 13)}
        signs_ta = {i: [] for i in range(1, 13)}

        # Ascendant SIGN marker
        asc_sign = self.get_sign_from_longitude(ascendant_sidereal_lon)
        signs[asc_sign].append("Asc")
        signs_ta[asc_sign].append("லக்")

        for planet, pos in positions.items():
            s = self.get_sign_from_longitude(pos['longitude'])
            signs[s].append(planet)
            signs_ta[s].append(PLANET_NAMES.get(planet, planet))

        return Chart(
            chart_type="rasi",
            houses=signs,             # here 'houses' means 12 rāsi cells
            houses_tamil=signs_ta,
            ascendant_house=asc_sign  # ascendant SIGN index 1..12
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

    def _create_navamsa_chart(self, navamsa_positions: Dict, ascendant_longitude: float = None) -> Chart:
        """Create Navamsa chart: planets grouped by D9 sign, including navamsa ascendant."""
        houses = {i: [] for i in range(1, 13)}
        houses_tamil = {i: [] for i in range(1, 13)}
        
        navamsa_asc_sign = 1  # default

        for planet, position in navamsa_positions.items():
            house = position['sign']
            if planet == 'Ascendant':
                # Mark navamsa ascendant
                houses[house].append("Asc")
                houses_tamil[house].append("லக்")
                navamsa_asc_sign = house
            else:
                houses[house].append(planet)
                houses_tamil[house].append(PLANET_NAMES.get(planet, planet))

        return Chart(
            chart_type="navamsa",
            houses=houses,
            houses_tamil=houses_tamil,
            ascendant_house=navamsa_asc_sign
        )

    def _calculate_dasa_periods(self, birth_nakshatra: int, birth_date: date, moon_longitude_deg: float) -> List[DasaPeriod]:
        """Vimshottari Mahadasha periods with first-dasha balance from Moon's position."""
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

        dasa_periods: List[DasaPeriod] = []
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
