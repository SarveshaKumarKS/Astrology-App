from datetime import datetime, date, time, timedelta
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
    
    def generate_horoscope(self, birth_details: BirthDetails, language: str = "tamil") -> HoroscopeResult:
        """Generate complete horoscope using Vakkiam system"""
        
        # Parse timezone
        timezone_offset = self._parse_timezone(birth_details.timezone)
        
        # Calculate Julian Day
        jd = self.get_julian_day(
            birth_details.date_of_birth, 
            birth_details.time_of_birth, 
            timezone_offset
        )
        
        # Calculate planetary positions
        planetary_positions_raw = self.calculate_planetary_positions(jd)
        
        # Calculate ascendant
        ascendant_longitude = self.calculate_ascendant(
            jd, birth_details.latitude, birth_details.longitude
        )
        
        # Calculate house cusps
        house_cusps = self.calculate_houses(ascendant_longitude)
        
        # Process planetary positions
        planetary_positions = []
        for planet_name, position in planetary_positions_raw.items():
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
                retrograde=False  # TODO: Calculate retrograde status
            )
            planetary_positions.append(planet_pos)
        
        # Calculate charts
        rasi_chart = self._create_rasi_chart(planetary_positions_raw, ascendant_longitude)
        navamsa_positions = self.calculate_navamsa(planetary_positions_raw)
        navamsa_chart = self._create_navamsa_chart(navamsa_positions)
        
        # Calculate Dasa periods
        moon_position = planetary_positions_raw['Moon']
        dasa_periods = self._calculate_dasa_periods(moon_position['nakshatra'], birth_details.date_of_birth)
        current_dasa = self._get_current_dasa(dasa_periods)
        
        # Get ascendant and moon sign info
        ascendant_sign = self.get_sign_from_longitude(ascendant_longitude)
        moon_sign = moon_position['sign']
        moon_nakshatra = moon_position['nakshatra']
        
        # Create horoscope result
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
            special_yogas=[],  # TODO: Calculate yogas
            special_yogas_tamil=[]
        )
        
        return horoscope
    
    def check_compatibility(self, male_details: BirthDetails, female_details: BirthDetails, 
                          language: str = "tamil") -> CompatibilityResult:
        """Check marriage compatibility using Vakkiam system"""
        
        # Generate horoscopes for both
        male_horoscope = self.generate_horoscope(male_details, language)
        female_horoscope = self.generate_horoscope(female_details, language)
        
        # Calculate compatibility factors
        factors = []
        total_points = 0
        max_total_points = 36  # Standard Ashtakoota system
        
        # Implement Ashtakoota matching
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
        
        # Calculate percentage and overall rating
        percentage = (total_points / max_total_points) * 100
        overall_rating = self._get_overall_rating(percentage)
        overall_rating_tamil = self._get_overall_rating_tamil(percentage)
        
        # Dosha analysis
        dosha_analysis = self._analyze_doshas(male_horoscope, female_horoscope)
        
        # Generate recommendation
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
    
    def _parse_timezone(self, timezone_str: str) -> float:
        """Parse timezone string to offset in hours"""
        # Simple parsing - extend as needed
        if timezone_str.startswith('+'):
            return float(timezone_str[1:])
        elif timezone_str.startswith('-'):
            return -float(timezone_str[1:])
        elif timezone_str.upper() == 'IST':
            return 5.5
        else:
            return 0.0
    
    def _create_rasi_chart(self, positions: Dict, ascendant: float) -> Chart:
        """Create Rasi chart"""
        houses = {i: [] for i in range(1, 13)}
        houses_tamil = {i: [] for i in range(1, 13)}
        
        # Place ascendant
        asc_house = 1
        houses[asc_house].append("Asc")
        houses_tamil[asc_house].append("லக்")
        
        # Place planets
        for planet, position in positions.items():
            house = self.get_planet_house(position['longitude'], self.calculate_houses(ascendant))
            houses[house].append(planet)
            houses_tamil[house].append(PLANET_NAMES.get(planet, planet))
        
        return Chart(
            chart_type="rasi",
            houses=houses,
            houses_tamil=houses_tamil,
            ascendant_house=asc_house
        )
    
    def _create_navamsa_chart(self, navamsa_positions: Dict) -> Chart:
        """Create Navamsa chart"""
        houses = {i: [] for i in range(1, 13)}
        houses_tamil = {i: [] for i in range(1, 13)}
        
        for planet, position in navamsa_positions.items():
            house = position['sign']
            houses[house].append(planet)
            houses_tamil[house].append(PLANET_NAMES.get(planet, planet))
        
        return Chart(
            chart_type="navamsa",
            houses=houses,
            houses_tamil=houses_tamil,
            ascendant_house=1  # Will be calculated properly
        )
    
    def _calculate_dasa_periods(self, birth_nakshatra: int, birth_date: date) -> List[DasaPeriod]:
        """Calculate Vimshottari Dasa periods"""
        # Determine starting dasa lord based on birth nakshatra
        nakshatra_lords = {
            1: 'Ketu', 2: 'Venus', 3: 'Sun', 4: 'Moon', 5: 'Mars', 6: 'Rahu', 7: 'Jupiter', 8: 'Saturn', 9: 'Mercury',
            10: 'Ketu', 11: 'Venus', 12: 'Sun', 13: 'Moon', 14: 'Mars', 15: 'Rahu', 16: 'Jupiter', 17: 'Saturn', 18: 'Mercury',
            19: 'Ketu', 20: 'Venus', 21: 'Sun', 22: 'Moon', 23: 'Mars', 24: 'Rahu', 25: 'Jupiter', 26: 'Saturn', 27: 'Mercury'
        }
        
        starting_lord = nakshatra_lords[birth_nakshatra]
        starting_index = DASA_ORDER.index(starting_lord)
        
        dasa_periods = []
        current_date = birth_date
        
        # Generate 120 years of dasa periods
        for cycle in range(2):  # Two complete cycles
            for i in range(9):
                planet_index = (starting_index + i) % 9
                planet = DASA_ORDER[planet_index]
                years = DASA_YEARS[planet]
                
                end_date = current_date + timedelta(days=years * 365.25)
                
                dasa_period = DasaPeriod(
                    planet=planet,
                    planet_tamil=PLANET_NAMES[planet],
                    start_date=current_date,
                    end_date=end_date,
                    level="maha",
                    years=years,
                    months=int(years * 12),
                    days=int(years * 365.25)
                )
                
                dasa_periods.append(dasa_period)
                current_date = end_date
        
        return dasa_periods
    
    def _get_current_dasa(self, dasa_periods: List[DasaPeriod]) -> DasaPeriod:
        """Get current running dasa"""
        today = date.today()
        
        for dasa in dasa_periods:
            if dasa.start_date <= today <= dasa.end_date:
                return dasa
        
        # Return first dasa if none found
        return dasa_periods[0] if dasa_periods else None
    
    def _calculate_compatibility_factor(self, factor: str, male_horoscope: HoroscopeResult, 
                                      female_horoscope: HoroscopeResult) -> float:
        """Calculate points for a specific compatibility factor"""
        # Simplified implementation - extend with actual calculation logic
        if factor == 'varna':
            return 1.0  # Placeholder
        elif factor == 'vashya':
            return 1.5  # Placeholder
        elif factor == 'tara':
            return 2.0  # Placeholder
        elif factor == 'yoni':
            return 3.0  # Placeholder
        elif factor == 'graha_maitri':
            return 4.0  # Placeholder
        elif factor == 'gana':
            return 5.0  # Placeholder
        elif factor == 'bhakoot':
            return 6.0  # Placeholder
        elif factor == 'nadi':
            return 7.0  # Placeholder
        else:
            return 0.0
    
    def _get_factor_value(self, factor: str, horoscope: HoroscopeResult) -> str:
        """Get the value of a compatibility factor for a horoscope"""
        if factor == 'varna':
            return "Brahmin"  # Placeholder
        elif factor == 'gana':
            return "Deva"  # Placeholder
        else:
            return "TBD"  # Placeholder
    
    def _get_status_from_points(self, points: float, max_points: float) -> str:
        """Get status description from points"""
        percentage = (points / max_points) * 100
        if percentage >= 80:
            return "excellent"
        elif percentage >= 60:
            return "good"
        elif percentage >= 40:
            return "average"
        else:
            return "poor"
    
    def _get_status_tamil(self, points: float, max_points: float) -> str:
        """Get Tamil status description from points"""
        percentage = (points / max_points) * 100
        if percentage >= 80:
            return "மிகச்சிறந்த"
        elif percentage >= 60:
            return "நல்ல"
        elif percentage >= 40:
            return "சராசரி"
        else:
            return "குறைவு"
    
    def _get_overall_rating(self, percentage: float) -> str:
        """Get overall compatibility rating"""
        if percentage >= 75:
            return "excellent"
        elif percentage >= 60:
            return "good"
        elif percentage >= 45:
            return "average"
        else:
            return "poor"
    
    def _get_overall_rating_tamil(self, percentage: float) -> str:
        """Get Tamil overall compatibility rating"""
        if percentage >= 75:
            return "மிகச்சிறந்த பொருத்தம்"
        elif percentage >= 60:
            return "நல்ல பொருத்தம்"
        elif percentage >= 45:
            return "சராசரி பொருத்தம்"
        else:
            return "பொருத்தமில்லை"
    
    def _analyze_doshas(self, male_horoscope: HoroscopeResult, female_horoscope: HoroscopeResult) -> Dict:
        """Analyze doshas in both horoscopes"""
        return {
            "male_doshas": [],  # TODO: Implement dosha detection
            "female_doshas": [],
            "combined_effects": [],
            "remedies": []
        }
    
    def _generate_recommendation(self, percentage: float, dosha_analysis: Dict, language: str) -> str:
        """Generate compatibility recommendation"""
        if percentage >= 75:
            return "Highly compatible match. Proceed with confidence."
        elif percentage >= 60:
            return "Good compatibility. Minor adjustments may be needed."
        elif percentage >= 45:
            return "Average compatibility. Consider consulting an astrologer."
        else:
            return "Low compatibility. Careful consideration recommended."
    
    def _generate_recommendation_tamil(self, percentage: float, dosha_analysis: Dict) -> str:
        """Generate Tamil compatibility recommendation"""
        if percentage >= 75:
            return "மிகச்சிறந்த பொருத்தம். நம்பிக்கையுடன் முன்னேறலாம்."
        elif percentage >= 60:
            return "நல்ல பொருத்தம். சிறிய மாற்றங்கள் தேவைப்படலாம்."
        elif percentage >= 45:
            return "சராசரி பொருத்தம். ஜோதிடரை ஆலோசிக்கவும்."
        else:
            return "குறைவான பொருத்தம். கவனமாக பரிசீலிக்கவும்."
