"""Regression tests for grouped correction submission payload/storage shape."""

import os
import uuid
from pathlib import Path

import pytest
import requests
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv(Path(__file__).resolve().parents[1] / ".env")
load_dotenv(Path(__file__).resolve().parents[2] / "frontend" / ".env")

# Public preview base URL used by end users.
BASE_URL = os.environ.get("EXPO_PUBLIC_BACKEND_URL", "").rstrip("/")
API = f"{BASE_URL}/api"

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]


@pytest.fixture(scope="session")
def mongo_db():
    """Mongo connection for persistence verification."""
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=3000)
    db = client[DB_NAME]
    yield db
    client.close()


class TestCorrectionsGroupedPayload:
    """Corrections API grouped storage and validation checks."""

    def test_grouped_submission_persists_single_document_with_required_nested_fields(self, mongo_db):
        marker = f"TEST_UI_BATCH_{uuid.uuid4().hex[:10]}"
        payload = {
            "birth_details": {
                "name": marker,
                "place_of_birth": "Chennai",
                "date_of_birth": "1991-07-03",
                "time_of_birth": "10:45:00",
            },
            "corrections": [
                {
                    "screen_id": "horoscope_result",
                    "field_name": "MoonSign",
                    "original_value": "Rishabam",
                    "corrected_value": "Mithunam",
                },
                {
                    "screen_id": "horoscope_result",
                    "field_name": "Nakshatra",
                    "original_value": "Rohini",
                    "corrected_value": "Mrigashirsha",
                },
            ],
            "metadata": {
                "app_version": "1.0.0",
                "device_model": "pytest-device",
                "platform": "web",
                "note": "TEST grouped corrections batch",
            },
        }

        response = requests.post(f"{API}/corrections", json=payload, timeout=30)
        assert response.status_code == 200, response.text
        body = response.json()
        assert body.get("success") is True
        assert body.get("count") == 2

        doc = mongo_db.corrections.find_one({"batch_id": body["batch_id"]}, {"_id": 0})
        try:
            assert doc is not None
            assert doc["birth_details"]["name"] == marker
            assert doc["birth_details"]["place_of_birth"] == "Chennai"
            assert doc["birth_details"]["date_of_birth"] == "1991-07-03"
            assert doc["birth_details"]["time_of_birth"] == "10:45:00"

            assert isinstance(doc["corrections"], list)
            assert len(doc["corrections"]) == 2
            assert doc["corrections"][0]["field_name"] == "MoonSign"
            assert doc["corrections"][1]["field_name"] == "Nakshatra"

            assert "field_name" not in doc
            assert "corrected_value" not in doc

            assert "metadata" in doc
            assert doc["metadata"]["app_version"] == "1.0.0"
            assert doc["metadata"]["device_model"] == "pytest-device"
            assert doc["metadata"]["platform"] == "web"
            assert doc["metadata"]["note"] == "TEST grouped corrections batch"
            assert "email" in doc["metadata"]
        finally:
            mongo_db.corrections.delete_one({"batch_id": body["batch_id"]})

    def test_empty_corrections_list_returns_400_and_does_not_persist(self, mongo_db):
        marker = f"TEST_EMPTY_{uuid.uuid4().hex[:8]}"
        payload = {
            "birth_details": {
                "name": marker,
                "place_of_birth": "Madurai",
                "date_of_birth": "1993-09-11",
                "time_of_birth": "11:11:00",
            },
            "corrections": [],
            "metadata": {
                "app_version": "1.0.0",
                "device_model": "pytest-device",
                "platform": "web",
                "note": "empty corrections should fail",
            },
        }

        before = mongo_db.corrections.count_documents({"birth_details.name": marker})
        response = requests.post(f"{API}/corrections", json=payload, timeout=30)
        assert response.status_code == 400, response.text
        assert "No corrections provided" in response.text
        after = mongo_db.corrections.count_documents({"birth_details.name": marker})
        assert before == after
