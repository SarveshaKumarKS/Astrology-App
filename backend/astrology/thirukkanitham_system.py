from datetime import datetime, date, time, timedelta
from typing import Dict, List
from astrology.calculations import AstronomicalCalculations
from astrology.models import (
    BirthDetails, HoroscopeResult, CompatibilityResult, PanchangamDetails
)
from astrology.vakkiam_system import VakkiamCalculator
from astrology.constants import (
    TITHI_NAMES, TITHI_NAMES_TAMIL, YOGA_NAMES, KARANA_NAMES,
    SIGNS, SIGNS_TAMIL, NAKSHATRAS, NAKSHATRAS_TAMIL
)

class ThirukkanithamCalculator(VakkiamCalculator):
    """Thirukkanitham system astrology calculations"""
    
    def __init__(self):
        super().__init__()
        self.system_name = "thirukkanitham"
        # Thirukkanitham uses the same sidereal calculations as base class
        # No additional ayanamsa offset needed since base class now handles sidereal conversion
    
    def generate_horoscope(self, birth_details: BirthDetails, language: str = "tamil") -> HoroscopeResult:
        """Generate horoscope using Thirukkanitham system"""
        # Use parent method but apply Thirukkanitham corrections
        horoscope = super().generate_horoscope(birth_details, language)
        
        # Apply Thirukkanitham specific corrections
        horoscope = self._apply_thirukkanitham_corrections(horoscope)
        horoscope.system = self.system_name
        
        return horoscope
    
    def check_compatibility(self, male_details: BirthDetails, female_details: BirthDetails, 
                          language: str = "tamil") -> CompatibilityResult:
        """Check compatibility using Thirukkanitham system"""
        # Use parent method but apply Thirukkanitham specific matching
        compatibility = super().check_compatibility(male_details, female_details, language)
        
        # Apply Thirukkanitham specific compatibility rules
        compatibility = self._apply_thirukkanitham_compatibility_rules(compatibility)
        compatibility.system = self.system_name
        
        return compatibility
    
    def get_daily_panchangam(self, target_date: date, language: str = "tamil") -> PanchangamDetails:
        """Get daily Panchangam details for Thirukkanitham system"""
        # Calculate panchangam elements for the given date
        
        # Create a dummy birth time for calculations (sunrise)
        birth_time = time(6, 0)  # 6 AM
        jd = self.get_julian_day(target_date, birth_time, 5.5)  # IST timezone
        
        # Calculate lunar day (Tithi)
        tithi = self._calculate_tithi(jd)
        
        # Calculate nakshatra
        moon_positions = self.calculate_planetary_positions(jd)
        moon_nakshatra = moon_positions['Moon']['nakshatra']
        
        # Calculate yoga
        yoga = self._calculate_yoga(jd)
        
        # Calculate karana
        karana = self._calculate_karana(jd)
        
        # Calculate important times
        sunrise, sunset = self._calculate_sun_times(jd, 13.0833, 80.2833)  # Chennai coordinates as default
        moonrise, moonset = self._calculate_moon_times(jd, 13.0833, 80.2833)
        
        # Calculate inauspicious times
        rahu_kalam = self._calculate_rahu_kalam(sunrise, sunset, target_date)
        yama_gandam = self._calculate_yama_gandam(sunrise, sunset, target_date)
        gulika_kalam = self._calculate_gulika_kalam(sunrise, sunset, target_date)
        
        # Calculate auspicious times
        abhijit_muhurta = self._calculate_abhijit_muhurta(sunrise, sunset)
        
        return PanchangamDetails(
            date=target_date,
            tithi=TITHI_NAMES.get(tithi, f"Tithi {tithi}"),
            tithi_tamil=TITHI_NAMES_TAMIL.get(tithi, f"திதி {tithi}"),
            nakshatra=self._get_nakshatra_name(moon_nakshatra),
            nakshatra_tamil=self._get_nakshatra_name_tamil(moon_nakshatra),
            yoga=YOGA_NAMES.get(yoga, f"Yoga {yoga}"),
            yoga_tamil=f"யோகம் {yoga}",
            karana=KARANA_NAMES.get(karana, f"Karana {karana}"),
            karana_tamil=f"கரணம் {karana}",
            sunrise=sunrise,
            sunset=sunset,
            moonrise=moonrise,
            moonset=moonset,
            rahu_kalam=rahu_kalam,
            yama_gandam=yama_gandam,
            gulika_kalam=gulika_kalam,
            abhijit_muhurta=abhijit_muhurta,
            auspicious_times=self._get_auspicious_times(),
            inauspicious_times=self._get_inauspicious_times()
        )
    
    def _apply_thirukkanitham_corrections(self, horoscope: HoroscopeResult) -> HoroscopeResult:
        """Apply Thirukkanitham specific corrections to horoscope"""
        # No additional ayanamsa correction needed since base class now handles sidereal conversion
        # Thirukkanitham uses the same sidereal positions as standard Indian astrology
        
        # Apply any Thirukkanitham-specific interpretations or formatting here
        # For now, just ensure Tamil names are properly set
        for planet_pos in horoscope.planetary_positions:
            # Ensure Tamil names are set
            planet_pos.sign_name_tamil = SIGNS_TAMIL[planet_pos.sign]
            planet_pos.nakshatra_name_tamil = NAKSHATRAS_TAMIL[planet_pos.nakshatra]
        
        return horoscope
    
    def _apply_thirukkanitham_compatibility_rules(self, compatibility: CompatibilityResult) -> CompatibilityResult:
        """Apply Thirukkanitham specific compatibility rules"""
        # Thirukkanitham may have different weightage for compatibility factors
        # This is a placeholder for specific rules
        
        # Adjust scoring based on Thirukkanitham traditions
        adjusted_points = compatibility.total_points * 1.1  # Example adjustment
        compatibility.total_points = min(adjusted_points, compatibility.max_points)
        compatibility.percentage = (compatibility.total_points / compatibility.max_points) * 100
        
        return compatibility
    
    def _calculate_tithi(self, jd: float) -> int:
        """Calculate Tithi (lunar day)"""
        # Simplified tithi calculation
        # In reality, this requires complex calculations of sun and moon longitudes
        
        positions = self.calculate_planetary_positions(jd)
        sun_longitude = positions['Sun']['longitude']
        moon_longitude = positions['Moon']['longitude']
        
        # Tithi is based on the difference between moon and sun longitudes
        longitude_diff = (moon_longitude - sun_longitude) % 360
        tithi = int(longitude_diff / 12) + 1
        
        return min(tithi, 15)  # Tithi ranges from 1-15
    
    def _calculate_yoga(self, jd: float) -> int:
        """Calculate Yoga"""
        positions = self.calculate_planetary_positions(jd)
        sun_longitude = positions['Sun']['longitude']
        moon_longitude = positions['Moon']['longitude']
        
        # Yoga calculation based on sum of sun and moon longitudes
        yoga_value = (sun_longitude + moon_longitude) % 360
        yoga = int(yoga_value / (360/27)) + 1
        
        return min(yoga, 27)
    
    def _calculate_karana(self, jd: float) -> int:
        """Calculate Karana"""
        tithi = self._calculate_tithi(jd)
        
        # Karana is half of tithi
        if tithi <= 14:
            karana = ((tithi - 1) * 2 + 1) % 7 + 1
        else:
            karana = 8  # Fixed karanas for 30th tithi
        
        return karana
    
    def _calculate_sun_times(self, jd: float, latitude: float, longitude: float) -> tuple:
        """Calculate sunrise and sunset times"""
        # Simplified calculation - in practice, use more accurate algorithms
        sunrise = time(6, 0)  # Placeholder
        sunset = time(18, 0)  # Placeholder
        return sunrise, sunset
    
    def _calculate_moon_times(self, jd: float, latitude: float, longitude: float) -> tuple:
        """Calculate moonrise and moonset times"""
        # Placeholder implementation
        moonrise = time(8, 0)
        moonset = time(20, 0)
        return moonrise, moonset
    
    def _calculate_rahu_kalam(self, sunrise: time, sunset: time, date: date) -> Dict[str, time]:
        """Calculate Rahu Kalam timing"""
        # Rahu Kalam varies by day of week
        day_of_week = date.weekday()  # 0 = Monday
        
        # Calculate day duration
        sunrise_minutes = sunrise.hour * 60 + sunrise.minute
        sunset_minutes = sunset.hour * 60 + sunset.minute
        day_duration = sunset_minutes - sunrise_minutes
        
        # Rahu Kalam periods (as fraction of day duration)
        rahu_periods = {
            0: (7/8, 1),      # Monday: 7th period
            1: (1/8, 2/8),    # Tuesday: 1st period  
            2: (6/8, 7/8),    # Wednesday: 6th period
            3: (3/8, 4/8),    # Thursday: 3rd period
            4: (5/8, 6/8),    # Friday: 5th period
            5: (4/8, 5/8),    # Saturday: 4th period
            6: (2/8, 3/8),    # Sunday: 2nd period
        }
        
        start_fraction, end_fraction = rahu_periods[day_of_week]
        
        start_minutes = sunrise_minutes + (day_duration * start_fraction)
        end_minutes = sunrise_minutes + (day_duration * end_fraction)
        
        start_time = time(int(start_minutes // 60), int(start_minutes % 60))
        end_time = time(int(end_minutes // 60), int(end_minutes % 60))
        
        return {"start": start_time, "end": end_time}
    
    def _calculate_yama_gandam(self, sunrise: time, sunset: time, date: date) -> Dict[str, time]:
        """Calculate Yama Gandam timing"""
        # Similar to Rahu Kalam but different periods
        day_of_week = date.weekday()
        
        sunrise_minutes = sunrise.hour * 60 + sunrise.minute
        sunset_minutes = sunset.hour * 60 + sunset.minute
        day_duration = sunset_minutes - sunrise_minutes
        
        yama_periods = {
            0: (4/8, 5/8),    # Monday
            1: (6/8, 7/8),    # Tuesday
            2: (2/8, 3/8),    # Wednesday
            3: (5/8, 6/8),    # Thursday
            4: (3/8, 4/8),    # Friday
            5: (1/8, 2/8),    # Saturday
            6: (7/8, 1),      # Sunday
        }
        
        start_fraction, end_fraction = yama_periods[day_of_week]
        
        start_minutes = sunrise_minutes + (day_duration * start_fraction)
        end_minutes = sunrise_minutes + (day_duration * end_fraction)
        
        start_time = time(int(start_minutes // 60), int(start_minutes % 60))
        end_time = time(int(end_minutes // 60), int(end_minutes % 60))
        
        return {"start": start_time, "end": end_time}
    
    def _calculate_gulika_kalam(self, sunrise: time, sunset: time, date: date) -> Dict[str, time]:
        """Calculate Gulika Kalam timing"""
        # Similar to Rahu Kalam and Yama Gandam
        day_of_week = date.weekday()
        
        sunrise_minutes = sunrise.hour * 60 + sunrise.minute
        sunset_minutes = sunset.hour * 60 + sunset.minute
        day_duration = sunset_minutes - sunrise_minutes
        
        gulika_periods = {
            0: (6/8, 7/8),    # Monday
            1: (5/8, 6/8),    # Tuesday  
            2: (4/8, 5/8),    # Wednesday
            3: (3/8, 4/8),    # Thursday
            4: (2/8, 3/8),    # Friday
            5: (7/8, 1),      # Saturday
            6: (1/8, 2/8),    # Sunday
        }
        
        start_fraction, end_fraction = gulika_periods[day_of_week]
        
        start_minutes = sunrise_minutes + (day_duration * start_fraction)
        end_minutes = sunrise_minutes + (day_duration * end_fraction)
        
        start_time = time(int(start_minutes // 60), int(start_minutes % 60))
        end_time = time(int(end_minutes // 60), int(end_minutes % 60))
        
        return {"start": start_time, "end": end_time}
    
    def _calculate_abhijit_muhurta(self, sunrise: time, sunset: time) -> Dict[str, time]:
        """Calculate Abhijit Muhurta (auspicious time)"""
        sunrise_minutes = sunrise.hour * 60 + sunrise.minute
        sunset_minutes = sunset.hour * 60 + sunset.minute
        
        # Abhijit is around midday
        midday_minutes = (sunrise_minutes + sunset_minutes) / 2
        
        # 48 minutes duration (24 minutes before and after midday)
        start_minutes = midday_minutes - 24
        end_minutes = midday_minutes + 24
        
        start_time = time(int(start_minutes // 60), int(start_minutes % 60))
        end_time = time(int(end_minutes // 60), int(end_minutes % 60))
        
        return {"start": start_time, "end": end_time}
    
    def _get_nakshatra_name(self, nakshatra_num: int) -> str:
        """Get nakshatra name in English"""
        return NAKSHATRAS.get(nakshatra_num, f"Nakshatra {nakshatra_num}")
    
    def _get_nakshatra_name_tamil(self, nakshatra_num: int) -> str:
        """Get nakshatra name in Tamil"""
        from astrology.constants import NAKSHATRAS_TAMIL
        return NAKSHATRAS_TAMIL.get(nakshatra_num, f"நட்சத்திரம் {nakshatra_num}")
    
    def _get_auspicious_times(self) -> List[Dict[str, any]]:
        """Get list of auspicious times"""
        return [
            {"name": "Abhijit Muhurta", "tamil": "அபிஜித் முகூர்த்தம்", "description": "Midday auspicious time"}
        ]
    
    def _get_inauspicious_times(self) -> List[Dict[str, any]]:
        """Get list of inauspicious times"""
        return [
            {"name": "Rahu Kalam", "tamil": "ராகு காலம்", "description": "Inauspicious period ruled by Rahu"},
            {"name": "Yama Gandam", "tamil": "யம கண்டம்", "description": "Period ruled by Yama"},
            {"name": "Gulika Kalam", "tamil": "குளிக காலம்", "description": "Period ruled by Gulika"}
        ]
