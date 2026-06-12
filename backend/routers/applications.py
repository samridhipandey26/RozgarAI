"""
backend/routers/applications.py — Application lifecycle
"""
from __future__ import annotations

import random
import sys
import time
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from backend.schemas.models import (
    ApplicationCreate, ApplicationResponse, ApplicationStatusUpdate,
)

router = APIRouter(prefix="/api/applications", tags=["applications"])
security = HTTPBearer(auto_error=False)


def _require_user(credentials: HTTPAuthorizationCredentials | None) -> str:
    if not credentials:
        raise HTTPException(401, "Authentication required")
    try:
        from backend.db.supabase_client import get_supabase
        sb = get_supabase()
        if sb:
            user_resp = sb.auth.get_user(credentials.credentials)
            return user_resp.user.id
    except Exception:
        pass
    raise HTTPException(401, "Invalid token")


# ── Apply for a job (HARD GATE) ───────────────────────────────────────────────

@router.post("/", response_model=ApplicationResponse, status_code=201)
async def apply_for_job(
    req: ApplicationCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    HARD GATE: req.confirmed must be True.
    Creates an Application record in DB.
    """
    if not req.confirmed:
        raise HTTPException(400, "Application requires explicit confirmation (confirmed=true)")

    user_id = _require_user(credentials)

    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))
    app_id = str(uuid.uuid4())
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    app_data = {
        "id": app_id,
        "worker_id": user_id,
        "job_id": req.job_id,
        "status": "applied",
        "otp": otp,
        "applied_at": now,
    }

    from backend.db.supabase_client import sb_insert, supabase_available

    if supabase_available():
        result = sb_insert("applications", app_data)
        if result is None:
            # Might already exist — check for duplicate
            from backend.db.supabase_client import sb_select
            existing = sb_select("applications", {"worker_id": user_id, "job_id": req.job_id})
            if existing:
                e = existing[0]
                return ApplicationResponse(
                    id=str(e["id"]),
                    worker_id=user_id,
                    job_id=req.job_id,
                    status=e["status"],
                    otp=e.get("otp"),
                    applied_at=str(e.get("applied_at", "")),
                )
            raise HTTPException(500, "Failed to create application")
    else:
        # SQLite fallback
        _sqlite_insert_application(app_data)

    # Optional: send Twilio notification to employer
    _notify_employer_optional(req.job_id, user_id)

    return ApplicationResponse(
        id=app_id,
        worker_id=user_id,
        job_id=req.job_id,
        status="applied",
        otp=otp,
        applied_at=now,
    )


# ── Worker: list own applications ─────────────────────────────────────────────

@router.get("/worker", response_model=list[ApplicationResponse])
async def list_worker_applications(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Worker sees their own application history + current status."""
    user_id = _require_user(credentials)

    from backend.db.supabase_client import sb_select, supabase_available

    if supabase_available():
        apps = sb_select("applications", {"worker_id": user_id}, limit=50)
    else:
        apps = _sqlite_get_applications(worker_id=user_id)

    return [
        ApplicationResponse(
            id=str(a["id"]),
            worker_id=str(a["worker_id"]),
            job_id=str(a["job_id"]),
            status=a["status"],
            otp=a.get("otp"),
            applied_at=str(a.get("applied_at", "")),
        )
        for a in apps
    ]


# ── Employer: list applicants for a job ───────────────────────────────────────

@router.get("/employer/{job_id}", response_model=list[ApplicationResponse])
async def list_job_applicants(
    job_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Employer sees all applicants for a specific job."""
    user_id = _require_user(credentials)

    from backend.db.supabase_client import sb_select, supabase_available

    if supabase_available():
        apps = sb_select("applications", {"job_id": job_id}, limit=100)
    else:
        apps = _sqlite_get_applications(job_id=job_id)

    return [
        ApplicationResponse(
            id=str(a["id"]),
            worker_id=str(a["worker_id"]),
            job_id=str(a["job_id"]),
            status=a["status"],
            otp=a.get("otp"),
            applied_at=str(a.get("applied_at", "")),
        )
        for a in apps
    ]


# ── Update status (employer) ──────────────────────────────────────────────────

@router.patch("/{app_id}/status")
async def update_application_status(
    app_id: str,
    req: ApplicationStatusUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Employer updates application status: contacted → confirmed → completed."""
    _require_user(credentials)

    valid = {"contacted", "confirmed", "completed", "rejected"}
    if req.status not in valid:
        raise HTTPException(400, f"Invalid status. Must be one of: {valid}")

    from backend.db.supabase_client import sb_update, supabase_available

    if supabase_available():
        sb_update("applications", app_id, {
            "status": req.status,
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        })
    else:
        _sqlite_update_application(app_id, req.status)

    return {"success": True, "app_id": app_id, "new_status": req.status}


# ── SQLite fallback helpers ───────────────────────────────────────────────────

def _sqlite_insert_application(data: dict) -> None:
    import sqlite3
    db_path = ROOT / "data" / "rozgar.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id TEXT PRIMARY KEY, worker_id TEXT, job_id TEXT,
            status TEXT DEFAULT 'applied', otp TEXT, applied_at TEXT, updated_at TEXT
        )
    """)
    conn.execute(
        "INSERT OR IGNORE INTO applications (id,worker_id,job_id,status,otp,applied_at) VALUES (?,?,?,?,?,?)",
        (data["id"], data["worker_id"], data["job_id"], data["status"], data["otp"], data["applied_at"])
    )
    conn.commit()
    conn.close()


def _sqlite_get_applications(worker_id: str = None, job_id: str = None) -> list[dict]:
    import sqlite3
    db_path = ROOT / "data" / "rozgar.db"
    if not db_path.exists():
        return []
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    if worker_id:
        rows = conn.execute("SELECT * FROM applications WHERE worker_id=?", (worker_id,)).fetchall()
    elif job_id:
        rows = conn.execute("SELECT * FROM applications WHERE job_id=?", (job_id,)).fetchall()
    else:
        rows = []
    conn.close()
    return [dict(r) for r in rows]


def _sqlite_update_application(app_id: str, status: str) -> None:
    import sqlite3
    db_path = ROOT / "data" / "rozgar.db"
    if not db_path.exists():
        return
    conn = sqlite3.connect(str(db_path))
    conn.execute("UPDATE applications SET status=? WHERE id=?", (status, app_id))
    conn.commit()
    conn.close()


def _notify_employer_optional(job_id: str, worker_id: str) -> None:
    """Fire Twilio SMS to employer if configured."""
    try:
        twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
        twilio_token = os.environ.get("TWILIO_AUTH_TOKEN", "")
        twilio_from = os.environ.get("TWILIO_FROM", "")
        if not (twilio_sid and twilio_token and twilio_from):
            return
        # Fetch employer phone from Supabase
        from backend.db.supabase_client import sb_select
        jobs = sb_select("jobs", {"id": job_id}, limit=1)
        if not jobs:
            return
        employer_id = jobs[0].get("employer_id")
        if not employer_id:
            return
        employer_roles = sb_select("user_roles", {"user_id": employer_id}, limit=1)
        if not employer_roles:
            return
        employer_phone = employer_roles[0].get("phone", "")
        if not employer_phone:
            return
        # Send SMS
        from twilio.rest import Client
        client = Client(twilio_sid, twilio_token)
        client.messages.create(
            body=f"RozgarAI: Ek naya worker ne aapke job '{jobs[0]['title']}' ke liye apply kiya hai!",
            from_=twilio_from,
            to=employer_phone,
        )
    except Exception as e:
        print(f"[Twilio] Employer notification failed (non-critical): {e}")


import os
