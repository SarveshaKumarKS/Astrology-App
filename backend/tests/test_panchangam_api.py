"""Panchangam API regression checks for real daily data fields."""

import os
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[2] / "frontend" / ".env")

# Public preview URL used by users; fail fast if missing.
BASE_URL = os.environ.get("EXPO_PUBLIC_BACKEND_URL")
assert BASE_URL, "EXPO_PUBLIC_BACKEND_URL is required for API tests"
API = f"{BASE_URL.rstrip('/')}/api"


class TestPanchangamApi:
    """/api/panchangam/{date} endpoint contract and content checks."""

    def test_get_panchangam_english_returns_200_and_required_fields(self):
        response = requests.get(
            f"{API}/panchangam/2026-08-19",
            params={"language": "english"},
            timeout=30,
        )
        assert response.status_code == 200, response.text

        body = response.json()
        assert body["date"] == "2026-08-19"

        for key in [
            "tithi",
            "nakshatra",
            "yoga",
            "karana",
            "sunrise",
            "sunset",
            "moonrise",
            "moonset",
            "rahu_kalam",
            "yama_gandam",
            "gulika_kalam",
            "abhijit_muhurta",
        ]:
            assert key in body

        # Ensure non-placeholder panchangam values are present.
        assert isinstance(body["tithi"], str) and body["tithi"].strip()
        assert isinstance(body["nakshatra"], str) and body["nakshatra"].strip()
        assert isinstance(body["yoga"], str) and body["yoga"].strip()
        assert isinstance(body["karana"], str) and body["karana"].strip()

        for period_key in ["rahu_kalam", "yama_gandam", "gulika_kalam", "abhijit_muhurta"]:
            period = body[period_key]
            assert isinstance(period, dict)
            assert isinstance(period.get("start"), str) and period["start"].strip()
            assert isinstance(period.get("end"), str) and period["end"].strip()
