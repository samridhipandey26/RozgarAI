"""
backend/schemas/models.py — Pydantic request/response models for all API endpoints
"""
from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# ── Auth ──────────────────────────────────────────────────────────────────────
# (OTP removed — now email/password based)

class AuthResponse(BaseModel):
    user_id: str
    access_token: str
    role: str
    is_new_user: bool = False
    name: Optional[str] = None
    onboarding_done: bool = False

class UserProfile(BaseModel):
    user_id: str
    email: str = ""
    role: str
    name: Optional[str] = None
    onboarding_done: bool = False

# Legacy OTP stubs kept for backward compat (unused)
class SendOTPRequest(BaseModel):
    phone: str = ""
class SendOTPResponse(BaseModel):
    success: bool = False
    message: str = ""
class VerifyOTPRequest(BaseModel):
    phone: str = ""
    otp: str = ""
    role: str = "worker"


# ── Worker Profile ─────────────────────────────────────────────────────────────

class WorkerProfileCreate(BaseModel):
    name: str
    city: str
    skill: str
    skills_all: List[str] = []
    years_exp: int = 0
    expected_wage: int = 500
    languages: List[str] = ["Hindi"]
    education: str = "Not specified"
    raw_transcript: Optional[str] = None

class WorkerProfileResponse(BaseModel):
    id: str
    user_id: str
    name: str
    city: str
    lat: Optional[float] = None
    lng: Optional[float] = None
    skill: str
    skills_all: List[str] = []
    years_exp: int
    expected_wage: int
    languages: List[str]
    education: str
    onboarding_done: bool = False
    created_at: Optional[str] = None


# ── Jobs ──────────────────────────────────────────────────────────────────────

class JobCreate(BaseModel):
    title: str
    title_hindi: str
    role_tag: str
    description: Optional[str] = None
    wage_per_day: int
    city: str
    address: str
    openings: int = 1
    start_date: Optional[date] = None

class JobResponse(BaseModel):
    id: str
    employer_id: Optional[str] = None
    employer_name: Optional[str] = None
    title: str
    title_hindi: str
    role_tag: str
    description: Optional[str] = None
    wage_per_day: int
    city: str
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    openings: int
    filled: int = 0
    start_date: Optional[str] = None
    status: str = "open"
    created_at: Optional[str] = None
    # Computed at match time:
    distance_km: Optional[float] = None
    match_score: Optional[float] = None
    match_pct: Optional[int] = None


# ── Pipeline ──────────────────────────────────────────────────────────────────

class PipelineStartRequest(BaseModel):
    transcript: Optional[str] = None   # text input fallback
    # audio is sent as multipart file, not in this body

class PipelineStartResponse(BaseModel):
    session_id: str
    message: str = "Pipeline started"

class PipelineConfirmRequest(BaseModel):
    session_id: str
    gate: str = Field(..., description="'apply'")
    confirmed: bool

class AgentEvent(BaseModel):
    event: str          # agent_started | agent_completed | gate_reached | pipeline_done | error
    agent: Optional[str] = None
    latency_ms: Optional[int] = None
    data: Optional[dict] = None
    message: Optional[str] = None


# ── Applications ──────────────────────────────────────────────────────────────

class ApplicationCreate(BaseModel):
    job_id: str
    confirmed: bool = Field(..., description="HARD GATE — must be True")

class ApplicationResponse(BaseModel):
    id: str
    worker_id: str
    job_id: str
    status: str
    otp: Optional[str] = None
    applied_at: Optional[str] = None
    job: Optional[JobResponse] = None

class ApplicationStatusUpdate(BaseModel):
    status: str = Field(..., description="contacted|confirmed|completed|rejected")


# ── Resumes ───────────────────────────────────────────────────────────────────

class ResumeResponse(BaseModel):
    id: str
    worker_id: str
    version: int
    pdf_url: Optional[str] = None
    pdf_path: Optional[str] = None
    created_at: Optional[str] = None

class ResumeListResponse(BaseModel):
    resumes: List[ResumeResponse]
    latest: Optional[ResumeResponse] = None


# ── Stats ─────────────────────────────────────────────────────────────────────

class StatsResponse(BaseModel):
    workers_registered: int
    jobs_filled: int
    avg_daily_wage: int
    active_cities: int
    open_jobs: int
    total_applications: int


# ── Geocoding ─────────────────────────────────────────────────────────────────

class GeocodeRequest(BaseModel):
    address: str

class GeocodeResponse(BaseModel):
    lat: float
    lng: float
    display_name: Optional[str] = None
