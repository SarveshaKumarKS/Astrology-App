from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, date, time

# Load environment BEFORE importing modules (e.g. auth) that read DB_NAME/MONGO_URL
# at import time, so they bind to the correct database.
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from astrology.vakkiam_system import VakkiamCalculator
from astrology.thirukkanitham_system import ThirukkanithamCalculator
from astrology.models import BirthDetails, HoroscopeResult, CompatibilityResult
from astrology.nkv_palan import compute_nkv_context, generate_nkv_predictions
from astrology.palan_pdf_generator import generate_palan_pdf
from astrology.karu_udayam import (
    get_karu_udayam_tamil_date,
    resolve_karu_udayam_gregorian_date,
    strip_lagnam_from_chart,
)
from auth import router as auth_router, get_current_user, ensure_indexes
from fastapi import Depends

# MongoDB connection (optional — persistence is best-effort for the demo build).
# Falls back to sensible defaults and a short server-selection timeout so the
# core horoscope/PDF endpoints work even when no MongoDB is running.
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=2000)
db = client[os.environ.get('DB_NAME', 'tamil_astrology')]

# Create the main app without a prefix
app = FastAPI(title="Tamil Astrology API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Astrology System Models
class BirthDetailsInput(BaseModel):
    name: str
    mother_name: Optional[str] = None
    father_name: Optional[str] = None
    date_of_birth: date
    time_of_birth: time
    place_of_birth: str
    latitude: float
    longitude: float
    timezone: str
    time_correction: int = 0  # in minutes

class HoroscopeRequest(BaseModel):
    birth_details: BirthDetailsInput
    system: str = "vakkiam"  # "vakkiam" or "thirukkanitham"
    language: str = "tamil"  # "tamil" or "english"

class CompatibilityRequest(BaseModel):
    male_details: BirthDetailsInput
    female_details: BirthDetailsInput
    system: str = "vakkiam"  # "vakkiam" or "thirukkanitham"
    language: str = "tamil"  # "tamil" or "english"

class UserProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    birth_details: BirthDetailsInput
    user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Initialize calculators
vakkiam_calc = VakkiamCalculator()
thirukkanitham_calc = ThirukkanithamCalculator()

# Basic status endpoints
@api_router.get("/")
async def root():
    return {"message": "Tamil Astrology API - Ready", "systems": ["vakkiam", "thirukkanitham"]}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Horoscope Generation
@api_router.post("/horoscope")
async def generate_horoscope(request: HoroscopeRequest):
    try:
        # Convert request to internal format
        birth_details = BirthDetails(
            name=request.birth_details.name,
            mother_name=request.birth_details.mother_name,
            father_name=request.birth_details.father_name,
            date_of_birth=request.birth_details.date_of_birth,
            time_of_birth=request.birth_details.time_of_birth,
            place_of_birth=request.birth_details.place_of_birth,
            latitude=request.birth_details.latitude,
            longitude=request.birth_details.longitude,
            timezone=request.birth_details.timezone,
            time_correction=request.birth_details.time_correction
        )
        
        # Select calculator based on system
        if request.system == "vakkiam":
            calculator = vakkiam_calc
        elif request.system == "thirukkanitham":
            calculator = thirukkanitham_calc
        else:
            raise HTTPException(status_code=400, detail="Invalid system. Use 'vakkiam' or 'thirukkanitham'")
        
        # Generate horoscope
        horoscope = calculator.generate_horoscope(birth_details, request.language)

        # Generate Karu Udayam (derived) Raasi chart from lookup table
        try:
            if horoscope.tamil_month and horoscope.tamil_day:
                karu_tamil = get_karu_udayam_tamil_date(horoscope.tamil_month, horoscope.tamil_day)
                if karu_tamil:
                    karu_month, karu_day = karu_tamil
                    karu_gregorian = resolve_karu_udayam_gregorian_date(
                        calculator,
                        birth_details,
                        karu_month,
                        karu_day,
                    )
                    if karu_gregorian:
                        karu_date, diff_days = karu_gregorian
                        karu_birth_details = BirthDetails(
                            name=birth_details.name,
                            mother_name=birth_details.mother_name,
                            father_name=birth_details.father_name,
                            date_of_birth=karu_date,
                            time_of_birth=birth_details.time_of_birth,
                            place_of_birth=birth_details.place_of_birth,
                            latitude=birth_details.latitude,
                            longitude=birth_details.longitude,
                            timezone=birth_details.timezone,
                            time_correction=birth_details.time_correction,
                        )
                        karu_horoscope = calculator.generate_horoscope(karu_birth_details, request.language)
                        horoscope.karu_udayam_rasi_chart = strip_lagnam_from_chart(karu_horoscope.rasi_chart)
                        horoscope.karu_udayam_date_of_birth = karu_date
                        horoscope.karu_udayam_time_of_birth = birth_details.time_of_birth
                        horoscope.karu_udayam_tamil_month = karu_month
                        horoscope.karu_udayam_tamil_day = karu_day
                        horoscope.karu_udayam_approx_diff_days = diff_days
        except Exception as e:
            logging.warning(f"Karu Udayam chart generation skipped: {str(e)}")
        
        # Save to database
        horoscope_dict = horoscope.dict()
        horoscope_dict['_id'] = str(uuid.uuid4())
        horoscope_dict['created_at'] = datetime.utcnow()
        horoscope_dict['system'] = request.system
        
        # Convert date objects to strings for MongoDB compatibility
        if 'birth_details' in horoscope_dict and 'date_of_birth' in horoscope_dict['birth_details']:
            horoscope_dict['birth_details']['date_of_birth'] = str(horoscope_dict['birth_details']['date_of_birth'])
        if 'birth_details' in horoscope_dict and 'time_of_birth' in horoscope_dict['birth_details']:
            horoscope_dict['birth_details']['time_of_birth'] = str(horoscope_dict['birth_details']['time_of_birth'])
        
        # Convert dasa period dates to strings
        if 'dasa_periods' in horoscope_dict:
            for dasa in horoscope_dict['dasa_periods']:
                if 'start_date' in dasa:
                    dasa['start_date'] = str(dasa['start_date'])
                if 'end_date' in dasa:
                    dasa['end_date'] = str(dasa['end_date'])
        
        if 'current_dasa' in horoscope_dict and horoscope_dict['current_dasa']:
            if 'start_date' in horoscope_dict['current_dasa']:
                horoscope_dict['current_dasa']['start_date'] = str(horoscope_dict['current_dasa']['start_date'])
            if 'end_date' in horoscope_dict['current_dasa']:
                horoscope_dict['current_dasa']['end_date'] = str(horoscope_dict['current_dasa']['end_date'])
            # Convert new date fields
            if 'next_dasa_end_date' in horoscope_dict['current_dasa'] and horoscope_dict['current_dasa']['next_dasa_end_date']:
                horoscope_dict['current_dasa']['next_dasa_end_date'] = str(horoscope_dict['current_dasa']['next_dasa_end_date'])
            if 'current_bhukti_end_date' in horoscope_dict['current_dasa'] and horoscope_dict['current_dasa']['current_bhukti_end_date']:
                horoscope_dict['current_dasa']['current_bhukti_end_date'] = str(horoscope_dict['current_dasa']['current_bhukti_end_date'])
            if 'next_bhukti_end_date' in horoscope_dict['current_dasa'] and horoscope_dict['current_dasa']['next_bhukti_end_date']:
                horoscope_dict['current_dasa']['next_bhukti_end_date'] = str(horoscope_dict['current_dasa']['next_bhukti_end_date'])
        if 'karu_udayam_date_of_birth' in horoscope_dict and horoscope_dict['karu_udayam_date_of_birth']:
            horoscope_dict['karu_udayam_date_of_birth'] = str(horoscope_dict['karu_udayam_date_of_birth'])
        if 'karu_udayam_time_of_birth' in horoscope_dict and horoscope_dict['karu_udayam_time_of_birth']:
            horoscope_dict['karu_udayam_time_of_birth'] = str(horoscope_dict['karu_udayam_time_of_birth'])
        
        # Convert chart house keys from integers to strings for MongoDB
        if 'rasi_chart' in horoscope_dict and 'houses' in horoscope_dict['rasi_chart']:
            horoscope_dict['rasi_chart']['houses'] = {str(k): v for k, v in horoscope_dict['rasi_chart']['houses'].items()}
        if 'rasi_chart' in horoscope_dict and 'houses_tamil' in horoscope_dict['rasi_chart']:
            horoscope_dict['rasi_chart']['houses_tamil'] = {str(k): v for k, v in horoscope_dict['rasi_chart']['houses_tamil'].items()}
        if 'navamsa_chart' in horoscope_dict and 'houses' in horoscope_dict['navamsa_chart']:
            horoscope_dict['navamsa_chart']['houses'] = {str(k): v for k, v in horoscope_dict['navamsa_chart']['houses'].items()}
        if 'navamsa_chart' in horoscope_dict and 'houses_tamil' in horoscope_dict['navamsa_chart']:
            horoscope_dict['navamsa_chart']['houses_tamil'] = {str(k): v for k, v in horoscope_dict['navamsa_chart']['houses_tamil'].items()}
        if 'karu_udayam_rasi_chart' in horoscope_dict and horoscope_dict['karu_udayam_rasi_chart']:
            if 'houses' in horoscope_dict['karu_udayam_rasi_chart']:
                horoscope_dict['karu_udayam_rasi_chart']['houses'] = {
                    str(k): v for k, v in horoscope_dict['karu_udayam_rasi_chart']['houses'].items()
                }
            if 'houses_tamil' in horoscope_dict['karu_udayam_rasi_chart']:
                horoscope_dict['karu_udayam_rasi_chart']['houses_tamil'] = {
                    str(k): v for k, v in horoscope_dict['karu_udayam_rasi_chart']['houses_tamil'].items()
                }
        
        try:
            await db.horoscopes.insert_one(horoscope_dict)
        except Exception as db_err:
            logging.warning(f"Skipping horoscope persistence (DB unavailable): {db_err}")

        # Return horoscope as JSON to properly serialize dates
        return horoscope.model_dump(mode='json')
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logging.error(f"Error generating horoscope: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating horoscope: {str(e)}")

# Generate PDF
@api_router.post("/generate-pdf")
async def generate_pdf(request: HoroscopeRequest):
    """
    Generate a PDF horoscope report
    """
    from fastapi.responses import Response
    from astrology.pdf_generator import generate_horoscope_pdf
    
    try:
        # Convert request to internal format
        birth_details = BirthDetails(
            name=request.birth_details.name,
            mother_name=request.birth_details.mother_name,
            father_name=request.birth_details.father_name,
            date_of_birth=request.birth_details.date_of_birth,
            time_of_birth=request.birth_details.time_of_birth,
            place_of_birth=request.birth_details.place_of_birth,
            latitude=request.birth_details.latitude,
            longitude=request.birth_details.longitude,
            timezone=request.birth_details.timezone,
            time_correction=request.birth_details.time_correction
        )
        
        system = request.system.lower()
        language = request.language.lower()
        
        # Validate system
        if system not in ["vakkiam", "thirukkanitham"]:
            raise HTTPException(status_code=400, detail="Invalid system. Use 'vakkiam' or 'thirukkanitham'")
        
        # Select calculator
        if system == "vakkiam":
            calculator = VakkiamCalculator()
        else:
            calculator = ThirukkanithamCalculator()
        
        # Generate horoscope
        horoscope = calculator.generate_horoscope(birth_details, language)
        
        # Prepare personal details for PDF
        personal_details = {
            "name": birth_details.name,
            "lagnam": horoscope.ascendant_tamil if language == "tamil" else horoscope.ascendant,
            "star_pada": f"{horoscope.nakshatra_tamil}" if language == "tamil" else f"{horoscope.nakshatra}",
            "rasi": horoscope.moon_sign_tamil if language == "tamil" else horoscope.moon_sign,
            "date": birth_details.date_of_birth.strftime("%d/%m/%Y"),
            "time": birth_details.time_of_birth.strftime("%H:%M:%S"),
            "place": birth_details.place_of_birth,
            "longitude": f"{birth_details.longitude}°",
            "latitude": f"{birth_details.latitude}°",
            "timezone": birth_details.timezone,
            "time_correction": str(birth_details.time_correction),
        }
        
        # Generate PDF
        pdf_bytes = generate_horoscope_pdf(horoscope, personal_details, system)
        
        # Return PDF as response - use ASCII-safe filename
        import re
        import unicodedata
        # Remove non-ASCII characters and normalize
        safe_name = unicodedata.normalize('NFKD', birth_details.name)
        safe_name = re.sub(r'[^\x00-\x7F]+', '', safe_name)  # Remove non-ASCII
        safe_name = re.sub(r'[^\w\s-]', '', safe_name)  # Remove special chars
        safe_name = re.sub(r'[-\s]+', '_', safe_name.replace(' ', '_'))  # Replace spaces/dashes
        if not safe_name:  # If name becomes empty, use default
            safe_name = "user"
        filename = f"horoscope_{safe_name}_{system}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error generating PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

# Generate NKV Palan PDF
@api_router.post("/generate-palan-pdf")
async def generate_palan_pdf_endpoint(request: HoroscopeRequest):
    """Generate an NKV Palan (prediction) PDF report."""
    from fastapi.responses import Response

    try:
        birth_details = BirthDetails(
            name=request.birth_details.name,
            date_of_birth=request.birth_details.date_of_birth,
            time_of_birth=request.birth_details.time_of_birth,
            place_of_birth=request.birth_details.place_of_birth,
            latitude=request.birth_details.latitude,
            longitude=request.birth_details.longitude,
            timezone=request.birth_details.timezone,
            time_correction=request.birth_details.time_correction,
        )

        system = request.system.lower()
        if system not in ("vakkiam", "thirukkanitham"):
            raise HTTPException(status_code=400, detail="Invalid system. Use 'vakkiam' or 'thirukkanitham'")

        calculator = VakkiamCalculator() if system == "vakkiam" else ThirukkanithamCalculator()
        horoscope = calculator.generate_horoscope(birth_details, request.language)

        context = compute_nkv_context(horoscope)
        palan_result = generate_nkv_predictions(context)

        pdf_bytes = generate_palan_pdf(palan_result, name=birth_details.name)

        import re, unicodedata
        safe_name = unicodedata.normalize("NFKD", birth_details.name)
        safe_name = re.sub(r"[^\x00-\x7F]+", "", safe_name)
        safe_name = re.sub(r"[^\w\s-]", "", safe_name)
        safe_name = re.sub(r"[-\s]+", "_", safe_name.replace(" ", "_"))
        if not safe_name:
            safe_name = "user"
        filename = f"palan_{safe_name}_{system}.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error generating Palan PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating Palan PDF: {str(e)}")

