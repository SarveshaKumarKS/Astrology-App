from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, date, time

class BirthDetails(BaseModel):
    name: str
    date_of_birth: date
    time_of_birth: time
    place_of_birth: str
    latitude: float
    longitude: float
    timezone: str
    time_correction: int = 0  # in minutes

class PlanetaryPosition(BaseModel):
    planet: str
    planet_tamil: str
    longitude: float
    sign: int  # 1-12
    sign_name: str
    sign_name_tamil: str
    nakshatra: int  # 1-27
    nakshatra_name: str
    nakshatra_name_tamil: str
    house: int  # 1-12
    retrograde: bool = False
    longitude_dms: Optional[str] = None  # DMS-formatted sidereal longitude
    longitude_in_sign: Optional[float] = None  # Longitude within its zodiac sign
    longitude_in_sign_dms: Optional[str] = None  # DMS-formatted longitude within the sign
    nakshatra_pada: Optional[int] = None  # 1-4 depending on which quarter of the nakshatra
    nakshatra_lord: Optional[str] = None  # Ruling planet of the nakshatra
    nakshatra_lord_tamil: Optional[str] = None  # Ruling planet of the nakshatra (Tamil name)

class DasaPeriod(BaseModel):
    planet: str
    planet_tamil: str
    start_date: date
    end_date: date
    level: str  # "maha", "antar", "pratyantar"
    years: float
    months: int
    days: int
    # Extended fields for current dasa
    balance_years: Optional[int] = None
    balance_months: Optional[int] = None
    balance_days: Optional[int] = None
    next_dasa_planet: Optional[str] = None
    next_dasa_planet_tamil: Optional[str] = None
    next_dasa_end_date: Optional[date] = None
    current_bhukti_planet: Optional[str] = None
    current_bhukti_planet_tamil: Optional[str] = None
    current_bhukti_end_date: Optional[date] = None
    next_bhukti_planet: Optional[str] = None
    next_bhukti_planet_tamil: Optional[str] = None
    next_bhukti_end_date: Optional[date] = None

class Chart(BaseModel):
    chart_type: str  # "rasi", "navamsa"
    houses: Dict[int, List[str]]  # house_number -> list of planets
    houses_tamil: Dict[int, List[str]]  # house_number -> list of planets in Tamil
    ascendant_house: int
    image_base64: Optional[str] = None  # South Indian chart image as base64
    
class HoroscopeResult(BaseModel):
    system_type: str = "Modern"
    birth_details: BirthDetails
    system: str  # "vakkiam" or "thirukkanitham"
    language: str
    ascendant: str
    ascendant_tamil: str
    moon_sign: str
    moon_sign_tamil: str
    nakshatra: str
    nakshatra_tamil: str
    planetary_positions: List[PlanetaryPosition]
    rasi_chart: Chart
    navamsa_chart: Chart
    dasa_periods: List[DasaPeriod]
    current_dasa: DasaPeriod
    special_yogas: List[str] = []
    special_yogas_tamil: List[str] = []
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    # Extended fields
    retrograde_planets: List[str] = []
    retrograde_planets_tamil: List[str] = []
    bhava_maruthal: Dict[str, int] = {}  # Planet -> House number
    bhava_maruthal_tamil: Dict[str, int] = {}  # Tamil planet name -> House number

class CompatibilityFactor(BaseModel):
    factor_name: str
    factor_name_tamil: str
    male_value: str
    female_value: str
    points: float
    max_points: float
    status: str  # "excellent", "good", "average", "poor"
    status_tamil: str
    description: str
    description_tamil: str

class CompatibilityResult(BaseModel):
    male_details: BirthDetails
    female_details: BirthDetails
    system: str
    language: str
    total_points: float
    max_points: float
    percentage: float
    overall_rating: str  # "excellent", "good", "average", "poor"
    overall_rating_tamil: str
    factors: List[CompatibilityFactor]
    dosha_analysis: Dict[str, Any]
    recommendation: str
    recommendation_tamil: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class PanchangamDetails(BaseModel):
    date: date
    tithi: str
    tithi_tamil: str
    nakshatra: str
    nakshatra_tamil: str
    yoga: str
    yoga_tamil: str
    karana: str
    karana_tamil: str
    sunrise: time
    sunset: time
    moonrise: time
    moonset: time
    rahu_kalam: Dict[str, time]  # start, end
    yama_gandam: Dict[str, time]  # start, end
    gulika_kalam: Dict[str, time]  # start, end
    abhijit_muhurta: Dict[str, time]  # start, end
    auspicious_times: List[Dict[str, Any]]
    inauspicious_times: List[Dict[str, Any]]