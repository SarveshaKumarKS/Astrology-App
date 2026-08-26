"""
Emergent-managed Google Auth for the Tamil Astrology app.

Exposes:
  - router: APIRouter with /auth/session, /auth/me, /auth/logout
  - get_current_user: FastAPI dependency that resolves the Bearer session_token
    to a user document (raises 401 when missing/invalid/expired).

Sessions and users are stored in MongoDB. Session tokens last 7 days.
"""
import os
import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

EMERGENT_SESSION_URL = "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data"
SESSION_TTL_DAYS = 7

mongo_url = os.environ["MONGO_URL"]
database_name = os.environ["DB_NAME"]
_client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=2000)
_db = _client[database_name]

router = APIRouter(prefix="/auth", tags=["auth"])


class SessionRequest(BaseModel):
    session_id: str


async def ensure_indexes() -> None:
    """Create the indexes required for auth. Best-effort (DB may be down)."""
    try:
        await _db.users.create_index("email", unique=True)
        await _db.users.create_index("user_id", unique=True)
        await _db.user_sessions.create_index("session_token", unique=True)
        await _db.user_sessions.create_index("user_id")
        # Expiry is enforced in _resolve_user. Avoid a MongoDB TTL index here:
        # deployment startup must not register automatic destructive cleanup.
    except Exception as e:  # pragma: no cover
        logger.warning(f"Auth index creation skipped (DB unavailable): {e}")


def _public_user(user: dict) -> dict:
    return {
        "user_id": user.get("user_id"),
        "email": user.get("email"),
        "name": user.get("name"),
        "picture": user.get("picture"),
    }


@router.post("/session")
async def create_session(payload: SessionRequest):
    """Exchange a one-time Emergent session_id for a 7-day session_token."""
    session_id = payload.session_id
    if not session_id:
        raise HTTPException(status_code=401, detail="Missing session_id")

    try:
        async with httpx.AsyncClient(timeout=15) as http:
            resp = await http.get(
                EMERGENT_SESSION_URL,
                headers={"X-Session-ID": session_id},
            )
    except Exception as e:
        logger.error(f"Auth exchange network error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    data = resp.json()
    email = data.get("email")
    name = data.get("name")
    picture = data.get("picture")
    session_token = data.get("session_token")
    if not email or not session_token:
        raise HTTPException(status_code=401, detail="Invalid session data")

    now = datetime.now(timezone.utc)

    # Upsert user by email (reuse existing user_id).
    existing = await _db.users.find_one({"email": email}, {"_id": 0})
    if existing:
        user_id = existing["user_id"]
        await _db.users.update_one(
            {"user_id": user_id},
            {"$set": {"name": name, "picture": picture, "last_login": now}},
        )
        user = {**existing, "name": name, "picture": picture}
    else:
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        user = {
            "user_id": user_id,
            "email": email,
            "name": name,
            "picture": picture,
            "created_at": now,
            "last_login": now,
        }
        await _db.users.insert_one(dict(user))

    await _db.user_sessions.insert_one({
        "session_token": session_token,
        "user_id": user_id,
        "created_at": now,
        "expires_at": now + timedelta(days=SESSION_TTL_DAYS),
    })

    return {"session_token": session_token, "user": _public_user(user)}


async def _resolve_user(request: Request) -> Optional[dict]:
    auth_header = request.headers.get("Authorization") or ""
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header[len("Bearer "):].strip()
    if not token:
        return None

    session = await _db.user_sessions.find_one({"session_token": token}, {"_id": 0})
    if not session:
        return None

    expires_at = session.get("expires_at")
    if isinstance(expires_at, datetime):
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            return None

    user = await _db.users.find_one({"user_id": session["user_id"]}, {"_id": 0})
    return user


async def get_current_user(request: Request) -> dict:
    """Dependency: require a valid Bearer session_token."""
    user = await _resolve_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


@router.get("/me")
async def get_me(request: Request):
    user = await _resolve_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"user": _public_user(user)}


@router.post("/logout")
async def logout(request: Request):
    auth_header = request.headers.get("Authorization") or ""
    if auth_header.startswith("Bearer "):
        token = auth_header[len("Bearer "):].strip()
        if token:
            try:
                await _db.user_sessions.delete_one({"session_token": token})
            except Exception as e:
                logger.warning(f"Logout cleanup failed: {e}")
    return {"success": True}