# Marriage Compatibility
@api_router.post("/compatibility")
async def check_compatibility(request: CompatibilityRequest):
    try:
        # Convert request to internal format
        male_details = BirthDetails(
            name=request.male_details.name,
            mother_name=request.male_details.mother_name,
            father_name=request.male_details.father_name,
            date_of_birth=request.male_details.date_of_birth,
            time_of_birth=request.male_details.time_of_birth,
            place_of_birth=request.male_details.place_of_birth,
            latitude=request.male_details.latitude,
            longitude=request.male_details.longitude,
            timezone=request.male_details.timezone,
            time_correction=request.male_details.time_correction
        )
        
        female_details = BirthDetails(
            name=request.female_details.name,
            mother_name=request.female_details.mother_name,
            father_name=request.female_details.father_name,
            date_of_birth=request.female_details.date_of_birth,
            time_of_birth=request.female_details.time_of_birth,
            place_of_birth=request.female_details.place_of_birth,
            latitude=request.female_details.latitude,
            longitude=request.female_details.longitude,
            timezone=request.female_details.timezone,
            time_correction=request.female_details.time_correction
        )
        
        # Select calculator based on system
        if request.system == "vakkiam":
            calculator = vakkiam_calc
        elif request.system == "thirukkanitham":
            calculator = thirukkanitham_calc
        else:
            raise HTTPException(status_code=400, detail="Invalid system. Use 'vakkiam' or 'thirukkanitham'")
        
        # Check compatibility
        compatibility = calculator.check_compatibility(male_details, female_details, request.language)
        
        # Save to database
        compatibility_dict = compatibility.dict()
        compatibility_dict['_id'] = str(uuid.uuid4())
        compatibility_dict['created_at'] = datetime.utcnow()
        compatibility_dict['system'] = request.system
        
        # Convert date objects to strings for MongoDB compatibility
        if 'male_details' in compatibility_dict and 'date_of_birth' in compatibility_dict['male_details']:
            compatibility_dict['male_details']['date_of_birth'] = str(compatibility_dict['male_details']['date_of_birth'])
        if 'male_details' in compatibility_dict and 'time_of_birth' in compatibility_dict['male_details']:
            compatibility_dict['male_details']['time_of_birth'] = str(compatibility_dict['male_details']['time_of_birth'])
        if 'female_details' in compatibility_dict and 'date_of_birth' in compatibility_dict['female_details']:
            compatibility_dict['female_details']['date_of_birth'] = str(compatibility_dict['female_details']['date_of_birth'])
        if 'female_details' in compatibility_dict and 'time_of_birth' in compatibility_dict['female_details']:
            compatibility_dict['female_details']['time_of_birth'] = str(compatibility_dict['female_details']['time_of_birth'])
        
        try:
            await db.compatibility_reports.insert_one(compatibility_dict)
        except Exception as db_err:
            logging.warning(f"Skipping compatibility persistence (DB unavailable): {db_err}")

        return compatibility
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logging.error(f"Error checking compatibility: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error checking compatibility: {str(e)}")

