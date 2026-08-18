"""
Regression tests for the Tamil Astrology backend:
  - Emergent Google Auth endpoints (/api/auth/session, /api/auth/me)
  - Auth-gated user profile CRUD (/api/profiles*) with per-user isolation
  - Core open endpoints still work without auth (horoscope, PDF, compatibility)

Sessions are seeded directly in MongoDB (bypasses Google) per the playbook.
"""

import os
import uuid
import pytest
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient

# Load backend .env for MONGO_URL / DB_NAME
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# Public URL (through k8s ingress) — matches what the user sees.
BASE_URL = (os.environ.get("EXPO_PUBLIC_BACKEND_URL")
            or "https://vakkiam-preview.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"

MONGO_URL = os.environ["MONGO_URL"]
# NOTE: The running backend's auth module reads DB_NAME at import time, BEFORE
# server.py's load_dotenv() runs, so auth actually writes to the fallback
# `tamil_astrology` DB while server.py (post-load_dotenv) writes profiles to
# `astrology_db`. This mismatch is a real bug we flag in the report; for tests
# we must seed into whichever DB the *auth module in the running backend* uses.
DB_NAME_AUTH = "tamil_astrology"  # matches the fallback in auth.py at import time
DB_NAME = os.environ["DB_NAME"]   # matches server.py post-load_dotenv (astrology_db)

SAMPLE_BIRTH = {
    "name": "Test",
    "date_of_birth": "1990-05-15",
    "time_of_birth": "08:30:00",
    "place_of_birth": "Chennai",
    "latitude": 13.0827,
    "longitude": 80.2707,
    "timezone": "Asia/Kolkata",
}
HOROSCOPE_BODY = {
    "birth_details": SAMPLE_BIRTH,
    "system": "vakkiam",
    "language": "tamil",
}


# ---------- fixtures ----------

@pytest.fixture(scope="session")
def mongo_db():
    """DB used by the auth module inside the running backend."""
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=3000)
    db = client[DB_NAME_AUTH]
    yield db
    client.close()


@pytest.fixture(scope="session")
def profile_db():
    """DB used by server.py (POST /api/profiles) for user_profiles collection."""
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=3000)
    db = client[DB_NAME]
    yield db
    client.close()


def _seed_user(db, tag: str):
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    email = f"{tag}_{uuid.uuid4().hex[:6]}@test.local"
    session_token = f"tok_{uuid.uuid4().hex}"
    now = datetime.now(timezone.utc)
    db.users.insert_one({
        "user_id": user_id, "email": email, "name": tag,
        "created_at": now, "last_login": now,
    })
    db.user_sessions.insert_one({
        "session_token": session_token, "user_id": user_id,
        "created_at": now, "expires_at": now + timedelta(days=7),
    })
    return {"user_id": user_id, "email": email, "token": session_token}


def _cleanup_user(db, user_id: str, profile_db=None):
    db.user_sessions.delete_many({"user_id": user_id})
    db.user_profiles.delete_many({"user_id": user_id})
    db.users.delete_many({"user_id": user_id})
    if profile_db is not None:
        profile_db.user_profiles.delete_many({"user_id": user_id})


@pytest.fixture()
def seeded_user_a(mongo_db, profile_db):
    ctx = _seed_user(mongo_db, "TEST_user_a")
    yield ctx
    _cleanup_user(mongo_db, ctx["user_id"], profile_db)


@pytest.fixture()
def seeded_user_b(mongo_db, profile_db):
    ctx = _seed_user(mongo_db, "TEST_user_b")
    yield ctx
    _cleanup_user(mongo_db, ctx["user_id"], profile_db)


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


# ---------- Auth endpoint tests ----------

class TestAuthEndpoints:
    def test_session_invalid_returns_401_not_500(self):
        r = requests.post(f"{API}/auth/session",
                          json={"session_id": "definitely-not-real"}, timeout=30)
        assert r.status_code == 401, f"expected 401, got {r.status_code}: {r.text}"

    def test_session_missing_id_returns_401(self):
        r = requests.post(f"{API}/auth/session", json={"session_id": ""}, timeout=30)
        assert r.status_code == 401

    def test_me_without_auth_returns_401(self):
        r = requests.get(f"{API}/auth/me", timeout=30)
        assert r.status_code == 401

    def test_me_with_seeded_token(self, seeded_user_a):
        r = requests.get(f"{API}/auth/me", headers=_auth(seeded_user_a["token"]), timeout=30)
        assert r.status_code == 200
        body = r.json()
        assert body["user"]["email"] == seeded_user_a["email"]
        assert body["user"]["user_id"] == seeded_user_a["user_id"]

    def test_logout_clears_session(self, mongo_db, seeded_user_a):
        token = seeded_user_a["token"]
        r = requests.post(f"{API}/auth/logout", headers=_auth(token), timeout=30)
        assert r.status_code == 200
        # session row must be gone
        assert mongo_db.user_sessions.find_one({"session_token": token}) is None
        # subsequent /me must be 401
        r2 = requests.get(f"{API}/auth/me", headers=_auth(token), timeout=30)
        assert r2.status_code == 401


