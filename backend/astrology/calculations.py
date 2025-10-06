import math
from datetime import datetime, date, time, timedelta
from typing import Dict, List, Tuple
import ephem
from astrology.constants import (
    PLANETS, SIGNS, NAKSHATRAS, HOUSES,
    PLANETS_TAMIL, SIGNS_TAMIL, NAKSHATRAS_TAMIL
)

class AstronomicalCalculations:
    """Base class for astronomical calculations used by both systems"""
    
    def __init__(self):
        self.planets = {
            'Sun': ephem.Sun(),
            'Moon': ephem.Moon(),
            'Mercury': ephem.Mercury(),
            'Venus': ephem.Venus(),
            'Mars': ephem.Mars(),
            'Jupiter': ephem.Jupiter(),
            'Saturn': ephem.Saturn(),
            'Rahu': None,  # Calculated separately
            'Ketu': None   # Calculated separately
        }
    
    def get_julian_day(self, birth_date: date, birth_time: time, timezone_offset: float) -> float:
        """Calculate Julian Day Number"""
        dt = datetime.combine(birth_date, birth_time)
        # Adjust for timezone
        dt = dt - timedelta(hours=timezone_offset)
        
        # Convert to Julian Day
        a = (14 - dt.month) // 12
        y = dt.year + 4800 - a
        m = dt.month + 12 * a - 3
        
        jdn = dt.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
        
        # Add time fraction
        time_fraction = (dt.hour + dt.minute / 60.0 + dt.second / 3600.0) / 24.0
        
        return jdn + time_fraction - 0.5
    
    def get_sidereal_time(self, jd: float, longitude: float) -> float:
        """Calculate Local Sidereal Time"""
        # Greenwich Sidereal Time at 0h UT
        t = (jd - 2451545.0) / 36525.0
        gst = 280.46061837 + 360.98564736629 * (jd - 2451545.0) + 0.000387933 * t * t - t * t * t / 38710000.0
        
        # Normalize to 0-360
        gst = gst % 360.0
        
        # Local Sidereal Time
        lst = gst + longitude
        return lst % 360.0
    
    def calculate_planetary_positions(self, jd: float) -> Dict[str, Dict]:
        """Calculate positions of all planets"""
        observer = ephem.Observer()
        # Fix the Julian Day conversion for ephem
        observer.date = ephem.Date(jd - 2415020.0)
        
        # Calculate ayanamsa for this date
        ayanamsa = self.calculate_lahiri_ayanamsa(jd)
        
        positions = {}
        
        for planet_name, planet_obj in self.planets.items():
            if planet_obj is None:  # Rahu/Ketu calculated separately
                continue
                
            planet_obj.compute(observer)
            # Get tropical longitude from ephem
            tropical_longitude = math.degrees(planet_obj.hlong)
            latitude = math.degrees(planet_obj.hlat)
            
            # Convert to sidereal longitude by subtracting ayanamsa
            sidereal_longitude = (tropical_longitude - ayanamsa) % 360.0
            
            positions[planet_name] = {
                'longitude': sidereal_longitude,
                'latitude': latitude,
                'sign': self.get_sign_from_longitude(sidereal_longitude),
                'nakshatra': self.get_nakshatra_from_longitude(sidereal_longitude)
            }
        
        # Calculate Rahu and Ketu (Lunar Nodes) - these are already sidereal
        rahu_longitude = self.get_rahu_longitude(jd)
        # Apply ayanamsa correction to Rahu as well
        rahu_sidereal = (rahu_longitude - ayanamsa) % 360.0
        ketu_sidereal = (rahu_sidereal + 180) % 360.0
        
        positions['Rahu'] = {
            'longitude': rahu_sidereal,
            'latitude': 0,
            'sign': self.get_sign_from_longitude(rahu_sidereal),
            'nakshatra': self.get_nakshatra_from_longitude(rahu_sidereal)
        }
        
        positions['Ketu'] = {
            'longitude': ketu_sidereal,
            'latitude': 0,
            'sign': self.get_sign_from_longitude(ketu_sidereal),
            'nakshatra': self.get_nakshatra_from_longitude(ketu_sidereal)
        }
        
        return positions
    
    def get_sign_from_longitude(self, longitude: float) -> int:
        """Get zodiac sign (1-12) from longitude"""
        return int(longitude // 30) + 1
    
    def get_nakshatra_from_longitude(self, longitude: float) -> int:
        """Get nakshatra (1-27) from longitude"""
        nakshatra_length = 360.0 / 27.0  # 13.333 degrees per nakshatra
        return int(longitude / nakshatra_length) + 1
    
    def get_moon_mean_longitude(self, jd: float) -> float:
        """Calculate Moon's mean longitude"""
        t = (jd - 2451545.0) / 36525.0
        longitude = 218.3164477 + 481267.88123421 * t - 0.0015786 * t * t + t * t * t / 538841.0 - t * t * t * t / 65194000.0
        return longitude % 360.0
    
    def get_rahu_longitude(self, jd: float) -> float:
        """Calculate Rahu's (North Node) longitude"""
        t = (jd - 2451545.0) / 36525.0
        omega = 125.04452 - 1934.136261 * t + 0.0020708 * t * t + t * t * t / 450000.0
        return (360.0 - omega) % 360.0
    
    def calculate_lahiri_ayanamsa(self, jd: float) -> float:
        """Calculate Lahiri Ayanamsa for given Julian Day"""
        # Lahiri Ayanamsa calculation based on Spica at 0° Libra
        # Reference epoch: J2000.0 (JD 2451545.0)
        t = (jd - 2451545.0) / 36525.0
        
        # Nutation in longitude
        omega = 125.04452 - 1934.136261 * t + 0.0020708 * t * t + t * t * t / 450000.0
        nutation = -17.20 * math.sin(math.radians(omega)) / 3600.0
        
        # Lahiri ayanamsa formula
        # At J2000.0, ayanamsa was approximately 23.85°
        ayanamsa = 23.85 + 50.27 * t + 0.000464 * t * t
        
        # Apply nutation correction
        ayanamsa += nutation
        
        return ayanamsa % 360.0
    
    def calculate_ascendant(self, jd: float, latitude: float, longitude: float) -> float:
        """Calculate Ascendant (Lagna)"""
        lst = self.get_sidereal_time(jd, longitude)
        
        # Convert to radians
        lst_rad = math.radians(lst)
        lat_rad = math.radians(latitude)
        
        # Calculate ascendant
        asc = math.atan2(math.cos(lst_rad), -math.sin(lst_rad) * math.cos(lat_rad))
        asc_deg = math.degrees(asc)
        
        if asc_deg < 0:
            asc_deg += 360
            
        return asc_deg
    
    def calculate_houses(self, ascendant: float, system: str = "placidus") -> List[float]:
        """Calculate house cusps"""
        houses = []
        
        if system == "equal":
            # Equal house system - 30 degrees per house
            for i in range(12):
                house_cusp = (ascendant + i * 30) % 360
                houses.append(house_cusp)
        else:
            # For now, use equal house system for both
            # TODO: Implement Placidus system
            for i in range(12):
                house_cusp = (ascendant + i * 30) % 360
                houses.append(house_cusp)
        
        return houses
    
    def get_planet_house(self, planet_longitude: float, house_cusps: List[float]) -> int:
        """Determine which house a planet is in"""
        for i in range(12):
            start = house_cusps[i]
            end = house_cusps[(i + 1) % 12]
            
            if start <= end:
                if start <= planet_longitude < end:
                    return i + 1
            else:  # House crosses 0 degrees
                if planet_longitude >= start or planet_longitude < end:
                    return i + 1
        
        return 1  # Default to first house
    
    def calculate_navamsa(self, rasi_positions: Dict[str, Dict]) -> Dict[str, Dict]:
        """Calculate Navamsa (D9) chart positions"""
        navamsa_positions = {}
        
        for planet, position in rasi_positions.items():
            longitude = position['longitude']
            
            # Each rasi is divided into 9 navamsas of 3°20' each
            navamsa_within_sign = int((longitude % 30) / (30/9))
            rasi_number = self.get_sign_from_longitude(longitude)
            
            # Calculate navamsa sign based on rasi and navamsa number
            if rasi_number in [1, 5, 9]:  # Aries, Leo, Sagittarius (Fire signs)
                navamsa_sign = ((navamsa_within_sign) % 12) + 1
            elif rasi_number in [2, 6, 10]:  # Taurus, Virgo, Capricorn (Earth signs)  
                navamsa_sign = ((navamsa_within_sign + 3) % 12) + 1
            elif rasi_number in [3, 7, 11]:  # Gemini, Libra, Aquarius (Air signs)
                navamsa_sign = ((navamsa_within_sign + 6) % 12) + 1
            else:  # Cancer, Scorpio, Pisces (Water signs)
                navamsa_sign = ((navamsa_within_sign + 9) % 12) + 1
            
            navamsa_positions[planet] = {
                'longitude': longitude,  # Keep original longitude for reference
                'sign': navamsa_sign,
                'nakshatra': position['nakshatra']
            }
        
        return navamsa_positions