# User Profile Management
@api_router.post("/profiles", response_model=UserProfile)
async def create_profile(profile_data: UserProfile, current_user: dict = Depends(get_current_user)):
    try:
        profile_dict = profile_data.dict()
        # Always bind the profile to the authenticated user (ignore any client value).
        profile_dict['user_id'] = current_user['user_id']

        # Convert date objects to strings for MongoDB compatibility
        if 'birth_details' in profile_dict and 'date_of_birth' in profile_dict['birth_details']:
            profile_dict['birth_details']['date_of_birth'] = str(profile_dict['birth_details']['date_of_birth'])
        if 'birth_details' in profile_dict and 'time_of_birth' in profile_dict['birth_details']:
            profile_dict['birth_details']['time_of_birth'] = str(profile_dict['birth_details']['time_of_birth'])

        await db.user_profiles.insert_one(dict(profile_dict))
        return UserProfile(**profile_dict)
    except Exception as e:
        logging.error(f"Error creating profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not save profile. Please try again.")

@api_router.get("/profiles", response_model=List[UserProfile])
async def get_profiles(current_user: dict = Depends(get_current_user)):
    try:
        profiles = await db.user_profiles.find(
            {"user_id": current_user['user_id']}, {"_id": 0}
        ).to_list(1000)
        return [UserProfile(**profile) for profile in profiles]
    except Exception as e:
        logging.warning(f"Returning empty profile list (DB unavailable): {str(e)}")
        return []

