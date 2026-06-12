"""
backend/routers/auth.py — Email/Password + local fallback auth
Strategy: Supabase email+password when SUPABASE_* env vars are set.
          Otherwise: local SQLite user store (dev mode).
"""
from __future__ import annotations

import hashlib
import os
import secrets
import sqlite3
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)

ROOT = Path(__file__).parent.parent.parent
LOCAL_DB = ROOT / "data" / "rozgar.db"


# ── Request / Response schemas ────────────────────────────────────────────────

class SignupRequest(BaseModel):
    email: str
    password: str
    role: str = "worker"
    name: str = ""

class LoginRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    user_id: str
    access_token: str
    role: str
    name: str | None = None
    is_new_user: bool = False
    onboarding_done: bool = False

class UserProfile(BaseModel):
    user_id: str
    email: str
    role: str
    name: str | None = None
    onboarding_done: bool = False


# ── Helpers ───────────────────────────────────────────────────────────────────

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def _make_token(user_id: str) -> str:
    """Simple deterministic token (replace with JWT in prod)."""
    secret = os.getenv("JWT_SECRET", "rozgar-dev-secret")
    raw = f"{user_id}:{secret}"
    return hashlib.sha256(raw.encode()).hexdigest()

def _get_supabase():
    """Return Supabase client if configured, else None."""
    try:
        from backend.db.supabase_client import get_supabase, supabase_available
        if supabase_available():
            return get_supabase()
    except Exception:
        pass
    return None


# ── Local SQLite auth fallback ────────────────────────────────────────────────

def _init_local_db():
    LOCAL_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(LOCAL_DB))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS local_users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'worker',
            name TEXT DEFAULT '',
            onboarding_done INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()

def _local_signup(email: str, password: str, role: str, name: str) -> dict:
    _init_local_db()
    import uuid
    uid = str(uuid.uuid4())
    conn = sqlite3.connect(str(LOCAL_DB))
    conn.row_factory = sqlite3.Row
    try:
        conn.execute(
            "INSERT INTO local_users (id, email, password_hash, role, name) VALUES (?,?,?,?,?)",
            (uid, email, _hash(password), role, name)
        )
        conn.commit()
        return {"id": uid, "email": email, "role": role, "name": name, "onboarding_done": 0}
    except sqlite3.IntegrityError:
        raise HTTPException(409, "An account with this email already exists.")
    finally:
        conn.close()

def _local_login(email: str, password: str) -> dict:
    _init_local_db()
    conn = sqlite3.connect(str(LOCAL_DB))
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM local_users WHERE email=? AND password_hash=?",
        (email, _hash(password))
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(401, "Invalid email/phone or password.")
    return dict(row)

def _local_get_user_by_token(token: str) -> dict | None:
    """Find user by matching their token."""
    _init_local_db()
    conn = sqlite3.connect(str(LOCAL_DB))
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM local_users").fetchall()
    conn.close()
    for row in rows:
        if _make_token(row["id"]) == token:
            return dict(row)
    return None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/signup", response_model=AuthResponse)
async def signup(req: SignupRequest):
    """
    Email/Password signup.
    Uses Supabase if configured, otherwise local SQLite (dev mode).
    Phone numbers are accepted as-is for the email field.
    """
    # Normalise: if it looks like a phone, prefix with a pseudo-domain
    email = req.email.strip()
    if email.startswith("+") or email.lstrip("+").isdigit():
        email = f"{email.lstrip('+')}@rozgarai.app"

    sb = _get_supabase()

    if sb:
        # ── Supabase path ────────────────────────────────────────────
        try:
            res = sb.auth.sign_up({"email": email, "password": req.password})
            if not res.user:
                raise HTTPException(400, "Signup failed — no user returned")
            user_id = res.user.id
            access_token = res.session.access_token if res.session else _make_token(user_id)
            # Save role + name
            sb.table("user_roles").upsert({
                "user_id": user_id,
                "role": req.role,
                "name": req.name,
                "phone": req.email if req.email.startswith("+") else "",
            }).execute()
            return AuthResponse(
                user_id=user_id, access_token=access_token,
                role=req.role, name=req.name, is_new_user=True,
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(400, f"Signup failed: {e}")
    else:
        # ── Local SQLite fallback ─────────────────────────────────────
        user = _local_signup(email, req.password, req.role, req.name)
        token = _make_token(user["id"])
        return AuthResponse(
            user_id=user["id"], access_token=token,
            role=user["role"], name=user["name"], is_new_user=True,
        )


@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest):
    """Email/Password login."""
    email = req.email.strip()
    if email.startswith("+") or email.lstrip("+").isdigit():
        email = f"{email.lstrip('+')}@rozgarai.app"

    sb = _get_supabase()

    if sb:
        try:
            res = sb.auth.sign_in_with_password({"email": email, "password": req.password})
            if not res.user or not res.session:
                raise HTTPException(401, "Invalid credentials")
            user_id = res.user.id
            access_token = res.session.access_token
            # Fetch role + onboarding state
            role_row = sb.table("user_roles").select("*").eq("user_id", user_id).execute()
            role_data = role_row.data[0] if role_row.data else {}
            profile_row = sb.table("worker_profiles").select("onboarding_done").eq("user_id", user_id).execute()
            onboarding_done = bool(profile_row.data[0].get("onboarding_done")) if profile_row.data else False
            return AuthResponse(
                user_id=user_id, access_token=access_token,
                role=role_data.get("role", "worker"),
                name=role_data.get("name"),
                onboarding_done=onboarding_done,
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(401, f"Login failed: {e}")
    else:
        user = _local_login(email, req.password)
        token = _make_token(user["id"])
        return AuthResponse(
            user_id=user["id"], access_token=token,
            role=user["role"], name=user.get("name"),
            onboarding_done=bool(user.get("onboarding_done", 0)),
        )


@router.get("/me", response_model=UserProfile)
async def get_me(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Return current user from JWT / session token."""
    if not credentials:
        raise HTTPException(401, "Not authenticated")
    token = credentials.credentials

    sb = _get_supabase()
    if sb:
        try:
            res = sb.auth.get_user(token)
            user = res.user
            if not user:
                raise HTTPException(401, "Invalid token")
            role_row = sb.table("user_roles").select("*").eq("user_id", user.id).execute()
            role_data = role_row.data[0] if role_row.data else {}
            profile_row = sb.table("worker_profiles").select("onboarding_done").eq("user_id", user.id).execute()
            onboarding_done = bool(profile_row.data[0].get("onboarding_done")) if profile_row.data else False
            return UserProfile(
                user_id=user.id, email=user.email or "",
                role=role_data.get("role", "worker"),
                name=role_data.get("name"),
                onboarding_done=onboarding_done,
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(401, f"Token validation failed: {e}")
    else:
        user = _local_get_user_by_token(token)
        if not user:
            raise HTTPException(401, "Invalid or expired token")
        return UserProfile(
            user_id=user["id"], email=user["email"],
            role=user["role"], name=user.get("name"),
            onboarding_done=bool(user.get("onboarding_done", 0)),
        )


@router.post("/logout")
async def logout():
    """Client-side: just clear localStorage. Server-side: revoke if using Supabase."""
    return {"success": True, "message": "Logged out"}