# ---------- /api/profiles auth gate tests ----------

class TestProfilesAuthGate:
    def test_get_profiles_requires_auth(self):
        assert requests.get(f"{API}/profiles", timeout=30).status_code == 401

    def test_post_profiles_requires_auth(self):
        payload = {"name": "Test", "birth_details": SAMPLE_BIRTH}
        assert requests.post(f"{API}/profiles", json=payload, timeout=30).status_code == 401

    def test_get_profile_by_id_requires_auth(self):
        assert requests.get(f"{API}/profiles/abc", timeout=30).status_code == 401

    def test_delete_profile_requires_auth(self):
        assert requests.delete(f"{API}/profiles/abc", timeout=30).status_code == 401


# ---------- /api/profiles CRUD + per-user isolation ----------

class TestProfilesCrudAndIsolation:
    def test_full_crud_and_scoping(self, seeded_user_a, seeded_user_b):
        ta, tb = seeded_user_a["token"], seeded_user_b["token"]

        # A creates a profile
        payload = {"name": "A_profile", "birth_details": SAMPLE_BIRTH}
        r = requests.post(f"{API}/profiles", json=payload, headers=_auth(ta), timeout=30)
        assert r.status_code == 200, r.text
        created = r.json()
        pid = created["id"]
        assert created["user_id"] == seeded_user_a["user_id"]
        assert created["birth_details"]["place_of_birth"] == "Chennai"

        # A sees it in the list
        r = requests.get(f"{API}/profiles", headers=_auth(ta), timeout=30)
        assert r.status_code == 200
        ids = [p["id"] for p in r.json()]
        assert pid in ids

        # B sees zero (no shared profiles)
        r = requests.get(f"{API}/profiles", headers=_auth(tb), timeout=30)
        assert r.status_code == 200
        assert all(p["user_id"] == seeded_user_b["user_id"] for p in r.json())
        b_ids = [p["id"] for p in r.json()]
        assert pid not in b_ids

        # B cannot GET A's profile
        r = requests.get(f"{API}/profiles/{pid}", headers=_auth(tb), timeout=30)
        assert r.status_code == 404

        # B cannot DELETE A's profile
        r = requests.delete(f"{API}/profiles/{pid}", headers=_auth(tb), timeout=30)
        assert r.status_code == 404

        # A can GET own
        r = requests.get(f"{API}/profiles/{pid}", headers=_auth(ta), timeout=30)
        assert r.status_code == 200
        assert r.json()["id"] == pid

        # A can DELETE own
        r = requests.delete(f"{API}/profiles/{pid}", headers=_auth(ta), timeout=30)
        assert r.status_code == 200
        assert r.json().get("success") is True

        # After delete: GET returns 404
        r = requests.get(f"{API}/profiles/{pid}", headers=_auth(ta), timeout=30)
        assert r.status_code == 404


# ---------- Open endpoints (no auth required) ----------

class TestOpenEndpoints:
    def test_horoscope_open(self):
        r = requests.post(f"{API}/horoscope", json=HOROSCOPE_BODY, timeout=60)
        assert r.status_code == 200, r.text
        body = r.json()
        assert "planetary_positions" in body
        assert body["birth_details"]["name"] == "Test"

    def test_generate_pdf_open(self):
        r = requests.post(f"{API}/generate-pdf", json=HOROSCOPE_BODY, timeout=90)
        assert r.status_code == 200, r.text[:400]
        assert r.headers.get("content-type", "").startswith("application/pdf")
        assert len(r.content) > 500  # some real bytes

    def test_compatibility_open(self):
        payload = {
            "male_details": SAMPLE_BIRTH,
            "female_details": {**SAMPLE_BIRTH, "name": "Test2",
                               "date_of_birth": "1992-06-20"},
            "system": "vakkiam",
            "language": "tamil",
        }
        r = requests.post(f"{API}/compatibility", json=payload, timeout=60)
        assert r.status_code == 200, r.text[:400]