@api_router.get("/profiles/{profile_id}", response_model=UserProfile)
async def get_profile(profile_id: str, current_user: dict = Depends(get_current_user)):
    try:
        profile = await db.user_profiles.find_one(
            {"id": profile_id, "user_id": current_user['user_id']}, {"_id": 0}
        )
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        return UserProfile(**profile)
    except HTTPException:
        raise
    except Exception as e:
        logging.warning(f"Profile lookup failed (DB unavailable): {str(e)}")
        raise HTTPException(status_code=404, detail="Profile not found")

@api_router.delete("/profiles/{profile_id}")
async def delete_profile(profile_id: str, current_user: dict = Depends(get_current_user)):
    try:
        result = await db.user_profiles.delete_one(
            {"id": profile_id, "user_id": current_user['user_id']}
        )
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Profile not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not delete profile. Please try again.")

# Panchangam (Thirukkanitham only)
@api_router.get("/panchangam/{date}")
async def get_panchangam(date: date, language: str = "tamil"):
    # NOTE: daily-panchangam (tithi/yoga/karana/muhurta) is not implemented in
    # this build — ThirukkanithamCalculator has no get_daily_panchangam method.
    # Return a clear 501 so the Panchangam screen degrades gracefully instead of
    # surfacing a 500 stack trace during the demo.
    if not hasattr(thirukkanitham_calc, "get_daily_panchangam"):
        raise HTTPException(
            status_code=501,
            detail="Daily Panchangam is not available in this build.",
        )
    try:
        panchangam = thirukkanitham_calc.get_daily_panchangam(date, language)
        return panchangam
    except Exception as e:
        logging.error(f"Error getting panchangam: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting panchangam: {str(e)}")

# Include the router in the main app
api_router.include_router(auth_router)
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_create_indexes():
    await ensure_indexes()

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
