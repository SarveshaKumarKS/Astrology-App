from datetime import date
from typing import Dict, List
import base64
from astrology.calculations import AstronomicalCalculations
from astrology.models import (
    BirthDetails, HoroscopeResult, CompatibilityResult, PlanetaryPosition,
    DasaPeriod, Chart, CompatibilityFactor
)
from astrology.constants import (
    PLANETS, SIGNS, NAKSHATRAS, PLANET_NAMES, SIGNS_TAMIL, NAKSHATRAS_TAMIL,
    DASA_ORDER, DASA_YEARS, COMPATIBILITY_FACTORS
)
from astrology.utils_chart import render_south_indian_chart

class ThirukkanithamCalculator(AstronomicalCalculations):
    """Thirukkanitham system astrology calculations (shares astronomy core)."""

    def __init__(self):
        super().__init__()
        self.system_name = "thirukkanitham"

    # At present we mirror Vakkiam's pipeline but keep hooks to diverge later.

    def generate_horoscope(self, birth_details: BirthDetails, language: str = "tamil") -> HoroscopeResult:
        tz = self._parse_timezone(birth_details.timezone)
        jd = self.get_julian_day(birth_details.date_of_birth, birth_details.time_of_birth, tz)

        # Drik / Thirukkanitham differences:
        # Use topocentric positions (true node included)
        positions = self.calculate_planetary_positions_topocentric(jd, birth_details.latitude, birth_details.longitude)
        # Use true obliquity for ascendant
        ascendant = self.calculate_ascendant_true_obliquity(jd, birth_details.latitude, birth_details.longitude)
        cusps = self.calculate_houses(ascendant)

        # Retrograde status via day-1 delta (also topocentric for consistency)
        prev_positions = self.calculate_planetary_positions_topocentric(jd - 1.0, birth_details.latitude, birth_details.longitude)
        planet_list: List[PlanetaryPosition] = []
        for name, pos in positions.items():
            if name in ("Rahu", "Ketu"):
                retro = False
            else:
                prev_lon = prev_positions[name]['longitude']
                cur_lon = pos['longitude']
                delta = (cur_lon - prev_lon + 540.0) % 360.0 - 180.0
                retro = delta < 0

            planet_list.append(PlanetaryPosition(
                planet=name,
                planet_tamil=PLANET_NAMES.get(name, name),
                longitude=pos['longitude'],
                sign=pos['sign'],
                sign_name=SIGNS[pos['sign']],
                sign_name_tamil=SIGNS_TAMIL[pos['sign']],
                nakshatra=pos['nakshatra'],
                nakshatra_name=NAKSHATRAS[pos['nakshatra']],
                nakshatra_name_tamil=NAKSHATRAS_TAMIL[pos['nakshatra']],
                house=self.get_planet_house(pos['longitude'], cusps),
                retrograde=retro
            ))

        rasi_chart = self._create_rasi_chart(positions, ascendant)
        nav_positions = self.calculate_navamsa(positions)
        nav_chart = self._create_navamsa_chart(nav_positions)

        moon = positions['Moon']
        dasa = self._calculate_dasa_periods(moon['nakshatra'], birth_details.date_of_birth, moon['longitude'])
        current = self._get_current_dasa(dasa)

        asc_sign = self.get_sign_from_longitude(ascendant)
        moon_sign = moon['sign']
        moon_nk = moon['nakshatra']

        return HoroscopeResult(
            birth_details=birth_details,
            system=self.system_name,
            language=language,
            ascendant=SIGNS[asc_sign],
            ascendant_tamil=SIGNS_TAMIL[asc_sign],
            moon_sign=SIGNS[moon_sign],
            moon_sign_tamil=SIGNS_TAMIL[moon_sign],
            nakshatra=NAKSHATRAS[moon_nk],
            nakshatra_tamil=NAKSHATRAS_TAMIL[moon_nk],
            planetary_positions=planet_list,
            rasi_chart=rasi_chart,
            navamsa_chart=nav_chart,
            dasa_periods=dasa,
            current_dasa=current,
            special_yogas=[], special_yogas_tamil=[]
        )

    # These helpers mirror Vakkiam; override later if Thirukkanitham has distinct rules.

    def _parse_timezone(self, s: str) -> float:
        s = s.strip().upper()
        if s == 'IST':
            return 5.5
        if (s.startswith('+') or s.startswith('-')) and ':' in s:
            sign = 1 if s[0] == '+' else -1
            hh, mm = s[1:].split(':', 1)
            return sign * (int(hh) + int(mm)/60.0)
        try:
            if s.startswith('+'):
                return float(s[1:])
            if s.startswith('-'):
                return -float(s[1:])
            return float(s)
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

        # Generate South Indian chart image
        chart_image_bytes = render_south_indian_chart(
            houses=signs_ta,  # Use Tamil labels for the chart
            title="ராசி",
            tamil=True
        )
        chart_image_base64 = base64.b64encode(chart_image_bytes).decode('utf-8')

        return Chart(
            chart_type="rasi",
            houses=signs,             # here 'houses' means 12 rāsi cells
            houses_tamil=signs_ta,
            ascendant_house=asc_sign,  # ascendant SIGN index 1..12
            image_base64=chart_image_base64
        )

    def _create_whole_sign_bhava_chart(self, positions: Dict, ascendant_sidereal_lon: float) -> Chart:
        """Whole-sign houses for Thirukkanitham bhava view."""
        asc_sign = self.get_sign_from_longitude(ascendant_sidereal_lon)
        houses = {i: [] for i in range(1, 13)}
        houses_ta = {i: [] for i in range(1, 13)}
        houses[1].append("Asc")
        houses_ta[1].append("லக்")

        for planet, pos in positions.items():
            s = self.get_sign_from_longitude(pos['longitude'])
            # House index relative to ascendant sign
            idx = ((s - asc_sign) % 12) + 1
            houses[idx].append(planet)
            houses_ta[idx].append(PLANET_NAMES.get(planet, planet))

        return Chart(
            chart_type="bhava_whole_sign",
            houses=houses,
            houses_tamil=houses_ta,
            ascendant_house=1
        )

    def _create_navamsa_chart(self, nav: Dict) -> Chart:
        houses = {i: [] for i in range(1, 13)}
        houses_tamil = {i: [] for i in range(1, 13)}
        for planet, pos in nav.items():
            houses[pos['sign']].append(planet)
            houses_tamil[pos['sign']].append(PLANET_NAMES.get(planet, planet))
        return Chart(chart_type="navamsa", houses=houses, houses_tamil=houses_tamil, ascendant_house=1)

    def _calculate_dasa_periods(self, birth_nakshatra: int, birth_date: date, moon_longitude_deg: float) -> List[DasaPeriod]:
        # delegate to Vakkiam implementation (identical logic)
        return super()._calculate_dasa_periods(birth_nakshatra, birth_date, moon_longitude_deg)

    def _get_current_dasa(self, periods: List[DasaPeriod]) -> DasaPeriod:
        return super()._get_current_dasa(periods)

    # Compatibility reuses Vakkiam placeholders for now
    def check_compatibility(self, male_details: BirthDetails, female_details: BirthDetails, language: str = "tamil") -> CompatibilityResult:
        # Simple reuse of Vakkiam's scoring placeholders
        factors: List[CompatibilityFactor] = []
        total = 0.0
        max_total = 36.0
        for k, info in COMPATIBILITY_FACTORS.items():
            pts = 0.0
            if k == 'varna':
                pts = 1.0
            elif k == 'vashya':
                pts = 1.5
            elif k == 'tara':
                pts = 2.0
            elif k == 'yoni':
                pts = 3.0
            elif k == 'graha_maitri':
                pts = 4.0
            elif k == 'gana':
                pts = 5.0
            elif k == 'bhakoot':
                pts = 6.0
            elif k == 'nadi':
                pts = 7.0
            factors.append(CompatibilityFactor(
                factor_name=info['name'],
                factor_name_tamil=info['tamil'],
                male_value="TBD", female_value="TBD",
                points=pts, max_points=info['max_points'],
                status="good", status_tamil="நல்ல",
                description=f"Points scored: {pts}/{info['max_points']}",
                description_tamil=f"மதிப்பெண்: {pts}/{info['max_points']}"
            ))
            total += pts
        pct = (total / max_total) * 100.0
        overall = "excellent" if pct >= 75 else "good" if pct >= 60 else "average" if pct >= 45 else "poor"
        overall_ta = "மிகச்சிறந்த பொருத்தம்" if pct >= 75 else "நல்ல பொருத்தம்" if pct >= 60 else "சராசரி பொருத்தம்" if pct >= 45 else "பொருத்தமில்லை"
        return CompatibilityResult(
            male_details=male_details, female_details=female_details, system=self.system_name, language=language,
            total_points=total, max_points=max_total, percentage=pct,
            overall_rating=overall, overall_rating_tamil=overall_ta,
            factors=factors, dosha_analysis={"male_doshas": [], "female_doshas": [], "combined_effects": [], "remedies": []},
            recommendation="Good compatibility.", recommendation_tamil="நல்ல பொருத்தம்."
        )
