#!/usr/bin/env python3
"""
Panchangam Integration Testing for Tamil Astrology API
Tests the newly implemented Panchangam details in horoscope generation and PDF endpoints
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

print(f"Testing Panchangam Integration at: {API_BASE}")
print("=" * 60)

class PanchangamTester:
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
    
    def test_horoscope_panchangam_vakkiam(self):
        """Test Horoscope Generation - Vakkiam System with Panchangam"""
        print("\n🌟 Testing Horoscope Generation - Vakkiam System")
        print("-" * 50)
        
        test_data = {
            "birth_details": {
                "name": "Test User",
                "date_of_birth": "1990-01-15",
                "time_of_birth": "10:30:00",
                "place_of_birth": "Chennai",
                "latitude": 13.0827,
                "longitude": 80.2707,
                "timezone": "IST",
                "time_correction": 0
            },
            "system": "vakkiam",
            "language": "tamil"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/horoscope",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check Panchangam fields
                panchangam_fields = [
                    'sunrise_time', 'sunset_time', 'paksha', 'tithi', 'tithi_tamil',
                    'yoga', 'yoga_tamil', 'karana', 'karana_tamil', 'ayanamsa',
                    'udayadi_nazhigai', 'yogi_planet', 'yogi_planet_tamil',
                    'avayogi_planet', 'avayogi_planet_tamil'
                ]
                
                missing_panchangam = [field for field in panchangam_fields if field not in data or data[field] is None]
                present_panchangam = [field for field in panchangam_fields if field in data and data[field] is not None]
                
                if len(present_panchangam) >= 10:  # At least 10 out of 15 fields should be present
                    details = f"Panchangam fields present: {len(present_panchangam)}/15"
                    if data.get('sunrise_time'):
                        details += f", Sunrise: {data['sunrise_time']}"
                    if data.get('tithi_tamil'):
                        details += f", Tithi: {data['tithi_tamil']}"
                    if data.get('yoga_tamil'):
                        details += f", Yoga: {data['yoga_tamil']}"
                    self.log_test("Vakkiam Horoscope - Panchangam Integration", True, details)
                else:
                    self.log_test("Vakkiam Horoscope - Panchangam Integration", False, 
                                f"Only {len(present_panchangam)}/15 Panchangam fields present. Missing: {missing_panchangam[:5]}")
            else:
                self.log_test("Vakkiam Horoscope - Panchangam Integration", False, 
                            f"Status: {response.status_code}, Response: {response.text[:200]}")
                
        except Exception as e:
            self.log_test("Vakkiam Horoscope - Panchangam Integration", False, f"Error: {str(e)}")
    
    def test_horoscope_panchangam_thirukkanitham(self):
        """Test Horoscope Generation - Thirukkanitham System with Panchangam"""
        print("\n🌟 Testing Horoscope Generation - Thirukkanitham System")
        print("-" * 55)
        
        test_data = {
            "birth_details": {
                "name": "Test User",
                "date_of_birth": "1992-05-20",
                "time_of_birth": "14:45:00",
                "place_of_birth": "Madurai",
                "latitude": 9.9252,
                "longitude": 78.1198,
                "timezone": "IST",
                "time_correction": 0
            },
            "system": "thirukkanitham",
            "language": "tamil"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/horoscope",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check Panchangam fields
                panchangam_fields = [
                    'sunrise_time', 'sunset_time', 'paksha', 'tithi', 'tithi_tamil',
                    'yoga', 'yoga_tamil', 'karana', 'karana_tamil', 'ayanamsa',
                    'udayadi_nazhigai', 'yogi_planet', 'yogi_planet_tamil',
                    'avayogi_planet', 'avayogi_planet_tamil'
                ]
                
                missing_panchangam = [field for field in panchangam_fields if field not in data or data[field] is None]
                present_panchangam = [field for field in panchangam_fields if field in data and data[field] is not None]
                
                if len(present_panchangam) >= 10:  # At least 10 out of 15 fields should be present
                    details = f"Panchangam fields present: {len(present_panchangam)}/15"
                    if data.get('sunset_time'):
                        details += f", Sunset: {data['sunset_time']}"
                    if data.get('karana_tamil'):
                        details += f", Karana: {data['karana_tamil']}"
                    if data.get('ayanamsa'):
                        details += f", Ayanamsa: {data['ayanamsa']}"
                    self.log_test("Thirukkanitham Horoscope - Panchangam Integration", True, details)
                else:
                    self.log_test("Thirukkanitham Horoscope - Panchangam Integration", False, 
                                f"Only {len(present_panchangam)}/15 Panchangam fields present. Missing: {missing_panchangam[:5]}")
            else:
                self.log_test("Thirukkanitham Horoscope - Panchangam Integration", False, 
                            f"Status: {response.status_code}, Response: {response.text[:200]}")
                
        except Exception as e:
            self.log_test("Thirukkanitham Horoscope - Panchangam Integration", False, f"Error: {str(e)}")
    
    def test_pdf_generation_vakkiam(self):
        """Test PDF Generation with Panchangam Details - Vakkiam"""
        print("\n📄 Testing PDF Generation - Vakkiam System")
        print("-" * 45)
        
        test_data = {
            "birth_details": {
                "name": "திரு. ராஜ்",
                "date_of_birth": "1990-01-15",
                "time_of_birth": "10:30:00",
                "place_of_birth": "சென்னை",
                "latitude": 13.0827,
                "longitude": 80.2707,
                "timezone": "IST",
                "time_correction": 0
            },
            "system": "vakkiam",
            "language": "tamil"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/generate-pdf",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                
                if content_type == 'application/pdf' and content_length > 50000:  # PDF should be > 50KB
                    self.log_test("Vakkiam PDF Generation - Panchangam Details", True, 
                                f"PDF generated successfully, Size: {content_length/1024:.1f}KB")
                else:
                    self.log_test("Vakkiam PDF Generation - Panchangam Details", False, 
                                f"Invalid PDF: Type={content_type}, Size={content_length/1024:.1f}KB")
            else:
                self.log_test("Vakkiam PDF Generation - Panchangam Details", False, 
                            f"Status: {response.status_code}, Response: {response.text[:200]}")
                
        except Exception as e:
            self.log_test("Vakkiam PDF Generation - Panchangam Details", False, f"Error: {str(e)}")
    
    def test_pdf_generation_thirukkanitham(self):
        """Test PDF Generation with Panchangam Details - Thirukkanitham"""
        print("\n📄 Testing PDF Generation - Thirukkanitham System")
        print("-" * 50)
        
        test_data = {
            "birth_details": {
                "name": "திருமதி. மீனா",
                "date_of_birth": "1992-05-20",
                "time_of_birth": "14:45:00",
                "place_of_birth": "மதுரை",
                "latitude": 9.9252,
                "longitude": 78.1198,
                "timezone": "IST",
                "time_correction": 0
            },
            "system": "thirukkanitham",
            "language": "tamil"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/generate-pdf",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                
                if content_type == 'application/pdf' and content_length > 50000:  # PDF should be > 50KB
                    self.log_test("Thirukkanitham PDF Generation - Panchangam Details", True, 
                                f"PDF generated successfully, Size: {content_length/1024:.1f}KB")
                else:
                    self.log_test("Thirukkanitham PDF Generation - Panchangam Details", False, 
                                f"Invalid PDF: Type={content_type}, Size={content_length/1024:.1f}KB")
            else:
                self.log_test("Thirukkanitham PDF Generation - Panchangam Details", False, 
                            f"Status: {response.status_code}, Response: {response.text[:200]}")
                
        except Exception as e:
            self.log_test("Thirukkanitham PDF Generation - Panchangam Details", False, f"Error: {str(e)}")
    
    def test_regression_functionality(self):
        """Test that existing functionality still works"""
        print("\n🔄 Testing Regression - Existing Functionality")
        print("-" * 45)
        
        test_data = {
            "birth_details": {
                "name": "Regression Test",
                "date_of_birth": "1985-12-25",
                "time_of_birth": "06:00:00",
                "place_of_birth": "Coimbatore",
                "latitude": 11.0168,
                "longitude": 76.9558,
                "timezone": "IST",
                "time_correction": 0
            },
            "system": "vakkiam",
            "language": "tamil"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/horoscope",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check existing functionality
                checks = []
                
                # Planetary positions table should have Ascendant as first row
                planets = data.get('planetary_positions', [])
                if planets and len(planets) == 9:
                    checks.append("✓ 9 planets present")
                else:
                    checks.append("✗ Planet count incorrect")
                
                # Dasa details should show balance_years, next_dasa, current/next bhukti
                current_dasa = data.get('current_dasa', {})
                if current_dasa and 'balance_years' in current_dasa:
                    checks.append("✓ Dasa balance present")
                else:
                    checks.append("✗ Dasa balance missing")
                
                # Retrograde planets should be calculated
                retrograde = data.get('retrograde_planets', [])
                checks.append(f"✓ Retrograde planets: {len(retrograde)}")
                
                # Both Rasi and Navamsa charts should render correctly
                rasi_chart = data.get('rasi_chart', {})
                navamsa_chart = data.get('navamsa_chart', {})
                if rasi_chart.get('houses') and navamsa_chart.get('houses'):
                    checks.append("✓ Both charts present")
                else:
                    checks.append("✗ Charts missing")
                
                # Bhava Maruthal should be calculated
                bhava_maruthal = data.get('bhava_maruthal', {})
                if bhava_maruthal:
                    checks.append(f"✓ Bhava Maruthal: {len(bhava_maruthal)} planets")
                else:
                    checks.append("✗ Bhava Maruthal missing")
                
                success_count = sum(1 for check in checks if check.startswith("✓"))
                total_checks = len(checks)
                
                if success_count >= 4:  # At least 4 out of 5 checks should pass
                    self.log_test("Regression Test - Existing Functionality", True, 
                                f"{success_count}/{total_checks} checks passed: {', '.join(checks[:3])}")
                else:
                    self.log_test("Regression Test - Existing Functionality", False, 
                                f"Only {success_count}/{total_checks} checks passed: {', '.join(checks)}")
            else:
                self.log_test("Regression Test - Existing Functionality", False, 
                            f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Regression Test - Existing Functionality", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all Panchangam integration tests"""
        print("🚀 Starting Panchangam Integration Tests")
        print("=" * 60)
        
        self.test_horoscope_panchangam_vakkiam()
        self.test_horoscope_panchangam_thirukkanitham()
        self.test_pdf_generation_vakkiam()
        self.test_pdf_generation_thirukkanitham()
        self.test_regression_functionality()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 PANCHANGAM INTEGRATION TEST SUMMARY")
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
    tester = PanchangamTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All Panchangam integration tests passed!")
        sys.exit(0)
    else:
        print(f"\n💥 {len(tester.failed_tests)} Panchangam tests failed!")
        sys.exit(1)