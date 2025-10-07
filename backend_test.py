#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Tamil Astrology API
Tests all endpoints with realistic Tamil astrology data
"""

import requests
import json
import sys
from datetime import datetime, date, time
from typing import Dict, Any

# Get backend URL from frontend .env
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('EXPO_PUBLIC_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except:
        pass
    return "http://localhost:8001"

BASE_URL = get_backend_url()
API_BASE = f"{BASE_URL}/api"

print(f"Testing Tamil Astrology API at: {API_BASE}")
print("=" * 60)

class TamilAstrologyTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.failed_tests = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
        
        if not success:
            self.failed_tests.append(test_name)
    
    def test_health_endpoints(self):
        """Test basic health and info endpoints"""
        print("\n🔍 Testing Health Endpoints")
        print("-" * 30)
        
        # Test root endpoint
        try:
            response = self.session.get(f"{API_BASE}/")
            if response.status_code == 200:
                data = response.json()
                if "Tamil Astrology API" in data.get("message", ""):
                    self.log_test("Root endpoint", True, f"Message: {data.get('message')}")
                else:
                    self.log_test("Root endpoint", False, f"Unexpected response: {data}")
            else:
                self.log_test("Root endpoint", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Root endpoint", False, f"Error: {str(e)}")
        
        # Test health endpoint
        try:
            response = self.session.get(f"{API_BASE}/health")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Health endpoint", True, f"Status: {data.get('status')}")
                else:
                    self.log_test("Health endpoint", False, f"Unexpected status: {data}")
            else:
                self.log_test("Health endpoint", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Health endpoint", False, f"Error: {str(e)}")
    
    def test_horoscope_generation(self):
        """Test horoscope generation - Focus on Thirukkanitham fix"""
        print("\n🌟 Testing Horoscope Generation (Focus: Thirukkanitham Fix)")
        print("-" * 55)
        
        # Test data as specified in review request - exact same data for both systems
        base_test_data = {
            "birth_details": {
                "name": "Test User",
                "date_of_birth": "1990-01-15",
                "time_of_birth": "14:30:00",
                "place_of_birth": "Chennai",
                "latitude": 13.0827,
                "longitude": 80.2707,
                "timezone": "IST",
                "time_correction": 0
            },
            "language": "tamil"
        }
        
        test_cases = [
            {
                "name": "Vakkiam System - Regression Test",
                "data": {**base_test_data, "system": "vakkiam"}
            },
            {
                "name": "Thirukkanitham System - Fixed Issue",
                "data": {**base_test_data, "system": "thirukkanitham"}
            }
        ]
        
        for test_case in test_cases:
            try:
                response = self.session.post(
                    f"{API_BASE}/horoscope",
                    json=test_case["data"],
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Validate response structure
                    required_fields = [
                        'birth_details', 'system', 'language', 'ascendant', 'ascendant_tamil',
                        'moon_sign', 'moon_sign_tamil', 'nakshatra', 'nakshatra_tamil', 
                        'planetary_positions', 'rasi_chart', 'navamsa_chart', 'dasa_periods', 'current_dasa'
                    ]
                    
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        # Specific validation for the fixed issues
                        planets = data.get('planetary_positions', [])
                        dasa_periods = data.get('dasa_periods', [])
                        current_dasa = data.get('current_dasa')
                        navamsa_chart = data.get('navamsa_chart', {})
                        
                        # Check system matches request
                        if data.get('system') != test_case['data']['system']:
                            self.log_test(f"Horoscope - {test_case['name']}", False, 
                                        f"System mismatch: expected {test_case['data']['system']}, got {data.get('system')}")
                        # Check we have 9 planets
                        elif len(planets) != 9:
                            self.log_test(f"Horoscope - {test_case['name']}", False, 
                                        f"Expected 9 planets, got {len(planets)}")
                        # Check dasa periods exist (fix for _calculate_dasa_periods)
                        elif not dasa_periods:
                            self.log_test(f"Horoscope - {test_case['name']}", False, 
                                        "No dasa periods found - _calculate_dasa_periods issue")
                        # Check current dasa exists (fix for _get_current_dasa)
                        elif not current_dasa:
                            self.log_test(f"Horoscope - {test_case['name']}", False, 
                                        "No current dasa found - _get_current_dasa issue")
                        # Check navamsa chart populated (fix for calculate_navamsa return statement)
                        elif not navamsa_chart.get('houses'):
                            self.log_test(f"Horoscope - {test_case['name']}", False, 
                                        "Navamsa chart empty - calculate_navamsa return issue")
                        else:
                            # All checks passed
                            details = f"✅ System: {data['system']}, Planets: {len(planets)}, Dasa periods: {len(dasa_periods)}"
                            if test_case['data']['system'] == 'thirukkanitham':
                                details += " - THIRUKKANITHAM FIX VERIFIED"
                            self.log_test(f"Horoscope - {test_case['name']}", True, details)
                    else:
                        self.log_test(f"Horoscope - {test_case['name']}", False, 
                                    f"Missing fields: {missing_fields}")
                else:
                    error_msg = f"Status: {response.status_code}"
                    if test_case['data']['system'] == 'thirukkanitham' and response.status_code == 500:
                        error_msg += " - THIRUKKANITHAM STILL FAILING (Expected fix not working)"
                    try:
                        error_data = response.json()
                        error_msg += f", Error: {error_data.get('detail', 'Unknown')}"
                    except:
                        error_msg += f", Response: {response.text[:200]}"
                    
                    self.log_test(f"Horoscope - {test_case['name']}", False, error_msg)
                    
            except Exception as e:
                self.log_test(f"Horoscope - {test_case['name']}", False, f"Error: {str(e)}")
    
    def test_compatibility_check(self):
        """Test marriage compatibility checking"""
        print("\n💕 Testing Marriage Compatibility")
        print("-" * 35)
        
        test_cases = [
            {
                "name": "Vakkiam Compatibility - Tamil",
                "data": {
                    "male_details": {
                        "name": "முருகன்",
                        "date_of_birth": "1990-03-15",
                        "time_of_birth": "08:30:00",
                        "place_of_birth": "Chennai, Tamil Nadu, India",
                        "latitude": 13.0827,
                        "longitude": 80.2707,
                        "timezone": "IST",
                        "time_correction": 0
                    },
                    "female_details": {
                        "name": "லக்ஷ்மி",
                        "date_of_birth": "1992-07-22",
                        "time_of_birth": "16:45:00",
                        "place_of_birth": "Trichy, Tamil Nadu, India",
                        "latitude": 10.7905,
                        "longitude": 78.7047,
                        "timezone": "IST",
                        "time_correction": 0
                    },
                    "system": "vakkiam",
                    "language": "tamil"
                }
            },
            {
                "name": "Thirukkanitham Compatibility - Tamil",
                "data": {
                    "male_details": {
                        "name": "கார்த்திக்",
                        "date_of_birth": "1989-11-08",
                        "time_of_birth": "12:15:00",
                        "place_of_birth": "Salem, Tamil Nadu, India",
                        "latitude": 11.664,
                        "longitude": 78.146,
                        "timezone": "IST",
                        "time_correction": 0
                    },
                    "female_details": {
                        "name": "பிரியா",
                        "date_of_birth": "1991-04-18",
                        "time_of_birth": "09:20:00",
                        "place_of_birth": "Erode, Tamil Nadu, India",
                        "latitude": 11.3410,
                        "longitude": 77.7172,
                        "timezone": "IST",
                        "time_correction": 0
                    },
                    "system": "thirukkanitham",
                    "language": "tamil"
                }
            }
        ]
        
        for test_case in test_cases:
            try:
                response = self.session.post(
                    f"{API_BASE}/compatibility",
                    json=test_case["data"],
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Validate response structure
                    required_fields = [
                        'male_details', 'female_details', 'system', 'language',
                        'total_points', 'max_points', 'percentage', 'overall_rating',
                        'factors', 'dosha_analysis', 'recommendation'
                    ]
                    
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        percentage = data.get('percentage', 0)
                        factors_count = len(data.get('factors', []))
                        self.log_test(f"Compatibility - {test_case['name']}", True, 
                                    f"Score: {percentage:.1f}%, Factors: {factors_count}")
                    else:
                        self.log_test(f"Compatibility - {test_case['name']}", False, 
                                    f"Missing fields: {missing_fields}")
                else:
                    self.log_test(f"Compatibility - {test_case['name']}", False, 
                                f"Status: {response.status_code}, Response: {response.text[:200]}")
                    
            except Exception as e:
                self.log_test(f"Compatibility - {test_case['name']}", False, f"Error: {str(e)}")
    
    def test_user_profiles(self):
        """Test user profile management"""
        print("\n👤 Testing User Profiles")
        print("-" * 25)
        
        # Test profile creation
        profile_data = {
            "name": "சுந்தர்",
            "birth_details": {
                "name": "சுந்தர்",
                "date_of_birth": "1985-09-12",
                "time_of_birth": "11:30:00",
                "place_of_birth": "Thanjavur, Tamil Nadu, India",
                "latitude": 10.7870,
                "longitude": 79.1378,
                "timezone": "IST",
                "time_correction": 0
            }
        }
        
        created_profile_id = None
        
        try:
            response = self.session.post(
                f"{API_BASE}/profiles",
                json=profile_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data and 'name' in data:
                    created_profile_id = data['id']
                    self.log_test("Profile Creation", True, f"Created profile ID: {created_profile_id}")
                else:
                    self.log_test("Profile Creation", False, f"Missing required fields in response")
            else:
                self.log_test("Profile Creation", False, 
                            f"Status: {response.status_code}, Response: {response.text[:200]}")
                
        except Exception as e:
            self.log_test("Profile Creation", False, f"Error: {str(e)}")
        
        # Test profile listing
        try:
            response = self.session.get(f"{API_BASE}/profiles")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Profile Listing", True, f"Retrieved {len(data)} profiles")
                else:
                    self.log_test("Profile Listing", False, "Response is not a list")
            else:
                self.log_test("Profile Listing", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Profile Listing", False, f"Error: {str(e)}")
        
        # Test individual profile retrieval
        if created_profile_id:
            try:
                response = self.session.get(f"{API_BASE}/profiles/{created_profile_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('id') == created_profile_id:
                        self.log_test("Profile Retrieval", True, f"Retrieved profile: {data.get('name')}")
                    else:
                        self.log_test("Profile Retrieval", False, "Profile ID mismatch")
                else:
                    self.log_test("Profile Retrieval", False, f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test("Profile Retrieval", False, f"Error: {str(e)}")
    
    def test_panchangam(self):
        """Test Panchangam (Thirukkanitham only)"""
        print("\n📅 Testing Panchangam")
        print("-" * 20)
        
        test_dates = [
            "2024-12-28",
            "2024-01-01",
            "2024-06-15"
        ]
        
        for test_date in test_dates:
            for language in ["tamil", "english"]:
                try:
                    response = self.session.get(f"{API_BASE}/panchangam/{test_date}?language={language}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Validate response structure
                        required_fields = [
                            'date', 'tithi', 'nakshatra', 'yoga', 'karana',
                            'sunrise', 'sunset', 'rahu_kalam', 'yama_gandam', 'gulika_kalam'
                        ]
                        
                        missing_fields = [field for field in required_fields if field not in data]
                        
                        if not missing_fields:
                            # Check for Tamil content if language is Tamil
                            if language == "tamil":
                                has_tamil = any([
                                    data.get('tithi_tamil'),
                                    data.get('nakshatra_tamil'),
                                    data.get('yoga_tamil')
                                ])
                                if has_tamil:
                                    self.log_test(f"Panchangam {test_date} ({language})", True, 
                                                f"Tithi: {data.get('tithi')}")
                                else:
                                    self.log_test(f"Panchangam {test_date} ({language})", False, 
                                                "Missing Tamil translations")
                            else:
                                self.log_test(f"Panchangam {test_date} ({language})", True, 
                                            f"Tithi: {data.get('tithi')}")
                        else:
                            self.log_test(f"Panchangam {test_date} ({language})", False, 
                                        f"Missing fields: {missing_fields}")
                    else:
                        self.log_test(f"Panchangam {test_date} ({language})", False, 
                                    f"Status: {response.status_code}, Response: {response.text[:200]}")
                        
                except Exception as e:
                    self.log_test(f"Panchangam {test_date} ({language})", False, f"Error: {str(e)}")
    
    def test_error_handling(self):
        """Test error handling with invalid data"""
        print("\n⚠️  Testing Error Handling")
        print("-" * 25)
        
        # Test invalid system
        try:
            invalid_data = {
                "birth_details": {
                    "name": "Test",
                    "date_of_birth": "1990-01-01",
                    "time_of_birth": "12:00:00",
                    "place_of_birth": "Chennai",
                    "latitude": 13.0827,
                    "longitude": 80.2707,
                    "timezone": "IST",
                    "time_correction": 0
                },
                "system": "invalid_system",
                "language": "tamil"
            }
            
            response = self.session.post(f"{API_BASE}/horoscope", json=invalid_data)
            
            if response.status_code == 400:
                self.log_test("Invalid System Error", True, "Correctly rejected invalid system")
            else:
                self.log_test("Invalid System Error", False, f"Expected 400, got {response.status_code}")
                
        except Exception as e:
            self.log_test("Invalid System Error", False, f"Error: {str(e)}")
        
        # Test missing required fields
        try:
            incomplete_data = {
                "birth_details": {
                    "name": "Test"
                    # Missing required fields
                },
                "system": "vakkiam"
            }
            
            response = self.session.post(f"{API_BASE}/horoscope", json=incomplete_data)
            
            if response.status_code in [400, 422]:  # 422 is common for validation errors
                self.log_test("Missing Fields Error", True, "Correctly rejected incomplete data")
            else:
                self.log_test("Missing Fields Error", False, f"Expected 400/422, got {response.status_code}")
                
        except Exception as e:
            self.log_test("Missing Fields Error", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Tamil Astrology API Tests")
        print("=" * 60)
        
        self.test_health_endpoints()
        self.test_horoscope_generation()
        self.test_compatibility_check()
        self.test_user_profiles()
        self.test_panchangam()
        self.test_error_handling()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if self.failed_tests:
            print(f"\n🔍 Failed Tests:")
            for test in self.failed_tests:
                print(f"  - {test}")
        
        return failed_tests == 0

if __name__ == "__main__":
    tester = TamilAstrologyTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"\n💥 {len(tester.failed_tests)} tests failed!")
        sys.exit(1)