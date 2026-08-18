"""
Regression tests for the Tamil Astrology backend:
  - Emergent Google Auth endpoints (/api/auth/session, /api/auth/me, /api/auth/logout)
  - Auth-gated user profile CRUD (/api/profiles*) with per-user isolation
  - Profile rename (PUT /api/profiles/{id}) — NEW this iteration
  - Feedback submission (POST /api/feedback) — NEW this iteration
  - Core open endpoints still work without auth (horoscope, PDF, compatibility)

After the load_dotenv reordering in server.py, auth.py now binds to the same DB
as the rest of the backend (astrology_db per backend/.env). We therefore seed
into DB_NAME (env) — no more split-DB workaround.
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
DB_NAME = os.environ["DB_NAME"]  # astrology_db — used by BOTH auth.py and server.py after fix

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
    """Single DB used by both auth.py and server.py after the load_dotenv fix."""
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=3000)
    db = client[DB_NAME]
    yield db
    client.close()


def _seed_user(db, tag: str):
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    email = f"TEST_{tag}_{uuid.uuid4().hex[:6]}@test.local"
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


def _cleanup_user(db, user_id: str):
    db.user_sessions.delete_many({"user_id": user_id})
    db.user_profiles.delete_many({"user_id": user_id})
    db.users.delete_many({"user_id": user_id})


@pytest.fixture()
def seeded_user_a(mongo_db):
    ctx = _seed_user(mongo_db, "user_a")
    yield ctx
    _cleanup_user(mongo_db, ctx["user_id"])


@pytest.fixture()
def seeded_user_b(mongo_db):
    ctx = _seed_user(mongo_db, "user_b")
    yield ctx
    _cleanup_user(mongo_db, ctx["user_id"])


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


# ---------- DB binding sanity check ----------

class TestDBBindingFix:
    """Confirm the load_dotenv reordering: auth.py now writes to DB_NAME=astrology_db."""

    def test_auth_binds_to_astrology_db(self, mongo_db, seeded_user_a):
        # If auth.py were still bound to the 'tamil_astrology' fallback,
        # /auth/me would return 401 (it would not find our seeded session in astrology_db).
        r = requests.get(f"{API}/auth/me", headers=_auth(seeded_user_a["token"]), timeout=30)
        assert r.status_code == 200, (
            f"/auth/me returned {r.status_code}; auth.py may still be bound to the "
            f"'tamil_astrology' fallback. DB_NAME={DB_NAME}"
        )
        # Sanity: session/user rows really live in DB_NAME
        assert mongo_db.users.find_one({"user_id": seeded_user_a["user_id"]}) is not None
        assert mongo_db.user_sessions.find_one({"session_token": seeded_user_a["token"]}) is not None


# ---------- Auth endpoint tests ----------

class TestAuthEndpoints:
    def test_session_invalid_returns_401(self):
        r = requests.post(f"{API}/auth/session",
                          json={"session_id": "definitely-not-real"}, timeout=30)
        assert r.status_code == 401

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
        assert mongo_db.user_sessions.find_one({"session_token": token}) is None
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

    def test_put_profile_rename_requires_auth(self):
        r = requests.put(f"{API}/profiles/abc", json={"label": "New"}, timeout=30)
        assert r.status_code == 401


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
        assert pid in [p["id"] for p in r.json()]

        # B sees zero (no shared profiles)
        r = requests.get(f"{API}/profiles", headers=_auth(tb), timeout=30)
        assert r.status_code == 200
        assert pid not in [p["id"] for p in r.json()]

        # B cannot GET A's profile
        assert requests.get(f"{API}/profiles/{pid}",
                            headers=_auth(tb), timeout=30).status_code == 404

        # B cannot DELETE A's profile
        assert requests.delete(f"{API}/profiles/{pid}",
                               headers=_auth(tb), timeout=30).status_code == 404

        # A GET own
        r = requests.get(f"{API}/profiles/{pid}", headers=_auth(ta), timeout=30)
        assert r.status_code == 200
        assert r.json()["id"] == pid

        # A DELETE own
        r = requests.delete(f"{API}/profiles/{pid}", headers=_auth(ta), timeout=30)
        assert r.status_code == 200
        assert r.json().get("success") is True

        # After delete: GET 404
        assert requests.get(f"{API}/profiles/{pid}",
                            headers=_auth(ta), timeout=30).status_code == 404


# ---------- NEW: PUT /api/profiles/{id} rename ----------

class TestProfileRename:
    def test_rename_own_profile_success(self, mongo_db, seeded_user_a):
        ta = seeded_user_a["token"]
        r = requests.post(f"{API}/profiles",
                          json={"name": "orig", "birth_details": SAMPLE_BIRTH},
                          headers=_auth(ta), timeout=30)
        assert r.status_code == 200
        pid = r.json()["id"]

        r = requests.put(f"{API}/profiles/{pid}",
                         json={"label": "My Chart"}, headers=_auth(ta), timeout=30)
        assert r.status_code == 200, r.text
        body = r.json()
        assert body.get("success") is True
        assert body.get("label") == "My Chart"

        # Verify persisted via GET
        r = requests.get(f"{API}/profiles/{pid}", headers=_auth(ta), timeout=30)
        assert r.status_code == 200
        assert r.json().get("label") == "My Chart"

        # DB row also has label set
        row = mongo_db.user_profiles.find_one({"id": pid})
        assert row and row.get("label") == "My Chart"

    def test_rename_empty_label_returns_400(self, seeded_user_a):
        ta = seeded_user_a["token"]
        r = requests.post(f"{API}/profiles",
                          json={"name": "orig", "birth_details": SAMPLE_BIRTH},
                          headers=_auth(ta), timeout=30)
        pid = r.json()["id"]

        r = requests.put(f"{API}/profiles/{pid}",
                         json={"label": "   "}, headers=_auth(ta), timeout=30)
        assert r.status_code == 400, r.text

    def test_rename_other_users_profile_returns_404(self, seeded_user_a, seeded_user_b):
        ta, tb = seeded_user_a["token"], seeded_user_b["token"]
        r = requests.post(f"{API}/profiles",
                          json={"name": "orig", "birth_details": SAMPLE_BIRTH},
                          headers=_auth(ta), timeout=30)
        pid = r.json()["id"]

        r = requests.put(f"{API}/profiles/{pid}",
                         json={"label": "Hacked"}, headers=_auth(tb), timeout=30)
        assert r.status_code == 404, r.text


# ---------- NEW: POST /api/feedback ----------

class TestFeedback:
    def test_feedback_open_no_auth_success(self, mongo_db):
        r = requests.post(f"{API}/feedback",
                          json={"message": "TEST_feedback anonymous",
                                "screen": "home", "platform": "web"}, timeout=30)
        assert r.status_code == 200, r.text
        assert r.json().get("success") is True
        doc = mongo_db.feedback.find_one({"message": "TEST_feedback anonymous"})
        assert doc is not None
        assert doc.get("email") is None
        assert doc.get("screen") == "home"
        # cleanup
        mongo_db.feedback.delete_many({"message": "TEST_feedback anonymous"})

    def test_feedback_empty_returns_400(self):
        r = requests.post(f"{API}/feedback", json={"message": "   "}, timeout=30)
        assert r.status_code == 400

    def test_feedback_with_auth_stores_email(self, mongo_db, seeded_user_a):
        marker = f"TEST_feedback_authed_{uuid.uuid4().hex[:6]}"
        r = requests.post(f"{API}/feedback",
                          json={"message": marker, "screen": "account"},
                          headers=_auth(seeded_user_a["token"]), timeout=30)
        assert r.status_code == 200
        assert r.json().get("success") is True
        doc = mongo_db.feedback.find_one({"message": marker})
        assert doc is not None
        assert doc.get("email") == seeded_user_a["email"]
        mongo_db.feedback.delete_many({"message": marker})


# ---------- Open endpoints (no auth required) ----------

class TestOpenEndpoints:
    def test_horoscope_open(self):
        r = requests.post(f"{API}/horoscope", json=HOROSCOPE_BODY, timeout=60)
        assert r.status_code == 200, r.text[:400]
        body = r.json()
        assert "planetary_positions" in body
        assert body["birth_details"]["name"] == "Test"

    def test_generate_pdf_open(self):
        r = requests.post(f"{API}/generate-pdf", json=HOROSCOPE_BODY, timeout=90)
        assert r.status_code == 200, r.text[:400]
        assert r.headers.get("content-type", "").startswith("application/pdf")
        assert len(r.content) > 500

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
